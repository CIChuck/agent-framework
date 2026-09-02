"""Agent typed-completion boundary tests."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from friday_agent.llm_completion import complete_agent_request
from friday_agent.repl_base import ReplAgentBase
from friday_llm import LiteLLMService


@pytest.mark.asyncio
async def test_agent_temperature_is_one_typed_request_override() -> None:
    client = AsyncMock(spec=LiteLLMService)
    client.chat_completion_request.return_value = SimpleNamespace(
        content="done",
        tool_calls=(),
        model="test",
        usage=SimpleNamespace(
            prompt_tokens=1,
            completion_tokens=2,
            total_tokens=3,
        ),
        reasoning_content="private",
    )

    response = await complete_agent_request(
        client,
        messages=[{"role": "user", "content": "work"}],
        tools=None,
        temperature=0.25,
    )

    request = client.chat_completion_request.call_args.args[0]
    assert request.overrides.sampling.temperature == 0.25
    assert request.overrides.reasoning is None
    assert response.content == "done"


def test_persisted_prompt_snapshot_excludes_reasoning_content() -> None:
    messages = [
        {"role": "user", "content": "work"},
        {
            "role": "assistant",
            "content": None,
            "reasoning_content": "private chain of thought",
            "tool_calls": [],
        },
    ]

    snapshot = ReplAgentBase._sanitize_prompt_messages(messages)

    assert "reasoning_content" not in snapshot[1]
    assert messages[1]["reasoning_content"] == "private chain of thought"
