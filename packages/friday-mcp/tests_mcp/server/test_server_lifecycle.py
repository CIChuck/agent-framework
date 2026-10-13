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


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
@pytest.mark.parametrize("blocked", ["drain", "lock"])
async def test_resistant_output_shutdown_blocks_restart_until_settlement(
    budget, blocked
):
    from friday_mcp.server import ModernStdioMCPServer
    from tests_mcp.server.test_modern_stdio import (
        BackpressuredWriter,
        MemoryWriter,
        turns_until,
    )

    server = ModernStdioMCPServer(
        limits=ServerLimits(
            active_requests=budget, timeout_seconds=0.03, shutdown_seconds=0.01
        )
    )
    reader, writer = asyncio.StreamReader(), BackpressuredWriter(resistant=True)
    old = asyncio.create_task(server.serve(reader=reader, writer=writer))
    await turns_until(lambda: server._generation is not None)
    generation = server._generation
    release_lock, locked = asyncio.Event(), asyncio.Event()

    class ResistantLock:
        async def __aenter__(self):
            locked.set()
            while not release_lock.is_set():
                try:
                    await release_lock.wait()
                except asyncio.CancelledError:
                    continue

        async def __aexit__(self, *exc):
            pass

    if blocked == "lock":
        generation.lock = ResistantLock()
    reader.feed_data(b"{}\n")
    await asyncio.wait_for(
        locked.wait() if blocked == "lock" else writer.draining.wait(), 0.2
    )
    with pytest.raises(TimeoutError, match="MCP stdio shutdown incomplete"):
        await server.stop()
    assert server._generation is generation and len(generation.outputs) == 1
    assert generation.serving is not old and generation.closing
    assert server._writer is writer and writer.closed
    with pytest.raises(RuntimeError, match="unsettled"):
        server.start()
    replacement_reader, replacement_writer = asyncio.StreamReader(), MemoryWriter()
    with pytest.raises(RuntimeError, match="active or unsettled"):
        await server.serve(reader=replacement_reader, writer=replacement_writer)
    assert not replacement_writer.closed and not replacement_writer.data
    writer.release.set()
    release_lock.set()
    await asyncio.gather(old, return_exceptions=True)
    await server.stop()  # Explicit retry settles retained generation and core work.
    assert server._generation is None and not generation.outputs
    new = asyncio.create_task(
        server.serve(reader=replacement_reader, writer=replacement_writer)
    )
    replacement_reader.feed_data(rpc(rid="replacement") + b"\n")
    await turns_until(lambda: bool(replacement_writer.data))
    assert not replacement_writer.closed
    # Re-entering a captured old finalizer cannot close the newer streams/core.
    await server._stop_connection(generation)
    assert server._writer is replacement_writer and not replacement_writer.closed
    assert not replacement_reader.at_eof()
    await server.stop()
    await new
    assert server._generation is None and server.active_requests == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
async def test_partial_start_resistant_read_truthful_ownership(budget):
    from friday_mcp.server import ModernStdioMCPServer
    from tests_mcp.server.test_modern_stdio import MemoryWriter, turns_until

    read_started, release = asyncio.Event(), asyncio.Event()

    class ResistantReader(asyncio.StreamReader):
        async def read(self, n=-1):
            read_started.set()
            while not release.is_set():
                try:
                    await release.wait()
                except asyncio.CancelledError:
                    continue
            return b""

    server = ModernStdioMCPServer(
        limits=ServerLimits(active_requests=budget, shutdown_seconds=0.01)
    )
    reader, writer = ResistantReader(), MemoryWriter()
    old = asyncio.create_task(server.serve(reader=reader, writer=writer))
    await asyncio.wait_for(read_started.wait(), 0.2)
    generation = server._generation
    with pytest.raises(TimeoutError, match="incomplete"):
        await server.stop()
    assert not old.done() and server._generation is generation and writer.closed
    with pytest.raises(RuntimeError, match="unsettled"):
        server.start()
    release.set()
    await old
    await server.stop()
    assert server._generation is None
    server.start()
    # A mismatched stream pair preserves the caller streams.
    unused = MemoryWriter()
    with pytest.raises(ValueError, match="both streams"):
        await server.serve(writer=unused)
    assert not unused.closed and server._generation is None
    next_reader, next_writer = asyncio.StreamReader(), MemoryWriter()
    new = asyncio.create_task(server.serve(reader=next_reader, writer=next_writer))
    next_reader.feed_data(rpc() + b"\n")
    await turns_until(lambda: bool(next_writer.data))
    await server.stop()
    await new


