"""Typed service API and global-state regression tests."""

import importlib
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import friday_llm
import litellm
import pytest
from friday_llm import (
    ChatCompletionRequest,
    GenerationConfig,
    GenerationOverrides,
    LiteLLMService,
    ModelTarget,
    ReasoningConfig,
    ReasoningMode,
    ResilienceConfig,
    SamplingConfig,
    TransportTarget,
    UnsupportedControlError,
)


def _service() -> LiteLLMService:
    return LiteLLMService(
        model_name="openai/qwen3.8-27b-mlx",
        api_key="test-key",
        api_base="http://127.0.0.1:1234/v1",
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


def _response() -> SimpleNamespace:
    message = SimpleNamespace(
        content="done",
        reasoning_content="private reasoning",
        tool_calls=[],
    )
    details = SimpleNamespace(reasoning_tokens=7)
    usage = SimpleNamespace(
        prompt_tokens=3,
        completion_tokens=9,
        total_tokens=12,
        completion_tokens_details=details,
    )
    return SimpleNamespace(
        choices=[SimpleNamespace(message=message, finish_reason="stop")],
        model="qwen3.8-27b-mlx",
        usage=usage,
    )


def test_import_does_not_mutate_litellm_parameter_policy() -> None:
    litellm.drop_params = False
    litellm.modify_params = False
    importlib.reload(friday_llm)
    assert litellm.drop_params is False
    assert litellm.modify_params is False


@pytest.mark.asyncio
async def test_typed_request_uses_strict_frozen_call_spec() -> None:
    service = _service()
    request = ChatCompletionRequest(
        messages=({"role": "user", "content": "fixed synthetic prompt"},),
        overrides=GenerationOverrides(
            reasoning=ReasoningConfig(mode=ReasoningMode.DISABLED),
            sampling=SamplingConfig(temperature=0.3, top_k=20),
            max_tokens=100,
        ),
    )
    with patch("litellm.acompletion", new_callable=AsyncMock) as completion:
        completion.return_value = _response()
        response = await service.chat_completion_request(request)

    kwargs = completion.call_args.kwargs
    assert kwargs["drop_params"] is False
    assert "modify_params" not in kwargs
    assert kwargs["extra_body"] == {
        "top_k": 20,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    assert response.reasoning_content == "private reasoning"
    assert response.usage.reasoning_tokens == 7
    assert response.assurance.acknowledged_fields == ()
    assert response.assurance.behaviorally_observed_fields == ()


@pytest.mark.asyncio
async def test_preflight_failure_never_invokes_transport() -> None:
    service = LiteLLMService(model_name="gpt-4", api_key="test")
    request = ChatCompletionRequest(
        messages=({"role": "user", "content": "test"},),
        overrides=GenerationOverrides(
            reasoning=ReasoningConfig(mode=ReasoningMode.ENABLED)
        ),
    )
    with patch("litellm.acompletion", new_callable=AsyncMock) as completion:
        with pytest.raises(UnsupportedControlError):
            await service.chat_completion_request(request)
        completion.assert_not_called()


def test_target_identity_conflict_fails_at_construction() -> None:
    with pytest.raises(friday_llm.TargetIdentityError):
        LiteLLMService(
            model_name="openai/model-a",
            transport_target=TransportTarget(
                provider="openai_compatible",
                dialect="openai_chat_completions",
                serving_engine="lm_studio",
            ),
            model_target=ModelTarget(
                model_id="model-b", family="qwen3_8", revision="1"
            ),
        )


def test_transport_identity_conflict_fails_at_construction() -> None:
    with pytest.raises(friday_llm.TargetIdentityError):
        LiteLLMService(
            model_name="anthropic/qwen3.8-27b-mlx",
            transport_target=TransportTarget(
                provider="openai_compatible",
                dialect="openai_chat_completions",
                serving_engine="lm_studio",
            ),
            model_target=ModelTarget(
                model_id="qwen3.8-27b-mlx",
                family="qwen3_8",
                revision="1",
            ),
        )


@pytest.mark.asyncio
async def test_retry_attempts_materialize_byte_equivalent_call_specs() -> None:
    service = LiteLLMService(
        model_name="openai/qwen3.8-27b-mlx",
        api_key="test-key",
        api_base="http://127.0.0.1:1234/v1",
        resilience=ResilienceConfig(
            max_retries=1,
            backoff_multiplier=0.1,
            backoff_min=0.1,
            backoff_max=1.0,
        ),
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
    request = ChatCompletionRequest(
        messages=({"role": "user", "content": "fixed"},),
        overrides=GenerationOverrides(
            sampling=SamplingConfig(temperature=0.4, top_k=10)
        ),
    )
    attempts: list[str] = []

    async def fail_then_succeed(**kwargs: object) -> SimpleNamespace:
        attempts.append(
            json.dumps(kwargs, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        )
        if len(attempts) == 1:
            raise litellm.APIConnectionError(
                message="synthetic connection failure",
                llm_provider="openai",
                model="qwen3.8-27b-mlx",
            )
        return _response()

    with patch("litellm.acompletion", side_effect=fail_then_succeed):
        await service.chat_completion_request(request)

    assert len(attempts) == 2
    assert attempts[0] == attempts[1]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("thinking_enabled", "expects_thinking"),
    [(None, True), (False, True), (True, False)],
)
async def test_legacy_thinking_compatibility(
    thinking_enabled: bool | None,
    expects_thinking: bool,
) -> None:
    if thinking_enabled is None:
        service = LiteLLMService(model_name="gpt-4", api_key="test")
    else:
        with pytest.warns(DeprecationWarning):
            service = LiteLLMService(
                model_name="gpt-4",
                api_key="test",
                thinking_enabled=thinking_enabled,
            )
    with patch("litellm.acompletion", new_callable=AsyncMock) as completion:
        completion.return_value = _response()
        await service.chat_completion([{"role": "user", "content": "fixed"}])

    assert ("thinking" in completion.call_args.kwargs) is expects_thinking


def test_equal_legacy_and_new_reasoning_values_are_accepted() -> None:
    with pytest.warns(DeprecationWarning):
        service = LiteLLMService(
            model_name="gpt-4",
            thinking_enabled=True,
            generation_defaults=GenerationConfig(
                reasoning=ReasoningConfig(mode=ReasoningMode.ENABLED)
            ),
        )
    assert service.generation_defaults is not None


def test_conflicting_legacy_and_new_reasoning_values_fail() -> None:
    with pytest.raises(friday_llm.LLMConfigurationError):
        LiteLLMService(
            model_name="gpt-4",
            thinking_enabled=False,
            generation_defaults=GenerationConfig(
                reasoning=ReasoningConfig(mode=ReasoningMode.ENABLED)
            ),
        )


@pytest.mark.asyncio
async def test_request_conflict_with_legacy_reasoning_fails_before_transport() -> None:
    with pytest.warns(DeprecationWarning):
        service = LiteLLMService(
            model_name="openai/qwen3.8-27b-mlx",
            thinking_enabled=False,
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
    request = ChatCompletionRequest(
        messages=({"role": "user", "content": "fixed"},),
        overrides=GenerationOverrides(
            reasoning=ReasoningConfig(mode=ReasoningMode.ENABLED)
        ),
    )

    with patch("litellm.acompletion", new_callable=AsyncMock) as completion:
        with pytest.raises(friday_llm.LLMConfigurationError):
            await service.chat_completion_request(request)
        completion.assert_not_called()
