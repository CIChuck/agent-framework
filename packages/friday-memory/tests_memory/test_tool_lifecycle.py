# mypy: ignore-errors
# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
# mypy: disallow-untyped-defs=False
"""
Tests for tool content lifecycle management.

Tests cover:
- Tracking outputs above threshold
- Ignoring small outputs
- Reference marking updates last_referenced_turn_id
- Decay triggers after gap threshold
- Summarization integration
- Per-tool policy overrides
- ToolResult lifecycle fields

Ref: docs/build-plan/to-do/tool-content-lifecycle-build-plan.md
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from friday_memory.lifecycle.tool_content import (
    ToolContentConfig,
    ToolContentManager,
    TrackedToolOutput,
)
from friday_memory.models.session import ToolResult


class TestTrackedToolOutput:
    """Tests for TrackedToolOutput dataclass."""

    def test_create_tracked_output(self) -> None:
        """Test creating a tracked tool output."""
        output = TrackedToolOutput(
            tool_call_id="tc_1",
            tool_name="read_file",
            content="File contents here",
            token_count=100,
            turn_id="turn_1",
        )
        assert output.tool_call_id == "tc_1"
        assert output.tool_name == "read_file"
        assert output.token_count == 100
        assert output.is_decayed is False
        assert output.summary is None
        assert output.referencing_turns == []

    def test_default_created_at(self) -> None:
        """Test that created_at has a default value."""
        output = TrackedToolOutput(
            tool_call_id="tc_1",
            tool_name="test",
            content="content",
            token_count=100,
            turn_id="turn_1",
        )
        assert output.created_at is not None


class TestToolContentConfig:
    """Tests for ToolContentConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ToolContentConfig()
        assert config.enabled is True
        assert config.min_tokens_for_tracking == 500
        assert config.decay_threshold_turns == 3
        assert config.tool_policies == {}

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = ToolContentConfig(
            enabled=False,
            min_tokens_for_tracking=1000,
            decay_threshold_turns=5,
            tool_policies={"read_file": 2, "web_search": 1},
        )
        assert config.enabled is False
        assert config.min_tokens_for_tracking == 1000
        assert config.decay_threshold_turns == 5
        assert config.tool_policies["read_file"] == 2


class TestToolContentManagerTracking:
    """Tests for ToolContentManager tracking functionality."""

    def test_track_output_above_threshold(self) -> None:
        """Test tracking output above minimum token threshold."""
        config = ToolContentConfig(min_tokens_for_tracking=100)
        manager = ToolContentManager(config)

        # Large content (400 chars = ~100 tokens with 4 chars/token estimate)
        content = "x" * 600
        result = manager.track_output("tc_1", "read_file", content, "turn_1")

        assert result is True
        assert manager.tracked_count == 1
        assert manager.get_output("tc_1") is not None

    def test_ignore_small_output(self) -> None:
        """Test that small outputs are not tracked."""
        config = ToolContentConfig(min_tokens_for_tracking=500)
        manager = ToolContentManager(config)

        # Small content (100 chars = ~25 tokens)
        content = "x" * 100
        result = manager.track_output("tc_1", "read_file", content, "turn_1")

        assert result is False
        assert manager.tracked_count == 0
        assert manager.get_output("tc_1") is None

    def test_track_output_with_explicit_token_count(self) -> None:
        """Test tracking with explicit token count."""
        config = ToolContentConfig(min_tokens_for_tracking=500)
        manager = ToolContentManager(config)

        # Small content but explicit token count is high
        result = manager.track_output(
            "tc_1", "read_file", "small", "turn_1", token_count=1000
        )

        assert result is True
        assert manager.tracked_count == 1

    def test_tracking_disabled(self) -> None:
        """Test that tracking doesn't occur when disabled."""
        config = ToolContentConfig(enabled=False)
        manager = ToolContentManager(config)

        content = "x" * 10000  # Very large
        result = manager.track_output("tc_1", "read_file", content, "turn_1")

        assert result is False
        assert manager.tracked_count == 0

    def test_track_multiple_outputs(self) -> None:
        """Test tracking multiple tool outputs."""
        config = ToolContentConfig(min_tokens_for_tracking=100)
        manager = ToolContentManager(config)

        content = "x" * 600
        manager.track_output("tc_1", "read_file", content, "turn_1")
        manager.track_output("tc_2", "web_search", content, "turn_1")
        manager.track_output("tc_3", "read_file", content, "turn_2")

        assert manager.tracked_count == 3
        assert manager.active_count == 3


