"""
Transcript data models.

Defines the core data structures for conversation transcripts:
- TranscriptEntry: Single turn in a conversation (immutable once written)
- TranscriptSession: Session-level metadata and aggregates
- ToolCall/ToolResult: Tool execution tracking
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class ToolCall(BaseModel):
    """Record of a tool invocation by the assistant."""

    id: str = Field(description="Unique identifier for this tool call")
    name: str = Field(description="Name of the tool/function called")
    arguments: dict[str, Any] = Field(
        default_factory=dict, description="Arguments passed to the tool"
    )


class ToolResult(BaseModel):
    """Result of a tool execution."""

    tool_call_id: str = Field(description="ID of the corresponding ToolCall")
    output: Any = Field(default=None, description="Result data from the tool")
    error: str | None = Field(default=None, description="Error message if execution failed")


class TranscriptEntry(BaseModel):
    """
    Single turn in a transcript - immutable once written.

    Captures the complete record of a conversation turn including:
    - User and assistant messages
    - Tool calls and results
    - Timing information
    - Token usage metrics
    - Model/context information

    In multi-agent scenarios, agent_id tracks which agent generated
    the response for provenance and auditing.
    """

    # Identity
    id: str = Field(description="Unique identifier (UUID)")
    session_id: str = Field(description="Parent session identifier")
    turn_number: int = Field(description="Sequence number within session (1-indexed)")

    # Messages
    user_message: str | None = Field(
        default=None, description="User's input (None for system-initiated turns)"
    )
    assistant_message: str | None = Field(
        default=None, description="Assistant's response"
    )

    # Agent tracking (for multi-agent provenance)
    agent_id: str | None = Field(
        default=None,
        description="Which agent generated this response (e.g., 'researcher', 'coder')"
    )

    # Tool execution
    tool_calls: list[ToolCall] = Field(
        default_factory=list, description="Tools invoked by assistant"
    )
    tool_results: list[ToolResult] = Field(
        default_factory=list, description="Results from tool executions"
    )

    # Timing
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the turn started"
    )
    response_started_at: datetime | None = Field(
        default=None, description="When first token was received"
    )
    response_completed_at: datetime | None = Field(
        default=None, description="When last token was received"
    )

    # Metrics
    prompt_tokens: int | None = Field(
        default=None, description="Tokens in the prompt"
    )
    completion_tokens: int | None = Field(
        default=None, description="Tokens in the completion"
    )
    total_tokens: int | None = Field(
        default=None, description="Total tokens used"
    )
    latency_ms: float | None = Field(
        default=None, description="Total response time in milliseconds"
    )

    # Context
    model_name: str | None = Field(
        default=None, description="Which LLM model was used"
    )
    temperature: float | None = Field(
        default=None, description="Temperature setting used"
    )
    context_tokens_used: int | None = Field(
        default=None, description="How much of context window was filled"
    )

    # Extensible metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    # Processing state
    consolidated: bool = Field(
        default=False,
        description="Whether this entry has been extracted to long-term memory"
    )
    compacted: bool = Field(
        default=False,
        description=(
            "Whether this entry has been summarized by "
            "InSessionCompactor and excluded from raw history "
            "retrieval."
        ),
    )

    model_config = ConfigDict(frozen=False)

    def compute_latency(self) -> float | None:
        """Compute latency from timestamps if not explicitly set."""
        if self.latency_ms is not None:
            return self.latency_ms
        if self.timestamp and self.response_completed_at:
            delta = self.response_completed_at - self.timestamp
            return delta.total_seconds() * 1000
        return None


class TranscriptSession(BaseModel):
    """
    Session-level metadata for a conversation transcript.

    Tracks session lifecycle and aggregates for analytics.
    """

    session_id: str = Field(description="Unique session identifier")
    user_id: str | None = Field(
        default=None, description="User identifier (if known)"
    )
    started_at: datetime = Field(
        default_factory=datetime.now, description="Session start time"
    )
    ended_at: datetime | None = Field(
        default=None, description="Session end time (None if active)"
    )

    # Configuration snapshot
    model_name: str = Field(description="Primary model used for this session")
    system_prompt: str | None = Field(
        default=None, description="System prompt used"
    )
    config_snapshot: dict[str, Any] = Field(
        default_factory=dict, description="Configuration at session start"
    )

    # Aggregates (updated as entries are added)
    total_turns: int = Field(default=0, description="Number of turns in session")
    total_tokens: int = Field(default=0, description="Total tokens used")
    total_latency_ms: float = Field(
        default=0.0, description="Cumulative latency in milliseconds"
    )

    # Extensible metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional session metadata"
    )

    # Archive state
    archived: bool = Field(
        default=False,
        description="Whether this session is archived (excluded from context assembly)"
    )

    def is_active(self) -> bool:
        """Check if session is still active."""
        return self.ended_at is None


class ContextLogEntry(BaseModel):
    """
    Raw prompt and response data for context engineering analysis.

    Stores the full messages array sent to the LLM and the complete response,
    enabling deep analysis of context engineering while keeping the entries
    table clean and lean.

    Relationship:
    - Primary: sessions -> context_log (one-to-many via session_id)
    - Optional: entries -> context_log (via entry_id for joining)
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this context log entry",
    )
    session_id: str = Field(
        ...,
        description="FK to sessions.session_id (primary relationship)",
    )
    turn_number: int = Field(
        ...,
        description="Turn number for ordering within session",
    )
    entry_id: str | None = Field(
        default=None,
        description="Optional FK to entries.id for joining with transcript entries",
    )
    raw_prompt: str = Field(
        ...,
        description="JSON-serialized messages array sent to LLM",
    )
    raw_response: str | None = Field(
        default=None,
        description="JSON-serialized LLM response with metadata",
    )
    captured_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when this context was captured",
    )
