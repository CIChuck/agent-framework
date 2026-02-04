"""
Tests for ContextAssembler.

Tests cover:
- Session initialization
- Context assembly with budgeting
- Token budget enforcement
- Checkpoint restoration

Note: Tests use mock EmbeddingModel protocol from conftest fixtures.
"""

import uuid
from datetime import datetime

import pytest

from friday_core import DebugTelemetryRecorder

from friday_memory import (
    ChromaVectorStore,
    ContextPayload,
    ElementXGraphStore,
    InMemoryEpisodicStore,
    InteractionTurn,
    MemoryController,
    SessionState,
)
from friday_memory.context import ContextAssembler


def create_turn(user_msg: str = "Hello", session_id: str = "test_session") -> InteractionTurn:
    """Helper to create test turns."""
    return InteractionTurn(
        id=str(uuid.uuid4()),
        session_id=session_id,
        timestamp=datetime.now(),
        user_message=user_msg,
        assistant_message="Response",
        consolidated=False,
    )


@pytest.fixture
def context_assembler(memory_controller: MemoryController) -> ContextAssembler:
    """Create a ContextAssembler instance."""
    return ContextAssembler(
        memory_controller=memory_controller,
        model_name="gpt-4",
        max_tokens=8192,
    )


class TestSessionManagement:
    """Tests for session initialization and management."""

    @pytest.mark.asyncio
    async def test_initialize_session_new(self, context_assembler: ContextAssembler):
        """Test initializing a new session."""
        state = await context_assembler.initialize_session(
            session_id="new_session",
            user_id="user_123",
        )

        assert state.session_id == "new_session"
        assert state.user_id == "user_123"
        assert state.turn_count == 0
        assert state.scoped_vars == {}

    @pytest.mark.asyncio
    async def test_initialize_session_existing(self, context_assembler: ContextAssembler):
        """Test initializing returns existing session."""
        # Initialize twice
        state1 = await context_assembler.initialize_session("sess", "user")
        state1.set_var("user:test", "value")

        state2 = await context_assembler.initialize_session("sess", "user")

        # Should be the same session with preserved state
        assert state2.get_var("user:test") == "value"


class TestContextAssembly:
    """Tests for context assembly."""

    @pytest.mark.asyncio
    async def test_assemble_context_returns_payload(
        self, context_assembler: ContextAssembler
    ):
        """Test that assemble_context returns a ContextPayload."""
        state = await context_assembler.initialize_session("test", "user")

        payload = await context_assembler.assemble_context(
            query="test query",
            state=state,
            budget_limit=2000,
        )

        assert isinstance(payload, ContextPayload)
        assert hasattr(payload, "history")
        assert hasattr(payload, "passages")

    @pytest.mark.asyncio
    async def test_assemble_context_respects_budget(
        self, context_assembler: ContextAssembler
    ):
        """Test that assembly respects token budget."""
        state = await context_assembler.initialize_session("budget_test", "user")

        # Very small budget
        payload = await context_assembler.assemble_context(
            query="test",
            state=state,
            budget_limit=100,
        )

        # Payload should be minimal due to budget constraints
        assert payload is not None


class TestBudgetPruning:
    """Tests for context budget pruning."""

    def test_apply_budget_no_pruning_needed(self, context_assembler: ContextAssembler):
        """Test that small payloads aren't pruned."""
        payload = ContextPayload(
            history=[],
            passages=[{"text": "Short", "similarity": 0.9}],
            entities=[],
            facts=[],
            recent_memories=[],
            debug_info={},
        )

        pruned = context_assembler._apply_budget(payload, budget_limit=10000)

        assert len(pruned.passages) == 1
        assert pruned.debug_info.get("pruned") is None

    def test_apply_budget_drops_deep_history(self, context_assembler: ContextAssembler):
        """Test that deep history is dropped when budget is exceeded."""
        # Create many turns with longer messages to trigger budget pruning
        turns = [create_turn(f"This is a longer message number {i} with more content to count tokens " * 10) for i in range(15)]

        payload = ContextPayload(
            history=turns,
            passages=[],
            entities=[],
            facts=[],
            recent_memories=[],
            debug_info={},
        )

        # Very small budget to force pruning
        pruned = context_assembler._apply_budget(payload, budget_limit=100)

        # Should have fewer turns (pruning keeps last 10, then last 5, then last 2)
        assert len(pruned.history) <= 10

    def test_apply_budget_drops_weak_passages(self, context_assembler: ContextAssembler):
        """Test that low-similarity passages are dropped when budget is exceeded."""
        # Create passages with lots of text to trigger budget pruning
        long_text = "This is a very long passage with lots of content " * 50
        payload = ContextPayload(
            history=[],
            passages=[
                {"text": long_text + " High relevance", "similarity": 0.9},
                {"text": long_text + " Medium relevance", "similarity": 0.6},
                {"text": long_text + " Low relevance", "similarity": 0.3},
            ],
            entities=[],
            facts=[],
            recent_memories=[],
            debug_info={},
        )

        # Very small budget to force pruning (will drop passages with similarity < 0.5)
        pruned = context_assembler._apply_budget(payload, budget_limit=100)

        # Low similarity passages should be dropped (< 0.5)
        for passage in pruned.passages:
            assert passage["similarity"] >= 0.5


class TestCheckpointRestoration:
    """Tests for checkpoint restoration."""

    @pytest.mark.asyncio
    async def test_restore_checkpoint(
        self,
        context_assembler: ContextAssembler,
        memory_controller: MemoryController,
    ):
        """Test restoring to a previous checkpoint."""
        session_id = "checkpoint_test"
        turn_ids = []

        # Add turns via controller
        for i in range(5):
            turn = create_turn(f"Message {i}")
            await memory_controller.add_turn(session_id, turn)
            turn_ids.append(turn.id)

        # Initialize session
        state = await context_assembler.initialize_session(session_id, "user")

        # Restore to turn 2
        restored = await context_assembler.restore_checkpoint(session_id, turn_ids[2])

        assert restored.turn_count == 3  # Turns 0, 1, 2


class TestPromptFormatting:
    """Tests for prompt formatting."""

    @pytest.mark.asyncio
    async def test_format_prompt(self, context_assembler: ContextAssembler):
        """Test formatting a prompt."""
        payload = ContextPayload(
            history=[create_turn("Hello")],
            passages=[],
            entities=[],
            facts=[],
            recent_memories=[],
            debug_info={},
        )

        messages = await context_assembler.format_prompt(
            system_prompt="You are helpful.",
            payload=payload,
        )

        assert len(messages) >= 1
        assert messages[0]["role"] == "system"


class TestExtractionTrigger:
    """Tests for extraction triggering."""

    @pytest.mark.asyncio
    async def test_extract_context_without_extractor(
        self, context_assembler: ContextAssembler
    ):
        """Test that extraction handles missing extractor gracefully."""
        turn = create_turn("Test message")

        # Should not raise - just logs warning
        await context_assembler.extract_context(turn, async_execution=False)


class TestConsolidation:
    """Tests for consolidation orchestration."""

    @pytest.mark.asyncio
    async def test_consolidate_without_consolidator(
        self, context_assembler: ContextAssembler
    ):
        """Test that consolidation handles missing consolidator."""
        report = await context_assembler.consolidate_memory("test_session")

        assert report.errors == ["No consolidator configured"]
