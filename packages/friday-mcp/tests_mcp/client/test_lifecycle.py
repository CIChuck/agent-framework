# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Protocol-owner cleanup regressions; no real server or network required."""

import asyncio
import contextlib
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from friday_mcp.client import stdio
from friday_mcp.client.base import MCPClientBase
from friday_mcp.client.manager import MCPClientManager
from friday_mcp.client.stdio import StdioMCPClient, StdioTransport
from friday_mcp.config import MCPConfig, MCPServerConfig


class FakeTransport:
    def __init__(self):
        self.is_connected = False
        self.disconnect_calls = 0
        self.eof = False

    async def connect(self):
        self.is_connected = True

    async def disconnect(self):
        self.disconnect_calls += 1
        self.is_connected = False

    async def send(self, message):
        pass

    async def receive(self):
        if self.eof:
            raise EOFError("SENTINEL-SECRET")
        await asyncio.Future()


class FakeClient(MCPClientBase):
    def __init__(self, mode="good"):
        super().__init__("fake")
        self.transport = FakeTransport()
        self.mode = mode
        self.handshake_entered = asyncio.Event()

    async def _create_transport(self):
        return self.transport

    async def _initialize(self):
        self.handshake_entered.set()
        if self.mode == "failure":
            raise ValueError("SENTINEL-SECRET")
        if self.mode == "timeout":
            await asyncio.Future()


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["good", "failure", "timeout"])
async def test_disconnect_releases_partial_and_successful_connections(mode):
    client = FakeClient(mode)
    if mode == "failure":
        with pytest.raises(ValueError):
            await client.connect()
    elif mode == "timeout":
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(client.connect(), timeout=0.02)
    else:
        await client.connect()
    await client.disconnect()
    await client.disconnect()
    assert not client.transport.is_connected
    assert client.transport.disconnect_calls == 1
    assert client._receive_task is None
    assert client._transport is None
    assert not client.is_connected


@pytest.mark.asyncio
async def test_cancel_handshake_releases_owned_resources():
    client = FakeClient("timeout")
    task = asyncio.create_task(client.connect())
    await client.handshake_entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert client._receive_task is None
    assert not client.transport.is_connected


@pytest.mark.asyncio
async def test_eof_terminates_receiver_and_fails_pending_request_without_raw_log(
    caplog,
):
    client = FakeClient()
    await client.connect()
    client.transport.eof = True
    client._receive_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await client._receive_task
    future = asyncio.get_running_loop().create_future()
    client._pending_requests["pending"] = future
    with caplog.at_level(logging.DEBUG):
        await client._receive_loop()
    with pytest.raises(ConnectionError, match="MCP transport closed"):
        await future
    await client.disconnect()
    assert "SENTINEL-SECRET" not in caplog.text
    assert not client._pending_requests


@pytest.mark.asyncio
async def test_disconnect_cancels_pending_requests():
    client = FakeClient()
    await client.connect()
    future = asyncio.get_running_loop().create_future()
    client._pending_requests["pending"] = future
    await client.disconnect()
    assert future.cancelled()
    assert not client._pending_requests


@pytest.mark.asyncio
async def test_manager_legacy_boolean_and_raising_api_cleanup(monkeypatch, caplog):
    manager = MCPClientManager(
        MCPConfig(servers=[MCPServerConfig(name="fake", command="fake")])
    )
    clients = []

    def create(config):
        client = FakeClient("failure")
        clients.append(client)
        return client

    monkeypatch.setattr(manager, "_create_client", create)
    with caplog.at_level(logging.DEBUG):
        assert not await manager.connect("fake")
        with pytest.raises(ValueError):
            await manager.connect_or_raise("fake")
    assert not manager.connected_servers
    assert all(client.transport.disconnect_calls == 1 for client in clients)
    assert "SENTINEL-SECRET" not in caplog.text
    with pytest.raises(KeyError):
        await manager.connect("missing")


@pytest.mark.asyncio
async def test_manager_repeated_connect_does_not_replace_live_client(monkeypatch):
    manager = MCPClientManager(
        MCPConfig(servers=[MCPServerConfig(name="fake", command="fake")])
    )
    client = FakeClient()
    create = MagicMock(return_value=client)
    monkeypatch.setattr(manager, "_create_client", create)
    assert await manager.connect("fake")
    assert await manager.connect("fake")
    assert create.call_count == 1
    await manager.disconnect_all()
    await manager.disconnect_all()
    assert client.transport.disconnect_calls == 1


@pytest.mark.asyncio
async def test_manager_retains_failed_cleanup_for_retry(monkeypatch):
    manager = MCPClientManager(
        MCPConfig(servers=[MCPServerConfig(name="fake", command="fake")])
    )
    client = FakeClient()
    monkeypatch.setattr(manager, "_create_client", lambda config: client)
    await manager.connect_or_raise("fake")
    original = client.disconnect
    monkeypatch.setattr(
        client, "disconnect", AsyncMock(side_effect=RuntimeError("SENTINEL-SECRET"))
    )
    with pytest.raises(RuntimeError, match="cleanup incomplete"):
        await manager.disconnect_all()
    assert manager.get_client("fake") is client
    monkeypatch.setattr(client, "disconnect", original)
    await manager.disconnect_all()


