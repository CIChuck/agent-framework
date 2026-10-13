"""Actual stdin/stdout framing, responsive cancellation and child settlement."""

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

from tests_mcp.server.test_modern_protocol import rpc

FIXTURE = Path(__file__).parents[1] / "fixtures/friday_modern_tools_server.py"


async def start_child(tmp_path):
    counter = tmp_path / "stdio-counters.jsonl"
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        str(FIXTURE),
        "stdio",
        str(counter),
        cwd=tmp_path,
        env=dict(os.environ),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    return process, counter


async def read_response(process):
    return json.loads(await asyncio.wait_for(process.stdout.readline(), 2))


async def finish(process):
    if process.returncode is None:
        process.terminate()
    await asyncio.wait_for(process.wait(), 2)
    stderr = await process.stderr.read()
    assert b"synthetic-private-exception" not in stderr
    assert process.returncode == 0, stderr.decode()


@pytest.mark.asyncio
async def test_real_stdio_fragmented_frames_and_stdout_only_json(tmp_path):
    process, counter = await start_child(tmp_path)
    try:
        raw = (
            rpc("tools/call", params={"name": "echo", "arguments": {"text": "世界"}})
            + b"\n"
        )
        process.stdin.write(raw[:13])
        await process.stdin.drain()
        process.stdin.write(raw[13:])
        await process.stdin.drain()
        assert (await read_response(process))["result"]["structuredContent"] == {
            "text": "世界"
        }
        process.stdin.write(rpc(rid="probe") + b"\n")
        await process.stdin.drain()
        assert (await read_response(process))["id"] == "probe"
    finally:
        await finish(process)
    rows = [json.loads(x) for x in counter.read_text().splitlines()]
    assert sum(r.get("event") == "handler_start" for r in rows) == 1
    assert rows[-1] == {"event": "server_stopped", "active": 0}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bad,code",
    [
        (b"\xff\n", -32700),
        (b"[{}]\n", -32600),
        (b'{"jsonrpc":"2.0","method":"x","method":"y"}\n', -32700),
        (b"x" * 65537 + b"\n", -32600),
    ],
)
async def test_bad_stdio_lines_do_not_poison_next_frame(tmp_path, bad, code):
    process, _ = await start_child(tmp_path)
    try:
        process.stdin.write(bad)
        await process.stdin.drain()
        assert (await read_response(process))["error"]["code"] == code
        process.stdin.write(rpc() + b"\n")
        await process.stdin.drain()
        assert "result" in await read_response(process)
    finally:
        await finish(process)


@pytest.mark.asyncio
async def test_stdio_reader_cancel_and_duplicate_active_id_no_replay(tmp_path):
    process, counter = await start_child(tmp_path)
    try:
        process.stdin.write(
            rpc(
                "tools/call",
                rid=10,
                params={"name": "echo", "arguments": {"hold": True}},
            )
            + b"\n"
        )
        await process.stdin.drain()
        for _ in range(100):
            if counter.exists() and "handler_start" in counter.read_text():
                break
            await asyncio.sleep(0.01)
        assert "handler_start" in counter.read_text()
        process.stdin.write(rpc("tools/call", rid=10, params={"name": "echo"}) + b"\n")
        await process.stdin.drain()
        assert (await read_response(process))["error"]["code"] == -32600
        process.stdin.write(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/cancelled",
                    "params": {"requestId": 10},
                }
            ).encode()
            + b"\n"
        )
        process.stdin.write(rpc(rid=11) + b"\n")
        await process.stdin.drain()
        assert (await read_response(process))["id"] == 11
        process.stdin.write(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/cancelled",
                    "params": {"requestId": 999},
                }
            ).encode()
            + b"\n"
        )
    finally:
        await finish(process)
    rows = [json.loads(x) for x in counter.read_text().splitlines()]
    assert sum(r.get("event") == "handler_start" for r in rows) == 1
    assert sum(r.get("event") == "handler_terminal" for r in rows) == 1
    assert rows[-1]["active"] == 0


