"""
Tests for friday-cli display functions.
"""

import io
from unittest.mock import patch

import pytest
from rich.console import Console

from friday_cli import (
    display_error,
    display_warning,
    display_success,
    display_info,
    display_json,
    display_code,
    display_table,
    display_banner,
    display_panel,
    display_help,
    set_console,
    get_console,
)


@pytest.fixture
def captured_console():
    """Create a console that captures output for testing."""
    string_io = io.StringIO()
    console = Console(file=string_io, force_terminal=True, width=80)
    set_console(console)
    yield string_io
    # Reset to default
    set_console(None)


class TestStatusMessages:
    """Test status message display functions."""

    def test_display_error(self, captured_console):
        display_error("Something went wrong")
        output = captured_console.getvalue()
        assert "Something went wrong" in output
        assert "✗" in output

    def test_display_error_with_exception(self, captured_console):
        try:
            raise ValueError("Test error")
        except ValueError as e:
            display_error("Operation failed", exception=e)
        output = captured_console.getvalue()
        assert "Operation failed" in output
        assert "ValueError" in output

    def test_display_warning(self, captured_console):
        display_warning("Be careful")
        output = captured_console.getvalue()
        assert "Be careful" in output
        assert "⚠" in output

    def test_display_success(self, captured_console):
        display_success("Task completed")
        output = captured_console.getvalue()
        assert "Task completed" in output
        assert "✓" in output

    def test_display_info(self, captured_console):
        display_info("FYI: This is info")
        output = captured_console.getvalue()
        assert "FYI: This is info" in output
        assert "ℹ" in output


class TestStructuredData:
    """Test structured data display functions."""

    def test_display_json(self, captured_console):
        data = {"key": "value", "number": 42}
        display_json(data)
        output = captured_console.getvalue()
        assert "key" in output
        assert "value" in output

    def test_display_json_with_title(self, captured_console):
        data = {"status": "ok"}
        display_json(data, title="Response")
        output = captured_console.getvalue()
        assert "Response" in output

    def test_display_code(self, captured_console):
        code = "def hello():\n    return 'world'"
        display_code(code, language="python")
        output = captured_console.getvalue()
        assert "def" in output
        assert "hello" in output

    def test_display_table(self, captured_console):
        data = [
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "25"},
        ]
        display_table(data, title="Users")
        output = captured_console.getvalue()
        assert "Alice" in output
        assert "Bob" in output
        assert "Users" in output

    def test_display_table_empty(self, captured_console):
        display_table([], title="Empty")
        output = captured_console.getvalue()
        assert "No data" in output


class TestBannerAndPanel:
    """Test banner and panel display functions."""

    def test_display_banner(self, captured_console):
        display_banner("Friday CLI", subtitle="Testing", version="1.0.0")
        output = captured_console.getvalue()
        assert "Friday CLI" in output
        assert "1.0.0" in output

    def test_display_panel(self, captured_console):
        display_panel("Important content", title="Notice", style="info")
        output = captured_console.getvalue()
        assert "Important content" in output
        assert "Notice" in output


class TestDomainSpecific:
    """Test domain-specific display functions."""

    def test_display_help(self, captured_console):
        commands = {
            "/help": "Show help",
            "/exit": "Exit the program",
        }
        display_help(commands)
        output = captured_console.getvalue()
        assert "/help" in output
        assert "Show help" in output

    def test_display_help_with_tips(self, captured_console):
        commands = {"/test": "Test command"}
        tips = ["Tip 1", "Tip 2"]
        display_help(commands, tips=tips)
        output = captured_console.getvalue()
        assert "Tip 1" in output


class TestConsoleManagement:
    """Test console singleton management."""

    def test_get_console_creates_singleton(self):
        # Reset any existing console
        set_console(None)
        console1 = get_console()
        console2 = get_console()
        assert console1 is console2

    def test_set_console_overrides(self):
        custom_console = Console(force_terminal=True)
        set_console(custom_console)
        assert get_console() is custom_console
        # Reset
        set_console(None)


