"""Public modern-server wire contract: positive and malformed field variants."""

import asyncio
import json
from dataclasses import fields

import pytest

from friday_mcp.server import (
    ModernToolsMCPServer,
    RegisteredTool,
    ServerLimits,
    ToolCallResult,
)
from friday_mcp.server.protocol import (
    PREFIX,
    VERSION,
    ServerRequest,
    ServerWireError,
    encode,
)


def rpc(method="server/discover", *, params=None, rid=1, meta=None):
    return json.dumps(
        {
            "jsonrpc": "2.0",
            "id": rid,
            "method": method,
            "params": {
                "_meta": meta
                if meta is not None
                else {
                    PREFIX + "protocolVersion": VERSION,
                    PREFIX + "clientCapabilities": {},
                },
                **(params or {}),
            },
        },
        ensure_ascii=False,
    ).encode()


async def echo(args):
    return ToolCallResult.structured(args)


def definition(name="echo", **extra):
    return {
        "name": name,
        "description": "Synthetic echo",
        "inputSchema": {"type": "object"},
        **extra,
    }


@pytest.mark.asyncio
async def test_discovery_empty_and_direct_call_no_session():
    server = ModernToolsMCPServer()
    result = (await server.handle(rpc()))["result"]
    assert result == {
        "ttlMs": 0,
        "cacheScope": "private",
        "resultType": "complete",
        "supportedVersions": [VERSION],
        "capabilities": {"tools": {}},
        "_meta": {
            PREFIX + "serverInfo": {"name": "FridayModernTools", "version": "1.0.0"}
        },
    }
    assert (await server.handle(rpc("tools/list")))["result"]["tools"] == []
    server.register_tool(definition(), echo)
    assert (
        await server.handle(
            rpc("tools/call", params={"name": "echo", "arguments": {"x": 1}})
        )
    )["result"]["structuredContent"] == {"x": 1}
    await server.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "raw,code",
    [
        (b"{", -32700),
        (b"{}", -32600),
        (b"[]", -32600),
        (b'[{"jsonrpc":"2.0"}]', -32600),
        (b'{"jsonrpc":"2.0","id":1,"result":{}}', -32600),
        (b'{"jsonrpc":"2.0","method":"x","method":"y"}', -32700),
        (b"\xff", -32700),
    ],
)
async def test_envelope_rejects_without_handlers(raw, code):
    server = ModernToolsMCPServer()
    result = await server.handle(raw)
    assert result["error"]["code"] == code
    assert "id" not in result
    assert server.active_requests == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("rid", [None, True, False, 1.5, [], {}, 2**54, "x" * 257])
async def test_invalid_id_has_no_echo(rid):
    result = await ModernToolsMCPServer().handle(rpc(rid=rid))
    assert result["error"]["code"] == -32600
    assert "id" not in result


@pytest.mark.asyncio
@pytest.mark.parametrize("rid", [0, -1, 2**53 - 1, "", "unicode-世界"])
async def test_valid_ids_echo_only_own_request(rid):
    assert (await ModernToolsMCPServer().handle(rpc(rid=rid)))["id"] == rid


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "key", [PREFIX + "protocolVersion", PREFIX + "clientCapabilities"]
)
@pytest.mark.parametrize("value", [None, False, 1, [], "bad"])
async def test_required_meta_types(key, value):
    meta = {PREFIX + "protocolVersion": VERSION, PREFIX + "clientCapabilities": {}}
    meta[key] = value
    result = await ModernToolsMCPServer().handle(rpc(meta=meta))
    assert result["error"]["code"] == (
        -32022 if key.endswith("protocolVersion") and isinstance(value, str) else -32602
    )
    assert result["id"] == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "key", [PREFIX + "protocolVersion", PREFIX + "clientCapabilities"]
)
async def test_required_meta_omission(key):
    meta = {PREFIX + "protocolVersion": VERSION, PREFIX + "clientCapabilities": {}}
    del meta[key]
    assert (await ModernToolsMCPServer().handle(rpc(meta=meta)))["error"][
        "code"
    ] == -32602


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "info",
    [
        None,
        {},
        {"name": "x"},
        {"version": "x"},
        {"name": 3, "version": "x"},
        {"name": "x", "version": "x", "title": None},
        {"name": "x", "version": "x", "icons": None},
        {"name": "x", "version": "x", "icons": [{"src": "x", "theme": "wrong"}]},
    ],
)
async def test_optional_implementation_malformed(info):
    assert (
        await ModernToolsMCPServer().handle(
            rpc(
                meta={
                    PREFIX + "protocolVersion": VERSION,
                    PREFIX + "clientCapabilities": {},
                    PREFIX + "clientInfo": info,
                }
            )
        )
    )["error"]["code"] == -32602


