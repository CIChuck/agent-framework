"""
Common Telemetry Models.

Shared base models and enums for all telemetry types.
"""

from pydantic import BaseModel, Field


class RequestContext(BaseModel):
    """
    Common context for request/response pairing across operations.

    Enables correlating operations within a session and conversation.
    """

    request_id: str = Field(description="Unique request identifier")
    session_id: str | None = Field(
        default=None, description="User session identifier"
    )
    conversation_id: str | None = Field(
        default=None, description="Conversation thread ID"
    )
    turn_id: str | None = Field(
        default=None, description="Current turn identifier"
    )
    parent_span_id: str | None = Field(
        default=None, description="Parent trace span for nested tracing"
    )
