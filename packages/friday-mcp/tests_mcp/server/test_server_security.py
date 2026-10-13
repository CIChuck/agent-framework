"""Access and observation rejection precede synthetic handler side effects."""

import asyncio
import hashlib
import json

import pytest
from friday_core import TelemetryInterface

from friday_mcp.server import (
    HTTPServerPolicy,
    ModernToolsMCPServer,
    ServerLimits,
    ToolCallResult,
)
from tests_mcp.server.test_modern_protocol import definition, rpc
from tests_mcp.server.test_streamable_http import headers, http_client, make_server


@pytest.mark.parametrize(
    "options",
    [
        {"path": "/"},
        {"path": "/mcp?token=x"},
        {"path": "/a/../mcp"},
        {"path": "//mcp"},
        {"bind_host": "localhost"},
        {"bind_host": "0.0.0.0"},
        {"bind_host": "192.0.2.1"},
        {"allowed_hosts": ("*.invalid",)},
        {"allowed_origins": ("*",)},
        {"allowed_origins": ("https://example.invalid/path",)},
        {"allowed_origins": ("https://user@example.invalid",)},
        {"bearer_token": ""},
        {"bearer_token": "secret\n"},
        {"port": True},
        {"port": 0},
        {"require_tls": 1},
    ],
)
def test_invalid_exposure_configuration(options):
    with pytest.raises(ValueError):
        HTTPServerPolicy(**options)


def test_explicit_nonlocal_policy_validates_without_binding_and_secret_nonrepr():
    policy = HTTPServerPolicy(
        bind_host="0.0.0.0",
        allowed_hosts=("example.invalid:8000",),
        allowed_origins=("https://example.invalid",),
        bearer_token="SECRET-NONREPR",
        require_tls=True,
    )
    assert "SECRET-NONREPR" not in repr(policy)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "overrides,status",
    [
        ({"Host": "evil.invalid"}, 400),
        ({"Host": "127.0.0.1:8000@evil.invalid"}, 400),
        ({"Origin": "https://evil.invalid"}, 403),
        ({"Origin": "null"}, 403),
        ({"Origin": "http://127.0.0.1:8000/"}, 403),
        ({"Authorization": "Bearer wrong-secret"}, 401),
        ({"Authorization": "Basic wrong-secret"}, 401),
        ({}, 401),
    ],
)
async def test_host_origin_bearer_reject_before_dispatch(overrides, status, caplog):
    policy = HTTPServerPolicy(
        bearer_token="configured-secret", allowed_origins=("http://127.0.0.1:8000",)
    )
    server, calls = make_server(policy=policy)
    h = {**headers(), **overrides}
    if status != 401:
        h["Authorization"] = "Bearer configured-secret"
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers=h,
            content=rpc(
                "tools/call",
                params={
                    "name": "echo",
                    "arguments": {"sentinel": "raw-argument-secret"},
                },
            ),
        )
        assert response.status_code == status
        assert "secret" not in response.text
    assert not calls
    assert (
        "raw-argument-secret" not in caplog.text
        and "configured-secret" not in caplog.text
    )


@pytest.mark.asyncio
async def test_bearer_origin_positive_and_query_token_rejected():
    server, calls = make_server(
        policy=HTTPServerPolicy(
            bearer_token="synthetic-access", allowed_origins=("http://127.0.0.1:8000",)
        )
    )
    h = {
        **headers(),
        "Authorization": "Bearer synthetic-access",
        "Origin": "http://127.0.0.1:8000",
    }
    async with http_client(server) as client:
        assert (
            await client.post(
                "/mcp", headers=h, content=rpc("tools/call", params={"name": "echo"})
            )
        ).status_code == 200
        assert (
            await client.post(
                "/mcp?token=synthetic-access",
                headers=h,
                content=rpc("tools/call", params={"name": "echo"}),
            )
        ).status_code == 400
    assert calls == [{}]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name",
    [
        "Host",
        "Origin",
        "Authorization",
        "Mcp-Method",
        "Mcp-Name",
        "MCP-Protocol-Version",
        "Content-Type",
        "Mcp-Param-X",
    ],
)
async def test_duplicate_case_insensitive_headers_fail_closed(name):
    server, calls = make_server()
    h = list(headers().items()) + [(name.lower(), "bad"), (name.upper(), "bad")]
    async with http_client(server) as client:
        response = await client.post(
            "/mcp", headers=h, content=rpc("tools/call", params={"name": "echo"})
        )
        assert response.status_code == 400
    assert not calls


