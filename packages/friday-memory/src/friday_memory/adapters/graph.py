# mypy: ignore-errors
"""
ElementX / NetworkX Graph Store Implementation.
Implements GraphStoreAdapter with persistence and schema enforcement.

Ref: Batch 1 Specification, Section 2.2
"""

import asyncio
import json
import logging
import pickle
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from time import perf_counter
from typing import Any

import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class LockMetrics:
    """Track lock contention for observability."""

    acquisitions: int = 0
    contentions: int = 0
    total_wait_ms: float = 0
    max_wait_ms: float = 0

    def reset(self) -> None:
        """Reset all metrics."""
        self.acquisitions = 0
        self.contentions = 0
        self.total_wait_ms = 0
        self.max_wait_ms = 0


from friday_core import GraphStoreAdapter, TelemetryInterface  # noqa: E402

from friday_memory.models import GraphEdge, GraphNode  # noqa: E402


class ElementXGraphStore(GraphStoreAdapter):
    """
    NetworkX-based implementation of GraphStoreAdapter.

    Provides a persistent graph store with:
    - Pydantic schema enforcement for nodes/edges
    - Provenance tracking on all data
    - Hebbian learning via hit_count
    - Entity resolution via merge_nodes
    - Fuzzy search for duplicate prevention
    - PageRank for importance ranking

    Persistence formats: .gpickle (pickle) or .json
    """

    def __init__(
        self,
        storage_path: str | None = None,
        schema_config: dict[str, Any] | None = None,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        """
        Initialize the graph store.

        Args:
            storage_path: Path to persist graph (.gpickle or .json).
                         If None, graph is in-memory only.
            schema_config: Optional dict defining allowed node types/edge relations.
            telemetry: Optional telemetry recorder for white-box testing.
        """
        self._storage_path = Path(storage_path) if storage_path else None
        self._schema_config = schema_config or {}
        self._telemetry = telemetry
        self._graph = nx.DiGraph()

        # Thread safety: asyncio lock with metrics
        self._lock = asyncio.Lock()
        self._lock_metrics = LockMetrics()

        # Load existing graph if path exists
        if self._storage_path and self._storage_path.exists():
            self._load()

    def _emit_event(self, event_name: str, data: dict) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    @asynccontextmanager
    async def _acquire_lock(self, timeout: float = 10.0):
        """
        Acquire lock with timeout and metrics tracking.

        Args:
            timeout: Maximum seconds to wait for lock (default 10s)

        Yields:
            None after lock is acquired

        Raises:
            asyncio.TimeoutError: If lock not acquired within timeout
        """
        start = perf_counter()

        if self._lock.locked():
            self._lock_metrics.contentions += 1

        try:
            await asyncio.wait_for(self._lock.acquire(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"Lock acquisition timeout after {timeout}s")
            raise

        wait_ms = (perf_counter() - start) * 1000
        self._lock_metrics.acquisitions += 1
        self._lock_metrics.total_wait_ms += wait_ms
        self._lock_metrics.max_wait_ms = max(self._lock_metrics.max_wait_ms, wait_ms)

        try:
            yield
        finally:
            self._lock.release()

    def _save(self) -> None:
        """
        Atomically persist graph to storage path.

        Uses temp file + rename pattern to prevent corruption on crash.
        """
        if not self._storage_path:
            return

        # Write to temp file first
        temp_path = Path(str(self._storage_path) + ".tmp")

        try:
            if self._storage_path.suffix == ".json":
                # JSON format - store node/edge data as dicts
                data = {
                    "nodes": {
                        nid: dict(self._graph.nodes[nid]) for nid in self._graph.nodes
                    },
                    "edges": [
                        {"source": u, "target": v, **d}
                        for u, v, d in self._graph.edges(data=True)
                    ],
                }
                temp_path.write_text(json.dumps(data, default=str, indent=2))
            else:
                # Pickle format (default)
                with open(temp_path, "wb") as f:
                    pickle.dump(self._graph, f)

            # Atomic rename (on POSIX systems)
            temp_path.replace(self._storage_path)
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise

    def _load(self) -> None:
        """Load graph from storage path."""
        if not self._storage_path or not self._storage_path.exists():
            return

        if self._storage_path.suffix == ".json":
            data = json.loads(self._storage_path.read_text())
            self._graph = nx.DiGraph()
            for nid, attrs in data.get("nodes", {}).items():
                self._graph.add_node(nid, **attrs)
            for edge in data.get("edges", []):
                source = edge.pop("source")
                target = edge.pop("target")
                self._graph.add_edge(source, target, **edge)
        else:
            with open(self._storage_path, "rb") as f:
                self._graph = pickle.load(f)

    # --- CRUD Operations ---

    async def add_node(
        self,
        node: GraphNode,
        check_duplicate: bool = True,
        skip_if_duplicate: bool = False,
    ) -> bool:
        """
        Adds a node to the graph with optional duplicate detection.

        Duplicate detection is based on label (case-insensitive) and type.
        This prevents creating multiple nodes representing the same entity.

        When a duplicate is detected and skipped, the existing node's hit_count
        is incremented and last_accessed is updated (Hebbian learning - repeated
        extraction strengthens the entity's importance).

        Args:
            node: The GraphNode to add (must include provenance)
            check_duplicate: If True, check for existing node with same label/type
            skip_if_duplicate: If True and duplicate found, skip adding and return False.
                              If False and duplicate found, logs a warning but still adds.

        Returns:
            True if node was added, False if skipped as duplicate
        """  # noqa: E501
        async with self._acquire_lock():
            # Check for duplicate by label (case-insensitive) and type
            if check_duplicate:
                existing = self._find_by_label_unlocked(node.label, node.type)
                if existing and existing.id != node.id:
                    if skip_if_duplicate:
                        # Reinforce existing node (Hebbian learning)
                        # Repeated extraction = this entity is important
                        existing_data = self._graph.nodes[existing.id]
                        existing_data["hit_count"] = (
                            existing_data.get("hit_count", 0) + 1
                        )
                        existing_data["last_accessed"] = datetime.now().isoformat()
                        self._save()
                        logger.debug(
                            f"Reinforced duplicate node (hit_count={existing_data['hit_count']}): "  # noqa: E501
                            f"'{node.label}' (type={node.type}) exists with id={existing.id}"  # noqa: E501
                        )
                        self._emit_event(
                            "graph_node_reinforced",
                            {
                                "node_id": existing.id,
                                "type": node.type,
                                "label": node.label,
                                "hit_count": existing_data["hit_count"],
                            },
                        )
                        return False
                    else:
                        logger.warning(
                            f"Adding duplicate node: '{node.label}' (type={node.type}) "
                            f"already exists with id={existing.id}, new id={node.id}. "
                            f"Consider using find_by_label() first or merge_nodes() after."  # noqa: E501
                        )

            # Store node data as dict for NetworkX
            node_data = node.model_dump()
            self._graph.add_node(node.id, **node_data)
            self._save()

        self._emit_event(
            "graph_node_added",
            {"node_id": node.id, "type": node.type, "label": node.label},
        )
        return True

    async def update_node(self, node: GraphNode) -> bool:
        """
        Updates an existing node in the graph.

        Args:
            node: The GraphNode with updated data

        Returns:
            True if successful, False if node doesn't exist
        """
        async with self._acquire_lock():
            if node.id not in self._graph.nodes:
                return False

            # Update node data
            node_data = node.model_dump()
            self._graph.nodes[node.id].update(node_data)
            self._save()

        self._emit_event(
            "graph_node_updated",
            {"node_id": node.id, "type": node.type, "label": node.label},
        )
        return True

    async def add_edge(
        self,
        edge: GraphEdge,
        skip_if_exists: bool = True,
        update_if_exists: bool = False,
    ) -> bool:
        """
        Adds an edge between two nodes with duplicate prevention.

        Duplicate detection is based on source_id, target_id, and relation
        (case-insensitive relation comparison).

        When a duplicate is detected, the edge's hit_count is incremented and
        last_accessed is updated (Hebbian learning - repeated extraction
        strengthens the connection).

        Args:
            edge: The GraphEdge to add (must include provenance)
            skip_if_exists: If True, skip adding if duplicate exists (default: True)
            update_if_exists: If True, update existing edge with new data (default: False)
                             Takes precedence over skip_if_exists.

        Returns:
            True if edge was added/updated, False if skipped as duplicate
        """  # noqa: E501
        async with self._acquire_lock():
            # Check for existing edge with same source, target, and relation
            existing_edge = self._graph.has_edge(edge.source_id, edge.target_id)
            if existing_edge:
                existing_data = self._graph.edges[edge.source_id, edge.target_id]
                existing_relation = existing_data.get("relation", "").lower()
                new_relation = edge.relation.lower()

                if existing_relation == new_relation:
                    # Duplicate edge detected - always record access (Hebbian learning)
                    # Repeated extraction = reinforcement of this relationship
                    existing_data["hit_count"] = existing_data.get("hit_count", 0) + 1
                    existing_data["last_accessed"] = datetime.now().isoformat()

                    if update_if_exists:
                        # Update existing edge with new data (preserving hit_count/last_accessed)  # noqa: E501
                        edge_data = edge.model_dump()
                        edge_data.pop("source_id")
                        edge_data.pop("target_id")
                        # Don't overwrite hit_count/last_accessed we just set
                        edge_data.pop("hit_count", None)
                        edge_data.pop("last_accessed", None)
                        existing_data.update(edge_data)
                        self._save()
                        logger.debug(
                            f"Updated existing edge (hit_count={existing_data['hit_count']}): "  # noqa: E501
                            f"{edge.source_id} --[{edge.relation}]--> {edge.target_id}"
                        )
                        self._emit_event(
                            "graph_edge_updated",
                            {
                                "source_id": edge.source_id,
                                "target_id": edge.target_id,
                                "relation": edge.relation,
                                "hit_count": existing_data["hit_count"],
                            },
                        )
                        return True
                    elif skip_if_exists:
                        # Skip adding but still save the hit_count/last_accessed update
                        self._save()
                        logger.debug(
                            f"Reinforced duplicate edge (hit_count={existing_data['hit_count']}): "  # noqa: E501
                            f"{edge.source_id} --[{edge.relation}]--> {edge.target_id}"
                        )
                        self._emit_event(
                            "graph_edge_reinforced",
                            {
                                "source_id": edge.source_id,
                                "target_id": edge.target_id,
                                "relation": edge.relation,
                                "hit_count": existing_data["hit_count"],
                            },
                        )
                        return False
                    # If neither flag is set, fall through and replace the edge

            edge_data = edge.model_dump()
            # Remove source/target from data since they're used as keys
            edge_data.pop("source_id")
            edge_data.pop("target_id")

            self._graph.add_edge(edge.source_id, edge.target_id, **edge_data)
            self._save()

        self._emit_event(
            "graph_edge_added",
            {
                "source_id": edge.source_id,
                "target_id": edge.target_id,
                "relation": edge.relation,
            },
        )
        return True

    async def remove_node(self, node_id: str) -> bool:
        """
        Removes a node and all its connected edges.

        Args:
            node_id: The ID of the node to remove

        Returns:
            True if node existed and was removed
        """
        async with self._acquire_lock():
            if node_id not in self._graph:
                return False

            self._graph.remove_node(node_id)
            self._save()

        self._emit_event("graph_node_removed", {"node_id": node_id})
        return True

    # --- Traversal Operations ---

    async def get_neighbors(self, node_id: str, depth: int = 1) -> list[dict[str, Any]]:
        """
        Gets connected nodes within the specified depth.

        This is a PURE READ operation - no side effects.
        To record access for Hebbian learning, call record_node_access() separately.

        Args:
            node_id: The starting node ID
            depth: How many hops to traverse

        Returns:
            List of neighbor node dicts with relationship info
        """
        # Take snapshot under lock, process outside
        async with self._acquire_lock():
            if node_id not in self._graph:
                return []

            neighbors = []
            visited = {node_id}

            # BFS to specified depth
            current_level = [node_id]
            for _ in range(depth):
                next_level = []
                for nid in current_level:
                    # Get successors (outgoing edges)
                    for neighbor in self._graph.successors(nid):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            next_level.append(neighbor)
                            edge_data = dict(self._graph.edges[nid, neighbor])
                            neighbors.append(
                                {
                                    "node": dict(self._graph.nodes[neighbor]),
                                    "node_id": neighbor,
                                    "from_node": nid,
                                    "relation": edge_data.get("relation", ""),
                                    "edge_weight": edge_data.get("weight", 1.0),
                                }
                            )
                    # Get predecessors (incoming edges)
                    for neighbor in self._graph.predecessors(nid):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            next_level.append(neighbor)
                            edge_data = dict(self._graph.edges[neighbor, nid])
                            neighbors.append(
                                {
                                    "node": dict(self._graph.nodes[neighbor]),
                                    "node_id": neighbor,
                                    "from_node": nid,
                                    "relation": edge_data.get("relation", ""),
                                    "edge_weight": edge_data.get("weight", 1.0),
                                }
                            )
                current_level = next_level

        return neighbors

    async def record_node_access(self, node_id: str) -> bool:
        """
        Record access for Hebbian learning - separate from reads.

        Increments hit_count and updates last_accessed timestamp.
        Call this explicitly when a node is retrieved for use.

        Args:
            node_id: The ID of the accessed node

        Returns:
            True if access was recorded, False if node not found
        """
        async with self._acquire_lock():
            if node_id not in self._graph.nodes:
                return False

            self._graph.nodes[node_id]["hit_count"] = (
                self._graph.nodes[node_id].get("hit_count", 0) + 1
            )
            self._graph.nodes[node_id]["last_accessed"] = datetime.now().isoformat()
            self._save()

        return True

    async def record_edge_access(self, source_id: str, target_id: str) -> bool:
        """
        Record access for Hebbian learning on an edge.

        Increments hit_count and updates last_accessed timestamp.
        Call this explicitly when an edge is traversed for use.

        Args:
            source_id: Source node ID of the edge
            target_id: Target node ID of the edge

        Returns:
            True if access was recorded, False if edge not found
        """
        async with self._acquire_lock():
            if not self._graph.has_edge(source_id, target_id):
                return False

            edge_data = self._graph.edges[source_id, target_id]
            edge_data["hit_count"] = edge_data.get("hit_count", 0) + 1
            edge_data["last_accessed"] = datetime.now().isoformat()
            self._save()

        return True

    async def record_edges_access(self, edges: list[tuple[str, str]]) -> int:
        """
        Batch record access for multiple edges.

        More efficient than calling record_edge_access() in a loop
        as it acquires the lock only once.

        Args:
            edges: List of (source_id, target_id) tuples

        Returns:
            Number of edges successfully updated
        """
        if not edges:
            return 0

        async with self._acquire_lock():
            count = 0
            now = datetime.now().isoformat()
            for source_id, target_id in edges:
                if self._graph.has_edge(source_id, target_id):
                    edge_data = self._graph.edges[source_id, target_id]
                    edge_data["hit_count"] = edge_data.get("hit_count", 0) + 1
                    edge_data["last_accessed"] = now
                    count += 1
            if count > 0:
                self._save()

        return count

    async def update_edge_embedding(
        self, source_id: str, target_id: str, embedding: list[float]
    ) -> bool:
        """
        Update the embedding for an edge.

        Used for backfilling edge embeddings for path relevancy scoring.

        Args:
            source_id: Source node ID of the edge
            target_id: Target node ID of the edge
            embedding: The embedding vector to set

        Returns:
            True if embedding was updated, False if edge not found
        """
        async with self._acquire_lock():
            if not self._graph.has_edge(source_id, target_id):
                return False

            edge_data = self._graph.edges[source_id, target_id]
            edge_data["embedding"] = embedding
            self._save()

        return True

    async def update_edges_embeddings(
        self, edges_with_embeddings: list[tuple[str, str, list[float]]]
    ) -> int:
        """
        Batch update embeddings for multiple edges.

        More efficient than calling update_edge_embedding() in a loop
        as it acquires the lock only once and saves once.

        Args:
            edges_with_embeddings: List of (source_id, target_id, embedding) tuples

        Returns:
            Number of edges successfully updated
        """
        if not edges_with_embeddings:
            return 0

        async with self._acquire_lock():
            count = 0
            for source_id, target_id, embedding in edges_with_embeddings:
                if self._graph.has_edge(source_id, target_id):
                    edge_data = self._graph.edges[source_id, target_id]
                    edge_data["embedding"] = embedding
                    count += 1
            if count > 0:
                self._save()

        return count

    async def find_path(
        self, start_id: str, end_id: str, max_depth: int = 5
    ) -> list[str]:
        """
        Finds a path between two nodes.

        Args:
            start_id: Starting node ID
            end_id: Target node ID
            max_depth: Maximum path length

        Returns:
            List of node IDs in the path, or empty list if no path
        """
        if start_id not in self._graph or end_id not in self._graph:
            return []

        try:
            # Use undirected view for path finding
            undirected = self._graph.to_undirected()
            path = nx.shortest_path(undirected, start_id, end_id, weight=None)
            if len(path) - 1 > max_depth:
                return []
            return path
        except nx.NetworkXNoPath:
            return []

    # --- Maintenance & Intelligence Operations ---

    async def merge_nodes(self, primary_id: str, secondary_id: str) -> bool:
        """
        Entity Resolution: Merges two nodes representing the same entity.

        Algorithm:
        1. Identify all edges where secondary is source/target
        2. Create copies pointing to/from primary
        3. Copy unique properties from secondary to primary (primary wins)
        4. Delete secondary node
        5. Emit 'graph_node_merged' event

        Args:
            primary_id: The node to keep
            secondary_id: The node to merge and delete

        Returns:
            True if successful
        """
        async with self._acquire_lock():
            if primary_id not in self._graph or secondary_id not in self._graph:
                return False

            # Get secondary's edges
            in_edges = list(self._graph.in_edges(secondary_id, data=True))
            out_edges = list(self._graph.out_edges(secondary_id, data=True))

            # Redirect edges to primary
            for source, _, data in in_edges:
                if source != primary_id:  # Avoid self-loops
                    self._graph.add_edge(source, primary_id, **data)

            for _, target, data in out_edges:
                if target != primary_id:  # Avoid self-loops
                    self._graph.add_edge(primary_id, target, **data)

            # Merge properties (primary wins conflicts)
            secondary_data = self._graph.nodes[secondary_id]
            primary_data = self._graph.nodes[primary_id]

            for key, value in secondary_data.items():
                if key not in primary_data or primary_data[key] is None:
                    primary_data[key] = value

            # Remove secondary
            self._graph.remove_node(secondary_id)
            self._save()

        self._emit_event(
            "graph_node_merged",
            {"primary_id": primary_id, "secondary_id": secondary_id},
        )
        return True

    async def fuzzy_search(self, query: str, threshold: float = 0.8) -> list[GraphNode]:
        """
        Finds nodes with similar names/labels.

        Uses SequenceMatcher for fuzzy string matching.
        Takes snapshot under lock, processes outside for thread safety.

        Args:
            query: The search string
            threshold: Minimum similarity (0.0 to 1.0)

        Returns:
            List of matching GraphNodes
        """
        # Snapshot under lock
        async with self._acquire_lock():
            node_data_list = [
                (node_id, dict(self._graph.nodes[node_id]))
                for node_id in self._graph.nodes
            ]

        # Process outside lock
        matches = []
        query_lower = query.lower()

        for _node_id, node_data in node_data_list:
            label = node_data.get("label", "")

            # Calculate similarity
            similarity = SequenceMatcher(None, query_lower, label.lower()).ratio()

            if similarity >= threshold:
                try:
                    node = GraphNode(**node_data)
                    matches.append((similarity, node))
                except Exception:
                    # Skip nodes that don't validate
                    pass

        # Sort by similarity descending
        matches.sort(key=lambda x: x[0], reverse=True)
        return [node for _, node in matches]

    async def rank_nodes(self, algorithm: str = "pagerank") -> list[dict[str, Any]]:
        """
        Ranks nodes by importance using graph algorithms.

        Args:
            algorithm: "pagerank" (default) or "hits"

        Returns:
            List of dicts with node_id and rank, sorted descending
        """
        if len(self._graph) == 0:
            return []

        if algorithm == "pagerank":
            scores = nx.pagerank(self._graph)
        elif algorithm == "hits":
            # HITS returns (hubs, authorities) - use authorities
            _, authorities = nx.hits(self._graph)
            scores = authorities
        else:
            scores = nx.pagerank(self._graph)

        ranked = [
            {"node_id": node_id, "rank": score} for node_id, score in scores.items()
        ]
        ranked.sort(key=lambda x: x["rank"], reverse=True)
        return ranked

    # --- Utility Methods ---

    async def get_node(self, node_id: str) -> GraphNode | None:
        """Get a node by ID."""
        if node_id not in self._graph:
            return None
        try:
            return GraphNode(**self._graph.nodes[node_id])
        except Exception:
            return None

    async def get_nodes_by_ids(self, node_ids: set[str]) -> dict[str, GraphNode]:
        """
        Get multiple nodes by ID (batch indexed retrieval).

        More efficient than multiple get_node() calls when you need
        several specific nodes.

        Args:
            node_ids: Set of node IDs to retrieve

        Returns:
            Dict mapping node_id -> GraphNode (missing IDs excluded)
        """
        if not node_ids:
            return {}

        async with self._acquire_lock():
            node_data_list = [
                (node_id, dict(self._graph.nodes[node_id]))
                for node_id in node_ids
                if node_id in self._graph.nodes
            ]

        result = {}
        for node_id, node_data in node_data_list:
            with suppress(Exception):
                result[node_id] = GraphNode(**node_data)
        return result

    async def get_all_nodes(self) -> list[GraphNode]:
        """Get all nodes in the graph. Uses snapshot pattern for thread safety."""
        # Snapshot under lock
        async with self._acquire_lock():
            node_data_list = [
                dict(self._graph.nodes[node_id]) for node_id in self._graph.nodes
            ]

        # Process outside lock
        nodes = []
        for node_data in node_data_list:
            with suppress(Exception):
                nodes.append(GraphNode(**node_data))
        return nodes

    async def get_top_nodes(
        self,
        n: int = 10,
        sort_by: str = "hit_count",
    ) -> list[GraphNode]:
        """
        Get top N nodes sorted by specified criteria with tiebreaker.

        Sorting priority:
        - hit_count: Primary sort by hit_count DESC, tiebreaker by last_accessed DESC
        - last_accessed: Primary sort by last_accessed DESC, tiebreaker by hit_count DESC

        Args:
            n: Number of nodes to return
            sort_by: Sort criteria - "hit_count" or "last_accessed"

        Returns:
            List of top GraphNodes sorted by the specified criteria
        """  # noqa: E501
        all_nodes = await self.get_all_nodes()

        if sort_by == "hit_count":
            # Primary: hit_count DESC, Tiebreaker: last_accessed DESC
            sorted_nodes = sorted(
                all_nodes,
                key=lambda x: (x.hit_count, x.last_accessed or datetime.min),
                reverse=True,
            )
        elif sort_by == "last_accessed":
            # Primary: last_accessed DESC, Tiebreaker: hit_count DESC
            sorted_nodes = sorted(
                all_nodes,
                key=lambda x: (x.last_accessed or datetime.min, x.hit_count),
                reverse=True,
            )
        else:
            sorted_nodes = all_nodes

        return sorted_nodes[:n]

    async def get_all_edges(self) -> list[GraphEdge]:
        """Get all edges in the graph. Uses snapshot pattern for thread safety."""
        # Snapshot under lock
        async with self._acquire_lock():
            edge_data_list = [
                (source, target, dict(data))
                for source, target, data in self._graph.edges(data=True)
            ]

        # Process outside lock
        edges = []
        for source, target, data in edge_data_list:
            try:
                # Build edge kwargs, only including optional fields if present
                edge_kwargs = {
                    "source_id": source,
                    "target_id": target,
                    "relation": data.get("relation", "related_to"),
                    "weight": data.get("weight", 1.0),
                    "provenance": data.get("provenance"),
                    "hit_count": data.get("hit_count", 0),
                }
                # Only include embedding if present (None would be default anyway)
                if data.get("embedding") is not None:
                    edge_kwargs["embedding"] = data["embedding"]
                # Only include datetime fields if present (avoid overriding defaults with None)  # noqa: E501
                if data.get("last_accessed") is not None:
                    edge_kwargs["last_accessed"] = data["last_accessed"]
                if data.get("created_at") is not None:
                    edge_kwargs["created_at"] = data["created_at"]

                edges.append(GraphEdge(**edge_kwargs))
            except Exception:
                pass
        return edges

    async def get_edges_for_nodes(
        self, node_ids: set[str], direction: str = "outgoing"
    ) -> list[GraphEdge]:
        """
        Get edges connected to specific nodes (indexed retrieval).

        More efficient than get_all_edges() + filter when you only need
        edges for a subset of nodes.

        Args:
            node_ids: Set of node IDs to get edges for
            direction: "outgoing" (source_id in node_ids),
                      "incoming" (target_id in node_ids),
                      or "both"

        Returns:
            List of GraphEdges connected to the specified nodes
        """
        if not node_ids:
            return []

        # Snapshot under lock - only edges connected to specified nodes
        async with self._acquire_lock():
            edge_data_list = []
            for source, target, data in self._graph.edges(data=True):
                include = False
                if (
                    direction == "outgoing"
                    and source in node_ids
                    or direction == "incoming"
                    and target in node_ids
                    or direction == "both"
                    and (source in node_ids or target in node_ids)
                ):
                    include = True

                if include:
                    edge_data_list.append((source, target, dict(data)))

        # Process outside lock
        edges = []
        for source, target, data in edge_data_list:
            try:
                edge_kwargs = {
                    "source_id": source,
                    "target_id": target,
                    "relation": data.get("relation", "related_to"),
                    "weight": data.get("weight", 1.0),
                    "provenance": data.get("provenance"),
                    "hit_count": data.get("hit_count", 0),
                }
                if data.get("embedding") is not None:
                    edge_kwargs["embedding"] = data["embedding"]
                if data.get("last_accessed") is not None:
                    edge_kwargs["last_accessed"] = data["last_accessed"]
                if data.get("created_at") is not None:
                    edge_kwargs["created_at"] = data["created_at"]

                edges.append(GraphEdge(**edge_kwargs))
            except Exception:
                pass
        return edges

    async def get_node_labels(self, node_ids: set[str] | None = None) -> dict[str, str]:
        """
        Get a mapping of node IDs to labels (indexed retrieval).

        More efficient than get_all_nodes() when you only need labels
        for lookups.

        Args:
            node_ids: Optional set of node IDs to get labels for.
                     If None, returns labels for all nodes.

        Returns:
            Dict mapping node_id -> label
        """
        async with self._acquire_lock():
            if node_ids is None:
                return {
                    node_id: self._graph.nodes[node_id].get("label", node_id)
                    for node_id in self._graph.nodes
                }
            else:
                return {
                    node_id: self._graph.nodes[node_id].get("label", node_id)
                    for node_id in node_ids
                    if node_id in self._graph.nodes
                }

    def _find_by_label_unlocked(
        self, label: str, node_type: str | None = None
    ) -> GraphNode | None:
        """
        Internal: Find node by label without acquiring lock.

        MUST be called while already holding self._lock.

        Args:
            label: The label to search for
            node_type: Optional type filter

        Returns:
            The matching GraphNode or None if not found
        """
        label_lower = label.lower()
        for node_id in self._graph.nodes:
            node_data = self._graph.nodes[node_id]
            if node_data.get("label", "").lower() == label_lower:  # noqa: SIM102
                if node_type is None or node_data.get("type") == node_type:
                    try:
                        return GraphNode(**node_data)
                    except Exception:
                        pass
        return None

    async def find_by_label(
        self, label: str, node_type: str | None = None
    ) -> GraphNode | None:
        """
        Find a node by exact label match (case-insensitive).

        Args:
            label: The label to search for
            node_type: Optional type filter

        Returns:
            The matching GraphNode or None if not found
        """
        async with self._acquire_lock():
            return self._find_by_label_unlocked(label, node_type)

    async def find_edge(
        self,
        source_id: str,
        target_id: str,
        relation: str | None = None,
    ) -> GraphEdge | None:
        """
        Find an edge by source, target, and optionally relation.

        Args:
            source_id: The source node ID
            target_id: The target node ID
            relation: Optional relation type filter (case-insensitive)

        Returns:
            The matching GraphEdge or None if not found
        """
        if not self._graph.has_edge(source_id, target_id):
            return None

        edge_data = self._graph.edges[source_id, target_id]

        # If relation filter specified, check it matches
        if relation is not None:
            edge_relation = edge_data.get("relation", "")
            if edge_relation.lower() != relation.lower():
                return None

        try:
            return GraphEdge(
                source_id=source_id,
                target_id=target_id,
                relation=edge_data.get("relation", "related_to"),
                weight=edge_data.get("weight", 1.0),
                provenance=edge_data.get("provenance"),
                properties=edge_data.get("properties", {}),
            )
        except Exception:
            return None

    async def edge_exists(
        self,
        source_id: str,
        target_id: str,
        relation: str | None = None,
    ) -> bool:
        """
        Check if an edge exists between two nodes.

        Args:
            source_id: The source node ID
            target_id: The target node ID
            relation: Optional relation type to check (case-insensitive)

        Returns:
            True if the edge exists, False otherwise
        """
        if not self._graph.has_edge(source_id, target_id):
            return False

        if relation is None:
            return True

        edge_data = self._graph.edges[source_id, target_id]
        edge_relation = edge_data.get("relation", "")
        return edge_relation.lower() == relation.lower()

    async def node_count(self) -> int:
        """Get the number of nodes."""
        return len(self._graph.nodes)

    async def edge_count(self) -> int:
        """Get the number of edges."""
        return len(self._graph.edges)

    async def clear(self) -> dict[str, int]:
        """
        Clear all nodes and edges from the graph.

        Returns:
            Dict with counts of deleted nodes and edges
        """
        async with self._acquire_lock():
            node_count = len(self._graph.nodes)
            edge_count = len(self._graph.edges)

            self._graph.clear()
            self._save()

        self._emit_event(
            "graph_store_cleared",
            {"nodes_deleted": node_count, "edges_deleted": edge_count},
        )
        return {"nodes_deleted": node_count, "edges_deleted": edge_count}
