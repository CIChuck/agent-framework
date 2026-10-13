# UP-05 modern tools-server contract

Status: Proposed; exact CD-MCP-UP-005 construction approval is separate.
Target: MCP2026-07-28 tools-only server over stdio and Streamable HTTP.
The complete official captures and TypeScript schema selected at upstream
`271ecc9accafdd9b83a3c869fa67c22953b2af80` control interpretation.

## Roles, APIs and compatibility

Add typed `ModernToolsMCPServer`, `ModernStdioMCPServer`,
`StreamableHTTPMCPServer`, `ServerLimits`, explicit HTTP policy and immutable
registered-tool/result models under `friday_mcp.server`. Export new names from
that stable module. Keep root-package imports, configuration enums/settings,
legacy base/stdio/SSE/agent/tools modules and their2024-11-05 behavior unchanged.
Remove the existing suppression from the modified server/__init__.py; all new
source and modified export code must pass typing without new suppression/casts.
Do not add a modern profile flag to legacy classes or reinterpret existing YAML.
Modern server supports2026-07-28 only;2025 compatibility remains client-side.
No initialize/initialized handshake, GET event stream, protocol sessions,
Mcp-Session-Id, DELETE session endpoint or SSE /message split in the modern API.

Only explicit tool registration and a separately named typed registry bridge are
available. Use public friday_core ToolRegistry/ToolDefinition contracts. Respect
explicit filters/prefixes, reject collisions, snapshot and validate definitions
before atomic registration. No implicit agent, prompt/resource listing, memory,
model tools or registry loading. A real DefaultToolRegistry populated with only
synthetic tools must exercise the bridge. Modern server imports must preserve
legacy/stdio use when optional HTTP dependencies are unavailable; HTTP app
construction gives a fixed dependency error, never installs packages.

## Request metadata, discovery and wire errors

Bound and validate the complete JSON-RPC envelope, duplicate JSON members,
UTF-8/finite JSON values, mandatory variant fields and omitted/null distinctions
before dispatch. IDs are bounded strings or integers, never bool/float/null
requests. Separate notifications and parse/invalid-request error IDs as defined
by the pinned schema. Never mistake an incoming response, batch or malformed
object for a request. Unknown extensions remain bounded, unused data.

Every modern request requires params._meta protocolVersion and clientCapabilities;
clientInfo is optional, validates Implementation when present, and grants no
security/admission authority. Capabilities are per-request; never retain an earlier
client's capabilities/identity as authority for another operation. Validate the
separate NotificationMetaObject grammar rather than requiring request-only fields
on notifications. Do not forward arbitrary trace, input state or metadata to tools.

Implement server/discover (even with no tools), tools/list and tools/call. Discovery
returns complete resultType, supportedVersions [2026-07-28], honest tools capability
and fixed software identity in the dated result metadata. Never advertise optional
callbacks, Tasks, subscriptions/caching/logging, prompts/resources or agent mode.
Clients may call an RPC without prior discovery; do not require hidden session state.
No caching TTL/cacheScope is supplied in this profile.

Use typed server wire errors with fixed messages: ParseError -32700, InvalidRequest
-32600, MethodNotFound -32601, InvalidParams -32602, InternalError -32603;
HeaderMismatch -32020 only for actual HTTP header validation, and
UnsupportedProtocolVersion -32022 with only supportedVersions safe data.
MissingRequiredClientCapability -32021 has its pinned meaning, not a Friday local
failure meaning; this tools-only server requires no optional client capability.
Do not copy friday_core MCPError/local exception codes or str(exception) onto wire.
No peer body/header/credential, schema, exception cause or callback detail appears
in diagnostic errors/logs/telemetry. Valid wire IDs are echoed only on their own
response; malformed/notification errors follow the exact dated grammar.

## Catalog, arguments and results

