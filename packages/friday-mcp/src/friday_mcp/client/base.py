"""Transport-neutral MCP client with bounded legacy/modern request ownership."""

from __future__ import annotations

import asyncio
import logging
import math
import uuid
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Literal

from friday_mcp import __version__
from friday_mcp.client.catalog import MCPCatalogSnapshot
from friday_mcp.client.protocol import (
    LEGACY_VERSION,
    META_PREFIX,
    MODERN_VERSION,
    MODERN_WIRE_ERRORS,
    CatalogPage,
    Discovery,
    FailureCode,
    FrozenJSON,
    ProtocolFailure,
    ProtocolLimits,
    ProtocolProfile,
    ResultSnapshot,
    RPCResponse,
    ToolDefinition,
    ToolResult,
    complete_result,
    encode_json,
    response_from_message,
    validate_message,
    validate_structured,
)
from friday_mcp.protocols import MCPTransport

logger = logging.getLogger(__name__)
type ToolFailureCode = (
    FailureCode | Literal["tool_error", "catalog_unavailable", "unsupported_task"]
)


class MCPError(Exception):
    """MCP protocol error. Peer error text is never passed to this constructor."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"MCP Error {code}: {message}")


class MCPToolExecutionError(MCPError):
    """Local adapter codes are never emitted or interpreted as wire errors."""

    def __init__(self, failure_code: ToolFailureCode) -> None:
        self.failure_code = failure_code
        if failure_code == "tool_error":
            super().__init__(-32020, "MCP tool execution failed")
        elif failure_code == "invalid_result":
            super().__init__(-32021, "Invalid MCP tool result")
        elif failure_code == "catalog_unavailable":
            super().__init__(-32101, "MCP tool catalog unavailable")
        elif failure_code == "unsupported_task":
            super().__init__(-32102, "MCP task execution is unsupported")
        else:
            super().__init__(-32100, str(ProtocolFailure(failure_code)))


class MCPClientBase(ABC):
    PROTOCOL_VERSION = LEGACY_VERSION

    def __init__(
        self,
        name: str,
        *,
        protocol_profile: ProtocolProfile = "legacy",
        limits: ProtocolLimits | None = None,
    ) -> None:
        if protocol_profile not in ("legacy", "modern", "auto"):
            raise ValueError("Invalid MCP protocol profile")
        if limits is not None and not isinstance(limits, ProtocolLimits):
            raise ValueError("Invalid MCP protocol limits")
        self.name = name
        self.protocol_profile = protocol_profile
        self.limits = limits or ProtocolLimits()
        self._selected_version = (
            LEGACY_VERSION if protocol_profile == "legacy" else MODERN_VERSION
        )
        self._transport: MCPTransport | None = None
        self._capabilities = FrozenJSON.from_value({}, self.limits)
        self._identity = FrozenJSON.from_value({}, self.limits)
        self._discovery: Discovery | None = None
        self._catalog: tuple[ToolDefinition, ...] = ()
        self._catalog_snapshot: MCPCatalogSnapshot | None = None
        self._catalog_generation = 0
        self._catalog_attempted = False
        self._catalog_lock = asyncio.Lock()
        self._refresh_tasks: set[asyncio.Task[MCPCatalogSnapshot]] = set()
        self._pending_requests: dict[str, asyncio.Future[RPCResponse]] = {}
        self._exchange_tasks: dict[str, asyncio.Task[RPCResponse]] = {}
        self._control_tasks: set[asyncio.Task[None]] = set()
        self._connected = False
        self._receive_task: asyncio.Task[None] | None = None
        self._connect_deadline: float | None = None
        self.request_timeout_seconds = float(self.limits.timeout_seconds)

    # Compatibility snapshots for existing subclasses; immutable models own
    # retained data. Changing a returned dictionary cannot mutate the client.
    @property
    def _server_capabilities(self) -> dict[str, Any]:
        return self._capabilities.object()

    @_server_capabilities.setter
    def _server_capabilities(self, value: dict[str, Any]) -> None:
        self._capabilities = FrozenJSON.from_value(value, self.limits)

    @property
    def _server_info(self) -> dict[str, Any]:
        return self._identity.object()

    @_server_info.setter
    def _server_info(self, value: dict[str, Any]) -> None:
        self._identity = FrozenJSON.from_value(value, self.limits)

    @property
    def _client_info(self) -> dict[str, str]:
        return {"name": "friday-mcp", "version": __version__}

    @property
    def negotiated_version(self) -> str:
        return self._selected_version

    @abstractmethod
    async def _create_transport(self) -> MCPTransport | None:
        """Create a shared transport; request-scoped subclasses own their lifecycle."""

    def _timeout(self, requested: float | None = None) -> float:
        timeout = self.request_timeout_seconds if requested is None else requested
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or timeout > 86400
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("Invalid MCP request timeout")
        return (
            min(timeout, self.limits.timeout_seconds)
            if self.protocol_profile != "legacy"
            else timeout
        )

    async def connect(self) -> None:
        if self._connected:
            return
        if self._transport is not None or self._exchange_tasks or self._control_tasks:
            await self.disconnect()
        self._invalidate_catalog()
        logger.info("Connecting to MCP server")
        try:
            self._connect_deadline = asyncio.get_running_loop().time() + self._timeout()
            async with asyncio.timeout_at(self._connect_deadline):
                self._transport = await self._create_transport()
                if self._transport is None:
                    raise RuntimeError("MCP shared transport unavailable")
                await self._transport.connect()
                self._receive_task = asyncio.create_task(
                    self._receive_loop(), name="mcp-receiver"
                )
                await self._initialize()
                self._connected = True
        except BaseException:
            try:
                await self.disconnect()
            except BaseException:
                logger.error("MCP connection cleanup incomplete")
            raise
        finally:
            self._connect_deadline = None
        logger.info("Connected to MCP server")

    async def disconnect(self) -> None:
        self._connected = False
        self._invalidate_catalog()
        await self._stop_refreshes()
        receiver = self._receive_task
        if receiver is not None:
            receiver.cancel()
            _, pending = await asyncio.wait((receiver,), timeout=0.5)
            if pending:
                raise RuntimeError("MCP receiver cleanup incomplete")
            if not receiver.cancelled():
                receiver.exception()
            self._receive_task = None
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()
        owned_tasks: set[asyncio.Task[object]] = set(self._control_tasks) | set(
            self._exchange_tasks.values()
        )
        if owned_tasks:
            for task in owned_tasks:
                task.cancel()
        if self._transport:
            await self._transport.disconnect()
            self._transport = None
        if owned_tasks:
            _, pending_control = await asyncio.wait(owned_tasks, timeout=0.5)
            if pending_control:
                raise RuntimeError("MCP request cleanup incomplete")
            self._control_tasks.clear()
            self._exchange_tasks.clear()
        self._capabilities = FrozenJSON.from_value({}, self.limits)
        self._identity = FrozenJSON.from_value({}, self.limits)
        self._invalidate_catalog()
        self._discovery = None

    async def _initialize(self) -> None:
        if self.protocol_profile != "legacy":
            self._selected_version = MODERN_VERSION
            try:
                # Auto reserves half the total connection budget for legacy.
                remaining = (
                    self._timeout()
                    if self._connect_deadline is None
                    else max(
                        0.000001,
                        self._connect_deadline - asyncio.get_running_loop().time(),
                    )
                )
                timeout = (
                    remaining / 2 if self.protocol_profile == "auto" else remaining
                )
                response = await self._request("server/discover", {}, timeout=timeout)
            except MCPError as exc:
                if self.protocol_profile != "auto" or exc.code in MODERN_WIRE_ERRORS:
                    raise
            except TimeoutError:
                if self.protocol_profile != "auto":
                    raise
            else:
                discovery = Discovery.parse(
                    FrozenJSON.from_value(response, self.limits).object(), self.limits
                )
                self._discovery = discovery
                self._capabilities = discovery.capabilities
                self._identity = discovery.server_info
                return
        self._selected_version = LEGACY_VERSION
        response = await self._request(
            "initialize",
            {
                "protocolVersion": LEGACY_VERSION,
                "capabilities": {},
                "clientInfo": self._client_info,
            },
        )
        if response.get("protocolVersion") != LEGACY_VERSION:
            raise ProtocolFailure("unsupported_version")
        capabilities = response.get("capabilities")
        info = response.get("serverInfo")
        if (
            not isinstance(capabilities, dict)
            or any(not isinstance(v, dict) for v in capabilities.values())
            or not isinstance(info, dict)
            or not isinstance(info.get("name"), str)
            or not isinstance(info.get("version"), str)
        ):
            raise ProtocolFailure()
        self._capabilities = FrozenJSON.from_value(capabilities, self.limits)
        self._identity = FrozenJSON.from_value(info, self.limits)
        await self._notify("notifications/initialized", {})

    async def _request(
        self, method: str, params: dict[str, Any], timeout: float | None = None
    ) -> dict[str, Any]:
        if self._transport is None:
            raise RuntimeError("Not connected")
        if self._receive_task is not None and self._receive_task.done():
            raise ConnectionError("MCP transport closed")
        budget = self._timeout(timeout)
        deadline = asyncio.get_running_loop().time() + budget
        if (
            len(set(self._pending_requests) | set(self._exchange_tasks))
            + len(self._control_tasks)
            >= self.limits.concurrent_requests
        ):
            raise ProtocolFailure("limit_exceeded")
        request_id = str(uuid.uuid4())
        payload: dict[str, Any] = FrozenJSON.from_value(
            params, self.limits, byte_limit=self.limits.frame_bytes
        ).object()
        if self._selected_version == MODERN_VERSION:
            payload["_meta"] = {
                META_PREFIX + "protocolVersion": MODERN_VERSION,
                META_PREFIX + "clientInfo": self._client_info,
                META_PREFIX + "clientCapabilities": {},
            }
        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": payload,
        }
        encode_json(message, self.limits, byte_limit=self.limits.frame_bytes)
        if asyncio.get_running_loop().time() >= deadline:
            raise TimeoutError("MCP request timed out")
        future: asyncio.Future[RPCResponse] = asyncio.get_running_loop().create_future()
        self._pending_requests[request_id] = future

        async def exchange() -> RPCResponse:
            if self._transport is None:
                raise ConnectionError("MCP transport closed")
            if asyncio.get_running_loop().time() >= deadline:
                raise TimeoutError("MCP request timed out")
            await self._transport.send(message)
            return await future

        exchange_task = asyncio.create_task(exchange(), name="mcp-request-exchange")
        self._exchange_tasks[request_id] = exchange_task

        def exchange_finished(done: asyncio.Task[RPCResponse]) -> None:
            if not done.cancelled():
                done.exception()
            if self._exchange_tasks.get(request_id) is done:
                self._exchange_tasks.pop(request_id, None)

        exchange_task.add_done_callback(exchange_finished)

        try:
            _, pending = await asyncio.wait(
                (exchange_task,),
                timeout=max(0, deadline - asyncio.get_running_loop().time()),
            )
            if pending:
                raise TimeoutError("MCP request timed out")
            response = exchange_task.result()
            if response.error_code is not None:
                raise MCPError(response.error_code, "MCP peer rejected request")
            if response.result is None:
                raise ProtocolFailure()
            result = response.result.object()
            complete_result(result, self._selected_version == MODERN_VERSION)
            return ResultSnapshot(result, response.wire_bytes)
        except (TimeoutError, asyncio.CancelledError):
            exchange_task.cancel()
            if method != "initialize" and self._request_was_issued(request_id):
                await self._cancel_request(request_id)
            raise
        finally:
            if not exchange_task.done():
                exchange_task.cancel()
            self._pending_requests.pop(request_id, None)
            self._forget_request(request_id)
            if not future.done():
                future.cancel()

    def _request_was_issued(self, request_id: str) -> bool:
        return False  # Transport-specific cancellation belongs to stdio.

    def _forget_request(self, request_id: str) -> None:
        return None

    def _received_wire_bytes(self, message: dict[str, Any]) -> int:
        return len(
            encode_json(message, self.limits, byte_limit=self.limits.frame_bytes)
        )

    async def _cancel_request(self, request_id: str) -> None:
        task = asyncio.create_task(
            self._notify("notifications/cancelled", {"requestId": request_id}),
            name="mcp-cancellation",
        )
        self._control_tasks.add(task)

        def settled(done: asyncio.Task[None]) -> None:
            if not done.cancelled():
                done.exception()
            self._control_tasks.discard(done)

        task.add_done_callback(settled)
        _, pending = await asyncio.wait((task,), timeout=0.1)
        if pending:
            task.cancel()
            await asyncio.wait((task,), timeout=0.1)

    async def _notify(self, method: str, params: dict[str, Any]) -> None:
        if self._transport is None:
            raise RuntimeError("Not connected")
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        encode_json(message, self.limits, byte_limit=self.limits.frame_bytes)
        await self._transport.send(message)

    async def _receive_loop(self) -> None:
        if self._transport is None:
            return
        while True:
            try:
                message = await self._transport.receive()
                await self._handle_message(message)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.error("MCP receive failed")
                self._connected = False
                self._invalidate_catalog()
                for future in self._pending_requests.values():
                    if not future.done():
                        future.set_exception(ConnectionError("MCP transport closed"))
                break

    async def _handle_message(self, message: dict[str, Any]) -> None:
        bounded = validate_message(
            message, self.limits, modern=self._selected_version == MODERN_VERSION
        )
        if "method" in bounded:
            await self._handle_server_message(bounded)
            return
        response = response_from_message(
            bounded, self.limits, self._received_wire_bytes(message)
        )
        # IDs are type-sensitive: an integer can never match our string UUIDs.
        if isinstance(response.request_id, str):
            future = self._pending_requests.get(response.request_id)
            if future is not None and not future.done():
                future.set_result(response)

    async def _handle_server_message(self, message: dict[str, Any]) -> None:
        if "id" in message:
            if self._selected_version == MODERN_VERSION:
                # Modern stdio forbids server requests AND client responses.
                raise ProtocolFailure()
            if self._transport is not None:
                await asyncio.wait_for(
                    self._transport.send(
                        {
                            "jsonrpc": "2.0",
                            "id": message["id"],
                            "error": {
                                "code": -32601,
                                "message": "Method not supported",
                            },
                        }
                    ),
                    timeout=0.25,
                )
        logger.debug("Received MCP server notification")

    @property
    def current_catalog_snapshot(self) -> MCPCatalogSnapshot | None:
        return self._catalog_snapshot

    @property
    def outstanding_catalog_owners(self) -> int:
        return len(self._refresh_tasks)

    def _invalidate_catalog(self) -> None:
        self._catalog_generation += 1
        self._catalog_snapshot = None
        self._catalog = ()

    async def _stop_refreshes(self) -> None:
        tasks = set(self._refresh_tasks)
        for task in tasks:
            task.cancel()
        if tasks:
            _, pending = await asyncio.wait(tasks, timeout=0.5)
            if pending:
                raise RuntimeError("MCP catalog cleanup incomplete")

    async def refresh_tool_catalog(self) -> MCPCatalogSnapshot:
        deadline = asyncio.get_running_loop().time() + self._timeout()
        if len(self._refresh_tasks) >= self.limits.concurrent_requests:
            raise ProtocolFailure("limit_exceeded")
        self._catalog_attempted = True
        task = asyncio.create_task(
            self._refresh_catalog(deadline), name="mcp-catalog-refresh"
        )
        self._refresh_tasks.add(task)

        def settled(done: asyncio.Task[MCPCatalogSnapshot]) -> None:
            if not done.cancelled():
                done.exception()
            self._refresh_tasks.discard(done)

        task.add_done_callback(settled)
        try:
            return await task
        finally:
            if not task.done():
                task.cancel()

    async def _refresh_catalog(self, deadline: float) -> MCPCatalogSnapshot:
        async with asyncio.timeout_at(deadline), self._catalog_lock:
            self._invalidate_catalog()
            generation = self._catalog_generation
            tools, excluded = await self._discover_catalog(deadline)
            snapshot = self._make_catalog_snapshot(generation, tools, excluded)
            if generation != self._catalog_generation:
                raise MCPToolExecutionError("catalog_unavailable")
            if asyncio.get_running_loop().time() >= deadline:
                raise TimeoutError("MCP catalog timeout")
            self._publish_catalog(snapshot)
            return snapshot

    def _make_catalog_snapshot(
        self,
        generation: int,
        tools: tuple[ToolDefinition, ...],
        excluded: tuple[str, ...],
    ) -> MCPCatalogSnapshot:
        return MCPCatalogSnapshot(
            generation, tools, len(excluded), excluded_task_names=excluded
        )

    def _publish_catalog(self, snapshot: MCPCatalogSnapshot) -> None:
        self._catalog = snapshot.definitions
        self._catalog_snapshot = snapshot

    async def _catalog_request(
        self, params: dict[str, Any], deadline: float
    ) -> dict[str, Any]:
        return await self._request(
            "tools/list",
            params,
            timeout=max(0.000001, deadline - asyncio.get_running_loop().time()),
        )

    async def _discover_catalog(
        self, deadline: float
    ) -> tuple[tuple[ToolDefinition, ...], tuple[str, ...]]:
        if "tools" not in self._capabilities.object():
            return (), ()
        tools: list[ToolDefinition] = []
        excluded: list[str] = []
        cursors: set[str] = set()
        names: set[str] = set()
        cursor: str | None = None
        total = 0
        for _ in range(self.limits.catalog_pages):
            response = await self._catalog_request(
                {"cursor": cursor} if cursor is not None else {}, deadline
            )
            total += (
                response.wire_bytes
                if isinstance(response, ResultSnapshot)
                else len(
                    encode_json(
                        response, self.limits, byte_limit=self.limits.frame_bytes
                    )
                )
            )
            if total > self.limits.catalog_bytes:
                raise ProtocolFailure("limit_exceeded")
            page = CatalogPage.parse(
                FrozenJSON.from_value(response, self.limits).object(),
                self._selected_version == MODERN_VERSION,
                self.limits,
            )
            if len(names) + len(page.tools) > self.limits.catalog_tools:
                raise ProtocolFailure("limit_exceeded")
            for tool in page.tools:
                if tool.name in names:
                    raise ProtocolFailure()
                names.add(tool.name)
                execution = tool.definition.object().get("execution")
                if (
                    self._selected_version == "2025-11-25"
                    and isinstance(execution, dict)
                    and execution.get("taskSupport") == "required"
                ):
                    excluded.append(tool.name)
                else:
                    tools.append(tool)
            cursor = page.cursor
            if cursor is None:
                return tuple(tools), tuple(excluded)
            if cursor in cursors:
                raise ProtocolFailure()
            cursors.add(cursor)
        raise ProtocolFailure("limit_exceeded")

    async def list_tools(self) -> list[dict[str, Any]]:
        return (await self.refresh_tool_catalog()).tools()

    async def call_tool_at_generation(
        self, name: str, arguments: dict[str, Any], generation: int
    ) -> str:
        return await self._call_tool(name, arguments, generation)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        return await self._call_tool(name, arguments, None)

    async def _call_tool(
        self, name: str, arguments: dict[str, Any], generation: int | None
    ) -> str:
        snapshot = (
            self.current_catalog_snapshot
            if generation is not None
            else self._catalog_for_direct_call()
        )
        if generation is not None and (
            type(generation) is not int
            or snapshot is None
            or generation != snapshot.generation
        ):
            raise MCPToolExecutionError("catalog_unavailable")
        if snapshot is not None and name in snapshot.excluded_task_names:
            raise MCPToolExecutionError("unsupported_task")
        tool = snapshot.tool(name) if snapshot is not None else None
        if (snapshot is not None and tool is None) or (
            self._catalog_attempted and snapshot is None
        ):
            raise MCPToolExecutionError("catalog_unavailable")
        output_schema = tool.output_schema if tool is not None else None
        try:
            response = await self._request_tool(name, arguments, snapshot)
            bounded = FrozenJSON.from_value(
                response, self.limits, byte_limit=self.limits.result_bytes
            ).object()
            result = ToolResult.parse(
                bounded,
                self._selected_version == MODERN_VERSION,
                self.limits,
                compatibility=self._selected_version == "2025-11-25",
            )
            if bounded.get("isError", False):
                raise MCPToolExecutionError("tool_error")
            if output_schema is not None:
                validate_structured(result.structured, output_schema, self.limits)
            return result.text(self.limits)
        except ProtocolFailure as exc:
            raise MCPToolExecutionError(exc.failure_code) from None

    def _catalog_for_direct_call(self) -> MCPCatalogSnapshot | None:
        return self.current_catalog_snapshot

    async def _request_tool(
        self, name: str, arguments: dict[str, Any], snapshot: MCPCatalogSnapshot | None
    ) -> dict[str, Any]:
        return await self._request("tools/call", {"name": name, "arguments": arguments})

    async def list_prompts(self) -> list[dict[str, Any]]:
        """
        Get available prompts from the server.

        Returns:
            List of prompt definitions.
        """
        if "prompts" not in self._server_capabilities:
            return []

        response = await self._request("prompts/list", {})
        prompts = response.get("prompts", [])
        if not isinstance(prompts, list):
            raise ValueError("Invalid MCP prompt catalog")
        return prompts

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
        resources = response.get("resources", [])
        if not isinstance(resources, list):
            raise ValueError("Invalid MCP resource catalog")
        return resources

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
        return self._capabilities.object()

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected

    async def __aenter__(self) -> MCPClientBase:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        if exc_val is None:
            await self.disconnect()
        else:
            try:
                await self.disconnect()
            except BaseException:
                logger.error("MCP context cleanup incomplete")
