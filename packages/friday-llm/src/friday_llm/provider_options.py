"""Bounded, namespaced provider-specific option models."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class LMStudioQwenOptions(BaseModel):
    """Qwen chat-template options accepted by the built-in LM Studio adapter."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    namespace: Literal["lm_studio.qwen3_8"] = "lm_studio.qwen3_8"
    enable_thinking: bool | None = None
    reasoning_effort: Literal["xhigh", "medium", "low"] | None = None
    preserve_thinking: bool | None = None


ProviderOptions = Annotated[LMStudioQwenOptions, Field(discriminator="namespace")]
