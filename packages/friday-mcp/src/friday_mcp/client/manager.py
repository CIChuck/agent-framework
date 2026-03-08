# mypy: ignore-errors
"""
MCP Client Manager.

Manages multiple MCP client connections and provides unified tool access.
"""

from __future__ import annotations

import logging
from typing import Any

from friday_mcp.client.adapter import MCPToolAdapter
from friday_mcp.client.base import MCPClientBase
from friday_mcp.client.sse import SSEMCPClient
from friday_mcp.client.stdio import StdioMCPClient
from friday_mcp.config import MCPConfig, MCPServerConfig, TransportType
from friday_mcp.protocols import ToolDefinition

logger = logging.getLogger(__name__)


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

    def __init__(self, config: MCPConfig):
        """
        Initialize client manager.

        Args:
            config: MCP configuration with server list
        """
        self.config = config
        self._clients: dict[str, MCPClientBase] = {}
        self._adapters: dict[str, MCPToolAdapter] = {}

    async def connect_all(self) -> dict[str, bool]:
        """
        Connect to all configured servers.

        Returns:
            Dict mapping server names to connection success status.
        """
        results: dict[str, bool] = {}

        for server_config in self.config.servers:
            if not server_config.enabled:
                logger.info(f"Skipping disabled server: {server_config.name}")
                results[server_config.name] = False
                continue

            try:
                client = self._create_client(server_config)
                await client.connect()

                self._clients[server_config.name] = client
                self._adapters[server_config.name] = MCPToolAdapter(
                    client,
                    prefix=f"{self.config.tool_name_prefix}{server_config.name}_",
                )

                results[server_config.name] = True
                logger.info(f"Connected to MCP server: {server_config.name}")

            except Exception as e:
                logger.error(f"Failed to connect to {server_config.name}: {e}")
                results[server_config.name] = False

        return results

    async def disconnect_all(self) -> None:
        """Disconnect from all servers."""
        for name, client in self._clients.items():
            try:
                await client.disconnect()
                logger.info(f"Disconnected from: {name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {name}: {e}")

        self._clients.clear()
        self._adapters.clear()

    async def connect(self, server_name: str) -> bool:
        """
        Connect to a specific server by name.

        Args:
            server_name: Name of the server to connect to

        Returns:
            True if connection successful
        """
        # Find the server config
        server_config = None
        for config in self.config.servers:
            if config.name == server_name:
                server_config = config
                break

        if server_config is None:
            raise KeyError(f"Server not found in config: {server_name}")

        try:
            client = self._create_client(server_config)
            await client.connect()

            self._clients[server_name] = client
            self._adapters[server_name] = MCPToolAdapter(
                client,
                prefix=f"{self.config.tool_name_prefix}{server_name}_",
            )

            logger.info(f"Connected to MCP server: {server_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to {server_name}: {e}")
            return False

    async def disconnect(self, server_name: str) -> None:
        """
        Disconnect from a specific server.

        Args:
            server_name: Name of the server to disconnect from
        """
        if server_name not in self._clients:
            return

        try:
            await self._clients[server_name].disconnect()
            logger.info(f"Disconnected from: {server_name}")
        except Exception as e:
            logger.error(f"Error disconnecting from {server_name}: {e}")
        finally:
            self._clients.pop(server_name, None)
            self._adapters.pop(server_name, None)

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

        for name, adapter in self._adapters.items():
            try:
                tools = await adapter.get_tools()
                all_tools.extend(tools)
            except Exception as e:
                logger.error(f"Failed to get tools from {name}: {e}")

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
                return await tool.execute(**arguments)

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

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect_all()
