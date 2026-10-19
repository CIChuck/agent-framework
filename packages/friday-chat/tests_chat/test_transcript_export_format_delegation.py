"""Chat export commands retain exact bytes while using neutral formatting."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest
from friday_chat.adapters import FrameworkTranscriptAdapter
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeTranscriptStore, FridayRuntime, build_runtime
from friday_chat.session import SessionIdentity
from friday_chat.transcripts import (
    TranscriptContextLogView,
    TranscriptEntryView,
    TranscriptSessionView,
)
from friday_transcript import (
    ContextLogEntry,
    SQLiteTranscriptStore,
    TranscriptEntry,
    TranscriptSession,
)

STAMP = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
SESSION_ID = "s-α"
EXPECTED_SHA256 = {
    "sessions.csv": "f259ccf80cb97232e5afaefbba5832a72c997351e82a16084300dc65e42134b2",
    "entries.csv": "4d918ce79fb4525be47f83b65b8fca830614e9a88131736a7bb9bf0e1288cd0c",
    "friday_current_session.csv": "4d918ce79fb4525be47f83b65b8fca830614e9a88131736a7bb9bf0e1288cd0c",
    "friday_current_session.jsonl": "243026aa856dffcb3bcdd700c391f0c1cda1dfc4ed3a40e8970f1c5b707fdb8c",
    "friday_current_session_training.jsonl": "998ffb447b36d5b5e4b0b6e8698447c84fa1c4da48925acb2a2dcd1bb746a09d",
    "friday_current_session.md": "515f2f3516ae6ea8ac8aa70ca19e4a4142939645afa07544d7c9bdf7e36f6c5c",
    "friday_prompts.json": "5b267f343e4fd44207121f0f7142cf4d673459ce91134fb86277c75610b675bf",
}


class FixedTranscriptStore(FakeTranscriptStore):
    """Supply the frozen persisted views to Chat without a provider."""

    include_entries = True
    include_logs = True

    async def query_sessions(
        self,
        *,
        limit: int = 1000,
        include_archived: bool = False,
    ) -> tuple[TranscriptSessionView, ...]:
        del include_archived
        return (self._fixed_session(),) if limit > 0 else ()

    async def query_session(self, session_id: str) -> TranscriptSessionView | None:
        return self._fixed_session() if session_id == SESSION_ID else None

    async def query_entries(self, session_id: str) -> tuple[TranscriptEntryView, ...]:
        if session_id != SESSION_ID or not self.include_entries:
            return ()
        return (
            TranscriptEntryView(
                "e-1",
                SESSION_ID,
                1,
                'Hi, "Friday"\nagain',
                "Voilà",
                STAMP,
            ),
        )

    async def query_context_logs(
        self, session_id: str
    ) -> tuple[TranscriptContextLogView, ...]:
        if session_id != SESSION_ID or not self.include_logs:
            return ()
        return (
            TranscriptContextLogView(
                "l-1", SESSION_ID, 1, "e-1", "raw\nπ", None, STAMP
            ),
        )

    @staticmethod
    def _fixed_session() -> TranscriptSessionView:
        return TranscriptSessionView(SESSION_ID, None, STAMP, None, "m", 1, 0)


async def _runtime(
    tmp_path: Path,
    *,
    backend: str,
    configured_export_root: bool = True,
) -> FridayRuntime:
    transcript_config: dict[str, object] = {"capture_raw_prompts": True}
    if configured_export_root:
        transcript_config["export_directory"] = str(tmp_path / "exports")
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "fake/export-format"},
            "transcript": transcript_config,
            "chat": {"user_name": "Chuck", "assistant_name": "FridayX"},
            "tools": {"enabled": False},
        }
    )
    runtime = build_runtime(config, session_identity=SessionIdentity(SESSION_ID))
    if backend == "fake":
        runtime.transcript = FixedTranscriptStore(session_id=SESSION_ID)
    elif backend == "sqlite":
        store = SQLiteTranscriptStore(tmp_path / "transcripts.sqlite")
        assert await store.create_session(
            TranscriptSession(
                session_id=SESSION_ID,
                user_id=None,
                started_at=STAMP,
                model_name="m",
                total_turns=0,
                total_tokens=0,
            )
        )
        assert await store.append_entry(
            TranscriptEntry(
                id="e-1",
                session_id=SESSION_ID,
                turn_number=1,
                user_message='Hi, "Friday"\nagain',
                assistant_message="Voilà",
                timestamp=STAMP,
            )
        )
        assert await store.store_context_log(
            ContextLogEntry(
                id="l-1",
                session_id=SESSION_ID,
                turn_number=1,
                entry_id="e-1",
                raw_prompt="raw\nπ",
                raw_response=None,
                captured_at=STAMP,
            )
        )
        runtime.transcript = FrameworkTranscriptAdapter(
            store=store,
            config=config,
            session_id=SESSION_ID,
        )
    else:
        raise ValueError(f"unknown backend: {backend}")
    return runtime


async def _execute(runtime: FridayRuntime, command: str) -> str:
    registry = build_default_registry()
    handled, result = await registry.execute(
        command,
        RegistryCommandContext(runtime=runtime, registry=registry),
    )
    assert handled is True
    assert result is not None
    return result.output


@pytest.mark.asyncio
@pytest.mark.parametrize("backend", ["fake", "sqlite"])
async def test_chat_commands_write_all_seven_frozen_export_files(
    tmp_path: Path,
    backend: str,
) -> None:
    runtime = await _runtime(tmp_path, backend=backend)
    root = tmp_path / "exports"

    all_output = await _execute(runtime, "/transcript export")
    directories = tuple(root.glob("transcript-export-*"))
    assert len(directories) == 1
    directory = directories[0]
    assert all_output == f"Exported 1 session and 1 entry to {directory}"
    assert {path.name for path in directory.iterdir()} == {
        "sessions.csv",
        "entries.csv",
    }

    assert await _execute(runtime, "/export") == (
        f"Exported current session (1 entry) to {root / 'friday_current_session.md'}"
    )
    for command, filename in (
        ("/export csv", "friday_current_session.csv"),
        ("/export jsonl", "friday_current_session.jsonl"),
        ("/export training", "friday_current_session_training.jsonl"),
        ("/export markdown", "friday_current_session.md"),
        ("/export md", "friday_current_session.md"),
    ):
        assert await _execute(runtime, command) == (
            f"Exported current session (1 entry) to {root / filename}"
        )
    assert await _execute(runtime, "/export-prompts") == (
        f"Exported 1 prompt record to {root / 'friday_prompts.json'}"
    )

    files = {path.name: path for path in directory.iterdir()}
    files.update({path.name: path for path in root.iterdir() if path.is_file()})
    assert files.keys() == EXPECTED_SHA256.keys()
    assert {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in files.items()
    } == EXPECTED_SHA256
    assert all(path.resolve().is_relative_to(root.resolve()) for path in files.values())


@pytest.mark.asyncio
async def test_empty_missing_default_root_and_no_prompt_log_behaviors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    runtime = await _runtime(
        tmp_path,
        backend="fake",
        configured_export_root=False,
    )
    assert isinstance(runtime.transcript, FixedTranscriptStore)
    runtime.transcript.include_entries = False
    runtime.transcript.include_logs = False
    root = tmp_path / "exports"

    assert await _execute(runtime, "/export csv") == (
        f"Exported current session (0 entries) to {root / 'friday_current_session.csv'}"
    )
    assert (root / "friday_current_session.csv").read_bytes() == (
        b'"session_id","turn_number","timestamp","user_message",'
        b'"assistant_message","model_name","total_tokens","latency_ms"\n'
    )
    assert await _execute(runtime, "/export jsonl") == (
        f"Exported current session (0 entries) to {root / 'friday_current_session.jsonl'}"
    )
    assert (root / "friday_current_session.jsonl").read_bytes() == b""
    assert await _execute(runtime, "/export markdown") == (
        f"Exported current session (0 entries) to {root / 'friday_current_session.md'}"
    )
    assert (root / "friday_current_session.md").read_text() == ("# Transcript: s-α\n")
    assert await _execute(runtime, "/transcript export") == (
        f"Exported 1 session and 0 entries to {next(root.glob('transcript-export-*'))}"
    )
    assert await _execute(runtime, "/export-prompts") == (
        f"No captured raw prompts for session {SESSION_ID}. "
        "Enable transcript.capture_raw_prompts to capture them."
    )
    assert not (root / "friday_prompts.json").exists()
    assert await _execute(runtime, "/transcript missing") == (
        "Transcript session not found: missing"
    )


@pytest.mark.asyncio
async def test_export_write_and_root_failures_keep_chat_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = await _runtime(tmp_path, backend="fake")

    def fail_write(_path: Path, _text: str, *, encoding: str) -> int:
        assert encoding == "utf-8"
        raise OSError("synthetic write failure")

    monkeypatch.setattr(Path, "write_text", fail_write)
    assert await _execute(runtime, "/export csv") == "Unable to export transcript data."
    assert await _execute(runtime, "/transcript export") == (
        "Unable to export transcript data."
    )
    assert await _execute(runtime, "/export-prompts") == (
        "Unable to export transcript data."
    )


@pytest.mark.asyncio
async def test_configured_export_root_that_is_a_file_keeps_chat_error(
    tmp_path: Path,
) -> None:
    runtime = await _runtime(tmp_path, backend="fake")
    root = tmp_path / "exports"
    root.write_text("file, not directory", encoding="utf-8")
    assert await _execute(runtime, "/export csv") == "Unable to export transcript data."
