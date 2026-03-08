# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
# mypy: disallow-untyped-defs=False
"""
Tests for NullGraphStore adapter.

Tests verify:
- All write operations succeed silently
- All read operations return empty results
- No exceptions are raised

NullGraphStore is a no-op implementation for vector-only and testing scenarios.
"""

import uuid

import pytest
from friday_memory.adapters.null_graph import NullGraphStore
from friday_memory.models.graph import GraphEdge, GraphNode, ProvenanceMetadata


class TestNullGraphStore:
    """Tests for NullGraphStore."""

    @pytest.fixture
    def null_graph_store(self) -> NullGraphStore:
        """Create a NullGraphStore instance."""
        return NullGraphStore()

    @pytest.fixture
    def sample_provenance(self) -> ProvenanceMetadata:
        """Create sample provenance metadata."""
        return ProvenanceMetadata(
            source_id="test_source",
            source_type="test",
            confidence=0.95,
        )

    @pytest.fixture
    def sample_node(self, sample_provenance) -> GraphNode:
        """Create a sample graph node."""
        return GraphNode(
            id=str(uuid.uuid4()),
            type="person",
            label="Alice",
            properties={"role": "developer"},
            provenance=sample_provenance,
        )

    @pytest.fixture
    def sample_edge(self, sample_provenance) -> GraphEdge:
        """Create a sample graph edge."""
        return GraphEdge(
            source_id="node_1",
            target_id="node_2",
            relation="works_with",
            weight=1.0,
            provenance=sample_provenance,
        )

    # --- CRUD Operations ---

    @pytest.mark.asyncio
    async def test_add_node_succeeds(
        self, null_graph_store: NullGraphStore, sample_node: GraphNode
    ) -> None:
        """Test that add_node always succeeds."""
        result = await null_graph_store.add_node(sample_node)
        assert result is True

    @pytest.mark.asyncio
    async def test_add_edge_succeeds(
        self, null_graph_store: NullGraphStore, sample_edge: GraphEdge
    ) -> None:
        """Test that add_edge always succeeds."""
        result = await null_graph_store.add_edge(sample_edge)
        assert result is True

    @pytest.mark.asyncio
    async def test_remove_node_succeeds(self, null_graph_store: NullGraphStore) -> None:
        """Test that remove_node always succeeds."""
        result = await null_graph_store.remove_node("any_node_id")
        assert result is True

    @pytest.mark.asyncio
    async def test_update_node_succeeds(
        self, null_graph_store: NullGraphStore, sample_node: GraphNode
    ) -> None:
        """Test that update_node always succeeds."""
        result = await null_graph_store.update_node(sample_node)
        assert result is True

    # --- Read Operations (All Return Empty) ---

    @pytest.mark.asyncio
    async def test_get_node_returns_none(self, null_graph_store: NullGraphStore) -> None:
        """Test that get_node always returns None."""
        result = await null_graph_store.get_node("any_id")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_nodes_returns_empty(self, null_graph_store: NullGraphStore) -> None:
        """Test that get_all_nodes always returns empty list."""
        result = await null_graph_store.get_all_nodes()
        assert result == []

    @pytest.mark.asyncio
    async def test_get_top_nodes_returns_empty(self, null_graph_store: NullGraphStore) -> None:
        """Test that get_top_nodes always returns empty list."""
        result = await null_graph_store.get_top_nodes(n=10)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_edges_returns_empty(self, null_graph_store: NullGraphStore) -> None:
        """Test that get_all_edges always returns empty list."""
        result = await null_graph_store.get_all_edges()
        assert result == []

    # --- Traversal Operations ---

    @pytest.mark.asyncio
    async def test_get_neighbors_returns_empty(self, null_graph_store: NullGraphStore) -> None:
        """Test that get_neighbors always returns empty list."""
        result = await null_graph_store.get_neighbors("any_node", depth=3)
        assert result == []

    @pytest.mark.asyncio
    async def test_find_path_returns_empty(self, null_graph_store: NullGraphStore) -> None:
        """Test that find_path always returns empty list."""
        result = await null_graph_store.find_path("start", "end", max_depth=5)
        assert result == []

    # --- Intelligence Operations ---

    @pytest.mark.asyncio
    async def test_merge_nodes_succeeds(self, null_graph_store: NullGraphStore) -> None:
        """Test that merge_nodes always succeeds."""
        result = await null_graph_store.merge_nodes("primary", "secondary")
        assert result is True

    @pytest.mark.asyncio
    async def test_fuzzy_search_returns_empty(self, null_graph_store: NullGraphStore) -> None:
        """Test that fuzzy_search always returns empty list."""
        result = await null_graph_store.fuzzy_search("query", threshold=0.5)
        assert result == []

    @pytest.mark.asyncio
    async def test_rank_nodes_returns_empty(self, null_graph_store: NullGraphStore) -> None:
        """Test that rank_nodes always returns empty list."""
        result = await null_graph_store.rank_nodes(algorithm="pagerank")
        assert result == []

    # --- Lookup Operations ---

    @pytest.mark.asyncio
    async def test_find_by_label_returns_none(self, null_graph_store: NullGraphStore) -> None:
        """Test that find_by_label always returns None."""
        result = await null_graph_store.find_by_label("Alice", node_type="person")
        assert result is None

    @pytest.mark.asyncio
    async def test_find_edge_returns_none(self, null_graph_store: NullGraphStore) -> None:
        """Test that find_edge always returns None."""
        result = await null_graph_store.find_edge(
            "source", "target", relation="works_with"
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_edge_exists_returns_false(self, null_graph_store: NullGraphStore) -> None:
        """Test that edge_exists always returns False."""
        result = await null_graph_store.edge_exists("source", "target")
        assert result is False

    # --- Access Tracking Operations ---

    @pytest.mark.asyncio
    async def test_record_node_access_returns_false(
        self, null_graph_store: NullGraphStore
    ) -> None:
        """Test that record_node_access returns False (no node found)."""
        result = await null_graph_store.record_node_access("any_id")
        assert result is False

    @pytest.mark.asyncio
    async def test_record_edge_access_returns_false(
        self, null_graph_store: NullGraphStore
    ) -> None:
        """Test that record_edge_access returns False (no edge found)."""
        result = await null_graph_store.record_edge_access("source", "target")
        assert result is False

    @pytest.mark.asyncio
    async def test_record_edges_access_returns_zero(
        self, null_graph_store: NullGraphStore
    ) -> None:
        """Test that record_edges_access returns 0."""
        result = await null_graph_store.record_edges_access([("a", "b"), ("c", "d")])
        assert result == 0

    # --- Embedding Operations ---

    @pytest.mark.asyncio
    async def test_update_edge_embedding_returns_false(
        self, null_graph_store: NullGraphStore
    ) -> None:
        """Test that update_edge_embedding returns False."""
        result = await null_graph_store.update_edge_embedding(
            "source", "target", [0.1, 0.2, 0.3]
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_update_edges_embeddings_returns_zero(
        self, null_graph_store: NullGraphStore
    ) -> None:
        """Test that update_edges_embeddings returns 0."""
        result = await null_graph_store.update_edges_embeddings(
            [
                ("a", "b", [0.1, 0.2]),
                ("c", "d", [0.3, 0.4]),
            ]
        )
        assert result == 0

    # --- Count Operations ---

    @pytest.mark.asyncio
    async def test_node_count_returns_zero(self, null_graph_store: NullGraphStore) -> None:
        """Test that node_count always returns 0."""
        result = await null_graph_store.node_count()
        assert result == 0

    @pytest.mark.asyncio
    async def test_edge_count_returns_zero(self, null_graph_store: NullGraphStore) -> None:
        """Test that edge_count always returns 0."""
        result = await null_graph_store.edge_count()
        assert result == 0

    # --- Clear Operation ---

    @pytest.mark.asyncio
    async def test_clear_returns_zeros(self, null_graph_store: NullGraphStore) -> None:
        """Test that clear returns dict with zero counts."""
        result = await null_graph_store.clear()
        assert result == {"nodes_deleted": 0, "edges_deleted": 0}


class TestNullGraphStoreUseCases:
    """Test real-world use cases for NullGraphStore."""

    @pytest.fixture
    def null_graph_store(self) -> NullGraphStore:
        """Create a NullGraphStore instance."""
        return NullGraphStore()

    @pytest.fixture
    def sample_provenance(self) -> ProvenanceMetadata:
        """Create sample provenance metadata."""
        return ProvenanceMetadata(
            source_id="test_source",
            source_type="test",
            confidence=0.95,
        )

    @pytest.mark.asyncio
    async def test_can_run_typical_workflow(
        self, null_graph_store: NullGraphStore, sample_provenance
    ) -> None:
        """
        Test that a typical graph workflow runs without errors.

        This simulates code that uses the graph store - it should work
        with NullGraphStore even though no data is stored.
        """
        # Create nodes
        node1 = GraphNode(
            id="node_1",
            type="person",
            label="Alice",
            properties={},
            provenance=sample_provenance,
        )
        node2 = GraphNode(
            id="node_2",
            type="person",
            label="Bob",
            properties={},
            provenance=sample_provenance,
        )

        # Add nodes (succeeds silently)
        await null_graph_store.add_node(node1)
        await null_graph_store.add_node(node2)

        # Create and add edge
        edge = GraphEdge(
            source_id="node_1",
            target_id="node_2",
            relation="knows",
            provenance=sample_provenance,
        )
        await null_graph_store.add_edge(edge)

        # Query operations return empty but don't fail
        neighbors = await null_graph_store.get_neighbors("node_1")
        assert neighbors == []

        path = await null_graph_store.find_path("node_1", "node_2")
        assert path == []

        similar = await null_graph_store.fuzzy_search("Alice")
        assert similar == []

        # Counts are zero
        assert await null_graph_store.node_count() == 0
        assert await null_graph_store.edge_count() == 0

    @pytest.mark.asyncio
    async def test_vector_only_deployment_scenario(
        self, null_graph_store: NullGraphStore
    ) -> None:
        """
        Test scenario: Vector-only deployment with graph disabled.

        Some deployments may want vector search without relationship tracking.
        NullGraphStore provides API compatibility with zero overhead.
        """
        # Simulate memory controller calling graph methods
        # All should succeed without storing data

        # Check for existing entity (returns None)
        existing = await null_graph_store.find_by_label("Entity Name")
        assert existing is None

        # "Add" entity (succeeds silently)

        node = GraphNode(
            id="entity_1",
            type="concept",
            label="Entity Name",
            properties={"description": "Some concept"},
            provenance=ProvenanceMetadata(
                source_id="turn_123",
                source_type="interaction",
                confidence=0.8,
            ),
        )
        result = await null_graph_store.add_node(node)
        assert result is True

        # Graph queries return empty (expected behavior)
        ranked = await null_graph_store.rank_nodes()
        assert ranked == []

        # Clear does nothing but doesn't fail
        cleared = await null_graph_store.clear()
        assert cleared["nodes_deleted"] == 0
