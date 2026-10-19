"""UI-neutral single-file transcript export effects."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from friday_runtime.transcript_export_format import (
    serialize_context_logs_json,
    serialize_entries_csv,
    serialize_entries_jsonl,
    serialize_training_jsonl,
    serialize_transcript_markdown,
)
from friday_runtime.transcript_views import (
    TranscriptContextLogView,
    TranscriptEntryView,
    TranscriptSessionView,
)


def write_current_session_file(
    destination: Path,
    session: TranscriptSessionView,
    entries: Sequence[TranscriptEntryView],
    *,
    export_format: str,
    user_name: str | None = None,
    assistant_name: str | None = None,
) -> None:
    """Write one current-session export to a caller-prevalidated path."""
    if export_format == "csv":
        text = serialize_entries_csv(entries)
    elif export_format == "jsonl":
        text = serialize_entries_jsonl(entries)
    elif export_format == "training":
        text = serialize_training_jsonl(entries)
    elif export_format == "markdown":
        if user_name is None or assistant_name is None:
            raise ValueError("Markdown export requires user and assistant names")
        text = serialize_transcript_markdown(
            session,
            entries,
            user_name=user_name,
            assistant_name=assistant_name,
        )
    else:
        raise ValueError(f"Unsupported transcript export format: {export_format}")
    destination.write_text(text, encoding="utf-8")


def write_context_log_file(
    destination: Path,
    session: TranscriptSessionView,
    context_logs: Sequence[TranscriptContextLogView],
) -> None:
    """Write one persisted context-log export to a caller-prevalidated path."""
    text = serialize_context_logs_json(session, context_logs)
    destination.write_text(text, encoding="utf-8")


__all__ = ["write_context_log_file", "write_current_session_file"]
