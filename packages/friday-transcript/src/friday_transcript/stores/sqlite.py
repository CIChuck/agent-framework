"""
SQLite-based transcript store.

Primary backend for persistent transcript storage.
Uses aiosqlite for async operations.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import aiosqlite

from friday_transcript.models.transcript import (
    TranscriptEntry,
    TranscriptSession,
    ToolCall,
    ToolResult,
)

logger = logging.getLogger(__name__)


class SQLiteTranscriptStore:
    """
    SQLite-backed transcript store.

    Provides persistent, append-only transcript storage with:
    - Full ACID compliance
    - Efficient queries via indexes
    - Built-in analytics aggregation
    """

    def __init__(self, db_path: str | Path) -> None:
        """
        Initialize SQLite transcript store.

        Args:
            db_path: Path to SQLite database file
        """
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Create tables if they don't exist."""
        if self._initialized:
            return

        async with aiosqlite.connect(self._db_path) as db:
            # Sessions table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    model_name TEXT NOT NULL,
                    system_prompt TEXT,
                    config_snapshot TEXT,
                    total_turns INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    total_latency_ms REAL DEFAULT 0,
                    metadata TEXT
                )
            """)

            # Entries table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    turn_number INTEGER NOT NULL,
                    user_message TEXT,
                    assistant_message TEXT,
                    tool_calls TEXT,
                    tool_results TEXT,
                    timestamp TEXT NOT NULL,
                    response_started_at TEXT,
                    response_completed_at TEXT,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    total_tokens INTEGER,
                    latency_ms REAL,
                    model_name TEXT,
                    temperature REAL,
                    context_tokens_used INTEGER,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)

            # Indexes for common queries
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_entries_session
                ON entries(session_id, turn_number)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_entries_timestamp
                ON entries(session_id, timestamp)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_user
                ON sessions(user_id, started_at)
            """)

            await db.commit()
            self._initialized = True

    # --- Session Management ---

    async def create_session(self, session: TranscriptSession) -> bool:
        """Create a new transcript session."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            try:
                await db.execute(
                    """
                    INSERT INTO sessions (
                        session_id, user_id, started_at, ended_at, model_name,
                        system_prompt, config_snapshot, total_turns, total_tokens,
                        total_latency_ms, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session.session_id,
                        session.user_id,
                        session.started_at.isoformat(),
                        session.ended_at.isoformat() if session.ended_at else None,
                        session.model_name,
                        session.system_prompt,
                        json.dumps(session.config_snapshot),
                        session.total_turns,
                        session.total_tokens,
                        session.total_latency_ms,
                        json.dumps(session.metadata),
                    ),
                )
                await db.commit()
                logger.debug(f"Created session: {session.session_id}")
                return True
            except aiosqlite.IntegrityError:
                logger.warning(f"Session already exists: {session.session_id}")
                return False

    async def end_session(self, session_id: str) -> bool:
        """Mark a session as ended."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                """
                UPDATE sessions SET ended_at = ?
                WHERE session_id = ? AND ended_at IS NULL
                """,
                (datetime.now().isoformat(), session_id),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def get_session(self, session_id: str) -> TranscriptSession | None:
        """Retrieve session metadata."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_session(row)

    async def list_sessions(
        self,
        limit: int = 100,
        offset: int = 0,
        user_id: str | None = None,
        active_only: bool = False,
    ) -> list[TranscriptSession]:
        """List transcript sessions."""
        await self._ensure_initialized()

        query = "SELECT * FROM sessions WHERE 1=1"
        params: list[Any] = []

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)

        if active_only:
            query += " AND ended_at IS NULL"

        query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [self._row_to_session(row) for row in rows]

    def _row_to_session(self, row: aiosqlite.Row) -> TranscriptSession:
        """Convert database row to TranscriptSession."""
        return TranscriptSession(
            session_id=row["session_id"],
            user_id=row["user_id"],
            started_at=datetime.fromisoformat(row["started_at"]),
            ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
            model_name=row["model_name"],
            system_prompt=row["system_prompt"],
            config_snapshot=json.loads(row["config_snapshot"] or "{}"),
            total_turns=row["total_turns"],
            total_tokens=row["total_tokens"],
            total_latency_ms=row["total_latency_ms"],
            metadata=json.loads(row["metadata"] or "{}"),
        )

    # --- Entry Management ---

    async def append_entry(self, entry: TranscriptEntry) -> bool:
        """Append a transcript entry."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            try:
                # Insert entry
                await db.execute(
                    """
                    INSERT INTO entries (
                        id, session_id, turn_number, user_message, assistant_message,
                        tool_calls, tool_results, timestamp, response_started_at,
                        response_completed_at, prompt_tokens, completion_tokens,
                        total_tokens, latency_ms, model_name, temperature,
                        context_tokens_used, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.id,
                        entry.session_id,
                        entry.turn_number,
                        entry.user_message,
                        entry.assistant_message,
                        json.dumps([tc.model_dump() for tc in entry.tool_calls]),
                        json.dumps([tr.model_dump() for tr in entry.tool_results]),
                        entry.timestamp.isoformat(),
                        entry.response_started_at.isoformat() if entry.response_started_at else None,
                        entry.response_completed_at.isoformat() if entry.response_completed_at else None,
                        entry.prompt_tokens,
                        entry.completion_tokens,
                        entry.total_tokens,
                        entry.latency_ms,
                        entry.model_name,
                        entry.temperature,
                        entry.context_tokens_used,
                        json.dumps(entry.metadata),
                    ),
                )

                # Update session aggregates
                await db.execute(
                    """
                    UPDATE sessions SET
                        total_turns = total_turns + 1,
                        total_tokens = total_tokens + COALESCE(?, 0),
                        total_latency_ms = total_latency_ms + COALESCE(?, 0)
                    WHERE session_id = ?
                    """,
                    (entry.total_tokens, entry.latency_ms, entry.session_id),
                )

                await db.commit()
                logger.debug(f"Appended entry: {entry.id} (turn {entry.turn_number})")
                return True
            except aiosqlite.IntegrityError as e:
                logger.warning(f"Failed to append entry {entry.id}: {e}")
                return False

    async def get_entries(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
        after: datetime | None = None,
        before: datetime | None = None,
    ) -> list[TranscriptEntry]:
        """Retrieve transcript entries for a session."""
        await self._ensure_initialized()

        query = "SELECT * FROM entries WHERE session_id = ?"
        params: list[Any] = [session_id]

        if after is not None:
            query += " AND timestamp > ?"
            params.append(after.isoformat())

        if before is not None:
            query += " AND timestamp < ?"
            params.append(before.isoformat())

        query += " ORDER BY turn_number ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [self._row_to_entry(row) for row in rows]

    async def get_entry(self, entry_id: str) -> TranscriptEntry | None:
        """Retrieve a single entry by ID."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM entries WHERE id = ?",
                (entry_id,),
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_entry(row)

    async def count_entries(self, session_id: str) -> int:
        """Count entries in a session."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM entries WHERE session_id = ?",
                (session_id,),
            )
            row = await cursor.fetchone()
            return row[0] if row else 0

    def _row_to_entry(self, row: aiosqlite.Row) -> TranscriptEntry:
        """Convert database row to TranscriptEntry."""
        tool_calls_data = json.loads(row["tool_calls"] or "[]")
        tool_results_data = json.loads(row["tool_results"] or "[]")

        return TranscriptEntry(
            id=row["id"],
            session_id=row["session_id"],
            turn_number=row["turn_number"],
            user_message=row["user_message"],
            assistant_message=row["assistant_message"],
            tool_calls=[ToolCall(**tc) for tc in tool_calls_data],
            tool_results=[ToolResult(**tr) for tr in tool_results_data],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            response_started_at=(
                datetime.fromisoformat(row["response_started_at"])
                if row["response_started_at"]
                else None
            ),
            response_completed_at=(
                datetime.fromisoformat(row["response_completed_at"])
                if row["response_completed_at"]
                else None
            ),
            prompt_tokens=row["prompt_tokens"],
            completion_tokens=row["completion_tokens"],
            total_tokens=row["total_tokens"],
            latency_ms=row["latency_ms"],
            model_name=row["model_name"],
            temperature=row["temperature"],
            context_tokens_used=row["context_tokens_used"],
            metadata=json.loads(row["metadata"] or "{}"),
        )

    # --- Analytics ---

    async def get_token_stats(self, session_id: str) -> dict[str, Any]:
        """Get token usage statistics for a session."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                """
                SELECT
                    COALESCE(SUM(prompt_tokens), 0) as total_prompt_tokens,
                    COALESCE(SUM(completion_tokens), 0) as total_completion_tokens,
                    COALESCE(SUM(total_tokens), 0) as total_tokens,
                    COALESCE(AVG(total_tokens), 0) as avg_tokens_per_turn,
                    COALESCE(MAX(total_tokens), 0) as max_tokens_turn,
                    COUNT(*) as turn_count
                FROM entries WHERE session_id = ?
                """,
                (session_id,),
            )
            row = await cursor.fetchone()

            return {
                "total_prompt_tokens": row[0],
                "total_completion_tokens": row[1],
                "total_tokens": row[2],
                "avg_tokens_per_turn": row[3],
                "max_tokens_turn": row[4],
                "turn_count": row[5],
            }

    async def get_latency_stats(self, session_id: str) -> dict[str, Any]:
        """Get latency statistics for a session."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            # Get all latencies for percentile calculation
            cursor = await db.execute(
                """
                SELECT latency_ms FROM entries
                WHERE session_id = ? AND latency_ms IS NOT NULL
                ORDER BY latency_ms
                """,
                (session_id,),
            )
            latencies = [row[0] for row in await cursor.fetchall()]

            if not latencies:
                return {
                    "total_latency_ms": 0,
                    "avg_latency_ms": 0,
                    "min_latency_ms": 0,
                    "max_latency_ms": 0,
                    "p50_latency_ms": 0,
                    "p95_latency_ms": 0,
                }

            n = len(latencies)
            return {
                "total_latency_ms": sum(latencies),
                "avg_latency_ms": sum(latencies) / n,
                "min_latency_ms": latencies[0],
                "max_latency_ms": latencies[-1],
                "p50_latency_ms": latencies[n // 2],
                "p95_latency_ms": latencies[int(n * 0.95)] if n > 1 else latencies[0],
            }
