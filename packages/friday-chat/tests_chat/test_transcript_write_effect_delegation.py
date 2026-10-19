"""Chat keeps its transcript policy while delegating neutral write effects."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from friday_chat import adapters as chat_adapters
from friday_chat.adapters import FrameworkTranscriptAdapter
from friday_chat.config import FridayChatConfig
from friday_chat.tools.schemas import ToolCallRecord
from friday_chat.turns.models import InteractionTurn, TurnMetrics
from friday_core.mcp import MCPToolCallProvenance, MCPToolMetadata
from friday_runtime.transcript_write_effects import (
    TranscriptWriteStore,
    append_transcript_entry_with_context,
)
from friday_transcript import (
    ContextLogEntry,
    SQLiteTranscriptStore,
    TranscriptEntry,
    TranscriptSession,
)


def _adapter(tmp_path: Path) -> FrameworkTranscriptAdapter:
    return FrameworkTranscriptAdapter(
        store=SQLiteTranscriptStore(tmp_path / "transcript.sqlite"),
        config=FridayChatConfig.model_validate(
            {"llm": {"model": "fake/test"}, "chat": {"user_name": "Chuck"}}
        ),
        session_id="session",
    )


def _turn(identifier: str, *calls: ToolCallRecord) -> InteractionTurn:
    return InteractionTurn(
        identifier,
        "user prompt",
        "assistant answer",
        "raw prompt",
        "context",
        ("memory",),
        TurnMetrics(0, 0, 0, 0.125),
        raw_prompt_captured=True,
        tool_calls=calls,
    )


def _facts() -> MCPToolCallProvenance:
    result = "safe result"
    return MCPToolCallProvenance(
        tool=MCPToolMetadata(
            canonical_name="mcp_peer_read",
            server_name="peer",
            original_name="read",
            transport="stdio",
            trust_level="local",
        ),
        call_id="mcp-call",
        status="succeeded",
        output_sanitization_state="unchanged",
        model_result_size_bytes=len(result.encode("utf-8")),
        transcript_correlation_id="entry-1",
    )


@pytest.mark.asyncio
async def test_chat_delegates_after_session_and_entry_construction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    store = adapter.store
    events: list[str] = []
    original_get = store.get_session
    original_create = store.create_session
    original_count = store.count_entries
    original_append = store.append_entry
    original_context = store.store_context_log
    original_effect = append_transcript_entry_with_context

    async def get_session(session_id: str) -> TranscriptSession | None:
        events.append("get_session")
        return await original_get(session_id)

    async def create_session(session: TranscriptSession) -> bool:
        events.append("create_session")
        created: bool = await original_create(session)
        return created

    async def count_entries(session_id: str) -> int:
        events.append("count_entries")
        count: int = await original_count(session_id)
        return count

    async def append(entry: TranscriptEntry) -> bool:
        events.append("append")
        appended: bool = await original_append(entry)
        return appended

    async def context(log: ContextLogEntry) -> bool:
        events.append("context")
        stored: bool = await original_context(log)
        return stored

    async def delegated(
        target: TranscriptWriteStore,
        entry: TranscriptEntry,
        pending: Callable[[], tuple[str, str] | None],
    ) -> bool:
        events.append("delegate")
        assert target is store
        assert entry.id == "entry-1"
        assert entry.turn_number == 1
        assert entry.metadata == {
            "raw_prompt_captured": True,
            "memory_snippets": ["memory"],
        }
        result = await original_effect(target, entry, pending)
        events.append("delegate_done")
        return result

    monkeypatch.setattr(store, "get_session", get_session)
    monkeypatch.setattr(store, "create_session", create_session)
    monkeypatch.setattr(store, "count_entries", count_entries)
    monkeypatch.setattr(store, "append_entry", append)
    monkeypatch.setattr(store, "store_context_log", context)
    monkeypatch.setattr(
        chat_adapters, "append_transcript_entry_with_context", delegated
    )

    await adapter.record_context_log("raw prompt", "raw response")
    await adapter.record_interaction(
        _turn("entry-1", ToolCallRecord("echo", {"value": 1}, "done"))
    )

    assert events == [
        "get_session",
        "create_session",
        "count_entries",
        "delegate",
        "append",
        "context",
        "delegate_done",
    ]
    entry = await store.get_entry("entry-1")
    assert entry is not None
    assert (entry.user_message, entry.assistant_message) == (
        "user prompt",
        "assistant answer",
    )
    assert (entry.model_name, entry.latency_ms, entry.temperature) == (
        "fake/test",
        125,
        adapter.config.llm.temperature,
    )
    assert entry.tool_calls[0].id == "entry-1:0:echo"
    assert entry.tool_results[0].output == "done"
    logs = await store.get_context_log_for_session("session")
    assert len(logs) == 1
    assert (logs[0].entry_id, logs[0].turn_number) == ("entry-1", 1)
    assert (logs[0].raw_prompt, logs[0].raw_response) == ("raw prompt", "raw response")
    assert adapter._pending_context_log is None
    assert adapter._turn_number == 1


@pytest.mark.asyncio
async def test_no_pending_context_skips_context_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)

    async def unexpected_context(log: ContextLogEntry) -> bool:
        pytest.fail("context store called without pending context")

    monkeypatch.setattr(adapter.store, "store_context_log", unexpected_context)
    await adapter.record_interaction(_turn("entry-1"))

    assert await adapter.store.get_entry("entry-1") is not None
    assert adapter._turn_number == 1


@pytest.mark.asyncio
async def test_false_context_result_still_clears_pending_and_advances(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    await adapter.record_context_log("pending", "response")

    async def false_context(log: ContextLogEntry) -> bool:
        return False

    monkeypatch.setattr(adapter.store, "store_context_log", false_context)
    await adapter.record_interaction(_turn("entry-1"))

    assert await adapter.store.get_entry("entry-1") is not None
    assert await adapter.store.get_context_log_for_session("session") == []
    assert adapter._pending_context_log is None
    assert adapter._turn_number == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("raises", [False, True])
async def test_failed_append_preserves_pending_and_cached_count(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, raises: bool
) -> None:
    adapter = _adapter(tmp_path)
    await adapter.record_context_log("pending", "response")
    failure = ValueError("append exception")

    async def failed_append(entry: TranscriptEntry) -> bool:
        if raises:
            raise failure
        return False

    monkeypatch.setattr(adapter.store, "append_entry", failed_append)
    if raises:
        with pytest.raises(ValueError) as caught_exception:
            await adapter.record_interaction(_turn("entry-1"))
        assert caught_exception.value is failure
    else:
        with pytest.raises(RuntimeError) as caught_runtime:
            await adapter.record_interaction(_turn("entry-1"))
        assert str(caught_runtime.value) == "Failed to append transcript entry."

    assert await adapter.store.get_session("session") is not None
    assert await adapter.store.get_entry("entry-1") is None
    assert adapter._pending_context_log == ("pending", "response")
    assert adapter._turn_number == 0


@pytest.mark.asyncio
async def test_context_exception_keeps_partial_entry_and_pending_for_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    await adapter.record_context_log("pending", "response")
    failure = ValueError("context exception")

    async def failed_context(log: ContextLogEntry) -> bool:
        raise failure

    monkeypatch.setattr(adapter.store, "store_context_log", failed_context)
    with pytest.raises(ValueError) as caught:
        await adapter.record_interaction(_turn("entry-1"))

    assert caught.value is failure
    assert await adapter.store.get_entry("entry-1") is not None
    assert await adapter.store.get_context_log_for_session("session") == []
    assert adapter._pending_context_log == ("pending", "response")
    assert adapter._turn_number == 0

    with pytest.raises(RuntimeError, match="Failed to append transcript entry"):
        await adapter.record_interaction(_turn("entry-1"))
    assert adapter._pending_context_log == ("pending", "response")


@pytest.mark.asyncio
async def test_chat_uses_context_set_during_append_await(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    await adapter.record_context_log("original", "response")
    original_append = adapter.store.append_entry

    async def append_and_update(entry: TranscriptEntry) -> bool:
        result: bool = await original_append(entry)
        await adapter.record_context_log("updated", "response")
        return result

    monkeypatch.setattr(adapter.store, "append_entry", append_and_update)
    await adapter.record_interaction(_turn("entry-1"))

    logs = await adapter.store.get_context_log_for_session("session")
    assert len(logs) == 1
    assert logs[0].raw_prompt == "updated"
    assert adapter._pending_context_log is None


@pytest.mark.asyncio
async def test_unsafe_mcp_preflight_never_delegates_to_write_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    await adapter.record_context_log("pending", "response")

    async def unexpected_effect(*args: object, **kwargs: object) -> bool:
        pytest.fail("unsafe MCP record reached write effect")

    async def unexpected_session(session_id: str) -> TranscriptSession | None:
        pytest.fail("unsafe MCP record reached transcript store")

    monkeypatch.setattr(
        chat_adapters, "append_transcript_entry_with_context", unexpected_effect
    )
    monkeypatch.setattr(adapter.store, "get_session", unexpected_session)
    unsafe = ToolCallRecord(
        "mcp_peer_read", {"raw": "unsafe"}, "safe result", "mcp-call", _facts()
    )
    with pytest.raises(ValueError) as caught:
        await adapter.record_interaction(_turn("entry-1", unsafe))

    assert (
        str(caught.value) == "MCP transcript requires safe, bounded, correlated records"
    )
    assert adapter._pending_context_log == ("pending", "response")
    assert await adapter.store.get_entries("session") == []


@pytest.mark.asyncio
async def test_mcp_receipt_readback_remains_after_delegated_append(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    original_effect = append_transcript_entry_with_context
    calls = 0

    async def delegated(
        store: TranscriptWriteStore,
        entry: TranscriptEntry,
        pending: Callable[[], tuple[str, str] | None],
    ) -> bool:
        nonlocal calls
        calls += 1
        return await original_effect(store, entry, pending)

    monkeypatch.setattr(
        chat_adapters, "append_transcript_entry_with_context", delegated
    )
    facts = _facts()
    turn = _turn(
        "entry-1",
        ToolCallRecord("mcp_peer_read", {}, "safe result", "mcp-call", facts),
    )
    receipt = await adapter.record_mcp_interaction(turn)

    assert calls == 1
    assert receipt.entry_id == "entry-1"
    assert len(receipt.calls) == 1
    assert receipt.calls[0].transcript_correlation_id == "entry-1"
    assert await adapter.read_mcp_interaction(turn) == receipt
    entry = await adapter.store.get_entry("entry-1")
    assert entry.tool_calls[0].mcp_provenance == receipt.calls[0]
    assert entry.tool_results[0].mcp_provenance == receipt.calls[0]
