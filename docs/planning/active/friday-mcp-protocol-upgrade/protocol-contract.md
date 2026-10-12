# MCP protocol and transport contract

Status: Approved by Chuck Russell on 2026-10-12; dated target `2026-07-28`.
Sources and implementation decision: [research record](research.md).
Normative authority and required proof: [conformance mapping](conformance-matrix.md).
All applicable mandatory rules of the dated specification/schema control the
declared profile; SDK compatibility alone cannot substitute for conformance.

## Supported profiles

| Role and transport | Revision | Decision and delivery |
| --- | --- | --- |
| Client stdio | `2026-07-28` | Add explicit modern mode and bounded auto-discovery in UP-02A |
| Client stdio | `2024-11-05` | Preserve current default and legacy initialization; test negotiated revision, not just a successful handshake |
| Client Streamable HTTP | `2026-07-28` | Primary remote target, UP-02B; runtime/Chat admission follows UP-03 |
| Client Streamable HTTP | `2025-11-25` | Explicit compatibility mode in UP-02B; separate session/initialization rules and tests |
| Client HTTP+SSE | `2024-11-05` | Existing programmatic API retained; no automatic HTTP-to-SSE fallback and no new integrated-runtime admission |
| Server stdio and Streamable HTTP | `2026-07-28` | Tools-only modern profile in UP-05, independently tested against the SDK client |
| Server stdio / HTTP+SSE | `2024-11-05` | Retain existing legacy entry points during migration |
| Other revisions, transports or optional extensions | Other | Unsupported until separately scoped and tested; SDK support alone does not extend Friday's matrix |

Existing constructors/configuration continue using the legacy stdio default in
UP-02A. Add keyword-only `protocol_profile` on `MCPClientBase` and `StdioMCPClient`
with `legacy`, `modern`, and `auto`; no runtime YAML change in that unit.
`legacy` negotiates only `2024-11-05`; `modern` discovers and requires
`2026-07-28`; `auto` probes modern discovery and can select only the tested
legacy stdio revision. HTTP compatibility will be explicit, not inferred from
a failed tool call. Later runtime configuration will expose these profiles.

## Modern client core

Every request supplies protocol version, Friday client identity and supported
client capabilities in `params._meta`. Identity/version come from the package,
never from credentials or workspace paths. Advertise no sampling, roots,
elicitation or extension capability until implemented. For the legacy profile,
remove today's unsupported roots/sampling claims as well.

Call `server/discover` before tool discovery. Parse supported versions,
capabilities, optional server identity and instructions as bounded untrusted
input. Never treat self-reported identity or instructions as authorization or
automatically place them in model context. A recognized modern version error
stays in the modern path; no supported intersection yields a fixed safe error.
Only the read-only discovery probe can drive stdio fallback. Bound it by the
connection deadline; ignore late probe responses. `auto` may fall back once on
a non-modern error/timeout as specified for stdio, then validates the legacy
initialize response before `notifications/initialized`. No repeated probing.

Require valid JSON-RPC envelopes, matching non-null IDs, exactly one result/error,
integer error codes and bounded result shapes. Reject bool IDs and malformed
metadata. Peer error message/data stay at the untrusted boundary, absent from
exception repr, logs and telemetry. Keep local failure identifiers distinct
from wire errors: the existing local `-32020`/`-32021` exception codes must not
be interpreted or emitted as modern HeaderMismatch/capability errors.

Modern result tags are mandatory; legacy absence means complete. Recognize
`complete` and `input_required`; reject unknown extension tags. This first
profile supplies no automatic interactive handler: input-required results yield
a fixed `input_required_unsupported` outcome, with no continuation, fabricated
input or replay. Request state/input requests remain untrusted and non-repr.

## Catalog and tool results

Walk `nextCursor` until complete, with repeated-cursor detection and a single
deadline across pages. Initial caps: 16 pages, 1 MiB aggregate catalog wire bytes,
256 entries before runtime admission, 64 KiB per tool result, JSON depth 32,
four concurrent requests and 30-second default request deadline. Positive
validated constructor limits may lower these caps; later runtime wiring can
pass its tighter accepted limits. Enforce bytes before JSON decoding and entry/
depth limits before retaining decoded structures. Reject a partial catalog on
failure rather than silently registering an incomplete view. Runtime's existing
25-tools-per-server/50-total and 8 KiB schema admission limits remain controlling.

