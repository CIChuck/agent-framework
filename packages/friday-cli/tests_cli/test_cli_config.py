"""
Tests for CLI configuration loading.
"""

import tempfile
from pathlib import Path

import pytest
from friday_cli.cli_config import (
    DEFAULT_THINKING_MESSAGES,
    DEFAULT_TOOL_PROCESSING_MESSAGES,
    CLIConfig,
    IconsConfig,
    PromptConfig,
    SpinnerConfig,
    ThemeConfig,
    get_cli_config,
    load_cli_config,
    set_cli_config,
)


class TestThemeConfig:
    """Test ThemeConfig class."""

    def test_defaults(self):
        theme = ThemeConfig()

        assert theme.error == "bold red"
        assert theme.warning == "bold yellow"
        assert theme.success == "bold green"
        assert theme.info == "bold blue"
        assert theme.muted == "dim"
        assert theme.highlight == "bold cyan"

    def test_from_dict_partial(self):
        theme = ThemeConfig.from_dict({"error": "red", "success": "green"})

        assert theme.error == "red"
        assert theme.success == "green"
        # Defaults for missing keys
        assert theme.warning == "bold yellow"
        assert theme.info == "bold blue"

    def test_to_dict(self):
        theme = ThemeConfig()
        d = theme.to_dict()

        assert d["error"] == "bold red"
        assert d["warning"] == "bold yellow"
        assert len(d) == 6


class TestIconsConfig:
    """Test IconsConfig class."""

    def test_defaults(self):
        icons = IconsConfig()

        assert icons.error == "✗"
        assert icons.warning == "⚠"
        assert icons.success == "✓"
        assert icons.info == "ℹ"

    def test_from_dict_partial(self):
        icons = IconsConfig.from_dict({"error": "[X]", "success": "[OK]"})

        assert icons.error == "[X]"
        assert icons.success == "[OK]"
        # Defaults for missing keys
        assert icons.warning == "⚠"
        assert icons.info == "ℹ"

    def test_ascii_alternatives(self):
        icons = IconsConfig.from_dict(
            {
                "error": "ERROR:",
                "warning": "WARN:",
                "success": "OK:",
                "info": "INFO:",
            }
        )

        assert icons.error == "ERROR:"
        assert icons.warning == "WARN:"
        assert icons.success == "OK:"
        assert icons.info == "INFO:"


class TestPromptConfig:
    """Test PromptConfig class."""

    def test_defaults(self):
        prompt = PromptConfig()

        assert prompt.style == "bold cyan"
        assert prompt.name_style == "bold cyan"
        assert prompt.separator_style == "white"
        assert prompt.continuation_style == "gray"

    def test_from_dict_partial(self):
        prompt = PromptConfig.from_dict({"style": "bold green"})

        assert prompt.style == "bold green"
        # Defaults for missing keys
        assert prompt.separator_style == "white"

    def test_to_style_dict(self):
        prompt = PromptConfig()
        d = prompt.to_style_dict()

        assert d["prompt"] == "bold cyan"
        assert d["prompt.name"] == "bold cyan"
        assert d["prompt.separator"] == "white"
        assert d["continuation"] == "gray"


class TestSpinnerConfig:
    """Test SpinnerConfig class."""

    def test_defaults(self):
        spinner = SpinnerConfig()

        assert spinner.thinking_messages == DEFAULT_THINKING_MESSAGES
        assert spinner.tool_messages == DEFAULT_TOOL_PROCESSING_MESSAGES
        assert spinner.spinner_type == "dots"
        assert spinner.randomize is True
        assert spinner.text_style == "bold cyan"
        assert spinner.spinner_style == "cyan"

    def test_default_messages_not_empty(self):
        # Ensure we have sensible defaults
        assert len(DEFAULT_THINKING_MESSAGES) >= 5
        assert len(DEFAULT_TOOL_PROCESSING_MESSAGES) >= 3
        assert "Thinking..." in DEFAULT_THINKING_MESSAGES

    def test_from_dict_partial(self):
        spinner = SpinnerConfig.from_dict(
            {
                "spinner_type": "line",
                "randomize": False,
            }
        )

        assert spinner.spinner_type == "line"
        assert spinner.randomize is False
        # Defaults for missing keys
        assert spinner.thinking_messages == DEFAULT_THINKING_MESSAGES
        assert spinner.text_style == "bold cyan"
        assert spinner.spinner_style == "cyan"

    def test_custom_styles(self):
        spinner = SpinnerConfig.from_dict(
            {
                "text_style": "bold magenta",
                "spinner_style": "yellow",
            }
        )

        assert spinner.text_style == "bold magenta"
        assert spinner.spinner_style == "yellow"

    def test_legacy_style_key(self):
        """Test backwards compatibility with old 'style' key."""
        spinner = SpinnerConfig.from_dict(
            {
                "style": "bold green",  # Old key name
            }
        )

        # Should map to text_style
        assert spinner.text_style == "bold green"
        # spinner_style should still be default
        assert spinner.spinner_style == "cyan"

    def test_from_dict_custom_messages(self):
        custom_thinking = ["Working...", "Processing..."]
        custom_tool = ["Analyzing..."]

        spinner = SpinnerConfig.from_dict(
            {
                "thinking_messages": custom_thinking,
                "tool_messages": custom_tool,
            }
        )

        assert spinner.thinking_messages == custom_thinking
        assert spinner.tool_messages == custom_tool

    def test_messages_are_independent_copies(self):
        # Each SpinnerConfig should get its own copy
        spinner1 = SpinnerConfig()
        spinner2 = SpinnerConfig()

        spinner1.thinking_messages.append("New message")

        # spinner2 should not be affected
        assert "New message" not in spinner2.thinking_messages


