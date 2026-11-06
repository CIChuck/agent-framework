# CD-MCP-UP-002 Streamable HTTP builder report

Stable product evidence; independent review pending. Whole MCP initiative remains
started/local. No push, merge, release or maintainer acceptance is inferred.

The new public `StreamableHTTPMCPClient` supports explicit MCP **2026-07-28**
request-scoped HTTP and a separately selected **2025-11-25** initialized/session
profile. Both JSON and SSE response bindings are supported. Every modern request
carries required version/client identity/capabilities metadata and matching method,
name and valid `x-mcp-header` parameter headers. Header annotations are validated
across the complete bounded catalog; invalid annotated tools are excluded. Static
nested paths, null/absent omission, safe integers, Unicode/control/whitespace and
exact Base64 sentinel encoding have positive and negative coverage.

The client validates dated envelopes/result fields, UTF-8, HTTP status/content-type,
own IDs, structured results and the accepted bounded JSON Schema output profile.
Catalog publication is atomic; a call binds its output schema before awaiting the
peer so concurrent catalog invalidation cannot bypass validation. The shared base
now permits request-scoped subclasses without allocating a fake shared transport;
existing stdio/SSE defaults remain unchanged. Compatibility parsing is explicit,
including typed text, object-root output/structured data and exact initialization.

Production endpoints require verified HTTPS; URL secrets, query/fragment/userinfo,
redirects, ambient proxies and cookies are excluded. A typed resolver is consulted
at each actual new connection; every answer must satisfy the exact endpoint/address/
port policy, and the borrowed connector receives only a validated numeric address.
Original hostname is retained for TLS verification. Explicit bearer credentials
remain origin scoped and non-repr. No trace/baggage propagation, payload observation,
provider mutation or telemetry rewiring occurs. Fixture plaintext requires exact
literal-loopback/address/allocated-port authorization.

Each request has one deadline and one isolated stream owner. Timeouts, cancellation,
ambiguous drops and session errors never replay a mutation. Modern cancellation
closes the stream. Compatibility cancellation is issued-only, never initialize;
session 404 performs at most one read-only fresh handshake without the old ID,
while the original call still fails. Public calls cannot issue during initialization.
Response, partial TLS/connect and pool owners remain visible and capacity-counted
until cleanup succeeds; cancellation-resistant cleanup is retryable. Borrowed
resolver/connector objects remain open, and cleanup preserves a primary failure.

Only fourteen authorized product paths changed. The sole dependency update adds
already locked **httpcore==1.0.9** as a direct runtime dependency (two lock edges).
Every existing selected version and artifact remains unchanged, including IDNA
3.20 and fixture-only official MCP SDK 2.3.0. No new source typing suppressions;
the preexisting public client module ignore remains unchanged and disclosed.

Evidence: [frozen products/check argv/environment](stable-check-freeze.json),
[criterion mapping](criterion-ledger.json), [complete normative mapping](normative-clause-ledger.json),
[effects/research identities](effects-and-check-profile.json),
[baseline comparison](baseline-comparison.json), [Ruff debt comparison](root-ruff-comparison.json),
and [all lossless raw artifacts](stored-manifest.json).

The normative ledger inventories 18 complete frozen source/schema captures,
218 mandatory paragraphs containing 347 MUST/REQUIRED occurrences, and 98 selected
schema interfaces with nested/inherited field declarations retained. Mapping is
builder evidence for independent classification, not a self-issued conformance
verdict. Server-only duties and optional feature exclusions have explicit reasons.
The original accepted core ledger and authority bytes remain immutable.

| Stable candidate gate | Result |
| --- | --- |
| New HTTP protocol/lifecycle/real-wire fixtures | 198 passed |
| Original four first-unit client files | 228 passed |
| MCP package | 462 passed |
| Runtime / Chat / Telemetry | 1,211 passed; 5 inherited skips; 1 inherited warning |
| Root configured suite | 3,529 passed; 14 inherited skips; 15 inherited warnings |
| Accepted-product baseline, same private environment | 3,331 passed; 14 skips; 15 warnings |
| Changed/new Python Ruff | Pass |
| Root Ruff | Exit 1: 327 exact baseline-identical findings; zero new |
| Changed/new client Mypy / full MCP source | Pass: 6 / 21 source files |
| Board / documentation / generated view / whitespace | Pass; closeout metadata rechecked before commit |

Real HTTP tests use the official SDK 2.3.0 modern server and independent deterministic
2025 peer for JSON/SSE, synthetic annotated/structured calls, session expiry,
unsupported server requests, ambiguous one-execution drops and cancellation.
The same named 2025 peer also supplies a real synthetic-CA TLS success/wrong-hostname
pair; private generated cert/key scratch files are not archived. All verification
is offline/guarded, apart from explicitly allowed literal 127.0.0.1 fixture listeners.
No real MCP/model/exporter service, credential or user-state access occurred.

Intermediate failures are retained in raw evidence: the initial compatibility
server-request error-response POST acknowledgement was corrected; a test incorrectly
inspected a socket after its successful close and was corrected; initial Mypy
variable narrowing was corrected. Console entry points missing from reused private
libraries execute as equivalent private `python -m pytest` / `python -m mypy`.
All final stable gates pass independently of these intermediate runs.

Profile limits: no OAuth discovery/browser flow, GET/resumption/Last-Event-ID,
subscriptions, Tasks, resource/prompt handlers, MRTR continuation or automatic
retry. The modern and 2025 profiles are selected explicitly; no HTTP+SSE 2024
fallback is attempted. Remote YAML/Runtime/Chat trust remains UP-03; selected result/
lifecycle integration is UP-04, modern Friday server UP-05, aggregate conformance
UP-06. Langfuse stays queued after the entire MCP upgrade is accepted.

The pinned HTTP library's DEBUG logging would expose headers, so this client fails
closed before I/O and at its documented per-request trace hook when sensitive
httpcore DEBUG loggers are enabled; application levels/filters are never changed.
The HTTP stream guard bounds wire/header bytes before HTTP/MCP decode. HTTP/1.1
parser defaults may reject incomplete headers more strictly than the 64 KiB
ceiling. The ceiling does not claim to bound kernel/native/asyncio packet buffering;
it bounds application parsing and retained protocol data. SSE events/lines and
core catalog/schema/result budgets can only be lowered from fixed ceilings.
