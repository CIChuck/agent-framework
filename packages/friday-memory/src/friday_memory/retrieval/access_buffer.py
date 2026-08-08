# mypy: ignore-errors
"""
Access Buffer for Lazy Access Tracking.

Buffers memory access events in-memory for batch processing during reorganization.
Eliminates synchronous DB writes during retrieval for better latency.

Ref: docs/archive/build-plans/completed/friday-core-legacy/memory-lifecycle-staging-decay.md - Optimization B
"""

import asyncio
import logging
import math
import os
import stat
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal, Protocol
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

logger = logging.getLogger(__name__)

# Reserved metadata written only by AccessBuffer maintenance. The versioned,
# package-namespaced key makes retry identity explicit without colliding with
# caller-owned lifecycle metadata.
_ACCESS_DRAIN_MARKER = "friday_memory_maintenance_access_drain_id_v1"


@dataclass
class AccessBufferConfig:
    """Configuration for AccessBuffer."""

    max_buffer_size: int = 1000
    """Maximum entries per buffer before auto-flush."""

    max_buffer_age_seconds: int = 300
    """Maximum age in seconds before time-based flush (5 minutes default)."""

    wal_path: Path | None = None
    """Optional write-ahead log path for crash recovery."""

    decay_score_boost: float = 0.1
    """How much to boost decay_score per access (short-term memories)."""


