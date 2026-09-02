"""Public structural protocols for Friday LLM typed clients."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from friday_llm.requests import ChatCompletionRequest, TypedChatCompletionResponse
from friday_llm.streaming import StreamEvent


@runtime_checkable
class TypedLLMClient(Protocol):
    """Provider-independent typed completion and streaming boundary."""

    async def chat_completion_request(
        self,
        request: ChatCompletionRequest,
    ) -> TypedChatCompletionResponse:
        """Execute one typed completion request."""
        ...

    def chat_completion_events(
        self,
        request: ChatCompletionRequest,
    ) -> AsyncIterator[StreamEvent]:
        """Stream normalized typed events for one request."""
        ...
