"""
Tests for friday-cli input handling.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from prompt_toolkit.document import Document

from friday_cli import (
    CommandCompleter,
    InputHandler,
    create_friday_input_handler,
    FRIDAY_COMMANDS,
    FRIDAY_COMMAND_DESCRIPTIONS,
)


class TestCommandCompleter:
    """Test command auto-completion."""

    def test_completes_commands_starting_with_slash(self):
        completer = CommandCompleter(commands=["help", "history", "exit"])
        document = Document("/h")

        completions = list(completer.get_completions(document, None))

        assert len(completions) == 2  # help, history
        # display is FormattedText, convert to string for comparison
        displays = [str(c.text) for c in completions]
        assert "/help" in displays
        assert "/history" in displays

    def test_no_completion_without_slash(self):
        completer = CommandCompleter(commands=["help", "history"])
        document = Document("h")

        completions = list(completer.get_completions(document, None))

        assert len(completions) == 0

    def test_completes_all_commands_with_just_slash(self):
        completer = CommandCompleter(commands=["help", "exit"])
        document = Document("/")

        completions = list(completer.get_completions(document, None))

        assert len(completions) == 2

    def test_includes_meta_descriptions(self):
        completer = CommandCompleter(
            commands=["help"],
            meta_dict={"help": "Show help"},
        )
        document = Document("/h")

        completions = list(completer.get_completions(document, None))

        assert len(completions) == 1
        # display_meta may be FormattedText or plain string
        meta = completions[0].display_meta
        meta_str = str(meta) if hasattr(meta, '__str__') else meta
        assert "Show help" in meta_str

    def test_case_insensitive_matching(self):
        completer = CommandCompleter(commands=["Help", "HISTORY"])
        document = Document("/h")

        completions = list(completer.get_completions(document, None))

        assert len(completions) == 2


class TestInputHandler:
    """Test InputHandler class."""

    def test_initialization_defaults(self):
        handler = InputHandler()

        assert handler.prompt_name == "User"
        assert handler.multiline is False
        assert handler._completer is None

    def test_initialization_with_commands(self):
        handler = InputHandler(
            prompt_name="Alice",
            commands=["help", "exit"],
        )

        assert handler.prompt_name == "Alice"
        assert handler._completer is not None

    def test_initialization_with_history_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "subdir" / "history"
            handler = InputHandler(history_file=history_path)

            # Directory should be created
            assert history_path.parent.exists()

    def test_update_commands(self):
        handler = InputHandler(commands=["old1", "old2"])

        handler.update_commands(["new1", "new2"], {"new1": "Description"})

        # Verify completer was updated
        assert handler._completer is not None
        document = Document("/new")
        completions = list(handler._completer.get_completions(document, None))
        assert len(completions) == 2

    def test_add_to_history(self):
        handler = InputHandler()

        handler.add_to_history("test command 1")
        handler.add_to_history("test command 2")

        history = handler.history
        assert "test command 1" in history
        assert "test command 2" in history


class TestFridayInputHandler:
    """Test pre-configured Friday input handler."""

    def test_create_friday_input_handler(self):
        handler = create_friday_input_handler(user_name="TestUser")

        assert handler.prompt_name == "TestUser"
        assert handler._completer is not None

        # Should complete Friday commands
        document = Document("/he")
        completions = list(handler._completer.get_completions(document, None))
        assert len(completions) == 1  # "help"
        assert completions[0].text == "/help"

    def test_friday_commands_list(self):
        # Verify essential commands exist
        assert "help" in FRIDAY_COMMANDS
        assert "exit" in FRIDAY_COMMANDS
        assert "history" in FRIDAY_COMMANDS
        assert "entities" in FRIDAY_COMMANDS
        assert "tools" in FRIDAY_COMMANDS

    def test_friday_command_descriptions(self):
        # Verify descriptions exist for key commands
        assert "help" in FRIDAY_COMMAND_DESCRIPTIONS
        assert FRIDAY_COMMAND_DESCRIPTIONS["help"] == "Show available commands"
        assert "exit" in FRIDAY_COMMAND_DESCRIPTIONS
        assert "entities" in FRIDAY_COMMAND_DESCRIPTIONS

    def test_all_commands_have_descriptions(self):
        # Every command should have a description
        for cmd in FRIDAY_COMMANDS:
            assert cmd in FRIDAY_COMMAND_DESCRIPTIONS, f"Missing description for /{cmd}"


class TestInputHandlerPromptFormatting:
    """Test prompt formatting."""

    def test_format_prompt_html(self):
        handler = InputHandler(prompt_name="Alice")
        prompt = handler._format_prompt()

        # Should return HTML formatted text
        assert "Alice" in prompt.value

    def test_continuation_prompt(self):
        handler = InputHandler(multiline=True)
        continuation = handler._format_continuation(width=80, line_number=2, is_soft_wrap=False)

        assert continuation == "... "


class TestKeyBindings:
    """Test custom key bindings."""

    def test_key_bindings_created(self):
        handler = InputHandler()

        # Should have key bindings defined
        assert handler._key_bindings is not None


class TestHistoryPersistence:
    """Test history file persistence."""

    def test_history_file_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "history"

            # Create handler - should create the file directory
            handler = InputHandler(history_file=history_path)

            # Add to history (appends to internal list)
            handler.add_to_history("/help")

            # Verify it's in the handler's history
            assert "/help" in handler.history

    def test_history_stores_multiple_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "history"
            handler = InputHandler(history_file=history_path)

            handler.add_to_history("/help")
            handler.add_to_history("/history")
            handler.add_to_history("/entities")

            history = handler.history
            assert len(history) >= 3
            assert "/help" in history
            assert "/history" in history
            assert "/entities" in history

    def test_in_memory_history_not_persisted(self):
        handler = InputHandler()  # No history file
        handler.add_to_history("command1")

        # Create another handler - should not share history
        handler2 = InputHandler()
        assert "command1" not in handler2.history
