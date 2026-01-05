"""
Tests for LiteLLM Embedding Service.

Tests embedding generation with mocked LiteLLM responses.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from friday_llm import LiteLLMEmbeddingService
from friday_core.telemetry import DebugTelemetryRecorder


class MockUsage:
    """Mock usage information."""

    def __init__(self, prompt_tokens: int = 10, total_tokens: int = 10):
        self.prompt_tokens = prompt_tokens
        self.total_tokens = total_tokens


class MockEmbeddingResponse:
    """Mock LiteLLM embedding response."""

    def __init__(self, embeddings: list[list[float]], prompt_tokens: int = 10):
        self.data = [{"embedding": emb} for emb in embeddings]
        self.usage = MockUsage(prompt_tokens=prompt_tokens, total_tokens=prompt_tokens)


@pytest.fixture
def embedding_service():
    """Create embedding service instance."""
    return LiteLLMEmbeddingService(
        model_name="text-embedding-3-small",
        api_key="test-key",
    )


@pytest.fixture
def embedding_service_with_telemetry():
    """Create embedding service with telemetry."""
    recorder = DebugTelemetryRecorder()
    return LiteLLMEmbeddingService(
        model_name="text-embedding-3-small",
        api_key="test-key",
        telemetry=recorder,
    ), recorder


class TestLiteLLMEmbeddingService:
    """Tests for LiteLLMEmbeddingService."""

    @pytest.mark.asyncio
    async def test_embed_single_query(self, embedding_service):
        """Test embedding a single query."""
        mock_embedding = [[0.1, 0.2, 0.3, 0.4, 0.5]]
        mock_response = MockEmbeddingResponse(mock_embedding)

        with patch("litellm.aembedding", new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = mock_response

            result = await embedding_service.embed_query("test query")

            assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
            mock_embed.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_multiple_documents(self, embedding_service):
        """Test embedding multiple documents."""
        mock_embeddings = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9],
        ]
        mock_response = MockEmbeddingResponse(mock_embeddings)

        with patch("litellm.aembedding", new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = mock_response

            result = await embedding_service.embed_documents(
                ["doc1", "doc2", "doc3"]
            )

            assert len(result) == 3
            assert result[0] == [0.1, 0.2, 0.3]
            assert result[1] == [0.4, 0.5, 0.6]
            assert result[2] == [0.7, 0.8, 0.9]

    @pytest.mark.asyncio
    async def test_embed_empty_list(self, embedding_service):
        """Test embedding an empty list returns empty list."""
        result = await embedding_service.embed_documents([])
        assert result == []

    @pytest.mark.asyncio
    async def test_batching(self, embedding_service):
        """Test that large document sets are batched."""
        embedding_service.batch_size = 2  # Small batch for testing

        mock_embeddings_batch1 = [[0.1, 0.2], [0.3, 0.4]]
        mock_embeddings_batch2 = [[0.5, 0.6]]

        call_count = [0]

        async def mock_embedding(**kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return MockEmbeddingResponse(mock_embeddings_batch1)
            else:
                return MockEmbeddingResponse(mock_embeddings_batch2)

        with patch("litellm.aembedding", side_effect=mock_embedding):
            result = await embedding_service.embed_documents(
                ["doc1", "doc2", "doc3"]
            )

            assert len(result) == 3
            assert call_count[0] == 2  # Called twice due to batching

    @pytest.mark.asyncio
    async def test_telemetry_events(self, embedding_service_with_telemetry):
        """Test that telemetry events are emitted."""
        service, recorder = embedding_service_with_telemetry
        mock_response = MockEmbeddingResponse([[0.1, 0.2, 0.3]])

        with patch("litellm.aembedding", new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = mock_response

            await service.embed_documents(["test"])

            assert "embeddings_generated" in recorder.event_names

    @pytest.mark.asyncio
    async def test_query_telemetry(self, embedding_service_with_telemetry):
        """Test telemetry for query embedding."""
        service, recorder = embedding_service_with_telemetry
        mock_response = MockEmbeddingResponse([[0.1, 0.2, 0.3]])

        with patch("litellm.aembedding", new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = mock_response

            await service.embed_query("test query")

            # Query embedding now uses unified telemetry, emits embeddings_generated
            assert "embeddings_generated" in recorder.event_names
