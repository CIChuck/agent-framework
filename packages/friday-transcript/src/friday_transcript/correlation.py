"""
Transcript correlation helpers for replay and promotion forensics.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from friday_transcript.models.transcript import TranscriptEntry

CORRELATION_KEYS = ("correlation_id", "proposal_id", "promotion_id")


def filter_entries_by_metadata(
    entries: list[TranscriptEntry], key: str, value: str
) -> list[TranscriptEntry]:
    """Return transcript entries where metadata[key] equals value."""
    return [entry for entry in entries if str(entry.metadata.get(key, "")) == value]


def correlate_promotion_entries(
    entries: list[TranscriptEntry],
    *,
    proposal_id: str | None = None,
    promotion_id: str | None = None,
    correlation_id: str | None = None,
) -> list[TranscriptEntry]:
    """Filter transcript entries using promotion-correlation metadata keys."""
    filtered = entries
    if proposal_id:
        filtered = filter_entries_by_metadata(filtered, "proposal_id", proposal_id)
    if promotion_id:
        filtered = filter_entries_by_metadata(filtered, "promotion_id", promotion_id)
    if correlation_id:
        filtered = filter_entries_by_metadata(
            filtered, "correlation_id", correlation_id
        )
    return filtered


def build_correlation_index(
    entries: list[TranscriptEntry], keys: tuple[str, ...] = CORRELATION_KEYS
) -> dict[str, dict[str, list[str]]]:
    """
    Build lookup index for transcript entry IDs grouped by metadata references.
    """
    index: dict[str, dict[str, list[str]]] = {}
    for key in keys:
        bucket: dict[str, list[str]] = defaultdict(list)
        for entry in entries:
            value = entry.metadata.get(key)
            if value is None:
                continue
            bucket[str(value)].append(entry.id)
        index[key] = dict(bucket)
    return index


def summarize_correlation_slice(
    entries: list[TranscriptEntry],
) -> dict[str, Any]:
    """Summarize a correlated transcript subset for forensic output."""
    if not entries:
        return {
            "entry_count": 0,
            "first_turn": None,
            "last_turn": None,
            "entry_ids": [],
            "agents": [],
        }
    sorted_entries = sorted(entries, key=lambda item: item.turn_number)
    return {
        "entry_count": len(sorted_entries),
        "first_turn": sorted_entries[0].turn_number,
        "last_turn": sorted_entries[-1].turn_number,
        "entry_ids": [entry.id for entry in sorted_entries],
        "agents": sorted(
            {entry.agent_id for entry in sorted_entries if entry.agent_id}
        ),
    }
