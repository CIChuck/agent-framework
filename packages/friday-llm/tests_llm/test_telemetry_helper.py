"""
Tests for LLM Telemetry Helper.

Tests telemetry context managers, streaming tracker, and error classification.
"""

import time
from unittest.mock import MagicMock

import litellm
import pytest
from friday_llm.exceptions import (
    CircuitBreakerOpenError,
    LLMTimeoutError,
)
from friday_llm.pricing import CostCalculator
from friday_llm.telemetry_helper import (
    CompletionTracker,
    EmbeddingTracker,
    LLMTelemetryHelper,
    OTelAttributes,
    StreamingTracker,
    classify_error,
)
from friday_llm.telemetry_models import (
    ConversationContext,
    ErrorCategory,
    TokenUsage,
)


class TestOTelAttributes:
    """Tests for OpenTelemetry attribute constants."""

    def test_standard_attributes(self):
        """Test standard GenAI attribute names."""
        assert OTelAttributes.OPERATION_NAME == "gen_ai.operation.name"
        assert OTelAttributes.PROVIDER_NAME == "gen_ai.provider.name"
        assert OTelAttributes.REQUEST_MODEL == "gen_ai.request.model"
        assert OTelAttributes.RESPONSE_MODEL == "gen_ai.response.model"
        assert OTelAttributes.INPUT_TOKENS == "gen_ai.usage.input_tokens"
        assert OTelAttributes.OUTPUT_TOKENS == "gen_ai.usage.output_tokens"
        assert OTelAttributes.CONVERSATION_ID == "gen_ai.conversation.id"

    def test_friday_extensions(self):
        """Test Friday-specific attribute names."""
        assert OTelAttributes.FRIDAY_COST_USD == "friday.cost.usd"
        assert OTelAttributes.FRIDAY_TTFT_MS == "friday.streaming.ttft_ms"
        assert OTelAttributes.FRIDAY_ERROR_CATEGORY == "friday.error.category"


class TestClassifyError:
    """Tests for error classification function."""

    def test_timeout_error(self):
        """Test timeout errors are classified correctly."""
        error = LLMTimeoutError(
            "Timeout",
            timeout_seconds=30.0,
            operation="chat",
            model="gpt-4",
        )
        assert classify_error(error) == ErrorCategory.TIMEOUT

    def test_circuit_breaker_error(self):
        """Test circuit breaker errors are classified correctly."""
        error = CircuitBreakerOpenError(
            message="Circuit open",
            model="gpt-4",
            retry_after=30.0,
        )
        assert classify_error(error) == ErrorCategory.CIRCUIT_BREAKER

    def test_rate_limit_error(self):
        """Test rate limit errors are classified correctly."""
        error = litellm.RateLimitError(
            message="Rate limit exceeded",
            llm_provider="openai",
            model="gpt-4",
        )
        assert classify_error(error) == ErrorCategory.RATE_LIMIT

    def test_auth_error(self):
        """Test authentication errors are classified correctly."""
        error = litellm.AuthenticationError(
            message="Invalid API key",
            llm_provider="openai",
            model="gpt-4",
        )
        assert classify_error(error) == ErrorCategory.AUTH_ERROR

    def test_connection_error(self):
        """Test connection errors are classified correctly."""
        error = litellm.APIConnectionError(
            message="Connection failed",
            llm_provider="openai",
            model="gpt-4",
        )
        assert classify_error(error) == ErrorCategory.NETWORK_ERROR

    def test_invalid_request_error(self):
        """Test invalid request errors are classified correctly."""
        error = litellm.BadRequestError(
            message="Invalid request",
            llm_provider="openai",
            model="gpt-4",
        )
        assert classify_error(error) == ErrorCategory.INVALID_REQUEST

    def test_unknown_error(self):
        """Test unknown errors are classified correctly."""
        error = Exception("Some random error")
        assert classify_error(error) == ErrorCategory.UNKNOWN


class TestStreamingTracker:
    """Tests for StreamingTracker."""

    def test_basic_tracking(self):
        """Test basic streaming tracking."""
        tracker = StreamingTracker()
        tracker.start()

        # Simulate receiving chunks
        time.sleep(0.01)  # Small delay for TTFT
        tracker.record_chunk(5)
        tracker.record_chunk(3)
        tracker.record_chunk(4)

        metrics = tracker.finish()

        assert metrics.chunk_count == 3
        assert metrics.time_to_first_token_ms is not None
        assert metrics.time_to_first_token_ms > 0
        assert metrics.total_stream_duration_ms > 0

    def test_ttft_not_set_without_chunks(self):
        """Test TTFT is None if no chunks recorded."""
        tracker = StreamingTracker()
        tracker.start()

        metrics = tracker.finish()

        assert metrics.chunk_count == 0
        assert metrics.time_to_first_token_ms is None

    def test_tokens_per_second(self):
        """Test tokens per second calculation."""
        tracker = StreamingTracker()
        tracker.start()

        # Record chunks with tokens
        tracker.record_chunk(10)
        time.sleep(0.05)
        tracker.record_chunk(10)

        metrics = tracker.finish()

        assert metrics.tokens_per_second is not None
        assert metrics.tokens_per_second > 0


