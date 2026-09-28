"""Deterministic stdio peer for WS-02 lifecycle tests; never contacts a network."""

import json
import sys
import time


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "good"
    print("SENTINEL-STDERR-SECRET", file=sys.stderr, flush=True)
    for line in sys.stdin:
        message = json.loads(line)
        if "id" not in message:
            continue
        method = message["method"]
        if mode == "exit":
            return
        if method == "initialize":
            if mode == "handshake_timeout":
                time.sleep(10)
            if mode == "handshake_fail":
                reply = {"error": {"code": -1, "message": "SENTINEL-PEER-SECRET"}}
            else:
                reply = {
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "fake", "version": "1"},
                    }
                }
        elif method == "tools/list":
            if mode == "list_timeout":
                time.sleep(10)
            if mode == "list_fail":
                reply = {"error": {"code": -1, "message": "SENTINEL-PEER-SECRET"}}
            else:
                reply = {
                    "result": {
                        "tools": [
                            {
                                "name": "probe",
                                "description": "Untrusted fake server tool",
                                "inputSchema": {"type": "object", "properties": {}},
                            }
                        ]
                    }
                }
        else:
            reply = {"result": {}}
        print(json.dumps({"jsonrpc": "2.0", "id": message["id"], **reply}), flush=True)


if __name__ == "__main__":
    main()
