# mypy: ignore-errors
"""
SQLite-based transcript store.

Primary backend for persistent transcript storage.
Uses aiosqlite for async operations.
"""

import asyncio
import hashlib
import json
import logging
import os
import shutil
import sqlite3
import stat
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from uuid import uuid4

import aiosqlite
from pydantic import ValidationError

from friday_transcript.models.snapshot import (
    TranscriptIntegrityResult,
    TranscriptRecoveryErrorCode,
    TranscriptRecoveryErrorDetail,
    TranscriptRestoreQuiescenceToken,
    TranscriptSnapshotManifest,
    TranscriptSnapshotResult,
    TranscriptSnapshotStatus,
)
from friday_transcript.models.transcript import (
    ContextLogEntry,
    ToolCall,
    ToolResult,
    TranscriptEntry,
    TranscriptSession,
)

logger = logging.getLogger(__name__)


class TranscriptRecoveryError(RuntimeError):
    """Base exception for transcript recovery invariant failures."""


class TranscriptPathError(TranscriptRecoveryError):
    """Raised when recovery paths alias or overlap live transcript state."""


class TranscriptQuiescenceError(TranscriptRecoveryError):
    """Raised when restore lacks the store-owned writer-gate token."""


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
        self._initialize_lock = asyncio.Lock()
        self._write_gate = asyncio.Lock()
        self._recovery_issuer_id = uuid4().hex
        self._active_restore_token: TranscriptRestoreQuiescenceToken | None = None

    @property
    def database_path(self) -> Path:
        """Return the configured SQLite database path."""
        return self._db_path

    @asynccontextmanager
    async def _writer_connection(self) -> AsyncIterator[aiosqlite.Connection]:
        """Open a writer connection while holding the store-owned write gate."""
        async with self._write_gate, aiosqlite.connect(self._db_path) as db:
            yield db

    async def _ensure_initialized(self) -> None:
        """Create tables if they don't exist."""
        if self._initialized:
            return

        async with self._initialize_lock:
            if self._initialized:
                return
            await self._initialize_database()

    async def _initialize_database(self) -> None:
        """Initialize schema while holding the same gate as ordinary writes."""
        async with self._writer_connection() as db:
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

            # Migration: Add compacted column if not exists
            if "compacted" not in columns:
                await db.execute(
                    "ALTER TABLE entries ADD COLUMN compacted INTEGER DEFAULT 0"
                )
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_entries_compacted
                    ON entries(session_id, compacted)
                """)
                logger.info("Added 'compacted' column to entries table")

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
                await db.execute("ALTER TABLE entries ADD COLUMN agent_id TEXT")
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_entries_agent
                    ON entries(session_id, agent_id)
                """)
                logger.info("Added 'agent_id' column to entries table")

            # context_log table for raw prompt/response storage
            # Primary relationship: sessions -> context_log (one-to-many)
            # Enables deep analysis of context engineering while keeping entries table clean  # noqa: E501
            await db.execute("""
                CREATE TABLE IF NOT EXISTS context_log (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    turn_number INTEGER NOT NULL,
                    entry_id TEXT,
                    raw_prompt TEXT NOT NULL,
                    raw_response TEXT,
                    captured_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
                    FOREIGN KEY (entry_id) REFERENCES entries(id)
                )
            """)

            # Primary index: session_id + turn_number for ordered session queries
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_log_session
                ON context_log(session_id, turn_number)
            """)

            # Secondary index: entry_id for optional entry joins
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_log_entry
                ON context_log(entry_id)
            """)

            await db.commit()
            self._initialized = True

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _path_contains(parent: Path, child: Path) -> bool:
        return parent == child or parent in child.parents

    def _validate_snapshot_destination(self, destination_directory: Path) -> Path:
        source = self._db_path.resolve(strict=False)
        destination = destination_directory.resolve(strict=False)
        if self._path_contains(destination, source) or self._path_contains(
            source, destination
        ):
            raise TranscriptPathError(
                "Transcript recovery destination overlaps the live database path"
            )
        if destination.exists():
            raise TranscriptPathError(
                "Transcript recovery destination must not already exist"
            )
        return destination

    @staticmethod
    def _set_directory_permissions(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=False, mode=0o700)
        if os.name == "posix":
            path.chmod(0o700)
            SQLiteTranscriptStore._fsync_directory(path.parent)

    @staticmethod
    def _set_file_permissions(path: Path) -> None:
        if os.name == "posix":
            path.chmod(0o600)

    @staticmethod
    def _write_manifest(path: Path, manifest: TranscriptSnapshotManifest) -> None:
        payload = manifest.model_dump_json(indent=2).encode("utf-8")
        temp_path = path.with_name(f".{path.name}.tmp")
        descriptor = os.open(temp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, path)
            SQLiteTranscriptStore._set_file_permissions(path)
            SQLiteTranscriptStore._fsync_directory(path.parent)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    @staticmethod
    def _online_backup(source: Path, destination: Path) -> None:
        source_uri = f"file:{source.resolve(strict=True)}?mode=ro"
        with (
            sqlite3.connect(source_uri, uri=True) as source_db,
            sqlite3.connect(destination) as destination_db,
        ):
            source_db.backup(destination_db)
            destination_db.commit()
        SQLiteTranscriptStore._set_file_permissions(destination)
        with destination.open("rb") as stream:
            os.fsync(stream.fileno())
        SQLiteTranscriptStore._fsync_directory(destination.parent)

    @staticmethod
    def _schema_fingerprint(connection: sqlite3.Connection) -> str:
        rows = connection.execute(
            """
            SELECT type, name, tbl_name, COALESCE(sql, '')
            FROM sqlite_schema
            WHERE name NOT LIKE 'sqlite_%'
            ORDER BY type, name, tbl_name, sql
            """
        ).fetchall()
        encoded = json.dumps(rows, separators=(",", ":"), ensure_ascii=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    @classmethod
    def _inspect_database(cls, database_path: Path) -> TranscriptIntegrityResult:
        database_uri = f"file:{database_path.resolve(strict=True)}?mode=ro"
        with sqlite3.connect(database_uri, uri=True) as connection:
            integrity_rows = connection.execute("PRAGMA integrity_check").fetchall()
            foreign_key_rows = connection.execute("PRAGMA foreign_key_check").fetchall()
            page_count_row = connection.execute("PRAGMA page_count").fetchone()
            page_count = int(page_count_row[0]) if page_count_row else 0
            return TranscriptIntegrityResult(
                integrity_ok=integrity_rows == [("ok",)],
                foreign_keys_ok=not foreign_key_rows,
                schema_fingerprint=cls._schema_fingerprint(connection),
                page_count=page_count,
            )

    @staticmethod
    def _failed_result(
        code: TranscriptRecoveryErrorCode,
        message: str,
        *,
        manifest_path: Path | None = None,
        integrity: TranscriptIntegrityResult | None = None,
    ) -> TranscriptSnapshotResult:
        return TranscriptSnapshotResult(
            status=TranscriptSnapshotStatus.FAILED,
            manifest_path=manifest_path,
            integrity=integrity,
            verified=False,
            errors=[TranscriptRecoveryErrorDetail(code=code, message=message)],
        )

    async def inspect_live(self) -> TranscriptSnapshotResult:
        """Inspect live SQLite integrity without initializing or writing state."""
        try:
            database_path = self._db_path.resolve(strict=True)
            if not database_path.is_file():
                raise FileNotFoundError
            integrity = await asyncio.to_thread(
                self._inspect_database,
                database_path,
            )
        except FileNotFoundError:
            return self._failed_result(
                TranscriptRecoveryErrorCode.SOURCE_ABSENT,
                "Live transcript database is absent",
            )
        except (OSError, sqlite3.Error):
            return self._failed_result(
                TranscriptRecoveryErrorCode.INTEGRITY_FAILED,
                "Live transcript is not a readable SQLite database",
            )
        if not integrity.verified:
            return self._failed_result(
                TranscriptRecoveryErrorCode.INTEGRITY_FAILED,
                "Live transcript integrity verification failed",
                integrity=integrity,
            )
        return TranscriptSnapshotResult(
            status=TranscriptSnapshotStatus.COMPLETED,
            integrity=integrity,
            verified=True,
        )

    async def create_snapshot(
        self, destination_directory: str | Path
    ) -> TranscriptSnapshotResult:
        """Create and verify a WAL-safe SQLite online backup."""
        try:
            await self._ensure_initialized()
        except (OSError, sqlite3.Error) as exc:
            return self._failed_result(
                TranscriptRecoveryErrorCode.SOURCE_ABSENT,
                f"Live transcript initialization failed: {type(exc).__name__}",
            )
        destination = self._validate_snapshot_destination(Path(destination_directory))
        artifact_path = destination / "transcript.sqlite3"
        manifest_path = destination / "manifest.json"

        try:
            self._set_directory_permissions(destination)
            await asyncio.to_thread(
                self._online_backup,
                self._db_path.resolve(strict=True),
                artifact_path,
            )
            integrity = await asyncio.to_thread(self._inspect_database, artifact_path)
            if not integrity.verified:
                return self._failed_result(
                    TranscriptRecoveryErrorCode.INTEGRITY_FAILED,
                    "SQLite snapshot integrity verification failed",
                    manifest_path=manifest_path,
                    integrity=integrity,
                )
            manifest = TranscriptSnapshotManifest(
                created_at=datetime.now(),
                source_path=str(self._db_path.resolve(strict=True)),
                artifact_filename=artifact_path.name,
                artifact_sha256=await asyncio.to_thread(self._sha256, artifact_path),
                artifact_size_bytes=artifact_path.stat().st_size,
                schema_fingerprint=integrity.schema_fingerprint,
                page_count=integrity.page_count,
                verified=True,
            )
            await asyncio.to_thread(self._write_manifest, manifest_path, manifest)
        except (OSError, sqlite3.Error) as exc:
            return self._failed_result(
                TranscriptRecoveryErrorCode.INTEGRITY_FAILED,
                f"SQLite online snapshot failed: {type(exc).__name__}",
                manifest_path=manifest_path,
            )

        return await self.verify_snapshot(manifest_path)

    async def verify_snapshot(
        self, manifest_path: str | Path
    ) -> TranscriptSnapshotResult:
        """Verify checksum, schema, and SQLite integrity for a snapshot."""
        normalized_manifest = Path(manifest_path).resolve(strict=False)
        try:
            manifest = TranscriptSnapshotManifest.model_validate_json(
                normalized_manifest.read_text()
            )
        except FileNotFoundError:
            return self._failed_result(
                TranscriptRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                "Transcript snapshot manifest is absent",
                manifest_path=normalized_manifest,
            )
        except (OSError, ValidationError, ValueError):
            return self._failed_result(
                TranscriptRecoveryErrorCode.SCHEMA_MISMATCH,
                "Transcript snapshot manifest is invalid",
                manifest_path=normalized_manifest,
            )

        if Path(manifest.artifact_filename).name != manifest.artifact_filename:
            return self._failed_result(
                TranscriptRecoveryErrorCode.INVALID_PATH,
                "Transcript artifact filename is not a local bundle filename",
                manifest_path=normalized_manifest,
            )
        if not manifest.verified:
            return self._failed_result(
                TranscriptRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                "Transcript snapshot manifest is not marked verified",
                manifest_path=normalized_manifest,
            )
        artifact_path = normalized_manifest.parent / manifest.artifact_filename
        if not artifact_path.is_file():
            return self._failed_result(
                TranscriptRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                "Transcript snapshot artifact is absent",
                manifest_path=normalized_manifest,
            )
        try:
            with TemporaryDirectory(
                prefix="friday-transcript-verify-"
            ) as temporary_directory:
                verification_directory = Path(temporary_directory)
                if os.name == "posix":
                    verification_directory.chmod(0o700)
                staged_artifact = verification_directory / "transcript.sqlite3"
                await asyncio.to_thread(
                    self._copy_owner_only, artifact_path, staged_artifact
                )
                artifact_checksum = await asyncio.to_thread(
                    self._sha256, staged_artifact
                )
                if artifact_checksum != manifest.artifact_sha256:
                    return self._failed_result(
                        TranscriptRecoveryErrorCode.CHECKSUM_MISMATCH,
                        "Transcript snapshot checksum does not match its manifest",
                        manifest_path=normalized_manifest,
                    )
                integrity = await asyncio.to_thread(
                    self._inspect_database, staged_artifact
                )
                artifact_size = staged_artifact.stat().st_size
        except OSError:
            return self._failed_result(
                TranscriptRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                "Transcript snapshot artifact became unavailable",
                manifest_path=normalized_manifest,
            )
        except sqlite3.Error:
            return self._failed_result(
                TranscriptRecoveryErrorCode.INTEGRITY_FAILED,
                "Transcript snapshot is not a readable SQLite database",
                manifest_path=normalized_manifest,
            )
        if not integrity.verified:
            return self._failed_result(
                TranscriptRecoveryErrorCode.INTEGRITY_FAILED,
                "Transcript snapshot integrity verification failed",
                manifest_path=normalized_manifest,
                integrity=integrity,
            )
        if (
            integrity.schema_fingerprint != manifest.schema_fingerprint
            or integrity.page_count != manifest.page_count
            or artifact_size != manifest.artifact_size_bytes
        ):
            return self._failed_result(
                TranscriptRecoveryErrorCode.SCHEMA_MISMATCH,
                "Transcript snapshot metadata does not match its manifest",
                manifest_path=normalized_manifest,
                integrity=integrity,
            )
        return TranscriptSnapshotResult(
            status=TranscriptSnapshotStatus.COMPLETED,
            manifest_path=normalized_manifest,
            integrity=integrity,
            verified=True,
        )

    @asynccontextmanager
    async def restore_quiescence(
        self,
    ) -> AsyncIterator[TranscriptRestoreQuiescenceToken]:
        """Hold the store writer gate and issue an identity-bound restore token."""
        await self._ensure_initialized()
        if self._active_restore_token is not None:
            raise TranscriptQuiescenceError("Transcript restore quiescence is active")
        await self._write_gate.acquire()
        token = TranscriptRestoreQuiescenceToken(
            self._recovery_issuer_id,
            hashlib.sha256(
                str(self._db_path.resolve(strict=False)).encode("utf-8")
            ).hexdigest(),
            uuid4().hex,
        )
        self._active_restore_token = token
        try:
            yield token
        finally:
            self._active_restore_token = None
            self._write_gate.release()

    def _validate_restore_token(
        self, token: TranscriptRestoreQuiescenceToken
    ) -> None:
        if token is not self._active_restore_token or not self._write_gate.locked():
            raise TranscriptQuiescenceError(
                "Restore requires the active store-issued quiescence token"
            )

    def _load_manifest_for_apply(
        self, manifest_path: Path
    ) -> TranscriptSnapshotManifest:
        """Revalidate the exact manifest instance selecting the restored artifact."""
        try:
            manifest = TranscriptSnapshotManifest.model_validate_json(
                manifest_path.read_bytes()
            )
        except (OSError, ValidationError, ValueError) as exc:
            raise TranscriptRecoveryError(
                "Transcript snapshot manifest became unavailable or invalid"
            ) from exc
        if not manifest.verified:
            raise TranscriptRecoveryError(
                "Transcript snapshot manifest is not verified"
            )
        if (
            Path(manifest.artifact_filename).name != manifest.artifact_filename
            or Path(manifest.source_path).resolve(strict=False)
            != self._db_path.resolve(strict=False)
        ):
            raise TranscriptPathError(
                "Transcript snapshot manifest is not valid for this database path"
            )
        return manifest

    @staticmethod
    def _checkpoint_database(database_path: Path) -> None:
        with sqlite3.connect(database_path) as connection:
            checkpoint = connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
            if checkpoint is None or int(checkpoint[0]) != 0:
                raise sqlite3.OperationalError("WAL checkpoint did not complete")

    @staticmethod
    def _copy_owner_only(source: Path, destination: Path) -> None:
        shutil.copyfile(source, destination)
        SQLiteTranscriptStore._set_file_permissions(destination)
        with destination.open("rb") as stream:
            os.fsync(stream.fileno())

    @staticmethod
    def _fsync_directory(directory: Path) -> None:
        if os.name != "posix":
            return
        descriptor = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    async def restore_snapshot(
        self,
        manifest_path: str | Path,
        token: TranscriptRestoreQuiescenceToken,
    ) -> TranscriptSnapshotResult:
        """Restore a verified snapshot only under store-owned quiescence."""
        self._validate_restore_token(token)
        verification = await self.verify_snapshot(manifest_path)
        if not verification.verified or verification.manifest_path is None:
            raise TranscriptRecoveryError("Transcript snapshot verification failed")

        manifest = self._load_manifest_for_apply(verification.manifest_path)

        artifact_path = verification.manifest_path.parent / manifest.artifact_filename
        staging_path = self._db_path.with_name(f".{self._db_path.name}.{uuid4().hex}.restore")
        try:
            live_mode = (
                stat.S_IMODE(self._db_path.stat().st_mode)
                if self._db_path.exists()
                else 0o600
            )
            await asyncio.to_thread(self._copy_owner_only, artifact_path, staging_path)
            staging_checksum = await asyncio.to_thread(self._sha256, staging_path)
            if (
                staging_checksum != manifest.artifact_sha256
                or staging_path.stat().st_size != manifest.artifact_size_bytes
            ):
                raise TranscriptRecoveryError(
                    "Staged transcript recovery artifact checksum mismatch"
                )
            staging_integrity = await asyncio.to_thread(
                self._inspect_database, staging_path
            )
            if (
                not staging_integrity.verified
                or staging_integrity.schema_fingerprint != manifest.schema_fingerprint
            ):
                raise TranscriptRecoveryError(
                    "Staged transcript recovery artifact failed integrity verification"
                )
            await asyncio.to_thread(self._checkpoint_database, self._db_path)
            self._db_path.with_name(f"{self._db_path.name}-wal").unlink(missing_ok=True)
            self._db_path.with_name(f"{self._db_path.name}-shm").unlink(missing_ok=True)
            os.replace(staging_path, self._db_path)
            if os.name == "posix":
                self._db_path.chmod(live_mode)
            await asyncio.to_thread(self._fsync_directory, self._db_path.parent)
        except TranscriptRecoveryError:
            staging_path.unlink(missing_ok=True)
            raise
        except (OSError, sqlite3.Error) as exc:
            staging_path.unlink(missing_ok=True)
            raise TranscriptRecoveryError(
                f"Transcript restore failed: {type(exc).__name__}"
            ) from exc

        live_result = await self.verify_live(verification.manifest_path)
        if not live_result.verified:
            raise TranscriptRecoveryError(
                "Restored transcript failed live integrity verification"
            )
        try:
            live_checksum = await asyncio.to_thread(self._sha256, self._db_path)
        except OSError as exc:
            raise TranscriptRecoveryError(
                "Restored transcript cannot be checksummed"
            ) from exc
        if live_checksum != manifest.artifact_sha256:
            raise TranscriptRecoveryError(
                "Restored transcript does not match the verified snapshot"
            )
        self._initialized = True
        return live_result

    async def verify_live(
        self, manifest_path: str | Path
    ) -> TranscriptSnapshotResult:
        """Verify live SQLite integrity and snapshot schema compatibility."""
        snapshot_result = await self.verify_snapshot(manifest_path)
        if not snapshot_result.verified or snapshot_result.manifest_path is None:
            return snapshot_result
        try:
            manifest = self._load_manifest_for_apply(
                snapshot_result.manifest_path
            )
        except TranscriptPathError:
            return self._failed_result(
                TranscriptRecoveryErrorCode.INVALID_PATH,
                "Transcript snapshot manifest is not valid for the live database",
                manifest_path=snapshot_result.manifest_path,
            )
        except TranscriptRecoveryError:
            return self._failed_result(
                TranscriptRecoveryErrorCode.SCHEMA_MISMATCH,
                "Transcript snapshot manifest became unavailable",
                manifest_path=snapshot_result.manifest_path,
            )
        try:
            integrity = await asyncio.to_thread(
                self._inspect_database, self._db_path.resolve(strict=True)
            )
        except (OSError, sqlite3.Error):
            return self._failed_result(
                TranscriptRecoveryErrorCode.INTEGRITY_FAILED,
                "Live transcript is not a readable SQLite database",
                manifest_path=snapshot_result.manifest_path,
            )
        if not integrity.verified:
            return self._failed_result(
                TranscriptRecoveryErrorCode.INTEGRITY_FAILED,
                "Live transcript integrity verification failed",
                manifest_path=snapshot_result.manifest_path,
                integrity=integrity,
            )
        if integrity.schema_fingerprint != manifest.schema_fingerprint:
            return self._failed_result(
                TranscriptRecoveryErrorCode.SCHEMA_MISMATCH,
                "Live transcript schema is incompatible with the snapshot",
                manifest_path=snapshot_result.manifest_path,
                integrity=integrity,
            )
        return TranscriptSnapshotResult(
            status=TranscriptSnapshotStatus.COMPLETED,
            manifest_path=snapshot_result.manifest_path,
            integrity=integrity,
            verified=True,
        )

    # --- Session Management ---

    async def create_session(self, session: TranscriptSession) -> bool:
        """Create a new transcript session."""
        await self._ensure_initialized()

        async with self._writer_connection() as db:
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
                logger.error(
                    f"Database operational error creating session {session.session_id}: {e}"  # noqa: E501
                )
                return False
            except Exception as e:
                logger.error(
                    f"Unexpected error creating session {session.session_id}: {e}"
                )
                return False

    async def end_session(self, session_id: str) -> bool:
        """Mark a session as ended."""
        await self._ensure_initialized()

        async with self._writer_connection() as db:
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

        async with self._writer_connection() as db:
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

        async with self._writer_connection() as db:
            await db.execute("PRAGMA foreign_keys = ON")
            cursor = await db.execute(
                "UPDATE sessions SET archived = 1 WHERE archived = 0 OR archived IS NULL"  # noqa: E501
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
        # Handle archived column (may not exist in older databases before migration runs)  # noqa: E501
        archived = False
        if "archived" in row:
            archived = bool(row["archived"])

        return TranscriptSession(
            session_id=row["session_id"],
            user_id=row["user_id"],
            started_at=datetime.fromisoformat(row["started_at"]),
            ended_at=datetime.fromisoformat(row["ended_at"])
            if row["ended_at"]
            else None,
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

        async with self._writer_connection() as db:
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
                    """,  # noqa: E501
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
                        entry.response_started_at.isoformat()
                        if entry.response_started_at
                        else None,
                        entry.response_completed_at.isoformat()
                        if entry.response_completed_at
                        else None,
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
        async with self._writer_connection() as db:
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

    async def mark_entries_compacted(self, entry_ids: list[str]) -> int:
        """Mark entries as compacted (summarized by InSessionCompactor).

        Compacted entries are excluded from raw history retrieval but
        remain in the transcript for audit purposes.

        Args:
            entry_ids: List of entry IDs to mark as compacted

        Returns:
            Number of entries updated
        """
        await self._ensure_initialized()

        if not entry_ids:
            return 0

        placeholders = ",".join("?" * len(entry_ids))
        async with self._writer_connection() as db:
            await db.execute("PRAGMA foreign_keys = ON")
            try:
                cursor = await db.execute(
                    f"UPDATE entries SET compacted = 1 WHERE id IN ({placeholders})",
                    entry_ids,
                )
                await db.commit()
                logger.debug(f"Marked {cursor.rowcount} entries as compacted")
                return cursor.rowcount
            except Exception as e:
                logger.error(f"Failed to mark entries compacted: {e}")
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
        if "agent_id" in row:
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
            consolidated=bool(row["consolidated"])
            if "consolidated" in row
            else False,
            compacted=bool(row["compacted"]) if "compacted" in row else False,
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

    # --- Context Log Management ---

    async def store_context_log(self, context_entry: ContextLogEntry) -> bool:
        """
        Store raw prompt/response for a turn.

        Args:
            context_entry: ContextLogEntry with raw prompt and response data

        Returns:
            True if stored successfully, False otherwise
        """
        await self._ensure_initialized()

        async with self._writer_connection() as db:
            await db.execute("PRAGMA foreign_keys = ON")
            try:
                await db.execute(
                    """
                    INSERT INTO context_log (
                        id, session_id, turn_number, entry_id,
                        raw_prompt, raw_response, captured_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        context_entry.id,
                        context_entry.session_id,
                        context_entry.turn_number,
                        context_entry.entry_id,
                        context_entry.raw_prompt,
                        context_entry.raw_response,
                        context_entry.captured_at.isoformat(),
                    ),
                )
                await db.commit()
                logger.debug(
                    f"Stored context log: {context_entry.id} "
                    f"(session={context_entry.session_id}, turn={context_entry.turn_number})"  # noqa: E501
                )
                return True
            except aiosqlite.IntegrityError as e:
                logger.warning(f"Context log already exists or FK violation: {e}")
                return False
            except Exception as e:
                logger.error(f"Failed to store context log {context_entry.id}: {e}")
                return False

    async def get_context_log_for_session(
        self, session_id: str, limit: int = 100
    ) -> list[ContextLogEntry]:
        """
        Get all context log entries for a session (primary query).

        Args:
            session_id: The session ID to query
            limit: Maximum number of entries to return (default 100)

        Returns:
            List of ContextLogEntry objects ordered by turn_number
        """
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT * FROM context_log
                WHERE session_id = ?
                ORDER BY turn_number ASC
                LIMIT ?
                """,
                (session_id, limit),
            )
            rows = await cursor.fetchall()
            return [self._row_to_context_log(row) for row in rows]

    async def get_context_log_by_entry(self, entry_id: str) -> ContextLogEntry | None:
        """
        Get context log data by entry ID (optional join).

        Args:
            entry_id: The transcript entry ID to look up

        Returns:
            ContextLogEntry if found, None otherwise
        """
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM context_log WHERE entry_id = ?",
                (entry_id,),
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_context_log(row)

    async def get_context_log_by_turn(
        self, session_id: str, turn_number: int
    ) -> ContextLogEntry | None:
        """
        Get context log for a specific turn in a session.

        Args:
            session_id: The session ID
            turn_number: The turn number to look up

        Returns:
            ContextLogEntry if found, None otherwise
        """
        await self._ensure_initialized()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT * FROM context_log
                WHERE session_id = ? AND turn_number = ?
                """,
                (session_id, turn_number),
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_context_log(row)

    async def export_context_log(
        self, session_id: str, format: str = "json"
    ) -> dict[str, Any]:
        """
        Export context log data for analysis.

        Args:
            session_id: The session ID to export
            format: Export format ("json" supported, extensible for "csv")

        Returns:
            Dictionary containing export data with session info and turns
        """
        await self._ensure_initialized()

        entries = await self.get_context_log_for_session(session_id)

        # Parse JSON fields for clean export
        turns = []
        for entry in entries:
            turn_data = {
                "turn_number": entry.turn_number,
                "entry_id": entry.entry_id,
                "captured_at": entry.captured_at.isoformat(),
                "raw_prompt": json.loads(entry.raw_prompt)
                if entry.raw_prompt
                else None,
                "raw_response": (
                    json.loads(entry.raw_response) if entry.raw_response else None
                ),
            }
            turns.append(turn_data)

        return {
            "session_id": session_id,
            "exported_at": datetime.now().isoformat(),
            "turn_count": len(turns),
            "turns": turns,
        }

    def _row_to_context_log(self, row: aiosqlite.Row) -> ContextLogEntry:
        """Convert database row to ContextLogEntry."""
        return ContextLogEntry(
            id=row["id"],
            session_id=row["session_id"],
            turn_number=row["turn_number"],
            entry_id=row["entry_id"],
            raw_prompt=row["raw_prompt"],
            raw_response=row["raw_response"],
            captured_at=datetime.fromisoformat(row["captured_at"]),
        )
