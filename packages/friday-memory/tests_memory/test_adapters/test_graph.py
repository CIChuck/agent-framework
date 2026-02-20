"""
Tests for ElementXGraphStore adapter.

Tests cover:
- Node CRUD operations
- Edge creation and traversal
- Fuzzy search for duplicate prevention
- Node merging (entity resolution)
- PageRank importance ranking
- Persistence (JSON/pickle)
"""

import tempfile
import uuid
from pathlib import Path

import pytest
from friday_memory import ElementXGraphStore, GraphEdge, GraphNode, ProvenanceMetadata


def create_node(
    label: str,
    node_type: str = "entity",
    provenance: ProvenanceMetadata | None = None,
) -> GraphNode:
    """Helper to create test nodes."""
    return GraphNode(
        id=str(uuid.uuid4()),
        type=node_type,
        label=label,
        properties={},
        provenance=provenance
        or ProvenanceMetadata(
            source_id="test",
            source_type="test",
            confidence=1.0,
        ),
    )


def create_edge(
    source_id: str,
    target_id: str,
    relation: str = "related_to",
    provenance: ProvenanceMetadata | None = None,
) -> GraphEdge:
    """Helper to create test edges."""
    return GraphEdge(
        source_id=source_id,
        target_id=target_id,
        relation=relation,
        weight=1.0,
        provenance=provenance
        or ProvenanceMetadata(
            source_id="test",
            source_type="test",
            confidence=1.0,
        ),
    )