@pytest.mark.asyncio
async def test_optional_implementation_extensions_and_per_request_caps():
    server = ModernToolsMCPServer()
    meta = {
        PREFIX + "protocolVersion": VERSION,
        PREFIX + "clientCapabilities": {
            "sampling": {"context": {}, "tools": {}},
            "roots": {},
            "elicitation": {"form": {}, "url": {}},
            "experimental": {"x": {}},
            "extensions": {"example.org/test": {}},
        },
        PREFIX + "clientInfo": {
            "name": "synthetic",
            "version": "1",
            "title": "Title",
            "description": "Description",
            "websiteUrl": "https://example.invalid",
            "icons": [
                {
                    "src": "data:image/png;base64,AA==",
                    "mimeType": "image/png",
                    "sizes": ["any"],
                    "theme": "light",
                }
            ],
        },
        "example.org/trace": {"secret": "sentinel"},
        "progressToken": 2,
        PREFIX + "logLevel": "info",
    }
    assert "result" in await server.handle(rpc(meta=meta))
    assert "result" in await server.handle(rpc())
    meta.pop(PREFIX + "clientCapabilities")
    assert (await server.handle(rpc(meta=meta)))["error"]["code"] == -32602
    assert "sentinel" not in str(server.tools)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cap", ["sampling", "roots", "elicitation", "experimental", "extensions"]
)
@pytest.mark.parametrize("value", [None, True, [], "bad"])
async def test_capability_variants(cap, value):
    assert (
        await ModernToolsMCPServer().handle(
            rpc(
                meta={
                    PREFIX + "protocolVersion": VERSION,
                    PREFIX + "clientCapabilities": {cap: value},
                }
            )
        )
    )["error"]["code"] == -32602


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method",
    [
        "initialize",
        "resources/list",
        "prompts/list",
        "subscriptions/listen",
        "tasks/get",
        "logging/setLevel",
        "ping",
        "unknown",
    ],
)
async def test_unsupported_methods_exact_wire_code(method):
    result = await ModernToolsMCPServer().handle(rpc(method))
    assert result == {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32601, "message": "Method not found"},
    }


@pytest.mark.asyncio
async def test_unsupported_version_safe_data():
    result = await ModernToolsMCPServer().handle(
        rpc(
            meta={
                PREFIX + "protocolVersion": "2025-11-25",
                PREFIX + "clientCapabilities": {},
            }
        )
    )
    assert result["error"] == {
        "code": -32022,
        "message": "Unsupported protocol version",
        "data": {"supported": [VERSION], "requested": "2025-11-25"},
    }


@pytest.mark.asyncio
async def test_catalog_atomic_deep_snapshots_and_stale_cursors():
    server = ModernToolsMCPServer(limits=ServerLimits(page_tools=1))
    original = definition("a")
    server.register_tool(original, echo)
    original["description"] = "mutated"
    server.register_tool(definition("b"), echo)
    first = (await server.handle(rpc("tools/list")))["result"]
    assert first["ttlMs"] == 0 and first["cacheScope"] == "private"
    assert first["tools"][0]["description"] == "Synthetic echo"
    cursor = first["nextCursor"]
    assert (await server.handle(rpc("tools/list", params={"cursor": cursor})))[
        "result"
    ]["tools"][0]["name"] == "b"
    export = server.tools
    export[0]["inputSchema"]["bad"] = True
    assert "bad" not in server.tools[0]["inputSchema"]
    with pytest.raises(ValueError, match="collision"):
        server.replace_tools(
            [RegisteredTool.from_definition(definition("a"), echo)] * 2
        )
    assert len(server.tools) == 2
    server.remove_tool("b")
    for invalid in (cursor, "forged", "", None, 1, "x" * 257):
        assert (await server.handle(rpc("tools/list", params={"cursor": invalid})))[
            "error"
        ]["code"] == -32602


