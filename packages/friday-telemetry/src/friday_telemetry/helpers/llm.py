"""
LLM Telemetry Helper.

Provides a reusable helper class for capturing LLM telemetry
with consistent OpenTelemetry attribute naming.

Ref: https://opentelemetry.io/docs/specs/semconv/gen-ai/
"""

from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generator, Protocol

from friday_telemetry.attributes import OTelAttributes
from friday_telemetry.models.llm import (
    ConversationContext,
    CostEstimate,
    EmbeddingMetrics,
    ErrorCategory,
    GenAIOperationType,
    LLMCallMetrics,
    StreamingMetrics,
    TokenUsage,
)

if TYPE_CHECKING:
    from friday_telemetry.interface import TelemetryInterface


class CostCalculatorProtocol(Protocol):
    """Protocol for cost calculators to avoid circular imports."""

    def calculate(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> CostEstimate:
        """Calculate cost for the given model and token counts."""
        ...


def classify_error(error: Exception) -> ErrorCategory:
    """
    Classify an exception into an error category.

    Args:
        error: The exception to classify

    Returns:
        ErrorCategory enum value
    """
    error_type = type(error).__name__.lower()
    error_msg = str(error).lower()

    # Check for specific error types by class name
    if "timeout" in error_type:
        return ErrorCategory.TIMEOUT
    if "circuitbreaker" in error_type:
        return ErrorCategory.CIRCUIT_BREAKER
    if "retryexhausted" in error_type:
        # Check for underlying error if available
        if hasattr(error, "last_error") and error.last_error:
            return classify_error(error.last_error)
        return ErrorCategory.UNKNOWN

    # Check error message content
    if "rate" in error_msg and "limit" in error_msg:
        return ErrorCategory.RATE_LIMIT
    if "ratelimit" in error_type:
        return ErrorCategory.RATE_LIMIT
    if "auth" in error_msg or "key" in error_msg or "unauthorized" in error_msg:
        return ErrorCategory.AUTH_ERROR
    if "authentication" in error_type:
        return ErrorCategory.AUTH_ERROR
    if "invalid" in error_msg or "validation" in error_msg:
        return ErrorCategory.INVALID_REQUEST
    if "connection" in error_msg or "network" in error_msg:
        return ErrorCategory.NETWORK_ERROR
    if "apiconnection" in error_type:
        return ErrorCategory.NETWORK_ERROR
    if "model" in error_msg and "not found" in error_msg:
        return ErrorCategory.MODEL_ERROR
    if "timeout" in error_msg or "timed out" in error_msg:
        return ErrorCategory.TIMEOUT

    return ErrorCategory.UNKNOWN


class StreamingTracker:
    """
    Tracks streaming metrics including time-to-first-token (TTFT).

    Example:
        tracker = StreamingTracker()
        tracker.start()

        async for chunk in stream:
            tracker.record_chunk()
            yield chunk

        metrics = tracker.finish()
        print(f"TTFT: {metrics.time_to_first_token_ms}ms")
    """

    def __init__(self) -> None:
        self._start_time: float | None = None
        self._first_token_time: float | None = None
        self._last_chunk_time: float | None = None
        self._chunk_count = 0
        self._total_tokens = 0
        self._inter_token_times: list[float] = []

    def start(self) -> None:
        """Mark the start of streaming."""
        self._start_time = time.perf_counter()

    def record_chunk(self, token_count: int = 1) -> None:
        """
        Record a received chunk.

        Args:
            token_count: Approximate number of tokens in this chunk
        """
        now = time.perf_counter()

        if self._first_token_time is None:
            self._first_token_time = now
        elif self._last_chunk_time is not None:
            self._inter_token_times.append(now - self._last_chunk_time)

        self._last_chunk_time = now
        self._chunk_count += 1
        self._total_tokens += token_count

    def finish(self) -> StreamingMetrics:
        """
        Finalize and return streaming metrics.

        Returns:
            StreamingMetrics with TTFT, chunk count, and throughput
        """
        end_time = time.perf_counter()

        ttft = None
        if self._start_time and self._first_token_time:
            ttft = (self._first_token_time - self._start_time) * 1000

        total_duration = 0.0
        if self._start_time:
            total_duration = (end_time - self._start_time) * 1000

        tokens_per_sec = None
        if total_duration > 0 and self._total_tokens > 0:
            tokens_per_sec = self._total_tokens / (total_duration / 1000)

        avg_inter_token = None
        if self._inter_token_times:
            avg_inter_token = (
                sum(self._inter_token_times) / len(self._inter_token_times)
            ) * 1000

        return StreamingMetrics(
            time_to_first_token_ms=ttft,
            chunk_count=self._chunk_count,
            tokens_per_second=tokens_per_sec,
            inter_token_latency_ms=avg_inter_token,
            total_stream_duration_ms=total_duration,
        )


class CompletionTracker:
    """Tracks a single chat completion request."""

    def __init__(
        self,
        helper: LLMTelemetryHelper,
        model: str,
        context: ConversationContext | None,
        temperature: float | None,
        max_tokens: int | None,
        tool_count: int,
    ) -> None:
        self.helper = helper
        self.model = model
        self.context = context
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tool_count = tool_count

        self.request_id = str(uuid.uuid4())
        self.span_id: str | None = None
        self._start_time: float = 0
        self._end_time: float = 0

        # Response data
        self.response_model: str | None = None
        self.response_id: str | None = None
        self.usage: TokenUsage = TokenUsage()
        self.finish_reasons: list[str] = []
        self.tool_calls_count = 0

        # Streaming
        self.streaming_metrics: StreamingMetrics | None = None

        # Retry info
        self.attempt_number = 1
        self.total_attempts = 1

        # Error info
        self.success = True
        self.error: Exception | None = None

    def start(self) -> None:
        """Start tracking."""
        self._start_time = time.perf_counter()
        if self.helper.telemetry:
            span_name = f"chat {self.model}"
            parent_id = self.context.parent_span_id if self.context else None
            self.span_id = self.helper.telemetry.start_span(span_name, parent_id)

    def set_response(
        self,
        response_model: str | None = None,
        response_id: str | None = None,
        usage: TokenUsage | None = None,
        finish_reasons: list[str] | None = None,
        tool_calls_count: int = 0,
    ) -> None:
        """
        Record response details.

        Args:
            response_model: Actual model used
            response_id: Provider's response ID
            usage: Token usage from response
            finish_reasons: Completion finish reasons
            tool_calls_count: Number of tool calls returned
        """
        self.response_model = response_model
        self.response_id = response_id
        if usage:
            self.usage = usage
        if finish_reasons:
            self.finish_reasons = finish_reasons
        self.tool_calls_count = tool_calls_count

    def set_streaming_metrics(self, metrics: StreamingMetrics) -> None:
        """Set streaming metrics from StreamingTracker."""
        self.streaming_metrics = metrics

    def set_retry_info(self, attempt: int, total: int) -> None:
        """
        Record retry information.

        Args:
            attempt: Current attempt number (1-based)
            total: Total attempts made
        """
        self.attempt_number = attempt
        self.total_attempts = total

    def set_error(self, error: Exception) -> None:
        """Record an error."""
        self.success = False
        self.error = error

    def finish(self) -> None:
        """Finish tracking and close span."""
        self._end_time = time.perf_counter()
        if self.span_id and self.helper.telemetry:
            self.helper.telemetry.end_span(self.span_id, {"success": str(self.success)})

    def to_metrics(self) -> LLMCallMetrics:
        """Convert to LLMCallMetrics."""
        duration_ms = (self._end_time - self._start_time) * 1000

        cost: CostEstimate | None = None
        if self.helper.cost_calculator:
            cost = self.helper.cost_calculator.calculate(
                model=self.response_model or self.model,
                input_tokens=self.usage.input_tokens,
                output_tokens=self.usage.output_tokens,
            )

        error_type = None
        error_category = None
        error_message = None
        if self.error:
            error_type = type(self.error).__name__
            error_category = classify_error(self.error)
            error_message = str(self.error)[:500]  # Truncate long messages

        return LLMCallMetrics(
            request_id=self.request_id,
            conversation_id=self.context.conversation_id if self.context else None,
            turn_id=self.context.turn_id if self.context else None,
            operation_name=GenAIOperationType.CHAT,
            provider_name=self.helper.provider_name,
            request_model=self.model,
            response_model=self.response_model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            tool_count=self.tool_count,
            start_time=datetime.now(),
            duration_ms=duration_ms,
            usage=self.usage,
            cost=cost,
            streaming=self.streaming_metrics,
            response_id=self.response_id,
            finish_reasons=self.finish_reasons,
            tool_calls_count=self.tool_calls_count,
            success=self.success,
            error_type=error_type,
            error_category=error_category,
            error_message=error_message,
            attempt_number=self.attempt_number,
            total_attempts=self.total_attempts,
        )


class EmbeddingTracker:
    """Tracks a single embedding operation."""

    def __init__(
        self,
        helper: LLMTelemetryHelper,
        model: str,
        text_count: int,
        total_characters: int,
    ) -> None:
        self.helper = helper
        self.model = model
        self.text_count = text_count
        self.total_characters = total_characters

        self.request_id = str(uuid.uuid4())
        self.span_id: str | None = None
        self._start_time: float = 0
        self._end_time: float = 0

        # Response data
        self.response_model: str | None = None
        self.embedding_dimensions: int | None = None
        self.batch_count = 1
        self.usage: TokenUsage = TokenUsage()

        # Retry info
        self.attempt_number = 1
        self.total_attempts = 1

        # Error info
        self.success = True
        self.error: Exception | None = None

    def start(self) -> None:
        """Start tracking."""
        self._start_time = time.perf_counter()
        if self.helper.telemetry:
            self.span_id = self.helper.telemetry.start_span(f"embeddings {self.model}")

    def set_response(
        self,
        response_model: str | None = None,
        embedding_dimensions: int | None = None,
        batch_count: int = 1,
        usage: TokenUsage | None = None,
    ) -> None:
        """
        Record response details.

        Args:
            response_model: Actual model used
            embedding_dimensions: Dimension of embedding vectors
            batch_count: Number of batches processed
            usage: Token usage from response
        """
        self.response_model = response_model
        self.embedding_dimensions = embedding_dimensions
        self.batch_count = batch_count
        if usage:
            self.usage = usage

    def set_error(self, error: Exception) -> None:
        """Record an error."""
        self.success = False
        self.error = error

    def set_retry_info(self, attempt_number: int, total_attempts: int) -> None:
        """Record retry information."""
        self.attempt_number = attempt_number
        self.total_attempts = total_attempts

    def finish(self) -> None:
        """Finish tracking and close span."""
        self._end_time = time.perf_counter()
        if self.span_id and self.helper.telemetry:
            self.helper.telemetry.end_span(self.span_id, {"success": str(self.success)})

    def to_metrics(self) -> EmbeddingMetrics:
        """Convert to EmbeddingMetrics."""
        duration_ms = (self._end_time - self._start_time) * 1000

        cost: CostEstimate | None = None
        if self.helper.cost_calculator:
            cost = self.helper.cost_calculator.calculate(
                model=self.response_model or self.model,
                input_tokens=self.usage.input_tokens,
                output_tokens=0,
            )

        error_type = None
        error_category = None
        error_message = None
        if self.error:
            error_type = type(self.error).__name__
            error_category = classify_error(self.error)
            error_message = str(self.error)[:500]

        return EmbeddingMetrics(
            request_id=self.request_id,
            provider_name=self.helper.provider_name,
            request_model=self.model,
            response_model=self.response_model,
            duration_ms=duration_ms,
            text_count=self.text_count,
            total_characters=self.total_characters,
            embedding_dimensions=self.embedding_dimensions,
            batch_count=self.batch_count,
            usage=self.usage,
            cost=cost,
            success=self.success,
            error_type=error_type,
            error_category=error_category,
            error_message=error_message,
        )


class LLMTelemetryHelper:
    """
    Helper class for capturing LLM telemetry.

    Reduces code duplication and ensures consistent attribute naming
    following OpenTelemetry GenAI semantic conventions.

    Example:
        helper = LLMTelemetryHelper(telemetry, cost_calculator)

        with helper.track_completion(
            model="gpt-4",
            context=conversation_context,
        ) as tracker:
            response = await llm.complete(messages)
            tracker.set_response(
                response_model=response.model,
                usage=TokenUsage.from_response(response.usage),
            )

        # Metrics automatically emitted on context exit
    """

    def __init__(
        self,
        telemetry: TelemetryInterface | None = None,
        cost_calculator: CostCalculatorProtocol | None = None,
        provider_name: str = "litellm",
    ) -> None:
        """
        Initialize telemetry helper.

        Args:
            telemetry: TelemetryInterface for capturing events and spans
            cost_calculator: CostCalculator for cost estimation
            provider_name: Provider name for OTel attributes
        """
        self.telemetry = telemetry
        self.cost_calculator = cost_calculator
        self.provider_name = provider_name

    @contextmanager
    def track_completion(
        self,
        model: str,
        context: ConversationContext | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tool_count: int = 0,
    ) -> Generator[CompletionTracker, None, None]:
        """
        Context manager for tracking a chat completion.

        Args:
            model: Model name
            context: Optional conversation context for pairing
            temperature: Request temperature
            max_tokens: Max tokens parameter
            tool_count: Number of tools provided

        Yields:
            CompletionTracker for recording response details
        """
        tracker = CompletionTracker(
            helper=self,
            model=model,
            context=context,
            temperature=temperature,
            max_tokens=max_tokens,
            tool_count=tool_count,
        )
        tracker.start()

        try:
            yield tracker
        except Exception as e:
            tracker.set_error(e)
            raise
        finally:
            tracker.finish()
            self._emit_completion_metrics(tracker)

    @contextmanager
    def track_embedding(
        self,
        model: str,
        text_count: int,
        total_characters: int,
    ) -> Generator[EmbeddingTracker, None, None]:
        """
        Context manager for tracking an embedding operation.

        Args:
            model: Embedding model name
            text_count: Number of texts being embedded
            total_characters: Total character count

        Yields:
            EmbeddingTracker for recording response details
        """
        tracker = EmbeddingTracker(
            helper=self,
            model=model,
            text_count=text_count,
            total_characters=total_characters,
        )
        tracker.start()

        try:
            yield tracker
        except Exception as e:
            tracker.set_error(e)
            raise
        finally:
            tracker.finish()
            self._emit_embedding_metrics(tracker)

    def create_streaming_tracker(self) -> StreamingTracker:
        """Create a new streaming tracker for TTFT measurement."""
        return StreamingTracker()

    def _emit_completion_metrics(self, tracker: CompletionTracker) -> None:
        """Emit telemetry for a completed chat completion."""
        if not self.telemetry:
            return

        metrics = tracker.to_metrics()

        # Build OTel-compatible attributes
        attributes: dict[str, Any] = {
            OTelAttributes.OPERATION_NAME: metrics.operation_name.value,
            OTelAttributes.PROVIDER_NAME: metrics.provider_name,
            OTelAttributes.REQUEST_MODEL: metrics.request_model,
            OTelAttributes.INPUT_TOKENS: metrics.usage.input_tokens,
            OTelAttributes.OUTPUT_TOKENS: metrics.usage.output_tokens,
            "duration_ms": metrics.duration_ms,
            "success": metrics.success,
            OTelAttributes.FRIDAY_REQUEST_ID: metrics.request_id,
        }

        if metrics.response_model:
            attributes[OTelAttributes.RESPONSE_MODEL] = metrics.response_model
        if metrics.response_id:
            attributes[OTelAttributes.RESPONSE_ID] = metrics.response_id
        if metrics.temperature is not None:
            attributes[OTelAttributes.TEMPERATURE] = metrics.temperature
        if metrics.conversation_id:
            attributes[OTelAttributes.CONVERSATION_ID] = metrics.conversation_id
        if metrics.turn_id:
            attributes[OTelAttributes.FRIDAY_TURN_ID] = metrics.turn_id
        if metrics.cost:
            attributes[OTelAttributes.FRIDAY_COST_USD] = metrics.cost.total_cost
        if metrics.finish_reasons:
            attributes[OTelAttributes.FINISH_REASONS] = ",".join(metrics.finish_reasons)
        if metrics.tool_calls_count > 0:
            attributes["tool_calls_count"] = metrics.tool_calls_count
        if metrics.tool_count > 0:
            attributes["tool_count"] = metrics.tool_count
        if metrics.total_attempts > 1:
            attributes[OTelAttributes.FRIDAY_ATTEMPT] = metrics.attempt_number
            attributes[OTelAttributes.FRIDAY_TOTAL_ATTEMPTS] = metrics.total_attempts

        # Streaming metrics
        if metrics.streaming:
            if metrics.streaming.time_to_first_token_ms is not None:
                attributes[OTelAttributes.FRIDAY_TTFT_MS] = (
                    metrics.streaming.time_to_first_token_ms
                )
            if metrics.streaming.tokens_per_second is not None:
                attributes[OTelAttributes.FRIDAY_TOKENS_PER_SEC] = (
                    metrics.streaming.tokens_per_second
                )
            attributes[OTelAttributes.FRIDAY_CHUNK_COUNT] = metrics.streaming.chunk_count

        # Error info
        if not metrics.success:
            if metrics.error_type:
                attributes[OTelAttributes.ERROR_TYPE] = metrics.error_type
            if metrics.error_category:
                attributes[OTelAttributes.FRIDAY_ERROR_CATEGORY] = (
                    metrics.error_category.value
                )
            if metrics.error_message:
                attributes["error_message"] = metrics.error_message

        # Emit event
        event_name = "llm_completion_success" if metrics.success else "llm_completion_error"
        self.telemetry.capture_event(event_name, attributes)

    def _emit_embedding_metrics(self, tracker: EmbeddingTracker) -> None:
        """Emit telemetry for a completed embedding operation."""
        if not self.telemetry:
            return

        metrics = tracker.to_metrics()

        attributes: dict[str, Any] = {
            OTelAttributes.OPERATION_NAME: metrics.operation_name.value,
            OTelAttributes.PROVIDER_NAME: metrics.provider_name,
            OTelAttributes.REQUEST_MODEL: metrics.request_model,
            OTelAttributes.INPUT_TOKENS: metrics.usage.input_tokens,
            "duration_ms": metrics.duration_ms,
            "text_count": metrics.text_count,
            "total_characters": metrics.total_characters,
            "batch_count": metrics.batch_count,
            "success": metrics.success,
            OTelAttributes.FRIDAY_REQUEST_ID: metrics.request_id,
        }

        if metrics.response_model:
            attributes[OTelAttributes.RESPONSE_MODEL] = metrics.response_model
        if metrics.embedding_dimensions:
            attributes[OTelAttributes.EMBEDDINGS_DIMENSION] = metrics.embedding_dimensions
        if metrics.cost:
            attributes[OTelAttributes.FRIDAY_COST_USD] = metrics.cost.total_cost

        # Error info
        if not metrics.success:
            if metrics.error_type:
                attributes[OTelAttributes.ERROR_TYPE] = metrics.error_type
            if metrics.error_category:
                attributes[OTelAttributes.FRIDAY_ERROR_CATEGORY] = (
                    metrics.error_category.value
                )
            if metrics.error_message:
                attributes["error_message"] = metrics.error_message

        event_name = "embeddings_generated" if metrics.success else "embeddings_error"
        self.telemetry.capture_event(event_name, attributes)
