# Friday Framework MCP

`friday-mcp` provides protocol-level MCP clients, transports and server APIs.
Its programmatic clients support stdio and SSE; the integrated Friday runtime
client currently configures **local stdio only**. The runtime owns discovery,
registration, filters, diagnostics and lifecycle. See the
[MCP client guide](../../docs/guides/17-mcp-client.md) for the canonical
`tools.providers.mcp` configuration and Friday Chat use.

## Installation

```bash
pip install friday-framework-mcp
```

The optional `server` extra provides standalone server dependencies. The
`full` extra includes the package's broader protocol integrations; neither
extra enables remote servers in the integrated runtime config.

## Programmatic client

This low-level example uses the repository's local synthetic peer. It runs
from a checkout and does not contact a network:

```python
import asyncio

from friday_mcp import MCPClientManager, MCPConfig, MCPServerConfig

async def main() -> None:
    config = MCPConfig(
        servers=[
            MCPServerConfig(
                name="demo",
                command="python",
                args=["-u", "tests/integration/mcp_fake_server.py", "good"],
            )
        ]
    )

    async with MCPClientManager(config) as manager:
        tools = await manager.get_all_tools()
        print([tool.name for tool in tools])

asyncio.run(main())
```

Run it from the repository root. For an installed application, substitute an
owned local server executable. The integrated
runtime path uses `friday_runtime.config.MCPToolProviderConfig` and imposes
stricter local transport, workspace, filtering, schema and result policies.

The package also exposes programmatic MCP server classes. They are separate
from `tools.providers.mcp`, which configures Friday as a client and does not
expose Friday as a server. Resources, prompts and external config includes
are not implemented by that integrated client.

## License

MIT

## Modern stdio client core

The client-core profile supports MCP **2026-07-28** over stdio and retains
**2024-11-05** initialization compatibility. Current constructors, manager and
integrated runtime YAML continue to select legacy behavior. Modern stdio is
an explicit programmatic choice:

```python
from friday_mcp.client.protocol import ProtocolLimits
from friday_mcp.client.stdio import StdioMCPClient

client = StdioMCPClient(
    name="reviewed-local-server",
    command="/absolute/path/to/server",
    protocol_profile="modern",  # alternatively "legacy" or "auto"
    limits=ProtocolLimits(timeout_seconds=10, concurrent_requests=2),
)
async with client:
    tools = await client.list_tools()
    result = await client.call_tool("reviewed_tool", {})
```

Modern requests carry the dated protocol revision, Friday package identity and
empty client capabilities on every request. Discovery precedes tool requests.
No roots, sampling, elicitation, extensions or subscriptions are advertised.
Self-reported server identity and instructions are retained as bounded untrusted
metadata; they do not authorize actions or enter model context automatically.
`auto` probes modern discovery once, reserving half the remaining connection
deadline for legacy fallback on a non-modern error or timeout. A recognized
modern wire error (`-32020`, `-32021` or `-32022`) remains an error. Calls are never replayed after an
ambiguous failure. Modern stdio rejects server requests without sending a
forbidden client response; legacy unknown requests receive MethodNotFound.

Streamable HTTP, remote YAML admission and a modern Friday server are subsequent
construction units. Existing programmatic HTTP+SSE remains legacy. This first
client-core slice does not claim whole-initiative conformance.

### Resource and result behavior

`ProtocolLimits` is frozen and validates positive values at construction; limits
may only lower the ceilings: 1 MiB per newline-delimited frame, 64 KiB per tool
result/adapted output, depth32, four pending requests, 16 catalog pages, 1 MiB
aggregate catalog wire bytes and 256 tools. JSON boundaries additionally cap
4096 nodes and 4096-bit integers. Byte limits precede stdio JSON decoding;
outgoing encoding and allocation of request waiters are bounded. A single
deadline covers connection/probe/fallback, each request's send+wait, and all
catalog pages. Cancellation of an issued stdio request sends a bounded
notification; initialization is excluded. Existing legacy config timeouts
remain honored, including values above the default 30 seconds.

Catalog failure returns no successful partial catalog and discards retained
schemas. Call `list_tools()` before invoking tools to enable validation against
their declared output schemas. Returned catalogs/capabilities are fresh JSON
snapshots; internal metadata/results are immutable and omit payloads from repr.
Runtime admission still enforces its existing 25-tools-per-server/50-total and
8 KiB input-schema restrictions.

Modern parsing validates metadata objects and key grammar at the declared
result/notification, Tool and supported TextContent locations. It checks typed
server identity (including optional titles/descriptions/website/icons), known
capability flags and extension settings, Tool annotations/icons, and TextContent
audience/priority/lastModified annotations. Unknown metadata values remain
bounded untrusted JSON; reserved fields are typed only in the schema context
that declares them. Optional URLs/icons are shape-checked without fetching.
Application JSON in arguments, structuredContent and schema annotations,
defaults or examples is not recursively interpreted as protocol metadata.
Legacy text extraction and optional-field compatibility remain unchanged.

Modern results require `resultType: complete`; legacy missing tags mean complete.
`input_required` yields fixed `input_required_unsupported`, without a continuation
or fabricated input. Unknown result tags are invalid. Text-only results retain
the string API. Structured-only values return deterministic JSON, including
scalars, arrays and explicit null; absent structured content is distinct from
null. Mixed results return a deterministic JSON envelope with `content` text
blocks and `structuredContent`. Modern non-text blocks yield
`unsupported_content`; no embedded resource, URL or image is fetched. Legacy
mixed text extraction remains compatible; non-text-only output fails explicitly.
The existing local `tool_error`/`invalid_result` identifiers and exception codes
remain local adapter outcomes, never modern wire error meanings. Peer error
message/data are not copied into public errors, logs or telemetry.

### Bounded output-schema profile

Output validation uses JSON Schema 2020-12 by default, `jsonschema==4.25.1` and
an explicit `referencing==0.37.0` registry whose default retrieval refuses
external resources. Schemas are capped at 8 KiB, depth16 and 256 expanded schema
nodes before evaluation. The supported profile includes types, properties,
required/additionalProperties, items/prefixItems, scalar enum/const, string and
array lengths, numeric bounds, metadata annotations, and acyclic local object
JSON-pointer references into `$defs`. Evaluation also caps a conservative
schema/result traversal budget at65536; structured results above256 nodes are
rejected for schema validation. Byte/depth bounds alone are not the work bound.

Other dialects, external references, `$id`, cyclic references, regex/patterns,
compositions/conditionals, uniqueItems/contains, complex enum/const and other
validation keywords yield fixed `unsupported_schema`. Local reference expansion
is bounded even for acyclic duplication. These explicit limitations are part of
the first client profile; unsupported schemas are errors, never silently skipped
validation. Invalid structured output produces `invalid_result`.

The official `mcp==2.3.0` SDK is a **development interoperability counterpart**
used only by the synthetic test fixture. Friday's production client continues
to own its protocol, process lifecycle and provider-neutral telemetry boundaries.
Its necessary IDNA 3.20 dependency change is recorded in approved A01; unrelated
existing versions are preserved. Verification requires the real SDK stdio child,
deterministic legacy peer and full MCP/Runtime/Chat/telemetry regressions.
