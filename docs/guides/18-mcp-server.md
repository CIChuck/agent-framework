# Modern MCP tools server

Friday exposes explicitly registered async tools as an MCP `2026-07-28` server
through `friday_mcp.server`. Choose newline stdio for a local subprocess or a
single Streamable HTTP POST endpoint with JSON or request-scoped SSE responses.
These programmatic APIs are separate from the legacy `2024-11-05` server APIs.
Existing server YAML defaults and the `stdio`/`sse` config enum remain unchanged.
For configuring Friday as a client, see [MCP client setup](17-mcp-client.md)
and [MCP migration](19-mcp-migration.md). These APIs implement the pinned
2026-07-28 tools server profile; 2025 HTTP compatibility belongs to the client.
Private fixture interoperability is separate from public deployment or whole
initiative acceptance.

## Register an async tool and serve stdio

```python
import asyncio

from friday_mcp.server import ModernStdioMCPServer, ToolCallResult
from friday_mcp.client.protocol import JSONValue

server = ModernStdioMCPServer()

async def echo(arguments: dict[str, JSONValue]) -> ToolCallResult:
    return ToolCallResult.structured(arguments)

server.register_tool(
    {
        "name": "echo",
        "description": "Return the supplied text",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
    },
    echo,
)

asyncio.run(server.serve())
```

Keep stdout exclusively for protocol messages. Handlers must be cooperative
async functions; synchronous handlers and executor dispatch are rejected.
`ToolCallResult.text(...)` emits text; `structured(...)` accepts any bounded JSON
value, including explicit `None`/JSON null, and includes text for compatibility.
`from_value(...)` accepts complete text blocks, annotations and optional structured
content. Omission of `structuredContent` remains distinct from explicit null.
Successful structured results must satisfy the tool's captured `outputSchema`.
Exceptions yield a fixed safe tool error. No automatic tool retry occurs.

## Use an explicit registry snapshot

`configure_modern_tools_mode(server, registry, tool_filter=["echo"], prefix="demo.")`
uses public Core `ToolRegistry`/`ToolDefinition` contracts, preserving the complete
`parameters_schema`. Supply an already populated registry. It publishes a staged,
validated snapshot atomically and rejects collisions or unsupported schemas.
There is no implicit registry loading, refresh, resource listing or agent assembly.
`replace_tools(...)` accepts immutable `RegisteredTool` models; exports are copies.
An issued call retains its definition, handler and output schema during catalog changes.

The supported JSON Schema subset is draft2020-12, regex-free and reference-free:
primitive/object/array types, properties/required/additionalProperties, items/
prefixItems, bounds, numeric constraints and scalar enum/const, plus ordinary
schema metadata. Remote or recursive references, regex, composition/conditionals
and unknown schema keywords are rejected before registration. No constraints are
silently removed and no remote schema retrieval occurs.

## Serve one HTTP endpoint

Install the declared optional server dependencies when provisioning the application.
Imports of legacy and modern stdio exports do not require FastAPI/uvicorn;
HTTP app construction reports a fixed missing-dependency error if unavailable.

```python
from friday_mcp.server import HTTPServerPolicy, StreamableHTTPMCPServer

http_server = StreamableHTTPMCPServer(
    policy=HTTPServerPolicy(
        path="/mcp",
        bind_host="127.0.0.1",
        port=8443,
        allowed_hosts=("127.0.0.1:8443",),
        allowed_origins=("https://127.0.0.1:8443",),
        bearer_token=admin_token,  # supplied explicitly by your application
        require_tls=True,
    ),
    response_mode="sse",  # alternatively "json"
)
# Register the application's explicitly selected tools here.
# In an async application:
# await http_server.serve(certificate=certificate_path, private_key=key_path)
```

`create_app()` returns an application with one exact POST path and lifecycle
shutdown. `serve(...)` owns its listener and shutdown. The TLS certificate/key
paths and in-memory administrative token are explicit caller inputs; Friday does
not discover credentials in files or environment variables. The default bind is
literal127.0.0.1, port8000; allowed Origins default to none, so a supplied Origin
must be explicitly allowed. Absent Origin is permitted. Configure exact Host
and Origin values, including ports. Query strings, ambiguous/duplicate headers,
invalid Host/Origin, wrong bearer credentials and TLS-policy violations fail
before body dispatch. Non-loopback binds require explicit Host/Origin, bearer
and TLS policy; they are outside the private interoperability fixtures.

Authentication is an administrative supplied-bearer profile. The MCP authorization
SHOULD tradeoff is explicit: this implementation does not implement optional
resource-owner OAuth discovery/login, authorization-server roles or delegated
resource metadata, and does not claim those conditional OAuth MUSTs. The local
unauthenticated default is for an explicitly controlled application boundary;
configure the supplied bearer policy for an authenticated endpoint.