@pytest.mark.asyncio
async def test_pagination_byte_partition_and_incompatible_limits_are_atomic():
    server = ModernToolsMCPServer(
        limits=ServerLimits(result_bytes=1500, identity_bytes=64)
    )
    server.replace_tools(
        RegisteredTool.from_definition(
            definition(str(i), description="世界" * 100), echo
        )
        for i in range(5)
    )
    cursor = None
    names = []
    while True:
        response = await server.handle(
            rpc("tools/list", params={} if cursor is None else {"cursor": cursor})
        )
        assert (
            response["result"]["ttlMs"] == 0
            and response["result"]["cacheScope"] == "private"
        )
        assert len(encode(response, server.limits)) <= 1500
        names += [t["name"] for t in response["result"]["tools"]]
        cursor = response["result"].get("nextCursor")
        if cursor is None:
            break
    assert names == list(map(str, range(5)))
    before = server.tools
    with pytest.raises((ValueError, ServerWireError)):
        server.register_tool(definition("large", description="x" * 2000), echo)
    assert server.tools == before
    with pytest.raises(ValueError):
        ModernToolsMCPServer(limits=ServerLimits(result_bytes=1))


@pytest.mark.parametrize(
    "schema",
    [
        {"type": "object", "$ref": "https://example.invalid"},
        {"type": "object", "$ref": "#"},
        {"type": "object", "patternProperties": {"(a+)+$": {}}},
        {"type": "object", "oneOf": [{}, {}]},
        {
            "type": "object",
            "properties": {"x": {"type": "string", "pattern": "(a+)+$"}},
        },
        {"type": "object", "$schema": "draft07"},
        {
            "type": "object",
            "properties": {"x": {"type": "number", "x-mcp-header": "X"}},
        },
        {"type": "object", "items": {"type": "string", "x-mcp-header": "X"}},
        {
            "type": "object",
            "properties": {
                "x": {"type": "string", "x-mcp-header": "X"},
                "y": {"type": "string", "x-mcp-header": "x"},
            },
        },
    ],
)
def test_unsupported_schema_rejected_without_registration(schema):
    server = ModernToolsMCPServer()
    with pytest.raises((ValueError, ServerWireError)):
        server.register_tool(definition(inputSchema=schema), echo)
    assert server.tools == ()


def test_sync_handler_rejected():
    with pytest.raises(ValueError, match="async"):
        ModernToolsMCPServer().register_tool(
            definition(), lambda args: ToolCallResult.text("bad")
        )


@pytest.mark.asyncio
async def test_argument_validation_zero_invocations_and_fixed_failure_privacy():
    calls = []

    async def handler(args):
        calls.append(args)
        raise RuntimeError("secret-peer-token")

    server = ModernToolsMCPServer()
    server.register_tool(
        definition(
            inputSchema={
                "type": "object",
                "properties": {"x": {"type": "integer", "minimum": 1}},
                "required": ["x"],
                "additionalProperties": False,
            }
        ),
        handler,
    )
    for args in (None, [], {}, {"x": True}, {"x": 0}, {"x": 1, "extra": "secret"}):
        assert (
            await server.handle(
                rpc("tools/call", params={"name": "echo", "arguments": args})
            )
        )["error"]["code"] == -32602
    assert not calls
    response = await server.handle(
        rpc("tools/call", params={"name": "echo", "arguments": {"x": 1}})
    )
    assert len(calls) == 1 and response["result"]["isError"] is True
    assert "secret-peer-token" not in str(response)


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [None, True, 0, 1.5, "世界", [1, None], {"x": 1}])
async def test_structured_arbitrary_json_and_explicit_null(value):
    async def handler(args):
        return ToolCallResult.structured(value, texts=("first", "second"))

    server = ModernToolsMCPServer()
    server.register_tool(definition(), handler)
    result = (await server.handle(rpc("tools/call", params={"name": "echo"})))["result"]
    assert "ttlMs" not in result and "cacheScope" not in result
    assert result["structuredContent"] == value
    assert [b["text"] for b in result["content"]] == ["first", "second"]
    assert "structuredContent" not in ToolCallResult.text("text").value()


