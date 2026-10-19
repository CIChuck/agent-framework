"""Chat registry keeps its export policy while delegating single-file effects."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest
from friday_chat.commands import transcript as chat_transcript
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeTranscriptStore, FridayRuntime, build_runtime
from friday_chat.session import SessionIdentity
from friday_chat.transcripts import TranscriptExportResult
from friday_runtime.transcript_export_files import (
    write_context_log_file,
    write_current_session_file,
)
from friday_runtime.transcript_export_format import (
    serialize_context_logs_json,
    serialize_entries_csv,
    serialize_entries_jsonl,
    serialize_training_jsonl,
    serialize_transcript_markdown,
)
from friday_runtime.transcript_views import (
    TranscriptContextLogView,
    TranscriptEntryView,
    TranscriptSessionView,
)


def _runtime(root: Path) -> FridayRuntime:
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "fake/export-files"},
            "chat": {"user_name": "Chuck", "assistant_name": "FridayX"},
            "transcript": {
                "export_directory": str(root),
                "capture_raw_prompts": True,
            },
            "tools": {"enabled": False},
        }
    )
    return build_runtime(config, session_identity=SessionIdentity("export-session"))


async def _execute(context: RegistryCommandContext, command: str) -> str:
    registry = context.registry
    handled, result = await registry.execute(command, context)
    assert handled and result is not None
    return result.output


@pytest.mark.asyncio
async def test_registry_delegates_five_single_files_and_preserves_results(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "exports"
    runtime = _runtime(root)
    store = FakeTranscriptStore(session_id="export-session")
    await store.record_turn('Hi, "Friday"\nagain', "Voilà")
    await store.record_context_log("raw\nπ", "reply")
    runtime.transcript = store
    registry = build_default_registry()
    context = RegistryCommandContext(runtime=runtime, registry=registry)
    session = await store.query_session("export-session")
    assert session is not None
    entries = await store.query_entries("export-session")
    logs = await store.query_context_logs("export-session")
    current_calls: list[tuple[Path, str, str | None, str | None]] = []
    log_calls: list[Path] = []

    def track_current(
        destination: Path,
        selected_session: TranscriptSessionView,
        selected_entries: Sequence[TranscriptEntryView],
        *,
        export_format: str,
        user_name: str | None = None,
        assistant_name: str | None = None,
    ) -> None:
        assert selected_session == session
        assert selected_entries == entries
        current_calls.append((destination, export_format, user_name, assistant_name))
        write_current_session_file(
            destination,
            selected_session,
            selected_entries,
            export_format=export_format,
            user_name=user_name,
            assistant_name=assistant_name,
        )

    def track_logs(
        destination: Path,
        selected_session: TranscriptSessionView,
        selected_logs: Sequence[TranscriptContextLogView],
    ) -> None:
        assert selected_session == session
        assert selected_logs == logs
        log_calls.append(destination)
        write_context_log_file(destination, selected_session, selected_logs)

    monkeypatch.setattr(chat_transcript, "write_current_session_file", track_current)
    monkeypatch.setattr(chat_transcript, "write_context_log_file", track_logs)

    files = (
        ("/export csv", "friday_current_session.csv", serialize_entries_csv(entries)),
        (
            "/export jsonl",
            "friday_current_session.jsonl",
            serialize_entries_jsonl(entries),
        ),
        (
            "/export training",
            "friday_current_session_training.jsonl",
            serialize_training_jsonl(entries),
        ),
        (
            "/export md",
            "friday_current_session.md",
            serialize_transcript_markdown(
                session,
                entries,
                user_name="Chuck",
                assistant_name="FridayX",
            ),
        ),
    )
    for command, filename, expected in files:
        destination = root / filename
        assert await _execute(context, command) == (
            f"Exported current session (1 entry) to {destination}"
        )
        assert destination.read_bytes() == expected.encode("utf-8")

    prompts = root / "friday_prompts.json"
    assert await _execute(context, "/export-prompts") == (
        f"Exported 1 prompt record to {prompts}"
    )
    assert prompts.read_bytes() == serialize_context_logs_json(session, logs).encode(
        "utf-8"
    )
    assert current_calls == [
        (root / "friday_current_session.csv", "csv", None, None),
        (root / "friday_current_session.jsonl", "jsonl", None, None),
        (root / "friday_current_session_training.jsonl", "training", None, None),
        (root / "friday_current_session.md", "markdown", "Chuck", "FridayX"),
    ]
    assert log_calls == [prompts]
    current = chat_transcript._write_current_session_export(
        context, session, entries, "csv"
    )
    prompt_result = chat_transcript._write_context_log_export(context, session, logs)
    assert type(current) is TranscriptExportResult
    assert type(prompt_result) is TranscriptExportResult
    assert TranscriptExportResult.__module__ == "friday_chat.transcripts"
    assert current.files == (root / "friday_current_session.csv",)
    assert current.entry_count == 1
    assert current.session_count == 0
    assert prompt_result.files == (prompts,)
    assert prompt_result.session_count == 1
    assert prompt_result.context_log_count == 1


@pytest.mark.asyncio
async def test_registry_keeps_no_log_and_write_error_behavior(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "exports"
    runtime = _runtime(root)
    store = FakeTranscriptStore(session_id="export-session")
    await store.record_turn("hello", "world")
    runtime.transcript = store
    registry = build_default_registry()
    context = RegistryCommandContext(runtime=runtime, registry=registry)

    assert await _execute(context, "/export-prompts") == (
        "No captured raw prompts for session export-session. "
        "Enable transcript.capture_raw_prompts to capture them."
    )
    assert not (root / "friday_prompts.json").exists()

    def fail_current(*_args: object, **_kwargs: object) -> None:
        raise PermissionError("write denied")

    monkeypatch.setattr(chat_transcript, "write_current_session_file", fail_current)
    assert await _execute(context, "/export csv") == (
        "Unable to export transcript data."
    )
    assert await _execute(context, "/export unknown") == (
        "Usage: /export [csv|jsonl|markdown|md|training]"
    )
    assert await _execute(context, "/export-prompts missing") == (
        "Transcript session not found: missing"
    )
