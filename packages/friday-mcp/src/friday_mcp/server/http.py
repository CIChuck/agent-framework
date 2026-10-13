"""One stateless POST endpoint; optional HTTP dependencies are imported lazily."""

from __future__ import annotations

import asyncio
import signal
import threading
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Literal

from friday_core import TelemetryInterface

from friday_mcp.server.http_policy import (
    HTTPAccessError,
    HTTPServerPolicy,
    validate_rpc_headers,
)
from friday_mcp.server.modern import ModernToolsMCPServer
from friday_mcp.server.protocol import (
    DEFAULT_SERVER_LIMITS,
    ServerLimits,
    ServerRequest,
    ServerWireError,
    encode,
    safe_error_id,
)

if TYPE_CHECKING:
    from fastapi import FastAPI
    from starlette.types import Receive, Scope, Send
    from uvicorn import Server


class StreamableHTTPMCPServer(ModernToolsMCPServer):
    def __init__(
        self,
        *,
        policy: HTTPServerPolicy | None = None,
        response_mode: Literal["json", "sse"] = "json",
        limits: ServerLimits = DEFAULT_SERVER_LIMITS,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        if policy is None:
            policy = HTTPServerPolicy()
        if not isinstance(policy, HTTPServerPolicy) or response_mode not in (
            "json",
            "sse",
        ):
            raise ValueError("Invalid MCP HTTP configuration")
        super().__init__(limits=limits, telemetry=telemetry)
        self.policy = policy
        self.response_mode = response_mode
        self._runner: Server | None = None
        self._listener_task: asyncio.Task[None] | None = None

    def create_app(self) -> FastAPI:
        try:
            from fastapi import FastAPI
            from starlette.routing import Route
        except ImportError:
            raise RuntimeError("MCP HTTP server dependencies unavailable") from None
        app = FastAPI(
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
            redirect_slashes=False,
            lifespan=self._lifespan,
        )
        app.router.routes.append(
            Route(self.policy.path, self, methods=["POST", "GET", "DELETE"])
        )
        return app

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        self.start()
        try:
            yield
        finally:
            await self.stop()

    @property
    def listening(self) -> bool:
        return (
            self._runner is not None
            and self._runner.started
            and not self._runner.should_exit
        )

    async def stop(self) -> None:
        deadline = asyncio.get_running_loop().time() + self.limits.shutdown_seconds
        runner = self._runner
        if runner is not None:
            runner.should_exit = True
            if runner.started:
                for listener in runner.servers:
                    listener.close()
        await super().stop()
        listener_task = self._listener_task
        if listener_task is not None and listener_task is not asyncio.current_task():
            _, pending = await asyncio.wait(
                (listener_task,),
                timeout=max(0, deadline - asyncio.get_running_loop().time()),
            )
            if pending:
                raise TimeoutError("MCP HTTP shutdown incomplete")
            self._listener_task = None
            self._runner = None

    async def serve(
        self, *, certificate: str | None = None, private_key: str | None = None
    ) -> None:
        if self.policy.require_tls and (certificate is None or private_key is None):
            raise ValueError("MCP HTTP TLS configuration required")
        try:
            import uvicorn
        except ImportError:
            raise RuntimeError("MCP HTTP server dependencies unavailable") from None
        if self._listener_task is not None and not self._listener_task.done():
            raise RuntimeError("MCP HTTP listener still active")
        self.start()
        config = uvicorn.Config(
            self.create_app(),
            host=self.policy.bind_host,
            port=self.policy.port,
            ssl_certfile=certificate,
            ssl_keyfile=private_key,
            access_log=False,
            log_config=None,
            log_level="critical",
            timeout_graceful_shutdown=0,
        )

        class OwnedServer(uvicorn.Server):
            @contextmanager
            def capture_signals(self) -> Iterator[None]:
                if threading.current_thread() is not threading.main_thread():
                    yield
                    return
                previous = {
                    sig: signal.signal(sig, self.handle_exit)
                    for sig in (signal.SIGTERM, signal.SIGINT)
                }
                try:
                    yield
                finally:
                    for sig, handler in previous.items():
                        signal.signal(sig, handler)

        server = OwnedServer(config)
        self._runner = server
        self._listener_task = asyncio.create_task(server.serve())
        try:
            await asyncio.shield(self._listener_task)
        finally:
            await self.stop()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            return
        if scope.get("path") != self.policy.path:
            await self._send(send, 404, b"", b"application/json")
            return
        if scope.get("method") != "POST":
            await self._send(
                send, 405, b"", b"application/json", extra=[(b"allow", b"POST")]
            )
            return
        deadline = asyncio.get_running_loop().time() + self.limits.timeout_seconds
        raw = bytearray()
        body_done = asyncio.Event()
        headers: dict[bytes, bytes] = {}
        try:
            headers = self.policy.validate(
                scope.get("headers", []),
                scheme=scope.get("scheme", "http"),
                query=scope.get("query_string", b""),
                limits=self.limits,
            )
        except HTTPAccessError as error:
            await self._send(
                send,
                error.status,
                encode(ServerWireError(-32600).response(), self.limits),
                b"application/json",
            )
            return

        async def operation() -> bytes:
            if (
                headers.get(b"content-type", b"").split(b";", 1)[0].strip().lower()
                != b"application/json"
            ):
                raise ServerWireError(-32600)
            accepts = {
                v.split(b";", 1)[0].strip().lower()
                for v in headers.get(b"accept", b"").split(b",")
            }
            if not {b"application/json", b"text/event-stream"}.issubset(accepts):
                raise ServerWireError(-32600)
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    raise asyncio.CancelledError
                if message["type"] != "http.request":
                    raise ServerWireError(-32600)
                chunk = message.get("body", b"")
                if len(raw) + len(chunk) > self.limits.request_bytes:
                    raise ServerWireError(-32600)
                raw.extend(chunk)
                if not message.get("more_body", False):
                    break
            body_done.set()
            request = ServerRequest.parse(bytes(raw), self.limits)
            validate_rpc_headers(headers, request, self.selected_tool(request))
            response = await self.dispatch(request)
            return encode(response, self.limits)

        async def disconnect() -> None:
            await body_done.wait()
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return

        running = asyncio.create_task(self.run_owned(operation, deadline))
        watcher = asyncio.create_task(disconnect())
        try:
            done, _ = await asyncio.wait(
                (running, watcher), return_when=asyncio.FIRST_COMPLETED
            )
            if watcher in done:
                running.cancel()
                await asyncio.gather(running, return_exceptions=True)
                return
            result = running.result()
            if self.response_mode == "sse":
                await self._send(
                    send,
                    200,
                    b"event: message\ndata: " + result + b"\n\n",
                    b"text/event-stream",
                    extra=[
                        (b"x-accel-buffering", b"no"),
                        (b"cache-control", b"no-cache"),
                    ],
                )
            else:
                await self._send(send, 200, result, b"application/json")
        except ServerWireError as error:
            await self._send(
                send,
                error.http_status,
                encode(
                    error.response(safe_error_id(bytes(raw), self.limits)), self.limits
                ),
                b"application/json",
            )
        except asyncio.CancelledError:
            running.cancel()
            await asyncio.gather(running, return_exceptions=True)
            raise
        except Exception:
            await self._send(
                send,
                500,
                encode(
                    ServerWireError(-32603).response(
                        safe_error_id(bytes(raw), self.limits)
                    ),
                    self.limits,
                ),
                b"application/json",
            )
        finally:
            watcher.cancel()
            await asyncio.gather(watcher, return_exceptions=True)

    async def _send(
        self,
        send: Send,
        status: int,
        body: bytes,
        content_type: bytes,
        *,
        extra: list[tuple[bytes, bytes]] | None = None,
    ) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    (b"content-type", content_type),
                    (b"content-length", str(len(body)).encode("ascii")),
                    *(extra or []),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})
