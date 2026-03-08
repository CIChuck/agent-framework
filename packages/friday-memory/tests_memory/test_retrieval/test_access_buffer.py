# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
# mypy: disallow-untyped-defs=False
"""Tests for AccessBuffer."""

import asyncio
import tempfile
from pathlib import Path

import pytest
from friday_memory.retrieval.access_buffer import (
    AccessBuffer,
    AccessBufferConfig,
    FlushResult,
)


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

        # Give async write time to complete
        await asyncio.sleep(0.1)

        # Check WAL file exists and has content
        assert temp_wal_path.exists()
        content = temp_wal_path.read_text()
        assert "mem1" in content
        assert "long_term" in content

    @pytest.mark.asyncio
    async def test_recover_from_wal(self, wal_buffer, temp_wal_path) -> None:
        """Test recovering access events from WAL."""
        # Write some events to WAL
        await wal_buffer.record_access("mem1", "short_term")
        await wal_buffer.record_access("mem2", "long_term")
        await asyncio.sleep(0.1)  # Let async writes complete

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
    async def test_recover_clears_wal(self, wal_buffer, temp_wal_path) -> None:
        """Test that WAL is cleared after successful recovery."""
        await wal_buffer.record_access("mem1", "long_term")
        await asyncio.sleep(0.1)

        wal_buffer.clear()
        await wal_buffer.recover_from_wal()

        # WAL should be cleared after recovery
        assert not temp_wal_path.exists()


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
