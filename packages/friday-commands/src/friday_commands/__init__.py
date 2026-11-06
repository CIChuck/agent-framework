"""Frontend-neutral command foundation; no built-in handlers or dependencies."""

from .contracts import (
    CommandArgument,
    CommandError,
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    CommandSpec,
    DispatchResult,
    ExitData,
    FoundationData,
    HelpData,
    NoData,
    UiEffect,
)
from .registry import CommandHandler, CommandRegistry

__all__ = [
    "CommandArgument",
    "CommandError",
    "CommandExecution",
    "CommandHandler",
    "CommandOutcome",
    "CommandRegistry",
    "CommandRequest",
    "CommandSpec",
    "DispatchResult",
    "ExitData",
    "FoundationData",
    "HelpData",
    "NoData",
    "UiEffect",
]
