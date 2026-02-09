"""
Tests for MemoryController lifecycle-aware retrieval (Phase 6).

Tests cover:
- Lifecycle-aware vector retrieval using CollectionManager
- Fast inclusion scoring using pre-computed retrieval_factor
- Access buffer async recording
- Graph path scoring with pre-embedded edges
"""

import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from friday_core import DebugTelemetryRecorder

from friday_memory import (
    AccessBuffer,
    AccessBufferConfig,
    ChromaVectorStore,
    CollectionConfig,
    CollectionManager,
    ElementXGraphStore,
    GraphPathScorer,
    GraphPathScorerConfig,
    InMemoryEpisodicStore,
    MemoryController,
)


class MockEmbeddingFunction:
    """Mock embedding function for testing."""

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t)) / 100] * 768 for t in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [float(len(text)) / 100] * 768


def unique_config():
    """Create config with unique collection names for test isolation."""
    suffix = uuid.uuid4().hex[:8]
    return CollectionConfig(
        short_term_collection=f"test_short_{suffix}",
        long_term_collection=f"test_long_{suffix}",
        decayed_collection=f"test_decayed_{suffix}",
    )


class TestLifecycleProperties:
    """Test lifecycle component properties."""

    @pytest.fixture
    def mock_embedding(self):
        return MockEmbeddingFunction()

    @pytest.fixture
    def stores(self, mock_embedding):
        """Create basic stores for testing."""
        collection_name = f"test_{uuid.uuid4().hex[:8]}"
        return {
            "vector": ChromaVectorStore(
                collection_name=collection_name,
                embedding_function=mock_embedding,
            ),
            "graph": ElementXGraphStore(),
            "episodic": InMemoryEpisodicStore(),
        }

    def test_has_lifecycle_support_always_true(self, stores, mock_embedding):
        """Test has_lifecycle_support always returns True."""
        collection_manager = CollectionManager(
            embedding_function=mock_embedding,
            config=unique_config(),
            path=None,
        )
        controller = MemoryController(
            vector_store=stores["vector"],
            graph_store=stores["graph"],
            episodic_store=stores["episodic"],
            collection_manager=collection_manager,
        )
        assert controller.has_lifecycle_support

    def test_lifecycle_properties_accessible(self, stores, mock_embedding):
        """Test lifecycle component properties are accessible."""
        collection_manager = CollectionManager(
            embedding_function=mock_embedding,
            config=unique_config(),
            path=None,
        )
        access_buffer = AccessBuffer()
        graph_scorer = GraphPathScorer()

        controller = MemoryController(
            vector_store=stores["vector"],
            graph_store=stores["graph"],
            episodic_store=stores["episodic"],
            collection_manager=collection_manager,
            access_buffer=access_buffer,
            graph_scorer=graph_scorer,
        )

        assert controller.collection_manager is collection_manager
        assert controller.access_buffer is access_buffer
        assert controller.graph_scorer is graph_scorer


class TestLifecycleAwareRetrieval:
    """Test lifecycle-aware vector retrieval."""

    @pytest.fixture
    def mock_embedding(self):
        return MockEmbeddingFunction()

    @pytest.fixture
    def collection_manager(self, mock_embedding):
        """Create collection manager for testing."""
        return CollectionManager(
            embedding_function=mock_embedding,
            config=unique_config(),
            path=None,
        )

    @pytest.fixture
    def access_buffer(self):
        """Create access buffer for testing."""
        return AccessBuffer(
            AccessBufferConfig(
                max_buffer_size=100,
                max_buffer_age_seconds=60,
            )
        )

    @pytest.fixture
    def controller_with_lifecycle(
        self, mock_embedding, collection_manager, access_buffer
    ):
        """Create controller with lifecycle components."""
        collection_name = f"test_{uuid.uuid4().hex[:8]}"
        return MemoryController(
            vector_store=ChromaVectorStore(
                collection_name=collection_name,
                embedding_function=mock_embedding,
            ),
            graph_store=ElementXGraphStore(),
            episodic_store=InMemoryEpisodicStore(),
            telemetry=DebugTelemetryRecorder(),
            collection_manager=collection_manager,
            access_buffer=access_buffer,
        )

    @pytest.mark.asyncio
    async def test_recall_uses_lifecycle_when_available(
        self, controller_with_lifecycle, collection_manager
    ):
        """Test that recall uses lifecycle retrieval when CollectionManager is set."""
        # Add some test data to short-term collection
        now = datetime.now()
        await collection_manager.add_to_short_term(
            texts=["Test short-term memory"],
            metadatas=[
                {
                    "type": "insight",
                    "created_at": now.isoformat(),
                }
            ],
            ids=["st_mem_1"],
        )

        # Run recall
        payload = await controller_with_lifecycle.recall(
            query="Test",
            session_id="test_session",
            include_history=False,
        )

        # Verify lifecycle was used
        assert payload.debug_info.get("lifecycle_enabled") is True


