"""Protocol contracts through an asynchronous wire-shaped transport."""

import asyncio
import copy
import json
import logging

import pytest
from referencing import Registry
from referencing.exceptions import NoSuchResource

from friday_mcp.client.base import MCPClientBase, MCPError
from friday_mcp.client.protocol import (
    LEGACY_VERSION,
    META_PREFIX,
    MODERN_VERSION,
    Discovery,
    FrozenJSON,
    ProtocolFailure,
    ProtocolLimits,
    ToolResult,
    decode_json,
    validate_message,
    validate_output_schema,
)


def complete(**kwargs):
    return {"resultType": "complete", **kwargs}


def cached(**kwargs):
    return complete(ttlMs=0, cacheScope="private", **kwargs)


def tool(name="echo", **kwargs):
    return {"name": name, "inputSchema": {"type": "object"}, **kwargs}


def discover(**kwargs):
    return cached(
        supportedVersions=[MODERN_VERSION], capabilities={"tools": {}}, **kwargs
    )


class Transport:
    def __init__(self):
        self.sent = []
        self.incoming = asyncio.Queue()
        self.is_connected = False
        self.handler = self.default
        self.closed = 0
        self.fail_cleanup = False

    def default(self, message):
        method = message["method"]
        if method == "server/discover":
            return {"result": discover()}
        if method == "initialize":
            return {
                "result": {
                    "protocolVersion": LEGACY_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "fixture", "version": "1"},
                }
            }
        if method == "tools/list":
            return {"result": cached(tools=[tool()])}
        if method == "tools/call":
            return {"result": complete(content=[{"type": "text", "text": "ok"}])}
        return {"result": complete()}

    async def connect(self):
        self.is_connected = True

    async def disconnect(self):
        self.closed += 1
        if self.fail_cleanup:
            raise RuntimeError("SENTINEL cleanup")
        self.is_connected = False

    async def send(self, message):
        self.sent.append(copy.deepcopy(message))
        if "id" in message and "method" in message:
            response = self.handler(message)
            if response is not None:
                await self.incoming.put(
                    {"jsonrpc": "2.0", "id": message["id"], **response}
                )

    async def receive(self):
        return await self.incoming.get()


class Client(MCPClientBase):
    def __init__(self, profile="modern", limits=None):
        super().__init__("synthetic", protocol_profile=profile, limits=limits)
        self.transport = Transport()

    async def _create_transport(self):
        return self.transport

    def _request_was_issued(self, request_id):
        return any(m.get("id") == request_id for m in self.transport.sent)


@pytest.mark.asyncio
async def test_modern_discovery_metadata_identity_and_capabilities_are_honest():
    client = Client()
    client.transport.handler = (
        lambda message: {
            "result": discover(
                _meta={
                    META_PREFIX + "serverInfo": {"name": "UNTRUSTED", "version": "1"}
                },
                instructions="UNTRUSTED",
            )
        }
        if message["method"] == "server/discover"
        else client.transport.default(message)
    )
    await client.connect()
    assert await client.list_tools() == [tool()]
    assert await client.call_tool("echo", {}) == "ok"
    assert client.negotiated_version == MODERN_VERSION
    assert [m["method"] for m in client.transport.sent] == [
        "server/discover",
        "tools/list",
        "tools/call",
    ]
    for message in client.transport.sent:
        assert message["params"]["_meta"] == {
            META_PREFIX + "protocolVersion": MODERN_VERSION,
            META_PREFIX + "clientCapabilities": {},
            META_PREFIX + "clientInfo": {"name": "friday-mcp", "version": "0.1.0a2"},
        }
    snapshot = client.server_capabilities
    snapshot["tools"]["unsafe"] = True
    assert client.server_capabilities == {"tools": {}}
    assert "UNTRUSTED" not in repr(client._discovery)
    await client.disconnect()


@pytest.mark.asyncio
async def test_legacy_default_initializes_and_checks_negotiated_version():
    client = Client("legacy")
    await client.connect()
    assert client.negotiated_version == LEGACY_VERSION
    assert client.transport.sent[0]["params"]["capabilities"] == {}
    assert "_meta" not in client.transport.sent[0]["params"]
    assert client.transport.sent[1]["method"] == "notifications/initialized"
    await client.disconnect()
    client.transport.handler = lambda message: {"result": {"protocolVersion": "WRONG"}}
    with pytest.raises(ProtocolFailure, match="Unsupported"):
        await client.connect()
    assert client._transport is None
    assert client._receive_task is None


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [-32601, -32602, -32000])
async def test_auto_falls_back_once_for_any_non_modern_error(error):
    client = Client("auto")
    client.transport.handler = (
        lambda message: {"error": {"code": error, "message": "SENTINEL"}}
        if message["method"] == "server/discover"
        else client.transport.default(message)
    )
    await client.connect()
    assert client.negotiated_version == LEGACY_VERSION
    assert [m["method"] for m in client.transport.sent] == [
        "server/discover",
        "initialize",
        "notifications/initialized",
    ]
    await client.disconnect()


