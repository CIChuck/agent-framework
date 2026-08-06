"""Compatibility scaffolding for parity-row contract coverage."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

PLANNING_ROOT = Path("docs/planning")
COMPATIBILITY_PLAN_ROOT = (
    PLANNING_ROOT / "build-plans" / "friday-chat-v2-aechive"
)
# These archived plans remain the pinned authority for FridayV2 parity coverage.
PARITY_MATRIX = COMPATIBILITY_PLAN_ROOT / "friday-chat-v2-parity-matrix.md"
CONTRACTS = COMPATIBILITY_PLAN_ROOT / "friday-chat-v2-behavioral-contracts.md"
OVERRIDES = Path(__file__).parent / "fixtures" / "parity_overrides.yaml"


def _load_overrides() -> dict[str, Any]:
    data = yaml.safe_load(OVERRIDES.read_text())
    if not isinstance(data, dict):
        raise TypeError("Parity overrides fixture must be a mapping.")
    return data


def _extract_command_rows() -> set[str]:
    commands: set[str] = set()
    for line in PARITY_MATRIX.read_text().splitlines():
        if not line.startswith("| `/") and not line.startswith("| `@"):
            continue
        label = line.split("|", maxsplit=2)[1]
        for command in re.findall(r"`([/@][^` ]+)", label):
            commands.add(command)
    return commands


def test_command_rows_have_contract_coverage_or_exemption() -> None:
    contracts = CONTRACTS.read_text()
    overrides = _load_overrides()
    exemptions = set(overrides["simple_command_exemptions"])

    missing = {
        command
        for command in _extract_command_rows()
        if command not in contracts and command not in exemptions
    }

    assert missing == set()


def test_config_contract_mentions_required_surface_keys() -> None:
    contracts = CONTRACTS.read_text()
    required_terms = {
        "logging",
        "llm",
        "extraction",
        "embedding",
        "memory.retrieval",
        "memory.priming",
        "maintenance.llm",
        "tools.loop",
        "web.reader",
        "security.sanitization",
        "speech.selection",
    }

    missing = {term for term in required_terms if term not in contracts}

    assert missing == set()
