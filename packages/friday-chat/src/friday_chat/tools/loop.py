"""Function-calling tool loop for FridayV2."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from friday_chat.display import HeartbeatFactory, NoopHeartbeatFactory
from friday_chat.tools.registry import FakeToolRegistry
from friday_chat.tools.schemas import ToolCallRecord, ToolDefinition


class ToolCallRegistry(Protocol):
    """Registry operations required by the tool loop."""

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute one named tool."""


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
    ) -> ToolLoopResult:
        """Run deterministic fake function calls found in supplied messages."""
        allowed = {tool.name for tool in tool_schemas}
        consecutive_failures = 0
        executed: list[ToolCallRecord] = []
        circuit_breaker_open = False
        reasoning_content: list[str] = []

        for message in messages[: self._max_iterations]:
            heartbeat = self._heartbeat_factory.create_heartbeat("tool")
            try:
                heartbeat.start()
                reasoning = message.get("reasoning_content")
                if isinstance(reasoning, str):
                    reasoning_content.append(reasoning)
                for call in _extract_tool_calls(message):
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
                        result = await self._registry.call_tool(name, arguments)
                    except KeyError:
                        consecutive_failures += 1
                        if consecutive_failures >= self._max_iterations:
                            circuit_breaker_open = True
                            break
                        continue
                    executed.append(
                        ToolCallRecord(
                            name=name,
                            arguments=arguments,
                            result=result,
                            call_id=(
                                str(call["id"])
                                if call.get("id") is not None
                                else None
                            ),
                        )
                    )
                    consecutive_failures = 0
                if circuit_breaker_open:
                    break
            finally:
                heartbeat.stop()

        return ToolLoopResult(
            messages=list(messages),
            tool_calls=executed,
            iterations=len(executed),
            circuit_breaker_open=circuit_breaker_open,
            token_usage=_estimate_token_usage(messages, executed),
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
