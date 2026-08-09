"""Gate E regressions for unified tool selection and schema budgeting."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping, Sequence
from dataclasses import FrozenInstanceError, dataclass, field
from types import SimpleNamespace
from typing import Any, cast

import pytest
from friday_chat.adapters import FrameworkMemoryAdapter
from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.commands.contracts import CommandMetadata
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.commands.tools import (
    clear_tools_handler,
    inject_tools_handler,
    tool_budget_handler,
)
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeMemoryController, FakeToolRegistry, build_runtime
from friday_chat.tools.schemas import ToolCallRecord, ToolDefinition
from friday_chat.tools.selection import (
    ToolRejectionReason,
    ToolSelectionError,
    ToolSelectionMode,
    ToolSelectionState,
    canonical_tool_schema_bytes,
)
from friday_chat.turns.models import ChatModelResponse
from friday_chat.turns.processor import TurnProcessor, TurnResult


def _config(
    *,
    enabled: bool = True,
    max_tools: int = 20,
    ratio: float = 1.0,
    context_window: int = 4096,
    output_buffer: int = 0,
    include_in_context: bool = False,
) -> FridayChatConfig:
    return FridayChatConfig.model_validate(
        {
            "llm": {"model": "fake/gate-e"},
            "memory": {
                "context_window": context_window,
                "output_buffer": output_buffer,
            },
            "tools": {
                "enabled": enabled,
                "context": {
                    "include_in_context": include_in_context,
                    "max_tools": max_tools,
                    "max_budget_ratio": ratio,
                    "recommendation_threshold": 0.5,
                },
            },
        }
    )


def _tool(
    name: str,
    *,
    description: str | None = None,
    category: str = "utility",
    padding: int = 0,
) -> ToolDefinition:
    return ToolDefinition(
        name=name,
        description=description or f"Use {name} deterministically.",
        input_schema={
            "type": "object",
            "properties": {
                "value": {
                    "type": "string",
                    "description": "x" * padding,
                }
            },
        },
        category=category,
    )


def _metadata() -> CommandMetadata:
    return CommandMetadata(
        name="inject-tools",
        description="test",
        category="tools",
        usage="/inject-tools <names>",
    )


@dataclass
class SchemaRecordingModel:
    """Provider-free model recording the exact definitions bound per call."""

    responses: list[ChatModelResponse] = field(default_factory=list)
    tool_calls: list[tuple[ToolDefinition, ...]] = field(default_factory=list)

    async def complete(
        self,
        _messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ChatModelResponse:
        definitions = tuple(tools)
        self.tool_calls.append(definitions)
        if self.responses:
            return self.responses.pop(0)
        return ChatModelResponse.from_text("deterministic response")

    async def stream_complete(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> AsyncIterator[str]:
        response = await self.complete(messages, tools=tools)
        yield response.content


def test_manual_injection_is_atomic_for_unknown_count_and_token_failures() -> None:
    first = _tool("first")
    second = _tool("second", padding=100)
    first_tokens = (len(canonical_tool_schema_bytes((first,))) + 3) // 4
    config = _config(max_tools=2, context_window=first_tokens, output_buffer=0)
    state = ToolSelectionState(config, (first, second))

    exact = state.inject_manual(("first",))
    assert exact.schema_tokens == exact.maximum_schema_tokens
    assert state.manual_names == ("first",)

    with pytest.raises(ToolSelectionError) as unknown:
        state.inject_manual(("missing",))
    assert unknown.value.reason is ToolRejectionReason.UNKNOWN_TOOL
    assert state.manual_names == ("first",)

    with pytest.raises(ToolSelectionError) as token_overflow:
        state.inject_manual(("first", "second"))
    assert token_overflow.value.reason is ToolRejectionReason.TOKEN_LIMIT
    assert state.manual_names == ("first",)

    count_state = ToolSelectionState(
        _config(max_tools=1),
        (first, second),
    )
    count_state.inject_manual(("first",))
    with pytest.raises(ToolSelectionError) as count_overflow:
        count_state.inject_manual(("first", "second"))
    assert count_overflow.value.reason is ToolRejectionReason.COUNT_LIMIT
    assert count_state.manual_names == ("first",)


def test_exact_boundary_and_one_token_overflow_are_deterministic() -> None:
    tool = _tool("boundary", padding=17)
    required = (len(canonical_tool_schema_bytes((tool,))) + 3) // 4

    exact_state = ToolSelectionState(
        _config(context_window=required, output_buffer=0),
        (tool,),
    )
    exact = exact_state.inject_manual((tool.name,))
    assert exact.schema_tokens == required
    assert exact.maximum_schema_tokens == required

    overflow_state = ToolSelectionState(
        _config(context_window=required - 1, output_buffer=0),
        (tool,),
    )
    with pytest.raises(ToolSelectionError) as overflow:
        overflow_state.inject_manual((tool.name,))
    assert overflow.value.reason is ToolRejectionReason.TOKEN_LIMIT
    automatic = overflow_state.select_for_turn("boundary")
    assert automatic.definitions == ()
    assert len(automatic.budget.rejections) == 1
    assert automatic.budget.rejections[0].name == tool.name
    assert automatic.budget.rejections[0].reason is ToolRejectionReason.TOKEN_LIMIT


def test_automatic_and_manual_ordering_are_deterministic() -> None:
    tools = (_tool("beta"), _tool("alpha"), _tool("gamma"))
    state = ToolSelectionState(_config(max_tools=2), tools)

    first = state.select_for_turn("unmatched query")
    second = state.select_for_turn("unmatched query")

    assert first.budget.selected_names == ("beta", "alpha")
    assert second.budget == first.budget
    assert [(item.name, item.reason) for item in first.budget.rejections] == [
        ("gamma", ToolRejectionReason.COUNT_LIMIT)
    ]

    manual = state.inject_manual(("alpha", "beta"))
    assert manual.selected_names == ("alpha", "beta")
    assert state.select_for_turn("gamma").budget.selected_names == (
        "alpha",
        "beta",
    )


async def test_manual_mode_persists_exact_set_until_clear_restores_automatic() -> None:
    runtime = build_runtime(_config(include_in_context=True))
    model = SchemaRecordingModel()
    runtime.chat_llm = model
    registry = build_default_registry()
    command_context = RegistryCommandContext(runtime=runtime, registry=registry)

    handled, injected = await registry.execute("/inject-tools echo", command_context)
    assert handled is True
    assert injected is not None
    first = await TurnProcessor(runtime).process("What date is it?")
    second = await TurnProcessor(runtime).process("remember this note")
    await registry.execute("/clear-tools", command_context)
    automatic = await TurnProcessor(runtime).process("What date is it?")

    assert first.selected_tool_names == ("echo",)
    assert second.selected_tool_names == ("echo",)
    assert "- echo:" in first.context
    assert "get_current_datetime" not in first.context
    assert "remember" not in first.context
    assert model.tool_calls[:2] == [(runtime.tools.list_tools()[0],)] * 2
    assert automatic.selected_tool_names == ("get_current_datetime",)
    assert runtime.tool_selection.mode is ToolSelectionMode.AUTOMATIC


async def test_turn_snapshot_matches_model_bytes_and_all_budget_consumers() -> None:
    runtime = build_runtime(
        _config(context_window=1000, output_buffer=100, include_in_context=True)
    )
    model = SchemaRecordingModel()
    runtime.chat_llm = model

    result = await TurnProcessor(runtime).process("echo this")

    assert result.tool_budget_snapshot is not None
    snapshot = result.tool_budget_snapshot
    assert snapshot.schema_bytes == canonical_tool_schema_bytes(model.tool_calls[0])
    assert snapshot.selected_names == tuple(tool.name for tool in model.tool_calls[0])
    assert result.selected_tool_names == snapshot.selected_names
    assert result.tool_schema_tokens == snapshot.schema_tokens
    assert result.budget_status is not None
    assert result.budget_status.tool_tokens == snapshot.schema_tokens
    assert result.context_budget_tokens == (
        snapshot.available_context_tokens
        - max(1, len(runtime.config.chat.system_prompt) // 4)
        - snapshot.schema_tokens
    )
    mutation_attempt: Any = snapshot
    with pytest.raises(FrozenInstanceError):
        mutation_attempt.schema_tokens = 0


async def test_provider_responses_do_not_change_schema_budget() -> None:
    echo = _tool("echo")

    async def run(response_text: str) -> tuple[bytes, int]:
        runtime = build_runtime(_config())
        runtime.tools = FakeToolRegistry((echo,))
        runtime.chat_llm = SchemaRecordingModel(
            responses=[ChatModelResponse.from_text(response_text)]
        )
        turn = await TurnProcessor(runtime).process("echo value")
        assert runtime.tools.calls == []
        assert runtime.tool_selection.last_executed_names == ()
        assert turn.tool_budget_snapshot is not None
        return turn.tool_budget_snapshot.schema_bytes, turn.tool_schema_tokens

    short = await run("brief provider response")
    long = await run("provider response " + "y" * 10000)
    assert short == long


def test_tool_execution_result_payloads_are_not_schema_budget_inputs() -> None:
    echo = _tool("echo")
    state = ToolSelectionState(_config(), (echo,))
    selection = state.select_for_turn("echo value")
    short_record = ToolCallRecord(name="echo", arguments={}, result="short")
    long_record = ToolCallRecord(name="echo", arguments={}, result="x" * 10000)

    short_result = TurnResult(
        user_message="echo value",
        assistant_message="done",
        retrieved_memory_count=0,
        tool_context_injected=False,
        tool_schema_tokens=selection.budget.schema_tokens,
        selected_tool_names=selection.budget.selected_names,
        tool_budget_snapshot=selection.budget,
        tool_calls=(short_record,),
    )
    long_result = TurnResult(
        user_message="echo value",
        assistant_message="done",
        retrieved_memory_count=0,
        tool_context_injected=False,
        tool_schema_tokens=selection.budget.schema_tokens,
        selected_tool_names=selection.budget.selected_names,
        tool_budget_snapshot=selection.budget,
        tool_calls=(long_record,),
    )

    assert short_result.tool_budget_snapshot is long_result.tool_budget_snapshot
    assert short_result.tool_schema_tokens == long_result.tool_schema_tokens
    assert selection.budget.schema_bytes == canonical_tool_schema_bytes((echo,))


async def test_tool_budget_reports_no_turn_manual_selected_and_executed_states() -> (
    None
):
    runtime = build_runtime(_config())
    registry = build_default_registry()
    context = RegistryCommandContext(runtime=runtime, registry=registry)

    before = await tool_budget_handler(context, (), _metadata())
    await inject_tools_handler(context, ("echo",), _metadata())
    manual = await tool_budget_handler(context, (), _metadata())

    runtime.chat_llm = SchemaRecordingModel()
    turn = await TurnProcessor(runtime).process("unrelated request")
    after = await tool_budget_handler(context, (), _metadata())

    assert "mode: automatic" in before.output
    assert "estimate_source: automatic_pre_turn" in before.output
    assert "last_selected: not yet selected" in before.output
    assert "mode: manual" in manual.output
    assert "pending_manual: 1 (echo)" in manual.output
    assert "estimate_source: pending_manual" in manual.output
    assert "last_selected: not yet selected" in manual.output
    assert turn.selected_tool_names == ("echo",)
    assert "last_completed_mode: manual" in after.output
    assert "last_selected: 1 (echo)" in after.output
    assert "executed: none" in after.output
    assert f"last_schema_tokens: {turn.tool_schema_tokens}" in after.output


async def test_clear_uses_prior_automatic_estimate_and_keeps_last_manual_turn() -> None:
    automatic_tool = _tool(
        "automatic_tool",
        description="Use the automatic tool for an automatic request.",
    )
    manual_tool = _tool(
        "manual_tool",
        description="Use the manual tool only when manually selected.",
        padding=500,
    )
    runtime = build_runtime(_config())
    runtime.tools = FakeToolRegistry((automatic_tool, manual_tool))
    runtime.chat_llm = SchemaRecordingModel()
    processor = TurnProcessor(runtime)
    context = RegistryCommandContext(runtime=runtime)

    automatic_turn = await processor.process("automatic request")
    await inject_tools_handler(context, ("manual_tool",), _metadata())
    manual_turn = await processor.process("automatic request")
    await clear_tools_handler(context, (), _metadata())
    output = (await tool_budget_handler(context, (), _metadata())).output

    assert automatic_turn.selected_tool_names == ("automatic_tool",)
    assert manual_turn.selected_tool_names == ("manual_tool",)
    assert automatic_turn.tool_schema_tokens != manual_turn.tool_schema_tokens
    assert runtime.tool_selection.last_automatic_snapshot is (
        automatic_turn.tool_budget_snapshot
    )
    assert runtime.tool_selection.last_turn_snapshot is manual_turn.tool_budget_snapshot
    assert "mode: automatic" in output
    assert "pending_manual: none" in output
    assert "estimate_source: last_automatic" in output
    assert "automatic_selected: 1 (automatic_tool)" in output
    assert f"automatic_schema_tokens: {automatic_turn.tool_schema_tokens}" in output
    assert f"estimated_schema_tokens: {automatic_turn.tool_schema_tokens}" in output
    assert "last_completed_mode: manual" in output
    assert "last_selected: 1 (manual_tool)" in output
    assert f"last_schema_tokens: {manual_turn.tool_schema_tokens}" in output


async def test_clear_without_prior_automatic_turn_reports_honest_pre_turn_state() -> (
    None
):
    manual_tool = _tool("manual_tool", padding=500)
    runtime = build_runtime(_config())
    runtime.tools = FakeToolRegistry((manual_tool,))
    runtime.chat_llm = SchemaRecordingModel()
    context = RegistryCommandContext(runtime=runtime)

    await inject_tools_handler(context, ("manual_tool",), _metadata())
    manual_turn = await TurnProcessor(runtime).process("anything")
    await clear_tools_handler(context, (), _metadata())
    output = (await tool_budget_handler(context, (), _metadata())).output

    assert runtime.tool_selection.last_automatic_snapshot is None
    assert runtime.tool_selection.last_turn_snapshot is manual_turn.tool_budget_snapshot
    assert "mode: automatic" in output
    assert "pending_manual: none" in output
    assert "estimate_source: automatic_pre_turn" in output
    assert "automatic_selected: not yet selected" in output
    assert "automatic_schema_tokens: not available" in output
    assert "estimated_schema_tokens: 0" in output
    assert "utilization_pct: 0.0" in output
    assert "last_completed_mode: manual" in output
    assert "last_selected: 1 (manual_tool)" in output
    assert f"last_schema_tokens: {manual_turn.tool_schema_tokens}" in output


async def test_disabled_and_empty_registries_offer_zero_schemas() -> None:
    disabled = build_runtime(_config(enabled=False))
    disabled_result = await TurnProcessor(disabled).process("echo")
    disabled_budget = await tool_budget_handler(
        RegistryCommandContext(runtime=disabled),
        (),
        _metadata(),
    )
    assert disabled_result.selected_tool_names == ()
    assert disabled_result.tool_schema_tokens == 0
    assert disabled_result.tool_budget_snapshot is not None
    assert disabled_result.tool_budget_snapshot.mode is ToolSelectionMode.DISABLED
    assert "mode: disabled" in disabled_budget.output
    assert "estimated_schema_tokens: 0" in disabled_budget.output

    empty = build_runtime(_config())
    empty.tools = FakeToolRegistry(())
    empty_result = await TurnProcessor(empty).process("echo")
    empty_budget = await tool_budget_handler(
        RegistryCommandContext(runtime=empty),
        (),
        _metadata(),
    )
    assert empty_result.selected_tool_names == ()
    assert empty_result.tool_schema_tokens == 0
    assert empty_result.tool_budget_snapshot is not None
    assert empty_result.tool_budget_snapshot.schema_bytes == b""
    assert "registered: none" in empty_budget.output


async def test_zero_output_buffer_and_tiny_context_reach_retrieval_exactly() -> None:
    runtime = build_runtime(_config(enabled=False, context_window=1, output_buffer=0))
    assert isinstance(runtime.memory, FakeMemoryController)

    result = await TurnProcessor(runtime).process("tiny")

    assert result.tool_budget_snapshot is not None
    assert result.tool_budget_snapshot.available_context_tokens == 1
    assert result.context_budget_tokens == 0
    assert result.budget_status is not None
    assert result.budget_status.available_budget == 1
    assert runtime.memory.retrieval_token_limits == [0]


async def test_framework_adapter_preserves_explicit_zero_token_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = cast(
        FrameworkMemoryAdapter,
        object.__new__(FrameworkMemoryAdapter),
    )
    adapter.config = _config(enabled=False)
    captured: list[int] = []

    async def recording_recall(
        _query: str,
        *,
        token_limit: int,
    ) -> SimpleNamespace:
        captured.append(token_limit)
        return SimpleNamespace(history=[], passages=[], insights=[])

    monkeypatch.setattr(adapter, "_recall", recording_recall)
    assert await adapter.retrieve("zero", token_limit=0) == []
    assert captured == [0]


async def test_command_display_sanitizes_and_bounds_untrusted_tool_metadata() -> None:
    unsafe_name = "unsafe\x1b[31m" + "n" * 200
    unsafe_category = "category\n\x1b[2J" + "c" * 200
    tool = _tool(unsafe_name, category=unsafe_category)
    runtime = build_runtime(_config())
    runtime.tools = FakeToolRegistry((tool,))
    context = RegistryCommandContext(runtime=runtime)

    injected = await inject_tools_handler(context, (unsafe_name,), _metadata())
    selection = runtime.tool_selection.select_for_turn("anything")
    runtime.tool_selection.record_completed_turn(selection.budget, (unsafe_name,))
    budget = await tool_budget_handler(context, (), _metadata())
    rejected = await inject_tools_handler(
        context,
        ("missing\x1b[31m" + "z" * 10000,),
        _metadata(),
    )

    combined_output = injected.output + budget.output + rejected.output
    assert "\x1b" not in combined_output
    assert "\n\x1b[2J" not in combined_output
    assert len(rejected.output) < 300
    assert "- executed: 1 (" in budget.output
    assert selection.budget.selected_names == (unsafe_name,)
    assert selection.budget.selected_categories == (unsafe_category,)
    assert selection.budget.schema_bytes == canonical_tool_schema_bytes((tool,))
    assert runtime.tool_selection.manual_names == (unsafe_name,)


async def test_app_retains_the_latest_immutable_tool_budget_snapshot() -> None:
    runtime = build_runtime(_config())
    runtime.chat_llm = SchemaRecordingModel()
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["echo the provided text"]),
        output_sink=ListOutputSink(),
    )

    result = await app.run()

    assert result.turns_processed == 1
    snapshot = app.command_context.last_tool_budget_snapshot
    assert snapshot is runtime.tool_selection.last_turn_snapshot
    assert snapshot is not None
    assert snapshot.selected_names == ("echo",)