@pytest.mark.asyncio
async def test_recognized_modern_version_error_and_no_intersection_do_not_fallback(
    caplog,
):
    for response in [
        {"error": {"code": -32022, "message": "SENTINEL", "data": "SENTINEL"}},
        {"result": cached(supportedVersions=["OTHER"], capabilities={})},
    ]:
        client = Client("auto")
        client.transport.handler = lambda message, response=response: response
        with (
            caplog.at_level(logging.DEBUG),
            pytest.raises((MCPError, ProtocolFailure)) as caught,
        ):
            await client.connect()
        assert "SENTINEL" not in repr(caught.value)
        assert "SENTINEL" not in caplog.text
        assert [m["method"] for m in client.transport.sent] == ["server/discover"]
        assert client._transport is None


@pytest.mark.asyncio
async def test_auto_timeout_reserves_legacy_budget_and_late_id_cannot_settle_it():
    client = Client("auto", ProtocolLimits(timeout_seconds=0.12))
    client.transport.handler = (
        lambda message: None
        if message["method"] == "server/discover"
        else client.transport.default(message)
    )
    await client.connect()
    assert client.negotiated_version == LEGACY_VERSION
    probe = client.transport.sent[0]
    await client._handle_message(
        {"jsonrpc": "2.0", "id": probe["id"], "result": discover()}
    )
    assert await client.call_tool("echo", {}) == "ok"
    assert not client._pending_requests
    await client.disconnect()


@pytest.mark.parametrize(
    "mutation",
    [
        {"jsonrpc": "1.0"},
        {"id": True},
        {"id": None},
        {"id": []},
        {"result": {}, "error": {"code": -1, "message": "SENTINEL"}},
        {"result": None},
        {"error": {"code": True, "message": "SENTINEL"}},
        {"error": {"code": -1, "message": 4}},
        {"_meta": []},
    ],
)
def test_bad_envelopes_reject_without_peer_details(mutation):
    message = {"jsonrpc": "2.0", "id": "a", "result": complete()}
    if "error" in mutation and "result" not in mutation:
        message.pop("result")
    message.update(mutation)
    with pytest.raises(ProtocolFailure) as caught:
        validate_message(message, ProtocolLimits())
    assert "SENTINEL" not in repr(caught.value)


@pytest.mark.asyncio
async def test_wrong_integer_and_duplicate_ids_do_not_cross_settle_requests():
    client = Client()
    await client.connect()
    client.transport.handler = lambda message: None
    tasks = [asyncio.create_task(client._request("ping", {})) for _ in range(2)]
    await asyncio.sleep(0.01)
    messages = client.transport.sent[-2:]
    await client._handle_message(
        {"jsonrpc": "2.0", "id": 1, "result": complete(value="wrong")}
    )
    assert not any(t.done() for t in tasks)
    for message in reversed(messages):
        response = {
            "jsonrpc": "2.0",
            "id": message["id"],
            "result": complete(value=message["id"]),
        }
        await client._handle_message(response)
        await client._handle_message(response)
    results = await asyncio.gather(*tasks)
    assert [r["value"] for r in results] == [m["id"] for m in messages]
    await client.disconnect()


