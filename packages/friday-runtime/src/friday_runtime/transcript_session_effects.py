"""UI-neutral transcript session get-or-create effect."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from friday_transcript import TranscriptSession

__all__ = ["TranscriptSessionStore", "ensure_transcript_session"]


class TranscriptSessionStore(Protocol):
    """The two session operations required before recording an interaction."""

    async def get_session(self, session_id: str) -> TranscriptSession | None: ...

    async def create_session(self, session: TranscriptSession) -> bool: ...


async def ensure_transcript_session(
    store: TranscriptSessionStore,
    session_id: str,
    session_factory: Callable[[], TranscriptSession],
) -> None:
    """Create a missing session while preserving the store's existing result policy."""
    if await store.get_session(session_id) is not None:
        return
    await store.create_session(session_factory())
