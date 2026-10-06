"""Typed completion boundary with one isolated legacy compatibility path."""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from friday_core.interfaces.llm import ChatCompletionResponse
from friday_llm import (
    ChatCompletionRequest,
    GenerationOverrides,
    ReasoningConfig,
    ReasoningMode,
    SamplingConfig,
    TypedLLMClient,
)
from pydantic import BaseModel

from friday_memory.json_response import parse_json_object_from_text

ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)
_legacy_warning_emitted = False


class LegacyMemoryLLMClient(Protocol):
    """Compatibility-only shape for legacy injected Memory clients."""

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        response_model: type[BaseModel] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        timeout: float | None = None,
    ) -> ChatCompletionResponse:
        """Execute one legacy completion."""
        ...


type MemoryLLMClient = TypedLLMClient | LegacyMemoryLLMClient


@dataclass(frozen=True, slots=True)
class MemoryCompletion:
    """Only completion fields permitted across Memory's LLM boundary."""

    content: str | None
    reasoning_content: str | None = None


async def complete_memory_request(
    client: MemoryLLMClient,
    *,
    messages: list[dict[str, Any]],
    temperature: float | None = None,
    max_tokens: int | None = None,
    timeout: float | None = None,
    reasoning_mode: ReasoningMode | None = None,
) -> MemoryCompletion:
    """Execute a typed Memory request and isolate legacy injection support."""

    if isinstance(client, TypedLLMClient):
        override_values: dict[str, object] = {}
        if reasoning_mode is not None:
            override_values["reasoning"] = ReasoningConfig(mode=reasoning_mode)
        if temperature is not None:
            override_values["sampling"] = SamplingConfig(temperature=temperature)
        if max_tokens is not None:
            override_values["max_tokens"] = max_tokens
        typed_response = await client.chat_completion_request(
            ChatCompletionRequest(
                messages=tuple(messages),
                overrides=GenerationOverrides.model_validate(override_values),
                timeout=timeout,
            )
        )
        return MemoryCompletion(
            content=typed_response.content,
            reasoning_content=typed_response.reasoning_content,
        )

    _warn_for_legacy_client()
    legacy_response = await client.chat_completion(
        messages=messages,
        temperature=temperature if temperature is not None else 0.7,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    return MemoryCompletion(
        content=legacy_response.content,
        reasoning_content=legacy_response.reasoning_content,
    )


async def complete_structured_memory_request[ResponseModelT: BaseModel](
    client: MemoryLLMClient,
    *,
    messages: list[dict[str, Any]],
    response_model: type[ResponseModelT],
    temperature: float | None = None,
    max_tokens: int | None = None,
    timeout: float | None = None,
) -> ResponseModelT | None:
    """Execute a request and validate only final text as a typed model."""

    if isinstance(client, TypedLLMClient):
        completion = await complete_memory_request(
            client,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        payload = parse_json_object_from_text(completion.content)
        if payload is None:
            return None
        return response_model.model_validate(payload)

    _warn_for_legacy_client()
    response = await client.chat_completion(
        messages=messages,
        response_model=response_model,
        temperature=temperature if temperature is not None else 0.7,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    parsed = response._parsed_model
    return parsed if isinstance(parsed, response_model) else None


def _warn_for_legacy_client() -> None:
    global _legacy_warning_emitted
    if _legacy_warning_emitted:
        return
    warnings.warn(
        "Legacy Memory LLM injection is deprecated; provide a TypedLLMClient",
        DeprecationWarning,
        stacklevel=3,
    )
    _legacy_warning_emitted = True
