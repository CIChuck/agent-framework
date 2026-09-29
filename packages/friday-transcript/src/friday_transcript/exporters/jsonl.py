"""
JSONL transcript exporter.

Exports transcripts to JSON Lines format for training data pipelines,
streaming processing, and data analysis.
"""

import json
from pathlib import Path
from typing import Any, TextIO

from friday_transcript.models.transcript import TranscriptEntry, TranscriptSession
from friday_transcript.stores.protocol import TranscriptStore


class JSONLExporter:
    """
    Export transcripts to JSON Lines format.

    Each line is a self-contained JSON object representing either a session
    or a turn entry. Useful for:
    - Training data pipelines
    - Streaming processing
    - Data analysis with tools like jq
    - Backup and archival
    """

    def __init__(self, store: TranscriptStore) -> None:
        """
        Initialize the JSONL exporter.

        Args:
            store: Transcript store to export from
        """
        self._store = store

    async def export_session(
        self,
        session_id: str,
        output: Path | TextIO,
        include_metadata: bool = True,
        include_session_header: bool = True,
    ) -> int:
        """
        Export a session to JSONL format.

        Args:
            session_id: Session to export
            output: Output file path or file-like object
            include_metadata: Include full metadata in each entry
            include_session_header: Include session info as first line

        Returns:
            Number of entries exported
        """
        # Get session and entries
        session = await self._store.get_session(session_id)
        entries = await self._store.get_entries(session_id, limit=100000)

        # Open file if path provided
        should_close = False
        f: TextIO
        if isinstance(output, Path):
            f = open(output, "w")  # noqa: SIM115
            should_close = True
        else:
            f = output

        try:
            count = 0

            # Write session header if requested
            if include_session_header and session:
                session_data = self._session_to_dict(session)
                session_data["_type"] = "session"
                f.write(json.dumps(session_data) + "\n")
                count += 1

            # Write entries
            for entry in entries:
                entry_data = self._entry_to_dict(entry, include_metadata)
                entry_data["_type"] = "entry"
                f.write(json.dumps(entry_data) + "\n")
                count += 1

            return count
        finally:
            if should_close:
                f.close()

    async def export_training_data(
        self,
        session_id: str,
        output: Path | TextIO,
        format_style: str = "chat",
    ) -> int:
        """
        Export session as training data format.

        Args:
            session_id: Session to export
            output: Output file path or file-like object
            format_style: Format style - "chat" (OpenAI format), "qa" (question/answer pairs)

        Returns:
            Number of examples exported
        """  # noqa: E501
        session = await self._store.get_session(session_id)
        entries = await self._store.get_entries(session_id, limit=100000)

        # Open file if path provided
        should_close = False
        f: TextIO
        if isinstance(output, Path):
            f = open(output, "w")  # noqa: SIM115
            should_close = True
        else:
            f = output

        try:
            count = 0

            if format_style == "chat":
                # OpenAI chat format
                messages = []
                if session and session.system_prompt:
                    messages.append(
                        {"role": "system", "content": session.system_prompt}
                    )

                for entry in entries:
                    if entry.user_message:
                        messages.append({"role": "user", "content": entry.user_message})
                    if entry.assistant_message:
                        messages.append(
                            {"role": "assistant", "content": entry.assistant_message}
                        )

                f.write(json.dumps({"messages": messages}) + "\n")
                count = 1

            elif format_style == "qa":
                # Question/answer pairs
                for entry in entries:
                    if entry.user_message and entry.assistant_message:
                        qa_data: dict[str, Any] = {
                            "question": entry.user_message,
                            "answer": entry.assistant_message,
                            "session_id": session_id,
                            "turn_number": entry.turn_number,
                        }
                        if entry.metadata:
                            qa_data["metadata"] = entry.metadata
                        f.write(json.dumps(qa_data) + "\n")
                        count += 1

            return count
        finally:
            if should_close:
                f.close()

    def _session_to_dict(self, session: TranscriptSession) -> dict[str, Any]:
        """Convert session to dict for JSON serialization."""
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "model_name": session.model_name,
            "system_prompt": session.system_prompt,
            "config_snapshot": session.config_snapshot,
            "total_turns": session.total_turns,
            "total_tokens": session.total_tokens,
            "total_latency_ms": session.total_latency_ms,
            "metadata": session.metadata,
        }

    def _entry_to_dict(
        self, entry: TranscriptEntry, include_metadata: bool = True
    ) -> dict[str, Any]:
        """Convert entry to dict for JSON serialization."""
        data: dict[str, Any] = {
            "session_id": entry.session_id,
            "turn_number": entry.turn_number,
            "user_message": entry.user_message,
            "assistant_message": entry.assistant_message,
            "timestamp": entry.timestamp.isoformat(),
        }

        if include_metadata:
            data["id"] = entry.id
            data["tool_calls"] = [tc.model_dump() for tc in entry.tool_calls]
            data["tool_results"] = [tr.model_dump() for tr in entry.tool_results]
            data["response_started_at"] = (
                entry.response_started_at.isoformat()
                if entry.response_started_at
                else None
            )
            data["response_completed_at"] = (
                entry.response_completed_at.isoformat()
                if entry.response_completed_at
                else None
            )
            data["prompt_tokens"] = entry.prompt_tokens
            data["completion_tokens"] = entry.completion_tokens
            data["total_tokens"] = entry.total_tokens
            data["latency_ms"] = entry.latency_ms
            data["model_name"] = entry.model_name
            data["temperature"] = entry.temperature
            data["context_tokens_used"] = entry.context_tokens_used
            data["metadata"] = entry.metadata

        return data
