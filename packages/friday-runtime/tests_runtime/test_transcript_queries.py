"""Persisted transcript queries remain usable without either frontend."""

from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from friday_runtime.transcript_queries import TranscriptQueryAdapter
from friday_runtime.transcript_views import TranscriptQueryStore
from friday_transcript import (
    ContextLogEntry,
    SQLiteTranscriptStore,
    TranscriptEntry,
    TranscriptSession,
)

START = datetime(2026, 1, 2, 12, tzinfo=UTC)


class RecordingReadStore:
    """Only the four read operations available to the neutral adapter."""

    def __init__(
        self,
        *,
        sessions: list[TranscriptSession] | None = None,
        entries: list[TranscriptEntry] | None = None,
        context_logs: list[ContextLogEntry] | None = None,
    ) -> None:
        self.sessions = sessions or []
        self.entries = entries or []
        self.context_logs = context_logs or []
        self.session_pages: list[tuple[int, int, bool]] = []
        self.entry_pages: list[tuple[str, int, int]] = []
        self.log_reads: list[tuple[str, int]] = []
        self.session_reads: list[str] = []
        self.fail_on: str | None = None
        self.failure = RuntimeError("synthetic transcript read failed")

    def _fail_if_requested(self, operation: str) -> None:
        if self.fail_on == operation:
            raise self.failure

    async def get_session(self, session_id: str) -> TranscriptSession | None:
        self.session_reads.append(session_id)
        self._fail_if_requested("get_session")
        return next(
            (session for session in self.sessions if session.session_id == session_id),
            None,
        )

    async def list_sessions(
        self,
        limit: int = 100,
        offset: int = 0,
        user_id: str | None = None,
        active_only: bool = False,
        include_archived: bool = False,
    ) -> list[TranscriptSession]:
        self.session_pages.append((limit, offset, include_archived))
        self._fail_if_requested("list_sessions")
        rows = (
            self.sessions
            if include_archived
            else [session for session in self.sessions if not session.archived]
        )
        if user_id is not None:
            rows = [session for session in rows if session.user_id == user_id]
        if active_only:
            rows = [session for session in rows if session.ended_at is None]
        return rows[offset : offset + limit]

    async def get_entries(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
        after: datetime | None = None,
        before: datetime | None = None,
    ) -> list[TranscriptEntry]:
        self.entry_pages.append((session_id, limit, offset))
        self._fail_if_requested("get_entries")
        rows = [entry for entry in self.entries if entry.session_id == session_id]
        if after is not None:
            rows = [entry for entry in rows if entry.timestamp > after]
        if before is not None:
            rows = [entry for entry in rows if entry.timestamp < before]
        return rows[offset : offset + limit]

    async def get_context_log_for_session(
        self,
        session_id: str,
        limit: int = 100,
    ) -> list[ContextLogEntry]:
        self.log_reads.append((session_id, limit))
        self._fail_if_requested("get_context_log_for_session")
        return [entry for entry in self.context_logs if entry.session_id == session_id][
            :limit
        ]


def _session(
    session_id: str,
    *,
    started_at: datetime = START,
    archived: bool = False,
) -> TranscriptSession:
    return TranscriptSession(
        session_id=session_id,
        user_id=None,
        started_at=started_at,
        model_name="fake/transcript",
        total_turns=2,
        total_tokens=11,
        archived=archived,
    )


