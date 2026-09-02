"""Typed agent-completion boundary with isolated legacy compatibility."""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any, Protocol

from friday_core.interfaces.llm import ChatCompletionResponse
from friday_llm import (
    ChatCompletionRequest,
    CompletionToolCall,
    GenerationOverrides,
    SamplingConfig,
    TypedLLMClient,
)

_legacy_warning_emitted = False


class LegacyAgentLLMClient(Protocol):
    """Compatibility-only injected client used during the 0.1.x window."""

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        response_model: type[Any] | None = None,
        temperature: float = 0.7,
    ) -> ChatCompletionResponse:
        """Execute one legacy agent completion."""
        ...


AgentLLMClient = TypedLLMClient | LegacyAgentLLMClient


@dataclass(frozen=True, slots=True)
class AgentCompletion:
    """Normalized response used by Agent's provider-independent loop."""

    content: str | None
    tool_calls: tuple[CompletionToolCall, ...]
    model: str
    usage: dict[str, int]
    reasoning_content: str | None = None

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


async def complete_agent_request(
    client: AgentLLMClient,
    *,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None,
    temperature: float,
) -> AgentCompletion:
    """Execute an agent request with typed sampling and tool contracts."""

    if isinstance(client, TypedLLMClient):
        response = await client.chat_completion_request(
            ChatCompletionRequest(
                messages=tuple(messages),
                tools=tuple(tools) if tools else None,
                overrides=GenerationOverrides(
                    sampling=SamplingConfig(temperature=temperature)
                ),
            )
        )
        return AgentCompletion(
            content=response.content,
            tool_calls=response.tool_calls,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            reasoning_content=response.reasoning_content,
        )

    _warn_for_legacy_client()
    response = await client.chat_completion(
        messages=messages,
        tools=tools,
        temperature=temperature,
    )
    return AgentCompletion(
        content=response.content,
        tool_calls=tuple(
            CompletionToolCall(
                id=tool_call.id,
                name=tool_call.name,
                arguments=tool_call.arguments,
            )
            for tool_call in response.tool_calls
        ),
        model=response.model,
        usage=dict(response.usage),
        reasoning_content=response.reasoning_content,
    )


def _warn_for_legacy_client() -> None:
    global _legacy_warning_emitted
    if _legacy_warning_emitted:
        return
    warnings.warn(
        "Legacy Agent LLM injection is deprecated; provide a TypedLLMClient",
        DeprecationWarning,
        stacklevel=3,
    )
    _legacy_warning_emitted = True
