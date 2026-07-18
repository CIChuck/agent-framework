"""Smoke tests for the FridayV2 CLI."""

import re
from pathlib import Path

import pytest
from friday_chat import __version__
from friday_chat.cli import app
from typer.testing import CliRunner

PACKAGE_PYPROJECT = Path("packages/friday-chat/pyproject.toml")
EXAMPLE_CONFIG = Path("packages/friday-chat/config.example.yaml")


def _set_placeholder_env(path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for env_name in sorted(set(re.findall(r"\$\{([A-Z0-9_]+)\}", path.read_text()))):
        monkeypatch.setenv(env_name, f"test-{env_name.lower()}")


def test_cli_help() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "FridayV2 chat application" in result.output
    assert "--version" in result.output
    assert "--config" in result.output
    assert "--cli-config" in result.output


def test_cli_version() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert f"friday-chat {__version__}" in result.output


def test_package_declares_console_script() -> None:
    text = PACKAGE_PYPROJECT.read_text()

    assert '[project.scripts]' in text
    assert 'friday-chat = "friday_chat.cli:app"' in text


def test_cli_config_starts_interactive_app(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "llm:\n"
        "  model: openai/test-chat-model\n"
        "chat:\n"
        "  system_prompt: You are Friday.\n"
    )
    runner = CliRunner()

    result = runner.invoke(app, ["--config", str(config_path)], input="hello\n/q\n")

    assert result.exit_code == 0
    assert "Friday: hello" in result.output
    assert "Goodbye." in result.output


def test_cli_accepts_explicit_cli_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "llm:\n"
        "  model: openai/test-chat-model\n"
        "chat:\n"
        "  user_name: Chuck\n"
        "  assistant_name: Friday\n"
        "  system_prompt: You are Friday.\n",
        encoding="utf-8",
    )
    cli_config_path = tmp_path / "custom-cli.yaml"
    cli_config_path.write_text(
        "theme:\n"
        "  error: bold red\n"
        "spinner:\n"
        "  spinner_type: dots12\n"
        "  randomize: false\n"
        "  thinking_messages:\n"
        "    - Thinking...\n"
        "  tool_messages:\n"
        "    - Tooling...\n",
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["--config", str(config_path), "--cli-config", str(cli_config_path)],
        input="/q\n",
    )

    assert result.exit_code == 0
    assert "Friday" in result.output
    assert "Goodbye." in result.output


def test_cli_config_starts_with_full_example_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_placeholder_env(EXAMPLE_CONFIG, monkeypatch)
    runner = CliRunner()

    result = runner.invoke(app, ["--config", str(EXAMPLE_CONFIG)], input="/q\n")

    assert result.exit_code == 0
    assert "Goodbye." in result.output


def test_cli_real_runtime_starts_without_uv_or_provider_call(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "llm:\n"
        "  model: openai/test-chat-model\n"
        "embedding:\n"
        "  model: openai/test-embedding-model\n"
        "memory:\n"
        f"  persist_directory: {tmp_path / 'vector'}\n"
        "transcript:\n"
        f"  export_directory: {tmp_path / 'exports'}\n"
        "lifecycle:\n"
        "  enabled: false\n"
        "tools:\n"
        "  registry: []\n"
    )
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["--runtime", "real", "--config", str(config_path)],
        input="/q\n",
    )

    assert result.exit_code == 0
    assert "Goodbye." in result.output
    assert (tmp_path / "exports" / "friday_transcripts.sqlite").exists()


def test_cli_config_validation_error_exits_nonzero(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("chat:\n  assistant_name: Friday\n")
    runner = CliRunner()

    result = runner.invoke(app, ["--config", str(config_path)])

    assert result.exit_code == 1
    assert "Config error:" in result.output
    assert "llm" in result.output