Every modern request carries required protocolVersion and clientCapabilities in
`params._meta`. clientInfo is optional, self-reported and never an access decision.
HTTP requests include `Content-Type: application/json`, Accept listing both JSON
and event-stream, `MCP-Protocol-Version`, `Mcp-Method`, and `Mcp-Name` for calls.
Static primitive `x-mcp-header` bindings, including nested property paths, must
match the body. Unicode/unsafe ASCII values use the dated Base64 sentinel.
HeaderMismatch (`-32020`) is an HTTP400 failure before any handler runs.
Malformed or case-insensitive duplicate mirrored parameter headers use this
fixed error as well; pre-body rejection omits the request ID and header values.
Mcp-Method and MCP-Protocol-Version are plain field values: visible ASCII,
space and horizontal tab are permitted and compared exactly with the body.
Other controls, DEL and raw non-ASCII bytes fail with HeaderMismatch before
body parsing or RPC routing. These two fields do not use Base64 decoding;
Mcp-Name and Mcp-Param values retain their separate sentinel encoding rules. Unknown
methods return HTTP404/`-32601`; unsupported versions HTTP400/`-32022` with bounded
supported/requested data. GET/DELETE return405. There are no protocol sessions,
GET event streams, session cookies/IDs, `/message` split endpoints or redirects.

## Discovery, limits and lifecycle

`server/discover` always advertises only tools. Discovery and every tools/list
page include required `ttlMs: 0` and `cacheScope: "private"`: immediately stale
and confined to the authorization context. There is no result-cache storage,
reuse or caching RPC. tools/call results do not carry those cacheable-only fields.
Calls require no prior discovery or initialize handshake. Tool names remain
case-sensitive and unique. ASCII names of1–128 characters are recommended;
bounded Unicode names are accepted deliberately and mirrored with sentinel
encoding rather than silently rewritten.

`ServerLimits` provides lower-only bounds: request/result wire64KiB, depth32,
nodes8192, catalog1MiB/256 tools/16 pages/64 tools per page,32 active operations,
headers16KiB, IDs/protocol-version strings256 bytes, cursors256 bytes,30s operation timeout and0.5s shutdown
settlement. Individual schemas are additionally capped at8KiB/256 schema nodes,
with bounded instance-validation work. Lower incompatible bounds fail before
publishing a partial catalog. Catalog pages account for the actual encoded wire
and worst permitted ID; opaque cursors expire when the catalog changes.
Admission bounds simultaneous invocations and tool starts per second, both
to active_requests (default32). The per-instance rolling one-second start window
persists across restart; denied starts have no handler span. Deployment-wide
policy remains an application responsibility. Deadlines include body/admission/handler/delivery work.
For stdio, the first frame byte starts the absolute deadline. Fragments and
oversized-frame discard retain that deadline; an expired partial frame closes
the connection before handler admission. Waiting on an idle connection consumes
no frame budget.

Stdio cancellation targets only the connection's pending request. HTTP disconnect
cancels only its originating POST. Stop closes streams/listeners and cancels owned
work; cancellation-resistant handlers, serving loops and output work remain tracked.
Stdio rejection delivery has a separate bounded pool of at most active_requests
tasks and shares the serialized output lock with admitted requests. The reader
continues processing cancellation and EOF while output is blocked. If that pool
is full, the connection closes instead of accumulating queued rejection work.
Signal registrations, streams and teardown belong to their connection generation. Incomplete settlement raises
a fixed TimeoutError and blocks unsafe restart until a later stop successfully
drains the owners. A restarted connection cannot publish an old reply or remove
its new owner. Python async cancellation requires cooperative handler behavior.

Optional `telemetry=...` accepts the existing public TelemetryInterface. It creates
one handler span with fixed method/outcome and a bounded hash of the registered
tool identity, without raw IDs, tool names,
arguments/results/schemas, credentials, URLs or client trace data. Observer failure
cannot replay a handler. No provider/exporter is created and Langfuse is optional
future work. Unsupported server profiles include2025 compatibility, prompts,
resources/media, agent mode, Tasks, subscriptions, input_required/MRTR callbacks,
sampling/roots/elicitation, logging RPCs and OAuth. Existing legacy APIs remain
available through their original names and semantics.

The server validates reserved trace metadata against the W3C field formats
([Trace Context](https://www.w3.org/TR/trace-context/),
[Baggage](https://www.w3.org/TR/baggage/)) but discards it at the handler and
observation boundary. It does not participate in or propagate a peer trace.
Unknown/completed/malformed stdio cancellation notifications are ignored, and
notifications receive no stdio response. The cancellation-reason logging SHOULD
is deliberately declined because peer reasons can contain credentials or PII.
HTTP has no core client notification to accept in this profile. Legacy initialize
requests are rejected under the mandatory modern metadata grammar; discovery
and unsupported-version errors provide the supported version rather than a
legacy handshake. The version-hint-on-initialize-error SHOULD is declined for a
uniform fixed-error policy. Application consent/UI policy remains with the
explicit tool owner; this server never loads arbitrary application tools.
Do not annotate sensitive parameters with x-mcp-header: intermediaries see them.

Unsupported-version errors carry exactly `data.supported` and `data.requested`
according to the pinned2026 error schema; discovery separately uses
`supportedVersions`. The bounded requested version appears only in its own wire
error data, with a fixed diagnostic message and no telemetry label. The server
refuses requestState/inputResponses and cannot construct the inactive missing-
client-capability error without an activated optional role. Complete tool/text/
result metadata is format-validated before emission; registered tool metadata
and trusted custom result metadata are immutable snapshots.

HTTP ownership includes response writes: a blocked send remains owned, disconnect
cancels only its request, and attempted headers are never replayed. The original
operation deadline covers successful body/handler/delivery work. A fixed terminal
timeout rejection may use only the remaining shutdown-settlement window measured
from that original deadline; it cannot restart a handler or extend its deadline.
If a response write already started, timeout closes that operation without a
second response. Cooperative cancellation is required of the ASGI transport.
