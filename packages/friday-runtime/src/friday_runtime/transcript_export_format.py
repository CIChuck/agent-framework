"""Pure transcript export formatting over UI-neutral persisted views."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Sequence

from friday_runtime.transcript_views import (
    TranscriptContextLogView,
    TranscriptEntryView,
    TranscriptSessionView,
)

_SESSION_CSV_HEADER = (
    "session_id",
    "user_id",
    "started_at",
    "ended_at",
    "model_name",
    "total_turns",
    "total_tokens",
    "archived",
)

_ENTRY_CSV_HEADER = (
    "session_id",
    "turn_number",
    "timestamp",
    "user_message",
    "assistant_message",
    "model_name",
    "total_tokens",
    "latency_ms",
)


def serialize_sessions_csv(sessions: Sequence[TranscriptSessionView]) -> str:
    """Format ordered session metadata as quote-all CSV."""
    rows = [
        (
            session.session_id,
            session.user_id or "",
            session.started_at.isoformat(),
            session.ended_at.isoformat() if session.ended_at is not None else "",
            session.model_name,
            session.total_turns,
            session.total_tokens,
            session.archived,
        )
        for session in sessions
    ]
    return _csv_text(_SESSION_CSV_HEADER, rows)


def serialize_entries_csv(entries: Sequence[TranscriptEntryView]) -> str:
    """Format ordered transcript entries as quote-all CSV."""
    return _csv_text(_ENTRY_CSV_HEADER, [_entry_csv_row(entry) for entry in entries])


def serialize_entries_jsonl(entries: Sequence[TranscriptEntryView]) -> str:
    """Format ordered entries as JSON lines without a final newline."""
    lines = [
        json.dumps(_entry_json_record(entry), ensure_ascii=False, sort_keys=True)
        for entry in entries
    ]
    return "\n".join(lines)


def serialize_training_jsonl(entries: Sequence[TranscriptEntryView]) -> str:
    """Format ordered user/assistant message pairs as training JSON lines."""
    lines = [
        json.dumps(
            {
                "messages": [
                    {"role": "user", "content": entry.user_message or ""},
                    {"role": "assistant", "content": entry.assistant_message or ""},
                ]
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        for entry in entries
    ]
    return "\n".join(lines)


def serialize_transcript_markdown(
    session: TranscriptSessionView,
    entries: Sequence[TranscriptEntryView],
    *,
    user_name: str,
    assistant_name: str,
) -> str:
    """Format ordered entries with caller-supplied display names."""
    lines = [f"# Transcript: {session.session_id}", ""]
    for entry in entries:
        lines.extend(
            (
                f"## Turn {entry.turn_number}",
                "",
                f"**{user_name}:** {entry.user_message or ''}",
                "",
                f"**{assistant_name}:** {entry.assistant_message or ''}",
                "",
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def serialize_context_logs_json(
    session: TranscriptSessionView,
    context_logs: Sequence[TranscriptContextLogView],
) -> str:
    """Format ordered persisted raw context logs as indented JSON."""
    payload = [
        {
            "session_id": session.session_id,
            "turn_number": entry.turn_number,
            "entry_id": entry.entry_id,
            "captured_at": entry.captured_at.isoformat(),
            "prompt": entry.raw_prompt,
            "raw_response": entry.raw_response,
        }
        for entry in context_logs
    ]
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def _csv_text(
    header: tuple[str, ...],
    rows: Sequence[Sequence[object]],
) -> str:
    handle = io.StringIO(newline="")
    writer = csv.writer(handle, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return handle.getvalue()


def _entry_csv_row(entry: TranscriptEntryView) -> tuple[object, ...]:
    return (
        entry.session_id,
        entry.turn_number,
        entry.timestamp.isoformat(),
        entry.user_message or "",
        entry.assistant_message or "",
        entry.model_name or "",
        entry.total_tokens if entry.total_tokens is not None else "",
        entry.latency_ms if entry.latency_ms is not None else "",
    )


def _entry_json_record(entry: TranscriptEntryView) -> dict[str, object]:
    return {
        "assistant_message": entry.assistant_message,
        "entry_id": entry.entry_id,
        "latency_ms": entry.latency_ms,
        "model_name": entry.model_name,
        "session_id": entry.session_id,
        "timestamp": entry.timestamp.isoformat(),
        "total_tokens": entry.total_tokens,
        "turn_number": entry.turn_number,
        "user_message": entry.user_message,
    }


__all__ = [
    "serialize_context_logs_json",
    "serialize_entries_csv",
    "serialize_entries_jsonl",
    "serialize_sessions_csv",
    "serialize_training_jsonl",
    "serialize_transcript_markdown",
]
