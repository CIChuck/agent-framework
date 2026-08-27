"""Final HTTP wire capture through LiteLLM's real OpenAI-compatible client."""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest
from friday_llm import (
    ChatCompletionRequest,
    GenerationOverrides,
    LiteLLMService,
    ModelTarget,
    NamedToolChoice,
    NamedToolChoiceFunction,
    ReasoningConfig,
    ReasoningMode,
    SamplingConfig,
    TransportTarget,
)


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
                "id": "synthetic-response",
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
                "id": "synthetic-stream",
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
                "id": "synthetic-stream",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "qwen3.8-27b-mlx",
                "choices": [
                    {"index": 0, "delta": {}, "finish_reason": "stop"}
                ],
            },
            {
                "id": "synthetic-stream",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "qwen3.8-27b-mlx",
                "choices": [],
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2,
                },
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


def _service(api_base: str) -> LiteLLMService:
    return LiteLLMService(
        model_name="openai/qwen3.8-27b-mlx",
        api_key="synthetic-placeholder",
        api_base=api_base,
        transport_target=TransportTarget(
            provider="openai_compatible",
            dialect="openai_chat_completions",
            serving_engine="lm_studio",
        ),
        model_target=ModelTarget(
            model_id="qwen3.8-27b-mlx",
            family="qwen3_8",
            revision="wire-fixture-1",
        ),
    )


def _request() -> ChatCompletionRequest:
    return ChatCompletionRequest(
        messages=({"role": "user", "content": "fixed synthetic prompt"},),
        overrides=GenerationOverrides(
            reasoning=ReasoningConfig(
                mode=ReasoningMode.ENABLED,
                effort="medium",
                preserve=False,
            ),
            sampling=SamplingConfig(
                temperature=0.3,
                top_k=20,
                min_p=0.0,
                repetition_penalty=1.0,
            ),
            max_tokens=64,
        ),
    )


@pytest.mark.asyncio
async def test_non_streaming_final_http_payload(
    capture_server: tuple[str, list[dict[str, Any]]],
) -> None:
    api_base, payloads = capture_server
    response = await _service(api_base).chat_completion_request(_request())

    assert response.content == "ok"
    assert len(payloads) == 1
    payload = payloads[0]
    assert payload["model"] == "qwen3.8-27b-mlx"
    assert payload["temperature"] == 0.3
    assert payload["top_k"] == 20
    assert payload["min_p"] == 0.0
    assert payload["repeat_penalty"] == 1.0
    assert payload["chat_template_kwargs"] == {
        "enable_thinking": True,
        "reasoning_effort": "medium",
        "preserve_thinking": False,
    }
    assert "api_key" not in payload
    assert "drop_params" not in payload


@pytest.mark.asyncio
async def test_streaming_uses_same_translated_fields(
    capture_server: tuple[str, list[dict[str, Any]]],
) -> None:
    api_base, payloads = capture_server
    events = [
        event async for event in _service(api_base).chat_completion_events(_request())
    ]

    assert [event.type for event in events] == ["text_delta", "finish", "usage"]
    payload = payloads[0]
    assert payload["stream"] is True
    assert payload["stream_options"] == {"include_usage": True}
    assert payload["chat_template_kwargs"]["reasoning_effort"] == "medium"


@pytest.mark.asyncio
@pytest.mark.parametrize("effort", ["xhigh", "medium", "low"])
async def test_each_qwen_effort_tier_reaches_final_http_json(
    capture_server: tuple[str, list[dict[str, Any]]],
    effort: str,
) -> None:
    api_base, payloads = capture_server
    request = ChatCompletionRequest(
        messages=({"role": "user", "content": "fixed synthetic prompt"},),
        overrides=GenerationOverrides(
            reasoning=ReasoningConfig(
                mode=ReasoningMode.ENABLED,
                effort=effort,
                preserve=True,
            )
        ),
    )

    await _service(api_base).chat_completion_request(request)

    assert payloads[0]["chat_template_kwargs"] == {
        "enable_thinking": True,
        "reasoning_effort": effort,
        "preserve_thinking": True,
    }


@pytest.mark.asyncio
async def test_provider_default_emits_no_reasoning_override(
    capture_server: tuple[str, list[dict[str, Any]]],
) -> None:
    api_base, payloads = capture_server
    request = ChatCompletionRequest(
        messages=({"role": "user", "content": "fixed synthetic prompt"},)
    )

    await _service(api_base).chat_completion_request(request)

    assert "chat_template_kwargs" not in payloads[0]
    assert "thinking" not in payloads[0]


@pytest.mark.asyncio
async def test_disabled_reasoning_reaches_final_http_json(
    capture_server: tuple[str, list[dict[str, Any]]],
) -> None:
    api_base, payloads = capture_server
    request = ChatCompletionRequest(
        messages=({"role": "user", "content": "fixed synthetic prompt"},),
        overrides=GenerationOverrides(
            reasoning=ReasoningConfig(mode=ReasoningMode.DISABLED)
        ),
    )

    await _service(api_base).chat_completion_request(request)

    assert payloads[0]["chat_template_kwargs"] == {"enable_thinking": False}


@pytest.mark.asyncio
async def test_named_tool_choice_uses_lm_studio_bounded_wire_form(
    capture_server: tuple[str, list[dict[str, Any]]],
) -> None:
    api_base, payloads = capture_server
    request = ChatCompletionRequest(
        messages=({"role": "user", "content": "fixed synthetic prompt"},),
        tools=(
            {
                "type": "function",
                "function": {"name": "other", "parameters": {"type": "object"}},
            },
            {
                "type": "function",
                "function": {
                    "name": "selected",
                    "parameters": {"type": "object"},
                },
            },
        ),
        tool_choice=NamedToolChoice(
            function=NamedToolChoiceFunction(name="selected")
        ),
    )

    await _service(api_base).chat_completion_request(request)

    assert payloads[0]["tool_choice"] == "required"
    assert [tool["function"]["name"] for tool in payloads[0]["tools"]] == [
        "selected"
    ]
