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
