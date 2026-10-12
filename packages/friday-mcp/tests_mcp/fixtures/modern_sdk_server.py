"""Synthetic official SDK 2.3.0 stdio counterpart; never a Friday service."""

import asyncio
import json
import os
from pathlib import Path

from mcp.server import MCPServer

server = MCPServer("friday-synthetic-sdk", version="fixture", subscriptions=False)


def record(name: str) -> None:
    path = os.environ.get("MCP_FIXTURE_COUNTER")
    if path:
        with Path(path).open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"tool": name}) + "\n")


@server.tool()
async def echo(text: str) -> str:
    """Return only the supplied synthetic text."""
    record("echo")
    return text


@server.tool()
async def structured(value: int) -> dict[str, int]:
    """Return a bounded synthetic structured value."""
    record("structured")
    return {"value": value}


@server.tool()
async def slow() -> str:
    """A cancellable synthetic operation."""
    record("slow")
    await asyncio.sleep(2)
    return "done"


@server.tool()
async def drop() -> str:
    """Record one execution then close without a result; never retry."""
    record("drop")
    os._exit(0)


if __name__ == "__main__":
    asyncio.run(server.run_stdio_async())
