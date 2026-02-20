"""
Tests for MemoryConsolidator.

Tests cover:
- Summarization using LLMClient
- Conflict resolution
- Entity deduplication

Note: Tests use mock LLMClient protocol from conftest fixtures.
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from friday_core.interfaces.llm import ChatCompletionResponse
from friday_memory import (
    ConflictResolutionResponse,
    InteractionTurn,
    MemoryController,
    ProvenanceMetadata,
    SummarizationResponse,
)
from friday_memory.context.consolidator import MemoryConsolidator


@pytest.fixture
def mock_llm_client_with_responses():
    """
    Mock LLMClient with configurable responses for consolidator tests.
    """
    mock = AsyncMock()

    # Default summarization response
    summarization_response = ChatCompletionResponse(
        content='{"summary": "Test summary", "key_topics": ["topic1"], "decisions": ["decision1"], "tokens_original": 100, "tokens_compressed": 20}',  # noqa: E501
    )
    summarization_response._parsed_model = SummarizationResponse(
        summary="Test summary",
        key_topics=["topic1"],
        decisions=["decision1"],
        tokens_original=100,
        tokens_compressed=20,
    )

    # Default conflict resolution response
    conflict_response = ChatCompletionResponse(
        content='{"has_conflict": true, "resolution": "Resolved", "current_value": "new_value", "historical_note": "Changed from old"}',  # noqa: E501
    )
    conflict_response._parsed_model = ConflictResolutionResponse(
        has_conflict=True,
        resolution="Resolved",
        current_value="new_value",
        historical_note="Changed from old",
    )

    mock.chat_completion = AsyncMock(return_value=summarization_response)
    mock._conflict_response = conflict_response
    mock._summarization_response = summarization_response

    return mock


class TestMemoryConsolidator:
    """Tests for MemoryConsolidator."""

    @pytest.mark.asyncio
    async def test_consolidator_init(
        self, memory_controller: MemoryController, mock_llm_client_with_responses
    ):
        """Test consolidator initialization."""
        consolidator = MemoryConsolidator(
            memory_controller=memory_controller,
            llm_client=mock_llm_client_with_responses,
        )

        assert consolidator._memory == memory_controller
        assert consolidator._llm_client == mock_llm_client_with_responses
        assert consolidator._min_turns == 5
        assert consolidator._max_turns == 10

    @pytest.mark.asyncio
    async def test_consolidate_not_enough_turns(
        self, memory_controller: MemoryController, mock_llm_client_with_responses
    ):
        """Test consolidation skips when not enough turns."""
        consolidator = MemoryConsolidator(
            memory_controller=memory_controller,
            llm_client=mock_llm_client_with_responses,
            min_turns_to_consolidate=5,
        )

        session_id = f"test_session_{uuid.uuid4().hex[:8]}"

        # Add only 3 turns (less than min of 5)
        for i in range(3):
            turn = InteractionTurn(
                id=str(uuid.uuid4()),
                session_id=session_id,
                timestamp=datetime.now(),
                user_message=f"Message {i}",
                assistant_message=f"Response {i}",
            )
            await memory_controller.add_turn(session_id, turn)

        report = await consolidator.consolidate(session_id)

        assert report.session_id == session_id
        assert report.nodes_created == 0
        assert report.tokens_condensed == 0
        assert len(report.errors) == 0
        # LLM should not be called
        mock_llm_client_with_responses.chat_completion.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolve_conflict_empty_facts(
        self, memory_controller: MemoryController, mock_llm_client_with_responses
    ):
        """Test conflict resolution with empty facts."""
        consolidator = MemoryConsolidator(
            memory_controller=memory_controller,
            llm_client=mock_llm_client_with_responses,
        )

        result = await consolidator.resolve_conflict([])

        assert result["has_conflict"] is False
        assert "No facts to resolve" in result["resolution"]

    @pytest.mark.asyncio
    async def test_resolve_conflict_with_facts(
        self, memory_controller: MemoryController, mock_llm_client_with_responses
    ):
        """Test conflict resolution with facts."""
        # Configure the mock to return conflict response
        conflict_response = mock_llm_client_with_responses._conflict_response
        mock_llm_client_with_responses.chat_completion.return_value = conflict_response

        consolidator = MemoryConsolidator(
            memory_controller=memory_controller,
            llm_client=mock_llm_client_with_responses,
        )

        facts = [
            {"timestamp": "2024-01-01", "text": "User prefers dark mode"},
            {"timestamp": "2024-01-15", "text": "User prefers light mode"},
        ]

        result = await consolidator.resolve_conflict(facts)

        assert result["has_conflict"] is True
        assert result["resolution"] == "Resolved"
        assert result["current_value"] == "new_value"
        mock_llm_client_with_responses.chat_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_recent_memories(
        self, memory_controller: MemoryController, mock_llm_client_with_responses
    ):
        """Test getting recent memories."""
        consolidator = MemoryConsolidator(
            memory_controller=memory_controller,
            llm_client=mock_llm_client_with_responses,
        )

        session_id = f"test_session_{uuid.uuid4().hex[:8]}"

        # Store some insights first
        provenance = ProvenanceMetadata(
            source_id=session_id,
            source_type="test",
            confidence=0.9,
            author_id="test",
        )

        await memory_controller.store_insight(
            "Test insight 1",
            provenance=provenance,
        )

        memories = await consolidator.get_recent_memories(session_id, limit=5)

        # Should return a list (may be empty if query doesn't match)
        assert isinstance(memories, list)

    @pytest.mark.asyncio
    async def test_count_tokens(
        self, memory_controller: MemoryController, mock_llm_client_with_responses
    ):
        """Test token counting."""
        consolidator = MemoryConsolidator(
            memory_controller=memory_controller,
            llm_client=mock_llm_client_with_responses,
        )

        tokens = consolidator._count_tokens("Hello, world!")

        assert isinstance(tokens, int)
        assert tokens > 0

    @pytest.mark.asyncio
    async def test_is_similar(
        self, memory_controller: MemoryController, mock_llm_client_with_responses
    ):
        """Test string similarity."""
        consolidator = MemoryConsolidator(
            memory_controller=memory_controller,
            llm_client=mock_llm_client_with_responses,
        )

        # Same string should be similar
        assert consolidator._is_similar("hello", "hello") is True

        # Very different strings should not be similar
        assert consolidator._is_similar("hello", "xyz") is False

        # Similar strings with typo
        assert consolidator._is_similar("hello", "helo", threshold=0.7) is True
