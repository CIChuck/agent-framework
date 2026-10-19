"""Chat keeps its transcript query API while using the neutral adapter."""

from __future__ import annotations

import inspect
from datetime import UTC, datetime
from pathlib import Path

import pytest
from friday_chat.adapters import FrameworkTranscriptAdapter
from friday_chat.config import FridayChatConfig
from friday_chat.transcripts import (
    TranscriptContextLogView,
    TranscriptEntryView,
    TranscriptSessionView,
)
from friday_runtime.transcript_queries import TranscriptQueryAdapter
from friday_transcript import SQLiteTranscriptStore

START = datetime(2026, 1, 2, tzinfo=UTC)


def _chat_adapter(tmp_path: Path) -> FrameworkTranscriptAdapter:
    return FrameworkTranscriptAdapter(
        store=SQLiteTranscriptStore(tmp_path / "transcripts.sqlite"),
        config=FridayChatConfig.model_validate({"llm": {"model": "fake/test"}}),
        session_id="current",
    )


@pytest.mark.asyncio
async def test_all_public_queries_delegate_to_neutral_adapter_with_same_store(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chat = _chat_adapter(tmp_path)
    session = TranscriptSessionView("session", None, START, None, "fake/test", 1, 2)
    entry = TranscriptEntryView("entry", "session", 1, "prompt", "answer", START)
    log = TranscriptContextLogView("log", "session", 1, "entry", "[]", None, START)
    calls: list[tuple[object, ...]] = []

    async def query_sessions(
        self: TranscriptQueryAdapter,
        *,
        limit: int = 1000,
        include_archived: bool = False,
    ) -> tuple[TranscriptSessionView, ...]:
        calls.append(("sessions", self.store, limit, include_archived))
        return (session,)

    async def query_session(
        self: TranscriptQueryAdapter,
        session_id: str,
    ) -> TranscriptSessionView | None:
        calls.append(("session", self.store, session_id))
        return session

    async def query_entries(
        self: TranscriptQueryAdapter,
        session_id: str,
    ) -> tuple[TranscriptEntryView, ...]:
        calls.append(("entries", self.store, session_id))
        return (entry,)

    async def query_context_logs(
        self: TranscriptQueryAdapter,
        session_id: str,
    ) -> tuple[TranscriptContextLogView, ...]:
        calls.append(("context_logs", self.store, session_id))
        return (log,)

    monkeypatch.setattr(TranscriptQueryAdapter, "query_sessions", query_sessions)
    monkeypatch.setattr(TranscriptQueryAdapter, "query_session", query_session)
    monkeypatch.setattr(TranscriptQueryAdapter, "query_entries", query_entries)
    monkeypatch.setattr(
        TranscriptQueryAdapter, "query_context_logs", query_context_logs
    )

    assert await chat.query_sessions(limit=3, include_archived=True) == (session,)
    assert await chat.query_session("selected") is session
    assert await chat.query_entries("selected") == (entry,)
    assert await chat.query_context_logs("selected") == (log,)
    assert calls == [
        ("sessions", chat.store, 3, True),
        ("session", chat.store, "selected"),
        ("entries", chat.store, "selected"),
        ("context_logs", chat.store, "selected"),
    ]


def test_chat_query_signatures_and_constructor_are_unchanged() -> None:
    assert tuple(inspect.signature(FrameworkTranscriptAdapter).parameters) == (
        "store",
        "config",
        "session_id",
        "_turn_number",
        "_pending_context_log",
    )
    sessions = inspect.signature(FrameworkTranscriptAdapter.query_sessions)
    assert tuple(sessions.parameters) == ("self", "limit", "include_archived")
    assert sessions.parameters["limit"].default == 1000
    assert sessions.parameters["include_archived"].default is False
    assert sessions.parameters["limit"].kind is inspect.Parameter.KEYWORD_ONLY
    for name in ("query_session", "query_entries", "query_context_logs"):
        assert tuple(
            inspect.signature(getattr(FrameworkTranscriptAdapter, name)).parameters
        ) == ("self", "session_id")


@pytest.mark.asyncio
async def test_chat_query_propagates_neutral_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chat = _chat_adapter(tmp_path)
    failure = RuntimeError("transcript store unavailable")

    async def fail_entries(
        self: TranscriptQueryAdapter,
        session_id: str,
    ) -> tuple[TranscriptEntryView, ...]:
        assert self.store is chat.store
        assert session_id == "selected"
        raise failure

    monkeypatch.setattr(TranscriptQueryAdapter, "query_entries", fail_entries)

    with pytest.raises(RuntimeError) as caught:
        await chat.query_entries("selected")
    assert caught.value is failure