@pytest.mark.asyncio
async def test_stale_finalizer_and_signal_do_not_touch_replacement(monkeypatch):
    import signal

    from friday_mcp.server import ModernStdioMCPServer
    from tests_mcp.server.test_modern_stdio import MemoryWriter, turns_until

    loop = asyncio.get_running_loop()
    signal_callbacks, removals, transports = [], [], []
    first_reader = asyncio.StreamReader()
    first_writer = MemoryWriter()

    class Transport:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    async def connect_read(factory, pipe):
        protocol = factory()
        reader = protocol._stream_reader
        reader.feed_eof()
        transport = Transport()
        transports.append(transport)
        return transport, protocol

    async def connect_write(factory, pipe):
        transport = Transport()
        transports.append(transport)
        return transport, factory()

    # Native setup uses actual captured stream plumbing but no user stdin/stdout I/O.
    monkeypatch.setattr(loop, "connect_read_pipe", connect_read)
    monkeypatch.setattr(loop, "connect_write_pipe", connect_write)
    monkeypatch.setattr(
        loop, "add_signal_handler", lambda sig, cb: signal_callbacks.append((sig, cb))
    )
    monkeypatch.setattr(loop, "remove_signal_handler", lambda sig: removals.append(sig))
    monkeypatch.setattr(asyncio, "StreamWriter", lambda *args: first_writer)
    server = ModernStdioMCPServer()
    await server.serve()
    assert first_writer.closed and all(t.closed for t in transports)
    assert removals == [signal.SIGTERM] and len(signal_callbacks) == 1
    next_writer = MemoryWriter()
    new = asyncio.create_task(server.serve(reader=first_reader, writer=next_writer))
    first_reader.feed_data(rpc(rid="new") + b"\n")
    await turns_until(lambda: bool(next_writer.data))
    signal_callbacks[0][1]()  # A queued callback from removed old signal registration.
    assert server._writer is next_writer and not next_writer.closed
    assert not first_reader.at_eof() and removals == [signal.SIGTERM]
    await server.stop()
    await new


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
async def test_close_wait_is_bounded_owned_and_retryable(budget):
    from friday_mcp.server import ModernStdioMCPServer
    from tests_mcp.server.test_modern_stdio import MemoryWriter, turns_until

    closing, release = asyncio.Event(), asyncio.Event()

    class ResistantClose(MemoryWriter):
        async def wait_closed(self):
            closing.set()
            while not release.is_set():
                try:
                    await release.wait()
                except asyncio.CancelledError:
                    continue

    server = ModernStdioMCPServer(
        limits=ServerLimits(active_requests=budget, shutdown_seconds=0.01)
    )
    reader, writer = asyncio.StreamReader(), ResistantClose()
    old = asyncio.create_task(server.serve(reader=reader, writer=writer))
    await turns_until(lambda: server._generation is not None)
    with pytest.raises(TimeoutError, match="incomplete"):
        await server.stop()
    await closing.wait()
    generation = server._generation
    assert generation.close_wait is not None and not generation.close_wait.done()
    with pytest.raises(RuntimeError, match="unsettled"):
        server.start()
    release.set()
    await asyncio.gather(old, return_exceptions=True)
    await server.stop()
    assert generation.close_wait.done() and server._generation is None


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
async def test_multiple_operation_writers_are_serialized_and_owned(budget):
    import json

    from friday_mcp.server import ModernStdioMCPServer
    from tests_mcp.server.test_modern_stdio import BackpressuredWriter, turns_until

    server = ModernStdioMCPServer(limits=ServerLimits(active_requests=budget))
    release_handlers = asyncio.Event()
    calls = []

    async def handler(args):
        calls.append(args["index"])
        await release_handlers.wait()
        return ToolCallResult.text(str(args["index"]))

    server.register_tool(definition(), handler)
    reader, writer = asyncio.StreamReader(), BackpressuredWriter()
    serving = asyncio.create_task(server.serve(reader=reader, writer=writer))
    for i in range(budget):
        reader.feed_data(
            rpc("tools/call", rid=i, params={"name": "echo", "arguments": {"index": i}})
            + b"\n"
        )
    await turns_until(lambda: len(calls) == budget)
    connection = server._generation
    release_handlers.set()
    await writer.draining.wait()
    assert len(connection.dispatchers) == budget and writer.writes == 1
    writer.release.set()
    await turns_until(lambda: not connection.dispatchers)
    replies = [json.loads(row) for row in writer.data.splitlines()]
    assert {row["id"] for row in replies} == set(range(budget))
    assert len(replies) == len(calls) == budget and writer.max_drains == 1
    await server.stop()
    await serving
    assert not connection.outputs and server.active_requests == 0


