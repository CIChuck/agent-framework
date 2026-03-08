# mypy: ignore-errors
"""
CSV transcript exporter.

Exports transcripts to CSV format for spreadsheet analysis,
database import, and data processing pipelines.

All fields are quoted for safe handling of text containing commas and quotes.
Text content is sanitized to remove newlines and tabs for single-line records.
"""

import csv
import json
from pathlib import Path
from typing import Any, TextIO

from friday_transcript.models.transcript import TranscriptEntry, TranscriptSession
from friday_transcript.stores.protocol import TranscriptStore


class CSVExporter:
    """
    Export transcripts to CSV format.

    Provides methods to export:
    - Individual sessions to a single CSV
    - All sessions metadata to sessions.csv
    - All entries to entries.csv
    - Complete database export (sessions + entries)

    Useful for:
    - Spreadsheet analysis (Excel, Google Sheets)
    - Database import
    - Data analysis with pandas
    - Backup and archival

    Note:
        All fields are quoted for safe handling of text containing
        commas, quotes, and special characters. Text content is
        sanitized to remove newlines and tabs.

        Import example:
            import pandas as pd
            df = pd.read_csv('entries.csv')
    """

    def __init__(
        self,
        store: TranscriptStore,
        delimiter: str = ",",
        quoting: int = csv.QUOTE_ALL,
    ) -> None:
        """
        Initialize the CSV exporter.

        Args:
            store: Transcript store to export from
            delimiter: Field delimiter (default: comma)
            quoting: CSV quoting mode (default: QUOTE_ALL for maximum safety)
        """
        self._store = store
        self._delimiter = delimiter
        self._quoting = quoting

    def _sanitize_text(self, text: str | None) -> str:
        """
        Sanitize text for safe CSV export.

        Removes problematic control characters and whitespace that can
        break CSV parsers or cause multi-line records:
        - Null bytes (\x00)
        - Carriage returns (\r)
        - Line feeds (\n)
        - Tabs (\t)

        Args:
            text: Text to sanitize (may be None)

        Returns:
            Sanitized single-line text string
        """
        if not text:
            return ""
        # Remove null bytes (can break parsers)
        text = text.replace("\x00", "")
        # Remove carriage returns and line feeds (prevent multi-line records)
        text = text.replace("\r\n", " ")  # Windows line endings first
        text = text.replace("\r", " ")
        text = text.replace("\n", " ")
        # Remove tabs
        text = text.replace("\t", " ")
        # Collapse multiple spaces into single space
        while "  " in text:
            text = text.replace("  ", " ")
        return text.strip()

    def _create_writer(
        self,
        f: TextIO,
        fieldnames: list[str],
    ) -> csv.DictWriter:
        """
        Create a CSV DictWriter with consistent configuration.

        Args:
            f: File-like object to write to
            fieldnames: List of column names

        Returns:
            Configured DictWriter instance
        """
        return csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter=self._delimiter,
            quoting=self._quoting,
            quotechar='"',
            doublequote=True,
        )

    async def export_session(
        self,
        session_id: str,
        output: Path | TextIO,
        include_header: bool = True,
    ) -> int:
        """
        Export a single session's entries to CSV.

        Args:
            session_id: Session to export
            output: Output file path or file-like object
            include_header: Include column headers

        Returns:
            Number of entries exported
        """
        entries = await self._store.get_entries(session_id, limit=100000)

        should_close = False
        if isinstance(output, Path):
            f = open(output, "w", newline="", encoding="utf-8")  # noqa: SIM115
            should_close = True
        else:
            f = output

        try:
            writer = self._create_writer(f, self._entry_fieldnames())
            if include_header:
                writer.writeheader()

            count = 0
            for entry in entries:
                writer.writerow(self._entry_to_row(entry))
                count += 1

            return count
        finally:
            if should_close:
                f.close()

    async def export_all_sessions(
        self,
        output_dir: Path,
        user_id: str | None = None,
    ) -> dict[str, int]:
        """
        Export entire transcript database to CSV files.

        Creates two files in output_dir:
        - sessions.csv: All session metadata
        - entries.csv: All transcript entries

        Args:
            output_dir: Directory to write CSV files
            user_id: Optional filter by user_id

        Returns:
            Dict with counts: {"sessions": N, "entries": M}
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export sessions
        sessions = await self._store.list_sessions(user_id=user_id, limit=100000)
        sessions_path = output_dir / "sessions.csv"
        sessions_count = await self._export_sessions_csv(sessions, sessions_path)

        # Export all entries
        entries_path = output_dir / "entries.csv"
        entries_count = 0

        with open(entries_path, "w", newline="", encoding="utf-8") as f:
            writer = self._create_writer(f, self._entry_fieldnames())
            writer.writeheader()

            for session in sessions:
                entries = await self._store.get_entries(
                    session.session_id, limit=100000
                )
                for entry in entries:
                    writer.writerow(self._entry_to_row(entry))
                    entries_count += 1

        return {"sessions": sessions_count, "entries": entries_count}

    async def _export_sessions_csv(
        self,
        sessions: list[TranscriptSession],
        output_path: Path,
    ) -> int:
        """Export sessions to CSV file."""
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = self._create_writer(f, self._session_fieldnames())
            writer.writeheader()

            for session in sessions:
                writer.writerow(self._session_to_row(session))

        return len(sessions)

    def _session_fieldnames(self) -> list[str]:
        """Column names for sessions CSV."""
        return [
            "session_id",
            "user_id",
            "started_at",
            "ended_at",
            "model_name",
            "system_prompt",
            "total_turns",
            "total_tokens",
            "total_latency_ms",
            "config_snapshot",
            "metadata",
        ]

    def _entry_fieldnames(self) -> list[str]:
        """Column names for entries CSV."""
        return [
            "id",
            "session_id",
            "turn_number",
            "timestamp",
            "user_message",
            "assistant_message",
            "tool_calls",
            "tool_results",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "latency_ms",
            "model_name",
            "temperature",
            "context_tokens_used",
            "response_started_at",
            "response_completed_at",
            "metadata",
        ]

    def _session_to_row(self, session: TranscriptSession) -> dict[str, Any]:
        """Convert session to CSV row dict with sanitized text fields."""
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else "",
            "model_name": session.model_name or "",
            "system_prompt": self._sanitize_text(session.system_prompt),
            "total_turns": session.total_turns,
            "total_tokens": session.total_tokens,
            "total_latency_ms": session.total_latency_ms,
            "config_snapshot": json.dumps(session.config_snapshot)
            if session.config_snapshot
            else "",
            "metadata": json.dumps(session.metadata) if session.metadata else "",
        }

    def _entry_to_row(self, entry: TranscriptEntry) -> dict[str, Any]:
        """Convert entry to CSV row dict with sanitized text fields."""
        return {
            "id": entry.id,
            "session_id": entry.session_id,
            "turn_number": entry.turn_number,
            "timestamp": entry.timestamp.isoformat(),
            "user_message": self._sanitize_text(entry.user_message),
            "assistant_message": self._sanitize_text(entry.assistant_message),
            "tool_calls": json.dumps([tc.model_dump() for tc in entry.tool_calls])
            if entry.tool_calls
            else "",
            "tool_results": json.dumps([tr.model_dump() for tr in entry.tool_results])
            if entry.tool_results
            else "",
            "prompt_tokens": entry.prompt_tokens
            if entry.prompt_tokens is not None
            else "",
            "completion_tokens": entry.completion_tokens
            if entry.completion_tokens is not None
            else "",
            "total_tokens": entry.total_tokens
            if entry.total_tokens is not None
            else "",
            "latency_ms": entry.latency_ms if entry.latency_ms is not None else "",
            "model_name": entry.model_name or "",
            "temperature": entry.temperature if entry.temperature is not None else "",
            "context_tokens_used": entry.context_tokens_used
            if entry.context_tokens_used is not None
            else "",
            "response_started_at": entry.response_started_at.isoformat()
            if entry.response_started_at
            else "",
            "response_completed_at": entry.response_completed_at.isoformat()
            if entry.response_completed_at
            else "",
            "metadata": json.dumps(entry.metadata) if entry.metadata else "",
        }
