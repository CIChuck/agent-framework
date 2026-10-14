"""Controlled public network backend: real httpcore parsing without external I/O."""

import asyncio
import json
import logging
import ssl
from copy import deepcopy
from dataclasses import dataclass, field

import httpcore
import pytest

from friday_mcp.client.base import MCPError, MCPToolExecutionError
from friday_mcp.client.http import StreamableHTTPMCPClient
from friday_mcp.client.http_protocol import HTTP_COMPAT_VERSION, HTTPLimits
from friday_mcp.client.protocol import MODERN_VERSION, ProtocolFailure, ProtocolLimits


@dataclass
class Reply:
    body: bytes = b""
    status: int = 200
    headers: list[tuple[str, str]] = field(default_factory=list)
    kind: str = "application/json"
    stall: asyncio.Event | None = None
    resistant: bool = False
    close_release: asyncio.Event | None = None
    width: int = 16384
    advertised_extra: int = 0


class Resolver:
    def __init__(self, answers=("93.184.216.34",)):
        self.answers = answers
        self.calls = 0
        self.stall = None

    async def resolve(self, host, port):
        self.calls += 1
        if self.stall is not None:
            await self.stall.wait()
        return self.answers


class WireStream(httpcore.AsyncNetworkStream):
    def __init__(self, connector):
        self.connector = connector
        self.outgoing = bytearray()
        self.reply = None
        self.response_head = b""
        self.position = 0
        self.closed = False
        self.ready = asyncio.Event()
        self.read_started = asyncio.Event()

    async def write(self, buffer, timeout=None):
        self.outgoing.extend(buffer)
        if self.reply is None and b"\r\n\r\n" in self.outgoing:
            head, body = bytes(self.outgoing).split(b"\r\n\r\n", 1)
            lines = head.split(b"\r\n")
            headers = {
                key.lower(): value
                for key, value in (line.split(b": ", 1) for line in lines[1:])
            }
            if len(body) >= int(headers.get(b"content-length", b"0")):
                request = json.loads(body) if body else {}
                self.reply = self.connector.dispatch(
                    lines[0].split()[0], headers, request
                )
                r = self.reply
                fields = [
                    ("Content-Type", r.kind),
                    ("Content-Length", str(len(r.body) + r.advertised_extra)),
                ] + r.headers
                self.response_head = (
                    f"HTTP/1.1 {r.status} Synthetic\r\n".encode()
                    + b"".join(f"{key}: {value}\r\n".encode() for key, value in fields)
                    + b"\r\n"
                )
                self.ready.set()

    async def read(self, max_bytes, timeout=None):
        await self.ready.wait()
        r = self.reply
        self.read_started.set()
        if self.position < len(self.response_head):
            chunk = self.response_head[self.position : self.position + max_bytes]
            self.position += len(chunk)
            return chunk
        if r.stall is not None:
            try:
                await r.stall.wait()
            except asyncio.CancelledError:
                if not r.resistant:
                    raise
                await r.stall.wait()
        body_pos = self.position - len(self.response_head)
        chunk = r.body[body_pos : body_pos + min(max_bytes, r.width)]
        self.position += len(chunk)
        return chunk

    async def aclose(self):
        if self.reply and self.reply.close_release:
            try:
                await self.reply.close_release.wait()
            except asyncio.CancelledError:
                await self.reply.close_release.wait()
        self.closed = True

    async def start_tls(self, ssl_context, server_hostname=None, timeout=None):
        self.connector.tls.append(
            (ssl_context.check_hostname, ssl_context.verify_mode, server_hostname)
        )
        return self

    def get_extra_info(self, info):
        return None


class Peer(httpcore.AsyncNetworkBackend):
    def __init__(self, version=MODERN_VERSION):
        self.version = version
        self.streams = []
        self.connections = []
        self.tls = []
        self.requests = []
        self.hook = None
        self.sessions = 0
        self.expire_once = False
        self.tools = [
            {
                "name": "echo",
                "inputSchema": {
                    "type": "object",
                    "properties": {"text": {"type": "string", "x-mcp-header": "Text"}},
                },
            }
        ]

    async def connect_tcp(
        self, host, port, timeout=None, local_address=None, socket_options=None
    ):
        self.connections.append((host, port))
        stream = WireStream(self)
        self.streams.append(stream)
        return stream

    def rpc(self, request, result=None, error=None, **options):
        data = {"jsonrpc": "2.0", "id": request["id"]}
        if error is not None:
            data["error"] = error
        else:
            if self.version == MODERN_VERSION:
                result = {"resultType": "complete", **result}
            data["result"] = result
        return Reply(json.dumps(data, ensure_ascii=False).encode(), **options)

    def dispatch(self, verb, headers, request):
        self.requests.append((verb, headers, request))
        if self.hook is not None:
            reply = self.hook(verb, headers, request)
            if reply is not None:
                return reply
        if verb == b"DELETE":
            return Reply(status=405)
        method = request.get("method")
        if method == "initialize":
            self.sessions += 1
            return self.rpc(
                request,
                {
                    "protocolVersion": self.version,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "fixture", "version": "1"},
                },
                headers=[("MCP-Session-Id", f"session-{self.sessions}")],
            )
        if "id" not in request:
            return Reply(status=202)
        if method == "server/discover":
            return self.rpc(
                request,
                {
                    "supportedVersions": [MODERN_VERSION],
                    "capabilities": {"tools": {}},
                    "ttlMs": 0,
                    "cacheScope": "private",
                },
            )
        if method == "tools/list":
            return self.rpc(
                request, {"tools": self.tools, "ttlMs": 0, "cacheScope": "private"}
            )
        if method == "tools/call":
            if self.expire_once:
                self.expire_once = False
                return Reply(status=404)
            return self.rpc(
                request,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": request["params"]["arguments"].get("text", "ok"),
                        }
                    ]
                },
            )
        return self.rpc(
            request, error={"code": -32601, "message": "untrusted secret"}, status=404
        )

    def methods(self):
        return [request.get("method", "DELETE") for _, _, request in self.requests]


