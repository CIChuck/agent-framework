"""
MCP Tool Adapter.

Adapts MCP tools to Friday's ToolDefinition protocol.
Follows the pattern from friday-tools/adapters/.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any, Literal

from friday_core.interfaces.tools import SchemaFormat
from friday_core.mcp import MCPToolMetadata

from friday_mcp.client.catalog import MCPCatalogSnapshot, MCPRefreshClient
from friday_mcp.protocols import MCPClient, ToolDefinition
from friday_mcp.utils.schema import mcp_to_friday_schema

logger = logging.getLogger(__name__)

MCPCallPhase = Literal["start", "finish", "failure"]
MCPCallOutcome = Literal["success", "timeout", "cancelled", "execution_error"]
MCPCallObserver = Callable[[MCPCallPhase, str, MCPCallOutcome | None], None]


@dataclass(frozen=True)
class MCPValidatedDefinition:
    """Immutable registration input; caller must validate/sanitize before use.

    JSON is the explicit dynamic boundary. Each export is independently decoded.
    This value does not assert universal prompt-injection resistance.
    """

    description: str = field(repr=False)
    parameters_json: str = field(repr=False)

    def parameters(self) -> dict[str, Any]:
        value: Any = json.loads(self.parameters_json)
        if not isinstance(value, dict):
            raise ValueError("MCP validated parameters must be an object")
        return value


class MCPToolWrapper:
    """
    Wraps an MCP tool as a Friday ToolDefinition.

    Similar to LangChainToolWrapper and AnthropicToolWrapper
    in friday-tools/adapters/.
    """

    def __init__(
        self,
        client: MCPClient,
        tool_def: dict[str, Any],
        name_prefix: str = "",
        *,
        catalog_snapshot: MCPCatalogSnapshot | None = None,
    ) -> None:
        """
        Initialize MCP tool wrapper.

        Args:
            client: Connected MCP client for executing the tool
            tool_def: MCP tool definition from tools/list
            name_prefix: Optional prefix for tool name
        """
        self._client = client
        self._refresh_client: MCPRefreshClient | None = (
            client if isinstance(client, MCPRefreshClient) else None
        )
        snapshot = catalog_snapshot
        if snapshot is None and self._refresh_client is not None:
            snapshot = self._refresh_client.current_catalog_snapshot
        self._catalog_generation = snapshot.generation if snapshot is not None else None
        self._tool_def = json.loads(json.dumps(tool_def, allow_nan=False))
        self._name_prefix = name_prefix
        original = tool_def.get("name", "unknown")
        if not isinstance(original, str):
            raise ValueError("MCP tool name must be a string")
        self._original_name = original
        self._canonical_name: str | None = None
        self._validated: MCPValidatedDefinition | None = None
        self._call_observer: MCPCallObserver | None = None

    def set_call_observer(self, observer: MCPCallObserver | None) -> None:
        """Attach optional metadata-only instrumentation to this wrapper."""
        if observer is not None and self._canonical_name is None:
            raise ValueError("MCP call observation requires checked metadata")
        self._call_observer = observer

    def _observe(self, phase: MCPCallPhase, outcome: MCPCallOutcome | None) -> None:
        observer = self._call_observer
        if observer is not None:
            # Optional observation cannot change an MCP call result.
            with suppress(Exception):
                observer(phase, self.name, outcome)

    @classmethod
    def from_validated(
        cls,
        client: MCPClient,
        metadata: MCPToolMetadata,
        definition: MCPValidatedDefinition,
    ) -> MCPToolWrapper:
        """Use canonical metadata directly; never concatenate another prefix."""
        if metadata.schema_sanitization_state not in {"unchanged", "sanitized"}:
            raise ValueError("MCP registration requires checked metadata")
        if (
            metadata.filter_state != "included"
            or metadata.discovery_state != "discovered"
        ):
            raise ValueError("MCP registration requires admitted metadata")
        definition.parameters()
        wrapper = cls(client, {"name": metadata.original_name})
        if wrapper._refresh_client is not None and wrapper._catalog_generation is None:
            # A checked definition assembled during an invalid catalog must never
            # become callable after a later refresh supplies different wire data.
            wrapper._catalog_generation = 0
        wrapper._canonical_name = metadata.canonical_name
        wrapper._validated = definition
        return wrapper

    @property
    def original_name(self) -> str:
        """Exact routing name; external provenance, not a logging label."""
        return self._original_name

    @property
    def name(self) -> str:
        """Tool name with optional prefix."""
        if self._canonical_name is not None:
            return self._canonical_name
        if self._name_prefix:
            return f"{self._name_prefix}{self._original_name}"
        return self._original_name

    @property
    def description(self) -> str:
        """Tool description."""
        if self._validated is not None:
            return self._validated.description
        value = self._tool_def.get("description", f"MCP tool: {self._original_name}")
        if not isinstance(value, str):
            raise ValueError("MCP tool description must be a string")
        return value

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Convert MCP inputSchema to Friday parameters_schema."""
        if self._validated is not None:
            return self._validated.parameters()
        input_schema = self._tool_def.get("inputSchema", {})
        value: Any = mcp_to_friday_schema(input_schema)
        if not isinstance(value, dict):
            raise ValueError("MCP tool parameters must be an object")
        snapshot: Any = json.loads(json.dumps(value, allow_nan=False))
        if not isinstance(snapshot, dict):
            raise ValueError("MCP tool parameters must be an object")
        return snapshot

    @property
    def category(self) -> str:
        return "mcp"

    @property
    def tags(self) -> list[str]:
        return ["mcp"]

    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool via MCP client."""
        self._observe("start", None)
        try:
            if (
                self._refresh_client is not None
                and self._catalog_generation is not None
            ):
                result = await self._refresh_client.call_tool_at_generation(
                    self._original_name, kwargs, self._catalog_generation
                )
            else:
                result = await self._client.call_tool(self._original_name, kwargs)
        except asyncio.CancelledError:
            self._observe("failure", "cancelled")
            raise
        except TimeoutError:
            self._observe("failure", "timeout")
            raise
        except Exception:
            self._observe("failure", "execution_error")
            raise
        self._observe("finish", "success")
        return result

    def to_schema(self, format: str = "plain") -> dict[str, Any]:
        """
        Convert to JSON schema format for LLM function calling.

        Args:
            format: Output format - "plain" or "openai".

        Returns:
            Dictionary suitable for LLM function calling.
        """
        plain_schema = {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
            "category": self.category,
            "tags": self.tags,
        }

        if format == SchemaFormat.OPENAI or format == "openai":
            return {
                "type": "function",
                "function": plain_schema,
            }

        return plain_schema

    def __repr__(self) -> str:
        # Standalone names may contain peer text. Never implicitly print it.
        return "MCPToolWrapper(provider='mcp')"


class MCPToolAdapter:
    """
    Adapts MCP tools to Friday's ToolDefinition protocol.

    Example:
        client = StdioMCPClient(...)
        await client.connect()

        adapter = MCPToolAdapter(client, prefix="mcp_filesystem_")
        tools = await adapter.get_tools()

        # Register with Friday's registry
        for tool in tools:
            registry.register(tool)
    """

    def __init__(
        self,
        client: MCPClient,
        prefix: str = "",
    ) -> None:
        """
        Initialize adapter.

        Args:
            client: Connected MCP client
            prefix: Prefix to add to tool names (e.g., "mcp_filesystem_")
        """
        self._client = client
        self._prefix = prefix
        self._tools_cache: list[MCPToolWrapper] | None = None
        self._cache_generation: int | None = None
        self._refresh_client: MCPRefreshClient | None = (
            client if isinstance(client, MCPRefreshClient) else None
        )

    async def get_tools(self, refresh: bool = False) -> list[ToolDefinition]:
        """
        Get all tools from the MCP server as Friday ToolDefinitions.

        Args:
            refresh: Force refresh of cached tools

        Returns:
            List of wrapped tools implementing ToolDefinition protocol.
        """
        current = (
            self._refresh_client.current_catalog_snapshot
            if self._refresh_client is not None
            else None
        )
        if self._refresh_client is not None and (
            current is None or current.generation != self._cache_generation
        ):
            self._tools_cache = None
        if self._tools_cache is not None and not refresh:
            return list(self._tools_cache)
        self._tools_cache = None
        self._cache_generation = None
        if self._refresh_client is not None:
            snapshot = await self._refresh_client.refresh_tool_catalog()
            mcp_tools = snapshot.tools()
        else:
            snapshot = None
            mcp_tools = await self._client.list_tools()
        wrappers = [
            MCPToolWrapper(
                self._client, tool_def, self._prefix, catalog_snapshot=snapshot
            )
            for tool_def in mcp_tools
        ]
        if self._refresh_client is not None:
            current = self._refresh_client.current_catalog_snapshot
            if (
                current is None
                or snapshot is None
                or current.generation != snapshot.generation
            ):
                return []
        self._tools_cache = wrappers
        self._cache_generation = snapshot.generation if snapshot is not None else None
        logger.debug("Adapted %d MCP tools", len(wrappers))
        return list(wrappers)

    async def get_tool(self, name: str) -> ToolDefinition | None:
        """
        Get a specific tool by name.

        Args:
            name: Tool name (with or without prefix)

        Returns:
            Wrapped tool or None if not found
        """
        tools = await self.get_tools()

        # Try exact match first
        for tool in tools:
            if tool.name == name:
                return tool

        # Try matching original name (without prefix)
        for tool in tools:
            if isinstance(tool, MCPToolWrapper) and tool.original_name == name:
                return tool

        return None

    def adapt(self, tool_def: dict[str, Any]) -> ToolDefinition:
        """
        Adapt a single tool definition.

        Args:
            tool_def: MCP tool definition

        Returns:
            Wrapped tool
        """
        return MCPToolWrapper(self._client, tool_def, self._prefix)

    def adapt_many(self, tool_defs: list[dict[str, Any]]) -> list[ToolDefinition]:
        """
        Adapt multiple tool definitions.

        Args:
            tool_defs: List of MCP tool definitions

        Returns:
            List of wrapped tools
        """
        return [self.adapt(tool_def) for tool_def in tool_defs]

    @property
    def client_name(self) -> str:
        """Get the name of the underlying client."""
        value = getattr(self._client, "name", "mcp")
        if not isinstance(value, str):
            raise ValueError("MCP client name must be a string")
        return value

    def clear_cache(self) -> None:
        """Clear the tools cache."""
        self._tools_cache = None
