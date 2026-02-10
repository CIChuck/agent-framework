"""
The Memory Controller Facade.
Orchestrates parallel retrieval from Vector, Graph, and Episodic stores.
Handles 'Store Fact', 'Recall', and 'Rollback' operations.

Supports lifecycle-aware retrieval with:
- Parallel queries to short-term and long-term collections
- Fast inclusion scoring using pre-computed retrieval_factor
- Graph path filtering using pre-embedded edges
- Async access tracking for latency optimization

Provenance tracking:
- Author tracking via set_author() for multi-agent attribution
- Query by author via get_facts_by_author(), get_insights_by_author()

Ref: Batch 2 Specification, Section 2
Ref: docs/build-plan/memory-lifecycle-staging-decay.md, Phase 6
Ref: docs/build-plan/shared-memory-provenance-build-plan.md
"""

import asyncio
import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

logger = logging.getLogger(__name__)

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
    ToolCall,
    ToolResult,
)

if TYPE_CHECKING:
    from friday_memory.retrieval import (
        AccessBuffer,
        CollectionManager,
        GraphPathScorer,
    )
    from friday_transcript import TranscriptStore


# Behavioral/conversational relation types to exclude from display
# These add noise without providing factual knowledge about entities
BEHAVIORAL_RELATIONS = {
    "SUGGESTS",
    "ASKS_ABOUT",
    "WILL_RESPOND_WITH",
    "WILL_OFFER",
    "WILL_PRIORITIZE",
    "WILL_FOCUS_ON",
    "WILL_STRIVE_FOR",
    "FINDS_PERPLEXING",
    "WISHES_TO_SHARE",
    "STATES_IMPORTANCE_OF",
    "NOT_EQUIPPED_TO_ANSWER",
    "APOLOGIZES_FOR",
    "RECALLS",
    "REMEMBERS_DISCUSSION_ABOUT",
    "WANTS_TO_DISCUSS",
    "HAS_LIMITED_KNOWLEDGE_ABOUT",
    "HAS_KNOWLEDGE_GAPS_ABOUT",
    "LACKS_CAPACITY_TO",
    "LACKS_ACCESS_TO",
    "CAN",
    "CANNOT",
    "CONFLATED",
    "UPDATING",
    "ATTEMPTED_TO_FIND",
    "THANKS_FOR",
    "READY_TO_RETAIN",
    "CONSIDERS_MISPLACED",
    "MAY_NOT_SHARE",
    "EXPRESSES_CONFUSION_ABOUT",
    "INTERESTED_IN",
    "DISCUSSING",
    "MENTIONED",
    "REFERRED_TO",
}


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

    Token Budget Awareness:
    - recall() respects token_limit by dynamically adjusting retrieval counts
    - Uses estimated tokens per item type for budget allocation
    """

    # Token estimates per item type (conservative averages)
    TOKENS_PER_HISTORY_TURN = 150  # user + assistant messages
    TOKENS_PER_INSIGHT = 80
    TOKENS_PER_SUMMARY = 100
    TOKENS_PER_ENTITY = 30
    TOKENS_PER_RELATIONSHIP = 40
    TOKENS_PER_PRIOR_TURN = 150

    # Default author for provenance tracking in multi-agent scenarios
    DEFAULT_AUTHOR = "system"

    def __init__(
        self,
        vector_store: VectorStoreAdapter,
        graph_store: GraphStoreAdapter,
        episodic_store: EpisodicStoreAdapter,
        collection_manager: "CollectionManager",
        telemetry: TelemetryInterface | None = None,
        priming_config: dict[str, Any] | None = None,
        # Lifecycle components (Phase 6)
        access_buffer: "AccessBuffer | None" = None,
        graph_scorer: "GraphPathScorer | None" = None,
        # Background recalculation config
        recalc_interval: int = 5,
        # Cross-session history support
        transcript_store: "TranscriptStore | None" = None,
        # Provenance tracking (Phase 3)
        default_author_id: str | None = None,
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
                - max_insights: int (default 10) - most recent insights to load
                - max_summaries: int (default 10) - most recent summaries to load
                - recency_days: int (default 0) - filter to last N days (0 = all)
                - min_turns: int (default 5) - turns before priming stops
                - previous_sessions: int (default 0) - number of prior sessions to include
                - previous_session_turns: int (default 5) - max turns per prior session
            collection_manager: CollectionManager for lifecycle-aware storage and retrieval
            access_buffer: Optional AccessBuffer for lazy access tracking
            graph_scorer: Optional GraphPathScorer for graph path filtering
            recalc_interval: Number of turns between background insight recalculation (0 = disabled)
            transcript_store: Optional TranscriptStore for cross-session history retrieval
            default_author_id: Default author for memory operations (for multi-agent provenance)
        """
        self.vector = vector_store
        self.graph = graph_store
        self.episodic = episodic_store
        self._telemetry = telemetry
        self._transcript_store = transcript_store

        # Provenance: Author tracking for multi-agent scenarios
        self._default_author_id = default_author_id or self.DEFAULT_AUTHOR

        # Lifecycle components
        self._collection_manager = collection_manager
        self._access_buffer = access_buffer
        self._graph_scorer = graph_scorer

        # Background recalculation settings
        self._recalc_interval = recalc_interval
        self._recalc_callback: (
            Callable[[str, list[InteractionTurn]], Awaitable[None]] | None
        ) = None

        # Priming configuration
        self._priming_config = priming_config or {
            "enabled": True,
            "top_entities": 10,
            "max_insights": 10,
            "max_summaries": 10,
            "max_facts": 10,
            "max_known_facts": 50,  # Cap on graph relationship summaries
            "recency_days": 0,
            "min_turns": 5,
            "previous_sessions": 0,  # Cross-session history: number of prior sessions
            "previous_session_turns": 5,  # Max turns per prior session
        }

        # Thread safety: state lock for session data
        self._state_lock = asyncio.Lock()

        # Priming state per session
        # _primed_content: session_id -> (entities, insights, summaries, relationship_summaries)
        self._primed_content: dict[
            str,
            tuple[
                list[GraphNode], list[dict[str, Any]], list[dict[str, Any]], list[str]
            ],
        ] = {}
        # _session_turn_counts: session_id -> turn count
        self._session_turn_counts: dict[str, int] = {}

    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    # =========================================================================
    # Author Management (Provenance Tracking)
    # =========================================================================

    @property
    def current_author(self) -> str:
        """
        Get the current default author for memory operations.

        Returns:
            Current author ID (agent name or user ID)
        """
        return self._default_author_id

    def set_author(self, author_id: str) -> None:
        """
        Set the current author for memory operations.

        Should be called when an agent starts processing to ensure
        all memory operations are attributed correctly.

        In multi-agent scenarios, each agent calls this when it becomes
        active, ensuring proper provenance tracking.

        Args:
            author_id: Agent name or user ID

        Raises:
            ValueError: If author_id is empty
        """
        if not author_id or not author_id.strip():
            raise ValueError("author_id cannot be empty")

        self._default_author_id = author_id.strip().lower()
        logger.debug(f"Memory author set to: {self._default_author_id}")
        self._emit_event(
            "memory_author_changed",
            {"author_id": self._default_author_id},
        )

    def _get_effective_author(self, author_id: str | None = None) -> str:
        """
        Get the effective author for a memory operation.

        Args:
            author_id: Optional override author

        Returns:
            Effective author ID (override or default)
        """
        if author_id:
            return author_id.strip().lower()
        return self._default_author_id

    async def get_facts_by_author(
        self,
        author_id: str,
        limit: int = 100,
    ) -> list[GraphNode]:
        """
        Get facts/entities created by a specific author.

        Args:
            author_id: Author to filter by
            limit: Maximum results

        Returns:
            List of GraphNodes created by that author
        """
        # Fetch all nodes and filter by author
        # Note: This is a simple implementation - can be optimized with
        # graph store support for metadata queries
        all_nodes = await self.graph.get_all_nodes()

        results = [
            node
            for node in all_nodes
            if node.provenance and node.provenance.author_id == author_id.lower()
        ]

        return results[:limit]

    async def get_insights_by_author(
        self,
        author_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get insights/summaries created by a specific author.

        Args:
            author_id: Author to filter by
            limit: Maximum results

        Returns:
            List of insight dicts created by that author
        """
        # Query across lifecycle collections with author filter
        try:
            results = await self._collection_manager.get_all(
                limit=limit,
                where={"provenance_author_id": author_id.lower()},
            )
            return results
        except Exception as e:
            logger.warning(f"get_insights_by_author failed: {e}")
            return []

    def _calculate_retrieval_limits(
        self,
        token_limit: int,
        history_limit: int,
        include_prior_sessions: bool = True,
    ) -> dict[str, int]:
        """
        Calculate token-budget-aware retrieval limits.

        Allocates the token budget across different content types using
        priority-based allocation, then applies priming_config ceilings
        so retrieval respects configured max_items.

        Budget allocation:
        1. History (35% of budget) - current session continuity
        2. Insights (25%) - extracted cross-session knowledge
        3. Summaries (20%) - conversation context summaries
        4. Facts/Entities (5%) - graph knowledge
        5. Prior sessions (15%) - cross-session turn history

        The budget-derived limits are capped by priming_config values
        (max_insights, max_summaries, max_known_facts) to prevent
        over-fetching beyond what downstream formatting will display.

        Args:
            token_limit: Total available tokens for retrieval
            history_limit: Maximum history turns (from priming config)
            include_prior_sessions: Whether to allocate for prior sessions

        Returns:
            Dict with adjusted limits: {
                'history': int, 'insights': int, 'summaries': int,
                'facts': int, 'entities': int, 'prior_turns': int,
                'relationships': int
            }
        """
        # Budget allocation percentages (must sum to 1.0)
        HISTORY_PERCENT = 0.35
        INSIGHTS_PERCENT = 0.25
        SUMMARIES_PERCENT = 0.20
        ENTITIES_PERCENT = 0.05
        PRIOR_PERCENT = 0.15 if include_prior_sessions else 0.0

        # Calculate item limits based on token budget
        history_budget = int(token_limit * HISTORY_PERCENT)
        insights_budget = int(token_limit * INSIGHTS_PERCENT)
        summaries_budget = int(token_limit * SUMMARIES_PERCENT)
        entities_budget = int(token_limit * ENTITIES_PERCENT)
        prior_budget = int(token_limit * PRIOR_PERCENT)

        # Convert to item counts
        max_history = min(
            history_limit, max(1, history_budget // self.TOKENS_PER_HISTORY_TURN)
        )
        max_insights = max(1, insights_budget // self.TOKENS_PER_INSIGHT)
        max_summaries = max(1, summaries_budget // self.TOKENS_PER_SUMMARY)
        max_entities = max(1, entities_budget // self.TOKENS_PER_ENTITY)
        max_prior = max(0, prior_budget // self.TOKENS_PER_PRIOR_TURN)
        max_relationships = max(1, max_entities)  # Match entity count

        # Apply priming_config ceilings — prevents over-fetching beyond
        # what the downstream layout will actually display
        max_insights = min(
            max_insights,
            self._priming_config.get("max_insights", 15),
        )
        max_summaries = min(
            max_summaries,
            self._priming_config.get("max_summaries", 10),
        )
        max_relationships = min(
            max_relationships,
            self._priming_config.get("max_known_facts", 50),
        )

        return {
            "history": max_history,
            "insights": max_insights,
            "summaries": max_summaries,
            "entities": max_entities,
            "prior_turns": max_prior,
            "relationships": max_relationships,
        }

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

        # Calculate budget-aware retrieval limits
        previous_sessions = self._priming_config.get("previous_sessions", 0)
        limits = self._calculate_retrieval_limits(
            token_limit=token_limit,
            history_limit=history_limit,
            include_prior_sessions=previous_sessions > 0,
        )

        debug_info: dict[str, Any] = {
            "query_length": len(query),
            "token_limit": token_limit,
            "budget_limits": limits,  # Record the calculated limits
        }

        try:
            # Initialize session priming if needed
            if session_id and self._priming_config.get("enabled", True):
                await self._ensure_session_primed(session_id)

            # Compute query embedding ONCE for reuse across vector + graph retrieval.
            # This avoids redundant embedding API calls (was 2 per recall, now 1).
            query_embedding = await self._collection_manager._embedding_function.embed_query(query)

            # Parallel retrieval from all stores (using budget-aware limits)
            tasks = []

            # Episodic retrieval - use budget-limited history count
            async def _empty_list() -> list:
                return []

            if include_history and session_id:
                tasks.append(self._retrieve_episodic(session_id, limits["history"]))
            else:
                tasks.append(_empty_list())

            # Vector retrieval via lifecycle collections (shared embedding)
            tasks.append(
                self._retrieve_vector_lifecycle(
                    query, vector_results, query_embedding=query_embedding
                )
            )
            debug_info["lifecycle_enabled"] = True

            # Graph retrieval with semantic path scoring (shared embedding)
            tasks.append(
                self._retrieve_graph_with_scoring(
                    query, graph_depth, query_embedding=query_embedding
                )
            )

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Unpack results (handle exceptions gracefully)
            history = results[0] if not isinstance(results[0], Exception) else []
            passages = results[1] if not isinstance(results[1], Exception) else []
            graph_data = results[2] if not isinstance(results[2], Exception) else {}

            entities = (
                graph_data.get("entities", []) if isinstance(graph_data, dict) else []
            )
            facts = graph_data.get("facts", []) if isinstance(graph_data, dict) else []
            scored_paths = (
                graph_data.get("scored_paths", [])
                if isinstance(graph_data, dict)
                else []
            )

            # Use budget-aware limits for insights and summaries
            recency_days = self._priming_config.get("recency_days", 0)

            recent_insights = await self._fetch_recent_insights(
                limits["insights"], recency_days
            )
            recent_summaries = await self._fetch_recent_summaries(
                limits["summaries"], recency_days
            )

            # Fetch prior session history for cross-session continuity
            prior_history: list[InteractionTurn] = []
            previous_session_turns = self._priming_config.get(
                "previous_session_turns", 5
            )
            if previous_sessions > 0 and session_id and limits["prior_turns"] > 0:
                prior_history = await self._fetch_prior_session_history(
                    session_id,
                    previous_sessions,
                    min(previous_session_turns, limits["prior_turns"]),
                )

            # Get top entities using budget-aware limit
            top_entities = await self.graph.get_top_nodes(
                limits["entities"],
                sort_by="hit_count",
            )

            # Merge top entities with query entities (dedup by ID)
            existing_ids = {e.id for e in entities}
            for entity in top_entities:
                if entity.id not in existing_ids:
                    entities.append(entity)
                    existing_ids.add(entity.id)

            # Build relationship summaries for all entities (budget-limited)
            # Uses merged list: query-matched + top entities by hit_count
            all_relationships = await self._build_relationship_summaries(entities)
            relationship_summaries = all_relationships[: limits["relationships"]]

            # Record debug info — includes retrieval limits for observability
            debug_info["retrieval_limits"] = limits
            debug_info["history_count"] = len(history)
            debug_info["prior_history_count"] = len(prior_history)
            debug_info["passages_count"] = len(passages)
            debug_info["entities_count"] = len(entities)
            debug_info["facts_count"] = len(facts)
            debug_info["insights_count"] = len(recent_insights)
            debug_info["summaries_count"] = len(recent_summaries)
            debug_info["relationships_count"] = len(relationship_summaries)
            debug_info["relationships_total"] = len(all_relationships)
            debug_info["scored_graph_paths"] = len(scored_paths)
            debug_info["query_embedding_shared"] = True
            debug_info["total_latency"] = time.time() - start_time

            self._emit_event("memory_recall_completed", debug_info)

            return ContextPayload(
                history=history,
                prior_history=prior_history,
                passages=passages,
                entities=entities,
                facts=facts,
                recent_memories=relationship_summaries,
                insights=recent_insights,
                summaries=recent_summaries,
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

        Thread-safe: Uses lock to prevent duplicate priming.

        Args:
            session_id: The session to prime
        """
        # Quick check without lock first (optimization)
        if session_id in self._primed_content:
            return
        if not self._priming_config.get("enabled", True):
            return

        # Check under lock to prevent duplicate priming
        async with self._state_lock:
            # Re-check after acquiring lock (another task may have primed)
            if session_id in self._primed_content:
                return

            # Initialize turn count for new session
            if session_id not in self._session_turn_counts:
                self._session_turn_counts[session_id] = 0

        # Load priming content outside lock (can be slow)
        entities, insights, summaries, relationships = await self.prime_context(
            top_entities=self._priming_config.get("top_entities", 10),
            max_insights=self._priming_config.get("max_insights", 10),
            recency_days=self._priming_config.get("recency_days", 0),
            max_summaries=self._priming_config.get("max_summaries", 10),
        )

        # Cache for injection during recall (under lock)
        async with self._state_lock:
            # Only store if not already primed by another task
            if session_id not in self._primed_content:
                self._primed_content[session_id] = (
                    entities,
                    insights,
                    summaries,
                    relationships,
                )

    async def prime_context(
        self,
        top_entities: int = 10,
        max_insights: int = 10,
        recency_days: int = 0,
        max_summaries: int = 10,
    ) -> tuple[list[GraphNode], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
        """
        Retrieve priming context using recency-based retrieval.

        Called on session startup to load prior knowledge when episodic
        history is empty. Creates continuity across sessions.

        Algorithm:
        1. Get top N entities by hit_count (Hebbian importance)
        2. Fetch most recent insights from vector store (sorted by created_at)
        3. Fetch most recent turn summaries from vector store (sorted by created_at)
        4. Apply recency filter if configured
        5. Build relationship summaries for entity context

        Args:
            top_entities: Number of top entities by hit_count to load
            max_insights: Maximum number of recent insights to include
            recency_days: Only include insights from last N days (0 = all time)
            max_summaries: Maximum number of turn summaries to include

        Returns:
            Tuple of (entities, insights, summaries, relationship_summaries)
            - entities: Top GraphNodes by hit_count
            - insights: Most recent insights from vector store
            - summaries: Most recent turn summaries from vector store
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

            # Step 2: Build recency cutoff for filtering.
            # Uses created_at_ts (numeric) when available, with fallback to
            # created_at (ISO string) for un-backfilled documents.
            recency_cutoff_ts: int | None = None
            recency_cutoff_iso: str | None = None
            if recency_days > 0:
                cutoff_dt = datetime.now() - timedelta(days=recency_days)
                recency_cutoff_ts = int(cutoff_dt.timestamp())
                recency_cutoff_iso = cutoff_dt.isoformat()

            # Step 3: Pre-fetch edges to build rich semantic queries (indexed retrieval)
            # We combine entity labels with their relationships for better matching
            entity_ids = {e.id for e in top_nodes}
            entity_lookup = {e.id: e.label for e in top_nodes}

            # Get only edges from top entities (indexed retrieval)
            entity_edges = await self.graph.get_edges_for_nodes(
                entity_ids, direction="outgoing"
            )

            # Get labels for edge targets not already in lookup
            target_ids = {
                edge.target_id
                for edge in entity_edges
                if edge.target_id not in entity_ids
            }
            if target_ids:
                target_labels = await self.graph.get_node_labels(target_ids)
                entity_lookup.update(target_labels)

            edges_by_source: dict[str, list[tuple[str, str]]] = {}
            for edge in entity_edges:
                target_label = entity_lookup.get(edge.target_id, edge.target_id[:8])
                if edge.source_id not in edges_by_source:
                    edges_by_source[edge.source_id] = []
                edges_by_source[edge.source_id].append((edge.relation, target_label))

            # Step 4: Fetch most recent insights from vector store
            all_insights: list[dict[str, Any]] = []
            try:
                raw_insights = await self._collection_manager.get_all(
                    limit=max_insights * 3,
                    where={"type": "insight"},
                )

                # Apply recency filter in Python — uses created_at_ts
                # (numeric) with fallback to created_at (ISO string) for
                # documents that haven't been backfilled yet.
                if recency_cutoff_ts is not None:
                    raw_insights = [
                        doc
                        for doc in raw_insights
                        if self._passes_recency_filter(
                            doc, recency_cutoff_ts, recency_cutoff_iso
                        )
                    ]

                # Sort by created_at descending (most recent first)
                raw_insights.sort(
                    key=lambda x: x.get("metadata", {}).get(
                        "created_at", ""
                    ),
                    reverse=True,
                )

                # Take the top max_insights
                all_insights = raw_insights[:max_insights]

            except Exception as e:
                if self._telemetry:
                    self._telemetry.capture_event(
                        "priming_insight_fetch_failed",
                        {"error": str(e)},
                    )

            # Step 5: Fetch most recent turn summaries from vector store
            turn_summaries: list[dict[str, Any]] = []
            try:
                raw_summaries = await self._collection_manager.get_all(
                    limit=max_summaries * 3,
                    where={"type": "summary"},
                )

                # Apply recency filter in Python
                if recency_cutoff_ts is not None:
                    raw_summaries = [
                        doc
                        for doc in raw_summaries
                        if self._passes_recency_filter(
                            doc, recency_cutoff_ts, recency_cutoff_iso
                        )
                    ]

                # Sort by created_at descending (most recent first)
                raw_summaries.sort(
                    key=lambda x: x.get("metadata", {}).get(
                        "created_at", ""
                    ),
                    reverse=True,
                )

                # Take the top max_summaries
                turn_summaries = raw_summaries[:max_summaries]

            except Exception as e:
                if self._telemetry:
                    self._telemetry.capture_event(
                        "priming_summary_fetch_failed",
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

    def clear_primed_content(self, session_id: str | None = None) -> int:
        """
        Clear cached primed content.

        Call this after resetting memory stores to ensure stale primed content
        is not used in subsequent context assemblies.

        Args:
            session_id: Specific session to clear, or None to clear all sessions

        Returns:
            Number of sessions cleared
        """
        if session_id:
            if session_id in self._primed_content:
                del self._primed_content[session_id]
                self._emit_event(
                    "primed_content_cleared",
                    {"session_id": session_id, "sessions_cleared": 1},
                )
                return 1
            return 0
        else:
            count = len(self._primed_content)
            self._primed_content.clear()
            self._emit_event(
                "primed_content_cleared",
                {"session_id": None, "sessions_cleared": count},
            )
            return count

    async def _build_relationship_summaries(
        self, entities: list[GraphNode]
    ) -> list[str]:
        """
        Build concise relationship summaries for each entity in natural language.

        Produces human-readable summaries like:
        - "Chuck created Friday and shared info about Tara"
        - "Noli loves AI and Raven"

        Filters out behavioral/conversational edges (e.g., SUGGESTS, ASKS_ABOUT)
        to focus on factual knowledge about entities.

        Args:
            entities: List of entities to summarize

        Returns:
            List of relationship summary strings in natural language
        """
        if not entities:
            return []

        # Build entity ID set for indexed retrieval
        entity_ids = {e.id for e in entities}

        # Get outgoing edges for these entities only (indexed retrieval)
        entity_edges = await self.graph.get_edges_for_nodes(
            entity_ids, direction="outgoing"
        )

        # Collect target IDs we need labels for
        target_ids = {
            edge.target_id for edge in entity_edges if edge.target_id not in entity_ids
        }

        # Get labels for entities + targets (indexed retrieval)
        entity_lookup = {e.id: e.label for e in entities}
        if target_ids:
            target_labels = await self.graph.get_node_labels(target_ids)
            entity_lookup.update(target_labels)

        # Group edges by source entity, filtering out behavioral edges
        edges_by_source: dict[
            str, list[tuple[str, str]]
        ] = {}  # (relation, target_label)

        for edge in entity_edges:
            # Filter out behavioral/conversational relations
            if edge.relation.upper() in BEHAVIORAL_RELATIONS:
                continue

            target_label = entity_lookup.get(edge.target_id, edge.target_id[:8])

            if edge.source_id not in edges_by_source:
                edges_by_source[edge.source_id] = []
            edges_by_source[edge.source_id].append((edge.relation, target_label))

        # Build natural language summaries for each entity
        summaries = []
        for entity in entities:
            outgoing = edges_by_source.get(entity.id, [])
            if not outgoing:
                continue

            # Group by relation type and convert to natural language
            relations_by_type: dict[str, list[str]] = {}
            for relation, target in outgoing[:10]:  # Limit to 10 relations per entity
                verb = self._relation_to_natural_verb(relation)
                if verb not in relations_by_type:
                    relations_by_type[verb] = []
                relations_by_type[verb].append(target)

            # Build natural language parts
            parts = []
            for verb, targets in list(relations_by_type.items())[:5]:  # Limit verbs
                if len(targets) == 1:
                    parts.append(f"{verb} {targets[0]}")
                else:
                    parts.append(f"{verb} {', '.join(targets[:3])}")

            if parts:
                summary = f"{entity.label} {' and '.join(parts)}"
                summaries.append(summary)

        return summaries

    def _relation_to_natural_verb(self, relation: str) -> str:
        """
        Convert a relation type to a natural language verb.

        Args:
            relation: The relation type (e.g., "IS_CREATOR_OF", "LOVES")

        Returns:
            Natural language verb phrase
        """
        mapping = {
            "IS_CREATOR_OF": "created",
            "CREATES": "creates",
            "LOVES": "loves",
            "IS_A": "is a",
            "WORKS_FOR": "works for",
            "PROVIDED_DATA_ABOUT": "shared info about",
            "HAS": "has",
            "KNOWS": "knows",
            "MANAGES": "manages",
            "OWNS": "owns",
            "USES": "uses",
            "RELATED_TO": "is related to",
            "SUGGESTS": "suggests",
            "WILL_RESPOND_WITH": "responds with",
            "WILL_OFFER": "offers",
            "WILL_PRIORITIZE": "prioritizes",
            "ASKS_ABOUT": "asks about",
            "STATES_IMPORTANCE_OF": "values",
            "FINDS_PERPLEXING": "finds perplexing",
            "WISHES_TO_SHARE": "wants to share",
            "HAS_FAVORITE_TEAM": "favors",
            "FAVORS": "favors",
            "TAUGHT": "taught",
            "WORKED_WITH": "worked with",
            "WAS_DESCRIBED_AS": "was described as",
        }
        upper_rel = relation.upper()
        if upper_rel in mapping:
            return mapping[upper_rel]
        # Default: convert underscores to spaces, lowercase
        return relation.replace("_", " ").lower()

    async def _fetch_recent_insights(
        self, max_count: int = 10, recency_days: int = 0
    ) -> list[dict[str, Any]]:
        """
        Fetch most recent insights from vector store, sorted by created_at desc.

        Called on every recall() to ensure newly extracted insights are included.

        Args:
            max_count: Maximum number of insights to return
            recency_days: Only include insights from last N days (0 = all time)

        Returns:
            List of insight dicts, most recent first
        """
        try:
            raw = await self._collection_manager.get_all(
                limit=max_count * 3, where={"type": "insight"}
            )
            # Apply recency filter — uses created_at_ts when available,
            # falls back to created_at string for un-backfilled documents.
            if recency_days > 0:
                cutoff_ts = int(
                    (
                        datetime.now() - timedelta(days=recency_days)
                    ).timestamp()
                )
                cutoff_iso = (
                    datetime.now() - timedelta(days=recency_days)
                ).isoformat()
                raw = [
                    doc
                    for doc in raw
                    if self._passes_recency_filter(
                        doc, cutoff_ts, cutoff_iso
                    )
                ]
            # get_all() already sorts by created_at desc
            # Deduplicate by topic/entities before returning
            deduped = self._dedupe_by_topic(raw)
            logger.debug(
                f"Insights: {len(raw)} raw → {len(deduped)} after dedup "
                f"→ {min(len(deduped), max_count)} returned "
                f"(max_count={max_count}, recency_days={recency_days})"
            )
            return deduped[:max_count]
        except Exception as e:
            if self._telemetry:
                self._emit_event(
                    "fetch_recent_insights_failed",
                    {"error": str(e)},
                )
            return []

    @staticmethod
    def _passes_recency_filter(
        doc: dict[str, Any],
        cutoff_ts: int,
        cutoff_iso: str | None,
    ) -> bool:
        """
        Check if a document passes the recency filter.

        Uses ``created_at_ts`` (numeric, fast) when present, with a
        fallback to ``created_at`` (ISO string comparison) for documents
        that haven't been backfilled with the numeric timestamp yet.

        Args:
            doc: Document dict with metadata.
            cutoff_ts: Unix epoch seconds cutoff.
            cutoff_iso: ISO string cutoff (fallback for un-backfilled docs).

        Returns:
            True if the document is within the recency window.
        """
        meta = doc.get("metadata", {})
        ts = meta.get("created_at_ts")
        if ts is not None:
            return ts >= cutoff_ts
        # Fallback: compare ISO strings (lexicographic, correct for ISO 8601)
        if cutoff_iso is not None:
            return meta.get("created_at", "") >= cutoff_iso
        return True

    def _dedupe_by_topic(self, insights: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Simple deduplication: if multiple insights mention same entities,
        keep only the most recent one.

        Also filters out insights marked as superseded during batch deduplication.

        This is a lightweight retrieval-time filter that reduces redundancy
        without expensive semantic similarity computation.

        Args:
            insights: List of insight dicts, already sorted by recency

        Returns:
            Deduplicated list, preserving recency order
        """
        seen_entity_sets: dict[frozenset[str], dict[str, Any]] = {}
        result: list[dict[str, Any]] = []

        for insight in insights:
            metadata = insight.get("metadata", {})

            # Skip insights that have been superseded by batch deduplication
            if metadata.get("superseded_by"):
                continue

            # Extract entities from metadata or text
            entities = self._extract_insight_entities(insight)

            if not entities:
                # No entities extracted - include by default
                result.append(insight)
                continue

            entity_key = frozenset(entities)

            if entity_key not in seen_entity_sets:
                seen_entity_sets[entity_key] = insight
                result.append(insight)
            # else: skip duplicate topic - we already have a more recent insight

        return result

    def _extract_insight_entities(self, insight: dict[str, Any]) -> set[str]:
        """
        Extract entity mentions from an insight for deduplication.

        Checks metadata first, then falls back to simple text extraction.

        Args:
            insight: Insight dict with text and metadata

        Returns:
            Set of normalized entity names
        """
        entities: set[str] = set()
        metadata = insight.get("metadata", {})

        # Primary: use entities_mentioned if available (semicolon-separated)
        entities_mentioned = metadata.get("entities_mentioned", "")
        if entities_mentioned:
            for entity in entities_mentioned.split(";"):
                entity = entity.strip().lower()
                if entity:
                    entities.add(entity)

        # Secondary: extract proper nouns/capitalized words from text
        if not entities:
            text = insight.get("text", "") or insight.get("document", "")
            words = text.split()
            for word in words:
                # Simple heuristic: capitalized words that aren't sentence starters
                clean_word = word.strip(".,!?\"'()[]")
                if (
                    clean_word
                    and clean_word[0].isupper()
                    and len(clean_word) > 2
                    and clean_word.lower()
                    not in {"the", "this", "that", "they", "their"}
                ):
                    entities.add(clean_word.lower())

        return entities

    async def _fetch_recent_summaries(
        self, max_count: int = 10, recency_days: int = 0
    ) -> list[dict[str, Any]]:
        """
        Fetch most recent summaries from vector store, sorted by created_at desc.

        Called on every recall() to ensure newly extracted summaries are included.

        Args:
            max_count: Maximum number of summaries to return
            recency_days: Only include summaries from last N days (0 = all time)

        Returns:
            List of summary dicts, most recent first
        """
        try:
            raw = await self._collection_manager.get_all(
                limit=max_count * 3, where={"type": "summary"}
            )
            # Apply recency filter — uses created_at_ts when available,
            # falls back to created_at string for un-backfilled documents.
            if recency_days > 0:
                cutoff_ts = int(
                    (
                        datetime.now() - timedelta(days=recency_days)
                    ).timestamp()
                )
                cutoff_iso = (
                    datetime.now() - timedelta(days=recency_days)
                ).isoformat()
                raw = [
                    doc
                    for doc in raw
                    if self._passes_recency_filter(
                        doc, cutoff_ts, cutoff_iso
                    )
                ]
            # get_all() already sorts by created_at desc
            return raw[:max_count]
        except Exception as e:
            if self._telemetry:
                self._emit_event(
                    "fetch_recent_summaries_failed",
                    {"error": str(e)},
                )
            return []

    async def _fetch_prior_session_history(
        self,
        current_session_id: str,
        num_sessions: int,
        turns_per_session: int,
    ) -> list[InteractionTurn]:
        """
        Fetch conversation turns from previous sessions for cross-session continuity.

        Retrieves the most recent N sessions (excluding current) and returns
        their conversation turns in chronological order (oldest session first).

        Args:
            current_session_id: The current session ID to exclude
            num_sessions: Number of prior sessions to include
            turns_per_session: Maximum turns to include per session

        Returns:
            List of InteractionTurns from prior sessions, ordered chronologically
            (oldest session turns first, newest session turns last)
        """
        if num_sessions <= 0 or not self._transcript_store:
            return []

        try:
            # List recent sessions (newest first)
            # Fetch extra to account for current session
            sessions = await self._transcript_store.list_sessions(
                limit=num_sessions + 1,
            )

            # Filter out current session and take the requested number
            prior_sessions = [
                s for s in sessions if s.session_id != current_session_id
            ][:num_sessions]

            if not prior_sessions:
                return []

            # Fetch turns from each prior session (in chronological order: oldest first)
            # Reverse the list since list_sessions returns newest first
            prior_sessions_chronological = list(reversed(prior_sessions))

            all_prior_turns: list[InteractionTurn] = []
            for session in prior_sessions_chronological:
                entries = await self._transcript_store.get_entries(
                    session.session_id,
                    limit=turns_per_session,
                )

                # Convert TranscriptEntry to InteractionTurn
                # Must convert ToolCall/ToolResult from friday_transcript types
                # to friday_memory types to satisfy Pydantic validation
                #
                # CRITICAL: Skip incomplete turns (no assistant_message).
                # Interrupted sessions may have orphaned user messages that would
                # appear as unanswered questions in the prompt, causing the LLM
                # to respond to old questions on startup.
                for entry in entries:
                    # Skip turns without a complete response
                    if not entry.assistant_message:
                        logger.debug(
                            f"Skipping incomplete turn {entry.id} from prior session "
                            f"{entry.session_id} (no assistant_message)"
                        )
                        continue

                    turn = InteractionTurn(
                        id=entry.id,
                        session_id=entry.session_id,
                        user_message=entry.user_message,
                        assistant_message=entry.assistant_message,
                        timestamp=entry.timestamp,
                        tool_calls=[
                            ToolCall(id=tc.id, name=tc.name, arguments=tc.arguments)
                            for tc in (entry.tool_calls or [])
                        ],
                        tool_results=[
                            ToolResult(
                                tool_call_id=tr.tool_call_id,
                                output=tr.output,
                                error=tr.error,
                            )
                            for tr in (entry.tool_results or [])
                        ],
                        metadata={
                            "from_prior_session": True,
                            "original_session_id": entry.session_id,
                        },
                    )
                    all_prior_turns.append(turn)

            logger.debug(
                f"_fetch_prior_session_history: Retrieved {len(all_prior_turns)} turns "
                f"from {len(prior_sessions)} prior sessions"
            )

            self._emit_event(
                "prior_session_history_fetched",
                {
                    "current_session_id": current_session_id,
                    "prior_sessions_count": len(prior_sessions),
                    "total_turns": len(all_prior_turns),
                },
            )

            return all_prior_turns

        except Exception as e:
            logger.error(f"_fetch_prior_session_history: Exception occurred: {e}")
            if self._telemetry:
                self._emit_event(
                    "fetch_prior_session_history_failed",
                    {"error": str(e)},
                )
            return []

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
        """Retrieve semantically similar passages.

        DEPRECATED: Use _retrieve_vector_lifecycle() instead.
        All retrieval now goes through CollectionManager.
        """
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
                    # Touch node for Hebbian learning (updates in-memory object)
                    node.touch()
                    # Persist hit_count to graph store (fire-and-forget)
                    asyncio.create_task(self.graph.record_node_access(node.id))

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

    # --- Lifecycle-Aware Retrieval (Phase 6) ---

    @property
    def has_lifecycle_support(self) -> bool:
        """Check if lifecycle components are configured.

        DEPRECATED: CollectionManager is now required. Always returns True.
        """
        return True

    @property
    def collection_manager(self) -> "CollectionManager":
        """Access to CollectionManager for lifecycle operations."""
        return self._collection_manager

    @property
    def access_buffer(self) -> "AccessBuffer | None":
        """Access to AccessBuffer for lazy tracking."""
        return self._access_buffer

    @property
    def graph_scorer(self) -> "GraphPathScorer | None":
        """Access to GraphPathScorer for path filtering."""
        return self._graph_scorer

    async def _retrieve_vector_lifecycle(
        self,
        query: str,
        n_results: int,
        query_embedding: list[float] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Lifecycle-aware vector retrieval using CollectionManager.

        Queries both short-term and long-term collections in parallel,
        applies fast inclusion scoring using pre-computed retrieval_factor,
        and records access events asynchronously.

        Args:
            query: The search query
            n_results: Number of results per collection
            query_embedding: Optional pre-computed query embedding

        Returns:
            Combined and scored results from both collections
        """

        start_time = time.time()

        # Query both collections in parallel (shared embedding avoids redundant calls)
        results = await self._collection_manager.query(
            query_text=query,
            n_results=n_results,
            include_decayed=False,  # Never include decayed in normal retrieval
            query_embedding=query_embedding,
        )

        short_term_results = results.get("short_term", [])
        long_term_results = results.get("long_term", [])

        # Apply fast inclusion scoring to long-term results
        scored_long_term = self._apply_fast_scoring(long_term_results)

        # Record accesses asynchronously (fire-and-forget)
        if self._access_buffer:
            for result in short_term_results:
                memory_id = result.get("id")
                if memory_id:
                    asyncio.create_task(
                        self._access_buffer.record_access(memory_id, "short_term")
                    )
            for result in scored_long_term:
                memory_id = result.get("id")
                if memory_id:
                    asyncio.create_task(
                        self._access_buffer.record_access(memory_id, "long_term")
                    )

        # Combine results (short-term first, then long-term sorted by score)
        combined = short_term_results + sorted(
            scored_long_term,
            key=lambda x: x.get("inclusion_score", 0),
            reverse=True,
        )

        if self._telemetry:
            self._emit_event(
                "lifecycle_vector_retrieval",
                {
                    "query_length": len(query),
                    "short_term_results": len(short_term_results),
                    "long_term_results": len(scored_long_term),
                    "total_results": len(combined),
                    "latency": time.time() - start_time,
                },
            )

        return combined

    def _apply_fast_scoring(
        self,
        results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Apply fast inclusion scoring using pre-computed retrieval_factor.

        Uses O(1) multiplication instead of expensive exponential calculations.
        Falls back to similarity score if retrieval_factor is not present.

        Args:
            results: Vector search results with similarity and metadata

        Returns:
            Results with inclusion_score added
        """
        scored = []
        for result in results:
            similarity = result.get("similarity", 0.0)
            metadata = result.get("metadata", {})

            # Use pre-computed retrieval_factor (falls back to 0.5)
            retrieval_factor = metadata.get("retrieval_factor", 0.5)
            inclusion_score = similarity * retrieval_factor

            scored.append(
                {
                    **result,
                    "inclusion_score": inclusion_score,
                }
            )

        return scored

    async def _retrieve_graph_with_scoring(
        self,
        query: str,
        depth: int,
        query_embedding: list[float] | None = None,
    ) -> dict[str, Any]:
        """
        Graph retrieval with path scoring using GraphPathScorer.

        Filters irrelevant graph paths based on semantic similarity
        to the query, using pre-embedded edges for fast scoring.

        Args:
            query: The search query
            depth: Graph traversal depth
            query_embedding: Optional pre-computed query embedding for scoring

        Returns:
            Dict with entities, facts, and scored_paths
        """
        # Get standard graph retrieval results
        base_result = await self._retrieve_graph(query, depth)
        entities = base_result.get("entities", [])
        facts = base_result.get("facts", [])

        # If no scorer or no query embedding, return base results
        if not self._graph_scorer or not query_embedding:
            return base_result

        # Score and filter paths using GraphPathScorer
        scored_paths = []
        try:
            # Build paths from entities and their edges (indexed retrieval)
            entity_ids = {e.id for e in entities}
            entity_lookup = {e.id: e for e in entities}

            # Get only edges from these entities
            entity_edges = await self.graph.get_edges_for_nodes(
                entity_ids, direction="outgoing"
            )

            # Get target nodes we need (that aren't already in entities)
            target_ids = {
                edge.target_id
                for edge in entity_edges
                if edge.target_id not in entity_ids
            }
            if target_ids:
                target_nodes = await self.graph.get_nodes_by_ids(target_ids)
                entity_lookup.update(target_nodes)

            paths_to_score = []
            for edge in entity_edges:
                source_node = entity_lookup.get(edge.source_id)
                target_node = entity_lookup.get(edge.target_id)
                if source_node and target_node:
                    paths_to_score.append((source_node, edge, target_node))

            # Score paths using pre-embedded edges (sync fast path —
            # all embeddings are pre-computed, no API calls needed)
            if paths_to_score and query_embedding:
                scored_paths = self._graph_scorer.filter_paths_sync(
                    paths_to_score,
                    query_embedding,
                )

            if self._telemetry:
                self._emit_event(
                    "graph_path_scoring",
                    {
                        "paths_evaluated": len(paths_to_score),
                        "paths_retained": len(scored_paths),
                    },
                )

        except Exception as e:
            if self._telemetry:
                self._emit_event(
                    "graph_path_scoring_failed",
                    {"error": str(e)},
                )

        return {
            "entities": entities,
            "facts": facts,
            "scored_paths": scored_paths,
        }

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

        # Store in short-term collection (lifecycle-aware)
        await self._collection_manager.add_to_short_term(
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

        # Store batch in short-term collection (lifecycle-aware)
        await self._collection_manager.add_to_short_term(
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

        # Store batch in short-term collection (lifecycle-aware)
        await self._collection_manager.add_to_short_term(
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

    async def store_document(
        self,
        text: str,
        metadata: dict[str, Any],
        doc_id: str | None = None,
        protected: bool = False,
    ) -> str:
        """
        Store a document in vector memory with lifecycle-aware routing.

        Automatically routes to lifecycle collections if available, otherwise
        falls back to the main vector store. This is the recommended entry point
        for explicit document ingestion (e.g., /ingest command).

        Args:
            text: The document text content
            metadata: Document metadata (source, type, etc.)
            doc_id: Optional document ID (generated if not provided)
            protected: If True, marks document as protected from decay.
                      Protected documents are fast-tracked for promotion
                      and never decay. Use for explicitly ingested documents.

        Returns:
            The document ID (provided or generated)

        Example:
            doc_id = await controller.store_document(
                text="File content here...",
                metadata={"source": "/path/to/file.txt", "type": "ingested_file"},
                protected=True,  # Explicitly ingested, don't decay
            )
        """
        doc_id = doc_id or f"doc_{uuid.uuid4().hex[:8]}"

        await self._collection_manager.add_to_short_term(
            texts=[text],
            metadatas=[metadata],
            ids=[doc_id],
            protected=protected,
        )
        self._emit_event(
            "document_stored",
            {
                "doc_id": doc_id,
                "text_length": len(text),
                "collection": "short_term",
                "protected": protected,
            },
        )

        return doc_id

    async def store_documents_batch(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str] | None = None,
        protected: bool = False,
    ) -> list[str]:
        """
        Store multiple documents in vector memory with lifecycle-aware routing.

        Batch version of store_document() for efficiency when ingesting
        multiple chunks from a single file.

        Args:
            texts: List of document texts
            metadatas: List of metadata dicts (must match texts length)
            ids: Optional list of document IDs (generated if not provided)
            protected: If True, marks documents as protected from decay.
                      Protected documents are fast-tracked for promotion
                      and never decay. Use for explicitly ingested documents.

        Returns:
            List of document IDs (provided or generated)
        """
        if not texts:
            return []

        if ids is None:
            ids = [f"doc_{uuid.uuid4().hex[:8]}" for _ in texts]

        await self._collection_manager.add_to_short_term(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
            protected=protected,
        )
        self._emit_event(
            "documents_batch_stored",
            {
                "count": len(texts),
                "total_chars": sum(len(t) for t in texts),
                "collection": "short_term",
                "protected": protected,
            },
        )

        return ids

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

    def set_recalc_callback(
        self,
        callback: Callable[[str, list[InteractionTurn]], Awaitable[None]],
    ) -> None:
        """
        Register a callback for background insight recalculation.

        The callback will be invoked (fire-and-forget) every `recalc_interval` turns
        with the session_id and recent turns to process.

        This allows the caller (e.g., the chat application) to hook up the
        MemoryExtractor without creating circular dependencies.

        Args:
            callback: Async function taking (session_id, recent_turns) as arguments.
                     Typically calls extractor.extract() on each turn.
        """
        self._recalc_callback = callback

    async def add_turn(self, session_id: str, turn: InteractionTurn) -> bool:
        """
        Add a conversation turn to episodic memory.

        Also increments the session turn count for priming management.
        Triggers background recalculation when turn count reaches recalc_interval.
        Thread-safe: Uses lock for turn count updates.

        Args:
            session_id: The session ID
            turn: The interaction turn to store

        Returns:
            True if successful
        """
        result = await self.episodic.add_turn(session_id, turn)

        # Increment turn count for priming management (under lock)
        should_recalc = False
        if result:
            async with self._state_lock:
                self._session_turn_counts[session_id] = (
                    self._session_turn_counts.get(session_id, 0) + 1
                )
                # Check if we should trigger recalculation
                if (
                    self._recalc_interval > 0
                    and self._recalc_callback
                    and self._session_turn_counts[session_id] % self._recalc_interval
                    == 0
                ):
                    should_recalc = True

        # Trigger background recalculation (fire-and-forget, outside lock)
        if should_recalc:
            asyncio.create_task(self._trigger_background_recalc(session_id))

        return result

    async def _trigger_background_recalc(self, session_id: str) -> None:
        """
        Trigger background insight recalculation for recent turns.

        Fetches the last `recalc_interval` turns and invokes the registered
        callback in the background. Errors are logged but don't propagate.

        Args:
            session_id: The session to recalculate insights for
        """
        if not self._recalc_callback:
            return

        try:
            # Fetch recent turns (the interval amount)
            recent_turns = await self.episodic.get_turns(
                session_id, limit=self._recalc_interval
            )
            if recent_turns:
                self._emit_event(
                    "background_recalc_triggered",
                    {
                        "session_id": session_id,
                        "turn_count": len(recent_turns),
                    },
                )
                await self._recalc_callback(session_id, recent_turns)
        except Exception as e:
            # Log but don't propagate - this is background work
            self._emit_event(
                "background_recalc_failed",
                {
                    "session_id": session_id,
                    "error": str(e),
                },
            )

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
            entities, insights, summaries, relationships = self._primed_content[
                session_id
            ]
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
