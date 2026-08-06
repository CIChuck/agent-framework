"""Display configuration and heartbeat tests for FridayV2."""

from __future__ import annotations

from pathlib import Path

import pytest
from friday_chat.app import FridayChatApp, ListInputSource
from friday_chat.config import FridayChatConfig
from friday_chat.display import (
    BannerDisplayConfig,
    DisplayConfigResult,
    FridayChatDisplayConfigError,
    FridayCliOutputSink,
    Heartbeat,
    HeartbeatKind,
    ResponseDisplayConfig,
    assistant_response_text,
    format_assistant_response,
    render_startup_banner,
    resolve_display_config,
    strip_assistant_prefix,
)
from friday_chat.runtime import build_runtime

EXAMPLE_CLI_CONFIG = Path("packages/friday-chat/cli-config.example.yaml")


class RecordingHeartbeat:
    """Heartbeat that records lifecycle events."""

    def __init__(self, events: list[str], kind: HeartbeatKind) -> None:
        self._events = events
        self._kind = kind

    def start(self) -> None:
        self._events.append(f"{self._kind}:start")

    def stop(self) -> None:
        self._events.append(f"{self._kind}:stop")


class RecordingDisplay:
    """Display controller used by app lifecycle tests."""

    def __init__(self) -> None:
        self.banners: list[tuple[str, str]] = []
        self.events: list[str] = []

    def render_banner(self, *, assistant_name: str, version: str) -> None:
        self.banners.append((assistant_name, version))

    def prompt_text(self, *, user_name: str) -> str:
        return f"{user_name}: "

    def create_heartbeat(self, kind: HeartbeatKind) -> Heartbeat:
        return RecordingHeartbeat(self.events, kind)


def _write_cli_config(path: Path, *, error_style: str) -> None:
    path.write_text(
        "theme:\n"
        f"  error: {error_style}\n"
        "icons:\n"
        "  error: X\n"
        "banner:\n"
        "  enabled: true\n"
        "  style: ascii\n"
        "  subtitle: '{assistant_name} custom CLI'\n"
        "  show_version: false\n"
        "  art: CUSTOM\n"
        "  gradient:\n"
        "    - '#00ff00'\n"
        "  tips_enabled: true\n"
        "  tips:\n"
        "    - '`/help` for more information.'\n"
        "prompt:\n"
        "  style: bold cyan\n"
        "response:\n"
        "  prefix: true\n"
        "  name_style: bold bright_green\n"
        "  separator_style: bright_green\n"
        "  text_style: bright_green\n"
        "spinner:\n"
        "  spinner_type: dots12\n"
        "  randomize: false\n"
        "  thinking_messages:\n"
        "    - Thinking...\n"
        "  tool_messages:\n"
        "    - Tooling...\n",
        encoding="utf-8",
    )


def test_display_config_auto_loads_sibling_cli_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("llm:\n  model: openai/test-chat-model\n", encoding="utf-8")
    _write_cli_config(tmp_path / "cli-config.yaml", error_style="bold magenta")

    result = resolve_display_config(config_path=config_path)

    assert result.source == "sibling"
    assert result.path == tmp_path / "cli-config.yaml"
    assert result.config.theme.error == "bold magenta"
    assert result.banner.style == "ascii"
    assert result.banner.subtitle == "{assistant_name} custom CLI"
    assert result.banner.show_version is False
    assert result.banner.art == "CUSTOM"
    assert result.banner.gradient == ("#00ff00",)
    assert result.banner.tips == ("`/help` for more information.",)
    assert result.response.text_style == "bright_green"
    assert result.config.spinner.spinner_type == "dots12"


