# mypy: ignore-errors
"""
Stdio MCP Server.

Exposes Friday via stdio (for CLI integration).
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from friday_mcp.server.base import MCPServerBase

logger = logging.getLogger(__name__)


class StdioMCPServer(MCPServerBase):
    """
    MCP server using stdio transport.

    Reads from stdin and writes to stdout for integration
    with MCP clients that spawn subprocesses.

    Example:
        server = StdioMCPServer()

        # Register tools
        server.register_tool(
            name="greet",
            description="Greet someone",
            input_schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            },
            handler=lambda name: f"Hello, {name}!"
        )

        # Start server (blocks until stdin closes)
        await server.start()
    """

    def __init__(self, name: str = "friday-mcp-stdio"):
        """
        Initialize stdio MCP server.

        Args:
            name: Server name for identification
        """
        super().__init__(name)
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def start(self) -> None:
        """
        Start reading from stdin.

        This method blocks until stdin is closed or stop() is called.
        """
        self._running = True
        logger.info(f"Starting stdio MCP server: {self.name}")

        # Set up async stdin reader
        loop = asyncio.get_event_loop()
        self._reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(self._reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        while self._running:
            try:
                line = await self._reader.readline()
                if not line:
                    logger.debug("stdin closed")
                    break

                try:
                    request = json.loads(line.decode())
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    continue

                response = await self.handle_request(request)

                if response:
                    await self._write_response(response)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing request: {e}")

        self._running = False
        logger.info("Stdio MCP server stopped")

    async def stop(self) -> None:
        """Stop the server."""
        self._running = False
        logger.info("Stopping stdio MCP server")

    async def _write_response(self, response: dict[str, Any]) -> None:
        """Write response to stdout."""
        data = json.dumps(response) + "\n"
        sys.stdout.write(data)
        sys.stdout.flush()

    async def run_forever(self) -> None:
        """
        Run the server until interrupted.

        Convenience method that handles KeyboardInterrupt.
        """
        try:
            await self.start()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await self.stop()
