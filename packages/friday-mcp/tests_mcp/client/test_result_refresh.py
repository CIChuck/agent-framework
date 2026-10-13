"""Public manual refresh, generation races and complete result regression proof."""

import asyncio
import copy
import traceback
from dataclasses import FrozenInstanceError

import pytest

from friday_mcp.client import MCPCatalogSnapshot, MCPRefreshClient
from friday_mcp.client.adapter import MCPToolAdapter
from friday_mcp.client.base import MCPError, MCPToolExecutionError
from friday_mcp.client.protocol import ProtocolFailure, ProtocolLimits, ToolResult
from tests_mcp.client.test_http_lifecycle import Peer, make_client
from tests_mcp.client.test_modern_protocol import Client, cached, complete, tool


def refresh_peer(profile, budget=4, timeout=30):
    limits = ProtocolLimits(concurrent_requests=budget, timeout_seconds=timeout)
    if profile == "stdio":
        client = Client(limits=limits)
        return client, client.transport
    peer = Peer(version=profile)
    client, _, _ = make_client(peer, limits=limits)
    return client, peer


def peer_messages(peer):
    return peer.sent if hasattr(peer, "sent") else [r[2] for r in peer.requests]


@pytest.mark.asyncio
@pytest.mark.parametrize("profile", ["stdio", "2026-07-28", "2025-11-25"])
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
async def test_capacity_rejection_retires_before_owned_discovery_schedules(
    profile, budget
):
    client, peer = refresh_peer(profile, budget)
    await client.connect()
    pending = []
    try:
        adapter = MCPToolAdapter(client)
        old = (await adapter.get_tools())[0]
        before = len(peer_messages(peer))
        pending = [
            asyncio.create_task(client.refresh_tool_catalog()) for _ in range(budget)
        ]
        # Each public entry point runs, but its separately owned discovery has
        # not run yet. Rejection must be safe in this exact scheduling window.
        await asyncio.sleep(0)
        assert client.outstanding_catalog_owners == budget
        assert len(peer_messages(peer)) == before
        with pytest.raises(ProtocolFailure) as rejected:
            await client.refresh_tool_catalog()
        assert rejected.value.failure_code == "limit_exceeded"
        assert client.current_catalog_snapshot is None
        with pytest.raises(MCPToolExecutionError) as stale:
            await old.execute()
        assert stale.value.failure_code == "catalog_unavailable"
        with pytest.raises(MCPToolExecutionError) as direct:
            await client.call_tool("echo", {})
        assert direct.value.failure_code == "catalog_unavailable"
        with pytest.raises(ProtocolFailure) as cached_read:
            await adapter.get_tools()
        assert cached_read.value.failure_code == "limit_exceeded"
        assert adapter._tools_cache is None
        assert len(peer_messages(peer)) == before
        snapshots = await asyncio.gather(*pending)
        assert all(isinstance(s, MCPCatalogSnapshot) for s in snapshots)
        assert len({s.generation for s in snapshots}) == budget
        assert snapshots[-1] is client.current_catalog_snapshot
        new = (await adapter.get_tools())[0]
        assert await new.execute() == "ok"
        await client.disconnect()
        await client.connect()
        with pytest.raises(MCPToolExecutionError) as reconnected:
            await new.execute()
        assert reconnected.value.failure_code == "catalog_unavailable"
        assert await (await adapter.get_tools())[0].execute() == "ok"
    finally:
        await client.disconnect()
        await asyncio.gather(*pending, return_exceptions=True)
    assert client.outstanding_catalog_owners == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("profile", ["stdio", "2026-07-28", "2025-11-25"])
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
async def test_cancelled_before_discovery_cannot_reuse_old_adapter_cache(
    profile, budget
):
    client, peer = refresh_peer(profile, budget)
    await client.connect()
    try:
        adapter = MCPToolAdapter(client)
        old = (await adapter.get_tools())[0]
        before = len(peer_messages(peer))
        pending = asyncio.create_task(client.refresh_tool_catalog())
        await asyncio.sleep(0)
        pending.cancel()
        with pytest.raises(asyncio.CancelledError):
            await pending
        assert client.current_catalog_snapshot is None
        with pytest.raises(MCPToolExecutionError) as stale:
            await old.execute()
        assert stale.value.failure_code == "catalog_unavailable"
        assert len(peer_messages(peer)) == before
        new = (await adapter.get_tools())[0]
        assert new is not old
        assert await new.execute() == "ok"
    finally:
        await client.disconnect()
    assert client.outstanding_catalog_owners == 0


