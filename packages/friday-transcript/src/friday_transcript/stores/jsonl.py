# mypy: ignore-errors
"""
JSONL-based transcript store.

Simple, portable backend using JSON Lines format.
Each line is a self-contained JSON object for easy streaming and processing.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from friday_transcript.models.transcript import (
    ToolCall,
    ToolResult,
    TranscriptEntry,
    TranscriptSession,
)

logger = logging.getLogger(__name__)


class JSONLTranscriptStore:
    """
    JSONL-backed transcript store.

    Stores transcripts in JSON Lines format:
    - sessions.jsonl: One session per line
    - entries.jsonl: One entry per line

    Simple, portable, and easy to process with standard tools.
    Suitable for export, backup, and data pipeline integration.
    """

    def __init__(self, directory: str | Path) -> None:
        """
        Initialize JSONL transcript store.

        Args:
            directory: Directory to store JSONL files
        """
        self._dir = Path(directory)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._sessions_file = self._dir / "sessions.jsonl"
        self._entries_file = self._dir / "entries.jsonl"

        # In-memory index for faster lookups
        self._session_cache: dict[str, TranscriptSession] = {}
        self._loaded = False

    async def _ensure_loaded(self) -> None:
        """Load session index into memory."""
        if self._loaded:
            return

        if self._sessions_file.exists():
            with open(self._sessions_file) as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        session = self._dict_to_session(data)
                        self._session_cache[session.session_id] = session

        self._loaded = True

    # --- Session Management ---

    async def create_session(self, session: TranscriptSession) -> bool:
        """Create a new transcript session."""
        await self._ensure_loaded()

        if session.session_id in self._session_cache:
            logger.warning(f"Session already exists: {session.session_id}")
            return False

        # Append to file
        with open(self._sessions_file, "a") as f:
            f.write(json.dumps(self._session_to_dict(session)) + "\n")

        # Update cache
        self._session_cache[session.session_id] = session
        logger.debug(f"Created session: {session.session_id}")
        return True

    async def end_session(self, session_id: str) -> bool:
        """Mark a session as ended."""
        await self._ensure_loaded()

        if session_id not in self._session_cache:
            return False

        session = self._session_cache[session_id]
        if session.ended_at is not None:
            return False

        # Update in memory
        session.ended_at = datetime.now()

        # Rewrite sessions file (JSONL doesn't support in-place updates)
        await self._rewrite_sessions()
        return True

    async def get_session(self, session_id: str) -> TranscriptSession | None:
        """Retrieve session metadata."""
        await self._ensure_loaded()
        return self._session_cache.get(session_id)

    async def list_sessions(
        self,
        limit: int = 100,
        offset: int = 0,
        user_id: str | None = None,
        active_only: bool = False,
    ) -> list[TranscriptSession]:
        """List transcript sessions."""
        await self._ensure_loaded()

        sessions = list(self._session_cache.values())

        # Filter
        if user_id is not None:
            sessions = [s for s in sessions if s.user_id == user_id]
        if active_only:
            sessions = [s for s in sessions if s.ended_at is None]

        # Sort by start time (newest first)
        sessions.sort(key=lambda s: s.started_at, reverse=True)

        # Paginate
        return sessions[offset : offset + limit]

    async def _rewrite_sessions(self) -> None:
        """Rewrite the sessions file from cache."""
        with open(self._sessions_file, "w") as f:
            for session in self._session_cache.values():
                f.write(json.dumps(self._session_to_dict(session)) + "\n")

    def _session_to_dict(self, session: TranscriptSession) -> dict[str, Any]:
        """Convert TranscriptSession to dict for JSON serialization."""
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

    def _dict_to_session(self, data: dict[str, Any]) -> TranscriptSession:
        """Convert dict to TranscriptSession."""
        return TranscriptSession(
            session_id=data["session_id"],
            user_id=data.get("user_id"),
            started_at=datetime.fromisoformat(data["started_at"]),
            ended_at=(
                datetime.fromisoformat(data["ended_at"])
                if data.get("ended_at")
                else None
            ),
            model_name=data["model_name"],
            system_prompt=data.get("system_prompt"),
            config_snapshot=data.get("config_snapshot", {}),
            total_turns=data.get("total_turns", 0),
            total_tokens=data.get("total_tokens", 0),
            total_latency_ms=data.get("total_latency_ms", 0),
            metadata=data.get("metadata", {}),
        )

    # --- Entry Management ---

    async def append_entry(self, entry: TranscriptEntry) -> bool:
        """Append a transcript entry."""
        await self._ensure_loaded()

        # Append to file
        with open(self._entries_file, "a") as f:
            f.write(json.dumps(self._entry_to_dict(entry)) + "\n")

        # Update session aggregates in cache
        if entry.session_id in self._session_cache:
            session = self._session_cache[entry.session_id]
            session.total_turns += 1
            session.total_tokens += entry.total_tokens or 0
            session.total_latency_ms += entry.latency_ms or 0
            # Note: Session file will be stale until end_session or explicit save

        logger.debug(f"Appended entry: {entry.id} (turn {entry.turn_number})")
        return True

    async def get_entries(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
        after: datetime | None = None,
        before: datetime | None = None,
    ) -> list[TranscriptEntry]:
        """Retrieve transcript entries for a session."""
        entries = []

        if not self._entries_file.exists():
            return entries

        with open(self._entries_file) as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                if data.get("session_id") != session_id:
                    continue

                timestamp = datetime.fromisoformat(data["timestamp"])
                if after is not None and timestamp <= after:
                    continue
                if before is not None and timestamp >= before:
                    continue

                entries.append(self._dict_to_entry(data))

        # Sort by turn number
        entries.sort(key=lambda e: e.turn_number)

        # Paginate
        return entries[offset : offset + limit]

    async def get_entry(self, entry_id: str) -> TranscriptEntry | None:
        """Retrieve a single entry by ID."""
        if not self._entries_file.exists():
            return None

        with open(self._entries_file) as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                if data.get("id") == entry_id:
                    return self._dict_to_entry(data)

        return None

    async def count_entries(self, session_id: str) -> int:
        """Count entries in a session."""
        count = 0

        if not self._entries_file.exists():
            return count

        with open(self._entries_file) as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                if data.get("session_id") == session_id:
                    count += 1

        return count

    def _entry_to_dict(self, entry: TranscriptEntry) -> dict[str, Any]:
        """Convert TranscriptEntry to dict for JSON serialization."""
        return {
            "id": entry.id,
            "session_id": entry.session_id,
            "turn_number": entry.turn_number,
            "user_message": entry.user_message,
            "assistant_message": entry.assistant_message,
            "tool_calls": [tc.model_dump() for tc in entry.tool_calls],
            "tool_results": [tr.model_dump() for tr in entry.tool_results],
            "timestamp": entry.timestamp.isoformat(),
            "response_started_at": (
                entry.response_started_at.isoformat()
                if entry.response_started_at
                else None
            ),
            "response_completed_at": (
                entry.response_completed_at.isoformat()
                if entry.response_completed_at
                else None
            ),
            "prompt_tokens": entry.prompt_tokens,
            "completion_tokens": entry.completion_tokens,
            "total_tokens": entry.total_tokens,
            "latency_ms": entry.latency_ms,
            "model_name": entry.model_name,
            "temperature": entry.temperature,
            "context_tokens_used": entry.context_tokens_used,
            "metadata": entry.metadata,
        }

    def _dict_to_entry(self, data: dict[str, Any]) -> TranscriptEntry:
        """Convert dict to TranscriptEntry."""
        return TranscriptEntry(
            id=data["id"],
            session_id=data["session_id"],
            turn_number=data["turn_number"],
            user_message=data.get("user_message"),
            assistant_message=data.get("assistant_message"),
            tool_calls=[ToolCall(**tc) for tc in data.get("tool_calls", [])],
            tool_results=[ToolResult(**tr) for tr in data.get("tool_results", [])],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            response_started_at=(
                datetime.fromisoformat(data["response_started_at"])
                if data.get("response_started_at")
                else None
            ),
            response_completed_at=(
                datetime.fromisoformat(data["response_completed_at"])
                if data.get("response_completed_at")
                else None
            ),
            prompt_tokens=data.get("prompt_tokens"),
            completion_tokens=data.get("completion_tokens"),
            total_tokens=data.get("total_tokens"),
            latency_ms=data.get("latency_ms"),
            model_name=data.get("model_name"),
            temperature=data.get("temperature"),
            context_tokens_used=data.get("context_tokens_used"),
            metadata=data.get("metadata", {}),
        )

    # --- Analytics ---

    async def get_token_stats(self, session_id: str) -> dict[str, Any]:
        """Get token usage statistics for a session."""
        entries = await self.get_entries(session_id, limit=10000)

        if not entries:
            return {
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_tokens": 0,
                "avg_tokens_per_turn": 0,
                "max_tokens_turn": 0,
                "turn_count": 0,
            }

        total_prompt = sum(e.prompt_tokens or 0 for e in entries)
        total_completion = sum(e.completion_tokens or 0 for e in entries)
        total = sum(e.total_tokens or 0 for e in entries)
        max_tokens = max((e.total_tokens or 0) for e in entries)

        return {
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_tokens": total,
            "avg_tokens_per_turn": total / len(entries) if entries else 0,
            "max_tokens_turn": max_tokens,
            "turn_count": len(entries),
        }

    async def get_latency_stats(self, session_id: str) -> dict[str, Any]:
        """Get latency statistics for a session."""
        entries = await self.get_entries(session_id, limit=10000)
        latencies = [e.latency_ms for e in entries if e.latency_ms is not None]

        if not latencies:
            return {
                "total_latency_ms": 0,
                "avg_latency_ms": 0,
                "min_latency_ms": 0,
                "max_latency_ms": 0,
                "p50_latency_ms": 0,
                "p95_latency_ms": 0,
            }

        latencies.sort()
        n = len(latencies)

        return {
            "total_latency_ms": sum(latencies),
            "avg_latency_ms": sum(latencies) / n,
            "min_latency_ms": latencies[0],
            "max_latency_ms": latencies[-1],
            "p50_latency_ms": latencies[n // 2],
            "p95_latency_ms": latencies[int(n * 0.95)] if n > 1 else latencies[0],
        }
