"""Named synthetic Friday subprocess counterpart: real stdio or private TLS HTTP."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from friday_mcp.server import (
    HTTPServerPolicy,
    ModernStdioMCPServer,
    StreamableHTTPMCPServer,
    ToolCallResult,
)
from friday_mcp.server.protocol import PREFIX


def record(path, item):
    with path.open("a") as stream:
        stream.write(json.dumps(item) + "\n")


def populate(server, counter):
    async def echo(arguments):
        record(counter, {"event": "handler_start"})
        try:
            if arguments.get("hold"):
                await asyncio.sleep(10)
            if arguments.get("fail"):
                raise RuntimeError("synthetic-private-exception")
            return ToolCallResult.structured({"text": arguments.get("text", "")})
        finally:
            record(counter, {"event": "handler_terminal"})

    server.register_tool(
        {
            "name": "echo",
            "description": "Explicit synthetic fixture",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "x-mcp-header": "Text"},
                    "hold": {"type": "boolean"},
                    "fail": {"type": "boolean"},
                },
                "additionalProperties": False,
            },
            "outputSchema": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
        echo,
    )


async def main():
    mode, counter_name, *options = sys.argv[1:]
    counter = Path(counter_name)

    class RecordedStdio(ModernStdioMCPServer):
        async def dispatch(self, request):
            meta = request.params.get("_meta", {})
            record(
                counter,
                {
                    "event": "request",
                    "method": request.method,
                    "version": request.version,
                    "has_capabilities": PREFIX + "clientCapabilities" in meta,
                },
            )
            return await super().dispatch(request)

    class RecordedHTTP(StreamableHTTPMCPServer):
        async def dispatch(self, request):
            meta = request.params.get("_meta", {})
            record(
                counter,
                {
                    "event": "request",
                    "method": request.method,
                    "version": request.version,
                    "has_capabilities": PREFIX + "clientCapabilities" in meta,
                },
            )
            return await super().dispatch(request)

    if mode == "stdio":
        server = RecordedStdio()
        populate(server, counter)
        await server.serve()
    else:
        port, certificate, key, ready = options
        server = RecordedHTTP(
            policy=HTTPServerPolicy(port=int(port), require_tls=True),
            response_mode=mode,
        )
        populate(server, counter)
        serving = asyncio.create_task(
            server.serve(certificate=certificate, private_key=key)
        )
        while not server.listening:
            if serving.done():
                await serving
                return
            await asyncio.sleep(0.01)
        Path(ready).write_text("ready")
        await serving
    record(counter, {"event": "server_stopped", "active": server.active_requests})


if __name__ == "__main__":
    asyncio.run(main())