def make_client(peer=None, resolver=None, **kwargs):
    peer = peer or Peer()
    resolver = resolver or Resolver()
    client = StreamableHTTPMCPClient(
        "https://example.test/mcp",
        protocol_version=peer.version,
        connector=peer,
        resolver=resolver,
        **kwargs,
    )
    return client, peer, resolver


async def ready_client(**kwargs):
    client, peer, resolver = make_client(**kwargs)
    await client.connect()
    await client.list_tools()
    return client, peer, resolver


@pytest.mark.asyncio
@pytest.mark.parametrize("version", [MODERN_VERSION, HTTP_COMPAT_VERSION])
async def test_profiles_and_exact_wire_headers_tls_and_borrowed_connector(version):
    client, peer, resolver = await ready_client(
        peer=Peer(version), bearer_token="synthetic-secret"
    )
    try:
        assert await client.call_tool("echo", {"text": "雪"}) == "雪"
        verb, headers, request = peer.requests[-1]
        assert verb == b"POST"
        assert headers[b"authorization"] == b"Bearer synthetic-secret"
        assert headers[b"mcp-protocol-version"] == version.encode()
        assert (
            b"application/json" in headers[b"accept"]
            and b"text/event-stream" in headers[b"accept"]
        )
        if version == MODERN_VERSION:
            assert headers[b"mcp-name"] == b"echo"
            assert headers[b"mcp-param-text"] == b"=?base64?6Zuq?="
            assert (
                request["params"]["_meta"]["io.modelcontextprotocol/protocolVersion"]
                == MODERN_VERSION
            )
            assert (
                request["params"]["_meta"]["io.modelcontextprotocol/clientCapabilities"]
                == {}
            )
            assert "initialize" not in peer.methods()
        else:
            assert headers[b"mcp-session-id"] == b"session-1"
            assert b"mcp-name" not in headers and "_meta" not in request["params"]
            assert peer.methods()[:2] == ["initialize", "notifications/initialized"]
        assert all(address == ("93.184.216.34", 443) for address in peer.connections)
        assert all(
            values == (True, ssl.CERT_REQUIRED, "example.test") for values in peer.tls
        )
        assert resolver.calls == len(peer.connections)
    finally:
        await client.disconnect()
    assert all(stream.closed for stream in peer.streams)
    assert client.outstanding_http_owners == 0 and client._pool is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "answers",
    [("127.0.0.1",), ("169.254.169.254",), ("::1",), ("93.184.216.34", "10.0.0.1"), ()],
)
async def test_connect_boundary_rejects_private_mixed_empty_dns_before_connector(
    answers,
):
    client, peer, _ = make_client(resolver=Resolver(answers))
    with pytest.raises(ProtocolFailure):
        await client.connect()
    assert not peer.connections and not peer.requests and client._pool is None


@pytest.mark.asyncio
async def test_each_new_connection_revalidates_changed_dns_no_rebinding():
    client, peer, resolver = await ready_client()
    resolver.answers = ("10.0.0.1",)
    count = len(peer.requests)
    with pytest.raises(MCPToolExecutionError):
        await client.call_tool("echo", {"text": "x"})
    assert len(peer.requests) == count
    await client.disconnect()


@pytest.mark.asyncio
async def test_invalid_tools_excluded_and_bad_arguments_fail_before_io():
    peer = Peer()
    peer.tools += [
        {
            "name": "bad",
            "inputSchema": {
                "type": "object",
                "properties": {"v": {"type": "number", "x-mcp-header": "Bad"}},
            },
        }
    ]
    client, _, _ = await ready_client(peer=peer)
    assert [tool["name"] for tool in await client.list_tools()] == ["echo"]
    assert client.rejected_http_tools == 1
    count = len(peer.requests)
    for name, args in (("echo", {"text": 3}), ("bad", {"v": 2})):
        with pytest.raises(MCPToolExecutionError):
            await client.call_tool(name, args)
    assert len(peer.requests) == count
    await client.disconnect()


