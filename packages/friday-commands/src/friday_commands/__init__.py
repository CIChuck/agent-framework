"""Frontend-neutral command foundation and opt-in, dependency-free pilot handlers."""

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
from .pilot import PILOT_SPECS, HelpCatalog, build_pilot_handlers, describe_help
from .registry import CommandHandler, CommandRegistry

__all__ = [
    "PILOT_SPECS",
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
    "HelpCatalog",
    "HelpData",
    "NoData",
    "UiEffect",
    "build_pilot_handlers",
    "describe_help",
]