class TestToolContentManagerReferencing:
    """Tests for reference tracking functionality."""

    def test_mark_referenced_updates_turn(self) -> None:
        """Test that marking referenced updates last_referenced_turn_id."""
        config = ToolContentConfig(min_tokens_for_tracking=100)
        manager = ToolContentManager(config)

        content = "x" * 600
        manager.track_output("tc_1", "read_file", content, "turn_1")

        manager.mark_referenced("tc_1", "turn_3")

        output = manager.get_output("tc_1")
        assert output.last_referenced_turn_id == "turn_3"
        assert "turn_3" in output.referencing_turns

    def test_mark_referenced_appends_to_history(self) -> None:
        """Test that multiple references are tracked."""
        config = ToolContentConfig(min_tokens_for_tracking=100)
        manager = ToolContentManager(config)

        content = "x" * 600
        manager.track_output("tc_1", "read_file", content, "turn_1")

        manager.mark_referenced("tc_1", "turn_2")
        manager.mark_referenced("tc_1", "turn_3")
        manager.mark_referenced("tc_1", "turn_5")

        output = manager.get_output("tc_1")
        assert len(output.referencing_turns) == 4  # Including initial turn_1
        assert output.referencing_turns == ["turn_1", "turn_2", "turn_3", "turn_5"]

    def test_mark_referenced_unknown_id(self) -> None:
        """Test marking unknown ID returns False."""
        manager = ToolContentManager()
        result = manager.mark_referenced("unknown", "turn_1")
        assert result is False


class TestToolContentManagerDecay:
    """Tests for decay functionality."""

    @pytest.mark.asyncio
    async def test_decay_triggers_after_threshold(self) -> None:
        """Test that decay triggers after gap exceeds threshold."""
        config = ToolContentConfig(
            min_tokens_for_tracking=100,
            decay_threshold_turns=3,
        )
        # Mock LLM for summarization
        mock_llm = AsyncMock()
        mock_llm.chat_completion = AsyncMock(
            return_value=MagicMock(content="This is a summary of the file contents.")
        )
        manager = ToolContentManager(config, mock_llm)

        content = "x" * 600
        manager.track_output("tc_1", "read_file", content, "1")

        # Check decay at turn 2 (gap=1, threshold=3) - no decay
        decayed = await manager.check_and_decay(2)
        assert decayed == []

        # Check decay at turn 5 (gap=4, threshold=3) - should decay
        decayed = await manager.check_and_decay(5)
        assert "tc_1" in decayed

        output = manager.get_output("tc_1")
        assert output.is_decayed is True
        assert output.summary is not None

    @pytest.mark.asyncio
    async def test_decay_respects_references(self) -> None:
        """Test that references reset the decay timer."""
        config = ToolContentConfig(
            min_tokens_for_tracking=100,
            decay_threshold_turns=3,
        )
        mock_llm = AsyncMock()
        manager = ToolContentManager(config, mock_llm)

        content = "x" * 600
        manager.track_output("tc_1", "read_file", content, "1")

        # Reference at turn 4 (resets timer)
        manager.mark_referenced("tc_1", "4")

        # Check decay at turn 6 (gap from turn 4 = 2, threshold=3) - no decay
        decayed = await manager.check_and_decay(6)
        assert decayed == []

        # Check decay at turn 8 (gap from turn 4 = 4, threshold=3) - should decay
        mock_llm.chat_completion = AsyncMock(return_value=MagicMock(content="Summary"))
        decayed = await manager.check_and_decay(8)
        assert "tc_1" in decayed

    @pytest.mark.asyncio
    async def test_decay_skips_already_decayed(self) -> None:
        """Test that already decayed outputs are skipped."""
        config = ToolContentConfig(
            min_tokens_for_tracking=100,
            decay_threshold_turns=3,
        )
        mock_llm = AsyncMock()
        mock_llm.chat_completion = AsyncMock(return_value=MagicMock(content="Summary"))
        manager = ToolContentManager(config, mock_llm)

        content = "x" * 600
        manager.track_output("tc_1", "read_file", content, "1")

        # First decay
        await manager.check_and_decay(10)
        assert manager.get_output("tc_1").is_decayed is True

        # Second check should not re-decay
        mock_llm.chat_completion.reset_mock()
        decayed = await manager.check_and_decay(20)
        assert decayed == []
        mock_llm.chat_completion.assert_not_called()

    @pytest.mark.asyncio
    async def test_decay_without_llm_uses_truncation(self) -> None:
        """Test decay fallback to truncation when no LLM available."""
        config = ToolContentConfig(
            min_tokens_for_tracking=100,
            decay_threshold_turns=2,
        )
        manager = ToolContentManager(config)  # No LLM

        content = "A" * 1000  # Large content
        manager.track_output("tc_1", "read_file", content, "1", token_count=500)

        # Should fallback to truncation
        decayed = await manager.check_and_decay(10)
        assert "tc_1" in decayed

        output = manager.get_output("tc_1")
        assert output.is_decayed is True
        assert "truncated" in output.summary
        assert "500 tokens" in output.summary


