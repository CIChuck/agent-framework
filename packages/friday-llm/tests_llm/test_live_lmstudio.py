"""Opt-in live evidence lane for the exact LM Studio/Qwen target."""

from __future__ import annotations

import os

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
    ResilienceConfig,
    SamplingConfig,
    TransportTarget,
)

pytestmark = pytest.mark.skipif(
    os.getenv("FRIDAY_LLM_LIVE") != "1",
    reason="set FRIDAY_LLM_LIVE=1 to authorize local LM Studio requests",
)


def _service() -> LiteLLMService:
    revision = os.environ["FRIDAY_LLM_LIVE_REVISION"]
    model = os.getenv("FRIDAY_LLM_LIVE_MODEL", "qwen3.8-27b-mlx")
    return LiteLLMService(
        model_name=f"openai/{model}",
        api_key="lm-studio",
        api_base="http://127.0.0.1:1234/v1",
        resilience=ResilienceConfig(max_retries=0),
        transport_target=TransportTarget(
            provider="openai_compatible",
            dialect="openai_chat_completions",
            serving_engine="lm_studio",
        ),
        model_target=ModelTarget(
            model_id=model,
            family="qwen3_8",
            revision=revision,
        ),
    )


def _request(reasoning: ReasoningConfig | None) -> ChatCompletionRequest:
    return ChatCompletionRequest(
        messages=(
            {
                "role": "user",
                "content": "Reply with exactly the word READY.",
            },
        ),
        overrides=GenerationOverrides(
            reasoning=reasoning,
            sampling=SamplingConfig(temperature=0.0),
            max_tokens=32,
        ),
        timeout=60.0,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "reasoning",
    [
        None,
        ReasoningConfig(mode=ReasoningMode.DISABLED),
        ReasoningConfig(mode=ReasoningMode.ENABLED, effort="xhigh"),
        ReasoningConfig(mode=ReasoningMode.ENABLED, effort="medium"),
        ReasoningConfig(mode=ReasoningMode.ENABLED, effort="low"),
    ],
    ids=["provider-default", "disabled", "xhigh", "medium", "low"],
)
async def test_live_reasoning_profiles_are_accepted(
    reasoning: ReasoningConfig | None,
) -> None:
    response = await _service().chat_completion_request(_request(reasoning))

    assert response.finish_reason is not None
    assert response.assurance.acknowledged_fields == ()
    assert response.assurance.behaviorally_observed_fields == ()


@pytest.mark.asyncio
async def test_live_stream_keeps_reasoning_text_usage_and_finish_separate() -> None:
    events = [
        event
        async for event in _service().chat_completion_events(
            _request(
                ReasoningConfig(mode=ReasoningMode.ENABLED, effort="medium")
            )
        )
    ]
    event_types = [event.type for event in events]

    assert "finish" in event_types
    assert "usage" in event_types


def _tool_request(*, stream_reasoning: bool) -> ChatCompletionRequest:
    return ChatCompletionRequest(
        messages=(
            {
                "role": "user",
                "content": "Call get_weather for Boston.",
            },
        ),
        tools=(
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Return synthetic weather.",
                    "parameters": {
                        "type": "object",
                        "properties": {"city": {"type": "string"}},
                        "required": ["city"],
                    },
                },
            },
        ),
        tool_choice=NamedToolChoice(
            function=NamedToolChoiceFunction(name="get_weather")
        ),
        overrides=GenerationOverrides(
            reasoning=ReasoningConfig(
                mode=(
                    ReasoningMode.ENABLED
                    if stream_reasoning
                    else ReasoningMode.DISABLED
                ),
                effort="medium" if stream_reasoning else None,
            ),
            max_tokens=128,
        ),
        timeout=60.0,
    )


@pytest.mark.asyncio
async def test_live_forced_tool_call_preserves_identity_and_arguments() -> None:
    response = await _service().chat_completion_request(
        _tool_request(stream_reasoning=False)
    )

    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].id
    assert response.tool_calls[0].name == "get_weather"
    assert isinstance(response.tool_calls[0].arguments, dict)


@pytest.mark.asyncio
async def test_live_streamed_tool_call_assembles_without_lane_contamination() -> None:
    events = [
        event
        async for event in _service().chat_completion_events(
            _tool_request(stream_reasoning=True)
        )
    ]
    event_types = [event.type for event in events]

    assert "tool_call_complete" in event_types
    assert "error" not in event_types
    assert "finish" in event_types