@pytest.mark.asyncio
async def test_2025_session_404_reinitializes_once_without_replaying_mutation():
    client, peer, _ = await ready_client(peer=Peer(HTTP_COMPAT_VERSION))
    peer.expire_once = True
    with pytest.raises(MCPToolExecutionError):
        await client.call_tool("echo", {"text": "first"})
    assert peer.methods().count("tools/call") == 1
    assert peer.methods().count("initialize") == 2
    init_headers = [h for _, h, r in peer.requests if r.get("method") == "initialize"]
    assert all(b"mcp-session-id" not in h for h in init_headers)
    assert client.is_connected
    assert await client.call_tool("echo", {"text": "next explicit"}) == "next explicit"
    assert peer.requests[-1][1][b"mcp-session-id"] == b"session-2"
    await client.disconnect()
    assert peer.methods().count("DELETE") == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode",
    [
        "wrong_id",
        "bool_id",
        "success_400",
        "bad_type",
        "utf16",
        "utf16-no-bom",
        "utf32-no-bom",
        "invalid_json",
        "duplicate_key",
        "truncated",
        "redirect",
        "wire_error",
    ],
)
async def test_bad_http_response_never_replays_or_leaks_peer_payload(mode):
    client, peer, _ = await ready_client()

    def hook(verb, headers, request):
        if request.get("method") != "tools/call":
            return None
        reply = peer.rpc(
            request, {"content": [{"type": "text", "text": "secret-payload"}]}
        )
        data = json.loads(reply.body)
        if mode == "wrong_id":
            data["id"] = "another-request"
        if mode == "bool_id":
            data["id"] = True
        if mode == "success_400":
            reply.status = 400
        if mode == "bad_type":
            reply.kind = "text/html"
        if mode == "redirect":
            reply.status = 302
            reply.headers.append(("Location", "https://attacker.test/secret"))
        if mode == "wire_error":
            return peer.rpc(
                request,
                error={
                    "code": -32020,
                    "message": "secret-payload",
                    "data": "secret-payload",
                },
                status=400,
            )
        reply.body = json.dumps(data).encode()
        if mode == "utf16":
            reply.body = json.dumps(data).encode("utf-16")
        if mode == "utf16-no-bom":
            reply.body = json.dumps(data).encode("utf-16-le")
        if mode == "utf32-no-bom":
            reply.body = json.dumps(data).encode("utf-32-le")
        if mode == "invalid_json":
            reply.body = b"secret-payload"
        if mode == "duplicate_key":
            reply.body = b'{"jsonrpc":"2.0","id":"a","id":"b","result":{}}'
        if mode == "truncated":
            reply.advertised_extra = 10
        return reply

    peer.hook = hook
    with pytest.raises((MCPToolExecutionError, MCPError)) as failure:
        await client.call_tool("echo", {"text": "x"})
    assert "secret-payload" not in str(failure.value) and "attacker" not in str(
        failure.value
    )
    assert peer.methods().count("tools/call") == 1
    await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize("version", [MODERN_VERSION, HTTP_COMPAT_VERSION])
async def test_single_timeout_issued_cancellation_and_stream_owners(version):
    client, peer, _ = await ready_client(
        peer=Peer(version), limits=ProtocolLimits(timeout_seconds=0.1)
    )
    peer.hook = (
        lambda verb, headers, request: peer.rpc(
            request, {"content": []}, stall=asyncio.Event()
        )
        if request.get("method") == "tools/call"
        else None
    )
    with pytest.raises(TimeoutError):
        await client.call_tool("echo", {"text": "x"})
    await asyncio.sleep(0.02)
    assert peer.methods().count("tools/call") == 1
    assert peer.methods().count("notifications/cancelled") == (
        version == HTTP_COMPAT_VERSION
    )
    await client.disconnect()
    assert not client.outstanding_http_owners and all(s.closed for s in peer.streams)


@pytest.mark.asyncio
async def test_dns_timeout_is_unissued_and_initialize_is_not_cancelled():
    resolver = Resolver()
    resolver.stall = asyncio.Event()
    client, peer, _ = make_client(
        peer=Peer(HTTP_COMPAT_VERSION),
        resolver=resolver,
        limits=ProtocolLimits(timeout_seconds=0.03),
    )
    with pytest.raises(TimeoutError):
        await client.connect()
    assert not peer.requests and "notifications/cancelled" not in peer.methods()
    assert client._pool is None


@pytest.mark.asyncio
async def test_cancellation_resistant_response_retains_capacity_then_reaps():
    client, peer, _ = await ready_client(
        limits=ProtocolLimits(timeout_seconds=0.05, concurrent_requests=1)
    )
    release = asyncio.Event()
    peer.hook = (
        lambda verb, headers, request: peer.rpc(
            request, {"content": []}, stall=release, resistant=True
        )
        if request.get("method") == "tools/call"
        else None
    )
    with pytest.raises(TimeoutError):
        await client.call_tool("echo", {"text": "x"})
    assert client.outstanding_http_owners == 1
    with pytest.raises(MCPToolExecutionError) as failure:
        await client.call_tool("echo", {"text": "second"})
    assert failure.value.failure_code == "limit_exceeded"
    assert peer.methods().count("tools/call") == 1
    release.set()
    await asyncio.sleep(0.03)
    await client.disconnect()
    assert client.outstanding_http_owners == 0