@pytest.mark.asyncio
async def test_2025_failed_capacity_refresh_retires_recovered_raw_call_catalog():
    client, peer = refresh_peer("2025-11-25", 1)
    await client.connect()
    try:
        old = (await MCPToolAdapter(client).get_tools())[0]
        peer.expire_once = True
        with pytest.raises(MCPToolExecutionError):
            await old.execute()
        assert await client.call_tool("echo", {}) == "ok"
        before = len(peer.requests)
        # Occupy the catalog owner budget without issuing a discovery. This
        # recreates the original admission-only rejection after HTTP recovery.
        await client._catalog_lock.acquire()
        pending = asyncio.create_task(client.refresh_tool_catalog())
        await asyncio.sleep(0)
        with pytest.raises(ProtocolFailure) as rejected:
            await client.refresh_tool_catalog()
        assert rejected.value.failure_code == "limit_exceeded"
        with pytest.raises(MCPToolExecutionError) as raw:
            await client.call_tool("echo", {})
        assert raw.value.failure_code == "catalog_unavailable"
        assert len(peer.requests) == before
        client._catalog_lock.release()
        await pending
        assert await client.call_tool("echo", {}) == "ok"
    finally:
        if client._catalog_lock.locked():
            client._catalog_lock.release()
        await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize("profile", ["stdio", "2026-07-28", "2025-11-25"])
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
@pytest.mark.parametrize("failure", ["partial", "cancel", "deadline"])
async def test_partial_refresh_failures_retire_all_admission_and_recover(
    profile, budget, failure
):
    client, peer = refresh_peer(profile, budget, 0.1 if failure == "deadline" else 30)
    await client.connect()
    started = asyncio.Event()
    gate = asyncio.Event()
    count = 0
    try:
        adapter = MCPToolAdapter(client)
        old = (await adapter.get_tools())[0]

        def response(message):
            nonlocal count
            if message.get("method") != "tools/list":
                return None
            count += 1
            if count == 1:
                return {"result": cached(tools=[tool()], nextCursor="next")}
            started.set()
            if failure == "partial":
                return {"error": {"code": -32603, "message": "SENTINEL"}}
            return None

        if profile == "stdio":
            peer.handler = response
        else:

            def hook(verb, headers, message):
                answer = response(message)
                if answer is None:
                    return peer.rpc(message, {"tools": []}, stall=gate)
                return peer.rpc(message, **answer)

            peer.hook = hook
        pending = asyncio.create_task(client.refresh_tool_catalog())
        await started.wait()
        before = len(peer_messages(peer))
        assert client.current_catalog_snapshot is None
        with pytest.raises(MCPToolExecutionError) as stale:
            await old.execute()
        assert stale.value.failure_code == "catalog_unavailable"
        assert len(peer_messages(peer)) == before
        if failure == "cancel":
            pending.cancel()
            with pytest.raises(asyncio.CancelledError):
                await pending
        elif failure == "deadline":
            with pytest.raises(TimeoutError):
                await pending
        else:
            with pytest.raises(MCPError):
                await pending
        assert client.current_catalog_snapshot is None
        assert client.outstanding_catalog_owners == 0
        with pytest.raises(MCPToolExecutionError) as raw:
            await client.call_tool("echo", {})
        assert raw.value.failure_code == "catalog_unavailable"
        # A cache read must rediscover explicitly, never return the old wrapper.
        if profile == "stdio":
            peer.handler = peer.default
        else:
            peer.hook = None
            # HTTP cancellation retains a bounded cleanup owner until settlement;
            # public stop/start drains it before reconnecting at lower budgets.
            assert client.outstanding_http_owners <= budget
            gate.set()
            await client.disconnect()
            assert client.outstanding_http_owners == 0
            await client.connect()
        new = (await adapter.get_tools())[0]
        assert new is not old
        assert await new.execute() == "ok"
        assert sum(m.get("method") == "tools/call" for m in peer_messages(peer)) == 1
    finally:
        gate.set()
        await client.disconnect()
    assert client.outstanding_catalog_owners == 0
    if profile != "stdio":
        assert client.outstanding_http_owners == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("profile", ["stdio", "2026-07-28", "2025-11-25"])
@pytest.mark.parametrize("budget", [1, 2, 3, 4])
async def test_failed_admission_does_not_cancel_already_issued_schema_binding(
    profile, budget
):
    client, peer = refresh_peer(profile, budget)
    result = {"content": [], "structuredContent": {"v": 7}}
    schema = {
        "type": "object",
        "properties": {"v": {"type": "integer"}},
        "required": ["v"],
    }
    gate = asyncio.Event()
    started = asyncio.Event()
    pending = []
    await client.connect()
    try:
        if profile == "stdio":
            original = peer.handler
            peer.handler = (
                lambda message: {"result": cached(tools=[tool(outputSchema=schema)])}
                if message["method"] == "tools/list"
                else original(message)
            )
        else:
            peer.tools[0]["outputSchema"] = schema
        old = (await MCPToolAdapter(client).get_tools())[0]
        if profile == "stdio":
            send = peer.send

            async def held_send(message):
                if message.get("method") == "tools/call":
                    peer.sent.append(copy.deepcopy(message))
                    started.set()
                    await gate.wait()
                    await peer.incoming.put(
                        {
                            "jsonrpc": "2.0",
                            "id": message["id"],
                            "result": complete(**result),
                        }
                    )
                else:
                    await send(message)

            peer.send = held_send
        else:

            def hook(verb, headers, message):
                if message.get("method") == "tools/call":
                    started.set()
                    return peer.rpc(message, result, stall=gate)
                return None

            peer.hook = hook
        running = asyncio.create_task(old.execute())
        await started.wait()
        await client._catalog_lock.acquire()
        pending = [
            asyncio.create_task(client.refresh_tool_catalog()) for _ in range(budget)
        ]
        await asyncio.sleep(0)
        with pytest.raises(ProtocolFailure) as rejected:
            await client.refresh_tool_catalog()
        assert rejected.value.failure_code == "limit_exceeded"
        before = len(peer_messages(peer))
        with pytest.raises(MCPToolExecutionError) as stale:
            await old.execute()
        assert stale.value.failure_code == "catalog_unavailable"
        assert len(peer_messages(peer)) == before
        gate.set()
        assert await running == '{"v":7}'
        assert sum(m.get("method") == "tools/call" for m in peer_messages(peer)) == 1
        client._catalog_lock.release()
        await asyncio.gather(*pending)
        assert client.current_catalog_snapshot is not None
    finally:
        gate.set()
        if client._catalog_lock.locked():
            client._catalog_lock.release()
        await client.disconnect()
        await asyncio.gather(*pending, return_exceptions=True)


