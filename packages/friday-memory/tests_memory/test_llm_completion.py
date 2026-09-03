"""Memory typed-completion boundary tests."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from friday_llm import LiteLLMService, ReasoningMode
from friday_memory import llm_completion
from friday_memory.llm_completion import complete_memory_request


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
