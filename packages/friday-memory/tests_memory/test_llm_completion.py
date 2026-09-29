"""Memory typed-completion boundary tests."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest
from friday_core.interfaces.llm import ChatCompletionResponse
from friday_llm import LiteLLMService, ReasoningMode
from friday_memory import llm_completion
from friday_memory.llm_completion import (
    complete_memory_request,
    complete_structured_memory_request,
)
from pydantic import BaseModel


class ExtractedFact(BaseModel):
    fact: str


@pytest.mark.asyncio
async def test_typed_client_receives_explicit_memory_controls() -> None:
    client = AsyncMock(spec=LiteLLMService)
    client.chat_completion_request.return_value = SimpleNamespace(
        content="result",
        reasoning_content="not persisted",
    )

    result = await complete_memory_request(
        client,
        messages=[{"role": "user", "content": "extract"}],
        temperature=0.0,
        max_tokens=500,
        timeout=30,
        reasoning_mode=ReasoningMode.DISABLED,
    )

    request = client.chat_completion_request.call_args.args[0]
    assert request.overrides.reasoning.mode.value == "disabled"
    assert request.overrides.sampling.temperature == 0.0
    assert request.overrides.max_tokens == 500
    assert request.timeout == 30
    assert result.content == "result"
    assert result.reasoning_content == "not persisted"


@pytest.mark.asyncio
async def test_legacy_client_isolated_behind_deprecation_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class LegacyClient:
        async def chat_completion(self, **kwargs: object) -> SimpleNamespace:
            return SimpleNamespace(content="legacy", reasoning_content=None)

    monkeypatch.setattr(llm_completion, "_legacy_warning_emitted", False)
    with pytest.warns(DeprecationWarning, match="TypedLLMClient"):
        result = await complete_memory_request(
            LegacyClient(),  # type: ignore[arg-type]
            messages=[{"role": "user", "content": "extract"}],
            temperature=0.1,
        )
    assert result.content == "legacy"


@pytest.mark.asyncio
async def test_structured_typed_and_legacy_clients_keep_distinct_contracts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    typed = AsyncMock(spec=LiteLLMService)
    typed.chat_completion_request.return_value = SimpleNamespace(
        content='{"fact": "typed"}', reasoning_content=None
    )
    typed_result = await complete_structured_memory_request(
        typed, messages=[{"role": "user", "content": "extract"}],
        response_model=ExtractedFact, temperature=0.0,
    )
    assert typed_result == ExtractedFact(fact="typed")
    assert typed.chat_completion_request.call_count == 1
    assert typed.chat_completion_request.call_args.args[0].overrides.sampling.temperature == 0.0

    class LegacyClient:
        def __init__(self):
            self.kwargs: dict[str, object] = {}

        async def chat_completion(
            self,
            messages: list[dict[str, Any]],
            tools: list[dict[str, Any]] | None = None,
            response_model: type[BaseModel] | None = None,
            temperature: float = 0.7,
            max_tokens: int | None = None,
            timeout: float | None = None,
        ) -> ChatCompletionResponse:
            self.kwargs = {
                "messages": messages,
                "response_model": response_model,
                "temperature": temperature,
            }
            return ChatCompletionResponse(
                _parsed_model=ExtractedFact(fact="legacy")
            )

    legacy = LegacyClient()
    monkeypatch.setattr(llm_completion, "_legacy_warning_emitted", False)
    with pytest.warns(DeprecationWarning, match="TypedLLMClient"):
        legacy_result = await complete_structured_memory_request(
            legacy,
            messages=[{"role": "user", "content": "extract"}],
            response_model=ExtractedFact, temperature=0.0,
        )
    assert legacy_result == ExtractedFact(fact="legacy")
    assert legacy.kwargs["response_model"] is ExtractedFact
    assert legacy.kwargs["temperature"] == 0.0