@pytest.mark.asyncio
async def test_failed_refresh_retires_cached_and_validated_wrappers_before_io():
    client = Client()
    await client.connect()
    try:
        adapter = MCPToolAdapter(client)
        old = (await adapter.get_tools())[0]
        assert isinstance(client, MCPRefreshClient)
        snapshot = client.current_catalog_snapshot
        assert isinstance(snapshot, MCPCatalogSnapshot)
        exported = snapshot.tools()
        exported[0]["name"] = "changed"
        assert snapshot.tools()[0]["name"] == "echo"
        with pytest.raises(FrozenInstanceError):
            snapshot.generation = 0
        client.transport.handler = lambda message: {
            "error": {"code": -32603, "message": "SENTINEL"}
        }
        with pytest.raises(MCPError):
            await adapter.get_tools(refresh=True)
        assert client.current_catalog_snapshot is None
        issued = len(client.transport.sent)
        with pytest.raises(MCPToolExecutionError) as exc:
            await old.execute()
        assert exc.value.failure_code == "catalog_unavailable"
        assert len(client.transport.sent) == issued
        with pytest.raises(MCPError):
            await adapter.get_tools()
        assert adapter._tools_cache is None
        client.transport.handler = client.transport.default
        new = (await adapter.get_tools(refresh=True))[0]
        assert await new.execute() == "ok"
        assert client.current_catalog_snapshot.generation > snapshot.generation
        with pytest.raises(MCPToolExecutionError):
            await old.execute()
    finally:
        await client.disconnect()
    assert client.outstanding_catalog_owners == 0


@pytest.mark.asyncio
async def test_call_keeps_old_output_schema_across_successful_refresh():
    client = Client()
    await client.connect()
    original = client.transport.default
    gate = asyncio.Event()
    issued = asyncio.Event()

    async def send(message):
        if message.get("method") == "tools/call":
            client.transport.sent.append(message)
            issued.set()
            await gate.wait()
            await client.transport.incoming.put(
                {
                    "jsonrpc": "2.0",
                    "id": message["id"],
                    "result": complete(content=[], structuredContent=7),
                }
            )
        else:
            await original_send(message)

    original_send = client.transport.send
    try:
        client.transport.handler = (
            lambda message: {
                "result": cached(tools=[tool(outputSchema={"type": "integer"})])
            }
            if message["method"] == "tools/list"
            else original(message)
        )
        adapter = MCPToolAdapter(client)
        old = (await adapter.get_tools())[0]
        client.transport.send = send
        running = asyncio.create_task(old.execute())
        await issued.wait()
        client.transport.handler = (
            lambda message: {
                "result": cached(tools=[tool(outputSchema={"type": "string"})])
            }
            if message["method"] == "tools/list"
            else original(message)
        )
        await adapter.get_tools(refresh=True)
        gate.set()
        assert await running == "7"
        with pytest.raises(MCPToolExecutionError):
            await old.execute()
        assert sum(m["method"] == "tools/call" for m in client.transport.sent) == 1
    finally:
        gate.set()
        await client.disconnect()