@pytest.mark.asyncio
async def test_cancelled_writer_cannot_emit_after_resistant_lock_release():
    from friday_mcp.server import ModernStdioMCPServer
    from tests_mcp.server.test_modern_stdio import (
        MemoryWriter,
        cancel_frame,
        turns_until,
    )

    locked, cancelled, release = asyncio.Event(), asyncio.Event(), asyncio.Event()

    class ResistantLock:
        async def __aenter__(self):
            locked.set()
            while not release.is_set():
                try:
                    await release.wait()
                except asyncio.CancelledError:
                    cancelled.set()

        async def __aexit__(self, *exc):
            pass

    server = ModernStdioMCPServer()
    reader, writer = asyncio.StreamReader(), MemoryWriter()
    serving = asyncio.create_task(server.serve(reader=reader, writer=writer))
    await turns_until(lambda: server._generation is not None)
    generation = server._generation
    generation.lock = ResistantLock()
    reader.feed_data(rpc(rid="cancelled-write") + b"\n")
    await locked.wait()
    reader.feed_data(cancel_frame("cancelled-write"))
    await asyncio.wait_for(cancelled.wait(), 0.2)
    release.set()
    await turns_until(lambda: not generation.dispatchers)
    assert not writer.data
    reader.feed_data(rpc(rid="unrelated") + b"\n")
    await turns_until(lambda: bool(writer.data))
    assert b"unrelated" in writer.data and b"cancelled-write" not in writer.data
    await server.stop()
    await serving


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
async def test_resistant_native_partial_start_blocks_restart_and_closes_old_transport(
    monkeypatch, budget
):
    from friday_mcp.server import ModernStdioMCPServer
    from tests_mcp.server.test_modern_stdio import MemoryWriter, turns_until

    loop = asyncio.get_running_loop()
    started, release = asyncio.Event(), asyncio.Event()

    class Transport:
        closed = False

        def close(self):
            self.closed = True

    transport = Transport()

    async def resistant_input(factory, pipe):
        started.set()
        while not release.is_set():
            try:
                await release.wait()
            except asyncio.CancelledError:
                continue
        return transport, factory()

    monkeypatch.setattr(loop, "connect_read_pipe", resistant_input)
    server = ModernStdioMCPServer(
        limits=ServerLimits(active_requests=budget, shutdown_seconds=0.01)
    )
    old = asyncio.create_task(server.serve())
    await started.wait()
    generation = server._generation
    with pytest.raises(TimeoutError, match="incomplete"):
        await server.stop()
    assert not generation.serving.done() and not old.done() and not transport.closed
    with pytest.raises(RuntimeError, match="unsettled"):
        server.start()
    release.set()
    await old
    await server.stop()
    assert transport.closed and server._generation is None
    reader, writer = asyncio.StreamReader(), MemoryWriter()
    new = asyncio.create_task(server.serve(reader=reader, writer=writer))
    reader.feed_data(rpc() + b"\n")
    await turns_until(lambda: bool(writer.data))
    await server._stop_connection(generation)
    assert not writer.closed
    await server.stop()
    await new
