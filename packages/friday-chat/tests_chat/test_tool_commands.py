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
                "context": {"max_schema_budget_percent": 12},
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


async def test_run_tool_supports_json_and_plain_text_parameters() -> None:
    registry = build_default_registry()
    context = _context()

    _, json_result = await registry.execute('/run-tool echo {"text": "hello"}', context)
    _, plain_result = await registry.execute("/run-tool remember durable note", context)

    assert json_result is not None
    assert json_result.output == "Tool echo result:\nhello"
    assert plain_result is not None
    assert "remembered: durable note" in plain_result.output


async def test_run_tool_validation_errors_are_user_facing() -> None:
    registry = build_default_registry()
    context = _context()

    _, unknown = await registry.execute("/run-tool missing {}", context)
    _, invalid_json = await registry.execute("/run-tool echo {not-json", context)
    _, missing_required = await registry.execute("/run-tool echo {}", context)
    _, no_runtime = await registry.execute("/run-tool echo hi", RegistryCommandContext())

    assert unknown is not None
    assert "Unknown tool: missing" in unknown.output
    assert invalid_json is not None
    assert "Invalid JSON parameters" in invalid_json.output
    assert missing_required is not None
    assert missing_required.output == "Missing required parameters for echo: text"
    assert no_runtime is not None
    assert no_runtime.output == "Error: Tool registry not initialized."


async def test_tool_sanitization_updates_security_stats() -> None:
    registry = build_default_registry()
    context = _context()

    _, result = await registry.execute(
        "/run-tool echo <script>alert(1)</script>",
        context,
    )

    assert result is not None
    assert "&lt;script&gt;" in result.output
    assert context.security_stats == {
        "total_scans": 1,
        "detections": 1,
        "blocked": 1,
        "patterns_seen": 1,
    }
    assert "<script" not in context.tool_results[0]


async def test_tool_result_truncation_lifecycle_and_ingestion_tracking() -> None:
    registry = build_default_registry()
    context = _context(max_tool_result_chars=5)

    _, result = await registry.execute(
        '/run-tool echo {"text": "hello world", "path": "/tmp/source.txt"}',
        context,
    )

    assert result is not None
    assert "hello\n[truncated]" in result.output
    assert context.tool_results == ["hello world"]
    assert context.tool_lifecycle_records == ["echo"]
    assert context.tool_ingestions == ["/tmp/source.txt"]


async def test_inject_clear_and_tool_budget_commands() -> None:
    registry = build_default_registry()
    context = _context()

    _, inject_result = await registry.execute("/inject-tools echo missing", context)
    _, budget_result = await registry.execute("/tool-budget", context)
    _, clear_result = await registry.execute("/clear-tools", context)
    _, cleared_budget = await registry.execute("/tool-budget", context)

    assert inject_result is not None
    assert "- echo (utility)" in inject_result.output
    assert "Missing tools: missing" in inject_result.output
    assert budget_result is not None
    assert "active_tools: 1" in budget_result.output
    assert "budget_limit_percent: 12" in budget_result.output
    assert clear_result is not None
    assert clear_result.output == "Cleared injected tools."
    assert cleared_budget is not None
    assert cleared_budget.output == "No active tools injected."


async def test_recommend_tools_returns_scored_results() -> None:
    registry = build_default_registry()
    context = _context()

    _, result = await registry.execute("/recommend-tools record memory note", context)

    assert result is not None
    assert result.output.startswith("Recommended tools:")
    assert "remember" in result.output
    assert "score=" in result.output


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