@pytest.mark.asyncio
async def test_serial_refresh_returns_own_generation_after_failure():
    client = Client()
    await client.connect()
    first = asyncio.Event()
    release = asyncio.Event()
    original = client._catalog_request
    count = 0

    async def request(params, deadline):
        nonlocal count
        count += 1
        if count == 1:
            first.set()
            await release.wait()
            raise ProtocolFailure()
        return await original(params, deadline)

    client._catalog_request = request
    try:
        one = asyncio.create_task(client.refresh_tool_catalog())
        await first.wait()
        two = asyncio.create_task(client.refresh_tool_catalog())
        await asyncio.sleep(0)
        release.set()
        with pytest.raises(ProtocolFailure):
            await one
        snapshot = await two
        assert snapshot is client.current_catalog_snapshot
        assert snapshot.tools()[0]["name"] == "echo"
        third = await client.refresh_tool_catalog()
        assert third.generation > snapshot.generation
        assert snapshot.generation != third.generation
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_refresh_wait_deadline_and_disconnect_settle_owned_tasks():
    client = Client(limits=ProtocolLimits(timeout_seconds=0.05))
    await client.connect()
    gate = asyncio.Event()
    started = asyncio.Event()

    async def request(params, deadline):
        started.set()
        await gate.wait()
        return cached(tools=[])

    client._catalog_request = request
    one = asyncio.create_task(client.refresh_tool_catalog())
    await started.wait()
    two = asyncio.create_task(client.refresh_tool_catalog())
    outcomes = await asyncio.gather(one, two, return_exceptions=True)
    assert all(isinstance(x, TimeoutError) for x in outcomes)
    assert client.current_catalog_snapshot is None
    assert client.outstanding_catalog_owners == 0
    three = asyncio.create_task(client.refresh_tool_catalog())
    await asyncio.sleep(0)
    await client.disconnect()
    with pytest.raises(asyncio.CancelledError):
        await three
    assert client.outstanding_catalog_owners == 0


@pytest.mark.asyncio
async def test_reconnect_removed_tool_and_failed_schema_cannot_issue_calls():
    client = Client()
    await client.connect()
    try:
        adapter = MCPToolAdapter(client)
        old = (await adapter.get_tools())[0]
        generation = client.current_catalog_snapshot.generation
        await client.disconnect()
        await client.connect()
        new = (await adapter.get_tools())[0]
        assert client.current_catalog_snapshot.generation > generation
        with pytest.raises(MCPToolExecutionError):
            await old.execute()
        assert await new.execute() == "ok"
        client.transport.handler = lambda message: {"result": cached(tools=[])}
        await adapter.get_tools(refresh=True)
        with pytest.raises(MCPToolExecutionError):
            await new.execute()
    finally:
        await client.disconnect()


@pytest.mark.parametrize("modern,compatibility", [(True, False), (False, True)])
@pytest.mark.parametrize(
    "block",
    [
        {"type": "image", "data": "eA==", "mimeType": "image/png"},
        {"type": "audio", "data": "eA==", "mimeType": "audio/wav"},
        {"type": "resource_link", "name": "synthetic", "uri": "https://invalid.test"},
        {"type": "resource", "resource": {"uri": "https://invalid.test", "text": "x"}},
        {
            "type": "resource",
            "resource": {"uri": "https://invalid.test", "blob": "eA=="},
        },
    ],
)
def test_valid_unsupported_content_is_not_fetched_or_silently_dropped(
    modern, compatibility, block
):
    value = complete(content=[{"type": "text", "text": "ok"}, block])
    with pytest.raises(ProtocolFailure) as exc:
        ToolResult.parse(value, modern, ProtocolLimits(), compatibility=compatibility)
    assert exc.value.failure_code == "unsupported_content"
    value["isError"] = True
    # A valid ordinary error needs no successful structured value.
    assert ToolResult.parse(
        value, modern, ProtocolLimits(), compatibility=compatibility
    ).texts == ("ok",)


@pytest.mark.parametrize("modern,compatibility", [(True, False), (False, True)])
@pytest.mark.parametrize(
    "block",
    [
        {"type": "image", "data": "SENTINEL"},
        {"type": "audio", "mimeType": "audio/wav"},
        {"type": "resource_link", "uri": "https://invalid.test"},
        {"type": "resource", "resource": {"text": "SENTINEL"}},
        {"type": "future", "text": "SENTINEL"},
        {"type": "text", "text": 3},
    ],
)
def test_malformed_error_content_is_invalid_before_error_disposition(
    modern, compatibility, block
):
    with pytest.raises(ProtocolFailure) as exc:
        ToolResult.parse(
            complete(content=[block], isError=True),
            modern,
            ProtocolLimits(),
            compatibility=compatibility,
        )
    assert exc.value.failure_code == "invalid_result"
    assert "SENTINEL" not in str(exc.value)


@pytest.mark.parametrize(
    "structured,expected",
    [(None, "null"), (7, "7"), ([1, 2], "[1,2]"), ({"v": 7}, '{"v":7}')],
)
def test_modern_structured_values_and_2025_object_only_are_explicit(
    structured, expected
):
    result = ToolResult.parse(
        complete(content=[], structuredContent=structured), True, ProtocolLimits()
    )
    assert result.text(ProtocolLimits()) == expected
    assert (
        ToolResult.parse(complete(content=[]), True, ProtocolLimits()).text(
            ProtocolLimits()
        )
        == ""
    )
    if not isinstance(structured, dict):
        with pytest.raises(ProtocolFailure):
            ToolResult.parse(
                {"content": [], "structuredContent": structured},
                False,
                ProtocolLimits(),
                compatibility=True,
            )