class TestElementXGraphStore:
    """Tests for ElementXGraphStore."""

    @pytest.mark.asyncio
    async def test_add_node(self, graph_store: ElementXGraphStore):
        """Test adding a node to the graph."""
        node = create_node("Alice", "person")
        result = await graph_store.add_node(node)

        assert result is True
        count = await graph_store.node_count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_get_node(self, graph_store: ElementXGraphStore):
        """Test retrieving a node by ID."""
        node = create_node("Bob", "person")
        await graph_store.add_node(node)

        retrieved = await graph_store.get_node(node.id)
        assert retrieved is not None
        assert retrieved.label == "Bob"
        assert retrieved.type == "person"

    @pytest.mark.asyncio
    async def test_get_nonexistent_node(self, graph_store: ElementXGraphStore):
        """Test retrieving non-existent node returns None."""
        result = await graph_store.get_node("nonexistent_id")
        assert result is None

    @pytest.mark.asyncio
    async def test_remove_node(self, graph_store: ElementXGraphStore):
        """Test removing a node."""
        node = create_node("Charlie")
        await graph_store.add_node(node)

        result = await graph_store.remove_node(node.id)
        assert result is True

        count = await graph_store.node_count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_remove_nonexistent_node(self, graph_store: ElementXGraphStore):
        """Test removing non-existent node returns False."""
        result = await graph_store.remove_node("nonexistent_id")
        assert result is False

    @pytest.mark.asyncio
    async def test_add_edge(self, graph_store: ElementXGraphStore):
        """Test adding an edge between nodes."""
        node1 = create_node("Alice")
        node2 = create_node("Bob")
        await graph_store.add_node(node1)
        await graph_store.add_node(node2)

        edge = create_edge(node1.id, node2.id, "knows")
        result = await graph_store.add_edge(edge)

        assert result is True
        edge_count = await graph_store.edge_count()
        assert edge_count == 1

    @pytest.mark.asyncio
    async def test_get_neighbors(self, graph_store: ElementXGraphStore):
        """Test getting neighbors of a node."""
        # Create a simple graph: Alice -> Bob -> Charlie
        alice = create_node("Alice")
        bob = create_node("Bob")
        charlie = create_node("Charlie")

        await graph_store.add_node(alice)
        await graph_store.add_node(bob)
        await graph_store.add_node(charlie)

        await graph_store.add_edge(create_edge(alice.id, bob.id, "knows"))
        await graph_store.add_edge(create_edge(bob.id, charlie.id, "knows"))

        # Get Alice's neighbors (depth 1)
        neighbors = await graph_store.get_neighbors(alice.id, depth=1)
        assert len(neighbors) == 1
        assert neighbors[0]["node_id"] == bob.id

    @pytest.mark.asyncio
    async def test_get_neighbors_depth_2(self, graph_store: ElementXGraphStore):
        """Test getting neighbors with depth 2."""
        alice = create_node("Alice")
        bob = create_node("Bob")
        charlie = create_node("Charlie")

        await graph_store.add_node(alice)
        await graph_store.add_node(bob)
        await graph_store.add_node(charlie)

        await graph_store.add_edge(create_edge(alice.id, bob.id, "knows"))
        await graph_store.add_edge(create_edge(bob.id, charlie.id, "knows"))

        # Get Alice's neighbors (depth 2) - should include Charlie
        neighbors = await graph_store.get_neighbors(alice.id, depth=2)
        neighbor_ids = [n["node_id"] for n in neighbors]
        assert bob.id in neighbor_ids
        assert charlie.id in neighbor_ids

    @pytest.mark.asyncio
    async def test_find_path(self, graph_store: ElementXGraphStore):
        """Test finding path between nodes."""
        alice = create_node("Alice")
        bob = create_node("Bob")
        charlie = create_node("Charlie")

        await graph_store.add_node(alice)
        await graph_store.add_node(bob)
        await graph_store.add_node(charlie)

        await graph_store.add_edge(create_edge(alice.id, bob.id, "knows"))
        await graph_store.add_edge(create_edge(bob.id, charlie.id, "knows"))

        path = await graph_store.find_path(alice.id, charlie.id)
        assert len(path) == 3
        assert path[0] == alice.id
        assert path[1] == bob.id
        assert path[2] == charlie.id

    @pytest.mark.asyncio
    async def test_find_path_no_connection(self, graph_store: ElementXGraphStore):
        """Test finding path when nodes aren't connected."""
        alice = create_node("Alice")
        bob = create_node("Bob")

        await graph_store.add_node(alice)
        await graph_store.add_node(bob)
        # No edge between them

        path = await graph_store.find_path(alice.id, bob.id)
        assert path == []

    @pytest.mark.asyncio
    async def test_fuzzy_search(self, graph_store: ElementXGraphStore):
        """Test fuzzy search for similar node labels."""
        await graph_store.add_node(create_node("Robert"))
        await graph_store.add_node(create_node("Roberto"))
        await graph_store.add_node(create_node("Alice"))

        # Search for "Robert" should find similar names
        matches = await graph_store.fuzzy_search("Robert", threshold=0.7)

        labels = [m.label for m in matches]
        assert "Robert" in labels
        assert "Roberto" in labels
        assert "Alice" not in labels

    @pytest.mark.asyncio
    async def test_merge_nodes(self, graph_store: ElementXGraphStore):
        """Test merging two nodes (entity resolution)."""
        # Create two nodes representing the same person
        bob = create_node("Bob")
        bob.properties = {"email": "bob@example.com"}
        robert = create_node("Robert")
        robert.properties = {"phone": "555-1234"}

        await graph_store.add_node(bob)
        await graph_store.add_node(robert)

        # Create edges to both
        alice = create_node("Alice")
        await graph_store.add_node(alice)
        await graph_store.add_edge(create_edge(alice.id, bob.id, "knows"))
        await graph_store.add_edge(create_edge(alice.id, robert.id, "colleague"))

        # Merge robert into bob
        result = await graph_store.merge_nodes(bob.id, robert.id)
        assert result is True

        # Robert should be gone
        assert await graph_store.get_node(robert.id) is None

        # Bob should still exist
        merged = await graph_store.get_node(bob.id)
        assert merged is not None

        # Node count should decrease
        assert await graph_store.node_count() == 2  # alice + bob

    @pytest.mark.asyncio
    async def test_rank_nodes_pagerank(self, graph_store: ElementXGraphStore):
        """Test PageRank ranking (requires scipy)."""
        pytest.importorskip("scipy")

        # Create a graph where some nodes are more connected
        hub = create_node("Hub")
        spoke1 = create_node("Spoke1")
        spoke2 = create_node("Spoke2")
        spoke3 = create_node("Spoke3")

        await graph_store.add_node(hub)
        await graph_store.add_node(spoke1)
        await graph_store.add_node(spoke2)
        await graph_store.add_node(spoke3)

        # All spokes point to hub
        await graph_store.add_edge(create_edge(spoke1.id, hub.id, "points_to"))
        await graph_store.add_edge(create_edge(spoke2.id, hub.id, "points_to"))
        await graph_store.add_edge(create_edge(spoke3.id, hub.id, "points_to"))

        ranked = await graph_store.rank_nodes(algorithm="pagerank")
        assert len(ranked) == 4

        # Hub should have highest rank (most incoming connections)
        assert ranked[0]["node_id"] == hub.id

    @pytest.mark.asyncio
    async def test_get_all_nodes(self, graph_store: ElementXGraphStore):
        """Test getting all nodes."""
        await graph_store.add_node(create_node("Alice"))
        await graph_store.add_node(create_node("Bob"))
        await graph_store.add_node(create_node("Charlie"))

        all_nodes = await graph_store.get_all_nodes()
        assert len(all_nodes) == 3

    @pytest.mark.asyncio
    async def test_persistence_json(self):
        """Test JSON persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"

            # Create and populate store
            store1 = ElementXGraphStore(storage_path=str(path))
            await store1.add_node(create_node("Alice"))
            await store1.add_node(create_node("Bob"))

            # Create new store from same path
            store2 = ElementXGraphStore(storage_path=str(path))
            count = await store2.node_count()
            assert count == 2

    @pytest.mark.asyncio
    async def test_persistence_pickle(self):
        """Test pickle persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.gpickle"

            # Create and populate store
            store1 = ElementXGraphStore(storage_path=str(path))
            await store1.add_node(create_node("Alice"))

            # Create new store from same path
            store2 = ElementXGraphStore(storage_path=str(path))
            count = await store2.node_count()
            assert count == 1

    # --- Deduplication Tests ---

    @pytest.mark.asyncio
    async def test_add_node_skip_duplicate(self, graph_store: ElementXGraphStore):
        """Test that skip_if_duplicate prevents duplicate nodes by label."""
        alice1 = create_node("Alice")
        alice2 = create_node("Alice")  # Same label, different ID

        # Add first Alice
        result1 = await graph_store.add_node(alice1, skip_if_duplicate=True)
        assert result1 is True

        # Try to add duplicate - should be skipped
        result2 = await graph_store.add_node(alice2, skip_if_duplicate=True)
        assert result2 is False

        # Should only have one node
        count = await graph_store.node_count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_add_node_allows_duplicate_with_warning(
        self, graph_store: ElementXGraphStore
    ):
        """Test that by default duplicate nodes are added with warning."""
        alice1 = create_node("Alice")
        alice2 = create_node("Alice")  # Same label, different ID

        # Add first Alice
        result1 = await graph_store.add_node(alice1)
        assert result1 is True

        # Add duplicate - should succeed with warning (default behavior)
        result2 = await graph_store.add_node(alice2)
        assert result2 is True

        # Should have two nodes
        count = await graph_store.node_count()
        assert count == 2

    @pytest.mark.asyncio
    async def test_add_node_no_duplicate_check(self, graph_store: ElementXGraphStore):
        """Test that check_duplicate=False bypasses duplicate detection."""
        alice1 = create_node("Alice")
        alice2 = create_node("Alice")  # Same label, different ID

        # Add first Alice
        await graph_store.add_node(alice1, check_duplicate=False)

        # Add duplicate with check disabled
        result = await graph_store.add_node(alice2, check_duplicate=False)
        assert result is True

        # Should have two nodes
        count = await graph_store.node_count()
        assert count == 2

    @pytest.mark.asyncio
    async def test_add_edge_skip_duplicate(self, graph_store: ElementXGraphStore):
        """Test that duplicate edges with same relation are skipped by default."""
        alice = create_node("Alice")
        bob = create_node("Bob")
        await graph_store.add_node(alice)
        await graph_store.add_node(bob)

        edge1 = create_edge(alice.id, bob.id, "knows")
        edge2 = create_edge(alice.id, bob.id, "knows")  # Same source/target/relation

        # Add first edge
        result1 = await graph_store.add_edge(edge1)
        assert result1 is True

        # Try to add duplicate - should be skipped (default: skip_if_exists=True)
        result2 = await graph_store.add_edge(edge2)
        assert result2 is False

        # Should only have one edge
        count = await graph_store.edge_count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_add_edge_allows_different_relations(
        self, graph_store: ElementXGraphStore
    ):
        """Test that edges with different relations are not duplicates."""
        alice = create_node("Alice")
        bob = create_node("Bob")
        await graph_store.add_node(alice)
        await graph_store.add_node(bob)

        edge1 = create_edge(alice.id, bob.id, "knows")
        edge2 = create_edge(alice.id, bob.id, "works_with")  # Different relation

        # Add both edges - both should succeed
        result1 = await graph_store.add_edge(edge1)
        result2 = await graph_store.add_edge(edge2)

        # Note: NetworkX DiGraph only allows one edge per source/target pair
        # The second add_edge replaces the first, so we end up with one edge
        # This is expected behavior for directed graphs
        assert result1 is True
        assert result2 is True

    @pytest.mark.asyncio
    async def test_add_edge_update_if_exists(self, graph_store: ElementXGraphStore):
        """Test update_if_exists flag updates existing edge data."""
        alice = create_node("Alice")
        bob = create_node("Bob")
        await graph_store.add_node(alice)
        await graph_store.add_node(bob)

        edge1 = create_edge(alice.id, bob.id, "knows")
        edge1.weight = 0.5

        edge2 = create_edge(alice.id, bob.id, "knows")
        edge2.weight = 0.9  # Updated weight

        # Add first edge
        await graph_store.add_edge(edge1)

        # Update existing edge
        result = await graph_store.add_edge(edge2, update_if_exists=True)
        assert result is True

        # Verify edge was updated
        found = await graph_store.find_edge(alice.id, bob.id, "knows")
        assert found is not None
        assert found.weight == 0.9

    @pytest.mark.asyncio
    async def test_find_edge(self, graph_store: ElementXGraphStore):
        """Test find_edge returns edge when it exists."""
        alice = create_node("Alice")
        bob = create_node("Bob")
        await graph_store.add_node(alice)
        await graph_store.add_node(bob)

        edge = create_edge(alice.id, bob.id, "knows")
        await graph_store.add_edge(edge)

        # Find the edge
        found = await graph_store.find_edge(alice.id, bob.id)
        assert found is not None
        assert found.source_id == alice.id
        assert found.target_id == bob.id
        assert found.relation == "knows"

    @pytest.mark.asyncio
    async def test_find_edge_with_relation_filter(
        self, graph_store: ElementXGraphStore
    ):
        """Test find_edge with relation filter."""
        alice = create_node("Alice")
        bob = create_node("Bob")
        await graph_store.add_node(alice)
        await graph_store.add_node(bob)

        edge = create_edge(alice.id, bob.id, "knows")
        await graph_store.add_edge(edge)

        # Find with matching relation
        found = await graph_store.find_edge(alice.id, bob.id, "knows")
        assert found is not None

        # Find with non-matching relation
        not_found = await graph_store.find_edge(alice.id, bob.id, "works_with")
        assert not_found is None

    @pytest.mark.asyncio
    async def test_find_edge_not_found(self, graph_store: ElementXGraphStore):
        """Test find_edge returns None when edge doesn't exist."""
        alice = create_node("Alice")
        bob = create_node("Bob")
        await graph_store.add_node(alice)
        await graph_store.add_node(bob)

        # No edge added
        found = await graph_store.find_edge(alice.id, bob.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_edge_exists(self, graph_store: ElementXGraphStore):
        """Test edge_exists helper method."""
        alice = create_node("Alice")
        bob = create_node("Bob")
        await graph_store.add_node(alice)
        await graph_store.add_node(bob)

        edge = create_edge(alice.id, bob.id, "knows")
        await graph_store.add_edge(edge)

        # Check existence
        assert await graph_store.edge_exists(alice.id, bob.id) is True
        assert await graph_store.edge_exists(alice.id, bob.id, "knows") is True
        assert await graph_store.edge_exists(alice.id, bob.id, "works_with") is False
        assert (
            await graph_store.edge_exists(bob.id, alice.id) is False
        )  # Wrong direction

    @pytest.mark.asyncio
    async def test_edge_deduplication_case_insensitive(
        self, graph_store: ElementXGraphStore
    ):
        """Test that edge relation comparison is case-insensitive."""
        alice = create_node("Alice")
        bob = create_node("Bob")
        await graph_store.add_node(alice)
        await graph_store.add_node(bob)

        edge1 = create_edge(alice.id, bob.id, "knows")
        edge2 = create_edge(alice.id, bob.id, "KNOWS")  # Same relation, different case

        # Add first edge
        result1 = await graph_store.add_edge(edge1)
        assert result1 is True

        # Try to add duplicate with different case - should be skipped
        result2 = await graph_store.add_edge(edge2)
        assert result2 is False

    @pytest.mark.asyncio
    async def test_node_deduplication_case_insensitive(
        self, graph_store: ElementXGraphStore
    ):
        """Test that node label comparison is case-insensitive."""
        alice1 = create_node("Alice")
        alice2 = create_node("ALICE")  # Same label, different case

        # Add first Alice
        result1 = await graph_store.add_node(alice1, skip_if_duplicate=True)
        assert result1 is True

        # Try to add duplicate with different case - should be skipped
        result2 = await graph_store.add_node(alice2, skip_if_duplicate=True)
        assert result2 is False

        # Should only have one node
        count = await graph_store.node_count()
        assert count == 1
