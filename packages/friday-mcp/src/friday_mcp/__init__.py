# mypy: ignore-errors
"""
Friday MCP Integration Package.

Provides bidirectional Model Context Protocol (MCP) integration:
- MCP Client: Connect to external MCP servers and consume their tools
- MCP Server: Expose Friday capabilities (agent or tools) via MCP

Example (Client - connecting to MCP servers):
    from friday_mcp import MCPClientManager, MCPConfig, MCPServerConfig

    config = MCPConfig(
        servers=[
            MCPServerConfig(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
            )
        ]
    )

    async with MCPClientManager(config) as manager:
        tools = await manager.get_all_tools()
        # Register tools with Friday's registry

Example (Server - exposing Friday via MCP):
    from friday_mcp import StdioMCPServer, MCPServerSettings
    from friday_mcp.server.agent_mode import configure_agent_mode

    server = StdioMCPServer()
    configure_agent_mode(server, agent, profile, settings)
    await server.start()
"""

from friday_mcp.config import (
    MCPConfig,
    MCPServerConfig,
    MCPServerSettings,
    ServerMode,
    TransportType,
)
from friday_mcp.protocols import (
    MCPClient,
    MCPServer,
    MCPTransport,
    ToolAdapter,
    ToolDefinition,
)

__version__ = "0.1.0a2"

__all__ = [
    # Protocols
    "MCPClient",
    "MCPServer",
    "MCPTransport",
    "ToolDefinition",
    "ToolAdapter",
    # Configuration
    "MCPConfig",
    "MCPServerConfig",
    "MCPServerSettings",
    "TransportType",
    "ServerMode",
]


# Lazy imports for client/server implementations
def __getattr__(name: str):
    """Lazy import client and server implementations."""
    if name == "MCPClientManager":
        from friday_mcp.client.manager import MCPClientManager

        return MCPClientManager
    if name == "StdioMCPClient":
        from friday_mcp.client.stdio import StdioMCPClient

        return StdioMCPClient
    if name == "SSEMCPClient":
        from friday_mcp.client.sse import SSEMCPClient

        return SSEMCPClient
    if name == "MCPToolAdapter":
        from friday_mcp.client.adapter import MCPToolAdapter

        return MCPToolAdapter
    if name == "StdioMCPServer":
        from friday_mcp.server.stdio import StdioMCPServer

        return StdioMCPServer
    if name == "SSEMCPServer":
        from friday_mcp.server.sse import SSEMCPServer

        return SSEMCPServer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
