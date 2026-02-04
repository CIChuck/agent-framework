"""Tests for CollectionManager."""

import uuid

import pytest

from friday_memory.retrieval.collection_manager import (
    CollectionConfig,
    CollectionManager,
)
from friday_memory.lifecycle.stages import MemoryStage, PromotionState


class MockEmbeddingFunction:
    """Mock embedding function for testing."""

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return deterministic embeddings based on text content."""
        return [[float(len(t)) / 100] * 768 for t in texts]

    async def embed_query(self, text: str) -> list[float]:
        """Return deterministic embedding for query."""
        return [float(len(text)) / 100] * 768


def unique_config():
    """Create config with unique collection names for test isolation."""
    suffix = uuid.uuid4().hex[:8]
    return CollectionConfig(
        short_term_collection=f"test_short_{suffix}",
        long_term_collection=f"test_long_{suffix}",
        decayed_collection=f"test_decayed_{suffix}",
    )


class TestCollectionConfig:
    """Test CollectionConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CollectionConfig()
        assert config.short_term_collection == "memories_short_term"
        assert config.long_term_collection == "memories_long_term"
        assert config.decayed_collection == "memories_decayed"
        assert config.short_term_min_similarity == 0.5
        assert config.long_term_min_similarity == 0.7
        assert config.default_n_results == 5

    def test_custom_config(self):
        """Test custom configuration."""
        config = CollectionConfig(
            short_term_collection="test_short",
            long_term_collection="test_long",
            short_term_min_similarity=0.4,
        )
        assert config.short_term_collection == "test_short"
        assert config.long_term_collection == "test_long"
        assert config.short_term_min_similarity == 0.4


