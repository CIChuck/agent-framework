"""
Introductory Example: Basic Structured Logging

This example demonstrates:
- Creating loggers with get_logger()
- Logging at different levels (debug, info, warning, error)
- Adding structured context to log messages
- Switching between development and production output formats

Run with: uv run python packages/friday-core/examples/01_introductory.py
"""

from friday_core import get_logger


def main():
    # Create a logger for this module
    # Development mode provides colored, human-readable output
    logger = get_logger("my_app", environment="development")

    print("=== Development Mode (Colored Console Output) ===\n")

    # Basic logging at different levels
    logger.debug("This is a debug message")
    logger.info("Application started")
    logger.warning("This is a warning")
    logger.error("Something went wrong")

    print("\n=== Structured Context Logging ===\n")

    # Add structured context to log messages
    # These key-value pairs are attached to the log entry
    logger.info("User logged in", user_id="user_123", ip_address="192.168.1.1")

    logger.info(
        "Processing request",
        request_id="req_abc",
        method="POST",
        path="/api/recall",
    )

    logger.warning(
        "Slow response detected", latency_ms=1500, threshold_ms=1000, endpoint="/search"
    )

    logger.error(
        "Database connection failed",
        error_code="DB_001",
        retry_count=3,
        database="postgres",
    )

    print("\n=== Production Mode (JSON Output) ===\n")

    # Production mode outputs JSON for machine parsing
    prod_logger = get_logger("my_app_prod", environment="production")

    prod_logger.info(
        "Request completed",
        request_id="req_xyz",
        status_code=200,
        duration_ms=45,
    )

    prod_logger.error(
        "API rate limit exceeded",
        provider="openai",
        requests_remaining=0,
        reset_at="2024-01-15T10:30:00Z",
    )

    print("\n=== Complex Nested Context ===\n")

    # Loggers handle complex nested data structures
    dev_logger = get_logger("complex_app", environment="development")

    dev_logger.info(
        "Memory operation completed",
        user={"id": "user_456", "role": "admin"},
        operation={"type": "recall", "budget_tokens": 4000},
        metrics={"latency_ms": 120, "tokens_used": 350, "cache_hit": True},
    )


if __name__ == "__main__":
    main()
