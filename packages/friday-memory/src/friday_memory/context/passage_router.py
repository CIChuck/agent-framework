"""
Passage Routing.

Uses a lightweight LLM router to decide whether to include vector passages
in the prompt for the current query. Supports heuristic fallback and
hard guardrails for passage filtering.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Literal, cast

from pydantic import BaseModel, Field

from friday_core.interfaces.llm import LLMClient

logger = logging.getLogger(__name__)


class PassageRoutingDecision(BaseModel):
    """Decision returned by the router."""

    include_passages: bool = Field(default=False)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str = Field(default="")


class PassageRouterConfig(BaseModel):
    """Configuration for passage routing behavior."""

    enabled: bool = Field(default=True)
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    max_tokens: int = Field(default=80, ge=20)
    timeout_seconds: float | None = Field(default=4.0, ge=0.5)
    min_confidence: float = Field(default=0.6, ge=0.0, le=1.0)
    include_on_empty_query: bool = Field(default=False)
    fallback_mode: Literal["heuristic", "include", "exclude"] = Field(
        default="heuristic"
    )
    system_prompt: str | None = Field(default=None)

    # Heuristic fallback keyword set (case-insensitive)
    heuristic_keywords: list[str] = Field(
        default_factory=lambda: [
            "remember",
            "recall",
            "previous",
            "earlier",
            "what did we",
            "where did we",
            "as you said",
            "as you mentioned",
            "source",
            "cite",
            "citation",
            "lookup",
            "look up",
            "search",
            "research",
            "web",
            "document",
            "file",
            "config",
            "transcript",
        ]
    )

    # Guardrails for passage inclusion (applied when router includes passages)
    min_similarity: float = Field(default=0.6, ge=0.0, le=1.0)
    min_similarity_tool_output: float = Field(default=0.75, ge=0.0, le=1.0)
    min_keep_on_empty: int = Field(default=1, ge=0)


class PassageRouter:
    """LLM-based router with heuristic fallback for passage inclusion."""

    DEFAULT_SYSTEM_PROMPT = (
        "You decide if vector-retrieved passages should be included in the prompt.\n"
        "Return JSON ONLY. Do not use code fences. Do not add extra text.\n"
        "Required keys: include_passages (bool), confidence (0-1), reason (string).\n"
        "Include passages when the user needs recall of prior content, sources, files, web info, "
        "or earlier conversation details. Exclude for small talk, meta questions, or self-contained tasks.\n"
        "Be conservative: include only when likely helpful."
    )

    def __init__(self, llm: LLMClient, config: PassageRouterConfig | None = None) -> None:
        self._llm = llm
        self._config = config or PassageRouterConfig()

    @property
    def config(self) -> PassageRouterConfig:
        return self._config

    async def decide(self, query: str) -> PassageRoutingDecision:
        """Return a router decision, with fallback on failure/low confidence."""
        if not self._config.enabled:
            return PassageRoutingDecision(
                include_passages=True,
                confidence=1.0,
                reason="router_disabled",
            )

        if not query or not query.strip():
            return PassageRoutingDecision(
                include_passages=self._config.include_on_empty_query,
                confidence=1.0,
                reason="empty_query",
            )

        system_prompt = self._config.system_prompt or self.DEFAULT_SYSTEM_PROMPT
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query.strip()},
        ]

        try:
            llm = cast(Any, self._llm)
            response = await llm.chat_completion(
                messages=messages,
                temperature=self._config.temperature,
                max_tokens=self._config.max_tokens,
                timeout=self._config.timeout_seconds,
            )
            decision = self._parse_decision_json(response.content or "")
            if not isinstance(decision, PassageRoutingDecision):
                return self._fallback_decision(query, "parse_failed")

            if decision.confidence < self._config.min_confidence:
                return self._fallback_decision(
                    query, f"low_confidence:{decision.confidence:.2f}"
                )

            return decision
        except Exception as e:
            logger.warning(f"Passage router failed: {e}")
            return self._fallback_decision(query, "router_error")

    def filter_passages(
        self, passages: list[dict[str, object]]
    ) -> tuple[list[dict[str, object]], int]:
        """Apply similarity guardrails to passages."""
        if not passages:
            return [], 0

        min_similarity = self._config.min_similarity
        min_tool_similarity = self._config.min_similarity_tool_output

        if min_similarity <= 0 and min_tool_similarity <= 0:
            return list(passages), 0

        filtered: list[dict[str, object]] = []
        excluded = 0
        scored: list[tuple[dict[str, object], float]] = []

        for passage in passages:
            metadata = passage.get("metadata", {}) if isinstance(passage, dict) else {}
            passage_type = metadata.get("type", "")
            similarity = passage.get("similarity")
            inclusion_score = passage.get("inclusion_score")

            score = None
            if isinstance(inclusion_score, (int, float)):
                score = float(inclusion_score)
            elif isinstance(similarity, (int, float)):
                score = float(similarity)
            else:
                score = 0.0

            if passage_type == "tool_output":
                if min_tool_similarity > 0 and score < min_tool_similarity:
                    excluded += 1
                    scored.append((passage, score))
                    continue
            else:
                if min_similarity > 0 and score < min_similarity:
                    excluded += 1
                    scored.append((passage, score))
                    continue

            filtered.append(passage)
            scored.append((passage, score))

        # If all were filtered out but router wanted passages, keep top N by score
        if not filtered and self._config.min_keep_on_empty > 0 and scored:
            scored.sort(key=lambda x: x[1], reverse=True)
            keep_n = min(self._config.min_keep_on_empty, len(scored))
            filtered = [p for p, _ in scored[:keep_n]]
            excluded = len(passages) - len(filtered)

        return filtered, excluded

    def _fallback_decision(self, query: str, reason: str) -> PassageRoutingDecision:
        """Fallback behavior when router is unavailable or uncertain."""
        mode = self._config.fallback_mode
        if mode == "include":
            return PassageRoutingDecision(
                include_passages=True, confidence=0.0, reason=f"fallback:{reason}"
            )
        if mode == "exclude":
            return PassageRoutingDecision(
                include_passages=False, confidence=0.0, reason=f"fallback:{reason}"
            )

        include = self._heuristic_should_include(query)
        return PassageRoutingDecision(
            include_passages=include,
            confidence=0.0,
            reason=f"fallback:{reason}:heuristic",
        )

    def _heuristic_should_include(self, query: str) -> bool:
        q = query.lower()
        return any(keyword in q for keyword in self._config.heuristic_keywords)

    def _parse_decision_json(self, content: str) -> PassageRoutingDecision | None:
        if not content:
            return None
        raw = content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            # Remove leading/trailing fences
            raw = raw.strip("`")
            # If language is specified, drop it
            if raw.startswith("json"):
                raw = raw[4:].lstrip()
        # If still contains fences, try to extract JSON by braces
        if "{" in raw and "}" in raw:
            start = raw.find("{")
            end = raw.rfind("}")
            if start >= 0 and end > start:
                raw = raw[start:end + 1]
        try:
            data = json.loads(raw)
            return PassageRoutingDecision.model_validate(data)
        except Exception:
            return None
