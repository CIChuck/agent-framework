"""Immutable, runtime-validated foundation models without host dependencies."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Literal


def _string(value: object, *, optional: bool = False) -> None:
    if optional and value is None:
        return
    if not isinstance(value, str):
        raise TypeError("Expected a string")


def _boolean(value: object) -> None:
    if type(value) is not bool:
        raise TypeError("Expected a boolean")


def _snapshot[T](
    value: Iterable[object], member_type: type[T], *, exact: bool = False
) -> tuple[T, ...]:
    if isinstance(value, (str, bytes, bytearray, Mapping)):
        raise TypeError("Expected a finite iterable collection")
    items: list[T] = []
    for item in value:
        if not isinstance(item, member_type) or (
            exact and type(item) is not member_type
        ):
            raise TypeError("Invalid collection member type")
        items.append(item)
    return tuple(items)


@dataclass(frozen=True, slots=True)
class CommandArgument:
    name: str
    description: str
    required: bool = False
    default: str | None = None
    choices: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _string(self.name)
        _string(self.description)
        _boolean(self.required)
        _string(self.default, optional=True)
        object.__setattr__(self, "choices", _snapshot(self.choices, str))


@dataclass(frozen=True, slots=True)
class CommandSpec:
    name: str
    description: str
    category: str
    usage: str
    aliases: tuple[str, ...] = ()
    arguments: tuple[CommandArgument, ...] = ()
    detail: str | None = None

    def __post_init__(self) -> None:
        _string(self.name)
        _string(self.description)
        _string(self.category)
        _string(self.usage)
        object.__setattr__(self, "aliases", _snapshot(self.aliases, str))
        object.__setattr__(
            self, "arguments", _snapshot(self.arguments, CommandArgument, exact=True)
        )
        _string(self.detail, optional=True)


@dataclass(frozen=True, slots=True)
class CommandRequest:
    name: str
    args: tuple[str, ...]
    spec: CommandSpec

    def __post_init__(self) -> None:
        _string(self.name)
        object.__setattr__(self, "args", _snapshot(self.args, str))
        if type(self.spec) is not CommandSpec:
            raise TypeError("Expected a CommandSpec")
        if self.name != self.spec.name:
            raise ValueError("Request and spec names must match")


@dataclass(frozen=True, slots=True)
class CommandExecution:
    session_id: str | None = None

    def __post_init__(self) -> None:
        _string(self.session_id, optional=True)


@dataclass(frozen=True, slots=True)
class NoData:
    """A typed successful result with no data fields."""


@dataclass(frozen=True, slots=True)
class HelpData:
    commands: tuple[CommandSpec, ...]
    focused_name: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "commands", _snapshot(self.commands, CommandSpec, exact=True)
        )
        _string(self.focused_name, optional=True)


@dataclass(frozen=True, slots=True)
class ExitData:
    requested: bool = True

    def __post_init__(self) -> None:
        _boolean(self.requested)


type FoundationData = NoData | HelpData | ExitData


@dataclass(frozen=True, slots=True)
class CommandError:
    code: Literal["unknown_command", "invalid_arguments", "unavailable", "failed"]
    command_name: str
    usage: str | None = None

    def __post_init__(self) -> None:
        _string(self.code)
        _string(self.command_name)
        _string(self.usage, optional=True)
        if self.code not in (
            "unknown_command",
            "invalid_arguments",
            "unavailable",
            "failed",
        ):
            raise ValueError("Unknown foundation error code")


class UiEffect(Enum):
    CLEAR_SCREEN = "clear_screen"


@dataclass(frozen=True, slots=True)
class CommandOutcome:
    data: FoundationData | None = None
    error: CommandError | None = None
    ui_effects: tuple[UiEffect, ...] = ()

    def __post_init__(self) -> None:
        if self.data is not None and not any(
            type(self.data) is variant for variant in (NoData, HelpData, ExitData)
        ):
            raise TypeError("Expected a closed foundation data variant")
        if self.error is not None and type(self.error) is not CommandError:
            raise TypeError("Expected a CommandError")
        object.__setattr__(
            self, "ui_effects", _snapshot(self.ui_effects, UiEffect, exact=True)
        )
        if (self.data is None) == (self.error is None):
            raise ValueError("Exactly one of data or error is required")
        if self.error is not None and self.ui_effects:
            raise ValueError("Error outcomes cannot request UI effects")


@dataclass(frozen=True, slots=True)
class DispatchResult:
    handled: bool
    outcome: CommandOutcome | None

    def __post_init__(self) -> None:
        _boolean(self.handled)
        if self.outcome is not None and type(self.outcome) is not CommandOutcome:
            raise TypeError("Expected a CommandOutcome")
        if self.handled != (self.outcome is not None):
            raise ValueError("Handled and outcome must agree")
