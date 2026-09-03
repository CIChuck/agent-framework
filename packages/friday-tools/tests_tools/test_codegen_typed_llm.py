"""Typed Friday LLM coverage for code generation."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from friday_llm import LiteLLMService

from friday_tools.codegen.tool import CodeGenerationTool


@pytest.mark.asyncio
async def test_codegen_uses_typed_sampling_override() -> None:
    llm = AsyncMock(spec=LiteLLMService)
    llm.chat_completion_request.return_value = SimpleNamespace(
        content="```python\nresult = 1\n```"
    )
    tool = CodeGenerationTool(
        llm=llm,
        manifest=MagicMock(),
        temperature=0.15,
    )

    response = await tool._complete_code_request(
        [{"role": "user", "content": "generate"}]
    )

    request = llm.chat_completion_request.call_args.args[0]
    assert request.overrides.sampling.temperature == 0.15
    assert response.content.startswith("```python")
