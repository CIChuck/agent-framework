"""Memory typed-completion boundary tests."""

import warnings
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest
from friday_core.interfaces.llm import ChatCompletionResponse
from friday_llm import (
    CompletionAssurance,
    LiteLLMService,
    ReasoningMode,
    TypedChatCompletionResponse,
)
from friday_memory import llm_completion
from friday_memory.llm_completion import (
    complete_memory_request,
    complete_structured_memory_request,
)
from pydantic import BaseModel, ValidationError


class ExtractedFact(BaseModel):
    fact: str


class _LegacyResponseClient:
    def __init__(self, response: ChatCompletionResponse, error: Exception | None = None):
        self.response = response
        self.error = error
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
            "tools": tools,
            "response_model": response_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": timeout,
        }
        if self.error is not None:
            raise self.error
        return self.response


def _typed_memory_response(content: str | None) -> TypedChatCompletionResponse:
    return TypedChatCompletionResponse(
        content=content,
        reasoning_content="synthetic reasoning",
        model="synthetic-memory",
        assurance=CompletionAssurance(),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("typed", [False, True])
@pytest.mark.parametrize("content", [None, "", "synthetic content"])
@pytest.mark.parametrize("temperature", [None, 0.0])
async def test_published_memory_responses_preserve_controls_projection_and_warning(
    typed, content, temperature, monkeypatch,
):
    messages = [{"role": "user", "content": "synthetic request"}]
    if typed:
        client = AsyncMock(spec=LiteLLMService)
        client.chat_completion_request.return_value = _typed_memory_response(content)
    else:
        client = _LegacyResponseClient(
            ChatCompletionResponse(content=content, reasoning_content="synthetic reasoning")
        )
    monkeypatch.setattr(llm_completion, "_legacy_warning_emitted", False)
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", DeprecationWarning)
        for _ in range(2):
            result = await complete_memory_request(
                client,
                messages=messages,
                temperature=temperature,
                max_tokens=777,
                timeout=12.0,
                reasoning_mode=ReasoningMode.DISABLED,
            )
            assert result.content == content
            assert result.reasoning_content == "synthetic reasoning"
    deprecations = [w for w in captured if w.category is DeprecationWarning]
    assert len(deprecations) == (0 if typed else 1)
    if typed:
        request = client.chat_completion_request.call_args.args[0]
        assert request.messages == tuple(messages)
        assert request.timeout == 12.0
        assert request.overrides.max_tokens == 777
        assert request.overrides.reasoning.mode is ReasoningMode.DISABLED
        if temperature is None:
            assert request.overrides.sampling is None
        else:
            assert request.overrides.sampling.temperature == temperature
    else:
        assert client.kwargs == {
            "messages": messages,
            "tools": None,
            "response_model": None,
            "temperature": 0.7 if temperature is None else temperature,
            "max_tokens": 777,
            "timeout": 12.0,
        }


@pytest.mark.asyncio
@pytest.mark.parametrize("typed", [False, True])
@pytest.mark.parametrize("content", [None, "", "not json", "[]", '{"wrong": true}'])
async def test_published_structured_memory_response_rejects_malformed_data(
    typed, content, monkeypatch,
):
    monkeypatch.setattr(llm_completion, "_legacy_warning_emitted", True)
    if typed:
        client = AsyncMock(spec=LiteLLMService)
        client.chat_completion_request.return_value = _typed_memory_response(content)
    else:
        client = _LegacyResponseClient(
            ChatCompletionResponse(content=content, _parsed_model={"wrong": True})
        )
    if typed and content == '{"wrong": true}':
        with pytest.raises(ValidationError):
            await complete_structured_memory_request(
                client, messages=[{"role": "user", "content": "synthetic request"}], response_model=ExtractedFact,
            )
    else:
        result = await complete_structured_memory_request(
            client, messages=[{"role": "user", "content": "synthetic request"}], response_model=ExtractedFact,
        )
        assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize("typed", [False, True])
async def test_published_structured_memory_response_keeps_model_and_controls(typed, monkeypatch):
    monkeypatch.setattr(llm_completion, "_legacy_warning_emitted", True)
    parsed = ExtractedFact(fact="synthetic fact")
    if typed:
        client = AsyncMock(spec=LiteLLMService)
        client.chat_completion_request.return_value = _typed_memory_response(parsed.model_dump_json())
    else:
        client = _LegacyResponseClient(
            ChatCompletionResponse(content=parsed.model_dump_json(), _parsed_model=parsed)
        )
    messages = [{"role": "user", "content": "synthetic extraction"}]
    result = await complete_structured_memory_request(
        client, messages=messages, response_model=ExtractedFact,
        temperature=0.0, max_tokens=321, timeout=9.0,
    )
    assert result == parsed
    if typed:
        request = client.chat_completion_request.call_args.args[0]
        assert request.messages == tuple(messages)
        assert request.overrides.sampling.temperature == 0.0
        assert request.overrides.max_tokens == 321
        assert request.timeout == 9.0
    else:
        assert result is parsed
        assert client.kwargs["response_model"] is ExtractedFact
        assert client.kwargs["messages"] is messages
        assert client.kwargs["temperature"] == 0.0
        assert client.kwargs["max_tokens"] == 321
        assert client.kwargs["timeout"] == 9.0


@pytest.mark.asyncio
@pytest.mark.parametrize("typed", [False, True])
@pytest.mark.parametrize("structured", [False, True])
async def test_memory_response_exception_propagates_unchanged(typed, structured, monkeypatch):
    monkeypatch.setattr(llm_completion, "_legacy_warning_emitted", True)
    error = LookupError("synthetic completion error")
    if typed:
        client = AsyncMock(spec=LiteLLMService)
        client.chat_completion_request.side_effect = error
    else:
        client = _LegacyResponseClient(ChatCompletionResponse(), error)
    with pytest.raises(LookupError) as raised:
        if structured:
            await complete_structured_memory_request(
                client, messages=[{"role": "user", "content": "synthetic request"}], response_model=ExtractedFact,
            )
        else:
            await complete_memory_request(client, messages=[{"role": "user", "content": "synthetic request"}])
    assert raised.value is error


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
