"""Concurrent, connection-owned newline stdio without diagnostics on stdout."""

from __future__ import annotations

import asyncio
import signal
import sys

from friday_core import TelemetryInterface

from friday_mcp.server.modern import ModernToolsMCPServer
from friday_mcp.server.protocol import (
    DEFAULT_SERVER_LIMITS,
    ServerLimits,
    ServerRequest,
    ServerWireError,
    encode,
    notification_envelope,
    safe_error_id,
)


class ModernStdioMCPServer(ModernToolsMCPServer):
    def __init__(
        self,
        *,
        limits: ServerLimits = DEFAULT_SERVER_LIMITS,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        super().__init__(limits=limits, telemetry=telemetry)
        self._connection: object | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._transports: list[asyncio.BaseTransport] = []
        self._dispatchers: dict[str | int, asyncio.Task[None]] = {}

    async def stop(self) -> None:
        deadline = asyncio.get_running_loop().time() + self.limits.shutdown_seconds
        self._connection = None
        for transport in self._transports:
            transport.close()
        if self._reader is not None:
            self._reader.feed_eof()
        if self._writer is not None:
            self._writer.close()
        for task in tuple(self._dispatchers.values()):
            task.cancel()
        await super().stop()
        pending = tuple(self._dispatchers.values())
        if pending:
            _, unfinished = await asyncio.wait(
                pending, timeout=max(0, deadline - asyncio.get_running_loop().time())
            )
            if unfinished:
                raise TimeoutError("MCP stdio shutdown incomplete")
        if self._writer is not None:
            remaining = deadline - asyncio.get_running_loop().time()
            try:
                async with asyncio.timeout(max(0, remaining)):
                    await self._writer.wait_closed()
            except (OSError, ConnectionError):
                pass
            self._writer = None

    async def serve(
        self,
        *,
        reader: asyncio.StreamReader | None = None,
        writer: asyncio.StreamWriter | None = None,
    ) -> None:
        if (
            self._connection is not None
            or self._dispatchers
            or self._writer is not None
        ):
            raise RuntimeError("MCP stdio connection already active")
        super().start()
        connection = object()
        self._connection = connection
        lock = asyncio.Lock()
        loop = asyncio.get_running_loop()
        installed_signal = False
        native = reader is None and writer is None
        if (reader is None) != (writer is None):
            self._connection = None
            raise ValueError("MCP stdio requires both streams")

        async def write_response(response: object, deadline: float) -> None:
            if writer is None or self._connection is not connection:
                return
            remaining = deadline - loop.time()
            if remaining <= 0:
                return
            try:
                raw = (
                    encode(
                        response, self.limits, byte_limit=self.limits.result_bytes - 1
                    )
                    + b"\n"
                )
                async with asyncio.timeout(remaining):
                    async with lock:
                        if self._connection is connection:
                            writer.write(raw)
                            await writer.drain()
            except (OSError, ConnectionError, TimeoutError):
                self._connection = None
                if reader is not None:
                    reader.feed_eof()

        async def dispatch(request: ServerRequest, raw: bytes, deadline: float) -> None:
            try:
                response = await self.handle(raw, deadline=deadline)
                await write_response(response, deadline)
            finally:
                task = asyncio.current_task()
                if (
                    request.request_id is not None
                    and self._dispatchers.get(request.request_id) is task
                ):
                    self._dispatchers.pop(request.request_id, None)

        async def line(raw: bytes) -> None:
            deadline = loop.time() + self.limits.timeout_seconds
            try:
                request = ServerRequest.parse(raw, self.limits)
                if request.request_id is None:
                    if request.method == "notifications/cancelled":
                        target = request.params.get("requestId")
                        if isinstance(target, (str, int)) and not isinstance(
                            target, bool
                        ):
                            task = self._dispatchers.get(target)
                            if task is not None:
                                task.cancel()
                        return
                    return
                if request.request_id in self._dispatchers:
                    raise ServerWireError(-32600)
                if len(self._dispatchers) >= self.limits.active_requests:
                    raise ServerWireError(-32603)
                self._dispatchers[request.request_id] = asyncio.create_task(
                    dispatch(request, raw, deadline)
                )
            except ServerWireError as error:
                if notification_envelope(raw, self.limits):
                    return
                await write_response(
                    error.response(safe_error_id(raw, self.limits)), deadline
                )

        try:
            if native:
                reader = asyncio.StreamReader(limit=self.limits.request_bytes + 1)
                protocol = asyncio.StreamReaderProtocol(reader)
                transport, _ = await loop.connect_read_pipe(
                    lambda: protocol, sys.stdin.buffer
                )
                self._transports.append(transport)
                out_protocol = asyncio.StreamReaderProtocol(asyncio.StreamReader())
                out_transport, _ = await loop.connect_write_pipe(
                    lambda: out_protocol, sys.stdout.buffer
                )
                self._transports.append(out_transport)
                writer = asyncio.StreamWriter(out_transport, out_protocol, None, loop)

                def terminate() -> None:
                    if reader is not None:
                        reader.feed_eof()
                    self._connection = None

                loop.add_signal_handler(signal.SIGTERM, terminate)
                installed_signal = True
            if reader is None or writer is None:
                raise RuntimeError("MCP stdio stream unavailable")
            self._reader = reader
            self._writer = writer
            frame = bytearray()
            oversized = False
            while self._connection is connection:
                chunk = await reader.read(min(4096, self.limits.request_bytes))
                if not chunk:
                    if frame or oversized:
                        await write_response(
                            ServerWireError(-32700).response(),
                            loop.time() + self.limits.timeout_seconds,
                        )
                    break
                for byte in chunk:
                    if byte == 10:
                        if oversized:
                            await write_response(
                                ServerWireError(-32600).response(),
                                loop.time() + self.limits.timeout_seconds,
                            )
                        else:
                            await line(bytes(frame))
                        frame.clear()
                        oversized = False
                    elif not oversized:
                        if len(frame) == self.limits.request_bytes:
                            frame.clear()
                            oversized = True
                        else:
                            frame.append(byte)
                # Start admitted operations while keeping cancellation reads responsive.
                await asyncio.sleep(0)
        except (OSError, ConnectionError):
            # Fixed diagnostics only; never stringify peer or I/O exceptions.
            if native:
                sys.stderr.write("MCP stdio transport failed\n")
        finally:
            if installed_signal:
                loop.remove_signal_handler(signal.SIGTERM)
            await self.stop()
            self._reader = None
            self._transports = []