@pytest.mark.asyncio
async def test_cleanup_resistant_owner_remains_observable_and_retryable():
    client, peer, _ = await ready_client(limits=ProtocolLimits(concurrent_requests=1))
    release = asyncio.Event()
    peer.hook = (
        lambda verb, headers, request: peer.rpc(
            request, {"content": [{"type": "text", "text": "x"}]}, close_release=release
        )
        if request.get("method") == "tools/call"
        else None
    )
    with pytest.raises(MCPToolExecutionError):
        await client.call_tool("echo", {"text": "x"})
    assert client.outstanding_http_owners == 1
    with pytest.raises(RuntimeError, match="cleanup incomplete"):
        await client.disconnect()
    release.set()
    await asyncio.sleep(0.02)
    await client.disconnect()
    assert client.outstanding_http_owners == 0


@pytest.mark.asyncio
async def test_debug_header_logging_is_fail_closed_without_global_changes(caplog):
    client, peer, _ = make_client(bearer_token="synthetic-secret")
    logger = logging.getLogger("httpcore.http11")
    level = logger.level
    try:
        logger.setLevel(logging.DEBUG)
        with pytest.raises(ProtocolFailure):
            await client.connect()
        assert logger.level == logging.DEBUG
        assert "synthetic-secret" not in caplog.text and not peer.requests
    finally:
        logger.setLevel(level)
    await client.connect()
    await client.list_tools()
    await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode", ["good", "wrong-id", "duplicate", "server-request", "truncated"]
)
async def test_modern_sse_notifications_chunked_utf8_and_response_isolation(mode):
    client, peer, _ = await ready_client()

    def hook(verb, headers, request):
        if request.get("method") != "tools/call":
            return None
        final = peer.rpc(request, {"content": [{"type": "text", "text": "雪"}]}).body
        if mode == "wrong-id":
            obj = json.loads(final)
            obj["id"] = "unrelated"
            final = json.dumps(obj).encode()
        prefix = (
            b': ignored\r\n\r\ndata: {"jsonrpc":"2.0",'
            b'"method":"notifications/progress",'
            b'"params":{"progressToken":"unadvertised","progress":1}}\n\n'
        )
        if mode == "server-request":
            prefix = (
                b'data: {"jsonrpc":"2.0","id":"peer",'
                b'"method":"sampling/createMessage","params":{}}\n\n'
            )
        body = prefix + b"event: message\ndata: " + final + b"\n\n"
        if mode == "duplicate":
            body += b"data: " + final + b"\n\n"
        if mode == "truncated":
            body = body[:-1]
        return Reply(
            body, kind="text/event-stream", width=16384 if mode == "duplicate" else 1
        )

    peer.hook = hook
    if mode == "good":
        assert await client.call_tool("echo", {"text": "x"}) == "雪"
    else:
        with pytest.raises(MCPToolExecutionError):
            await client.call_tool("echo", {"text": "x"})
    assert peer.methods().count("tools/call") == 1
    await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "code,status",
    [(-32020, 200), (-32021, 200), (-32022, 200), (-32602, 200), (-32601, 400)],
)
async def test_modern_reserved_wire_error_status_relationship(code, status):
    client, peer, _ = await ready_client()
    peer.hook = (
        lambda verb, headers, request: peer.rpc(
            request, error={"code": code, "message": "untrusted"}, status=status
        )
        if request.get("method") == "tools/call"
        else None
    )
    with pytest.raises(MCPToolExecutionError):
        await client.call_tool("echo", {"text": "x"})
    assert peer.methods().count("tools/call") == 1
    await client.disconnect()


@pytest.mark.asyncio
async def test_concurrent_streams_have_independent_owners_and_cancellation():
    client, peer, _ = await ready_client()
    release = asyncio.Event()
    peer.hook = (
        lambda verb, headers, request: peer.rpc(
            request,
            {
                "content": [
                    {"type": "text", "text": request["params"]["arguments"]["text"]}
                ]
            },
            stall=release,
        )
        if request.get("method") == "tools/call"
        else None
    )
    tasks = [
        asyncio.create_task(client.call_tool("echo", {"text": str(i)}))
        for i in range(4)
    ]
    while peer.methods().count("tools/call") < 4:
        await asyncio.sleep(0)
    assert client.outstanding_http_owners == 4
    with pytest.raises(MCPToolExecutionError) as failure:
        await client.call_tool("echo", {"text": "fifth"})
    assert failure.value.failure_code == "limit_exceeded"
    tasks[0].cancel()
    with pytest.raises(asyncio.CancelledError):
        await tasks[0]
    release.set()
    assert await asyncio.gather(*tasks[1:]) == ["1", "2", "3"]
    assert "notifications/cancelled" not in peer.methods()
    await client.disconnect()
    assert all(s.closed for s in peer.streams)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode", ["cycle", "bad-second", "metadata", "oversized", "too-many"]
)
async def test_catalog_pages_fail_without_partial_or_stale_schemas(mode):
    client, peer, _ = await ready_client(
        limits=ProtocolLimits(catalog_tools=2, catalog_bytes=3000)
    )

    def hook(verb, headers, request):
        if request.get("method") != "tools/list":
            return None
        cursor = request["params"].get("cursor")
        tool = {
            "name": "first" if cursor is None else "second",
            "inputSchema": {"type": "object"},
        }
        result = {
            "tools": [tool],
            "ttlMs": 0,
            "cacheScope": "private",
            "nextCursor": "next",
        }
        if mode == "bad-second" and cursor:
            result["tools"] = False
        if mode == "metadata":
            tool["_meta"] = {"bad/name/key": 1}
        if mode == "oversized":
            tool["description"] = "x" * 4000
        if mode == "too-many":
            result["tools"] = [tool] * 3
        return peer.rpc(request, result)

    peer.hook = hook
    with pytest.raises(ProtocolFailure):
        await client.list_tools()
    assert not client._catalog and not client._bindings
    await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["headers", "body", "events", "line", "outgoing"])