@pytest.mark.asyncio
@pytest.mark.parametrize("capability", [False, True])
async def test_2025_required_task_tools_excluded_without_enabling_tasks(capability):
    peer = Peer(version="2025-11-25")
    peer.tools = [tool(name="required", execution={"taskSupport": "required"})] + [
        tool(
            name=name,
            **({"execution": {"taskSupport": name}} if name != "absent" else {}),
        )
        for name in ["absent", "forbidden", "optional"]
    ]
    client, _, _ = make_client(peer)
    try:
        await client.connect()
        if capability:
            client._server_capabilities = {
                "tools": {},
                "tasks": {"requests": {"tools": {"call": {}}}},
            }
        snapshot = await client.refresh_tool_catalog()
        assert {t["name"] for t in snapshot.tools()} == {
            "absent",
            "forbidden",
            "optional",
        }
        assert snapshot.rejected_task_tools == 1
        before = len(peer.requests)
        with pytest.raises(MCPToolExecutionError) as exc:
            await client.call_tool("required", {})
        assert exc.value.failure_code == "unsupported_task"
        assert len(peer.requests) == before
        assert "task" not in str(peer.requests)
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_modern_http_headers_and_schema_are_captured_before_scheduling_exchange():
    peer = Peer()
    peer.tools[0]["outputSchema"] = {"type": "integer"}
    client, _, _ = make_client(peer)
    await client.connect()
    try:
        adapter = MCPToolAdapter(client)
        old = (await adapter.get_tools())[0]
        start = client._start
        captured = asyncio.Event()
        release = asyncio.Event()

        async def wait_before_issue(name, arguments, snapshot):
            captured.set()
            await release.wait()
            return await original(name, arguments, snapshot)

        original = client._request_tool
        client._request_tool = wait_before_issue
        running = asyncio.create_task(old.execute(text="雪"))
        await captured.wait()
        peer.tools[0]["inputSchema"]["properties"]["text"]["x-mcp-header"] = "Changed"
        peer.tools[0]["outputSchema"] = {"type": "string"}
        await client.refresh_tool_catalog()
        peer.hook = (
            lambda verb, headers, message: peer.rpc(
                message, complete(content=[], structuredContent=7)
            )
            if message.get("method") == "tools/call"
            else None
        )
        release.set()
        assert await running == "7"
        _, headers, message = next(
            r for r in peer.requests if r[2].get("method") == "tools/call"
        )
        assert b"mcp-param-text" in headers
        assert b"mcp-param-changed" not in headers
        assert message["params"]["arguments"] == {"text": "雪"}
        assert client._start == start
        with pytest.raises(MCPToolExecutionError):
            await old.execute(text="again")
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_error_shape_validation_precedes_success_schema_and_error_disposition():
    client = Client()
    await client.connect()
    try:
        client.transport.handler = lambda message: {
            "result": cached(tools=[tool(outputSchema={"type": "integer"})])
        }
        wrapper = (await MCPToolAdapter(client).get_tools())[0]
        for content, expected in [([], "tool_error"), ("SENTINEL", "invalid_result")]:
            client.transport.handler = lambda message, content=content: {
                "result": complete(isError=True, content=content)
            }
            with pytest.raises(MCPToolExecutionError) as exc:
                await wrapper.execute()
            assert exc.value.failure_code == expected
            assert "SENTINEL" not in str(exc.value)
    finally:
        await client.disconnect()


@pytest.mark.parametrize(
    "value",
    [
        {"resultType": "input_required", "requestState": None, "inputRequests": {}},
        {
            "resultType": "input_required",
            "requestState": "opaque",
            "inputRequests": None,
        },
        {"resultType": "input_required", "inputRequests": {"x": {"method": "unknown"}}},
        {
            "resultType": "input_required",
            "inputRequests": {"x": {"method": "sampling/createMessage", "params": {}}},
        },
        {
            "resultType": "input_required",
            "inputRequests": {
                "x": {"method": "elicitation/create", "params": {"message": "x"}}
            },
        },
        {"resultType": "complete", "task": {"taskId": "unsolicited"}},
    ],
)
def test_malformed_input_requests_and_unsolicited_task_results_are_never_promoted(
    value,
):
    with pytest.raises(ProtocolFailure):
        ToolResult.parse(value, True, ProtocolLimits())


@pytest.mark.parametrize(
    "params",
    [
        {"method": "roots/list"},
        {
            "method": "sampling/createMessage",
            "params": {"messages": [], "maxTokens": 5},
        },
        {
            "method": "elicitation/create",
            "params": {"mode": "url", "message": "x", "url": "https://invalid.test"},
        },
    ],
)
def test_valid_input_requests_remain_unsupported_without_continuation(params):
    with pytest.raises(ProtocolFailure) as exc:
        ToolResult.parse(
            {"resultType": "input_required", "inputRequests": {"x": params}},
            True,
            ProtocolLimits(),
        )
    assert exc.value.failure_code == "input_required_unsupported"


