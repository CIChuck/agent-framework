"""Command registry tests for FridayV2."""

from __future__ import annotations

import pytest
from friday_chat.commands.registry import (
    CommandRegistry,
    RegistryCommandContext,
    build_default_registry,
)


def test_default_registry_includes_session_commands_and_fallback_prototypes() -> None:
    registry = build_default_registry()

    names = registry.command_names()

    assert {"exit", "quit", "q", "help"}.issubset(names)
    assert {"debug-retrieval", "list-ingested"}.issubset(names)


def test_duplicate_command_registration_fails() -> None:
    registry = CommandRegistry()
    registry.register(
        "exit",
        description="Exit.",
        category="session",
        aliases=("quit",),
    )

    with pytest.raises(ValueError, match="/quit"):
        registry.register(
            "leave",
            description="Exit by another name.",
            category="session",
            aliases=("quit",),
        )


async def test_help_includes_every_registered_command_and_alias() -> None:
    registry = build_default_registry()
    context = RegistryCommandContext(registry=registry)

    was_command, result = await registry.execute("/help", context)

    assert was_command is True
    assert result is not None
    assert result.output.startswith("Available commands:")
    missing = {
        command_name
        for command_name in registry.command_names()
        if f"/{command_name}" not in result.output
    }
    assert missing == set()


async def test_help_for_alias_resolves_canonical_command() -> None:
    registry = build_default_registry()
    context = RegistryCommandContext(registry=registry)

    was_command, result = await registry.execute("/help quit", context)

    assert was_command is True
    assert result is not None
    assert "/exit" in result.output
    assert "Aliases: /quit, /q" in result.output


async def test_unknown_command_returns_registry_response() -> None:
    registry = build_default_registry()

    was_command, result = await registry.execute("/does-not-exist")

    assert was_command is True
    assert result is not None
    assert result.output == (
        "Unknown command: /does-not-exist. Type /help for available commands."
    )


async def test_non_command_input_is_not_dispatched() -> None:
    registry = build_default_registry()

    was_command, result = await registry.execute("hello")

    assert was_command is False
    assert result is None


async def test_exit_alias_requests_exit() -> None:
    registry = build_default_registry()

    was_command, result = await registry.execute("/q")

    assert was_command is True
    assert result is not None
    assert result.exit_requested is True
