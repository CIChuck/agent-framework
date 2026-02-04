"""
Tests for LLM Telemetry Models.

Tests Pydantic model validation and data conversion.
"""

import pytest
from datetime import datetime

from friday_llm.telemetry_models import (
    TokenUsage,
    CostEstimate,
    StreamingMetrics,
    ConversationContext,
    LLMCallMetrics,
    EmbeddingMetrics,
    GenAIOperationType,
    ErrorCategory,
)


class TestTokenUsage:
    """Tests for TokenUsage model."""

    def test_default_values(self):
        """Test default token counts are zero."""
        usage = TokenUsage()
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0
        assert usage.total_tokens == 0

    def test_custom_values(self):
        """Test setting custom token counts."""
        usage = TokenUsage(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        )
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.total_tokens == 150

    def test_from_response_with_dict(self):
        """Test creating from response dict."""
        response_dict = {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }
        usage = TokenUsage.from_response(response_dict)
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.total_tokens == 150

    def test_from_response_with_none(self):
        """Test creating from None returns default."""
        usage = TokenUsage.from_response(None)
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0
        assert usage.total_tokens == 0

    def test_from_response_with_empty_dict(self):
        """Test creating from empty dict returns defaults."""
        usage = TokenUsage.from_response({})
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0

    def test_negative_values_rejected(self):
        """Test that negative values are rejected."""
        with pytest.raises(ValueError):
            TokenUsage(input_tokens=-1)


class TestCostEstimate:
    """Tests for CostEstimate model."""

    def test_default_values(self):
        """Test default costs are zero."""
        cost = CostEstimate()
        assert cost.input_cost == 0.0
        assert cost.output_cost == 0.0
        assert cost.total_cost == 0.0
        assert cost.currency == "USD"
        assert cost.pricing_model is None

    def test_custom_values(self):
        """Test setting custom costs."""
        cost = CostEstimate(
            input_cost=0.001,
            output_cost=0.002,
            total_cost=0.003,
            currency="EUR",
            pricing_model="gpt-4",
        )
        assert cost.input_cost == 0.001
        assert cost.output_cost == 0.002
        assert cost.total_cost == 0.003
        assert cost.currency == "EUR"
        assert cost.pricing_model == "gpt-4"

    def test_negative_costs_rejected(self):
        """Test that negative costs are rejected."""
        with pytest.raises(ValueError):
            CostEstimate(input_cost=-0.001)


class TestStreamingMetrics:
    """Tests for StreamingMetrics model."""

    def test_default_values(self):
        """Test default streaming values."""
        metrics = StreamingMetrics()
        assert metrics.time_to_first_token_ms is None
        assert metrics.chunk_count == 0
        assert metrics.tokens_per_second is None
        assert metrics.inter_token_latency_ms is None
        assert metrics.total_stream_duration_ms == 0.0

    def test_custom_values(self):
        """Test setting streaming metrics."""
        metrics = StreamingMetrics(
            time_to_first_token_ms=150.5,
            chunk_count=10,
            tokens_per_second=25.0,
            inter_token_latency_ms=40.0,
            total_stream_duration_ms=500.0,
        )
        assert metrics.time_to_first_token_ms == 150.5
        assert metrics.chunk_count == 10
        assert metrics.tokens_per_second == 25.0
        assert metrics.inter_token_latency_ms == 40.0
        assert metrics.total_stream_duration_ms == 500.0


class TestConversationContext:
    """Tests for ConversationContext model."""

    def test_required_session_id(self):
        """Test session_id is required."""
        context = ConversationContext(session_id="user-123")
        assert context.session_id == "user-123"
        assert context.conversation_id is None
        assert context.turn_id is None
        assert context.turn_number == 0
        assert context.parent_span_id is None
        assert context.message_count == 0

    def test_full_context(self):
        """Test full conversation context."""
        context = ConversationContext(
            session_id="user-123",
            conversation_id="conv-456",
            turn_id="turn-1",
            turn_number=3,
            parent_span_id="span-789",
            message_count=5,
        )
        assert context.session_id == "user-123"
        assert context.conversation_id == "conv-456"
        assert context.turn_id == "turn-1"
        assert context.turn_number == 3
        assert context.parent_span_id == "span-789"
        assert context.message_count == 5


