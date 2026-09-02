"""No-tool turn processing tests for FridayV2."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Sequence

import pytest
from friday_chat.config import FridayChatConfig
from friday_chat.display import Heartbeat, HeartbeatKind
from friday_chat.runtime import (
    FakeChatModel,
    FakeMemoryController,
    FakeToolRegistry,
    FakeTranscriptStore,
    Message,
    build_runtime,
)
from friday_chat.tools.schemas import ToolDefinition
from friday_chat.turns.models import ChatModelResponse, ToolCallRequest
from friday_chat.turns.processor import (
    TurnCircuitBreakerOpenError,
    TurnPersistenceError,
    TurnProcessor,
    TurnRetryExhaustedError,
    TurnTimeoutError,
    _serialize_response,
)


def _config(data: dict[str, object]) -> FridayChatConfig:
    return FridayChatConfig.model_validate(data)


def test_persisted_raw_response_excludes_reasoning_content() -> None:
    payload = json.loads(
        _serialize_response(
            ChatModelResponse(
                content="final answer",
                reasoning_content="private chain of thought",
            )
        )
    )

    assert payload["content"] == "final answer"
    assert "reasoning_content" not in payload


class FailingTranscriptStore(FakeTranscriptStore):
    """Transcript store that fails during basic turn persistence."""

    async def record_turn(self, user_message: str, assistant_message: str) -> None:
        raise OSError("transcript unavailable")


class RecordingHeartbeat:
    """Heartbeat that records start/stop calls."""

    def __init__(self, events: list[str], kind: HeartbeatKind) -> None:
        self._events = events
        self._kind = kind

    def start(self) -> None:
        self._events.append(f"{self._kind}:start")

    def stop(self) -> None:
        self._events.append(f"{self._kind}:stop")


class RecordingHeartbeatFactory:
    """Heartbeat factory for turn-processing assertions."""

    def __init__(self) -> None:
        self.events: list[str] = []

    def create_heartbeat(self, kind: HeartbeatKind) -> Heartbeat:
        return RecordingHeartbeat(self.events, kind)


class RecordingToolAwareChatModel:
    """Chat model that records tool schemas supplied to each completion."""

    def __init__(self) -> None:
        self.tool_names_by_call: list[list[str]] = []

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ChatModelResponse:
        tool_names = [str(getattr(tool, "name", "")) for tool in tools]
        self.tool_names_by_call.append(tool_names)
        if messages and messages[-1].get("role") == "tool":
            return ChatModelResponse.from_text(f"Friday: {messages[-1]['content']}")
        if "get_current_datetime" in tool_names:
            return ChatModelResponse(
                tool_calls=(
                    ToolCallRequest(
                        name="get_current_datetime",
                        arguments={"format": "human", "timezone_name": "local"},
                        call_id="recording-date-time",
                    ),
                )
            )
        return ChatModelResponse.from_text("No tool selected.")

    async def stream_complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> AsyncIterator[str]:
        response = await self.complete(messages, tools=tools)
        yield response.content


class TextToolCallChatModel:
    """Chat model that emits a textual tool-call expression."""

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ChatModelResponse:
        if messages and messages[-1].get("role") == "tool":
            return ChatModelResponse.from_text(f"Friday: {messages[-1]['content']}")
        return ChatModelResponse.from_text(
            "get_current_datetime(format='human', timezone_name='local')"
        )

    async def stream_complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> AsyncIterator[str]:
        response = await self.complete(messages, tools=tools)
        yield response.content


async def test_no_tool_turn_processing_omits_tool_schemas_when_disabled() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "tools": {"enabled": False},
            }
        )
    )

    result = await TurnProcessor(runtime).process("hello")

    assert result.assistant_message == "Friday: hello"
    assert result.tool_context_injected is False
    assert result.metrics is not None
    assert result.metrics.total_seconds >= 0


async def test_no_tool_turn_heartbeat_starts_and_stops() -> None:
    runtime = build_runtime(_config({"llm": {"model": "openai/test-chat-model"}}))
    heartbeat_factory = RecordingHeartbeatFactory()

    result = await TurnProcessor(
        runtime,
        heartbeat_factory=heartbeat_factory,
    ).process("hello")

    assert result.assistant_message == "Friday: hello"
    assert heartbeat_factory.events == ["thinking:start", "thinking:stop"]


async def test_heartbeat_stops_when_retries_fail() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {
                    "model": "openai/test-chat-model",
                    "max_retries": 1,
                }
            }
        )
    )
    assert isinstance(runtime.chat_llm, FakeChatModel)
    runtime.chat_llm.failures = [RuntimeError("one"), RuntimeError("two")]
    heartbeat_factory = RecordingHeartbeatFactory()

    with pytest.raises(TurnRetryExhaustedError, match="exhausted"):
        await TurnProcessor(
            runtime,
            heartbeat_factory=heartbeat_factory,
        ).process("fail")

    assert heartbeat_factory.events == [
        "thinking:start",
        "thinking:stop",
        "thinking:start",
        "thinking:stop",
    ]


async def test_dynamic_context_budget_subtracts_tool_schema_tokens() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "memory": {"context_window": 2000, "output_buffer": 200},
                "chat": {"system_prompt": "system prompt"},
                "tools": {"context": {"include_in_context": True}},
            }
        )
    )

    result = await TurnProcessor(runtime).process("budget")

    assert result.tool_schema_tokens > 0
    assert result.context_budget_tokens < 1800
    assert isinstance(runtime.memory, FakeMemoryController)
    assert runtime.memory.retrieval_token_limits == [result.context_budget_tokens]


async def test_tool_call_only_response_executes_tool_and_returns_final_content() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "tools": {"enabled": True},
            }
        )
    )
    assert isinstance(runtime.chat_llm, FakeChatModel)
    runtime.chat_llm.responses = [
        ChatModelResponse(
            tool_calls=(
                ToolCallRequest(
                    name="get_current_datetime",
                    arguments={"format": "iso"},
                    call_id="call-date",
                ),
            )
        ),
        ChatModelResponse.from_text("Today is in the tool result."),
    ]

    result = await TurnProcessor(runtime).process("Use the tool result.")

    assert result.assistant_message == "Today is in the tool result."
    assert result.tool_calls[0].name == "get_current_datetime"
    assert result.tool_calls[0].call_id == "call-date"
    assert isinstance(runtime.tools, FakeToolRegistry)
    assert runtime.tools.calls[0].name == "get_current_datetime"
    second_call_messages = runtime.chat_llm.calls[1]
    assert second_call_messages[-1]["role"] == "tool"
    assert second_call_messages[-1]["tool_call_id"] == "call-date"


async def test_fake_date_question_uses_datetime_tool() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "tools": {"enabled": True},
            }
        )
    )

    result = await TurnProcessor(runtime).process("What is today's date?")

    assert result.assistant_message.startswith("Friday: Current time")
    assert result.tool_calls[0].name == "get_current_datetime"
    assert isinstance(runtime.tools, FakeToolRegistry)
    assert runtime.tools.calls[0].name == "get_current_datetime"
    assert isinstance(runtime.chat_llm, FakeChatModel)
    assert len(runtime.chat_llm.calls) == 2


async def test_date_question_sends_relevant_tool_subset_to_model() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "tools": {
                    "enabled": True,
                    "context": {
                        "recommendation_threshold": 0.5,
                        "max_tools": 20,
                    },
                },
            }
        )
    )
    model = RecordingToolAwareChatModel()
    runtime.chat_llm = model

    result = await TurnProcessor(runtime).process("What day is it?")

    assert model.tool_names_by_call[0] == ["get_current_datetime"]
    assert result.tool_calls[0].name == "get_current_datetime"
    assert "Date:" in result.assistant_message


async def test_file_review_question_sends_file_read_not_file_write() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "tools": {
                    "enabled": True,
                    "context": {
                        "recommendation_threshold": 0.5,
                        "max_tools": 20,
                    },
                },
            }
        )
    )
    runtime.tools = FakeToolRegistry(
        (
            ToolDefinition(
                name="file_write",
                description="Write content to a text file.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["path", "content"],
                },
                category="filesystem",
            ),
            ToolDefinition(
                name="file_read",
                description="Read and process files of any size.",
                input_schema={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
                category="filesystem",
            ),
        )
    )
    model = RecordingToolAwareChatModel()
    runtime.chat_llm = model

    await TurnProcessor(runtime).process(
        "Evaluate /workspace/example-project/config.yaml"
    )

    assert model.tool_names_by_call[0] == ["file_read"]


async def test_web_search_query_does_not_select_datetime_for_current_modifier() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "tools": {
                    "enabled": True,
                    "context": {
                        "recommendation_threshold": 0.5,
                        "max_tools": 20,
                    },
                },
            }
        )
    )
    runtime.tools = FakeToolRegistry(
        (
            ToolDefinition(
                name="get_current_datetime",
                description="Get the current date and time.",
                input_schema={"type": "object", "properties": {}},
                category="utility",
            ),
            ToolDefinition(
                name="serper_search",
                description="Search Google using Serper.dev API.",
                input_schema={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
                category="web",
            ),
        )
    )
    model = RecordingToolAwareChatModel()
    runtime.chat_llm = model

    await TurnProcessor(runtime).process("Search the web for current Python release notes")

    assert model.tool_names_by_call[0] == ["serper_search"]


async def test_textual_tool_call_response_is_executed() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "tools": {"enabled": True},
            }
        )
    )
    runtime.chat_llm = TextToolCallChatModel()

    result = await TurnProcessor(runtime).process("What day is it?")

    assert result.tool_calls[0].name == "get_current_datetime"
    assert result.tool_calls[0].arguments == {
        "format": "human",
        "timezone_name": "local",
    }
    assert result.assistant_message.startswith("Friday: Current time")


async def test_multi_turn_prompt_payload_contains_previous_session_history() -> None:
    runtime = build_runtime(_config({"llm": {"model": "openai/test-chat-model"}}))
    assert isinstance(runtime.chat_llm, FakeChatModel)
    runtime.chat_llm.responses = [
        "First answer.",
        "Second answer.",
        "Third answer.",
        "You asked for a summary of the first three turns.",
    ]
    processor = TurnProcessor(runtime)

    await processor.process("Remember alpha.")
    await processor.process("Remember beta.")
    await processor.process("Remember gamma.")
    result = await processor.process("Summarize our conversation so far.")

    assert result.assistant_message == "You asked for a summary of the first three turns."
    fourth_payload = "\n".join(
        str(message.get("content", "")) for message in runtime.chat_llm.calls[3]
    )
    assert "Remember alpha." in fourth_payload
    assert "First answer." in fourth_payload
    assert "Turn: 4" in fourth_payload


async def test_raw_prompt_capture_records_actual_model_payload() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "transcript": {"capture_raw_prompts": True},
            }
        )
    )

    result = await TurnProcessor(runtime).process("capture payload")

    assert isinstance(runtime.chat_llm, FakeChatModel)
    assert isinstance(runtime.transcript, FakeTranscriptStore)
    actual_payload = runtime.chat_llm.calls[0]
    assert result.prompt in runtime.transcript.context_logs[0][0]
    assert actual_payload[0]["role"] == "system"
    assert actual_payload[-1]["content"] == "capture payload"
    assert runtime.transcript.context_logs[0][1] == result.raw_response


async def test_model_payload_combines_system_prompt_and_context() -> None:
    runtime = build_runtime(_config({"llm": {"model": "openai/test-chat-model"}}))

    await TurnProcessor(runtime).process("hello")

    assert isinstance(runtime.chat_llm, FakeChatModel)
    actual_payload = runtime.chat_llm.calls[0]
    assert [message["role"] for message in actual_payload] == ["system", "user"]
    system_content = actual_payload[0]["content"]
    assert isinstance(system_content, str)
    assert system_content.startswith("You are Friday.\n\nTurn: 1\nContext payload:")
    assert "Memory: none" in system_content


async def test_streaming_path_uses_fake_llm_response() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "tools": {"enabled": False},
            }
        )
    )

    chunks = [chunk async for chunk in TurnProcessor(runtime).stream_process("hello")]

    assert "".join(chunks) == "Friday: hello"


async def test_streaming_heartbeat_stops_before_first_chunk() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "tools": {"enabled": False},
            }
        )
    )
    heartbeat_factory = RecordingHeartbeatFactory()
    events = heartbeat_factory.events

    async def record_chunk(chunk: str) -> None:
        events.append(f"chunk:{chunk}")

    result = await TurnProcessor(
        runtime,
        heartbeat_factory=heartbeat_factory,
    ).process_streaming("hello", on_chunk=record_chunk)

    assert result.assistant_message == "Friday: hello"
    assert events == [
        "thinking:start",
        "thinking:stop",
        "chunk:Friday: hello",
    ]


async def test_raw_prompt_capture_records_context_log_and_interaction() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "transcript": {"capture_raw_prompts": True},
            }
        )
    )

    result = await TurnProcessor(runtime).process("capture this")

    assert isinstance(runtime.transcript, FakeTranscriptStore)
    assert runtime.transcript.session_system_prompt == "You are Friday."
    assert runtime.transcript.context_logs == [(result.prompt, result.raw_response)]
    assert len(runtime.transcript.interactions) == 1
    assert runtime.transcript.interactions[0].raw_prompt_captured is True
    assert runtime.transcript.interactions[0].prompt == result.prompt


async def test_persistence_failure_rolls_back_fake_memory() -> None:
    runtime = build_runtime(_config({"llm": {"model": "openai/test-chat-model"}}))
    runtime.transcript = FailingTranscriptStore()

    with pytest.raises(TurnPersistenceError, match="persist"):
        await TurnProcessor(runtime).process("will fail")

    assert isinstance(runtime.memory, FakeMemoryController)
    assert runtime.memory.stored_turns == []


async def test_speech_enabled_startup_augments_prompt_and_transcript_metadata() -> None:
    from friday_chat.speech import SPEECH_PROMPT_SNIPPET

    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "chat": {"system_prompt": "Base prompt."},
                "speech": {"enabled": True},
            }
        )
    )

    result = await TurnProcessor(runtime).process("speech")

    assert SPEECH_PROMPT_SNIPPET.strip() in result.prompt
    assert isinstance(runtime.transcript, FakeTranscriptStore)
    assert runtime.transcript.session_system_prompt is not None
    assert SPEECH_PROMPT_SNIPPET.strip() in runtime.transcript.session_system_prompt


async def test_timeout_error_leaves_state_unpersisted() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {
                    "model": "openai/test-chat-model",
                    "timeout_seconds": 0.001,
                }
            }
        )
    )
    assert isinstance(runtime.chat_llm, FakeChatModel)
    runtime.chat_llm.delay_seconds = 0.01

    with pytest.raises(TurnTimeoutError, match="timed out"):
        await TurnProcessor(runtime).process("slow")

    assert isinstance(runtime.memory, FakeMemoryController)
    assert runtime.memory.stored_turns == []


async def test_retry_exhaustion_leaves_state_unpersisted() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {
                    "model": "openai/test-chat-model",
                    "max_retries": 1,
                }
            }
        )
    )
    assert isinstance(runtime.chat_llm, FakeChatModel)
    runtime.chat_llm.failures = [RuntimeError("one"), RuntimeError("two")]

    with pytest.raises(TurnRetryExhaustedError, match="exhausted"):
        await TurnProcessor(runtime).process("fail")

    assert len(runtime.chat_llm.calls) == 2
    assert isinstance(runtime.memory, FakeMemoryController)
    assert runtime.memory.stored_turns == []


async def test_circuit_breaker_error_leaves_state_unpersisted() -> None:
    runtime = build_runtime(_config({"llm": {"model": "openai/test-chat-model"}}))

    with pytest.raises(TurnCircuitBreakerOpenError, match="circuit breaker"):
        await TurnProcessor(runtime, circuit_breaker_open=True).process("blocked")

    assert isinstance(runtime.memory, FakeMemoryController)
    assert runtime.memory.retrievals == []
    assert runtime.memory.stored_turns == []


async def test_cancellation_leaves_state_unpersisted() -> None:
    runtime = build_runtime(_config({"llm": {"model": "openai/test-chat-model"}}))
    assert isinstance(runtime.chat_llm, FakeChatModel)
    runtime.chat_llm.failures = [asyncio.CancelledError()]

    with pytest.raises(asyncio.CancelledError):
        await TurnProcessor(runtime).process("cancel")

    assert isinstance(runtime.memory, FakeMemoryController)
    assert runtime.memory.stored_turns == []
