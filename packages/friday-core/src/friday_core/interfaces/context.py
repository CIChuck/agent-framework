"""
Context Engineering Interface Protocol.
Defines the standard lifecycle for context engineering strategies.

Ref: Batch 2a Specification, Section 1.1

Note: Type references like 'SessionState', 'ConsolidationReport', 'ContextPayload',
and 'Interaction' are forward references to models that will be defined in
friday-memory/models/. This allows the protocol to be defined without circular imports.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Forward references to types defined in friday-memory/models/
    # These are only used for type checking, not at runtime


    type SessionState = Any  # Will be friday_memory.models.SessionState
    type ConsolidationReport = (
        Any  # Will be friday_memory.models.ConsolidationReport
    )
    type ContextPayload = Any  # Will be friday_memory.models.ContextPayload
    type Interaction = Any  # Will be friday_memory.models.Interaction


class ContextEngineeringInterface(ABC):
    """
    The Master Protocol for Context Engineering.

    Defines the standard lifecycle methods that any context strategy must
    implement. This abstraction ensures the underlying Memory Architecture
    is decoupled from the strategy used to process it.

    Lifecycle:
    1. initialize_session() - Start or resume a session
    2. extract_context() - Harvest facts from new interactions
    3. consolidate_memory() - Merge short-term into long-term memory
    4. assemble_context() - Build the context payload for inference
    5. format_prompt() - Structure the final prompt for the LLM

    Implementations:
    - ContextAssembler (default for Friday Copilot)
    - Custom strategies can be "snapped in" via this interface
    """

    # --- Session Management ---

    @abstractmethod
    async def initialize_session(self, session_id: str, user_id: str) -> "SessionState":
        """
        Loads or creates the session context, establishing the 'Thread'.

        Args:
            session_id: Unique identifier for the session
            user_id: Unique identifier for the user

        Returns:
            SessionState containing session metadata and scoped variables
        """
        pass

    @abstractmethod
    async def restore_checkpoint(self, session_id: str, turn_id: str) -> "SessionState":
        """
        Reverts the session state to a previous turn.

        Used for error recovery - allows "time travel" to undo mistakes.

        Algorithm:
        1. Triggers MemoryController.rollback_session()
        2. Reloads the SessionState effective at that time

        Args:
            session_id: Unique identifier for the session
            turn_id: The turn ID to restore to

        Returns:
            SessionState as it was at the target turn
        """
        pass

    # --- The Ingestion Cycle (Extraction) ---

    @abstractmethod
    async def extract_context(
        self, interaction_turn: "Interaction", async_execution: bool = True
    ) -> None:
        """
        Analyzes the last turn to identify 'Hot' facts or memories.

        Triggers 'Memory Generation' (Extraction) tasks to harvest
        entities, preferences, and other structured data from the
        raw conversation.

        Args:
            interaction_turn: The completed interaction to analyze
            async_execution: If True, run extraction in background (default)
                           If False, block until extraction completes
        """
        pass

    # --- The Maintenance Cycle (Consolidation) ---

    @abstractmethod
    async def consolidate_memory(self, session_id: str) -> "ConsolidationReport":
        """
        Merges fragmented short-term memories into solidified long-term blocks.

        Performs:
        - Deduplication of similar facts
        - Summarization of verbose interaction sequences
        - Conflict resolution when facts contradict
        - Entity resolution (merging 'Bob' and 'Robert')

        Args:
            session_id: The session to consolidate

        Returns:
            ConsolidationReport with statistics on the consolidation
        """
        pass

    # --- The Retrieval Cycle (Construction) ---

    @abstractmethod
    async def assemble_context(
        self,
        query: str,
        state: "SessionState",
        budget_limit: int,
        context_strategy: str = "standard",
    ) -> "ContextPayload":
        """
        The core 'Recall' step - selects, ranks, and compresses data.

        Supports both Passive and Active retrieval:
        - Passive: query is the user's message (broad search)
        - Active: query is agent-generated for specific lookup

        Uses the Knapsack algorithm to fit content within token budget,
        prioritizing by the defined hierarchy (immediate context > recent
        history > weak matches > deep history).

        Args:
            query: The search string (user message or agent query)
            state: Current SessionState with scoped variables
            budget_limit: Maximum tokens for dynamic content
            context_strategy: Retrieval strategy name. `minimal` may bypass
                semantic recall, while `standard` and `extended` use the full
                semantic memory pipeline.

        Returns:
            ContextPayload with history, passages, entities, facts
        """
        pass

    # --- The Formatting Cycle (Architecture) ---

    @abstractmethod
    async def format_prompt(
        self, system_prompt: str, payload: "ContextPayload"
    ) -> list[dict[str, Any]]:
        """
        Physically arranges the messages for optimal model attention.

        Structures the prompt to combat "Lost in the Middle" by placing
        critical information at start and end of context.

        Layout order:
        1. System Block (identity & guardrails)
        2. Transparency Block (recent auto-archived memories)
        3. Procedural Memory (few-shot examples)
        4. Semantic Memory (vector passages)
        5. Episodic Memory (conversation history)
        6. State Memory (scoped variables)
        7. User Trigger (the query)

        Args:
            system_prompt: The system instructions
            payload: The assembled ContextPayload

        Returns:
            List of message dicts ready for LLM API (role, content format)
        """
        pass
