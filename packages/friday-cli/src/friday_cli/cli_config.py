# mypy: ignore-errors
"""
CLI configuration for theming and styling.

Loads optional cli-config.yaml for customizing the look and feel
of the Friday CLI terminal interface.

Ref: docs/archive/build-plans/completed/friday-core-legacy/memory-chat-v2-prd.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ThemeConfig:
    """Color theme configuration for Rich console output."""

    error: str = "bold red"
    warning: str = "bold yellow"
    success: str = "bold green"
    info: str = "bold blue"
    muted: str = "dim"
    highlight: str = "bold cyan"

    def to_dict(self) -> dict[str, str]:
        """Convert to dict for Rich Theme constructor."""
        return {
            "error": self.error,
            "warning": self.warning,
            "success": self.success,
            "info": self.info,
            "muted": self.muted,
            "highlight": self.highlight,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ThemeConfig:
        """Create from dictionary, using defaults for missing keys."""
        return cls(
            error=data.get("error", "bold red"),
            warning=data.get("warning", "bold yellow"),
            success=data.get("success", "bold green"),
            info=data.get("info", "bold blue"),
            muted=data.get("muted", "dim"),
            highlight=data.get("highlight", "bold cyan"),
        )


@dataclass
class IconsConfig:
    """Icon configuration for status messages."""

    error: str = "✗"
    warning: str = "⚠"
    success: str = "✓"
    info: str = "ℹ"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IconsConfig:
        """Create from dictionary, using defaults for missing keys."""
        return cls(
            error=data.get("error", "✗"),
            warning=data.get("warning", "⚠"),
            success=data.get("success", "✓"),
            info=data.get("info", "ℹ"),
        )


@dataclass
class PromptConfig:
    """Prompt styling configuration for input handler."""

    style: str = "bold cyan"
    name_style: str = "bold cyan"
    separator_style: str = "white"
    continuation_style: str = "gray"

    def to_style_dict(self) -> dict[str, str]:
        """Convert to dict for prompt_toolkit Style.from_dict()."""
        return {
            "prompt": self.style,
            "prompt.name": self.name_style,
            "prompt.separator": self.separator_style,
            "continuation": self.continuation_style,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PromptConfig:
        """Create from dictionary, using defaults for missing keys."""
        return cls(
            style=data.get("style", "bold cyan"),
            name_style=data.get("name_style", "bold cyan"),
            separator_style=data.get("separator_style", "white"),
            continuation_style=data.get("continuation_style", "gray"),
        )


# Default thinking messages - a mix of classic and humorous
DEFAULT_THINKING_MESSAGES: list[str] = [
    "Thinking...",
    "Pondering the possibilities...",
    "Consulting the neural networks...",
    "Brewing some thoughts...",
    "Crunching the cognitive cookies...",
    "Warming up the brain cells...",
    "Spinning up the thought hamsters...",
    "Searching the knowledge vaults...",
    "Assembling an intelligent response...",
    "Loading wisdom.dll...",
]

DEFAULT_TOOL_PROCESSING_MESSAGES: list[str] = [
    "Processing tool results...",
    "Analyzing the data...",
    "Digesting the output...",
    "Making sense of things...",
    "Connecting the dots...",
    "Synthesizing results...",
]


@dataclass
class SpinnerConfig:
    """Configuration for the thinking spinner."""

    # Messages shown while waiting for initial LLM response
    thinking_messages: list[str] = field(
        default_factory=lambda: list(DEFAULT_THINKING_MESSAGES)
    )

    # Messages shown while processing tool results (Re-Act loop)
    tool_messages: list[str] = field(
        default_factory=lambda: list(DEFAULT_TOOL_PROCESSING_MESSAGES)
    )

    # Spinner animation type (dots, line, dots12, bouncingBar, etc.)
    spinner_type: str = "dots"

    # Whether to randomly select messages (False = always use first message)
    randomize: bool = True

    # Color/style for the message text (Rich style format)
    text_style: str = "bold cyan"

    # Color/style for the spinner animation symbols (Rich style format)
    spinner_style: str = "cyan"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpinnerConfig:
        """Create from dictionary, using defaults for missing keys."""
        # Support legacy 'style' key for backwards compatibility
        text_style = data.get("text_style", data.get("style", "bold cyan"))
        return cls(
            thinking_messages=data.get(
                "thinking_messages", list(DEFAULT_THINKING_MESSAGES)
            ),
            tool_messages=data.get(
                "tool_messages", list(DEFAULT_TOOL_PROCESSING_MESSAGES)
            ),
            spinner_type=data.get("spinner_type", "dots"),
            randomize=data.get("randomize", True),
            text_style=text_style,
            spinner_style=data.get("spinner_style", "cyan"),
        )


@dataclass
class CLIConfig:
    """
    Complete CLI configuration container.

    Holds theme, icons, prompt styling, and spinner settings.
    Can be loaded from cli-config.yaml or use defaults.
    """

    theme: ThemeConfig = field(default_factory=ThemeConfig)
    icons: IconsConfig = field(default_factory=IconsConfig)
    prompt: PromptConfig = field(default_factory=PromptConfig)
    spinner: SpinnerConfig = field(default_factory=SpinnerConfig)

    # Path to config file (if loaded from file)
    config_path: Path | None = None

    @classmethod
    def from_yaml(cls, path: str | Path) -> CLIConfig:
        """
        Load CLI configuration from a YAML file.

        Args:
            path: Path to cli-config.yaml

        Returns:
            CLIConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
        """
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"CLI config file not found: {config_path}")

        with open(config_path) as f:
            raw = yaml.safe_load(f) or {}

        return cls(
            theme=ThemeConfig.from_dict(raw.get("theme", {})),
            icons=IconsConfig.from_dict(raw.get("icons", {})),
            prompt=PromptConfig.from_dict(raw.get("prompt", {})),
            spinner=SpinnerConfig.from_dict(raw.get("spinner", {})),
            config_path=config_path,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CLIConfig:
        """
        Create CLI configuration from a dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            CLIConfig instance
        """
        return cls(
            theme=ThemeConfig.from_dict(data.get("theme", {})),
            icons=IconsConfig.from_dict(data.get("icons", {})),
            prompt=PromptConfig.from_dict(data.get("prompt", {})),
            spinner=SpinnerConfig.from_dict(data.get("spinner", {})),
        )

    @classmethod
    def defaults(cls) -> CLIConfig:
        """Create CLI configuration with all defaults."""
        return cls()


# Global CLI config instance (singleton pattern)
_cli_config: CLIConfig | None = None


def get_cli_config() -> CLIConfig:
    """
    Get the current CLI configuration.

    Returns the global config if set, otherwise returns defaults.
    """
    global _cli_config
    if _cli_config is None:
        _cli_config = CLIConfig.defaults()
    return _cli_config


def set_cli_config(config: CLIConfig | None) -> None:
    """
    Set the global CLI configuration.

    Args:
        config: CLIConfig instance, or None to reset to defaults
    """
    global _cli_config
    _cli_config = config


def load_cli_config(config_path: str | Path | None = None) -> CLIConfig:
    """
    Load CLI configuration from file or use defaults.

    If config_path is provided, looks for cli-config.yaml in the same directory.
    If cli-config.yaml doesn't exist, returns defaults without error.

    Args:
        config_path: Path to main config.yaml (cli-config.yaml is loaded
                     from the same directory), or direct path to cli-config.yaml

    Returns:
        CLIConfig instance (from file or defaults)
    """
    global _cli_config

    if config_path is None:
        _cli_config = CLIConfig.defaults()
        return _cli_config

    path = Path(config_path)

    # If path points to main config.yaml, look for cli-config.yaml next to it
    if path.name != "cli-config.yaml":
        cli_config_path = path.parent / "cli-config.yaml"
    else:
        cli_config_path = path

    if cli_config_path.exists():
        try:
            _cli_config = CLIConfig.from_yaml(cli_config_path)
            logger.info(f"Loaded CLI config from {cli_config_path}")
        except Exception as e:
            logger.warning(f"Failed to load CLI config: {e}. Using defaults.")
            _cli_config = CLIConfig.defaults()
    else:
        logger.debug(f"No cli-config.yaml found at {cli_config_path}. Using defaults.")
        _cli_config = CLIConfig.defaults()

    return _cli_config
