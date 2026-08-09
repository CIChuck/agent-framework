"""Transcript and export command tests for FridayV2."""

from __future__ import annotations

import json
from pathlib import Path

from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeTranscriptStore, FridayRuntime, build_runtime
from friday_chat.turns.processor import TurnProcessor


def _runtime(
    tmp_path: Path,
    *,
    capture_raw_prompts: bool = False,
) -> FridayRuntime:
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "openai/test-chat-model"},
            "transcript": {
                "export_directory": str(tmp_path),
                "capture_raw_prompts": capture_raw_prompts,
            },
        }
    )
    return build_runtime(config)


async def test_sessions_and_transcript_commands_use_fake_transcript(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path)
    await TurnProcessor(runtime).process("hello")
    registry = build_default_registry()
    context = RegistryCommandContext(runtime=runtime, registry=registry)

    _, sessions = await registry.execute("/sessions", context)
    _, transcript = await registry.execute("/transcript", context)

    assert sessions is not None
    assert (
        f"- {runtime.session_identity.value} (1 turns) [current]" in sessions.output
    )
    assert transcript is not None
    assert f"Transcript: {runtime.session_identity.value}" in transcript.output
    assert "User: hello" in transcript.output


async def test_transcript_export_writes_database_csv(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    await TurnProcessor(runtime).process("hello")
    registry = build_default_registry()
    context = RegistryCommandContext(runtime=runtime, registry=registry)

    _, result = await registry.execute("/transcript export", context)

    assert result is not None
    directories = list(tmp_path.glob("transcript-export-*"))
    assert len(directories) == 1
    sessions_path = directories[0] / "sessions.csv"
    entries_path = directories[0] / "entries.csv"
    assert sessions_path.exists()
    assert entries_path.exists()
    assert '"session_id","turn_number"' in entries_path.read_text()
    assert str(directories[0]) in result.output


async def test_current_session_export_formats(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    await TurnProcessor(runtime).process("hello")
    registry = build_default_registry()
    context = RegistryCommandContext(runtime=runtime, registry=registry)

    for command in (
        "/export csv",
        "/export jsonl",
        "/export markdown",
        "/export training",
    ):
        _, result = await registry.execute(command, context)
        assert result is not None
        assert result.output.startswith("Exported current session")

    assert (tmp_path / "friday_current_session.csv").exists()
    assert (tmp_path / "friday_current_session.jsonl").exists()
    assert (tmp_path / "friday_current_session.md").exists()
    assert (tmp_path / "friday_current_session_training.jsonl").exists()


async def test_export_prompts_handles_missing_context_log(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    registry = build_default_registry()
    context = RegistryCommandContext(runtime=runtime, registry=registry)

    _, result = await registry.execute("/export-prompts", context)

    assert result is not None
    assert result.output.endswith(
        "Enable transcript.capture_raw_prompts to capture them."
    )
    assert not (tmp_path / "friday_prompts.json").exists()


async def test_export_prompts_writes_context_log(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path, capture_raw_prompts=True)
    await TurnProcessor(runtime).process("capture prompt")
    registry = build_default_registry()
    context = RegistryCommandContext(runtime=runtime, registry=registry)

    _, result = await registry.execute("/export-prompts", context)

    assert result is not None
    path = tmp_path / "friday_prompts.json"
    payload = json.loads(path.read_text())
    assert len(payload) == 1
    assert payload[0]["prompt"].startswith("System:")
    assert isinstance(runtime.transcript, FakeTranscriptStore)
    assert str(path) in result.output