@pytest.mark.asyncio
async def test_header_and_request_body_byte_budgets_zero_handler():
    server, calls = make_server(
        limits=ServerLimits(header_bytes=400, request_bytes=1000)
    )
    async with http_client(server) as client:
        response = await client.post(
            "/mcp",
            headers={**headers(), "x-large": "x" * 401},
            content=rpc("tools/call", params={"name": "echo"}),
        )
        assert response.status_code == 400

        async def fragmented():
            for _ in range(20):
                yield b"x" * 80

        response = await client.post("/mcp", headers=headers(), content=fragmented())
        assert response.status_code == 400
    assert not calls


class Observer(TelemetryInterface):
    def __init__(self, fail=None):
        self.events = []
        self.fail = fail

    def capture_event(self, event_name, data):
        self.events.append((event_name, data))

    def start_span(self, name, parent_id=None):
        self.events.append(("start", name, parent_id))
        if self.fail == "start":
            raise RuntimeError("observer-secret")
        return "private-span"

    def end_span(self, span_id, data=None):
        self.events.append(("end", data))
        if self.fail == "end":
            raise RuntimeError("observer-secret")


@pytest.mark.asyncio
@pytest.mark.parametrize("fail", [None, "start", "end"])
async def test_provider_neutral_observer_privacy_and_no_replay(fail, caplog):
    one, two = Observer(fail), Observer()
    calls = []

    async def handler(args):
        calls.append(args)
        return ToolCallResult.text("output-secret")

    server = ModernToolsMCPServer(telemetry=one)
    other = ModernToolsMCPServer(telemetry=two)
    server.register_tool(definition("registered-secret-name"), handler)
    other.register_tool(definition(), handler)
    assert (
        await server.handle(
            rpc(
                "tools/call",
                params={"name": "missing", "arguments": {"arg": "argument-secret"}},
            )
        )
    )["error"]["code"] == -32602
    assert not one.events
    response = await server.handle(
        rpc(
            "tools/call",
            rid="client-secret-id",
            params={
                "name": "registered-secret-name",
                "arguments": {"arg": "argument-secret"},
            },
        )
    )
    assert response["result"]["content"][0]["text"] == "output-secret"
    assert len(calls) == 1 and not two.events
    assert [e[0] for e in one.events] == (
        ["start"] if fail == "start" else ["start", "end"]
    )
    observed = json.dumps(one.events) + caplog.text
    for secret in (
        "argument-secret",
        "output-secret",
        "client-secret-id",
        "registered-secret-name",
        "observer-secret",
    ):
        assert secret not in observed


@pytest.mark.asyncio
async def test_cancelled_observation_one_start_and_terminal():
    observer = Observer()
    server = ModernToolsMCPServer(telemetry=observer)
    started = asyncio.Event()

    async def handler(args):
        started.set()
        await asyncio.Event().wait()

    server.register_tool(definition(), handler)
    issued = asyncio.create_task(
        server.handle(rpc("tools/call", params={"name": "echo"}))
    )
    await started.wait()
    issued.cancel()
    await asyncio.gather(issued, return_exceptions=True)
    await server.stop()
    assert observer.events == [
        ("start", "mcp.tools.call", None),
        (
            "end",
            {
                "method": "tools/call",
                "tool_id": hashlib.sha256(b"echo").hexdigest()[:16],
                "outcome": "cancelled",
            },
        ),
    ]


@pytest.mark.parametrize(
    "options",
    [
        {"bind_host": True},
        {"bind_host": 2130706433},
        {"allowed_origins": ("\thttps://example.invalid",)},
        {"allowed_origins": ("https://example.invalid\n",)},
        {"allowed_hosts": ("a" * 257,)},
    ],
)
def test_policy_rejects_nonstring_bind_and_noncanonical_authorities(options):
    with pytest.raises(ValueError):
        HTTPServerPolicy(**options)


@pytest.mark.asyncio
async def test_bearer_scheme_case_insensitive_credentials_case_sensitive():
    server, calls = make_server(policy=HTTPServerPolicy(bearer_token="SyntheticToken"))
    async with http_client(server) as client:
        for scheme in ("bearer", "BEARER", "bEaReR"):
            result = await client.post(
                "/mcp",
                headers={**headers(), "Authorization": scheme + " SyntheticToken"},
                content=rpc("tools/call", params={"name": "echo"}),
            )
            assert result.status_code == 200
        result = await client.post(
            "/mcp",
            headers={**headers(), "Authorization": "Bearer synthetictoken"},
            content=rpc("tools/call", params={"name": "echo"}),
        )
        assert result.status_code == 401
    assert len(calls) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["GET", "DELETE", "HEAD", "OPTIONS"])
async def test_invalid_origin_rejected_on_all_endpoint_methods(method):
    server, calls = make_server()
    async with http_client(server) as client:
        response = await client.request(
            method, "/mcp", headers={"Origin": "https://evil.invalid"}
        )
        assert response.status_code == 403
        valid = await client.request(method, "/mcp")
        assert valid.status_code == 405
    assert not calls
