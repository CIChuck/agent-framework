# mypy: ignore-errors
"""
Input handling with Prompt Toolkit.

Provides readline-style editing, history, auto-completion, and multi-line input.

Ref: docs/build-plan/memory-chat-v2-prd.md
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from .cli_config import get_cli_config


def _build_prompt_style() -> Style:
    """Build prompt_toolkit Style from current CLI configuration."""
    config = get_cli_config()
    return Style.from_dict(config.prompt.to_style_dict())


# Default style for the prompt (for backwards compatibility)
DEFAULT_STYLE = Style.from_dict(
    {
        "prompt": "bold cyan",
        "prompt.name": "bold cyan",
        "prompt.separator": "white",
        "continuation": "gray",
    }
)


class CommandCompleter(Completer):
    """
    Auto-completer for slash commands.

    Provides tab completion for commands starting with '/'.
    """

    def __init__(
        self,
        commands: list[str],
        meta_dict: dict[str, str] | None = None,
    ):
        """
        Initialize command completer.

        Args:
            commands: List of command names (without leading slash)
            meta_dict: Optional dict of command -> description for tooltip
        """
        self.commands = sorted(commands)
        self.meta_dict = meta_dict or {}

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        """Generate completions for the current input."""
        text = document.text_before_cursor

        # Only complete if starting with /
        if not text.startswith("/"):
            return

        # Get the partial command (without /)
        word = text[1:].lower()

        for cmd in self.commands:
            if cmd.lower().startswith(word):
                # Calculate how much to replace
                yield Completion(
                    f"/{cmd}",
                    start_position=-len(text),
                    display=f"/{cmd}",
                    display_meta=self.meta_dict.get(cmd, ""),
                )


class InputHandler:
    """
    Advanced input handler using Prompt Toolkit.

    Features:
    - Readline-style line editing (Ctrl+A, Ctrl+E, etc.)
    - Persistent history with up/down arrows
    - Tab completion for slash commands
    - Auto-suggestions from history
    - Customizable prompt styling

    Usage:
        handler = InputHandler(
            prompt_name="User",
            commands=["help", "history", "exit"],
        )

        while True:
            text = handler.get_input()
            if text is None:  # EOF/Ctrl+D
                break
            process(text)
    """

    def __init__(
        self,
        prompt_name: str = "User",
        commands: list[str] | None = None,
        command_descriptions: dict[str, str] | None = None,
        history_file: str | Path | None = None,
        style: Style | None = None,
        multiline: bool = False,
        enable_auto_suggest: bool = True,
        extra_key_bindings: Callable[[KeyBindings], None] | None = None,
    ):
        """
        Initialize input handler.

        Args:
            prompt_name: Name to display in prompt (e.g., "User", "Alice")
            commands: List of slash commands for auto-completion
            command_descriptions: Dict of command -> description for tooltips
            history_file: Path to history file (None for in-memory only)
            style: Custom prompt_toolkit Style
            multiline: Enable multi-line input by default
            enable_auto_suggest: Show suggestions from history while typing
        """
        self.prompt_name = prompt_name
        self.multiline = multiline
        self._extra_key_bindings = extra_key_bindings
        # Use provided style, or build from CLI config, or fall back to default
        self.style = style or _build_prompt_style()

        # Set up history
        if history_file:
            history_path = Path(history_file)
            history_path.parent.mkdir(parents=True, exist_ok=True)
            self._history = FileHistory(str(history_path))
        else:
            self._history = InMemoryHistory()

        # Set up completer
        self._completer: Completer | None = None
        if commands:
            self._completer = CommandCompleter(
                commands=commands,
                meta_dict=command_descriptions,
            )

        # Set up auto-suggest
        self._auto_suggest = AutoSuggestFromHistory() if enable_auto_suggest else None

        # Create key bindings for multi-line and double-Esc
        self._key_bindings = self._create_key_bindings()

        # Create prompt session
        self._session: PromptSession[str] = PromptSession(
            history=self._history,
            completer=self._completer,
            auto_suggest=self._auto_suggest,
            style=self.style,
            key_bindings=self._key_bindings,
            multiline=self.multiline,
            enable_history_search=True,
        )

    def _create_key_bindings(self) -> KeyBindings:
        """Create custom key bindings."""
        bindings = KeyBindings()

        @bindings.add("escape", "enter")
        def _multiline_enter(event):
            """Alt+Enter for newline in multi-line mode."""
            event.current_buffer.insert_text("\n")

        # Double-Esc to clear input buffer
        @bindings.add("escape", "escape")
        def _double_escape_clear(event):
            """Double-Esc clears the input buffer."""
            event.current_buffer.reset()

        if self._extra_key_bindings:
            self._extra_key_bindings(bindings)

        return bindings

    def _format_prompt(self) -> HTML:
        """Format the input prompt with styling."""
        return HTML(
            f"<prompt.name>{self.prompt_name}</prompt.name><prompt.separator>: </prompt.separator>"  # noqa: E501
        )

    def _format_continuation(
        self, width: int, line_number: int, is_soft_wrap: bool
    ) -> str:
        """Format continuation prompt for multi-line input."""
        return "... "

    def get_input(self, prompt_override: str | None = None) -> str | None:
        """
        Get input from user with full editing capabilities.

        Args:
            prompt_override: Optional custom prompt text

        Returns:
            User input string, or None on EOF (Ctrl+D)
        """
        try:
            if prompt_override:
                result = self._session.prompt(prompt_override)
            else:
                result = self._session.prompt(
                    self._format_prompt(),
                    prompt_continuation=self._format_continuation
                    if self.multiline
                    else None,
                )
            return result.strip()
        except EOFError:
            return None
        except KeyboardInterrupt:
            # Return empty string on Ctrl+C to allow caller to handle
            raise

    async def get_input_async(self, prompt_override: str | None = None) -> str | None:
        """
        Async version of get_input for use in async contexts.

        Args:
            prompt_override: Optional custom prompt text

        Returns:
            User input string, or None on EOF (Ctrl+D)
        """
        try:
            if prompt_override:
                result = await self._session.prompt_async(prompt_override)
            else:
                result = await self._session.prompt_async(
                    self._format_prompt(),
                    prompt_continuation=self._format_continuation
                    if self.multiline
                    else None,
                )
            return result.strip()
        except EOFError:
            return None
        except KeyboardInterrupt:
            raise

    def add_to_history(self, text: str) -> None:
        """
        Manually add text to history.

        Useful for adding programmatically generated commands.

        Args:
            text: Text to add to history
        """
        self._history.append_string(text)

    def update_commands(
        self,
        commands: list[str],
        descriptions: dict[str, str] | None = None,
    ) -> None:
        """
        Update the list of commands for auto-completion.

        Args:
            commands: New list of commands
            descriptions: Optional new descriptions
        """
        self._completer = CommandCompleter(
            commands=commands,
            meta_dict=descriptions,
        )
        self._session.completer = self._completer

    @property
    def history(self) -> list[str]:
        """Get list of history entries."""
        return list(self._history.get_strings())


# Default commands for Friday CLI
FRIDAY_COMMANDS = [
    "help",
    "exit",
    "quit",
    "clear",
    "history",
    "memory",
    "context",
    "prompt",
    "debug",
    "entities",
    "facts",
    "insights",
    "summaries",
    "meta",
    "prime",
    "sessions",
    "transcript",
    "export",
    "reset",
    "reorganize",
    "lifecycle",
    "vars",
    "set",
    "migrate",
    "tools",
    "run-tool",
    "inject-tools",
    "clear-tools",
    "recommend-tools",
    "tool-budget",
]

FRIDAY_COMMAND_DESCRIPTIONS = {
    "help": "Show available commands",
    "exit": "Exit the program",
    "quit": "Exit the program",
    "clear": "Clear conversation history",
    "history": "Show conversation history",
    "memory": "Show memory status",
    "context": "Show assembled context",
    "prompt": "Show formatted prompt",
    "debug": "Toggle debug mode",
    "entities": "Show graph entities",
    "facts": "Show stored facts",
    "insights": "Show insights",
    "summaries": "Show conversation summaries",
    "meta": "Show meta-insights",
    "prime": "Prime context with prior data",
    "sessions": "List all sessions",
    "transcript": "Show session transcript",
    "export": "Export session data",
    "reset": "Reset memory stores",
    "reorganize": "Reorganize memory",
    "lifecycle": "Manage memory lifecycle",
    "vars": "Show session variables",
    "set": "Set a session variable",
    "migrate": "Run migrations",
    "tools": "List available tools",
    "run-tool": "Execute a tool",
    "inject-tools": "Add tools to session",
    "clear-tools": "Remove injected tools",
    "recommend-tools": "Get tool recommendations",
    "tool-budget": "Show tool execution stats",
}


def create_friday_input_handler(
    user_name: str = "User",
    history_file: str | Path | None = None,
    multiline: bool = False,
    extra_key_bindings: Callable[[KeyBindings], None] | None = None,
) -> InputHandler:
    """
    Create an InputHandler pre-configured for Friday CLI.

    Args:
        user_name: Display name for the prompt
        history_file: Path to history file (optional)
        multiline: Enable multi-line input

    Returns:
        Configured InputHandler instance
    """
    return InputHandler(
        prompt_name=user_name,
        commands=FRIDAY_COMMANDS,
        command_descriptions=FRIDAY_COMMAND_DESCRIPTIONS,
        history_file=history_file,
        multiline=multiline,
        extra_key_bindings=extra_key_bindings,
    )