async def test_http_limits_at_wire_and_pre_io_boundaries(mode):
    client, peer, _ = await ready_client(
        http_limits=HTTPLimits(
            header_bytes=1024, wire_bytes=3000, sse_events=2, sse_line_bytes=200
        )
    )
    before = len(peer.requests)

    def hook(verb, headers, request):
        if request.get("method") != "tools/call":
            return None
        reply = peer.rpc(request, {"content": [{"type": "text", "text": "x"}]})
        if mode == "headers":
            reply.headers.append(("X-Synthetic", "s" * 1100))
        if mode == "body":
            reply.body = b"x" * 4000
        if mode == "events":
            reply.kind = "text/event-stream"
            reply.body = b": a\n: b\n: c\n"
        if mode == "line":
            reply.kind = "text/event-stream"
            reply.body = b"data: " + b"x" * 201
        return reply

    peer.hook = hook
    with pytest.raises(MCPToolExecutionError):
        await client.call_tool(
            "echo", {"text": "x" * 1100 if mode == "outgoing" else "x"}
        )
    assert len(peer.requests) == before + (mode != "outgoing")
    await client.disconnect()


@pytest.mark.asyncio
async def test_single_catalog_deadline_includes_all_pages_without_progress_reset():
    client, peer, _ = await ready_client(limits=ProtocolLimits(timeout_seconds=0.05))
    peer.hook = (
        lambda verb, headers, request: peer.rpc(
            request,
            {"tools": [], "ttlMs": 0, "cacheScope": "private", "nextCursor": "next"},
            stall=asyncio.Event() if request["params"].get("cursor") else None,
        )
        if request.get("method") == "tools/list"
        else None
    )
    start = asyncio.get_running_loop().time()
    with pytest.raises(TimeoutError):
        await client.list_tools()
    assert asyncio.get_running_loop().time() - start < 0.3
    assert not client._catalog and not client._bindings
    await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize("shape", [None, 3, [1, 2], {"a": 1}])
async def test_modern_structured_only_scalar_null_array_object_fidelity(shape):
    client, peer, _ = await ready_client()
    peer.hook = (
        lambda verb, headers, request: peer.rpc(
            request, {"content": [], "structuredContent": shape}
        )
        if request.get("method") == "tools/call"
        else None
    )
    assert json.loads(await client.call_tool("echo", {"text": "x"})) == shape
    await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "result,expected",
    [
        (
            {"resultType": "input_required", "requestState": "opaque"},
            "input_required_unsupported",
        ),
        (
            {"content": [{"type": "image", "data": "opaque", "mimeType": "image/png"}]},
            "unsupported_content",
        ),
        ({"content": [], "isError": True}, "tool_error"),
        ({"content": [{"type": "text", "text": "x" * 66000}]}, "limit_exceeded"),
    ],
)
async def test_http_result_dispositions_never_continue_or_replay(result, expected):
    client, peer, _ = await ready_client()
    peer.hook = (
        lambda verb, headers, request: peer.rpc(request, result)
        if request.get("method") == "tools/call"
        else None
    )
    with pytest.raises(MCPToolExecutionError) as failure:
        await client.call_tool("echo", {"text": "x"})
    assert failure.value.failure_code == expected
    assert peer.methods().count("tools/call") == 1
    await client.disconnect()


@pytest.mark.asyncio
async def test_call_output_schema_snapshot_survives_concurrent_catalog_invalidation():
    peer = Peer()
    peer.tools[0]["outputSchema"] = {
        "type": "object",
        "properties": {"v": {"type": "integer"}},
        "required": ["v"],
    }
    client, peer, _ = await ready_client(peer=peer)
    release = asyncio.Event()
    peer.hook = (
        lambda verb, headers, request: peer.rpc(
            request, {"content": [], "structuredContent": {"v": "wrong"}}, stall=release
        )
        if request.get("method") == "tools/call"
        else None
    )
    task = asyncio.create_task(client.call_tool("echo", {"text": "x"}))
    while peer.methods().count("tools/call") < 1:
        await asyncio.sleep(0)
    client._catalog = ()  # Same invalidation performed before any real refresh.
    release.set()
    with pytest.raises(MCPToolExecutionError) as failure:
        await task
    assert failure.value.failure_code == "invalid_result"
    await client.disconnect()


