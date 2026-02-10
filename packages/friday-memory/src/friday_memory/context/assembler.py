"""
Context Assembler.
Implements the 'Knapsack' budgeting logic to fit memory into the token window.
Handles Active Search queries.

Updated for lifecycle-aware budgeting:
- Uses inclusion_score for relevancy-based ranking
- Prioritizes short-term over long-term memories
- Excludes DECAYED memories by default

Tool context integration (Phase 3):
- Integrates ToolContextManager for tool selection and budgeting
- Provides set_active_tools(), expand_tools(), clear_tools() methods
- Preserves tool fields through all filtering operations

Ref: Batch 2a Specification, Section 2
Ref: docs/build-plan/memory-lifecycle-staging-decay.md, Phase 7
Ref: docs/build-plan/tool-calling-build-plan.md, Phase 3
"""

import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from friday_core import ContextEngineeringInterface, TelemetryInterface

from friday_memory.context.layout import PromptArchitect
from friday_memory.context.passage_router import PassageRouter
from friday_memory.context.token_estimator import build_token_estimator
from friday_memory.context.tool_manager import ToolContextManager
from friday_memory.controller import MemoryController
from friday_memory.lifecycle.stages import MemoryStage
from friday_memory.lifecycle.tool_content import ToolContentManager
from friday_memory.models import (
    ConsolidationReport,
    ContextPayload,
    InteractionTurn,
    SessionState,
    ToolRecommendation,
)

logger = logging.getLogger(__name__)


