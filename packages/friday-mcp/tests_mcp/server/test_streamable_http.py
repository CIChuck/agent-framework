"""Independent raw HTTP header oracle, ASGI framing and tool side-effect counters."""

import base64
import json

import httpx
import pytest

from friday_mcp.server import HTTPServerPolicy, StreamableHTTPMCPServer, ToolCallResult
from friday_mcp.server.protocol import PREFIX, VERSION
from tests_mcp.server.test_modern_protocol import definition, rpc


def headers(method="tools/call", *, name="echo"):
    result = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": VERSION,
        "Mcp-Method": method,
    }
    if name is not None:
        result["Mcp-Name"] = name
    return result


def make_server(mode="json", *, policy=None, schema=None, limits=None):
    calls = []

    async def handler(args):
        calls.append(args)
        return ToolCallResult.structured(args)

    options = {"policy": policy or HTTPServerPolicy(port=8000), "response_mode": mode}
    if limits is not None:
        options["limits"] = limits
    server = StreamableHTTPMCPServer(**options)
    server.register_tool(definition(inputSchema=schema or {"type": "object"}), handler)
    return server, calls


def http_client(server):
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=server.create_app()),
        base_url="http://127.0.0.1:8000",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["json", "sse"])
async def test_single_post_stateless_json_and_sse(mode):
    server, calls = make_server(mode)
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers=headers(),
            content=rpc("tools/call", params={"name": "echo", "arguments": {"x": 1}}),
        )
        assert response.status_code == 200
        data = (
            response.json()
            if mode == "json"
            else json.loads(response.text.split("data: ", 1)[1])
        )
        assert data["result"]["structuredContent"] == {"x": 1}
        assert "mcp-session-id" not in response.headers
        if mode == "sse":
            assert response.headers["x-accel-buffering"] == "no"
            assert response.text.count("data: ") == 1
        assert len(calls) == 1
        for method in ("GET", "DELETE"):
            rejected = await client.request(method, "/mcp")
            assert rejected.status_code == 405
        assert (
            await client.post("/mcp/", headers=headers(), content=rpc())
        ).status_code == 404
        assert (
            await client.post("/message", headers=headers(), content=rpc())
        ).status_code == 404
    await server.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["unknown", "initialize", "subscriptions/listen"])
async def test_http_unsupported_rpc_exact_404(method):
    server, calls = make_server()
    async with http_client(server) as client:
        response = await client.post(
            "/mcp", headers=headers(method, name=None), content=rpc(method)
        )
        assert (
            response.status_code == 404 and response.json()["error"]["code"] == -32601
        )
    assert not calls


@pytest.mark.asyncio
async def test_version_header_vs_body_and_unsupported_version_distinct():
    server, calls = make_server()
    async with http_client(server) as client:
        h = headers("server/discover", name=None)
        h["MCP-Protocol-Version"] = "2025-11-25"
        response = await client.post("/mcp", headers=h, content=rpc())
        assert (
            response.status_code == 400 and response.json()["error"]["code"] == -32020
        )
        response = await client.post(
            "/mcp",
            headers=h,
            content=rpc(
                meta={
                    PREFIX + "protocolVersion": "2025-11-25",
                    PREFIX + "clientCapabilities": {},
                }
            ),
        )
        assert (
            response.status_code == 400 and response.json()["error"]["code"] == -32022
        )
    assert not calls


