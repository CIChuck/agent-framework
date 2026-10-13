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