@pytest.mark.asyncio
async def test_captured_output_schema_during_replacement():
    held = asyncio.Event()
    release = asyncio.Event()

    async def handler(args):
        held.set()
        await release.wait()
        return ToolCallResult.structured(5)

    server = ModernToolsMCPServer()
    server.register_tool(definition(outputSchema={"type": "integer"}), handler)
    issued = asyncio.create_task(
        server.handle(rpc("tools/call", params={"name": "echo"}))
    )
    await held.wait()
    server.replace_tools(
        [
            RegisteredTool.from_definition(
                definition(outputSchema={"type": "string"}), echo
            )
        ]
    )
    release.set()
    assert (await issued)["result"]["structuredContent"] == 5


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "returned",
    [
        ToolCallResult.text("missing"),
        ToolCallResult.structured("wrong"),
        ToolCallResult(
            b'{"content":[{"type":"image","data":"AA==","mimeType":"image/png"}]}'
        ),
        ToolCallResult(b'{"content":null}'),
        "wrong",
    ],
)
async def test_malformed_or_schema_invalid_result_fixed_error(returned):
    calls = 0

    async def handler(args):
        nonlocal calls
        calls += 1
        return returned

    server = ModernToolsMCPServer()
    server.register_tool(definition(outputSchema={"type": "integer"}), handler)
    assert (await server.handle(rpc("tools/call", params={"name": "echo"})))["error"][
        "code"
    ] == -32603
    assert calls == 1


@pytest.mark.asyncio
async def test_legitimate_tool_error_skips_success_schema_and_oversize_actual_wire():
    async def handler(args):
        return ToolCallResult.text("failure", is_error=True)

    server = ModernToolsMCPServer()
    server.register_tool(definition(outputSchema={"type": "integer"}), handler)
    assert (await server.handle(rpc("tools/call", params={"name": "echo"})))["result"][
        "isError"
    ] is True

    async def oversized(args):
        return ToolCallResult.text("界" * 21800)

    server.replace_tools([RegisteredTool.from_definition(definition(), oversized)])
    assert (await server.handle(rpc("tools/call", params={"name": "echo"})))["error"][
        "code"
    ] == -32603


@pytest.mark.parametrize("name", [f.name for f in fields(ServerLimits)])
@pytest.mark.parametrize("value", [True, False, 0, -1, float("inf"), float("nan")])
def test_lower_only_limits_invalid_values(name, value):
    with pytest.raises(ValueError):
        ServerLimits(**{name: value})


@pytest.mark.parametrize("name", [f.name for f in fields(ServerLimits)])
def test_limits_cannot_increase(name):
    with pytest.raises(ValueError):
        ServerLimits(**{name: getattr(ServerLimits(), name) + 1})


@pytest.mark.parametrize(
    "meta",
    [None, [], {PREFIX + "subscriptionId": None}, {PREFIX + "subscriptionId": True}],
)
def test_notification_meta_separate_grammar(meta):
    raw = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "notifications/cancelled",
            "params": {"requestId": 1, "_meta": meta},
        }
    ).encode()
    with pytest.raises(ServerWireError):
        ServerRequest.parse(raw, ServerLimits())


def test_notification_valid_without_request_metadata():
    for params in (
        {"requestId": 1},
        {
            "requestId": "a",
            "reason": "ignored",
            "_meta": {PREFIX + "subscriptionId": 2},
        },
    ):
        request = ServerRequest.parse(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/cancelled",
                    "params": params,
                }
            ).encode(),
            ServerLimits(),
        )
        assert request.request_id is None


