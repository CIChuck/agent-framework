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


class LLMConfigurationError(LLMServiceError):
    """Base error for deterministic preflight failures."""


class ModelLibraryError(LLMConfigurationError):
    """Raised when a catalog or service binding cannot be resolved."""


class CredentialResolutionError(ModelLibraryError):
    """Raised when a selected credential cannot be resolved safely."""


class UnsupportedControlError(LLMConfigurationError):
    """Raised before I/O when a target does not support an explicit control."""

    def __init__(
        self,
        control: str,
        state: str,
        sources: tuple[str, ...] = (),
    ) -> None:
        source_text = ", ".join(sources) if sources else "no capability record"
        super().__init__(
            f"control {control!r} is {state} for the selected target "
            f"(sources: {source_text})"
        )
        self.control = control
        self.state = state
        self.sources = sources


class CapabilityConflictError(LLMConfigurationError):
    """Raised when applicable capability records contradict one another."""

    def __init__(self, control: str, sources: tuple[str, ...], reason: str) -> None:
        super().__init__(
            f"capability conflict for {control!r}: {reason} "
            f"(sources: {', '.join(sources)})"
        )
        self.control = control
        self.sources = sources
        self.reason = reason


class ProviderOptionsError(LLMConfigurationError):
    """Raised when typed provider options do not match the selected target."""


class TranslationConflictError(LLMConfigurationError):
    """Raised when translators attempt an undeclared wire-field collision."""


class TargetIdentityError(LLMConfigurationError):
    """Raised when explicit routing and capability identities conflict."""


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
    """  # noqa: E501

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
            f"(operation={self.operation}, timeout={self.timeout_seconds}s, model={self.model})"  # noqa: E501
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
            f"(attempts={self.attempts}, last_error={type(self.last_error).__name__}: {self.last_error}, "  # noqa: E501
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
            f"{self.args[0]} (retry_after={self.retry_after:.1f}s, model={self.model})"
        )
