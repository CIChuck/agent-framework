"""
Budget monitoring and compaction data models.

Provides data structures for tracking context budget utilization,
classifying severity, configuring in-session compaction, and
reporting compaction results.

Used by:
- PromptArchitect._validate_prompt_budget() → BudgetStatus
- ContextBudgetMonitor → tracks BudgetStatus history
- InSessionCompactor → uses CompactionConfig, produces CompactionResult
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class BudgetSeverity(str, Enum):
    """Budget utilization severity levels.

    Thresholds:
    - NORMAL: < 70% utilization
    - ELEVATED: 70-85% — monitoring only, no action
    - WARNING: 85-95% — compaction recommended
    - CRITICAL: > 95% — compaction urgent (higher time budget)
    - OVERAGE: > 100% — over budget, immediate compaction
    """

    NORMAL = "normal"
    ELEVATED = "elevated"
    WARNING = "warning"
    CRITICAL = "critical"
    OVERAGE = "overage"

    @classmethod
    def from_utilization(cls, pct: float) -> BudgetSeverity:
        """Classify severity from utilization percentage.

        Args:
            pct: Utilization as percentage (0.0-200.0+).

        Returns:
            The appropriate BudgetSeverity level.
        """
        if pct > 100.0:
            return cls.OVERAGE
        if pct > 95.0:
            return cls.CRITICAL
        if pct > 85.0:
            return cls.WARNING
        if pct > 70.0:
            return cls.ELEVATED
        return cls.NORMAL


class BudgetStatus(BaseModel):
    """Budget utilization status returned by _validate_prompt_budget().

    Replaces the void return of the previous implementation with
    actionable data that the ContextBudgetMonitor can consume to
    decide whether in-session compaction is needed.

    Attributes:
        total_tokens: Total tokens in the formatted prompt.
        available_budget: Max tokens minus output buffer.
        utilization_pct: Usage as percentage (0.0-200.0+).
        overage_tokens: Tokens over budget (0 if under).
        severity: Classified severity level.
        message_tokens: Tokens from message content only.
        tool_tokens: Tokens from tool definitions only.
        timestamp: When this status was recorded.
    """

    total_tokens: int = Field(
        ...,
        description="Total tokens in formatted prompt",
    )
    available_budget: int = Field(
        ...,
        description="Max tokens minus output buffer",
    )
    utilization_pct: float = Field(
        ...,
        ge=0.0,
        description="Usage as percentage (0.0-200.0+)",
    )
    overage_tokens: int = Field(
        default=0,
        ge=0,
        description="Tokens over budget (0 if under)",
    )
    severity: BudgetSeverity = Field(
        default=BudgetSeverity.NORMAL,
        description="Classified severity level",
    )
    message_tokens: int = Field(
        default=0,
        description="Tokens from message content",
    )
    tool_tokens: int = Field(
        default=0,
        description="Tokens from tool definitions",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
    )


class CompactionConfig(BaseModel):
    """Configuration for goal-driven in-session compaction.

    Controls when and how background compaction is triggered
    to reduce context size. All thresholds and limits are
    configurable via config.yaml under ``memory.compaction``.

    The compactor uses a **goal-driven** approach: it calculates
    how many tokens need to be freed to bring utilization down
    to ``target_utilization``, then loops through summarization
    batches until the goal is met. Time budgets serve as safety
    nets, not primary stopping conditions.

    Attributes:
        enabled: Enable in-session compaction.
        compaction_threshold: Utilization % that triggers compaction.
        critical_threshold: Utilization % classified as critical.
        target_utilization: Target utilization after compaction.
            Compactor loops until utilization reaches this level.
        cooldown_turns: Min turns between compaction runs.
        max_duration_ms: Time budget per normal compaction (ms).
            Acts as a safety net; primary stop is goal achievement.
        critical_max_duration_ms: Time budget for critical runs (ms).
            Acts as a safety net; primary stop is goal achievement.
        min_turns_to_summarize: Min unconsolidated turns before
            summarization.
        max_turns_per_summary: Max turns per summary batch.
        insight_dedup_enabled: Enable insight deduplication.
        insight_similarity_threshold: Similarity threshold for
            merging duplicate insights.
        max_insights_to_check: Max insights to check per run.
        trend_window: Recent turns for utilization trend tracking.
    """

    enabled: bool = Field(
        default=True,
        description="Enable in-session compaction",
    )
    compaction_threshold: float = Field(
        default=0.85,
        ge=0.5,
        le=1.0,
        description=(
            "Utilization fraction that triggers compaction"
        ),
    )
    critical_threshold: float = Field(
        default=0.95,
        ge=0.5,
        le=1.0,
        description=(
            "Utilization fraction classified as critical"
        ),
    )
    target_utilization: float = Field(
        default=0.70,
        ge=0.30,
        le=0.95,
        description=(
            "Target utilization after compaction. "
            "Compactor loops until utilization is at "
            "or below this level."
        ),
    )
    cooldown_turns: int = Field(
        default=3,
        ge=1,
        description=(
            "Minimum turns between compaction runs"
        ),
    )
    max_duration_ms: int = Field(
        default=15000,
        ge=100,
        le=120000,
        description=(
            "Time budget per normal compaction run (ms). "
            "Acts as a safety net; primary stop condition "
            "is goal achievement."
        ),
    )
    critical_max_duration_ms: int = Field(
        default=45000,
        ge=500,
        le=180000,
        description=(
            "Time budget for critical compaction (ms). "
            "Acts as a safety net; primary stop condition "
            "is goal achievement."
        ),
    )
    min_turns_to_summarize: int = Field(
        default=5,
        ge=2,
        description=(
            "Min unconsolidated turns before summarization"
        ),
    )
    max_turns_per_summary: int = Field(
        default=8,
        ge=2,
        description="Max turns per summary batch",
    )
    compaction_recency_window: int = Field(
        default=4,
        ge=2,
        le=50,
        description=(
            "Number of most-recent turns to protect from "
            "compaction. These turns are always kept as raw "
            "history for conversational continuity."
        ),
    )
    insight_dedup_enabled: bool = Field(
        default=True,
        description="Enable insight dedup during compaction",
    )
    insight_similarity_threshold: float = Field(
        default=0.90,
        ge=0.5,
        le=1.0,
        description="Similarity threshold for merging insights",
    )
    max_insights_to_check: int = Field(
        default=50,
        ge=5,
        description="Max insights to check per compaction run",
    )
    trend_window: int = Field(
        default=10,
        ge=3,
        le=50,
        description=(
            "Recent turns for utilization trend tracking"
        ),
    )


@dataclass
class CompactionResult:
    """Result of a goal-driven in-session compaction run.

    Tracks statistics from all three compaction phases
    (turn summarization, insight dedup, memory promotion)
    plus timing, goal achievement, and error information.

    Attributes:
        started_at: When the compaction started.
        completed_at: When the compaction finished.
        duration_ms: Total duration in milliseconds.
        turns_summarized: Number of turns summarized.
        tokens_saved_from_summarization: Tokens saved by
            compressing turns into summaries.
        tokens_target: How many tokens the compactor aimed
            to free to reach the target utilization.
        target_met: Whether token savings met or exceeded
            the target (savings >= tokens_target).
        insights_deduplicated: Number of duplicate insights
            marked as superseded.
        memories_promoted: Short-term memories promoted to
            long-term.
        time_budget_exhausted: Whether time budget ran out.
        trigger_reason: Why compaction was triggered.
        errors: List of error messages from failed operations.
    """

    started_at: datetime = field(
        default_factory=datetime.now,
    )
    completed_at: datetime | None = None
    duration_ms: float = 0.0

    # Turn summarization
    turns_summarized: int = 0
    tokens_saved_from_summarization: int = 0

    # Goal tracking
    tokens_target: int = 0
    target_met: bool = False

    # Insight deduplication
    insights_deduplicated: int = 0

    # Promotions
    memories_promoted: int = 0

    # Time budget
    time_budget_exhausted: bool = False
    trigger_reason: str = ""

    # Errors
    errors: list[str] = field(default_factory=list)

    def complete(self) -> None:
        """Mark compaction as complete and record duration."""
        self.completed_at = datetime.now()
        self.duration_ms = (
            (self.completed_at - self.started_at)
            .total_seconds()
            * 1000
        )