@pytest.mark.parametrize("method", ["server/discover", "tools/list"])
@pytest.mark.parametrize(
    "key,value,omit",
    [
        ("ttlMs", None, True),
        ("ttlMs", None, False),
        ("ttlMs", "bad", False),
        ("ttlMs", -1, False),
        ("cacheScope", None, True),
        ("cacheScope", None, False),
        ("cacheScope", "other", False),
        ("cacheScope", {}, False),
    ],
)
def test_sdk_dated_cacheable_field_variants(method, key, value, omit):
    from mcp_types.methods import validate_server_result
    from pydantic import ValidationError

    valid = {"resultType": "complete", "ttlMs": 0, "cacheScope": "private"}
    valid.update(
        {"tools": []}
        if method == "tools/list"
        else {"supportedVersions": [VERSION], "capabilities": {"tools": {}}}
    )
    validate_server_result(method, VERSION, valid)
    invalid = dict(valid)
    if omit:
        invalid.pop(key)
    else:
        invalid[key] = value
    with pytest.raises(ValidationError):
        validate_server_result(method, VERSION, invalid)


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [1.5, "token", 1, 0])
async def test_progress_token_number_or_string_accepted_without_notifications(value):
    meta = {
        PREFIX + "protocolVersion": VERSION,
        PREFIX + "clientCapabilities": {},
        "progressToken": value,
    }
    assert "result" in await ModernToolsMCPServer().handle(rpc(meta=meta))


@pytest.mark.parametrize(
    "extra",
    [
        {"title": None},
        {"icons": None},
        {"icons": [{"src": None}]},
        {"icons": [{"src": "x", "mimeType": None}]},
        {"icons": [{"src": "x", "sizes": [None]}]},
        {"annotations": None},
        {"annotations": {"title": None}},
        {"annotations": {"readOnlyHint": None}},
        {"annotations": {"destructiveHint": "true"}},
        {"annotations": {"idempotentHint": 1}},
        {"annotations": {"openWorldHint": []}},
        {"_meta": None},
    ],
)
def test_optional_tool_field_null_and_malformed_variants(extra):
    with pytest.raises(ValueError):
        RegisteredTool.from_definition(definition(**extra), echo)


def test_complete_tool_optional_fields_are_immutable_and_preserved():
    optional = {
        "title": "Display",
        "icons": [
            {
                "src": "data:image/png;base64,AA==",
                "mimeType": "image/png",
                "sizes": ["any"],
                "theme": "dark",
            }
        ],
        "annotations": {
            "title": "Annotation",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "_meta": {"example.org/note": "Synthetic"},
        "outputSchema": {"type": "integer"},
    }
    tool = RegisteredTool.from_definition(definition(**optional), echo)
    assert tool.definition() == definition(**optional)
    optional["annotations"]["readOnlyHint"] = False
    assert tool.definition()["annotations"]["readOnlyHint"] is True


@pytest.mark.parametrize(
    "annotations",
    [
        None,
        {"audience": None},
        {"audience": ["wrong"]},
        {"priority": True},
        {"priority": -1},
        {"priority": 2},
        {"lastModified": None},
    ],
)
def test_text_annotations_malformed_rejected(annotations):
    with pytest.raises(ServerWireError):
        ToolCallResult.from_value(
            {
                "content": [
                    {"type": "text", "text": "synthetic", "annotations": annotations}
                ]
            }
        )


def test_text_annotation_metadata_complete_and_input_required_rejected():
    content = [
        {
            "type": "text",
            "text": "synthetic",
            "annotations": {
                "audience": ["user", "assistant"],
                "priority": 0.5,
                "lastModified": "2026-10-13T12:00:00Z",
            },
            "_meta": {"example.org/note": "synthetic"},
        }
    ]
    assert ToolCallResult.from_value({"content": content}).value()["content"] == content
    for result_type in (None, "input_required", "unknown"):
        with pytest.raises(ServerWireError):
            ToolCallResult.from_value({"content": content, "resultType": result_type})


@pytest.mark.asyncio
async def test_page_worst_encoded_valid_id_and_low_catalog_count():
    server = ModernToolsMCPServer(
        limits=ServerLimits(result_bytes=2500, identity_bytes=192)
    )
    server.register_tool(definition(), echo)
    result = await server.handle(rpc("tools/list", rid=chr(0) * 192))
    assert "result" in result and len(encode(result, server.limits)) <= 2500
    tiny = ModernToolsMCPServer(limits=ServerLimits(catalog_tools=1))
    tiny.register_tool(definition(), echo)
    with pytest.raises(ValueError):
        tiny.register_tool(definition("second"), echo)
    assert len(tiny.tools) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "key,value",
    [
        ("traceparent", None),
        ("traceparent", "bad-secret"),
        ("traceparent", "00-" + "0" * 32 + "-" + "1" * 16 + "-01"),
        ("traceparent", "ff-" + "1" * 32 + "-" + "1" * 16 + "-01"),
        ("tracestate", None),
        ("tracestate", "A=x"),
        ("tracestate", "a=x,a=y"),
        ("tracestate", "a="),
        ("tracestate", "a=x=y"),
        ("baggage", None),
        ("baggage", "missing-equals"),
        ("baggage", "x=bad%QQ"),
        ("baggage", "x=unicode-世界"),
        ("baggage", "x=unencoded space"),
    ],
)
async def test_reserved_trace_fields_malformed_rejected_without_handler(key, value):
    server = ModernToolsMCPServer()
    meta = {
        PREFIX + "protocolVersion": VERSION,
        PREFIX + "clientCapabilities": {},
        key: value,
    }
    assert (await server.handle(rpc(meta=meta)))["error"]["code"] == -32602


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "trace",
    [
        {"traceparent": "00-" + "1" * 32 + "-" + "2" * 16 + "-01"},
        {"traceparent": "01-" + "1" * 32 + "-" + "2" * 16 + "-01-future"},
        {"tracestate": "tenant@vendor=opaque, ,other=x"},
        {"tracestate": ""},
        {"baggage": "key=value;property;other=encoded%20space"},
        {"baggage": "key=x,key=y"},
        {"baggage": ""},
    ],
)
async def test_valid_trace_fields_never_forwarded_to_handler(trace):
    received = []

    async def handler(args):
        received.append(args)
        return ToolCallResult.text("done")

    server = ModernToolsMCPServer()
    server.register_tool(definition(), handler)
    meta = {
        PREFIX + "protocolVersion": VERSION,
        PREFIX + "clientCapabilities": {},
        **trace,
    }
    response = await server.handle(
        rpc("tools/call", params={"name": "echo"}, meta=meta)
    )
    assert "result" in response and received == [{}]
    assert all(key not in str(response) for key in trace)