@pytest.mark.asyncio
async def test_pagination_complete_fresh_catalog_and_retained_output_schema():
    client = Client()
    await client.connect()

    def handler(message):
        if message["method"] == "tools/list":
            if message["params"].get("cursor") == "next":
                return {"result": cached(tools=[tool("two")])}
            return {
                "result": cached(
                    tools=[tool("one", outputSchema={"type": "integer"})],
                    nextCursor="next",
                )
            }
        return {"result": complete(content=[], structuredContent=3)}

    client.transport.handler = handler
    catalog = await client.list_tools()
    assert [t["name"] for t in catalog] == ["one", "two"]
    catalog[0]["outputSchema"]["type"] = "string"
    assert await client.call_tool("one", {}) == "3"
    client.transport.handler = lambda message: {
        "result": complete(content=[], structuredContent="wrong")
    }
    with pytest.raises(MCPError) as caught:
        await client.call_tool("one", {})
    assert caught.value.failure_code == "invalid_result"
    await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case",
    [
        "cycle",
        "endless",
        "cursor",
        "tools",
        "entries",
        "bytes",
        "duplicate",
        "missing-cache",
    ],
)
async def test_catalog_failures_never_retain_a_successful_partial_list(case):
    limits = ProtocolLimits(catalog_pages=2, catalog_tools=2, catalog_bytes=1024)
    client = Client(limits=limits)
    await client.connect()
    pages = 0

    def handler(message):
        nonlocal pages
        pages += 1
        result = cached(tools=[tool(str(pages))], nextCursor=str(pages))
        if case == "cycle":
            result["nextCursor"] = "same"
        elif case == "cursor":
            result["nextCursor"] = None
        elif case == "tools":
            result["tools"] = "SENTINEL"
        elif case == "entries":
            result["tools"] = [tool(str(i)) for i in range(3)]
        elif case == "bytes":
            result["tools"] = [tool(description="x" * 1500)]
        elif case == "duplicate":
            result["tools"] = [tool("same")]
        elif case == "missing-cache":
            result.pop("cacheScope")
        return {"result": result}

    client.transport.handler = handler
    with pytest.raises(ProtocolFailure):
        await client.list_tools()
    assert client._catalog == ()
    assert pages <= 2
    await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [None, [1, 2], 7, True, "value", {"b": 2, "a": 1}])
async def test_structured_scalar_array_null_preservation(value):
    client = Client()
    await client.connect()
    client.transport.handler = lambda message: {
        "result": complete(content=[], structuredContent=value)
    }
    assert json.loads(await client.call_tool("echo", {})) == value
    client.transport.handler = lambda message: {
        "result": complete(
            content=[{"type": "text", "text": "narrative"}], structuredContent=value
        )
    }
    envelope = json.loads(await client.call_tool("echo", {}))
    assert envelope == {
        "content": [{"type": "text", "text": "narrative"}],
        "structuredContent": value,
    }
    await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "result,code",
    [
        ({"content": []}, "invalid_result"),
        ({"resultType": "future", "content": []}, "invalid_result"),
        (
            {"resultType": "input_required", "requestState": "SENTINEL"},
            "input_required_unsupported",
        ),
        (complete(content=["legacy-string"]), "invalid_result"),
        (
            complete(content=[{"type": "image", "data": "SENTINEL"}]),
            "unsupported_content",
        ),
        (complete(content=[], isError=True), "tool_error"),
        (complete(content=[], isError="SENTINEL"), "invalid_result"),
    ],
)
async def test_modern_result_tags_and_content_have_safe_no_replay_outcomes(
    result, code, caplog
):
    client = Client()
    await client.connect()
    client.transport.handler = lambda message: {"result": result}
    with caplog.at_level(logging.DEBUG), pytest.raises(MCPError) as caught:
        await client.call_tool("echo", {"secret": "SENTINEL"})
    assert caught.value.failure_code == code
    assert "SENTINEL" not in str(caught.value) + repr(caught.value) + caplog.text
    assert len([m for m in client.transport.sent if m["method"] == "tools/call"]) == 1
    await client.disconnect()


@pytest.mark.parametrize(
    "schema",
    [
        {"$schema": "http://json-schema.org/draft-07/schema#"},
        {"$ref": "https://example.com/secret"},
        {"$id": "https://example.com"},
        {"$ref": "#/$defs/a", "$defs": {"a": {"$ref": "#/$defs/a"}}},
        {"pattern": "(a+)+$"},
        {"oneOf": [{}, {}]},
        {"uniqueItems": True},
        {"allOf": [{}] * 100},
        {"enum": [{}]},
        {"type": "wrong"},
    ],
)
def test_schema_resource_profile_refuses_external_cycles_regex_and_unbounded_features(
    schema,
):
    with pytest.raises(ProtocolFailure, match="unsupported"):
        validate_output_schema(schema, ProtocolLimits())


@pytest.mark.parametrize(
    "schema",
    [
        {
            "type": "object",
            "properties": {"n": {"type": "integer"}},
            "required": ["n"],
            "additionalProperties": False,
        },
        {"type": "array", "items": {"type": "string"}, "maxItems": 8},
        {"$defs": {"n": {"type": "integer"}}, "$ref": "#/$defs/n"},
    ],
)
def test_bounded_output_schema_profile_accepts_2020_12_objects_arrays_local_refs(
    schema,
):
    assert validate_output_schema(schema, ProtocolLimits()).object() == schema


