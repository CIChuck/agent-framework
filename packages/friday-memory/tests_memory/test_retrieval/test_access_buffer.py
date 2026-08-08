# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
# mypy: disallow-untyped-defs=False
"""Tests for AccessBuffer."""

import asyncio
import os
import stat
import tempfile
import threading
from pathlib import Path

import pytest
from friday_memory.retrieval.access_buffer import (
    AccessBuffer,
    AccessBufferConfig,
    AccessBufferQuiescenceError,
    AccessBufferQuiescenceToken,
    AccessBufferWalCommitError,
    AccessBufferWalError,
    AccessCollectionType,
    AccessWalRecord,
    FlushResult,
)
from pydantic import ValidationError


class RecordingCollection:
    """Stateful collection double for retry and unknown-outcome tests."""

    def __init__(
        self,
        *,
        failing_ids: set[str] | None = None,
        false_ids: set[str] | None = None,
        raise_after_commit_ids: set[str] | None = None,
        block_after_commit_ids: set[str] | None = None,
    ) -> None:
        self.failing_ids = failing_ids or set()
        self.false_ids = false_ids or set()
        self.raise_after_commit_ids = raise_after_commit_ids or set()
        self.block_after_commit_ids = block_after_commit_ids or set()
        self.updates: list[tuple[str, dict[str, object]]] = []
        self.metadata: dict[str, dict[str, object]] = {}
        self.committed = asyncio.Event()
        self.release = asyncio.Event()

    def metadata_for(self, memory_id: str) -> dict[str, object]:
        return self.metadata.setdefault(
            memory_id,
            {"decay_score": 0.5, "access_count": 0, "hit_count": 0},
        )

    async def get_by_id(self, memory_id: str) -> dict[str, object]:
        return {"metadata": self.metadata_for(memory_id).copy()}

    async def update_metadata(
        self, memory_id: str, metadata: dict[str, object]
    ) -> bool:
        if memory_id in self.failing_ids:
            raise RuntimeError("synthetic update failure")
        if memory_id in self.false_ids:
            return False
        self.metadata_for(memory_id).update(metadata)
        self.updates.append((memory_id, metadata))
        if memory_id in self.block_after_commit_ids:
            self.committed.set()
            await self.release.wait()
        if memory_id in self.raise_after_commit_ids:
            raise RuntimeError("synthetic unknown update outcome")
        return True


def read_wal_records(wal_path: Path) -> list[AccessWalRecord]:
    """Read strict JSONL records written by the current WAL schema."""
    return [
        AccessWalRecord.model_validate_json(line)
        for line in wal_path.read_text().splitlines()
    ]


