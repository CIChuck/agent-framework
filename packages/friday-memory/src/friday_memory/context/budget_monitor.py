"""
Context Budget Monitor.

Tracks per-turn budget utilization and triggers background compaction
when utilization exceeds configurable thresholds.  Sits between the
``PromptArchitect`` (which measures utilization) and the
``InSessionCompactor`` (which performs compaction).

Signal flow::

    process_turn()
      -> format_prompt()
        -> _validate_prompt_budget()  →  BudgetStatus
      -> monitor.record_turn(budget_status)
      -> if monitor.should_compact():
           asyncio.create_task(compactor.run_compaction())

The monitor maintains a sliding window of recent utilization readings
and classifies whether compaction is needed based on severity,
trend direction, and a configurable cooldown period.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import TYPE_CHECKING, Any

from friday_memory.models.budget import (
    BudgetSeverity,
    BudgetStatus,
    CompactionConfig,
)

if TYPE_CHECKING:
    from friday_core import TelemetryInterface

logger = logging.getLogger(__name__)


class ContextBudgetMonitor:
    """Monitors context budget utilization and signals compaction.

    Maintains a sliding window of recent ``BudgetStatus`` readings
    and determines when background compaction should be triggered
    based on severity thresholds, utilization trend, and a cooldown
    period to prevent thrashing.

    Example::

        monitor = ContextBudgetMonitor(
            config=CompactionConfig(compaction_threshold=0.85),
        )

        # After each turn in process_turn()
        status = assembler.last_budget_status
        monitor.record_turn(status)

        if monitor.should_compact():
            monitor.mark_compaction_started()
            asyncio.create_task(
                compactor.run_compaction(session_id, ...)
            )

    Args:
        config: Compaction configuration with thresholds.
        telemetry: Optional telemetry interface.
    """

    def __init__(
        self,
        config: CompactionConfig | None = None,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        """Initialize the budget monitor.

        Args:
            config: Compaction configuration with thresholds.
            telemetry: Optional telemetry interface for events.
        """
        self._config = config or CompactionConfig()
        self._telemetry = telemetry

        # Sliding window of utilization readings
        self._history: deque[BudgetStatus] = deque(
            maxlen=self._config.trend_window,
        )

        # Compaction state tracking
        self._turns_since_last_compaction: int = 0
        self._total_compactions: int = 0
        self._compaction_in_progress: bool = False

    @property
    def config(self) -> CompactionConfig:
        """Access the compaction configuration."""
        return self._config

    def _emit_event(
        self,
        event_name: str,
        data: dict[str, Any],
    ) -> None:
        """Emit telemetry event if configured.

        Args:
            event_name: The event name.
            data: Event data payload.
        """
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    def record_turn(self, status: BudgetStatus) -> None:
        """Record budget utilization for the current turn.

        Appends the status to the sliding window and increments
        the turns-since-compaction counter.

        Args:
            status: BudgetStatus from
                ``PromptArchitect._validate_prompt_budget()``.
        """
        self._history.append(status)
        self._turns_since_last_compaction += 1

        self._emit_event(
            "budget_utilization_recorded",
            {
                "utilization_pct": status.utilization_pct,
                "severity": status.severity.value,
                "total_tokens": status.total_tokens,
                "available_budget": status.available_budget,
                "overage": status.overage_tokens,
                "trend": self.get_utilization_trend(),
            },
        )

    def should_compact(self) -> bool:
        """Determine whether compaction should be triggered.

        Returns ``True`` when all of these conditions are met:

        1. Compaction is enabled in config.
        2. No compaction is currently in progress.
        3. The cooldown period has elapsed since last compaction.
        4. Current or recent utilization exceeds the threshold
           (WARNING/CRITICAL/OVERAGE severity, or rising trend
           above the compaction threshold).

        Returns:
            True if compaction should be triggered.
        """
        if not self._config.enabled:
            return False

        if self._compaction_in_progress:
            return False

        if (
            self._turns_since_last_compaction
            < self._config.cooldown_turns
        ):
            return False

        if not self._history:
            return False

        latest = self._history[-1]

        # Critical/overage: immediate compaction
        if latest.severity in (
            BudgetSeverity.CRITICAL,
            BudgetSeverity.OVERAGE,
        ):
            logger.warning(
                "Budget %s (%.1f%%), triggering compaction",
                latest.severity.value,
                latest.utilization_pct,
            )
            return True

        # Warning: compaction recommended
        if latest.severity == BudgetSeverity.WARNING:
            logger.info(
                "Budget warning (%.1f%%), "
                "triggering compaction",
                latest.utilization_pct,
            )
            return True

        # Rising trend above threshold
        trend = self.get_utilization_trend()
        threshold_pct = self._config.compaction_threshold * 100
        if trend > 0 and latest.utilization_pct > threshold_pct:
            logger.info(
                "Rising utilization trend "
                "(%.1f%%, trend=+%.1f), "
                "triggering compaction",
                latest.utilization_pct,
                trend,
            )
            return True

        return False

    def get_time_budget_ms(self) -> int:
        """Get the time budget for the current compaction.

        Uses the higher ``critical_max_duration_ms`` for
        CRITICAL or OVERAGE severity, otherwise uses the
        standard ``max_duration_ms``.

        Returns:
            Time budget in milliseconds.
        """
        if not self._history:
            return self._config.max_duration_ms

        latest = self._history[-1]
        if latest.severity in (
            BudgetSeverity.CRITICAL,
            BudgetSeverity.OVERAGE,
        ):
            return self._config.critical_max_duration_ms

        return self._config.max_duration_ms

    def get_budget_context(self) -> dict[str, int | float]:
        """Get current budget context for goal-driven compaction.

        Provides the compactor with the data it needs to calculate
        how many tokens to free: current total tokens, available
        budget, and the target utilization from config.

        Returns:
            Dict with keys:

            - ``current_tokens``: Total tokens in the last prompt.
            - ``available_budget``: Max tokens minus output buffer.
            - ``target_utilization``: Desired post-compaction
              utilization level (0.0-1.0).
        """
        if not self._history:
            return {
                "current_tokens": 0,
                "available_budget": 0,
                "target_utilization": (
                    self._config.target_utilization
                ),
            }

        latest = self._history[-1]
        return {
            "current_tokens": latest.total_tokens,
            "available_budget": latest.available_budget,
            "target_utilization": (
                self._config.target_utilization
            ),
        }

    def mark_compaction_started(self) -> None:
        """Mark that a compaction run is in progress.

        While in-progress, ``should_compact()`` will return
        ``False`` to prevent overlapping runs.
        """
        self._compaction_in_progress = True

    def mark_compaction_complete(self) -> None:
        """Mark that the compaction run has finished.

        Resets the cooldown counter and increments the total
        compaction count.
        """
        self._compaction_in_progress = False
        self._turns_since_last_compaction = 0
        self._total_compactions += 1

    def get_utilization_trend(self) -> float:
        """Calculate the utilization trend over the window.

        Uses a simple linear estimate: ``(last - first) / count``.

        Returns:
            Positive = rising, negative = falling, 0 = stable.
            Value represents average per-turn change in
            utilization percentage points.
        """
        if len(self._history) < 2:
            return 0.0

        values = [s.utilization_pct for s in self._history]
        return (values[-1] - values[0]) / len(values)

    def get_metrics(self) -> dict[str, Any]:
        """Get monitoring metrics for observability.

        Suitable for debug commands (e.g. ``/budget``) or
        telemetry dashboards.

        Returns:
            Dict with current utilization, trend, compaction
            stats, and history window size.
        """
        latest = self._history[-1] if self._history else None
        return {
            "current_utilization_pct": (
                latest.utilization_pct if latest else 0.0
            ),
            "current_severity": (
                latest.severity.value
                if latest
                else BudgetSeverity.NORMAL.value
            ),
            "trend": self.get_utilization_trend(),
            "turns_since_compaction": (
                self._turns_since_last_compaction
            ),
            "total_compactions": self._total_compactions,
            "compaction_in_progress": (
                self._compaction_in_progress
            ),
            "history_size": len(self._history),
        }