@pytest.mark.asyncio
async def test_2025_raw_call_recovery_keeps_schema_and_retires_wrappers():
    peer = Peer(version="2025-11-25")
    peer.tools[0]["outputSchema"] = {
        "type": "object",
        "properties": {"v": {"type": "integer"}},
        "required": ["v"],
    }
    client, _, _ = make_client(peer)
    await client.connect()
    try:
        old = (await MCPToolAdapter(client).get_tools())[0]
        peer.expire_once = True
        with pytest.raises(MCPToolExecutionError):
            await old.execute(text="first")
        assert client.current_catalog_snapshot is None
        before = peer.methods().count("tools/call")
        with pytest.raises(MCPToolExecutionError) as stale:
            await old.execute(text="stale")
        assert stale.value.failure_code == "catalog_unavailable"
        assert peer.methods().count("tools/call") == before
        peer.hook = (
            lambda verb, headers, message: peer.rpc(
                message, {"content": [], "structuredContent": {"v": "wrong"}}
            )
            if message.get("method") == "tools/call"
            else None
        )
        with pytest.raises(MCPToolExecutionError) as invalid:
            await client.call_tool("echo", {})
        assert invalid.value.failure_code == "invalid_result"
        assert peer.methods().count("tools/call") == before + 1
        peer.hook = (
            lambda verb, headers, message: peer.rpc(
                message, {"content": [], "structuredContent": {"v": 7}}
            )
            if message.get("method") == "tools/call"
            else None
        )
        assert await client.call_tool("echo", {}) == '{"v":7}'
        peer.hook = (
            lambda verb, headers, message: peer.rpc(
                message, error={"code": -32603, "message": "synthetic"}
            )
            if message.get("method") == "tools/list"
            else None
        )
        with pytest.raises(MCPError):
            await client.refresh_tool_catalog()
        before = len(peer.requests)
        with pytest.raises(MCPToolExecutionError) as blocked:
            await client.call_tool("echo", {})
        assert blocked.value.failure_code == "catalog_unavailable"
        assert len(peer.requests) == before
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_existing_base_subclass_raw_virtual_methods_are_not_bypassed():
    class LegacySubclass(Client):
        async def list_tools(self):
            return [tool(name="Custom.Exact")]

        async def call_tool(self, name, arguments):
            assert name == "Custom.Exact"
            return "custom"

    client = LegacySubclass()
    await client.connect()
    try:
        adapter = MCPToolAdapter(client)
        wrapper = (await adapter.get_tools())[0]
        assert await wrapper.execute() == "custom"
        assert not client.supports_catalog_refresh
        assert wrapper is (await adapter.get_tools())[0]
    finally:
        await client.disconnect()


def sampling_request(content, **fields):
    return {
        "method": "sampling/createMessage",
        "params": {
            "messages": [{"role": "assistant", "content": content}],
            "maxTokens": 5,
            **fields,
        },
    }


def form_request(property_schema, **fields):
    return {
        "method": "elicitation/create",
        "params": {
            "message": "SENTINEL prompt",
            "requestedSchema": {
                "type": "object",
                "properties": {"field": property_schema},
                **fields,
            },
        },
    }