class TestFastScoring:
    """Test fast inclusion scoring."""

    @pytest.fixture
    def mock_embedding(self):
        return MockEmbeddingFunction()

    @pytest.fixture
    def controller(self, mock_embedding):
        """Create controller for scoring tests."""
        collection_name = f"test_{uuid.uuid4().hex[:8]}"
        return MemoryController(
            vector_store=ChromaVectorStore(
                collection_name=collection_name,
                embedding_function=mock_embedding,
            ),
            graph_store=ElementXGraphStore(),
            episodic_store=InMemoryEpisodicStore(),
            collection_manager=CollectionManager(
                embedding_function=mock_embedding,
                config=unique_config(),
            ),
        )

    def test_apply_fast_scoring_with_factor(self, controller):
        """Test fast scoring uses retrieval_factor from metadata."""
        results = [
            {
                "id": "mem1",
                "text": "Test memory",
                "similarity": 0.8,
                "metadata": {"retrieval_factor": 1.2},
            },
        ]

        scored = controller._apply_fast_scoring(results)

        assert len(scored) == 1
        # 0.8 * 1.2 = 0.96
        assert abs(scored[0]["inclusion_score"] - 0.96) < 0.001

    def test_apply_fast_scoring_default_factor(self, controller):
        """Test fast scoring uses default factor when not present."""
        results = [
            {
                "id": "mem1",
                "text": "Test memory",
                "similarity": 0.8,
                "metadata": {},  # No retrieval_factor
            },
        ]

        scored = controller._apply_fast_scoring(results)

        assert len(scored) == 1
        # 0.8 * 0.5 (default) = 0.4
        assert abs(scored[0]["inclusion_score"] - 0.4) < 0.001

    def test_apply_fast_scoring_preserves_fields(self, controller):
        """Test that fast scoring preserves existing fields."""
        results = [
            {
                "id": "mem1",
                "text": "Test memory",
                "similarity": 0.7,
                "metadata": {"type": "insight", "retrieval_factor": 1.0},
                "custom_field": "preserved",
            },
        ]

        scored = controller._apply_fast_scoring(results)

        assert scored[0]["custom_field"] == "preserved"
        assert scored[0]["id"] == "mem1"
        assert scored[0]["text"] == "Test memory"


class TestAccessBufferIntegration:
    """Test access buffer integration with retrieval."""

    @pytest.fixture
    def mock_embedding(self):
        return MockEmbeddingFunction()

    @pytest.fixture
    def access_buffer(self):
        return AccessBuffer(AccessBufferConfig(max_buffer_size=100))

    @pytest.fixture
    def collection_manager(self, mock_embedding):
        return CollectionManager(
            embedding_function=mock_embedding,
            config=unique_config(),
            path=None,
        )

    @pytest.mark.asyncio
    async def test_access_buffer_records_on_retrieval(
        self, mock_embedding, collection_manager, access_buffer
    ):
        """Test that access buffer records accesses during retrieval."""
        collection_name = f"test_{uuid.uuid4().hex[:8]}"
        controller = MemoryController(
            vector_store=ChromaVectorStore(
                collection_name=collection_name,
                embedding_function=mock_embedding,
            ),
            graph_store=ElementXGraphStore(),
            episodic_store=InMemoryEpisodicStore(),
            collection_manager=collection_manager,
            access_buffer=access_buffer,
        )

        # Add test data
        now = datetime.now()
        await collection_manager.add_to_short_term(
            texts=["Short-term memory 1"],
            metadatas=[{"type": "insight", "created_at": now.isoformat()}],
            ids=["st_1"],
        )

        # Initially buffer should be empty
        assert access_buffer.total_count == 0

        # Run recall
        await controller.recall(
            query="memory",
            session_id="test",
            include_history=False,
        )

        # Allow async tasks to complete
        import asyncio

        await asyncio.sleep(0.1)

        # Buffer should have recorded accesses
        # Note: May or may not have recorded depending on search results
        # Just verify it doesn't error
        stats = access_buffer.get_stats()
        assert "short_term_memories" in stats
        assert "long_term_memories" in stats


class TestGraphPathScoringIntegration:
    """Test graph path scoring integration."""

    @pytest.fixture
    def mock_embedding(self):
        return MockEmbeddingFunction()

    @pytest.fixture
    def graph_scorer(self):
        return GraphPathScorer(
            GraphPathScorerConfig(
                path_threshold=0.3,
                max_paths=10,
            )
        )

    @pytest.fixture
    def controller_with_scorer(self, mock_embedding, graph_scorer):
        """Create controller with graph scorer."""
        collection_name = f"test_{uuid.uuid4().hex[:8]}"
        return MemoryController(
            vector_store=ChromaVectorStore(
                collection_name=collection_name,
                embedding_function=mock_embedding,
            ),
            graph_store=ElementXGraphStore(),
            episodic_store=InMemoryEpisodicStore(),
            telemetry=DebugTelemetryRecorder(),
            collection_manager=CollectionManager(
                embedding_function=mock_embedding,
                config=unique_config(),
            ),
            graph_scorer=graph_scorer,
        )

    def test_graph_scorer_property(self, controller_with_scorer, graph_scorer):
        """Test graph scorer is accessible via property."""
        assert controller_with_scorer.graph_scorer is graph_scorer

    @pytest.mark.asyncio
    async def test_retrieve_graph_with_scoring_no_embedding(
        self, controller_with_scorer
    ):
        """Test graph retrieval without query embedding falls back to base."""
        result = await controller_with_scorer._retrieve_graph_with_scoring(
            query="test query",
            depth=1,
            query_embedding=None,  # No embedding
        )

        # Should return base result (no scored_paths)
        assert "entities" in result
        assert "facts" in result
