"""Deterministic synthetic legacy peer and adversarial framing modes."""

import json
import os
import sys
from pathlib import Path

mode = sys.argv[1] if len(sys.argv) > 1 else "good"


def emit(message: dict) -> None:
    print(json.dumps(message), flush=True)


def record(message: dict) -> None:
    path = os.environ.get("MCP_FIXTURE_COUNTER")
    if path:
        with Path(path).open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(message) + "\n")


def main() -> None:
    late_id = None
    for line in sys.stdin:
        request = json.loads(line)
        method = request.get("method")
        record({"method": method})
        if "id" not in request:
            continue
        request_id = request["id"]
        if method == "server/discover":
            if mode in {"ignore-probe", "late-probe"}:
                late_id = request_id
                continue
            emit(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": "Legacy only"},
                }
            )
            continue
        if method == "initialize":
            if late_id is not None and mode == "late-probe":
                emit(
                    {
                        "jsonrpc": "2.0",
                        "id": late_id,
                        "error": {"code": -32601, "message": "Late old probe"},
                    }
                )
            version = "WRONG" if mode == "bad-version" else "2024-11-05"
            result = {
                "protocolVersion": version,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "legacy-fixture", "version": "fixture"},
            }
        elif method == "tools/list":
            result = {"tools": [{"name": "echo", "inputSchema": {"type": "object"}}]}
        elif method == "tools/call":
            if mode == "oversized":
                sys.stdout.write("X" * 100000 + "\n")
                sys.stdout.flush()
                continue
            if mode == "server-request":
                emit(
                    {
                        "jsonrpc": "2.0",
                        "id": "peer-request",
                        "method": "sampling/createMessage",
                        "params": {},
                    }
                )
            if request["params"]["name"] == "drop":
                sys.exit(0)
            if request["params"]["name"] == "slow":
                continue
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": request["params"]
                        .get("arguments", {})
                        .get("text", "legacy"),
                    }
                ]
            }
        else:
            emit(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": "Unknown method"},
                }
            )
            continue
        emit({"jsonrpc": "2.0", "id": request_id, "result": result})


if __name__ == "__main__":
    main()