@pytest.mark.asyncio
async def test_stdio_cleanup_already_exited_process_and_stderr(monkeypatch, caplog):
    process = MagicMock()
    process.returncode = 0
    process.wait = AsyncMock(return_value=0)
    process.stdout.read = AsyncMock(return_value=b"")
    process.stderr.read = AsyncMock(side_effect=[b"SENTINEL-SECRET", b""])
    monkeypatch.setattr(
        asyncio, "create_subprocess_exec", AsyncMock(return_value=process)
    )
    transport = StdioTransport(
        "SENTINEL-COMMAND", ["SENTINEL-ARG"], {"KEY": "SENTINEL-ENV"}, Path(".")
    )
    with caplog.at_level(logging.DEBUG):
        await transport.connect()
        await asyncio.sleep(0)
        await transport.disconnect()
        await transport.disconnect()
    assert not process.terminate.called
    assert transport._process is None
    assert transport._stderr_task is None
    assert "SENTINEL" not in caplog.text


@pytest.mark.asyncio
async def test_stdio_config_timeout_reaches_rpc_wait_without_hidden_30_second_cap(
    monkeypatch,
):
    client = StdioMCPClient.from_config(
        MCPServerConfig(name="fake", command="fake", timeout_seconds=77)
    )
    transport = FakeTransport()
    client._transport = transport
    observed = []
    original = asyncio.wait_for

    async def send(message):
        client._pending_requests[message["id"]].set_result({"result": {"tools": []}})

    async def wait(future, timeout):
        observed.append(timeout)
        return await original(future, timeout)

    monkeypatch.setattr(transport, "send", send)
    monkeypatch.setattr(asyncio, "wait_for", wait)
    await client._request("tools/list", {})
    assert observed == [77.0]
    await client.disconnect()


@pytest.mark.asyncio
async def test_stdio_cancel_during_spawn_reaps_child(monkeypatch):
    entered = asyncio.Event()
    release = asyncio.Event()
    process = MagicMock()
    process.returncode = None
    process.wait = AsyncMock(return_value=0)
    process.stdout.read = AsyncMock(return_value=b"")
    process.stderr.read = AsyncMock(return_value=b"")

    async def spawn(*args, **kwargs):
        entered.set()
        await release.wait()
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    transport = StdioTransport("fake")
    task = asyncio.create_task(transport.connect())
    await entered.wait()
    task.cancel()
    release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    process.terminate.assert_called_once()
    assert transport._process is None


def short_cleanup_budgets(monkeypatch):
    for name in (
        "_READER_STOP_SECONDS",
        "_GRACEFUL_EXIT_SECONDS",
        "_FORCED_EXIT_SECONDS",
        "_PIPE_EOF_SECONDS",
        "_FAILED_TASK_STOP_SECONDS",
    ):
        monkeypatch.setattr(stdio, name, 0.02)


def process_double():
    process = MagicMock()
    process.returncode = None
    process.wait = AsyncMock(return_value=0)
    process.stdout.read = AsyncMock(return_value=b"")
    process.stderr.read = AsyncMock(return_value=b"")
    return process


@pytest.fixture
async def stdio_owner():
    owned = []

    def create(process, command="fake", args=None, env=None):
        transport = StdioTransport(command, args, env)
        owned.append((transport, process))
        return transport

    try:
        yield create
    finally:
        # Runs after the test assertions, even if they fail. Reset only the
        # synthetic obstruction, then settle the owner through its public API.
        # A fixture error is reported separately, not in place of an assertion.
        for transport, process in owned:
            process.stdout.read = AsyncMock(return_value=b"")
            process.stderr.read = AsyncMock(return_value=b"")
            process.wait = AsyncMock(return_value=0)
            await asyncio.wait_for(transport.disconnect(), 13)


@pytest.mark.asyncio
async def test_stdio_discard_is_incremental_and_redacted(
    monkeypatch, caplog, stdio_owner
):
    process = process_double()
    payload = b"SENTINEL-SECRET" * 290
    process.stdout.read = AsyncMock(side_effect=[payload] * 1024 + [b""])
    process.stderr.read = AsyncMock(side_effect=[payload] * 1024 + [b""])
    monkeypatch.setattr(
        asyncio, "create_subprocess_exec", AsyncMock(return_value=process)
    )
    transport = stdio_owner(
        process, "SENTINEL-COMMAND", ["SENTINEL-ARG"], {"K": "SENTINEL-ENV"}
    )
    with caplog.at_level(logging.DEBUG):
        await transport.connect()
        await transport.disconnect()
    assert all(call.args == (4096,) for call in process.stdout.read.await_args_list)
    assert all(call.args == (4096,) for call in process.stderr.read.await_args_list)
    assert "SENTINEL" not in caplog.text
    assert transport._process is None


