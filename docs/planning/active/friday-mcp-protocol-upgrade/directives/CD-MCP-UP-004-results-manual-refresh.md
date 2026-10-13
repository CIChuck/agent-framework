# CD-MCP-UP-004: Result fidelity and manual tool-catalog refresh

Status: **Proposed; maintainer approval pending.** Prepared 2026-10-12.
Initiative: `friday-mcp-protocol-upgrade`; work unit: `MCP-UP-04`.

## Objective, authority and baseline

Close the reproduced stale-wrapper/output-schema bypass after a failed explicit
refresh, make calls bind catalog/schema/HTTP headers to one immutable generation,
and validate complete dated tool results before error/unsupported classification.
Target the pinned MCP **2026-07-28** client tools profile, explicit **2025-11-25**
HTTP compatibility and preserved **2024-11-05** defaults. Match applicable dated
requirements without claiming optional-feature or whole-initiative conformance.

[AGENTS.md](../../../../../AGENTS.md), its engineering/lifecycle/independent-review
policies, approved [build plan](../build-plan.md), [protocol contract](../protocol-contract.md),
[tactical plan](../tactical-plan.md) and immutable prior controls apply.
The exact [result/refresh contract](../up04-results-refresh-contract.md),
[verification profile](../verification-profile-UP-04.json) and
[proposal manifest](../proposals/UP-04-authority-manifest.json) bind this directive.

Product baseline is `3fd5437088c5ddf5d68be3a2a097770c294cba6b`. Chuck Russell's “accepted, continue” accepts
independently VERIFIED UP-03 and authorizes this packet preparation; the
[acceptance receipt](../acceptance/MCP-UP-03.json) and
[original independent evidence](../validation/VAL-UP03-02/report.md) are immutable.
Use `feature/friday-mcp-protocol-upgrade`, the existing private sparse checkout,
Python3.13.10 and pinned no-install environment. No source edits until exact
approval of this directive/contract/profile/manifest is recorded in a separate
receipt and approved execution manifest. Do not rewrite proposed controls after
approval. Run board validate/next/show and verify started/granted/named branch,
current unit authority, frozen controls and product/dependency hashes first.

## Exact product scope

17 existing paths, changed only for the bound requirements:

- `packages/friday-mcp/src/friday_mcp/client/base.py`
- `packages/friday-mcp/src/friday_mcp/client/protocol.py`
- `packages/friday-mcp/src/friday_mcp/client/http.py`
- `packages/friday-mcp/src/friday_mcp/client/adapter.py`
- `packages/friday-mcp/src/friday_mcp/client/__init__.py`
- `packages/friday-mcp/tests_mcp/client/test_modern_protocol.py`
- `packages/friday-mcp/tests_mcp/client/test_http_protocol.py`
- `packages/friday-mcp/tests_mcp/client/test_http_lifecycle.py`
- `packages/friday-mcp/tests_mcp/client/test_lifecycle.py`
- `packages/friday-mcp/tests_mcp/client/test_adapter.py`
- `packages/friday-mcp/tests_mcp/fixtures/modern_sdk_server.py`
- `packages/friday-mcp/tests_mcp/fixtures/http_sdk_server.py`
- `packages/friday-mcp/tests_mcp/fixtures/http_compat_server.py`
- `packages/friday-runtime/tests_runtime/test_mcp_http_integration.py`
- `packages/friday-chat/tests_chat/test_mcp_http_integration.py`
- `packages/friday-mcp/README.md`
- `docs/guides/17-mcp-client.md`

Three new paths:

- `packages/friday-mcp/src/friday_mcp/client/catalog.py`
- `packages/friday-mcp/tests_mcp/client/test_result_refresh.py`
- `packages/friday-mcp/tests_mcp/client/test_result_refresh_interop.py`

This 20-path budget is not permission for general refactoring. Evidence, separate
approval/acceptance receipts, current-process state, execution log and board/view
are process paths. Preserve original index, frozen ledgers/reports/controls and
all unrelated root dirt. Dependencies/lock/package metadata remain immutable.
Core, Runtime/Chat product source, telemetry, memory, transcripts, turn selection,
stdio/legacySSE transport source, http_policy/http_protocol and checker controls
are out of scope. A legitimate need outside scope stops construction for an
exact authority amendment; an old initiative-level grant is insufficient.

