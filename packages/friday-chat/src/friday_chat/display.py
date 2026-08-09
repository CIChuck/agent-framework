"""Display and heartbeat boundary for FridayV2."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol, cast

import yaml
from friday_cli import (
    CLIConfig,
    ThinkingIndicator,
    get_console,
    reset_console,
    set_cli_config,
)
from rich.panel import Panel
from rich.text import Text

from friday_chat.input_sources import AsyncPromptCallable, AsyncPromptReader

HeartbeatKind = Literal["thinking", "tool"]
DisplayConfigSource = Literal["explicit", "sibling", "defaults"]

DEFAULT_BANNER_ART = """\
          ███████╗██████╗ ██╗██████╗  █████╗ ██╗   ██╗
         ██╔════╝██╔══██╗██║██╔══██╗██╔══██╗╚██╗ ██╔╝
        █████╗  ██████╔╝██║██║  ██║███████║ ╚████╔╝
       ██╔══╝  ██╔══██╗██║██║  ██║██╔══██║  ╚██╔╝
      ██║     ██║  ██║██║██████╔╝██║  ██║   ██║
     ╚═╝     ╚═╝  ╚═╝╚═╝╚═════╝ ╚═╝  ╚═╝   ╚═╝\
"""

DEFAULT_BANNER_GRADIENT = (
    "#4A90D9",
    "#5B7FD9",
    "#6C6ED9",
    "#7D5DD9",
    "#8E4CD9",
    "#9F5CB8",
    "#B06C97",
    "#C17C76",
    "#B08090",
)


class FridayChatDisplayConfigError(ValueError):
    """Raised when FridayV2 CLI display configuration cannot be loaded."""


class Heartbeat(Protocol):
    """Progress indicator used while waiting for model responses."""

    def start(self) -> None:
        """Start the indicator."""

    def stop(self) -> None:
        """Stop the indicator."""


class HeartbeatFactory(Protocol):
    """Factory for configured heartbeat indicators."""

    def create_heartbeat(self, kind: HeartbeatKind) -> Heartbeat:
        """Create one heartbeat for the requested wait state."""


class DisplayController(HeartbeatFactory, Protocol):
    """Display operations required by the app lifecycle."""

    def render_banner(self, *, assistant_name: str, version: str) -> None:
        """Render startup banner or greeting."""

    def prompt_text(self, *, user_name: str) -> str:
        """Return the interactive input prompt string."""

    def clear_screen(self) -> None:
        """Clear the interactive terminal display."""


@dataclass(frozen=True)
class ResponseDisplayConfig:
    """Terminal styling for assistant chat responses."""

    prefix: bool = True
    name_style: str = "bold bright_green"
    separator_style: str = "bright_green"
    text_style: str = "bright_green"

    @classmethod
    def from_dict(cls, data: object) -> ResponseDisplayConfig:
        if not isinstance(data, dict):
            return cls()
        return cls(
            prefix=bool(data.get("prefix", True)),
            name_style=str(data.get("name_style", "bold bright_green")),
            separator_style=str(data.get("separator_style", "bright_green")),
            text_style=str(data.get("text_style", "bright_green")),
        )


@dataclass(frozen=True)
class BannerDisplayConfig:
    """Terminal startup banner configuration."""

    enabled: bool = True
    style: Literal["panel", "ascii"] = "panel"
    title: str = "Friday"
    subtitle: str = "{assistant_name} CLI"
    show_version: bool = True
    art: str = DEFAULT_BANNER_ART
    gradient: tuple[str, ...] = DEFAULT_BANNER_GRADIENT
    border_style: str = "cyan"
    title_style: str = "bold cyan"
    subtitle_style: str = "muted"
    version_style: str = "dim cyan"
    shadow_style: str = "#1a1a2e"
    bottom_shadow_width: int = 52
    tips_enabled: bool = False
    tips_title: str = "Tips for getting started:"
    tips: tuple[str, ...] = ()
    tips_title_style: str = "dim white"
    tip_number_style: str = "dim white"
    tip_text_style: str = "white"
    command_style: str = "bold #9F5CB8"

    @classmethod
    def from_dict(cls, data: object) -> BannerDisplayConfig:
        if not isinstance(data, dict):
            return cls()
        style = str(data.get("style", "panel")).strip().lower()
        if style not in {"panel", "ascii"}:
            style = "panel"
        tips = data.get("tips", ())
        gradient = data.get("gradient", DEFAULT_BANNER_GRADIENT)
        return cls(
            enabled=bool(data.get("enabled", True)),
            style=cast(Literal["panel", "ascii"], style),
            title=str(data.get("title", "Friday")),
            subtitle=str(data.get("subtitle", "{assistant_name} CLI")),
            show_version=bool(data.get("show_version", True)),
            art=str(data.get("art", DEFAULT_BANNER_ART)),
            gradient=_string_tuple(gradient, DEFAULT_BANNER_GRADIENT),
            border_style=str(data.get("border_style", "cyan")),
            title_style=str(data.get("title_style", "bold cyan")),
            subtitle_style=str(data.get("subtitle_style", "muted")),
            version_style=str(data.get("version_style", "dim cyan")),
            shadow_style=str(data.get("shadow_style", "#1a1a2e")),
            bottom_shadow_width=int(data.get("bottom_shadow_width", 52)),
            tips_enabled=bool(data.get("tips_enabled", False)),
            tips_title=str(data.get("tips_title", "Tips for getting started:")),
            tips=_string_tuple(tips, ()),
            tips_title_style=str(data.get("tips_title_style", "dim white")),
            tip_number_style=str(data.get("tip_number_style", "dim white")),
            tip_text_style=str(data.get("tip_text_style", "white")),
            command_style=str(data.get("command_style", "bold #9F5CB8")),
        )


@dataclass(frozen=True)
class DisplayConfigResult:
    """Resolved FridayV2 CLI display configuration."""

    config: CLIConfig
    banner: BannerDisplayConfig
    response: ResponseDisplayConfig
    source: DisplayConfigSource
    path: Path | None = None


class NoopHeartbeat:
    """Heartbeat used by tests and non-interactive app construction."""

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None


class NoopHeartbeatFactory:
    """Default heartbeat factory that performs no terminal work."""

    def create_heartbeat(self, _kind: HeartbeatKind) -> Heartbeat:
        return NoopHeartbeat()


@dataclass
class FridayCliHeartbeat:
    """Production heartbeat adapter over ``friday-cli`` progress indicators."""

    indicator: ThinkingIndicator

    @classmethod
    def for_kind(cls, kind: HeartbeatKind) -> FridayCliHeartbeat:
        if kind == "tool":
            return cls(ThinkingIndicator.random_tool_processing())
        return cls(ThinkingIndicator.random_thinking())

    def start(self) -> None:
        self.indicator.start()

    def stop(self) -> None:
        self.indicator.stop()


@dataclass(frozen=True)
class FridayCliDisplay:
    """Production display adapter using ``friday-cli`` components."""

    config: CLIConfig
    banner: BannerDisplayConfig = BannerDisplayConfig()
    response: ResponseDisplayConfig = ResponseDisplayConfig()

    def render_banner(self, *, assistant_name: str, version: str) -> None:
        render_startup_banner(
            assistant_name=assistant_name,
            version=version,
            config=self.banner,
        )

    def prompt_text(self, *, user_name: str) -> str:
        return f"{user_name}: "

    def create_heartbeat(self, kind: HeartbeatKind) -> Heartbeat:
        return FridayCliHeartbeat.for_kind(kind)

    def clear_screen(self) -> None:
        """Delegate terminal clearing to the configured Rich console."""
        get_console().clear()


class FridayCliOutputSink:
    """Console output sink backed by Friday CLI Rich console."""

    def __init__(
        self,
        response_config: ResponseDisplayConfig | None = None,
    ) -> None:
        self.response_config = response_config or ResponseDisplayConfig()
        self._stream_assistant_name = "Friday"
        self._stream_prefix_checked = True
        self._stream_prefix_buffer = ""

    async def write(self, text: str) -> None:
        get_console().print(text, markup=False)

    async def write_assistant_response(self, text: str, *, assistant_name: str) -> None:
        get_console().print(
            assistant_response_text(
                text,
                assistant_name=assistant_name,
                config=self.response_config,
            )
        )

    async def begin_assistant_response(self, *, assistant_name: str) -> None:
        self._stream_assistant_name = assistant_name
        self._stream_prefix_checked = False
        self._stream_prefix_buffer = ""
        if self.response_config.prefix:
            get_console().print(
                Text.assemble(
                    (assistant_name, self.response_config.name_style),
                    (": ", self.response_config.separator_style),
                ),
                end="",
            )

    async def write_chunk(self, text: str) -> None:
        sys.stdout.write(text)
        sys.stdout.flush()

    async def write_assistant_chunk(self, text: str) -> None:
        chunk = self._strip_streamed_assistant_prefix(text)
        if chunk:
            get_console().print(
                Text(chunk, style=self.response_config.text_style),
                end="",
            )

    def _strip_streamed_assistant_prefix(self, text: str) -> str:
        if self._stream_prefix_checked:
            return text
        (
            self._stream_prefix_buffer,
            stripped,
            self._stream_prefix_checked,
        ) = _strip_stream_prefix_chunk(
            buffer=self._stream_prefix_buffer,
            chunk=text,
            assistant_name=self._stream_assistant_name,
        )
        return stripped

    async def finish_stream(self) -> None:
        if not self._stream_prefix_checked and self._stream_prefix_buffer:
            get_console().print(
                Text(
                    self._stream_prefix_buffer,
                    style=self.response_config.text_style,
                ),
                end="",
            )
            self._stream_prefix_buffer = ""
            self._stream_prefix_checked = True
        sys.stdout.write("\n")
        sys.stdout.flush()


class FridayCliInputSource:
    """Console input source with configured prompt text."""

    def __init__(
        self,
        prompt: str,
        *,
        prompt_fn: AsyncPromptCallable | None = None,
    ) -> None:
        self._prompt = prompt
        self._reader = AsyncPromptReader(prompt_fn)

    async def read(self) -> str:
        return await self._reader.read(self._prompt)


def resolve_display_config(
    *,
    config_path: Path | None,
    cli_config_path: Path | None = None,
) -> DisplayConfigResult:
    """Resolve and activate FridayV2 CLI display configuration."""
    if cli_config_path is not None:
        return _load_display_config(cli_config_path, source="explicit")

    if config_path is not None:
        sibling = config_path.parent / "cli-config.yaml"
        if sibling.exists():
            return _load_display_config(sibling, source="sibling")

    result = DisplayConfigResult(
        config=CLIConfig.defaults(),
        banner=BannerDisplayConfig(),
        response=ResponseDisplayConfig(),
        source="defaults",
    )
    set_cli_config(result.config)
    reset_console()
    return result


def _load_display_config(path: Path, *, source: DisplayConfigSource) -> DisplayConfigResult:
    try:
        config = CLIConfig.from_yaml(path)
        raw = yaml.safe_load(path.read_text()) or {}
    except FileNotFoundError as exc:
        raise FridayChatDisplayConfigError(
            f"CLI display config file not found: {path}"
        ) from exc
    except Exception as exc:
        raise FridayChatDisplayConfigError(
            f"Failed to load CLI display config {path}: {exc}"
        ) from exc
    response = ResponseDisplayConfig.from_dict(
        raw.get("response", {}) if isinstance(raw, dict) else {}
    )
    banner = BannerDisplayConfig.from_dict(
        raw.get("banner", {}) if isinstance(raw, dict) else {}
    )
    result = DisplayConfigResult(
        config=config,
        banner=banner,
        response=response,
        source=source,
        path=path,
    )
    set_cli_config(config)
    reset_console()
    return result


def render_startup_banner(
    *,
    assistant_name: str,
    version: str,
    config: BannerDisplayConfig | None = None,
) -> None:
    """Render the configured FridayV2 startup banner."""
    banner_config = config or BannerDisplayConfig()
    if not banner_config.enabled:
        return
    if banner_config.style == "ascii":
        _render_ascii_banner(
            assistant_name=assistant_name,
            version=version,
            config=banner_config,
        )
        return
    _render_panel_banner(
        assistant_name=assistant_name,
        version=version,
        config=banner_config,
    )


def assistant_response_text(
    text: str,
    *,
    assistant_name: str,
    config: ResponseDisplayConfig | None = None,
) -> Text:
    """Return Rich-styled assistant response text for non-streaming output."""
    response_config = config or ResponseDisplayConfig()
    body = strip_assistant_prefix(text, assistant_name=assistant_name)
    if not response_config.prefix:
        return Text(body, style=response_config.text_style)
    return Text.assemble(
        (assistant_name, response_config.name_style),
        (": ", response_config.separator_style),
        (body, response_config.text_style),
    )


def format_assistant_response(text: str, *, assistant_name: str) -> str:
    """Return plain assistant response text with exactly one configured prefix."""
    body = strip_assistant_prefix(text, assistant_name=assistant_name)
    return f"{assistant_name}: {body}"


def strip_assistant_prefix(text: str, *, assistant_name: str) -> str:
    """Remove a duplicate model-emitted assistant prefix from display output."""
    prefix = f"{assistant_name}:"
    if text.startswith(prefix):
        return text[len(prefix) :].lstrip()
    return text


def _render_panel_banner(
    *,
    assistant_name: str,
    version: str,
    config: BannerDisplayConfig,
) -> None:
    content = Text()
    content.append(
        _format_banner_value(
            config.title,
            assistant_name=assistant_name,
            version=version,
        ),
        style=config.title_style,
    )
    subtitle = _format_banner_value(
        config.subtitle,
        assistant_name=assistant_name,
        version=version,
    )
    if subtitle:
        content.append("\n")
        content.append(subtitle, style=config.subtitle_style)
    if config.show_version:
        content.append("\n")
        content.append(f"v{version}", style=config.version_style)
    get_console().print(
        Panel(
            content,
            border_style=config.border_style,
            expand=False,
            padding=(1, 4),
        )
    )


def _render_ascii_banner(
    *,
    assistant_name: str,
    version: str,
    config: BannerDisplayConfig,
) -> None:
    console = get_console()
    console.print()
    art = _format_banner_value(
        config.art,
        assistant_name=assistant_name,
        version=version,
    )
    for line in art.splitlines():
        console.print(_gradient_line(line, config.gradient, config.shadow_style))
    if config.bottom_shadow_width > 0:
        console.print(
            _bottom_shadow(config.bottom_shadow_width, config.gradient),
        )
    _render_ascii_banner_metadata(
        assistant_name=assistant_name,
        version=version,
        config=config,
    )
    if config.tips_enabled and config.tips:
        _render_banner_tips(config)
    console.print()


def _render_ascii_banner_metadata(
    *,
    assistant_name: str,
    version: str,
    config: BannerDisplayConfig,
) -> None:
    subtitle = _format_banner_value(
        config.subtitle,
        assistant_name=assistant_name,
        version=version,
    )
    if not subtitle and not config.show_version:
        console = get_console()
        console.print()
        return
    text = Text()
    if subtitle:
        text.append(subtitle, style=config.subtitle_style)
    if config.show_version:
        if subtitle:
            text.append("  ")
        text.append(f"v{version}", style=config.version_style)
    get_console().print(text)
    get_console().print()


def _render_banner_tips(config: BannerDisplayConfig) -> None:
    tips = Text()
    tips.append(f"{config.tips_title}\n", style=config.tips_title_style)
    for index, tip in enumerate(config.tips, start=1):
        tips.append(f"{index}. ", style=config.tip_number_style)
        _append_tip(tips, tip, config.command_style, config.tip_text_style)
        if index < len(config.tips):
            tips.append("\n")
    get_console().print(tips)


def _append_tip(text: Text, tip: str, command_style: str, text_style: str) -> None:
    parts = tip.split("`")
    for index, part in enumerate(parts):
        if not part:
            continue
        text.append(part, style=command_style if index % 2 else text_style)


def _gradient_line(line: str, gradient: tuple[str, ...], shadow_style: str) -> Text:
    text = Text()
    line_len = len(line.rstrip())
    for index, char in enumerate(line):
        if char == " ":
            text.append(char)
            continue
        color = _gradient_color(index, line_len, gradient)
        text.append(char, style=f"bold {color}")
    if line.rstrip():
        text.append("░", style=shadow_style)
    return text


def _bottom_shadow(width: int, gradient: tuple[str, ...]) -> Text:
    text = Text("    ")
    for index in range(width):
        color = _gradient_color(index, width, gradient)
        text.append("░", style=f"dim {color}")
    return text


def _gradient_color(index: int, width: int, gradient: tuple[str, ...]) -> str:
    if not gradient:
        return "cyan"
    if width <= 1:
        return gradient[0]
    progress = index / max(width - 1, 1)
    color_index = int(progress * (len(gradient) - 1))
    return gradient[color_index]


def _format_banner_value(value: str, *, assistant_name: str, version: str) -> str:
    return value.replace("{assistant_name}", assistant_name).replace(
        "{version}",
        version,
    )


def _string_tuple(value: object, default: tuple[str, ...]) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return default
    return tuple(str(item) for item in value)


def _is_possible_prefix(buffer: str, *, assistant_name: str) -> bool:
    return f"{assistant_name}:".startswith(buffer)


def _is_complete_prefix(buffer: str, *, assistant_name: str) -> bool:
    return buffer.startswith(f"{assistant_name}:")


def _strip_complete_prefix(buffer: str, *, assistant_name: str) -> str:
    return buffer[len(f"{assistant_name}:") :].lstrip()


def _strip_stream_prefix_chunk(
    *,
    buffer: str,
    chunk: str,
    assistant_name: str,
) -> tuple[str, str, bool]:
    updated = buffer + chunk
    if _is_complete_prefix(updated, assistant_name=assistant_name):
        return "", _strip_complete_prefix(updated, assistant_name=assistant_name), True
    if _is_possible_prefix(updated, assistant_name=assistant_name):
        return updated, "", False
    return "", updated, True


def heartbeat_events(factory: HeartbeatFactory) -> Sequence[str]:
    """Return recorded heartbeat events when a fake factory exposes them."""
    events = getattr(factory, "events", ())
    if isinstance(events, list):
        return tuple(str(event) for event in events)
    if isinstance(events, tuple):
        return tuple(str(event) for event in events)
    return ()


__all__ = [
    "DisplayConfigResult",
    "DisplayConfigSource",
    "DisplayController",
    "BannerDisplayConfig",
    "FridayChatDisplayConfigError",
    "FridayCliDisplay",
    "FridayCliHeartbeat",
    "FridayCliInputSource",
    "FridayCliOutputSink",
    "Heartbeat",
    "HeartbeatFactory",
    "HeartbeatKind",
    "NoopHeartbeat",
    "NoopHeartbeatFactory",
    "ResponseDisplayConfig",
    "assistant_response_text",
    "format_assistant_response",
    "heartbeat_events",
    "render_startup_banner",
    "resolve_display_config",
    "strip_assistant_prefix",
]