@dataclass
class FlushResult:
    """Result from flushing access buffers."""

    short_term_flushed: int = 0
    long_term_flushed: int = 0
    short_term_remaining: int = 0
    long_term_remaining: int = 0
    wal_verified: bool = True
    errors: list[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def summary(self) -> str:
        parts = []
        if self.short_term_flushed > 0:
            parts.append(f"short_term={self.short_term_flushed}")
        if self.long_term_flushed > 0:
            parts.append(f"long_term={self.long_term_flushed}")
        if not parts:
            return "No accesses flushed"
        return f"Flushed: {', '.join(parts)}"

    @property
    def verified_drained(self) -> bool:
        """Return whether every buffered effect was durably drained."""
        return (
            not self.errors
            and self.short_term_remaining == 0
            and self.long_term_remaining == 0
            and self.wal_verified
        )


class AccessBufferQuiescenceError(RuntimeError):
    """Raised when maintenance drain admission invariants are violated."""


class AccessBufferQuiescenceToken:
    """Opaque proof that this AccessBuffer has closed recorder admission."""

    __slots__ = ("_issuer_id", "_nonce")

    def __init__(self, issuer_id: str, nonce: str) -> None:
        self._issuer_id = issuer_id
        self._nonce = nonce


class AccessBufferWalError(RuntimeError):
    """Raised when the configured access WAL is unavailable or invalid."""


class AccessBufferWalCommitError(AccessBufferWalError):
    """Report whether the requested WAL state became logically visible."""

    def __init__(self, message: str, *, logically_committed: bool) -> None:
        super().__init__(message)
        self.logically_committed = logically_committed


class AccessCollectionType(str, Enum):
    """Closed collection kinds accepted by the access buffer."""

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


class AccessMetadataCollection(Protocol):
    """Collection operations required by an idempotent access drain."""

    async def get_by_id(self, memory_id: str) -> dict[str, object] | None:
        """Return a memory document and its metadata when present."""
        ...

    async def update_metadata(
        self,
        memory_id: str,
        metadata: dict[str, object],
    ) -> bool:
        """Return whether the identified memory was updated."""
        ...


class AccessWalRecord(BaseModel):
    """Strict persisted access event or in-progress idempotent drain batch."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: Literal[1, 2]
    memory_id: str = Field(min_length=1)
    collection_type: AccessCollectionType
    count: int = Field(gt=0)
    timestamp: float | None = None
    drain_id: str | None = Field(
        default=None,
        min_length=32,
        max_length=32,
        pattern=r"^[0-9a-f]{32}$",
    )

    @model_validator(mode="after")
    def validate_version_shape(self) -> "AccessWalRecord":
        """Keep event and pending-drain records unambiguous."""
        if self.schema_version == 1:
            if (
                self.count != 1
                or self.timestamp is None
                or not math.isfinite(self.timestamp)
                or self.drain_id is not None
            ):
                raise ValueError("invalid access WAL event record")
        elif self.timestamp is not None or not self.drain_id:
            raise ValueError("invalid access WAL pending-drain record")
        _validate_memory_id(self.memory_id)
        return self


def _validate_memory_id(memory_id: str) -> None:
    if (
        not isinstance(memory_id, str)
        or not memory_id
        or "," in memory_id
        or "\n" in memory_id
        or "\r" in memory_id
        or "\x00" in memory_id
    ):
        raise ValueError("memory_id is not safely representable in the access WAL")
    try:
        memory_id.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise ValueError(
            "memory_id is not safely representable in the access WAL"
        ) from exc


class AccessBuffer:
    """
    Buffer access events for batch processing.

    Eliminates synchronous DB writes during retrieval.
    Flushed during reorganization, on graceful shutdown, or after max_buffer_age_seconds.
    Optionally persists to a write-ahead log (WAL) for crash recovery.

    Usage:
        # At retrieval:
        await buffer.record_access(memory_id, "long_term")

        # During reorganization:
        result = await buffer.flush_all(short_term_collection, long_term_collection)

        # At startup (optional crash recovery):
        recovered = await buffer.recover_from_wal()
    """  # noqa: E501

    def __init__(self, config: AccessBufferConfig | None = None):
        self._config = config or AccessBufferConfig()
        self._short_term_buffer: dict[str, int] = {}  # memory_id → access_count
        self._long_term_buffer: dict[str, int] = {}
        self._last_flush_time = time.time()
        self._lock = asyncio.Lock()
        self._admission = asyncio.Condition()
        self._maintenance_active = False
        self._recovery_active = False
        self._active_recorders = 0
        self._quiescence_issuer_id = uuid4().hex
        self._active_quiescence_token: AccessBufferQuiescenceToken | None = None
        self._pending_drain_ids: dict[tuple[str, str], str] = {}
        self._wal_initialized = False
        self._wal_recovery_required = self._existing_wal_requires_recovery()
        self._force_drain_after_recovery = False
        self._reconciliation_required = self._wal_recovery_required

    @property
    def config(self) -> AccessBufferConfig:
        return self._config

    @property
    def short_term_count(self) -> int:
        """Number of unique memories in short-term buffer."""
        return len(self._short_term_buffer)

    @property
    def long_term_count(self) -> int:
        """Number of unique memories in long-term buffer."""
        return len(self._long_term_buffer)

    @property
    def total_count(self) -> int:
        """Total unique memories across both buffers."""
        return self.short_term_count + self.long_term_count

    @property
    def total_accesses(self) -> int:
        """Total access events buffered."""
        return sum(self._short_term_buffer.values()) + sum(
            self._long_term_buffer.values()
        )

    def get_stats(self) -> dict[str, int]:
        """Get buffer statistics."""
        return {
            "short_term_memories": self.short_term_count,
            "long_term_memories": self.long_term_count,
            "short_term_accesses": sum(self._short_term_buffer.values()),
            "long_term_accesses": sum(self._long_term_buffer.values()),
            "seconds_since_flush": int(time.time() - self._last_flush_time),
        }

    async def record_access(
        self,
        memory_id: str,
        collection_type: str,  # "short_term" or "long_term"
    ) -> None:
        """
        Record an access event after any configured WAL append is durable.

        The bounded filesystem transaction runs off the event loop. Callers may
        still use fire-and-forget task scheduling, but must retain task failures.

        Args:
            memory_id: ID of the accessed memory.
            collection_type: Either "short_term" or "long_term".
        """
        _validate_memory_id(memory_id)
        if not isinstance(collection_type, str) or collection_type not in {
            AccessCollectionType.SHORT_TERM.value,
            AccessCollectionType.LONG_TERM.value,
        }:
            raise ValueError("collection_type must be short_term or long_term")
        await self._enter_recorder()
        try:
            async with self._lock:
                buffer = (
                    self._short_term_buffer
                    if collection_type == "short_term"
                    else self._long_term_buffer
                )
                cancellation_requested = False
                if self._config.wal_path:
                    try:
                        cancellation_requested = await self._persist_to_wal(
                            memory_id,
                            collection_type,
                        )
                    except AccessBufferWalCommitError as exc:
                        if exc.logically_committed:
                            self._wal_recovery_required = True
                            self._force_drain_after_recovery = True
                            self._reconciliation_required = True
                        raise
                self._wal_initialized = True
                buffer[memory_id] = buffer.get(memory_id, 0) + 1

                if cancellation_requested:
                    raise asyncio.CancelledError

                if len(buffer) > self._config.max_buffer_size:
                    logger.info(
                        f"Auto-flushing {collection_type} buffer (size exceeded {self._config.max_buffer_size})"  # noqa: E501
                    )

                if (
                    time.time() - self._last_flush_time
                    > self._config.max_buffer_age_seconds
                ):
                    logger.debug(
                        f"Buffer age exceeded {self._config.max_buffer_age_seconds}s, "
                        "consider calling flush_all()"
                    )
        finally:
            await self._leave_recorder()

    async def _enter_recorder(self) -> None:
        async with self._admission:
            while self._maintenance_active or self._recovery_active:
                await self._admission.wait()
            if not self._wal_initialized and self._existing_wal_requires_recovery():
                self._wal_recovery_required = True
                self._reconciliation_required = True
            if self._reconciliation_required:
                raise AccessBufferQuiescenceError(
                    "AccessBuffer requires maintenance drain reconciliation"
                )
            self._active_recorders += 1

    async def _leave_recorder(self) -> None:
        async with self._admission:
            self._active_recorders -= 1
            self._admission.notify_all()

    @asynccontextmanager
    async def maintenance_quiescence(
        self,
    ) -> AsyncIterator[AccessBufferQuiescenceToken]:
        """Close recorder admission before awaiting already admitted writers."""
        activated = False
        try:
            async with self._admission:
                if self._maintenance_active:
                    raise AccessBufferQuiescenceError(
                        "AccessBuffer maintenance quiescence is already active"
                    )
                while self._recovery_active:
                    await self._admission.wait()
                self._maintenance_active = True
                activated = True
                while self._active_recorders > 0:
                    await self._admission.wait()
                token = AccessBufferQuiescenceToken(
                    self._quiescence_issuer_id,
                    uuid4().hex,
                )
                self._active_quiescence_token = token
            yield token
        finally:
            if activated:
                async with self._admission:
                    self._active_quiescence_token = None
                    self._maintenance_active = False
                    self._admission.notify_all()

    def _validate_quiescence_token(
        self, token: AccessBufferQuiescenceToken
    ) -> None:
        if (
            token is not self._active_quiescence_token
            or token._issuer_id != self._quiescence_issuer_id
            or not self._maintenance_active
        ):
            raise AccessBufferQuiescenceError(
                "Drain requires this buffer's active maintenance token"
            )

    async def _persist_to_wal(
        self,
        memory_id: str,
        collection_type: str,
    ) -> bool:
        """Durably append off-loop and report deferred task cancellation."""
        wal_path = self._config.wal_path
        if wal_path is None:
            return False
        record = AccessWalRecord(
            schema_version=1,
            memory_id=memory_id,
            collection_type=AccessCollectionType(collection_type),
            count=1,
            timestamp=time.time(),
        )
        payload = (record.model_dump_json() + "\n").encode("utf-8")
        append_task = asyncio.create_task(
            asyncio.to_thread(self._append_wal_record, wal_path, payload)
        )
        cancellation_requested = False
        while not append_task.done():
            try:
                await asyncio.shield(append_task)
            except asyncio.CancelledError:
                cancellation_requested = True
        append_task.result()
        return cancellation_requested

    def _append_wal_record(self, wal_path: Path, payload: bytes) -> None:
        """Perform one owner-only, durable append transaction."""
        wal_path.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_WRONLY | os.O_APPEND
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        if hasattr(os, "O_NONBLOCK"):
            flags |= os.O_NONBLOCK
        created = False
        mutated = False
        try:
            try:
                descriptor = os.open(
                    wal_path,
                    flags | os.O_CREAT | os.O_EXCL,
                    0o600,
                )
                created = True
            except FileExistsError:
                descriptor = os.open(wal_path, flags)
            try:
                info = os.fstat(descriptor)
                if not stat.S_ISREG(info.st_mode):
                    raise OSError("Access WAL target is not a regular file")
                if os.name == "posix":
                    os.fchmod(descriptor, 0o600)
                mutated = True
                self._write_all(descriptor, payload)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            if created:
                self._fsync_directory(wal_path.parent)
        except OSError as exc:
            raise AccessBufferWalCommitError(
                "Access WAL append could not be persisted",
                logically_committed=mutated,
            ) from exc

    def _existing_wal_requires_recovery(self) -> bool:
        """Inspect a WAL candidate without parsing or mutating its contents."""
        wal_path = self._config.wal_path
        if wal_path is None:
            return False
        try:
            path_info = wal_path.lstat()
        except FileNotFoundError:
            return False
        except OSError:
            return True
        if not stat.S_ISREG(path_info.st_mode):
            return True

        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        if hasattr(os, "O_NONBLOCK"):
            flags |= os.O_NONBLOCK
        try:
            descriptor = os.open(wal_path, flags)
            try:
                opened_info = os.fstat(descriptor)
                if (
                    not stat.S_ISREG(opened_info.st_mode)
                    or opened_info.st_dev != path_info.st_dev
                    or opened_info.st_ino != path_info.st_ino
                ):
                    return True
                return opened_info.st_size > 0
            finally:
                os.close(descriptor)
        except OSError:
            return True

    async def recover_from_wal(self) -> int:
        """
        Replay WAL entries on startup (if WAL exists).

        Returns:
            Number of access events recovered.
        """
        wal_path = self._config.wal_path
        if wal_path is None:
            return 0
        await self._enter_recovery()
        try:
            if not wal_path.exists():
                if self._wal_recovery_required:
                    raise AccessBufferWalError(
                        "Access WAL recovery is required but the WAL is unavailable"
                    )
                return 0
            async with self._lock:
                counts, pending_ids = self._load_wal_state(wal_path)
                short_term = {
                    memory_id: count
                    for (collection_type, memory_id), count in counts.items()
                    if collection_type == AccessCollectionType.SHORT_TERM.value
                }
                long_term = {
                    memory_id: count
                    for (collection_type, memory_id), count in counts.items()
                    if collection_type == AccessCollectionType.LONG_TERM.value
                }
                live_counts = {
                    **{
                        (AccessCollectionType.SHORT_TERM.value, memory_id): count
                        for memory_id, count in self._short_term_buffer.items()
                    },
                    **{
                        (AccessCollectionType.LONG_TERM.value, memory_id): count
                        for memory_id, count in self._long_term_buffer.items()
                    },
                }
                if any(
                    counts.get(key, 0) < live_count
                    for key, live_count in live_counts.items()
                ):
                    raise AccessBufferWalError(
                        "Access WAL conflicts with live in-memory buffer state"
                    )
                force_maintenance_drain = self._force_drain_after_recovery
                self._short_term_buffer = short_term
                self._long_term_buffer = long_term
                self._pending_drain_ids = pending_ids
                self._wal_recovery_required = False
                self._force_drain_after_recovery = False
                self._wal_initialized = True
                self._reconciliation_required = (
                    bool(pending_ids) or force_maintenance_drain
                )
                recovered = sum(counts.values())
                logger.info("Recovered buffered access state from durable WAL")
                return recovered
        finally:
            await self._leave_recovery()

    async def _enter_recovery(self) -> None:
        async with self._admission:
            if self._maintenance_active or self._recovery_active:
                raise AccessBufferQuiescenceError(
                    "Access WAL recovery is unavailable during quiescence"
                )
            self._recovery_active = True
            try:
                while self._active_recorders > 0:
                    await self._admission.wait()
            except BaseException:
                self._recovery_active = False
                self._admission.notify_all()
                raise

    async def _leave_recovery(self) -> None:
        async with self._admission:
            self._recovery_active = False
            self._admission.notify_all()

    @staticmethod
    def _write_all(descriptor: int, payload: bytes) -> None:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("Access WAL write did not make progress")
            view = view[written:]

    @staticmethod
    def _read_all(descriptor: int) -> bytes:
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)

    @classmethod
    def _read_wal_records(cls, wal_path: Path) -> list[AccessWalRecord]:
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            descriptor = os.open(wal_path, flags)
            try:
                info = os.fstat(descriptor)
                if not stat.S_ISREG(info.st_mode):
                    raise AccessBufferWalError("Access WAL is not a regular file")
                if os.name == "posix":
                    os.fchmod(descriptor, 0o600)
                payload = cls._read_all(descriptor)
            finally:
                os.close(descriptor)
        except OSError as exc:
            raise AccessBufferWalError("Access WAL cannot be read safely") from exc

        try:
            text = payload.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise AccessBufferWalError("Access WAL is not valid UTF-8") from exc
        if payload and not payload.endswith(b"\n"):
            raise AccessBufferWalError(
                "Access WAL contains a partial record; preserve it for recovery"
            )
        records: list[AccessWalRecord] = []
        for line in text.splitlines():
            if not line:
                raise AccessBufferWalError("Access WAL contains an empty record")
            try:
                if line.startswith("{"):
                    record = AccessWalRecord.model_validate_json(line)
                else:
                    record = cls._adapt_legacy_wal_line(line)
            except (ValueError, TypeError) as exc:
                raise AccessBufferWalError(
                    "Access WAL contains an invalid record; preserve it for recovery"
                ) from exc
            records.append(record)
        return records

    @staticmethod
    def _adapt_legacy_wal_line(line: str) -> AccessWalRecord:
        """Strict all-or-nothing compatibility adapter for historical CSV WALs."""
        parts = line.split(",")
        if len(parts) != 3:
            raise ValueError("legacy access WAL record must have three fields")
        memory_id, collection_type, raw_timestamp = parts
        _validate_memory_id(memory_id)
        parsed_type = AccessCollectionType(collection_type)
        timestamp = float(raw_timestamp)
        if not math.isfinite(timestamp):
            raise ValueError("legacy access WAL timestamp must be finite")
        return AccessWalRecord(
            schema_version=1,
            memory_id=memory_id,
            collection_type=parsed_type,
            count=1,
            timestamp=timestamp,
        )

    @classmethod
    def _load_wal_state(
        cls, wal_path: Path
    ) -> tuple[dict[tuple[str, str], int], dict[tuple[str, str], str]]:
        counts: dict[tuple[str, str], int] = {}
        pending_ids: dict[tuple[str, str], str] = {}
        used_drain_ids: set[str] = set()
        records = cls._read_wal_records(wal_path)
        if len({record.schema_version for record in records}) > 1:
            raise AccessBufferWalError(
                "Access WAL mixes event and pending-drain schemas"
            )
        for record in records:
            key = (record.collection_type.value, record.memory_id)
            if record.schema_version == 2:
                if key in counts or key in pending_ids or record.drain_id in used_drain_ids:
                    raise AccessBufferWalError(
                        "Access WAL contains ambiguous pending drain state"
                    )
                if record.drain_id is None:
                    raise AccessBufferWalError(
                        "Access WAL pending drain is missing its identity"
                    )
                counts[key] = record.count
                pending_ids[key] = record.drain_id
                used_drain_ids.add(record.drain_id)
            else:
                if key in pending_ids:
                    raise AccessBufferWalError(
                        "Access WAL mixes pending and new events for one memory"
                    )
                counts[key] = counts.get(key, 0) + 1
        return counts, pending_ids

    async def flush_all(
        self,
        short_term_collection: AccessMetadataCollection | None = None,
        long_term_collection: AccessMetadataCollection | None = None,
    ) -> FlushResult:
        """
        Batch-write all buffered accesses to collections.

        Called during reorganization or graceful shutdown.

        Args:
            short_term_collection: Collection for short-term memories.
            long_term_collection: Collection for long-term memories.

        Returns:
            FlushResult with counts and any errors.
        """
        async with self.maintenance_quiescence() as token:
            return await self.drain_for_maintenance(
                token,
                short_term_collection=short_term_collection,
                long_term_collection=long_term_collection,
            )

    async def drain_for_maintenance(
        self,
        token: AccessBufferQuiescenceToken,
        *,
        short_term_collection: AccessMetadataCollection | None = None,
        long_term_collection: AccessMetadataCollection | None = None,
    ) -> FlushResult:
        """Idempotently drain batches whose identities are durable before update."""
        self._validate_quiescence_token(token)
        async with self._lock:
            result = FlushResult()
            try:
                self._ensure_pending_drain_state()
            except AccessBufferWalCommitError:
                result.wal_verified = False
                result.short_term_remaining = len(self._short_term_buffer)
                result.long_term_remaining = len(self._long_term_buffer)
                result.errors.append("Access WAL pending state is not durable")
                self._reconciliation_required = True
                return result
            except AccessBufferWalError:
                result.wal_verified = False
                result.short_term_remaining = len(self._short_term_buffer)
                result.long_term_remaining = len(self._long_term_buffer)
                result.errors.append("Access WAL pending state is invalid")
                self._reconciliation_required = True
                return result

            successful_short_term: set[str] = set()
            successful_long_term: set[str] = set()

            if self._short_term_buffer and short_term_collection is None:
                result.errors.append("Short-term access collection is unavailable")
            elif short_term_collection is not None:
                for memory_id, count in self._short_term_buffer.items():
                    drain_id = self._pending_drain_ids[("short_term", memory_id)]
                    if await self._apply_access_batch(
                        short_term_collection,
                        memory_id=memory_id,
                        count=count,
                        collection_type=AccessCollectionType.SHORT_TERM,
                        drain_id=drain_id,
                    ):
                        successful_short_term.add(memory_id)
                        result.short_term_flushed += 1
                    else:
                        result.errors.append(
                            "One short-term access batch remains unreconciled"
                        )

            if self._long_term_buffer and long_term_collection is None:
                result.errors.append("Long-term access collection is unavailable")
            elif long_term_collection is not None:
                for memory_id, count in self._long_term_buffer.items():
                    drain_id = self._pending_drain_ids[("long_term", memory_id)]
                    if await self._apply_access_batch(
                        long_term_collection,
                        memory_id=memory_id,
                        count=count,
                        collection_type=AccessCollectionType.LONG_TERM,
                        drain_id=drain_id,
                    ):
                        successful_long_term.add(memory_id)
                        result.long_term_flushed += 1
                    else:
                        result.errors.append(
                            "One long-term access batch remains unreconciled"
                        )

            remaining_short_term = {
                memory_id: count
                for memory_id, count in self._short_term_buffer.items()
                if memory_id not in successful_short_term
            }
            remaining_long_term = {
                memory_id: count
                for memory_id, count in self._long_term_buffer.items()
                if memory_id not in successful_long_term
            }
            desired_records = self._pending_records_for(
                remaining_short_term,
                remaining_long_term,
            )
            try:
                self._replace_wal_records(desired_records)
            except AccessBufferWalCommitError as exc:
                result.wal_verified = False
                result.errors.append("Access WAL remainder durability is unverified")
                if exc.logically_committed:
                    self._commit_buffer_remainder(
                        remaining_short_term,
                        remaining_long_term,
                    )
            else:
                self._commit_buffer_remainder(
                    remaining_short_term,
                    remaining_long_term,
                )

            result.short_term_remaining = len(self._short_term_buffer)
            result.long_term_remaining = len(self._long_term_buffer)
            self._reconciliation_required = (
                not result.wal_verified
                or result.short_term_remaining > 0
                or result.long_term_remaining > 0
            )

            if result.short_term_flushed > 0 or result.long_term_flushed > 0:
                logger.info(f"Flushed access buffer: {result.summary()}")
            return result

    async def _apply_access_batch(
        self,
        collection: AccessMetadataCollection,
        *,
        memory_id: str,
        count: int,
        collection_type: AccessCollectionType,
        drain_id: str,
    ) -> bool:
        try:
            doc = await collection.get_by_id(memory_id)
            if not doc:
                return False
            metadata = doc.get("metadata", {})
            if metadata.get(_ACCESS_DRAIN_MARKER) == drain_id:
                return True
            updates: dict[str, object] = {
                "last_accessed_at": datetime.now().isoformat(),
                _ACCESS_DRAIN_MARKER: drain_id,
            }
            if collection_type is AccessCollectionType.SHORT_TERM:
                current_score = metadata.get("decay_score", 0.5)
                updates.update(
                    {
                        "decay_score": min(
                            1.0,
                            current_score
                            + (self._config.decay_score_boost * count),
                        ),
                        "access_count": metadata.get("access_count", 0) + count,
                    }
                )
            else:
                updates["hit_count"] = metadata.get("hit_count", 0) + count
            updated = await collection.update_metadata(memory_id, updates)
            return updated is not False
        except asyncio.CancelledError:
            raise
        except Exception:
            try:
                reconciled = await collection.get_by_id(memory_id)
            except Exception:
                return False
            if not reconciled:
                return False
            try:
                metadata = reconciled.get("metadata", {})
                return metadata.get(_ACCESS_DRAIN_MARKER) == drain_id
            except (AttributeError, TypeError):
                return False

    def _ensure_pending_drain_state(self) -> None:
        if self._wal_recovery_required:
            raise AccessBufferWalError(
                "Access WAL requires strict recovery before maintenance drain"
            )
        current_counts = {
            **{
                (AccessCollectionType.SHORT_TERM.value, memory_id): count
                for memory_id, count in self._short_term_buffer.items()
            },
            **{
                (AccessCollectionType.LONG_TERM.value, memory_id): count
                for memory_id, count in self._long_term_buffer.items()
            },
        }
        wal_path = self._config.wal_path
        if self._pending_drain_ids:
            if set(self._pending_drain_ids) != set(current_counts):
                raise AccessBufferWalError(
                    "Pending access drain IDs do not match buffered state"
                )
            if wal_path is not None:
                wal_counts, wal_pending = self._load_wal_state(wal_path)
                if wal_counts != current_counts or wal_pending != self._pending_drain_ids:
                    raise AccessBufferWalError(
                        "Access WAL does not match pending in-memory drain state"
                    )
            return

        if wal_path is not None:
            try:
                wal_path.lstat()
            except FileNotFoundError:
                if current_counts:
                    raise AccessBufferWalError(
                        "Access WAL is missing buffered access events"
                    ) from None
            except OSError as exc:
                raise AccessBufferWalError(
                    "Access WAL state cannot be validated"
                ) from exc
            else:
                wal_counts, wal_pending = self._load_wal_state(wal_path)
                if wal_pending or wal_counts != current_counts:
                    raise AccessBufferWalError(
                        "Access WAL does not match buffered event state"
                    )

        pending_ids = {key: uuid4().hex for key in current_counts}
        records = [
            AccessWalRecord(
                schema_version=2,
                memory_id=memory_id,
                collection_type=AccessCollectionType(collection_type),
                count=count,
                drain_id=pending_ids[(collection_type, memory_id)],
            )
            for (collection_type, memory_id), count in sorted(current_counts.items())
        ]
        try:
            self._replace_wal_records(records)
        except AccessBufferWalCommitError as exc:
            if exc.logically_committed:
                self._pending_drain_ids = pending_ids
            raise
        self._pending_drain_ids = pending_ids
        self._reconciliation_required = bool(pending_ids)

    def _pending_records_for(
        self,
        short_term: dict[str, int],
        long_term: dict[str, int],
    ) -> list[AccessWalRecord]:
        records: list[AccessWalRecord] = []
        for collection_type, buffer in (
            (AccessCollectionType.SHORT_TERM, short_term),
            (AccessCollectionType.LONG_TERM, long_term),
        ):
            for memory_id, count in sorted(buffer.items()):
                records.append(
                    AccessWalRecord(
                        schema_version=2,
                        memory_id=memory_id,
                        collection_type=collection_type,
                        count=count,
                        drain_id=self._pending_drain_ids[
                            (collection_type.value, memory_id)
                        ],
                    )
                )
        return records

    def _commit_buffer_remainder(
        self,
        short_term: dict[str, int],
        long_term: dict[str, int],
    ) -> None:
        self._short_term_buffer = short_term
        self._long_term_buffer = long_term
        remaining_keys = {
            *(
                (AccessCollectionType.SHORT_TERM.value, memory_id)
                for memory_id in short_term
            ),
            *(
                (AccessCollectionType.LONG_TERM.value, memory_id)
                for memory_id in long_term
            ),
        }
        self._pending_drain_ids = {
            key: drain_id
            for key, drain_id in self._pending_drain_ids.items()
            if key in remaining_keys
        }
        self._wal_initialized = bool(remaining_keys)
        self._last_flush_time = time.time()

    @staticmethod
    def _fsync_directory(directory: Path) -> None:
        if os.name != "posix":
            return
        descriptor = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def _replace_wal_records(self, records: list[AccessWalRecord]) -> None:
        wal_path = self._config.wal_path
        if wal_path is None:
            return
        if not records:
            try:
                wal_path.unlink(missing_ok=True)
            except OSError as exc:
                raise AccessBufferWalCommitError(
                    "Access WAL could not be removed",
                    logically_committed=False,
                ) from exc
            try:
                if wal_path.parent.exists():
                    self._fsync_directory(wal_path.parent)
            except OSError as exc:
                raise AccessBufferWalCommitError(
                    "Access WAL removal durability is unverified",
                    logically_committed=True,
                ) from exc
            return
        payload = "".join(record.model_dump_json() + "\n" for record in records).encode(
            "utf-8"
        )
        wal_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = wal_path.with_name(f".{wal_path.name}.{uuid4().hex}.tmp")
        replaced = False
        try:
            descriptor = os.open(
                temp_path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
            try:
                if os.name == "posix":
                    os.fchmod(descriptor, 0o600)
                self._write_all(descriptor, payload)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            os.replace(temp_path, wal_path)
            replaced = True
            if os.name == "posix":
                wal_path.chmod(0o600)
            self._fsync_directory(wal_path.parent)
            verified_records = self._read_wal_records(wal_path)
            if verified_records != records:
                raise OSError("Access WAL replacement verification failed")
        except OSError as exc:
            with suppress(OSError):
                temp_path.unlink(missing_ok=True)
            raise AccessBufferWalCommitError(
                "Access WAL replacement could not be verified",
                logically_committed=replaced,
            ) from exc

    def needs_flush(self) -> bool:
        """Check if buffer should be flushed (size or time exceeded)."""
        if self.total_count == 0:
            return False

        size_exceeded = (
            self.short_term_count > self._config.max_buffer_size
            or self.long_term_count > self._config.max_buffer_size
        )
        time_exceeded = (
            time.time() - self._last_flush_time > self._config.max_buffer_age_seconds
        )

        return size_exceeded or time_exceeded

    def clear(self) -> None:
        """Clear all buffers without flushing to collections."""
        if (
            self._maintenance_active
            or self._recovery_active
            or self._active_recorders > 0
            or self._lock.locked()
            or self._reconciliation_required
        ):
            raise AccessBufferQuiescenceError(
                "AccessBuffer cannot be cleared while mutation is admitted"
            )
        self._short_term_buffer.clear()
        self._long_term_buffer.clear()
        self._pending_drain_ids.clear()
        self._wal_initialized = False
        self._wal_recovery_required = self._existing_wal_requires_recovery()
        self._force_drain_after_recovery = False
        self._reconciliation_required = self._wal_recovery_required
        self._last_flush_time = time.time()