@pytest.mark.asyncio
async def test_public_call_cannot_issue_before_compatibility_handshake_completes():
    peer = Peer(HTTP_COMPAT_VERSION)
    release = asyncio.Event()

    def hook(verb, headers, request):
        if request.get("method") == "initialize":
            return peer.rpc(
                request,
                {
                    "protocolVersion": HTTP_COMPAT_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "fixture", "version": "1"},
                },
                stall=release,
            )

    peer.hook = hook
    client, _, _ = make_client(peer=peer)
    connecting = asyncio.create_task(client.connect())
    try:
        for _ in range(100):
            if "initialize" in peer.methods():
                break
            await asyncio.sleep(0.001)
        assert "initialize" in peer.methods()
        with pytest.raises(RuntimeError, match="disconnected"):
            await client.call_tool("echo", {"text": "no early mutation"})
        assert "tools/call" not in peer.methods()
        release.set()
        await connecting
        assert client.is_connected
    finally:
        release.set()
        await asyncio.gather(connecting, return_exceptions=True)
        await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name,kind",
    [("Hidden", "string"), ("bad name", "string"), (9, "string"), ("Hidden", "number")],
)
@pytest.mark.parametrize("nested", [False, True])
async def test_content_schema_invalid_tools_are_counted_after_atomic_catalog(
    name, kind, nested
):
    peer = Peer()
    child = {
        "type": "object",
        "properties": {"v": {"type": kind, "x-mcp-header": name}},
    }
    schema = {"type": "object", "contentSchema": child}
    if nested:
        schema = {
            "type": "object",
            "properties": {
                "payload": {
                    "type": "string",
                    "contentMediaType": "application/json",
                    "contentSchema": child,
                }
            },
        }
    bad = {"name": "bad", "inputSchema": schema}
    page_started = asyncio.Event()
    page_release = asyncio.Event()

    def hook(verb, headers, request):
        if request.get("method") != "tools/list":
            return None
        if "cursor" not in request["params"]:
            return peer.rpc(
                request,
                {
                    "tools": [bad],
                    "nextCursor": "next",
                    "ttlMs": 0,
                    "cacheScope": "private",
                },
            )
        page_started.set()
        return peer.rpc(
            request,
            {"tools": peer.tools, "ttlMs": 0, "cacheScope": "private"},
            stall=page_release,
        )

    peer.hook = hook
    client, _, _ = make_client(peer=peer)
    await client.connect()
    listing = asyncio.create_task(client.list_tools())
    try:
        await asyncio.wait_for(page_started.wait(), 1)
        assert client._catalog == () and client._bindings == {}
        assert client.rejected_http_tools == 0
        page_release.set()
        assert [t["name"] for t in await listing] == ["echo"]
        assert client.rejected_http_tools == 1
        before = len(peer.requests)
        with pytest.raises(MCPToolExecutionError):
            await client.call_tool("bad", {"payload": "x"})
        assert len(peer.requests) == before
        assert await client.call_tool("echo", {"text": "雪"}) == "雪"
        assert peer.requests[-1][1][b"mcp-param-text"] == b"=?base64?6Zuq?="
    finally:
        page_release.set()
        await asyncio.gather(listing, return_exceptions=True)
        await client.disconnect()
    assert client.outstanding_http_owners == 0


class OrderedExpiryStream(WireStream):
    async def read(self, max_bytes, timeout=None):
        await self.ready.wait()
        if b'"text":"late"' in self.outgoing:
            await self.connector.late_release.wait()
        return await super().read(max_bytes, timeout)


class OrderedExpiryPeer(Peer):
    def __init__(self):
        super().__init__(HTTP_COMPAT_VERSION)
        self.late_release = asyncio.Event()
        self.late_issued = asyncio.Event()

    async def connect_tcp(
        self, host, port, timeout=None, local_address=None, socket_options=None
    ):
        self.connections.append((host, port))
        stream = OrderedExpiryStream(self)
        self.streams.append(stream)
        return stream

    def dispatch(self, verb, headers, request):
        if (
            request.get("method") == "tools/call"
            and request["params"]["arguments"].get("text") == "late"
        ):
            self.late_issued.set()
        return super().dispatch(verb, headers, request)


@pytest.mark.asyncio
@pytest.mark.parametrize("first_recovery", ["success", "failure"])
async def test_old_generation_404_cannot_disconnect_recovered_session(first_recovery):
    peer = OrderedExpiryPeer()
    client, _, _ = await ready_client(peer=peer)
    recovery_failed = False

    def hook(verb, headers, request):
        nonlocal recovery_failed
        if request.get("method") == "tools/call":
            return Reply(status=404)
        if (
            request.get("method") == "initialize"
            and first_recovery == "failure"
            and not recovery_failed
        ):
            recovery_failed = True
            return Reply(body=b"invalid")
        return None

    peer.hook = hook
    late = asyncio.create_task(client.call_tool("echo", {"text": "late"}))
    try:
        await asyncio.wait_for(peer.late_issued.wait(), 1)
        with pytest.raises(MCPToolExecutionError) as fast_failure:
            await client.call_tool("echo", {"text": "fast"})
        assert fast_failure.value.failure_code == "invalid_protocol"
        if first_recovery == "failure":
            assert not client.is_connected and client._session_id is None
            await client.connect()
        assert client.is_connected and client._session_id == b"session-2"
        peer.hook = None
        healthy_catalog = await client.list_tools()
        catalog_owner = client._catalog
        generation = client._generation
        peer.late_release.set()
        if first_recovery == "failure":
            with pytest.raises(asyncio.CancelledError):
                await late
        else:
            with pytest.raises(MCPToolExecutionError) as late_failure:
                await late
            assert late_failure.value.failure_code == "invalid_protocol"
        assert peer.methods().count("initialize") == (
            3 if first_recovery == "failure" else 2
        )
        assert peer.methods().count("tools/call") == 2
        assert client.is_connected and client._session_id == b"session-2"
        assert client._generation == generation and client._catalog is catalog_owner
        assert await client.list_tools() == healthy_catalog
        assert await client.call_tool("echo", {"text": "next"}) == "next"
        assert peer.requests[-1][1][b"mcp-session-id"] == b"session-2"
        assert all(
            b"mcp-session-id" not in h
            for _, h, r in peer.requests
            if r.get("method") == "initialize"
        )
    finally:
        peer.late_release.set()
        await asyncio.gather(late, return_exceptions=True)
        await client.disconnect()
    assert client.outstanding_http_owners == 0 and all(s.closed for s in peer.streams)


