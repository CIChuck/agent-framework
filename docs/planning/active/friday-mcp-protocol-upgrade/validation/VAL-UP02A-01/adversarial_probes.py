"""Readable presentation of the original independent diagnostic probe.

Original executed bytes are preserved losslessly in
artifacts/adversarial_probes.py.gz and recorded in stored-manifest.json.
This presentation changes formatting only and was not used for the review.
"""

import asyncio
import json

from friday_mcp.client.base import MCPClientBase
from friday_mcp.client.protocol import (
    MODERN_VERSION,
    CatalogPage,
    Discovery,
    ProtocolLimits,
    ToolResult,
)


def discovery(**kwargs):
    return {
        "resultType": "complete",
        "supportedVersions": [MODERN_VERSION],
        "capabilities": {"tools": {}},
        "ttlMs": 0,
        "cacheScope": "private",
        **kwargs,
    }


class SyntheticTransport:
    def __init__(self, error):
        self.error = error
        self.messages = []
        self.queue = asyncio.Queue()

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    async def receive(self):
        return await self.queue.get()

    async def send(self, message):
        self.messages.append(message)
        if "id" not in message:
            return
        if message["method"] == "server/discover":
            reply = {
                "error": {
                    "code": self.error,
                    "message": "synthetic rejection",
                    "data": {"requiredCapabilities": {"elicitation": {}}},
                }
            }
        else:
            reply = {
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "synthetic", "version": "1"},
                }
            }
        await self.queue.put({"jsonrpc": "2.0", "id": message["id"], **reply})


class Client(MCPClientBase):
    def __init__(self, error):
        super().__init__("synthetic", protocol_profile="auto")
        self.wire = SyntheticTransport(error)

    async def _create_transport(self):
        return self.wire


async def main():
    output = {}
    for code in (-32020, -32021, -32022):
        client = Client(code)
        try:
            await client.connect()
            result = {"connected": True, "selected_version": client.negotiated_version}
        except Exception as exc:
            result = {"connected": False, "failure_type": type(exc).__name__}
        finally:
            await client.disconnect()
        result["methods"] = [m["method"] for m in client.wire.messages]
        output[str(code)] = result
    limits = ProtocolLimits()
    probes = {
        "discovery_invalid_meta_key": lambda: Discovery.parse(
            discovery(_meta={"bad prefix/key": "synthetic"}), limits
        ),
        "discovery_malformed_capability": lambda: Discovery.parse(
            discovery(capabilities={"tools": {"listChanged": "not-a-bool"}}), limits
        ),
        "catalog_tool_nonobject_meta": lambda: CatalogPage.parse(
            {
                "resultType": "complete",
                "ttlMs": 0,
                "cacheScope": "private",
                "tools": [
                    {"name": "echo", "inputSchema": {"type": "object"}, "_meta": []}
                ],
            },
            True,
            limits,
        ),
        "tool_result_nonobject_text_meta": lambda: ToolResult.parse(
            {
                "resultType": "complete",
                "content": [{"type": "text", "text": "ok", "_meta": []}],
            },
            True,
            limits,
        ),
        "tool_result_malformed_annotations": lambda: ToolResult.parse(
            {
                "resultType": "complete",
                "content": [
                    {"type": "text", "text": "ok", "annotations": {"priority": "high"}}
                ],
            },
            True,
            limits,
        ),
        "result_invalid_meta_key": lambda: ToolResult.parse(
            {
                "resultType": "complete",
                "_meta": {"bad prefix/key": 0},
                "content": [{"type": "text", "text": "ok"}],
            },
            True,
            limits,
        ),
    }
    for name, call in probes.items():
        try:
            value = call()
            output[name] = {"accepted": True, "type": type(value).__name__}
        except Exception as exc:
            output[name] = {"accepted": False, "failure_type": type(exc).__name__}
    print(json.dumps(output, indent=2))


asyncio.run(main())
