"""Typed streaming event tests."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from friday_llm import (
    ChatCompletionRequest,
    GenerationOverrides,
    LiteLLMService,
    LLMTimeoutError,
    ModelTarget,
    ReasoningConfig,
    ReasoningMode,
    StreamEvent,
    TransportTarget,
)


class FakeStream:
    def __init__(self, chunks: list[SimpleNamespace]) -> None:
        self._chunks = chunks
        self.closed = False

    def __aiter__(self) -> FakeStream:
        return self

    async def __anext__(self) -> SimpleNamespace:
        if not self._chunks:
            raise StopAsyncIteration
        return self._chunks.pop(0)

    async def aclose(self) -> None:
        self.closed = True


class SlowStream(FakeStream):
    def __init__(self, chunks: list[SimpleNamespace]) -> None:
        super().__init__(chunks)
        self.started = asyncio.Event()

    async def __anext__(self) -> SimpleNamespace:
        self.started.set()
        await asyncio.sleep(60)
        raise StopAsyncIteration


def _chunk(
    *,
    content: str | None = None,
    reasoning: str | None = None,
    tool_calls: list[SimpleNamespace] | None = None,
    finish_reason: str | None = None,
    usage: SimpleNamespace | None = None,
) -> SimpleNamespace:
    choices = []
    if any(value is not None for value in (content, reasoning, tool_calls, finish_reason)):
        delta = SimpleNamespace(
            content=content,
            reasoning_content=reasoning,
            tool_calls=tool_calls or [],
        )
        choices = [SimpleNamespace(delta=delta, finish_reason=finish_reason)]
    return SimpleNamespace(choices=choices, usage=usage)


def _service() -> LiteLLMService:
    return LiteLLMService(
        model_name="openai/qwen3.8-27b-mlx",
        transport_target=TransportTarget(
            provider="openai_compatible",
            dialect="openai_chat_completions",
            serving_engine="lm_studio",
        ),
        model_target=ModelTarget(
            model_id="qwen3.8-27b-mlx",
            family="qwen3_8",
            revision="test-revision",
        ),
    )


@pytest.mark.asyncio
async def test_typed_stream_separates_reasoning_text_tools_usage_and_finish() -> None:
    tool_one = SimpleNamespace(
        index=0,
        id="call_1",
        function=SimpleNamespace(name="lookup", arguments='{"q":'),
    )
    tool_two = SimpleNamespace(
        index=0,
        id=None,
        function=SimpleNamespace(name=None, arguments='"x"}'),
    )
    usage = SimpleNamespace(
        prompt_tokens=4,
        completion_tokens=5,
        total_tokens=9,
        completion_tokens_details=SimpleNamespace(reasoning_tokens=2),
    )
    stream = FakeStream(
        [
            _chunk(reasoning="think"),
            _chunk(tool_calls=[tool_one]),
            _chunk(tool_calls=[tool_two]),
            _chunk(content="answer"),
            _chunk(finish_reason="tool_calls"),
            _chunk(usage=usage),
        ]
    )
    request = ChatCompletionRequest(
        messages=({"role": "user", "content": "fixed"},),
        overrides=GenerationOverrides(
            reasoning=ReasoningConfig(mode=ReasoningMode.ENABLED, effort="low")
        ),
    )
    with patch("litellm.acompletion", new_callable=AsyncMock) as completion:
        completion.return_value = stream
        events = [event async for event in _service().chat_completion_events(request)]

    assert [event.type for event in events] == [
        "reasoning_delta",
        "tool_call_delta",
        "tool_call_delta",
        "text_delta",
        "tool_call_complete",
        "finish",
        "usage",
    ]
    completed = events[4]
    assert completed.type == "tool_call_complete"
    assert completed.call_id == "call_1"
    assert completed.name == "lookup"
    assert completed.arguments == {"q": "x"}
    assert completion.call_args.kwargs["stream"] is True
    assert completion.call_args.kwargs["stream_options"] == {"include_usage": True}


@pytest.mark.asyncio
async def test_malformed_tool_arguments_yield_safe_error_before_finish() -> None:
    tool = SimpleNamespace(
        index=0,
        id="call_1",
        function=SimpleNamespace(name="lookup", arguments="not-json"),
    )
    stream = FakeStream(
        [_chunk(tool_calls=[tool]), _chunk(finish_reason="tool_calls")]
    )
    request = ChatCompletionRequest(messages=({"role": "user", "content": "x"},))

    with patch("litellm.acompletion", new_callable=AsyncMock) as completion:
        completion.return_value = stream
        events = [event async for event in _service().chat_completion_events(request)]

    assert [event.type for event in events] == [
        "tool_call_delta",
        "error",
        "finish",
    ]
    error = events[1]
    assert error.type == "error"
    assert error.code == "malformed_tool_arguments"
    assert "not-json" not in error.message


@pytest.mark.asyncio
async def test_typed_stream_timeout_closes_upstream() -> None:
    stream = SlowStream([])
    request = ChatCompletionRequest(
        messages=({"role": "user", "content": "x"},),
        timeout=0.01,
    )
    with patch("litellm.acompletion", new_callable=AsyncMock) as completion:
        completion.return_value = stream
        with pytest.raises(LLMTimeoutError):
            _ = [
                event
                async for event in _service().chat_completion_events(request)
            ]

    assert stream.closed is True


@pytest.mark.asyncio
async def test_typed_stream_cancellation_closes_upstream() -> None:
    stream = SlowStream([])
    request = ChatCompletionRequest(messages=({"role": "user", "content": "x"},))
    with patch("litellm.acompletion", new_callable=AsyncMock) as completion:
        completion.return_value = stream
        events = _service().chat_completion_events(request)
        task: asyncio.Future[StreamEvent] = asyncio.ensure_future(anext(events))
        await stream.started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    assert stream.closed is True
