# mypy: ignore-errors
"""
Fact Checker for Friday Memory.

Classifies and verifies facts:
- Determines if facts are falsifiable (verifiable) or conversational (opinion)
- Verifies falsifiable claims using researcher + judge LLM pattern
- Updates fact metadata with verification results
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import chromadb

from friday_memory.json_response import (
    json_parse_warning_detail,
    parse_json_object_from_text,
)
from friday_memory.maintenance.models import (
    ClaimType,
    ClassifiedFact,
    FactCheckConfig,
    PromptsConfig,
    VerificationReport,
    VerificationVerdict,
    VerifiedClaim,
)

if TYPE_CHECKING:
    from friday_llm import LiteLLMService

    from friday_memory.maintenance.logger import ReorganizationLogger

logger = logging.getLogger(__name__)


class FactChecker:
    """
    Classifies and verifies facts stored in memory.

    Uses a multi-stage pipeline:
    1. Classification: Determine if fact is falsifiable
    2. Research: Gather evidence (for falsifiable claims)
    3. Judge: Render verdict based on evidence

    Example:
        from friday_llm import LiteLLMService

        llm = LiteLLMService(model_name="gpt-4")
        checker = FactChecker(
            memory_dir="./memory",
            classifier_llm=llm,
            researcher_llm=llm,
            judge_llm=llm,
        )

        # Classify all facts
        classified = await checker.classify_facts()

        # Verify falsifiable claims
        report = await checker.verify_claims(dry_run=False)
    """

    def __init__(
        self,
        memory_dir: str | Path,
        classifier_llm: LiteLLMService | None = None,
        researcher_llm: LiteLLMService | None = None,
        judge_llm: LiteLLMService | None = None,
        config: FactCheckConfig | None = None,
        prompts: PromptsConfig | None = None,
        reorg_logger: ReorganizationLogger | None = None,
    ) -> None:
        """
        Initialize the fact checker.

        Args:
            memory_dir: Directory containing memory stores
            classifier_llm: LLM for classifying facts (falsifiable vs conversational)
            researcher_llm: LLM for researching claims
            judge_llm: LLM for rendering verdicts
            config: Configuration for fact checking
            prompts: Prompts configuration (defaults used if not provided)
            reorg_logger: Optional logger for recording actions
        """
        self._memory_dir = Path(memory_dir)
        self._classifier = classifier_llm
        self._researcher = researcher_llm
        self._judge = judge_llm
        self._config = config or FactCheckConfig()
        self._prompts = prompts or PromptsConfig()
        self._reorg_logger = reorg_logger

    def _parse_json_response(
        self,
        content: str,
        *,
        reasoning_content: str | None = None,
    ) -> dict[str, Any]:
        """
        Parse JSON from LLM response, handling various formats.

        LLMs often wrap JSON in markdown code blocks or add extra text.
        This method tries multiple strategies to extract valid JSON.

        Args:
            content: Raw LLM response content

        Returns:
            Parsed JSON as dict, or empty dict if parsing fails
        """
        parse_content = content if content.strip() else reasoning_content or ""
        parsed = parse_json_object_from_text(parse_content)
        if parsed is not None:
            return parsed

        # Strategy 5: Return empty structure
        logger.warning(
            json_parse_warning_detail(
                "memory fact-checking",
                content,
                reasoning_content=reasoning_content,
            )
        )
        return {}

    def _get_chroma_client(self) -> chromadb.ClientAPI | None:
        """Get ChromaDB client."""
        # Try both possible locations for ChromaDB:
        # 1. Directly in memory_dir (when memory_dir IS the vector dir)
        # 2. In memory_dir/vector subdirectory
        for vector_dir in [self._memory_dir, self._memory_dir / "vector"]:
            chroma_db = vector_dir / "chroma.sqlite3"
            if chroma_db.exists():
                try:
                    return chromadb.PersistentClient(path=str(vector_dir))
                except Exception as e:
                    logger.warning(f"Failed to open ChromaDB at {vector_dir}: {e}")
                    continue

        logger.warning(
            f"ChromaDB not found in {self._memory_dir} or {self._memory_dir / 'vector'}"
        )
        return None

    def _get_unclassified_facts(self) -> list[dict[str, Any]]:
        """Get facts that haven't been classified yet."""
        client = self._get_chroma_client()
        if not client:
            return []

        try:
            collections = client.list_collections()
            if not collections:
                return []

            collection = collections[0]

            # Get all documents
            data = collection.get(
                include=["metadatas", "documents"],
            )

            facts = []
            for i, doc_id in enumerate(data["ids"]):
                metadata = data["metadatas"][i] if data["metadatas"] else {}
                doc_type = metadata.get("type", "")

                # Only process insights (facts)
                if doc_type != "insight":
                    continue

                # Skip already classified
                if "falsifiable" in metadata:
                    continue

                facts.append(
                    {
                        "id": doc_id,
                        "text": data["documents"][i] if data["documents"] else "",
                        "metadata": metadata,
                    }
                )

            return facts

        except Exception as e:
            logger.error(f"Error getting unclassified facts: {e}")
            return []

    def _get_falsifiable_claims(
        self,
        unverified_only: bool = True,
    ) -> list[dict[str, Any]]:
        """Get falsifiable claims that need verification."""
        client = self._get_chroma_client()
        if not client:
            return []

        try:
            collections = client.list_collections()
            if not collections:
                return []

            collection = collections[0]
            data = collection.get(include=["metadatas", "documents"])

            claims = []
            for i, doc_id in enumerate(data["ids"]):
                metadata = data["metadatas"][i] if data["metadatas"] else {}

                # Only falsifiable claims
                if not metadata.get("falsifiable"):
                    continue

                # Skip already verified if requested
                if unverified_only and metadata.get("verified") is not None:
                    continue

                claims.append(
                    {
                        "id": doc_id,
                        "text": data["documents"][i] if data["documents"] else "",
                        "metadata": metadata,
                    }
                )

            return claims

        except Exception as e:
            logger.error(f"Error getting falsifiable claims: {e}")
            return []

    async def _classify_single_fact(self, fact_text: str) -> dict[str, Any]:
        """
        Classify a single fact using LLM.

        Args:
            fact_text: The fact text to classify

        Returns:
            Classification result dict
        """
        if self._classifier is None:
            raise ValueError("No classifier LLM configured")

        prompt = self._prompts.classification.format(statement=fact_text)

        response = await self._classifier.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        return self._parse_json_response(
            response.content or "",
            reasoning_content=getattr(response, "reasoning_content", None),
        )

    async def _research_claim(self, claim_text: str) -> dict[str, Any]:
        """
        Research a claim using LLM.

        Args:
            claim_text: The claim to research

        Returns:
            Research result dict
        """
        if self._researcher is None:
            raise ValueError("No researcher LLM configured")

        prompt = self._prompts.research.format(claim=claim_text)

        response = await self._researcher.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return self._parse_json_response(
            response.content or "",
            reasoning_content=getattr(response, "reasoning_content", None),
        )

    async def _judge_claim(
        self,
        claim_text: str,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Judge a claim based on evidence.

        Args:
            claim_text: The original claim
            evidence: Research evidence

        Returns:
            Judge verdict dict
        """
        if self._judge is None:
            raise ValueError("No judge LLM configured")

        evidence_text = json.dumps(evidence, indent=2)
        prompt = self._prompts.judge.format(claim=claim_text, evidence=evidence_text)

        response = await self._judge.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        return self._parse_json_response(
            response.content or "",
            reasoning_content=getattr(response, "reasoning_content", None),
        )

    def _update_fact_metadata(
        self,
        fact_id: str,
        updates: dict[str, Any],
    ) -> bool:
        """
        Update metadata for a fact in the vector store.

        Args:
            fact_id: ID of the fact to update
            updates: Metadata fields to update

        Returns:
            True if updated successfully
        """
        client = self._get_chroma_client()
        if not client:
            return False

        try:
            collections = client.list_collections()
            if not collections:
                return False

            collection = collections[0]

            # Get current metadata
            data = collection.get(ids=[fact_id], include=["metadatas"])
            if not data["ids"]:
                return False

            current_metadata = data["metadatas"][0] if data["metadatas"] else {}

            # Merge updates
            new_metadata = {**current_metadata, **updates}

            # Update
            collection.update(
                ids=[fact_id],
                metadatas=[new_metadata],
            )

            return True

        except Exception as e:
            logger.error(f"Error updating fact metadata: {e}")
            return False

    async def classify_facts(
        self,
        limit: int = 100,
        unclassified_only: bool = True,
        dry_run: bool = True,
    ) -> list[ClassifiedFact]:
        """
        Classify facts as falsifiable or conversational.

        Args:
            limit: Maximum number of facts to classify
            unclassified_only: Only classify facts without existing classification
            dry_run: If True, don't update metadata

        Returns:
            List of classified facts
        """
        if self._classifier is None:
            logger.warning("No classifier LLM configured")
            return []

        facts = self._get_unclassified_facts() if unclassified_only else []
        facts = facts[:limit]

        logger.info(f"Classifying {len(facts)} facts")

        classified: list[ClassifiedFact] = []

        for fact in facts:
            try:
                # Get raw prompt for logging
                prompt = self._prompts.classification.format(statement=fact["text"])
                result = await self._classify_single_fact(fact["text"])

                # Map claim_type to enum
                claim_type_str = result.get("claim_type", "opinion").lower()
                try:
                    claim_type = ClaimType(claim_type_str)
                except ValueError:
                    claim_type = ClaimType.OPINION

                falsifiable = result.get("falsifiable", False)
                reasoning = result.get("reasoning", "")

                classified_fact = ClassifiedFact(
                    fact_id=fact["id"],
                    original_text=fact["text"],
                    falsifiable=falsifiable,
                    claim_type=claim_type,
                    reasoning=reasoning,
                    suggested_verification=result.get("suggested_verification"),
                )
                classified.append(classified_fact)

                # Log the classification
                if self._reorg_logger:
                    self._reorg_logger.log_fact_classified(
                        fact_id=fact["id"],
                        falsifiable=falsifiable,
                        claim_type=claim_type.value,
                        reason=reasoning,
                        content_preview=fact["text"][:200] if fact["text"] else None,
                        prompt_sent=prompt,
                        llm_response_raw=str(result),
                        llm_response_parsed=result,
                    )

                # Update metadata if not dry run
                if not dry_run:
                    self._update_fact_metadata(
                        fact["id"],
                        {
                            "falsifiable": falsifiable,
                            "claim_type": claim_type.value,
                            "classification_reasoning": reasoning,
                            "classified_at": datetime.now().isoformat(),
                        },
                    )

            except Exception as e:
                logger.error(f"Error classifying fact {fact['id']}: {e}")

        logger.info(
            f"Classified {len(classified)} facts: "
            f"{sum(1 for c in classified if c.falsifiable)} falsifiable, "
            f"{sum(1 for c in classified if not c.falsifiable)} conversational"
        )

        return classified

    async def identify_falsifiable_claims(
        self,
        unverified_only: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Get all falsifiable claims pending verification.

        Args:
            unverified_only: Only return unverified claims

        Returns:
            List of claim dicts
        """
        return self._get_falsifiable_claims(unverified_only)

    async def verify_claims(
        self,
        claims: list[dict[str, Any]] | None = None,
        dry_run: bool = True,
    ) -> VerificationReport:
        """
        Verify falsifiable claims using researcher + judge pattern.

        Args:
            claims: Optional list of claims to verify. If None, gets unverified.
            dry_run: If True, don't update metadata

        Returns:
            VerificationReport with results
        """
        if self._researcher is None or self._judge is None:
            logger.warning("Researcher and judge LLMs required for verification")
            return VerificationReport(dry_run=dry_run)

        if claims is None:
            claims = self._get_falsifiable_claims(unverified_only=True)

        claims = claims[: self._config.batch_size]

        logger.info(f"Verifying {len(claims)} claims (dry_run={dry_run})")

        report = VerificationReport(dry_run=dry_run, total_claims=len(claims))

        for claim in claims:
            try:
                claim_text = claim["text"]
                claim_id = claim["id"]

                # 1. Research the claim
                logger.debug(f"Researching claim: {claim_text[:50]}...")
                evidence = await self._research_claim(claim_text)

                # 2. Judge the claim
                logger.debug("Judging claim...")
                verdict_result = await self._judge_claim(claim_text, evidence)

                # Parse verdict
                verdict_str = verdict_result.get("verdict", "UNVERIFIABLE").upper()
                try:
                    verdict = VerificationVerdict(verdict_str)
                except ValueError:
                    verdict = VerificationVerdict.UNVERIFIABLE

                confidence = verdict_result.get("confidence", 0.5)
                evidence_summary = evidence.get("evidence_summary", "")
                sources = evidence.get("sources", [])
                correction = verdict_result.get("correction")
                judge_reasoning = verdict_result.get("reasoning", "")

                verified_claim = VerifiedClaim(
                    claim_id=claim_id,
                    original_text=claim_text,
                    falsifiable=True,
                    verdict=verdict,
                    confidence=confidence,
                    evidence_summary=evidence_summary,
                    sources=sources,
                    correction=correction,
                    judge_reasoning=judge_reasoning,
                )
                report.verified_claims.append(verified_claim)

                # Log the verification
                if self._reorg_logger:
                    research_prompt = self._prompts.research.format(claim=claim_text)
                    judge_prompt = self._prompts.judge.format(
                        claim=claim_text,
                        evidence=json.dumps(evidence, indent=2),
                    )
                    self._reorg_logger.log_fact_verified(
                        fact_id=claim_id,
                        verdict=verdict.value,
                        confidence=confidence,
                        reason=judge_reasoning,
                        content_preview=claim_text[:200] if claim_text else None,
                        evidence_summary=evidence_summary,
                        sources=sources,
                        correction=correction,
                        prompt_sent=f"RESEARCH:\n{research_prompt}\n\nJUDGE:\n{judge_prompt}",
                        llm_response_raw=str(verdict_result),
                        llm_response_parsed={
                            "research": evidence,
                            "verdict": verdict_result,
                        },
                    )

                # Update counts
                if verdict == VerificationVerdict.VERIFIED:
                    report.verified_true += 1
                elif verdict == VerificationVerdict.DISPUTED:
                    report.verified_false += 1
                else:
                    report.unverifiable += 1

                # Update metadata if not dry run
                if not dry_run:
                    self._update_fact_metadata(
                        claim_id,
                        {
                            "verified": verdict == VerificationVerdict.VERIFIED,
                            "verification_verdict": verdict.value,
                            "verification_confidence": confidence,
                            "verification_sources": json.dumps(sources),
                            "verification_note": correction or "",
                            "verified_at": datetime.now().isoformat(),
                            "verified_by": "fact_checker_v1",
                        },
                    )

            except Exception as e:
                logger.error(f"Error verifying claim {claim.get('id', 'unknown')}: {e}")
                report.errors.append(str(e))

        logger.info(
            f"Verification complete: "
            f"verified={report.verified_true}, "
            f"disputed={report.verified_false}, "
            f"unverifiable={report.unverifiable}"
        )

        return report

    async def update_fact_confidence(
        self,
        adjustments: list[tuple[str, float]],
    ) -> int:
        """
        Bulk update confidence scores based on verification.

        Args:
            adjustments: List of (fact_id, new_confidence) tuples

        Returns:
            Number of facts updated
        """
        updated = 0
        for fact_id, confidence in adjustments:
            if self._update_fact_metadata(fact_id, {"confidence": confidence}):
                updated += 1
        return updated

    async def run_full_check(self, dry_run: bool = True) -> VerificationReport:
        """
        Run full fact checking pipeline: classify then verify.

        Args:
            dry_run: If True, don't update metadata

        Returns:
            VerificationReport with all results
        """
        logger.info(f"Running full fact check (dry_run={dry_run})")

        report = VerificationReport(dry_run=dry_run)

        # 1. Classify unclassified facts
        classified = await self.classify_facts(
            limit=self._config.batch_size,
            unclassified_only=True,
            dry_run=dry_run,
        )
        report.classified_facts = classified

        # Count conversational facts
        report.skipped_conversational = sum(1 for c in classified if not c.falsifiable)

        # 2. Get falsifiable claims (including newly classified)
        falsifiable_claims = self._get_falsifiable_claims(unverified_only=True)
        falsifiable_claims = falsifiable_claims[: self._config.batch_size]

        report.total_claims = len(falsifiable_claims)

        # 3. Verify falsifiable claims
        if falsifiable_claims and self._researcher and self._judge:
            verify_result = await self.verify_claims(
                claims=falsifiable_claims,
                dry_run=dry_run,
            )

            report.verified_claims = verify_result.verified_claims
            report.verified_true = verify_result.verified_true
            report.verified_false = verify_result.verified_false
            report.unverifiable = verify_result.unverifiable
            report.errors.extend(verify_result.errors)

        return report

    def generate_report_summary(self, report: VerificationReport) -> str:
        """
        Generate a human-readable summary of the verification report.

        Args:
            report: The verification report

        Returns:
            Formatted summary string
        """
        status = "DRY RUN" if report.dry_run else "EXECUTED"

        lines = [
            "=" * 60,
            f"FACT VERIFICATION REPORT ({status})",
            "=" * 60,
            f"Time: {report.verified_at.isoformat()}",
            "",
            "CLASSIFICATION:",
            f"  Total classified: {len(report.classified_facts)}",
            f"  Conversational (skipped): {report.skipped_conversational}",
            "",
            "VERIFICATION:",
            f"  Total claims: {report.total_claims}",
            f"  Verified TRUE: {report.verified_true}",
            f"  Verified FALSE: {report.verified_false}",
            f"  Unverifiable: {report.unverifiable}",
            "",
        ]

        if report.verified_claims:
            lines.append("VERIFIED CLAIMS:")
            for claim in report.verified_claims[:10]:
                preview = (
                    claim.original_text[:50] + "..."
                    if len(claim.original_text) > 50
                    else claim.original_text
                )
                lines.append(f"  [{claim.verdict.value}] {preview}")
                if claim.correction:
                    lines.append(f"    Correction: {claim.correction}")
            if len(report.verified_claims) > 10:
                lines.append(f"  ... and {len(report.verified_claims) - 10} more")

        if report.errors:
            lines.append("")
            lines.append("ERRORS:")
            for error in report.errors:
                lines.append(f"  - {error}")

        lines.append("=" * 60)

        return "\n".join(lines)