@pytest.mark.asyncio
@pytest.mark.parametrize("key", ["Mcp-Method", "MCP-Protocol-Version", "Mcp-Name"])
@pytest.mark.parametrize("value", [None, "wrong", "TOOLS/CALL"])
async def test_missing_or_mismatched_required_headers_zero_calls(key, value):
    server, calls = make_server()
    h = headers()
    if value is None:
        del h[key]
    else:
        h[key] = value
    async with http_client(server) as client:
        response = await client.post(
            "/mcp", headers=h, content=rpc("tools/call", params={"name": "echo"})
        )
        assert (
            response.status_code == 400 and response.json()["error"]["code"] == -32020
        )
    assert not calls


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value",
    ["Hello, 世界", " padded ", "line1\nline2", "=?base64?literal?=", "", "plain"],
)
async def test_custom_nested_unicode_sentinel_uses_independent_base64_oracle(value):
    schema = {
        "type": "object",
        "properties": {
            "nested": {
                "type": "object",
                "properties": {"text": {"type": "string", "x-mcp-header": "Text"}},
            }
        },
    }
    server, calls = make_server(schema=schema)
    h = headers()
    h["mCp-PaRaM-tExT"] = "=?base64?" + base64.b64encode(value.encode()).decode() + "?="
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers=h,
            content=rpc(
                "tools/call",
                params={"name": "echo", "arguments": {"nested": {"text": value}}},
            ),
        )
        assert response.status_code == 200 and len(calls) == 1
        h["mCp-PaRaM-tExT"] = "wrong"
        response = await client.post(
            "/mcp",
            headers=h,
            content=rpc(
                "tools/call",
                params={"name": "echo", "arguments": {"nested": {"text": value}}},
            ),
        )
        assert (
            response.status_code == 400
            and response.json()["error"]["code"] == -32020
            and len(calls) == 1
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value,header,success",
    [
        (42, "42.0", True),
        (-7, "-7", True),
        (2**53 - 1, str(2**53 - 1), True),
        (2**53, str(2**53), False),
        (True, "1", False),
        (1.5, "1.5", False),
        (1, "nan", False),
        (1, "2", False),
    ],
)
async def test_custom_integer_safe_numeric_equality(value, header, success):
    server, calls = make_server(
        schema={
            "type": "object",
            "properties": {"x": {"type": "integer", "x-mcp-header": "X"}},
        }
    )
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers={**headers(), "Mcp-Param-X": header},
            content=rpc(
                "tools/call", params={"name": "echo", "arguments": {"x": value}}
            ),
        )
        assert response.status_code == (200 if success else 400)
    assert len(calls) == int(success)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "args", [{}, {"nested": {}}, {"nested": None}, {"nested": {"text": None}}]
)
async def test_null_absent_binding_header_omitted_and_unexpected_rejected(args):
    # Schema-invalid null arguments fail after header validation.
    schema = {
        "type": "object",
        "properties": {
            "nested": {
                "type": ["object", "null"],
                "properties": {"text": {"type": "string", "x-mcp-header": "Text"}},
            }
        },
    }
    server, calls = make_server(schema=schema)
    async with http_client(server) as client:
        raw = rpc("tools/call", params={"name": "echo", "arguments": args})
        response = await client.post("/mcp", headers=headers(), content=raw)
        assert response.status_code == (
            400 if args == {"nested": {"text": None}} else 200
        )
        response = await client.post(
            "/mcp", headers={**headers(), "Mcp-Param-Text": "extra"}, content=raw
        )
        assert (
            response.status_code == 400 and response.json()["error"]["code"] == -32020
        )
    assert len(calls) == (0 if args == {"nested": {"text": None}} else 1)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value",
    [
        "=?base64?!!!!?=",
        "=?base64?YQ?=",
        "=?base64?/w==?=",
        "=?base64?YR==?=",
        " wrong ",
    ],
)
async def test_bad_base64_or_unencoded_whitespace_zero_calls(value):
    server, calls = make_server()
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers={**headers(), "Mcp-Name": value},
            content=rpc("tools/call", params={"name": "echo"}),
        )
        assert (
            response.status_code == 400 and response.json()["error"]["code"] == -32020
        )
    assert not calls


