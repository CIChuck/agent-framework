"""Provider-neutral generation contract tests."""

import math

import pytest
from friday_llm import (
    GenerationConfig,
    GenerationOverrides,
    ReasoningConfig,
    ReasoningMode,
    SamplingConfig,
)
from friday_llm.generation import resolve_generation
from pydantic import ValidationError


def test_generation_models_forbid_provider_fields() -> None:
    with pytest.raises(ValidationError):
        GenerationConfig.model_validate(
            {"reasoning": {"mode": "enabled"}, "enable_thinking": True}
        )


@pytest.mark.parametrize("value", [math.inf, -math.inf, math.nan])
def test_sampling_rejects_non_finite_values(value: float) -> None:
    with pytest.raises(ValidationError):
        SamplingConfig(temperature=value)


def test_disabled_reasoning_rejects_active_controls() -> None:
    with pytest.raises(ValidationError):
        ReasoningConfig(mode=ReasoningMode.DISABLED, effort="low")


def test_explicit_null_clears_default_and_omission_inherits() -> None:
    defaults = GenerationConfig(
        sampling=SamplingConfig(temperature=0.3),
        max_tokens=500,
    )
    inherited = resolve_generation(defaults, GenerationOverrides())
    cleared = resolve_generation(defaults, GenerationOverrides(max_tokens=None))

    assert inherited.max_tokens == 500
    assert inherited.sampling == SamplingConfig(temperature=0.3)
    assert cleared.max_tokens is None
    assert defaults.max_tokens == 500


def test_nested_sampling_omission_inherits_and_null_clears() -> None:
    defaults = GenerationConfig(
        sampling=SamplingConfig(temperature=0.3, top_k=20)
    )
    resolved = resolve_generation(
        defaults,
        GenerationOverrides(sampling=SamplingConfig(temperature=None)),
    )

    assert resolved.sampling == SamplingConfig(temperature=None, top_k=20)


def test_nested_reasoning_fields_merge_without_mutation() -> None:
    defaults = GenerationConfig(
        reasoning=ReasoningConfig(
            mode=ReasoningMode.ENABLED,
            effort="medium",
            preserve=True,
        )
    )
    resolved = resolve_generation(
        defaults,
        GenerationOverrides(
            reasoning=ReasoningConfig(
                mode=ReasoningMode.ENABLED,
                effort="low",
            )
        ),
    )

    assert resolved.reasoning == ReasoningConfig(
        mode=ReasoningMode.ENABLED,
        effort="low",
        preserve=True,
    )
    assert defaults.reasoning is not None
    assert defaults.reasoning.effort == "medium"


def test_public_generation_schema_is_provider_independent() -> None:
    schema_text = str(GenerationConfig.model_json_schema()).lower()
    forbidden = ("qwen", "anthropic", "openai", "lm_studio", "extra_body")
    assert not any(value in schema_text for value in forbidden)
