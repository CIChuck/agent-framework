# mypy: ignore-errors
"""
MCP Server Base Implementation.

Abstract base class for MCP servers.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class MCPServerBase(ABC):
    """
    Abstract base class for MCP servers.

    Handles MCP protocol logic while delegating transport to subclasses.
    """

    PROTOCOL_VERSION = "2024-11-05"

    def __init__(self, name: str = "friday-mcp-server"):
        """
        Initialize MCP server.

        Args:
            name: Server name for identification
        """
        self.name = name
        self._tools: dict[str, dict[str, Any]] = {}
        self._tool_handlers: dict[str, Callable[..., Any]] = {}
        self._prompts: dict[str, dict[str, Any]] = {}
        self._prompt_handlers: dict[str, Callable[..., Any]] = {}
        self._resources: dict[str, dict[str, Any]] = {}
        self._resource_handlers: dict[str, Callable[..., Any]] = {}
        self._running = False
        self._client_capabilities: dict[str, Any] = {}

    @abstractmethod
    async def start(self) -> None:
        """Start the server transport."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the server transport."""
        pass

    async def handle_request(
        self,
        request: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Handle an incoming JSON-RPC request.

        Routes to appropriate handler based on method.

        Args:
            request: JSON-RPC request message

        Returns:
            JSON-RPC response message
        """
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            result = await self._dispatch(method, params)

            if request_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result,
                }
            return {}  # Notification, no response

        except Exception as e:
            logger.error(f"Error handling {method}: {e}")
            if request_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": str(e),
                    },
                }
            return {}

    async def _dispatch(
        self,
        method: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Dispatch method to handler."""
        handlers: dict[str, Callable[[dict[str, Any]], Any]] = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "prompts/list": self._handle_prompts_list,
            "prompts/get": self._handle_prompts_get,
            "resources/list": self._handle_resources_list,
            "resources/read": self._handle_resources_read,
        }

        handler = handlers.get(method)
        if not handler:
            # Handle notifications silently
            if method.startswith("notifications/"):
                return {}
            raise ValueError(f"Unknown method: {method}")

        return await handler(params)

    async def _handle_initialize(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle initialize request."""
        self._client_capabilities = params.get("capabilities", {})

        capabilities: dict[str, Any] = {}
        if self._tools:
            capabilities["tools"] = {}
        if self._prompts:
            capabilities["prompts"] = {}
        if self._resources:
            capabilities["resources"] = {}

        return {
            "protocolVersion": self.PROTOCOL_VERSION,
            "capabilities": capabilities,
            "serverInfo": {
                "name": self.name,
                "version": "0.1.0",
            },
        }

    async def _handle_tools_list(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle tools/list request."""
        return {"tools": list(self._tools.values())}

    async def _handle_tools_call(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle tools/call request."""
        name = params.get("name")
        arguments = params.get("arguments", {})

        if name not in self._tool_handlers:
            raise ValueError(f"Unknown tool: {name}")

        handler = self._tool_handlers[name]

        # Execute handler (supports async)
        if asyncio.iscoroutinefunction(handler):
            result = await handler(**arguments)
        else:
            result = handler(**arguments)

        return {
            "content": [{"type": "text", "text": str(result)}],
        }

    async def _handle_prompts_list(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle prompts/list request."""
        return {"prompts": list(self._prompts.values())}

    async def _handle_prompts_get(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle prompts/get request."""
        name = params.get("name")
        arguments = params.get("arguments", {})

        if name not in self._prompt_handlers:
            raise ValueError(f"Unknown prompt: {name}")

        handler = self._prompt_handlers[name]

        if asyncio.iscoroutinefunction(handler):
            result = await handler(**arguments)
        else:
            result = handler(**arguments)

        return result

    async def _handle_resources_list(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle resources/list request."""
        return {"resources": list(self._resources.values())}

    async def _handle_resources_read(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle resources/read request."""
        uri = params.get("uri")

        if uri not in self._resource_handlers:
            raise ValueError(f"Unknown resource: {uri}")

        handler = self._resource_handlers[uri]

        if asyncio.iscoroutinefunction(handler):
            result = await handler()
        else:
            result = handler()

        return result

    # --- Registration Methods ---

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable[..., Any],
    ) -> None:
        """
        Register a tool.

        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON Schema for tool parameters
            handler: Function to execute when tool is called
        """
        self._tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
        }
        self._tool_handlers[name] = handler
        logger.debug(f"Registered tool: {name}")

    def register_prompt(
        self,
        name: str,
        description: str,
        arguments: list[dict[str, Any]] | None,
        handler: Callable[..., Any],
    ) -> None:
        """
        Register a prompt.

        Args:
            name: Prompt name
            description: Prompt description
            arguments: Prompt argument definitions
            handler: Function to get prompt content
        """
        self._prompts[name] = {
            "name": name,
            "description": description,
            "arguments": arguments or [],
        }
        self._prompt_handlers[name] = handler
        logger.debug(f"Registered prompt: {name}")

    def register_resource(
        self,
        uri: str,
        name: str,
        description: str,
        mime_type: str,
        handler: Callable[..., Any],
    ) -> None:
        """
        Register a resource.

        Args:
            uri: Resource URI
            name: Resource name
            description: Resource description
            mime_type: Resource MIME type
            handler: Function to read resource content
        """
        self._resources[uri] = {
            "uri": uri,
            "name": name,
            "description": description,
            "mimeType": mime_type,
        }
        self._resource_handlers[uri] = handler
        logger.debug(f"Registered resource: {uri}")

    def unregister_tool(self, name: str) -> None:
        """Unregister a tool."""
        self._tools.pop(name, None)
        self._tool_handlers.pop(name, None)

    def unregister_prompt(self, name: str) -> None:
        """Unregister a prompt."""
        self._prompts.pop(name, None)
        self._prompt_handlers.pop(name, None)

    def unregister_resource(self, uri: str) -> None:
        """Unregister a resource."""
        self._resources.pop(uri, None)
        self._resource_handlers.pop(uri, None)

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running

    @property
    def tool_count(self) -> int:
        """Number of registered tools."""
        return len(self._tools)

    @property
    def prompt_count(self) -> int:
        """Number of registered prompts."""
        return len(self._prompts)

    @property
    def resource_count(self) -> int:
        """Number of registered resources."""
        return len(self._resources)
