"""Session and basic memory command tests for FridayV2."""

from __future__ import annotations

from pathlib import Path

from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeMemoryController, FridayRuntime, build_runtime


def _runtime(tmp_path: Path | None = None) -> FridayRuntime:
    export_directory = str(tmp_path) if tmp_path is not None else "./exports"
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "openai/test-chat-model"},
            "memory": {
                "context_window": 1000,
                "output_buffer": 100,
                "priming": {"enabled": True, "previous_sessions": 2},
            },
            "transcript": {"export_directory": export_directory},
            "tools": {"context": {"include_in_context": True}},
        }
    )
    return build_runtime(config)


async def test_exit_alias_requests_app_shutdown() -> None:
    output = ListOutputSink()
    app = FridayChatApp(
        runtime=_runtime(),
        input_source=ListInputSource(["/q"]),
        output_sink=output,
    )

    result = await app.run()

    assert result.exit_reason == "command_exit"
    assert output.values == ["Goodbye."]


async def test_history_and_clear_commands_use_session_state() -> None:
    output = ListOutputSink()
    runtime = _runtime()
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["hello", "/history", "/clear", "/history"]),
        output_sink=output,
    )

    result = await app.run()

    assert result.turns_processed == 1
    assert "Conversation history:" in output.values[1]
    assert "User: hello" in output.values[1]
    assert output.values[2] == "Conversation history cleared."
    assert output.values[3] == "No conversation history."
    assert isinstance(runtime.memory, FakeMemoryController)
    assert runtime.memory.stored_turns == []


async def test_vars_and_set_commands() -> None:
    registry = build_default_registry()
    context = RegistryCommandContext(registry=registry)

    _, set_result = await registry.execute("/set project Friday V2", context)
    _, vars_result = await registry.execute("/vars", context)

    assert set_result is not None
    assert set_result.output == "Set project."
    assert vars_result is not None
    assert "- project: Friday V2" in vars_result.output


async def test_basic_memory_diagnostic_commands_with_fake_runtime(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    registry = build_default_registry()
    context = RegistryCommandContext(
        runtime=runtime,
        registry=registry,
        history=[("hello", "Friday: hello")],
        last_context="Context payload:\nAvailable tools:\n- echo",
        last_prompt="System: You are Friday.\nUser: hello\nFriday: hello",
        last_debug={"retrieved_memory_count": "0"},
        last_timing={"last_turn": 0.125},
    )

    command_outputs: dict[str, str] = {}
    for command in (
        "/memory",
        "/context --debug",
        "/prompt",
        "/debug",
        "/debug-budget",
        "/timing",
        "/prime",
        "/debug-retrieval hello",
        "/entities",
        "/insights",
        "/summaries",
        "/meta",
    ):
        _, result = await registry.execute(command, context)
        assert result is not None
        command_outputs[command] = result.output

    assert "episodic_current_session_turns: 0" in command_outputs["/memory"]
    assert "Graph:\n- nodes: not configured" in command_outputs["/memory"]
    assert "Last context:\n- total_tokens: unavailable" in command_outputs["/memory"]
    assert "characters" in command_outputs["/context --debug"]
    assert "System: You are Friday." in command_outputs["/prompt"]
    assert "retrieved_memory_count" in command_outputs["/debug"]
    assert "context_window: 1000" in command_outputs["/debug-budget"]
    assert "last_turn: 0.125s" in command_outputs["/timing"]
    assert "previous_sessions: 2" in command_outputs["/prime"]
    assert "Retrieval diagnostics:" in command_outputs["/debug-retrieval hello"]
    assert command_outputs["/entities"] == "No entities found."
    assert command_outputs["/insights"] == "No insights found."
    assert command_outputs["/summaries"] == "No summaries found."
    assert "No meta insights found." in command_outputs["/meta"]
    assert "Decayed records: excluded" in command_outputs["/meta"]


async def test_entities_command_lists_relationships() -> None:
    runtime = _runtime()
    assert isinstance(runtime.memory, FakeMemoryController)
    runtime.memory.entities = [
        {"id": "chuck", "label": "Chuck", "type": "person", "hit_count": 2},
        {"id": "friday-labs", "label": "Friday Labs", "type": "organization"},
    ]
    runtime.memory.relationships = [
        {
            "source_label": "Chuck",
            "source_id": "chuck",
            "relation": "founder",
            "target_label": "Friday Labs",
            "target_id": "friday-labs",
            "hit_count": 1,
        }
    ]
    registry = build_default_registry()
    context = RegistryCommandContext(runtime=runtime, registry=registry)

    _, all_result = await registry.execute("/entities", context)
    _, filtered_result = await registry.execute("/entities chuck", context)
    _, relation_result = await registry.execute("/entities founder", context)
    _, nodes_result = await registry.execute("/entities nodes", context)

    assert all_result is not None
    assert "Entities:" in all_result.output
    assert "- Chuck (person), hits=2" in all_result.output
    assert "Relationships:" in all_result.output
    assert "- Chuck -[founder]-> Friday Labs, hits=1" in all_result.output
    assert filtered_result is not None
    assert "- Chuck -[founder]-> Friday Labs, hits=1" in filtered_result.output
    assert relation_result is not None
    assert "- Chuck -[founder]-> Friday Labs, hits=1" in relation_result.output
    assert nodes_result is not None
    assert "Entities:" in nodes_result.output
    assert "Relationships:" not in nodes_result.output


async def test_context_and_prompt_file_exports_are_fixed_and_safe(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path)
    registry = build_default_registry()
    context = RegistryCommandContext(
        runtime=runtime,
        registry=registry,
        last_context="safe context",
        last_prompt="safe prompt",
    )

    _, context_result = await registry.execute("/context --file", context)
    _, prompt_result = await registry.execute("/prompt --file", context)

    assert context_result is not None
    assert prompt_result is not None
    context_path = tmp_path / "friday_context.txt"
    prompt_path = tmp_path / "friday_prompt.txt"
    assert context_path.read_text() == "safe context"
    assert prompt_path.read_text() == "safe prompt"
    assert str(context_path) in context_result.output
    assert str(prompt_path) in prompt_result.output
