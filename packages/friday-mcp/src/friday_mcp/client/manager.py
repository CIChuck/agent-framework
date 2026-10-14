"""
MCP Client Manager.

Manages multiple MCP client connections and provides unified tool access.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any

from friday_mcp.client.adapter import MCPToolAdapter
from friday_mcp.client.base import MCPClientBase
from friday_mcp.client.sse import SSEMCPClient
from friday_mcp.client.stdio import StdioMCPClient
from friday_mcp.config import MCPConfig, MCPServerConfig, TransportType
from friday_mcp.protocols import ToolDefinition

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MCPManagedServer:
    """Explicit typed connection factory; the manager owns its returned client."""

    name: str
    enabled: bool
    factory: Callable[[], MCPClientBase] = field(repr=False)

    def __post_init__(self) -> None:
        if (
            not isinstance(self.name, str)
            or not self.name
            or type(self.enabled) is not bool
            or not callable(self.factory)
        ):
            raise ValueError("Invalid MCP managed server")


class MCPClientManager:
    """
    Manages connections to multiple MCP servers.

    Provides unified access to tools from all connected servers,
    with configurable prefixing to avoid name collisions.

    Example:
        config = MCPConfig(
            servers=[
                MCPServerConfig(name="filesystem", command="npx", args=[...]),
                MCPServerConfig(name="github", command="npx", args=[...])
            ],
            tool_name_prefix="mcp_"
        )

        manager = MCPClientManager(config)
        await manager.connect_all()

        all_tools = await manager.get_all_tools()
        # Returns tools from all servers with prefixed names like:
        # "mcp_filesystem_read_file", "mcp_github_create_issue"

    Or using context manager:
        async with MCPClientManager(config) as manager:
            tools = await manager.get_all_tools()
    """

    def __init__(
        self,
        config: MCPConfig,
        *,
        managed_servers: Sequence[MCPManagedServer] | None = None,
    ) -> None:
        """
        Initialize client manager.

        Args:
            config: MCP configuration with server list
        """
        self.config = config
        self._managed_servers = (
            tuple(managed_servers) if managed_servers is not None else None
        )
        if self._managed_servers is not None:
            if config.servers or any(
                not isinstance(entry, MCPManagedServer)
                for entry in self._managed_servers
            ):
                raise ValueError("Invalid MCP managed server configuration")
            names = [entry.name for entry in self._managed_servers]
            if len(set(names)) != len(names):
                raise ValueError("Duplicate MCP managed server")
        self._clients: dict[str, MCPClientBase] = {}
        self._adapters: dict[str, MCPToolAdapter] = {}

    async def connect_all(self) -> dict[str, bool]:
        """
        Connect to all configured servers.

        Returns:
            Dict mapping server names to connection success status.
        """
        results: dict[str, bool] = {}

        for server_config in self._entries:
            if not server_config.enabled:
                logger.info("Skipping disabled MCP server")
                results[server_config.name] = False
                continue

            results[server_config.name] = await self.connect(server_config.name)

        return results

    async def disconnect_all(self) -> None:
        """Disconnect from all servers."""
        for name in tuple(self._clients):
            try:
                await self.disconnect(name)
            except Exception:
                logger.error("MCP disconnect failed")
        if self._clients:
            raise RuntimeError("MCP client cleanup incomplete")

    async def connect(self, server_name: str) -> bool:
        """
        Connect to a specific server by name.

        Args:
            server_name: Name of the server to connect to

        Returns:
            True if connection successful
        """
        if not any(server.name == server_name for server in self._entries):
            raise KeyError(f"Server not found in config: {server_name}")
        try:
            await self.connect_or_raise(server_name)
            return True
        except Exception:
            logger.error("MCP connection failed")
            return False

    async def connect_or_raise(self, server_name: str) -> None:
        """Connect with observable failure/cancellation for lifecycle owners.

        The legacy ``connect`` boolean API is preserved. Partial connections
        remain manager-owned until public disconnect completes successfully.
        """
        if server_name in self._clients:
            if self._clients[server_name].is_connected:
                return
            await self.disconnect(server_name)
        server_config = None
        for config in self._entries:
            if config.name == server_name:
                server_config = config
                break

        if server_config is None:
            raise KeyError(f"Server not found in config: {server_name}")
        if not server_config.enabled:
            raise ValueError("MCP server is disabled")

        client = (
            server_config.factory()
            if isinstance(server_config, MCPManagedServer)
            else self._create_client(server_config)
        )
        if not isinstance(client, MCPClientBase) or client.name != server_name:
            raise TypeError("Invalid MCP managed client")
        self._clients[server_name] = client
        try:
            await client.connect()
            self._adapters[server_name] = MCPToolAdapter(
                client,
                prefix=f"{self.config.tool_name_prefix}{server_name}_",
            )

        except BaseException:
            try:
                await self.disconnect(server_name)
            except BaseException:
                logger.error("MCP client cleanup incomplete; retained by manager")
            raise
        logger.info("MCP connection established")

    @property
    def _entries(self) -> Sequence[MCPServerConfig] | tuple[MCPManagedServer, ...]:
        return (
            self.config.servers
            if self._managed_servers is None
            else self._managed_servers
        )

    async def disconnect(self, server_name: str) -> None:
        """
        Disconnect from a specific server.

        Args:
            server_name: Name of the server to disconnect from
        """
        if server_name not in self._clients:
            return

        await self._clients[server_name].disconnect()
        self._clients.pop(server_name, None)
        self._adapters.pop(server_name, None)
        logger.info("MCP connection released")

    def _create_client(
        self,
        config: MCPServerConfig,
    ) -> MCPClientBase:
        """Create appropriate client based on transport type."""
        if config.transport == TransportType.STDIO:
            return StdioMCPClient.from_config(config)
        elif config.transport == TransportType.SSE:
            return SSEMCPClient.from_config(config)
        else:
            raise ValueError(f"Unknown transport: {config.transport}")

    async def get_all_tools(self) -> list[ToolDefinition]:
        """
        Get tools from all connected servers.

        Returns:
            Unified list of tools with prefixed names to avoid collisions.
        """
        all_tools: list[ToolDefinition] = []

        for adapter in self._adapters.values():
            try:
                tools = await adapter.get_tools()
                all_tools.extend(tools)
            except Exception:
                logger.error("MCP tool discovery failed")

        return all_tools

    async def get_server_tools(self, server_name: str) -> list[ToolDefinition]:
        """
        Get tools from a specific server.

        Args:
            server_name: Name of the server

        Returns:
            List of tools from that server
        """
        if server_name not in self._adapters:
            raise KeyError(f"Server not connected: {server_name}")

        return await self._adapters[server_name].get_tools()

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> str:
        """
        Call a tool by its full name.

        Args:
            tool_name: Full tool name (including prefix)
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        # Find the tool across all adapters
        for adapter in self._adapters.values():
            tool = await adapter.get_tool(tool_name)
            if tool is not None:
                result = await tool.execute(**arguments)
                if not isinstance(result, str):
                    raise TypeError("MCP tool result must be text")
                return result

        raise KeyError(f"Tool not found: {tool_name}")

    def get_client(self, server_name: str) -> MCPClientBase:
        """
        Get a specific client by server name.

        Args:
            server_name: Name of the server

        Returns:
            The MCP client for that server
        """
        if server_name not in self._clients:
            raise KeyError(f"Server not connected: {server_name}")
        return self._clients[server_name]

    def get_adapter(self, server_name: str) -> MCPToolAdapter:
        """
        Get a specific adapter by server name.

        Args:
            server_name: Name of the server

        Returns:
            The tool adapter for that server
        """
        if server_name not in self._adapters:
            raise KeyError(f"Server not connected: {server_name}")
        return self._adapters[server_name]

    @property
    def connected_servers(self) -> list[str]:
        """List of connected server names."""
        return list(self._clients.keys())

    @property
    def is_connected(self) -> bool:
        """Check if any servers are connected."""
        return len(self._clients) > 0

    async def __aenter__(self) -> MCPClientManager:
        """Async context manager entry."""
        if self.config.auto_connect:
            await self.connect_all()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.disconnect_all()
