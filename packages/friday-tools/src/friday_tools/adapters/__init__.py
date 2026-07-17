# mypy: ignore-errors
"""
Framework adapters for converting external tools to Friday format.

Ref: docs/reference/specs/tool_specification.md - Section 6: Adapters

These adapters allow tools from other frameworks (LangChain, Anthropic,
OpenAI) to be used within the Friday framework.

Optional Dependencies:
    - langchain-core: For LangChainToolAdapter
    - anthropic: For AnthropicToolAdapter
    - openai: For OpenAIToolAdapter

Example:
    ```python
    from friday_tools.adapters import LangChainToolAdapter
    from langchain_community.tools import DuckDuckGoSearchRun

    adapter = LangChainToolAdapter()
    friday_tool = adapter.adapt(DuckDuckGoSearchRun())
    ```
"""

from .anthropic import AnthropicToolAdapter
from .langchain import LangChainToolAdapter
from .openai import OpenAIToolAdapter

__all__ = [
    "LangChainToolAdapter",
    "AnthropicToolAdapter",
    "OpenAIToolAdapter",
]