@pytest.mark.asyncio
async def test_unicode_tool_name_and_marker_safe_decoding():
    for name in ("工具", "=?base64?literal?="):
        server = StreamableHTTPMCPServer()
        calls = []

        async def handler(args, calls=calls):
            calls.append(1)
            return ToolCallResult.text("ok")

        server.register_tool(definition(name), handler)
        h = headers(name="=?base64?" + base64.b64encode(name.encode()).decode() + "?=")
        async with http_client(server) as client:
            assert (
                await client.post(
                    "/mcp", headers=h, content=rpc("tools/call", params={"name": name})
                )
            ).status_code == 200
        assert calls == [1]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content_type,accept",
    [
        ("text/plain", "application/json, text/event-stream"),
        ("application/json", "application/json"),
        ("application/json", "text/event-stream"),
        ("application/json", "*/*"),
    ],
)
async def test_content_negotiation_before_dispatch(content_type, accept):
    server, calls = make_server()
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers={**headers(), "Content-Type": content_type, "Accept": accept},
            content=rpc("tools/call", params={"name": "echo"}),
        )
        assert response.status_code == 400
    assert not calls


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method", ["notifications/cancelled", "notifications/initialized", "custom/notify"]
)
async def test_http_notifications_unsupported_no_id_no_handler(method):
    server, calls = make_server()
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers=headers(),
            content=json.dumps(
                {"jsonrpc": "2.0", "method": method, "params": {"requestId": 1}}
            ),
        )
        assert response.status_code == 404 and "id" not in response.json()
    assert not calls


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content_type,accept",
    [
        ("application/json; garbage", "application/json,text/event-stream"),
        ("application/json; charset=latin1", "application/json,text/event-stream"),
        (
            "application/json; charset=utf-8; charset=utf-8",
            "application/json,text/event-stream",
        ),
        ("application/json", "application/json;q=0,text/event-stream"),
        ("application/json", "application/json,text/event-stream;q=0"),
        ("application/json", "application/json;q=2,text/event-stream"),
        ("application/json", "application/json;,text/event-stream"),
        ("application/json", "application/json;q=0.0001,text/event-stream"),
    ],
)
async def test_media_header_parameter_and_quality_failures_zero_handler(
    content_type, accept
):
    server, calls = make_server()
    async with http_client(server) as client:
        result = await client.post(
            "/mcp",
            headers={**headers(), "Content-Type": content_type, "Accept": accept},
            content=rpc("tools/call", params={"name": "echo"}),
        )
        assert result.status_code == 400 and result.json()["error"]["code"] == -32600
    assert not calls


@pytest.mark.asyncio
async def test_media_header_valid_parameters_and_unsupported_error_data():
    from mcp_types import UnsupportedProtocolVersionErrorData

    server, calls = make_server()
    async with http_client(server) as client:
        good = {
            **headers(),
            "Content-Type": 'Application/JSON; charset="UTF-8"',
            "Accept": "application/json;q=0.5,text/event-stream;q=1.000",
        }
        assert (
            await client.post(
                "/mcp", headers=good, content=rpc("tools/call", params={"name": "echo"})
            )
        ).status_code == 200
        version = "2026-08-01"
        bad = {**headers("server/discover", name=None), "MCP-Protocol-Version": version}
        response = await client.post(
            "/mcp",
            headers=bad,
            content=rpc(
                meta={
                    PREFIX + "protocolVersion": version,
                    PREFIX + "clientCapabilities": {},
                }
            ),
        )
        assert response.status_code == 400
        parsed = UnsupportedProtocolVersionErrorData.model_validate(
            response.json()["error"]["data"]
        )
        assert parsed.supported == [VERSION] and parsed.requested == version
        assert len(calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "header",
    [
        "9007199254740991.1",
        "9007199254740990.9",
        "9007199254740991_0",
        "NaN",
        "Infinity",
    ],
)
async def test_large_integer_header_does_not_round_mismatch_into_match(header):
    server, calls = make_server(
        schema={
            "type": "object",
            "properties": {"value": {"type": "integer", "x-mcp-header": "Value"}},
        }
    )
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers={**headers(), "Mcp-Param-Value": header},
            content=rpc(
                "tools/call", params={"name": "echo", "arguments": {"value": 2**53 - 1}}
            ),
        )
        assert (
            response.status_code == 400 and response.json()["error"]["code"] == -32020
        )
    assert not calls


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["Mcp-Method", "Mcp-Name", "MCP-Protocol-Version"])
async def test_duplicate_standard_metadata_header_exact_header_mismatch(name):
    server, calls = make_server()
    values = list(headers().items()) + [(name.lower(), "conflict")]
    async with http_client(server) as client:
        response = await client.post(
            "/mcp", headers=values, content=rpc("tools/call", params={"name": "echo"})
        )
        assert (
            response.status_code == 400 and response.json()["error"]["code"] == -32020
        )
        assert "id" not in response.json()  # Header rejection preceded body parsing.
    assert not calls


