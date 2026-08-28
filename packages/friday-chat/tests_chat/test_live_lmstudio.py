"""Opt-in Friday Chat evidence lane for the supported LM Studio target."""

from __future__ import annotations

import ipaddress
import os
from urllib.parse import urlsplit

import pytest
from friday_chat.adapters import build_framework_chat_model
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import build_runtime
from friday_chat.tools.schemas import ToolDefinition
from friday_chat.turns.processor import TurnProcessor


def _validate_loopback_endpoint(endpoint: str) -> str:
    parsed = urlsplit(endpoint)
    host = parsed.hostname
    if parsed.scheme != "http" or not host or parsed.query or parsed.fragment:
        raise ValueError("live Friday Chat endpoint must be a plain loopback HTTP URL")
    try:
        is_loopback = ipaddress.ip_address(host).is_loopback
    except ValueError:
        is_loopback = host == "localhost"
    if not is_loopback:
        raise ValueError("live Friday Chat endpoint must resolve to loopback")
    return endpoint.rstrip("/")


def _live_config(*, reasoning_mode: str) -> FridayChatConfig:
    endpoint = _validate_loopback_endpoint(
        os.getenv("FRIDAY_CHAT_LIVE_API_BASE", "http://127.0.0.1:1234/v1")
    )
    revision = os.environ["FRIDAY_CHAT_LIVE_REVISION"]
    model = os.getenv("FRIDAY_CHAT_LIVE_MODEL", "qwen3.8-27b-mlx")
    return FridayChatConfig.model_validate(
        {
            "llm": {
                "model": f"openai/{model}",
                "api_base": endpoint,
                "api_key": os.getenv("FRIDAY_CHAT_LIVE_API_KEY", "lm-studio"),
                "max_retries": 0,
                "timeout_seconds": 60.0,
                "generation": {
                    "reasoning": {
                        "mode": reasoning_mode,
                        "effort": "medium" if reasoning_mode == "enabled" else None,
                        "preserve": False,
                    },
                    "sampling": {
                        "temperature": 0.0,
                        "top_p": 0.95,
                        "top_k": 40,
                        "min_p": 0.0,
                    },
                    "max_tokens": 128,
                },
                "transport_target": {
                    "provider": "openai_compatible",
                    "dialect": "openai_chat_completions",
                    "serving_engine": "lm_studio",
                },
                "model_target": {
                    "model_id": model,
                    "family": "qwen3_8",
                    "revision": revision,
                },
            },
            "tools": {"enabled": False},
            "speech": {"enabled": False},
        }
    )


live = pytest.mark.skipif(
    os.getenv("FRIDAY_CHAT_LIVE") != "1",
    reason="set FRIDAY_CHAT_LIVE=1 to authorize loopback LM Studio requests",
)


@pytest.mark.parametrize(
    "endpoint",
    (
        "https://127.0.0.1:1234/v1",
        "http://example.com/v1",
        "http://192.0.2.10:1234/v1",
        "http://127.0.0.1:1234/v1?token=not-allowed",
    ),
)
def test_live_lane_rejects_non_allowlisted_endpoint(endpoint: str) -> None:
    with pytest.raises(ValueError, match="loopback"):
        _validate_loopback_endpoint(endpoint)


@live
@pytest.mark.asyncio
@pytest.mark.parametrize("reasoning_mode", ("disabled", "enabled"))
async def test_live_primary_complete_accepts_supported_controls(
    reasoning_mode: str,
) -> None:
    response = await build_framework_chat_model(
        _live_config(reasoning_mode=reasoning_mode)
    ).complete([{"role": "user", "content": "Reply with exactly READY."}])

    assert response.content


@live
@pytest.mark.asyncio
async def test_live_primary_stream_exposes_visible_text_only() -> None:
    model = build_framework_chat_model(_live_config(reasoning_mode="enabled"))

    chunks = [
        chunk
        async for chunk in model.stream_complete(
            [{"role": "user", "content": "Reply with exactly READY."}]
        )
    ]

    assert "".join(chunks).strip()


@live
@pytest.mark.asyncio
async def test_live_primary_automatic_tool_selection() -> None:
    response = await build_framework_chat_model(
        _live_config(reasoning_mode="disabled")
    ).complete(
        [
            {
                "role": "user",
                "content": "Call get_weather once for Boston; do not answer directly.",
            }
        ],
        tools=(
            ToolDefinition(
                name="get_weather",
                description="Return synthetic weather for one city.",
                input_schema={
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            ),
        ),
    )

    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "get_weather"
    assert isinstance(response.tool_calls[0].arguments, dict)


@live
@pytest.mark.asyncio
async def test_live_bounded_turn_processor_flow() -> None:
    config = _live_config(reasoning_mode="disabled")
    runtime = build_runtime(config)
    runtime.chat_llm = build_framework_chat_model(config)

    result = await TurnProcessor(runtime).process("Reply with exactly READY.")

    assert result.assistant_message
    assert result.metrics is not None