def input_variant_cases():
    """Pinned schema-derived wire cases: IDs expose variant, field and mutation."""
    cases = []

    def add(name, request, valid):
        cases.append(
            pytest.param(
                request,
                "input_required_unsupported" if valid else "invalid_result",
                id=name,
            )
        )

    def fields(name, value, required, optional, wrap):
        add(name + "-minimal", wrap(copy.deepcopy(value)), True)
        for key in required:
            for mutation in ("omitted", "null", "wrong"):
                changed = copy.deepcopy(value)
                if mutation == "omitted":
                    del changed[key]
                else:
                    changed[key] = (
                        None
                        if mutation == "null"
                        else "wrong"
                        if isinstance(value[key], (int, float))
                        else 42
                    )
                add(f"{name}-{key}-{mutation}", wrap(changed), False)
        for key, good, bad in optional:
            changed = copy.deepcopy(value)
            changed[key] = good
            add(f"{name}-{key}-valid", wrap(changed), True)
            for mutation, bad_value in [("null", None), ("wrong", bad)]:
                changed = copy.deepcopy(value)
                changed[key] = bad_value
                add(f"{name}-{key}-{mutation}", wrap(changed), False)

    use = {"type": "tool_use", "id": "use", "name": "echo", "input": {}}
    result = {
        "type": "tool_result",
        "toolUseId": "use",
        "content": [{"type": "text", "text": "SENTINEL result"}],
    }
    content_variants = [
        ("text", {"type": "text", "text": "SENTINEL"}, ["type", "text"]),
        (
            "image",
            {"type": "image", "data": "SENTINEL", "mimeType": "image/png"},
            ["type", "data", "mimeType"],
        ),
        (
            "audio",
            {"type": "audio", "data": "SENTINEL", "mimeType": "audio/wav"},
            ["type", "data", "mimeType"],
        ),
        ("tool-use", use, ["type", "id", "name", "input"]),
        ("tool-result", result, ["type", "toolUseId", "content"]),
    ]
    for name, value, required in content_variants:
        wrap = (
            (lambda block: sampling_request([copy.deepcopy(use), block]))
            if name == "tool-result"
            else sampling_request
        )
        fields(name, value, required, [("_meta", {"safe": 7}, 42)], wrap)
        add(
            name + "-content-array",
            wrap([value]) if name != "tool-result" else sampling_request([use, value]),
            True,
        )
    for block in [
        {"type": "resource_link", "uri": "https://invalid.test/SENTINEL", "name": "r"},
        {
            "type": "resource",
            "resource": {"uri": "https://invalid.test/SENTINEL", "text": "x"},
        },
    ]:
        add("sampling-outer-" + block["type"], sampling_request(block), False)
        add(
            "tool-result-nested-" + block["type"],
            sampling_request([use, {**result, "content": [block]}]),
            True,
        )
    for value in [None, 7, [1], {"v": 7}, "SENTINEL", True]:
        add(
            "tool-result-structured-" + type(value).__name__,
            sampling_request([use, {**result, "structuredContent": value}]),
            True,
        )
    fields(
        "tool-result-optional",
        result,
        [],
        [("isError", True, "SENTINEL")],
        lambda block: sampling_request([use, block]),
    )
    add("tool-result-unmatched-id", sampling_request(result), False)
    add(
        "tool-result-nested-tool-use",
        sampling_request([use, {**result, "content": [use]}]),
        False,
    )

    text = {"type": "text", "text": "SENTINEL"}
    fields(
        "sampling-params",
        sampling_request(text)["params"],
        ["messages", "maxTokens"],
        [
            ("systemPrompt", "SENTINEL", 7),
            ("temperature", 0.5, True),
            ("includeContext", "none", "unknown"),
            ("stopSequences", ["x"], [7]),
            ("metadata", {"provider": None}, []),
            ("modelPreferences", {}, []),
            ("toolChoice", {}, []),
            ("tools", [], {}),
        ],
        lambda params: {"method": "sampling/createMessage", "params": params},
    )
    add("maxTokens-bool", sampling_request(text, maxTokens=True), False)
    fields(
        "sampling-message",
        {"role": "user", "content": text},
        ["role", "content"],
        [("_meta", {"safe": 1}, [])],
        lambda message: {
            "method": "sampling/createMessage",
            "params": {"messages": [message], "maxTokens": 5},
        },
    )
    fields(
        "model-preferences",
        {},
        [],
        [
            ("hints", [{}, {"name": "SENTINEL"}], [7]),
            ("costPriority", 0.5, True),
            ("speedPriority", 1, -1),
            ("intelligencePriority", 0, 2),
        ],
        lambda prefs: sampling_request(text, modelPreferences=prefs),
    )
    add(
        "model-hint-name-null",
        sampling_request(text, modelPreferences={"hints": [{"name": None}]}),
        False,
    )
    fields(
        "tool-choice",
        {},
        [],
        [("mode", "required", "unknown")],
        lambda choice: sampling_request(text, toolChoice=choice),
    )
    fields(
        "sampling-tool",
        {"name": "echo", "inputSchema": {"type": "object"}},
        ["name", "inputSchema"],
        [("outputSchema", {"type": "integer"}, [])],
        lambda t: sampling_request(text, tools=[t]),
    )
    for key in ["inputSchema", "outputSchema"]:
        schema = {"type": "object"} if key == "inputSchema" else {}
        fields(
            "sampling-tool-" + key,
            schema,
            ["type"] if key == "inputSchema" else [],
            [("$schema", "https://invalid.test/SENTINEL", 7)],
            lambda schema, key=key: sampling_request(
                text,
                tools=[
                    {
                        "name": "echo",
                        "inputSchema": {"type": "object"},
                        key: schema,
                    }
                ],
            ),
        )

    properties = [
        (
            "string",
            {"type": "string"},
            ["type"],
            [
                ("minLength", 0, True),
                ("maxLength", 8, "x"),
                ("format", "email", "unknown"),
                ("default", "x", 7),
            ],
        ),
        (
            "number",
            {"type": "number"},
            ["type"],
            [
                ("minimum", 0, True),
                ("maximum", 8, "x"),
                ("default", 2.5, True),
            ],
        ),
        ("integer", {"type": "integer"}, ["type"], [("default", 2, "x")]),
        ("boolean", {"type": "boolean"}, ["type"], [("default", True, 0)]),
        (
            "single-enum",
            {"type": "string", "enum": ["a"]},
            ["type"],
            [("enum", ["a"], [7]), ("default", "a", [])],
        ),
        (
            "single-titled",
            {"type": "string", "oneOf": [{"const": "a", "title": "A"}]},
            ["type"],
            [("oneOf", [{"const": "a", "title": "A"}], [{}])],
        ),
        (
            "legacy-titled",
            {"type": "string", "enum": ["a"]},
            ["type"],
            [("enumNames", ["A"], [7])],
        ),
        (
            "multi-enum",
            {"type": "array", "items": {"type": "string", "enum": ["a"]}},
            ["type", "items"],
            [("minItems", 0, True), ("maxItems", 3, "x"), ("default", ["a"], [7])],
        ),
        (
            "multi-titled",
            {"type": "array", "items": {"anyOf": [{"const": "a", "title": "A"}]}},
            ["type", "items"],
            [("default", ["a"], [7])],
        ),
    ]
    for name, value, required, optional in properties:
        fields(
            name,
            value,
            required,
            optional
            + [
                ("title", "SENTINEL", 7),
                ("description", "SENTINEL", []),
            ],
            form_request,
        )
    for kind in ["oneOf", "anyOf"]:
        for field in ["const", "title"]:
            for mutation in ["omitted", "null", "wrong"]:
                option = {"const": "a", "title": "A"}
                if mutation == "omitted":
                    del option[field]
                else:
                    option[field] = None if mutation == "null" else 7
                value = (
                    {"type": "string", "oneOf": [option]}
                    if kind == "oneOf"
                    else {"type": "array", "items": {"anyOf": [option]}}
                )
                add(f"{kind}-{field}-{mutation}", form_request(value), False)
    for items in [
        {},
        {"type": "string"},
        {"enum": ["a"]},
        {"type": "string", "enum": None},
        {"anyOf": None},
    ]:
        add(
            "array-items-" + str(items),
            form_request({"type": "array", "items": items}),
            False,
        )
    for value in [
        None,
        42,
        {},
        {"type": "object"},
        {"type": "array", "items": {"type": "number"}},
    ]:
        add("invalid-property-" + str(value), form_request(value), False)
    schema = {"type": "object", "properties": {"field": {"type": "string"}}}
    fields(
        "requested-schema",
        schema,
        ["type", "properties"],
        [
            ("$schema", "https://invalid.test/SENTINEL", 7),
            ("required", ["field"], [7]),
        ],
        lambda s: {
            "method": "elicitation/create",
            "params": {"message": "SENTINEL", "requestedSchema": s},
        },
    )
    fields(
        "form-params",
        {"message": "SENTINEL", "requestedSchema": schema},
        ["message", "requestedSchema"],
        [("mode", "form", "unknown")],
        lambda params: {"method": "elicitation/create", "params": params},
    )
    fields(
        "url-params",
        {"mode": "url", "message": "SENTINEL", "url": "https://invalid.test/SENTINEL"},
        ["mode", "message", "url"],
        [],
        lambda params: {"method": "elicitation/create", "params": params},
    )
    add("roots-omitted-params", {"method": "roots/list"}, True)
    add("roots-empty-params", {"method": "roots/list", "params": {}}, True)
    add("roots-null-params", {"method": "roots/list", "params": None}, False)
    for method in ["sampling/createMessage", "elicitation/create"]:
        for mutation, value in [
            ("omitted", {}),
            ("null", {"params": None}),
            ("wrong", {"params": []}),
        ]:
            add(method + "-params-" + mutation, {"method": method, **value}, False)
    add("unknown-method", {"method": "SENTINEL unknown", "params": {}}, False)
    add(
        "form-malformed-sibling",
        {
            "method": "elicitation/create",
            "params": {
                "message": "SENTINEL",
                "requestedSchema": {
                    "type": "object",
                    "properties": {"valid": {"type": "string"}, "bad": None},
                },
            },
        },
        False,
    )
    return cases