@pytest.mark.asyncio
@pytest.mark.parametrize("mode,status", [("json", 200), ("sse", 500)])
async def test_actual_sse_framing_budget_and_single_invocation(mode, status):
    from friday_mcp.server import ServerLimits

    limit = 2048
    server, _ = make_server(
        mode, limits=ServerLimits(result_bytes=limit, identity_bytes=64)
    )
    skeleton = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "resultType": "complete",
            "content": [{"type": "text", "text": ""}],
            "isError": False,
            "_meta": {
                PREFIX + "serverInfo": {"name": "FridayModernTools", "version": "1.0.0"}
            },
        },
    }
    count = (
        limit
        - 1
        - len(json.dumps(skeleton, separators=(",", ":"), sort_keys=True).encode())
    )
    called = []

    async def handler(args):
        called.append(1)
        return ToolCallResult.text("x" * count)

    server.replace_tools([])
    server.register_tool(definition(), handler)
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers=headers(),
            content=rpc("tools/call", params={"name": "echo"}),
        )
        assert response.status_code == status and len(response.content) <= limit
        if mode == "json":
            assert len(response.content) == limit - 1
        else:
            assert response.json()["error"]["code"] == -32603
    assert called == [1]


async def raw_boundary_response(server, pairs):
    consumed, messages = [], []

    async def receive():
        consumed.append(1)
        return {"type": "http.request", "body": rpc(), "more_body": False}

    async def send(message):
        messages.append(message)

    await server(
        {
            "type": "http",
            "path": "/mcp",
            "method": "POST",
            "scheme": "http",
            "query_string": b"",
            "headers": [(b"host", b"127.0.0.1:8000"), *pairs],
        },
        receive,
        send,
    )
    return messages[0]["status"], json.loads(messages[1]["body"]), consumed


@pytest.mark.asyncio
@pytest.mark.parametrize("bad", [b"x\rprivate", b"x\nprivate", b"x\0private"])
async def test_custom_header_invalid_bytes_exact_mismatch_before_body(bad):
    server, calls = make_server(
        schema={
            "type": "object",
            "properties": {"x": {"type": "string", "x-mcp-header": "X"}},
        }
    )
    status, body, consumed = await raw_boundary_response(
        server, [(b"mCp-PaRaM-X", bad)]
    )
    assert status == 400 and body == {
        "jsonrpc": "2.0",
        "error": {"code": -32020, "message": "Header mismatch"},
    }
    assert not calls and not consumed
    await server.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bad", [b"\x7f", b"\x80", b"\x01", b" padded ", b"=?base64?!!!!?="]
)
async def test_recognized_custom_header_invalid_encoding_zero_handler(bad):
    server, calls = make_server(
        schema={
            "type": "object",
            "properties": {"x": {"type": "string", "x-mcp-header": "X"}},
        }
    )
    h = [(k.encode(), v.encode()) for k, v in headers().items()]
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers=[*h, (b"Mcp-Param-X", bad)],
            content=rpc("tools/call", params={"name": "echo", "arguments": {"x": "x"}}),
        )
    assert response.status_code == 400 and response.json() == {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32020, "message": "Header mismatch"},
    }
    assert not calls
    await server.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("second", [b"same", b"conflicting-private"])
