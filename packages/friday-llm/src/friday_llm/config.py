# mypy: ignore-errors
"""
Resilience configuration for LLM services.

Provides configuration for retry logic, timeouts, and circuit breaker
behavior in LLM API calls.

Ref: Batch 3 Specification, Section 3.1 - Resilience
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import litellm
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    pass


# Default retryable exceptions from litellm
DEFAULT_RETRY_EXCEPTIONS: tuple[type[Exception], ...] = (
    litellm.RateLimitError,
    litellm.ServiceUnavailableError,
    litellm.APIConnectionError,
    litellm.InternalServerError,
)


class CircuitBreakerConfig(BaseModel):
    """
    Circuit breaker configuration for fail-fast behavior.

    When enabled, after `failure_threshold` consecutive failures,
    the circuit opens and subsequent calls fail fast for `recovery_timeout`
    seconds before attempting again.

    Example:
        config = CircuitBreakerConfig(
            enabled=True,
            failure_threshold=3,
            recovery_timeout=60.0,
        )
    """

    enabled: bool = Field(
        default=False,
        description="Enable circuit breaker pattern",
    )
    failure_threshold: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of consecutive failures before opening circuit",
    )
    recovery_timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Seconds to wait before attempting recovery",
    )
    half_open_max_calls: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Max calls allowed in half-open state",
    )


class ResilienceConfig(BaseModel):
    """
    Configuration for retry logic, timeouts, and circuit breaker.

    Sensible defaults are provided for typical production use:
    - 3 retries with exponential backoff
    - 30 second timeout
    - Retry on rate limits and transient errors

    Example:
        # Default usage - just works
        service = LiteLLMService(model_name="gpt-4")

        # Custom resilience settings
        config = ResilienceConfig(
            max_retries=5,
            timeout_seconds=60.0,
            circuit_breaker=CircuitBreakerConfig(enabled=True),
        )
        service = LiteLLMService(model_name="gpt-4", resilience=config)
    """

    # Retry Configuration
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts (0 disables retries)",
    )

    # Backoff Configuration
    backoff_multiplier: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Multiplier for exponential backoff",
    )
    backoff_min: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Minimum backoff time in seconds",
    )
    backoff_max: float = Field(
        default=10.0,
        ge=1.0,
        le=120.0,
        description="Maximum backoff time in seconds",
    )

    # Timeout Configuration
    timeout_seconds: float = Field(
        default=30.0,
        ge=1.0,
        le=600.0,
        description="Timeout for individual API calls in seconds",
    )
    stream_timeout_seconds: float = Field(
        default=60.0,
        ge=5.0,
        le=600.0,
        description="Timeout for streaming calls (typically longer)",
    )

    # Circuit Breaker
    circuit_breaker: CircuitBreakerConfig = Field(
        default_factory=CircuitBreakerConfig,
    )

    model_config = {"arbitrary_types_allowed": True}

    def get_retry_exceptions(self) -> tuple[type[Exception], ...]:
        """Get the exceptions that should trigger retries."""
        return DEFAULT_RETRY_EXCEPTIONS

    @classmethod
    def disabled(cls) -> ResilienceConfig:
        """
        Create config with all resilience features disabled.

        Useful for testing or when you want raw errors to propagate.

        Example:
            service = LiteLLMService(
                model_name="gpt-4",
                resilience=ResilienceConfig.disabled(),
            )
        """
        return cls(
            max_retries=0,
            timeout_seconds=600.0,  # Very long timeout
            stream_timeout_seconds=600.0,
            circuit_breaker=CircuitBreakerConfig(enabled=False),
        )

    @classmethod
    def aggressive(cls) -> ResilienceConfig:
        """
        Create config with aggressive retry/recovery settings.

        More retries, longer timeouts, circuit breaker enabled.
        Good for production systems where availability is critical.

        Example:
            service = LiteLLMService(
                model_name="gpt-4",
                resilience=ResilienceConfig.aggressive(),
            )
        """
        return cls(
            max_retries=5,
            timeout_seconds=60.0,
            stream_timeout_seconds=120.0,
            backoff_multiplier=2.0,
            backoff_max=30.0,
            circuit_breaker=CircuitBreakerConfig(
                enabled=True,
                failure_threshold=3,
                recovery_timeout=60.0,
            ),
        )

    @classmethod
    def from_environment(cls) -> ResilienceConfig:
        """
        Create config from environment variables.

        Environment variables:
        - FRIDAY_LLM_MAX_RETRIES: Maximum retry attempts (default: 3)
        - FRIDAY_LLM_TIMEOUT_SECONDS: Timeout in seconds (default: 30.0)
        - FRIDAY_LLM_STREAM_TIMEOUT_SECONDS: Stream timeout (default: 60.0)
        - FRIDAY_LLM_BACKOFF_MULTIPLIER: Backoff multiplier (default: 1.0)
        - FRIDAY_LLM_BACKOFF_MAX: Max backoff seconds (default: 10.0)
        - FRIDAY_LLM_CIRCUIT_BREAKER_ENABLED: Enable circuit breaker (default: false)
        - FRIDAY_LLM_CB_FAILURE_THRESHOLD: Failure threshold (default: 5)
        - FRIDAY_LLM_CB_RECOVERY_TIMEOUT: Recovery timeout (default: 30.0)

        Example:
            # In shell: export FRIDAY_LLM_MAX_RETRIES=5
            config = ResilienceConfig.from_environment()
        """
        return cls(
            max_retries=int(os.getenv("FRIDAY_LLM_MAX_RETRIES", "3")),
            timeout_seconds=float(os.getenv("FRIDAY_LLM_TIMEOUT_SECONDS", "30.0")),
            stream_timeout_seconds=float(
                os.getenv("FRIDAY_LLM_STREAM_TIMEOUT_SECONDS", "60.0")
            ),
            backoff_multiplier=float(os.getenv("FRIDAY_LLM_BACKOFF_MULTIPLIER", "1.0")),
            backoff_max=float(os.getenv("FRIDAY_LLM_BACKOFF_MAX", "10.0")),
            circuit_breaker=CircuitBreakerConfig(
                enabled=os.getenv("FRIDAY_LLM_CIRCUIT_BREAKER_ENABLED", "false").lower()
                == "true",
                failure_threshold=int(
                    os.getenv("FRIDAY_LLM_CB_FAILURE_THRESHOLD", "5")
                ),
                recovery_timeout=float(
                    os.getenv("FRIDAY_LLM_CB_RECOVERY_TIMEOUT", "30.0")
                ),
            ),
        )