@pytest.mark.asyncio
async def test_stale_recovery_waiter_deadline_does_not_invalidate_active_recovery():
    peer = Peer(HTTP_COMPAT_VERSION)
    client, _, _ = await ready_client(peer=peer)
    initialize_started = asyncio.Event()
    initialize_release = asyncio.Event()

    def hook(verb, headers, request):
        if request.get("method") == "tools/call":
            return Reply(status=404)
        if request.get("method") == "initialize":
            initialize_started.set()
            peer.sessions += 1
            return peer.rpc(
                request,
                {
                    "protocolVersion": HTTP_COMPAT_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "fixture", "version": "1"},
                },
                headers=[("MCP-Session-Id", "session-2")],
                stall=initialize_release,
            )
        return None

    peer.hook = hook
    # Both requests are issued in generation 1 before either response is settled.
    fast = asyncio.create_task(
        client._request(
            "tools/call", {"name": "echo", "arguments": {"text": "fast"}}, timeout=1
        )
    )
    waiter = asyncio.create_task(
        client._request(
            "tools/call",
            {"name": "echo", "arguments": {"text": "waiting"}},
            timeout=0.05,
        )
    )
    try:
        await asyncio.wait_for(initialize_started.wait(), 1)
        with pytest.raises(ProtocolFailure):
            await waiter
        assert not client.is_connected and client._session_id == b"session-2"
        initialize_release.set()
        with pytest.raises(ProtocolFailure):
            await fast
        assert client.is_connected and client._session_id == b"session-2"
        assert peer.methods().count("initialize") == 2
        assert peer.methods().count("tools/call") == 2
        peer.hook = None
        assert await client.call_tool("echo", {"text": "next"}) == "next"
    finally:
        initialize_release.set()
        await asyncio.gather(fast, waiter, return_exceptions=True)
        await client.disconnect()
    assert client.outstanding_http_owners == 0 and all(s.closed for s in peer.streams)