async def test_custom_header_duplicate_exact_mismatch_before_body(second):
    server, calls = make_server(
        schema={
            "type": "object",
            "properties": {"x": {"type": "string", "x-mcp-header": "X"}},
        }
    )
    status, body, consumed = await raw_boundary_response(
        server, [(b"Mcp-Param-X", b"same"), (b"mCp-PaRaM-x", second)]
    )
    assert status == 400 and body == {
        "jsonrpc": "2.0",
        "error": {"code": -32020, "message": "Header mismatch"},
    }
    assert not calls and not consumed
    await server.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name,bad,status",
    [
        (b"host", b"private-invalid", 400),
        (b"origin", b"https://private.invalid", 403),
        (b"authorization", b"Bearer private-credential", 401),
    ],
)
async def test_access_failures_keep_exact_status_and_private_body(name, bad, status):
    server, calls = make_server()
    pairs = [(name, bad)]
    actual, body, consumed = await raw_boundary_response(server, pairs)
    assert actual == status and body == {
        "jsonrpc": "2.0",
        "error": {"code": -32600, "message": "Invalid request"},
    }
    assert not calls and not consumed and "private" not in json.dumps(body)
    await server.stop()


@pytest.mark.asyncio
async def test_custom_header_interior_tab_and_unknown_valid_header_preserved():
    server, calls = make_server(
        schema={
            "type": "object",
            "properties": {"x": {"type": "string", "x-mcp-header": "X"}},
        }
    )
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers={**headers(), "Mcp-Param-X": "a\tb", "Mcp-Param-Unknown": "unused"},
            content=rpc(
                "tools/call", params={"name": "echo", "arguments": {"x": "a\tb"}}
            ),
        )
    assert response.status_code == 200 and calls == [{"x": "a\tb"}]
    await server.stop()


async def standard_header_case(field, value, *, body_value=None):
    import asyncio

    server, calls = make_server()
    method = value if field == "mcp-method" else "tools/call"
    version = value if field == "mcp-protocol-version" else VERSION
    if body_value is not None:
        if field == "mcp-method":
            method = body_value
        else:
            version = body_value
    body = rpc(
        method,
        params={"name": "echo"},
        meta={PREFIX + "protocolVersion": version, PREFIX + "clientCapabilities": {}},
    )
    pairs = [(k.lower().encode(), v.encode()) for k, v in headers().items()]
    pairs = [
        (k, value.encode("latin-1") if k == field.encode() else v) for k, v in pairs
    ]
    queue, consumed, messages = asyncio.Queue(), [], []
    await queue.put({"type": "http.request", "body": body, "more_body": False})

    async def receive():
        message = await queue.get()
        consumed.append(message)
        return message

    async def send(message):
        messages.append(message)

    try:
        await server(
            {
                "type": "http",
                "path": "/mcp",
                "method": "POST",
                "scheme": "http",
                "query_string": b"",
                "headers": [(b"host", b"127.0.0.1:8000"), *pairs],
            },
            receive,
            send,
        )
        return messages[0]["status"], json.loads(messages[1]["body"]), calls, consumed
    finally:
        await server.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["mcp-method", "mcp-protocol-version"])
@pytest.mark.parametrize("byte", [*range(0, 9), *range(10, 32), *range(127, 256)])
async def test_plain_standard_header_invalid_byte_sweep_exact_mismatch(field, byte):
    value = "synthetic-private-" + chr(byte) + "-sentinel"
    status, body, calls, consumed = await standard_header_case(field, value)
    assert status == 400 and body == {
        "jsonrpc": "2.0",
        "error": {"code": -32020, "message": "Header mismatch"},
    }
    assert not calls and not consumed and "sentinel" not in json.dumps(body)


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["mcp-method", "mcp-protocol-version"])
@pytest.mark.parametrize("byte", [9, *range(32, 127)])
async def test_plain_standard_header_valid_byte_sweep_keeps_routing_category(
    field, byte
):
    value = "unknown-plain-" + chr(byte) + "-value"
    status, body, calls, consumed = await standard_header_case(field, value)
    if field == "mcp-method":
        assert status == 404 and body == {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32601, "message": "Method not found"},
        }
    else:
        assert status == 400 and body == {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32022,
                "message": "Unsupported protocol version",
                "data": {"supported": [VERSION], "requested": value},
            },
        }
    assert not calls and len(consumed) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["mcp-method", "mcp-protocol-version"])
