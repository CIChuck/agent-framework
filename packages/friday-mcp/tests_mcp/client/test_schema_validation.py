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


def test_large_argument_tree_rejects_before_serialization(monkeypatch) -> None:
    def forbidden_dumps(*_args, **_kwargs):
        raise AssertionError("serialization ran before the node cap")

    monkeypatch.setattr(
        "friday_mcp.client.schema_validation.json.dumps", forbidden_dumps
    )
    with pytest.raises(MCPArgumentValidationError) as failure:
        validate_arguments_with_deadline(
            {"items": list(range(1_000_000))},
            {"type": "object"},
            "2020-12",
            timeout_seconds=0.001,
        )
    assert failure.value.reason == "validation_limit"


def test_deadline_includes_preflight_work() -> None:
    with pytest.raises(MCPArgumentValidationError) as failure:
        validate_arguments_with_deadline(
            {"value": "safe"},
            {"type": "object"},
            "2020-12",
            timeout_seconds=0,
        )
    assert failure.value.reason == "validation_limit"
