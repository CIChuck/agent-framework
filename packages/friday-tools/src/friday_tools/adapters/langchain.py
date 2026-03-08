# mypy: ignore-errors
"""
LangChain tool adapter.

Ref: docs/specs/tool_specification.md - Section 6.1: LangChain Adapter

Converts LangChain BaseTool instances to Friday's ToolDefinition format.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from ..definition import BaseTool
from ..protocols import ToolDefinition

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool as LCBaseTool

logger = logging.getLogger(__name__)


class LangChainToolWrapper(BaseTool):
    """Wraps a LangChain tool as a Friday tool."""

    def __init__(self, lc_tool: LCBaseTool):
        """
        Initialize wrapper.

        Args:
            lc_tool: The LangChain tool to wrap.
        """
        self._lc_tool = lc_tool

    @property
    def name(self) -> str:
        return self._lc_tool.name

    @property
    def description(self) -> str:
        return self._lc_tool.description

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Convert LangChain schema to JSON Schema."""
        # LangChain tools have an args_schema (Pydantic model)
        if hasattr(self._lc_tool, "args_schema") and self._lc_tool.args_schema:
            return self._lc_tool.args_schema.model_json_schema()

        # Fallback to simple string input
        return {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Input to the tool",
                }
            },
            "required": ["input"],
        }

    async def execute(self, **kwargs: Any) -> str:
        """Execute the LangChain tool."""
        # LangChain tools can be sync or async
        if hasattr(self._lc_tool, "arun"):
            # Use async version if available
            if len(kwargs) == 1 and "input" in kwargs:
                result = await self._lc_tool.arun(kwargs["input"])
            else:
                result = await self._lc_tool.arun(**kwargs)
        elif hasattr(self._lc_tool, "run"):
            # Fall back to sync version
            loop = asyncio.get_event_loop()
            if len(kwargs) == 1 and "input" in kwargs:
                result = await loop.run_in_executor(
                    None, self._lc_tool.run, kwargs["input"]
                )
            else:
                result = await loop.run_in_executor(
                    None, lambda: self._lc_tool.run(**kwargs)
                )
        else:
            raise RuntimeError("LangChain tool has no run or arun method")

        return str(result) if result is not None else ""


class LangChainToolAdapter:
    """
    Adapts LangChain BaseTool to Friday ToolDefinition.

    Example:
        ```python
        from langchain_community.tools import DuckDuckGoSearchRun

        adapter = LangChainToolAdapter()
        ddg_tool = DuckDuckGoSearchRun()
        friday_tool = adapter.adapt(ddg_tool)

        # Now use with Friday
        result = await friday_tool.execute(input="weather today")
        ```
    """

    def adapt(self, external_tool: LCBaseTool) -> ToolDefinition:
        """
        Convert a LangChain tool to Friday's ToolDefinition.

        Args:
            external_tool: LangChain BaseTool instance.

        Returns:
            Friday ToolDefinition (actually a LangChainToolWrapper).
        """
        self._validate_langchain_tool(external_tool)
        return LangChainToolWrapper(external_tool)

    def adapt_many(self, tools: list[LCBaseTool]) -> list[ToolDefinition]:
        """
        Convert multiple LangChain tools.

        Args:
            tools: List of LangChain BaseTool instances.

        Returns:
            List of Friday ToolDefinition instances.
        """
        return [self.adapt(tool) for tool in tools]

    def _validate_langchain_tool(self, tool: Any) -> None:
        """Validate that the object is a LangChain tool."""
        try:
            from langchain_core.tools import BaseTool as LCBaseTool

            if not isinstance(tool, LCBaseTool):
                raise TypeError(
                    f"Expected LangChain BaseTool, got {type(tool).__name__}"
                )
        except ImportError:
            raise ImportError(  # noqa: B904
                "langchain-core is required for LangChainToolAdapter. "
                "Install with: pip install langchain-core"
            )
