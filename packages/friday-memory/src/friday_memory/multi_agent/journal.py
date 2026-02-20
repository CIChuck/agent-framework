"""
Promotion journal for additive multi-agent memory mode.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from friday_memory.multi_agent.models import (
    PromotionJournalEntry,
    PromotionJournalEvent,
    PromotionJournalState,
)

TERMINAL_STATES = {
    PromotionJournalState.COMMITTED,
    PromotionJournalState.FAILED,
    PromotionJournalState.COMPENSATED,
}


class PromotionJournal:
    """
    Lightweight append-only journal.

    Uses in-memory storage by default, with optional jsonl persistence.
    """

    def __init__(self, path: str | None = None) -> None:
        self._entries: dict[str, PromotionJournalEntry] = {}
        self._events_by_proposal: dict[str, list[PromotionJournalEvent]] = {}
        self._path = Path(path) if path else None

    def append(self, entry: PromotionJournalEntry) -> None:
        self._entries[entry.proposal_id] = entry
        self._record_event(entry)
        self._persist(entry)

    def update_state(
        self,
        proposal_id: str,
        state: PromotionJournalState,
        error: str | None = None,
        *,
        details: dict[str, Any] | None = None,
        promotion_id: str | None = None,
    ) -> PromotionJournalEntry:
        current = self._entries[proposal_id]
        resolved_promotion_id = promotion_id or current.promotion_id
        updated = current.model_copy(
            update={
                "state": state,
                "error": error,
                "promotion_id": resolved_promotion_id,
                "updated_at": datetime.now(timezone.utc),
            },
            deep=True,
        )
        self._entries[proposal_id] = updated
        self._record_event(updated, details=details)
        self._persist(updated)
        return updated

    def get(self, proposal_id: str) -> PromotionJournalEntry | None:
        return self._entries.get(proposal_id)

    def list_non_terminal(self) -> list[PromotionJournalEntry]:
        return [
            entry
            for entry in self._entries.values()
            if entry.state not in TERMINAL_STATES
        ]

    def list_all(self) -> list[PromotionJournalEntry]:
        return sorted(self._entries.values(), key=lambda item: item.created_at)

    def replay(self, proposal_id: str) -> list[PromotionJournalEvent]:
        return list(self._events_by_proposal.get(proposal_id, ()))

    def replay_session(self, session_id: str) -> list[PromotionJournalEvent]:
        events: list[PromotionJournalEvent] = []
        for proposal_events in self._events_by_proposal.values():
            events.extend(
                event for event in proposal_events if event.session_id == session_id
            )
        return sorted(events, key=lambda item: item.recorded_at)

    def list_partial_commit_candidates(self) -> list[PromotionJournalEntry]:
        candidates: list[PromotionJournalEntry] = []
        for proposal_id, entry in self._entries.items():
            if entry.state == PromotionJournalState.COMMITTED:
                continue
            timeline = self._events_by_proposal.get(proposal_id, ())
            touched_shared_store = any(
                event.state
                in (
                    PromotionJournalState.GRAPH_WRITTEN,
                    PromotionJournalState.VECTOR_WRITTEN,
                )
                for event in timeline
            )
            if touched_shared_store:
                candidates.append(entry)
        return sorted(candidates, key=lambda item: item.updated_at)

    def _record_event(
        self,
        entry: PromotionJournalEntry,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        event = PromotionJournalEvent(
            proposal_id=entry.proposal_id,
            state=entry.state,
            session_id=entry.session_id,
            namespace=entry.namespace,
            author_id=entry.author_id,
            correlation_id=entry.correlation_id,
            transcript_entry_id=entry.transcript_entry_id,
            promotion_id=entry.promotion_id,
            error=entry.error,
            details=details or {},
            recorded_at=entry.updated_at,
        )
        self._events_by_proposal.setdefault(entry.proposal_id, []).append(event)

    def _persist(self, entry: PromotionJournalEntry) -> None:
        if self._path is None:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry.model_dump(mode="json")) + "\n")
