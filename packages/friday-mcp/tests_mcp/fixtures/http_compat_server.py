"""Independent exact 2025-11-25 synthetic HTTP peer, with bounded real wire."""

import asyncio
import json
import os
import ssl
import sys
from contextlib import suppress
from pathlib import Path

sessions = 0
expired = False
mode = "good"


def record(verb, request, headers):
    path = os.environ.get("MCP_FIXTURE_COUNTER")
    if path:
        with Path(path).open("a", encoding="utf-8") as stream:
            stream.write(
                json.dumps(
                    {
                        "method": request.get("method", "response"),
                        "verb": verb,
                        "has_session": "mcp-session-id" in headers,
                    }
                )
                + "\n"
            )


async def handle(reader, writer):
    global sessions, expired
    try:
        head = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 2)
        if len(head) > 65536:
            return
        lines = head.decode("ascii").split("\r\n")
        verb = lines[0].split()[0]
        headers = dict(
            (k.lower(), v.strip())
            for k, v in (line.split(":", 1) for line in lines[1:] if line)
        )
        size = int(headers.get("content-length", "0"))
        if not 0 <= size <= 1048576:
            return
        body = await asyncio.wait_for(reader.readexactly(size), 2)
        request = json.loads(body) if body else {}
        record(verb, request, headers)
        method = request.get("method")
        status, kind, extras = 200, "application/json", []
        result = None
        if verb == "DELETE":
            status = 405
        elif method == "initialize":
            sessions += 1
            result = {
                "protocolVersion": "2024-11-05"
                if mode == "wrong-version"
                else "2025-11-25",
                "serverInfo": {"name": "independent-http-peer", "version": "fixture"},
                "capabilities": {"tools": {}},
            }
            extras = [("MCP-Session-Id", f"fixture-session-{sessions}")]
        elif "id" not in request or "method" not in request:
            status = 202
        elif method == "tools/list":
            result = {
                "tools": [
                    {"name": "echo", "inputSchema": {"type": "object"}},
                    {"name": "drop", "inputSchema": {"type": "object"}},
                    {"name": "slow", "inputSchema": {"type": "object"}},
                ]
            }
        elif method == "tools/call":
            name = request["params"]["name"]
            if name == "drop":
                return
            if mode == "session-404" and not expired:
                expired = True
                status = 404
            else:
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": request["params"]["arguments"].get(
                                "text", "compat-exact"
                            ),
                        }
                    ]
                }
        else:
            status = 400
        encoded = (
            json.dumps(
                {"jsonrpc": "2.0", "id": request.get("id"), "result": result},
                ensure_ascii=False,
            ).encode()
            if result is not None
            else b""
        )
        if (
            mode in ("sse", "server-request")
            and result is not None
            and method != "initialize"
        ):
            kind = "text/event-stream"
            prefix = b": bounded-keepalive\r\n\r\nid: ignored\r\ndata:\r\n\r\n"
            if mode == "server-request" and method == "tools/call":
                prefix += (
                    b'data: {"jsonrpc":"2.0","id":"peer-request",'
                    b'"method":"sampling/createMessage","params":{}}\n\n'
                )
            encoded = prefix + b"event: message\ndata: " + encoded + b"\n\n"
        fields = [
            ("Content-Type", kind),
            ("Content-Length", str(len(encoded))),
            ("Connection", "close"),
        ] + extras
        writer.write(
            f"HTTP/1.1 {status} Synthetic\r\n".encode()
            + b"".join(f"{k}: {v}\r\n".encode() for k, v in fields)
            + b"\r\n"
        )
        await writer.drain()
        if method == "tools/call" and request["params"]["name"] == "slow":
            await asyncio.sleep(2)
        for pos in range(0, len(encoded), 7):
            writer.write(encoded[pos : pos + 7])
            await writer.drain()
            await asyncio.sleep(0)
    except (ValueError, ConnectionError, asyncio.IncompleteReadError, TimeoutError):
        pass
    finally:
        writer.close()
        with suppress(Exception):
            await writer.wait_closed()


async def main():
    context = None
    if mode.startswith("tls"):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(
            os.environ["MCP_FIXTURE_TLS_CERT"], os.environ["MCP_FIXTURE_TLS_KEY"]
        )
    async with await asyncio.start_server(
        handle, "127.0.0.1", int(sys.argv[1]), limit=65536, ssl=context
    ) as server:
        await server.serve_forever()


if __name__ == "__main__":
    mode = sys.argv[2]
    asyncio.run(main())
