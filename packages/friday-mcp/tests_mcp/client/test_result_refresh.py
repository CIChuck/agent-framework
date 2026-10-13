"""Public manual refresh, generation races and complete result regression proof."""

import asyncio
from dataclasses import FrozenInstanceError

import pytest

from friday_mcp.client import MCPCatalogSnapshot, MCPRefreshClient
from friday_mcp.client.adapter import MCPToolAdapter
from friday_mcp.client.base import MCPError, MCPToolExecutionError
from friday_mcp.client.protocol import ProtocolFailure, ProtocolLimits, ToolResult
from tests_mcp.client.test_http_lifecycle import Peer, make_client
from tests_mcp.client.test_modern_protocol import Client, cached, complete, tool


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