class ContextAssembler(ContextEngineeringInterface):
    """
    Standard assembler for the Friday Copilot.

    Implements rigid token budgeting and active search capabilities.
    Orchestrates the full context engineering lifecycle.

    Features:
    - Session management (initialize, restore checkpoint)
    - Memory extraction triggering
    - Consolidation orchestration
    - Context assembly with token budgeting
    - Prompt formatting via PromptArchitect
    """

    def __init__(
        self,
        memory_controller: MemoryController,
        prompt_architect: PromptArchitect | None = None,
        tool_manager: ToolContextManager | None = None,
        passage_router: PassageRouter | None = None,
        query_relevance_config: dict[str, Any] | None = None,
        model_name: str = "gpt-4",
        max_tokens: int = 8192,
        token_estimator_config: dict[str, Any] | None = None,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        """
        Initialize the Context Assembler.

        Args:
            memory_controller: The memory controller facade
            prompt_architect: Optional custom prompt architect
            tool_manager: Optional tool context manager for tool selection
            model_name: Model name for token counting
            max_tokens: Maximum context window tokens
            token_estimator_config: Optional token estimator configuration
            telemetry: Optional telemetry recorder
        """
        self._memory = memory_controller
        self._architect = prompt_architect or PromptArchitect(
            model_name=model_name,
            max_tokens=max_tokens,
        )
        self._tool_manager = tool_manager or ToolContextManager()
        self._passage_router = passage_router
        self._query_relevance_config = self._merge_query_relevance_config(
            query_relevance_config
        )
        self._model_name = model_name
        self._max_tokens = max_tokens
        self._telemetry = telemetry
        # Token counting now uses a configurable estimator (approx by default).
        self._token_estimator = build_token_estimator(token_estimator_config, model_name)

        # Session state storage (in production, this would be persistent)
        self._sessions: dict[str, SessionState] = {}

        # Extraction/consolidation callbacks (set by extractor/consolidator)
        self._extractor = None
        self._consolidator = None

        # Tool content lifecycle manager (optional)
        self._tool_content_manager: ToolContentManager | None = None

    def set_tool_content_manager(self, manager: ToolContentManager) -> None:
        """
        Set the tool content manager for lifecycle tracking.

        The tool content manager tracks large tool outputs and manages
        reference-based decay. When outputs aren't referenced for N turns,
        they're summarized to save context tokens.

        Args:
            manager: The ToolContentManager instance
        """
        self._tool_content_manager = manager
        logger.debug("Tool content manager configured for context assembler")

    @property
    def tool_content_manager(self) -> ToolContentManager | None:
        """Get the tool content manager (if configured)."""
        return self._tool_content_manager

    def set_extractor(self, extractor: Any) -> None:
        """Set the memory extractor for extraction cycles."""
        self._extractor = extractor

    def set_consolidator(self, consolidator: Any) -> None:
        """Set the memory consolidator for consolidation cycles."""
        self._consolidator = consolidator

    @property
    def last_budget_status(self) -> Any:
        """Budget status from the most recent format_prompt() call.

        Returns the ``BudgetStatus`` computed by
        ``PromptArchitect._validate_prompt_budget()`` during the last
        ``format_prompt()`` invocation.  Returns ``None`` if
        ``format_prompt()`` has not been called yet.

        Returns:
            BudgetStatus or None.
        """
        return self._architect.last_budget_status

    def set_passage_router(self, router: PassageRouter | None) -> None:
        """Set the passage router for conditional passage inclusion."""
        self._passage_router = router

    def set_query_relevance_config(self, config: dict[str, Any] | None) -> None:
        """Set the query relevance filter configuration."""
        self._query_relevance_config = self._merge_query_relevance_config(config)

    # --- Tool Management ---

    def set_active_tools(self, tools: list[dict[str, Any]]) -> None:
        """
        Set the active tools for the current task.

        This method allows an agent to inject selected tools into the
        context assembly process. Only active tools will be included
        in the context payload.

        Args:
            tools: List of tool schemas to activate. Each schema should
                   have 'name', 'description', and 'parameters' fields.

        Example:
            ```python
            assembler.set_active_tools([
                {"name": "read_file", "description": "Read file contents", ...},
                {"name": "write_file", "description": "Write to file", ...},
            ])
            ```
        """
        self._tool_manager.set_active_tools(tools)
        self._emit_event(
            "active_tools_set",
            {"tool_count": len(tools), "tool_names": [t.get("name") for t in tools]},
        )

    def expand_tools(self, additional_tools: list[dict[str, Any]]) -> int:
        """
        Expand active tools with additional ones.

        Used in hybrid mode when an agent needs to add more tools
        mid-task without replacing the existing set.

        Args:
            additional_tools: Tools to add to the active set.

        Returns:
            Number of tools actually added (respects max_tools limit).
        """
        added = self._tool_manager.expand_tools(additional_tools)
        if added > 0:
            self._emit_event(
                "tools_expanded",
                {"tools_added": added, "total_tools": len(self._tool_manager.active_tools)},
            )
        return added

    def clear_tools(self) -> None:
        """
        Clear all active tools and recommendations.

        Should be called at the end of a task to reset tool state.
        """
        self._tool_manager.clear_tools()
        self._emit_event("tools_cleared", {})

    def get_tool_budget_info(
        self, tools: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """
        Get information about tool token budget usage.

        Args:
            tools: Tools to analyze (uses active_tools if None).

        Returns:
            Dictionary with budget information including:
            - tool_count: Number of tools
            - estimated_tokens: Estimated token usage
            - budget_limit: Maximum allowed tokens
            - usage_percent: Percentage of budget used
        """
        return self._tool_manager.get_budget_info(tools)

    def recommend_tools(
        self,
        query: str,
        available_tools: list[dict[str, Any]] | None = None,
        top_k: int = 5,
    ) -> list[ToolRecommendation]:
        """
        Generate tool recommendations based on query.

        Uses the ToolContextManager's recommendation logic to suggest
        relevant tools for a given query.

        Args:
            query: User query or task description.
            available_tools: Tools to consider (uses active tools if None).
            top_k: Maximum recommendations to return.

        Returns:
            List of ToolRecommendation objects with scores and reasons.
        """
        tools = available_tools if available_tools is not None else self._tool_manager.active_tools
        return self._tool_manager.generate_recommendations(query, tools, top_k)

    @property
    def active_tools(self) -> list[dict[str, Any]]:
        """Get currently active tool schemas."""
        return self._tool_manager.active_tools

    @property
    def tool_recommendations(self) -> list[ToolRecommendation]:
        """Get current tool recommendations."""
        return self._tool_manager.recommendations

    def calculate_budget_limit(
        self,
        system_prompt: str,
        tool_definitions: list[dict[str, Any]] | None = None,
    ) -> int:
        """
        Calculate the available token budget for dynamic content.

        Uses PromptArchitect.calculate_dynamic_limit() to compute:
        Dynamic_Limit = Model_Max_Tokens - Fixed_Cost

        Fixed_Cost = len(System_Prompt) + len(Tool_Definitions) + Output_Buffer

        Args:
            system_prompt: The base system prompt
            tool_definitions: Optional tool definitions

        Returns:
            Available tokens for dynamic content (context + history)
        """
        return self._architect.calculate_dynamic_limit(system_prompt, tool_definitions)

    @property
    def max_tokens(self) -> int:
        """Get the maximum context window tokens."""
        return self._max_tokens

    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    def _count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        # Swapped from tiktoken to estimator to reduce CPU latency.
        return self._token_estimator.count(text)

    # --- Session Management ---

    async def initialize_session(
        self, session_id: str, user_id: str
    ) -> SessionState:
        """
        Loads or creates the session context, establishing the 'Thread'.

        Args:
            session_id: Unique session identifier
            user_id: User identifier for personalization

        Returns:
            SessionState for the session
        """
        if session_id in self._sessions:
            # Return existing session
            return self._sessions[session_id]

        # Create new session
        state = SessionState(
            session_id=session_id,
            user_id=user_id,
            turn_count=0,
            start_time=datetime.now(),
            active_goals=[],
            scoped_vars={},
        )
        self._sessions[session_id] = state

        self._emit_event(
            "session_initialized",
            {"session_id": session_id, "user_id": user_id},
        )
        return state

    async def restore_checkpoint(
        self, session_id: str, turn_id: str
    ) -> SessionState:
        """
        Reverts the session state to a previous turn.

        1. Triggers MemoryController.rewind_session()
        2. Reloads the SessionState effective at that time

        Args:
            session_id: The session to restore
            turn_id: The turn ID to restore to

        Returns:
            The restored SessionState
        """
        # Rewind the episodic history
        await self._memory.rewind_session(session_id, turn_id)

        # Get the remaining turns to determine turn count
        remaining_turns = await self._memory.episodic.get_turns(session_id, limit=1000)

        # Update session state
        if session_id in self._sessions:
            state = self._sessions[session_id]
            state.turn_count = len(remaining_turns)
        else:
            # Recreate session state
            state = SessionState(
                session_id=session_id,
                user_id="unknown",
                turn_count=len(remaining_turns),
                start_time=datetime.now(),
                active_goals=[],
                scoped_vars={},
            )
            self._sessions[session_id] = state

        self._emit_event(
            "checkpoint_restored",
            {"session_id": session_id, "turn_id": turn_id, "turns_remaining": len(remaining_turns)},
        )
        return state

    # --- The Ingestion Cycle (Extraction) ---

    async def extract_context(
        self,
        interaction_turn: InteractionTurn,
        async_execution: bool = True,
    ) -> None:
        """
        Analyzes the last turn to identify 'Hot' facts or memories.
        Triggers 'Memory Generation' (Extraction) tasks.

        Args:
            interaction_turn: The interaction turn to analyze
            async_execution: If True, run extraction asynchronously
        """
        if self._extractor is None:
            logger.warning("No extractor configured, skipping extraction")
            return

        if async_execution:
            # In a real implementation, this would use an event bus
            # For now, we just call the extractor directly
            import asyncio
            asyncio.create_task(
                self._extractor.extract(interaction_turn)
            )
        else:
            # Blocking extraction for critical updates
            await self._extractor.extract(interaction_turn)

        self._emit_event(
            "extraction_triggered",
            {"turn_id": interaction_turn.id, "async": async_execution},
        )

    # --- The Maintenance Cycle (Consolidation) ---

    async def consolidate_memory(self, session_id: str) -> ConsolidationReport:
        """
        Merges fragmented short-term memories into solidified long-term blocks.
        Resolves conflicts and summarizes 'drift'.

        Args:
            session_id: The session to consolidate

        Returns:
            ConsolidationReport with telemetry
        """
        if self._consolidator is None:
            logger.warning("No consolidator configured, returning empty report")
            return ConsolidationReport(
                session_id=session_id,
                nodes_created=0,
                nodes_merged=0,
                conflicts_resolved=0,
                tokens_condensed=0,
                errors=["No consolidator configured"],
            )

        return await self._consolidator.consolidate(session_id)

    # --- The Retrieval Cycle (Construction) ---

    async def assemble_context(
        self,
        query: str,
        state: SessionState,
        budget_limit: int,
        available_tools: list[dict[str, Any]] | None = None,
    ) -> ContextPayload:
        """
        The core 'Recall' step.
        Selects, Ranks, and Compresses data into the Context Window.

        Supports both Passive and Active retrieval scenarios:
        - Passive: Query is the user's last message
        - Active: Query is an Agent-generated search string

        Context priming (injecting prior session knowledge) is handled
        by MemoryController.recall().

        Tool context integration:
        - If available_tools provided, builds tool context with budgeting
        - If active_tools already set, uses those instead
        - Tool schemas and recommendations are included in payload

        Args:
            query: The search string
            state: Current session state
            budget_limit: Calculated token ceiling (Dynamic_Limit)
            available_tools: Optional tools to consider for selection.
                            If None, uses active_tools from tool_manager.

        Returns:
            ContextPayload: Strictly budgeted retrieval results with tool context
        """
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("context_assembly")

        try:
            # Retrieve from memory controller (includes priming if enabled)
            payload = await self._memory.recall(
                query=query,
                session_id=state.session_id,
                token_limit=budget_limit,
                include_history=True,
            )

            # Optionally route/guard passage inclusion
            if self._passage_router:
                payload = await self._apply_passage_routing(payload, query)

            # Apply token budget with priority hierarchy
            budgeted_payload = self._apply_budget(payload, budget_limit, query=query)

            # Build tool context if tools are available
            tool_schemas: list[dict[str, Any]] = []
            recommendations: list[ToolRecommendation] = []
            tool_hints: list[str] = []

            tools_to_use = available_tools if available_tools is not None else self._tool_manager.active_tools
            if tools_to_use:
                # Calculate tool budget (25% of total budget by default)
                tool_budget = int(budget_limit * 0.25)

                tool_schemas, recommendations = self._tool_manager.build_tool_context(
                    query=query,
                    budget=tool_budget,
                    available_tools=tools_to_use,
                )

                # Generate usage hints based on recommendations
                if recommendations:
                    for rec in recommendations[:3]:  # Top 3 hints
                        tool_hints.append(f"Consider using {rec.tool_name}: {rec.reason}")

            # Create final payload with tool context
            final_payload = ContextPayload(
                history=budgeted_payload.history,
                prior_history=budgeted_payload.prior_history,
                passages=budgeted_payload.passages,
                entities=budgeted_payload.entities,
                facts=budgeted_payload.facts,
                recent_memories=budgeted_payload.recent_memories,
                insights=budgeted_payload.insights,
                summaries=budgeted_payload.summaries,
                                # Tool context fields
                tool_schemas=tool_schemas,
                recommended_tools=recommendations,
                tool_usage_hints=tool_hints,
                debug_info={
                    **budgeted_payload.debug_info,
                    "tool_count": len(tool_schemas),
                    "recommendation_count": len(recommendations),
                },
            )

            self._emit_event(
                "context_assembled",
                {
                    "session_id": state.session_id,
                    "query_length": len(query),
                    "budget_limit": budget_limit,
                    "history_count": len(final_payload.history),
                    "passages_count": len(final_payload.passages),
                    "entities_count": len(final_payload.entities),
                    "tool_count": len(tool_schemas),
                    "recommendation_count": len(recommendations),
                },
            )

            return final_payload

        finally:
            if span_id:
                self._telemetry.end_span(span_id)

    async def _apply_passage_routing(
        self, payload: ContextPayload, query: str
    ) -> ContextPayload:
        """
        Use the passage router to decide whether to include vector passages.

        Applies similarity guardrails when passages are included.
        Adds routing metadata to debug_info for observability.
        """
        if not payload.passages:
            return payload

        decision = await self._passage_router.decide(query)
        original_count = len(payload.passages)

        if decision.include_passages:
            filtered_passages, excluded = self._passage_router.filter_passages(
                payload.passages
            )
            included = len(filtered_passages)
        else:
            filtered_passages = []
            excluded = original_count
            included = 0

        return ContextPayload(
            history=payload.history,
            prior_history=payload.prior_history,
            passages=filtered_passages,
            entities=payload.entities,
            facts=payload.facts,
            recent_memories=payload.recent_memories,
            insights=payload.insights,
            summaries=payload.summaries,
                        # Preserve tool fields (even if empty at this stage)
            tool_schemas=payload.tool_schemas,
            recommended_tools=payload.recommended_tools,
            tool_usage_hints=payload.tool_usage_hints,
            debug_info={
                **payload.debug_info,
                "passage_router_enabled": True,
                "passage_router_include": decision.include_passages,
                "passage_router_confidence": decision.confidence,
                "passage_router_reason": decision.reason,
                "passage_router_original": original_count,
                "passage_router_included": included,
                "passage_router_excluded": excluded,
            },
        )

    def _apply_budget(
        self, payload: ContextPayload, budget_limit: int, query: str = ""
    ) -> ContextPayload:
        """
        Apply token budget with lifecycle-aware priority hierarchy.

        Priority Hierarchy (Drop Order - lowest first):
        1. DECAYED memories: Always excluded
        2. Deep History: Turns 10+ ago
        3. Low relevancy long-term: Long-term with inclusion_score < 0.3
        4. Weak Matches: Vector passages with relevancy_score < 0.5
        5. Recent History: Turns 3-10
        6. Immediate Context: Last 2 Turns, User Query, Short-term memories

        Lifecycle-aware enhancements:
        - Uses inclusion_score (similarity × retrieval_factor) when available
        - Prioritizes short-term memories (hot context) over long-term
        - Filters DECAYED memories as safety measure
        - Conditionally excludes summaries when full history is present
        - Filters insights/summaries by query relevance (keyword overlap)
        """
        # Step 0: Filter out any DECAYED memories that slipped through
        filtered_payload = self._filter_decayed(payload)

        # Step 0.5: Conditionally exclude summaries if history is complete
        # Summaries are redundant when we have full conversation history
        filtered_payload = self._apply_conditional_summaries(filtered_payload)

        # Step 0.6: Filter supporting context by query relevance (keyword overlap)
        # This reduces irrelevant artifacts without expensive embedding computation
        if query:
            filtered_payload = self._filter_by_query_relevance(filtered_payload, query)

        current_tokens = self._estimate_payload_tokens(filtered_payload)

        if current_tokens <= budget_limit:
            return filtered_payload

        logger.info(
            f"Context pruning required: {current_tokens} > {budget_limit} tokens"
        )

        # Make mutable copies (including prior_history which was previously ignored!)
        prior_history = list(filtered_payload.prior_history)
        history = list(filtered_payload.history)
        passages = list(filtered_payload.passages)
        entities = list(filtered_payload.entities)
        facts = list(filtered_payload.facts)
        insights = list(filtered_payload.insights) if filtered_payload.insights else []
        summaries = list(filtered_payload.summaries) if filtered_payload.summaries else []

        # Separate short-term and long-term passages for lifecycle-aware pruning
        short_term, long_term = self._separate_by_stage(passages)

        # 0. Drop prior_history first (lowest priority - from previous sessions)
        # This is cross-session history that should be dropped before current session
        if prior_history:
            prior_history = []  # Drop all prior history first
            current_tokens = self._estimate_tokens_full(
                prior_history + history, short_term + long_term, entities, facts, insights, summaries
            )
            if current_tokens <= budget_limit:
                return self._create_pruned_payload_full(
                    filtered_payload, history, short_term + long_term, entities, facts, insights, summaries,
                    prior_history=prior_history
                )

        # 1. Drop deep history (turns 10+)
        if len(history) > 10:
            history = history[-10:]
            current_tokens = self._estimate_tokens_full(
                history, short_term + long_term, entities, facts, insights, summaries
            )
            if current_tokens <= budget_limit:
                return self._create_pruned_payload_full(
                    filtered_payload, history, short_term + long_term, entities, facts, insights, summaries,
                    prior_history=prior_history
                )

        # 2. Drop low-relevancy long-term memories (inclusion_score < 0.3)
        long_term = [p for p in long_term if self._get_relevancy_score(p) >= 0.3]
        current_tokens = self._estimate_tokens_full(
            history, short_term + long_term, entities, facts, insights, summaries
        )
        if current_tokens <= budget_limit:
            return self._create_pruned_payload_full(
                filtered_payload, history, short_term + long_term, entities, facts, insights, summaries,
                prior_history=prior_history
            )

        # 3. Drop weak vector matches (relevancy_score < 0.5)
        short_term = [p for p in short_term if self._get_relevancy_score(p) >= 0.5]
        long_term = [p for p in long_term if self._get_relevancy_score(p) >= 0.5]
        current_tokens = self._estimate_tokens_full(
            history, short_term + long_term, entities, facts, insights, summaries
        )
        if current_tokens <= budget_limit:
            return self._create_pruned_payload_full(
                filtered_payload, history, short_term + long_term, entities, facts, insights, summaries,
                prior_history=prior_history
            )

        # 4. Drop more history (keep last 5)
        if len(history) > 5:
            history = history[-5:]
            current_tokens = self._estimate_tokens_full(
                history, short_term + long_term, entities, facts, insights, summaries
            )
            if current_tokens <= budget_limit:
                return self._create_pruned_payload_full(
                    filtered_payload, history, short_term + long_term, entities, facts, insights, summaries,
                    prior_history=prior_history
                )

        # 5. Reduce to top passages by relevancy (keep short-term first)
        short_term = self._sort_by_relevancy(short_term)[:3]
        long_term = self._sort_by_relevancy(long_term)[:2]
        current_tokens = self._estimate_tokens_full(
            history, short_term + long_term, entities, facts, insights, summaries
        )
        if current_tokens <= budget_limit:
            return self._create_pruned_payload_full(
                filtered_payload, history, short_term + long_term, entities, facts, insights, summaries,
                prior_history=prior_history
            )

        # 6. Drop insights and summaries
        insights = insights[:3]
        summaries = summaries[:3]
        current_tokens = self._estimate_tokens_full(
            history, short_term + long_term, entities, facts, insights, summaries
        )
        if current_tokens <= budget_limit:
            return self._create_pruned_payload_full(
                filtered_payload, history, short_term + long_term, entities, facts, insights, summaries,
                prior_history=prior_history
            )

        # 7. Drop entities and facts
        entities = entities[:5]
        facts = facts[:5]
        current_tokens = self._estimate_tokens_full(
            history, short_term + long_term, entities, facts, insights, summaries
        )
        if current_tokens <= budget_limit:
            return self._create_pruned_payload_full(
                filtered_payload, history, short_term + long_term, entities, facts, insights, summaries,
                prior_history=prior_history
            )

        # 8. Keep only last 2 turns (critical)
        history = history[-2:] if len(history) >= 2 else history
        short_term = short_term[:2]
        long_term = []
        entities = []
        facts = []
        insights = []
        summaries = []

        self._emit_event(
            "context_pruning_warning",
            {
                "original_tokens": self._estimate_payload_tokens(payload),
                "budget_limit": budget_limit,
                "final_tokens": self._estimate_tokens_full(
                    history, short_term, entities, facts, insights, summaries
                ),
            },
        )

        return self._create_pruned_payload_full(
            filtered_payload, history, short_term, entities, facts, insights, summaries,
            prior_history=prior_history
        )

    def _filter_decayed(self, payload: ContextPayload) -> ContextPayload:
        """
        Filter out DECAYED memories from the payload.

        Safety measure to ensure DECAYED memories never appear in context,
        even if they somehow slip through retrieval filters.

        Args:
            payload: The context payload to filter

        Returns:
            Filtered payload with no DECAYED memories
        """
        filtered_passages = []
        decayed_count = 0

        for passage in payload.passages:
            metadata = passage.get("metadata", {})
            stage = metadata.get("stage", "")

            # Check if memory is decayed
            if stage == MemoryStage.DECAYED.value or stage == "decayed":
                decayed_count += 1
                continue

            filtered_passages.append(passage)

        if decayed_count > 0:
            logger.info(f"Filtered {decayed_count} DECAYED memories from context")
            self._emit_event(
                "decayed_memories_filtered",
                {"count": decayed_count},
            )

        # Return new payload if filtering occurred
        if decayed_count > 0:
            return ContextPayload(
                history=payload.history,
                prior_history=payload.prior_history,
                passages=filtered_passages,
                entities=payload.entities,
                facts=payload.facts,
                recent_memories=payload.recent_memories,
                insights=payload.insights,
                summaries=payload.summaries,
                                # Preserve tool fields
                tool_schemas=payload.tool_schemas,
                recommended_tools=payload.recommended_tools,
                tool_usage_hints=payload.tool_usage_hints,
                debug_info={
                    **payload.debug_info,
                    "decayed_filtered": decayed_count,
                },
            )

        return payload

    def _apply_conditional_summaries(self, payload: ContextPayload) -> ContextPayload:
        """
        Conditionally exclude conversation summaries when full history is present.

        Summaries are valuable ONLY when:
        1. History was truncated (summaries fill the gap for older context)
        2. Session is "cold" (no recent turns - summaries provide prior knowledge)

        When we have complete recent history, summaries are redundant and waste tokens.

        Args:
            payload: The context payload to process

        Returns:
            Payload with summaries cleared if conditions are met
        """
        # Define thresholds
        expected_history_limit = 10  # Typical history limit
        cold_session_threshold = 3   # If fewer turns, session is "cold"

        history_count = len(payload.history)
        summaries_count = len(payload.summaries) if payload.summaries else 0

        # No summaries to process
        if summaries_count == 0:
            return payload

        # Check if we should include summaries
        session_is_cold = history_count < cold_session_threshold
        history_is_complete = history_count >= expected_history_limit

        # Include summaries if session is cold OR history was NOT complete
        should_include_summaries = session_is_cold or not history_is_complete

        if should_include_summaries:
            logger.debug(
                f"Including summaries: session_cold={session_is_cold}, "
                f"history_complete={history_is_complete}, history_count={history_count}"
            )
            return payload

        # Exclude summaries - history is complete and session is warm
        logger.info(
            f"Excluding {summaries_count} summaries: full history present "
            f"({history_count} turns)"
        )
        self._emit_event(
            "summaries_excluded",
            {
                "reason": "full_history_present",
                "summaries_excluded": summaries_count,
                "history_count": history_count,
            },
        )

        return ContextPayload(
            history=payload.history,
            prior_history=payload.prior_history,
            passages=payload.passages,
            entities=payload.entities,
            facts=payload.facts,
            recent_memories=payload.recent_memories,
            insights=payload.insights,
            summaries=[],  # Clear summaries
                        # Preserve tool fields
            tool_schemas=payload.tool_schemas,
            recommended_tools=payload.recommended_tools,
            tool_usage_hints=payload.tool_usage_hints,
            debug_info={
                **payload.debug_info,
                "summaries_excluded": summaries_count,
                "summaries_exclusion_reason": "full_history_present",
            },
        )

    def _filter_by_query_relevance(
        self, payload: ContextPayload, query: str
    ) -> ContextPayload:
        """
        Filter supporting context by relevance to the current query.

        Uses lightweight keyword/entity overlap scoring to filter out
        items that are unlikely to be relevant to the query.
        This avoids expensive embedding computation while still improving
        context quality.
        """
        config = self._query_relevance_config
        if not config.get("enabled", False):
            return payload

        # Extract keywords from query (lowercased, removing common words)
        query_keywords = self._extract_keywords(query)
        min_query_keywords = int(config.get("min_query_keywords", 0))
        if config.get("skip_on_short_query", False) and len(query_keywords) < min_query_keywords:
            return payload

        apply_to = set(config.get("apply_to", []))
        min_overlap_ratio = float(config.get("min_overlap_ratio", 0.1))
        min_overlap_count = int(config.get("min_overlap_count", 1))
        keep_recent = config.get("keep_recent", {})

        def score_item(text: str, extra_keywords: set[str] | None = None) -> tuple[float, int]:
            item_keywords = self._extract_keywords(text)
            if extra_keywords:
                item_keywords |= extra_keywords
            if not item_keywords:
                return 0.0, 0
            overlap = query_keywords & item_keywords
            overlap_count = len(overlap)
            score = overlap_count / max(len(query_keywords), 1)
            return score, overlap_count

        def filter_items(
            items: list[dict[str, Any]],
            section: str,
            get_text: Callable[[dict[str, Any]], str],
            get_extra_keywords: Callable[[dict[str, Any]], set[str]] | None = None,
        ) -> tuple[list[dict[str, Any]], int]:
            if not items:
                return items, 0

            scored: list[tuple[dict[str, Any], float, int]] = []
            for item in items:
                text = get_text(item)
                extra = get_extra_keywords(item) if get_extra_keywords else None
                score, overlap_count = score_item(text, extra)
                scored.append((item, score, overlap_count))

            relevant: list[dict[str, Any]] = []
            relevant_ids: set[int] = set()
            for item, score, overlap_count in scored:
                if overlap_count >= min_overlap_count and score >= min_overlap_ratio:
                    relevant.append(item)
                    relevant_ids.add(id(item))

            keep_n = int(keep_recent.get(section, 0))
            if len(relevant) < keep_n:
                for item, _, _ in scored:
                    if id(item) in relevant_ids:
                        continue
                    relevant.append(item)
                    relevant_ids.add(id(item))
                    if len(relevant) >= keep_n:
                        break

            excluded = len(items) - len(relevant)
            return relevant, excluded

        insights = payload.insights
        summaries = payload.summaries
        passages = payload.passages

        excluded_insights = 0
        excluded_summaries = 0
        excluded_passages = 0

        if "insights" in apply_to and insights:
            def insight_extra_keywords(item: dict[str, Any]) -> set[str]:
                entities_mentioned = item.get("metadata", {}).get("entities_mentioned", "")
                if not entities_mentioned:
                    return set()
                return {e.strip().lower() for e in entities_mentioned.split(";") if e.strip()}

            insights, excluded_insights = filter_items(
                insights,
                "insights",
                lambda i: i.get("text", "") or i.get("document", ""),
                insight_extra_keywords,
            )

        if "summaries" in apply_to and summaries:
            summaries, excluded_summaries = filter_items(
                summaries,
                "summaries",
                lambda s: s.get("text", "") or s.get("document", ""),
            )

        if "passages" in apply_to and passages:
            def passage_extra_keywords(item: dict[str, Any]) -> set[str]:
                metadata = item.get("metadata", {})
                extra_parts = [
                    metadata.get("filename", ""),
                    metadata.get("source", ""),
                    metadata.get("title", ""),
                    metadata.get("tool_name", ""),
                    metadata.get("source_path", ""),
                    metadata.get("url", ""),
                ]
                extra_text = " ".join(p for p in extra_parts if p)
                return self._extract_keywords(extra_text)

            passages, excluded_passages = filter_items(
                passages,
                "passages",
                lambda p: p.get("text", ""),
                passage_extra_keywords,
            )

        if any([excluded_insights, excluded_summaries, excluded_passages]):
            logger.debug(
                "Query relevance filtering removed "
                f"insights={excluded_insights}, summaries={excluded_summaries}, "
                f"passages={excluded_passages}"
            )

        return ContextPayload(
            history=payload.history,
            prior_history=payload.prior_history,
            passages=passages,
            entities=payload.entities,
            facts=payload.facts,
            recent_memories=payload.recent_memories,
            insights=insights,
            summaries=summaries,
            # Preserve tool fields
            tool_schemas=payload.tool_schemas,
            recommended_tools=payload.recommended_tools,
            tool_usage_hints=payload.tool_usage_hints,
            debug_info={
                **payload.debug_info,
                "query_relevance_enabled": True,
                "query_relevance_sections": list(apply_to),
                "insights_filtered_by_relevance": excluded_insights,
                "summaries_filtered_by_relevance": excluded_summaries,
                "passages_filtered_by_relevance": excluded_passages,
            },
        )

    def _merge_query_relevance_config(
        self, config: dict[str, Any] | None
    ) -> dict[str, Any]:
        defaults: dict[str, Any] = {
            "enabled": False,
            "apply_to": ["insights"],
            "min_overlap_ratio": 0.1,
            "min_overlap_count": 1,
            "keep_recent": {
                "insights": 5,
                "summaries": 2,
                "passages": 2,
            },
            "min_query_keywords": 0,
            "skip_on_short_query": False,
        }

        if not config:
            return defaults

        merged = {**defaults, **config}
        merged_keep = {**defaults["keep_recent"], **config.get("keep_recent", {})}
        merged["keep_recent"] = merged_keep
        return merged

    def _extract_keywords(self, text: str) -> set[str]:
        """
        Extract meaningful keywords from text for relevance scoring.

        Uses simple word extraction with stopword filtering.
        Lightweight alternative to embedding-based similarity.

        Args:
            text: The text to extract keywords from

        Returns:
            Set of lowercase keywords
        """
        # Common stopwords to filter out
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
            "from", "up", "about", "into", "through", "during", "before", "after",
            "above", "below", "between", "under", "again", "further", "then",
            "once", "here", "there", "when", "where", "why", "how", "all", "each",
            "few", "more", "most", "other", "some", "such", "no", "nor", "not",
            "only", "own", "same", "so", "than", "too", "very", "just", "and",
            "but", "if", "or", "because", "as", "until", "while", "this", "that",
            "these", "those", "am", "it", "its", "i", "me", "my", "myself", "we",
            "our", "ours", "ourselves", "you", "your", "yours", "yourself",
            "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
            "herself", "they", "them", "their", "theirs", "themselves", "what",
            "which", "who", "whom", "also", "get", "got", "getting", "like",
            "really", "think", "know", "want", "make", "see", "say", "said",
        }

        # Extract words, lowercase, filter stopwords and short words
        words = text.lower().split()
        keywords = set()

        for word in words:
            # Clean punctuation
            clean_word = word.strip(".,!?\"'()[]{}:;-")
            if (
                clean_word
                and len(clean_word) > 2
                and clean_word not in stopwords
                and not clean_word.isdigit()
            ):
                keywords.add(clean_word)

        return keywords

    def _separate_by_stage(
        self, passages: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """
        Separate passages into short-term and long-term lists.

        Short-term memories are prioritized in budget decisions.

        Args:
            passages: List of passage dicts

        Returns:
            Tuple of (short_term, long_term) passage lists
        """
        short_term = []
        long_term = []

        for passage in passages:
            metadata = passage.get("metadata", {})
            stage = metadata.get("stage", "")

            if stage == MemoryStage.SHORT_TERM.value or stage == "short_term":
                short_term.append(passage)
            else:
                # Default to long-term if no stage (legacy data)
                long_term.append(passage)

        return short_term, long_term

    def _get_relevancy_score(self, passage: dict[str, Any]) -> float:
        """
        Get the relevancy score for a passage.

        Uses inclusion_score if available (lifecycle-aware scoring),
        falls back to similarity score.

        Args:
            passage: Passage dict with similarity/inclusion_score

        Returns:
            Relevancy score between 0.0 and 1.0
        """
        # Prefer inclusion_score (combines similarity + retrieval_factor)
        if "inclusion_score" in passage:
            return passage["inclusion_score"]

        # Fall back to similarity
        return passage.get("similarity", 0.0)

    def _sort_by_relevancy(
        self, passages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Sort passages by relevancy score (highest first).

        Args:
            passages: List of passage dicts

        Returns:
            Sorted list
        """
        return sorted(
            passages,
            key=lambda x: self._get_relevancy_score(x),
            reverse=True,
        )

    def _estimate_tokens_full(
        self,
        history: list,
        passages: list,
        entities: list,
        facts: list,
        insights: list,
        summaries: list,
    ) -> int:
        """Estimate tokens for given content including insights and summaries."""
        total = self._estimate_tokens(history, passages, entities, facts)

        # Insight tokens
        for insight in insights:
            total += self._count_tokens(insight.get("text", ""))

        # Summary tokens
        for summary in summaries:
            total += self._count_tokens(summary.get("text", ""))

        return total

    def _create_pruned_payload_full(
        self,
        original: ContextPayload,
        history: list,
        passages: list,
        entities: list,
        facts: list,
        insights: list,
        summaries: list,
        prior_history: list | None = None,
    ) -> ContextPayload:
        """Create a new payload with pruned content including insights/summaries."""
        return ContextPayload(
            history=history,
            prior_history=prior_history if prior_history is not None else original.prior_history,
            passages=passages,
            entities=entities,
            facts=facts,
            recent_memories=original.recent_memories,
            insights=insights,
            summaries=summaries,
            # Preserve tool fields
            tool_schemas=original.tool_schemas,
            recommended_tools=original.recommended_tools,
            tool_usage_hints=original.tool_usage_hints,
            debug_info={
                **original.debug_info,
                "pruned": True,
                "original_history": len(original.history),
                "original_prior_history": len(original.prior_history),
                "original_passages": len(original.passages),
                "original_insights": len(original.insights) if original.insights else 0,
                "original_summaries": len(original.summaries) if original.summaries else 0,
            },
        )

    def _estimate_payload_tokens(self, payload: ContextPayload) -> int:
        """Estimate total tokens in a payload (includes prior_history)."""
        return self._estimate_tokens_full(
            list(payload.prior_history) + list(payload.history),
            payload.passages,
            payload.entities,
            payload.facts,
            payload.insights or [],
            payload.summaries or [],
        )

    def _estimate_tokens(
        self,
        history: list,
        passages: list,
        entities: list,
        facts: list,
    ) -> int:
        """Estimate tokens for given content."""
        total = 0

        # History tokens
        for turn in history:
            if hasattr(turn, "user_message"):
                total += self._count_tokens(turn.user_message or "")
            if hasattr(turn, "assistant_message"):
                total += self._count_tokens(turn.assistant_message or "")

        # Passage tokens
        for passage in passages:
            total += self._count_tokens(passage.get("text", ""))

        # Entity tokens (estimate)
        total += len(entities) * 50  # ~50 tokens per entity

        # Fact tokens (estimate)
        total += len(facts) * 30  # ~30 tokens per fact

        return total

    def _create_pruned_payload(
        self,
        original: ContextPayload,
        history: list,
        passages: list,
        entities: list,
        facts: list,
    ) -> ContextPayload:
        """Create a new payload with pruned content."""
        return ContextPayload(
            history=history,
            prior_history=original.prior_history,
            passages=passages,
            entities=entities,
            facts=facts,
            recent_memories=original.recent_memories,
            insights=original.insights,
            summaries=original.summaries,
            # Preserve tool fields
            tool_schemas=original.tool_schemas,
            recommended_tools=original.recommended_tools,
            tool_usage_hints=original.tool_usage_hints,
            debug_info={
                **original.debug_info,
                "pruned": True,
                "original_history": len(original.history),
                "original_prior_history": len(original.prior_history),
                "original_passages": len(original.passages),
            },
        )

    # --- The Formatting Cycle (Architecture) ---

    async def format_prompt(
        self,
        system_prompt: str,
        payload: ContextPayload,
        context_format: str = "plain",
        user_query: str | None = None,
        turn_count: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Physically arranges messages for optimal model attention.

        Delegates to PromptArchitect for the actual formatting.

        Args:
            system_prompt: The base system prompt
            payload: The assembled context payload
            context_format: Output format for supporting context.
                Options: "plain" (default), "json", "xml", "markdown"
            user_query: The current user message. If None, extracts from
                the last history item.
            turn_count: Current conversation turn count (for cache eligibility)

        Returns:
            List of message dicts in OpenAI-compatible format
        """
        # Get session state if available
        state = None
        if payload.debug_info.get("session_id"):
            state = self._sessions.get(payload.debug_info["session_id"])

        # Use provided user_query, or extract from last history item
        query = user_query
        if query is None:
            query = ""
            if payload.history:
                last_turn = payload.history[-1]
                if hasattr(last_turn, "user_message"):
                    query = last_turn.user_message or ""

        return self._architect.format_prompt(
            system_prompt=system_prompt,
            user_query=query,
            payload=payload,
            state=state,
            context_format=context_format,
            turn_count=turn_count,
        )
