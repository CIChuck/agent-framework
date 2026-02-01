"""
Session management commands for Friday Chat.

Commands:
- /exit, /quit - Exit the chat session
- /clear - Clear conversation history
- /cls - Clear the terminal screen
"""

from typing import TYPE_CHECKING

from friday_cli import get_console

if TYPE_CHECKING:
    from ..session import MemoryChatSession


def cmd_clear(session: "MemoryChatSession") -> str:
    """Clear conversation history."""
    session.turn_ids.clear()
    session.last_payload = None
    if session.state:
        session.state.turn_count = 0
    return "Conversation history cleared."


def cmd_cls(session: "MemoryChatSession") -> str:
    """Clear the terminal screen."""
    get_console().clear()
    return ""


def register_session_commands(registry, session: "MemoryChatSession") -> None:
    """Register session management commands with the registry."""
    registry.register(
        "exit",
        lambda ctx: "EXIT",
        aliases=["quit", "q"],
        description="Exit the chat session",
        category="session",
    )

    registry.register(
        "clear",
        lambda ctx: cmd_clear(ctx),
        description="Clear conversation history for current session",
        category="session",
    )

    registry.register(
        "cls",
        lambda ctx: cmd_cls(ctx),
        aliases=["clearscreen"],
        description="Clear the terminal screen",
        category="session",
    )
