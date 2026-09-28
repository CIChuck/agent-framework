"""Deterministic stdio peer for WS-02 lifecycle tests; never contacts a network."""

import json
import os
import signal
import sys
import time


def flood_outputs() -> None:
    """Bounded producer chunks, intentionally oversized unterminated stdout."""
    chunk = b"SENTINEL-OUTPUT-SECRET" * 128
    for descriptor in (2, 1):
        for _ in range(512):
            remaining = memoryview(chunk)
            while remaining:
                remaining = remaining[os.write(descriptor, remaining) :]
    time.sleep(30)


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "good"
    if mode.startswith("noisy_"):
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
    print("SENTINEL-STDERR-SECRET", file=sys.stderr, flush=True)
    for line in sys.stdin:
        message = json.loads(line)
        if "id" not in message:
            continue
        method = message["method"]
        if mode == "exit":
            return
        if method == "initialize":
            if mode == "noisy_handshake":
                flood_outputs()
                return
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
            if mode in ("list_fail", "noisy_list_fail"):
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
        if method == "tools/list" and mode.startswith("noisy_"):
            flood_outputs()
            return


if __name__ == "__main__":
    main()
