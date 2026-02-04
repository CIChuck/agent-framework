"""
Tests for InMemoryEpisodicStore adapter.

Tests cover:
- Adding and retrieving turns
- Pagination with limit/offset
- Consolidation tracking
- History rewind (time-travel)
"""

import uuid
from datetime import datetime

import pytest

from friday_memory import InMemoryEpisodicStore, InteractionTurn


def create_turn(user_msg: str = "Hello", assistant_msg: str = "Hi", session_id: str = "test_session") -> InteractionTurn:
    """Helper to create test turns."""
    return InteractionTurn(
        id=str(uuid.uuid4()),
        session_id=session_id,
        timestamp=datetime.now(),
        user_message=user_msg,
        assistant_message=assistant_msg,
        consolidated=False,
    )


class TestInMemoryEpisodicStore:
    """Tests for InMemoryEpisodicStore."""

    @pytest.mark.asyncio
    async def test_add_turn(self, episodic_store: InMemoryEpisodicStore):
        """Test adding a turn to a session."""
        turn = create_turn()
        result = await episodic_store.add_turn("session_1", turn)

        assert result is True
        count = await episodic_store.get_turn_count("session_1")
        assert count == 1

    @pytest.mark.asyncio
    async def test_get_turns(self, episodic_store: InMemoryEpisodicStore):
        """Test retrieving turns from a session."""
        # Add multiple turns
        for i in range(5):
            turn = create_turn(f"Message {i}", f"Response {i}")
            await episodic_store.add_turn("session_1", turn)

        turns = await episodic_store.get_turns("session_1")
        assert len(turns) == 5
        assert turns[0].user_message == "Message 0"
        assert turns[4].user_message == "Message 4"

    @pytest.mark.asyncio
    async def test_get_turns_with_limit(self, episodic_store: InMemoryEpisodicStore):
        """Test retrieving turns with limit."""
        for i in range(10):
            turn = create_turn(f"Message {i}")
            await episodic_store.add_turn("session_1", turn)

        turns = await episodic_store.get_turns("session_1", limit=5)
        assert len(turns) == 5

    @pytest.mark.asyncio
    async def test_get_turns_with_offset(self, episodic_store: InMemoryEpisodicStore):
        """Test retrieving turns with offset for pagination."""
        for i in range(10):
            turn = create_turn(f"Message {i}")
            await episodic_store.add_turn("session_1", turn)

        turns = await episodic_store.get_turns("session_1", limit=3, offset=5)
        assert len(turns) == 3
        assert turns[0].user_message == "Message 5"

    @pytest.mark.asyncio
    async def test_get_unconsolidated_turns(self, episodic_store: InMemoryEpisodicStore):
        """Test getting turns that haven't been consolidated."""
        # Add some turns
        turn_ids = []
        for i in range(5):
            turn = create_turn(f"Message {i}")
            await episodic_store.add_turn("session_1", turn)
            turn_ids.append(turn.id)

        # All should be unconsolidated initially
        unconsolidated = await episodic_store.get_unconsolidated_turns("session_1")
        assert len(unconsolidated) == 5

    @pytest.mark.asyncio
    async def test_mark_consolidated(self, episodic_store: InMemoryEpisodicStore):
        """Test marking turns as consolidated."""
        # Add turns
        turn_ids = []
        for i in range(5):
            turn = create_turn(f"Message {i}")
            await episodic_store.add_turn("session_1", turn)
            turn_ids.append(turn.id)

        # Mark first 3 as consolidated
        await episodic_store.mark_consolidated(turn_ids[:3])

        # Should only have 2 unconsolidated
        unconsolidated = await episodic_store.get_unconsolidated_turns("session_1")
        assert len(unconsolidated) == 2

    @pytest.mark.asyncio
    async def test_rewind_history(self, episodic_store: InMemoryEpisodicStore):
        """Test rewinding history to a specific turn."""
        # Add turns and track IDs
        turn_ids = []
        for i in range(5):
            turn = create_turn(f"Message {i}")
            await episodic_store.add_turn("session_1", turn)
            turn_ids.append(turn.id)

        # Rewind to turn 2 (index 2, keep turns 0, 1, 2)
        result = await episodic_store.rewind_history("session_1", turn_ids[2])
        assert result is True

        # Should only have 3 turns now
        count = await episodic_store.get_turn_count("session_1")
        assert count == 3

    @pytest.mark.asyncio
    async def test_rewind_history_invalid_turn(self, episodic_store: InMemoryEpisodicStore):
        """Test rewinding to non-existent turn returns False."""
        turn = create_turn()
        await episodic_store.add_turn("session_1", turn)

        result = await episodic_store.rewind_history("session_1", "nonexistent_id")
        assert result is False

    @pytest.mark.asyncio
    async def test_multiple_sessions(self, episodic_store: InMemoryEpisodicStore):
        """Test managing multiple sessions independently."""
        # Add turns to different sessions
        await episodic_store.add_turn("session_1", create_turn("S1 M1"))
        await episodic_store.add_turn("session_1", create_turn("S1 M2"))
        await episodic_store.add_turn("session_2", create_turn("S2 M1"))

        # Verify isolation
        s1_count = await episodic_store.get_turn_count("session_1")
        s2_count = await episodic_store.get_turn_count("session_2")

        assert s1_count == 2
        assert s2_count == 1

    @pytest.mark.asyncio
    async def test_get_session_ids(self, episodic_store: InMemoryEpisodicStore):
        """Test getting all session IDs."""
        await episodic_store.add_turn("session_a", create_turn())
        await episodic_store.add_turn("session_b", create_turn())
        await episodic_store.add_turn("session_c", create_turn())

        session_ids = await episodic_store.get_session_ids()
        assert len(session_ids) == 3
        assert "session_a" in session_ids
        assert "session_b" in session_ids
        assert "session_c" in session_ids

    @pytest.mark.asyncio
    async def test_clear_session(self, episodic_store: InMemoryEpisodicStore):
        """Test clearing a session."""
        await episodic_store.add_turn("session_1", create_turn())
        await episodic_store.add_turn("session_1", create_turn())

        result = await episodic_store.clear_session("session_1")
        assert result is True

        count = await episodic_store.get_turn_count("session_1")
        assert count == 0
