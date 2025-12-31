"""
Base exception hierarchy for the Friday Framework.
Defines FridayError, MemoryError, ContextOverflowError, etc.

Ref: Batch 0 Specification, Section 4.2
"""


class FridayError(Exception):
    """
    Root exception for the Friday Framework.

    All framework-specific exceptions inherit from this class,
    allowing consumers to catch all Friday errors with a single handler.
    """

    pass


class MemoryError(FridayError):
    """
    Base exception for database/storage failures.

    Raised when operations on Vector, Graph, or Episodic stores fail.
    """

    pass


class ContextOverflowError(FridayError):
    """
    Raised when the Context Budget is impossible to satisfy.

    This occurs when the minimum required context (system prompt,
    immediate history, critical user data) exceeds the available
    token budget.
    """

    pass


class ProviderAPIError(FridayError):
    """
    Raised when LLM provider API calls fail.

    Wraps errors from LiteLLM, OpenAI, or other provider SDKs
    to provide a consistent error interface.
    """

    pass
