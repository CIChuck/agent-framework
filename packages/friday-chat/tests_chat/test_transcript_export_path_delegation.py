"""Chat registry exports keep their file effects through neutral path rules."""

from __future__ import annotations

from pathlib import Path

import pytest
from friday_chat.commands import transcript as chat_transcript
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeTranscriptStore, FridayRuntime, build_runtime
from friday_chat.session import SessionIdentity
from friday_runtime.transcript_export_paths import (
    resolve_export_directory,
    safe_export_path,
)


def _runtime(export_root: Path) -> FridayRuntime:
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "fake/export-path"},
            "transcript": {
                "export_directory": str(export_root),
                "capture_raw_prompts": True,
            },
            "tools": {"enabled": False},
        }
    )
    return build_runtime(config, session_identity=SessionIdentity("path-session"))


@pytest.mark.asyncio
async def test_context_and_prompt_registry_exports_use_shared_neutral_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "nested" / "exports"
    runtime = _runtime(root)
    registry = build_default_registry()
    context = RegistryCommandContext(
        runtime=runtime,
        registry=registry,
        last_context="context π",
        last_prompt="prompt α",
    )
    root_calls: list[str | None] = []

    def tracking_root(raw_directory: str | None) -> Path:
        root_calls.append(raw_directory)
        return resolve_export_directory(raw_directory)

    monkeypatch.setattr(chat_transcript, "resolve_export_directory", tracking_root)

    handled, context_result = await registry.execute("/context --file", context)
    assert handled and context_result is not None
    assert context_result.output == (
        f"context π\n\nExported context to {root / 'friday_context.txt'}"
    )
    handled, prompt_result = await registry.execute("/prompt --file", context)
    assert handled and prompt_result is not None
    assert prompt_result.output == (
        f"prompt α\n\nExported prompt to {root / 'friday_prompt.txt'}"
    )

    assert root_calls == [str(root), str(root)]
    assert (root / "friday_context.txt").read_bytes() == "context π".encode()
    assert (root / "friday_prompt.txt").read_bytes() == "prompt α".encode()
    assert {path.name for path in root.iterdir()} == {
        "friday_context.txt",
        "friday_prompt.txt",
    }


@pytest.mark.asyncio
async def test_transcript_registry_exports_delegate_safe_paths_and_keep_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "exports"
    runtime = _runtime(root)
    store = FakeTranscriptStore(session_id="path-session")
    await store.record_turn("hello", "world")
    await store.record_context_log("raw prompt", "raw response")
    runtime.transcript = store
    registry = build_default_registry()
    context = RegistryCommandContext(runtime=runtime, registry=registry)
    path_calls: list[tuple[Path, tuple[str, ...]]] = []

    def tracking_path(path_root: Path, *parts: str) -> Path:
        path_calls.append((path_root, parts))
        return safe_export_path(path_root, *parts)

    monkeypatch.setattr(chat_transcript, "safe_export_path", tracking_path)

    outputs: list[str] = []
    for command in (
        "/transcript export",
        "/export csv",
        "/export jsonl",
        "/export training",
        "/export markdown",
        "/export-prompts",
    ):
        handled, result = await registry.execute(command, context)
        assert handled and result is not None
        outputs.append(result.output)

    directories = tuple(root.glob("transcript-export-*"))
    assert len(directories) == 1
    directory = directories[0]
    assert outputs == [
        f"Exported 1 session and 1 entry to {directory}",
        f"Exported current session (1 entry) to {root / 'friday_current_session.csv'}",
        f"Exported current session (1 entry) to {root / 'friday_current_session.jsonl'}",
        f"Exported current session (1 entry) to {root / 'friday_current_session_training.jsonl'}",
        f"Exported current session (1 entry) to {root / 'friday_current_session.md'}",
        f"Exported 1 prompt record to {root / 'friday_prompts.json'}",
    ]
    assert (directory / "sessions.csv").is_file()
    assert (directory / "entries.csv").is_file()
    assert {path.name for path in root.iterdir() if path.is_file()} == {
        "friday_current_session.csv",
        "friday_current_session.jsonl",
        "friday_current_session_training.jsonl",
        "friday_current_session.md",
        "friday_prompts.json",
    }
    assert (root, (directory.name,)) in path_calls
    assert (directory, ("sessions.csv",)) in path_calls
    assert (directory, ("entries.csv",)) in path_calls
    assert (root, ("friday_prompts.json",)) in path_calls
    assert all(path.is_relative_to(root) for path, _parts in path_calls)


@pytest.mark.asyncio
@pytest.mark.parametrize("command", ["/context --file", "/prompt --file"])
async def test_shared_registry_exports_preserve_root_file_error(
    tmp_path: Path,
    command: str,
) -> None:
    root = tmp_path / "exports"
    root.write_text("existing", encoding="utf-8")
    runtime = _runtime(root)
    registry = build_default_registry()
    context = RegistryCommandContext(
        runtime=runtime,
        registry=registry,
        last_context="context",
        last_prompt="prompt",
    )

    with pytest.raises(FileExistsError):
        await registry.execute(command, context)

    assert root.read_text(encoding="utf-8") == "existing"
