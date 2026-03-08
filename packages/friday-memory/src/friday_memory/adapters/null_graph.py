# mypy: ignore-errors
"""
No-op graph store for vector-only and testing scenarios.
Implements GraphStoreAdapter with all operations succeeding silently.

Ref: Phase 1 - Scalable Adapters Build Plan
"""

from typing import Any

from friday_core.interfaces.memory import GraphStoreAdapter

from friday_memory.models.graph import GraphEdge, GraphNode


class NullGraphStore(GraphStoreAdapter):
    """
    No-op graph store that accepts but discards all data.

    All write operations succeed silently.
    All read operations return empty results.

    Use Cases:
    - Vector-only deployments
    - Testing without graph complexity
    - Minimal memory footprint scenarios
    - Agents that don't need relationship tracking

    Example:
        store = NullGraphStore()
        await store.add_node(node)  # Succeeds silently
        neighbors = await store.get_neighbors("any_id")  # Returns []
    """

    # --- CRUD Operations (Protocol Requirements) ---

    async def add_node(self, node: GraphNode) -> bool:
        """
        Accept node but don't store it.

        Args:
            node: The GraphNode to add (ignored)

        Returns:
            True (always succeeds)
        """
        return True

    async def add_edge(self, edge: GraphEdge) -> bool:
        """
        Accept edge but don't store it.

        Args:
            edge: The GraphEdge to add (ignored)

        Returns:
            True (always succeeds)
        """
        return True

    async def remove_node(self, node_id: str) -> bool:
        """
        Accept delete but do nothing.

        Args:
            node_id: The ID of the node to remove (ignored)

        Returns:
            True (always succeeds)
        """
        return True

    # --- Traversal Operations (Protocol Requirements) ---

    async def get_neighbors(self, node_id: str, depth: int = 1) -> list[dict[str, Any]]:
        """
        Always returns empty list.

        Args:
            node_id: The starting node ID (ignored)
            depth: How many hops to traverse (ignored)

        Returns:
            Empty list
        """
        return []

    async def find_path(
        self, start_id: str, end_id: str, max_depth: int = 5
    ) -> list[str]:
        """
        Always returns empty path.

        Args:
            start_id: Starting node ID (ignored)
            end_id: Target node ID (ignored)
            max_depth: Maximum path length (ignored)

        Returns:
            Empty list (no path)
        """
        return []

    # --- Maintenance & Intelligence Operations (Protocol Requirements) ---

    async def merge_nodes(self, primary_id: str, secondary_id: str) -> bool:
        """
        Accept merge but do nothing.

        Args:
            primary_id: The node to keep (ignored)
            secondary_id: The node to merge and delete (ignored)

        Returns:
            True (always succeeds)
        """
        return True

    async def fuzzy_search(self, query: str, threshold: float = 0.8) -> list[GraphNode]:
        """
        Always returns empty list.

        Args:
            query: The search string (ignored)
            threshold: Minimum similarity (ignored)

        Returns:
            Empty list (no matches)
        """
        return []

    async def rank_nodes(self, algorithm: str = "pagerank") -> list[dict[str, Any]]:
        """
        Always returns empty list.

        Args:
            algorithm: The ranking algorithm (ignored)

        Returns:
            Empty list (no rankings)
        """
        return []

    # --- Utility Methods (matching ElementXGraphStore API) ---

    async def get_node(self, node_id: str) -> GraphNode | None:
        """Always returns None (no storage)."""
        return None

    async def update_node(self, node: GraphNode) -> bool:
        """Accept update but do nothing."""
        return True

    async def get_all_nodes(self) -> list[GraphNode]:
        """Always returns empty list."""
        return []

    async def get_top_nodes(
        self,
        n: int = 10,
        sort_by: str = "hit_count",
    ) -> list[GraphNode]:
        """Always returns empty list."""
        return []

    async def get_all_edges(self) -> list[GraphEdge]:
        """Always returns empty list."""
        return []

    async def find_by_label(
        self, label: str, node_type: str | None = None
    ) -> GraphNode | None:
        """Always returns None."""
        return None

    async def find_edge(
        self,
        source_id: str,
        target_id: str,
        relation: str | None = None,
    ) -> GraphEdge | None:
        """Always returns None."""
        return None

    async def edge_exists(
        self,
        source_id: str,
        target_id: str,
        relation: str | None = None,
    ) -> bool:
        """Always returns False."""
        return False

    async def record_node_access(self, node_id: str) -> bool:
        """Accept but return False (no node found)."""
        return False

    async def record_edge_access(self, source_id: str, target_id: str) -> bool:
        """Accept but return False (no edge found)."""
        return False

    async def record_edges_access(self, edges: list[tuple[str, str]]) -> int:
        """Accept but return 0 (no edges updated)."""
        return 0

    async def update_edge_embedding(
        self, source_id: str, target_id: str, embedding: list[float]
    ) -> bool:
        """Accept but return False (no edge found)."""
        return False

    async def update_edges_embeddings(
        self, edges_with_embeddings: list[tuple[str, str, list[float]]]
    ) -> int:
        """Accept but return 0 (no edges updated)."""
        return 0

    async def node_count(self) -> int:
        """Always returns 0."""
        return 0

    async def edge_count(self) -> int:
        """Always returns 0."""
        return 0

    async def clear(self) -> dict[str, int]:
        """No-op (nothing to clear)."""
        return {"nodes_deleted": 0, "edges_deleted": 0}
