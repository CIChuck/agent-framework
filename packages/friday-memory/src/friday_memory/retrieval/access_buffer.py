# mypy: ignore-errors
"""
Access Buffer for Lazy Access Tracking.

Buffers memory access events in-memory for batch processing during reorganization.
Eliminates synchronous DB writes during retrieval for better latency.

Ref: docs/build-plan/memory-lifecycle-staging-decay.md - Optimization B
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from friday_memory.retrieval.collection_manager import ManagedCollection

logger = logging.getLogger(__name__)


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


class AccessBuffer:
    """
    Buffer access events for batch processing.

    Eliminates synchronous DB writes during retrieval.
    Flushed during reorganization, on graceful shutdown, or after max_buffer_age_seconds.
    Optionally persists to a write-ahead log (WAL) for crash recovery.

    Usage:
        # At retrieval (fire-and-forget, no await needed for recording):
        asyncio.create_task(buffer.record_access(memory_id, "long_term"))

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
        Record access event (O(1), in-memory only).

        This is called during retrieval - must be fast.
        Use fire-and-forget: asyncio.create_task(buffer.record_access(...))

        Args:
            memory_id: ID of the accessed memory.
            collection_type: Either "short_term" or "long_term".
        """
        async with self._lock:
            buffer = (
                self._short_term_buffer
                if collection_type == "short_term"
                else self._long_term_buffer
            )
            buffer[memory_id] = buffer.get(memory_id, 0) + 1

            # Optional: persist to WAL for crash recovery
            if self._config.wal_path:
                await self._persist_to_wal(memory_id, collection_type)

            # Auto-flush if buffer gets too large
            if len(buffer) > self._config.max_buffer_size:
                logger.info(
                    f"Auto-flushing {collection_type} buffer (size exceeded {self._config.max_buffer_size})"  # noqa: E501
                )
                # Note: We can't flush here without collection references
                # This is a signal that flush_all should be called soon

            # Time-based flush check (log warning, actual flush needs collections)
            if (
                time.time() - self._last_flush_time
                > self._config.max_buffer_age_seconds
            ):
                logger.debug(
                    f"Buffer age exceeded {self._config.max_buffer_age_seconds}s, "
                    "consider calling flush_all()"
                )

    async def _persist_to_wal(self, memory_id: str, collection_type: str) -> None:
        """Optional: Append to WAL for crash recovery."""
        if not self._config.wal_path:
            return

        try:
            # Use sync file operations in thread pool to avoid aiofiles dependency
            def write_wal():
                with open(self._config.wal_path, "a") as f:
                    f.write(f"{memory_id},{collection_type},{time.time()}\n")

            await asyncio.get_event_loop().run_in_executor(None, write_wal)
        except Exception as e:
            logger.warning(f"Failed to persist to WAL: {e}")

    async def recover_from_wal(self) -> int:
        """
        Replay WAL entries on startup (if WAL exists).

        Returns:
            Number of access events recovered.
        """
        if not self._config.wal_path or not self._config.wal_path.exists():
            return 0

        recovered = 0

        try:

            def read_wal():
                entries = []
                with open(self._config.wal_path) as f:
                    for line in f:
                        try:
                            parts = line.strip().split(",")
                            if len(parts) >= 2:
                                entries.append((parts[0], parts[1]))
                        except ValueError:
                            continue
                return entries

            entries = await asyncio.get_event_loop().run_in_executor(None, read_wal)

            async with self._lock:
                for memory_id, collection_type in entries:
                    buffer = (
                        self._short_term_buffer
                        if collection_type == "short_term"
                        else self._long_term_buffer
                    )
                    buffer[memory_id] = buffer.get(memory_id, 0) + 1
                    recovered += 1

            # Clear WAL after successful recovery
            if recovered > 0:
                self._config.wal_path.unlink(missing_ok=True)
                logger.info(f"Recovered {recovered} access events from WAL")

        except Exception as e:
            logger.error(f"Failed to recover from WAL: {e}")

        return recovered

    async def flush_all(
        self,
        short_term_collection: "ManagedCollection | None" = None,
        long_term_collection: "ManagedCollection | None" = None,
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
        result = FlushResult()

        async with self._lock:
            short_term_copy = self._short_term_buffer.copy()
            long_term_copy = self._long_term_buffer.copy()
            self._short_term_buffer.clear()
            self._long_term_buffer.clear()
            self._last_flush_time = time.time()

        # Batch update short-term (boost decay_score)
        if short_term_collection and short_term_copy:
            for memory_id, count in short_term_copy.items():
                try:
                    doc = await short_term_collection.get_by_id(memory_id)
                    if doc:
                        metadata = doc.get("metadata", {})
                        current_score = metadata.get("decay_score", 0.5)
                        new_score = min(
                            1.0,
                            current_score + (self._config.decay_score_boost * count),
                        )
                        await short_term_collection.update_metadata(
                            memory_id,
                            {
                                "decay_score": new_score,
                                "access_count": metadata.get("access_count", 0) + count,
                                "last_accessed_at": datetime.now().isoformat(),
                            },
                        )
                        result.short_term_flushed += 1
                except Exception as e:
                    result.errors.append(
                        f"Failed to update short-term {memory_id}: {e}"
                    )

        # Batch update long-term (increment hit_count)
        if long_term_collection and long_term_copy:
            for memory_id, count in long_term_copy.items():
                try:
                    doc = await long_term_collection.get_by_id(memory_id)
                    if doc:
                        metadata = doc.get("metadata", {})
                        current_hits = metadata.get("hit_count", 0)
                        await long_term_collection.update_metadata(
                            memory_id,
                            {
                                "hit_count": current_hits + count,
                                "last_accessed_at": datetime.now().isoformat(),
                            },
                        )
                        result.long_term_flushed += 1
                except Exception as e:
                    result.errors.append(f"Failed to update long-term {memory_id}: {e}")

        # Clear WAL after successful flush
        if self._config.wal_path:
            try:
                self._config.wal_path.unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Failed to clear WAL: {e}")

        if result.short_term_flushed > 0 or result.long_term_flushed > 0:
            logger.info(f"Flushed access buffer: {result.summary()}")

        return result

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
        self._short_term_buffer.clear()
        self._long_term_buffer.clear()
        self._last_flush_time = time.time()
