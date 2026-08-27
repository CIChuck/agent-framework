"""Capability composition and translation tests."""

import pytest
from friday_llm import (
    GenerationConfig,
    LMStudioQwenOptions,
    ModelTarget,
    ProviderOptionsError,
    ReasoningConfig,
    ReasoningMode,
    SamplingConfig,
    TranslationConflictError,
    TransportTarget,
    UnsupportedControlError,
)
from friday_llm.capabilities import (
    CapabilityState,
    ProviderCapabilities,
    compose_capabilities,
)
from friday_llm.provider_options import ProviderOptions
from friday_llm.targets import ExecutionTarget
from friday_llm.translation import (
    GenerationTranslation,
    TranslationSummary,
    translate_generation,
    translate_with_adapter,
)


class _TopLevelTemperatureAdapter:
    def translate(
        self,
        target: ExecutionTarget | None,
        config: GenerationConfig,
        capabilities: ProviderCapabilities,
        provider_options: ProviderOptions | None,
    ) -> GenerationTranslation:
        temperature = config.sampling.temperature if config.sampling else None
        return GenerationTranslation(
            kwargs={"temperature": temperature},
            summary=TranslationSummary(
                requested_fields=("sampling.temperature",),
                emitted_fields=("temperature",),
                capability_sources=capabilities.record_versions,
            ),
        )


class _NestedTemperatureAdapter:
    def translate(
        self,
        target: ExecutionTarget | None,
        config: GenerationConfig,
        capabilities: ProviderCapabilities,
        provider_options: ProviderOptions | None,
    ) -> GenerationTranslation:
        temperature = config.sampling.temperature if config.sampling else None
        return GenerationTranslation(
            kwargs={"extra_body": {"temperature_control": temperature}},
            summary=TranslationSummary(
                requested_fields=("sampling.temperature",),
                emitted_fields=("extra_body.temperature_control",),
                capability_sources=capabilities.record_versions,
            ),
        )


@pytest.fixture
def target() -> ExecutionTarget:
    return ExecutionTarget(
        transport=TransportTarget(
            provider="openai_compatible",
            dialect="openai_chat_completions",
            serving_engine="lm_studio",
        ),
        model=ModelTarget(
            model_id="qwen3.8-27b-mlx",
            family="qwen3_8",
            revision="test-revision",
        ),
    )


def test_capabilities_compose_by_independent_axes(target: ExecutionTarget) -> None:
    capabilities = compose_capabilities(target)

    assert capabilities.for_control("reasoning.effort").state is CapabilityState.SUPPORTED
    assert capabilities.for_control("reasoning.budget_tokens").state is CapabilityState.UNSUPPORTED
    assert capabilities.for_control("sampling.temperature").state is CapabilityState.SUPPORTED
    assert capabilities.for_control("missing").state is CapabilityState.UNKNOWN
    assert len(capabilities.record_versions) == 3


def test_qwen_lm_studio_translation_is_bounded(target: ExecutionTarget) -> None:
    translated = translate_generation(
        target,
        GenerationConfig(
            reasoning=ReasoningConfig(
                mode=ReasoningMode.ENABLED, effort="medium", preserve=False
            ),
            sampling=SamplingConfig(
                temperature=0.3,
                top_p=0.8,
                top_k=20,
                min_p=0.0,
                presence_penalty=1.5,
                repetition_penalty=1.0,
            ),
            max_tokens=8000,
        ),
    )

    assert translated.kwargs == {
        "temperature": 0.3,
        "top_p": 0.8,
        "presence_penalty": 1.5,
        "max_tokens": 8000,
        "extra_body": {
            "top_k": 20,
            "min_p": 0.0,
            "repeat_penalty": 1.0,
            "chat_template_kwargs": {
                "enable_thinking": True,
                "reasoning_effort": "medium",
                "preserve_thinking": False,
            },
        },
    }
    assert "reasoning.mode" in translated.summary.requested_fields
    assert "chat_template_kwargs.enable_thinking" in translated.summary.emitted_fields


def test_unknown_explicit_control_fails_preflight() -> None:
    with pytest.raises(UnsupportedControlError) as error:
        translate_generation(
            None,
            GenerationConfig(
                reasoning=ReasoningConfig(mode=ReasoningMode.DISABLED)
            ),
        )
    assert error.value.state == "unknown"


def test_unknown_auto_emits_no_override() -> None:
    translated = translate_generation(
        None,
        GenerationConfig(reasoning=ReasoningConfig(mode=ReasoningMode.AUTO)),
    )
    assert translated.kwargs == {}


def test_unsupported_budget_fails(target: ExecutionTarget) -> None:
    with pytest.raises(UnsupportedControlError) as error:
        translate_generation(
            target,
            GenerationConfig(
                reasoning=ReasoningConfig(
                    mode=ReasoningMode.ENABLED, budget_tokens=1000
                )
            ),
        )
    assert error.value.control == "reasoning.budget_tokens"


def test_provider_options_require_matching_target() -> None:
    other = ExecutionTarget(
        transport=TransportTarget(
            provider="openai_compatible",
            dialect="openai_chat_completions",
            serving_engine="other",
        ),
        model=ModelTarget(model_id="other", family="other", revision="1"),
    )
    with pytest.raises(ProviderOptionsError):
        translate_generation(
            other,
            GenerationConfig(),
            LMStudioQwenOptions(enable_thinking=False),
        )


def test_provider_options_cannot_conflict_with_normalized_intent(
    target: ExecutionTarget,
) -> None:
    with pytest.raises(TranslationConflictError):
        translate_generation(
            target,
            GenerationConfig(
                reasoning=ReasoningConfig(mode=ReasoningMode.ENABLED)
            ),
            LMStudioQwenOptions(enable_thinking=False),
        )


def test_synthetic_adapters_translate_same_normalized_intent_differently(
    target: ExecutionTarget,
) -> None:
    config = GenerationConfig(sampling=SamplingConfig(temperature=0.4))
    before = config.model_dump_json()

    top_level = translate_with_adapter(
        target, config, _TopLevelTemperatureAdapter()
    )
    nested = translate_with_adapter(target, config, _NestedTemperatureAdapter())

    assert top_level.kwargs == {"temperature": 0.4}
    assert nested.kwargs == {"extra_body": {"temperature_control": 0.4}}
    assert config.model_dump_json() == before
