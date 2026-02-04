"""
Thread safety tests for friday-memory adapters.

Tests verify:
- Concurrent operations don't crash
- Lock metrics are properly tracked
- No data corruption under concurrent access
"""

import asyncio

import pytest

from friday_memory.adapters.episodic import InMemoryEpisodicStore
from friday_memory.adapters.graph import ElementXGraphStore, LockMetrics
from friday_memory.models import GraphEdge, GraphNode, InteractionTurn, ProvenanceMetadata


class TestGraphStoreThreadSafety:
    """Test ElementXGraphStore thread safety."""

    @pytest.fixture
    def graph_store(self):
        """Create an in-memory graph store."""
        return ElementXGraphStore()

    @pytest.fixture
    def provenance(self):
        """Create test provenance."""
        return ProvenanceMetadata(
            source_type="test",
            source_id="test-1",
            confidence=0.9,
        )

    @pytest.mark.asyncio
    async def test_concurrent_node_add_operations(self, graph_store, provenance):
        """Verify no crashes under concurrent node additions."""
        errors = []

        async def add_nodes(prefix: str, count: int):
            try:
                for i in range(count):
                    node = GraphNode(
                        id=f"{prefix}-{i}",
                        label=f"Node {prefix} {i}",
                        type="concept",
                        provenance=provenance,
                    )
                    await graph_store.add_node(node, check_duplicate=False)
            except Exception as e:
                errors.append(e)

        # Run 5 concurrent tasks, each adding 20 nodes
        await asyncio.gather(
            add_nodes("a", 20),
            add_nodes("b", 20),
            add_nodes("c", 20),
            add_nodes("d", 20),
            add_nodes("e", 20),
        )

        assert len(errors) == 0, f"Errors during concurrent add: {errors}"
        # Should have 100 nodes total
        count = await graph_store.node_count()
        assert count == 100

    @pytest.mark.asyncio
    async def test_concurrent_node_add_remove(self, graph_store, provenance):
        """Verify concurrent add/remove operations don't crash."""
        errors = []

        async def add_remove_cycle(prefix: str, count: int):
            try:
                for i in range(count):
                    node_id = f"{prefix}-{i}"
                    node = GraphNode(
                        id=node_id,
                        label=f"Node {prefix} {i}",
                        type="concept",
                        provenance=provenance,
                    )
                    await graph_store.add_node(node, check_duplicate=False)
                    await graph_store.remove_node(node_id)
            except Exception as e:
                errors.append(e)

        await asyncio.gather(
            add_remove_cycle("a", 20),
            add_remove_cycle("b", 20),
            add_remove_cycle("c", 20),
        )

        assert len(errors) == 0, f"Errors during add/remove: {errors}"

    @pytest.mark.asyncio
    async def test_concurrent_reads_during_writes(self, graph_store, provenance):
        """Verify reads don't crash during concurrent writes."""
        # Add initial data
        for i in range(10):
            node = GraphNode(
                id=f"init-{i}",
                label=f"Initial {i}",
                type="concept",
                provenance=provenance,
            )
            await graph_store.add_node(node, check_duplicate=False)

        errors = []

        async def reader():
            try:
                for _ in range(30):
                    await graph_store.get_all_nodes()
                    await asyncio.sleep(0.001)
            except Exception as e:
                errors.append(e)

        async def writer():
            try:
                for i in range(30):
                    node = GraphNode(
                        id=f"new-{i}",
                        label=f"New {i}",
                        type="concept",
                        provenance=provenance,
                    )
                    await graph_store.add_node(node, check_duplicate=False)
                    await asyncio.sleep(0.001)
            except Exception as e:
                errors.append(e)

        await asyncio.gather(reader(), reader(), writer())
        assert len(errors) == 0, f"Errors during concurrent read/write: {errors}"

    @pytest.mark.asyncio
    async def test_lock_metrics_tracking(self, graph_store, provenance):
        """Verify lock metrics are recorded."""
        # Perform some operations
        for i in range(5):
            node = GraphNode(
                id=f"metric-{i}",
                label=f"Metric {i}",
                type="concept",
                provenance=provenance,
            )
            await graph_store.add_node(node, check_duplicate=False)

        metrics = graph_store._lock_metrics
        assert metrics.acquisitions > 0, "Lock acquisitions should be recorded"
        assert metrics.total_wait_ms >= 0, "Wait time should be non-negative"

    @pytest.mark.asyncio
    async def test_record_node_access_separate_from_read(self, graph_store, provenance):
        """Verify hit_count is not incremented by get_neighbors (decoupled)."""
        # Add nodes with edges
        node1 = GraphNode(
            id="n1",
            label="Node 1",
            type="concept",
            provenance=provenance,
            hit_count=0,
        )
        node2 = GraphNode(
            id="n2",
            label="Node 2",
            type="concept",
            provenance=provenance,
        )
        await graph_store.add_node(node1, check_duplicate=False)
        await graph_store.add_node(node2, check_duplicate=False)

        edge = GraphEdge(
            source_id="n1",
            target_id="n2",
            relation="related_to",
            provenance=provenance,
        )
        await graph_store.add_edge(edge)

        # Get initial hit count
        initial_node = await graph_store.get_node("n1")
        initial_hit_count = initial_node.hit_count

        # Call get_neighbors - should NOT increment hit_count
        await graph_store.get_neighbors("n1")
        await graph_store.get_neighbors("n1")

        # Verify hit_count unchanged
        node_after = await graph_store.get_node("n1")
        assert node_after.hit_count == initial_hit_count, "get_neighbors should not increment hit_count"

        # Now explicitly record access
        await graph_store.record_node_access("n1")

        # Verify hit_count incremented
        node_accessed = await graph_store.get_node("n1")
        assert node_accessed.hit_count == initial_hit_count + 1, "record_node_access should increment hit_count"