@pytest.mark.asyncio
async def test_eof_and_partial_line_cleanup(tmp_path):
    process, _ = await start_child(tmp_path)
    process.stdin.write(b"partial")
    await process.stdin.drain()
    process.stdin.close()
    assert (await read_response(process))["error"]["code"] == -32700
    await asyncio.wait_for(process.wait(), 2)
    assert process.returncode == 0


class MemoryWriter:
    def __init__(self, fail=False):
        self.data = bytearray()
        self.closed = False
        self.fail = fail

    def write(self, raw):
        if self.fail:
            raise BrokenPipeError("synthetic-private-pipe-error")
        self.data.extend(raw)

    async def drain(self):
        await asyncio.sleep(0)

    def close(self):
        self.closed = True

    async def wait_closed(self):
        await asyncio.sleep(0)


@pytest.mark.asyncio
@pytest.mark.parametrize("fail", [False, True])
async def test_owned_stream_stop_restart_and_write_failure(fail):
    from friday_mcp.server import ModernStdioMCPServer

    server = ModernStdioMCPServer()
    reader = asyncio.StreamReader()
    writer = MemoryWriter(fail)
    serving = asyncio.create_task(server.serve(reader=reader, writer=writer))
    reader.feed_data(rpc() + b"\n")
    for _ in range(100):
        if writer.data or fail and server._connection is None:
            break
        await asyncio.sleep(0)
    if not fail:
        assert json.loads(writer.data)["result"]["supportedVersions"]
    await server.stop()
    await asyncio.wait_for(serving, 0.2)
    assert writer.closed and server.active_requests == 0
    next_reader, next_writer = asyncio.StreamReader(), MemoryWriter()
    restarted = asyncio.create_task(
        server.serve(reader=next_reader, writer=next_writer)
    )
    next_reader.feed_data(rpc(rid="new-owner") + b"\n")
    for _ in range(100):
        if next_writer.data:
            break
        await asyncio.sleep(0)
    assert json.loads(next_writer.data)["id"] == "new-owner"
    await server.stop()
    await asyncio.wait_for(restarted, 0.2)
    assert next_writer.closed


@pytest.mark.asyncio
async def test_unknown_completed_malformed_notifications_have_no_response():
    from friday_mcp.server import ModernStdioMCPServer

    server = ModernStdioMCPServer()
    reader, writer = asyncio.StreamReader(), MemoryWriter()
    serving = asyncio.create_task(server.serve(reader=reader, writer=writer))
    notifications = [
        {"jsonrpc": "2.0", "method": "custom/notify"},
        {
            "jsonrpc": "2.0",
            "method": "notifications/cancelled",
            "params": {"requestId": 999},
        },
        {
            "jsonrpc": "2.0",
            "method": "notifications/cancelled",
            "params": {"requestId": None},
        },
        {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": None},
    ]
    reader.feed_data(
        b"\n".join(json.dumps(n).encode() for n in notifications)
        + b"\n"
        + rpc(rid="only-response")
        + b"\n"
    )
    for _ in range(100):
        if writer.data:
            break
        await asyncio.sleep(0)
    assert len(writer.data.splitlines()) == 1
    assert json.loads(writer.data)["id"] == "only-response"
    await server.stop()
    await serving


class BackpressuredWriter(MemoryWriter):
    def __init__(self, *, resistant=False):
        super().__init__()
        self.draining = asyncio.Event()
        self.release = asyncio.Event()
        self.resistant = resistant
        self.writes = 0
        self.in_drain = 0
        self.max_drains = 0

    def write(self, raw):
        self.writes += 1
        super().write(raw)

    async def drain(self):
        self.draining.set()
        self.in_drain += 1
        self.max_drains = max(self.max_drains, self.in_drain)
        try:
            while not self.release.is_set():
                try:
                    await self.release.wait()
                except asyncio.CancelledError:
                    if not self.resistant:
                        raise
        finally:
            self.in_drain -= 1


async def turns_until(predicate):
    for _ in range(200):
        if predicate():
            return
        await asyncio.sleep(0)
    assert predicate()


def cancel_frame(rid):
    return (
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "notifications/cancelled",
                "params": {"requestId": rid},
            }
        ).encode()
        + b"\n"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