class TestCompletionTracker:
    """Tests for CompletionTracker."""

    def test_basic_tracking(self):
        """Test basic completion tracking."""
        helper = LLMTelemetryHelper(telemetry=None, cost_calculator=None)

        tracker = CompletionTracker(
            helper=helper,
            model="gpt-4",
            context=None,
            temperature=0.7,
            max_tokens=1000,
            tool_count=0,
        )

        tracker.start()
        tracker.set_response(
            response_model="gpt-4-0613",
            usage=TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150),
            finish_reasons=["stop"],
        )
        tracker.finish()

        metrics = tracker.to_metrics()

        assert metrics.request_model == "gpt-4"
        assert metrics.response_model == "gpt-4-0613"
        assert metrics.temperature == 0.7
        assert metrics.usage.input_tokens == 100
        assert metrics.usage.output_tokens == 50
        assert metrics.finish_reasons == ["stop"]
        assert metrics.success is True

    def test_error_tracking(self):
        """Test error tracking in completion."""
        helper = LLMTelemetryHelper(telemetry=None, cost_calculator=None)

        tracker = CompletionTracker(
            helper=helper,
            model="gpt-4",
            context=None,
            temperature=0.7,
            max_tokens=None,
            tool_count=0,
        )

        tracker.start()
        error = LLMTimeoutError(
            "Timed out",
            timeout_seconds=30.0,
            operation="chat",
            model="gpt-4",
        )
        tracker.set_error(error)
        tracker.finish()

        metrics = tracker.to_metrics()

        assert metrics.success is False
        assert metrics.error_type == "LLMTimeoutError"
        assert metrics.error_category == ErrorCategory.TIMEOUT

    def test_retry_info(self):
        """Test retry information tracking."""
        helper = LLMTelemetryHelper(telemetry=None, cost_calculator=None)

        tracker = CompletionTracker(
            helper=helper,
            model="gpt-4",
            context=None,
            temperature=0.7,
            max_tokens=None,
            tool_count=0,
        )

        tracker.start()
        tracker.set_retry_info(3, 3)  # (attempt_number, total_attempts)
        tracker.finish()

        metrics = tracker.to_metrics()

        assert metrics.attempt_number == 3
        assert metrics.total_attempts == 3

    def test_with_conversation_context(self):
        """Test tracking with conversation context."""
        helper = LLMTelemetryHelper(telemetry=None, cost_calculator=None)
        context = ConversationContext(
            session_id="user-123",
            conversation_id="conv-456",
            turn_id="turn-1",
        )

        tracker = CompletionTracker(
            helper=helper,
            model="gpt-4",
            context=context,
            temperature=0.7,
            max_tokens=None,
            tool_count=0,
        )

        tracker.start()
        tracker.finish()

        metrics = tracker.to_metrics()

        assert metrics.conversation_id == "conv-456"
        assert metrics.turn_id == "turn-1"


class TestEmbeddingTracker:
    """Tests for EmbeddingTracker."""

    def test_basic_tracking(self):
        """Test basic embedding tracking."""
        helper = LLMTelemetryHelper(telemetry=None, cost_calculator=None)

        tracker = EmbeddingTracker(
            helper=helper,
            model="text-embedding-3-small",
            text_count=5,
            total_characters=500,
        )

        tracker.start()
        tracker.set_response(
            response_model="text-embedding-3-small",
            embedding_dimensions=1536,
            batch_count=2,
            usage=TokenUsage(input_tokens=100),
        )
        tracker.finish()

        metrics = tracker.to_metrics()

        assert metrics.request_model == "text-embedding-3-small"
        assert metrics.text_count == 5
        assert metrics.total_characters == 500
        assert metrics.embedding_dimensions == 1536
        assert metrics.batch_count == 2
        assert metrics.usage.input_tokens == 100
        assert metrics.success is True

    def test_retry_info(self):
        """Test retry information tracking in embeddings."""
        helper = LLMTelemetryHelper(telemetry=None, cost_calculator=None)

        tracker = EmbeddingTracker(
            helper=helper,
            model="text-embedding-3-small",
            text_count=1,
            total_characters=100,
        )

        tracker.start()
        tracker.set_retry_info(attempt_number=2, total_attempts=2)
        tracker.finish()

        assert tracker.attempt_number == 2
        assert tracker.total_attempts == 2


