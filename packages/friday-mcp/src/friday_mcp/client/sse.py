# mypy: ignore-errors
"""
SSE MCP Client.

Connects to MCP servers via Server-Sent Events (HTTP streaming).
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from typing import Any

import httpx

from friday_mcp.client.base import MCPClientBase
from friday_mcp.config import MCPServerConfig

logger = logging.getLogger(__name__)


class SSETransport:
    """Transport implementation using Server-Sent Events."""

    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int = 30,
    ):
        """
        Initialize SSE transport.

        Args:
            url: SSE endpoint URL
            headers: Optional HTTP headers
            timeout: Connection timeout in seconds
        """
        self.url = url
        self.headers = headers or {}
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._sse_response: httpx.Response | None = None
        self._message_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._connected = False
        self._receive_task: asyncio.Task[None] | None = None
        self._session_url: str | None = None

    async def connect(self) -> None:
        """Establish SSE connection."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers=self.headers,
        )

        logger.debug(f"Connecting to SSE endpoint: {self.url}")

        # Initial connection to SSE stream
        self._sse_response = await self._client.send(
            self._client.build_request("GET", self.url),
            stream=True,
        )

        self._connected = True

        # Start SSE message receiver
        self._receive_task = asyncio.create_task(self._receive_sse())

        # Wait for endpoint message
        await self._wait_for_endpoint()

    async def _wait_for_endpoint(self, timeout: float = 10.0) -> None:
        """Wait for the session endpoint URL from the SSE stream."""
        try:
            # The first message should contain the endpoint URL
            start_time = asyncio.get_event_loop().time()
            while self._session_url is None:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    raise TimeoutError("Timeout waiting for session endpoint")
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error waiting for endpoint: {e}")
            raise

    async def disconnect(self) -> None:
        """Close the SSE connection."""
        if self._receive_task:
            self._receive_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._receive_task

        if self._sse_response:
            await self._sse_response.aclose()

        if self._client:
            await self._client.aclose()

        self._connected = False
        self._session_url = None

    async def send(self, message: dict[str, Any]) -> None:
        """Send a message via HTTP POST."""
        if not self._client or not self._session_url:
            raise RuntimeError("Not connected or no session URL")

        await self._client.post(
            self._session_url,
            json=message,
        )

    async def receive(self) -> dict[str, Any]:
        """Receive a message from the SSE stream."""
        return await self._message_queue.get()

    async def _receive_sse(self) -> None:
        """Process incoming SSE events."""
        if not self._sse_response:
            return

        try:
            async for line in self._sse_response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    try:
                        message = json.loads(data)

                        # Check for endpoint message
                        if "endpoint" in message:
                            self._session_url = message["endpoint"]
                            logger.debug(
                                f"Received session endpoint: {self._session_url}"
                            )
                        else:
                            await self._message_queue.put(message)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in SSE: {data}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in SSE receive loop: {e}")

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected


class SSEMCPClient(MCPClientBase):
    """
    MCP client using SSE transport.

    Connects to remote MCP servers via HTTP Server-Sent Events.

    Example:
        client = SSEMCPClient(
            name="remote-api",
            url="https://mcp.example.com/sse"
        )
        await client.connect()
        tools = await client.list_tools()

    Or using context manager:
        async with SSEMCPClient(name="api", url="...") as client:
            tools = await client.list_tools()
    """

    def __init__(
        self,
        name: str,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: int = 30,
    ):
        """
        Initialize SSE MCP client.

        Args:
            name: Unique name for this client
            url: SSE endpoint URL
            headers: Optional HTTP headers for authentication
            timeout: Connection timeout in seconds
        """
        super().__init__(name)
        self.url = url
        self.headers = headers or {}
        self.timeout = timeout

    @classmethod
    def from_config(cls, config: MCPServerConfig) -> SSEMCPClient:
        """
        Create client from configuration.

        Args:
            config: MCP server configuration

        Returns:
            Configured SSEMCPClient instance
        """
        if not config.url:
            raise ValueError("SSE transport requires url")

        return cls(
            name=config.name,
            url=config.url,
            headers=config.headers if config.headers else None,
            timeout=config.timeout_seconds,
        )

    async def _create_transport(self) -> SSETransport:
        """Create SSE transport."""
        return SSETransport(
            url=self.url,
            headers=self.headers,
            timeout=self.timeout,
        )