@pytest.mark.parametrize(
    "name,value",
    [
        ("concurrent_requests", 5),
        ("catalog_pages", 0),
        ("depth", True),
        ("timeout_seconds", float("nan")),
        ("timeout_seconds", 31),
        ("frame_bytes", 1048577),
    ],
)
def test_limits_are_positive_validated_and_can_only_lower_caps(name, value):
    with pytest.raises(ValueError):
        ProtocolLimits(**{name: value})


def test_decoder_checks_bytes_depth_duplicate_keys_nonfinite_and_repr_privacy():
    for data in [
        b" " * 1048577,
        b"[" * 50 + b"0" + b"]" * 50,
        b'{"a":1,"a":2}',
        b'{"a":NaN}',
    ]:
        with pytest.raises(ProtocolFailure):
            decode_json(data, ProtocolLimits())
    assert "SENTINEL" not in repr(
        FrozenJSON.from_value({"data": "SENTINEL"}, ProtocolLimits())
    )
    assert "SENTINEL" not in repr(
        ToolResult.parse(
            complete(content=[], structuredContent="SENTINEL"), True, ProtocolLimits()
        )
    )
    assert Discovery.parse(discover(), ProtocolLimits()).versions == (MODERN_VERSION,)


@pytest.mark.asyncio
async def test_concurrency_bound_checked_before_allocating_another_waiter():
    client = Client(limits=ProtocolLimits(concurrent_requests=2))
    await client.connect()
    client.transport.handler = lambda message: None
    tasks = [asyncio.create_task(client._request("ping", {})) for _ in range(2)]
    await asyncio.sleep(0.01)
    with pytest.raises(ProtocolFailure, match="limit"):
        await client._request("ping", {})
    assert len(client._pending_requests) == 2
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    assert not client._pending_requests
    await client.disconnect()


@pytest.mark.asyncio
async def test_stalled_send_is_in_request_deadline_and_unissued_request_not_cancelled():
    client = Client(limits=ProtocolLimits(timeout_seconds=0.05))
    await client.connect()

    async def send(message):
        await asyncio.Future()

    client.transport.send = send
    with pytest.raises(TimeoutError):
        await client.call_tool("echo", {})
    assert not client._pending_requests
    assert not client._control_tasks
    await client.disconnect()


@pytest.mark.asyncio
async def test_catalog_pages_share_one_deadline():
    client = Client(limits=ProtocolLimits(timeout_seconds=0.06))
    await client.connect()
    original = client.transport.send

    async def send(message):
        await asyncio.sleep(0.04)
        await original(message)

    client.transport.send = send
    client.transport.handler = lambda message: {
        "result": cached(tools=[], nextCursor=message["id"])
    }
    start = asyncio.get_running_loop().time()
    with pytest.raises(TimeoutError):
        await client.list_tools()
    assert asyncio.get_running_loop().time() - start < 0.15
    assert client._catalog == ()
    await client.disconnect()


@pytest.mark.asyncio
async def test_modern_server_request_fails_without_emitting_client_response():
    client = Client()
    await client.connect()
    before = len(client.transport.sent)
    with pytest.raises(ProtocolFailure):
        await client._handle_message(
            {"jsonrpc": "2.0", "id": "peer", "method": "sampling/createMessage"}
        )
    assert len(client.transport.sent) == before
    await client.disconnect()


@pytest.mark.asyncio
async def test_legacy_unknown_server_request_gets_fixed_method_error():
    client = Client("legacy")
    await client.connect()
    await client._handle_message({"jsonrpc": "2.0", "id": "peer", "method": "SENTINEL"})
    assert client.transport.sent[-1] == {
        "jsonrpc": "2.0",
        "id": "peer",
        "error": {"code": -32601, "message": "Method not supported"},
    }
    await client.disconnect()


@pytest.mark.asyncio
async def test_primary_handshake_failure_survives_retryable_cleanup_failure():
    client = Client()
    client.transport.handler = lambda message: {
        "error": {"code": -32022, "message": "SENTINEL"}
    }
    client.transport.fail_cleanup = True
    with pytest.raises(MCPError) as caught:
        await client.connect()
    assert caught.value.code == -32022
    assert client._transport is client.transport
    client.transport.fail_cleanup = False
    await client.disconnect()
    assert client._transport is None


def test_registry_default_refuses_external_retrieval():
    with pytest.raises(NoSuchResource):
        Registry().get_or_retrieve("https://example.com/private-schema")


