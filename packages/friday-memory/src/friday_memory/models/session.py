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
    """Represents the result of a tool call."""

    tool_call_id: str = Field(..., description="ID of the corresponding tool call")
    output: Any = Field(..., description="Result returned by the tool")
    error: str | None = Field(default=None, description="Error message if tool failed")


class InteractionTurn(BaseModel):
    """
    Represents a single turn in a conversation.

    Captures the full interaction including user input, assistant response,
    and any tool calls made during the turn.
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
        description="Additional turn metadata (tokens used, latency, etc.)",
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    consolidated: bool = Field(
        default=False,
        description="Whether this turn has been processed by MemoryConsolidator",
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
