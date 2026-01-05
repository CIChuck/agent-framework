"""
Exceptions for friday-llm package.

Provides clear, context-rich exceptions for resilience failures.
Callers can catch these to handle errors gracefully and provide
appropriate user feedback.

Ref: Batch 3 Specification, Section 3.1 - Resilience
"""

from __future__ import annotations


class LLMServiceError(Exception):
    """
    Base exception for all friday-llm errors.

    Catch this to handle any LLM service error generically.

    Example:
        try:
            response = await service.chat_completion(messages)
        except LLMServiceError as e:
            logger.error(f"LLM error: {e}")
            return "Service error, please try again"
    """

    pass


class LLMTimeoutError(LLMServiceError):
    """
    Raised when an LLM call times out.

    Attributes:
        timeout_seconds: The timeout that was exceeded
        operation: Which operation timed out (chat_completion, streaming, embedding)
        model: The model being called

    Example:
        try:
            response = await service.chat_completion(messages)
        except LLMTimeoutError as e:
            logger.warning(f"{e.operation} timed out after {e.timeout_seconds}s on {e.model}")
            return "The AI is taking too long to respond..."
    """

    def __init__(
        self,
        message: str,
        *,
        timeout_seconds: float,
        operation: str,
        model: str,
    ) -> None:
        super().__init__(message)
        self.timeout_seconds = timeout_seconds
        self.operation = operation
        self.model = model

    def __str__(self) -> str:
        return (
            f"{self.args[0]} "
            f"(operation={self.operation}, timeout={self.timeout_seconds}s, model={self.model})"
        )


class LLMRetryExhaustedError(LLMServiceError):
    """
    Raised when max retries are exceeded.

    Attributes:
        attempts: Number of attempts made
        last_error: The final error that caused failure
        model: The model being called

    Example:
        try:
            response = await service.chat_completion(messages)
        except LLMRetryExhaustedError as e:
            logger.error(f"Failed after {e.attempts} attempts: {e.last_error}")
            return "Service temporarily unavailable"
    """

    def __init__(
        self,
        message: str,
        *,
        attempts: int,
        last_error: Exception,
        model: str,
    ) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error
        self.model = model

    def __str__(self) -> str:
        return (
            f"{self.args[0]} "
            f"(attempts={self.attempts}, last_error={type(self.last_error).__name__}: {self.last_error}, "
            f"model={self.model})"
        )


class CircuitBreakerOpenError(LLMServiceError):
    """
    Raised when circuit breaker is open - failing fast.

    The circuit breaker opens after consecutive failures to prevent
    cascading failures. Callers should wait before retrying.

    Attributes:
        retry_after: Seconds until the circuit breaker may allow calls again
        model: The model being called

    Example:
        try:
            response = await service.chat_completion(messages)
        except CircuitBreakerOpenError as e:
            logger.warning(f"Circuit open for {e.model}, retry in {e.retry_after}s")
            return f"Service recovering, please wait {e.retry_after:.0f} seconds"
    """

    def __init__(
        self,
        message: str,
        *,
        retry_after: float,
        model: str,
    ) -> None:
        super().__init__(message)
        self.retry_after = retry_after
        self.model = model

    def __str__(self) -> str:
        return (
            f"{self.args[0]} "
            f"(retry_after={self.retry_after:.1f}s, model={self.model})"
        )
