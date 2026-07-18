"""Compatibility scaffolding for FridayV2 command surface parity."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

REFERENCE_CLI = Path("tests/integration/memory/friday.py")
FALLBACK_ONLY_COMMANDS = {"debug-retrieval", "list-ingested"}


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _extract_registered_commands(source_path: Path) -> set[str]:
    tree = ast.parse(source_path.read_text())
    commands: set[str] = set()
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "register"
        ):
            continue
        if node.args:
            command_name = _literal_string(node.args[0])
            if command_name:
                commands.add(command_name)
        for keyword in node.keywords:
            if keyword.arg != "aliases" or not isinstance(keyword.value, ast.List):
                continue
            for element in keyword.value.elts:
                alias = _literal_string(element)
                if alias:
                    commands.add(alias)
    return commands


def _load_friday_v2_command_names() -> set[str]:
    from friday_chat.commands import registry

    builder = getattr(registry, "build_default_registry", None)
    if builder is None:
        pytest.xfail("FridayV2 command registry is not implemented yet.")
    command_registry = builder()
    names = getattr(command_registry, "command_names", None)
    if not callable(names):
        pytest.xfail("FridayV2 command registry does not expose command_names().")
    result = names()
    if not isinstance(result, set):
        return set(result)
    return result


def test_reference_command_parser_includes_registry_and_fallback_commands() -> None:
    commands = _extract_registered_commands(REFERENCE_CLI) | FALLBACK_ONLY_COMMANDS

    assert "exit" in commands
    assert "quit" in commands
    assert "q" in commands
    assert "debug-retrieval" in commands
    assert "list-ingested" in commands
    assert len(commands) == 52


def test_friday_v2_command_surface_matches_reference() -> None:
    reference_commands = _extract_registered_commands(REFERENCE_CLI)
    reference_commands |= FALLBACK_ONLY_COMMANDS

    friday_v2_commands = _load_friday_v2_command_names()

    assert reference_commands - friday_v2_commands == set()


def test_parity_override_fixture_shape() -> None:
    import yaml

    fixture = Path(__file__).parent / "fixtures" / "parity_overrides.yaml"
    data: dict[str, Any] = yaml.safe_load(fixture.read_text())

    assert sorted(data) == ["accepted_differences", "simple_command_exemptions"]
    assert isinstance(data["accepted_differences"], list)
    assert isinstance(data["simple_command_exemptions"], list)
