# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""
Tests for LiteLLM Embedding Service.

Tests embedding generation with mocked LiteLLM responses.
"""

from unittest.mock import AsyncMock, patch

import pytest
from friday_core.telemetry import DebugTelemetryRecorder
from friday_llm import LiteLLMEmbeddingService


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

            result = await embedding_service.embed_documents(["doc1", "doc2", "doc3"])

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
            result = await embedding_service.embed_documents(["doc1", "doc2", "doc3"])

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


class TestEmbeddingCache:
    """Tests for embedding cache functionality."""

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        """Test that repeated queries hit the cache."""
        service = LiteLLMEmbeddingService(
            model_name="text-embedding-3-small",
            api_key="test-key",
            cache_size=10,
        )
        mock_response = MockEmbeddingResponse([[0.1, 0.2, 0.3]])

        with patch("litellm.aembedding", new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = mock_response

            # First call - cache miss
            result1 = await service.embed_query("test query")
            assert mock_embed.call_count == 1

            # Second call - cache hit
            result2 = await service.embed_query("test query")
            assert mock_embed.call_count == 1  # Still 1, no new call

            # Results should be identical
            assert result1 == result2
            assert result1 == [0.1, 0.2, 0.3]

            # Verify cache stats
            assert service.cache_stats["hits"] == 1
            assert service.cache_stats["misses"] == 1
            assert service.cache_stats["size"] == 1

    @pytest.mark.asyncio
    async def test_cache_miss_different_queries(self):
        """Test that different queries result in cache misses."""
        service = LiteLLMEmbeddingService(
            model_name="text-embedding-3-small",
            api_key="test-key",
            cache_size=10,
        )
        mock_response1 = MockEmbeddingResponse([[0.1, 0.2, 0.3]])
        mock_response2 = MockEmbeddingResponse([[0.4, 0.5, 0.6]])

        with patch("litellm.aembedding", new_callable=AsyncMock) as mock_embed:
            mock_embed.side_effect = [mock_response1, mock_response2]

            # First query
            result1 = await service.embed_query("query one")
            assert mock_embed.call_count == 1

            # Different query - cache miss
            result2 = await service.embed_query("query two")
            assert mock_embed.call_count == 2

            # Results should be different
            assert result1 == [0.1, 0.2, 0.3]
            assert result2 == [0.4, 0.5, 0.6]

            # Verify cache stats
            assert service.cache_stats["hits"] == 0
            assert service.cache_stats["misses"] == 2
            assert service.cache_stats["size"] == 2

    @pytest.mark.asyncio
    async def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        service = LiteLLMEmbeddingService(
            model_name="text-embedding-3-small",
            api_key="test-key",
            cache_size=2,  # Small cache for testing eviction
        )

        call_count = [0]

        async def mock_embedding(**kwargs):
            call_count[0] += 1
            return MockEmbeddingResponse([[float(call_count[0])]])

        with patch("litellm.aembedding", side_effect=mock_embedding):
            # Fill cache with 2 entries
            await service.embed_query("query1")
            await service.embed_query("query2")
            assert service.cache_stats["size"] == 2

            # Add third query - should evict query1 (LRU)
            await service.embed_query("query3")
            assert service.cache_stats["size"] == 2

            # query1 should be evicted, will need new API call
            # query2 and query3 should still be cached

            # Reset call count to track new calls
            current_calls = call_count[0]

            # query2 should hit cache
            await service.embed_query("query2")
            assert call_count[0] == current_calls  # No new call

            # query3 should hit cache
            await service.embed_query("query3")
            assert call_count[0] == current_calls  # No new call

            # query1 was evicted, should miss cache
            await service.embed_query("query1")
            assert call_count[0] == current_calls + 1  # New call needed

    @pytest.mark.asyncio
    async def test_cache_disabled(self):
        """Test that cache can be disabled with cache_size=0."""
        service = LiteLLMEmbeddingService(
            model_name="text-embedding-3-small",
            api_key="test-key",
            cache_size=0,  # Disable cache
        )
        mock_response = MockEmbeddingResponse([[0.1, 0.2, 0.3]])

        with patch("litellm.aembedding", new_callable=AsyncMock) as mock_embed:
            mock_embed.return_value = mock_response

            # Multiple calls to same query
            await service.embed_query("test query")
            await service.embed_query("test query")
            await service.embed_query("test query")

            # Each call should hit the API
            assert mock_embed.call_count == 3

            # Cache should be empty
            assert service.cache_stats["size"] == 0
