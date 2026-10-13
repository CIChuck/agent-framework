"""Lower budgets, absolute deadlines and honest resistant-cancellation ownership."""

import asyncio

import pytest

from friday_mcp.server import ModernToolsMCPServer, ServerLimits, ToolCallResult
from tests_mcp.server.test_modern_protocol import definition, rpc
from tests_mcp.server.test_streamable_http import headers, make_server


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
async def test_bounded_admission_and_unrelated_cancellation(budget):
    server = ModernToolsMCPServer(limits=ServerLimits(active_requests=budget))
    release = asyncio.Event()
    starts = []

    async def handler(args):
        starts.append(args["index"])
        await release.wait()
        return ToolCallResult.text("done")

    server.register_tool(definition(), handler)
    issued = [
        asyncio.create_task(
            server.handle(
                rpc(
                    "tools/call",
                    rid=i,
                    params={"name": "echo", "arguments": {"index": i}},
                )
            )
        )
        for i in range(budget)
    ]
    for _ in range(20):
        if len(starts) == budget:
            break
        await asyncio.sleep(0)
    assert len(starts) == server.active_requests == budget
    assert (await server.handle(rpc("tools/call", rid=99, params={"name": "echo"})))[
        "error"
    ]["code"] == -32603
    assert len(starts) == budget
    issued[0].cancel()
    await asyncio.gather(issued[0], return_exceptions=True)
    release.set()
    results = await asyncio.gather(*issued[1:])
    assert all(r["result"]["content"][0]["text"] == "done" for r in results)
    await server.stop()
    assert server.active_requests == 0
    server.start()
    await server.stop()


@pytest.mark.asyncio
async def test_deadline_and_retry_shutdown_preserve_resistant_owner():
    server = ModernToolsMCPServer(
        limits=ServerLimits(
            active_requests=1, timeout_seconds=0.03, shutdown_seconds=0.01
        )
    )
    release = asyncio.Event()
    starts = []

    async def handler(args):
        starts.append(1)
        while not release.is_set():
            try:
                await release.wait()
            except asyncio.CancelledError:
                continue
        return ToolCallResult.text("late")

    server.register_tool(definition(), handler)
    response = await asyncio.wait_for(
        server.handle(rpc("tools/call", params={"name": "echo"})), 0.2
    )
    assert response["error"]["code"] == -32603 and starts == [1]
    assert server.active_requests == 1
    with pytest.raises(TimeoutError, match="incomplete"):
        await server.stop()
    assert server.active_requests == 1
    with pytest.raises(RuntimeError, match="unsettled"):
        server.start()
    release.set()
    await server.stop()
    assert server.active_requests == 0
    server.start()
    assert "result" in await server.handle(rpc())
    await server.stop()


@pytest.mark.asyncio
async def test_expired_original_deadline_zero_invocations():
    server = ModernToolsMCPServer()
    starts = []

    async def handler(args):
        starts.append(1)
        return ToolCallResult.text("done")

    server.register_tool(definition(), handler)
    response = await server.handle(
        rpc("tools/call", params={"name": "echo"}),
        deadline=asyncio.get_running_loop().time() - 1,
    )
    assert response["error"]["code"] == -32603 and not starts


@pytest.mark.asyncio
async def test_http_disconnect_owns_only_one_operation():
    server, _ = make_server()
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def handler(args):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    server.replace_tools([])
    server.register_tool(definition(), handler)
    incoming = asyncio.Queue()
    await incoming.put(
        {
            "type": "http.request",
            "body": rpc("tools/call", params={"name": "echo"}),
            "more_body": False,
        }
    )
    scope = {
        "type": "http",
        "path": "/mcp",
        "method": "POST",
        "scheme": "http",
        "query_string": b"",
        "headers": [
            (k.lower().encode(), v.encode())
            for k, v in {"Host": "127.0.0.1:8000", **headers()}.items()
        ],
    }
    sent = []

    async def send(message):
        sent.append(message)

    request = asyncio.create_task(server(scope, incoming.get, send))
    await started.wait()
    # Same ID on a distinct HTTP owner is legal and unaffected by cancellation.
    assert "result" in await server.handle(rpc())
    await incoming.put({"type": "http.disconnect"})
    await asyncio.wait_for(request, 0.2)
    await cancelled.wait()
    assert not sent
    await server.stop()
    assert server.active_requests == 0


@pytest.mark.asyncio
async def test_http_body_wait_consumes_original_deadline():
    server, calls = make_server(limits=ServerLimits(timeout_seconds=0.03))
    queue = asyncio.Queue()
    scope = {
        "type": "http",
        "path": "/mcp",
        "method": "POST",
        "scheme": "http",
        "query_string": b"",
        "headers": [
            (k.lower().encode(), v.encode())
            for k, v in {"Host": "127.0.0.1:8000", **headers()}.items()
        ],
    }
    messages = []

    async def send(message):
        messages.append(message)

    await asyncio.wait_for(server(scope, queue.get, send), 0.2)
    assert messages[0]["status"] == 500 and not calls
    await server.stop()
    assert server.active_requests == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
