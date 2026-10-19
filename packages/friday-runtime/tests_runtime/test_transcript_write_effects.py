"""Direct UI-neutral transcript write-effect behavior and failure ordering."""

from __future__ import annotations

import asyncio
import subprocess
import sys
from collections.abc import Callable
from datetime import datetime

import pytest
from friday_runtime.transcript_write_effects import (
    append_transcript_entry_with_context,
)
from friday_transcript import ContextLogEntry, TranscriptEntry


class FakeWriteStore:
    def __init__(self) -> None:
        self.events: list[str] = []
        self.entries: list[TranscriptEntry] = []
        self.logs: list[ContextLogEntry] = []
        self.append_outcome: bool | BaseException = True
        self.context_outcome: bool | BaseException = True
        self.on_append: Callable[[], None] | None = None

    async def append_entry(self, entry: TranscriptEntry) -> bool:
        self.events.append("append")
        if self.on_append is not None:
            self.on_append()
        if isinstance(self.append_outcome, BaseException):
            raise self.append_outcome
        if self.append_outcome:
            self.entries.append(entry)
        return self.append_outcome

    async def store_context_log(self, context_entry: ContextLogEntry) -> bool:
        self.events.append("context")
        if isinstance(self.context_outcome, BaseException):
            raise self.context_outcome
        if self.context_outcome:
            self.logs.append(context_entry)
        return self.context_outcome


def _entry() -> TranscriptEntry:
    return TranscriptEntry(
        id="entry-1",
        session_id="session",
        turn_number=3,
        user_message="prompt",
        assistant_message="answer",
    )


@pytest.mark.asyncio
async def test_append_without_pending_context_keeps_entry_and_skips_context_store() -> (
    None
):
    store = FakeWriteStore()
    entry = _entry()

    def pending() -> None:
        store.events.append("pending")
        return None

    attempted = await append_transcript_entry_with_context(store, entry, pending)

    assert attempted is False
    assert store.events == ["append", "pending"]
    assert store.entries == [entry]
    assert store.entries[0] is entry
    assert store.logs == []


@pytest.mark.asyncio
@pytest.mark.parametrize("context_result", [True, False])
async def test_context_log_attempt_uses_entry_identity_and_ignores_false_result(
    context_result: bool,
) -> None:
    store = FakeWriteStore()
    store.context_outcome = context_result

    def pending() -> tuple[str, str]:
        store.events.append("pending")
        return ("raw prompt", "raw response")

    attempted = await append_transcript_entry_with_context(store, _entry(), pending)

    assert attempted is True
    assert store.events == ["append", "pending", "context"]
    assert len(store.entries) == 1
    assert len(store.logs) == int(context_result)
    if context_result:
        log = store.logs[0]
        assert (log.session_id, log.turn_number, log.entry_id) == (
            "session",
            3,
            "entry-1",
        )
        assert (log.raw_prompt, log.raw_response) == ("raw prompt", "raw response")
        assert log.id
        assert isinstance(log.captured_at, datetime)


@pytest.mark.asyncio
async def test_false_append_has_exact_error_and_never_reads_pending() -> None:
    store = FakeWriteStore()
    store.append_outcome = False

    def unexpected_pending() -> tuple[str, str]:
        pytest.fail("pending context read after failed append")

    with pytest.raises(RuntimeError) as caught:
        await append_transcript_entry_with_context(store, _entry(), unexpected_pending)

    assert str(caught.value) == "Failed to append transcript entry."
    assert store.events == ["append"]
    assert store.entries == []
    assert store.logs == []


@pytest.mark.asyncio
async def test_append_exception_propagates_without_pending_or_context_effect() -> None:
    store = FakeWriteStore()
    failure = ValueError("append failed")
    store.append_outcome = failure

    def unexpected_pending() -> tuple[str, str]:
        pytest.fail("pending context read after append exception")

    with pytest.raises(ValueError) as caught:
        await append_transcript_entry_with_context(store, _entry(), unexpected_pending)

    assert caught.value is failure
    assert store.events == ["append"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure", [ValueError("context failed"), asyncio.CancelledError()]
)
async def test_context_exception_or_cancellation_propagates_after_entry_append(
    failure: BaseException,
) -> None:
    store = FakeWriteStore()
    store.context_outcome = failure

    with pytest.raises(type(failure)) as caught:
        await append_transcript_entry_with_context(
            store, _entry(), lambda: ("raw prompt", "raw response")
        )

    assert caught.value is failure
    assert store.events == ["append", "context"]
    assert len(store.entries) == 1
    assert store.logs == []


@pytest.mark.asyncio
async def test_pending_context_is_sampled_after_awaited_append() -> None:
    store = FakeWriteStore()
    pending = ("original", "response")

    def update_pending() -> None:
        nonlocal pending
        pending = ("updated", "response")

    store.on_append = update_pending
    attempted = await append_transcript_entry_with_context(
        store, _entry(), lambda: pending
    )

    assert attempted is True
    assert store.logs[0].raw_prompt == "updated"


def test_runtime_write_effect_import_does_not_load_chat_or_cli() -> None:
    code = """
import asyncio
import builtins
import sys
from friday_transcript import TranscriptEntry
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name.startswith(('friday_chat', 'friday_cli')):
        raise RuntimeError(name)
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
from friday_runtime.transcript_write_effects import append_transcript_entry_with_context
class Store:
    async def append_entry(self, entry): return True
    async def store_context_log(self, log): raise RuntimeError('unexpected context')
entry = TranscriptEntry(id='entry', session_id='session', turn_number=1)
assert asyncio.run(append_transcript_entry_with_context(Store(), entry, lambda: None)) is False
assert not any(name.startswith(('friday_chat', 'friday_cli')) for name in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
