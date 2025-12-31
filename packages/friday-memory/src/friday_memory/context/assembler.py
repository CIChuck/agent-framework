"""
Context Assembler.
Implements the 'Knapsack' budgeting logic to fit memory into the token window.
Handles Active Search queries.

Ref: Batch 2a Specification, Section 2
"""

import logging
from datetime import datetime
from typing import Any

import tiktoken

from friday_core import ContextEngineeringInterface, TelemetryInterface

from friday_memory.context.layout import PromptArchitect
from friday_memory.controller import MemoryController
from friday_memory.models import (
    ConsolidationReport,
    ContextPayload,
    InteractionTurn,
    SessionState,
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
        model_name: str = "gpt-4",
        max_tokens: int = 8192,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        """
        Initialize the Context Assembler.

        Args:
            memory_controller: The memory controller facade
            prompt_architect: Optional custom prompt architect
            model_name: Model name for token counting
            max_tokens: Maximum context window tokens
            telemetry: Optional telemetry recorder
        """
        self._memory = memory_controller
        self._architect = prompt_architect or PromptArchitect(
            model_name=model_name,
            max_tokens=max_tokens,
        )
        self._model_name = model_name
        self._max_tokens = max_tokens
        self._telemetry = telemetry

        # Session state storage (in production, this would be persistent)
        self._sessions: dict[str, SessionState] = {}

        # Initialize tokenizer
        try:
            self._encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self._encoding = tiktoken.get_encoding("cl100k_base")

        # Extraction/consolidation callbacks (set by extractor/consolidator)
        self._extractor = None
        self._consolidator = None

    def set_extractor(self, extractor: Any) -> None:
        """Set the memory extractor for extraction cycles."""
        self._extractor = extractor

    def set_consolidator(self, consolidator: Any) -> None:
        """Set the memory consolidator for consolidation cycles."""
        self._consolidator = consolidator

    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    def _count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self._encoding.encode(text))

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
    ) -> ContextPayload:
        """
        The core 'Recall' step.
        Selects, Ranks, and Compresses data into the Context Window.

        Supports both Passive and Active retrieval scenarios:
        - Passive: Query is the user's last message
        - Active: Query is an Agent-generated search string

        Args:
            query: The search string
            state: Current session state
            budget_limit: Calculated token ceiling (Dynamic_Limit)

        Returns:
            ContextPayload: Strictly budgeted retrieval results
        """
        span_id = None
        if self._telemetry:
            span_id = self._telemetry.start_span("context_assembly")

        try:
            # Retrieve from memory controller
            payload = await self._memory.recall(
                query=query,
                session_id=state.session_id,
                token_limit=budget_limit,
                include_history=True,
            )

            # Apply token budget with priority hierarchy
            budgeted_payload = self._apply_budget(payload, budget_limit)

            self._emit_event(
                "context_assembled",
                {
                    "session_id": state.session_id,
                    "query_length": len(query),
                    "budget_limit": budget_limit,
                    "history_count": len(budgeted_payload.history),
                    "passages_count": len(budgeted_payload.passages),
                    "entities_count": len(budgeted_payload.entities),
                },
            )

            return budgeted_payload

        finally:
            if span_id:
                self._telemetry.end_span(span_id)

    def _apply_budget(
        self, payload: ContextPayload, budget_limit: int
    ) -> ContextPayload:
        """
        Apply token budget with priority hierarchy.

        Priority Hierarchy (Drop Order - lowest first):
        1. Deep History: Turns 10+ ago
        2. Scoped State: 'app:' vars (Low), 'session:' vars (High)
        3. Weak Matches: Vector passages with low similarity
        4. Recent History: Turns 3-10
        5. Immediate Context: Last 2 Turns, User Query, 'user:' scoped vars
        """
        current_tokens = self._estimate_payload_tokens(payload)

        if current_tokens <= budget_limit:
            return payload

        logger.info(
            f"Context pruning required: {current_tokens} > {budget_limit} tokens"
        )

        # Make mutable copies
        history = list(payload.history)
        passages = list(payload.passages)
        entities = list(payload.entities)
        facts = list(payload.facts)

        # 1. Drop deep history (turns 10+)
        if len(history) > 10:
            history = history[-10:]
            current_tokens = self._estimate_tokens(history, passages, entities, facts)
            if current_tokens <= budget_limit:
                return self._create_pruned_payload(
                    payload, history, passages, entities, facts
                )

        # 2. Drop weak vector matches (similarity < 0.5)
        passages = [p for p in passages if p.get("similarity", 0) >= 0.5]
        current_tokens = self._estimate_tokens(history, passages, entities, facts)
        if current_tokens <= budget_limit:
            return self._create_pruned_payload(
                payload, history, passages, entities, facts
            )

        # 3. Drop more history (keep last 5)
        if len(history) > 5:
            history = history[-5:]
            current_tokens = self._estimate_tokens(history, passages, entities, facts)
            if current_tokens <= budget_limit:
                return self._create_pruned_payload(
                    payload, history, passages, entities, facts
                )

        # 4. Reduce passages to top 3
        passages = sorted(passages, key=lambda x: x.get("similarity", 0), reverse=True)[:3]
        current_tokens = self._estimate_tokens(history, passages, entities, facts)
        if current_tokens <= budget_limit:
            return self._create_pruned_payload(
                payload, history, passages, entities, facts
            )

        # 5. Drop entities and facts
        entities = entities[:5]
        facts = facts[:5]
        current_tokens = self._estimate_tokens(history, passages, entities, facts)
        if current_tokens <= budget_limit:
            return self._create_pruned_payload(
                payload, history, passages, entities, facts
            )

        # 6. Keep only last 2 turns (critical)
        history = history[-2:] if len(history) >= 2 else history
        passages = passages[:2]
        entities = []
        facts = []

        self._emit_event(
            "context_pruning_warning",
            {
                "original_tokens": self._estimate_payload_tokens(payload),
                "budget_limit": budget_limit,
                "final_tokens": self._estimate_tokens(history, passages, entities, facts),
            },
        )

        return self._create_pruned_payload(
            payload, history, passages, entities, facts
        )

    def _estimate_payload_tokens(self, payload: ContextPayload) -> int:
        """Estimate total tokens in a payload."""
        return self._estimate_tokens(
            payload.history, payload.passages, payload.entities, payload.facts
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
            passages=passages,
            entities=entities,
            facts=facts,
            recent_memories=original.recent_memories,
            debug_info={
                **original.debug_info,
                "pruned": True,
                "original_history": len(original.history),
                "original_passages": len(original.passages),
            },
        )

    # --- The Formatting Cycle (Architecture) ---

    async def format_prompt(
        self,
        system_prompt: str,
        payload: ContextPayload,
    ) -> list[dict[str, Any]]:
        """
        Physically arranges messages for optimal model attention.

        Delegates to PromptArchitect for the actual formatting.

        Args:
            system_prompt: The base system prompt
            payload: The assembled context payload

        Returns:
            List of message dicts in OpenAI-compatible format
        """
        # Get session state if available
        state = None
        if payload.debug_info.get("session_id"):
            state = self._sessions.get(payload.debug_info["session_id"])

        # Extract user query from the last history item or use empty
        user_query = ""
        if payload.history:
            last_turn = payload.history[-1]
            if hasattr(last_turn, "user_message"):
                user_query = last_turn.user_message or ""

        return self._architect.format_prompt(
            system_prompt=system_prompt,
            user_query=user_query,
            payload=payload,
            state=state,
        )
