"""Function-calling tool loop for FridayV2."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from friday_chat.display import HeartbeatFactory, NoopHeartbeatFactory
from friday_chat.tools.output import redact_tool_request_message
from friday_chat.tools.registry import FakeToolRegistry
from friday_chat.tools.schemas import ToolCallRecord, ToolDefinition


class ToolCallRegistry(Protocol):
    """Registry operations required by the tool loop."""

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute one named tool."""


@runtime_checkable
class RecordingToolCallRegistry(Protocol):
    """Optional atomic recording boundary; native/fake registries need not add it."""

    def is_mcp_tool(self, name: str) -> bool: ...

    async def call_tool_record(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        call_id: str | None = None,
        used_call_ids: set[str] | None = None,
    ) -> ToolCallRecord: ...


@dataclass
class ToolLoopResult:
    """Result from one deterministic FridayV2 tool-loop pass."""

    messages: list[Mapping[str, Any]]
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    iterations: int = 0
    circuit_breaker_open: bool = False
    token_usage: dict[str, int] = field(default_factory=dict)
    reasoning_content: list[str] = field(default_factory=list)


class ToolLoop:
    """Small fake-compatible tool loop used until real runtime wiring lands."""

    def __init__(
        self,
        registry: ToolCallRegistry | None = None,
        *,
        max_iterations: int = 1,
        heartbeat_factory: HeartbeatFactory | None = None,
    ) -> None:
        self._registry = registry or FakeToolRegistry()
        self._max_iterations = max_iterations
        self._heartbeat_factory = heartbeat_factory or NoopHeartbeatFactory()

    async def run(
        self,
        messages: Sequence[Mapping[str, Any]],
        tool_schemas: Sequence[ToolDefinition],
        *,
        used_call_ids: set[str] | None = None,
        mcp_tool_names: frozenset[str] = frozenset(),
    ) -> ToolLoopResult:
        """Run deterministic fake function calls found in supplied messages."""
        allowed = {tool.name for tool in tool_schemas}
        consecutive_failures = 0
        executed: list[ToolCallRecord] = []
        circuit_breaker_open = False
        reasoning_content: list[str] = []
        identifiers = used_call_ids if used_call_ids is not None else set()
        recorder = (
            self._registry
            if isinstance(self._registry, RecordingToolCallRegistry)
            else None
        )
        request_names = {
            call["name"]
            for message in messages
            for call in _extract_tool_calls(message)
            if isinstance(call.get("name"), str)
        }
        mcp_names = {
            name
            for name in allowed | request_names
            if recorder and recorder.is_mcp_tool(name)
        }
        mcp_names.update(mcp_tool_names)
        # Every supplied response is already known here. Reserve native IDs
        # across the entire pass before executing any MCP call.
        identifiers.update(
            str(call["id"])
            for message in messages
            for call in _extract_tool_calls(message)
            if call.get("id") is not None
            and (
                not isinstance(call.get("name"), str)
                or call.get("name") not in mcp_names
            )
        )
        safe_messages: list[Mapping[str, Any]] = [
            redact_tool_request_message(message, (), mcp_names) for message in messages
        ]

        for index, message in enumerate(messages[: self._max_iterations]):
            message_records: list[ToolCallRecord] = []
            calls = _extract_tool_calls(message)
            heartbeat = self._heartbeat_factory.create_heartbeat("tool")
            try:
                heartbeat.start()
                reasoning = message.get("reasoning_content")
                if isinstance(reasoning, str) and not any(
                    isinstance(call.get("name"), str) and call.get("name") in mcp_names
                    for call in calls
                ):
                    reasoning_content.append(reasoning)
                for call in calls:
                    name = call.get("name")
                    arguments = call.get("arguments", {})
                    if not isinstance(name, str) or name not in allowed:
                        consecutive_failures += 1
                        if consecutive_failures >= self._max_iterations:
                            circuit_breaker_open = True
                            break
                        continue
                    if not isinstance(arguments, dict):
                        arguments = {}
                    try:
                        raw_id = call.get("id")
                        identifier = (
                            raw_id
                            if isinstance(raw_id, str)
                            else (
                                None
                                if name in mcp_names or raw_id is None
                                else str(raw_id)
                            )
                        )
                        if recorder is not None:
                            record = await recorder.call_tool_record(
                                name,
                                arguments,
                                call_id=identifier,
                                used_call_ids=identifiers,
                            )
                        else:
                            result = await self._registry.call_tool(name, arguments)
                            record = ToolCallRecord(name, arguments, result, identifier)
                        if name in mcp_names and (
                            record.mcp_provenance is None
                            or record.arguments
                            or record.name != name
                            or record.call_id != record.mcp_provenance.call_id
                            or record.mcp_provenance.tool.canonical_name != name
                            or record.mcp_provenance.output_sanitization_state
                            == "not_checked"
                            or record.mcp_provenance.model_result_size_bytes
                            != len(record.result.encode("utf-8"))
                        ):
                            raise RuntimeError(
                                "MCP execution requires checked per-call provenance"
                            )
                    except KeyError:
                        consecutive_failures += 1
                        if consecutive_failures >= self._max_iterations:
                            circuit_breaker_open = True
                            break
                        continue
                    executed.append(record)
                    message_records.append(record)
                    consecutive_failures = 0
                if circuit_breaker_open:
                    break
            finally:
                heartbeat.stop()
                safe_messages[index] = redact_tool_request_message(
                    message, message_records, mcp_names
                )

        return ToolLoopResult(
            messages=safe_messages,
            tool_calls=executed,
            iterations=len(executed),
            circuit_breaker_open=circuit_breaker_open,
            token_usage=_estimate_token_usage(safe_messages, executed),
            reasoning_content=reasoning_content,
        )


def _extract_tool_calls(message: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_calls = message.get("tool_calls", [])
    if not isinstance(raw_calls, list):
        return []
    calls: list[dict[str, Any]] = []
    for call in raw_calls:
        if not isinstance(call, dict):
            continue
        function = call.get("function")
        if isinstance(function, Mapping):
            arguments = function.get("arguments", {})
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}
            calls.append(
                {
                    "id": call.get("id"),
                    "name": function.get("name"),
                    "arguments": arguments,
                }
            )
            continue
        calls.append(call)
    return calls


def _estimate_token_usage(
    messages: Sequence[Mapping[str, Any]],
    calls: Sequence[ToolCallRecord],
) -> dict[str, int]:
    prompt_tokens = sum(len(str(message)) // 4 for message in messages)
    completion_tokens = sum(len(call.result) // 4 for call in calls)
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }


def prune_tool_message_pairs(
    messages: Sequence[Mapping[str, Any]],
    *,
    max_messages: int,
) -> list[Mapping[str, Any]]:
    """Prune messages while preserving assistant/tool result pairs."""
    if max_messages <= 0:
        return []
    if len(messages) <= max_messages:
        return list(messages)

    kept: list[Mapping[str, Any]] = []
    index = len(messages) - 1
    while index >= 0 and len(kept) < max_messages:
        message = messages[index]
        if message.get("role") == "tool" and index > 0:
            previous = messages[index - 1]
            if previous.get("tool_calls"):
                pair = [previous, message]
                available = max_messages - len(kept)
                if available >= 2:
                    kept.extend(reversed(pair))
                    index -= 2
                    continue
        kept.append(message)
        index -= 1

    return list(reversed(kept))