class TestThinkingIndicator:
    """Test ThinkingIndicator class for async spinner."""

    def test_start_stop(self):
        from friday_cli import ThinkingIndicator

        indicator = ThinkingIndicator("Thinking...")
        assert not indicator.is_running

        indicator.start()
        assert indicator.is_running

        indicator.stop()
        assert not indicator.is_running

    def test_stop_idempotent(self):
        from friday_cli import ThinkingIndicator

        indicator = ThinkingIndicator("Thinking...")
        indicator.start()

        # Multiple stops should be safe
        indicator.stop()
        indicator.stop()
        indicator.stop()

        assert not indicator.is_running

    def test_start_idempotent(self):
        from friday_cli import ThinkingIndicator

        indicator = ThinkingIndicator("Thinking...")

        # Multiple starts should be safe
        indicator.start()
        indicator.start()

        assert indicator.is_running
        indicator.stop()

    def test_context_manager(self):
        from friday_cli import ThinkingIndicator

        indicator = ThinkingIndicator("Processing...")

        with indicator:
            assert indicator.is_running

        assert not indicator.is_running

    def test_update_message(self):
        from friday_cli import ThinkingIndicator

        indicator = ThinkingIndicator("Step 1...")
        indicator.start()
        indicator.update("Step 2...")
        # Just verify no exception
        indicator.stop()

    def test_update_when_not_running(self):
        from friday_cli import ThinkingIndicator

        indicator = ThinkingIndicator("Thinking...")
        # Should not raise even when not running
        indicator.update("New message")

    def test_custom_spinner_type(self):
        from friday_cli import ThinkingIndicator

        indicator = ThinkingIndicator("Loading...", spinner_type="line")
        indicator.start()
        assert indicator.is_running
        indicator.stop()

    def test_random_thinking_creates_indicator(self):
        from friday_cli import ThinkingIndicator
        from friday_cli.cli_config import DEFAULT_THINKING_MESSAGES, set_cli_config

        # Reset to defaults
        set_cli_config(None)

        indicator = ThinkingIndicator.random_thinking()
        # Message should be from the default list
        assert indicator.message in DEFAULT_THINKING_MESSAGES
        indicator.stop()

    def test_random_tool_processing_creates_indicator(self):
        from friday_cli import ThinkingIndicator
        from friday_cli.cli_config import DEFAULT_TOOL_PROCESSING_MESSAGES, set_cli_config

        # Reset to defaults
        set_cli_config(None)

        indicator = ThinkingIndicator.random_tool_processing()
        # Message should be from the default tool list
        assert indicator.message in DEFAULT_TOOL_PROCESSING_MESSAGES
        indicator.stop()

    def test_random_thinking_uses_config(self):
        from friday_cli import ThinkingIndicator, CLIConfig, set_cli_config

        # Set custom config with specific messages
        custom_config = CLIConfig.from_dict({
            "spinner": {
                "thinking_messages": ["Custom thinking..."],
                "randomize": True,
            }
        })
        set_cli_config(custom_config)

        indicator = ThinkingIndicator.random_thinking()
        assert indicator.message == "Custom thinking..."

        # Cleanup
        set_cli_config(None)

    def test_random_thinking_no_randomize(self):
        from friday_cli import ThinkingIndicator, CLIConfig, set_cli_config

        # Set config with randomize=False
        custom_config = CLIConfig.from_dict({
            "spinner": {
                "thinking_messages": ["First", "Second", "Third"],
                "randomize": False,
            }
        })
        set_cli_config(custom_config)

        # Should always return first message
        for _ in range(5):
            indicator = ThinkingIndicator.random_thinking()
            assert indicator.message == "First"

        # Cleanup
        set_cli_config(None)

    def test_spinner_type_from_config(self):
        from friday_cli import ThinkingIndicator, CLIConfig, set_cli_config

        # Set custom spinner type
        custom_config = CLIConfig.from_dict({
            "spinner": {
                "spinner_type": "line",
            }
        })
        set_cli_config(custom_config)

        indicator = ThinkingIndicator.random_thinking()
        assert indicator.spinner_type == "line"

        # Cleanup
        set_cli_config(None)

    def test_default_spinner_type_from_config(self):
        from friday_cli import ThinkingIndicator, set_cli_config

        # Reset to defaults
        set_cli_config(None)

        # When no spinner_type passed, should use config default
        indicator = ThinkingIndicator("Test...")
        assert indicator.spinner_type == "dots"

    def test_spinner_style_from_config(self):
        from friday_cli import ThinkingIndicator, CLIConfig, set_cli_config

        # Set custom spinner styles
        custom_config = CLIConfig.from_dict({
            "spinner": {
                "text_style": "bold magenta",
                "spinner_style": "yellow",
            }
        })
        set_cli_config(custom_config)

        # Start indicator to verify styles are applied (no crash)
        indicator = ThinkingIndicator.random_thinking()
        indicator.start()
        assert indicator.is_running
        indicator.stop()

        # Cleanup
        set_cli_config(None)
