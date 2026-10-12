# CD-MCP-UP-002: Streamable HTTP client and dated compatibility

Status: **Proposed; maintainer approval pending.** Prepared 2026-10-12.
Initiative: `friday-mcp-protocol-upgrade`; work unit: `MCP-UP-02B`.

## Authority and result

Deliver a programmatic Streamable HTTP tools client that matches all applicable
mandatory MCP **2026-07-28** rules in the declared profile. Provide a separate,
explicit **2025-11-25** compatibility profile. HTTP+SSE 2024 is a distinct existing
transport; neither a failed HTTP handshake nor a failed tool call selects it.
SDK interoperability is required evidence, not a substitute for normative proof.

Apply [AGENTS.md](../../../../../AGENTS.md), the engineering, lifecycle and
independent-validation policies pinned in the [prior authority manifest](../authority-manifest.json),
the approved [build plan](../build-plan.md), [protocol contract](../protocol-contract.md),
[tactical plan](../tactical-plan.md), and this directive. The separate
[proposal manifest](../proposals/UP-02B-authority-manifest.json) pins this draft,
its inputs and exact product baseline; it grants no construction authority.
The [first-unit acceptance receipt](../acceptance/MCP-UP-02A.json) records
CD-MCP-UP-001 acceptance without closing the initiative or approving this unit.

Baseline: `256d09d2f6a89846b5b77c4ae6436750d9bdbd95`, containing the independently
reviewed client core at `a36142fb41f59a743b72088d8cce749b71b32202`.
Branch: `feature/friday-mcp-protocol-upgrade`. Before source edits, record exact
maintainer approval of this draft and its manifest, verify every input hash,
and validate board `started`/`granted`/branch agreement. The general initiative
authority and first-unit acceptance do not approve this later directive.

## Exact product scope

Existing six paths, changed only for the behavior below:

- `packages/friday-mcp/src/friday_mcp/client/base.py`
- `packages/friday-mcp/src/friday_mcp/client/protocol.py`
- `packages/friday-mcp/src/friday_mcp/client/__init__.py`
- `packages/friday-mcp/README.md`
- `packages/friday-mcp/pyproject.toml`
- `uv.lock`

New eight paths:

- `packages/friday-mcp/src/friday_mcp/client/http.py`
- `packages/friday-mcp/src/friday_mcp/client/http_protocol.py`
- `packages/friday-mcp/src/friday_mcp/client/http_policy.py`
- `packages/friday-mcp/tests_mcp/client/test_http_protocol.py`
- `packages/friday-mcp/tests_mcp/client/test_http_lifecycle.py`
- `packages/friday-mcp/tests_mcp/client/test_http_interop.py`
- `packages/friday-mcp/tests_mcp/fixtures/http_sdk_server.py`
- `packages/friday-mcp/tests_mcp/fixtures/http_compat_server.py`

Exactly fourteen product paths. Board, approval, process state, logs, normative
ledger and execution/validation evidence are separate process paths. Preserve
the earlier frozen authority/index/approval and raw reports byte for byte.
Do not modify stdio, legacy SSE, manager/config, Friday server, Core, Runtime,
Chat, Telemetry or YAML examples. Do not expand existing source suppressions.

Declare only runtime `httpcore==1.0.9`, already locked, for its public typed
`AsyncNetworkBackend`/`AsyncConnectionPool(network_backend=...)` interfaces.
Keep every existing selected dependency version/artifact, including approved
IDNA 3.20 and development SDK `mcp==2.3.0`. Allow only that new direct dependency
edge and required lock metadata; stop on version churn, private HTTP internals
or an unavailable typed public interface. The MCP SDK remains fixture-only.

## Research and conformance

Use complete frozen [2026 inputs](../research-sources/manifest.json), particularly
[Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http),
plus the [additional dated captures](../research-sources/up02b/manifest.json):
[2025 transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports),
[2025 lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle),
[2025 tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools),
the dated base/cancellation rules and schema, and modern cancellation rules.
Both dated schemas are pinned to upstream commit
`271ecc9accafdd9b83a3c869fa67c22953b2af80`; capture hashes control research inputs.

Before construction, map every applicable mandatory clause and schema field to
HTTP-AC-01 through10 and a positive/negative test, or a justified profile-level
not-applicable entry. Include transport security and headers, not just JSON-RPC.
No full-spec conformance claim for optional features outside this profile.
If a mandatory requirement cannot be met within scope, stop for an exact revision.

## Profile and wire behavior

Expose `StreamableHTTPMCPClient` through the public client module, with required
endpoint and keyword-only explicit revision/profile, bounded HTTP limits and
typed endpoint policy. `http.py` owns transport/lifecycle, `http_protocol.py`
owns headers/SSE and dated HTTP rules, and `http_policy.py` owns endpoint and
actual-connect enforcement. Reuse the accepted immutable core models rather
than duplicating catalog/result parsing. Preserve all old public defaults.

