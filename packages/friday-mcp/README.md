# Friday Framework MCP

`friday-mcp` provides protocol-level MCP clients, transports and server APIs.
Its programmatic clients support stdio, Streamable HTTP and legacy SSE. The
integrated Friday runtime supports local stdio and explicitly admitted HTTPS
Streamable HTTP peers. The runtime owns discovery,
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
integrated runtime YAML default to legacy behavior. YAML may explicitly select
`protocol_profile: modern` or `auto`. Modern stdio is
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

Streamable HTTP and remote YAML admission are available through the Runtime
provider described below. A modern Friday server remains a separate construction
unit. Existing programmatic HTTP+SSE remains legacy. Client integration does not
claim whole-initiative or optional-feature conformance.

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
## Streamable HTTP programmatic client

`StreamableHTTPMCPClient` supports explicit MCP `2026-07-28` and `2025-11-25`
tools profiles. It is a separate transport from the retained 2024 HTTP+SSE
client. Runtime/Chat `config.yaml` can select either dated HTTP profile explicitly
with the matching global remote policy and per-peer `trust_level: remote`. Local
stdio and disabled-provider defaults are preserved.

```python
from friday_mcp.client import HTTPEndpointPolicy, StreamableHTTPMCPClient

client = StreamableHTTPMCPClient(
    "https://mcp.example.com/mcp",
    protocol_version="2026-07-28",
    endpoint_policy=HTTPEndpointPolicy(),
    # Optional bearer_token is supplied explicitly by your secret provider.
)
async with client:
    tools = await client.list_tools()
    # Call only a discovered tool, using its real name and validated arguments.
    # result = await client.call_tool("example_tool", {"argument": "value"})
```

Modern calls require a complete successful catalog first, so all declared
`x-mcp-header` fields are mirrored. Invalid HTTP annotations exclude only that
tool; `rejected_http_tools` exposes a bounded count. Failed/malformed catalog
refresh invalidates the catalog and header bindings. Header extraction follows
only reachable argument properties. Annotations in other schema-bearing locations,
including `contentSchema`, exclude the tool; example/default/const JSON stays opaque.
The full catalog is validated before publishing tools, bindings or rejected counts.
Absent/null values are omitted, and unsafe/Unicode or
sentinel-shaped values use exact UTF-8 Base64 encoding. Structured/text output
uses the accepted bounded core adapter and schema validator, including preserving
the call's output-schema snapshot across concurrent catalog invalidation.

Modern HTTP has no initialize, protocol session, GET stream or resumption.
The explicit `2025-11-25` mode initializes and retains an origin-scoped in-memory
session when supplied. A session 404 starts bounded fresh initialization, but
the failed call is never replayed. The next explicit call needs a healthy new
session. Recovery is serialized per connection generation: delayed failures and
expired waiters from an old session cannot invalidate a newer healthy session or
catalog. Failed recovery stays disconnected until an explicit `connect()`.
2025 input schemas use JSON Schema 2020-12 by default or by explicit
`$schema: https://json-schema.org/draft/2020-12/schema`; malformed or unsupported
dialect declarations fail with `unsupported_schema` before catalog publication.
No schema URI is fetched. This preserves permissive 2024 parsing.
2025 metadata objects and key grammar are checked at received request/notification
parameters, result, Tool and TextContent boundaries. Valid metadata values stay
opaque, including reserved keys; application JSON is not recursively interpreted.
Older structured results/output schemas must be objects; legacy bare
string content is not accepted as a 2025 content block. Unsupported content and
input requests fail safely, without resource retrieval or interactive continuation.

Production policy requires verified HTTPS. URLs are ASCII/punycode with encoded
paths, no query/userinfo/fragment, and default port 443. Other ports and exact
private addresses need explicit `HTTPEndpointPolicy` opt-ins for that peer.
Every new connection resolves and validates all returned addresses, then connects
to a validated numeric address with the original TLS hostname. Mixed public/
disallowed answers fail closed. Redirects, environment proxies and cookies are
unused; credentials remain on the configured origin. A typed borrowed resolver/
connector is a trusted application dependency, never an arbitrary HTTP client.
Its returned streams belong to this client; the provider itself remains open.

`ProtocolLimits` and `HTTPLimits` accept positive lower-only ceilings: four owned
requests, 30 seconds, 16 pages/256 tools, 1 MiB aggregate catalog and frame/wire,
64 KiB tool result/header/line, 256 SSE events/comments and depth 32/4096 JSON
nodes. Raw HTTP wire accounting includes framing/headers; httpcore/h11 also has
a stricter 16 KiB incomplete-header parser bound. SSE comments, progress and
priming events never reset the deadline. There is no HTTP pool retry or mutating
call replay. Cancellation closes only the modern request stream; compatible
cancellation notifications require a fully issued non-initialize request.

