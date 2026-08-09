"""Cycle-free typed contracts shared by Friday Chat commands."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from friday_memory.models.budget import BudgetStatus

    from friday_chat.runtime import FridayRuntime
    from friday_chat.session import FridaySession, SessionIdentity
    from friday_chat.tools.selection import ToolBudgetSnapshot


class CommandUiEffect(str, Enum):
    """UI effects a command may ask the app display boundary to perform."""

    CLEAR_SCREEN = "clear_screen"


@dataclass
class CommandContext:
    """Runtime context passed to command handlers."""

    runtime: FridayRuntime | None = None
    command_progress: Callable[[str], Awaitable[None]] | None = None
    exit_requested: bool = False
    variables: dict[str, str] = field(default_factory=dict)
    history: list[tuple[str, str]] = field(default_factory=list)
    last_context: str | None = None
    last_prompt: str | None = None
    last_debug: dict[str, str] = field(default_factory=dict)
    last_timing: dict[str, float] = field(default_factory=dict)
    last_budget_status: BudgetStatus | None = None
    last_tool_budget_snapshot: ToolBudgetSnapshot | None = None
    session: FridaySession | None = None
    tool_results: list[str] = field(default_factory=list)
    tool_lifecycle_records: list[str] = field(default_factory=list)
    tool_ingestions: list[str] = field(default_factory=list)
    injected_payload: str | None = None
    security_stats: dict[str, int] = field(
        default_factory=lambda: {
            "total_scans": 0,
            "detections": 0,
            "blocked": 0,
            "patterns_seen": 0,
        }
    )

    @property
    def session_identity(self) -> SessionIdentity | None:
        """Return the runtime-owned identity used by command queries."""
        if self.runtime is None:
            return None
        return self.runtime.session_identity


@dataclass(frozen=True)
class CommandResult:
    """Result from command dispatch."""

    output: str
    handled: bool = True
    exit_requested: bool = False
    ui_effects: tuple[CommandUiEffect, ...] = ()


@dataclass(frozen=True)
class CommandArgument:
    """One user-facing command argument used by generated help."""

    name: str
    description: str
    required: bool = False
    default: str | None = None
    choices: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandMetadata:
    """Command metadata used for dispatch and generated help."""

    name: str
    description: str
    category: str
    usage: str
    aliases: tuple[str, ...] = ()
    arguments: tuple[CommandArgument, ...] = ()
    detail: str | None = None


CommandHandler = Callable[
    [CommandContext, tuple[str, ...], CommandMetadata],
    Awaitable[CommandResult],
]


__all__ = [
    "CommandArgument",
    "CommandContext",
    "CommandHandler",
    "CommandMetadata",
    "CommandResult",
    "CommandUiEffect",
]
