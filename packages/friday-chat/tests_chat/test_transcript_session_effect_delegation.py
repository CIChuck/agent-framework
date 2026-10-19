"""Chat retains session policy while delegating the neutral ensure effect."""

from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from friday_chat import adapters as chat_adapters
from friday_chat.adapters import FrameworkTranscriptAdapter
from friday_chat.config import FridayChatConfig
from friday_chat.tools.schemas import ToolCallRecord
from friday_chat.turns.models import InteractionTurn, TurnMetrics
from friday_core.mcp import MCPToolCallProvenance, MCPToolMetadata
from friday_runtime.transcript_session_effects import (
    TranscriptSessionStore,
    ensure_transcript_session,
)
from friday_transcript import SQLiteTranscriptStore, TranscriptEntry, TranscriptSession


def _configuration() -> FridayChatConfig:
    return FridayChatConfig.model_validate(
        {
            "llm": {"model": "fake/test"},
            "chat": {"user_name": "Chuck", "system_prompt": "Friday system"},
            "tools": {
                "providers": {
                    "mcp": {
                        "enabled": True,
                        "mode": "all",
                        "config": {
                            "servers": [{"name": "peer", "command": "synthetic-peer"}]
                        },
                    },
                    "native_example": {"shape": "preserved"},
                }
            },
        }
    )


def _adapter(tmp_path: Path, session_id: str = "session") -> FrameworkTranscriptAdapter:
    return FrameworkTranscriptAdapter(
        SQLiteTranscriptStore(tmp_path / "transcript.sqlite"),
        _configuration(),
        session_id,
    )


def _turn(identifier: str = "entry-1", *calls: ToolCallRecord) -> InteractionTurn:
    return InteractionTurn(
        identifier,
        "user prompt",
        "assistant answer",
        "raw prompt",
        "context",
        (),
        TurnMetrics(0, 0, 0, 0),
        tool_calls=calls,
    )


