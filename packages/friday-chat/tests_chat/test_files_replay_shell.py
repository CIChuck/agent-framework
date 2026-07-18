"""File, replay, and shell tests for FridayV2."""

from __future__ import annotations

from pathlib import Path

from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.cli import app as cli_app
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.replay import ReplayService, load_replay_csv
from friday_chat.runtime import FakeMemoryController, build_runtime
from friday_chat.shell import ShellService
from typer.testing import CliRunner


def _context() -> RegistryCommandContext:
    config = FridayChatConfig.model_validate(
        {"llm": {"model": "openai/test-chat-model"}}
    )
    registry = build_default_registry()
    return RegistryCommandContext(runtime=build_runtime(config), registry=registry)


async def test_read_dispatches_supported_extensions(tmp_path: Path) -> None:
    files = {
        "notes.txt": "a\nb\nc\n",
        "notes.md": "# Title\n",
        "config.yaml": "a: 1\n",
        "data.json": '{"b": 2, "a": 1}',
        "script.py": "print('hi')\n",
        "data.csv": "a,b\n1,2\n",
        "data.tsv": "a\tb\n1\t2\n",
        "report.pdf": "%PDF placeholder",
        "doc.docx": "placeholder",
        "book.xlsx": "placeholder",
    }
    registry = build_default_registry()
    context = _context()

    outputs: list[str] = []
    for name, content in files.items():
        path = tmp_path / name
        path.write_text(content, encoding="utf-8")
        _, result = await registry.execute(f"/read {path}", context)
        assert result is not None
        outputs.append(result.output)

    assert any("Reader: text" in output for output in outputs)
    assert any("Reader: csv" in output and "Rows: 2" in output for output in outputs)
    assert any("Reader: xlsx" in output and "Sheets: Sheet1" in output for output in outputs)


async def test_read_errors_and_malformed_line_limit(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("\n".join(str(index) for index in range(120)), encoding="utf-8")
    directory = tmp_path / "folder"
    directory.mkdir()
    unsupported = tmp_path / "file.bin"
    unsupported.write_text("x", encoding="utf-8")
    registry = build_default_registry()
    context = _context()

    _, missing = await registry.execute(f"/read {tmp_path / 'missing.txt'}", context)
    _, dir_result = await registry.execute(f"/read {directory}", context)
    _, unsupported_result = await registry.execute(f"/read {unsupported}", context)
    _, limited = await registry.execute(f"/read {path} --lines=bad", context)

    assert missing is not None and "File not found" in missing.output
    assert dir_result is not None and "Path is a directory" in dir_result.output
    assert unsupported_result is not None and "Unsupported file type" in unsupported_result.output
    assert limited is not None and "Truncated: true" in limited.output
    assert "119" not in limited.output


async def test_ingest_records_source_metadata_and_list_ingested(tmp_path: Path) -> None:
    path = tmp_path / "notes.md"
    path.write_text("# Notes\nUseful content", encoding="utf-8")
    registry = build_default_registry()
    context = _context()
    assert context.runtime is not None

    _, ingest = await registry.execute(f"/ingest {path} project notes", context)
    _, listed = await registry.execute("/list-ingested", context)

    assert ingest is not None and "chunks: 1" in ingest.output
    assert isinstance(context.runtime.memory, FakeMemoryController)
    assert context.runtime.memory.ingested_documents[0]["source_path"] == str(
        path.resolve()
    )
    assert context.runtime.memory.ingested_documents[0]["description"] == "project notes"
    assert listed is not None and str(path.resolve()) in listed.output


async def test_replay_service_orders_resets_and_processes_fixture(tmp_path: Path) -> None:
    csv_path = tmp_path / "replay.csv"
    csv_path.write_text(
        "turn_number,user_message,assistant_message\n"
        "2,Second,old second\n"
        "1,First,old first\n"
        "3,,ignored\n",
        encoding="utf-8",
    )
    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    service = ReplayService(sleep=fake_sleep)

    result = await service.replay_csv(csv_path, delay_seconds=0.5)

    assert [turn.user_message for turn in load_replay_csv(csv_path)] == ["First", "Second"]
    assert result.processed_turns == 2
    assert "transcripts: archived" in result.reset_output
    assert service.processed_messages == ["First", "Second"]
    assert delays == [0.5]


async def test_replay_command_handles_missing_invalid_and_empty_csv(tmp_path: Path) -> None:
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("turn_number,user_message,assistant_message\n", encoding="utf-8")
    registry = build_default_registry()
    context = _context()

    _, missing = await registry.execute(f"/replay {tmp_path / 'missing.csv'}", context)
    _, invalid_delay = await registry.execute(f"/replay {empty_csv} nope", context)
    _, empty = await registry.execute(f"/replay {empty_csv}", context)

    assert missing is not None and "Replay CSV not found" in missing.output
    assert invalid_delay is not None and invalid_delay.output == "Replay delay must be numeric."
    assert empty is not None and empty.output == "Replay CSV contains no user messages."


def test_cli_replay_mode(tmp_path: Path) -> None:
    csv_path = tmp_path / "replay.csv"
    csv_path.write_text(
        "turn_number,user_message,assistant_message\n1,Hello,Old\n",
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(cli_app, ["--replay", str(csv_path), "--replay-delay", "0"])

    assert result.exit_code == 0
    assert f"Replayed 1 turns from {csv_path}" in result.output


async def test_shell_service_disabled_by_default_and_app_route() -> None:
    output = ListOutputSink()
    app = FridayChatApp(
        input_source=ListInputSource(["!echo hi"]),
        output_sink=output,
    )

    await app.run()

    assert "Shell execution is disabled." in output.values[0]


async def test_shell_service_enabled_success_nonzero_stderr_and_timeout(
    tmp_path: Path,
) -> None:
    service = ShellService(enabled=True, cwd=tmp_path, timeout_seconds=0.05)

    success = await service.execute("pwd")
    nonzero = await service.execute("python -c 'import sys; print(\"bad\", file=sys.stderr); sys.exit(2)'")
    timeout = await service.execute(
        "python -c 'import time; time.sleep(1)'"
    )

    assert success.returncode == 0
    assert str(tmp_path) in success.stdout
    assert nonzero.returncode == 2
    assert "bad" in nonzero.stderr
    assert timeout.timed_out is True
    assert "timed out" in timeout.format()