@pytest.mark.asyncio
async def test_version_error_required_data_sdk_model():
    from mcp_types import UnsupportedProtocolVersionErrorData
    from pydantic import ValidationError

    server = ModernToolsMCPServer()
    version = "2026-08-01"
    response = await server.handle(
        rpc(
            meta={
                PREFIX + "protocolVersion": version,
                PREFIX + "clientCapabilities": {},
            }
        )
    )
    data = response["error"]["data"]
    parsed = UnsupportedProtocolVersionErrorData.model_validate(data)
    assert parsed.supported == [VERSION] and parsed.requested == version
    assert set(data) == {"supported", "requested"}
    discovery = (await server.handle(rpc()))["result"]
    assert discovery["supportedVersions"] == [VERSION] and "supported" not in discovery
    for malformed in (
        {"supportedVersions": [VERSION]},
        {"supported": None, "requested": version},
        {"supported": [VERSION], "requested": None},
        {"supported": [None], "requested": version},
        {"supported": [VERSION]},
        {"requested": version},
    ):
        with pytest.raises(ValidationError):
            UnsupportedProtocolVersionErrorData.model_validate(malformed)


@pytest.mark.asyncio
async def test_version_error_owner_privacy(caplog):
    from tests_mcp.server.test_server_security import Observer

    observer = Observer()
    server = ModernToolsMCPServer(telemetry=observer)
    version = "bounded-requested-version"
    meta = {
        PREFIX + "protocolVersion": version,
        PREFIX + "clientCapabilities": {},
        "example.org/token": "metadata-secret",
    }
    response = await server.handle(rpc(rid="own-id", meta=meta))
    assert (
        response["id"] == "own-id" and response["error"]["data"]["requested"] == version
    )
    assert version not in response["error"]["message"]
    assert "metadata-secret" not in str(response) and not observer.events
    assert version not in caplog.text
    other = await server.handle(rpc())
    assert version not in str(other)
    meta[PREFIX + "protocolVersion"] = "x" * 257
    assert (await server.handle(rpc(meta=meta)))["error"]["code"] == -32602


