"""Primary Friday Chat adapter coverage for Friday LLM's typed API."""

from __future__ import annotations

import json
import threading
import warnings
from collections.abc import AsyncIterator, Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest
from friday_chat.adapters import (
    FridayChatStreamProtocolError,
    build_framework_chat_model,
)
from friday_chat.config import FridayChatConfig, TypedLLMExecutionConfig
from friday_chat.tools.schemas import ToolDefinition
from friday_llm import (
    ChatCompletionRequest,
    CompletionAssurance,
    CompletionToolCall,
    CompletionUsage,
    FinishEvent,
    ProviderOptionsError,
    ReasoningDeltaEvent,
    TextDeltaEvent,
    ToolCallDeltaEvent,
    TypedChatCompletionResponse,
    UsageEvent,
)


def _typed_config(
    *,
    api_base: str = "http://127.0.0.1:1234/v1",
    generation: dict[str, object] | None = None,
    provider_options: dict[str, object] | None = None,
    serving_engine: str = "lm_studio",
) -> FridayChatConfig:
    llm: dict[str, object] = {
        "model": "openai/qwen3.8-27b-mlx",
        "api_base": api_base,
        "api_key": "synthetic-placeholder",
        "timeout_seconds": 10.0,
        "max_retries": 0,
        "transport_target": {
            "provider": "openai_compatible",
            "dialect": "openai_chat_completions",
            "serving_engine": serving_engine,
        },
        "model_target": {
            "model_id": "qwen3.8-27b-mlx",
            "family": "qwen3_8",
            "revision": "test-revision",
        },
    }
    if generation is not None:
        llm["generation"] = generation
    if provider_options is not None:
        llm["provider_options"] = provider_options
    return FridayChatConfig.model_validate({"llm": llm})


def _typed_response() -> TypedChatCompletionResponse:
    return TypedChatCompletionResponse(
        content="typed answer",
        reasoning_content="sensitive reasoning",
        tool_calls=(
            CompletionToolCall(
                id="call-1",
                name="echo",
                arguments={"text": "hello"},
            ),
        ),
        model="qwen3.8-27b-mlx",
        usage=CompletionUsage(
            prompt_tokens=2,
            completion_tokens=3,
            total_tokens=5,
            reasoning_tokens=1,
        ),
        finish_reason="tool_calls",
        assurance=CompletionAssurance(),
    )


def test_typed_builder_sets_targets_and_generation_without_deprecation() -> None:
    config = _typed_config(
        generation={
            "reasoning": {"mode": "enabled", "effort": "medium"},
            "sampling": {"temperature": 0.2, "top_p": 0.9, "top_k": 40},
            "max_tokens": 512,
        }
    )

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        model = build_framework_chat_model(config)

    assert isinstance(model.execution, TypedLLMExecutionConfig)
    assert model.service.execution_target is not None
    assert model.service.generation_defaults == model.execution.generation
    assert not [warning for warning in captured if warning.category is DeprecationWarning]


@pytest.mark.parametrize("thinking", [None, True, False])
def test_legacy_builder_contains_upstream_thinking_deprecation(
    thinking: bool | None,
) -> None:
    llm: dict[str, object] = {"model": "openai/test"}
    if thinking is not None:
        llm["thinking"] = thinking
    config = FridayChatConfig.model_validate({"llm": llm})

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        model = build_framework_chat_model(config)

    assert model.service.thinking_enabled is bool(thinking)
    assert not [warning for warning in captured if warning.category is DeprecationWarning]


@pytest.mark.asyncio
async def test_typed_complete_converts_request_response_and_automatic_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = build_framework_chat_model(_typed_config())
    requests: list[ChatCompletionRequest] = []

    async def complete(
        request: ChatCompletionRequest,
    ) -> TypedChatCompletionResponse:
        requests.append(request)
        return _typed_response()

    monkeypatch.setattr(model.service, "chat_completion_request", complete)
    result = await model.complete(
        [{"role": "user", "content": "hello"}],
        tools=(
            ToolDefinition(
                name="echo",
                description="Echo text",
                input_schema={
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                },
            ),
        ),
    )

    request = requests[0]
    assert request.tool_choice == "auto"
    assert request.tools is not None
    assert request.tools[0]["function"]["name"] == "echo"
    assert result.content == "typed answer"
    assert result.reasoning_content == "sensitive reasoning"
    assert result.tool_calls[0].call_id == "call-1"
    assert result.tool_calls[0].arguments == {"text": "hello"}
    assert result.usage == {
        "prompt_tokens": 2,
        "completion_tokens": 3,
        "total_tokens": 5,
        "reasoning_tokens": 1,
    }


