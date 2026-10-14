# CD-MCP-UP-005: Modern tools-only Friday server

Status: Proposed; exact maintainer construction approval pending.
Initiative: friday-mcp-protocol-upgrade. Work unit: MCP-UP-05.

## Objective, authority and baseline

Deliver the pinned MCP2026-07-28 server tools profile through actual Friday
stdio and Streamable HTTP servers, independently exercised by official SDK2.3.0
Client. Replace neither the legacy server nor the accepted client/runtime layer.
[Bound contract](../up05-server-contract.md), [verification profile](../verification-profile-UP-05.json)
and [exact proposal manifest](../proposals/UP-05-authority-manifest.json) define
all scope, wire/error/privacy/lifecycle requirements, tests and permitted effects.
AGENTS.md and canonical engineering/lifecycle/independent-review policies apply.
[UP-04 acceptance](../acceptance/MCP-UP-04.json) records Chuck Russell's “approved”
at its explicit acceptance gate; it authorizes this packet preparation only.

Product baseline: `f876603c74d8a90639fb5dc90d287d17ab523705`. Use the existing named feature branch,
private sparse candidate, accepted UP04 baseline and pinned no-install Python3.13.10
environment. Read board validate/next/show and verify current unit/branch/authority,
all frozen controls/product/metadata hashes before source edits. Separate exact
approval receipt and execution authority are required; original proposed controls
and earlier reports remain immutable. An initiative-wide old grant supplies no
UP-05 construction authority.

## Exact18-path product budget

Two existing paths:

- `packages/friday-mcp/src/friday_mcp/server/__init__.py`
- `packages/friday-mcp/README.md`

Sixteen new paths:

- `packages/friday-mcp/src/friday_mcp/server/protocol.py`
- `packages/friday-mcp/src/friday_mcp/server/modern.py`
- `packages/friday-mcp/src/friday_mcp/server/modern_stdio.py`
- `packages/friday-mcp/src/friday_mcp/server/http.py`
- `packages/friday-mcp/src/friday_mcp/server/registry.py`
- `packages/friday-mcp/src/friday_mcp/server/http_policy.py`
- `packages/friday-mcp/tests_mcp/server/test_modern_protocol.py`
- `packages/friday-mcp/tests_mcp/server/test_modern_stdio.py`
- `packages/friday-mcp/tests_mcp/server/test_streamable_http.py`
- `packages/friday-mcp/tests_mcp/server/test_server_security.py`
- `packages/friday-mcp/tests_mcp/server/test_server_lifecycle.py`
- `packages/friday-mcp/tests_mcp/server/test_registry.py`
- `packages/friday-mcp/tests_mcp/server/test_server_interop.py`
- `packages/friday-mcp/tests_mcp/server/test_legacy_compatibility.py`
- `packages/friday-mcp/tests_mcp/fixtures/friday_modern_tools_server.py`
- `docs/guides/18-mcp-server.md`

New source modules own modern protocol/typed models, core dispatch, stdio, HTTP,
registry bridge and access policy; exports add the named modern APIs. New tests
cover protocol/stdio/HTTP/security/lifecycle/registry/SDK/legacy contracts; the
single named fixture runs synthetic Friday servers. Documentation records actual
public APIs and unsupported profiles. This budget permits no opportunistic refactor.
Remove the existing mypy ignore from the modified server export file; new source
cannot introduce suppression, blanket casts or essential assert-only enforcement.
Legacy base/stdio/SSE/tools/agent modules, root package imports, client/config enums,
Core/Runtime/Chat/telemetry/memory/CLI sources, all dependency/checker/lock metadata
and original index/controls/reports are outside product scope. Process receipts,
state/log/board/dashboard and source/requirement/review evidence are separate paths.
Stop before any necessary extra product path or dependency change.

## Required implementation and proof order

1. Freeze complete server-role clause/field/positive/negative/omitted/null plan
   from all19 complete captures; earlier client-role exclusions are not server proof.
2. Build strict typed modern protocol/core/catalog/result/registry boundary and
   test it through public APIs, with actual Core registry synthetic tools.
3. Add owned concurrent newline stdio and stateless POST HTTP JSON/SSE; enforce
   every access/header/body check before handler admission, with zero-call negatives.
4. Exercise limit1..4 races, schema/call snapshots, cancelled/failed/reconnect/stop
   ownership, actual SDK stdio and private verified TLS endpoints, privacy/observer
   isolation and preserved legacy/optional-import behavior.
5. Run all20 bound commands, retain raw child failures and exact baseline comparisons,
   freeze stable candidate and final actual clause/schema/test/command ledger.
6. Fresh-context read-only full-unit validator reviews every criterion/source/wire
   and required check. VERIFIED precedes completion proposal; acceptance is separate.

## Acceptance criteria

