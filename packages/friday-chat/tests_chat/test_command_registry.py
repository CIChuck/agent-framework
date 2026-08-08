"""Command registry tests for FridayV2."""

from __future__ import annotations

import pytest
from friday_chat.commands.registry import (
    CommandArgument,
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
    for metadata in registry.commands.values():
        assert f"Description: {metadata.description}" in result.output
        assert f"Usage: {metadata.usage}" in result.output
        for argument in metadata.arguments:
            requirement = "required" if argument.required else "optional"
            assert f"- {argument.name} [{requirement}]" in result.output
    missing = {
        command_name
        for command_name in registry.command_names()
        if f"/{command_name}" not in result.output
    }
    assert missing == set()


def test_help_uses_legacy_verbose_category_format() -> None:
    registry = CommandRegistry()
    registry.register(
        "inspect",
        description="Inspect an item.",
        category="utility",
        usage="/inspect <name> [format]",
        aliases=("show",),
        arguments=(
            CommandArgument("name", "Item name.", required=True),
            CommandArgument(
                "format",
                "Output format.",
                default="text",
                choices=("text", "json"),
            ),
        ),
    )

    assert registry.render_help() == (
        "Available commands:\n"
        "Use /help <command> for focused details.\n"
        "\n"
        "UTILITY\n"
        "-\n"
        "/inspect (aliases: /show)\n"
        "  Description: Inspect an item.\n"
        "  Usage: /inspect <name> [format]\n"
        "  Arguments:\n"
        "    - name [required]: Item name.\n"
        "    - format [optional] (default=text, choices=text, json): Output format."
    )


def test_default_help_metadata_matches_handler_syntax() -> None:
    commands = build_default_registry().commands

    assert commands["read"].usage == "/read <path> [--lines=N]"
    assert commands["replay"].usage == "/replay <csv_path> [delay_seconds]"
    assert commands["security-test"].usage.endswith(
        "[instruction|delimiter|jailbreak|exfil|all]"
    )
    assert commands["security-config"].usage == (
        "/security-config <sensitivity|action|wrapping> <value>"
    )
    assert commands["migrate"].usage == "/migrate [--force|--execute|--stats]"
    assert commands["export-prompts"].usage == "/export-prompts"


@pytest.mark.parametrize(
    ("field", "description", "category", "usage"),
    [
        ("description", " ", "utility", "/inspect"),
        ("category", "Inspect an item.", " ", "/inspect"),
        ("usage", "Inspect an item.", "utility", " "),
    ],
)
def test_registration_rejects_missing_help_metadata(
    field: str,
    description: str,
    category: str,
    usage: str,
) -> None:
    registry = CommandRegistry()

    with pytest.raises(ValueError, match=field):
        registry.register(
            "inspect",
            description=description,
            category=category,
            usage=usage,
        )


def test_registration_rejects_undocumented_argument() -> None:
    registry = CommandRegistry()

    with pytest.raises(ValueError, match="requires a description"):
        registry.register(
            "inspect",
            description="Inspect an item.",
            category="utility",
            arguments=(CommandArgument("name", ""),),
        )


async def test_help_for_alias_resolves_canonical_command() -> None:
    registry = build_default_registry()
    context = RegistryCommandContext(registry=registry)

    was_command, result = await registry.execute("/help quit", context)

    assert was_command is True
    assert result is not None
    assert "/exit" in result.output
    assert "Usage: /exit" in result.output
    assert "Description: Exit the chat session." in result.output
    assert "Aliases: /quit, /q" in result.output
    assert "Arguments: none" in result.output


async def test_focused_help_includes_structured_argument_details() -> None:
    registry = build_default_registry()
    context = RegistryCommandContext(registry=registry)

    _, result = await registry.execute("/help context", context)

    assert result is not None
    assert "Usage: /context [--debug] [--file]" in result.output
    assert "Arguments:" in result.output
    assert "- --debug [optional]: Include detailed token diagnostics." in result.output
    assert "- --file [optional]: Export the context to a file." in result.output


async def test_reorganize_help_documents_exact_execution_and_recovery() -> None:
    registry = build_default_registry()
    context = RegistryCommandContext(registry=registry)

    _, result = await registry.execute("/help reorganize", context)

    assert result is not None
    assert "/reorganize --recover <run-id> [--execute]" in result.output
    assert "dry-run by default" in result.output
    assert "Plain 'execute' and --no-backup are rejected" in result.output
    assert "Transcript content is recovery-only" in result.output
    assert "defaults to disabled" in result.output


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