@pytest.mark.parametrize("suffix", ["世界", "é"])
async def test_plain_standard_header_raw_utf8_matching_body_exact_mismatch(
    field, suffix
):
    server, calls = make_server()
    method = "tools/call" + (suffix if field == "mcp-method" else "")
    version = VERSION + (suffix if field == "mcp-protocol-version" else "")
    pairs = [(k.lower().encode(), v.encode()) for k, v in headers(method).items()]
    pairs = [
        (k, version.encode() if k == b"mcp-protocol-version" else v) for k, v in pairs
    ]
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers=pairs,
            content=rpc(
                method,
                params={"name": "echo"},
                meta={
                    PREFIX + "protocolVersion": version,
                    PREFIX + "clientCapabilities": {},
                },
            ),
        )
    assert response.status_code == 400 and response.json() == {
        "jsonrpc": "2.0",
        "error": {"code": -32020, "message": "Header mismatch"},
    }
    assert not calls and suffix not in response.text
    await server.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field,actual", [("mcp-method", "tools/call"), ("mcp-protocol-version", VERSION)]
)
@pytest.mark.parametrize("variation", ["upper", "space", "tab", "base64"])
async def test_plain_standard_header_equality_does_not_normalize_or_decode(
    field, actual, variation
):
    value = {
        "upper": actual.upper() if field == "mcp-method" else "2026-07-2B",
        "space": " " + actual + " ",
        "tab": "\t" + actual + "\t",
        "base64": "=?base64?" + base64.b64encode(actual.encode()).decode() + "?=",
    }[variation]
    status, body, calls, consumed = await standard_header_case(
        field, value, body_value=actual
    )
    assert status == 400 and body == {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32020, "message": "Header mismatch"},
    }
    assert not calls and len(consumed) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["json", "sse"])
async def test_real_tls_raw_utf8_standard_headers_exact_mismatch(tmp_path, mode):
    from tests_mcp.server.test_server_interop import tls_friday

    observations = []
    async with (
        tls_friday(tmp_path, mode) as (url, context, counter, process),
        httpx.AsyncClient(
            verify=context, trust_env=False, follow_redirects=False
        ) as client,
    ):
        for field in ("mcp-method", "mcp-protocol-version"):
            for suffix in ("世界", "é"):
                method = "tools/call" + (suffix if field == "mcp-method" else "")
                version = VERSION + (suffix if field == "mcp-protocol-version" else "")
                pairs = [
                    (k.lower().encode(), v.encode()) for k, v in headers(method).items()
                ]
                pairs = [
                    (k, version.encode() if k == b"mcp-protocol-version" else v)
                    for k, v in pairs
                ]
                response = await client.post(
                    url,
                    headers=pairs,
                    content=rpc(
                        method,
                        params={"name": "echo"},
                        meta={
                            PREFIX + "protocolVersion": version,
                            PREFIX + "clientCapabilities": {},
                        },
                    ),
                )
                assert response.status_code == 400 and response.json() == {
                    "jsonrpc": "2.0",
                    "error": {"code": -32020, "message": "Header mismatch"},
                }
                observations.append((field, suffix, response.status_code))
    rows = [json.loads(row) for row in counter.read_text().splitlines()]
    assert sum(row.get("event") == "handler_start" for row in rows) == 0
    assert rows[-1] == {"event": "server_stopped", "active": 0}
    assert process.returncode == 0 and len(observations) == 4
