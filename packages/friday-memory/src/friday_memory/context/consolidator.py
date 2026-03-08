# mypy: ignore-errors
"""
Memory Consolidator (The Synthesizer).
Handles deduplication, summarization, and drift management of long-term memory.

Ref: Batch 2a Specification, Section 4

Consolidation Logic:
1. Deduplication: Merging duplicate entities into single Graph Nodes
2. Summarization: Compressing conversation history into episodic summaries
3. Conflict Resolution: Handling contradictory facts with lineage tracking
"""

import logging
from typing import TYPE_CHECKING, Any

from friday_core import TelemetryInterface

from friday_memory.context.token_estimator import build_token_estimator
from friday_memory.controller import MemoryController
from friday_memory.models import (
    ConflictResolutionResponse,
    ConsolidationReport,
    ProvenanceMetadata,
    SummarizationResponse,
)

if TYPE_CHECKING:
    from friday_core.interfaces import LLMClient


logger = logging.getLogger(__name__)


# Summarization prompt template
SUMMARIZATION_PROMPT = """Summarize the following conversation turns into a concise episodic memory.

Conversation Turns:
{turns}

Create a summary that:
1. Captures the key topics discussed
2. Notes any decisions or conclusions reached
3. Highlights important facts or preferences revealed
4. Preserves the chronological flow of events

Keep the summary under 200 words. Focus on information that would be useful for future context.

Respond in JSON format:
{{
    "summary": "concise summary text",
    "key_topics": ["topic1", "topic2"],
    "decisions": ["decision1", "decision2"],
    "tokens_original": estimated_original_token_count,
    "tokens_compressed": estimated_compressed_token_count
}}
"""  # noqa: E501

# Conflict resolution prompt template
CONFLICT_RESOLUTION_PROMPT = """Analyze the following potentially conflicting facts and determine the current truth.

Facts (ordered by time, oldest first):
{facts}

Determine:
1. Whether there is an actual conflict (vs. complementary information)
2. If conflicting, which value should be considered current
3. How to preserve the historical record

Respond in JSON format:
{{
    "has_conflict": true/false,
    "resolution": "explanation of resolution",
    "current_value": "the current/latest valid value",
    "historical_note": "note about value changes if applicable"
}}
"""  # noqa: E501


