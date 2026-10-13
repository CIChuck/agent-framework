"""Official SDK 2.3.0 real HTTP counterpart; synthetic tools and loopback only."""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Annotated

import uvicorn
from mcp.server import MCPServer
from pydantic import Field

server = MCPServer("friday-synthetic-http-sdk", version="fixture", subscriptions=False)


def record(name: str) -> None:
    path = os.environ.get("MCP_FIXTURE_COUNTER")
    if path:
        with Path(path).open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"tool": name}) + "\n")


@server.tool()
async def echo(
    text: Annotated[str, Field(json_schema_extra={"x-mcp-header": "Text"})],
) -> str:
    """Return synthetic input with required HTTP header mirroring."""
    record("echo")
    return text


@server.tool()
async def structured(value: int) -> dict[str, int]:
    """Return a bounded structured object."""
    record("structured")
    return {"value": value}


@server.tool()
async def slow() -> str:
    """A cancellable synthetic call."""
    record("slow")
    await asyncio.sleep(2)
    return "done"


@server.tool()
async def drop() -> str:
    """Record one execution then drop without a response."""
    record("drop")
    os._exit(0)


if __name__ == "__main__":
    if os.environ.get("MCP_FIXTURE_TLS_CERT"):
        app = server.streamable_http_app(
            host="127.0.0.1",
            json_response=sys.argv[2] != "tls-sse",
            stateless_http=True,
        )
        inner = app

        async def app(scope, receive, send):
            if scope["type"] == "http":
                headers = dict(scope["headers"])
                path = os.environ.get("MCP_FIXTURE_WIRE_COUNTER")
                expected = os.environ.get("MCP_FIXTURE_EXPECT_BEARER")
                matches = (
                    expected is None
                    or headers.get(b"authorization") == ("Bearer " + expected).encode()
                )
                if path:
                    safe = {
                        k.decode(): v.decode()
                        for k, v in headers.items()
                        if k
                        in (
                            b"mcp-protocol-version",
                            b"mcp-method",
                            b"mcp-name",
                            b"mcp-param-text",
                        )
                    }
                    safe.update(
                        auth_matches=matches,
                        trace_present=any(
                            k in headers
                            for k in (b"traceparent", b"tracestate", b"baggage")
                        ),
                    )
                    with Path(path).open("a") as stream:
                        stream.write(json.dumps(safe) + "\n")
                if not matches:
                    await send(
                        {"type": "http.response.start", "status": 401, "headers": []}
                    )
                    await send({"type": "http.response.body", "body": b""})
                    return
            await inner(scope, receive, send)

        asyncio.run(
            uvicorn.Server(
                uvicorn.Config(
                    app,
                    host="127.0.0.1",
                    port=int(sys.argv[1]),
                    log_level="error",
                    ssl_certfile=os.environ["MCP_FIXTURE_TLS_CERT"],
                    ssl_keyfile=os.environ["MCP_FIXTURE_TLS_KEY"],
                )
            ).serve()
        )
    else:
        asyncio.run(
            server.run_streamable_http_async(
                host="127.0.0.1",
                port=int(sys.argv[1]),
                json_response=sys.argv[2] == "json",
                stateless_http=True,
            )
        )
