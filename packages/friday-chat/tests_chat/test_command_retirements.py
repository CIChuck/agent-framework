"""Pinned catalog and no-effect obligations for the nine retired slash names."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path

import pytest
from friday_chat.commands.contracts import CommandContext, CommandResult
from friday_chat.commands.registry import (
    _SHARED_ADMISSION_COMMANDS,
    BASIC_COMMAND_HANDLERS,
    CommandRegistry,
    RegistryCommandContext,
    build_default_registry,
)

RETIRED = frozenset(
    {
        "clear-tools",
        "inject-payload",
        "inject-tools",
        "prime",
        "recommend-tools",
        "run-tool",
        "set",
        "tool-budget",
        "vars",
    }
)
ORACLE = (
    Path(__file__).resolve().parents[3]
    / "docs/planning/active/command-refactor/validation/command-matrix.json"
)


def test_exact_retained_catalog_and_metadata() -> None:
    raw = ORACLE.read_bytes()
    assert (
        hashlib.sha256(raw).hexdigest()
        == "87c7880b21bbd7b02f227a7f93373dc3acc67db91e3ced18fd65511c34081f85"
    )
    fields = (
        "name",
        "description",
        "category",
        "usage",
        "aliases",
        "arguments",
        "detail",
    )
    expected = [
        {key: row[key] for key in fields}
        for row in json.loads(raw)["commands"]
        if row["name"] not in RETIRED
    ]
    registry = build_default_registry()
    actual = json.loads(
        json.dumps(
            [
                dataclasses.asdict(registry.commands[name])
                for name in sorted(registry.canonical_names())
            ]
        )
    )
    assert actual == expected
    assert len(actual) == 41
    aliases = {
        alias: spec.name
        for spec in registry.commands.values()
        for alias in spec.aliases
    }
    assert aliases == {"q": "exit", "quit": "exit", "clearscreen": "cls"}
    assert registry.command_names() == {row["name"] for row in expected} | set(aliases)
    assert not RETIRED.intersection(BASIC_COMMAND_HANDLERS)
    expected_admission = {
        "reset",
        "lifecycle",
        "migrate",
        "compact",
        "ingest",
        "replay",
    }
    assert expected_admission == _SHARED_ADMISSION_COMMANDS
    for name in RETIRED:
        assert f"/{name}" not in registry.render_help().split()
        assert (
            registry.render_help(name)
            == f"Unknown command: /{name}. Type /help for available commands."
        )


class ForbiddenRuntime:
    def __getattr__(self, name: str) -> object:
        raise AssertionError(f"Retired command accessed runtime capability {name}")


class ForbiddenGate:
    def shared(self, *args: object) -> object:
        raise AssertionError("Retired command entered admission")


class UnreadableVariables(dict[str, str]):
    def __iter__(self):
        raise AssertionError("Retired command enumerated variables")

    def __len__(self):
        raise AssertionError("Retired command read variable count")

    def items(self):
        raise AssertionError("Retired command enumerated variable values")

    def __setitem__(self, key, value):
        raise AssertionError("Retired command wrote variables")


@pytest.mark.parametrize("name", sorted(RETIRED))
@pytest.mark.parametrize(
    "variant",
    [
        "ordinary",
        "uppercase",
        "double",
        "space-slash",
        "argument",
        "quotes",
        "triple",
        "leading-space",
    ],
)
@pytest.mark.parametrize("context_kind", ["absent", "seeded", "tripwire"])
async def test_retired_names_have_exact_unknown_response_and_no_effects(
    name, variant, context_kind
) -> None:
    registry = build_default_registry()
    context = None
    if context_kind != "absent":
        context = RegistryCommandContext(
            registry=registry,
            variables={"project": "preserve"},
            history=[("user", "assistant")],
            security_stats={
                "total_scans": 7,
                "detections": 2,
                "blocked": 1,
                "patterns_seen": 3,
            },
        )
        context.exit_requested = True
        if context_kind == "tripwire":
            context.runtime = ForbiddenRuntime()
            context.maintenance_gate = ForbiddenGate()
            context.variables = UnreadableVariables({"project": "preserve"})
        before = vars(context).copy()
        before_containers = {
            key: value.copy()
            for key, value in vars(context).items()
            if isinstance(value, (dict, list))
        }
    inputs = {
        "ordinary": f"/{name}",
        "uppercase": f"/{name.upper()}",
        "double": f"//{name}",
        "space-slash": f"/ /{name}",
        "argument": f"/{name} replace /tmp/never-write",
        "quotes": f'/{name} "a b"',
        "triple": f"///{name}",
        "leading-space": f" /{name}",
    }
    handled, result = await registry.execute(inputs[variant], context)
    if variant == "leading-space":
        assert (handled, result) == (False, None)
    else:
        parsed = "/" + name if variant == "triple" else name
        assert handled is True
        assert result == CommandResult(
            output=f"Unknown command: /{parsed}. Type /help for available commands."
        )
        assert result.exit_requested is False
        assert result.ui_effects == ()
    if context is not None:
        assert vars(context) == before
        for key, expected in before_containers.items():
            assert vars(context)[key] == expected


def test_removed_context_fields_only() -> None:
    fields = {field.name for field in dataclasses.fields(CommandContext)}
    assert not fields.intersection(
        {
            "injected_payload",
            "tool_results",
            "tool_lifecycle_records",
            "tool_ingestions",
        }
    )
    assert {
        "variables",
        "last_tool_budget_snapshot",
        "security_stats",
        "runtime",
        "session",
        "command_progress",
        "exit_requested",
    } <= fields


async def test_custom_registry_can_still_register_a_retired_spelling() -> None:
    registry = CommandRegistry()
    calls = []

    async def custom(context, args, metadata):
        calls.append((args, metadata.name))
        return CommandResult(output="custom handler")

    registry.register(
        "run-tool",
        description="A caller-owned custom command.",
        category="custom",
        handler=custom,
    )
    handled, result = await registry.execute("/run-tool argument")
    assert handled and result == CommandResult(output="custom handler")
    assert calls == [(("argument",), "run-tool")]
