"""
Session State Models.
Defines SessionState, InteractionTurn, and ConsolidationReport.

Ref: Batch 2a Specification, Section 1.2
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Represents a tool/function call made by the assistant."""

    id: str = Field(..., description="Unique identifier for this tool call")
    name: str = Field(..., description="Name of the tool/function called")
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments passed to the tool",
    )


class ToolResult(BaseModel):
    """
    Represents the result of a tool call with lifecycle tracking.

    Lifecycle fields enable reference-based decay: large tool outputs
    are tracked and automatically summarized when they become stale
    (not referenced for N turns).

    Ref: docs/build-plan/to-do/tool-content-lifecycle-build-plan.md
    """

    tool_call_id: str = Field(..., description="ID of the corresponding tool call")
    output: Any = Field(..., description="Result returned by the tool")
    error: str | None = Field(default=None, description="Error message if tool failed")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for tool results (e.g., security flags)",
    )

    # Lifecycle Metadata
    turn_id: str | None = Field(
        default=None,
        description="Turn where this tool was executed",
    )
    last_referenced_turn_id: str | None = Field(
        default=None,
        description="Last turn that referenced this output",
    )
    referencing_turns: list[str] = Field(
        default_factory=list,
        description="Audit trail of turns that referenced this output",
    )

    # Decay State
    is_decayed: bool = Field(
        default=False,
        description="Whether content has been summarized due to staleness",
    )
    summary: str | None = Field(
        default=None,
        description="Summary of output if decayed (replaces full content in context)",
    )
    original_token_count: int | None = Field(
        default=None,
        description="Original size in tokens before decay",
    )


class InteractionTurn(BaseModel):
    """
    Represents a single turn in a conversation.

    Captures the full interaction including user input, assistant response,
    and any tool calls made during the turn.

    In multi-agent scenarios, agent_id tracks which agent generated
    the response for provenance and auditing.
    """

    id: str = Field(..., description="Unique turn identifier")
    session_id: str = Field(..., description="Parent session identifier")
    user_message: str | None = Field(
        default=None,
        description="User's input message (None for system-initiated turns)",
    )
    assistant_message: str | None = Field(
        default=None,
        description="Assistant's response message",
    )

    # Agent tracking (for multi-agent provenance)
    agent_id: str | None = Field(
        default=None,
        description="Which agent generated this response (e.g., 'researcher', 'coder')",
    )

    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="Tools called by the assistant during this turn",
    )
    tool_results: list[ToolResult] = Field(
        default_factory=list,
        description="Results from tool executions",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional turn metadata",
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    consolidated: bool = Field(
        default=False,
        description="Whether this turn has been processed by MemoryConsolidator",
    )
    compacted: bool = Field(
        default=False,
        description=(
            "Whether this turn has been summarized by "
            "InSessionCompactor and excluded from raw history "
            "retrieval. Distinct from 'consolidated' which "
            "tracks extraction status."
        ),
    )

    # Timing metrics
    response_started_at: datetime | None = Field(
        default=None,
        description="When first token was received from LLM",
    )
    response_completed_at: datetime | None = Field(
        default=None,
        description="When last token was received from LLM",
    )

    # Token usage metrics
    prompt_tokens: int | None = Field(
        default=None,
        description="Number of tokens in the prompt",
    )
    completion_tokens: int | None = Field(
        default=None,
        description="Number of tokens in the completion",
    )
    total_tokens: int | None = Field(
        default=None,
        description="Total tokens used (prompt + completion)",
    )
    latency_ms: float | None = Field(
        default=None,
        description="Total response time in milliseconds",
    )

    # Model configuration
    model_name: str | None = Field(
        default=None,
        description="Which LLM model was used",
    )
    temperature: float | None = Field(
        default=None,
        description="Temperature setting used for generation",
    )
    context_tokens_used: int | None = Field(
        default=None,
        description="How much of the context window was filled",
    )

    # Raw prompt/response for context engineering analysis
    raw_prompt: str | None = Field(
        default=None,
        description="JSON-serialized messages array sent to LLM",
    )
    raw_response: str | None = Field(
        default=None,
        description="JSON-serialized raw LLM response with metadata",
    )


class SessionState(BaseModel):
    """
    Tracks the continuity of an interaction thread.

    Manages session metadata and scoped variables that persist across turns.
    Variables use prefixes to control scope and persistence:
    - 'user:' - Persists across sessions for this user
    - 'app:' - Global app configuration
    - 'session:' - Ephemeral, clears on session reset
    """

    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    turn_count: int = Field(default=0, ge=0)
    start_time: datetime = Field(default_factory=datetime.now)
    active_goals: list[str] = Field(
        default_factory=list,
        description="High-level intent stack (e.g., ['Debug App', 'Check Logs'])",
    )
    scoped_vars: dict[str, Any] = Field(
        default_factory=dict,
        description="Scoped variable store with prefix-based access control",
    )

    # Valid prefixes for scoped variables
    VALID_PREFIXES: tuple[str, ...] = ("user:", "app:", "session:")

    def get_var(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a scoped variable.

        Args:
            key: Variable key (should include prefix)
            default: Value to return if key not found

        Returns:
            The variable value or default
        """
        return self.scoped_vars.get(key, default)

    def set_var(self, key: str, value: Any) -> None:
        """
        Set a scoped variable.

        Args:
            key: Variable key (must start with valid prefix)
            value: Value to store

        Raises:
            ValueError: If key doesn't start with a valid prefix
        """
        if not any(key.startswith(p) for p in self.VALID_PREFIXES):
            raise ValueError(
                f"Keys must start with one of: {', '.join(self.VALID_PREFIXES)}"
            )
        self.scoped_vars[key] = value

    def delete_var(self, key: str) -> bool:
        """
        Delete a scoped variable.

        Args:
            key: Variable key to delete

        Returns:
            True if key existed and was deleted, False otherwise
        """
        if key in self.scoped_vars:
            del self.scoped_vars[key]
            return True
        return False

    def clear_session_vars(self) -> int:
        """
        Clear all session-scoped variables.

        Returns:
            Number of variables cleared
        """
        session_keys = [k for k in self.scoped_vars if k.startswith("session:")]
        for key in session_keys:
            del self.scoped_vars[key]
        return len(session_keys)

    def increment_turn(self) -> int:
        """Increment turn count and return new value."""
        self.turn_count += 1
        return self.turn_count


class ConsolidationReport(BaseModel):
    """
    Telemetry returned by the consolidation cycle.

    Provides metrics on what the MemoryConsolidator accomplished.
    """

    session_id: str = Field(..., description="Session that was consolidated")
    turns_processed: int = Field(
        default=0,
        ge=0,
        description="Number of turns analyzed",
    )
    nodes_created: int = Field(
        default=0,
        ge=0,
        description="New graph nodes created from extracted facts",
    )
    nodes_merged: int = Field(
        default=0,
        ge=0,
        description="Duplicate nodes merged via entity resolution",
    )
    edges_created: int = Field(
        default=0,
        ge=0,
        description="New relationships discovered",
    )
    conflicts_resolved: int = Field(
        default=0,
        ge=0,
        description="Conflicting facts reconciled",
    )
    tokens_condensed: int = Field(
        default=0,
        ge=0,
        description="Estimated token savings from summarization",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Any errors encountered during consolidation",
    )
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Time taken for consolidation in milliseconds",
    )