Use immutable bounded registered definition/handler snapshots with one catalog
revision. Public exports are copies, never mutable aliases. Tool names/descriptions,
inputSchema, optional outputSchema/annotations and result metadata obey the pinned
Tool/CallTool schema. Validate supported JSON Schema subset before registration;
block remote/recursive reference retrieval, regex evaluation hazards and unsupported
schema constructs. Empty reference registry and bounded evaluation are mandatory.
Do not silently drop constraints or header annotations in registry conversion.

Pagination is deterministic, count- and byte-aware, with bounded opaque cursors
bound to the catalog revision. Invalid, oversized, forged, obsolete/cyclic cursor
requests fail locally without invoking a handler or publishing a partial catalog.
Do not add subscriptions or implicit registry refresh. Registration/removal updates
are atomic; configuration failure preserves the previous complete catalog.

Capture the selected definition, output schema and handler before awaiting tool
execution. Validate bounded arguments against that definition before the handler;
unknown/removed/filtered names and malformed arguments execute zero times. Invoke
an async handler once, never retry after disconnect/error/header mismatch. In-flight
calls retain their captured schemas even if registration changes. Registration of
synchronous blocking handlers is rejected or explicitly adapted without violating
owned cancellation; do not add an unbounded thread/executor path.

Return typed complete text/structured results with exact omitted-versus-null
structuredContent semantics and deterministic content ordering. Validate every
emitted variant and actual encoded wire size. Declared output schema validates
successful structured output against the captured definition; a legitimate isError
result has no success-schema requirement. Handler exceptions produce a fixed safe
tool error, not raw Python errors or schema-free malformed output. No input_required,
interactive fulfillment, inputResponses fabrication or server-to-client RPC is
emitted. Tool output stays on wire; raw content remains absent from diagnostics.

## Transport and access boundaries

Modern stdio is newline-delimited UTF-8 JSON-RPC only on stdout; fixed diagnostics
use stderr. Concurrent owned dispatch keeps the reader responsive to cancellation.
Handle split writes, malformed/oversized lines, invalid bytes, duplicate active IDs,
EOF, read/write failures, partial startup, stop/restart and SIGTERM without orphans.
An old task cannot publish into a newer connection or remove a newer owner.

Streamable HTTP has one exact configurable POST endpoint, application/json or
request-scoped text/event-stream final responses. Exercise both response modes;
there is no global event stream. Enforce JSON Content-Type, Accept, bounded body
streaming and duplicate/case-insensitive header handling. Valid unsupported methods
return HTTP404/-32601; unsupported versions HTTP400/-32022. Header failures are
HTTP400/-32020. GET/DELETE return405 and do not create sessions. Accepted
notification mechanics are202/no body; unsupported/malformed notifications return
appropriate HTTP error using notification-error grammar, without dispatch. Modern
HTTP defines no core client cancellation notification; disconnect cancels only the
corresponding operation. Never emit server-sent cancellation outside subscription
semantics, which this profile does not implement.

Validate MCP-Protocol-Version and Mcp-Method on each request, and Mcp-Name when
applicable, against the body before handler admission. Implement exact Base64
sentinel decoding, case rules and duplicate rejection. Validate every recognized
Mcp-Param-* binding derived from valid static primitive x-mcp-header annotations,
including nested properties, Unicode/marker encoding, null/absent omission,
booleans/numbers/safe integer bounds and collisions. Unknown headers do not grant
trust or route tools. HeaderMismatch must always occur before any handler side effect.
Do not use Friday client encoding helpers as the sole negative-test oracle.

