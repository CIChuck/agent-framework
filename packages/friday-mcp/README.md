# Friday MCP

MCP tools clients, transports and programmatic servers. Use the protocol APIs directly or let Friday Runtime own discovery, tool admission, diagnostics and lifecycle.

**Distribution:** [friday-framework-mcp](https://pypi.org/project/friday-framework-mcp/) · **Import:** `friday_mcp`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-mcp==0.1.0a4"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: a local tools server and client

These two files use installed packages and an owned local subprocess. They require no network, credentials or model. Save this as `server.py`:

```python
import asyncio
from friday_mcp.client.protocol import JSONValue
from friday_mcp.server import ModernStdioMCPServer, ToolCallResult

server = ModernStdioMCPServer()

async def echo(arguments: dict[str, JSONValue]) -> ToolCallResult:
    return ToolCallResult.text(str(arguments["message"]))

server.register_tool(
    {
        "name": "echo", "description": "Echo a message",
        "inputSchema": {
            "type": "object", "properties": {"message": {"type": "string"}},
            "required": ["message"], "additionalProperties": False,
        },
    },
    echo,
)

asyncio.run(server.serve())
```

Save this beside it as `client.py`, then run `python client.py`:

```python
import asyncio
from pathlib import Path
import sys
from friday_mcp.client.stdio import StdioMCPClient

async def main() -> None:
    async with StdioMCPClient(
        name="demo", command=sys.executable,
        args=["-u", str(Path(__file__).with_name("server.py"))],
        protocol_profile="modern",
    ) as client:
        await client.list_tools()
        print(await client.call_tool("echo", {"message": "Hello from MCP"}))

asyncio.run(main())
```

Expected output: `Hello from MCP`. Keep server stdout exclusively for protocol messages. Always await client/server teardown. This is a tools-profile demonstration, not whole-protocol conformance.

## Supported roles and profiles

| Role | Implemented transport/profile |
| --- | --- |
| Modern programmatic client | Explicit `2026-07-28` stdio and Streamable HTTP |
| Compatible HTTP client | Explicit `2025-11-25`, including initialization/session handling |
| Modern programmatic server | `2026-07-28` stdio or Streamable HTTP |
| Retained legacy clients/server APIs | `2024-11-05` compatibility, including legacy HTTP+SSE |
| Integrated Runtime/Chat client | Configured stdio; explicitly opted-in HTTPS Streamable HTTP |

Legacy HTTP+SSE is not the modern Streamable HTTP transport. Stdio configuration defaults to legacy compatibility; select `modern` or `auto` explicitly. HTTP requires a dated version and matching admission policy. The official `mcp` SDK is a development interoperability dependency, not Friday's production protocol implementation.

The optional `server` extra installs standalone HTTP server dependencies: `python -m pip install "friday-framework-mcp[server]==0.1.0a4"`. `full` adds broader Friday integrations; extras do not activate remote peers.

## Integrated Runtime/Chat configuration

`tools.providers.mcp` configures Friday as a **client**, not as a server. It is disabled by default. The client guide contains complete `config.yaml` examples for stdio and dated HTTPS profiles, remote/global opt-ins, environment credential references and canonical tool filters.

Runtime owns startup/reconnect discovery and registration. A required missing selected tool can stop startup even for an optional peer. Use public stop/start for integrated rediscovery. Programmatic clients also offer explicit generation-bound catalog refresh; it never replays a tool call and is not an automatic subscription.

## Boundaries to understand

- These are bounded **tools** profiles. Modern clients do not advertise roots, sampling, elicitation or Tasks; interactive `input_required` continuation is unsupported. Integrated resources/prompts are not implemented. Do not claim complete MCP conformance.
- Modern text and structured JSON results are supported within dated rules. Unsupported media/resources and interactive continuation fail explicitly; no implicit URL/resource fetching occurs.
- Output-schema validation supports a bounded JSON Schema 2020-12 subset; external references, regex and unsupported constructs are rejected, not silently ignored.
- Default client ceilings include 1 MiB frames/catalog aggregate, 64 KiB tool results, four pending requests, 16 catalog pages and 256 tools. Runtime adds stricter admission/schema caps. User limits only lower the applicable modern ceilings.
- Remote clients require verified HTTPS and per-connection address policy. No redirects, environment proxies, TLS relaxation or automatic failed-call replay. Bearer credentials are explicit; OAuth discovery/login is not implemented.
- The modern HTTP server has one POST endpoint with explicit Host/Origin/bearer/TLS policy. It does not supply protocol sessions, a cache engine or OAuth login. Authentication and deployment remain application responsibilities.

See the guides for the full role/revision matrix, server lifecycle, protocol-specific errors, schema/result limits, security policy and controlled migration.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-mcp/tests_mcp -q
```

## Documentation and support

[Client configuration](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/17-mcp-client.md) · [Server APIs](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/18-mcp-server.md) · [Protocol migration](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/19-mcp-migration.md) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-mcp/src/friday_mcp) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