@pytest.mark.asyncio
@pytest.mark.parametrize("key", ["requestState", "inputResponses"])
@pytest.mark.parametrize("value", [None, "state", {}, [], True, 1])
async def test_interactive_state_fields_rejected(key, value):
    server = ModernToolsMCPServer()
    invoked = []

    async def handler(args):
        invoked.append(args)
        return ToolCallResult.text("done")

    server.register_tool(definition(), handler)
    response = await server.handle(
        rpc("tools/call", params={"name": "echo", key: value})
    )
    assert response["error"]["code"] == -32602 and not invoked
    assert "result" in await server.handle(rpc("tools/call", params={"name": "echo"}))
    assert invoked == [{}]


def test_inactive_error_variant_cannot_be_constructed():
    with pytest.raises(ValueError, match="Inactive"):
        ServerWireError(-32021)
    with pytest.raises(ValueError, match="requires requested"):
        ServerWireError(-32022)
    with pytest.raises(ValueError):
        ServerWireError(-32022, requested_version="x" * 257)
    with pytest.raises(ValueError):
        ServerWireError(-32603, requested_version="wrong-role")


@pytest.mark.parametrize("level", ["result", "text", "tool"])
@pytest.mark.parametrize(
    "key,value",
    [
        ("traceparent", None),
        ("traceparent", "bad-secret"),
        ("tracestate", "A=x"),
        ("baggage", "x=bad%QQ"),
    ],
)
def test_emitted_meta_reserved_trace_variants(level, key, value):
    meta = {key: value}
    with pytest.raises((ValueError, ServerWireError)):
        if level == "tool":
            RegisteredTool.from_definition(definition(_meta=meta), echo)
        elif level == "text":
            ToolCallResult.from_value(
                {"content": [{"type": "text", "text": "done", "_meta": meta}]}
            )
        else:
            ToolCallResult.from_value({"content": [], "_meta": meta})


@pytest.mark.asyncio
async def test_result_meta_preserved_with_fixed_server_identity():
    async def handler(args):
        return ToolCallResult.from_value(
            {
                "content": [
                    {
                        "type": "text",
                        "text": "done",
                        "_meta": {"example.org/block": "block"},
                    }
                ],
                "_meta": {
                    "example.org/annotation": "trusted",
                    PREFIX + "serverInfo": {"name": "override-attempt", "version": "1"},
                },
            }
        )

    server = ModernToolsMCPServer()
    server.register_tool(definition(), handler)
    result = (await server.handle(rpc("tools/call", params={"name": "echo"})))["result"]
    assert result["_meta"]["example.org/annotation"] == "trusted"
    assert result["_meta"][PREFIX + "serverInfo"]["name"] == "FridayModernTools"
    assert result["content"][0]["_meta"] == {"example.org/block": "block"}


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [b"NaN", b"Infinity", b"-Infinity", b"1e999"])
async def test_nonfinite_json_tokens_parse_error_zero_handler(value):
    raw = rpc(
        "tools/call", params={"name": "echo", "arguments": {"value": "PLACEHOLDER"}}
    ).replace(b'"PLACEHOLDER"', value)
    response = await ModernToolsMCPServer().handle(raw)
    assert response["error"]["code"] == -32700


@pytest.mark.asyncio
async def test_surrogate_object_key_rejected_before_handler():
    received = []

    async def handler(args):
        received.append(args)
        return ToolCallResult.text("done")

    server = ModernToolsMCPServer()
    server.register_tool(definition(), handler)
    raw = rpc(
        "tools/call", params={"name": "echo", "arguments": {"key": "value"}}
    ).replace(b'"key"', b'"\\ud800"')
    assert (await server.handle(raw))["error"]["code"] == -32602
    assert not received


