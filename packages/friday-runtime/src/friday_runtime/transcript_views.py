"""UI-neutral transcript query views and read-only store contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class TranscriptSessionView:
    """Sanitized persisted session metadata exposed to a frontend."""

    session_id: str
    user_id: str | None
    started_at: datetime
    ended_at: datetime | None
    model_name: str
    total_turns: int
    total_tokens: int
    archived: bool = False


@dataclass(frozen=True)
class TranscriptEntryView:
    """Persisted user/assistant turn exposed to a frontend."""

    entry_id: str
    session_id: str
    turn_number: int
    user_message: str | None
    assistant_message: str | None
    timestamp: datetime
    model_name: str | None = None
    total_tokens: int | None = None
    latency_ms: float | None = None


@dataclass(frozen=True)
class TranscriptContextLogView:
    """Persisted raw prompt/response capture exposed to a frontend."""

    log_id: str
    session_id: str
    turn_number: int
    entry_id: str | None
    raw_prompt: str
    raw_response: str | None
    captured_at: datetime


class TranscriptQueryStore(Protocol):
    """Narrow asynchronous transcript reads for frontend commands."""

    async def query_sessions(
        self,
        *,
        limit: int = 1000,
        include_archived: bool = False,
    ) -> tuple[TranscriptSessionView, ...]:
        """Return persisted sessions newest first."""

    async def query_session(self, session_id: str) -> TranscriptSessionView | None:
        """Return one persisted session by exact identifier."""

    async def query_entries(
        self,
        session_id: str,
    ) -> tuple[TranscriptEntryView, ...]:
        """Return all persisted entries in chronological turn order."""

    async def query_context_logs(
        self,
        session_id: str,
    ) -> tuple[TranscriptContextLogView, ...]:
        """Return persisted context logs in chronological turn order."""


__all__ = [
    "TranscriptContextLogView",
    "TranscriptEntryView",
    "TranscriptQueryStore",
    "TranscriptSessionView",
]
