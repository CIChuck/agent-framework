"""Tool command tests for FridayV2."""

from __future__ import annotations

from typing import Any

from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.display import Heartbeat, HeartbeatKind
from friday_chat.runtime import build_runtime
from friday_chat.tools.loop import ToolLoop, prune_tool_message_pairs


def _context(*, max_tool_result_chars: int = 50000) -> RegistryCommandContext:
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "openai/test-chat-model"},
            "tools": {
                "loop": {"max_tool_result_chars": max_tool_result_chars},
                "context": {"max_budget_ratio": 0.25},
            },
        }
    )
    registry = build_default_registry()
    return RegistryCommandContext(
        runtime=build_runtime(config),
        registry=registry,
    )


class RecordingHeartbeat:
    """Heartbeat that records starts and stops."""

    def __init__(self, events: list[str], kind: HeartbeatKind) -> None:
        self._events = events
        self._kind = kind

    def start(self) -> None:
        self._events.append(f"{self._kind}:start")

    def stop(self) -> None:
        self._events.append(f"{self._kind}:stop")


class RecordingHeartbeatFactory:
    """Heartbeat factory for tool-loop tests."""

    def __init__(self) -> None:
        self.events: list[str] = []

    def create_heartbeat(self, kind: HeartbeatKind) -> Heartbeat:
        return RecordingHeartbeat(self.events, kind)


async def test_tools_command_lists_and_filters_by_category() -> None:
    registry = build_default_registry()
    context = _context()

    _, all_tools = await registry.execute("/tools", context)
    _, utility_tools = await registry.execute("/tools utility", context)
    _, missing_tools = await registry.execute("/tools finance", context)

    assert all_tools is not None
    assert "[utility]" in all_tools.output
    assert "[memory]" in all_tools.output
    assert utility_tools is not None
    assert "echo" in utility_tools.output
    assert "remember" not in utility_tools.output
    assert missing_tools is not None
    assert "Available categories: memory, utility" in missing_tools.output














async def test_tool_loop_executes_explicit_function_call_records() -> None:
    context = _context()
    assert context.runtime is not None
    tool_loop = ToolLoop(context.runtime.tools)

    result = await tool_loop.run(
        messages=[
            {"tool_calls": [{"name": "echo", "arguments": {"text": "hello"}}]},
        ],
        tool_schemas=context.runtime.tools.list_tools(),
    )

    assert result.iterations == 1
    assert result.tool_calls[0].name == "echo"
    assert result.tool_calls[0].result == "hello"
    assert result.token_usage["total_tokens"] >= result.token_usage["completion_tokens"]
    assert result.circuit_breaker_open is False


async def test_tool_loop_preserves_reasoning_content() -> None:
    context = _context()
    assert context.runtime is not None
    tool_loop = ToolLoop(context.runtime.tools)

    result = await tool_loop.run(
        messages=[
            {
                "reasoning_content": "Need to echo.",
                "tool_calls": [{"name": "echo", "arguments": {"text": "hello"}}],
            },
        ],
        tool_schemas=context.runtime.tools.list_tools(),
    )

    assert result.reasoning_content == ["Need to echo."]


async def test_tool_loop_uses_tool_processing_heartbeats() -> None:
    context = _context()
    assert context.runtime is not None
    heartbeat_factory = RecordingHeartbeatFactory()
    tool_loop = ToolLoop(
        context.runtime.tools,
        max_iterations=2,
        heartbeat_factory=heartbeat_factory,
    )

    await tool_loop.run(
        messages=[
            {"tool_calls": [{"name": "echo", "arguments": {"text": "first"}}]},
            {"tool_calls": [{"name": "echo", "arguments": {"text": "second"}}]},
        ],
        tool_schemas=context.runtime.tools.list_tools(),
    )

    assert heartbeat_factory.events == [
        "tool:start",
        "tool:stop",
        "tool:start",
        "tool:stop",
    ]


async def test_tool_loop_circuit_breaker_for_unknown_tool() -> None:
    context = _context()
    assert context.runtime is not None
    tool_loop = ToolLoop(context.runtime.tools, max_iterations=1)

    result = await tool_loop.run(
        messages=[
            {"tool_calls": [{"name": "missing", "arguments": {}}]},
        ],
        tool_schemas=context.runtime.tools.list_tools(),
    )

    assert result.tool_calls == []
    assert result.circuit_breaker_open is True


def test_tool_message_pruning_preserves_assistant_tool_pairs() -> None:
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": "old"},
        {"role": "assistant", "content": "", "tool_calls": [{"name": "echo"}]},
        {"role": "tool", "content": "old result"},
        {"role": "user", "content": "new"},
    ]

    pruned = prune_tool_message_pairs(messages, max_messages=3)

    assert pruned == messages[1:]