@pytest.mark.parametrize("kind", ["malformed", "duplicate", "admission", "oversize"])
@pytest.mark.parametrize("blocked", ["drain", "lock"])
async def test_backpressured_rejections_keep_reader_responsive(budget, kind, blocked):
    from friday_mcp.server import ModernStdioMCPServer, ServerLimits
    from tests_mcp.server.test_modern_protocol import definition

    server = ModernStdioMCPServer(
        limits=ServerLimits(active_requests=budget, timeout_seconds=0.5)
    )
    reader, writer = asyncio.StreamReader(), BackpressuredWriter()
    starts, cancelled = [], asyncio.Event()

    async def held(args):
        starts.append(args["index"])
        try:
            await asyncio.Event().wait()
        finally:
            if args["index"] == 0:
                cancelled.set()

    server.register_tool(definition(), held)
    serving = asyncio.create_task(server.serve(reader=reader, writer=writer))
    try:
        for i in range(budget):
            reader.feed_data(
                rpc(
                    "tools/call",
                    rid=i,
                    params={"name": "echo", "arguments": {"index": i}},
                )
                + b"\n"
            )
        await turns_until(lambda: len(starts) == budget)
        connection = server._generation
        if blocked == "lock":
            await connection.lock.acquire()
        bad = {
            "malformed": b"{}\n",
            "duplicate": rpc("tools/call", rid=0, params={"name": "echo"}) + b"\n",
            "admission": rpc("tools/call", rid=99, params={"name": "echo"}) + b"\n",
            "oversize": b"x" * 65537 + b"\n",
        }[kind]
        reader.feed_data(bad)
        await turns_until(lambda: len(connection.outputs) == 1)
        if blocked == "drain":
            await asyncio.wait_for(writer.draining.wait(), 0.2)
        reader.feed_data(cancel_frame(0))
        await asyncio.wait_for(cancelled.wait(), 0.2)
        assert starts == list(range(budget))
        assert len(connection.outputs) <= budget
        assert len(connection.dispatchers) <= budget
        assert writer.writes == int(blocked == "drain")
        assert writer.max_drains <= 1
        # EOF remains readable with no delivery progress.
        reader.feed_eof()
        await asyncio.wait_for(serving, 0.3)
        assert writer.closed and not connection.outputs and not connection.dispatchers
        assert server.active_requests == 0
    finally:
        writer.release.set()
        if server._generation is not None and server._generation.lock.locked():
            server._generation.lock.release()
        await server.stop()
        await asyncio.gather(serving, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
async def test_rejection_output_saturation_closes_without_unbounded_work(budget):
    from friday_mcp.server import ModernStdioMCPServer, ServerLimits

    server = ModernStdioMCPServer(limits=ServerLimits(active_requests=budget))
    reader, writer = asyncio.StreamReader(), BackpressuredWriter()
    serving = asyncio.create_task(server.serve(reader=reader, writer=writer))
    await turns_until(lambda: server._generation is not None)
    connection = server._generation
    reader.feed_data(b"{}\n" * budget)
    await turns_until(lambda: len(connection.outputs) == budget)
    reader.feed_data(b"{}\n")
    await asyncio.wait_for(serving, 0.3)
    assert writer.closed and writer.writes <= 1 and writer.max_drains <= 1
    assert not connection.outputs and not connection.dispatchers
    assert server._generation is None and server.active_requests == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
@pytest.mark.parametrize("oversized", [False, True])
async def test_first_byte_deadline_expires_fragmented_frame_without_handler(
    budget, oversized
):
    from friday_mcp.server import ModernStdioMCPServer, ServerLimits, ToolCallResult
    from tests_mcp.server.test_modern_protocol import definition

    server = ModernStdioMCPServer(
        limits=ServerLimits(active_requests=budget, timeout_seconds=0.03)
    )
    calls = []

    async def handler(args):
        calls.append(1)
        return ToolCallResult.text("done")

    server.register_tool(definition(), handler)
    reader, writer = asyncio.StreamReader(), MemoryWriter()
    serving = asyncio.create_task(server.serve(reader=reader, writer=writer))
    raw = rpc("tools/call", params={"name": "echo"})
    reader.feed_data(b"x" * 65537 if oversized else raw[:20])
    await asyncio.sleep(0.06)
    # Expiry closes the input before a peer can finish the late frame.
    assert reader.at_eof()
    await asyncio.wait_for(serving, 0.2)
    assert not calls and not writer.data and writer.closed
    assert server._generation is None and server.active_requests == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
async def test_fragment_assembly_consumes_handler_and_output_deadline(budget):
    from friday_mcp.server import ModernStdioMCPServer, ServerLimits, ToolCallResult
    from tests_mcp.server.test_modern_protocol import definition

    server = ModernStdioMCPServer(
        limits=ServerLimits(active_requests=budget, timeout_seconds=0.08)
    )
    started, cancelled = asyncio.Event(), asyncio.Event()

    async def handler(args):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()
        return ToolCallResult.text("late")

    server.register_tool(definition(), handler)
    reader, writer = asyncio.StreamReader(), MemoryWriter()
    serving = asyncio.create_task(server.serve(reader=reader, writer=writer))
    raw = rpc("tools/call", params={"name": "echo"})
    reader.feed_data(raw[:10])
    await asyncio.sleep(0.02)
    reader.feed_data(raw[10:20])
    await asyncio.sleep(0.02)
    reader.feed_data(raw[20:] + b"\n")
    await asyncio.wait_for(started.wait(), 0.03)
    # A refreshed 80ms handler budget cannot satisfy this remaining 60ms bound.
    await asyncio.wait_for(cancelled.wait(), 0.06)
    assert not writer.data
    await server.stop()
    await serving

    # Delivery lock waits also use the first-byte deadline, not a new phase.
    reader, writer = asyncio.StreamReader(), MemoryWriter()
    serving = asyncio.create_task(server.serve(reader=reader, writer=writer))
    await turns_until(lambda: server._generation is not None)
    connection = server._generation
    await connection.lock.acquire()
    raw = rpc()
    reader.feed_data(raw[:10])
    await asyncio.sleep(0.05)
    reader.feed_data(raw[10:] + b"\n")
    await turns_until(lambda: bool(connection.dispatchers))
    await asyncio.wait_for(serving, 0.06)
    connection.lock.release()
    assert not writer.data and writer.closed and server._generation is None


@pytest.mark.asyncio
async def test_idle_before_frame_does_not_consume_frame_budget():
    from friday_mcp.server import ModernStdioMCPServer, ServerLimits

    server = ModernStdioMCPServer(limits=ServerLimits(timeout_seconds=0.03))
    reader, writer = asyncio.StreamReader(), MemoryWriter()
    serving = asyncio.create_task(server.serve(reader=reader, writer=writer))
    await asyncio.sleep(0.06)
    assert not serving.done()
    reader.feed_data(rpc(rid="after-idle") + b"\n")
    await turns_until(lambda: bool(writer.data))
    assert json.loads(writer.data)["id"] == "after-idle"
    await server.stop()
    await serving


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
async def test_partial_eof_uses_frame_deadline_and_closes(budget):
    from friday_mcp.server import ModernStdioMCPServer, ServerLimits

    server = ModernStdioMCPServer(
        limits=ServerLimits(active_requests=budget, timeout_seconds=0.1)
    )
    reader, writer = asyncio.StreamReader(), MemoryWriter()
    serving = asyncio.create_task(server.serve(reader=reader, writer=writer))
    reader.feed_data(b"partial")
    await turns_until(lambda: not reader._buffer)
    reader.feed_eof()
    await asyncio.wait_for(serving, 0.2)
    assert json.loads(writer.data) == {
        "jsonrpc": "2.0",
        "error": {"code": -32700, "message": "Parse error"},
    }
    assert writer.closed and server._generation is None and server.active_requests == 0
