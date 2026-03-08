# mypy: ignore-errors
"""
Stdio MCP Client.

Connects to MCP servers via subprocess stdio transport.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
from pathlib import Path
from typing import Any

from friday_mcp.client.base import MCPClientBase
from friday_mcp.config import MCPServerConfig

logger = logging.getLogger(__name__)


class StdioTransport:
    """Transport implementation using subprocess stdio."""

    def __init__(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
    ):
        """
        Initialize stdio transport.

        Args:
            command: Command to execute
            args: Command arguments
            env: Additional environment variables
            cwd: Working directory
        """
        self.command = command
        self.args = args or []
        self.env = env
        self.cwd = cwd
        self._process: asyncio.subprocess.Process | None = None
        self._connected = False
        self._stderr_task: asyncio.Task[None] | None = None

    async def connect(self) -> None:
        """Start the subprocess."""
        env = os.environ.copy()
        if self.env:
            env.update(self.env)

        logger.debug(f"Starting subprocess: {self.command} {' '.join(self.args)}")

        self._process = await asyncio.create_subprocess_exec(
            self.command,
            *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd=self.cwd,
        )
        self._connected = True

        # Start stderr logging task
        self._stderr_task = asyncio.create_task(self._log_stderr())

    async def disconnect(self) -> None:
        """Terminate the subprocess."""
        if self._stderr_task:
            self._stderr_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._stderr_task

        if self._process:
            self._process.terminate()
            try:
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self._process.kill()
                await self._process.wait()
            self._process = None

        self._connected = False

    async def send(self, message: dict[str, Any]) -> None:
        """Send a message via stdin."""
        if not self._process or not self._process.stdin:
            raise RuntimeError("Not connected")

        data = json.dumps(message) + "\n"
        self._process.stdin.write(data.encode())
        await self._process.stdin.drain()

    async def receive(self) -> dict[str, Any]:
        """Receive a message from stdout."""
        if not self._process or not self._process.stdout:
            raise RuntimeError("Not connected")

        line = await self._process.stdout.readline()
        if not line:
            raise EOFError("Process closed stdout")

        return json.loads(line.decode())

    async def _log_stderr(self) -> None:
        """Log stderr output from the subprocess."""
        if not self._process or not self._process.stderr:
            return

        while True:
            try:
                line = await self._process.stderr.readline()
                if not line:
                    break
                logger.debug(f"MCP server stderr: {line.decode().strip()}")
            except asyncio.CancelledError:
                break

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected and self._process is not None


class StdioMCPClient(MCPClientBase):
    """
    MCP client using stdio transport.

    Spawns an MCP server as a subprocess and communicates via stdin/stdout.

    Example:
        client = StdioMCPClient(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/path"]
        )
        await client.connect()
        tools = await client.list_tools()
        result = await client.call_tool("read_file", {"path": "/tmp/test.txt"})
        await client.disconnect()

    Or using context manager:
        async with StdioMCPClient(name="fs", command="...") as client:
            tools = await client.list_tools()
    """

    def __init__(
        self,
        name: str,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
    ):
        """
        Initialize stdio MCP client.

        Args:
            name: Unique name for this client
            command: Command to run (e.g., "npx", "python", "node")
            args: Command arguments
            env: Additional environment variables
            cwd: Working directory for the subprocess
        """
        super().__init__(name)
        self.command = command
        self.args = args or []
        self.env = env
        self.cwd = cwd

    @classmethod
    def from_config(cls, config: MCPServerConfig) -> StdioMCPClient:
        """
        Create client from configuration.

        Args:
            config: MCP server configuration

        Returns:
            Configured StdioMCPClient instance
        """
        if not config.command:
            raise ValueError("stdio transport requires command")

        return cls(
            name=config.name,
            command=config.command,
            args=config.args,
            env=config.env if config.env else None,
            cwd=config.cwd,
        )

    async def _create_transport(self) -> StdioTransport:
        """Create stdio transport."""
        return StdioTransport(
            command=self.command,
            args=self.args,
            env=self.env,
            cwd=self.cwd,
        )