## Required architecture and behavior

Implement every requirement of the [bound contract](../up04-results-refresh-contract.md).
The public typed optional refresh seam lives in client/catalog.py and preserves
legacy/custom clients. Generations identify complete snapshots; they do not grant
tool admission. Validated adapter wrappers keep original routing and observer.
Explicit refresh is atomic, bounded and deadline-aware. Failed refresh invalidates
cached definitions; stale/removed/reconnected wrappers fail before mutating I/O.
Issued calls capture matching schema and header bindings and settle once. Preserve
direct no-catalog compatibility; do not permit failed modern/2025 refresh to remove
established output validation. No implicit refresh, replay or registry replacement.

Validate mandatory envelope/tag/content/metadata before isError or unsupported
classification. Preserve modern all-JSON structured values, 2025 object-only dated
rules, safe text/string adaptation and empty external schema Registry. Exclude
2025 required-task tools from non-task clients; absent/forbidden/optional remain
normal candidates. Tasks and interactive input remain unimplemented. Keep
provider-neutral single-call telemetry, untrusted provenance, quarantine, atomic
transcripts and explicit memory opt-in intact.

## Dated research and complete requirement proof

Use all 18 original complete [sources](../research-sources/manifest.json) and
[additional sources/schemas](../research-sources/up02b/manifest.json), plus the
complete [2025 Tasks capture](../research-sources/up04/manifest.json).
Both selected dated schemas remain pinned to upstream commit
`271ecc9accafdd9b83a3c869fa67c22953b2af80`. Moving latest URLs cannot change scope.
The official [2025 tool-level task negotiation](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks#tool-level-negotiation)
supports the non-task exclusion; this directive grants no Tasks implementation.

Before product edits, read all 19 complete captures and schema/old clause ledgers;
produce requirement-to-criterion/positive/negative test plans for every applicable
mandatory clause/selected field, identifying accepted transport evidence and
server-only/unsupported optional-role exclusions. Preserve old347-count history;
new accounting uses original raw 349 (the two-occurrence discrepancy is BCP14
terminology, not missing obligations). At candidate freeze replace plans with
actual source/test/command evidence and map the new Tasks duties honestly. Missing
or unexplained mandatory obligations block independent verification.

## Acceptance criteria and required evidence

| ID | Positive, negative and regression proof |
| --- | --- |
| RES-AC-01 | Declared public MCPRefreshClient/MCPCatalogSnapshot, immutable bounded exports, exact operation-returned generation, legacy constructors/list_tools/call_tool/get_tools and custom-client compatibility; validated wrappers retain routing/admission/observer metadata. Negative: mutated exports, invalid generation and unsupported custom seam. |
| RES-AC-02 | Successful all-page explicit refresh atomically replaces definitions/schema/header bindings/rejection counts. Negative: failed/cancelled/oversized/partial/overlapping refresh leaves no stale adapter cache or partial publication; later success is not cleared by older failure. |
| RES-AC-03 | Already-issued call validates output and sends argument headers from its captured generation exactly once. New stale/removed/excluded/reconnected wrapper calls fail before I/O; failed explicit refresh cannot cause schema-free modern/2025 calls. Preserve direct no-catalog legacy compatibility. Prove real wire headers and issued-call counters under controlled races. |
| RES-AC-04 | Complete dated envelopes, content tags and mandatory fields validated before isError. Ordered text and deterministic mixed adaptation; modern scalar/array/null structured values and absent/null distinction; 2025 object-only and dated metadata; legitimate error remains tool_error without success-schema requirement. Negative malformed error flag/content/tag/metadata/structured result. |
| RES-AC-05 | Exclude 2025 execution.taskSupport=required from non-task catalog/calls, including inconsistent missing capability; absent/forbidden/optional remain normal tools. Modern schema is independent. Valid unsupported content/input_required gets safe fixed disposition; malformed variants are invalid. No Tasks/interactive continuation/subscription/callback/resource fetch or automatic notification refresh. |
| RES-AC-06 | Existing depth32/pages16/catalog1MiB/256/results64KiB/four-request/default30s and lower budgets hold across parser/refresh/adaptation. Output schema validates against existing bounded2020-12 subset with empty external Registry. Negative remote refs/regex/deep/oversized payloads cannot trigger external I/O or uncontrolled rendering; safe fixed error chains. |
| RES-AC-07 | Real SDK subprocess stdio and real literal127.0.0.1 TLS Streamable HTTP fixtures through public client/adapter APIs exercise success/failure refresh, date-specific result semantics and exact original routing; modern and explicit2025 profiles. In-memory observations alone are insufficient interop proof. |
| RES-AC-08 | Refresh lock waits/tasks share the original absolute deadline and bounded concurrency; disconnect/cancel/partial startup settle ownership or retain retryable cleanup owner; no tools/call replay, implicit retry or abandoned owned handles. Repeat successful public stop/start and reconnect. |
| RES-AC-09 | Real Runtime/Chat public startup -> admission/selection -> call -> safe provenance/quarantine/transcript/memory opt-in -> shutdown regressions. Native tools, filters/collisions/count/schema/token limits and borrowed ownership remain. Exactly one injected provider-neutral logical-call observer; no payload/credential leakage or peer instructions. |
| RES-AC-10 | Accurate public docs, exact20-path delta, unchanged dependencies/metadata/checker controls/accepted contracts, complete19-source and selected-schema requirement mapping, all 20 required checks, exact inherited diagnostics/skip/warning comparison and fresh read-only independent full-unit VERIFIED. No blanket conformance/publication claim. |

All 20 exact commands and supplemental inspections in the
[verification profile](../verification-profile-UP-04.json) are mandatory. First
freeze argv, concrete environment, caches, guard/runner and candidate/source
hashes. Use fresh private per-check caches; retain any failed/warmed attempt.
Inspect every child receipt, since the wrapper can exit0 for a failed child.
Focused/touched/MCP typing checks must pass. Full Ruff and full Core/MCP/Runtime/
Chat Mypy may carry only identical 327 complete Ruff objects/fixes and four
untouched profiles.py no-any-return objects; compare paths/line/column/code/message,
not counts alone. Compare full root skip reasons/locations and normalized warnings
against the current accepted baseline. No new waiver or suppression is authorized.

## Execution, effects and stop conditions

1. After exact approval, record separate approved authority, validate board/branch
   and every pin, then freeze the complete requirement/test plan before code.
2. Build the typed catalog seam and generation-safe refresh/call behavior with
   deterministic adversarial races; then complete dated result validation.
3. Add meaningful real SDK stdio and literal127.0.0.1 TLS HTTP interop and public
   Runtime/Chat regression coverage, safe examples and no optional-feature claims.
4. Run the entire frozen profile sequentially, retain raw results and comparison
   evidence, produce final clause/schema/criterion ledger and stable commit.
5. Hand exact authority, candidate/diff, criteria and required checks to a fresh
   read-only independent validation subagent. It returns VERIFIED,
   CHANGES_REQUESTED or BLOCKED; builder conclusions are excluded from handoff.
6. Only VERIFIED permits a completion proposal. Maintainer acceptance, UP-05
   Friday-server modernization, UP-06 aggregate conformance and publication are
   later separate gates. Langfuse remains queued after whole MCP acceptance.

The later approved test effects are restricted to named private synthetic SDK
stdio/TLS fixtures and accepted cross/root fixtures under the pinned guard.
No public peers/provider calls, credentials, dependency install/sync, protected
user-state access or remote push/merge/release. Planning does not authorize product
fixture edits or their new execution. Stop for scope/authority/hash drift, a new
normative contradiction, dependency need, new diagnostic, unowned cleanup,
credential/payload exposure or failed semantic criteria. Preserve evidence; do
not silently patch authority or accepted history to obtain a passing verdict.