class MemoryConsolidator:
    """
    The Synthesizer - consolidates fragmented memories.

    Prevents Context Fragmentation by merging short-term observations
    into cohesive long-term facts.

    Operations:
    - Deduplication: Merge duplicate entities
    - Summarization: Compress conversation history
    - Conflict Resolution: Handle contradictory facts
    """

    def __init__(
        self,
        memory_controller: MemoryController,
        llm_client: "LLMClient",
        min_turns_to_consolidate: int = 5,
        max_turns_per_summary: int = 10,
        telemetry: TelemetryInterface | None = None,
        token_estimator_config: dict[str, Any] | None = None,
        model_name: str = "gpt-4",
    ) -> None:
        """
        Initialize the Memory Consolidator.

        Args:
            memory_controller: The memory controller facade
            llm_client: LLMClient for summarization and conflict resolution
            min_turns_to_consolidate: Minimum turns before consolidation
            max_turns_per_summary: Maximum turns per summary block
            telemetry: Optional telemetry recorder
            token_estimator_config: Optional token estimator configuration
            model_name: Model name for token counting
        """
        self._memory = memory_controller
        self._llm_client = llm_client
        self._min_turns = min_turns_to_consolidate
        self._max_turns = max_turns_per_summary
        self._telemetry = telemetry

        # Token counting now uses a configurable estimator (approx by default).
        self._token_estimator = build_token_estimator(
            token_estimator_config, model_name
        )

    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    def _count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        # Swapped from tiktoken to estimator to reduce CPU latency.
        return self._token_estimator.count(text)

    async def consolidate(self, session_id: str) -> ConsolidationReport:
        """
        Run the full consolidation cycle for a session.

        Steps:
        1. Fetch unconsolidated turns
        2. Deduplicate graph entities
        3. Summarize conversation history
        4. Mark turns as consolidated

        Args:
            session_id: The session to consolidate

        Returns:
            ConsolidationReport with statistics
        """
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("memory_consolidation")

        errors: list[str] = []
        nodes_created = 0
        nodes_merged = 0
        conflicts_resolved = 0
        tokens_condensed = 0

        try:
            # 1. Fetch unconsolidated turns
            turns = await self._memory.fetch_unconsolidated_events(session_id)

            if len(turns) < self._min_turns:
                logger.info(
                    f"Not enough turns to consolidate: {len(turns)} < {self._min_turns}"
                )
                return ConsolidationReport(
                    session_id=session_id,
                    nodes_created=0,
                    nodes_merged=0,
                    conflicts_resolved=0,
                    tokens_condensed=0,
                    errors=[],
                )

            # 2. Deduplicate graph entities
            try:
                merge_stats = await self._deduplicate_entities()
                nodes_merged = merge_stats.get("merged", 0)
            except Exception as e:
                logger.error(f"Deduplication failed: {e}")
                errors.append(f"Deduplication failed: {e}")

            # 3. Summarize conversation history
            try:
                summary_stats = await self._summarize_turns(session_id, turns)
                nodes_created = summary_stats.get("summaries_created", 0)
                tokens_condensed = summary_stats.get("tokens_saved", 0)
            except Exception as e:
                logger.error(f"Summarization failed: {e}")
                errors.append(f"Summarization failed: {e}")

            # 4. Mark turns as consolidated
            turn_ids = [turn.id for turn in turns]
            await self._memory.mark_events_consolidated(turn_ids)

            self._emit_event(
                "consolidation_completed",
                {
                    "session_id": session_id,
                    "turns_processed": len(turns),
                    "nodes_merged": nodes_merged,
                    "tokens_condensed": tokens_condensed,
                },
            )

            return ConsolidationReport(
                session_id=session_id,
                nodes_created=nodes_created,
                nodes_merged=nodes_merged,
                conflicts_resolved=conflicts_resolved,
                tokens_condensed=tokens_condensed,
                errors=errors,
            )

        except Exception as e:
            logger.error(f"Consolidation failed: {e}")
            return ConsolidationReport(
                session_id=session_id,
                nodes_created=nodes_created,
                nodes_merged=nodes_merged,
                conflicts_resolved=conflicts_resolved,
                tokens_condensed=tokens_condensed,
                errors=[str(e)],
            )
        finally:
            if span_id:
                self._telemetry.end_span(span_id)

    async def _deduplicate_entities(self) -> dict[str, int]:
        """
        Find and merge duplicate entities in the graph.

        Uses fuzzy matching to identify potential duplicates.

        Returns:
            Statistics about merged entities
        """
        stats = {"merged": 0, "candidates_found": 0}

        # Get all nodes from graph
        all_nodes = await self._memory.graph.get_all_nodes()

        if len(all_nodes) < 2:
            return stats

        # Build label -> nodes mapping
        label_map: dict[str, list] = {}
        for node in all_nodes:
            label_lower = node.label.lower()
            if label_lower not in label_map:
                label_map[label_lower] = []
            label_map[label_lower].append(node)

        # Find exact duplicates first
        for _label, nodes in label_map.items():
            if len(nodes) > 1:
                stats["candidates_found"] += len(nodes) - 1
                # Keep the oldest (first) node, merge others into it
                primary = nodes[0]
                for secondary in nodes[1:]:
                    try:
                        await self._memory.merge_identities(primary.id, secondary.id)
                        stats["merged"] += 1
                    except Exception as e:
                        logger.warning(
                            f"Failed to merge {secondary.id} into {primary.id}: {e}"
                        )

        # Fuzzy matching for near-duplicates
        labels = list(label_map.keys())
        for i, label1 in enumerate(labels):
            for label2 in labels[i + 1 :]:
                # Simple similarity check
                if self._is_similar(label1, label2):
                    nodes1 = label_map[label1]
                    nodes2 = label_map[label2]
                    if nodes1 and nodes2:
                        stats["candidates_found"] += 1
                        try:
                            await self._memory.merge_identities(
                                nodes1[0].id, nodes2[0].id
                            )
                            stats["merged"] += 1
                        except Exception as e:
                            logger.warning(f"Failed fuzzy merge: {e}")

        return stats

    def _is_similar(self, s1: str, s2: str, threshold: float = 0.85) -> bool:
        """Check if two strings are similar enough to be duplicates."""
        from difflib import SequenceMatcher

        return SequenceMatcher(None, s1, s2).ratio() >= threshold

    async def _summarize_turns(self, session_id: str, turns: list) -> dict[str, int]:
        """
        Summarize conversation turns into episodic memory blocks.

        Args:
            session_id: The session ID
            turns: List of turns to summarize

        Returns:
            Statistics about summaries created
        """
        stats = {"summaries_created": 0, "tokens_saved": 0}

        # Process in batches
        for i in range(0, len(turns), self._max_turns):
            batch = turns[i : i + self._max_turns]

            if len(batch) < 2:
                continue

            # Format turns for summarization
            turns_text = self._format_turns_for_summary(batch)
            original_tokens = self._count_tokens(turns_text)

            try:
                # Call LLM for summarization
                response = await self._llm_client.chat_completion(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a precise conversation summarizer.",
                        },
                        {
                            "role": "user",
                            "content": SUMMARIZATION_PROMPT.format(turns=turns_text),
                        },
                    ],
                    response_model=SummarizationResponse,
                    temperature=0.0,
                )

                # Get the parsed Pydantic model
                result = response._parsed_model
                if result is None:
                    logger.error("Failed to parse summarization response")
                    continue

                summary_text = result.summary
                summary_tokens = self._count_tokens(summary_text)

                # Store summary as an insight
                provenance = ProvenanceMetadata(
                    source_id=session_id,
                    source_type="consolidation_summary",
                    confidence=0.9,
                    author_id="memory_consolidator",
                )

                # Store the summary with type="summary" metadata for priming queries
                summary_metadata = {"type": "summary"}
                await self._memory.store_insight(
                    f"[Session Summary] {summary_text}",
                    provenance,
                    summary_metadata,
                )

                stats["summaries_created"] += 1
                stats["tokens_saved"] += max(0, original_tokens - summary_tokens)

            except Exception as e:
                logger.error(f"Failed to summarize batch: {e}")

        return stats

    def _format_turns_for_summary(self, turns: list) -> str:
        """Format turns into a string for summarization."""
        formatted = []
        for i, turn in enumerate(turns, 1):
            user_msg = getattr(turn, "user_message", "") or ""
            assistant_msg = getattr(turn, "assistant_response", "") or ""
            timestamp = getattr(turn, "timestamp", None)
            ts_str = timestamp.isoformat() if timestamp else "unknown"

            formatted.append(f"Turn {i} ({ts_str}):")
            if user_msg:
                formatted.append(f"  User: {user_msg[:500]}")  # Truncate long messages
            if assistant_msg:
                formatted.append(f"  Assistant: {assistant_msg[:500]}")
            formatted.append("")

        return "\n".join(formatted)

    async def resolve_conflict(self, facts: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Resolve conflicting facts using LLM reasoning.

        Args:
            facts: List of potentially conflicting facts with timestamps

        Returns:
            Resolution result with current value and historical note
        """
        if not facts:
            return {"has_conflict": False, "resolution": "No facts to resolve"}

        try:
            facts_text = "\n".join(
                f"- [{f.get('timestamp', 'unknown')}] {f.get('text', '')}"
                for f in facts
            )

            response = await self._llm_client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise conflict resolution system.",
                    },
                    {
                        "role": "user",
                        "content": CONFLICT_RESOLUTION_PROMPT.format(facts=facts_text),
                    },
                ],
                response_model=ConflictResolutionResponse,
                temperature=0.0,
            )

            # Get the parsed Pydantic model
            result = response._parsed_model
            if result is None:
                raise ValueError("Failed to parse conflict resolution response")

            return {
                "has_conflict": result.has_conflict,
                "resolution": result.resolution,
                "current_value": result.current_value,
                "historical_note": result.historical_note,
            }

        except Exception as e:
            logger.error(f"Conflict resolution failed: {e}")
            return {
                "has_conflict": True,
                "resolution": f"Resolution failed: {e}",
                "current_value": facts[-1].get("text", "") if facts else "",
            }

    async def get_recent_memories(self, session_id: str, limit: int = 5) -> list[str]:
        """
        Get recent memories for the transparency block.

        Returns a list of strings describing recent auto-archived memories.

        Args:
            session_id: The session ID
            limit: Maximum number of recent memories

        Returns:
            List of memory description strings
        """
        recent: list[str] = []

        # Get recent vector store additions
        try:
            results = await self._memory.vector.query(
                f"session:{session_id}",
                n_results=limit,
                where={"type": "insight"},
            )
            for result in results:
                text = result.get("text", "")
                if text:
                    # Truncate long texts
                    if len(text) > 100:
                        text = text[:97] + "..."
                    recent.append(f"Archived: {text}")
        except Exception as e:
            logger.warning(f"Failed to fetch recent memories: {e}")

        return recent[:limit]
