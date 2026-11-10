"""Opt-in help, exit and clear-screen behavior with host-owned effects."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Protocol

from .contracts import (
    CommandArgument,
    CommandError,
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    CommandSpec,
    ExitData,
    HelpData,
    NoData,
    UiEffect,
)
from .registry import CommandHandler

# Exact metadata from the maintained Chat baseline; importing this tuple does
# not register commands or select a host catalog.
PILOT_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec(
        "help",
        "Show available commands or focused command help.",
        "session",
        "/help [command]",
        arguments=(CommandArgument("command", "Command name or alias to inspect."),),
    ),
    CommandSpec(
        "exit",
        "Exit the chat session.",
        "session",
        "/exit",
        aliases=("quit", "q"),
    ),
    CommandSpec(
        "cls",
        "Clear the terminal through the display boundary.",
        "session",
        "/cls",
        aliases=("clearscreen",),
        detail=(
            "Requests one clear-screen UI effect and emits no replacement text. "
            "Unavailable or failed display boundaries report an honest error."
        ),
    ),
)


class HelpCatalog(Protocol):
    """Synchronous metadata snapshots and lookup of an already normalized key."""

    def specs(self) -> tuple[CommandSpec, ...]: ...

    def lookup_key(self, key: str) -> CommandSpec | None: ...


def describe_help(
    catalog: HelpCatalog, focused_name: str | None = None
) -> CommandOutcome:
    """Select typed help data without formatting, dispatch or host access."""
    if focused_name is not None and not isinstance(focused_name, str):
        raise TypeError("Expected a string focus or None")
    if not focused_name:
        commands = tuple(sorted(catalog.specs(), key=lambda spec: spec.name))
        return CommandOutcome(data=HelpData(commands))
    key = focused_name.removeprefix("/").strip().lower()
    spec = catalog.lookup_key(key)
    if spec is None:
        return CommandOutcome(error=CommandError("unknown_command", key))
    return CommandOutcome(data=HelpData((spec,), focused_name=spec.name))


def _validate_invocation(
    request: CommandRequest, execution: CommandExecution, canonical_name: str
) -> None:
    # Check both exact types before inspecting any request fields.
    if type(request) is not CommandRequest:
        raise TypeError("Expected a CommandRequest")
    if type(execution) is not CommandExecution:
        raise TypeError("Expected a CommandExecution")
    if request.name != canonical_name:
        raise ValueError("Request does not match this pilot handler")


def build_pilot_handlers(catalog: HelpCatalog) -> Mapping[str, CommandHandler]:
    """Build immutable injected handlers without reading the supplied catalog."""

    async def help_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "help")
        return describe_help(catalog, request.args[0] if request.args else None)

    async def exit_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "exit")
        return CommandOutcome(data=ExitData(True))

    async def cls_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "cls")
        return CommandOutcome(data=NoData(), ui_effects=(UiEffect.CLEAR_SCREEN,))

    return MappingProxyType(
        {"help": help_handler, "exit": exit_handler, "cls": cls_handler}
    )
