"""Stateless modern tools role with atomic catalog and honest task ownership."""

from __future__ import annotations

import asyncio
import secrets
from collections.abc import Awaitable, Callable, Iterable
from contextlib import suppress
from dataclasses import dataclass

from friday_core import TelemetryInterface

from friday_mcp.client.protocol import JSONValue
from friday_mcp.server.protocol import (
    DEFAULT_SERVER_LIMITS,
    IDENTITY,
    PREFIX,
    VERSION,
    RegisteredTool,
    ServerLimits,
    ServerRequest,
    ServerWireError,
    ToolCallResult,
    ToolHandler,
    encode,
    safe_error_id,
)


@dataclass(frozen=True)
class _Catalog:
    tools: tuple[RegisteredTool, ...]
    pages: tuple[tuple[RegisteredTool, ...], ...]
    cursors: tuple[str, ...]


class ModernToolsMCPServer:
    """Explicit async tools only. No protocol sessions, callbacks or hidden registry."""

    def __init__(
        self,
        *,
        limits: ServerLimits = DEFAULT_SERVER_LIMITS,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        if not isinstance(limits, ServerLimits):
            raise ValueError("Invalid MCP server limits")
        self.limits = limits
        self._telemetry = telemetry
        self._owners: set[asyncio.Task[object]] = set()
        self._closed = False
        self._catalog = self._stage(())

    @property
    def active_requests(self) -> int:
        return len(self._owners)

    @property
    def tools(self) -> tuple[dict[str, JSONValue], ...]:
        return tuple(t.definition(self.limits) for t in self._catalog.tools)

    def _result(self, fields: dict[str, JSONValue]) -> dict[str, JSONValue]:
        return {
            "resultType": "complete",
            "_meta": {PREFIX + "serverInfo": dict(IDENTITY)},
            **fields,
        }

    def _page(
        self, tools: tuple[RegisteredTool, ...], cursor: str | None
    ) -> dict[str, JSONValue]:
        fields: dict[str, JSONValue] = {
            "tools": [t.definition(self.limits) for t in tools]
        }
        if cursor is not None:
            fields["nextCursor"] = cursor
        return self._result({**fields, "ttlMs": 0, "cacheScope": "private"})

    def _stage(self, tools: Iterable[RegisteredTool]) -> _Catalog:
        staged: list[RegisteredTool] = []
        names: set[str] = set()
        total = 0
        for tool in tools:
            if len(staged) >= self.limits.catalog_tools or not isinstance(
                tool, RegisteredTool
            ):
                raise ValueError("MCP catalog limit exceeded")
            # Revalidate direct constructors and lower limits before publishing.
            checked = RegisteredTool.from_definition(
                tool.definition(self.limits), tool.handler, limits=self.limits
            )
            if checked.name in names:
                raise ValueError("MCP tool name collision")
            total += len(
                encode(
                    checked.definition(self.limits),
                    self.limits,
                    byte_limit=self.limits.catalog_bytes,
                )
            )
            if total > self.limits.catalog_bytes:
                raise ValueError("MCP catalog limit exceeded")
            names.add(checked.name)
            staged.append(checked)
        staged.sort(key=lambda t: t.name)
        pages: list[tuple[RegisteredTool, ...]] = []
        current: list[RegisteredTool] = []
        # Reserve the worst encoded ID and full cursor before byte partitioning.
        reserved_id = "\0" * self.limits.identity_bytes
        reserved_cursor = "x" * min(32, self.limits.cursor_bytes)

        def fits(items: list[RegisteredTool]) -> bool:
            try:
                encode(
                    {
                        "jsonrpc": "2.0",
                        "id": reserved_id,
                        "result": self._page(tuple(items), reserved_cursor),
                    },
                    self.limits,
                )
                return True
            except ServerWireError:
                return False

        for tool in staged:
            if len(current) == self.limits.page_tools or not fits([*current, tool]):
                if not current:
                    raise ValueError("MCP page limits cannot represent catalog")
                pages.append(tuple(current))
                current = []
            current.append(tool)
            if not fits(current):
                raise ValueError("MCP page limits cannot represent catalog")
        pages.append(tuple(current))
        if len(pages) > self.limits.catalog_pages or not fits([]):
            raise ValueError("MCP page limits cannot represent catalog")
        # Cursor length is bounded even with deliberately tiny configuration.
        if len(pages) > 1 and self.limits.cursor_bytes < 24:
            raise ValueError("MCP cursor limits cannot represent catalog")
        cursors = tuple(secrets.token_urlsafe(18) for _ in range(len(pages) - 1))
        return _Catalog(tuple(staged), tuple(pages), cursors)

    def replace_tools(self, tools: Iterable[RegisteredTool]) -> None:
        self._catalog = self._stage(tools)

    def register_tool(self, definition: object, handler: ToolHandler) -> None:
        tool = RegisteredTool.from_definition(definition, handler, limits=self.limits)
        self.replace_tools((*self._catalog.tools, tool))

    def remove_tool(self, name: str) -> None:
        self.replace_tools(t for t in self._catalog.tools if t.name != name)

    def start(self) -> None:
        if self._owners:
            raise RuntimeError("MCP server has unsettled operations")
        self._closed = False

    async def stop(self) -> None:
        self._closed = True
        owners = tuple(self._owners)
        for task in owners:
            task.cancel()
        if owners:
            _, pending = await asyncio.wait(
                owners, timeout=self.limits.shutdown_seconds
            )
            if pending:
                raise TimeoutError("MCP server shutdown incomplete")

    async def run_owned[T](
        self, operation: Callable[[], Awaitable[T]], deadline: float
    ) -> T:
        """Bound admission and retain owners that resist cancellation."""
        if self._closed or len(self._owners) >= self.limits.active_requests:
            raise ServerWireError(-32603)
        remaining = deadline - asyncio.get_running_loop().time()
        if remaining <= 0:
            raise ServerWireError(-32603)

        async def invoke() -> T:
            return await operation()

        task = asyncio.create_task(invoke())
        tracked: asyncio.Task[object] = task
        self._owners.add(tracked)

        def settled(done: asyncio.Task[object]) -> None:
            self._owners.discard(done)
            if not done.cancelled():
                done.exception()

        tracked.add_done_callback(settled)
        try:
            done, _ = await asyncio.wait((tracked,), timeout=remaining)
            if not done:
                tracked.cancel()
                raise ServerWireError(-32603)
            return task.result()
        except asyncio.CancelledError:
            tracked.cancel()
            raise

    async def handle(
        self, raw: bytes, *, deadline: float | None = None
    ) -> dict[str, JSONValue]:
        until = (
            asyncio.get_running_loop().time() + self.limits.timeout_seconds
            if deadline is None
            else deadline
        )

        async def operation() -> dict[str, JSONValue]:
            request = ServerRequest.parse(raw, self.limits)
            return await self.dispatch(request)

        try:
            return await self.run_owned(operation, until)
        except ServerWireError as error:
            return error.response(safe_error_id(raw, self.limits))
        except Exception:
            return ServerWireError(-32603).response(safe_error_id(raw, self.limits))

    async def dispatch(self, request: ServerRequest) -> dict[str, JSONValue]:
        if request.request_id is None:
            raise ServerWireError(-32601)
        if request.version != VERSION:
            raise ServerWireError(-32022)
        params = request.params
        catalog = self._catalog
        if request.method == "server/discover":
            result = self._result(
                {
                    "supportedVersions": [VERSION],
                    "capabilities": {"tools": {}},
                    "ttlMs": 0,
                    "cacheScope": "private",
                }
            )
        elif request.method == "tools/list":
            page = 0
            if "cursor" in params:
                cursor = params["cursor"]
                if (
                    not isinstance(cursor, str)
                    or not cursor
                    or len(cursor.encode("utf-8")) > self.limits.cursor_bytes
                    or cursor not in catalog.cursors
                ):
                    raise ServerWireError(-32602)
                page = catalog.cursors.index(cursor) + 1
            result = self._page(
                catalog.pages[page],
                catalog.cursors[page] if page < len(catalog.cursors) else None,
            )
        elif request.method == "tools/call":
            name = params.get("name")
            args = params.get("arguments", {})
            tool = next((t for t in catalog.tools if t.name == name), None)
            if (
                not isinstance(name, str)
                or tool is None
                or not isinstance(args, dict)
                or not tool.validate_input(args, self.limits)
            ):
                raise ServerWireError(-32602)
            try:
                result = await self._execute(tool, args)
            except ServerWireError:
                raise ServerWireError(-32603) from None
        else:
            raise ServerWireError(-32601)
        response: dict[str, JSONValue] = {
            "jsonrpc": "2.0",
            "id": request.request_id,
            "result": result,
        }
        try:
            encode(response, self.limits)
        except ServerWireError:
            raise ServerWireError(-32603) from None
        return response

    def selected_tool(self, request: ServerRequest) -> RegisteredTool | None:
        return next(
            (t for t in self._catalog.tools if t.name == request.params.get("name")),
            None,
        )

    async def _execute(
        self, tool: RegisteredTool, arguments: dict[str, JSONValue]
    ) -> dict[str, JSONValue]:
        span: str | None = None
        outcome = "error"
        observer = self._telemetry
        if observer is not None:
            with suppress(Exception):
                span = observer.start_span("mcp.tools.call")
        try:
            try:
                returned = await tool.handler(arguments)
            except asyncio.CancelledError:
                outcome = "cancelled"
                raise
            except Exception:
                returned = ToolCallResult.text(
                    "Tool execution failed", is_error=True, limits=self.limits
                )
            if not isinstance(returned, ToolCallResult):
                raise ServerWireError(-32603)
            # Validate immutable direct constructors as well as factories.
            try:
                result = ToolCallResult.from_value(
                    returned.value(self.limits), limits=self.limits
                ).value(self.limits)
            except ServerWireError:
                raise ServerWireError(-32603) from None
            if not tool.validate_output(result, self.limits):
                raise ServerWireError(-32603)
            result["_meta"] = {PREFIX + "serverInfo": dict(IDENTITY)}
            outcome = "error" if result.get("isError") is True else "success"
            return result
        finally:
            if observer is not None and span is not None:
                with suppress(Exception):
                    observer.end_span(
                        span, {"method": "tools/call", "outcome": outcome}
                    )
