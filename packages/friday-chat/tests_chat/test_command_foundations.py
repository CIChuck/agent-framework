"""Gate B coverage for shared command contracts and category ownership."""

from __future__ import annotations

from friday_chat.commands import contracts
from friday_chat.commands.registry import (
    BASIC_COMMAND_HANDLERS,
    CommandResult,
    CommandUiEffect,
    build_default_registry,
)


def test_registry_reexports_the_cycle_free_command_contracts() -> None:
    result = CommandResult(output="unchanged")

    assert CommandResult is contracts.CommandResult
    assert CommandUiEffect is contracts.CommandUiEffect
    assert result.ui_effects == ()
    assert CommandUiEffect.CLEAR_SCREEN.value == "clear_screen"


def test_affected_handlers_are_owned_by_their_category_modules() -> None:
    expected_modules = {
        "cls": "friday_chat.commands.session",
        "memory": "friday_chat.commands.memory",
        "insights": "friday_chat.commands.memory",
        "summaries": "friday_chat.commands.memory",
        "meta": "friday_chat.commands.memory",
        "sessions": "friday_chat.commands.transcript",
        "transcript": "friday_chat.commands.transcript",
        "export": "friday_chat.commands.transcript",
        "export-prompts": "friday_chat.commands.transcript",
        "inject-tools": "friday_chat.commands.tools",
        "clear-tools": "friday_chat.commands.tools",
        "tool-budget": "friday_chat.commands.tools",
    }

    assert {
        name: BASIC_COMMAND_HANDLERS[name].__module__ for name in expected_modules
    } == expected_modules


async def test_registry_remains_the_canonical_alias_help_and_dispatch_surface() -> None:
    registry = build_default_registry()

    handled, result = await registry.execute("/clearscreen")

    assert handled is True
    assert result == CommandResult(
        output="",
        ui_effects=(CommandUiEffect.CLEAR_SCREEN,),
    )
    assert "Aliases: /clearscreen" in registry.render_help("cls")