httpcore's DEBUG mode exposes response headers. This profile fails closed when
its transport DEBUG logging is enabled, checks again through its public request
trace hook, and never changes application logger levels, filters or providers.
Turn transport DEBUG logging off in application configuration to use the client.
No payload/header logging, automatic W3C trace/baggage propagation or telemetry
provider changes are introduced.

`outstanding_http_owners` includes request/cleanup tasks and retained partial
streams. Incomplete teardown raises a fixed cleanup failure, retains ownership,
and allows a later `disconnect()` retry. A teardown failure does not replace an
existing request failure. Always await shutdown; no background owner is silently
forgotten. Fixture-only plaintext HTTP is restricted to an explicitly allowlisted
literal 127.0.0.1/port and cannot relax production TLS.


### Runtime factory ownership

`friday_mcp.client.MCPManagedServer` is a frozen name/enabled/client-factory
record. `MCPClientManager(config, managed_servers=entries)` owns the complete
ordered entry list; config.servers must be empty in that mode. Duplicate names
and invalid entries fail before invocation. The default MCPConfig API retains
stdio/SSE compatibility. Factories return MCPClientBase; the manager adopts the
client before connecting and retains incomplete cleanup owners for public retry.
Runtime uses this typed seam, without injecting clients into private dictionaries.


### Explicit manual catalog refresh

The client package exposes the optional typed `MCPRefreshClient` contract and
immutable `MCPCatalogSnapshot`. `refresh_tool_catalog()` returns the exact complete
generation produced by that operation; `current_catalog_snapshot` is `None`
while refresh is in progress or after failure. Exported tool dictionaries are
independent copies. A generation identifies wire definitions, output schemas
and HTTP argument-header bindings; it does not grant tool admission.

```python
from friday_mcp.client import MCPToolAdapter

adapter = MCPToolAdapter(client)  # connected, explicitly configured client
tools = await adapter.get_tools()
fresh_tools = await adapter.get_tools(refresh=True)
```

A failed refresh clears usable cached definitions. Previously created wrappers
fail with `catalog_unavailable` before issuing a call after failure, removal or
reconnect. An already-issued call settles once against its captured output schema
and HTTP header bindings. Refresh never replays a tool call. An explicit successful
refresh creates new wrappers; code should replace its own programmatic references
after applying its existing admission rules. Custom clients implementing only the
original MCPClient contract remain supported, without generation guarantees.

Runtime and Chat retain startup/reconnect discovery and transactional registration.
They expose no in-place refresh YAML option or automatic list-change subscription.
Use their public stop/start lifecycle for integrated rediscovery. Existing selection,
filters, collision and schema/token budgets, provenance, quarantine, transcripts,
explicit memory opt-in and injected provider-neutral telemetry remain controlling.

### Dated tool results and optional features

Modern MCP2026-07-28 preserves ordered text and structured JSON values, including
null, scalars and arrays; omitted structured content remains distinct from null.
Mixed text/structured results use the bounded deterministic JSON envelope. Explicit
2025-11-25 HTTP structured content remains object-only. Both dated profiles validate
complete content/tag/metadata shapes before classifying ordinary tool errors. A
well-formed tool error needs no successful structured output; malformed error
content is an invalid result. The output-schema subset remains bounded JSON Schema
2020-12 with no network reference retrieval or regex evaluation.

Valid image/audio/resource-link/embedded content returns `unsupported_content`;
malformed variants are invalid results. No media decoding, URL retrieval or resource
fetch occurs. Valid modern input requests return `input_required_unsupported`,
with no callback, opaque-state forwarding or interactive continuation.

Friday advertises no Tasks capability. In the explicit2025 profile, tools declaring
`execution.taskSupport: required` are excluded; attempts to call an observed
excluded tool return `unsupported_task` before I/O. Absent, forbidden and optional
task support remain ordinary tool candidates. This dated field does not enable a
modern extension. No Tasks RPC, polling, persistence, subscriptions, automatic
refresh, cross-call result cache or outgoing trace/baggage is added. This tools-client
profile and SDK fixture interoperability do not claim whole MCP conformance.

The accepted2025 raw `call_tool` API permits a later explicit call after session
recovery, without replaying the failed call. It retains the prior output schema
for that raw call; generation-bound wrappers stay invalid and current catalog
snapshot stays unavailable until explicit rediscovery. Manual refresh failure or
explicit disconnect clears this compatibility data. Runtime/Chat wrappers use
public stop/start rediscovery after recovery.

Custom MCPClientBase subclasses that override raw `list_tools` or `call_tool`
keep their virtual APIs. `supports_catalog_refresh` defaults to false for these
subclasses; they may explicitly opt in when their optional refresh/generation
methods implement this contract. Other custom clients can implement the declared
MCPRefreshClient protocol directly.