@pytest.mark.asyncio
async def test_chat_delegates_after_preflight_with_lazy_snapshot_and_same_write_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    store = adapter.store
    expected_snapshot = adapter.config.model_dump(
        mode="json", exclude={"tools": {"providers": {"mcp"}}}
    )
    original_preflight = chat_adapters.validate_transcript_tool_provenance
    original_ensure = ensure_transcript_session
    original_get = store.get_session
    original_create = store.create_session
    original_count = store.count_entries
    original_append = store.append_entry
    original_dump = FridayChatConfig.model_dump
    events: list[str] = []

    def preflight(*args: Any, **kwargs: Any) -> Any:
        events.append("preflight")
        return original_preflight(*args, **kwargs)

    async def delegated(
        target: TranscriptSessionStore,
        session_id: str,
        factory: Callable[[], TranscriptSession],
    ) -> None:
        events.append("delegate")
        assert target is store
        assert session_id == "session"
        await original_ensure(target, session_id, factory)

    async def get(session_id: str) -> TranscriptSession | None:
        events.append("get")
        return await original_get(session_id)

    def dump(self: FridayChatConfig, *args: Any, **kwargs: Any) -> dict[str, Any]:
        if self is adapter.config:
            events.append("snapshot")
        result: dict[str, Any] = original_dump(self, *args, **kwargs)
        return result

    async def create(session: TranscriptSession) -> bool:
        events.append("create")
        assert session.config_snapshot == expected_snapshot
        result: bool = await original_create(session)
        return result

    async def count(session_id: str) -> int:
        events.append("count")
        result: int = await original_count(session_id)
        return result

    async def append(entry: TranscriptEntry) -> bool:
        events.append("append")
        result: bool = await original_append(entry)
        return result

    monkeypatch.setattr(chat_adapters, "validate_transcript_tool_provenance", preflight)
    monkeypatch.setattr(chat_adapters, "ensure_transcript_session", delegated)
    monkeypatch.setattr(FridayChatConfig, "model_dump", dump)
    monkeypatch.setattr(store, "get_session", get)
    monkeypatch.setattr(store, "create_session", create)
    monkeypatch.setattr(store, "count_entries", count)
    monkeypatch.setattr(store, "append_entry", append)

    await adapter.record_interaction(_turn())

    assert events == [
        "preflight",
        "delegate",
        "get",
        "snapshot",
        "create",
        "count",
        "append",
    ]
    session = await original_get("session")
    assert session is not None
    assert (session.session_id, session.user_id, session.model_name) == (
        "session",
        "Chuck",
        "fake/test",
    )
    assert session.system_prompt == "Friday system"
    assert session.config_snapshot == expected_snapshot
    assert session.config_snapshot["tools"]["providers"] == {
        "native_example": {"shape": "preserved"}
    }
    assert await store.get_entry("entry-1") is not None
    assert adapter._turn_number == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ended,archived", [(False, False), (True, False), (False, True)]
)
async def test_existing_historical_session_is_not_resnapshotted_or_reopened(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ended: bool, archived: bool
) -> None:
    adapter = _adapter(tmp_path)
    historical = TranscriptSession(
        session_id="session",
        model_name="old/model",
        user_id="old-user",
        ended_at=datetime(2020, 1, 2) if ended else None,
        archived=archived,
        config_snapshot={"tools": {"providers": {"mcp": {"historical": True}}}},
    )
    assert await adapter.store.create_session(historical)
    if archived:
        assert await adapter.store.archive_session("session")

    def unexpected_dump(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("existing session evaluated a new Chat snapshot")

    monkeypatch.setattr(FridayChatConfig, "model_dump", unexpected_dump)
    await adapter.record_interaction(_turn())

    saved = await adapter.store.get_session("session")
    assert saved is not None
    assert saved.model_name == "old/model"
    assert saved.user_id == "old-user"
    assert saved.ended_at == historical.ended_at
    assert saved.config_snapshot == historical.config_snapshot
    assert await adapter.store.get_entry("entry-1") is not None
    with sqlite3.connect(tmp_path / "transcript.sqlite") as connection:
        archived_row = connection.execute(
            "SELECT archived FROM sessions WHERE session_id = ?", ("session",)
        ).fetchone()
    assert archived_row is not None
    assert bool(archived_row[0]) is archived


@pytest.mark.asyncio
async def test_false_create_keeps_existing_downstream_append_error_and_cached_count(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)
    events: list[str] = []
    original_get = adapter.store.get_session
    original_count = adapter.store.count_entries
    original_append = adapter.store.append_entry

    async def get(session_id: str) -> TranscriptSession | None:
        events.append("get")
        return await original_get(session_id)

    async def false_create(session: TranscriptSession) -> bool:
        events.append("create")
        return False

    async def count(session_id: str) -> int:
        events.append("count")
        result: int = await original_count(session_id)
        return result

    async def append(entry: TranscriptEntry) -> bool:
        events.append("append")
        result: bool = await original_append(entry)
        return result

    monkeypatch.setattr(adapter.store, "get_session", get)
    monkeypatch.setattr(adapter.store, "create_session", false_create)
    monkeypatch.setattr(adapter.store, "count_entries", count)
    monkeypatch.setattr(adapter.store, "append_entry", append)

    with pytest.raises(RuntimeError) as caught:
        await adapter.record_interaction(_turn())

    assert str(caught.value) == "Failed to append transcript entry."
    assert events == ["get", "create", "count", "append"]
    assert await original_get("session") is None
    assert await adapter.store.get_entry("entry-1") is None
    assert adapter._turn_number == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["get", "create"])
@pytest.mark.parametrize("failure_type", [ValueError, asyncio.CancelledError])
async def test_chat_propagates_session_store_failure_or_cancellation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
    failure_type: type[BaseException],
) -> None:
    adapter = _adapter(tmp_path)
    failure = failure_type("injected")

    async def failed_get(session_id: str) -> TranscriptSession | None:
        raise failure

    async def failed_create(session: TranscriptSession) -> bool:
        raise failure

    monkeypatch.setattr(
        adapter.store,
        "get_session" if operation == "get" else "create_session",
        failed_get if operation == "get" else failed_create,
    )
    with pytest.raises(failure_type) as caught:
        await adapter.record_interaction(_turn())

    assert caught.value is failure
    assert adapter._turn_number is None
    assert await adapter.store.get_entry("entry-1") is None


def _unsafe_mcp_call() -> ToolCallRecord:
    facts = MCPToolCallProvenance(
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
        model_result_size_bytes=len(b"safe result"),
        transcript_correlation_id="entry-1",
    )
    return ToolCallRecord(
        "mcp_peer_read", {"raw": "unsafe"}, "safe result", "mcp-call", facts
    )


@pytest.mark.asyncio
async def test_unsafe_preflight_stops_before_neutral_session_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path)

    async def unexpected_effect(*args: Any, **kwargs: Any) -> None:
        pytest.fail("unsafe preflight reached session effect")

    monkeypatch.setattr(chat_adapters, "ensure_transcript_session", unexpected_effect)
    with pytest.raises(ValueError, match="safe, bounded, correlated records"):
        await adapter.record_interaction(_turn("entry-1", _unsafe_mcp_call()))
    assert await adapter.store.get_session("session") is None
