"""
ElementX / NetworkX Graph Store Implementation.
Implements GraphStoreAdapter with persistence and schema enforcement.

Ref: Batch 1 Specification, Section 2.2
"""

import json
import logging
import pickle
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import networkx as nx

logger = logging.getLogger(__name__)

from friday_core import GraphStoreAdapter, TelemetryInterface

from friday_memory.models import GraphEdge, GraphNode


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

        # Load existing graph if path exists
        if self._storage_path and self._storage_path.exists():
            self._load()

    def _emit_event(self, event_name: str, data: dict) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    def _save(self) -> None:
        """Persist graph to storage path."""
        if not self._storage_path:
            return

        if self._storage_path.suffix == ".json":
            # JSON format - store node/edge data as dicts
            data = {
                "nodes": {
                    nid: self._graph.nodes[nid] for nid in self._graph.nodes
                },
                "edges": [
                    {"source": u, "target": v, **d}
                    for u, v, d in self._graph.edges(data=True)
                ],
            }
            self._storage_path.write_text(json.dumps(data, default=str, indent=2))
        else:
            # Pickle format (default)
            with open(self._storage_path, "wb") as f:
                pickle.dump(self._graph, f)

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

        Args:
            node: The GraphNode to add (must include provenance)
            check_duplicate: If True, check for existing node with same label/type
            skip_if_duplicate: If True and duplicate found, skip adding and return False.
                              If False and duplicate found, logs a warning but still adds.

        Returns:
            True if node was added, False if skipped as duplicate
        """
        # Check for duplicate by label (case-insensitive) and type
        if check_duplicate:
            existing = await self.find_by_label(node.label, node.type)
            if existing and existing.id != node.id:
                if skip_if_duplicate:
                    logger.debug(
                        f"Skipping duplicate node: '{node.label}' (type={node.type}) "
                        f"already exists with id={existing.id}"
                    )
                    return False
                else:
                    logger.warning(
                        f"Adding duplicate node: '{node.label}' (type={node.type}) "
                        f"already exists with id={existing.id}, new id={node.id}. "
                        f"Consider using find_by_label() first or merge_nodes() after."
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

        Args:
            edge: The GraphEdge to add (must include provenance)
            skip_if_exists: If True, skip adding if duplicate exists (default: True)
            update_if_exists: If True, update existing edge with new data (default: False)
                             Takes precedence over skip_if_exists.

        Returns:
            True if edge was added/updated, False if skipped as duplicate
        """
        # Check for existing edge with same source, target, and relation
        existing_edge = self._graph.has_edge(edge.source_id, edge.target_id)
        if existing_edge:
            existing_data = self._graph.edges[edge.source_id, edge.target_id]
            existing_relation = existing_data.get("relation", "").lower()
            new_relation = edge.relation.lower()

            if existing_relation == new_relation:
                # Duplicate edge detected
                if update_if_exists:
                    # Update existing edge with new data
                    edge_data = edge.model_dump()
                    edge_data.pop("source_id")
                    edge_data.pop("target_id")
                    self._graph.edges[edge.source_id, edge.target_id].update(edge_data)
                    self._save()
                    logger.debug(
                        f"Updated existing edge: {edge.source_id} --[{edge.relation}]--> {edge.target_id}"
                    )
                    self._emit_event(
                        "graph_edge_updated",
                        {
                            "source_id": edge.source_id,
                            "target_id": edge.target_id,
                            "relation": edge.relation,
                        },
                    )
                    return True
                elif skip_if_exists:
                    logger.debug(
                        f"Skipping duplicate edge: {edge.source_id} --[{edge.relation}]--> {edge.target_id}"
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
        if node_id not in self._graph:
            return False

        self._graph.remove_node(node_id)
        self._save()

        self._emit_event("graph_node_removed", {"node_id": node_id})
        return True

    # --- Traversal Operations ---

    async def get_neighbors(
        self, node_id: str, depth: int = 1
    ) -> list[dict[str, Any]]:
        """
        Gets connected nodes within the specified depth.

        Args:
            node_id: The starting node ID
            depth: How many hops to traverse

        Returns:
            List of neighbor node dicts with relationship info
        """
        if node_id not in self._graph:
            return []

        # Touch the source node (Hebbian learning)
        if "hit_count" in self._graph.nodes[node_id]:
            self._graph.nodes[node_id]["hit_count"] += 1
            self._graph.nodes[node_id]["last_accessed"] = datetime.now().isoformat()

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
                        edge_data = self._graph.edges[nid, neighbor]
                        neighbors.append(
                            {
                                "node": self._graph.nodes[neighbor],
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
                        edge_data = self._graph.edges[neighbor, nid]
                        neighbors.append(
                            {
                                "node": self._graph.nodes[neighbor],
                                "node_id": neighbor,
                                "from_node": nid,
                                "relation": edge_data.get("relation", ""),
                                "edge_weight": edge_data.get("weight", 1.0),
                            }
                        )
            current_level = next_level

        self._save()
        return neighbors

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
            path = nx.shortest_path(
                undirected, start_id, end_id, weight=None
            )
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

    async def fuzzy_search(
        self, query: str, threshold: float = 0.8
    ) -> list[GraphNode]:
        """
        Finds nodes with similar names/labels.

        Uses SequenceMatcher for fuzzy string matching.

        Args:
            query: The search string
            threshold: Minimum similarity (0.0 to 1.0)

        Returns:
            List of matching GraphNodes
        """
        matches = []
        query_lower = query.lower()

        for node_id in self._graph.nodes:
            node_data = self._graph.nodes[node_id]
            label = node_data.get("label", "")

            # Calculate similarity
            similarity = SequenceMatcher(
                None, query_lower, label.lower()
            ).ratio()

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

    async def rank_nodes(
        self, algorithm: str = "pagerank"
    ) -> list[dict[str, Any]]:
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
            {"node_id": node_id, "rank": score}
            for node_id, score in scores.items()
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

    async def get_all_nodes(self) -> list[GraphNode]:
        """Get all nodes in the graph."""
        nodes = []
        for node_id in self._graph.nodes:
            try:
                nodes.append(GraphNode(**self._graph.nodes[node_id]))
            except Exception:
                pass
        return nodes

    async def get_top_nodes(
        self,
        n: int = 10,
        sort_by: str = "hit_count",
    ) -> list[GraphNode]:
        """
        Get top N nodes sorted by specified criteria.

        Args:
            n: Number of nodes to return
            sort_by: Sort criteria - "hit_count" or "last_accessed"

        Returns:
            List of top GraphNodes sorted by the specified criteria
        """
        all_nodes = await self.get_all_nodes()

        if sort_by == "hit_count":
            sorted_nodes = sorted(
                all_nodes, key=lambda x: x.hit_count, reverse=True
            )
        elif sort_by == "last_accessed":
            sorted_nodes = sorted(
                all_nodes,
                key=lambda x: x.last_accessed or datetime.min,
                reverse=True,
            )
        else:
            sorted_nodes = all_nodes

        return sorted_nodes[:n]

    async def get_all_edges(self) -> list[GraphEdge]:
        """Get all edges in the graph."""
        edges = []
        for source, target, data in self._graph.edges(data=True):
            try:
                edges.append(GraphEdge(
                    source_id=source,
                    target_id=target,
                    relation=data.get("relation", "related_to"),
                    weight=data.get("weight", 1.0),
                    provenance=data.get("provenance"),
                ))
            except Exception:
                pass
        return edges

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
        label_lower = label.lower()
        for node_id in self._graph.nodes:
            node_data = self._graph.nodes[node_id]
            if node_data.get("label", "").lower() == label_lower:
                if node_type is None or node_data.get("type") == node_type:
                    try:
                        return GraphNode(**node_data)
                    except Exception:
                        pass
        return None

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
        node_count = len(self._graph.nodes)
        edge_count = len(self._graph.edges)

        self._graph.clear()
        self._save()

        self._emit_event(
            "graph_store_cleared",
            {"nodes_deleted": node_count, "edges_deleted": edge_count},
        )
        return {"nodes_deleted": node_count, "edges_deleted": edge_count}
