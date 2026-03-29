"""Deterministic LLM used by the prompt/transcript audit experiment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from friday_core.interfaces import ChatCompletionResponse
from pydantic import BaseModel

DEFAULT_PROMPT = "Record that Chuck Russell is validating the Phase 5-A prompt and transcript contract."
DEFAULT_RESPONSE = (
    "Chuck Russell is validating the Phase 5-A prompt layering and transcript capture contract."
)


@dataclass
class DeterministicAuditLLMClient:
    """Minimal deterministic chat-completion client for transcript auditing."""

    response_map: dict[str, str] = field(default_factory=dict)
    default_response: str = DEFAULT_RESPONSE
    model_name: str = "deterministic-prompt-transcript-audit"

    @property
    def model(self) -> str:
        return self.model_name

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        response_model: type[BaseModel] | None = None,
        temperature: float = 0.7,
    ) -> ChatCompletionResponse:
        del tools, response_model, temperature

        prompt = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                prompt = str(message.get("content", ""))
                break

        content = self.response_map.get(prompt, self.default_response)
        return ChatCompletionResponse(
            content=content,
            tool_calls=[],
            model=self.model_name,
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        )