@pytest.mark.asyncio
async def test_every_emitted_error_variant_pinned_fields():
    from mcp_types.jsonrpc import ErrorData, JSONRPCError

    server = ModernToolsMCPServer()

    async def malformed(args):
        return ToolCallResult(b'{"content":null}')

    server.register_tool(definition(), malformed)
    inputs = [
        (b"{", -32700),
        (b"{}", -32600),
        (rpc("unknown"), -32601),
        (
            rpc(
                meta={
                    PREFIX + "protocolVersion": VERSION,
                    PREFIX + "clientCapabilities": None,
                }
            ),
            -32602,
        ),
        (rpc("tools/call", params={"name": "echo"}), -32603),
    ]
    for raw, code in inputs:
        response = await server.handle(raw)
        # The dated schema permits no-id parse/invalid errors. The SDK generic
        # JSONRPCError wrapper still requires id, so validate the common body
        # and separately check the dated envelope rather than fabricating id.
        error = ErrorData.model_validate(response["error"])
        assert error.code == code and set(response["error"]) == {"code", "message"}
        if "id" in response:
            assert JSONRPCError.model_validate(response).error.code == code
        else:
            assert set(response) == {"jsonrpc", "error"}
    await server.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "key,value",
    [
        ("progressToken", None),
        ("progressToken", True),
        ("progressToken", {}),
        (PREFIX + "logLevel", None),
        (PREFIX + "logLevel", "invalid"),
        (PREFIX + "clientCapabilities", {"sampling": {"context": None}}),
        (PREFIX + "clientCapabilities", {"sampling": {"tools": None}}),
        (PREFIX + "clientCapabilities", {"elicitation": {"form": None}}),
        (PREFIX + "clientCapabilities", {"elicitation": {"url": None}}),
        (PREFIX + "clientCapabilities", {"extensions": {"unprefixed": {}}}),
        (PREFIX + "clientCapabilities", {"extensions": {"example.org/test": None}}),
    ],
)
async def test_known_meta_dependent_field_null_malformed(key, value):
    meta = {
        PREFIX + "protocolVersion": VERSION,
        PREFIX + "clientCapabilities": {},
        key: value,
    }
    assert (await ModernToolsMCPServer().handle(rpc(meta=meta)))["error"][
        "code"
    ] == -32602


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "level",
    ["debug", "info", "notice", "warning", "error", "critical", "alert", "emergency"],
)
async def test_log_level_enum_valid_but_no_logging_role(level):
    meta = {
        PREFIX + "protocolVersion": VERSION,
        PREFIX + "clientCapabilities": {},
        PREFIX + "logLevel": level,
    }
    response = await ModernToolsMCPServer().handle(rpc(meta=meta))
    assert response["result"]["capabilities"] == {"tools": {}}


def test_text_metadata_omitted_null_and_invalid_key():
    assert "_meta" not in ToolCallResult.text("done").value()["content"][0]
    for meta in (None, [], {"invalid/key/format": "x"}, {PREFIX + "serverInfo": None}):
        with pytest.raises(ServerWireError):
            ToolCallResult.from_value({"content": [], "_meta": meta})


@pytest.mark.parametrize("field", ["jsonrpc", "method", "params"])
@pytest.mark.asyncio
async def test_request_envelope_mandatory_field_omission_or_null(field):
    for null in (True, False):
        value = json.loads(rpc())
        if null:
            value[field] = None
        else:
            value.pop(field)
        response = await ModernToolsMCPServer().handle(json.dumps(value).encode())
        assert response["error"]["code"] == (-32602 if field == "params" else -32600)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "body",
    [
        {"jsonrpc": "2.0", "id": "known"},
        {"jsonrpc": "wrong", "method": "server/discover", "id": "known"},
        {"jsonrpc": "2.0", "method": None, "id": "known"},
    ],
)
async def test_malformed_request_known_id_echoes_only_own_error(body):
    response = await ModernToolsMCPServer().handle(json.dumps(body).encode())
    assert response["error"]["code"] == -32600 and response["id"] == "known"


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"requestId": None},
        {"requestId": True},
        {"requestId": 1.5},
        {"requestId": 1, "reason": None},
        {"requestId": 1, "_meta": {PREFIX + "subscriptionId": None}},
    ],
)
def test_notification_dependent_params_exact_invalid_params(params):
    raw = json.dumps(
        {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": params}
    ).encode()
    with pytest.raises(ServerWireError) as error:
        ServerRequest.parse(raw, ServerLimits())
    assert error.value.code == -32602
