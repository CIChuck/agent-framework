# mypy: ignore-errors
"""Tests for transcript correlation helpers."""

from datetime import datetime

from friday_transcript.correlation import (
    build_correlation_index,
    correlate_promotion_entries,
    summarize_correlation_slice,
)
from friday_transcript.models.transcript import TranscriptEntry


def _entry(
    entry_id: str,
    turn_number: int,
    *,
    agent_id: str | None = None,
    metadata: dict | None = None,
) -> TranscriptEntry:
    return TranscriptEntry(
        id=entry_id,
        session_id="session-1",
        turn_number=turn_number,
        user_message="u",
        assistant_message="a",
        agent_id=agent_id,
        timestamp=datetime.now(),
        metadata=metadata or {},
    )


def test_correlate_promotion_entries_filters_by_metadata_keys():
    entries = [
        _entry(
            "e1",
            1,
            metadata={
                "correlation_id": "corr-1",
                "proposal_id": "proposal-1",
                "promotion_id": "promotion-1",
            },
        ),
        _entry(
            "e2",
            2,
            metadata={"correlation_id": "corr-1", "proposal_id": "proposal-2"},
        ),
        _entry(
            "e3",
            3,
            metadata={"correlation_id": "corr-2", "proposal_id": "proposal-1"},
        ),
    ]

    result = correlate_promotion_entries(
        entries,
        proposal_id="proposal-1",
        correlation_id="corr-1",
    )
    assert [entry.id for entry in result] == ["e1"]


def test_build_correlation_index_and_slice_summary():
    entries = [
        _entry("e1", 1, agent_id="planner", metadata={"correlation_id": "corr-1"}),
        _entry(
            "e2",
            2,
            agent_id="writer",
            metadata={"correlation_id": "corr-1", "proposal_id": "proposal-1"},
        ),
    ]

    index = build_correlation_index(entries)
    assert index["correlation_id"]["corr-1"] == ["e1", "e2"]
    assert index["proposal_id"]["proposal-1"] == ["e2"]

    summary = summarize_correlation_slice(entries)
    assert summary["entry_count"] == 2
    assert summary["first_turn"] == 1
    assert summary["last_turn"] == 2
    assert summary["agents"] == ["planner", "writer"]