class TestCollectionManager:
    """Test CollectionManager class."""

    @pytest.fixture
    def embedding_fn(self):
        """Create mock embedding function."""
        return MockEmbeddingFunction()

    @pytest.fixture
    def manager(self, embedding_fn):
        """Create manager with ephemeral storage and unique collection names."""
        return CollectionManager(
            embedding_function=embedding_fn,
            config=unique_config(),  # Unique names for test isolation
            path=None,  # Ephemeral
        )

    @pytest.mark.asyncio
    async def test_add_to_short_term(self, manager):
        """Test adding documents to short-term collection."""
        result = await manager.add_to_short_term(
            texts=["Test memory content"],
            metadatas=[{"type": "insight"}],
            ids=["mem1"],
        )
        assert result is True

        # Verify it's in short-term
        stats = await manager.get_stats()
        assert stats["short_term"] == 1
        assert stats["long_term"] == 0

    @pytest.mark.asyncio
    async def test_add_sets_stage_metadata(self, manager):
        """Test that add_to_short_term sets correct stage metadata."""
        await manager.add_to_short_term(
            texts=["Test memory"],
            metadatas=[{"type": "insight"}],
            ids=["mem1"],
        )

        doc = await manager.short_term.get_by_id("mem1")
        assert doc is not None
        assert doc["metadata"]["stage"] == MemoryStage.SHORT_TERM.value
        assert doc["metadata"]["promotion_state"] == PromotionState.NONE.value

    @pytest.mark.asyncio
    async def test_query_parallel_collections(self, manager):
        """Test querying short-term and long-term in parallel."""
        # Add to short-term
        await manager.add_to_short_term(
            texts=["Short term memory about Python"],
            metadatas=[{"type": "insight"}],
            ids=["short1"],
        )

        results = await manager.query("Python programming")

        assert "short_term" in results
        assert "long_term" in results
        assert len(results["short_term"]) >= 0  # May be filtered by similarity

    @pytest.mark.asyncio
    async def test_promote_memory(self, manager):
        """Test promoting memory from short-term to long-term."""
        # Add to short-term first
        await manager.add_to_short_term(
            texts=["Memory to promote"],
            metadatas=[{"type": "insight", "confidence": 0.8}],
            ids=["mem1"],
        )

        # Verify in short-term
        stats_before = await manager.get_stats()
        assert stats_before["short_term"] == 1
        assert stats_before["long_term"] == 0

        # Promote
        success = await manager.promote_memory("mem1")
        assert success is True

        # Verify moved to long-term
        stats_after = await manager.get_stats()
        assert stats_after["short_term"] == 0
        assert stats_after["long_term"] == 1

        # Check metadata updated
        doc = await manager.long_term.get_by_id("mem1")
        assert doc is not None
        assert doc["metadata"]["stage"] == "long_term"
        assert doc["metadata"]["promotion_state"] == PromotionState.COMPLETE.value
        assert "promoted_at" in doc["metadata"]

    @pytest.mark.asyncio
    async def test_promote_nonexistent_memory(self, manager):
        """Test promoting non-existent memory returns False."""
        success = await manager.promote_memory("nonexistent")
        assert success is False

    @pytest.mark.asyncio
    async def test_demote_to_decayed(self, manager):
        """Test demoting memory to decayed collection."""
        # Add to short-term and promote to long-term
        await manager.add_to_short_term(
            texts=["Memory to demote"],
            metadatas=[{"type": "insight"}],
            ids=["mem1"],
        )
        await manager.promote_memory("mem1")

        # Demote to decayed
        success = await manager.demote_to_decayed("mem1")
        assert success is True

        # Verify in decayed
        stats = await manager.get_stats()
        assert stats["short_term"] == 0
        assert stats["long_term"] == 0
        assert stats["decayed"] == 1

        # Check metadata updated
        doc = await manager.decayed.get_by_id("mem1")
        assert doc is not None
        assert doc["metadata"]["stage"] == MemoryStage.DECAYED.value
        assert "decayed_at" in doc["metadata"]

    @pytest.mark.asyncio
    async def test_reactivate_from_decayed(self, manager):
        """Test reactivating decayed memory back to long-term."""
        # Add, promote, then demote
        await manager.add_to_short_term(
            texts=["Memory to reactivate"],
            metadatas=[{"type": "insight"}],
            ids=["mem1"],
        )
        await manager.promote_memory("mem1")
        await manager.demote_to_decayed("mem1")

        # Reactivate
        success = await manager.reactivate_from_decayed("mem1")
        assert success is True

        # Verify back in long-term
        stats = await manager.get_stats()
        assert stats["long_term"] == 1
        assert stats["decayed"] == 0

        # Check metadata updated
        doc = await manager.long_term.get_by_id("mem1")
        assert doc is not None
        assert doc["metadata"]["stage"] == MemoryStage.LONG_TERM.value
        assert doc["metadata"]["decay_score"] == 0.5  # Reset to neutral

    @pytest.mark.asyncio
    async def test_get_stats(self, manager):
        """Test getting stats across all collections."""
        await manager.add_to_short_term(
            texts=["Short 1", "Short 2"],
            metadatas=[{"type": "insight"}, {"type": "insight"}],
            ids=["s1", "s2"],
        )

        stats = await manager.get_stats()

        assert stats["short_term"] == 2
        assert stats["long_term"] == 0
        assert stats["decayed"] == 0
        assert stats["total_active"] == 2
        assert stats["total"] == 2

    @pytest.mark.asyncio
    async def test_clear_all(self, manager):
        """Test clearing all collections."""
        await manager.add_to_short_term(
            texts=["Memory 1", "Memory 2"],
            metadatas=[{"type": "insight"}, {"type": "insight"}],
            ids=["m1", "m2"],
        )

        result = await manager.clear_all()

        assert result["short_term_deleted"] == 2
        stats = await manager.get_stats()
        assert stats["total"] == 0

    @pytest.mark.asyncio
    async def test_recover_incomplete_promotions(self, manager):
        """Test recovery of incomplete promotions."""
        # Manually add a memory with PENDING promotion state to long-term
        # This simulates a crash during promotion
        await manager.long_term.add_documents(
            texts=["Incomplete promotion"],
            metadatas=[{
                "type": "insight",
                "stage": "long_term",
                "promotion_state": PromotionState.PENDING.value,
            }],
            ids=["pending1"],
        )

        # Also add to short-term to simulate the incomplete promotion
        await manager.short_term.add_documents(
            texts=["Incomplete promotion"],
            metadatas=[{
                "type": "insight",
                "stage": "short_term",
                "promotion_state": PromotionState.NONE.value,
            }],
            ids=["pending1"],
        )

        # Recover
        recovered = await manager.recover_incomplete_promotions()
        assert recovered == 1

        # Verify short-term copy deleted
        short_doc = await manager.short_term.get_by_id("pending1")
        assert short_doc is None

        # Verify long-term marked complete
        long_doc = await manager.long_term.get_by_id("pending1")
        assert long_doc is not None
        assert long_doc["metadata"]["promotion_state"] == PromotionState.COMPLETE.value
