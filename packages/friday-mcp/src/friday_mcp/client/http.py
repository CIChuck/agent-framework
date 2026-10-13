"""Request-scoped tools client, explicit MCP revisions, no mutation replay."""

from __future__ import annotations

import asyncio
import logging
import ssl
import uuid
from contextlib import suppress
from contextvars import ContextVar
from typing import Any

import httpcore

from friday_mcp.client.base import MCPClientBase, MCPError
from friday_mcp.client.catalog import MCPCatalogSnapshot
from friday_mcp.client.http_policy import (
    HTTPEndpoint,
    HTTPEndpointPolicy,
    HTTPResolver,
    PolicyHTTPBackend,
)
from friday_mcp.client.http_protocol import (
    HTTP_COMPAT_VERSION,
    HeaderBinding,
    HTTPLimits,
    HTTPVersion,
    SSEDecoder,
    compatibility_result,
    content_type,
    header_bindings,
    header_value,
    response_headers,
    session_id,
)
from friday_mcp.client.protocol import (
    META_PREFIX,
    MODERN_VERSION,
    Discovery,
    FrozenJSON,
    JSONValue,
    ProtocolFailure,
    ProtocolLimits,
    ResultSnapshot,
    RPCResponse,
    ToolDefinition,
    complete_result,
    decode_json,
    encode_json,
    response_from_message,
    validate_message,
)
from friday_mcp.protocols import MCPTransport


def safe_http_logging() -> None:
    # httpcore's documented debug mode exposes headers. Do not change application
    # loggers: fail closed before I/O and at each public trace callback instead.
    if any(
        logging.getLogger(name).isEnabledFor(logging.DEBUG)
        for name in (
            "httpcore.connection",
            "httpcore.http11",
            "httpcore.http2",
        )
    ):
        raise ProtocolFailure()


async def safe_http_trace(event: str, info: dict[str, object]) -> None:
    """Public request extension; no inspection, copying, emission or global filter."""
    safe_http_logging()


class _SessionExpired(ProtocolFailure):
    pass