class TestLLMTelemetryHelper:
    """Tests for LLMTelemetryHelper."""

    def test_creation_without_telemetry(self):
        """Test creating helper without telemetry."""
        helper = LLMTelemetryHelper(
            telemetry=None,
            cost_calculator=None,
            provider_name="openai",
        )

        assert helper.telemetry is None
        assert helper.cost_calculator is None
        assert helper.provider_name == "openai"

    def test_creation_with_cost_calculator(self):
        """Test creating helper with cost calculator."""
        calculator = CostCalculator()
        helper = LLMTelemetryHelper(
            telemetry=None,
            cost_calculator=calculator,
            provider_name="openai",
        )

        assert helper.cost_calculator is calculator

    def test_track_completion_context_manager(self):
        """Test track_completion context manager."""
        helper = LLMTelemetryHelper(telemetry=None, cost_calculator=None)

        with helper.track_completion(
            model="gpt-4",
            context=None,
            temperature=0.7,
            tool_count=2,
        ) as tracker:
            tracker.set_response(
                response_model="gpt-4",
                usage=TokenUsage(input_tokens=100, output_tokens=50),
            )

        # Tracker should have finished automatically
        assert tracker._end_time > 0

    def test_track_completion_with_error(self):
        """Test track_completion handles errors correctly."""
        helper = LLMTelemetryHelper(telemetry=None, cost_calculator=None)

        with (
            pytest.raises(ValueError),
            helper.track_completion(
                model="gpt-4",
                context=None,
                temperature=0.7,
                tool_count=0,
            ) as tracker,
        ):
            raise ValueError("Test error")

        # Error should be recorded
        assert tracker.success is False
        assert tracker.error is not None

    def test_track_embedding_context_manager(self):
        """Test track_embedding context manager."""
        helper = LLMTelemetryHelper(telemetry=None, cost_calculator=None)

        with helper.track_embedding(
            model="text-embedding-3-small",
            text_count=5,
            total_characters=500,
        ) as tracker:
            tracker.set_response(
                response_model="text-embedding-3-small",
                embedding_dimensions=1536,
            )

        # Tracker should have finished automatically
        assert tracker._end_time > 0

    def test_create_streaming_tracker(self):
        """Test creating streaming tracker."""
        helper = LLMTelemetryHelper(telemetry=None, cost_calculator=None)

        tracker = helper.create_streaming_tracker()

        assert isinstance(tracker, StreamingTracker)

    def test_with_mock_telemetry(self):
        """Test helper with mock telemetry interface."""
        mock_telemetry = MagicMock()
        mock_telemetry.start_span.return_value = "span-123"

        helper = LLMTelemetryHelper(
            telemetry=mock_telemetry,
            cost_calculator=None,
            provider_name="openai",
        )

        with helper.track_completion(
            model="gpt-4",
            context=None,
            temperature=0.7,
            tool_count=0,
        ):
            pass

        # Telemetry methods should have been called
        mock_telemetry.start_span.assert_called_once()
        mock_telemetry.end_span.assert_called_once()
        mock_telemetry.capture_event.assert_called()

    def test_cost_calculation(self):
        """Test cost is calculated in metrics."""
        calculator = CostCalculator()
        helper = LLMTelemetryHelper(
            telemetry=None,
            cost_calculator=calculator,
            provider_name="openai",
        )

        with helper.track_completion(
            model="gpt-4",
            context=None,
            temperature=0.7,
            tool_count=0,
        ) as tracker:
            tracker.set_response(
                response_model="gpt-4",
                usage=TokenUsage(
                    input_tokens=1000, output_tokens=500, total_tokens=1500
                ),
            )

        metrics = tracker.to_metrics()

        assert metrics.cost is not None
        assert metrics.cost.total_cost > 0

    def test_otel_attributes_in_event(self):
        """Test OTel attributes are included in telemetry events."""
        mock_telemetry = MagicMock()
        mock_telemetry.start_span.return_value = "span-123"

        helper = LLMTelemetryHelper(
            telemetry=mock_telemetry,
            cost_calculator=None,
            provider_name="openai",
        )

        with helper.track_completion(
            model="gpt-4",
            context=None,
            temperature=0.7,
            tool_count=0,
        ) as tracker:
            tracker.set_response(
                response_model="gpt-4-0613",
                usage=TokenUsage(input_tokens=100, output_tokens=50),
            )

        # Check that capture_event was called with correct attributes
        call_args = mock_telemetry.capture_event.call_args
        event_name = call_args[0][0]
        event_data = call_args[0][1]

        assert event_name == "llm_completion_success"
        assert OTelAttributes.REQUEST_MODEL in event_data
        assert OTelAttributes.RESPONSE_MODEL in event_data
        assert OTelAttributes.PROVIDER_NAME in event_data
