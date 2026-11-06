"""One-pass command parsing and atomic registration of injected handlers."""

from __future__ import annotations

import inspect
from typing import Protocol

from .contracts import (
    CommandArgument,
    CommandError,
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    CommandSpec,
    DispatchResult,
)


class CommandHandler(Protocol):
    async def __call__(
        self, request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome: ...


def _normalize(text: str) -> str:
    return str.removeprefix(text, "/").strip().lower()


def _copy_argument(argument: CommandArgument) -> CommandArgument:
    if not str.strip(argument.name) or not str.strip(argument.description):
        raise ValueError("Argument name and description must not be blank")
    return CommandArgument(
        argument.name,
        argument.description,
        argument.required,
        argument.default,
        argument.choices,
    )


class CommandRegistry:
    def __init__(self) -> None:
        self._entries: dict[str, tuple[CommandSpec, CommandHandler]] = {}

    def register(self, spec: CommandSpec, handler: CommandHandler) -> None:
        if type(spec) is not CommandSpec:
            raise TypeError("Expected a CommandSpec")
        if not callable(handler):
            raise TypeError("Expected a callable handler")
        name = _normalize(spec.name)
        aliases = tuple(_normalize(alias) for alias in spec.aliases)
        description = str.strip(spec.description)
        category = str.strip(spec.category)
        usage = str.strip(spec.usage)
        keys = (name, *aliases)
        if any(not key for key in keys):
            raise ValueError("Names and aliases must not be blank")
        if not description or not category or not usage:
            raise ValueError("Description, category and usage must not be blank")
        arguments = tuple(_copy_argument(argument) for argument in spec.arguments)
        if len(set(keys)) != len(keys) or any(key in self._entries for key in keys):
            raise ValueError("Canonical and alias keys must be unique")
        candidate = CommandSpec(
            name, description, category, usage, aliases, arguments, spec.detail
        )
        # Build everything before a single publication; failed candidates cannot
        # leave a canonical name, alias or handler in the previous registry.
        updated = self._entries.copy()
        updated.update(dict.fromkeys(keys, (candidate, handler)))
        self._entries = updated

    def specs(self) -> tuple[CommandSpec, ...]:
        return tuple(
            spec for key, (spec, _) in sorted(self._entries.items()) if key == spec.name
        )

    def names(self) -> frozenset[str]:
        return frozenset(self._entries)

    def resolve(self, name: str) -> CommandSpec | None:
        if not isinstance(name, str):
            raise TypeError("Expected a string name")
        entry = self._entries.get(_normalize(name))
        return entry[0] if entry is not None else None

    async def execute_text(
        self, text: str, execution: CommandExecution
    ) -> DispatchResult:
        if not isinstance(text, str):
            raise TypeError("Expected string command text")
        if type(execution) is not CommandExecution:
            raise TypeError("Expected a CommandExecution")
        if not str.startswith(text, "/"):
            return DispatchResult(False, None)
        tokens = str.removeprefix(text, "/").strip().split()
        key = _normalize(tokens[0]) if tokens else ""
        entry = self._entries.get(key)
        if entry is None:
            return DispatchResult(
                True, CommandOutcome(error=CommandError("unknown_command", key))
            )
        spec, handler = entry
        request = CommandRequest(spec.name, tuple(tokens[1:]), spec)
        result = handler(request, execution)
        if not inspect.isawaitable(result):
            raise TypeError("Handler must return an awaitable")
        outcome = await result
        if type(outcome) is not CommandOutcome:
            raise TypeError("Handler must return a CommandOutcome")
        return DispatchResult(True, outcome)