Modern requests use one POST per request at the configured endpoint, accept
JSON and SSE, and carry required `_meta`, `MCP-Protocol-Version`, `Mcp-Method`
and method-dependent `Mcp-Name` headers. Validate status/content-type/body
relationships, UTF-8, JSON-RPC envelopes, matching IDs and dated result tags.
Modern HTTP never initializes, opens a protocol GET stream, retains a protocol
session, sends client JSON-RPC responses or resumes with `Last-Event-ID`.
Request-related notifications are bounded and cannot invoke unsupported effects.
Reject unsupported server requests safely. An SSE stream settles only its own
request; late/duplicate/cross-stream responses never settle another waiter.

Implement comments, multiline data, arbitrary chunk/UTF-8 splits, CRLF and
truncated EOF according to the frozen SSE binding. Ignore only bounded permitted
events; malformed data cannot become successful empty output. Empty compatibility
priming events are bounded, without enabling resumption. No progress event resets
the original request deadline.

Implement all applicable modern `x-mcp-header` rules: validate nonempty HTTP
field-token names and case-insensitive uniqueness, allowed scalar types and
statically reachable property chains. No array/composition/conditional/ref
traversal. Integers stay within the normative safe range. Omit absent arguments;
reject invalid supplied values before sending. Encode non-ASCII, unsafe/control
characters, leading/trailing whitespace and sentinel-shaped values as UTF-8
Base64 using the exact `=?base64?...?=` markers; apply the same rule to names.
An invalid HTTP annotation excludes that tool with a fixed diagnostic/count;
malformed protocol metadata still fails the catalog. Fully validate the entire
bounded catalog before publishing the remaining annotated-tool view.

Compatibility is selected explicitly as 2025-11-25. Initialize first, require
that exact negotiated version, then send initialized notification and the dated
version header on subsequent messages. Advertise only implemented capabilities.
Validate the 2025 schema independently: modern tags/header requirements do not
leak into older messages, and permissive 2024 parsing is not proof of 2025 support.
Keep optional visible-ASCII session IDs bounded to 256 bytes, in memory and
scoped to the exact configured origin. A session 404 invalidates the old session
and starts one read-only reinitialization without that ID within the remaining
operation deadline; if that cannot finish, stay disconnected and require explicit
connect. The original tool call still fails and is never retried. A later explicit
call requires a healthy new session. Budget initialization and initialized
notification together; never send cancellation for initialize itself.
Attempt bounded session DELETE on shutdown, tolerating the specified unsupported
response. No optional GET subscription, event replay or session resumption.
Handle unsupported legacy server requests with fixed method errors where required.

Keep typed complete/input-required dispositions, text/structured output, safe
schema validation and `call_tool(...) -> str` behavior. Unsupported content or
interactive outcomes fail explicitly; no resource retrieval, continuation,
fabricated input or automatic mutation replay. A dated schema may legitimately
restrict a result shape that is accepted in another revision.

## Bounds, cancellation and ownership

Retain accepted limits: 1 MiB frame/aggregate catalog, 64 KiB tool result, depth
32, 4096 JSON nodes, four outstanding requests including retained cleanup owners,
16 pages, 256 tools, and a 30-second default deadline. Lower-only positive typed
HTTP limits additionally cap aggregate response wire bytes at 1 MiB per POST,
256 SSE events including comments/priming/progress, 64 KiB SSE line, 1 MiB event,
64 KiB outgoing/response headers and a 4096-character configured URL. Enforce
pre-decode/pre-retention bounds; a final tool result retains its smaller cap.
Bound generated annotation headers and session IDs before retaining/sending them.

Use one monotonic deadline across encoding, DNS, connect/TLS, send, headers,
response reading and evaluation; catalog pagination shares one operation budget.
Bound waiters before allocation and inspect transport buffering/header limits,
not only decoded objects. Disable pool retries (`retries=0`). No retry of
`tools/call` after any ambiguous status/header/stream/session/cancellation failure.

Modern cancellation closes the owned response stream for that request only;
never send modern HTTP `notifications/cancelled`. Older compatibility may send
a bounded cancellation notification only for an issued request, with its dated
rules. Cleanup failures cannot replace the primary error. Own every task,
stream and pool; incomplete cleanup retains an observable retryable owner.
Borrowed network providers remain open. No arbitrary borrowed HTTP client may
bypass the endpoint policy; test injection uses a typed controlled backend.

## Programmatic endpoint policy

Require HTTPS with certificate verification for production, exact origin/port,
no URL userinfo/fragments/query, no redirects, environment proxies or cookie
persistence. Permit an explicit origin-scoped bearer credential as non-repr
input, or unauthenticated operation; no ambient credential reads, arbitrary
header override, OAuth or credential forwarding. Preserve original hostname for
TLS verification/SNI. Errors, logs and diagnostics contain fixed codes/counts,
never tokens, URL secrets, headers, schemas, arguments, results or peer messages.