@pytest.mark.asyncio
async def test_timed_out_recovery_retains_disconnected_state_until_explicit_connect():
    peer = OrderedExpiryPeer()
    client, _, _ = await ready_client(peer=peer)
    initialize_started = asyncio.Event()
    never_release = asyncio.Event()

    def hook(verb, headers, request):
        if request.get("method") == "tools/call":
            return Reply(status=404)
        if request.get("method") == "initialize":
            initialize_started.set()
            return peer.rpc(
                request,
                {
                    "protocolVersion": HTTP_COMPAT_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "fixture", "version": "1"},
                },
                stall=never_release,
            )
        return None

    peer.hook = hook
    late = asyncio.create_task(client.call_tool("echo", {"text": "late"}))
    try:
        await asyncio.wait_for(peer.late_issued.wait(), 1)
        with pytest.raises(ProtocolFailure):
            await client._request(
                "tools/call",
                {"name": "echo", "arguments": {"text": "fast"}},
                timeout=0.05,
            )
        assert initialize_started.is_set()
        assert (
            not client.is_connected
            and client._session_id is None
            and not client._catalog
        )
        peer.hook = None
        # Settle the old response before reconnect cleanup cancels its owner.
        peer.late_release.set()
        with pytest.raises(MCPToolExecutionError):
            await late
        await client.connect()
        await client.list_tools()
        assert (
            client.is_connected
            and await client.call_tool("echo", {"text": "next"}) == "next"
        )
        assert peer.methods().count("initialize") == 3
        assert peer.methods().count("tools/call") == 3
    finally:
        never_release.set()
        peer.late_release.set()
        await asyncio.gather(late, return_exceptions=True)
        await client.disconnect()
    assert client.outstanding_http_owners == 0 and all(s.closed for s in peer.streams)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dialect", [None, "https://json-schema.org/draft/2020-12/schema"]
)
async def test_2025_default_and_declared_input_dialect_are_validated_without_retrieval(
    dialect,
):
    peer = Peer(HTTP_COMPAT_VERSION)
    if dialect is not None:
        peer.tools[0]["inputSchema"]["$schema"] = dialect
    client, _, resolver = await ready_client(peer=peer)
    try:
        assert await client.call_tool("echo", {"text": "ok"}) == "ok"
        assert resolver.calls == len(peer.requests)
        assert all(host == "93.184.216.34" for host, _ in peer.connections)
    finally:
        await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dialect",
    [
        "https://unsupported.example/unknown-schema",
        "http://json-schema.org/draft-07/schema#",
        "",
        None,
        42,
        {},
    ],
)
async def test_2025_unsupported_input_dialect_discards_entire_catalog(
    dialect,
):
    peer = Peer(HTTP_COMPAT_VERSION)
    client, _, resolver = await ready_client(peer=peer)
    bad = deepcopy(peer.tools[0])
    bad["name"] = "bad"
    bad["inputSchema"]["$schema"] = dialect

    def hook(verb, headers, request):
        if request.get("method") != "tools/list":
            return None
        if "cursor" not in request["params"]:
            return peer.rpc(request, {"tools": peer.tools, "nextCursor": "next"})
        return peer.rpc(request, {"tools": [bad]})

    peer.hook = hook
    try:
        before = len(peer.requests)
        with pytest.raises(ProtocolFailure) as failure:
            await client.list_tools()
        assert failure.value.failure_code == "unsupported_schema"
        assert str(failure.value) == "MCP output schema is unsupported"
        assert not client._catalog and not client._bindings
        assert len(peer.requests) == before + 2
        assert peer.methods().count("tools/call") == 0
        assert resolver.calls == len(peer.requests)
        assert all(host == "93.184.216.34" for host, _ in peer.connections)
    finally:
        await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "location",
    [
        "tool",
        "result",
        "text",
        "list-result",
        "initialize",
        "request-params",
        "notification-params",
    ],
)
@pytest.mark.parametrize(
    "key",
    [
        "bad/name/key",
        "9bad/name",
        "bad-/name",
        "bad..prefix/name",
        "bad/_name",
        "bad/name-",
        "/name",
    ],
)
async def test_2025_malformed_metadata_is_rejected_at_each_boundary(location, key):
    peer = Peer(HTTP_COMPAT_VERSION)
    if location == "tool":
        peer.tools[0]["_meta"] = {key: "private-payload"}

    def hook(verb, headers, request):
        method = request.get("method")
        if location == "initialize" and method == "initialize":
            return peer.rpc(
                request,
                {
                    "protocolVersion": HTTP_COMPAT_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "fixture", "version": "1"},
                    "_meta": {key: "private-payload"},
                },
            )
        if location == "list-result" and method == "tools/list":
            return peer.rpc(
                request, {"tools": peer.tools, "_meta": {key: "private-payload"}}
            )
        if method != "tools/call":
            return None
        block = {"type": "text", "text": "ok"}
        result = {"content": [block]}
        if location in ("result", "text"):
            (result if location == "result" else block)["_meta"] = {
                key: "private-payload"
            }
            return peer.rpc(request, result)
        if location in ("request-params", "notification-params"):
            message = {
                "jsonrpc": "2.0",
                "method": "unsupported",
                "params": {"_meta": {key: "private-payload"}},
            }
            if location == "request-params":
                message["id"] = "server-request"
            body = (
                b"data: "
                + json.dumps(message).encode()
                + b"\n\n"
                + b"data: "
                + peer.rpc(request, result).body
                + b"\n\n"
            )
            return Reply(body=body, kind="text/event-stream")
        return None

    peer.hook = hook
    client, _, _ = make_client(peer=peer)
    try:
        if location == "initialize":
            with pytest.raises(ProtocolFailure) as failure:
                await client.connect()
            assert not client.is_connected
        else:
            await client.connect()
            if location in ("tool", "list-result"):
                with pytest.raises(ProtocolFailure) as failure:
                    await client.list_tools()
                assert not client._catalog and not client._bindings
            else:
                await client.list_tools()
                with pytest.raises(MCPToolExecutionError) as failure:
                    await client.call_tool("echo", {"text": "x"})
        assert failure.value.failure_code == "invalid_protocol"
        assert key not in str(failure.value) and "private-payload" not in str(
            failure.value
        )
        assert peer.methods().count("tools/call") == (
            0 if location in ("initialize", "tool", "list-result") else 1
        )
    finally:
        await client.disconnect()
    assert client.outstanding_http_owners == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "key",
    [
        "",
        "a",
        "a.b_c-d",
        "com.example/",
        "com.example/name",
        "io.modelcontextprotocol/serverInfo",
        "io.modelcontextprotocol/subscriptionId",
    ],
)
async def test_2025_metadata_grammar_preserves_opaque_values_and_application_json(key):
    peer = Peer(HTTP_COMPAT_VERSION)
    opaque = {
        "_meta": {"bad/name/key": "data"},
        "contentSchema": {"x-mcp-header": "data"},
    }
    peer.tools[0]["_meta"] = {key: opaque}
    peer.tools[0]["inputSchema"]["default"] = opaque

    def hook(verb, headers, request):
        if request.get("method") != "tools/call":
            return None
        return peer.rpc(
            request,
            {
                "content": [{"type": "text", "text": "ok", "_meta": {key: "opaque"}}],
                "_meta": {key: "opaque"},
                "structuredContent": opaque,
            },
        )

    peer.hook = hook
    client, _, _ = await ready_client(peer=peer)
    try:
        output = json.loads(
            await client.call_tool(
                "echo", {"text": "x", "_meta": {"bad/name/key": "ordinary argument"}}
            )
        )
        assert output["structuredContent"] == opaque
        assert output["content"] == [{"type": "text", "text": "ok"}]
        assert (await client.list_tools())[0]["_meta"] == {key: opaque}
    finally:
        await client.disconnect()