| Criterion | Required positive and negative behavior |
| --- | --- |
| SRV-AC-01 | Typed2026-only per-request server role; complete bounded envelope/request/notification/metadata grammar with omitted/null cases, optional clientInfo, per-request required capabilities and exact fixed wire codes. No initialize/session-state trust or local-code leakage. |
| SRV-AC-02 | Honest empty/nonempty discover/tools capability, immutable complete catalog/definitions and bounded byte/count pagination, atomic filter/prefix/collision/schema registration. Invalid/obsolete/oversized cursors and definitions fail with zero handler I/O; old failures cannot mutate a newer catalog. |
| SRV-AC-03 | Captured definition/schema/handler, validated arguments before exactly one invocation; complete typed text/structured results (omitted/null/mixed/order), captured successful output validation and legitimate safe tool errors. Mutation during issued call preserves captured schema; malformed/unsafe output and unknown tools cannot cause replay. |
| SRV-AC-04 | Real newline stdio with clean stdout, responsive concurrent dispatch, owner-local cancellation, partial-line/UTF8/JSON/batch/duplicate-ID negatives, EOF/partial-start/pipe/stop/restart/SIGTERM cleanup. No stale owner reply or server cancellation outside unsupported subscription role. |
| SRV-AC-05 | Single stateless HTTP POST endpoint, JSON and request-scoped SSE, exact status/body/header grammar; protocol/method/name/custom parameter/header/body agreement, Base64 and null/absent/type cases, no handler before validation. GET/DELETE405, unsupported404/-32601, version400/-32022, HeaderMismatch400/-32020; no sessions/legacy split. |
| SRV-AC-06 | Explicit typed bind/path/Host/Origin/bearer/TLS access policy with pre-dispatch rejection/counter0, duplicate/query/Unicode/header-size negatives, token nonrepr/privacy, no clientInfo authorization. Static administrative gate does not claim optional OAuth conformance; all fixtures literal127 only, no live exposure. |
| SRV-AC-07 | Lower-only limits and original absolute deadlines, bounded admission/owners/body/header/schema/output/page work, request/connection-owned cancellation and retryable shutdown. Lower budgets1..4 and ignored cancellation retain truthful owners; no orphan process/task/stream, unrelated cancellation or mutating replay. |
| SRV-AC-08 | Declared public Core ToolRegistry/ToolDefinition integration using real public DefaultToolRegistry with synthetic tools; strict staged snapshots/filter/prefix/collision/unsupported schema negatives and distinct instances. No implicit agent/prompt/resource/memory/model loading or incidental private contracts. |
| SRV-AC-09 | New strict-typed exports preserve optional-dependency import behavior and all legacy imports/constructors/config/version/tool/agent/prompt/resource/SSE interfaces and readonly hashes. No modifications to accepted client/Runtime/Chat/Core/telemetry sources or config defaults. |
| SRV-AC-10 | Optional existing TelemetryInterface injection, one admitted-handler start/terminal observation, safe trusted labels and provider/state isolation; observer failure causes no duplicate invocation/replay. Credentials/raw arguments/results/schema/client IDs/URLs/trace state absent from logs/telemetry, no new provider/exporter/global state. |
| SRV-AC-11 | Official SDK2.3.0 Client against actual Friday server real subprocess stdio and private verified TLS HTTP JSON/SSE. Explicit2026 mode/cacheNone/no interactive extensions; actual discovery/version/metadata/wire counters, errors/cancel/disconnect/child exit. Deterministic/raw negatives complement SDK, no self-client-only or in-process shortcut proof. |
| SRV-AC-12 | Accurate programmatic modern/legacy guide/API examples and explicit unsupported OAuth/agent/extensions;18-path source budget,19 unchanged metadata, existing22009-library/192dist integrity, all19 captures and full server-role clause/field plan/final actual mapping; all20 required checks and exact inherited debt/skip/warning comparisons plus fresh independent full-unit VERIFIED before completion. |

## Non-goals and stop conditions

No2025 server, legacy redesign, agent/prompt/resource/model exposure, Tasks,
interactive input/state, subscriptions/caching/logging RPCs, OAuth login/delegated
resource metadata, YAML server expansion, global telemetry provider/Langfuse,
public service/deployment, live user tools or remote publication. Static bearer
administrative policy is not OAuth conformance. Only the bound synthetic private
fixtures run. Do not read root credentials/runtime stores or use inherited provider
environment. Existing327 Ruff/four Mypy debt is not permission to add violations;
full objects and successful skip/warning sections must exactly match baseline.
Changed product/controlling bytes invalidate review. Unexpected effects or scope
ambiguity stop; every security remediation requires the policy's separate role and
bounded directive. Stop after two unsuccessful remediation cycles. UP06 aggregate
acceptance and whole MCP completion remain future gates; Langfuse stays queued.
