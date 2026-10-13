"""Concurrent, connection-owned newline stdio without diagnostics on stdout."""

from __future__ import annotations

import asyncio
import signal
import sys
from contextlib import suppress
from dataclasses import dataclass, field

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


@dataclass(eq=False)
class _Connection:
    serving: asyncio.Task[object]
    reader: asyncio.StreamReader | None
    writer: asyncio.StreamWriter | None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    transports: list[asyncio.BaseTransport] = field(default_factory=list)
    dispatchers: dict[str | int, asyncio.Task[None]] = field(default_factory=dict)
    outputs: set[asyncio.Task[None]] = field(default_factory=set)
    closing: bool = False
    signal_owned: bool = False
    close_wait: asyncio.Task[None] | None = None
    settled: bool = False


class ModernStdioMCPServer(ModernToolsMCPServer):
    def __init__(
        self,
        *,
        limits: ServerLimits = DEFAULT_SERVER_LIMITS,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        super().__init__(limits=limits, telemetry=telemetry)
        self._connection: _Connection | None = None
        self._generation: _Connection | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._transports: list[asyncio.BaseTransport] = []
        self._dispatchers: dict[str | int, asyncio.Task[None]] = {}

    def start(self) -> None:
        if self._generation is not None:
            raise RuntimeError("MCP stdio connection has unsettled work")
        super().start()

    def _clear(self, connection: _Connection) -> None:
        if (
            self._generation is connection
            and connection.settled
            and (
                connection.serving.done()
                or connection.serving is asyncio.current_task()
            )
            and not connection.dispatchers
            and not connection.outputs
        ):
            self._generation = None
            self._reader = None
            self._writer = None
            self._transports = []
            self._dispatchers = {}

    async def _stop_connection(self, connection: _Connection) -> None:
        # A finalizer for an older generation cannot stop the current core/streams.
        if self._generation is not connection:
            return
        loop = asyncio.get_running_loop()
        deadline = loop.time() + self.limits.shutdown_seconds
        connection.closing = True
        if self._connection is connection:
            self._connection = None
        if connection.signal_owned:
            loop.remove_signal_handler(signal.SIGTERM)
            connection.signal_owned = False
        for transport in connection.transports:
            transport.close()
        if connection.reader is not None:
            connection.reader.feed_eof()
        if connection.writer is not None and connection.close_wait is None:
            connection.writer.close()
            connection.close_wait = asyncio.create_task(connection.writer.wait_closed())

            def closed(done: asyncio.Task[None]) -> None:
                if not done.cancelled():
                    done.exception()

            connection.close_wait.add_done_callback(closed)
        current = asyncio.current_task()
        tasks: tuple[asyncio.Task[object], ...] = (
            *connection.dispatchers.values(),
            *connection.outputs,
            *((connection.serving,) if connection.serving is not current else ()),
        )
        for task in tasks:
            if not task.done():
                task.cancel()
        # Inspect every transport owner within the original stop budget.
        with suppress(TimeoutError):
            await super().stop()
        pending = [task for task in tasks if not task.done()]
        if connection.close_wait is not None:
            pending.append(connection.close_wait)
        if pending:
            _, unfinished = await asyncio.wait(
                pending, timeout=max(0, deadline - loop.time())
            )
            if unfinished:
                raise TimeoutError("MCP stdio shutdown incomplete")
        if self._owners:
            raise TimeoutError("MCP stdio shutdown incomplete")
        if connection.close_wait is not None:
            with suppress(OSError, ConnectionError, asyncio.CancelledError):
                connection.close_wait.result()
        connection.settled = True
        self._clear(connection)

    async def stop(self) -> None:
        connection = self._generation
        if connection is None:
            await super().stop()
        else:
            await self._stop_connection(connection)

    async def serve(
        self,
        *,
        reader: asyncio.StreamReader | None = None,
        writer: asyncio.StreamWriter | None = None,
    ) -> None:
        if self._generation is not None:
            raise RuntimeError("MCP stdio connection already active or unsettled")
        if (reader is None) != (writer is None):
            raise ValueError("MCP stdio requires both streams")
        serving = asyncio.current_task()
        if serving is None:
            raise RuntimeError("MCP stdio requires an owning task")
        super().start()
        connection = _Connection(serving, reader, writer)
        self._generation = self._connection = connection
        self._dispatchers = connection.dispatchers
        running = asyncio.create_task(self._serve_connection(connection))
        connection.serving = running

        def serving_done(done: asyncio.Task[object]) -> None:
            if not done.cancelled():
                done.exception()
            self._clear(connection)

        running.add_done_callback(serving_done)
        try:
            await asyncio.shield(running)
        except asyncio.CancelledError:
            await self._stop_connection(connection)
            raise

    async def _serve_connection(self, connection: _Connection) -> None:
        reader, writer = connection.reader, connection.writer
        loop = asyncio.get_running_loop()
        native = reader is None

        async def write_response(response: object, deadline: float) -> None:
            if connection.writer is None or self._connection is not connection:
                return
            if deadline <= loop.time():
                return
            try:
                raw = (
                    encode(
                        response, self.limits, byte_limit=self.limits.result_bytes - 1
                    )
                    + b"\n"
                )
                async with asyncio.timeout_at(deadline):
                    async with connection.lock:
                        task = asyncio.current_task()
                        if (
                            self._connection is connection
                            and deadline > loop.time()
                            and task is not None
                            and not task.cancelling()
                        ):
                            connection.writer.write(raw)
                            await connection.writer.drain()
            except (ServerWireError, OSError, ConnectionError, TimeoutError):
                if self._connection is connection:
                    self._connection = None
                    if connection.reader is not None:
                        connection.reader.feed_eof()

        def reject(response: object, deadline: float) -> None:
            # Bounded separate capacity keeps cancellation/EOF reads responsive even
            # when every admitted handler or output lock is blocked. Saturation
            # terminates this connection rather than queueing or shedding tasks.
            if self._connection is not connection or deadline <= loop.time():
                return
            if len(connection.outputs) >= self.limits.active_requests:
                self._connection = None
                if connection.reader is not None:
                    connection.reader.feed_eof()
                return
            task = asyncio.create_task(write_response(response, deadline))
            connection.outputs.add(task)

            def settled(done: asyncio.Task[None]) -> None:
                connection.outputs.discard(done)
                if not done.cancelled():
                    done.exception()
                self._clear(connection)

            task.add_done_callback(settled)

        async def dispatch(request: ServerRequest, raw: bytes, deadline: float) -> None:
            try:
                response = await self.handle(raw, deadline=deadline)
                await write_response(response, deadline)
            finally:
                task = asyncio.current_task()
                if (
                    request.request_id is not None
                    and connection.dispatchers.get(request.request_id) is task
                ):
                    connection.dispatchers.pop(request.request_id, None)

        def line(raw: bytes, deadline: float) -> None:
            if self._connection is not connection or deadline <= loop.time():
                return
            try:
                request = ServerRequest.parse(raw, self.limits)
                if deadline <= loop.time():
                    return
                if request.request_id is None:
                    if request.method == "notifications/cancelled":
                        target = request.params.get("requestId")
                        if isinstance(target, (str, int)) and not isinstance(
                            target, bool
                        ):
                            task = connection.dispatchers.get(target)
                            if task is not None:
                                task.cancel()
                    return
                if request.request_id in connection.dispatchers:
                    raise ServerWireError(-32600)
                if len(connection.dispatchers) >= self.limits.active_requests:
                    raise ServerWireError(-32603)
                connection.dispatchers[request.request_id] = asyncio.create_task(
                    dispatch(request, raw, deadline)
                )
            except ServerWireError as error:
                if not notification_envelope(raw, self.limits):
                    reject(error.response(safe_error_id(raw, self.limits)), deadline)

        try:
            if native:
                reader = asyncio.StreamReader(limit=self.limits.request_bytes + 1)
                connection.reader = reader
                protocol = asyncio.StreamReaderProtocol(reader)
                transport, _ = await loop.connect_read_pipe(
                    lambda: protocol, sys.stdin.buffer
                )
                connection.transports.append(transport)
                if connection.closing:
                    raise asyncio.CancelledError
                out_protocol = asyncio.StreamReaderProtocol(asyncio.StreamReader())
                out_transport, _ = await loop.connect_write_pipe(
                    lambda: out_protocol, sys.stdout.buffer
                )
                connection.transports.append(out_transport)
                writer = asyncio.StreamWriter(out_transport, out_protocol, None, loop)
                connection.writer = writer
                if connection.closing:
                    raise asyncio.CancelledError

                def terminate() -> None:
                    if self._connection is connection:
                        reader.feed_eof()
                        self._connection = None

                loop.add_signal_handler(signal.SIGTERM, terminate)
                connection.signal_owned = True
            if reader is None or writer is None:
                raise RuntimeError("MCP stdio stream unavailable")
            self._reader = reader
            self._writer = writer
            self._transports = connection.transports
            frame = bytearray()
            oversized = False
            frame_deadline: float | None = None
            while self._connection is connection:
                if frame_deadline is None:
                    chunk = await reader.read(min(4096, self.limits.request_bytes))
                else:
                    async with asyncio.timeout_at(frame_deadline):
                        chunk = await reader.read(min(4096, self.limits.request_bytes))
                if not chunk:
                    if frame_deadline is not None:
                        reject(ServerWireError(-32700).response(), frame_deadline)
                        await asyncio.sleep(0)
                    break
                received_at = loop.time()
                for byte in chunk:
                    if self._connection is not connection:
                        break
                    if frame_deadline is None:
                        frame_deadline = received_at + self.limits.timeout_seconds
                    if frame_deadline <= loop.time():
                        raise TimeoutError
                    if byte == 10:
                        if oversized:
                            reject(ServerWireError(-32600).response(), frame_deadline)
                        else:
                            line(bytes(frame), frame_deadline)
                        frame.clear()
                        oversized = False
                        frame_deadline = None
                    elif not oversized:
                        if len(frame) == self.limits.request_bytes:
                            frame.clear()
                            oversized = True
                        else:
                            frame.append(byte)
                # Start admitted/output work without waiting on delivery.
                await asyncio.sleep(0)
        except asyncio.CancelledError:
            if not connection.closing:
                raise
        except TimeoutError:
            # An expired partial frame cannot be reused as a fresh request.
            pass
        except (OSError, ConnectionError):
            if native:
                sys.stderr.write("MCP stdio transport failed\n")
        finally:
            await self._stop_connection(connection)
