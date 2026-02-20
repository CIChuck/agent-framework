"""
MCP Client Base Implementation.

Abstract base class providing common MCP client functionality.
Transport-agnostic implementation.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any

from friday_mcp.protocols import MCPTransport
from friday_mcp.utils.schema import extract_text_content

logger = logging.getLogger(__name__)


class MCPError(Exception):
    """MCP protocol error."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"MCP Error {code}: {message}")


class MCPClientBase(ABC):
    """
    Abstract base class for MCP clients.

    Implements the MCP protocol logic while delegating
    transport details to subclasses.
    """

    # MCP Protocol Version
    PROTOCOL_VERSION = "2024-11-05"

    def __init__(self, name: str):
        """
        Initialize MCP client.

        Args:
            name: Unique name for this client connection
        """
        self.name = name
        self._transport: MCPTransport | None = None
        self._server_capabilities: dict[str, Any] = {}
        self._server_info: dict[str, Any] = {}
        self._client_info = {"name": "friday-mcp", "version": "0.1.0"}
        self._pending_requests: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._connected = False
        self._receive_task: asyncio.Task[None] | None = None

    @abstractmethod
    async def _create_transport(self) -> MCPTransport:
        """Create the transport instance. Implemented by subclasses."""
        pass

    async def connect(self) -> None:
        """
        Establish connection and perform MCP handshake.
        """
        if self._connected:
            return

        logger.info(f"Connecting to MCP server: {self.name}")

        # Create and connect transport
        self._transport = await self._create_transport()
        await self._transport.connect()

        # Start message receiver
        self._receive_task = asyncio.create_task(self._receive_loop())

        # Perform MCP handshake
        await self._initialize()
        self._connected = True

        logger.info(
            f"Connected to MCP server: {self.name} "
            f"(capabilities: {list(self._server_capabilities.keys())})"
        )

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if not self._connected:
            return

        logger.info(f"Disconnecting from MCP server: {self.name}")

        if self._receive_task:
            self._receive_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._receive_task

        if self._transport:
            await self._transport.disconnect()

        self._connected = False
        self._server_capabilities = {}

    async def _initialize(self) -> None:
        """Perform MCP initialize handshake."""
        response = await self._request(
            "initialize",
            {
                "protocolVersion": self.PROTOCOL_VERSION,
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {},
                },
                "clientInfo": self._client_info,
            },
        )

        self._server_capabilities = response.get("capabilities", {})
        self._server_info = response.get("serverInfo", {})

        # Send initialized notification
        await self._notify("notifications/initialized", {})

    async def _request(
        self,
        method: str,
        params: dict[str, Any],
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """Send a JSON-RPC request and wait for response."""
        if not self._transport:
            raise RuntimeError("Not connected")

        request_id = str(uuid.uuid4())

        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }

        future: asyncio.Future[dict[str, Any]] = (
            asyncio.get_event_loop().create_future()
        )
        self._pending_requests[request_id] = future

        try:
            await self._transport.send(message)
            response = await asyncio.wait_for(future, timeout=timeout)

            if "error" in response:
                raise MCPError(
                    response["error"].get("code", -1),
                    response["error"].get("message", "Unknown error"),
                )

            return response.get("result", {})
        finally:
            self._pending_requests.pop(request_id, None)

    async def _notify(self, method: str, params: dict[str, Any]) -> None:
        """Send a JSON-RPC notification (no response expected)."""
        if not self._transport:
            raise RuntimeError("Not connected")

        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }
        await self._transport.send(message)

    async def _receive_loop(self) -> None:
        """Continuously receive messages from the transport."""
        if not self._transport:
            return

        while True:
            try:
                message = await self._transport.receive()
                await self._handle_message(message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                # Don't break on errors, try to continue receiving

    async def _handle_message(self, message: dict[str, Any]) -> None:
        """Handle an incoming message."""
        msg_id = message.get("id")

        if msg_id is not None and msg_id in self._pending_requests:
            # Response to a request we sent
            future = self._pending_requests[msg_id]
            if not future.done():
                future.set_result(message)
        elif "method" in message:
            # Notification or request from server
            await self._handle_server_message(message)

    async def _handle_server_message(self, message: dict[str, Any]) -> None:
        """Handle notifications/requests from the server."""
        method = message.get("method", "")
        # Handle server-initiated messages (e.g., progress, logging)
        logger.debug(f"Server message: {method}")

    # --- MCP API Methods ---

    async def list_tools(self) -> list[dict[str, Any]]:
        """
        Get available tools from the server.

        Returns:
            List of tool definitions with name, description, inputSchema.
        """
        if "tools" not in self._server_capabilities:
            return []

        response = await self._request("tools/list", {})
        return response.get("tools", [])

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> str:
        """
        Execute a tool on the server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result as string
        """
        response = await self._request(
            "tools/call",
            {
                "name": name,
                "arguments": arguments,
            },
        )

        return extract_text_content(response)

    async def list_prompts(self) -> list[dict[str, Any]]:
        """
        Get available prompts from the server.

        Returns:
            List of prompt definitions.
        """
        if "prompts" not in self._server_capabilities:
            return []

        response = await self._request("prompts/list", {})
        return response.get("prompts", [])

    async def get_prompt(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get a specific prompt with optional arguments.

        Args:
            name: Prompt name
            arguments: Optional prompt arguments

        Returns:
            Prompt content with messages.
        """
        return await self._request(
            "prompts/get",
            {
                "name": name,
                "arguments": arguments or {},
            },
        )

    async def list_resources(self) -> list[dict[str, Any]]:
        """
        Get available resources from the server.

        Returns:
            List of resource definitions.
        """
        if "resources" not in self._server_capabilities:
            return []

        response = await self._request("resources/list", {})
        return response.get("resources", [])

    async def read_resource(self, uri: str) -> dict[str, Any]:
        """
        Read a specific resource by URI.

        Args:
            uri: Resource URI

        Returns:
            Resource contents.
        """
        return await self._request("resources/read", {"uri": uri})

    @property
    def server_capabilities(self) -> dict[str, Any]:
        """Get negotiated server capabilities."""
        return self._server_capabilities

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected

    async def __aenter__(self) -> MCPClientBase:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()
