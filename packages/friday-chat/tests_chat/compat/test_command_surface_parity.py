"""Compatibility scaffolding for FridayV2 command surface parity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

REFERENCE_COMMANDS = Path(__file__).parent / "fixtures" / "legacy_command_names.yaml"


def _load_reference_commands() -> set[str]:
    import yaml

    commands: list[str] = yaml.safe_load(REFERENCE_COMMANDS.read_text())
    return set(commands)


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


def test_reference_fixture_includes_registry_and_fallback_commands() -> None:
    commands = _load_reference_commands()

    assert "exit" in commands
    assert "quit" in commands
    assert "q" in commands
    assert "debug-retrieval" in commands
    assert "list-ingested" in commands
    assert len(commands) == 52


def test_friday_v2_command_surface_matches_reference() -> None:
    reference_commands = _load_reference_commands()

    friday_v2_commands = _load_friday_v2_command_names()

    assert reference_commands - friday_v2_commands == set()


def test_parity_override_fixture_shape() -> None:
    import yaml

    fixture = Path(__file__).parent / "fixtures" / "parity_overrides.yaml"
    data: dict[str, Any] = yaml.safe_load(fixture.read_text())

    assert sorted(data) == ["accepted_differences", "simple_command_exemptions"]
    assert isinstance(data["accepted_differences"], list)
    assert isinstance(data["simple_command_exemptions"], list)