@pytest.mark.asyncio
async def test_typed_stream_projects_only_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = build_framework_chat_model(_typed_config())

    async def events(_request: object) -> AsyncIterator[object]:
        yield ReasoningDeltaEvent(text="sensitive reasoning")
        yield TextDeltaEvent(text="visible ")
        yield UsageEvent(total_tokens=2)
        yield TextDeltaEvent(text="answer")
        yield FinishEvent(finish_reason="stop")

    monkeypatch.setattr(model.service, "chat_completion_events", events)

    chunks = [
        chunk
        async for chunk in model.stream_complete(
            [{"role": "user", "content": "hello"}]
        )
    ]

    assert chunks == ["visible ", "answer"]


@pytest.mark.asyncio
async def test_typed_stream_rejects_unrepresentable_tool_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = build_framework_chat_model(_typed_config())

    async def events(_request: object) -> AsyncIterator[object]:
        yield ToolCallDeltaEvent(index=0, call_id="call-1", name="echo")

    monkeypatch.setattr(model.service, "chat_completion_events", events)

    with pytest.raises(FridayChatStreamProtocolError, match="non-text tool event"):
        _ = [
            chunk
            async for chunk in model.stream_complete(
                [{"role": "user", "content": "hello"}]
            )
        ]


class _CaptureHandler(BaseHTTPRequestHandler):
    payloads: list[dict[str, Any]] = []

    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length))
        if not isinstance(payload, dict):
            self.send_error(400)
            return
        self.payloads.append(payload)
        if payload.get("stream"):
            self._send_stream()
        else:
            self._send_completion()

    def _send_completion(self) -> None:
        body = json.dumps(
            {
                "id": "chat-adapter-test",
                "object": "chat.completion",
                "created": 0,
                "model": "qwen3.8-27b-mlx",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "ok"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2,
                },
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_stream(self) -> None:
        chunks = [
            {
                "id": "chat-adapter-stream",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "qwen3.8-27b-mlx",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": "ok"},
                        "finish_reason": None,
                    }
                ],
            },
            {
                "id": "chat-adapter-stream",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "qwen3.8-27b-mlx",
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            },
        ]
        body = "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks)
        body += "data: [DONE]\n\n"
        encoded = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


@pytest.fixture
def capture_server() -> Iterator[tuple[str, list[dict[str, Any]]]]:
    _CaptureHandler.payloads = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _CaptureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host = str(server.server_address[0])
    port = int(server.server_address[1])
    try:
        yield f"http://{host}:{port}/v1", _CaptureHandler.payloads
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _wire_generation() -> dict[str, object]:
    return {
        "reasoning": {
            "mode": "enabled",
            "effort": "medium",
            "preserve": False,
        },
        "sampling": {
            "temperature": 0.2,
            "top_p": 0.9,
            "top_k": 40,
            "min_p": 0.0,
            "presence_penalty": 0.1,
            "frequency_penalty": 0.2,
            "repetition_penalty": 1.0,
        },
        "max_tokens": 64,
    }


@pytest.mark.asyncio
async def test_chat_adapter_controls_reach_final_http_json(
    capture_server: tuple[str, list[dict[str, Any]]],
) -> None:
    api_base, payloads = capture_server
    model = build_framework_chat_model(
        _typed_config(api_base=api_base, generation=_wire_generation())
    )

    response = await model.complete([{"role": "user", "content": "fixed"}])

    assert response.content == "ok"
    assert len(payloads) == 1
    payload = payloads[0]
    assert payload["temperature"] == 0.2
    assert payload["top_p"] == 0.9
    assert payload["top_k"] == 40
    assert payload["min_p"] == 0.0
    assert payload["presence_penalty"] == 0.1
    assert payload["frequency_penalty"] == 0.2
    assert payload["repeat_penalty"] == 1.0
    assert payload["max_tokens"] == 64
    assert payload["chat_template_kwargs"] == {
        "enable_thinking": True,
        "reasoning_effort": "medium",
        "preserve_thinking": False,
    }
    assert "api_key" not in payload


@pytest.mark.asyncio
async def test_chat_adapter_typed_stream_reuses_generation_defaults(
    capture_server: tuple[str, list[dict[str, Any]]],
) -> None:
    api_base, payloads = capture_server
    model = build_framework_chat_model(
        _typed_config(api_base=api_base, generation=_wire_generation())
    )

    chunks = [
        chunk
        async for chunk in model.stream_complete(
            [{"role": "user", "content": "fixed"}]
        )
    ]

    assert chunks == ["ok"]
    assert payloads[0]["stream"] is True
    assert payloads[0]["top_k"] == 40
    assert payloads[0]["chat_template_kwargs"]["reasoning_effort"] == "medium"


@pytest.mark.asyncio
async def test_provider_option_target_mismatch_fails_before_http(
    capture_server: tuple[str, list[dict[str, Any]]],
) -> None:
    api_base, payloads = capture_server
    model = build_framework_chat_model(
        _typed_config(
            api_base=api_base,
            serving_engine="vllm",
            provider_options={
                "namespace": "lm_studio.qwen3_8",
                "enable_thinking": True,
            },
        )
    )

    with pytest.raises(ProviderOptionsError, match="matching explicit target"):
        await model.complete([{"role": "user", "content": "fixed"}])

    assert payloads == []
