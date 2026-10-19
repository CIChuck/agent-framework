"""UI-neutral transcript entry and optional raw-context write effects."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from friday_transcript import ContextLogEntry, TranscriptEntry

__all__ = ["TranscriptWriteStore", "append_transcript_entry_with_context"]


class TranscriptWriteStore(Protocol):
    """The two append operations needed for one interaction write."""

    async def append_entry(self, entry: TranscriptEntry) -> bool: ...

    async def store_context_log(self, context_entry: ContextLogEntry) -> bool: ...


async def append_transcript_entry_with_context(
    store: TranscriptWriteStore,
    entry: TranscriptEntry,
    pending_context: Callable[[], tuple[str, str] | None],
) -> bool:
    """Append an entry, then attempt the current pending raw-context write.

    The return value reports whether the context-log call was attempted. The
    store's Boolean result for that second call is deliberately ignored to
    preserve the established caller behavior.
    """
    if not await store.append_entry(entry):
        raise RuntimeError("Failed to append transcript entry.")

    context = pending_context()
    if context is None:
        return False

    prompt, raw_response = context
    await store.store_context_log(
        ContextLogEntry(
            session_id=entry.session_id,
            turn_number=entry.turn_number,
            entry_id=entry.id,
            raw_prompt=prompt,
            raw_response=raw_response,
        )
    )
    return True
