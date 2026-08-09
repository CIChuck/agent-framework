"""Persisted transcript and export commands for FridayV2."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

from friday_chat.commands.contracts import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)
from friday_chat.transcripts import (
    TranscriptContextLogView,
    TranscriptEntryView,
    TranscriptExportResult,
    TranscriptSessionView,
)

SESSION_QUERY_LIMIT = 1000
TRANSCRIPT_DISPLAY_ENTRY_LIMIT = 100
TRANSCRIPT_DISPLAY_MESSAGE_LIMIT = 500

_TRANSCRIPT_UNAVAILABLE = "Transcript storage is unavailable."
_TRANSCRIPT_EXPORT_FAILED = "Unable to export transcript data."


async def sessions_handler(
    context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """List persisted transcript sessions and in-process identity markers."""
    if context.runtime is None or context.session_identity is None:
        return CommandResult(output=_TRANSCRIPT_UNAVAILABLE)
    try:
        sessions = await context.runtime.transcript.query_sessions(
            limit=SESSION_QUERY_LIMIT,
            include_archived=False,
        )
    except Exception:
        return CommandResult(output=_TRANSCRIPT_UNAVAILABLE)

    current_id = context.session_identity.value
    persisted_ids = {session.session_id for session in sessions}
    primed_ids = _primed_session_ids(context, sessions, current_id=current_id)
    lines = ["Transcript sessions:"]
    if current_id not in persisted_ids:
        try:
            current_session = await context.runtime.transcript.query_session(current_id)
        except Exception:
            return CommandResult(output=_TRANSCRIPT_UNAVAILABLE)
        if current_session is None:
            lines.append(f"- {current_id} (0 turns) [current, not persisted]")
        else:
            archived_marker = ", archived" if current_session.archived else ""
            lines.append(
                f"- {current_id} ({current_session.total_turns} turns) "
                f"[current{archived_marker}]"
            )
    for session in sessions:
        markers: list[str] = []
        if session.session_id == current_id:
            markers.append("current")
        if session.session_id in primed_ids:
            markers.append("primed")
        marker_text = f" [{', '.join(markers)}]" if markers else ""
        lines.append(
            f"- {session.session_id} ({session.total_turns} turns){marker_text}"
        )
    return CommandResult(output="\n".join(lines))


async def transcript_handler(
    context: CommandContext,
    args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """Show a persisted transcript or export all non-archived sessions."""
    if context.runtime is None or context.session_identity is None:
        return CommandResult(output=_TRANSCRIPT_UNAVAILABLE)
    if args and args[0] == "export":
        if len(args) > 1:
            return CommandResult(output="Usage: /transcript [session_id|export]")
        return await _export_all_sessions(context)
    if len(args) > 1:
        return CommandResult(output="Usage: /transcript [session_id|export]")

    session_id = args[0] if args else context.session_identity.value
    try:
        session = await context.runtime.transcript.query_session(session_id)
        if session is None:
            return _missing_session_result(
                session_id,
                current_id=context.session_identity.value,
            )
        entries = await context.runtime.transcript.query_entries(session_id)
    except Exception:
        return CommandResult(output=_TRANSCRIPT_UNAVAILABLE)
    return CommandResult(output=_format_transcript(context, session, entries))


async def export_handler(
    context: CommandContext,
    args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """Export the current persisted session in one supported format."""
    if context.runtime is None or context.session_identity is None:
        return CommandResult(output=_TRANSCRIPT_UNAVAILABLE)
    if len(args) > 1:
        return CommandResult(output="Usage: /export [csv|jsonl|markdown|md|training]")
    export_format = args[0].lower() if args else "markdown"
    if export_format == "md":
        export_format = "markdown"
    if export_format not in {"csv", "jsonl", "markdown", "training"}:
        return CommandResult(output="Usage: /export [csv|jsonl|markdown|md|training]")

    session_id = context.session_identity.value
    try:
        session = await context.runtime.transcript.query_session(session_id)
        if session is None:
            return _missing_session_result(session_id, current_id=session_id)
        entries = await context.runtime.transcript.query_entries(session_id)
        export = _write_current_session_export(
            context,
            session,
            entries,
            export_format,
        )
    except Exception:
        return CommandResult(output=_TRANSCRIPT_EXPORT_FAILED)
    return CommandResult(
        output=(
            "Exported current session "
            f"({_record_count(export.entry_count, 'entry')}) to {export.files[0]}"
        )
    )


async def export_prompts_handler(
    context: CommandContext,
    args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """Export persisted raw context logs for current or selected session."""
    if context.runtime is None or context.session_identity is None:
        return CommandResult(output=_TRANSCRIPT_UNAVAILABLE)
    if len(args) > 1:
        return CommandResult(output="Usage: /export-prompts [session_id]")
    session_id = args[0] if args else context.session_identity.value
    try:
        session = await context.runtime.transcript.query_session(session_id)
        if session is None:
            return _missing_session_result(
                session_id,
                current_id=context.session_identity.value,
            )
        context_logs = await context.runtime.transcript.query_context_logs(session_id)
        if not context_logs:
            return CommandResult(
                output=(
                    f"No captured raw prompts for session {session_id}. "
                    "Enable transcript.capture_raw_prompts to capture them."
                )
            )
        export = _write_context_log_export(context, session, context_logs)
    except Exception:
        return CommandResult(output=_TRANSCRIPT_EXPORT_FAILED)
    return CommandResult(
        output=(
            f"Exported {_record_count(export.context_log_count, 'prompt record')} "
            f"to {export.files[0]}"
        )
    )


async def _export_all_sessions(context: CommandContext) -> CommandResult:
    if context.runtime is None:
        return CommandResult(output=_TRANSCRIPT_UNAVAILABLE)
    try:
        sessions = await context.runtime.transcript.query_sessions(
            limit=SESSION_QUERY_LIMIT,
            include_archived=False,
        )
        collected_entries: list[
            tuple[TranscriptSessionView, tuple[TranscriptEntryView, ...]]
        ] = []
        for session in sessions:
            entries = await context.runtime.transcript.query_entries(
                session.session_id
            )
            collected_entries.append((session, entries))
        entries_by_session = tuple(collected_entries)
        export = _write_all_session_export(context, entries_by_session)
    except Exception:
        return CommandResult(output=_TRANSCRIPT_EXPORT_FAILED)
    return CommandResult(
        output=(
            f"Exported {_record_count(export.session_count, 'session')} and "
            f"{_record_count(export.entry_count, 'entry')} to "
            f"{export.files[0].parent}"
        )
    )


def export_directory(context: CommandContext) -> Path:
    """Resolve and create the configured transcript export root."""
    directory = Path("./exports")
    if context.runtime is not None and context.runtime.config.transcript.export_directory:
        directory = Path(context.runtime.config.transcript.export_directory)
    resolved = directory.resolve(strict=False)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _primed_session_ids(
    context: CommandContext,
    sessions: tuple[TranscriptSessionView, ...],
    *,
    current_id: str,
) -> frozenset[str]:
    if context.runtime is None:
        return frozenset()
    priming = context.runtime.config.memory.priming
    if priming.get("enabled") is not True:
        return frozenset()
    raw_count = priming.get("previous_sessions", 0)
    count = raw_count if isinstance(raw_count, int) and not isinstance(raw_count, bool) else 0
    if count <= 0:
        return frozenset()
    previous = [
        session.session_id
        for session in sessions
        if session.session_id != current_id and not session.archived
    ]
    return frozenset(previous[:count])


def _missing_session_result(session_id: str, *, current_id: str) -> CommandResult:
    if session_id == current_id:
        return CommandResult(
            output=f"No persisted transcript exists for current session: {session_id}"
        )
    return CommandResult(output=f"Transcript session not found: {session_id}")


def _format_transcript(
    context: CommandContext,
    session: TranscriptSessionView,
    entries: tuple[TranscriptEntryView, ...],
) -> str:
    status = "archived" if session.archived else (
        "active" if session.ended_at is None else "ended"
    )
    lines = [
        f"Transcript: {session.session_id}",
        f"Status: {status}",
        f"Started: {session.started_at.isoformat()}",
        f"Model: {session.model_name}",
        f"Entries: {len(entries)}",
    ]
    if not entries:
        lines.append("No transcript entries recorded.")
        return "\n".join(lines)

    user_name = (
        context.runtime.config.chat.user_name if context.runtime is not None else "User"
    )
    assistant_name = (
        context.runtime.config.chat.assistant_name
        if context.runtime is not None
        else "Friday"
    )
    for entry in entries[:TRANSCRIPT_DISPLAY_ENTRY_LIMIT]:
        lines.append(
            f"{entry.turn_number}. {user_name}: "
            f"{_display_text(entry.user_message)}"
        )
        lines.append(f"   {assistant_name}: {_display_text(entry.assistant_message)}")
    omitted = len(entries) - TRANSCRIPT_DISPLAY_ENTRY_LIMIT
    if omitted > 0:
        lines.append(f"... {_record_count(omitted, 'additional entry')} omitted.")
    return "\n".join(lines)


def _display_text(text: str | None) -> str:
    if text is None:
        return "(none)"
    normalized = " ".join(text.split())
    if len(normalized) <= TRANSCRIPT_DISPLAY_MESSAGE_LIMIT:
        return normalized
    return normalized[: TRANSCRIPT_DISPLAY_MESSAGE_LIMIT - 3] + "..."


def _write_all_session_export(
    context: CommandContext,
    entries_by_session: tuple[
        tuple[TranscriptSessionView, tuple[TranscriptEntryView, ...]],
        ...,
    ],
) -> TranscriptExportResult:
    root = export_directory(context)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    directory = _safe_export_path(root, f"transcript-export-{timestamp}")
    directory.mkdir(parents=False, exist_ok=False)
    sessions_path = _safe_export_path(directory, "sessions.csv")
    entries_path = _safe_export_path(directory, "entries.csv")

    session_rows = [
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
        for session, _entries in entries_by_session
    ]
    entry_rows = [
        _entry_csv_row(entry)
        for _session, entries in entries_by_session
        for entry in entries
    ]
    sessions_path.write_text(
        _csv_text(
            (
                "session_id",
                "user_id",
                "started_at",
                "ended_at",
                "model_name",
                "total_turns",
                "total_tokens",
                "archived",
            ),
            session_rows,
        ),
        encoding="utf-8",
    )
    entries_path.write_text(
        _csv_text(
            (
                "session_id",
                "turn_number",
                "timestamp",
                "user_message",
                "assistant_message",
                "model_name",
                "total_tokens",
                "latency_ms",
            ),
            entry_rows,
        ),
        encoding="utf-8",
    )
    return TranscriptExportResult(
        files=(sessions_path, entries_path),
        session_count=len(session_rows),
        entry_count=len(entry_rows),
    )


def _write_current_session_export(
    context: CommandContext,
    session: TranscriptSessionView,
    entries: tuple[TranscriptEntryView, ...],
    export_format: str,
) -> TranscriptExportResult:
    root = export_directory(context)
    if export_format == "csv":
        path = _safe_export_path(root, "friday_current_session.csv")
        path.write_text(
            _csv_text(
                (
                    "session_id",
                    "turn_number",
                    "timestamp",
                    "user_message",
                    "assistant_message",
                    "model_name",
                    "total_tokens",
                    "latency_ms",
                ),
                [_entry_csv_row(entry) for entry in entries],
            ),
            encoding="utf-8",
        )
    elif export_format == "jsonl":
        path = _safe_export_path(root, "friday_current_session.jsonl")
        lines = [
            json.dumps(_entry_json_record(entry), ensure_ascii=False, sort_keys=True)
            for entry in entries
        ]
        path.write_text("\n".join(lines), encoding="utf-8")
    elif export_format == "training":
        path = _safe_export_path(root, "friday_current_session_training.jsonl")
        lines = [
            json.dumps(
                {
                    "messages": [
                        {"role": "user", "content": entry.user_message or ""},
                        {
                            "role": "assistant",
                            "content": entry.assistant_message or "",
                        },
                    ]
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            for entry in entries
        ]
        path.write_text("\n".join(lines), encoding="utf-8")
    else:
        path = _safe_export_path(root, "friday_current_session.md")
        path.write_text(
            _format_transcript_markdown(context, session, entries),
            encoding="utf-8",
        )
    return TranscriptExportResult(files=(path,), entry_count=len(entries))


def _write_context_log_export(
    context: CommandContext,
    session: TranscriptSessionView,
    context_logs: tuple[TranscriptContextLogView, ...],
) -> TranscriptExportResult:
    path = _safe_export_path(export_directory(context), "friday_prompts.json")
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
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return TranscriptExportResult(
        files=(path,),
        session_count=1,
        context_log_count=len(context_logs),
    )


def _safe_export_path(root: Path, *parts: str) -> Path:
    resolved_root = root.resolve(strict=False)
    candidate = resolved_root.joinpath(*parts).resolve(strict=False)
    if not candidate.is_relative_to(resolved_root):
        raise ValueError("export path escaped configured root")
    return candidate


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


def _format_transcript_markdown(
    context: CommandContext,
    session: TranscriptSessionView,
    entries: tuple[TranscriptEntryView, ...],
) -> str:
    user_name = (
        context.runtime.config.chat.user_name if context.runtime is not None else "User"
    )
    assistant_name = (
        context.runtime.config.chat.assistant_name
        if context.runtime is not None
        else "Friday"
    )
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


def _record_count(count: int, noun: str) -> str:
    if count == 1:
        return f"{count} {noun}"
    irregular = {
        "additional entry": "additional entries",
        "entry": "entries",
    }
    return f"{count} {irregular.get(noun, noun + 's')}"


__all__ = [
    "export_directory",
    "export_handler",
    "export_prompts_handler",
    "sessions_handler",
    "transcript_handler",
]