Enforce DNS/address policy at the actual connection boundary using public typed
httpcore APIs. Validate every resolved candidate, connect only to a validated
address, and revalidate each new connection; no unchecked second DNS resolution.
Reject private/link-local/loopback/reserved/multicast/unspecified destinations
unless explicitly allowlisted for that exact peer/address/port. Default port is
443; other ports require explicit typed policy. Mixed allowed/disallowed answers
fail closed. This programmatic policy does not grant Runtime/Chat remote admission
or replace the later UP-03 YAML/credential/trust review. Fixture HTTP requires
explicit exact loopback/allocated-port permission and cannot relax production TLS.

No automatic W3C trace/baggage propagation, payload observation, global tracer
or provider changes. Preserve TelemetryInterface and accepted lifecycle contracts.

## Acceptance criteria

| ID | Required proof |
| --- | --- |
| HTTP-AC-01 | Explicit dated profiles, honest capabilities, metadata and result schemas; all accepted legacy/modern stdio behavior preserved |
| HTTP-AC-02 | JSON/SSE parsing, status/envelope/ID validation, split/truncated/adversarial streams and concurrent request isolation |
| HTTP-AC-03 | Required modern header/body agreement and exact safe encoding; valid/malformed annotations, collisions and invalid supplied arguments |
| HTTP-AC-04 | Pre-decode wire/header/event/catalog bounds, single deadlines including stalled send/DNS and retained-owner capacity |
| HTTP-AC-05 | Zero mutating replay; issued-call counters under timeout/disconnect/status/session errors; separate cancellation rules |
| HTTP-AC-06 | Exact 2025 initialize/session lifecycle, bounded 404 reinitialization without replay, DELETE and unsupported legacy requests |
| HTTP-AC-07 | Pre-I/O endpoint rejection and actual-connect DNS/address/port enforcement, TLS hostname retention, no redirect/proxy/credential leak |
| HTTP-AC-08 | Observable stream/task/pool cleanup through partial startup and cancellation; borrowed-provider and primary-error preservation |
| HTTP-AC-09 | Real loopback HTTP interoperability with official SDK 2.3.0 modern server and deterministic exact 2025 peer; positive and negative normative ledger |
| HTTP-AC-10 | Exact dependency/path scope, useful public API docs, complete raw verification evidence and unchanged accepted telemetry/security regressions |

Each criterion requires both success and failure/edge evidence where applicable.
Resolver tests must inspect the address handed to the connector and changing DNS
answers, not merely prove URL validation. Cleanup tests inspect task/stream/pool
owners, not just `is_connected`. Parser tests alone do not prove wire interoperability.

## Effects and verification

Use isolated sparse snapshots and private dependencies/cache/HOME/temp directories;
exclude protected state before checkout and inventory effects before execution.
Reuse the approved locked private Python 3.13 environment offline. Fixtures may
spawn the two named Python HTTP peers, listen only on literal 127.0.0.1 allocated
ports, and execute synthetic tools with bounded counters. Network-policy tests
use controlled resolvers/connectors; no public DNS/TCP destination is contacted.
No real MCP/model/exporter service, credential reads, user state writes, browser,
npm process, shared environment synchronization, push, merge or publication.

Required commands in the guarded private candidate, with full raw receipts:

1. Board `validate`, `next`, `show friday-mcp-protocol-upgrade`; source and input
   hashes, fourteen-path inventory and frozen first-unit preservation checks.
2. Pytest the three new HTTP client test files, then all original first-unit
   focused files, then `packages/friday-mcp/tests_mcp`.
3. Pytest Runtime, Chat and Telemetry package suites, then root configured pytest;
   compare skips/warnings/failures with a preserved accepted pre-unit baseline.
4. Ruff all changed/new Python files and root Ruff against exact baseline debt;
   no new findings. Mypy the changed/new client modules and full MCP source using
   the accepted scoped profile; disclose existing inherited ignores unchanged.
5. `scripts/check-documentation-lifecycle.py`, board render check, proposal/input
   manifest checks and `git diff --check`.

Freeze exact argv/environment/guard hashes before executing these checks. Existing
live-service skips remain distinct from deterministic proof. Never waive a failed
gate or fix unrelated debt. Re-run only affected gates after changes, then the
complete required profile for the stable candidate.

## Stops and handoff

Stop on authority/hash/branch disagreement, scope outside fourteen product paths,
dependency churn, unexpected external effects, unchecked network access, mandatory
spec conflict, cleanup ownership loss, new suppression or new lint/type/test failure.
Retain blocker evidence and propose the smallest concrete adjustment for approval.

Record candidate commit, exact diff, criterion/clause mapping, command exits/raw
artifacts, SDK/dependency/input hashes, effect inventory, baseline comparison and
limitations. Commit a stable candidate and dispatch the policy-required fresh,
read-only independent validator with exact frozen authority and evidence. Only a
VERIFIED result permits unit completion proposal; maintainer acceptance remains
separate. Whole-initiative completion additionally requires the later Runtime/
Chat, selected lifecycle/result, Friday-server and aggregate directives.

Langfuse remains queued after the full MCP upgrade is accepted.
