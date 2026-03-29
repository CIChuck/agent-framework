"""Deterministic LLM used by the agent quality experiment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from friday_core.interfaces import ChatCompletionResponse
from pydantic import BaseModel

DEFAULT_PROMPT = "Summarize the phrase 'Phase Four Ready' in one short sentence."
DEFAULT_RESPONSE = "Phase Four Ready means the system is ready for Phase 4 validation."


@dataclass
class DeterministicLLMClient:
    """Minimal deterministic chat-completion client for smoke tests."""

    response_map: dict[str, str] = field(default_factory=dict)
    default_response: str = DEFAULT_RESPONSE
    model_name: str = "deterministic-quality-probe"

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
