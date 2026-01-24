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
            # ACID compliance pragmas
            await db.execute("PRAGMA foreign_keys = ON")
            await db.execute("PRAGMA journal_mode = WAL")
            await db.execute("PRAGMA synchronous = NORMAL")

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

            # Migration: Add consolidated column if not exists
            cursor = await db.execute("PRAGMA table_info(entries)")
            columns = {row[1] for row in await cursor.fetchall()}
            if "consolidated" not in columns:
                await db.execute(
                    "ALTER TABLE entries ADD COLUMN consolidated INTEGER DEFAULT 0"
                )
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_entries_consolidated
                    ON entries(session_id, consolidated)
                """)
                logger.info("Added 'consolidated' column to entries table")

            # Migration: Add archived column to sessions if not exists
            cursor = await db.execute("PRAGMA table_info(sessions)")
            session_columns = {row[1] for row in await cursor.fetchall()}
            if "archived" not in session_columns:
                await db.execute(
                    "ALTER TABLE sessions ADD COLUMN archived INTEGER DEFAULT 0"
                )
                logger.info("Added 'archived' column to sessions table")

            # Migration: Add agent_id column to entries if not exists
            cursor = await db.execute("PRAGMA table_info(entries)")
            entry_columns = {row[1] for row in await cursor.fetchall()}
            if "agent_id" not in entry_columns:
                await db.execute(
                    "ALTER TABLE entries ADD COLUMN agent_id TEXT"
                )
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_entries_agent
                    ON entries(session_id, agent_id)
                """)
                logger.info("Added 'agent_id' column to entries table")

            await db.commit()
            self._initialized = True

    # --- Session Management ---

    async def create_session(self, session: TranscriptSession) -> bool:
        """Create a new transcript session."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
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
            except aiosqlite.OperationalError as e:
                logger.error(f"Database operational error creating session {session.session_id}: {e}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error creating session {session.session_id}: {e}")
                return False

    async def end_session(self, session_id: str) -> bool:
        """Mark a session as ended."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            cursor = await db.execute(
                """
                UPDATE sessions SET ended_at = ?
                WHERE session_id = ? AND ended_at IS NULL
                """,
                (datetime.now().isoformat(), session_id),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def archive_session(self, session_id: str) -> bool:
        """
        Archive a session (soft delete).

        Archived sessions are preserved but excluded from normal queries.
        Data remains in the database for historical reference.

        Args:
            session_id: Session to archive

        Returns:
            True if archived successfully, False if session not found
        """
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            cursor = await db.execute(
                "UPDATE sessions SET archived = 1 WHERE session_id = ?",
                (session_id,),
            )
            await db.commit()
            if cursor.rowcount > 0:
                logger.info(f"Archived session: {session_id}")
                return True
            return False

    async def archive_all_sessions(self) -> int:
        """
        Archive all non-archived sessions.

        Used for clean slate resets where all prior session history
        should be excluded from future context assembly.

        Returns:
            Number of sessions archived
        """
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            cursor = await db.execute(
                "UPDATE sessions SET archived = 1 WHERE archived = 0 OR archived IS NULL"
            )
            await db.commit()
            count = cursor.rowcount
            if count > 0:
                logger.info(f"Archived {count} sessions (clean slate)")
            return count

    async def get_session(self, session_id: str) -> TranscriptSession | None:
        """Retrieve session metadata."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
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
        include_archived: bool = False,
    ) -> list[TranscriptSession]:
        """
        List transcript sessions.

        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            user_id: Filter by user ID
            active_only: Only return sessions without ended_at
            include_archived: If False (default), exclude archived sessions

        Returns:
            List of TranscriptSession objects
        """
        await self._ensure_initialized()

        query = "SELECT * FROM sessions WHERE 1=1"
        params: list[Any] = []

        # Filter out archived sessions by default
        if not include_archived:
            query += " AND (archived = 0 OR archived IS NULL)"

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)

        if active_only:
            query += " AND ended_at IS NULL"

        query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [self._row_to_session(row) for row in rows]

    def _row_to_session(self, row: aiosqlite.Row) -> TranscriptSession:
        """Convert database row to TranscriptSession."""
        # Handle archived column (may not exist in older databases before migration runs)
        archived = False
        if "archived" in row.keys():
            archived = bool(row["archived"])

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
            archived=archived,
        )

    # --- Entry Management ---

    async def append_entry(self, entry: TranscriptEntry) -> bool:
        """Append a transcript entry."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            try:
                # Insert entry
                await db.execute(
                    """
                    INSERT INTO entries (
                        id, session_id, turn_number, user_message, assistant_message,
                        agent_id, tool_calls, tool_results, timestamp, response_started_at,
                        response_completed_at, prompt_tokens, completion_tokens,
                        total_tokens, latency_ms, model_name, temperature,
                        context_tokens_used, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.id,
                        entry.session_id,
                        entry.turn_number,
                        entry.user_message,
                        entry.assistant_message,
                        entry.agent_id,
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
                logger.warning(f"Integrity error on entry {entry.id}: {e}")
                return False
            except aiosqlite.OperationalError as e:
                logger.error(f"Database operational error on entry {entry.id}: {e}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error saving entry {entry.id}: {e}")
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
            await db.execute("PRAGMA foreign_keys = ON")
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [self._row_to_entry(row) for row in rows]

    async def get_entry(self, entry_id: str) -> TranscriptEntry | None:
        """Retrieve a single entry by ID."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
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
            await db.execute("PRAGMA foreign_keys = ON")
            cursor = await db.execute(
                "SELECT COUNT(*) FROM entries WHERE session_id = ?",
                (session_id,),
            )
            row = await cursor.fetchone()
            return row[0] if row else 0

    # --- Consolidation Management ---

    async def mark_entries_consolidated(self, entry_ids: list[str]) -> int:
        """Mark entries as consolidated (extracted to long-term memory).

        Args:
            entry_ids: List of entry IDs to mark as consolidated

        Returns:
            Number of entries updated
        """
        await self._ensure_initialized()

        if not entry_ids:
            return 0

        placeholders = ",".join("?" * len(entry_ids))
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            try:
                cursor = await db.execute(
                    f"UPDATE entries SET consolidated = 1 WHERE id IN ({placeholders})",
                    entry_ids,
                )
                await db.commit()
                logger.debug(f"Marked {cursor.rowcount} entries as consolidated")
                return cursor.rowcount
            except Exception as e:
                logger.error(f"Failed to mark entries consolidated: {e}")
                return 0

    async def get_unconsolidated_entries(
        self,
        session_id: str,
        limit: int = 100,
    ) -> list[TranscriptEntry]:
        """Get entries not yet consolidated (extracted to long-term memory).

        Args:
            session_id: Session ID to query
            limit: Maximum number of entries to return

        Returns:
            List of unconsolidated entries, ordered by turn number
        """
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT * FROM entries
                WHERE session_id = ? AND (consolidated = 0 OR consolidated IS NULL)
                ORDER BY turn_number ASC
                LIMIT ?
                """,
                (session_id, limit),
            )
            rows = await cursor.fetchall()
            return [self._row_to_entry(row) for row in rows]

    def _row_to_entry(self, row: aiosqlite.Row) -> TranscriptEntry:
        """Convert database row to TranscriptEntry."""
        tool_calls_data = json.loads(row["tool_calls"] or "[]")
        tool_results_data = json.loads(row["tool_results"] or "[]")

        # Handle agent_id column (may not exist in older databases before migration)
        agent_id = None
        if "agent_id" in row.keys():
            agent_id = row["agent_id"]

        return TranscriptEntry(
            id=row["id"],
            session_id=row["session_id"],
            turn_number=row["turn_number"],
            user_message=row["user_message"],
            assistant_message=row["assistant_message"],
            agent_id=agent_id,
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
            consolidated=bool(row["consolidated"]) if "consolidated" in row.keys() else False,
        )

    async def get_entries_by_agent(
        self,
        session_id: str,
        agent_id: str,
        limit: int = 100,
    ) -> list[TranscriptEntry]:
        """
        Get entries from a specific agent.

        Args:
            session_id: Session ID to query
            agent_id: Agent ID to filter by
            limit: Maximum number of entries to return

        Returns:
            List of entries from the specified agent, ordered by turn number
        """
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT * FROM entries
                WHERE session_id = ? AND agent_id = ?
                ORDER BY turn_number ASC
                LIMIT ?
                """,
                (session_id, agent_id, limit),
            )
            rows = await cursor.fetchall()
            return [self._row_to_entry(row) for row in rows]

    # --- Analytics ---

    async def get_token_stats(self, session_id: str) -> dict[str, Any]:
        """Get token usage statistics for a session."""
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
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
            await db.execute("PRAGMA foreign_keys = ON")
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