class TestAccessBufferConfig:
    """Test AccessBufferConfig defaults and customization."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = AccessBufferConfig()
        assert config.max_buffer_size == 1000
        assert config.max_buffer_age_seconds == 300
        assert config.wal_path is None
        assert config.decay_score_boost == 0.1

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = AccessBufferConfig(
            max_buffer_size=500,
            max_buffer_age_seconds=60,
            wal_path=Path("/tmp/test.wal"),
            decay_score_boost=0.2,
        )
        assert config.max_buffer_size == 500
        assert config.max_buffer_age_seconds == 60
        assert config.wal_path == Path("/tmp/test.wal")
        assert config.decay_score_boost == 0.2


class TestFlushResult:
    """Test FlushResult dataclass."""

    def test_default_values(self) -> None:
        """Test default initialization."""
        result = FlushResult()
        assert result.short_term_flushed == 0
        assert result.long_term_flushed == 0
        assert result.errors == []
        assert not result.has_errors()

    def test_has_errors(self) -> None:
        """Test error detection."""
        result = FlushResult(errors=["Something went wrong"])
        assert result.has_errors()

    def test_summary_no_flushes(self) -> None:
        """Test summary with no flushes."""
        result = FlushResult()
        assert result.summary() == "No accesses flushed"

    def test_summary_with_flushes(self) -> None:
        """Test summary with flushed data."""
        result = FlushResult(short_term_flushed=5, long_term_flushed=10)
        summary = result.summary()
        assert "short_term=5" in summary
        assert "long_term=10" in summary


class TestAccessBuffer:
    """Test AccessBuffer class."""

    @pytest.fixture
    def config(self):
        """Create default config."""
        return AccessBufferConfig()

    @pytest.fixture
    def buffer(self, config):
        """Create buffer with default config."""
        return AccessBuffer(config)

    def test_init_defaults(self) -> None:
        """Test buffer initializes with defaults."""
        buffer = AccessBuffer()
        assert buffer.short_term_count == 0
        assert buffer.long_term_count == 0
        assert buffer.total_count == 0
        assert buffer.total_accesses == 0

    @pytest.mark.asyncio
    async def test_record_access_short_term(self, buffer) -> None:
        """Test recording short-term access."""
        await buffer.record_access("mem1", "short_term")

        assert buffer.short_term_count == 1
        assert buffer.long_term_count == 0
        assert buffer.total_accesses == 1

    @pytest.mark.asyncio
    async def test_record_access_long_term(self, buffer) -> None:
        """Test recording long-term access."""
        await buffer.record_access("mem1", "long_term")

        assert buffer.short_term_count == 0
        assert buffer.long_term_count == 1
        assert buffer.total_accesses == 1

    @pytest.mark.asyncio
    async def test_record_multiple_accesses_same_memory(self, buffer) -> None:
        """Test multiple accesses to same memory accumulate."""
        await buffer.record_access("mem1", "long_term")
        await buffer.record_access("mem1", "long_term")
        await buffer.record_access("mem1", "long_term")

        assert buffer.long_term_count == 1  # Unique count
        assert buffer.total_accesses == 3  # Total accesses

    @pytest.mark.asyncio
    async def test_record_multiple_memories(self, buffer) -> None:
        """Test tracking multiple different memories."""
        await buffer.record_access("mem1", "short_term")
        await buffer.record_access("mem2", "short_term")
        await buffer.record_access("mem3", "long_term")

        assert buffer.short_term_count == 2
        assert buffer.long_term_count == 1
        assert buffer.total_count == 3

    def test_get_stats(self, buffer) -> None:
        """Test get_stats returns correct statistics."""
        stats = buffer.get_stats()

        assert "short_term_memories" in stats
        assert "long_term_memories" in stats
        assert "short_term_accesses" in stats
        assert "long_term_accesses" in stats
        assert "seconds_since_flush" in stats

    @pytest.mark.asyncio
    async def test_get_stats_after_accesses(self, buffer) -> None:
        """Test stats update after recording accesses."""
        await buffer.record_access("mem1", "short_term")
        await buffer.record_access("mem1", "short_term")
        await buffer.record_access("mem2", "long_term")

        stats = buffer.get_stats()
        assert stats["short_term_memories"] == 1
        assert stats["short_term_accesses"] == 2
        assert stats["long_term_memories"] == 1
        assert stats["long_term_accesses"] == 1

    def test_needs_flush_empty_buffer(self, buffer) -> None:
        """Test needs_flush returns False for empty buffer."""
        assert not buffer.needs_flush()

    @pytest.mark.asyncio
    async def test_needs_flush_with_data(self, buffer) -> None:
        """Test needs_flush returns False when below thresholds."""
        await buffer.record_access("mem1", "short_term")
        # Default max_buffer_size is 1000, so this shouldn't trigger
        assert not buffer.needs_flush()

    def test_clear_buffer(self, buffer) -> None:
        """Test clearing buffers."""
        # This is a sync operation
        buffer._short_term_buffer["mem1"] = 5
        buffer._long_term_buffer["mem2"] = 3

        buffer.clear()

        assert buffer.short_term_count == 0
        assert buffer.long_term_count == 0

    @pytest.mark.asyncio
    async def test_flush_all_empty(self, buffer) -> None:
        """Test flush_all with empty buffers."""
        result = await buffer.flush_all()

        assert result.short_term_flushed == 0
        assert result.long_term_flushed == 0
        assert not result.has_errors()


class TestAccessBufferWAL:
    """Test AccessBuffer WAL (write-ahead log) functionality."""

    @pytest.fixture
    def temp_wal_path(self):
        """Create a temporary WAL file path."""
        with tempfile.NamedTemporaryFile(suffix=".wal", delete=False) as f:
            return Path(f.name)

    @pytest.fixture
    def wal_config(self, temp_wal_path):
        """Create config with WAL enabled."""
        return AccessBufferConfig(wal_path=temp_wal_path)

    @pytest.fixture
    def wal_buffer(self, wal_config):
        """Create buffer with WAL enabled."""
        return AccessBuffer(wal_config)

    @pytest.mark.asyncio
    async def test_wal_persists_on_access(self, wal_buffer, temp_wal_path) -> None:
        """Test that WAL file is written on access."""
        await wal_buffer.record_access("mem1", "long_term")

        assert temp_wal_path.exists()
        records = read_wal_records(temp_wal_path)
        assert len(records) == 1
        assert records[0].schema_version == 1
        assert records[0].memory_id == "mem1"
        assert records[0].collection_type is AccessCollectionType.LONG_TERM
        assert records[0].count == 1
        assert records[0].timestamp is not None

    @pytest.mark.asyncio
    async def test_recover_from_wal(self, wal_buffer, temp_wal_path) -> None:
        """Test recovering access events from WAL."""
        # Write some events to WAL
        await wal_buffer.record_access("mem1", "short_term")
        await wal_buffer.record_access("mem2", "long_term")

        # Clear the buffer (simulating crash)
        wal_buffer.clear()
        assert wal_buffer.total_count == 0

        # Recover from WAL
        recovered = await wal_buffer.recover_from_wal()

        assert recovered == 2
        assert wal_buffer.short_term_count == 1
        assert wal_buffer.long_term_count == 1

    @pytest.mark.asyncio
    async def test_recover_from_nonexistent_wal(self, wal_buffer, temp_wal_path) -> None:
        """Test recovery handles missing WAL file."""
        # Delete the WAL file
        temp_wal_path.unlink(missing_ok=True)

        recovered = await wal_buffer.recover_from_wal()
        assert recovered == 0

    @pytest.mark.asyncio
    async def test_recover_preserves_wal_until_drain(
        self, wal_buffer, temp_wal_path
    ) -> None:
        """Recovery keeps the durable source until effects are drained."""
        await wal_buffer.record_access("mem1", "long_term")

        wal_buffer.clear()
        await wal_buffer.recover_from_wal()

        assert temp_wal_path.exists()
        assert len(read_wal_records(temp_wal_path)) == 1


class TestAccessBufferConcurrency:
    """Test AccessBuffer thread safety."""

    @pytest.mark.asyncio
    async def test_concurrent_access_recording(self) -> None:
        """Test concurrent access recording is thread-safe."""
        buffer = AccessBuffer()

        async def record_many(prefix: str, count: int):
            for i in range(count):
                await buffer.record_access(f"{prefix}_{i}", "long_term")

        # Run concurrent recordings
        await asyncio.gather(
            record_many("a", 100),
            record_many("b", 100),
            record_many("c", 100),
        )

        # Should have 300 unique memories
        assert buffer.long_term_count == 300
        assert buffer.total_accesses == 300


class TestAccessBufferWalSafety:
    """Tests for strict WAL parsing, durability, and admission cleanup."""

    def test_persisted_model_rejects_coercion_and_invalid_drain_ids(self) -> None:
        with pytest.raises(ValidationError):
            AccessWalRecord.model_validate_json(
                '{"schema_version":"1","memory_id":"coerced",'
                '"collection_type":"long_term","count":"1",'
                '"timestamp":1.0,"drain_id":null}'
            )

        for invalid_drain_id in (
            "short",
            "A" * 32,
            "00000000-0000-0000-0000-000000000000",
        ):
            with pytest.raises(ValidationError):
                AccessWalRecord(
                    schema_version=2,
                    memory_id="invalid-drain-id",
                    collection_type=AccessCollectionType.LONG_TERM,
                    count=1,
                    drain_id=invalid_drain_id,
                )

    @pytest.mark.asyncio
    async def test_fresh_v1_wal_requires_recovery_before_record_or_drain(
        self, tmp_path: Path
    ) -> None:
        wal_path = tmp_path / "access.wal"
        record = AccessWalRecord(
            schema_version=1,
            memory_id="restart-v1",
            collection_type=AccessCollectionType.LONG_TERM,
            count=1,
            timestamp=1.0,
        )
        original = (record.model_dump_json() + "\n").encode()
        wal_path.write_bytes(original)
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))

        with pytest.raises(AccessBufferQuiescenceError):
            await buffer.record_access("new-before-recovery", "long_term")
        async with buffer.maintenance_quiescence() as token:
            blocked = await buffer.drain_for_maintenance(
                token,
                long_term_collection=RecordingCollection(),
            )
        assert not blocked.verified_drained
        assert wal_path.read_bytes() == original

        assert await buffer.recover_from_wal() == 1
        await buffer.record_access("restart-v1", "long_term")
        collection = RecordingCollection()
        async with buffer.maintenance_quiescence() as token:
            drained = await buffer.drain_for_maintenance(
                token,
                long_term_collection=collection,
            )
        assert drained.verified_drained
        assert collection.metadata_for("restart-v1")["hit_count"] == 2

    @pytest.mark.asyncio
    async def test_fresh_v2_wal_stays_gated_until_reconciled(
        self, tmp_path: Path
    ) -> None:
        wal_path = tmp_path / "access.wal"
        record = AccessWalRecord(
            schema_version=2,
            memory_id="restart-v2",
            collection_type=AccessCollectionType.LONG_TERM,
            count=3,
            drain_id="b" * 32,
        )
        original = (record.model_dump_json() + "\n").encode()
        wal_path.write_bytes(original)
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))

        with pytest.raises(AccessBufferQuiescenceError):
            await buffer.record_access("new-before-v2-recovery", "long_term")
        async with buffer.maintenance_quiescence() as token:
            blocked = await buffer.drain_for_maintenance(token)
        assert not blocked.verified_drained
        assert wal_path.read_bytes() == original

        assert await buffer.recover_from_wal() == 3
        with pytest.raises(AccessBufferQuiescenceError):
            await buffer.record_access("new-before-v2-drain", "long_term")
        collection = RecordingCollection()
        async with buffer.maintenance_quiescence() as token:
            drained = await buffer.drain_for_maintenance(
                token,
                long_term_collection=collection,
            )
        assert drained.verified_drained
        assert collection.metadata_for("restart-v2")["hit_count"] == 3

    @pytest.mark.asyncio
    async def test_fresh_unsafe_wal_candidates_block_and_are_preserved(
        self, tmp_path: Path
    ) -> None:
        corrupt_path = tmp_path / "corrupt.wal"
        corrupt_bytes = b'{"schema_version":1'
        corrupt_path.write_bytes(corrupt_bytes)

        symlink_target = tmp_path / "symlink-target.wal"
        symlink_bytes = b"target-must-not-change\n"
        symlink_target.write_bytes(symlink_bytes)
        symlink_path = tmp_path / "symlink.wal"
        symlink_supported = True
        try:
            symlink_path.symlink_to(symlink_target)
        except (NotImplementedError, OSError):
            symlink_supported = False

        non_regular_path = tmp_path / "directory.wal"
        non_regular_path.mkdir()

        candidates = [corrupt_path, non_regular_path]
        if symlink_supported:
            candidates.append(symlink_path)
        for wal_path in candidates:
            buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
            with pytest.raises(AccessBufferQuiescenceError):
                await buffer.record_access("blocked-unsafe-wal", "long_term")
            async with buffer.maintenance_quiescence() as token:
                blocked = await buffer.drain_for_maintenance(token)
            assert not blocked.verified_drained

        assert corrupt_path.read_bytes() == corrupt_bytes
        if symlink_supported:
            assert symlink_path.is_symlink()
        assert symlink_target.read_bytes() == symlink_bytes
        assert non_regular_path.is_dir()

    @pytest.mark.asyncio
    async def test_fresh_unreadable_wal_candidate_blocks_without_mutation(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        wal_path = tmp_path / "unreadable.wal"
        original = b""
        wal_path.write_bytes(original)
        real_open = os.open

        def deny_wal_open(path: str | bytes | os.PathLike[str], flags: int, *args):
            if os.fspath(path) == os.fspath(wal_path):
                raise PermissionError("synthetic unreadable WAL")
            return real_open(path, flags, *args)

        monkeypatch.setattr(os, "open", deny_wal_open)
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))

        with pytest.raises(AccessBufferQuiescenceError):
            await buffer.record_access("blocked-unreadable-wal", "long_term")
        async with buffer.maintenance_quiescence() as token:
            blocked = await buffer.drain_for_maintenance(token)

        assert not blocked.verified_drained
        assert wal_path.read_bytes() == original

    @pytest.mark.asyncio
    async def test_invalid_input_is_rejected_before_admission(
        self, tmp_path: Path
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))

        async with buffer.maintenance_quiescence():
            with pytest.raises(ValueError):
                await asyncio.wait_for(
                    buffer.record_access("unsafe\nidentifier", "long_term"),
                    timeout=0.5,
                )
            with pytest.raises(ValueError):
                await asyncio.wait_for(
                    buffer.record_access("safe-identifier", "unknown"),
                    timeout=0.5,
                )

        assert not wal_path.exists()
        assert buffer.total_count == 0

    @pytest.mark.asyncio
    async def test_owner_only_append_rejects_non_regular_target(
        self, tmp_path: Path
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
        await buffer.record_access("owner-only", "long_term")

        if os.name == "posix":
            assert stat.S_IMODE(wal_path.stat().st_mode) == 0o600

        other_path = tmp_path / "not-a-file.wal"
        other_path.mkdir()
        other = AccessBuffer(AccessBufferConfig(wal_path=other_path))
        with pytest.raises(AccessBufferQuiescenceError):
            await other.record_access("not-regular", "long_term")
        assert other.total_count == 0

    @pytest.mark.asyncio
    async def test_legacy_wal_adapter_is_all_or_nothing(self, tmp_path: Path) -> None:
        wal_path = tmp_path / "access.wal"
        wal_path.write_text(
            "legacy-short,short_term,1.0\nlegacy-long,long_term,2.0\n"
        )
        os.chmod(wal_path, 0o600)
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))

        assert await buffer.recover_from_wal() == 2
        assert buffer.short_term_count == 1
        assert buffer.long_term_count == 1

        corrupt_path = tmp_path / "corrupt.wal"
        original = b"valid,long_term,1.0\ninvalid,long_term,nan\n"
        corrupt_path.write_bytes(original)
        corrupt = AccessBuffer(AccessBufferConfig(wal_path=corrupt_path))
        with pytest.raises(AccessBufferWalError):
            await corrupt.recover_from_wal()
        assert corrupt.total_count == 0
        assert corrupt_path.read_bytes() == original

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload",
        [
            b'{"schema_version":1,"memory_id":"partial"',
            (
                b'{"schema_version":1,"memory_id":"unknown-type",'
                b'"collection_type":"other","count":1,"timestamp":1.0,'
                b'"drain_id":null}\n'
            ),
            b"not,valid,legacy,wal\n",
            (
                b'{"schema_version":1,"memory_id":"event","collection_type":'
                b'"long_term","count":1,"timestamp":1.0,"drain_id":null}\n'
                b'{"schema_version":2,"memory_id":"pending","collection_type":'
                b'"long_term","count":1,"timestamp":null,'
                b'"drain_id":"pending-id"}\n'
            ),
        ],
    )
    async def test_invalid_wal_is_preserved_and_fails_closed(
        self, tmp_path: Path, payload: bytes
    ) -> None:
        wal_path = tmp_path / "access.wal"
        wal_path.write_bytes(payload)
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))

        with pytest.raises(AccessBufferWalError) as error:
            await buffer.recover_from_wal()

        assert "unknown-type" not in str(error.value)
        assert wal_path.read_bytes() == payload
        assert buffer.total_count == 0

    @pytest.mark.asyncio
    async def test_cancelled_append_commits_matching_buffer_before_cleanup(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
        append_started = threading.Event()
        release_append = threading.Event()
        original_append = buffer._append_wal_record

        def blocking_append(path: Path, payload: bytes) -> None:
            append_started.set()
            if not release_append.wait(timeout=2):
                raise OSError("synthetic append timeout")
            original_append(path, payload)

        monkeypatch.setattr(buffer, "_append_wal_record", blocking_append)
        recorder = asyncio.create_task(
            buffer.record_access("cancelled-append", "long_term")
        )
        assert await asyncio.to_thread(append_started.wait, 1)

        maintenance_entered = asyncio.Event()

        async def enter_maintenance() -> None:
            async with buffer.maintenance_quiescence():
                maintenance_entered.set()

        maintenance = asyncio.create_task(enter_maintenance())
        await asyncio.sleep(0)
        assert not maintenance_entered.is_set()

        recorder.cancel()
        await asyncio.sleep(0)
        assert not recorder.done()
        release_append.set()
        with pytest.raises(asyncio.CancelledError):
            await recorder
        await asyncio.wait_for(maintenance_entered.wait(), timeout=1)
        await maintenance

        assert buffer.total_accesses == 1
        assert len(read_wal_records(wal_path)) == 1

    @pytest.mark.asyncio
    async def test_append_failure_releases_recorder_admission(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        buffer = AccessBuffer(AccessBufferConfig(wal_path=tmp_path / "access.wal"))

        async def fail_append(memory_id: str, collection_type: str) -> bool:
            raise AccessBufferWalCommitError(
                "synthetic pre-append failure",
                logically_committed=False,
            )

        monkeypatch.setattr(buffer, "_persist_to_wal", fail_append)
        with pytest.raises(AccessBufferWalCommitError):
            await buffer.record_access("append-failure", "long_term")

        async def enter_maintenance() -> None:
            async with buffer.maintenance_quiescence():
                pass

        await asyncio.wait_for(enter_maintenance(), timeout=1)

    @pytest.mark.asyncio
    async def test_complete_uncertain_append_requires_recovery_then_drain(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
        original_fsync_directory = buffer._fsync_directory
        calls = 0

        def fail_first_directory_fsync(directory: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise OSError("synthetic directory fsync failure")
            original_fsync_directory(directory)

        monkeypatch.setattr(
            buffer,
            "_fsync_directory",
            fail_first_directory_fsync,
        )
        with pytest.raises(AccessBufferWalCommitError):
            await buffer.record_access("uncertain-complete", "long_term")
        original = wal_path.read_bytes()
        assert len(read_wal_records(wal_path)) == 1

        async with buffer.maintenance_quiescence() as token:
            blocked = await buffer.drain_for_maintenance(
                token,
                long_term_collection=RecordingCollection(),
            )
        assert not blocked.verified_drained
        assert wal_path.read_bytes() == original
        with pytest.raises(AccessBufferQuiescenceError):
            await buffer.record_access("blocked-before-recovery", "long_term")

        assert await buffer.recover_from_wal() == 1
        with pytest.raises(AccessBufferQuiescenceError):
            await buffer.record_access("blocked-before-drain", "long_term")
        collection = RecordingCollection()
        async with buffer.maintenance_quiescence() as token:
            result = await buffer.drain_for_maintenance(
                token,
                long_term_collection=collection,
            )
        assert result.verified_drained
        assert collection.metadata_for("uncertain-complete")["hit_count"] == 1

    @pytest.mark.asyncio
    async def test_partial_uncertain_append_is_preserved(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))

        def partial_write(descriptor: int, payload: bytes) -> None:
            os.write(descriptor, payload[:20])
            raise OSError("synthetic partial write")

        monkeypatch.setattr(buffer, "_write_all", partial_write)
        with pytest.raises(AccessBufferWalCommitError):
            await buffer.record_access("uncertain-partial", "long_term")
        original = wal_path.read_bytes()
        assert original and not original.endswith(b"\n")

        async with buffer.maintenance_quiescence() as token:
            blocked = await buffer.drain_for_maintenance(
                token,
                long_term_collection=RecordingCollection(),
            )
        assert not blocked.verified_drained
        with pytest.raises(AccessBufferWalError):
            await buffer.recover_from_wal()
        with pytest.raises(AccessBufferQuiescenceError):
            await buffer.record_access("still-blocked", "long_term")
        assert wal_path.read_bytes() == original


class TestAccessBufferMaintenanceQuiescence:
    """Tests for lossless coordinator-owned access draining."""

    @pytest.mark.asyncio
    async def test_quiescence_blocks_new_recorders_until_release(
        self, tmp_path: Path
    ) -> None:
        buffer = AccessBuffer(AccessBufferConfig(wal_path=tmp_path / "access.wal"))

        async with buffer.maintenance_quiescence() as token:
            pending = asyncio.create_task(
                buffer.record_access("synthetic-pending", "long_term")
            )
            await asyncio.sleep(0)
            assert not pending.done()
            result = await buffer.drain_for_maintenance(
                token,
                short_term_collection=RecordingCollection(),
                long_term_collection=RecordingCollection(),
            )
            assert result.verified_drained

        await pending
        assert buffer.long_term_count == 1

    @pytest.mark.asyncio
    async def test_partial_failure_retains_exact_buffer_and_wal_remainder(
        self, tmp_path: Path
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
        await buffer.record_access("synthetic-short", "short_term")
        await buffer.record_access("synthetic-long-failure", "long_term")
        await buffer.record_access("synthetic-long-failure", "long_term")
        short_collection = RecordingCollection()
        long_collection = RecordingCollection(
            failing_ids={"synthetic-long-failure"}
        )

        async with buffer.maintenance_quiescence() as token:
            result = await buffer.drain_for_maintenance(
                token,
                short_term_collection=short_collection,
                long_term_collection=long_collection,
            )
            assert not result.verified_drained
            assert result.short_term_flushed == 1
            assert result.long_term_flushed == 0
            assert result.short_term_remaining == 0
            assert result.long_term_remaining == 1
            assert buffer.short_term_count == 0
            assert buffer.long_term_count == 1
            records = read_wal_records(wal_path)
            assert len(records) == 1
            assert records[0].schema_version == 2
            assert records[0].memory_id == "synthetic-long-failure"
            assert records[0].count == 2
            drain_id = records[0].drain_id

        long_collection.failing_ids.clear()
        async with buffer.maintenance_quiescence() as token:
            retry = await buffer.drain_for_maintenance(
                token,
                short_term_collection=short_collection,
                long_term_collection=long_collection,
            )
            assert retry.verified_drained
            assert buffer.total_count == 0
            assert not wal_path.exists()
            assert long_collection.metadata_for("synthetic-long-failure")[
                "hit_count"
            ] == 2
            assert drain_id is not None

    @pytest.mark.asyncio
    async def test_drain_rejects_stale_or_foreign_token(self, tmp_path: Path) -> None:
        buffer = AccessBuffer(AccessBufferConfig(wal_path=tmp_path / "access.wal"))
        fabricated = AccessBufferQuiescenceToken("other", "other")
        with pytest.raises(AccessBufferQuiescenceError):
            await buffer.drain_for_maintenance(fabricated)

        async with buffer.maintenance_quiescence() as token:
            assert (await buffer.drain_for_maintenance(token)).verified_drained
        with pytest.raises(AccessBufferQuiescenceError):
            await buffer.drain_for_maintenance(token)

    @pytest.mark.asyncio
    async def test_missing_collection_preserves_buffer_and_wal(
        self, tmp_path: Path
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
        await buffer.record_access("synthetic-memory", "short_term")

        async with buffer.maintenance_quiescence() as token:
            result = await buffer.drain_for_maintenance(token)
            assert not result.verified_drained
            assert result.short_term_remaining == 1
            assert buffer.total_accesses == 1
            records = read_wal_records(wal_path)
            assert len(records) == 1
            assert records[0].schema_version == 2
            assert records[0].memory_id == "synthetic-memory"
            assert records[0].count == 1

    @pytest.mark.asyncio
    async def test_clear_and_recovery_reject_active_quiescence(
        self, tmp_path: Path
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
        await buffer.record_access("quiesced", "long_term")

        async with buffer.maintenance_quiescence():
            with pytest.raises(AccessBufferQuiescenceError):
                buffer.clear()
            with pytest.raises(AccessBufferQuiescenceError):
                await buffer.recover_from_wal()

        buffer.clear()
        assert buffer.total_count == 0
        assert wal_path.exists()

    @pytest.mark.asyncio
    async def test_false_update_result_retains_exact_batch(
        self, tmp_path: Path
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
        await buffer.record_access("false-result", "long_term")
        collection = RecordingCollection(false_ids={"false-result"})

        async with buffer.maintenance_quiescence() as token:
            result = await buffer.drain_for_maintenance(
                token,
                long_term_collection=collection,
            )

        assert not result.verified_drained
        assert result.long_term_remaining == 1
        assert collection.metadata_for("false-result")["hit_count"] == 0
        records = read_wal_records(wal_path)
        assert len(records) == 1
        assert records[0].count == 1

    @pytest.mark.asyncio
    async def test_unknown_update_outcome_reconciles_marker(
        self, tmp_path: Path
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
        await buffer.record_access("unknown-outcome", "long_term")
        await buffer.record_access("unknown-outcome", "long_term")
        collection = RecordingCollection(
            raise_after_commit_ids={"unknown-outcome"}
        )

        async with buffer.maintenance_quiescence() as token:
            result = await buffer.drain_for_maintenance(
                token,
                long_term_collection=collection,
            )

        assert result.verified_drained
        assert collection.metadata_for("unknown-outcome")["hit_count"] == 2
        assert not wal_path.exists()

    @pytest.mark.asyncio
    async def test_cancel_after_collection_commit_retries_without_double_apply(
        self, tmp_path: Path
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
        await buffer.record_access("cancel-after-commit", "long_term")
        await buffer.record_access("cancel-after-commit", "long_term")
        collection = RecordingCollection(
            block_after_commit_ids={"cancel-after-commit"}
        )

        async with buffer.maintenance_quiescence() as token:
            drain = asyncio.create_task(
                buffer.drain_for_maintenance(
                    token,
                    long_term_collection=collection,
                )
            )
            await asyncio.wait_for(collection.committed.wait(), timeout=1)
            drain.cancel()
            with pytest.raises(asyncio.CancelledError):
                await drain
            assert buffer.total_accesses == 2
            records = read_wal_records(wal_path)
            assert len(records) == 1
            assert records[0].schema_version == 2
            assert records[0].count == 2

        with pytest.raises(AccessBufferQuiescenceError):
            await buffer.record_access("admission-blocked", "long_term")
        collection.block_after_commit_ids.clear()
        async with buffer.maintenance_quiescence() as token:
            retry = await buffer.drain_for_maintenance(
                token,
                long_term_collection=collection,
            )

        assert retry.verified_drained
        assert collection.metadata_for("cancel-after-commit")["hit_count"] == 2

    @pytest.mark.asyncio
    async def test_recovery_preserves_v2_batch_identity(self, tmp_path: Path) -> None:
        wal_path = tmp_path / "access.wal"
        record = AccessWalRecord(
            schema_version=2,
            memory_id="pending-v2",
            collection_type=AccessCollectionType.LONG_TERM,
            count=3,
            drain_id="a" * 32,
        )
        wal_path.write_text(record.model_dump_json() + "\n")
        os.chmod(wal_path, 0o600)
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))

        assert await buffer.recover_from_wal() == 3
        with pytest.raises(AccessBufferQuiescenceError):
            await buffer.record_access("cannot-coalesce", "long_term")
        async with buffer.maintenance_quiescence() as token:
            result = await buffer.drain_for_maintenance(token)

        assert not result.verified_drained
        recovered_record = read_wal_records(wal_path)
        assert recovered_record == [record]

    @pytest.mark.asyncio
    async def test_replace_failure_retains_full_buffer_for_marker_retry(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
        await buffer.record_access("applied-before-replace-failure", "long_term")
        await buffer.record_access("collection-failure", "long_term")
        collection = RecordingCollection(false_ids={"collection-failure"})
        original_replace = os.replace
        replace_calls = 0

        def fail_second_replace(source: Path, target: Path) -> None:
            nonlocal replace_calls
            replace_calls += 1
            if replace_calls == 2:
                raise OSError("synthetic replace failure")
            original_replace(source, target)

        monkeypatch.setattr(os, "replace", fail_second_replace)
        async with buffer.maintenance_quiescence() as token:
            result = await buffer.drain_for_maintenance(
                token,
                long_term_collection=collection,
            )

        assert not result.wal_verified
        assert buffer.total_accesses == 2
        assert len(read_wal_records(wal_path)) == 2
        assert collection.metadata_for("applied-before-replace-failure")[
            "hit_count"
        ] == 1
        with pytest.raises(AccessBufferQuiescenceError):
            await buffer.record_access("blocked-after-replace", "long_term")

        monkeypatch.setattr(os, "replace", original_replace)
        collection.false_ids.clear()
        async with buffer.maintenance_quiescence() as token:
            retry = await buffer.drain_for_maintenance(
                token,
                long_term_collection=collection,
            )
        assert retry.verified_drained
        assert collection.metadata_for("applied-before-replace-failure")[
            "hit_count"
        ] == 1
        assert collection.metadata_for("collection-failure")["hit_count"] == 1

    @pytest.mark.asyncio
    async def test_post_replace_fsync_failure_commits_only_exact_remainder(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        wal_path = tmp_path / "access.wal"
        buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
        await buffer.record_access("applied-before-fsync-failure", "long_term")
        await buffer.record_access("fsync-remainder", "long_term")
        collection = RecordingCollection(false_ids={"fsync-remainder"})
        original_fsync_directory = buffer._fsync_directory
        fsync_calls = 0

        def fail_second_fsync(directory: Path) -> None:
            nonlocal fsync_calls
            fsync_calls += 1
            if fsync_calls == 2:
                raise OSError("synthetic fsync failure")
            original_fsync_directory(directory)

        monkeypatch.setattr(buffer, "_fsync_directory", fail_second_fsync)
        async with buffer.maintenance_quiescence() as token:
            result = await buffer.drain_for_maintenance(
                token,
                long_term_collection=collection,
            )

        assert not result.wal_verified
        assert buffer.total_accesses == 1
        records = read_wal_records(wal_path)
        assert len(records) == 1
        assert records[0].memory_id == "fsync-remainder"
        assert collection.metadata_for("applied-before-fsync-failure")[
            "hit_count"
        ] == 1

        monkeypatch.setattr(buffer, "_fsync_directory", original_fsync_directory)
        collection.false_ids.clear()
        async with buffer.maintenance_quiescence() as token:
            retry = await buffer.drain_for_maintenance(
                token,
                long_term_collection=collection,
            )
        assert retry.verified_drained
        assert collection.metadata_for("applied-before-fsync-failure")[
            "hit_count"
        ] == 1
        assert collection.metadata_for("fsync-remainder")["hit_count"] == 1
