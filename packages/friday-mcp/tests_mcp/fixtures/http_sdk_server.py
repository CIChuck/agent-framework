"""Official SDK 2.3.0 real HTTP counterpart; synthetic tools and loopback only."""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Annotated

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
    asyncio.run(
        server.run_streamable_http_async(
            host="127.0.0.1",
            port=int(sys.argv[1]),
            json_response=sys.argv[2] == "json",
            stateless_http=True,
        )
    )
