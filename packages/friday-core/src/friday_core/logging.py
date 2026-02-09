"""
Structured logging wrapper.
Provides JSON logging for production and colored output for dev.

Routes all structlog output through Python's stdlib logging so that
the application-level log level (set via ``logging.basicConfig``) is
honoured consistently across the entire framework.

Ref: Batch 0 Specification, Section 4.1
"""

from typing import Any, Protocol

import structlog


class LoggerProtocol(Protocol):
    """
    Abstract logger interface for swappability.

    Defines the standard logging methods that any logger implementation
    must provide. This allows swapping structlog for another logging
    library without changing consumer code.
    """

    def debug(self, msg: str, **context: Any) -> None:
        """Log a debug message with optional structured context."""
        ...

    def info(self, msg: str, **context: Any) -> None:
        """Log an info message with optional structured context."""
        ...

    def warning(self, msg: str, **context: Any) -> None:
        """Log a warning message with optional structured context."""
        ...

    def error(self, msg: str, **context: Any) -> None:
        """Log an error message with optional structured context."""
        ...

    def exception(self, msg: str, **context: Any) -> None:
        """Log an exception with traceback and optional structured context."""
        ...


def _configure_structlog(environment: str) -> None:
    """
    Configure structlog processors based on environment.

    Uses ``structlog.stdlib.LoggerFactory`` so that all output is
    routed through Python's stdlib logging system.  This ensures the
    application-wide log level (e.g. ``logging.WARNING``) is respected
    by every logger created via ``get_logger()``.

    Args:
        environment: ``"production"`` for JSON output,
            ``"development"`` for colored console.
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if environment == "production":
        # JSON output for production (machine-parseable)
        shared_processors.append(
            structlog.processors.JSONRenderer()
        )
    else:
        # Colored console output for development (human-readable)
        shared_processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=(
                    structlog.dev.plain_traceback
                ),
            )
        )

    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Track if structlog has been configured
_configured_for: str | None = None


def get_logger(
    name: str, environment: str = "development"
) -> LoggerProtocol:
    """
    Factory function for structured loggers.

    Returns a structlog logger that routes through Python's stdlib
    logging, so the application-wide log level is respected.

    Args:
        name: Logger name (typically ``__name__`` of the calling
            module).
        environment: ``"production"`` for JSON output,
            ``"development"`` for colored console.

    Returns:
        A logger instance conforming to ``LoggerProtocol``.

    Example::

        logger = get_logger(__name__)
        logger.info("Processing request", user_id="123")
    """
    global _configured_for

    # Configure structlog if not already done or if environment changed
    if _configured_for != environment:
        _configure_structlog(environment)
        _configured_for = environment

    return structlog.get_logger(name)
