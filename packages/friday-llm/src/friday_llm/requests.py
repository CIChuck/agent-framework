"""Typed request and response contracts for Friday LLM."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue

from friday_llm.generation import GenerationOverrides
from friday_llm.provider_options import ProviderOptions


class NamedToolChoiceFunction(BaseModel):
    """Function selector for a named tool choice."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, max_length=256)


class NamedToolChoice(BaseModel):
    """Typed OpenAI Chat named-function selector."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["function"] = "function"
    function: NamedToolChoiceFunction


ToolChoice = Literal["auto", "none", "required"] | NamedToolChoice


class ChatCompletionRequest(BaseModel):
    """Typed completion request using normalized generation overrides."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    messages: tuple[dict[str, JsonValue], ...] = Field(min_length=1)
    tools: tuple[dict[str, JsonValue], ...] | None = None
    tool_choice: ToolChoice | None = None
    overrides: GenerationOverrides | None = None
    provider_options: ProviderOptions | None = None
    timeout: float | None = Field(default=None, gt=0)


class CompletionToolCall(BaseModel):
    """Normalized tool call returned by the typed completion API."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    name: str
    arguments: dict[str, JsonValue]


class CompletionUsage(BaseModel):
    """Normalized usage including optional reasoning tokens."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    reasoning_tokens: int | None = None


class CompletionAssurance(BaseModel):
    """Bounded evidence about configuration and translation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    requested_fields: tuple[str, ...] = ()
    resolved_fields: tuple[str, ...] = ()
    emitted_fields: tuple[str, ...] = ()
    capability_sources: tuple[str, ...] = ()
    target_profile: tuple[str, ...] = ()
    litellm_version: str = Field(default="", max_length=32)
    acknowledged_fields: tuple[str, ...] = ()
    behaviorally_observed_fields: tuple[str, ...] = ()


class TypedChatCompletionResponse(BaseModel):
    """Provider-normalized response for typed completion calls."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    content: str | None = None
    reasoning_content: str | None = None
    tool_calls: tuple[CompletionToolCall, ...] = ()
    model: str
    usage: CompletionUsage = Field(default_factory=CompletionUsage)
    finish_reason: str | None = None
    assurance: CompletionAssurance
