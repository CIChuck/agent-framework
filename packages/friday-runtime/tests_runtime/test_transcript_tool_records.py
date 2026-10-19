"""Direct, frontend-independent transcript tool-record contracts."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, replace

import pytest
from friday_core.mcp import MCPToolCallProvenance, MCPToolMetadata
from friday_runtime.transcript_tool_records import (
    build_transcript_tool_records,
    validate_transcript_tool_provenance,
)


@dataclass(frozen=True)
class ToolInput:
    name: str
    arguments: dict[str, object]
    result: str
    call_id: str | None = None
    mcp_provenance: MCPToolCallProvenance | None = None


def _facts(
    result: str = "é",
    *,
    call_id: str | None = "mcp-call",
    status: str = "succeeded",
    failure_code: str | None = None,
    correlation: str | None = None,
) -> MCPToolCallProvenance:
    return MCPToolCallProvenance.model_validate(
        {
            "tool": MCPToolMetadata(
                canonical_name="mcp_peer_read",
                server_name="peer",
                original_name="read",
                transport="stdio",
                trust_level="local",
            ),
            "call_id": call_id,
            "status": status,
            "output_sanitization_state": "unchanged",
            "model_result_size_bytes": len(result.encode("utf-8")),
            "failure_code": failure_code,
            "transcript_correlation_id": correlation,
        }
    )


def test_empty_and_native_records_preserve_ids_order_and_argument_copy() -> None:
    assert validate_transcript_tool_provenance("turn", (), 0) == []
    assert build_transcript_tool_records("turn", (), ()) == ([], [])

    arguments: dict[str, object] = {"value": "first"}
    calls = (
        ToolInput("echo", arguments, "one", "given"),
        ToolInput("calculate", {"n": 2}, "two"),
    )
    provenance = validate_transcript_tool_provenance("turn", calls, 0)
    tool_calls, tool_results = build_transcript_tool_records("turn", calls, provenance)
    arguments["value"] = "changed"

    assert provenance == [None, None]
    assert [call.id for call in tool_calls] == ["given", "turn:1:calculate"]
    assert [call.name for call in tool_calls] == ["echo", "calculate"]
    assert [call.arguments for call in tool_calls] == [
        {"value": "first"},
        {"n": 2},
    ]
    assert [result.tool_call_id for result in tool_results] == [
        "given",
        "turn:1:calculate",
    ]
    assert [result.output for result in tool_results] == ["one", "two"]
    assert all(result.error is None for result in tool_results)
    assert all(call.mcp_provenance is None for call in tool_calls)


def test_mixed_mcp_and_native_records_keep_correlated_safe_facts() -> None:
    facts = _facts(status="failed", failure_code="tool_error")
    calls = (
        ToolInput("native", {"safe": True}, "native result"),
        ToolInput("mcp_peer_read", {}, "é", "mcp-call", facts),
    )
    provenance = validate_transcript_tool_provenance("turn", calls, 2)
    assert provenance[0] is None
    correlated = provenance[1]
    assert correlated is not None
    assert correlated is not facts
    assert correlated.transcript_correlation_id == "turn"
    assert facts.transcript_correlation_id is None

    tool_calls, tool_results = build_transcript_tool_records("turn", calls, provenance)
    assert [call.id for call in tool_calls] == ["turn:0:native", "mcp-call"]
    assert tool_calls[1].arguments == {}
    assert tool_calls[1].mcp_provenance == provenance[1]
    assert tool_results[1].tool_call_id == "mcp-call"
    assert tool_results[1].output == "é"
    assert tool_results[1].error == "tool_error"
    assert tool_results[1].mcp_provenance == provenance[1]


@pytest.mark.parametrize(
    "change",
    (
        "raw_arguments",
        "call_id",
        "name",
        "not_checked",
        "wrong_size",
        "over_limit",
        "wrong_correlation",
    ),
)
def test_unsafe_mcp_preflight_keeps_exact_failure_message(change: str) -> None:
    facts = _facts()
    call = ToolInput("mcp_peer_read", {}, "é", "mcp-call", facts)
    limit = 2
    if change == "raw_arguments":
        call = replace(call, arguments={"secret": "raw"})
    elif change == "call_id":
        call = replace(call, call_id="different")
    elif change == "name":
        call = replace(call, name="different")
    elif change == "not_checked":
        call = replace(
            call,
            mcp_provenance=facts.model_copy(
                update={"output_sanitization_state": "not_checked"}
            ),
        )
    elif change == "wrong_size":
        call = replace(
            call,
            mcp_provenance=facts.model_copy(update={"model_result_size_bytes": 1}),
        )
    elif change == "over_limit":
        limit = 1
    elif change == "wrong_correlation":
        call = replace(
            call,
            mcp_provenance=facts.model_copy(
                update={"transcript_correlation_id": "other"}
            ),
        )

    with pytest.raises(ValueError) as caught:
        validate_transcript_tool_provenance("turn", (call,), limit)
    assert str(caught.value) == (
        "MCP transcript requires safe, bounded, correlated records"
    )


def test_invalid_turn_correlation_keeps_distinct_failure_message() -> None:
    call = ToolInput("mcp_peer_read", {}, "é", "mcp-call", _facts())
    with pytest.raises(ValueError) as caught:
        validate_transcript_tool_provenance("bad/id", (call,), 2)
    assert str(caught.value) == "Invalid MCP transcript correlation"


def test_runtime_import_does_not_load_chat_or_cli() -> None:
    code = """
import builtins
import sys
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name.startswith(('friday_chat', 'friday_cli')):
        raise RuntimeError(name)
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
from friday_runtime.transcript_tool_records import (
    build_transcript_tool_records,
    validate_transcript_tool_provenance,
)
assert build_transcript_tool_records('turn', (), ()) == ([], [])
assert validate_transcript_tool_provenance('turn', (), 0) == []
assert not any(name.startswith(('friday_chat', 'friday_cli')) for name in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
