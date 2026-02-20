"""
Operational observability helpers for multi-agent promotion workflows.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from friday_memory.multi_agent.journal import PromotionJournal
from friday_memory.multi_agent.models import PromotionJournalState


def build_promotion_ops_snapshot(
    journal: PromotionJournal,
    *,
    backlog_threshold: int = 10,
    stale_pending_after_seconds: int = 300,
    failure_rate_threshold: float = 0.2,
) -> dict:
    """
    Build bounded operational metrics and warning-level alerts.

    Alerts are advisory and can be wired into telemetry backends.
    """
    entries = journal.list_all()
    totals = {
        "pending": 0,
        "graph_written": 0,
        "vector_written": 0,
        "committed": 0,
        "failed": 0,
        "compensated": 0,
    }
    for entry in entries:
        totals[entry.state.value] += 1

    backlog = totals["pending"] + totals["graph_written"] + totals["vector_written"]
    completed = totals["committed"] + totals["failed"] + totals["compensated"]
    failure_rate = (totals["failed"] / completed) if completed > 0 else 0.0
    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(seconds=stale_pending_after_seconds)
    stale_backlog = [
        entry
        for entry in entries
        if entry.state
        in {
            PromotionJournalState.PENDING,
            PromotionJournalState.GRAPH_WRITTEN,
            PromotionJournalState.VECTOR_WRITTEN,
        }
        and entry.updated_at < stale_cutoff
    ]
    partial_commit_candidates = journal.list_partial_commit_candidates()

    alerts: list[dict[str, str | int | float]] = []
    if backlog >= backlog_threshold:
        alerts.append(
            {
                "severity": "warning",
                "code": "recovery_backlog_high",
                "message": "Promotion backlog exceeds threshold",
                "value": backlog,
            }
        )
    if stale_backlog:
        alerts.append(
            {
                "severity": "warning",
                "code": "degraded_arbitrator_flow",
                "message": "Backlog contains stale pending promotions",
                "value": len(stale_backlog),
            }
        )
    if failure_rate >= failure_rate_threshold:
        alerts.append(
            {
                "severity": "warning",
                "code": "promotion_failure_rate_high",
                "message": "Promotion failure rate exceeds threshold",
                "value": round(failure_rate, 4),
            }
        )

    return {
        "metrics": {
            "proposal_volume": len(entries),
            "promotion_backlog": backlog,
            "recovery_backlog": len(stale_backlog),
            "conflict_rate": failure_rate,
            "compensation_events": totals["compensated"],
            "partial_commit_candidates": len(partial_commit_candidates),
        },
        "alerts": alerts,
    }