class TestToolContentManagerPolicies:
    """Tests for per-tool policy overrides."""

    @pytest.mark.asyncio
    async def test_per_tool_policy_override(self) -> None:
        """Test that per-tool decay thresholds are respected."""
        config = ToolContentConfig(
            min_tokens_for_tracking=100,
            decay_threshold_turns=5,  # Default
            tool_policies={
                "read_file": 2,  # Faster decay for files
                "web_search": 1,  # Even faster for web
            },
        )
        mock_llm = AsyncMock()
        mock_llm.chat_completion = AsyncMock(return_value=MagicMock(content="Summary"))
        manager = ToolContentManager(config, mock_llm)

        content = "x" * 600

        # Track different tool types
        manager.track_output("tc_file", "read_file", content, "1")
        manager.track_output("tc_web", "web_search", content, "1")
        manager.track_output("tc_other", "other_tool", content, "1")

        # At turn 3: web_search should decay (gap=2 > threshold=1)
        #           read_file should not decay yet (gap=2, threshold=2)
        #           other_tool should not decay (gap=2, threshold=5)
        decayed = await manager.check_and_decay(3)
        assert "tc_web" in decayed
        assert "tc_file" not in decayed
        assert "tc_other" not in decayed

        # At turn 4: read_file should decay (gap=3 > threshold=2)
        decayed = await manager.check_and_decay(4)
        assert "tc_file" in decayed
        assert "tc_other" not in decayed


class TestToolContentManagerStats:
    """Tests for statistics and utility methods."""

    def test_get_stats(self) -> None:
        """Test statistics gathering."""
        config = ToolContentConfig(min_tokens_for_tracking=100)
        manager = ToolContentManager(config)

        content = "x" * 600
        manager.track_output("tc_1", "read_file", content, "turn_1", token_count=500)
        manager.track_output("tc_2", "web_search", content, "turn_1", token_count=300)

        stats = manager.get_stats()
        assert stats["total_tracked"] == 2
        assert stats["active_count"] == 2
        assert stats["decayed_count"] == 0
        assert stats["active_tokens"] == 800
        assert stats["decayed_tokens"] == 0

    def test_get_active_and_decayed_outputs(self) -> None:
        """Test getting active and decayed outputs."""
        config = ToolContentConfig(min_tokens_for_tracking=100)
        manager = ToolContentManager(config)

        content = "x" * 600
        manager.track_output("tc_1", "read_file", content, "turn_1")
        manager.track_output("tc_2", "web_search", content, "turn_1")

        # Manually decay one
        manager._tracked["tc_1"].is_decayed = True
        manager._tracked["tc_1"].summary = "Summary"

        active = manager.get_active_outputs()
        decayed = manager.get_decayed_outputs()

        assert len(active) == 1
        assert active[0].tool_call_id == "tc_2"
        assert len(decayed) == 1
        assert decayed[0].tool_call_id == "tc_1"

    def test_clear(self) -> None:
        """Test clearing all tracked outputs."""
        config = ToolContentConfig(min_tokens_for_tracking=100)
        manager = ToolContentManager(config)

        content = "x" * 600
        manager.track_output("tc_1", "read_file", content, "turn_1")
        manager.track_output("tc_2", "web_search", content, "turn_1")

        count = manager.clear()

        assert count == 2
        assert manager.tracked_count == 0
        assert manager.active_count == 0


class TestToolResultLifecycleFields:
    """Tests for ToolResult lifecycle fields."""

    def test_tool_result_default_lifecycle_fields(self) -> None:
        """Test ToolResult default lifecycle field values."""
        result = ToolResult(
            tool_call_id="tc_1",
            output="Result data",
        )
        assert result.turn_id is None
        assert result.last_referenced_turn_id is None
        assert result.referencing_turns == []
        assert result.is_decayed is False
        assert result.summary is None
        assert result.original_token_count is None

    def test_tool_result_with_lifecycle_fields(self) -> None:
        """Test ToolResult with lifecycle fields populated."""
        result = ToolResult(
            tool_call_id="tc_1",
            output="Result data",
            turn_id="turn_5",
            last_referenced_turn_id="turn_8",
            referencing_turns=["turn_5", "turn_6", "turn_8"],
            is_decayed=True,
            summary="This is a summary of the result.",
            original_token_count=1500,
        )
        assert result.turn_id == "turn_5"
        assert result.last_referenced_turn_id == "turn_8"
        assert len(result.referencing_turns) == 3
        assert result.is_decayed is True
        assert result.summary == "This is a summary of the result."
        assert result.original_token_count == 1500

    def test_tool_result_serialization(self) -> None:
        """Test ToolResult serialization includes lifecycle fields."""
        result = ToolResult(
            tool_call_id="tc_1",
            output="Result data",
            is_decayed=True,
            summary="Summary",
        )
        data = result.model_dump()

        assert "is_decayed" in data
        assert data["is_decayed"] is True
        assert "summary" in data
        assert data["summary"] == "Summary"
        assert "referencing_turns" in data
