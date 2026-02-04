"""
Tests for LLM resilience features.

Tests retry logic, timeouts, circuit breaker, and exception handling.
"""

import asyncio
import warnings

import litellm
import pytest
from unittest.mock import AsyncMock, patch

from friday_llm import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    LiteLLMEmbeddingService,
    LiteLLMService,
    LLMRetryExhaustedError,
    LLMTimeoutError,
    ResilienceConfig,
)
from friday_llm.circuit_breaker import CircuitState


# =============================================================================
# Mock Classes for Testing
# =============================================================================


class MockChoice:
    """Mock LiteLLM response choice."""

    def __init__(self, content: str = None, tool_calls: list = None):
        self.message = type("Message", (), {
            "content": content,
            "tool_calls": tool_calls or [],
        })()


class MockResponse:
    """Mock LiteLLM response."""

    def __init__(self, content: str = None, tool_calls: list = None):
        self.choices = [MockChoice(content, tool_calls)]
        self.model = "gpt-4"
        self.usage = type("Usage", (), {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        })()


class MockEmbeddingData:
    """Mock embedding data item."""

    def __init__(self, embedding: list[float]):
        self.embedding = embedding


class MockEmbeddingResponse:
    """Mock LiteLLM embedding response."""

    def __init__(self, embeddings: list[list[float]]):
        self.data = [{"embedding": e} for e in embeddings]


# =============================================================================
# ResilienceConfig Tests
# =============================================================================


class TestResilienceConfig:
    """Tests for ResilienceConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ResilienceConfig()

        assert config.max_retries == 3
        assert config.timeout_seconds == 30.0
        assert config.stream_timeout_seconds == 60.0
        assert config.backoff_multiplier == 1.0
        assert config.backoff_min == 1.0
        assert config.backoff_max == 10.0
        assert config.circuit_breaker.enabled is False

    def test_disabled_factory(self):
        """Test ResilienceConfig.disabled() factory method."""
        config = ResilienceConfig.disabled()

        assert config.max_retries == 0
        assert config.timeout_seconds == 600.0
        assert config.circuit_breaker.enabled is False

    def test_aggressive_factory(self):
        """Test ResilienceConfig.aggressive() factory method."""
        config = ResilienceConfig.aggressive()

        assert config.max_retries == 5
        assert config.timeout_seconds == 60.0
        assert config.stream_timeout_seconds == 120.0
        assert config.backoff_multiplier == 2.0
        assert config.circuit_breaker.enabled is True
        assert config.circuit_breaker.failure_threshold == 3

    def test_from_environment(self):
        """Test ResilienceConfig.from_environment() factory method."""
        with patch.dict(
            "os.environ",
            {
                "FRIDAY_LLM_MAX_RETRIES": "5",
                "FRIDAY_LLM_TIMEOUT_SECONDS": "45.0",
                "FRIDAY_LLM_CIRCUIT_BREAKER_ENABLED": "true",
            },
        ):
            config = ResilienceConfig.from_environment()

            assert config.max_retries == 5
            assert config.timeout_seconds == 45.0
            assert config.circuit_breaker.enabled is True

    def test_get_retry_exceptions(self):
        """Test that retry exceptions include expected LiteLLM errors."""
        config = ResilienceConfig()
        exceptions = config.get_retry_exceptions()

        assert litellm.RateLimitError in exceptions
        assert litellm.APIConnectionError in exceptions
        assert litellm.InternalServerError in exceptions
        assert litellm.ServiceUnavailableError in exceptions


class TestCircuitBreakerConfig:
    """Tests for CircuitBreakerConfig."""

    def test_default_values(self):
        """Test default circuit breaker configuration."""
        config = CircuitBreakerConfig()

        assert config.enabled is False
        assert config.failure_threshold == 5
        assert config.recovery_timeout == 30.0
        assert config.half_open_max_calls == 1

    def test_custom_values(self):
        """Test custom circuit breaker configuration."""
        config = CircuitBreakerConfig(
            enabled=True,
            failure_threshold=3,
            recovery_timeout=60.0,
            half_open_max_calls=2,
        )

        assert config.enabled is True
        assert config.failure_threshold == 3
        assert config.recovery_timeout == 60.0
        assert config.half_open_max_calls == 2


# =============================================================================
# Circuit Breaker Tests
# =============================================================================


class TestCircuitBreaker:
    """Tests for CircuitBreaker."""

    @pytest.mark.asyncio
    async def test_disabled_passes_through(self):
        """Test that disabled circuit breaker just passes calls through."""
        config = CircuitBreakerConfig(enabled=False)
        cb = CircuitBreaker(config, model="test")

        async def success():
            return "ok"

        result = await cb.call(success)
        assert result == "ok"
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_enabled_tracks_failures(self):
        """Test that enabled circuit breaker tracks failures."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=3)
        cb = CircuitBreaker(config, model="test")

        async def failing():
            raise ValueError("test error")

        # First two failures - circuit stays closed
        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(failing)

        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 2

    @pytest.mark.asyncio
    async def test_opens_after_threshold(self):
        """Test that circuit opens after failure threshold."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=3)
        cb = CircuitBreaker(config, model="test")

        async def failing():
            raise ValueError("test error")

        # Reach failure threshold
        for _ in range(3):
            with pytest.raises(ValueError):
                await cb.call(failing)

        assert cb.state == CircuitState.OPEN

        # Next call should fail fast
        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            await cb.call(failing)

        assert exc_info.value.model == "test"
        assert exc_info.value.retry_after >= 0

    @pytest.mark.asyncio
    async def test_success_resets_failure_count(self):
        """Test that success resets the failure count."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=3)
        cb = CircuitBreaker(config, model="test")

        async def failing():
            raise ValueError("test error")

        async def success():
            return "ok"

        # Two failures
        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(failing)

        assert cb.failure_count == 2

        # Success resets count
        await cb.call(success)
        assert cb.failure_count == 0
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_manual_reset(self):
        """Test manual circuit breaker reset."""
        config = CircuitBreakerConfig(enabled=True, failure_threshold=2)
        cb = CircuitBreaker(config, model="test")

        async def failing():
            raise ValueError("test error")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(failing)

        assert cb.state == CircuitState.OPEN

        # Manual reset
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0