Explicit typed HTTP policy validates configured path/bind/authority/Origins before
startup and Host/Origin/access credentials before parsing/dispatch. Invalid Origin
returns403, invalid authority/ambiguous access headers fail closed, and missing/wrong
configured bearer access returns401 with fixed safe diagnostics. Default local bind
is literal127.0.0.1; wildcard/non-loopback use requires explicit host/origin access
policy, bearer gate and TLS, and is never run in this packet's fixtures. No wildcard
Origins, query credentials, redirects, clientInfo trust or token forwarding.
Supplied bearer secrets are in-memory, non-repr and compared safely; no credential
file/environment discovery. This is the existing bounded administrative access
profile, not delegated resource-owner OAuth. Optional MCP OAuth discovery/login/
resource metadata, authorization-server roles and live deployment remain deferred.
Record the authorization SHOULD tradeoff explicitly; do not claim OAuth conformance
or mark its conditional MUSTs implemented by the static gate.

## Limits, lifecycle and observation

ServerLimits defaults are lower-only: depth32/nodes8192, incoming request and tool
result wire64KiB, catalog1MiB/256 tools/16 pages, at most64 tools per page,
32 owned active requests and16KiB aggregate HTTP headers. Registration must ensure
all page byte/count limits can complete the catalog; lowered incompatible bounds
fail configuration instead of silently truncating. IDs/cursors/identity strings
are individually bounded. Timeouts default30s per owned operation and0.5s shutdown
settlement; configuration rejects bool/nonfinite/nonpositive or increased caps.
Deadline starts before operation waits/body processing and is never reset by phase.

Request identity belongs to a connection/POST owner, not a globally reusable ID.
Admission and lock waits are bounded. Stdio cancellation references only that
connection's pending request; HTTP disconnect owns only its request-scoped response.
Stop closes input/listeners/streams, cancels and settles owned tasks. Incomplete
settlement retains honest bounded owners and blocks unsafe restart until explicit
retry drains them. Never clear a task set to claim shutdown. Already-issued calls
are not replayed; unrelated operations continue when another request cancels.

Optional constructor injection uses existing public TelemetryInterface; no provider
creation/global registration/exporter/Langfuse import. One admitted handler yields
one start/terminal observation with bounded trusted method/tool/outcome fields.
Invalid requests do not invoke a tool or create duplicate tool spans. Never capture
auth headers/tokens, raw client IDs/metadata, arguments/results/schema, trace state,
URLs or Python error messages. Observer failure must not change handler ownership
or trigger replay. Test two independent instances for state/provider isolation.

## Verification and stop gates

Before source edits, freeze a complete server-role clause/field/variant plan from
all19 captured inputs. Reassess earlier client-only server exclusions; prior393
keyword/241 paragraph and98-interface/231-field ledgers are historical evidence,
not proof for the new server role. Map every applicable MUST/SHOULD and dependent
schema field to a positive/negative/omitted/null assertion or explicit supported-role
exclusion. Final ledger maps actual source/test/command evidence, with honest counts.

Official SDK2.3.0 Client must talk over real stdio subprocess and verified private
literal127 TLS HTTP JSON/SSE to Friday's server, not an SDK server or in-process
shortcut. Pin mode2026-07-28, disable SDK cache/interactive callbacks/extensions,
inspect actual wire discovery/metadata and avoid synthesised discovery as proof.
Use public session/request APIs for malformed traffic to prevent automatic SDK
HeaderMismatch retry/input drivers from masking zero-invocation negatives. Count
handler starts/finishes and streams/processes/owners; preserve all failed attempts.

Repeat the entire bound20-command profile on a stable corrected candidate against
accepted UP04 baselinef876603. Preserve original controllers/reports/captures,
accepted client/Runtime/Chat/telemetry/security/provenance behavior,19 metadata
hashes and22009 private library files/192 distributions. All new/touched code must
be Ruff/Mypy clean; full327 Ruff/four Mypy objects, exact skip reasons/locations and
complete normalized warnings match baseline. No checker weakening/waiver/install.
Fresh read-only full-unit review is required. Stop on scope/control drift, unexpected
effects, needed dependency/path expansion or new findings; prepare bounded approved
remediation. VERIFIED precedes completion proposal; acceptance/UP06/publication
remain separate. Planning and fixture success never establish blanket conformance.
