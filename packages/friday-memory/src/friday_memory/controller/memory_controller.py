"""
The Memory Controller Facade.
Orchestrates parallel retrieval from Vector, Graph, and Episodic stores.
Handles 'Store Fact', 'Recall', and 'Rollback' operations.

Ref: Batch 2 Specification, Section 2
"""

import asyncio
import time
import uuid
from datetime import datetime, timedelta
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
        priming_config: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the Memory Controller.

        Args:
            vector_store: VectorStoreAdapter for semantic search
            graph_store: GraphStoreAdapter for entity/relationship storage
            episodic_store: EpisodicStoreAdapter for conversation history
            telemetry: Optional telemetry recorder for observability
            priming_config: Optional config for context priming on startup
                - enabled: bool (default True)
                - top_entities: int (default 10)
                - recent_facts: int (default 5)
                - min_turns: int (default 5) - turns before priming stops
        """
        self.vector = vector_store
        self.graph = graph_store
        self.episodic = episodic_store
        self._telemetry = telemetry

        # Priming configuration
        self._priming_config = priming_config or {
            "enabled": True,
            "top_entities": 10,
            "recent_facts": 5,
            "min_turns": 5,
        }

        # Priming state per session
        # _primed_content: session_id -> (entities, insights, summaries, relationship_summaries)
        self._primed_content: dict[
            str, tuple[list[GraphNode], list[dict[str, Any]], list[dict[str, Any]], list[str]]
        ] = {}
        # _session_turn_counts: session_id -> turn count
        self._session_turn_counts: dict[str, int] = {}

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
        4. Priming: Injects prior session knowledge while session is "cold"
        5. Fusion: Deduplicates entities found in both Vector/Graph/Priming

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
            # Initialize session priming if needed
            if session_id and self._priming_config.get("enabled", True):
                await self._ensure_session_primed(session_id)

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

            entities = (
                graph_data.get("entities", []) if isinstance(graph_data, dict) else []
            )
            facts = graph_data.get("facts", []) if isinstance(graph_data, dict) else []
            recent_memories: list[str] = []

            # Inject primed content while session is "cold"
            primed_entity_count = 0
            primed_insight_count = 0
            primed_summary_count = 0
            primed_relationship_count = 0
            if session_id:
                turn_count = self._session_turn_counts.get(session_id, 0)
                min_turns = self._priming_config.get("min_turns", 5)

                if turn_count < min_turns and session_id in self._primed_content:
                    primed_entities, primed_insights, primed_summaries, primed_relationships = (
                        self._primed_content[session_id]
                    )

                    # Add relationship summaries as priming context
                    # Format: "EntityLabel: relation→Target1, relation→Target2, ..."
                    if primed_relationships:
                        recent_memories.append("Prior knowledge:")
                        for summary in primed_relationships:
                            recent_memories.append(f"  {summary}")

                    # Add turn summaries (paragraph summaries of prior conversations)
                    if primed_summaries:
                        recent_memories.append("Prior conversation summaries:")
                        for summary_doc in primed_summaries[:5]:  # Limit to top 5
                            text = summary_doc.get("text", "")
                            # Truncate very long summaries
                            if len(text) > 300:
                                text = text[:297] + "..."
                            recent_memories.append(f"  • {text}")

                    # Add entity-related insights (from semantic search)
                    # Format: "[EntityLabel] Insight text..."
                    if primed_insights:
                        recent_memories.append("Related insights:")
                        for insight in primed_insights[:10]:  # Limit to top 10
                            entity_label = insight.get("related_entity", "")
                            text = insight.get("text", "")
                            # Truncate long insights for readability
                            if len(text) > 150:
                                text = text[:147] + "..."
                            recent_memories.append(f"  [{entity_label}] {text}")

                    # Merge primed entities (dedup by ID)
                    existing_ids = {e.id for e in entities}
                    for entity in primed_entities:
                        if entity.id not in existing_ids:
                            entities.append(entity)
                            existing_ids.add(entity.id)

                    primed_entity_count = len(primed_entities)
                    primed_insight_count = len(primed_insights)
                    primed_summary_count = len(primed_summaries)
                    primed_relationship_count = len(primed_relationships)

                elif turn_count >= min_turns and session_id in self._primed_content:
                    # Session is warm, clean up priming cache
                    del self._primed_content[session_id]

            # Record debug info
            debug_info["history_count"] = len(history)
            debug_info["passages_count"] = len(passages)
            debug_info["entities_count"] = len(entities)
            debug_info["facts_count"] = len(facts)
            debug_info["primed_entities"] = primed_entity_count
            debug_info["primed_insights"] = primed_insight_count
            debug_info["primed_summaries"] = primed_summary_count
            debug_info["primed_relationships"] = primed_relationship_count
            debug_info["total_latency"] = time.time() - start_time

            self._emit_event("memory_recall_completed", debug_info)

            return ContextPayload(
                history=history,
                passages=passages,
                entities=entities,
                facts=facts,
                recent_memories=recent_memories,
                debug_info=debug_info,
            )

        finally:
            if span_id:
                self._telemetry.end_span(span_id, {"latency": time.time() - start_time})

    async def _ensure_session_primed(self, session_id: str) -> None:
        """
        Ensure a session has been primed with prior context.

        Called internally by recall() on first access to a session.
        Loads top entities, entity-related insights, and relationship summaries.

        Args:
            session_id: The session to prime
        """
        # Skip if already primed or priming disabled
        if session_id in self._primed_content:
            return
        if not self._priming_config.get("enabled", True):
            return

        # Initialize turn count for new session
        if session_id not in self._session_turn_counts:
            self._session_turn_counts[session_id] = 0

        # Load priming content using entity-driven semantic search
        entities, insights, summaries, relationships = await self.prime_context(
            top_entities=self._priming_config.get("top_entities", 10),
            insights_per_entity=self._priming_config.get("insights_per_entity", 3),
            recency_days=self._priming_config.get("recency_days", 0),
        )

        # Cache for injection during recall
        self._primed_content[session_id] = (entities, insights, summaries, relationships)

    async def prime_context(
        self,
        top_entities: int = 10,
        insights_per_entity: int = 3,
        recency_days: int = 0,
        max_summaries: int = 10,
    ) -> tuple[list[GraphNode], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
        """
        Retrieve priming context using entity-driven semantic search.

        Called on session startup to load prior knowledge when episodic
        history is empty. Creates continuity across sessions.

        Algorithm:
        1. Get top N entities by hit_count (Hebbian importance)
        2. For each entity, query vector store for semantically related insights
        3. Query for recent turn summaries (type="summary")
        4. Apply recency filter if configured
        5. Build relationship summaries for entity context

        Args:
            top_entities: Number of top entities by hit_count to load
            insights_per_entity: Number of insights to retrieve per entity
            recency_days: Only include insights from last N days (0 = all time)
            max_summaries: Maximum number of turn summaries to include

        Returns:
            Tuple of (entities, insights, summaries, relationship_summaries)
            - entities: Top GraphNodes by hit_count
            - insights: Semantically related insights from vector store
            - summaries: Recent turn summaries from vector store
            - relationship_summaries: Concise entity relationship strings
        """
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("context_priming")

        try:
            # Step 1: Get top entities by hit_count
            top_nodes = await self.graph.get_top_nodes(
                top_entities, sort_by="hit_count"
            )

            if not top_nodes:
                return [], [], [], []

            # Step 2: Build recency filter if configured
            where_filter = None
            if recency_days > 0:
                cutoff = (datetime.now() - timedelta(days=recency_days)).isoformat()
                where_filter = {"created_at": {"$gte": cutoff}}

            # Step 3: Pre-fetch edges to build rich semantic queries
            # We combine entity labels with their relationships for better matching
            all_edges = await self.graph.get_all_edges()
            edges_by_source: dict[str, list[tuple[str, str]]] = {}
            entity_lookup = {e.id: e.label for e in top_nodes}

            # Also include non-top entities in lookup for target label resolution
            all_nodes = await self.graph.get_all_nodes()
            for node in all_nodes:
                if node.id not in entity_lookup:
                    entity_lookup[node.id] = node.label

            for edge in all_edges:
                if edge.source_id in {e.id for e in top_nodes}:
                    target_label = entity_lookup.get(edge.target_id, edge.target_id[:8])
                    if edge.source_id not in edges_by_source:
                        edges_by_source[edge.source_id] = []
                    edges_by_source[edge.source_id].append(
                        (edge.relation, target_label)
                    )

            # Step 4: Query vector store for insights related to each entity
            all_insights: list[dict[str, Any]] = []
            seen_ids: set[str] = set()

            for entity in top_nodes:
                try:
                    # Build rich query: entity label + relationship context
                    query_parts = [entity.label]

                    # Add relationship context (e.g., "creates Friday", "works_with Python")
                    if entity.id in edges_by_source:
                        for relation, target in edges_by_source[entity.id][:3]:
                            query_parts.append(f"{relation} {target}")

                    query_text = " ".join(query_parts)
                    # Example: "Chuck creates Friday works_with Python"

                    results = await self.vector.query(
                        query_text=query_text,
                        n_results=insights_per_entity,
                        where=where_filter,
                    )

                    # Deduplicate by ID and track source entity
                    for result in results:
                        if result["id"] not in seen_ids:
                            seen_ids.add(result["id"])
                            result["related_entity"] = entity.label
                            all_insights.append(result)
                except Exception as e:
                    # Continue if one entity query fails
                    if self._telemetry:
                        self._telemetry.capture_event(
                            "priming_entity_query_failed",
                            {"entity": entity.label, "error": str(e)},
                        )

            # Step 5: Query for recent turn summaries
            turn_summaries: list[dict[str, Any]] = []
            try:
                # Build query for summaries - use entity labels for semantic matching
                summary_query = " ".join([e.label for e in top_nodes[:5]])
                summary_filter = {"type": "summary"}
                if where_filter:
                    # Combine with recency filter if configured
                    summary_filter.update(where_filter)

                summary_results = await self.vector.query(
                    query_text=summary_query,
                    n_results=max_summaries,
                    where=summary_filter,
                )
                turn_summaries = summary_results
            except Exception as e:
                if self._telemetry:
                    self._telemetry.capture_event(
                        "priming_summary_query_failed",
                        {"error": str(e)},
                    )

            # Step 6: Build relationship summaries for each top entity
            relationship_summaries = await self._build_relationship_summaries(top_nodes)

            self._emit_event(
                "context_primed",
                {
                    "entities": len(top_nodes),
                    "insights": len(all_insights),
                    "summaries": len(turn_summaries),
                    "relationships": len(relationship_summaries),
                    "recency_days": recency_days,
                },
            )

            return top_nodes, all_insights, turn_summaries, relationship_summaries

        finally:
            if span_id:
                self._telemetry.end_span(span_id)

    async def _build_relationship_summaries(
        self, entities: list[GraphNode]
    ) -> list[str]:
        """
        Build concise relationship summaries for each entity.

        For each top entity, shows ALL its relationships in a clear directional format:
        - Outgoing (entity is subject): "EntityLabel relation Target"
        - Incoming (entity is object): "Source relation EntityLabel"

        This respects edge direction - if there's only one edge between A and B,
        it will only appear once in the summary (from the source entity's perspective).

        Args:
            entities: List of entities to summarize

        Returns:
            List of relationship summary strings in natural language
        """
        if not entities:
            return []

        # Build entity ID to label lookup
        entity_lookup = {e.id: e.label for e in entities}

        # Get all nodes for label resolution
        all_nodes = await self.graph.get_all_nodes()
        for node in all_nodes:
            if node.id not in entity_lookup:
                entity_lookup[node.id] = node.label

        # Get all edges
        all_edges = await self.graph.get_all_edges()

        # Group edges by source and target entity
        # Each edge is stored with full info to construct natural sentences
        edges_by_source: dict[
            str, list[tuple[str, str, str]]
        ] = {}  # (relation, target_label, target_id)
        edges_by_target: dict[
            str, list[tuple[str, str, str]]
        ] = {}  # (relation, source_label, source_id)

        for edge in all_edges:
            target_label = entity_lookup.get(edge.target_id, edge.target_id[:8])
            source_label = entity_lookup.get(edge.source_id, edge.source_id[:8])

            # Outgoing: source → target
            if edge.source_id not in edges_by_source:
                edges_by_source[edge.source_id] = []
            edges_by_source[edge.source_id].append(
                (edge.relation, target_label, edge.target_id)
            )

            # Incoming: source → target (entity is the target)
            if edge.target_id not in edges_by_target:
                edges_by_target[edge.target_id] = []
            edges_by_target[edge.target_id].append(
                (edge.relation, source_label, edge.source_id)
            )

        # Track which entities are in our top list for dedup
        top_entity_ids = {e.id for e in entities}

        # Build summaries for each top entity
        summaries = []
        for entity in entities:
            outgoing = []
            incoming = []

            # Outgoing edges: entity --relation--> target
            # Format: "relation target" e.g., "creates Friday"
            for relation, target_label, _ in edges_by_source.get(entity.id, []):
                outgoing.append(f"{relation} {target_label}")

            # Incoming edges: source --relation--> entity
            # Only include if source is NOT a top entity (to avoid duplication)
            # If source IS a top entity, that relationship will appear in source's outgoing
            for relation, source_label, source_id in edges_by_target.get(entity.id, []):
                if source_id not in top_entity_ids:
                    # Source is not a top entity, so this is the only place this rel appears
                    incoming.append(f"{source_label} {relation}")

            # Combine into natural summary
            parts = []
            if outgoing:
                parts.append(f"→ {'; '.join(outgoing)}")
            if incoming:
                parts.append(f"← {'; '.join(incoming)}")

            if parts:
                summary = f"{entity.label}: {' | '.join(parts)}"
                summaries.append(summary)

        return summaries

    async def _retrieve_episodic(
        self, session_id: str, limit: int
    ) -> list[InteractionTurn]:
        """Retrieve recent conversation history."""
        start_time = time.time()
        turns = await self.episodic.get_turns(session_id, limit=limit)
        if self._telemetry:
            self._emit_event(
                "episodic_retrieval",
                {
                    "session_id": session_id,
                    "turns": len(turns),
                    "latency": time.time() - start_time,
                },
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
                {
                    "query_length": len(query),
                    "results": len(results),
                    "latency": time.time() - start_time,
                },
            )
        return results

    async def _retrieve_graph(self, query: str, depth: int) -> dict[str, Any]:
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

    async def store_fact(self, node: GraphNode, edge: GraphEdge | None = None) -> bool:
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
        self,
        text: str,
        provenance: ProvenanceMetadata | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Writes a semantic block (e.g., insight, summary) to the Vector store.

        Args:
            text: The text content to store
            provenance: Provenance metadata (required)
            extra_metadata: Optional additional metadata (type, topic, sentiment, etc.)
                These fields are merged with provenance metadata.

        Returns:
            True if successful

        Raises:
            ValueError: If provenance is missing
        """
        if provenance is None:
            raise ValueError(
                "Provenance metadata is required for all stored data. "
                "The provenance parameter cannot be None."
            )

        # Generate unique ID
        insight_id = str(uuid.uuid4())

        # Prepare metadata dict with provenance
        meta_dict: dict[str, Any] = {
            "type": "insight",  # Default type, can be overridden by extra_metadata
            "provenance_source_id": provenance.source_id,
            "provenance_source_type": provenance.source_type,
            "provenance_confidence": provenance.confidence,
            "provenance_author_id": provenance.author_id or "",
            "created_at": provenance.created_at.isoformat(),
        }

        # Merge extra metadata (type, topic, sentiment, entities_mentioned, etc.)
        if extra_metadata:
            meta_dict.update(extra_metadata)

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
                "source_type": provenance.source_type,
                "doc_type": meta_dict.get("type", "insight"),
            },
        )
        return True

    async def store_insights_batch(
        self, texts: list[str], metadata: ProvenanceMetadata | None = None
    ) -> int:
        """
        Batch store multiple insights to the Vector store.

        More efficient than calling store_insight() multiple times because:
        - Single embedding API call for all texts
        - Single database write operation

        Args:
            texts: List of text contents to store
            metadata: Provenance metadata (applied to all, required)

        Returns:
            Number of insights stored

        Raises:
            ValueError: If metadata/provenance is missing
        """
        if not texts:
            return 0

        if metadata is None:
            raise ValueError(
                "Provenance metadata is required for all stored data. "
                "The metadata parameter cannot be None."
            )

        # Generate unique IDs for each text
        ids = [str(uuid.uuid4()) for _ in texts]

        # Prepare metadata dict with provenance (same for all)
        base_meta = {
            "type": "insight",
            "provenance_source_id": metadata.source_id,
            "provenance_source_type": metadata.source_type,
            "provenance_confidence": metadata.confidence,
            "provenance_author_id": metadata.author_id or "",
            "created_at": metadata.created_at.isoformat(),
        }
        metadatas = [base_meta.copy() for _ in texts]

        # Single batch store to vector store
        await self.vector.add_documents(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
        )

        self._emit_event(
            "insights_batch_stored",
            {
                "count": len(texts),
                "total_chars": sum(len(t) for t in texts),
                "source_type": metadata.source_type,
            },
        )
        return len(texts)

    async def store_insights_batch_with_metadata(
        self,
        items: list[tuple[str, dict[str, Any]]],
        provenance: ProvenanceMetadata | None = None,
    ) -> int:
        """
        Batch store insights with per-item metadata to the Vector store.

        More efficient than calling store_insight() multiple times because:
        - Single embedding API call for all texts
        - Single database write operation

        Args:
            items: List of (text, extra_metadata) tuples. Each extra_metadata dict
                can contain: type, topic, sentiment, entities_mentioned, confidence
            provenance: Provenance metadata (applied to all, required)

        Returns:
            Number of insights stored

        Raises:
            ValueError: If provenance is missing
        """
        if not items:
            return 0

        if provenance is None:
            raise ValueError(
                "Provenance metadata is required for all stored data. "
                "The provenance parameter cannot be None."
            )

        # Generate unique IDs for each item
        ids = [str(uuid.uuid4()) for _ in items]
        texts = [text for text, _ in items]

        # Build metadata for each item: provenance + extra_metadata
        base_provenance = {
            "provenance_source_id": provenance.source_id,
            "provenance_source_type": provenance.source_type,
            "provenance_confidence": provenance.confidence,
            "provenance_author_id": provenance.author_id or "",
            "created_at": provenance.created_at.isoformat(),
        }

        metadatas = []
        for _, extra_meta in items:
            meta = {"type": "insight"}  # Default
            meta.update(base_provenance)
            if extra_meta:
                meta.update(extra_meta)
            metadatas.append(meta)

        # Single batch store to vector store
        await self.vector.add_documents(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
        )

        self._emit_event(
            "insights_batch_stored",
            {
                "count": len(texts),
                "total_chars": sum(len(t) for t in texts),
                "source_type": provenance.source_type,
                "with_metadata": True,
            },
        )
        return len(texts)

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

    async def merge_identities(self, primary_id: str, secondary_id: str) -> bool:
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

        Also increments the session turn count for priming management.

        Args:
            session_id: The session ID
            turn: The interaction turn to store

        Returns:
            True if successful
        """
        result = await self.episodic.add_turn(session_id, turn)

        # Increment turn count for priming management
        if result:
            self._session_turn_counts[session_id] = (
                self._session_turn_counts.get(session_id, 0) + 1
            )

        return result

    def get_priming_info(self, session_id: str) -> dict[str, Any]:
        """
        Get priming information for a session.

        Useful for displaying priming status on startup.

        Args:
            session_id: The session ID

        Returns:
            Dict with priming info (entities, insights, summaries, relationships, etc.)
        """
        if session_id in self._primed_content:
            entities, insights, summaries, relationships = self._primed_content[session_id]
            return {
                "enabled": self._priming_config.get("enabled", True),
                "primed": True,
                "entity_count": len(entities),
                "insight_count": len(insights),
                "summary_count": len(summaries),
                "relationship_count": len(relationships),
                "entity_labels": [e.label for e in entities[:10]],
                "relationship_summaries": relationships[:10],
            }
        return {
            "enabled": self._priming_config.get("enabled", True),
            "primed": False,
            "entity_count": 0,
            "insight_count": 0,
            "summary_count": 0,
            "relationship_count": 0,
            "entity_labels": [],
            "relationship_summaries": [],
        }

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
