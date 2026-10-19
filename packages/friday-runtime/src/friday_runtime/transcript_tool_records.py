"""UI-neutral preparation of transcript tool calls and results."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol

from friday_core.mcp import MCPToolCallProvenance
from friday_transcript import ToolCall, ToolResult

__all__ = [
    "TranscriptToolCallInput",
    "validate_transcript_tool_provenance",
    "build_transcript_tool_records",
]


class TranscriptToolCallInput(Protocol):
    """Tool facts required for a transcript record, without a frontend type."""

    @property
    def name(self) -> str: ...

    @property
    def arguments(self) -> Mapping[str, object]: ...

    @property
    def result(self) -> str: ...

    @property
    def call_id(self) -> str | None: ...

    @property
    def mcp_provenance(self) -> MCPToolCallProvenance | None: ...


def validate_transcript_tool_provenance(
    turn_id: str,
    calls: Sequence[TranscriptToolCallInput],
    max_result_bytes: int,
) -> list[MCPToolCallProvenance | None]:
    """Reject unsafe MCP facts before the caller starts a transcript write."""
    provenance: list[MCPToolCallProvenance | None] = []
    for call in calls:
        facts = call.mcp_provenance
        if facts is None:
            provenance.append(None)
            continue
        if (
            call.arguments
            or call.call_id != facts.call_id
            or call.name != facts.tool.canonical_name
            or facts.output_sanitization_state == "not_checked"
            or facts.model_result_size_bytes != len(call.result.encode("utf-8"))
            or len(call.result.encode("utf-8")) > max_result_bytes
            or facts.transcript_correlation_id not in {None, turn_id}
        ):
            raise ValueError(
                "MCP transcript requires safe, bounded, correlated records"
            )
        try:
            correlated = MCPToolCallProvenance.model_validate(
                {
                    **facts.model_dump(),
                    "transcript_correlation_id": turn_id,
                }
            )
        except ValueError:
            raise ValueError("Invalid MCP transcript correlation") from None
        provenance.append(correlated)
    return provenance


def build_transcript_tool_records(
    turn_id: str,
    calls: Sequence[TranscriptToolCallInput],
    provenance: Sequence[MCPToolCallProvenance | None],
) -> tuple[list[ToolCall], list[ToolResult]]:
    """Construct models after the caller has established session and turn order."""
    tool_call_ids = [
        call.call_id or f"{turn_id}:{index}:{call.name}"
        for index, call in enumerate(calls)
    ]
    tool_calls = [
        ToolCall(
            id=tool_call_ids[index],
            name=call.name,
            arguments=dict(call.arguments),
            mcp_provenance=provenance[index],
        )
        for index, call in enumerate(calls)
    ]
    tool_results = [
        ToolResult(
            tool_call_id=tool_call_ids[index],
            output=call.result,
            error=(
                facts.failure_code if (facts := provenance[index]) is not None else None
            ),
            mcp_provenance=provenance[index],
        )
        for index, call in enumerate(calls)
    ]
    return tool_calls, tool_results
