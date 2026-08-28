"""Bounded diagnostics and sensitive-value regression tests."""

import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from friday_llm import LiteLLMService, TranslationConflictError
from friday_llm.translation import _validate_translator_owned_json


def test_translator_owned_json_rejects_oversized_values_without_echo() -> None:
    canary = "sensitive-canary-" + ("x" * 200)

    with pytest.raises(TranslationConflictError) as error:
        _validate_translator_owned_json({"value": canary})

    assert canary not in str(error.value)


def test_malformed_tool_argument_log_does_not_include_argument_value(
    caplog: pytest.LogCaptureFixture,
) -> None:
    canary = "sensitive-tool-argument-canary"
    service = LiteLLMService(model_name="gpt-4")

    with caplog.at_level(logging.WARNING, logger="friday_llm.service"):
        result = service._parse_tool_arguments(canary, "synthetic-tool")

    assert result == {"raw": canary}
    assert canary not in caplog.text


@pytest.mark.asyncio
async def test_reasoning_api_key_and_api_base_query_are_not_logged(
    caplog: pytest.LogCaptureFixture,
) -> None:
    reasoning_canary = "sensitive-reasoning-canary"
    key_canary = "sensitive-api-key-canary"
    query_canary = "sensitive-query-canary"
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content="ok",
                    reasoning_content=reasoning_canary,
                    tool_calls=[],
                ),
                finish_reason="stop",
            )
        ],
        model="gpt-4",
        usage=None,
    )
    service = LiteLLMService(
        model_name="gpt-4",
        api_key=key_canary,
        api_base=f"http://127.0.0.1:1234/v1?token={query_canary}",
    )

    with (
        caplog.at_level(logging.DEBUG, logger="friday_llm.service"),
        patch("litellm.acompletion", new_callable=AsyncMock) as completion,
    ):
        completion.return_value = response
        result = await service.chat_completion(
            [{"role": "user", "content": "fixed"}]
        )

    assert result.reasoning_content == reasoning_canary
    assert reasoning_canary not in caplog.text
    assert key_canary not in caplog.text
    assert query_canary not in caplog.text
