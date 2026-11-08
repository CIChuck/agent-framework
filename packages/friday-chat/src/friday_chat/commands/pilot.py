"""Typed Chat compatibility adapters for the shared three-command pilot."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

import friday_commands.pilot as shared_pilot
from friday_commands import (
    CommandArgument as SharedCommandArgument,
)
from friday_commands import (
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    ExitData,
    HelpCatalog,
    HelpData,
    NoData,
    UiEffect,
)
from friday_commands import (
    CommandSpec as SharedCommandSpec,
)

from friday_chat.commands.contracts import (
    CommandArgument,
    CommandMetadata,
    CommandResult,
    CommandUiEffect,
)

_PILOT_BY_NAME = MappingProxyType(
    {spec.name: spec for spec in shared_pilot.PILOT_SPECS}
)


def _to_shared(metadata: CommandMetadata) -> SharedCommandSpec:
    # Project displayed legacy values without making Chat registration stricter.
    arguments = tuple(
        SharedCommandArgument(
            argument.name,
            argument.description,
            bool(argument.required),
            None if argument.default is None else f"{argument.default}",
            tuple(argument.choices) if argument.choices else (),
        )
        for argument in metadata.arguments
    )
    return SharedCommandSpec(
        metadata.name,
        metadata.description,
        metadata.category,
        metadata.usage,
        metadata.aliases,
        arguments,
        metadata.detail,
    )


@dataclass(frozen=True, slots=True)
class RegistryCatalog:
    """A live Chat metadata view with snapshots and exact normalized-key lookup."""

    commands: Mapping[str, CommandMetadata]
    aliases: Mapping[str, str]

    def specs(self) -> tuple[SharedCommandSpec, ...]:
        return tuple(_to_shared(metadata) for metadata in self.commands.values())

    def lookup_key(self, key: str) -> SharedCommandSpec | None:
        metadata = self.commands.get(self.aliases.get(key, key))
        return None if metadata is None else _to_shared(metadata)


@dataclass(frozen=True, slots=True)
class _EmptyCatalog:
    def specs(self) -> tuple[SharedCommandSpec, ...]:
        return ()

    def lookup_key(self, key: str) -> SharedCommandSpec | None:
        return None


_EMPTY_CATALOG = _EmptyCatalog()


def pilot_metadata(name: str) -> CommandMetadata:
    """Project a shared definition into the unchanged public Chat model."""
    spec = _PILOT_BY_NAME[name]
    arguments = tuple(
        CommandArgument(
            argument.name,
            argument.description,
            argument.required,
            argument.default,
            argument.choices,
        )
        for argument in spec.arguments
    )
    return CommandMetadata(
        spec.name,
        spec.description,
        spec.category,
        spec.usage,
        spec.aliases,
        arguments,
        spec.detail,
    )


def adapt_outcome(outcome: CommandOutcome) -> CommandResult:
    """Accept only the pilot's explicit result shapes at the host boundary."""
    if type(outcome) is not CommandOutcome:
        raise ValueError("Unsupported pilot outcome type")
    if outcome.error is not None:
        if (
            outcome.error.code != "unknown_command"
            or outcome.error.usage is not None
            or outcome.ui_effects
        ):
            raise ValueError("Unsupported pilot error outcome")
        return CommandResult(
            output=f"Unknown command: /{outcome.error.command_name}. Type /help for available commands."
        )
    data = outcome.data
    if type(data) is HelpData and not outcome.ui_effects:
        if data.focused_name is None:
            return CommandResult(output=_render_general_help(data.commands))
        if len(data.commands) == 1 and data.commands[0].name == data.focused_name:
            return CommandResult(output=_render_command_detail(data.commands[0]))
        raise ValueError("Unsupported focused help shape")
    if type(data) is ExitData and data.requested and not outcome.ui_effects:
        return CommandResult(output="Goodbye.", exit_requested=True)
    if type(data) is NoData and outcome.ui_effects == (UiEffect.CLEAR_SCREEN,):
        return CommandResult(output="", ui_effects=(CommandUiEffect.CLEAR_SCREEN,))
    raise ValueError("Unsupported pilot data/effect outcome")


def render_help(catalog: HelpCatalog, focused_name: str | None = None) -> str:
    # Legacy direct callers use any falsy focus for general help.
    return adapt_outcome(
        shared_pilot.describe_help(catalog, focused_name or None)
    ).output


async def invoke_pilot(
    name: str, args: tuple[str, ...], catalog: HelpCatalog = _EMPTY_CATALOG
) -> CommandResult:
    spec = _PILOT_BY_NAME[name]
    request = CommandRequest(spec.name, args, spec)
    handler = shared_pilot.build_pilot_handlers(catalog)[name]
    return adapt_outcome(await handler(request, CommandExecution()))


def _render_general_help(commands: tuple[SharedCommandSpec, ...]) -> str:
    lines = ["Available commands:", "Use /help <command> for focused details."]
    for category in sorted({command.category for command in commands}):
        lines.append("")
        lines.append(category.upper())
        lines.append("-")
        category_commands = sorted(
            (command for command in commands if command.category == category),
            key=lambda command: command.name,
        )
        for index, command in enumerate(category_commands):
            lines.extend(_render_command_summary(command))
            if index < len(category_commands) - 1:
                lines.append("")
    return "\n".join(lines)


def _render_command_detail(metadata: SharedCommandSpec) -> str:
    lines = [
        f"/{metadata.name}",
        f"Category: {metadata.category}",
        f"Usage: {metadata.usage}",
        f"Description: {metadata.description}",
    ]
    if metadata.aliases:
        lines.append("Aliases: " + ", ".join(f"/{alias}" for alias in metadata.aliases))
    lines.extend(_render_arguments(metadata.arguments))
    if metadata.detail:
        lines.append("")
        lines.append(metadata.detail)
    return "\n".join(lines)


def _render_command_summary(metadata: SharedCommandSpec) -> list[str]:
    alias_text = ""
    if metadata.aliases:
        aliases = ", ".join(f"/{alias}" for alias in metadata.aliases)
        alias_text = f" (aliases: {aliases})"
    lines = [
        f"/{metadata.name}{alias_text}",
        f"  Description: {metadata.description}",
        f"  Usage: {metadata.usage}",
    ]
    lines.extend(_render_arguments(metadata.arguments, indent="  "))
    return lines


def _render_arguments(
    arguments: tuple[SharedCommandArgument, ...],
    *,
    indent: str = "",
) -> list[str]:
    if not arguments:
        return [f"{indent}Arguments: none"]

    lines = [f"{indent}Arguments:"]
    for argument in arguments:
        requirement = "required" if argument.required else "optional"
        qualifiers: list[str] = []
        if argument.default is not None:
            qualifiers.append(f"default={argument.default}")
        if argument.choices:
            qualifiers.append(f"choices={', '.join(argument.choices)}")
        qualifier_text = f" ({', '.join(qualifiers)})" if qualifiers else ""
        lines.append(
            f"{indent}  - {argument.name} [{requirement}]{qualifier_text}: "
            f"{argument.description}"
        )
    return lines
