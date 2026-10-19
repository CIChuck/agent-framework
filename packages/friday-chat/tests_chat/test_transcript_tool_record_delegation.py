"""Chat transcript effects stay ordered around neutral tool-record preparation."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest
from friday_chat import adapters as chat_adapters
from friday_chat.adapters import FrameworkTranscriptAdapter
from friday_chat.config import FridayChatConfig
from friday_chat.tools.schemas import ToolCallRecord
from friday_chat.turns.models import InteractionTurn, TurnMetrics
from friday_core.mcp import MCPToolCallProvenance, MCPToolMetadata
from friday_runtime.transcript_tool_records import (
    TranscriptToolCallInput,
    build_transcript_tool_records,
    validate_transcript_tool_provenance,
)
from friday_transcript import (
    ContextLogEntry,
    SQLiteTranscriptStore,
    ToolCall,
    ToolResult,
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


def _turn(
    identifier: str,
    *calls: ToolCallRecord,
    snippets: tuple[str, ...] = (),
    raw_prompt_captured: bool = False,
) -> InteractionTurn:
    return InteractionTurn(
        identifier,
        "user prompt",
        "assistant answer",
        "raw prompt",
        "context",
        snippets,
        TurnMetrics(0, 0, 0, 0.125),
        raw_prompt_captured=raw_prompt_captured,
        tool_calls=calls,
    )


def _facts(
    result: str = "safe result",
    *,
    call_id: str | None = "mcp-call",
    correlation: str | None = None,
) -> MCPToolCallProvenance:
    return MCPToolCallProvenance(
        tool=MCPToolMetadata(
            canonical_name="mcp_peer_read",
            server_name="peer",
            original_name="read",
            transport="stdio",
            trust_level="local",
        ),
        call_id=call_id,
        status="succeeded",
        output_sanitization_state="unchanged",
        model_result_size_bytes=len(result.encode("utf-8")),
        transcript_correlation_id=correlation,
    )


@pytest.mark.asyncio
async def test_chat_delegates_in_order_and_keeps_entry_and_context_effects(
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

    def validate(
        turn_id: str,
        calls: Sequence[TranscriptToolCallInput],
        max_result_bytes: int,
    ) -> list[MCPToolCallProvenance | None]:
        events.append("validate")
        assert turn_id == "entry-1"
        assert calls[0].name == "echo"
        return validate_transcript_tool_provenance(turn_id, calls, max_result_bytes)

    def build(
        turn_id: str,
        calls: Sequence[TranscriptToolCallInput],
        provenance: Sequence[MCPToolCallProvenance | None],
    ) -> tuple[list[ToolCall], list[ToolResult]]:
        events.append("build")
        assert provenance == [None]
        return build_transcript_tool_records(turn_id, calls, provenance)

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

    async def append_entry(entry: TranscriptEntry) -> bool:
        events.append("append_entry")
        appended: bool = await original_append(entry)
        return appended

    async def store_context_log(log: ContextLogEntry) -> bool:
        events.append("store_context_log")
        stored: bool = await original_context(log)
        return stored

    monkeypatch.setattr(chat_adapters, "validate_transcript_tool_provenance", validate)
    monkeypatch.setattr(chat_adapters, "build_transcript_tool_records", build)
    monkeypatch.setattr(store, "get_session", get_session)
    monkeypatch.setattr(store, "create_session", create_session)
    monkeypatch.setattr(store, "count_entries", count_entries)
    monkeypatch.setattr(store, "append_entry", append_entry)
    monkeypatch.setattr(store, "store_context_log", store_context_log)

    await adapter.record_context_log("pending prompt", "pending response")
    await adapter.record_interaction(
        _turn(
            "entry-1",
            ToolCallRecord("echo", {"text": "safe"}, "done"),
            snippets=("memory",),
            raw_prompt_captured=True,
        )
    )
    assert events == [
        "validate",
        "get_session",
        "create_session",
        "count_entries",
        "build",
        "append_entry",
        "store_context_log",
    ]
    entry = await store.get_entry("entry-1")
    assert entry.session_id == "session"
    assert entry.turn_number == 1
    assert entry.user_message == "user prompt"
    assert entry.assistant_message == "assistant answer"
    assert entry.model_name == "fake/test"
    assert entry.latency_ms == 125
    assert entry.metadata == {
        "raw_prompt_captured": True,
        "memory_snippets": ["memory"],
    }
    assert entry.tool_calls[0].model_dump() == {
        "id": "entry-1:0:echo",
        "name": "echo",
        "arguments": {"text": "safe"},
    }
    assert entry.tool_results[0].model_dump() == {
        "tool_call_id": "entry-1:0:echo",
        "output": "done",
        "error": None,
    }
    logs = await store.get_context_log_for_session("session")
    assert len(logs) == 1
    assert (logs[0].entry_id, logs[0].raw_prompt, logs[0].raw_response) == (
        "entry-1",
        "pending prompt",
        "pending response",
    )
    assert adapter._pending_context_log is None


@pytest.mark.asyncio
async def test_chat_persists_mixed_calls_and_retains_mcp_receipt_readback(
    tmp_path: Path,
) -> None:
    adapter = _adapter(tmp_path)
    facts = _facts(correlation="entry-1")
    turn = _turn(
        "entry-1",
        ToolCallRecord("mcp_peer_read", {}, "safe result", "mcp-call", facts),
        ToolCallRecord("native", {"value": 1}, "native result"),
    )
    receipt = await adapter.record_mcp_interaction(turn)
    assert receipt.entry_id == "entry-1"
    assert receipt.calls == (facts,)
    entry = await adapter.store.get_entry("entry-1")
    assert [call.id for call in entry.tool_calls] == [
        "mcp-call",
        "entry-1:1:native",
    ]
    assert entry.tool_calls[0].mcp_provenance == facts
    assert entry.tool_results[0].mcp_provenance == facts
    assert entry.tool_results[0].error is None
    assert entry.tool_results[1].output == "native result"
    assert await adapter.read_mcp_interaction(turn) == receipt

    await adapter.record_interaction(_turn("entry-2"))
    assert (await adapter.store.get_entry("entry-2")).turn_number == 2


@pytest.mark.asyncio
async def test_unsafe_mcp_preflight_does_not_touch_store_or_pending_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    await adapter.record_context_log("pending", "response")

    async def unexpected_store_call(*args: object, **kwargs: object) -> None:
        pytest.fail("MCP preflight touched the transcript store")

    monkeypatch.setattr(adapter.store, "get_session", unexpected_store_call)
    turn = _turn(
        "entry-1",
        ToolCallRecord(
            "mcp_peer_read",
            {"raw": "not safe"},
            "safe result",
            "mcp-call",
            _facts(),
        ),
    )
    with pytest.raises(ValueError) as caught:
        await adapter.record_interaction(turn)
    assert str(caught.value) == (
        "MCP transcript requires safe, bounded, correlated records"
    )
    assert await adapter.store.get_entries("session") == []
    assert adapter._pending_context_log == ("pending", "response")


@pytest.mark.asyncio
async def test_model_construction_failure_stays_after_session_creation(
    tmp_path: Path,
) -> None:
    adapter = _adapter(tmp_path)
    turn = _turn(
        "entry-1",
        ToolCallRecord("mcp_peer_read", {}, "safe result", None, _facts(call_id=None)),
    )
    with pytest.raises(ValueError, match="MCP transcript call requires"):
        await adapter.record_interaction(turn)
    assert await adapter.store.get_session("session") is not None
    assert await adapter.store.get_entries("session") == []
    assert adapter._turn_number == 0


@pytest.mark.asyncio
async def test_append_failure_keeps_pending_context_and_turn_number_for_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    await adapter.record_context_log("pending", "response")
    original_append = adapter.store.append_entry

    async def false_append(entry: TranscriptEntry) -> bool:
        return False

    monkeypatch.setattr(adapter.store, "append_entry", false_append)
    with pytest.raises(RuntimeError, match="Failed to append transcript entry"):
        await adapter.record_interaction(_turn("entry-1"))
    assert await adapter.store.get_session("session") is not None
    assert await adapter.store.get_entries("session") == []
    assert adapter._pending_context_log == ("pending", "response")
    assert adapter._turn_number == 0

    monkeypatch.setattr(adapter.store, "append_entry", original_append)
    await adapter.record_interaction(_turn("entry-1"))
    assert (await adapter.store.get_entry("entry-1")).turn_number == 1
    assert len(await adapter.store.get_context_log_for_session("session")) == 1
    assert adapter._pending_context_log is None