class TestLLMCallMetrics:
    """Tests for LLMCallMetrics model."""

    def test_minimal_creation(self):
        """Test creating with minimal required fields."""
        metrics = LLMCallMetrics(
            request_id="req-123",
            request_model="gpt-4",
        )
        assert metrics.request_id == "req-123"
        assert metrics.request_model == "gpt-4"
        assert metrics.operation_name == GenAIOperationType.CHAT
        assert metrics.provider_name == "litellm"
        assert metrics.success is True
        assert metrics.attempt_number == 1
        assert metrics.total_attempts == 1

    def test_full_creation(self):
        """Test creating with all fields."""
        metrics = LLMCallMetrics(
            request_id="req-123",
            conversation_id="conv-456",
            turn_id="turn-1",
            operation_name=GenAIOperationType.CHAT,
            provider_name="openai",
            request_model="gpt-4",
            response_model="gpt-4-0613",
            temperature=0.7,
            max_tokens=1000,
            tool_count=3,
            duration_ms=500.0,
            usage=TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150),
            cost=CostEstimate(total_cost=0.01),
            success=True,
            finish_reasons=["stop"],
            tool_calls_count=2,
        )
        assert metrics.request_id == "req-123"
        assert metrics.conversation_id == "conv-456"
        assert metrics.provider_name == "openai"
        assert metrics.tool_count == 3
        assert metrics.duration_ms == 500.0
        assert metrics.usage.input_tokens == 100
        assert metrics.finish_reasons == ["stop"]

    def test_error_tracking(self):
        """Test error tracking fields."""
        metrics = LLMCallMetrics(
            request_id="req-123",
            request_model="gpt-4",
            success=False,
            error_type="APIError",
            error_category=ErrorCategory.RATE_LIMIT,
            error_message="Rate limit exceeded",
        )
        assert metrics.success is False
        assert metrics.error_type == "APIError"
        assert metrics.error_category == ErrorCategory.RATE_LIMIT
        assert metrics.error_message == "Rate limit exceeded"


class TestEmbeddingMetrics:
    """Tests for EmbeddingMetrics model."""

    def test_minimal_creation(self):
        """Test creating with minimal required fields."""
        metrics = EmbeddingMetrics(
            request_id="req-123",
            request_model="text-embedding-3-small",
        )
        assert metrics.request_id == "req-123"
        assert metrics.request_model == "text-embedding-3-small"
        assert metrics.operation_name == GenAIOperationType.EMBEDDINGS
        assert metrics.text_count == 0
        assert metrics.batch_count == 1

    def test_full_creation(self):
        """Test creating with all fields."""
        metrics = EmbeddingMetrics(
            request_id="req-123",
            request_model="text-embedding-3-small",
            response_model="text-embedding-3-small",
            duration_ms=100.0,
            text_count=5,
            total_characters=500,
            embedding_dimensions=1536,
            batch_count=2,
            usage=TokenUsage(input_tokens=100),
            cost=CostEstimate(total_cost=0.001),
            success=True,
        )
        assert metrics.text_count == 5
        assert metrics.total_characters == 500
        assert metrics.embedding_dimensions == 1536
        assert metrics.batch_count == 2


class TestEnums:
    """Tests for enum values."""

    def test_operation_types(self):
        """Test GenAIOperationType values."""
        assert GenAIOperationType.CHAT.value == "chat"
        assert GenAIOperationType.TEXT_COMPLETION.value == "text_completion"
        assert GenAIOperationType.EMBEDDINGS.value == "embeddings"

    def test_error_categories(self):
        """Test ErrorCategory values."""
        assert ErrorCategory.TIMEOUT.value == "timeout"
        assert ErrorCategory.RATE_LIMIT.value == "rate_limit"
        assert ErrorCategory.AUTH_ERROR.value == "auth_error"
        assert ErrorCategory.NETWORK_ERROR.value == "network_error"
        assert ErrorCategory.CIRCUIT_BREAKER.value == "circuit_breaker"
