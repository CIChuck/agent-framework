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