# =============================================================================
# LiteLLMService Resilience Tests
# =============================================================================


class TestLiteLLMServiceResilience:
    """Tests for LiteLLMService resilience features."""

    @pytest.fixture
    def service_no_retry(self):
        """Service with retries disabled for fast tests."""
        return LiteLLMService(
            model_name="gpt-4",
            api_key="test-key",
            resilience=ResilienceConfig(max_retries=0),
        )

    @pytest.fixture
    def service_with_retry(self):
        """Service with limited retries for testing."""
        return LiteLLMService(
            model_name="gpt-4",
            api_key="test-key",
            resilience=ResilienceConfig(
                max_retries=2,
                backoff_min=0.1,
                backoff_max=1.0,
            ),
        )

    @pytest.mark.asyncio
    async def test_connection_error_raises_retry_exhausted(self, service_with_retry):
        """Test that connection errors are wrapped in LLMRetryExhaustedError."""
        with patch("litellm.acompletion", new_callable=AsyncMock) as mock:
            mock.side_effect = litellm.APIConnectionError(
                message="Connection refused",
                llm_provider="openai",
                model="gpt-4",
            )

            with pytest.raises(LLMRetryExhaustedError) as exc_info:
                await service_with_retry.chat_completion(
                    messages=[{"role": "user", "content": "test"}],
                )

            error = exc_info.value
            assert error.attempts == 3  # 1 initial + 2 retries
            assert error.model == "gpt-4"
            assert isinstance(error.last_error, litellm.APIConnectionError)

    @pytest.mark.asyncio
    async def test_rate_limit_error_retries(self, service_with_retry):
        """Test that rate limit errors trigger retries."""
        call_count = 0

        async def rate_limit_then_succeed(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise litellm.RateLimitError(
                    message="Rate limited",
                    llm_provider="openai",
                    model="gpt-4",
                    response=None,
                )
            # Return mock response on 3rd call
            return MockResponse(content="Success after retry")

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock:
            mock.side_effect = rate_limit_then_succeed

            response = await service_with_retry.chat_completion(
                messages=[{"role": "user", "content": "test"}],
            )

            assert response.content == "Success after retry"
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_timeout_error_raised(self, service_no_retry):
        """Test that timeouts are wrapped in LLMTimeoutError."""
        with patch("litellm.acompletion", new_callable=AsyncMock) as mock:
            mock.side_effect = asyncio.TimeoutError()

            with pytest.raises(LLMTimeoutError) as exc_info:
                await service_no_retry.chat_completion(
                    messages=[{"role": "user", "content": "test"}],
                    timeout=5.0,
                )

            error = exc_info.value
            assert error.timeout_seconds == 5.0
            assert error.operation == "chat_completion"
            assert error.model == "gpt-4"

    @pytest.mark.asyncio
    async def test_streaming_retry_exhausted(self, service_with_retry):
        """Test that streaming connection errors are wrapped properly."""
        with patch("litellm.acompletion", new_callable=AsyncMock) as mock:
            mock.side_effect = litellm.APIConnectionError(
                message="Connection refused",
                llm_provider="openai",
                model="gpt-4",
            )

            with pytest.raises(LLMRetryExhaustedError) as exc_info:
                async for _ in service_with_retry.chat_completion_stream(
                    messages=[{"role": "user", "content": "test"}],
                ):
                    pass

            error = exc_info.value
            assert error.attempts == 3
            assert error.model == "gpt-4"

    @pytest.mark.asyncio
    async def test_resilience_property(self):
        """Test that resilience config is accessible."""
        config = ResilienceConfig(max_retries=5)
        service = LiteLLMService(
            model_name="gpt-4",
            api_key="test-key",
            resilience=config,
        )

        assert service.resilience.max_retries == 5

    def test_deprecated_max_retries_warning(self):
        """Test that max_retries parameter emits deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            service = LiteLLMService(
                model_name="gpt-4",
                api_key="test-key",
                max_retries=5,  # Deprecated parameter
            )

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "max_retries" in str(w[0].message)
            assert service.resilience.max_retries == 5


# =============================================================================
# LiteLLMEmbeddingService Resilience Tests
# =============================================================================


class TestLiteLLMEmbeddingServiceResilience:
    """Tests for LiteLLMEmbeddingService resilience features."""

    @pytest.fixture
    def embedding_service(self):
        """Embedding service with limited retries."""
        return LiteLLMEmbeddingService(
            model_name="text-embedding-3-small",
            api_key="test-key",
            resilience=ResilienceConfig(
                max_retries=2,
                backoff_min=0.1,
                backoff_max=1.0,
            ),
        )

    @pytest.mark.asyncio
    async def test_embedding_connection_error(self, embedding_service):
        """Test that embedding connection errors are wrapped properly."""
        with patch("litellm.aembedding", new_callable=AsyncMock) as mock:
            mock.side_effect = litellm.APIConnectionError(
                message="Connection refused",
                llm_provider="openai",
                model="text-embedding-3-small",
            )

            with pytest.raises(LLMRetryExhaustedError) as exc_info:
                await embedding_service.embed_documents(["test text"])

            error = exc_info.value
            assert error.attempts == 3
            assert error.model == "text-embedding-3-small"

    @pytest.mark.asyncio
    async def test_embedding_timeout_error(self):
        """Test that embedding timeouts are wrapped properly."""
        service = LiteLLMEmbeddingService(
            model_name="text-embedding-3-small",
            api_key="test-key",
            resilience=ResilienceConfig(max_retries=0),
        )

        with patch("litellm.aembedding", new_callable=AsyncMock) as mock:
            mock.side_effect = asyncio.TimeoutError()

            with pytest.raises(LLMTimeoutError) as exc_info:
                await service.embed_query("test query", timeout=5.0)

            error = exc_info.value
            assert error.timeout_seconds == 5.0
            assert error.operation == "embedding"

    @pytest.mark.asyncio
    async def test_embedding_empty_input(self, embedding_service):
        """Test that empty input returns empty list without API call."""
        with patch("litellm.aembedding", new_callable=AsyncMock) as mock:
            result = await embedding_service.embed_documents([])

            assert result == []
            mock.assert_not_called()


# =============================================================================
# Exception Context Tests
# =============================================================================


class TestExceptionContext:
    """Tests for exception context and attributes."""

    def test_timeout_error_context(self):
        """Test LLMTimeoutError has all context attributes."""
        error = LLMTimeoutError(
            "Request timed out",
            timeout_seconds=30.0,
            operation="chat_completion",
            model="gpt-4",
        )

        assert error.timeout_seconds == 30.0
        assert error.operation == "chat_completion"
        assert error.model == "gpt-4"
        assert "Request timed out" in str(error)

    def test_retry_exhausted_error_context(self):
        """Test LLMRetryExhaustedError has all context attributes."""
        original_error = ValueError("original error")
        error = LLMRetryExhaustedError(
            "Retries exhausted",
            attempts=4,
            last_error=original_error,
            model="gpt-4",
        )

        assert error.attempts == 4
        assert error.last_error is original_error
        assert error.model == "gpt-4"
        assert "Retries exhausted" in str(error)

    def test_circuit_breaker_error_context(self):
        """Test CircuitBreakerOpenError has all context attributes."""
        error = CircuitBreakerOpenError(
            "Circuit is open",
            retry_after=30.0,
            model="gpt-4",
        )

        assert error.retry_after == 30.0
        assert error.model == "gpt-4"
        assert "Circuit is open" in str(error)


# =============================================================================
# Integration-like Tests (with mocked network)
# =============================================================================


class TestResilienceIntegration:
    """Integration-style tests for resilience features."""

    @pytest.mark.asyncio
    async def test_full_retry_cycle_chat(self):
        """Test complete retry cycle for chat completion."""
        service = LiteLLMService(
            model_name="gpt-4",
            api_key="test-key",
            resilience=ResilienceConfig(
                max_retries=3,
                backoff_min=0.1,
                backoff_max=1.0,
            ),
        )

        call_count = 0

        async def fail_then_succeed(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise litellm.InternalServerError(
                    message="Server error",
                    llm_provider="openai",
                    model="gpt-4",
                )
            return MockResponse(content="Finally worked!")

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock:
            mock.side_effect = fail_then_succeed

            response = await service.chat_completion(
                messages=[{"role": "user", "content": "test"}],
            )

            assert response.content == "Finally worked!"
            assert call_count == 3  # 2 failures + 1 success

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self):
        """Test circuit breaker opens and blocks calls."""
        service = LiteLLMService(
            model_name="gpt-4",
            api_key="test-key",
            resilience=ResilienceConfig(
                max_retries=0,  # No retries so we can control failure count
                circuit_breaker=CircuitBreakerConfig(
                    enabled=True,
                    failure_threshold=2,
                    recovery_timeout=60.0,
                ),
            ),
        )

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock:
            mock.side_effect = litellm.InternalServerError(
                message="Server error",
                llm_provider="openai",
                model="gpt-4",
            )

            # First two calls fail with InternalServerError (via RetryExhausted)
            for _ in range(2):
                with pytest.raises(LLMRetryExhaustedError):
                    await service.chat_completion(
                        messages=[{"role": "user", "content": "test"}],
                    )

            # Third call should fail fast with CircuitBreakerOpenError
            with pytest.raises(CircuitBreakerOpenError) as exc_info:
                await service.chat_completion(
                    messages=[{"role": "user", "content": "test"}],
                )

            assert exc_info.value.retry_after > 0