class TestCLIConfig:
    """Test CLIConfig class."""

    def test_defaults(self):
        config = CLIConfig.defaults()

        assert config.theme.error == "bold red"
        assert config.icons.success == "✓"
        assert config.prompt.style == "bold cyan"
        assert config.config_path is None

    def test_from_dict(self):
        config = CLIConfig.from_dict(
            {
                "theme": {"error": "red"},
                "icons": {"error": "[X]"},
            }
        )

        assert config.theme.error == "red"
        assert config.icons.error == "[X]"
        # Other defaults
        assert config.theme.success == "bold green"
        assert config.prompt.style == "bold cyan"

    def test_from_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
theme:
  error: "red"
  success: "green"
icons:
  error: "[ERR]"
prompt:
  style: "bold magenta"
""")
            f.flush()

            config = CLIConfig.from_yaml(f.name)

            assert config.theme.error == "red"
            assert config.theme.success == "green"
            assert config.theme.warning == "bold yellow"  # default
            assert config.icons.error == "[ERR]"
            assert config.prompt.style == "bold magenta"
            assert config.config_path == Path(f.name)

    def test_from_yaml_not_found(self):
        with pytest.raises(FileNotFoundError):
            CLIConfig.from_yaml("/nonexistent/cli-config.yaml")

    def test_from_yaml_empty(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            f.flush()

            config = CLIConfig.from_yaml(f.name)

            # All defaults
            assert config.theme.error == "bold red"
            assert config.icons.success == "✓"


class TestGlobalConfig:
    """Test global config management functions."""

    def setup_method(self):
        """Reset global config before each test."""
        set_cli_config(None)

    def test_get_cli_config_returns_defaults(self):
        config = get_cli_config()

        assert config.theme.error == "bold red"
        assert config.icons.success == "✓"

    def test_set_cli_config(self):
        custom = CLIConfig.from_dict({"theme": {"error": "magenta"}})
        set_cli_config(custom)

        config = get_cli_config()
        assert config.theme.error == "magenta"

    def test_set_cli_config_none_resets(self):
        custom = CLIConfig.from_dict({"theme": {"error": "magenta"}})
        set_cli_config(custom)
        set_cli_config(None)

        # Next get should return new defaults
        config = get_cli_config()
        assert config.theme.error == "bold red"


class TestLoadCLIConfig:
    """Test load_cli_config function."""

    def setup_method(self):
        """Reset global config before each test."""
        set_cli_config(None)

    def test_load_with_no_path_uses_defaults(self):
        config = load_cli_config(None)

        assert config.theme.error == "bold red"

    def test_load_from_cli_config_yaml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cli_config_path = Path(tmpdir) / "cli-config.yaml"
            cli_config_path.write_text("""
theme:
  error: "bold magenta"
icons:
  success: "[DONE]"
""")

            config = load_cli_config(cli_config_path)

            assert config.theme.error == "bold magenta"
            assert config.icons.success == "[DONE]"

    def test_load_relative_to_main_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create main config.yaml (content doesn't matter)
            main_config = Path(tmpdir) / "config.yaml"
            main_config.write_text("llm:\n  model: test\n")

            # Create cli-config.yaml next to it
            cli_config = Path(tmpdir) / "cli-config.yaml"
            cli_config.write_text("""
theme:
  info: "bold white"
""")

            # Load by passing main config path
            config = load_cli_config(main_config)

            assert config.theme.info == "bold white"
            # Others are defaults
            assert config.theme.error == "bold red"

    def test_load_missing_cli_config_uses_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create main config.yaml but no cli-config.yaml
            main_config = Path(tmpdir) / "config.yaml"
            main_config.write_text("llm:\n  model: test\n")

            config = load_cli_config(main_config)

            # Should use defaults without error
            assert config.theme.error == "bold red"
            assert config.icons.success == "✓"

    def test_load_sets_global_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cli_config_path = Path(tmpdir) / "cli-config.yaml"
            cli_config_path.write_text("theme:\n  error: cyan\n")

            load_cli_config(cli_config_path)

            # Global config should be updated
            config = get_cli_config()
            assert config.theme.error == "cyan"