class StreamableHTTPMCPClient(MCPClientBase):
    def __init__(
        self,
        endpoint: str,
        *,
        protocol_version: HTTPVersion,
        name: str = "remote",
        endpoint_policy: HTTPEndpointPolicy | None = None,
        limits: ProtocolLimits | None = None,
        http_limits: HTTPLimits | None = None,
        bearer_token: str | None = None,
        resolver: HTTPResolver | None = None,
        connector: httpcore.AsyncNetworkBackend | None = None,
    ) -> None:
        if protocol_version not in (MODERN_VERSION, HTTP_COMPAT_VERSION):
            raise ValueError("Invalid MCP HTTP version")
        super().__init__(
            name,
            protocol_profile="modern"
            if protocol_version == MODERN_VERSION
            else "legacy",
            limits=limits,
        )
        self._selected_version = protocol_version
        if http_limits is not None and not isinstance(http_limits, HTTPLimits):
            raise ValueError("Invalid MCP HTTP limits")
        self.http_limits = http_limits or HTTPLimits()
        self._endpoint = HTTPEndpoint.parse(
            endpoint, endpoint_policy or HTTPEndpointPolicy()
        )
        if bearer_token is not None and (
            not isinstance(bearer_token, str)
            or not 0 < len(bearer_token) <= 8192
            or any(not 0x21 <= ord(c) <= 0x7E for c in bearer_token)
        ):
            raise ValueError("Invalid MCP HTTP credential")
        self._bearer_token = bearer_token
        self._backend = PolicyHTTPBackend(
            self._endpoint,
            self.http_limits.header_bytes,
            self.http_limits.wire_bytes,
            resolver,
            connector,
        )
        self._pool: httpcore.AsyncConnectionPool | None = None
        self._jobs: dict[str, asyncio.Task[RPCResponse | None]] = {}
        self._cleanup: dict[str, asyncio.Task[None]] = {}
        self._pool_cleanup: asyncio.Task[None] | None = None
        self._session_id: bytes | None = None
        self._generation = 0
        self._lifecycle = asyncio.Lock()
        self._bindings: dict[str, tuple[HeaderBinding, ...]] = {}
        self._call_bindings: ContextVar[tuple[HeaderBinding, ...] | None] = ContextVar(
            "mcp-call-bindings", default=None
        )
        self._recovered_call_catalog: MCPCatalogSnapshot | None = None
        self._initializing = False
        self._issued = self._backend.issued
        self.rejected_http_tools = 0

    async def _create_transport(self) -> MCPTransport | None:
        return None  # HTTP has request-scoped streams, no shared receiver.

    def _timeout(self, requested: float | None = None) -> float:
        return min(super()._timeout(requested), self.limits.timeout_seconds)

    @property
    def outstanding_http_owners(self) -> int:
        owners = set(self._jobs) | set(self._cleanup)
        owners.update(s.owner for s in self._backend.streams if not s.closed)
        return len(owners) + (self._pool_cleanup is not None)

    async def connect(self) -> None:
        async with self._lifecycle:
            if self._connected:
                return
            if self._pool is not None or self.outstanding_http_owners:
                await self._disconnect_owned()
            safe_http_logging()
            self._invalidate_catalog()
            self._bindings.clear()
            self._session_id = None
            self._generation += 1
            # No proxies/cookies/redirects, no keepalive or connection retry.
            deadline = asyncio.get_running_loop().time() + self._timeout()
            self._pool = httpcore.AsyncConnectionPool(
                ssl_context=ssl.create_default_context(),
                http2=False,
                retries=0,
                max_connections=self.limits.concurrent_requests,
                max_keepalive_connections=0,
                network_backend=self._backend,
            )
            self._initializing = True
            try:
                async with asyncio.timeout_at(deadline):
                    await self._handshake(deadline)
                self._connected = True
            except BaseException:
                # Keep retryable owners and the original failure.
                with suppress(BaseException):
                    await self._disconnect_owned()
                raise
            finally:
                self._initializing = False

    async def _handshake(self, deadline: float) -> None:
        if self._selected_version == MODERN_VERSION:
            result = await self._request_budget("server/discover", {}, deadline)
            discovery = Discovery.parse(
                FrozenJSON.from_value(result, self.limits).object(), self.limits
            )
            self._discovery = discovery
            self._capabilities = discovery.capabilities
            self._identity = discovery.server_info
        else:
            result = await self._request_budget(
                "initialize",
                {
                    "protocolVersion": HTTP_COMPAT_VERSION,
                    "capabilities": {},
                    "clientInfo": self._client_info,
                },
                deadline,
            )
            if result.get("protocolVersion") != HTTP_COMPAT_VERSION:
                raise ProtocolFailure("unsupported_version")
            self._capabilities = FrozenJSON.from_value(
                result["capabilities"], self.limits
            )
            self._identity = FrozenJSON.from_value(result["serverInfo"], self.limits)
            await self._control(
                {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
                deadline,
            )

    async def disconnect(self) -> None:
        self._connected = False
        self._generation += 1
        self._invalidate_catalog()
        await self._stop_refreshes()
        async with self._lifecycle:
            await self._disconnect_owned()

    async def _close_pool(self) -> None:
        # Directly owned streams also cover TLS/partial-connect failures not yet
        # adopted by the pool. Borrowed resolver/connector objects are never closed.
        await self._backend.aclose()
        if self._pool is not None:
            await self._pool.aclose()

    async def _disconnect_owned(self) -> None:
        self._connected = False
        self._invalidate_catalog()
        self._bindings.clear()
        self._capabilities = FrozenJSON.from_value({}, self.limits)
        self._identity = FrozenJSON.from_value({}, self.limits)
        for task in tuple(self._jobs.values()):
            task.cancel()
        tasks: set[asyncio.Task[object]] = set(self._jobs.values()) | set(
            self._cleanup.values()
        )
        if tasks:
            _, pending = await asyncio.wait(tasks, timeout=0.2)
            if pending:
                raise RuntimeError("MCP HTTP request cleanup incomplete")
        if self._session_id is not None and self._pool is not None:
            session = self._session_id
            self._session_id = None
            # Advisory DELETE never replaces owned resource cleanup.
            with suppress(Exception):
                await self._control(
                    None,
                    asyncio.get_running_loop().time() + 0.2,
                    delete_session=session,
                )
        if self._pool is not None or self._backend.streams:
            if self._pool_cleanup is None:
                self._pool_cleanup = asyncio.create_task(
                    self._close_pool(), name="mcp-http-pool-close"
                )
            task = self._pool_cleanup
            _, pending = await asyncio.wait((task,), timeout=0.2)
            if pending:
                raise RuntimeError("MCP HTTP pool cleanup incomplete")
            try:
                task.result()
            except BaseException:
                self._pool_cleanup = None
                raise RuntimeError("MCP HTTP pool cleanup incomplete") from None
            self._pool_cleanup = None
            if any(
                not t.done() for t in (*self._jobs.values(), *self._cleanup.values())
            ):
                raise RuntimeError("MCP HTTP request cleanup incomplete")
            self._pool = None
        self._session_id = None
        self._discovery = None

    def _headers(
        self,
        message: dict[str, JSONValue] | None,
        session: bytes | None,
        body_bytes: int,
    ) -> list[tuple[bytes, bytes]]:
        headers = [
            (b"Accept", b"application/json, text/event-stream"),
            (b"MCP-Protocol-Version", self._selected_version.encode("ascii")),
        ]
        host = self._endpoint.host
        authority = f"[{host}]" if ":" in host else host
        headers.extend(
            [
                (b"Host", f"{authority}:{self._endpoint.port}".encode("ascii")),
                (b"Content-Length", str(body_bytes).encode("ascii")),
                (b"Connection", b"close"),
            ]
        )
        if message is not None:
            headers.append((b"Content-Type", b"application/json"))
        if self._bearer_token is not None:
            headers.append(
                (b"Authorization", b"Bearer " + self._bearer_token.encode("ascii"))
            )
        if session is not None:
            headers.append((b"MCP-Session-Id", session))
        if message is not None and self._selected_version == MODERN_VERSION:
            method = message.get("method")
            params = message.get("params")
            if not isinstance(method, str) or not isinstance(params, dict):
                raise ProtocolFailure()
            headers.append((b"Mcp-Method", method.encode("ascii")))
            if method == "tools/call":
                name, arguments = params.get("name"), params.get("arguments")
                if (
                    not isinstance(name, str)
                    or not isinstance(arguments, dict)
                    or (
                        self._call_bindings.get() is None and name not in self._bindings
                    )
                ):
                    raise ProtocolFailure()
                headers.append((b"Mcp-Name", header_value(name)))
                captured = self._call_bindings.get()
                for binding in self._bindings[name] if captured is None else captured:
                    value = binding.extract(arguments)
                    if value is not None:
                        headers.append(
                            (("Mcp-Param-" + binding.name).encode("ascii"), value)
                        )
        if (
            sum(len(k) + len(v) + 4 for k, v in headers) + len(self._endpoint.url) + 32
            > self.http_limits.header_bytes
        ):
            raise ProtocolFailure("limit_exceeded")
        return headers

    def _decode(self, data: bytes, request_id: str) -> dict[str, JSONValue]:
        if b"\x00" in data:
            # Reject raw NUL, including BOM-less UTF-16/32 that json.loads(bytes)
            # would otherwise autodetect even though it decodes as UTF-8 bytes.
            raise ProtocolFailure()
        try:
            # JSON bytes parser also accepts UTF-16; HTTP profile requires UTF-8.
            data.decode("utf-8")
        except UnicodeError:
            raise ProtocolFailure() from None
        message = validate_message(
            decode_json(data, self.limits),
            self.limits,
            modern=self._selected_version == MODERN_VERSION,
            compatibility=self._selected_version == HTTP_COMPAT_VERSION,
        )
        if "method" not in message and (
            type(message.get("id")) is not str or message["id"] != request_id
        ):
            raise ProtocolFailure()
        return message

    async def _server_message(
        self, message: dict[str, JSONValue], deadline: float
    ) -> None:
        if "id" in message:
            if self._selected_version == MODERN_VERSION:
                raise ProtocolFailure()
            await self._control(
                {
                    "jsonrpc": "2.0",
                    "id": message["id"],
                    "error": {"code": -32601, "message": "Method not supported"},
                },
                deadline,
            )
        # No progress token, log level or subscriptions are advertised. Bounded
        # unsolicited notifications are ignored without storing/propagating data.

    async def _close_response(
        self,
        response: httpcore.Response | None,
        owner: str,
    ) -> None:
        close = (
            response.aclose()
            if response is not None
            else self._backend.close_owner(owner)
        )
        task = asyncio.create_task(close, name="mcp-http-response-close")
        self._cleanup[owner] = task

        def settled(done: asyncio.Task[None]) -> None:
            if not done.cancelled():
                done.exception()
            if self._cleanup.get(owner) is done:
                self._cleanup.pop(owner, None)

        task.add_done_callback(settled)
        _, pending = await asyncio.wait((task,), timeout=0.1)
        if pending:
            task.cancel()
            _, pending = await asyncio.wait((task,), timeout=0.1)
            if pending:
                raise RuntimeError("MCP HTTP response cleanup incomplete")
        task.result()

    async def _exchange(
        self,
        message: dict[str, JSONValue] | None,
        owner: str,
        deadline: float,
        generation: int,
        *,
        delete_session: bytes | None = None,
    ) -> RPCResponse | None:
        safe_http_logging()
        pool = self._pool
        if pool is None:
            raise RuntimeError("MCP HTTP disconnected")
        session = delete_session if delete_session is not None else self._session_id
        body = (
            encode_json(message, self.limits, byte_limit=self.limits.frame_bytes)
            if message is not None
            else b""
        )
        headers = self._headers(message, session, len(body))
        remaining = deadline - asyncio.get_running_loop().time()
        if remaining <= 0:
            raise TimeoutError("MCP HTTP timeout")
        token = self._backend.owner.set(owner)
        response: httpcore.Response | None = None
        primary: BaseException | None = None
        try:
            # The network stream records issue only after a successful header write.
            response = await pool.handle_async_request(
                httpcore.Request(
                    "DELETE" if delete_session is not None else "POST",
                    self._endpoint.url,
                    headers=headers,
                    content=body,
                    extensions={
                        "timeout": {
                            k: remaining for k in ("connect", "read", "write", "pool")
                        },
                        "trace": safe_http_trace,
                    },
                )
            )
            incoming = response_headers(response.headers, self.http_limits)
            if delete_session is not None:
                if response.status not in (200, 202, 204, 404, 405):
                    raise ProtocolFailure()
                return None
            if (
                self._selected_version == HTTP_COMPAT_VERSION
                and session is not None
                and response.status == 404
            ):
                raise _SessionExpired()
            request_id = (
                message.get("id")
                if message is not None and "method" in message
                else None
            )
            if request_id is None:
                if response.status != 202:
                    raise ProtocolFailure()
                async for chunk in response.aiter_stream():
                    if chunk:
                        raise ProtocolFailure()
                return None
            if not isinstance(request_id, str):
                raise ProtocolFailure()
            if message is not None and message.get("method") == "initialize":
                if generation != self._generation:
                    raise ProtocolFailure()
                self._session_id = session_id(incoming.get(b"mcp-session-id"))
            elif (
                self._selected_version == MODERN_VERSION
                and b"mcp-session-id" in incoming
            ):
                raise ProtocolFailure()
            kind = content_type(incoming)
            wire = 0
            final: dict[str, JSONValue] | None = None
            if kind == b"application/json":
                document = bytearray()
                async for chunk in response.aiter_stream():
                    wire += len(chunk)
                    if wire > min(self.http_limits.wire_bytes, self.limits.frame_bytes):
                        raise ProtocolFailure("limit_exceeded")
                    document.extend(chunk)
                final = self._decode(bytes(document), request_id)
                if "method" in final:
                    raise ProtocolFailure()
            else:
                decoder = SSEDecoder(self.http_limits)
                async for chunk in response.aiter_stream():
                    wire += len(chunk)
                    for data in decoder.feed(chunk):
                        item = self._decode(data, request_id)
                        if "method" in item:
                            if final is not None:
                                raise ProtocolFailure()
                            await self._server_message(item, deadline)
                        else:
                            if final is not None:
                                raise ProtocolFailure()
                            final = item
                    if final is not None:
                        if decoder.buffer or decoder.data:
                            raise ProtocolFailure()
                        break  # A final result need not wait for stream EOF.
                if final is None:
                    for data in decoder.finish():
                        item = self._decode(data, request_id)
                        if "method" in item or final is not None:
                            raise ProtocolFailure()
                        final = item
            if final is None:
                raise ProtocolFailure()
            rpc = response_from_message(final, self.limits, wire)
            if rpc.error_code is None and response.status != 200:
                raise ProtocolFailure()
            if self._selected_version == MODERN_VERSION:
                expected = {
                    -32020: 400,
                    -32021: 400,
                    -32022: 400,
                    -32602: 400,
                    -32601: 404,
                }.get(rpc.error_code or 0)
                if expected is not None and response.status != expected:
                    raise ProtocolFailure()
            return rpc
        except BaseException as exc:
            primary = exc
            raise
        finally:
            if response is not None or any(
                s.owner == owner for s in self._backend.streams
            ):
                try:
                    await self._close_response(response, owner)
                except BaseException:
                    if primary is None:
                        raise ProtocolFailure() from None
            self._issued.discard(owner)
            self._backend.owner.reset(token)

    def _start(
        self,
        message: dict[str, JSONValue] | None,
        owner: str,
        deadline: float,
        *,
        delete_session: bytes | None = None,
    ) -> asyncio.Task[RPCResponse | None]:
        self._jobs = {
            key: value for key, value in self._jobs.items() if not value.done()
        }
        if self.outstanding_http_owners >= self.limits.concurrent_requests:
            raise ProtocolFailure("limit_exceeded")
        task = asyncio.create_task(
            self._exchange(
                message,
                owner,
                deadline,
                self._generation,
                delete_session=delete_session,
            ),
            name="mcp-http-request",
        )
        self._jobs[owner] = task

        def settled(done: asyncio.Task[RPCResponse | None]) -> None:
            if not done.cancelled():
                done.exception()
            if self._jobs.get(owner) is done:
                self._jobs.pop(owner, None)

        task.add_done_callback(settled)
        return task

    async def _wait(
        self, task: asyncio.Task[RPCResponse | None], deadline: float
    ) -> RPCResponse | None:
        _, pending = await asyncio.wait(
            (task,), timeout=max(0, deadline - asyncio.get_running_loop().time())
        )
        if pending:
            raise TimeoutError("MCP HTTP timeout")
        return task.result()

    async def _control(
        self,
        message: dict[str, JSONValue] | None,
        deadline: float,
        *,
        delete_session: bytes | None = None,
    ) -> None:
        owner = str(uuid.uuid4())
        task = self._start(message, owner, deadline, delete_session=delete_session)
        try:
            await self._wait(task, deadline)
        finally:
            if not task.done():
                task.cancel()

    async def _request(
        self, method: str, params: dict[str, Any], timeout: float | None = None
    ) -> dict[str, Any]:
        if not self._connected:
            raise RuntimeError("MCP HTTP disconnected")
        return await self._request_budget(
            method, params, asyncio.get_running_loop().time() + self._timeout(timeout)
        )

    async def _request_budget(
        self, method: str, params: dict[str, Any], deadline: float
    ) -> dict[str, Any]:
        if (
            method not in ("server/discover", "tools/list", "tools/call", "initialize")
            or (method == "initialize" and self._selected_version == MODERN_VERSION)
            or (
                method == "server/discover"
                and self._selected_version == HTTP_COMPAT_VERSION
            )
        ):
            raise ProtocolFailure("unsupported_content")
        if asyncio.get_running_loop().time() >= deadline:
            raise TimeoutError("MCP HTTP timeout")
        payload = FrozenJSON.from_value(
            params, self.limits, byte_limit=self.limits.frame_bytes
        ).object()
        if self._selected_version == MODERN_VERSION:
            payload["_meta"] = {
                META_PREFIX + "protocolVersion": MODERN_VERSION,
                META_PREFIX + "clientInfo": FrozenJSON.from_value(
                    self._client_info, self.limits
                ).object(),
                META_PREFIX + "clientCapabilities": {},
            }
        owner = str(uuid.uuid4())
        message: dict[str, JSONValue] = {
            "jsonrpc": "2.0",
            "id": owner,
            "method": method,
            "params": payload,
        }
        task = self._start(message, owner, deadline)
        generation = self._generation
        issued = False
        try:
            rpc = await self._wait(task, deadline)
            if rpc is None or rpc.result is None and rpc.error_code is None:
                raise ProtocolFailure()
            if rpc.error_code is not None:
                raise MCPError(rpc.error_code, "MCP peer rejected request")
            if rpc.result is None:
                raise ProtocolFailure()
            result = rpc.result.object()
            complete_result(result, self._selected_version == MODERN_VERSION)
            if self._selected_version == HTTP_COMPAT_VERSION:
                if generation != self._generation:
                    raise ProtocolFailure()
                compatibility_result(result, method, self.limits)
            return ResultSnapshot(result, rpc.wire_bytes)
        except _SessionExpired:
            try:
                # The lifecycle lock serializes recovery with explicit reconnect
                # and shutdown. A stale response/waiter never owns newer state.
                async with asyncio.timeout_at(deadline), self._lifecycle:
                    if generation == self._generation:
                        prior_call_catalog = self._catalog_for_direct_call()
                        self._generation += 1
                        recovery_generation = self._generation
                        self._connected = False
                        self._invalidate_catalog()
                        self._bindings.clear()
                        self._session_id = None
                        try:
                            await self._handshake(deadline)
                            if recovery_generation == self._generation:
                                self._connected = True
                                # Preserve the accepted explicit 2025 raw call API
                                # with its prior schema, never a schema-free retry.
                                # Generation-bound wrappers remain invalid.
                                self._recovered_call_catalog = prior_call_catalog
                        except BaseException:
                            if recovery_generation == self._generation:
                                self._connected = False
                                self._session_id = None
                                self._invalidate_catalog()
                                self._bindings.clear()
                            raise
            except Exception:
                pass  # Only the recovery owner above may invalidate its state.
            raise ProtocolFailure() from None
        except (TimeoutError, asyncio.CancelledError):
            issued = owner in self._issued
            task.cancel()
            if (
                issued
                and self._selected_version == HTTP_COMPAT_VERSION
                and method != "initialize"
            ):
                with suppress(BaseException):
                    await self._control(
                        {
                            "jsonrpc": "2.0",
                            "method": "notifications/cancelled",
                            "params": {"requestId": owner},
                        },
                        asyncio.get_running_loop().time() + 0.1,
                    )
            raise
        except (ProtocolFailure, MCPError):
            raise
        except Exception:
            raise ProtocolFailure() from None
        finally:
            if not task.done():
                task.cancel()

    def _invalidate_catalog(self) -> None:
        super()._invalidate_catalog()
        self._recovered_call_catalog = None
        self._bindings.clear()
        self.rejected_http_tools = 0

    def _catalog_for_direct_call(self) -> MCPCatalogSnapshot | None:
        return self.current_catalog_snapshot or (
            self._recovered_call_catalog
            if self._selected_version == HTTP_COMPAT_VERSION and self._connected
            else None
        )

    async def _catalog_request(
        self, params: dict[str, Any], deadline: float
    ) -> dict[str, Any]:
        if not self._connected:
            raise RuntimeError("MCP HTTP disconnected")
        return await self._request_budget("tools/list", params, deadline)

    def _make_catalog_snapshot(
        self,
        generation: int,
        tools: tuple[ToolDefinition, ...],
        excluded: tuple[str, ...],
    ) -> MCPCatalogSnapshot:
        retained: list[ToolDefinition] = []
        bindings_by_name: list[tuple[str, tuple[HeaderBinding, ...]]] = []
        rejected = 0
        for tool in tools:
            schema = tool.definition.object().get("inputSchema")
            if not isinstance(schema, dict):
                raise ProtocolFailure()
            try:
                bindings = (
                    header_bindings(schema)
                    if self._selected_version == MODERN_VERSION
                    else ()
                )
            except ProtocolFailure:
                rejected += 1
                continue
            retained.append(tool)
            bindings_by_name.append((tool.name, bindings))
        return MCPCatalogSnapshot(
            generation,
            tuple(retained),
            len(excluded),
            rejected,
            excluded,
            tuple(bindings_by_name),
        )

    def _publish_catalog(self, snapshot: MCPCatalogSnapshot) -> None:
        self._bindings = dict(snapshot.bindings)
        self.rejected_http_tools = snapshot.rejected_http_tools
        super()._publish_catalog(snapshot)

    async def _request_tool(
        self, name: str, arguments: dict[str, Any], snapshot: MCPCatalogSnapshot | None
    ) -> dict[str, Any]:
        token = self._call_bindings.set(
            snapshot.headers(name) if snapshot is not None else None
        )
        try:
            return await super()._request_tool(name, arguments, snapshot)
        finally:
            self._call_bindings.reset(token)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        deadline = asyncio.get_running_loop().time() + self._timeout()
        async with asyncio.timeout_at(deadline):
            result = await super().call_tool(name, arguments)
        if asyncio.get_running_loop().time() >= deadline:
            raise TimeoutError("MCP HTTP timeout")
        return result

    async def call_tool_at_generation(
        self, name: str, arguments: dict[str, Any], generation: int
    ) -> str:
        deadline = asyncio.get_running_loop().time() + self._timeout()
        async with asyncio.timeout_at(deadline):
            result = await super().call_tool_at_generation(name, arguments, generation)
        if asyncio.get_running_loop().time() >= deadline:
            raise TimeoutError("MCP HTTP timeout")
        return result
