"""
The Memory Controller Facade.
Orchestrates parallel retrieval from Vector, Graph, and Episodic stores.
Handles 'Store Fact', 'Recall', and 'Rollback' operations.

Ref: Batch 2 Specification, Section 2
"""

import asyncio
import time
import uuid
from typing import Any

from friday_core import (
    EpisodicStoreAdapter,
    GraphStoreAdapter,
    TelemetryInterface,
    VectorStoreAdapter,
)

from friday_memory.models import (
    ContextPayload,
    GraphEdge,
    GraphNode,
    InteractionTurn,
    ProvenanceMetadata,
)


class MemoryController:
    """
    Unified facade for all memory operations.

    Sits between the Data Layer (Batch 1 Adapters) and Context Strategies (Batch 2a).
    Provides a unified API to read/write across Vector, Graph, and Episodic stores.

    Core Operations:
    - recall(): Parallel retrieval from all stores
    - store_fact(): Write entities/facts to Graph
    - store_insight(): Write summaries to Vector
    - Consolidation proxies for Episodic management
    """

    def __init__(
        self,
        vector_store: VectorStoreAdapter,
        graph_store: GraphStoreAdapter,
        episodic_store: EpisodicStoreAdapter,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        """
        Initialize the Memory Controller.

        Args:
            vector_store: VectorStoreAdapter for semantic search
            graph_store: GraphStoreAdapter for entity/relationship storage
            episodic_store: EpisodicStoreAdapter for conversation history
            telemetry: Optional telemetry recorder for observability
        """
        self.vector = vector_store
        self.graph = graph_store
        self.episodic = episodic_store
        self._telemetry = telemetry

    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    # --- Core API: Retrieval (The "Recall" Loop) ---

    async def recall(
        self,
        query: str,
        session_id: str | None = None,
        token_limit: int = 2000,
        include_history: bool = True,
        history_limit: int = 10,
        vector_results: int = 5,
        graph_depth: int = 1,
    ) -> ContextPayload:
        """
        Orchestrates parallel retrieval from all memory stores.

        Algorithm:
        1. Episodic: Fetches recent turns (if include_history=True)
        2. Vector: Queries chunks using semantic search
        3. Graph: Extracts entities, traverses neighbors, triggers Hebbian learning
        4. Fusion: Deduplicates entities found in both Vector/Graph

        Args:
            query: The search query
            session_id: Session ID for episodic history (required if include_history=True)
            token_limit: Maximum tokens for retrieved content (for budgeting)
            include_history: Whether to include conversation history
            history_limit: Maximum history turns to retrieve
            vector_results: Number of vector search results
            graph_depth: Depth for graph traversal

        Returns:
            ContextPayload with aggregated retrieval results
        """
        start_time = time.time()
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("memory_recall")

        debug_info: dict[str, Any] = {
            "query_length": len(query),
            "token_limit": token_limit,
        }

        try:
            # Parallel retrieval from all stores
            tasks = []

            # Episodic retrieval
            async def _empty_list() -> list:
                return []

            if include_history and session_id:
                tasks.append(self._retrieve_episodic(session_id, history_limit))
            else:
                tasks.append(_empty_list())

            # Vector retrieval
            tasks.append(self._retrieve_vector(query, vector_results))

            # Graph retrieval (entities from query)
            tasks.append(self._retrieve_graph(query, graph_depth))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Unpack results (handle exceptions gracefully)
            history = results[0] if not isinstance(results[0], Exception) else []
            passages = results[1] if not isinstance(results[1], Exception) else []
            graph_data = results[2] if not isinstance(results[2], Exception) else {}

            entities = graph_data.get("entities", []) if isinstance(graph_data, dict) else []
            facts = graph_data.get("facts", []) if isinstance(graph_data, dict) else []

            # Record debug info
            debug_info["history_count"] = len(history)
            debug_info["passages_count"] = len(passages)
            debug_info["entities_count"] = len(entities)
            debug_info["facts_count"] = len(facts)
            debug_info["total_latency"] = time.time() - start_time

            self._emit_event("memory_recall_completed", debug_info)

            return ContextPayload(
                history=history,
                passages=passages,
                entities=entities,
                facts=facts,
                recent_memories=[],  # Populated by Consolidator
                debug_info=debug_info,
            )

        finally:
            if span_id:
                self._telemetry.end_span(span_id, {"latency": time.time() - start_time})

    async def _retrieve_episodic(
        self, session_id: str, limit: int
    ) -> list[InteractionTurn]:
        """Retrieve recent conversation history."""
        start_time = time.time()
        turns = await self.episodic.get_turns(session_id, limit=limit)
        if self._telemetry:
            self._emit_event(
                "episodic_retrieval",
                {"session_id": session_id, "turns": len(turns), "latency": time.time() - start_time},
            )
        return turns

    async def _retrieve_vector(
        self, query: str, n_results: int
    ) -> list[dict[str, Any]]:
        """Retrieve semantically similar passages."""
        start_time = time.time()
        results = await self.vector.query(query, n_results=n_results)
        if self._telemetry:
            self._emit_event(
                "vector_retrieval",
                {"query_length": len(query), "results": len(results), "latency": time.time() - start_time},
            )
        return results

    async def _retrieve_graph(
        self, query: str, depth: int
    ) -> dict[str, Any]:
        """
        Retrieve entities and facts from the graph.

        Uses fuzzy search to find matching entities, then traverses
        neighbors to gather related facts.
        """
        start_time = time.time()
        entities: list[GraphNode] = []
        facts: list[GraphEdge] = []

        # Fuzzy search for entities matching the query
        # Split query into words and search for each
        query_terms = query.lower().split()

        for term in query_terms[:5]:  # Limit to first 5 terms
            if len(term) < 3:
                continue
            matches = await self.graph.fuzzy_search(term, threshold=0.6)
            for node in matches[:3]:  # Limit matches per term
                if node not in entities:
                    entities.append(node)
                    # Touch node for Hebbian learning
                    node.touch()

        # Traverse neighbors for each found entity
        seen_edges: set[tuple[str, str, str]] = set()
        for entity in entities[:10]:  # Limit traversal
            neighbors = await self.graph.get_neighbors(entity.id, depth=depth)
            for neighbor_data in neighbors:
                edge_key = (
                    neighbor_data.get("from_node", ""),
                    neighbor_data.get("node_id", ""),
                    neighbor_data.get("relation", ""),
                )
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    # Create edge representation
                    facts.append(
                        GraphEdge(
                            source_id=neighbor_data.get("from_node", ""),
                            target_id=neighbor_data.get("node_id", ""),
                            relation=neighbor_data.get("relation", "related_to"),
                            weight=neighbor_data.get("edge_weight", 1.0),
                            provenance=ProvenanceMetadata(
                                source_id="graph_traversal",
                                source_type="inferred",
                                confidence=0.8,
                            ),
                        )
                    )

        if self._telemetry:
            self._emit_event(
                "graph_retrieval",
                {
                    "entities": len(entities),
                    "facts": len(facts),
                    "latency": time.time() - start_time,
                },
            )

        return {"entities": entities, "facts": facts}

    # --- Core API: Storage (The "Memorize" Loop) ---

    async def store_fact(
        self, node: GraphNode, edge: GraphEdge | None = None
    ) -> bool:
        """
        Writes a specific entity/fact to the Graph.

        Validates that node.provenance is populated (Batch 1/2a requirement).

        Args:
            node: The GraphNode to store
            edge: Optional GraphEdge to connect the node

        Returns:
            True if successful

        Raises:
            ValueError: If provenance is missing
        """
        # Validate provenance
        if node.provenance is None:
            raise ValueError(
                "Provenance is required for all stored data. "
                "GraphNode.provenance cannot be None."
            )

        # Store node
        await self.graph.add_node(node)

        # Store edge if provided
        if edge is not None:
            if edge.provenance is None:
                raise ValueError(
                    "Provenance is required for all stored data. "
                    "GraphEdge.provenance cannot be None."
                )
            await self.graph.add_edge(edge)

        self._emit_event(
            "fact_stored",
            {
                "node_id": node.id,
                "node_type": node.type,
                "has_edge": edge is not None,
            },
        )
        return True

    async def store_insight(
        self, text: str, metadata: ProvenanceMetadata | None = None
    ) -> bool:
        """
        Writes a semantic block (e.g., summary) to the Vector store.

        Args:
            text: The text content to store
            metadata: Provenance metadata (required)

        Returns:
            True if successful

        Raises:
            ValueError: If metadata/provenance is missing
        """
        if metadata is None:
            raise ValueError(
                "Provenance metadata is required for all stored data. "
                "The metadata parameter cannot be None."
            )

        # Generate unique ID
        insight_id = str(uuid.uuid4())

        # Prepare metadata dict with provenance
        meta_dict = {
            "type": "insight",
            "provenance_source_id": metadata.source_id,
            "provenance_source_type": metadata.source_type,
            "provenance_confidence": metadata.confidence,
            "provenance_author_id": metadata.author_id or "",
        }

        # Store in vector store
        await self.vector.add_documents(
            texts=[text],
            metadatas=[meta_dict],
            ids=[insight_id],
        )

        self._emit_event(
            "insight_stored",
            {
                "insight_id": insight_id,
                "text_length": len(text),
                "source_type": metadata.source_type,
            },
        )
        return True

    # --- Core API: Maintenance (The "Consolidate" Loop) ---

    async def fetch_unconsolidated_events(
        self, session_id: str
    ) -> list[InteractionTurn]:
        """
        Proxies EpisodicStoreAdapter.get_unconsolidated_turns.

        Args:
            session_id: The session to fetch events from

        Returns:
            List of unprocessed InteractionTurns
        """
        return await self.episodic.get_unconsolidated_turns(session_id)

    async def mark_events_consolidated(self, event_ids: list[str]) -> bool:
        """
        Proxies EpisodicStoreAdapter.mark_consolidated.

        Args:
            event_ids: List of turn IDs to mark as consolidated

        Returns:
            True if successful
        """
        return await self.episodic.mark_consolidated(event_ids)

    async def merge_identities(
        self, primary_id: str, secondary_id: str
    ) -> bool:
        """
        Proxies GraphStoreAdapter.merge_nodes.

        Used when the Agent realizes two nodes represent the same entity
        (e.g., 'Bob' and 'Robert' are the same person).

        Args:
            primary_id: The node ID to keep
            secondary_id: The node ID to merge and delete

        Returns:
            True if successful
        """
        result = await self.graph.merge_nodes(primary_id, secondary_id)
        if result:
            self._emit_event(
                "identities_merged",
                {"primary_id": primary_id, "secondary_id": secondary_id},
            )
        return result

    # --- Utility Methods ---

    async def add_turn(self, session_id: str, turn: InteractionTurn) -> bool:
        """
        Add a conversation turn to episodic memory.

        Convenience method that proxies to the episodic store.

        Args:
            session_id: The session ID
            turn: The interaction turn to store

        Returns:
            True if successful
        """
        return await self.episodic.add_turn(session_id, turn)

    async def rewind_session(self, session_id: str, target_turn_id: str) -> bool:
        """
        Rewind session history to a specific turn.

        Deletes all turns after the target turn (hard reset).

        Args:
            session_id: The session ID
            target_turn_id: The turn ID to rewind to

        Returns:
            True if successful
        """
        result = await self.episodic.rewind_history(session_id, target_turn_id)
        if result:
            self._emit_event(
                "session_rewound",
                {"session_id": session_id, "target_turn_id": target_turn_id},
            )
        return result
