"""Application lifecycle tests for FridayV2."""

from __future__ import annotations

import asyncio

import httpx
import pytest
from friday_chat.app import (
    FridayChatApp,
    ListInputSource,
    ListOutputSink,
    _format_turn_processing_error,
)
from friday_chat.background import BackgroundTaskManager
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeTranscriptStore, build_runtime
from friday_chat.turns.processor import (
    TurnResult,
    TurnRetryExhaustedError,
    TurnTimeoutError,
)


def _config(data: dict[str, object]) -> FridayChatConfig:
    return FridayChatConfig.model_validate(data)


class KeyboardInterruptInputSource:
    """Input source that simulates Ctrl-C."""

    async def read(self) -> str:
        raise KeyboardInterrupt


class FailingTurnHandler:
    """Turn handler that fails after input is read."""

    async def process(self, user_message: str) -> TurnResult:
        raise RuntimeError(f"failed turn: {user_message}")


class TimeoutTurnHandler:
    """Turn handler that simulates a recoverable model timeout."""

    async def process(self, user_message: str) -> TurnResult:
        raise TurnTimeoutError("LLM turn timed out.", timeout_seconds=60.0)


class PlainTurnHandler:
    """Turn handler that returns model text without an assistant label."""

    async def process(self, user_message: str) -> TurnResult:
        return TurnResult(
            user_message=user_message,
            assistant_message="plain response",
            retrieved_memory_count=0,
            tool_context_injected=False,
        )


class RetryWrapperError(RuntimeError):
    """Test double matching friday-llm retry errors with nested provider cause."""

    def __init__(self, last_error: BaseException) -> None:
        super().__init__("LLM call failed after 4 attempts")
        self.last_error = last_error


class ChunkRecordingOutputSink(ListOutputSink):
    """Output sink that records streaming chunk writes distinctly."""

    async def write_chunk(self, text: str) -> None:
        self.values.append(f"chunk:{text}")


async def test_app_exits_cleanly_on_eof() -> None:
    runtime = build_runtime(_config({"llm": {"model": "openai/test-chat-model"}}))
    output = ListOutputSink()
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["hello"]),
        output_sink=output,
    )

    result = await app.run()

    assert result.exit_reason == "eof"
    assert result.turns_processed == 1
    assert output.values == ["Friday: hello"]
    assert result.maintenance_actions == (
        "flush_pending_extraction",
        "flush_memory",
        "run_lifecycle",
    )
    assert app.started is False
    assert app.background.closed is True
    assert app.background.pending_count == 0
    assert isinstance(runtime.transcript, FakeTranscriptStore)
    assert runtime.transcript.finalized is True


async def test_app_streams_chat_turns_through_chunk_sink() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "tools": {"enabled": False},
            }
        )
    )
    output = ChunkRecordingOutputSink()
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["hello"]),
        output_sink=output,
    )

    result = await app.run()

    assert result.turns_processed == 1
    assert output.values == ["chunk:Friday: hello"]


async def test_app_formats_plain_assistant_response_with_configured_name() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "chat": {"assistant_name": "Friday"},
            }
        )
    )
    output = ListOutputSink()
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["hello"]),
        output_sink=output,
        turn_handler=PlainTurnHandler(),
    )

    result = await app.run()

    assert result.turns_processed == 1
    assert output.values == ["Friday: plain response"]


def test_turn_processing_error_includes_direct_provider_cause() -> None:
    config = _config({"llm": {"model": "openai/test-chat-model"}})
    error = TurnRetryExhaustedError("LLM retry attempts exhausted.")
    error.__cause__ = RuntimeError("provider returned 429 Too Many Requests")

    assert _format_turn_processing_error(error, config) == (
        "Turn failed: LLM retry attempts exhausted. "
        "Last error: RuntimeError: provider returned 429 Too Many Requests"
    )


def test_turn_processing_error_unwraps_retry_provider_cause() -> None:
    config = _config({"llm": {"model": "openai/test-chat-model"}})
    error = TurnRetryExhaustedError("LLM retry attempts exhausted.")
    error.__cause__ = RetryWrapperError(
        ValueError("unsupported parameter: thinking")
    )

    assert _format_turn_processing_error(error, config) == (
        "Turn failed: LLM retry attempts exhausted. "
        "Last error: ValueError: unsupported parameter: thinking"
    )


def test_turn_processing_error_includes_http_response_body() -> None:
    config = _config({"llm": {"model": "openai/test-chat-model"}})
    error = TurnRetryExhaustedError("LLM retry attempts exhausted.")
    request = httpx.Request("POST", "http://10.190.8.25:8000/v1/chat/completions")
    response = httpx.Response(
        400,
        request=request,
        text='{"error":{"message":"extra fields not permitted: metadata"}}',
    )
    error.__cause__ = httpx.HTTPStatusError(
        "Client error '400 Bad Request'",
        request=request,
        response=response,
    )

    assert _format_turn_processing_error(error, config) == (
        "Turn failed: LLM retry attempts exhausted. "
        "Last error: HTTPStatusError: Client error '400 Bad Request' "
        'Response body: {"error":{"message":"extra fields not permitted: metadata"}}'
    )


