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

# Per teardown attempt: reader cancellation (1), graceful exit (5), forced
# exit (2), pipe EOF (2), and failed-attempt task cancellation (1) = 11 seconds.
# asyncio.wait bounds even cancellation-resistant tasks without abandoning
# their references. These budgets do not change connection or RPC deadlines.
_READER_STOP_SECONDS = 1.0
_GRACEFUL_EXIT_SECONDS = 5.0
_FORCED_EXIT_SECONDS = 2.0
_PIPE_EOF_SECONDS = 2.0
_FAILED_TASK_STOP_SECONDS = 1.0
_DISCARD_CHUNK_BYTES = 4096


class StdioTransport:
    """Transport implementation using subprocess stdio."""

    def __init__(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
    ) -> None:
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
        self._stdout_read_task: asyncio.Task[bytes] | None = None
        self._stdout_drain_task: asyncio.Task[None] | None = None
        self._process_wait_task: asyncio.Task[int] | None = None
        self._cleanup_task: asyncio.Task[None] | None = None

    async def connect(self) -> None:
        """Start the subprocess."""
        if self.is_connected:
            return
        if self._process is not None:
            await self.disconnect()
        env = os.environ.copy()
        if self.env:
            env.update(self.env)

        logger.debug("Starting MCP stdio subprocess")

        spawn = asyncio.create_task(
            asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=self.cwd,
            )
        )
        try:
            self._process = await asyncio.shield(spawn)
        except asyncio.CancelledError:
            # If cancellation races process creation, acquire ownership before
            # re-raising so the public cleanup path can reap the child.
            self._process = await spawn
            await self.disconnect()
            raise
        self._connected = True

        self._stderr_task = asyncio.create_task(
            self._log_stderr(), name="mcp-stdio-stderr-drain"
        )

    async def disconnect(self) -> None:
        """Drain and reap within an 11-second attempt budget, retaining failures.

        Caller cancellation propagates while the explicitly owned cleanup task
        continues. A later disconnect joins it or retries an incomplete attempt.
        Success requires process exit, both output EOFs, and settled tasks.
        """
        self._connected = False
        cleanup = self._cleanup_task
        if cleanup is None or cleanup.done():
            if cleanup is not None and not cleanup.cancelled():
                cleanup.exception()
            if self._process is None:
                self._cleanup_task = None
                return
            cleanup = asyncio.create_task(
                self._finish_disconnect(), name="mcp-stdio-cleanup"
            )
            self._cleanup_task = cleanup
            cleanup.add_done_callback(self._cleanup_finished)
        await asyncio.shield(cleanup)

    def _cleanup_finished(self, task: asyncio.Task[None]) -> None:
        # Retrieve failures even if the caller was cancelled. Failed cleanup
        # remains inspectably owned; only successful cleanup clears its slot.
        if (
            not task.cancelled()
            and task.exception() is None
            and self._cleanup_task is task
        ):
            self._cleanup_task = None

    async def _finish_disconnect(self) -> None:
        process = self._process
        if process is None:
            return
        try:
            reader = self._stdout_read_task
            if reader is not None:
                reader.cancel()
                stopped_readers, pending_readers = await asyncio.wait(
                    (reader,), timeout=_READER_STOP_SECONDS
                )
                if pending_readers:
                    raise RuntimeError("MCP stdio cleanup incomplete")
                for task in stopped_readers:
                    if not task.cancelled():
                        task.exception()
                self._stdout_read_task = None

            # The protocol reader has stopped: take over stdout without
            # competing readers. Keep stderr draining through terminate/kill.
            self._stdout_drain_task = self._ensure_drain(
                process.stdout, self._stdout_drain_task, "mcp-stdio-stdout-drain"
            )
            self._stderr_task = self._ensure_drain(
                process.stderr, self._stderr_task, "mcp-stdio-stderr-drain"
            )
            if process.stdin is not None:
                process.stdin.close()
            if process.returncode is None:
                with contextlib.suppress(ProcessLookupError):
                    process.terminate()
            if self._process_wait_task is None or self._process_wait_task.done():
                self._process_wait_task = asyncio.create_task(
                    process.wait(), name="mcp-stdio-process-wait"
                )
            wait_task = self._process_wait_task
            done, pending = await asyncio.wait(
                (wait_task,), timeout=_GRACEFUL_EXIT_SECONDS
            )
            if pending:
                with contextlib.suppress(ProcessLookupError):
                    process.kill()
                done, pending = await asyncio.wait(
                    (wait_task,), timeout=_FORCED_EXIT_SECONDS
                )
            if pending:
                raise RuntimeError("MCP stdio cleanup incomplete")
            wait_task.result()
            drains = {
                task
                for task in (self._stdout_drain_task, self._stderr_task)
                if task is not None
            }
            if drains:
                done_drains, pending_drains = await asyncio.wait(
                    drains, timeout=_PIPE_EOF_SECONDS
                )
                if pending_drains:
                    raise RuntimeError("MCP stdio cleanup incomplete")
                for drain in done_drains:
                    drain.result()
        except asyncio.CancelledError:
            await self._stop_owned_io_tasks()
            raise
        except Exception:
            await self._stop_owned_io_tasks()
            raise RuntimeError("MCP stdio cleanup incomplete") from None
        self._stdout_drain_task = None
        self._stderr_task = None
        self._process_wait_task = None
        self._process = None

    @staticmethod
    def _ensure_drain(
        stream: asyncio.StreamReader | None,
        task: asyncio.Task[None] | None,
        name: str,
    ) -> asyncio.Task[None] | None:
        if stream is None:
            return None
        if task is not None:
            if not task.done():
                return task
            if not task.cancelled() and task.exception() is None:
                return task
        return asyncio.create_task(StdioTransport._discard_stream(stream), name=name)

    async def _stop_owned_io_tasks(self) -> None:
        tasks: set[asyncio.Task[object]] = {
            task
            for task in (
                self._stdout_read_task,
                self._stdout_drain_task,
                self._stderr_task,
                self._process_wait_task,
            )
            if task is not None
        }
        if not tasks:
            return
        for task in tasks:
            if not task.done():
                task.cancel()
        done, _ = await asyncio.wait(tasks, timeout=_FAILED_TASK_STOP_SECONDS)
        for task in done:
            if not task.cancelled():
                task.exception()
        # Do not clear process or task slots on an incomplete attempt. Pending
        # tasks stay owned, and retries never start a competing stream reader.

    @staticmethod
    async def _discard_stream(stream: asyncio.StreamReader) -> None:
        while await stream.read(_DISCARD_CHUNK_BYTES):
            pass

    async def send(self, message: dict[str, Any]) -> None:
        """Send a message via stdin."""
        if not self._connected or not self._process or not self._process.stdin:
            raise RuntimeError("Not connected")

        data = json.dumps(message) + "\n"
        self._process.stdin.write(data.encode())
        await self._process.stdin.drain()

    async def receive(self) -> dict[str, Any]:
        """Receive a message from stdout."""
        if not self._connected or not self._process or not self._process.stdout:
            raise RuntimeError("Not connected")

        if self._stdout_read_task is not None:
            raise RuntimeError("MCP stdout reader already active")
        reader = asyncio.create_task(
            self._process.stdout.readline(), name="mcp-stdio-stdout-reader"
        )
        self._stdout_read_task = reader
        try:
            line = await reader
        finally:
            if reader.done() and self._stdout_read_task is reader:
                self._stdout_read_task = None
        if not line:
            raise EOFError("Process closed stdout")

        message = json.loads(line.decode())
        if not isinstance(message, dict):
            raise ValueError("Invalid MCP message object")
        return message

    async def _log_stderr(self) -> None:
        """Drain stderr without logging or persisting untrusted content."""
        if not self._process or not self._process.stderr:
            return

        await self._discard_stream(self._process.stderr)

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return (
            self._connected
            and self._process is not None
            and self._process.returncode is None
        )


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
    ) -> None:
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

        client = cls(
            name=config.name,
            command=config.command,
            args=config.args,
            env=config.env if config.env else None,
            cwd=config.cwd,
        )
        client.request_timeout_seconds = float(config.timeout_seconds)
        return client

    async def _create_transport(self) -> StdioTransport:
        """Create stdio transport."""
        return StdioTransport(
            command=self.command,
            args=self.args,
            env=self.env,
            cwd=self.cwd,
        )
