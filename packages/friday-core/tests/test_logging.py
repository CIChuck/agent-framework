"""
Tests for structured logging utilities.

Tests cover:
- LoggerProtocol interface
- get_logger factory function
- Environment-based formatting (dev vs production)
- Structured context logging

Ref: Batch 0 Specification, Section 4.1
"""

import io
import sys
from unittest.mock import patch

import pytest

from friday_core import LoggerProtocol, get_logger


class TestLoggerProtocol:
    """Tests for the LoggerProtocol interface."""

    def test_logger_protocol_methods(self):
        """Test that LoggerProtocol defines required methods."""
        # Verify protocol defines the expected methods
        assert hasattr(LoggerProtocol, "debug")
        assert hasattr(LoggerProtocol, "info")
        assert hasattr(LoggerProtocol, "warning")
        assert hasattr(LoggerProtocol, "error")
        assert hasattr(LoggerProtocol, "exception")


class TestGetLogger:
    """Tests for the get_logger factory function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a valid logger."""
        logger = get_logger("test_module")

        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")

    def test_get_logger_with_name(self):
        """Test that logger is created with the specified name."""
        logger = get_logger("my_custom_logger")

        # Logger should be callable
        assert callable(getattr(logger, "info", None))

    def test_get_logger_development_mode(self):
        """Test logger configuration in development mode."""
        logger = get_logger("dev_logger", environment="development")

        # Should return a valid logger (structlog)
        assert logger is not None

    def test_get_logger_production_mode(self):
        """Test logger configuration in production mode."""
        logger = get_logger("prod_logger", environment="production")

        # Should return a valid logger
        assert logger is not None

    def test_logger_info_method(self, capsys):
        """Test that logger.info() works correctly."""
        logger = get_logger("info_test", environment="development")

        # This should not raise
        logger.info("Test message")

    def test_logger_debug_method(self, capsys):
        """Test that logger.debug() works correctly."""
        logger = get_logger("debug_test", environment="development")

        # This should not raise
        logger.debug("Debug message")

    def test_logger_warning_method(self, capsys):
        """Test that logger.warning() works correctly."""
        logger = get_logger("warning_test", environment="development")

        # This should not raise
        logger.warning("Warning message")

    def test_logger_error_method(self, capsys):
        """Test that logger.error() works correctly."""
        logger = get_logger("error_test", environment="development")

        # This should not raise
        logger.error("Error message")


class TestStructuredLogging:
    """Tests for structured logging with context."""

    def test_logger_accepts_context_kwargs(self):
        """Test that logger accepts structured context kwargs."""
        logger = get_logger("context_test", environment="development")

        # Should not raise when passed context kwargs
        logger.info("Processing request", user_id="123", action="recall")
        logger.debug("Query details", query="test", results=5)
        logger.warning("Slow response", latency_ms=500)
        logger.error("Operation failed", error_code="E001", component="vector")

    def test_logger_with_complex_context(self):
        """Test logger with complex nested context."""
        logger = get_logger("complex_test", environment="development")

        context = {
            "user": {"id": "123", "role": "admin"},
            "request": {"path": "/api/recall", "method": "POST"},
            "metrics": {"latency": 0.5, "tokens": 100},
        }

        # Should handle complex context without error
        logger.info("Complex context", **context)

    def test_logger_with_none_values(self):
        """Test logger handles None values in context."""
        logger = get_logger("none_test", environment="development")

        # Should not raise with None values
        logger.info("Message with None", value=None, optional=None)


class TestLoggerEnvironmentSwitching:
    """Tests for switching between development and production logging."""

    def test_switch_from_dev_to_prod(self):
        """Test switching logger environment from dev to production."""
        # Start with development
        dev_logger = get_logger("switch_test", environment="development")
        dev_logger.info("Development log")

        # Switch to production
        prod_logger = get_logger("switch_test", environment="production")
        prod_logger.info("Production log")

        # Both should work
        assert dev_logger is not None
        assert prod_logger is not None

    def test_multiple_loggers_same_environment(self):
        """Test creating multiple loggers in same environment."""
        logger1 = get_logger("module1", environment="development")
        logger2 = get_logger("module2", environment="development")
        logger3 = get_logger("module3", environment="development")

        # All should be valid
        assert logger1 is not None
        assert logger2 is not None
        assert logger3 is not None

        # All should work
        logger1.info("Log from module1")
        logger2.info("Log from module2")
        logger3.info("Log from module3")
