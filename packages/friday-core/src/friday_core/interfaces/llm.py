"""
LLM Client Protocols.

Defines abstract interfaces for LLM inference and embeddings.
These protocols enable dependency injection and provider flexibility.

Ref: Batch 3 Specification, Section 2.1-2.2
"""

from dataclasses import dataclass, field
from typing import Any, Protocol

from pydantic import BaseModel


@dataclass
class ToolCall:
    """
    Represents a tool call requested by the LLM.

    This is the LLM-layer representation used for parsing responses.
    See friday_memory.models.session.ToolCall for the storage representation.
    """

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ChatCompletionResponse:
    """
    Structured response from chat completion.

    Provides a unified format regardless of the underlying LLM provider.
    Supports both text responses and tool calling.
    """

    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)

    @property
    def has_tool_calls(self) -> bool:
        """Check if the response contains tool calls."""
        return len(self.tool_calls) > 0


class LLMClient(Protocol):
    """
    Abstract interface for LLM inference.

    Implementations should handle:
    - Provider-specific API formatting
    - Retry logic for transient errors
    - Tool call parsing from responses
    - Telemetry/observability hooks
    """

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        response_model: type[BaseModel] | None = None,
        temperature: float = 0.7,
    ) -> ChatCompletionResponse:
        """
        Unified chat completion with optional tool calling.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
                     Supported roles: 'system', 'user', 'assistant', 'tool'
            tools: Optional list of tool JSON schemas in OpenAI format.
                   Each schema should have 'type': 'function' and 'function' keys.
            response_model: Optional Pydantic model for structured output.
                           If provided, response.content will be parsed into this model.
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)

        Returns:
            ChatCompletionResponse with content and/or tool_calls.
            Use response.has_tool_calls to check if tools were requested.

        Raises:
            LLMError: If the API call fails after retries
        """
        ...


class EmbeddingModel(Protocol):
    """
    Abstract interface for text embeddings.

    Supports both document embedding (for indexing) and query embedding
    (for search), enabling asymmetric embedding models like E5 or BGE.
    """

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed multiple documents for indexing.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (one per input text)
        """
        ...

    async def embed_query(self, text: str) -> list[float]:
        """
        Embed a single query for search.

        Some models use different prompts for queries vs documents.

        Args:
            text: Query text to embed

        Returns:
            Single embedding vector
        """
        ...
