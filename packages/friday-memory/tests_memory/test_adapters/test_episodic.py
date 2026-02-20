"""
Tests for InMemoryEpisodicStore adapter.

Tests cover:
- Adding and retrieving turns
- Most-recent retrieval with limit
- Compacted turn filtering
- Consolidation tracking
- Compaction tracking
- History rewind (time-travel)
"""

import uuid
from datetime import datetime

import pytest
from friday_memory import InMemoryEpisodicStore, InteractionTurn


def create_turn(
    user_msg: str = "Hello", assistant_msg: str = "Hi", session_id: str = "test_session"
) -> InteractionTurn:
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
    async def test_get_turns_with_limit_returns_most_recent(
        self,
        episodic_store: InMemoryEpisodicStore,
    ):
        """Test that get_turns with limit returns the most recent turns."""
        for i in range(10):
            turn = create_turn(f"Message {i}")
            await episodic_store.add_turn("session_1", turn)

        turns = await episodic_store.get_turns("session_1", limit=5)
        assert len(turns) == 5
        # Should be the MOST RECENT 5 turns (Message 5-9)
        assert turns[0].user_message == "Message 5"
        assert turns[4].user_message == "Message 9"

    @pytest.mark.asyncio
    async def test_get_turns_with_offset(
        self,
        episodic_store: InMemoryEpisodicStore,
    ):
        """Test retrieving turns with offset skips most recent."""
        for i in range(10):
            turn = create_turn(f"Message {i}")
            await episodic_store.add_turn("session_1", turn)

        # offset=5 skips the 5 most recent, limit=3 gets 3 before that
        turns = await episodic_store.get_turns("session_1", limit=3, offset=5)
        assert len(turns) == 3
        # Turns 2, 3, 4 (skipping 5-9, taking 3 before that)
        assert turns[0].user_message == "Message 2"
        assert turns[2].user_message == "Message 4"

    @pytest.mark.asyncio
    async def test_get_turns_excludes_compacted(
        self,
        episodic_store: InMemoryEpisodicStore,
    ):
        """Test that get_turns filters out compacted turns."""
        turn_ids = []
        for i in range(10):
            turn = create_turn(f"Message {i}")
            await episodic_store.add_turn("session_1", turn)
            turn_ids.append(turn.id)

        # Compact the first 5 turns
        await episodic_store.mark_compacted(turn_ids[:5])

        # get_turns should only return the 5 non-compacted turns
        turns = await episodic_store.get_turns("session_1", limit=10)
        assert len(turns) == 5
        assert turns[0].user_message == "Message 5"
        assert turns[4].user_message == "Message 9"

    @pytest.mark.asyncio
    async def test_get_turns_excludes_compacted_with_limit(
        self,
        episodic_store: InMemoryEpisodicStore,
    ):
        """Test limit applies after compacted filtering."""
        turn_ids = []
        for i in range(10):
            turn = create_turn(f"Message {i}")
            await episodic_store.add_turn("session_1", turn)
            turn_ids.append(turn.id)

        # Compact first 5
        await episodic_store.mark_compacted(turn_ids[:5])

        # Request limit=3 — should get last 3 of the 5 active
        turns = await episodic_store.get_turns("session_1", limit=3)
        assert len(turns) == 3
        assert turns[0].user_message == "Message 7"
        assert turns[2].user_message == "Message 9"

    @pytest.mark.asyncio
    async def test_get_unconsolidated_turns(
        self, episodic_store: InMemoryEpisodicStore
    ):
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
    async def test_mark_compacted(
        self,
        episodic_store: InMemoryEpisodicStore,
    ):
        """Test marking turns as compacted."""
        turn_ids = []
        for i in range(5):
            turn = create_turn(f"Message {i}")
            await episodic_store.add_turn("session_1", turn)
            turn_ids.append(turn.id)

        result = await episodic_store.mark_compacted(turn_ids[:3])
        assert result is True

        # Compacted turns should be excluded from get_turns
        turns = await episodic_store.get_turns("session_1", limit=10)
        assert len(turns) == 2
        assert turns[0].user_message == "Message 3"
        assert turns[1].user_message == "Message 4"

    @pytest.mark.asyncio
    async def test_compacted_independent_of_consolidated(
        self,
        episodic_store: InMemoryEpisodicStore,
    ):
        """Test that compacted and consolidated are independent flags."""
        turn_ids = []
        for i in range(5):
            turn = create_turn(f"Message {i}")
            await episodic_store.add_turn("session_1", turn)
            turn_ids.append(turn.id)

        # Consolidate all, compact first 3
        await episodic_store.mark_consolidated(turn_ids)
        await episodic_store.mark_compacted(turn_ids[:3])

        # get_turns should exclude compacted (returns 2)
        turns = await episodic_store.get_turns("session_1", limit=10)
        assert len(turns) == 2

        # get_unconsolidated should return 0 (all consolidated)
        unconsolidated = await episodic_store.get_unconsolidated_turns("session_1")
        assert len(unconsolidated) == 0

    @pytest.mark.asyncio
    async def test_compacted_field_defaults_false(self):
        """Test that InteractionTurn.compacted defaults to False."""
        turn = create_turn()
        assert turn.compacted is False

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
    async def test_rewind_history_invalid_turn(
        self, episodic_store: InMemoryEpisodicStore
    ):
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
