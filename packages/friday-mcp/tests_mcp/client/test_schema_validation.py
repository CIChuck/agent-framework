"""A hostile input schema cannot hold the MCP call path indefinitely."""

from __future__ import annotations

import time

import pytest

from friday_mcp.client.schema_validation import (
    MCPArgumentValidationError,
    validate_arguments_with_deadline,
)


def test_catastrophic_pattern_is_stopped_before_tool_call() -> None:
    schema = {
        "type": "object",
        "properties": {"value": {"type": "string", "pattern": "^(a+)+$"}},
    }
    started = time.monotonic()
    with pytest.raises(MCPArgumentValidationError, match="local validation") as failure:
        validate_arguments_with_deadline(
            {"value": "a" * 60 + "!"}, schema, "2020-12", timeout_seconds=1.0
        )
    assert failure.value.reason == "validation_limit"
    assert time.monotonic() - started < 2.5