@pytest.mark.asyncio
async def test_stdio_unreaped_process_retained_for_public_retry(
    monkeypatch, caplog, stdio_owner
):
    short_cleanup_budgets(monkeypatch)
    process = process_double()
    exited = asyncio.Event()

    async def wait():
        await exited.wait()
        return 0

    process.wait = AsyncMock(side_effect=wait)
    monkeypatch.setattr(
        asyncio, "create_subprocess_exec", AsyncMock(return_value=process)
    )
    transport = stdio_owner(process)
    await transport.connect()
    try:
        with caplog.at_level(logging.DEBUG), pytest.raises(RuntimeError) as error:
            await asyncio.wait_for(transport.disconnect(), 0.5)
        assert str(error.value) == "MCP stdio cleanup incomplete"
        assert transport._process is process
        assert transport._process_wait_task is not None
        assert transport._cleanup_task is not None
        assert not transport.is_connected
        process.kill.assert_called_once()
        assert "SENTINEL" not in caplog.text
    finally:
        exited.set()
        await transport.disconnect()
    assert transport._process is None


@pytest.mark.asyncio
async def test_stdio_cancellation_resistant_drain_retains_owner_and_retries(
    monkeypatch,
    stdio_owner,
):
    short_cleanup_budgets(monkeypatch)
    process = process_double()
    entered, release = asyncio.Event(), asyncio.Event()

    async def read(size):
        entered.set()
        while not release.is_set():
            try:
                await release.wait()
            except asyncio.CancelledError:
                continue
        return b""

    process.stdout.read = AsyncMock(side_effect=read)
    monkeypatch.setattr(
        asyncio, "create_subprocess_exec", AsyncMock(return_value=process)
    )
    transport = stdio_owner(process)
    await transport.connect()
    try:
        with pytest.raises(RuntimeError, match="^MCP stdio cleanup incomplete$"):
            await asyncio.wait_for(transport.disconnect(), 0.5)
        await entered.wait()
        retained = transport._stdout_drain_task
        assert retained is not None and not retained.done()
        assert transport._process is process
    finally:
        release.set()
        await transport.disconnect()
    assert retained.done()
    assert transport._stdout_drain_task is None
    assert transport._process is None


@pytest.mark.asyncio
async def test_stdio_cleanup_caller_cancel_keeps_joinable_owner(
    monkeypatch, stdio_owner
):
    process = process_double()
    entered, release = asyncio.Event(), asyncio.Event()

    async def wait():
        entered.set()
        await release.wait()
        return 0

    process.wait = AsyncMock(side_effect=wait)
    monkeypatch.setattr(
        asyncio, "create_subprocess_exec", AsyncMock(return_value=process)
    )
    transport = stdio_owner(process)
    await transport.connect()
    caller = asyncio.create_task(transport.disconnect())
    try:
        await entered.wait()
        caller.cancel()
        with pytest.raises(asyncio.CancelledError):
            await caller
        assert transport._process is process
        assert transport._cleanup_task is not None
        release.set()
        await transport.disconnect()
        await transport.disconnect()
        assert transport._cleanup_task is None
        assert transport._process is None
    finally:
        release.set()
        caller.cancel()
        await asyncio.gather(caller, return_exceptions=True)


@pytest.mark.asyncio
async def test_stdio_stops_active_protocol_reader_before_discard(
    monkeypatch, stdio_owner
):
    process = process_double()
    entered = asyncio.Event()
    reading = False

    async def readline():
        nonlocal reading
        reading = True
        entered.set()
        try:
            await asyncio.Future()
        finally:
            reading = False

    async def read(size):
        assert not reading
        return b""

    process.stdout.readline = AsyncMock(side_effect=readline)
    process.stdout.read = AsyncMock(side_effect=read)
    monkeypatch.setattr(
        asyncio, "create_subprocess_exec", AsyncMock(return_value=process)
    )
    transport = stdio_owner(process)
    await transport.connect()
    receiver = asyncio.create_task(transport.receive())
    try:
        await entered.wait()
        await transport.disconnect()
        with pytest.raises(asyncio.CancelledError):
            await receiver
        assert transport._stdout_read_task is None
        assert transport._stdout_drain_task is None
    finally:
        receiver.cancel()
        await asyncio.gather(receiver, return_exceptions=True)


@pytest.mark.asyncio
async def test_stdio_cleanup_stream_error_is_static_and_retryable(
    monkeypatch, caplog, stdio_owner
):
    process = process_double()
    process.stdout.read = AsyncMock(side_effect=ValueError("SENTINEL-STREAM-SECRET"))
    monkeypatch.setattr(
        asyncio, "create_subprocess_exec", AsyncMock(return_value=process)
    )
    transport = stdio_owner(process)
    await transport.connect()
    with caplog.at_level(logging.DEBUG), pytest.raises(RuntimeError) as error:
        await transport.disconnect()
    assert str(error.value) == "MCP stdio cleanup incomplete"
    assert error.value.__suppress_context__
    assert transport._process is process
    assert "SENTINEL" not in caplog.text
    process.stdout.read = AsyncMock(return_value=b"")
    await transport.disconnect()
    assert transport._process is None