async def test_tool_start_rate_budget_is_instance_local_and_bounded(budget):
    from tests_mcp.server.test_server_security import Observer

    observer = Observer()
    server = ModernToolsMCPServer(
        limits=ServerLimits(active_requests=budget), telemetry=observer
    )
    starts = []

    async def handler(args):
        starts.append(1)
        return ToolCallResult.text("done")

    server.register_tool(definition(), handler)
    for _ in range(budget):
        assert "result" in await server.handle(
            rpc("tools/call", params={"name": "echo"})
        )
    assert server.active_requests == 0
    response = await server.handle(rpc("tools/call", params={"name": "echo"}))
    assert response["error"]["code"] == -32603 and len(starts) == budget
    assert len(observer.events) == 2 * budget
    other = ModernToolsMCPServer(limits=ServerLimits(active_requests=budget))
    other.register_tool(definition(), handler)
    assert "result" in await other.handle(rpc("tools/call", params={"name": "echo"}))
    await asyncio.sleep(1.01)
    assert "result" in await server.handle(rpc("tools/call", params={"name": "echo"}))
    assert len(starts) == budget + 2
    await server.stop()
    await other.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("deadline", [True, float("nan"), float("inf")])
async def test_invalid_public_deadline_no_owned_operation(deadline):
    server = ModernToolsMCPServer()
    assert (await server.handle(rpc(), deadline=deadline))["error"]["code"] == -32603
    assert server.active_requests == 0


@pytest.mark.asyncio
async def test_public_later_deadline_cannot_extend_operation_budget():
    server = ModernToolsMCPServer(limits=ServerLimits(timeout_seconds=0.03))

    async def handler(args):
        await asyncio.sleep(1)
        return ToolCallResult.text("late")

    server.register_tool(definition(), handler)
    result = await asyncio.wait_for(
        server.handle(
            rpc("tools/call", params={"name": "echo"}),
            deadline=asyncio.get_running_loop().time() + 10,
        ),
        0.2,
    )
    assert result["error"]["code"] == -32603
    await server.stop()


@pytest.mark.asyncio
async def test_http_blocked_send_remains_owned_until_deadline_without_replay():
    server, calls = make_server(limits=ServerLimits(timeout_seconds=0.03))
    queue = asyncio.Queue()
    await queue.put({"type": "http.request", "body": rpc(), "more_body": False})
    scope = {
        "type": "http",
        "path": "/mcp",
        "method": "POST",
        "scheme": "http",
        "query_string": b"",
        "headers": [
            (k.lower().encode(), v.encode())
            for k, v in {
                "Host": "127.0.0.1:8000",
                **headers("server/discover", name=None),
            }.items()
        ],
    }
    started = asyncio.Event()
    messages = []

    async def send(message):
        messages.append(message)
        if message["type"] == "http.response.start":
            started.set()
        else:
            await asyncio.Event().wait()

    task = asyncio.create_task(server(scope, queue.get, send))
    await started.wait()
    assert server.active_requests == 1
    await asyncio.wait_for(task, 0.2)
    assert [m["type"] for m in messages] == [
        "http.response.start",
        "http.response.body",
    ]
    assert not calls
    await server.stop()
    assert server.active_requests == 0


@pytest.mark.asyncio
async def test_http_disconnect_during_send_has_no_new_messages_or_orphan():
    server, _ = make_server()
    queue = asyncio.Queue()
    await queue.put({"type": "http.request", "body": rpc(), "more_body": False})
    scope = {
        "type": "http",
        "path": "/mcp",
        "method": "POST",
        "scheme": "http",
        "query_string": b"",
        "headers": [
            (k.lower().encode(), v.encode())
            for k, v in {
                "Host": "127.0.0.1:8000",
                **headers("server/discover", name=None),
            }.items()
        ],
    }
    blocked = asyncio.Event()
    messages = []

    async def send(message):
        messages.append(message)
        if message["type"] == "http.response.body":
            blocked.set()
            await asyncio.Event().wait()

    issued = asyncio.create_task(server(scope, queue.get, send))
    await blocked.wait()
    assert server.active_requests == 1
    await queue.put({"type": "http.disconnect"})
    await asyncio.wait_for(issued, 0.2)
    await server.stop()
    assert server.active_requests == 0 and len(messages) == 2


@pytest.mark.asyncio
async def test_resistant_http_send_retains_owner_and_blocks_restart_until_drain():
    server, _ = make_server(
        limits=ServerLimits(
            active_requests=1, timeout_seconds=0.03, shutdown_seconds=0.01
        )
    )
    queue = asyncio.Queue()
    await queue.put({"type": "http.request", "body": rpc(), "more_body": False})
    scope = {
        "type": "http",
        "path": "/mcp",
        "method": "POST",
        "scheme": "http",
        "query_string": b"",
        "headers": [
            (k.lower().encode(), v.encode())
            for k, v in {
                "Host": "127.0.0.1:8000",
                **headers("server/discover", name=None),
            }.items()
        ],
    }
    blocked, release = asyncio.Event(), asyncio.Event()

    async def send(message):
        if message["type"] == "http.response.body":
            blocked.set()
            while not release.is_set():
                try:
                    await release.wait()
                except asyncio.CancelledError:
                    continue

    issued = asyncio.create_task(server(scope, queue.get, send))
    await blocked.wait()
    await asyncio.wait_for(issued, 0.2)
    assert server.active_requests == 1
    with pytest.raises(TimeoutError, match="incomplete"):
        await server.stop()
    with pytest.raises(RuntimeError, match="unsettled"):
        server.start()
    release.set()
    await server.stop()
    assert server.active_requests == 0
    server.start()
    await server.stop()
