# mypy: ignore-errors
"""
Circuit breaker pattern for LLM API calls.

Prevents cascading failures when an API is down by failing fast
after a threshold of consecutive failures.

Ref: Batch 3 Specification, Section 3.1 - Resilience
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from enum import Enum, auto
from typing import Any, TypeVar

from friday_llm.config import CircuitBreakerConfig
from friday_llm.exceptions import CircuitBreakerOpenError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = auto()  # Normal operation - calls pass through
    OPEN = auto()  # Failure mode - calls fail fast
    HALF_OPEN = auto()  # Testing recovery - limited calls allowed


class CircuitBreaker:
    """
    Circuit breaker for async operations.

    Thread-safe implementation using asyncio locks.

    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Failing fast, calls rejected immediately
    - HALF_OPEN: Testing if service recovered, limited calls allowed

    Example:
        config = CircuitBreakerConfig(enabled=True, failure_threshold=3)
        cb = CircuitBreaker(config, model="gpt-4")

        try:
            result = await cb.call(my_async_function, arg1, arg2)
        except CircuitBreakerOpenError as e:
            print(f"Service down, retry in {e.retry_after}s")
    """

    def __init__(self, config: CircuitBreakerConfig, model: str = "unknown") -> None:
        """
        Initialize circuit breaker.

        Args:
            config: Circuit breaker configuration
            model: Model name for error context
        """
        self.config = config
        self.model = model
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Current circuit state."""
        return self._state

    @property
    def is_closed(self) -> bool:
        """Check if circuit allows calls."""
        return self._state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)

    @property
    def failure_count(self) -> int:
        """Current consecutive failure count."""
        return self._failure_count

    async def call(
        self,
        func: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """
        Execute function through circuit breaker.

        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result from func

        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        if not self.config.enabled:
            return await func(*args, **kwargs)

        async with self._lock:
            await self._check_state()

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception:
            await self._on_failure()
            raise

    async def _check_state(self) -> None:
        """Check and potentially transition state."""
        if self._state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                logger.info(
                    "Circuit breaker entering half-open state",
                    extra={"model": self.model},
                )
            else:
                retry_after = self._get_retry_after()
                raise CircuitBreakerOpenError(
                    "Circuit breaker is open - failing fast",
                    retry_after=retry_after,
                    model=self.model,
                )

        if self._state == CircuitState.HALF_OPEN:
            if self._half_open_calls >= self.config.half_open_max_calls:
                raise CircuitBreakerOpenError(
                    "Circuit breaker is half-open - max calls reached",
                    retry_after=self.config.recovery_timeout,
                    model=self.model,
                )
            self._half_open_calls += 1

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._last_failure_time is None:
            return True
        elapsed = time.monotonic() - self._last_failure_time
        return elapsed >= self.config.recovery_timeout

    def _get_retry_after(self) -> float:
        """Get seconds until circuit may close."""
        if self._last_failure_time is None:
            return 0.0
        elapsed = time.monotonic() - self._last_failure_time
        return max(0.0, self.config.recovery_timeout - elapsed)

    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                logger.info(
                    "Circuit breaker closing after successful call",
                    extra={"model": self.model},
                )
            self._state = CircuitState.CLOSED
            self._failure_count = 0

    async def _on_failure(self) -> None:
        """Handle failed call."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning(
                    "Circuit breaker reopening after half-open failure",
                    extra={"model": self.model, "failure_count": self._failure_count},
                )
            elif self._failure_count >= self.config.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(
                    f"Circuit breaker opening after {self._failure_count} failures",
                    extra={"model": self.model, "failure_count": self._failure_count},
                )

    def reset(self) -> None:
        """Manually reset circuit breaker to closed state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0
        logger.info(
            "Circuit breaker manually reset",
            extra={"model": self.model},
        )