The public `call_tool(...) -> str` adapter remains compatible. Preserve valid
text extraction for old peers. Internally retain a typed result envelope and
validate structured content against a declared output schema before adaptation.
For a structured-only result return deterministic JSON; for text plus structured
content return a deterministic envelope containing both, bounded by the result
limit. Both pass through existing downstream sanitization/provenance. Unsupported
non-text blocks yield an explicit safe failure rather than an empty success;
do not fetch resource links, image URLs or embedded external content. Ordinary
tool errors remain tool failures, distinct from malformed protocol results.

Cache hints are parsed but no cross-call result cache or subscription is opened
in the initial profile. Catalog refresh occurs at startup/reconnect or an explicit
future refresh API. UP-04 may add bounded subscriptions with registry revalidation;
it cannot silently replace the accepted per-turn tool selection policy.

## HTTP binding requirements for UP-02B

Use a single configured endpoint and POST each request separately. Support
application/json and request-scoped text/event-stream responses. Validate
content type, HTTP status/JSON-RPC error relationship and IDs; support comments,
split UTF-8 chunks and multiline SSE data without unbounded buffering.
The protocol/version header matches body metadata. Send required method/name
headers and implement safe encoding and validated `x-mcp-header` extraction.
Malformed annotations exclude the affected tool with a safe diagnostic.

Modern HTTP has no initialize, GET notification stream, protocol sessions,
Last-Event-ID resumption or client JSON-RPC responses. Closing the request stream
signals cancellation. The older `2025-11-25` profile uses its own handshake,
session and cancellation rules; keep session IDs in memory, scoped to the exact
peer, and test them separately. Never resume/replay tools/call after an ambiguous
disconnect, timeout or cancellation. Header/version rejection does not authorize
automatic mutating-call replay; rediscovery can inform the next explicit call.

One owner settles each response stream/task and each owned HTTP client. Borrowed
clients/providers remain open. Cancellation cannot overwrite the primary failure
with teardown failure; incomplete cleanup retains an observable retryable owner.
No global environment/callback/tracer changes and no automatic trace context or
baggage propagation across the wire in this profile.

## Remote configuration and trust requirements for UP-03

Keep `tools.providers.mcp.config.servers` as the YAML entry point. Distinguish
`stdio`, `streamable_http` and unsupported values before any I/O. Remote entries
use URL, explicit remote trust, authentication selection, credential environment
reference and bounded timeouts; local entries use command/args/env/workspace cwd.
Forbid mixing command fields into HTTP entries or credential/URL fields into
stdio entries. Disabled/required semantics remain intact. Example values in this
packet are a proposal until the exact UP-03 field names are approved and tested.

Production HTTP requires HTTPS with certificate verification. Reject userinfo,
fragments, credential-bearing query parameters and uncontrolled redirect/proxy
behavior. Scope bearer credentials to the configured origin; disable redirects,
environment proxies and cookie persistence. Environment references are resolved
at connection assembly without serializing values into config diagnostics.
Private/link-local/loopback destinations require explicit per-peer network
allowlisting; fixture-only loopback authority does not relax runtime policy.
The later directive must freeze DNS/rebinding enforcement at the actual connect
boundary, address classes, port policy and secret-safe error handling before
remote registration becomes reachable. Do not substitute a one-time DNS check
for connection enforcement or broaden accepted `local_stdio_only` contracts
without an explicit reviewed Core/runtime change.

Remote results retain untrusted provenance. Required-peer failure blocks startup;
optional failure produces bounded diagnostics and cleanup. Canonical naming,
collision/filter/budget decisions precede model-schema exposure. Raw tokens,
headers, URL secrets, arguments, results, schemas and peer messages stay out of
telemetry. Existing TelemetryInterface observation/correlation owns the call.

## Server profile for UP-05

Add honest discovery and tools capability responses; retain legacy entry points
as explicitly separate profiles. Modern handlers validate required metadata and
HTTP header/body agreement, refuse unsupported methods/capabilities, and never
encode Friday local error codes as reserved MCP wire errors. Bind fixture servers
to loopback; production exposure requires explicit origin/authentication/bind
policy. Agent mode, prompt/resource model exposure and publication are deferred;
tools-only server interoperability is the initial modern server claim.