class TestEpisodicStoreThreadSafety:
    """Test InMemoryEpisodicStore thread safety."""

    @pytest.fixture
    def episodic_store(self):
        """Create an in-memory episodic store."""
        return InMemoryEpisodicStore()

    @pytest.mark.asyncio
    async def test_concurrent_turn_additions(self, episodic_store):
        """Verify concurrent turn additions don't crash."""
        errors = []

        async def add_turns(session_prefix: str, count: int):
            try:
                session_id = f"session-{session_prefix}"
                for i in range(count):
                    turn = InteractionTurn(
                        id=f"{session_prefix}-turn-{i}",
                        session_id=session_id,
                        user_message=f"Message {i}",
                        assistant_response=f"Response {i}",
                    )
                    await episodic_store.add_turn(session_id, turn)
            except Exception as e:
                errors.append(e)

        await asyncio.gather(
            add_turns("a", 20),
            add_turns("b", 20),
            add_turns("c", 20),
        )

        assert len(errors) == 0, f"Errors during concurrent add: {errors}"

        # Verify counts
        count_a = await episodic_store.get_turn_count("session-a")
        count_b = await episodic_store.get_turn_count("session-b")
        count_c = await episodic_store.get_turn_count("session-c")
        assert count_a == 20
        assert count_b == 20
        assert count_c == 20

    @pytest.mark.asyncio
    async def test_concurrent_read_write(self, episodic_store):
        """Verify reads and writes can happen concurrently."""
        session_id = "concurrent-session"
        errors = []

        async def writer():
            try:
                for i in range(50):
                    turn = InteractionTurn(
                        id=f"turn-{i}",
                        session_id=session_id,
                        user_message=f"Message {i}",
                        assistant_response=f"Response {i}",
                    )
                    await episodic_store.add_turn(session_id, turn)
                    await asyncio.sleep(0.001)
            except Exception as e:
                errors.append(e)

        async def reader():
            try:
                for _ in range(50):
                    await episodic_store.get_turns(session_id)
                    await asyncio.sleep(0.001)
            except Exception as e:
                errors.append(e)

        await asyncio.gather(writer(), reader(), reader())
        assert len(errors) == 0, f"Errors during concurrent read/write: {errors}"


class TestLockMetrics:
    """Test LockMetrics dataclass."""

    def test_lock_metrics_defaults(self):
        """Test LockMetrics has correct defaults."""
        metrics = LockMetrics()
        assert metrics.acquisitions == 0
        assert metrics.contentions == 0
        assert metrics.total_wait_ms == 0
        assert metrics.max_wait_ms == 0

    def test_lock_metrics_reset(self):
        """Test LockMetrics reset."""
        metrics = LockMetrics(
            acquisitions=10,
            contentions=2,
            total_wait_ms=100.5,
            max_wait_ms=50.0,
        )

        metrics.reset()

        assert metrics.acquisitions == 0
        assert metrics.contentions == 0
        assert metrics.total_wait_ms == 0
        assert metrics.max_wait_ms == 0


class TestConcurrencyStress:
    """Stress tests for concurrent operations."""

    @pytest.fixture
    def graph_store(self):
        """Create an in-memory graph store."""
        return ElementXGraphStore()

    @pytest.fixture
    def provenance(self):
        """Create test provenance."""
        return ProvenanceMetadata(source_type="test", source_id="stress-test", confidence=0.9)

    @pytest.mark.asyncio
    async def test_high_concurrency_graph_operations(self, graph_store, provenance):
        """Test graph store under high concurrency."""
        errors = []
        operations_per_task = 50
        num_tasks = 10

        async def mixed_operations(task_id: int):
            try:
                for i in range(operations_per_task):
                    # Add node
                    node = GraphNode(
                        id=f"stress-{task_id}-{i}",
                        label=f"Stress {task_id} {i}",
                        type="concept",
                        provenance=provenance,
                    )
                    await graph_store.add_node(node, check_duplicate=False)

                    # Read all nodes
                    if i % 5 == 0:
                        await graph_store.get_all_nodes()

                    # Fuzzy search
                    if i % 10 == 0:
                        await graph_store.fuzzy_search("Stress", threshold=0.5)

            except Exception as e:
                errors.append((task_id, i, e))

        tasks = [mixed_operations(i) for i in range(num_tasks)]
        await asyncio.gather(*tasks)

        assert len(errors) == 0, f"Errors during stress test: {errors}"

        # Verify expected node count
        count = await graph_store.node_count()
        expected = operations_per_task * num_tasks
        assert count == expected, f"Expected {expected} nodes, got {count}"
