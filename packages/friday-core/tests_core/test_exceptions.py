# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""
Tests for the Friday exception hierarchy.

Tests cover:
- Exception inheritance
- Catching specific exceptions
- Catching root FridayError

Ref: Batch 0 Specification, Section 4.2
"""

import pytest
from friday_core import (
    ContextOverflowError,
    FridayError,
    MemoryError,
    ProviderAPIError,
)


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_friday_error_is_base_exception(self):
        """Test that FridayError inherits from Exception."""
        assert issubclass(FridayError, Exception)

    def test_memory_error_inherits_friday_error(self):
        """Test that MemoryError is a FridayError."""
        assert issubclass(MemoryError, FridayError)
        assert issubclass(MemoryError, Exception)

    def test_context_overflow_error_inherits_friday_error(self):
        """Test that ContextOverflowError is a FridayError."""
        assert issubclass(ContextOverflowError, FridayError)
        assert issubclass(ContextOverflowError, Exception)

    def test_provider_api_error_inherits_friday_error(self):
        """Test that ProviderAPIError is a FridayError."""
        assert issubclass(ProviderAPIError, FridayError)
        assert issubclass(ProviderAPIError, Exception)


class TestExceptionRaising:
    """Tests for raising and catching exceptions."""

    def test_raise_friday_error(self):
        """Test raising and catching FridayError."""
        with pytest.raises(FridayError) as exc_info:
            raise FridayError("Generic Friday error")

        assert "Generic Friday error" in str(exc_info.value)

    def test_raise_memory_error(self):
        """Test raising and catching MemoryError."""
        with pytest.raises(MemoryError) as exc_info:
            raise MemoryError("Database connection failed")

        assert "Database connection failed" in str(exc_info.value)

    def test_raise_context_overflow_error(self):
        """Test raising and catching ContextOverflowError."""
        with pytest.raises(ContextOverflowError) as exc_info:
            raise ContextOverflowError("Token budget exceeded")

        assert "Token budget exceeded" in str(exc_info.value)

    def test_raise_provider_api_error(self):
        """Test raising and catching ProviderAPIError."""
        with pytest.raises(ProviderAPIError) as exc_info:
            raise ProviderAPIError("OpenAI API rate limit exceeded")

        assert "OpenAI API rate limit exceeded" in str(exc_info.value)


class TestExceptionCatching:
    """Tests for exception catching patterns."""

    def test_catch_specific_exception(self):
        """Test catching a specific exception type."""
        caught = False
        try:
            raise MemoryError("Specific error")
        except MemoryError:
            caught = True

        assert caught is True

    def test_catch_friday_error_catches_subclasses(self):
        """Test that catching FridayError catches all subclasses."""
        caught_memory = False
        caught_context = False
        caught_provider = False

        # MemoryError
        try:
            raise MemoryError("Memory failure")
        except FridayError:
            caught_memory = True

        # ContextOverflowError
        try:
            raise ContextOverflowError("Overflow")
        except FridayError:
            caught_context = True

        # ProviderAPIError
        try:
            raise ProviderAPIError("API failure")
        except FridayError:
            caught_provider = True

        assert caught_memory is True
        assert caught_context is True
        assert caught_provider is True

    def test_exception_not_caught_by_unrelated_type(self):
        """Test that exceptions aren't caught by unrelated types."""
        with pytest.raises(MemoryError):
            try:
                raise MemoryError("Memory error")
            except ProviderAPIError:
                pass  # Should not catch MemoryError

    def test_exception_with_cause(self):
        """Test exception chaining with __cause__."""
        original = ValueError("Original error")

        try:
            try:
                raise original
            except ValueError as e:
                raise MemoryError("Wrapped error") from e
        except MemoryError as e:
            assert e.__cause__ is original
            assert "Wrapped error" in str(e)
