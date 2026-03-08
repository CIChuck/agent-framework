# mypy: ignore-errors
"""
MCP Integration Protocols.

Defines abstract interfaces for MCP client and server functionality.
Tool protocols are imported from friday-core for unified definitions.

Ref: Model Context Protocol Specification (https://modelcontextprotocol.io)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

# Import unified tool protocols from friday-core
from friday_core.interfaces.tools import (
    SchemaFormat,
    ToolAdapter,
    ToolDefinition,
)

__all__ = [
    # Re-exported from friday-core
    "SchemaFormat",
    "ToolDefinition",
    "ToolAdapter",
    # MCP-specific protocols
    "MCPTransport",
    "MCPClient",
    "MCPServer",
]


@runtime_checkable
class MCPTransport(Protocol):
    """
    Abstract transport layer for MCP communication.

    Implementations handle the actual communication (stdio, SSE, etc.)
    while the client/server logic remains transport-agnostic.
    """

    async def connect(self) -> None:
        """Establish connection to the transport."""
        ...

    async def disconnect(self) -> None:
        """Close the transport connection."""
        ...

    async def send(self, message: dict[str, Any]) -> None:
        """Send a JSON-RPC message."""
        ...

    async def receive(self) -> dict[str, Any]:
        """Receive a JSON-RPC message."""
        ...

    @property
    def is_connected(self) -> bool:
        """Check if transport is connected."""
        ...


@runtime_checkable
class MCPClient(Protocol):
    """
    Client for connecting to external MCP servers.

    Enables Friday to consume tools from federated MCP servers,
    adapting them to Friday's ToolDefinition protocol.
    """

    async def connect(self) -> None:
        """
        Establish connection to the MCP server.

        Performs:
        - Transport connection
        - Protocol handshake (initialize/initialized)
        - Capability negotiation
        """
        ...

    async def disconnect(self) -> None:
        """Gracefully disconnect from the MCP server."""
        ...

    async def list_tools(self) -> list[dict[str, Any]]:
        """
        Get available tools from the MCP server.

        Returns:
            List of MCP tool definitions with name, description, inputSchema.
        """
        ...

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> str:
        """
        Execute a tool on the MCP server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result as string
        """
        ...

    async def list_prompts(self) -> list[dict[str, Any]]:
        """Get available prompts from the MCP server."""
        ...

    async def get_prompt(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get a specific prompt with optional arguments."""
        ...

    async def list_resources(self) -> list[dict[str, Any]]:
        """Get available resources from the MCP server."""
        ...

    async def read_resource(self, uri: str) -> dict[str, Any]:
        """Read a specific resource by URI."""
        ...

    @property
    def server_capabilities(self) -> dict[str, Any]:
        """Get negotiated server capabilities."""
        ...


@runtime_checkable
class MCPServer(Protocol):
    """
    Server for exposing Friday capabilities via MCP.

    Enables external MCP clients to interact with Friday's
    agent or tool registry.
    """

    async def start(self) -> None:
        """
        Start the MCP server.

        Begins listening for incoming connections and requests.
        """
        ...

    async def stop(self) -> None:
        """Stop the MCP server gracefully."""
        ...

    async def handle_request(
        self,
        request: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Handle an incoming JSON-RPC request.

        Routes to appropriate handler based on method.
        """
        ...

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable[..., Any],
    ) -> None:
        """Register a tool to expose via MCP."""
        ...

    def register_prompt(
        self,
        name: str,
        description: str,
        arguments: list[dict[str, Any]] | None,
        handler: Callable[..., Any],
    ) -> None:
        """Register a prompt template."""
        ...

    def register_resource(
        self,
        uri: str,
        name: str,
        description: str,
        mime_type: str,
        handler: Callable[..., Any],
    ) -> None:
        """Register a resource."""
        ...

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        ...