async def test_app_exits_cleanly_on_keyboard_interrupt() -> None:
    runtime = build_runtime(_config({"llm": {"model": "openai/test-chat-model"}}))
    output = ListOutputSink()
    app = FridayChatApp(
        runtime=runtime,
        input_source=KeyboardInterruptInputSource(),
        output_sink=output,
    )

    result = await app.run()

    assert result.exit_reason == "keyboard_interrupt"
    assert result.turns_processed == 0
    assert output.values == []
    assert app.background.closed is True
    assert isinstance(runtime.transcript, FakeTranscriptStore)
    assert runtime.transcript.finalized is True


async def test_transcript_finalizes_on_turn_error() -> None:
    runtime = build_runtime(_config({"llm": {"model": "openai/test-chat-model"}}))
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["boom"]),
        output_sink=ListOutputSink(),
        turn_handler=FailingTurnHandler(),
    )

    with pytest.raises(RuntimeError, match="failed turn"):
        await app.run()

    assert app.background.closed is True
    assert isinstance(runtime.transcript, FakeTranscriptStore)
    assert runtime.transcript.finalized is True


async def test_turn_timeout_reports_concise_error_without_traceback() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {
                    "model": "openai/test-chat-model",
                    "timeout_seconds": 60.0,
                }
            }
        )
    )
    output = ListOutputSink()
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["slow"]),
        output_sink=output,
        turn_handler=TimeoutTurnHandler(),
    )

    result = await app.run()

    assert result.exit_reason == "eof"
    assert result.turns_processed == 0
    assert output.values == [
        "LLM turn timed out after 60s. Tool calls may have completed, "
        "but the follow-up model response exceeded llm.timeout_seconds. "
        "Consider increasing llm.timeout_seconds or reducing tool result size."
    ]
    assert app.session.turn_ids == []
    assert isinstance(runtime.transcript, FakeTranscriptStore)
    assert runtime.transcript.finalized is True


async def test_exit_maintenance_follows_session_config() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "session": {
                    "flush_on_exit": False,
                    "lifecycle_on_exit": True,
                    "reorganize_on_exit": True,
                    "reorganize_mode": "deep",
                },
            }
        )
    )
    app = FridayChatApp(runtime=runtime, input_source=ListInputSource([]))

    result = await app.run()

    assert result.maintenance_actions == (
        "flush_pending_extraction",
        "run_lifecycle",
        "reorganize_memory:deep",
    )


async def test_exit_maintenance_warning_does_not_block_transcript_finalization() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "session": {
                    "flush_on_exit": False,
                    "lifecycle_on_exit": False,
                    "reorganize_on_exit": True,
                    "reorganize_mode": "fast",
                },
            }
        )
    )
    runtime.maintenance.errors = [RuntimeError("reorganize failed")]
    app = FridayChatApp(runtime=runtime, input_source=ListInputSource([]))

    result = await app.run()

    assert result.exit_reason == "eof"
    assert runtime.diagnostics.maintenance_warnings == [
        "reorganize_memory:fast: reorganize failed"
    ]
    assert isinstance(runtime.transcript, FakeTranscriptStore)
    assert runtime.transcript.finalized is True


async def test_session_initializes_lazily_on_first_chat_turn() -> None:
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "chat": {"user_name": "Chuck", "assistant_name": "Friday"},
            }
        )
    )
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["/help", "hello"]),
        output_sink=ListOutputSink(),
    )

    assert app.session.initialized is False

    result = await app.run()

    assert result.turns_processed == 1
    assert app.session.initialized is True
    assert app.session.scoped_defaults == {
        "user_name": "Chuck",
        "assistant_name": "Friday",
    }
    assert app.session.turn_ids == ["1"]


async def test_app_help_output_includes_usage_and_argument_descriptions() -> None:
    runtime = build_runtime(_config({"llm": {"model": "openai/test-chat-model"}}))
    output = ListOutputSink()
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["/help", "/q"]),
        output_sink=output,
    )

    result = await app.run()

    assert result.exit_reason == "command_exit"
    assert "Usage: /context [--debug] [--file]" in output.values[0]
    assert "- --debug [optional]: Include detailed token diagnostics." in (
        output.values[0]
    )
    assert "Description: Show the assembled context payload." in output.values[0]


async def test_command_only_session_does_not_initialize_chat_defaults() -> None:
    runtime = build_runtime(_config({"llm": {"model": "openai/test-chat-model"}}))
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["/q"]),
        output_sink=ListOutputSink(),
    )

    result = await app.run()

    assert result.exit_reason == "command_exit"
    assert app.session.initialized is False
    assert app.session.turn_ids == []


async def test_app_closes_supervised_background_tasks() -> None:
    async def wait_forever() -> None:
        await asyncio.sleep(60)

    runtime = build_runtime(_config({"llm": {"model": "openai/test-chat-model"}}))
    background = BackgroundTaskManager()
    background.create_task(wait_forever())
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource([]),
        background=background,
    )

    result = await app.run()

    assert result.exit_reason == "eof"
    assert background.closed is True
    assert background.pending_count == 0