@pytest.mark.asyncio
@pytest.mark.parametrize("profile", ["stdio", "2026-07-28"])
@pytest.mark.parametrize("input_request,expected", input_variant_cases())
async def test_input_variant_public_disposition_privacy_and_zero_continuation(
    profile, input_request, expected, caplog
):
    client, peer = refresh_peer(profile)
    value = {
        "resultType": "input_required",
        "requestState": "SENTINEL state",
        "inputRequests": {"SENTINEL id": input_request},
    }
    await client.connect()
    try:
        old = (await MCPToolAdapter(client).get_tools())[0]
        if profile == "stdio":
            peer.handler = lambda message: {"result": value}
        else:
            peer.hook = lambda verb, headers, message: peer.rpc(message, value)
        before = len(peer_messages(peer))
        with pytest.raises(MCPToolExecutionError) as failure:
            await old.execute()
        assert failure.value.failure_code == expected
        assert failure.value.code == (
            -32100 if expected == "input_required_unsupported" else -32021
        )
        assert "SENTINEL" not in str(failure.value)
        assert "SENTINEL" not in "".join(traceback.format_exception(failure.value))
        assert "SENTINEL" not in caplog.text
        messages = peer_messages(peer)[before:]
        assert len(messages) == 1
        assert messages[0]["method"] == "tools/call"
        params = messages[0]["params"]
        assert set(params) == {"name", "arguments", "_meta"}
        assert params["name"] == "echo" and params["arguments"] == {}
        assert set(params["_meta"]) == {
            "io.modelcontextprotocol/protocolVersion",
            "io.modelcontextprotocol/clientCapabilities",
            "io.modelcontextprotocol/clientInfo",
        }
        assert params["_meta"]["io.modelcontextprotocol/clientCapabilities"] == {}
        assert "SENTINEL" not in str(messages)
        if profile == "stdio":
            peer.handler = peer.default
        else:
            peer.hook = None
        assert await old.execute() == "ok"
    finally:
        await client.disconnect()
    assert client.outstanding_catalog_owners == 0
    assert not client._pending_requests
    if profile != "stdio":
        assert client.outstanding_http_owners == 0
        assert all(stream.closed for stream in peer.streams)