@pytest.mark.parametrize(
    "data",
    [
        {
            "supportedVersions": [MODERN_VERSION],
            "capabilities": [],
            "ttlMs": 0,
            "cacheScope": "private",
        },
        {
            "supportedVersions": [MODERN_VERSION],
            "capabilities": {},
            "ttlMs": True,
            "cacheScope": "private",
        },
        {
            "supportedVersions": [MODERN_VERSION],
            "capabilities": {},
            "ttlMs": 10**1000,
            "cacheScope": "private",
        },
        {
            "supportedVersions": [MODERN_VERSION],
            "capabilities": {},
            "ttlMs": 0,
            "cacheScope": "future",
        },
        {
            "supportedVersions": [],
            "capabilities": {},
            "ttlMs": 0,
            "cacheScope": "private",
        },
    ],
)
def test_discovery_versions_capabilities_and_cache_hints_are_validated(data):
    with pytest.raises(ProtocolFailure):
        Discovery.parse(complete(**data), ProtocolLimits())


@pytest.mark.asyncio
async def test_connect_deadline_includes_spawn_and_reserves_fallback_budget():
    client = Client("auto", ProtocolLimits(timeout_seconds=0.1))
    original_connect = client.transport.connect

    async def connect():
        await asyncio.sleep(0.06)
        await original_connect()

    client.transport.connect = connect
    client.transport.handler = (
        lambda message: None
        if message["method"] == "server/discover"
        else client.transport.default(message)
    )
    start = asyncio.get_running_loop().time()
    await client.connect()
    assert client.negotiated_version == LEGACY_VERSION
    assert asyncio.get_running_loop().time() - start < 0.13
    await client.disconnect()


@pytest.mark.asyncio
async def test_outgoing_limit_precedes_send_and_waiter_allocation():
    client = Client(limits=ProtocolLimits(frame_bytes=1024))
    await client.connect()
    count = len(client.transport.sent)
    with pytest.raises(MCPError) as caught:
        await client.call_tool("echo", {"text": "x" * 2000})
    assert caught.value.failure_code == "limit_exceeded"
    assert len(client.transport.sent) == count
    assert not client._pending_requests
    await client.disconnect()


@pytest.mark.asyncio
async def test_catalog_accounts_wire_whitespace_and_envelope_bytes():
    from friday_mcp.client.protocol import ResultSnapshot

    client = Client(limits=ProtocolLimits(catalog_bytes=100))
    client._server_capabilities = {"tools": {}}

    async def request(method, params):
        return ResultSnapshot(cached(tools=[]), wire_bytes=200)

    client._request = request
    with pytest.raises(ProtocolFailure, match="limit"):
        await client.list_tools()
    assert client._catalog == ()


@pytest.mark.asyncio
async def test_context_primary_failure_survives_cleanup_failure_with_owner_retained():
    client = Client()
    await client.connect()
    client.transport.fail_cleanup = True
    with pytest.raises(ValueError, match="primary"):
        async with client:
            raise ValueError("primary")
    assert client._transport is client.transport
    client.transport.fail_cleanup = False
    await client.disconnect()


@pytest.mark.asyncio
async def test_cancel_resistant_send_is_bounded_and_retained_for_cleanup_retry():
    client = Client(limits=ProtocolLimits(timeout_seconds=0.03, concurrent_requests=1))
    await client.connect()
    release = asyncio.Event()

    async def send(message):
        while not release.is_set():
            try:
                await release.wait()
            except asyncio.CancelledError:
                continue

    client.transport.send = send
    start = asyncio.get_running_loop().time()
    try:
        with pytest.raises(TimeoutError):
            await client.call_tool("echo", {})
        assert asyncio.get_running_loop().time() - start < 0.1
        assert len(client._exchange_tasks) == 1
        with pytest.raises(ProtocolFailure, match="limit"):
            await client._request("ping", {})
        with pytest.raises(RuntimeError, match="cleanup incomplete"):
            await client.disconnect()
        assert len(client._exchange_tasks) == 1
    finally:
        release.set()
        await asyncio.sleep(0.01)
        await client.disconnect()
    assert not client._exchange_tasks


def test_invalid_constructor_models_are_rejected_and_modern_timeout_cannot_expand():
    with pytest.raises(ValueError):
        Client(limits={})
    client = Client(limits=ProtocolLimits(timeout_seconds=0.1))
    client.request_timeout_seconds = 77
    assert client._timeout() == 0.1


@pytest.mark.asyncio
async def test_expired_preparation_deadline_issues_no_request():
    client = Client()
    await client.connect()
    before = len(client.transport.sent)
    client.request_timeout_seconds = 1e-12
    with pytest.raises(TimeoutError):
        await client.call_tool("echo", {})
    assert len(client.transport.sent) == before
    assert not client._pending_requests and not client._exchange_tasks
    await client.disconnect()
