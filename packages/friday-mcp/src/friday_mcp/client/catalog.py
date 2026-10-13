"""Typed optional manual-refresh contract; catalog identity never grants admission."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from friday_mcp.client.http_protocol import HeaderBinding
from friday_mcp.client.protocol import ProtocolFailure, ToolDefinition


@dataclass(frozen=True, repr=False)
class MCPCatalogSnapshot:
    """One complete owner-local generation, with independently decoded exports.

    Definitions remain bounded untrusted peer input. No connection credentials,
    endpoint, peer instructions or live handles are retained here.
    """

    generation: int
    definitions: tuple[ToolDefinition, ...] = field(repr=False)
    rejected_task_tools: int = 0
    rejected_http_tools: int = 0
    excluded_task_names: tuple[str, ...] = field(default=(), repr=False)
    bindings: tuple[tuple[str, tuple[HeaderBinding, ...]], ...] = field(
        default=(), repr=False
    )

    def __post_init__(self) -> None:
        if (
            not isinstance(self.definitions, tuple)
            or any(not isinstance(tool, ToolDefinition) for tool in self.definitions)
            or not isinstance(self.excluded_task_names, tuple)
            or any(not isinstance(name, str) for name in self.excluded_task_names)
            or not isinstance(self.bindings, tuple)
        ):
            raise ProtocolFailure()
        if type(self.generation) is not int or self.generation <= 0:
            raise ProtocolFailure()
        if (
            any(
                type(n) is not int or not 0 <= n <= 256
                for n in (self.rejected_task_tools, self.rejected_http_tools)
            )
            or len(self.definitions)
            + self.rejected_task_tools
            + self.rejected_http_tools
            > 256
        ):
            raise ProtocolFailure("limit_exceeded")

    def tools(self) -> list[dict[str, Any]]:
        """JSON is the public dynamic wire boundary; callers own each export."""
        return [tool.definition.object() for tool in self.definitions]

    def tool(self, name: str) -> ToolDefinition | None:
        return next((tool for tool in self.definitions if tool.name == name), None)

    def headers(self, name: str) -> tuple[HeaderBinding, ...]:
        return next((bindings for key, bindings in self.bindings if key == name), ())


@runtime_checkable
class MCPRefreshClient(Protocol):
    """Optional declared extension; existing MCPClient implementations still work."""

    @property
    def current_catalog_snapshot(self) -> MCPCatalogSnapshot | None: ...

    async def refresh_tool_catalog(self) -> MCPCatalogSnapshot: ...

    async def call_tool_at_generation(
        self, name: str, arguments: dict[str, Any], generation: int
    ) -> str: ...
