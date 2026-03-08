"""
Telemetry Data Models for LLM Operations.

Provides Pydantic models for structured LLM telemetry following
OpenTelemetry GenAI semantic conventions.

Ref: https://opentelemetry.io/docs/specs/semconv/gen-ai/
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class GenAIOperationType(str, Enum):
    """OpenTelemetry GenAI operation types."""

    CHAT = "chat"
    TEXT_COMPLETION = "text_completion"
    EMBEDDINGS = "embeddings"


class ErrorCategory(str, Enum):
    """Classification of LLM errors for analysis."""

    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    AUTH_ERROR = "auth_error"
    INVALID_REQUEST = "invalid_request"
    MODEL_ERROR = "model_error"
    NETWORK_ERROR = "network_error"
    CIRCUIT_BREAKER = "circuit_breaker"
    UNKNOWN = "unknown"


class TokenUsage(BaseModel):
    """Token usage breakdown for an LLM call."""

    input_tokens: int = Field(default=0, ge=0, description="Prompt/input tokens")
    output_tokens: int = Field(default=0, ge=0, description="Completion/output tokens")
    total_tokens: int = Field(default=0, ge=0, description="Total tokens used")

    @classmethod
    def from_response(cls, usage_dict: dict[str, Any] | None) -> TokenUsage:
        """Create from LiteLLM usage dict."""
        if not usage_dict:
            return cls()
        return cls(
            input_tokens=usage_dict.get("prompt_tokens", 0),
            output_tokens=usage_dict.get("completion_tokens", 0),
            total_tokens=usage_dict.get("total_tokens", 0),
        )


class CostEstimate(BaseModel):
    """Cost estimation for an LLM call."""

    input_cost: float = Field(
        default=0.0, ge=0.0, description="Cost for input tokens (USD)"
    )
    output_cost: float = Field(
        default=0.0, ge=0.0, description="Cost for output tokens (USD)"
    )
    total_cost: float = Field(default=0.0, ge=0.0, description="Total cost (USD)")
    currency: str = Field(default="USD", description="Currency code")
    pricing_model: str | None = Field(
        default=None, description="Model pricing tier used"
    )


class StreamingMetrics(BaseModel):
    """Metrics specific to streaming responses."""

    time_to_first_token_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Time from request start to first token (ms)",
    )
    chunk_count: int = Field(default=0, ge=0, description="Number of chunks received")
    tokens_per_second: float | None = Field(
        default=None,
        ge=0.0,
        description="Average output tokens per second",
    )
    inter_token_latency_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Average time between tokens (ms)",
    )
    total_stream_duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total streaming duration (ms)",
    )


class ConversationContext(BaseModel):
    """
    Context for request/response pairing within a conversation.

    Enables correlating LLM calls with conversation turns and sessions.

    Example:
        context = ConversationContext(
            session_id="user-123",
            conversation_id="conv-456",
            turn_id="turn-1",
        )
        response = await service.chat_completion(
            messages=[...],
            conversation_context=context,
        )
    """

    session_id: str = Field(description="User session identifier")
    conversation_id: str | None = Field(
        default=None,
        description="Conversation thread ID (gen_ai.conversation.id)",
    )
    turn_id: str | None = Field(default=None, description="Current turn identifier")
    turn_number: int = Field(default=0, ge=0, description="Turn sequence number")
    parent_span_id: str | None = Field(default=None, description="Parent trace span")
    message_count: int = Field(default=0, ge=0, description="Messages in context")
    workflow_id: str | None = Field(
        default=None,
        description="Workflow identifier for execution attribution",
    )
    execution_id: str | None = Field(
        default=None,
        description="Workflow execution identifier for attribution",
    )
    pipeline_id: str | None = Field(
        default=None,
        description="Pipeline identifier for execution attribution",
    )
    task_id: str | None = Field(
        default=None,
        description="Task identifier for execution attribution",
    )
    assignment_id: str | None = Field(
        default=None,
        description="Assignment identifier for execution attribution",
    )
    agent_id: str | None = Field(
        default=None,
        description="Assigned agent identifier for attribution",
    )
    llm_service: str | None = Field(
        default=None,
        description="Resolved runtime LLM service name for the operation",
    )


class LLMCallMetrics(BaseModel):
    """
    Comprehensive metrics for a single LLM call.

    Captures latency, tokens, cost, model info, and error classification.
    Follows OpenTelemetry GenAI semantic conventions where applicable.
    """

    # Identity & Context
    request_id: str = Field(description="Unique request identifier")
    conversation_id: str | None = Field(
        default=None,
        description="Conversation/session context (gen_ai.conversation.id)",
    )
    turn_id: str | None = Field(default=None, description="Turn within conversation")
    workflow_id: str | None = Field(
        default=None,
        description="Workflow identifier for execution attribution",
    )
    execution_id: str | None = Field(
        default=None,
        description="Workflow execution identifier for attribution",
    )
    pipeline_id: str | None = Field(
        default=None,
        description="Pipeline identifier for execution attribution",
    )
    task_id: str | None = Field(
        default=None,
        description="Task identifier for execution attribution",
    )
    assignment_id: str | None = Field(
        default=None,
        description="Assignment identifier for execution attribution",
    )
    agent_id: str | None = Field(
        default=None,
        description="Assigned agent identifier for attribution",
    )
    llm_service: str | None = Field(
        default=None,
        description="Resolved runtime LLM service name for the request",
    )

    # Operation Info (OpenTelemetry attributes)
    operation_name: GenAIOperationType = Field(
        default=GenAIOperationType.CHAT,
        description="Type of operation (gen_ai.operation.name)",
    )
    provider_name: str = Field(
        default="litellm",
        description="Provider identifier (gen_ai.provider.name)",
    )

    # Model Info
    request_model: str = Field(description="Requested model (gen_ai.request.model)")
    response_model: str | None = Field(
        default=None,
        description="Actual model used (gen_ai.response.model)",
    )

    # Request Parameters
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)
    tool_count: int = Field(default=0, ge=0, description="Number of tools provided")

    # Timing
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: datetime | None = Field(default=None)
    duration_ms: float = Field(
        default=0.0, ge=0.0, description="Total operation duration (ms)"
    )

    # Usage & Cost
    usage: TokenUsage = Field(default_factory=TokenUsage)
    cost: CostEstimate | None = Field(default=None)

    # Streaming (optional)
    streaming: StreamingMetrics | None = Field(default=None)

    # Response Info
    response_id: str | None = Field(
        default=None,
        description="Provider's response ID (gen_ai.response.id)",
    )
    finish_reasons: list[str] = Field(
        default_factory=list,
        description="Completion finish reasons (gen_ai.response.finish_reasons)",
    )
    tool_calls_count: int = Field(
        default=0, ge=0, description="Number of tool calls returned"
    )

    # Error Tracking
    success: bool = Field(default=True)
    error_type: str | None = Field(default=None, description="Error type (error.type)")
    error_category: ErrorCategory | None = Field(default=None)
    error_message: str | None = Field(default=None)

    # Retry/Resilience Info
    attempt_number: int = Field(default=1, ge=1, description="Attempt number (1-based)")
    total_attempts: int = Field(default=1, ge=1, description="Total attempts made")
    retry_delay_total_ms: float = Field(
        default=0.0, ge=0.0, description="Total retry delay"
    )


class EmbeddingMetrics(BaseModel):
    """Metrics for embedding operations."""

    request_id: str = Field(description="Unique request identifier")
    operation_name: GenAIOperationType = Field(default=GenAIOperationType.EMBEDDINGS)
    provider_name: str = Field(default="litellm")
    request_model: str = Field(description="Embedding model name")
    response_model: str | None = Field(default=None)
    workflow_id: str | None = Field(
        default=None,
        description="Workflow identifier for execution attribution",
    )
    execution_id: str | None = Field(
        default=None,
        description="Workflow execution identifier for attribution",
    )
    pipeline_id: str | None = Field(
        default=None,
        description="Pipeline identifier for execution attribution",
    )
    task_id: str | None = Field(
        default=None,
        description="Task identifier for execution attribution",
    )
    assignment_id: str | None = Field(
        default=None,
        description="Assignment identifier for execution attribution",
    )
    agent_id: str | None = Field(
        default=None,
        description="Assigned agent identifier for attribution",
    )
    llm_service: str | None = Field(
        default=None,
        description="Resolved runtime LLM service name for the embedding call",
    )

    # Timing
    start_time: datetime = Field(default_factory=datetime.now)
    duration_ms: float = Field(default=0.0, ge=0.0)

    # Embedding-specific
    text_count: int = Field(default=0, ge=0, description="Number of texts embedded")
    total_characters: int = Field(default=0, ge=0, description="Total input characters")
    embedding_dimensions: int | None = Field(
        default=None,
        description="Embedding vector dimension (gen_ai.embeddings.dimension.count)",
    )
    batch_count: int = Field(default=1, ge=1, description="Number of batches processed")

    # Usage & Cost
    usage: TokenUsage = Field(default_factory=TokenUsage)
    cost: CostEstimate | None = Field(default=None)

    # Error Tracking
    success: bool = Field(default=True)
    error_type: str | None = Field(default=None)
    error_category: ErrorCategory | None = Field(default=None)
    error_message: str | None = Field(default=None)
