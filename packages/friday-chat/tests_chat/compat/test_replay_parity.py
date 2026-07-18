"""Compatibility scaffolding for FridayV2 replay parity."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "replay_basic.csv"


def test_replay_fixture_orders_user_messages_by_turn_number() -> None:
    with FIXTURE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    user_rows = [row for row in rows if row["user_message"].strip()]
    ordered = sorted(user_rows, key=lambda row: int(row["turn_number"]))

    assert [row["user_message"] for row in ordered] == [
        "First prompt",
        "Second prompt",
    ]


async def test_friday_v2_replay_service_processes_fixture() -> None:
    from friday_chat import replay

    service_type = getattr(replay, "ReplayService", None)
    if service_type is None:
        pytest.xfail("FridayV2 replay service is not implemented yet.")

    service = service_type()
    result = await service.replay_csv(FIXTURE)

    assert result.processed_turns == 2
