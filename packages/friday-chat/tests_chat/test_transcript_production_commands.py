"""Gate C persisted transcript command coverage through production adapters."""

from __future__ import annotations

import asyncio
import csv
import json
import socket
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from friday_chat.adapters import FrameworkTranscriptAdapter
from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeTranscriptStore, FridayRuntime, build_runtime
from friday_chat.session import SessionIdentity
from friday_chat.transcripts import (
    TranscriptContextLogView,
    TranscriptEntryView,
    TranscriptSessionView,
)
from friday_chat.turns.processor import TurnProcessor
from friday_transcript import (
    ContextLogEntry,
    SQLiteTranscriptStore,
    TranscriptEntry,
    TranscriptSession,
)

START = datetime(2026, 8, 8, 12, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def prohibit_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail before any synchronous or asynchronous network attempt."""

    def reject_network(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("network access is prohibited in Gate C tests")

    async def reject_async_network(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("network access is prohibited in Gate C tests")

    monkeypatch.setattr(socket.socket, "connect", reject_network)
    monkeypatch.setattr(socket.socket, "connect_ex", reject_network)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    monkeypatch.setattr(asyncio, "open_connection", reject_async_network)


def _runtime(
    tmp_path: Path,
    *,
    database_path: Path | None = None,
    identity: SessionIdentity | None = None,
    previous_sessions: int = 0,
    capture_raw_prompts: bool = False,
) -> FridayRuntime:
    state_root = tmp_path / "state"
    transcript_path = database_path or state_root / "transcripts.sqlite"
    export_root = state_root / "exports"
    assert transcript_path.resolve(strict=False).is_relative_to(tmp_path.resolve())
    assert export_root.resolve(strict=False).is_relative_to(tmp_path.resolve())
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "fake/gate-c-chat"},
            "memory": {
                "priming": {
                    "enabled": previous_sessions > 0,
                    "previous_sessions": previous_sessions,
                }
            },
            "transcript": {
                "export_directory": str(export_root),
                "capture_raw_prompts": capture_raw_prompts,
            },
            "chat": {
                "user_name": "Chuck",
                "assistant_name": "FridayX",
            },
            "tools": {"enabled": False},
            "session": {
                "flush_on_exit": False,
                "lifecycle_on_exit": False,
            },
        }
    )
    runtime = build_runtime(config, session_identity=identity)
    runtime.transcript = FrameworkTranscriptAdapter(
        store=SQLiteTranscriptStore(transcript_path),
        config=config,
        session_id=runtime.session_identity.value,
    )
    return runtime


def _framework_transcript(runtime: FridayRuntime) -> FrameworkTranscriptAdapter:
    assert isinstance(runtime.transcript, FrameworkTranscriptAdapter)
    return runtime.transcript


async def _seed_session(
    runtime: FridayRuntime,
    *,
    session_id: str,
    started_at: datetime,
    messages: tuple[tuple[int, str, str], ...] = (),
    context_logs: tuple[tuple[int, str, str], ...] = (),
    archived: bool = False,
) -> None:
    adapter = _framework_transcript(runtime)
    created = await adapter.store.create_session(
        TranscriptSession(
            session_id=session_id,
            user_id="synthetic-user",
            started_at=started_at,
            model_name="fake/seeded-model",
            system_prompt="synthetic system prompt",
            config_snapshot={"provider_key": "must-not-export"},
        )
    )
    assert created is True
    for turn_number, user_message, assistant_message in messages:
        appended = await adapter.store.append_entry(
            TranscriptEntry(
                id=f"entry-{abs(hash((session_id, turn_number)))}",
                session_id=session_id,
                turn_number=turn_number,
                user_message=user_message,
                assistant_message=assistant_message,
                timestamp=started_at + timedelta(minutes=turn_number),
                model_name="fake/seeded-model",
                total_tokens=turn_number * 10,
                latency_ms=float(turn_number),
            )
        )
        assert appended is True
    for turn_number, prompt, response in context_logs:
        stored = await adapter.store.store_context_log(
            ContextLogEntry(
                id=f"context-{abs(hash((session_id, turn_number)))}",
                session_id=session_id,
                turn_number=turn_number,
                raw_prompt=prompt,
                raw_response=response,
                captured_at=started_at + timedelta(minutes=turn_number),
            )
        )
        assert stored is True
    if archived:
        assert await adapter.store.archive_session(session_id) is True


async def _execute(runtime: FridayRuntime, command: str) -> str:
    registry = build_default_registry()
    handled, result = await registry.execute(
        command,
        RegistryCommandContext(runtime=runtime, registry=registry),
    )
    assert handled is True
    assert result is not None
    return result.output


class RecordingSessionLimitTranscript(FakeTranscriptStore):
    """Fake that records the command's public session query limit."""

    requested_limits: list[int]

    def __init__(self, *, session_id: str) -> None:
        super().__init__(session_id=session_id)
        self.requested_limits = []

    async def query_sessions(
        self,
        *,
        limit: int = 1000,
        include_archived: bool = False,
    ) -> tuple[TranscriptSessionView, ...]:
        self.requested_limits.append(limit)
        return await super().query_sessions(
            limit=limit,
            include_archived=include_archived,
        )


async def test_fake_and_framework_adapters_share_typed_query_contract(
    tmp_path: Path,
) -> None:
    fake = build_runtime(
        FridayChatConfig.model_validate(
            {
                "llm": {"model": "fake/query-contract"},
                "transcript": {"capture_raw_prompts": True},
                "tools": {"enabled": False},
            }
        ),
        session_identity=SessionIdentity("fake-query-session"),
    )
    await TurnProcessor(fake).process("fake typed query")
    fake_sessions = await fake.transcript.query_sessions()
    fake_entries = await fake.transcript.query_entries("fake-query-session")
    fake_logs = await fake.transcript.query_context_logs("fake-query-session")

    framework = _runtime(
        tmp_path,
        identity=SessionIdentity("framework-query-session"),
    )
    await _seed_session(
        framework,
        session_id="framework-query-session",
        started_at=START,
        messages=((1, "framework user", "framework assistant"),),
        context_logs=((1, "framework prompt", "framework response"),),
    )
    framework_sessions = await framework.transcript.query_sessions()
    framework_entries = await framework.transcript.query_entries(
        "framework-query-session"
    )
    framework_logs = await framework.transcript.query_context_logs(
        "framework-query-session"
    )

    assert isinstance(fake_sessions[0], TranscriptSessionView)
    assert isinstance(fake_entries[0], TranscriptEntryView)
    assert isinstance(fake_logs[0], TranscriptContextLogView)
    assert isinstance(framework_sessions[0], TranscriptSessionView)
    assert isinstance(framework_entries[0], TranscriptEntryView)
    assert isinstance(framework_logs[0], TranscriptContextLogView)
    assert framework_entries[0].user_message == "framework user"


async def test_sessions_are_newest_first_mark_current_and_configured_primed(
    tmp_path: Path,
) -> None:
    current_id = "current-production-session"
    runtime = _runtime(
        tmp_path,
        identity=SessionIdentity(current_id),
        previous_sessions=1,
    )
    await _seed_session(
        runtime,
        session_id="archived-newest",
        started_at=START + timedelta(days=4),
        archived=True,
    )
    await _seed_session(
        runtime,
        session_id=current_id,
        started_at=START + timedelta(days=3),
        messages=((1, "current user", "current assistant"),),
    )
    await _seed_session(
        runtime,
        session_id="previous-newer",
        started_at=START + timedelta(days=2),
        messages=((1, "newer user", "newer assistant"),),
    )
    await _seed_session(
        runtime,
        session_id="previous-older",
        started_at=START + timedelta(days=1),
    )

    output = await _execute(runtime, "/sessions")

    assert "archived-newest" not in output
    assert f"- {current_id} (1 turns) [current]" in output
    assert "- previous-newer (1 turns) [primed]" in output
    assert "- previous-older (0 turns)" in output
    assert output.index(current_id) < output.index("previous-newer")
    assert output.index("previous-newer") < output.index("previous-older")

    unpersisted = _runtime(
        tmp_path,
        database_path=tmp_path / "state" / "unpersisted.sqlite",
        identity=SessionIdentity("unpersisted-current"),
    )
    assert "unpersisted-current (0 turns) [current, not persisted]" in (
        await _execute(unpersisted, "/sessions")
    )

    recording = RecordingSessionLimitTranscript(
        session_id=unpersisted.session_identity.value
    )
    unpersisted.transcript = recording
    await _execute(unpersisted, "/sessions")
    assert recording.requested_limits == [1000]


async def test_transcript_handles_current_selected_untrusted_empty_and_archived(
    tmp_path: Path,
) -> None:
    current_id = "current-transcript"
    untrusted_id = "../../δοκιμή';DROP_TABLE--"
    long_message = "x" * 520
    runtime = _runtime(tmp_path, identity=SessionIdentity(current_id))
    await _seed_session(
        runtime,
        session_id=current_id,
        started_at=START,
        messages=((1, "current marker", "current response"),),
    )
    await _seed_session(
        runtime,
        session_id=untrusted_id,
        started_at=START + timedelta(hours=1),
        messages=(
            (2, "second user", "second assistant"),
            (1, long_message, "first assistant"),
        ),
    )
    await _seed_session(
        runtime,
        session_id="empty-session",
        started_at=START + timedelta(hours=2),
    )
    await _seed_session(
        runtime,
        session_id="archived-session",
        started_at=START + timedelta(hours=3),
        messages=((1, "archived user", "archived assistant"),),
        archived=True,
    )

    current = await _execute(runtime, "/transcript")
    selected = await _execute(runtime, f"/transcript {untrusted_id}")
    empty = await _execute(runtime, "/transcript empty-session")
    archived = await _execute(runtime, "/transcript archived-session")
    missing = await _execute(runtime, "/transcript missing-session")

    assert "current marker" in current
    assert selected.index("1. Chuck:") < selected.index("2. Chuck:")
    assert "x" * 497 + "..." in selected
    assert "x" * 498 not in selected
    assert "Entries: 0" in empty
    assert "No transcript entries recorded." in empty
    assert "Status: archived" in archived
    assert "archived user" in archived
    assert missing == "Transcript session not found: missing-session"
    assert not (tmp_path / "δοκιμή';DROP_TABLE--").exists()

    archived_current = _runtime(
        tmp_path,
        identity=SessionIdentity("archived-session"),
    )
    archived_sessions = await _execute(archived_current, "/sessions")
    assert "archived-session (1 turns) [current, archived]" in archived_sessions


async def test_exports_share_persisted_queries_and_safe_static_paths(
    tmp_path: Path,
) -> None:
    current_id = "current-export"
    selected_id = "../selected-δοκιμή';DELETE--"
    runtime = _runtime(
        tmp_path,
        identity=SessionIdentity(current_id),
        capture_raw_prompts=True,
    )
    await _seed_session(
        runtime,
        session_id=current_id,
        started_at=START + timedelta(days=2),
        messages=((1, 'current, "quoted"\nuser', "current assistant"),),
    )
    await _seed_session(
        runtime,
        session_id=selected_id,
        started_at=START + timedelta(days=1),
        messages=((1, "selected user", "selected assistant"),),
        context_logs=((1, "selected prompt", "selected raw response"),),
    )
    await _seed_session(
        runtime,
        session_id="archived-export",
        started_at=START + timedelta(days=3),
        messages=((1, "archived", "excluded"),),
        archived=True,
    )

    all_output = await _execute(runtime, "/transcript export")
    export_root = tmp_path / "state" / "exports"
    export_directories = sorted(export_root.glob("transcript-export-*"))
    assert len(export_directories) == 1
    all_directory = export_directories[0]
    sessions_path = all_directory / "sessions.csv"
    entries_path = all_directory / "entries.csv"
    assert all_output == f"Exported 2 sessions and 2 entries to {all_directory}"
    assert {path.name for path in all_directory.iterdir()} == {
        "sessions.csv",
        "entries.csv",
    }
    assert sessions_path.read_text().startswith('"session_id"')
    with sessions_path.open(newline="", encoding="utf-8") as handle:
        session_rows = list(csv.DictReader(handle))
    with entries_path.open(newline="", encoding="utf-8") as handle:
        entry_rows = list(csv.DictReader(handle))
    assert [row["session_id"] for row in session_rows] == [current_id, selected_id]
    assert len(entry_rows) == 2
    assert entry_rows[0]["user_message"] == 'current, "quoted"\nuser'
    assert "must-not-export" not in sessions_path.read_text()
    assert not list(all_directory.glob("*.sqlite*"))

    default_output = await _execute(runtime, "/export")
    csv_output = await _execute(runtime, "/export csv")
    await _execute(runtime, "/export jsonl")
    await _execute(runtime, "/export md")
    await _execute(runtime, "/export training")
    assert "(1 entry)" in default_output
    assert "(1 entry)" in csv_output
    markdown = (export_root / "friday_current_session.md").read_text()
    assert "**Chuck:**" in markdown
    assert "**FridayX:**" in markdown
    assert (export_root / "friday_current_session.csv").read_text().startswith(
        '"session_id"'
    )
    assert (export_root / "friday_current_session.jsonl").exists()
    assert (export_root / "friday_current_session_training.jsonl").exists()

    prompt_output = await _execute(runtime, f"/export-prompts {selected_id}")
    prompts_path = export_root / "friday_prompts.json"
    payload = json.loads(prompts_path.read_text())
    assert prompt_output == f"Exported 1 prompt record to {prompts_path}"
    assert payload[0]["session_id"] == selected_id
    assert payload[0]["prompt"] == "selected prompt"
    assert prompts_path.resolve().is_relative_to(export_root.resolve())
    assert not (tmp_path / "selected-δοκιμή';DELETE--").exists()


async def test_empty_missing_and_context_log_export_states_are_explicit(
    tmp_path: Path,
) -> None:
    runtime = _runtime(
        tmp_path,
        identity=SessionIdentity("empty-current"),
    )
    missing_current = await _execute(runtime, "/transcript")
    missing_export = await _execute(runtime, "/export")
    missing_prompts = await _execute(runtime, "/export-prompts")
    all_export = await _execute(runtime, "/transcript export")

    assert missing_current == (
        "No persisted transcript exists for current session: empty-current"
    )
    assert missing_export == missing_current
    assert missing_prompts == missing_current
    assert "Exported 0 sessions and 0 entries" in all_export
    directory = next((tmp_path / "state" / "exports").glob("transcript-export-*"))
    assert len((directory / "sessions.csv").read_text().splitlines()) == 1
    assert len((directory / "entries.csv").read_text().splitlines()) == 1

    await _seed_session(
        runtime,
        session_id="empty-current",
        started_at=START,
    )
    no_prompts = await _execute(runtime, "/export-prompts")
    empty_file_output = await _execute(runtime, "/export csv")
    assert no_prompts.endswith(
        "Enable transcript.capture_raw_prompts to capture them."
    )
    assert "(0 entries)" in empty_file_output


async def test_two_app_invocations_share_wal_visible_store_with_distinct_ids(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "state" / "shared.sqlite"
    first = _runtime(tmp_path, database_path=database_path, previous_sessions=1)
    first_output = ListOutputSink()
    first_result = await FridayChatApp(
        runtime=first,
        input_source=ListInputSource(["first app marker"]),
        output_sink=first_output,
    ).run()
    with sqlite3.connect(database_path) as connection:
        journal_mode = connection.execute("PRAGMA journal_mode").fetchone()
    assert journal_mode is not None
    assert journal_mode[0] == "wal"

    second = _runtime(tmp_path, database_path=database_path, previous_sessions=1)
    second_output = ListOutputSink()
    second_result = await FridayChatApp(
        runtime=second,
        input_source=ListInputSource(
            [
                "second app marker",
                "/sessions",
                f"/transcript {first.session_identity.value}",
            ]
        ),
        output_sink=second_output,
    ).run()

    assert first_result.turns_processed == 1
    assert second_result.turns_processed == 1
    assert first.session_identity != second.session_identity
    combined = "\n".join(second_output.values)
    assert first.session_identity.value in combined
    assert second.session_identity.value in combined
    assert "[primed]" in combined
    assert "Status: ended" in combined
    assert "first app marker" in combined
    assert await second.transcript.query_session(first.session_identity.value) is not None


class FailingTranscriptQueries(FakeTranscriptStore):
    """Query double whose exception content must never reach command output."""

    async def query_sessions(
        self,
        *,
        limit: int = 1000,
        include_archived: bool = False,
    ) -> tuple[TranscriptSessionView, ...]:
        raise OSError("SELECT secret marker FROM /private/transcripts.sqlite")

    async def query_session(self, session_id: str) -> TranscriptSessionView | None:
        raise OSError("SELECT secret marker FROM /private/transcripts.sqlite")


class PartialFailureTranscript(FakeTranscriptStore):
    """Session listing succeeds before entry retrieval fails."""

    async def query_entries(
        self,
        session_id: str,
    ) -> tuple[TranscriptEntryView, ...]:
        raise OSError("entry content secret and /private/transcripts.sqlite")


async def test_query_and_partial_export_failures_are_sanitized(
    tmp_path: Path,
) -> None:
    runtime = _runtime(
        tmp_path,
        identity=SessionIdentity("failure-session"),
    )
    runtime.transcript = FailingTranscriptQueries(session_id="failure-session")
    outputs = [
        await _execute(runtime, command)
        for command in (
            "/sessions",
            "/transcript",
            "/transcript export",
            "/export",
            "/export-prompts",
        )
    ]
    assert outputs == [
        "Transcript storage is unavailable.",
        "Transcript storage is unavailable.",
        "Unable to export transcript data.",
        "Unable to export transcript data.",
        "Unable to export transcript data.",
    ]
    assert all("secret" not in output and "/private" not in output for output in outputs)

    runtime.transcript = PartialFailureTranscript(session_id="failure-session")
    partial = await _execute(runtime, "/transcript export")
    assert partial == "Unable to export transcript data."
    export_root = tmp_path / "state" / "exports"
    assert not list(export_root.glob("transcript-export-*"))
