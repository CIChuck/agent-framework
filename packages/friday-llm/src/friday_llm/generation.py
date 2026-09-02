"""Provider-neutral generation configuration for Friday LLM."""

from __future__ import annotations

import math
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ReasoningMode(str, Enum):
    """Normalized reasoning intent."""

    AUTO = "auto"
    ENABLED = "enabled"
    DISABLED = "disabled"


class ReasoningConfig(BaseModel):
    """Provider-neutral reasoning configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: ReasoningMode = ReasoningMode.AUTO
    effort: str | None = Field(default=None, min_length=1, max_length=32)
    budget_tokens: int | None = Field(default=None, gt=0)
    preserve: bool | None = None

    @model_validator(mode="after")
    def validate_combination(self) -> ReasoningConfig:
        if self.mode is ReasoningMode.DISABLED and (
            self.effort is not None
            or self.budget_tokens is not None
            or self.preserve is True
        ):
            raise ValueError(
                "disabled reasoning cannot request effort, budget, or preservation"
            )
        if self.mode is not ReasoningMode.ENABLED and (
            self.effort is not None or self.budget_tokens is not None
        ):
            raise ValueError("effort and budget_tokens require reasoning mode enabled")
        return self


class SamplingConfig(BaseModel):
    """Provider-neutral optional sampling controls."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = Field(default=None, gt=0)
    min_p: float | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    repetition_penalty: float | None = None

    @field_validator(
        "temperature",
        "top_p",
        "min_p",
        "presence_penalty",
        "frequency_penalty",
        "repetition_penalty",
    )
    @classmethod
    def require_finite(cls, value: float | None) -> float | None:
        if value is not None and not math.isfinite(value):
            raise ValueError("sampling values must be finite")
        return value


class GenerationConfig(BaseModel):
    """Resolved or service-level provider-neutral generation controls."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    reasoning: ReasoningConfig | None = None
    sampling: SamplingConfig | None = None
    max_tokens: int | None = Field(default=None, gt=0)


class GenerationOverrides(BaseModel):
    """Per-request generation overrides with field-set-aware merge semantics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    reasoning: ReasoningConfig | None = None
    sampling: SamplingConfig | None = None
    max_tokens: int | None = Field(default=None, gt=0)


def resolve_generation(
    defaults: GenerationConfig | None,
    overrides: GenerationOverrides | None,
) -> GenerationConfig:
    """Resolve defaults and overrides without mutating either input."""

    baseline = defaults or GenerationConfig()
    if overrides is None:
        return baseline.model_copy(deep=True)

    values: dict[str, object] = {
        "reasoning": baseline.reasoning,
        "sampling": baseline.sampling,
        "max_tokens": baseline.max_tokens,
    }
    if "reasoning" in overrides.model_fields_set:
        values["reasoning"] = _merge_reasoning(
            baseline.reasoning,
            overrides.reasoning,
        )
    if "sampling" in overrides.model_fields_set:
        values["sampling"] = _merge_sampling(
            baseline.sampling,
            overrides.sampling,
        )
    if "max_tokens" in overrides.model_fields_set:
        values["max_tokens"] = overrides.max_tokens
    return GenerationConfig.model_validate(values)


def _merge_reasoning(
    defaults: ReasoningConfig | None,
    overrides: ReasoningConfig | None,
) -> ReasoningConfig | None:
    if overrides is None:
        return None
    baseline = defaults or ReasoningConfig()
    values = {
        field_name: (
            getattr(overrides, field_name)
            if field_name in overrides.model_fields_set
            else getattr(baseline, field_name)
        )
        for field_name in ("mode", "effort", "budget_tokens", "preserve")
    }
    if (
        "mode" in overrides.model_fields_set
        and overrides.mode is not ReasoningMode.ENABLED
    ):
        for dependent_field in ("effort", "budget_tokens", "preserve"):
            if dependent_field not in overrides.model_fields_set:
                values[dependent_field] = None
    return ReasoningConfig.model_validate(values)


def _merge_sampling(
    defaults: SamplingConfig | None,
    overrides: SamplingConfig | None,
) -> SamplingConfig | None:
    if overrides is None:
        return None
    baseline = defaults or SamplingConfig()
    fields = (
        "temperature",
        "top_p",
        "top_k",
        "min_p",
        "presence_penalty",
        "frequency_penalty",
        "repetition_penalty",
    )
    values = {
        field_name: (
            getattr(overrides, field_name)
            if field_name in overrides.model_fields_set
            else getattr(baseline, field_name)
        )
        for field_name in fields
    }
    return SamplingConfig.model_validate(values)