def _entry(
    entry_id: str,
    turn_number: int,
    *,
    timestamp: datetime = START,
) -> TranscriptEntry:
    return TranscriptEntry(
        id=entry_id,
        session_id="session",
        turn_number=turn_number,
        user_message=None,
        assistant_message="answer",
        timestamp=timestamp,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("limit,expected", [(0, 0), (-5, 0), (1001, 1000)])
async def test_session_limit_is_clamped_before_store_read(
    limit: int, expected: int
) -> None:
    store = RecordingReadStore(sessions=[_session("session")])
    query: TranscriptQueryStore = TranscriptQueryAdapter(store)

    await query.query_sessions(limit=limit)

    assert store.session_pages == [(expected, 0, False)]


@pytest.mark.asyncio
async def test_sessions_sort_newest_first_and_derive_archive_membership() -> None:
    store = RecordingReadStore(
        sessions=[
            _session("older", started_at=START - timedelta(days=1)),
            _session("a", started_at=START.replace(tzinfo=None)),
            _session("z", started_at=START),
            _session("archived", started_at=START + timedelta(days=1), archived=True),
        ]
    )
    query = TranscriptQueryAdapter(store)

    visible = await query.query_sessions()
    all_sessions = await query.query_sessions(include_archived=True)

    assert [session.session_id for session in visible] == ["z", "a", "older"]
    assert [session.session_id for session in all_sessions] == [
        "archived",
        "z",
        "a",
        "older",
    ]
    assert [session.archived for session in all_sessions] == [
        True,
        False,
        False,
        False,
    ]
    assert all_sessions[1].user_id is None
    assert all_sessions[1].total_tokens == 11
    assert store.session_pages == [
        (1000, 0, False),
        (1000, 0, True),
        (1000, 0, False),
    ]


@pytest.mark.asyncio
async def test_archive_scan_reaches_later_pages_for_exact_session() -> None:
    sessions = [_session(f"visible-{index}") for index in range(1001)]
    sessions.append(_session("archived", archived=True))
    store = RecordingReadStore(sessions=sessions)
    query = TranscriptQueryAdapter(store)

    visible = await query.query_session("visible-1000")
    archived = await query.query_session("archived")
    assert visible is not None and visible.archived is False
    assert archived is not None and archived.archived is True
    assert await query.query_session("missing") is None
    assert store.session_reads == ["visible-1000", "archived", "missing"]
    assert store.session_pages == [
        (1000, 0, False),
        (1000, 1000, False),
        (1000, 0, False),
        (1000, 1000, False),
    ]


@pytest.mark.asyncio
async def test_entries_page_past_one_thousand_and_sort_stably() -> None:
    entries = [_entry(f"entry-{index:04d}", index + 2) for index in range(1001)]
    entries.extend(
        [
            _entry("same-z", 1, timestamp=START),
            _entry("same-a", 1, timestamp=START.replace(tzinfo=None)),
        ]
    )
    store = RecordingReadStore(entries=entries)
    query = TranscriptQueryAdapter(store)

    views = await query.query_entries("session")

    assert len(views) == 1003
    assert [view.entry_id for view in views[:3]] == [
        "same-a",
        "same-z",
        "entry-0000",
    ]
    assert views[-1].entry_id == "entry-1000"
    assert views[0].user_message is None
    assert views[0].model_name is None
    assert views[0].total_tokens is None
    assert views[0].latency_ms is None
    assert store.entry_pages == [
        ("session", 1000, 0),
        ("session", 1000, 1000),
    ]


@pytest.mark.asyncio
async def test_context_logs_keep_single_limited_read_and_order() -> None:
    store = RecordingReadStore(
        context_logs=[
            ContextLogEntry(
                id="later",
                session_id="session",
                turn_number=2,
                raw_prompt="prompt two",
                raw_response=None,
                captured_at=START + timedelta(minutes=1),
            ),
            ContextLogEntry(
                id="z",
                session_id="session",
                turn_number=1,
                raw_prompt="prompt z",
                raw_response="response z",
                captured_at=START,
            ),
            ContextLogEntry(
                id="a",
                session_id="session",
                turn_number=1,
                entry_id="entry-a",
                raw_prompt="prompt a",
                raw_response=None,
                captured_at=START.replace(tzinfo=None),
            ),
        ]
    )

    views = await TranscriptQueryAdapter(store).query_context_logs("session")

    assert [view.log_id for view in views] == ["a", "z", "later"]
    assert views[0].entry_id == "entry-a"
    assert views[0].raw_response is None
    assert views[0].raw_prompt == "prompt a"
    assert store.log_reads == [("session", 100_000)]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation,store_method",
    [
        ("sessions", "list_sessions"),
        ("session", "get_session"),
        ("entries", "get_entries"),
        ("logs", "get_context_log_for_session"),
    ],
)
async def test_store_read_errors_propagate_without_fallback(
    operation: str, store_method: str
) -> None:
    store = RecordingReadStore()
    store.fail_on = store_method
    query = TranscriptQueryAdapter(store)

    with pytest.raises(RuntimeError) as caught:
        if operation == "sessions":
            await query.query_sessions()
        elif operation == "session":
            await query.query_session("session")
        elif operation == "entries":
            await query.query_entries("session")
        else:
            await query.query_context_logs("session")

    assert caught.value is store.failure


@pytest.mark.asyncio
async def test_disposable_sqlite_store_is_queryable_without_chat(
    tmp_path: Path,
) -> None:
    store = SQLiteTranscriptStore(tmp_path / "transcripts.sqlite")
    assert await store.create_session(_session("session")) is True
    assert await store.append_entry(_entry("entry", 1)) is True
    assert (
        await store.store_context_log(
            ContextLogEntry(
                id="context",
                session_id="session",
                turn_number=1,
                entry_id="entry",
                raw_prompt="[]",
                raw_response=None,
                captured_at=START,
            )
        )
        is True
    )
    query = TranscriptQueryAdapter(store)

    assert [session.session_id for session in await query.query_sessions()] == [
        "session"
    ]
    session = await query.query_session("session")
    assert session is not None and session.model_name == "fake/transcript"
    assert [entry.entry_id for entry in await query.query_entries("session")] == [
        "entry"
    ]
    assert [log.log_id for log in await query.query_context_logs("session")] == [
        "context"
    ]
    assert await store.archive_session("session") is True
    assert await query.query_sessions() == ()
    archived = await query.query_session("session")
    assert archived is not None and archived.archived is True


def test_neutral_module_import_does_not_load_frontends() -> None:
    process = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "import friday_runtime.transcript_queries; "
                "assert not any(name.startswith(('friday_chat', 'friday_cli')) "
                "for name in sys.modules)"
            ),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode == 0, process.stderr