def test_display_config_explicit_override_wins(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("llm:\n  model: openai/test-chat-model\n", encoding="utf-8")
    _write_cli_config(tmp_path / "cli-config.yaml", error_style="bold red")
    explicit = tmp_path / "custom-cli.yaml"
    _write_cli_config(explicit, error_style="bold green")

    result = resolve_display_config(
        config_path=config_path,
        cli_config_path=explicit,
    )

    assert result.source == "explicit"
    assert result.path == explicit
    assert result.config.theme.error == "bold green"


def test_display_config_defaults_when_sibling_missing(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("llm:\n  model: openai/test-chat-model\n", encoding="utf-8")

    result = resolve_display_config(config_path=config_path)

    assert isinstance(result, DisplayConfigResult)
    assert result.source == "defaults"
    assert result.path is None
    assert result.config.theme.error == "bold red"
    assert result.banner == BannerDisplayConfig()
    assert result.response == ResponseDisplayConfig()


def test_display_config_invalid_yaml_fails_actionably(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("llm:\n  model: openai/test-chat-model\n", encoding="utf-8")
    cli_config_path = tmp_path / "cli-config.yaml"
    cli_config_path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(FridayChatDisplayConfigError, match="Failed to load"):
        resolve_display_config(config_path=config_path)


def test_packaged_example_cli_config_loads() -> None:
    result = resolve_display_config(
        config_path=None,
        cli_config_path=EXAMPLE_CLI_CONFIG,
    )

    assert result.banner.style == "ascii"
    assert "███████" in result.banner.art
    assert result.config.spinner.tool_messages[0] == "Gluing..."


async def test_app_renders_configured_startup_banner() -> None:
    runtime = build_runtime(
        FridayChatConfig.model_validate({"llm": {"model": "openai/test-chat-model"}})
    )
    display = RecordingDisplay()
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["/q"]),
        display=display,
        version="9.9.9",
    )

    result = await app.run()

    assert result.exit_reason == "command_exit"
    assert display.banners == [("Friday", "9.9.9")]


def test_startup_banner_can_be_disabled(
    capsys: pytest.CaptureFixture[str],
) -> None:
    render_startup_banner(
        assistant_name="Friday",
        version="1.2.3",
        config=BannerDisplayConfig(enabled=False),
    )

    assert capsys.readouterr().out == ""


def test_panel_startup_banner_uses_configurable_text(
    capsys: pytest.CaptureFixture[str],
) -> None:
    render_startup_banner(
        assistant_name="Friday",
        version="1.2.3",
        config=BannerDisplayConfig(
            style="panel",
            title="{assistant_name}",
            subtitle="{assistant_name} custom CLI",
            show_version=True,
            border_style="green",
            title_style="bold green",
        ),
    )

    output = capsys.readouterr().out
    assert "Friday" in output
    assert "Friday custom CLI" in output
    assert "v1.2.3" in output


def test_ascii_startup_banner_uses_configurable_art_and_tips(
    capsys: pytest.CaptureFixture[str],
) -> None:
    render_startup_banner(
        assistant_name="Friday",
        version="1.2.3",
        config=BannerDisplayConfig(
            style="ascii",
            art="FRIDAY",
            gradient=("#00ff00",),
            subtitle="{assistant_name} custom CLI",
            bottom_shadow_width=3,
            tips_enabled=True,
            tips=("`/help` for more information.",),
        ),
    )

    output = capsys.readouterr().out
    assert "FRIDAY" in output
    assert "Friday custom CLI" in output
    assert "Tips for getting started:" in output
    assert "/help" in output


def test_assistant_response_formatting_uses_configured_name_once() -> None:
    assert format_assistant_response("hello", assistant_name="Friday") == (
        "Friday: hello"
    )
    assert format_assistant_response("Friday: hello", assistant_name="Friday") == (
        "Friday: hello"
    )
    assert strip_assistant_prefix("Friday: hello", assistant_name="Friday") == "hello"


def test_assistant_response_text_applies_configured_rich_styles() -> None:
    text = assistant_response_text(
        "Friday: hello",
        assistant_name="Friday",
        config=ResponseDisplayConfig(
            name_style="bold green",
            separator_style="green",
            text_style="bright_green",
        ),
    )

    assert text.plain == "Friday: hello"
    assert "bold green" in str(text.spans[0].style)
    assert "bright_green" in str(text.spans[-1].style)


async def test_generic_output_sink_preserves_literal_help_arguments(
    capsys: pytest.CaptureFixture[str],
) -> None:
    sink = FridayCliOutputSink()

    await sink.write(
        "Usage: /help [command]\nUsage: /run-tool <name> [json]"
    )

    assert capsys.readouterr().out == (
        "Usage: /help [command]\nUsage: /run-tool <name> [json]\n"
    )


async def test_streaming_sink_strips_duplicate_assistant_prefix(
    capsys: pytest.CaptureFixture[str],
) -> None:
    sink = FridayCliOutputSink(
        ResponseDisplayConfig(
            prefix=True,
            name_style="green",
            separator_style="green",
            text_style="green",
        )
    )

    await sink.begin_assistant_response(assistant_name="Friday")
    await sink.write_assistant_chunk("Fri")
    await sink.write_assistant_chunk("day: hello")
    await sink.finish_stream()

    assert capsys.readouterr().out == "Friday: hello\n"
