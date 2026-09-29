# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
# mypy: disallow-untyped-defs=False
"""Tests for CollectionManager."""

import uuid
from types import SimpleNamespace

import pytest
from friday_core.mcp import MCPIngestionPolicy, MCPToolCallProvenance, MCPToolMetadata
from friday_memory.ingestion.mcp import MCPMemoryIngester
from friday_memory.lifecycle.stages import MemoryStage, PromotionState
from friday_memory.retrieval.collection_manager import (
    CollectionConfig,
    CollectionManager,
)


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

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = CollectionConfig()
        assert config.short_term_collection == "memories_short_term"
        assert config.long_term_collection == "memories_long_term"
        assert config.decayed_collection == "memories_decayed"
        assert config.short_term_min_similarity == 0.5
        assert config.long_term_min_similarity == 0.7
        assert config.default_n_results == 5

    def test_custom_config(self) -> None:
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
    async def test_add_to_short_term(self, manager) -> None:
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
    async def test_add_sets_stage_metadata(self, manager) -> None:
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
    async def test_query_parallel_collections(self, manager) -> None:
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
    async def test_query_quarantines_unverified_maintenance_synthesis(
        self, manager
    ) -> None:
        await manager.add_to_short_term(
            texts=[
                "Verified synthesis",
                "Unverified synthesis",
                "Rejected synthesis",
                "Ordinary unverified memory",
            ],
            metadatas=[
                {
                    "type": "meta_insight",
                    "maintenance_generated": True,
                    "verification_status": "verified",
                },
                {
                    "type": "meta_insight",
                    "maintenance_generated": True,
                    "verification_status": "unverified",
                },
                {
                    "type": "meta_insight",
                    "maintenance_generated": True,
                    "verification_status": "rejected",
                },
                {"type": "insight", "verification_status": "unverified"},
            ],
            ids=["verified", "unverified", "rejected", "ordinary"],
        )

        results = await manager.query("synthesis", n_results=10)
        returned_ids = {
            result["id"]
            for collection_results in results.values()
            for result in collection_results
        }

        assert "verified" in returned_ids
        assert "ordinary" in returned_ids
        assert "unverified" not in returned_ids
        assert "rejected" not in returned_ids

    @pytest.mark.asyncio
    async def test_promote_memory(self, manager) -> None:
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
    async def test_promote_nonexistent_memory(self, manager) -> None:
        """Test promoting non-existent memory returns False."""
        success = await manager.promote_memory("nonexistent")
        assert success is False

    @pytest.mark.asyncio
    async def test_demote_to_decayed(self, manager) -> None:
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
    async def test_reactivate_from_decayed(self, manager) -> None:
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
    async def test_stage_moves_preserve_numeric_embedding(self, manager) -> None:
        text = "Memory carried through stages"
        await manager.add_to_short_term([text], [{"type": "insight"}], ["mem1"])
        expected = [float(len(text)) / 100] * 768

        assert await manager.promote_memory("mem1")
        assert await manager.demote_to_decayed("mem1")
        assert await manager.reactivate_from_decayed("mem1")

        for store, expected_count in (
            (manager.short_term, 0),
            (manager.decayed, 0),
            (manager.long_term, 1),
        ):
            assert await store.count() == expected_count
        stored = manager.long_term._collection.get(
            ids=["mem1"], include=["embeddings"]
        )
        assert stored["embeddings"] is not None
        assert list(stored["embeddings"][0]) == pytest.approx(expected)

    @pytest.mark.asyncio
    async def test_get_stats(self, manager) -> None:
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
    async def test_clear_all(self, manager) -> None:
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
    async def test_recover_incomplete_promotions(self, manager) -> None:
        """Test recovery of incomplete promotions."""
        # Manually add a memory with PENDING promotion state to long-term
        # This simulates a crash during promotion
        await manager.long_term.add_documents(
            texts=["Incomplete promotion"],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "long_term",
                    "promotion_state": PromotionState.PENDING.value,
                }
            ],
            ids=["pending1"],
        )

        # Also add to short-term to simulate the incomplete promotion
        await manager.short_term.add_documents(
            texts=["Incomplete promotion"],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "short_term",
                    "promotion_state": PromotionState.NONE.value,
                }
            ],
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


def test_mcp_pending_or_malformed_cannot_bypass_collection_eligibility():
    for metadata in ({"source_type": "mcp_tool"}, {"type": "mcp_tool_snapshot"},
                     {"mcp_state": "pending"}, {"mcp_provenance": "{}"}):
        assert not CollectionManager._is_retrieval_eligible({"id": "bad", "text": "raw", "metadata": metadata})
    assert CollectionManager._is_retrieval_eligible({"id": "old", "text": "native", "metadata": {}})


@pytest.mark.asyncio
async def test_owned_mcp_lookup_excludes_native_and_reuses_actual_call(tmp_path):
    manager = CollectionManager(
        MockEmbeddingFunction(), config=unique_config(), path=str(tmp_path / "vectors")
    )
    await manager.add_to_short_term(["native"], [{"type": "insight"}], ["native-id"])
    assert await manager.find_mcp_snapshot("entry", "call") is None
    text = '<untrusted_content source="mcp">\nresult\n</untrusted_content>'
    facts = MCPToolCallProvenance(
        tool=MCPToolMetadata(
            canonical_name="mcp_peer_read", server_name="peer",
            original_name="read", transport="stdio", trust_level="local",
        ),
        call_id="call", status="succeeded",
        output_sanitization_state="sanitized",
        model_result_size_bytes=len(text.encode()),
    )
    policy = MCPIngestionPolicy(
        long_term_memory_enabled=True, opted_in_servers=("peer",)
    )
    ingester = MCPMemoryIngester(manager)
    first = await ingester.prepare(facts, text, "entry", policy)
    owned = await manager.find_mcp_snapshot("entry", "call")
    assert owned is not None and owned.snapshot == first.snapshot
    repeated = await ingester.prepare(facts, text, "entry", policy)
    assert repeated.snapshot == first.snapshot
    assert await manager.short_term.count() == 2


@pytest.mark.asyncio
async def test_orphan_cleanup_requires_listing_and_keeps_shared_nodes(tmp_path):
    manager = CollectionManager(
        MockEmbeddingFunction(), config=unique_config(), path=str(tmp_path / "vectors")
    )

    class ListingGraph:
        def __init__(self):
            self.nodes = [
                SimpleNamespace(id="orphan", source_memory_ids=["gone"]),
                SimpleNamespace(id="shared", source_memory_ids=["gone", "kept"]),
                SimpleNamespace(id="unlinked", source_memory_ids=[]),
            ]
            self.removed = []

        async def get_all_nodes(self):
            return self.nodes

        async def remove_node(self, node_id):
            self.removed.append(node_id)
            return True

    graph = ListingGraph()
    preview = await manager.cleanup_orphaned_graph_nodes({"gone"}, graph)
    assert preview == {
        "deleted_count": 1, "deleted_node_ids": ["orphan"], "dry_run": True
    }
    assert graph.removed == []

    deleted = await manager.cleanup_orphaned_graph_nodes(
        {"gone"}, graph, dry_run=False
    )
    assert deleted["deleted_node_ids"] == ["orphan"]
    assert graph.removed == ["orphan"]

    absent = await manager.cleanup_orphaned_graph_nodes(
        {"gone"}, SimpleNamespace(remove_node=graph.remove_node), dry_run=False
    )
    assert absent["deleted_count"] == 0
    assert absent["error"] == "Graph store does not support node listing"
    assert graph.removed == ["orphan"]
