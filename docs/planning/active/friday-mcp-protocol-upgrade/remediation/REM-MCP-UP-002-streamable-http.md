# REM-MCP-UP-002: bounded Streamable HTTP corrections

Status: **Proposed; maintainer approval pending.** Prepared 2026-10-12.
Initiative: `friday-mcp-protocol-upgrade`; work unit: `MCP-UP-02B`.

## Authority and objective

Correct every numbered finding in the [original independent report](../validation/VAL-UP02B-01/artifacts/report.md.gz)
for candidate `2a3cec520f20442515d3d9a5a1a33eb500bd8846`. The original report SHA256 is
`e97e199a556be162ff99a46d6d3ec6db75de3ef61cff5985447b47fbd73487c3`. Apply unchanged CD-MCP-UP-002, its approved execution
manifest/receipt, the prior frozen controls, repository policies and complete
frozen MCP 2026-07-28 and 2025-11-25 captures. The [proposal manifest](../proposals/REM-MCP-UP-002-authority-manifest.json)
pins the exact inputs and baseline. This proposal grants no source-edit authority;
record a separate exact approval receipt before remediation starts.

Original full directive: [CD-MCP-UP-002](../directives/CD-MCP-UP-002-streamable-http.md).
Independent review: [navigation report](../validation/VAL-UP02B-01/report.md).
Original approved execution authority: [UP-02B manifest](../authority-UP-02B.json).
Scope and profiles remain unchanged; no new protocol feature is introduced.
Use a separate bounded remediator and then a fresh read-only independent validator.

## Exact product scope

Only these six paths from the original fourteen-path scope may change:

- `packages/friday-mcp/src/friday_mcp/client/http_protocol.py`
- `packages/friday-mcp/src/friday_mcp/client/http.py`
- `packages/friday-mcp/src/friday_mcp/client/protocol.py`
- `packages/friday-mcp/tests_mcp/client/test_http_protocol.py`
- `packages/friday-mcp/tests_mcp/client/test_http_lifecycle.py`
- `packages/friday-mcp/README.md`

All other product paths, dependency versions/artifacts/edges and source suppressions
remain unchanged. New directive/approval, process state, board/log, builder ledger
and review evidence are separate process paths. Preserve all original frozen
controls, acceptance/proposal receipts, candidate evidence and original reports
byte for byte. Store updated builder evidence in a new remediation directory;
do not replace the original HTTP evidence or its normative ledger.

## Findings and required fixes

### VAL-UP02B-001 — schema-bearing contentSchema bypass

Validate annotations in the JSON Schema 2020-12 `contentSchema` child as a
schema-bearing location outside a statically reachable argument-property chain.
A valid-looking or malformed `x-mcp-header` anywhere under that child must exclude
the entire invalid tool after complete catalog validation, with the fixed count/
diagnostic and no request issuance. Audit the supported dialect's schema-bearing
keywords for equivalent omissions while preserving opaque example/default/const
JSON data. Do not perform external schema retrieval or broaden supported dialects.

Required evidence: direct/nested `contentSchema`, valid and malformed annotation
names/types, correct rejected-tool counts and atomic catalog publication; ordinary
JSON examples containing those keys remain opaque; valid reachable scalar property
annotations continue to produce exact matching wire headers.
Criteria: HTTP-AC-03, HTTP-AC-04, HTTP-AC-09.

### VAL-UP02B-002 — stale concurrent 2025 session expiry

Make recovery/state changes generation-aware and serialized. A delayed 404 from
an old generation must fail its own operation without clearing or replacing a
healthy newer connection/session/catalog. At most one read-only handshake occurs
for the expired generation; it omits the old session ID. Failure or timeout of
that recovery leaves its own generation disconnected, without stale operations
invalidating a later successful recovery. Preserve the original operation deadline,
cleanup ownership and exact one-execution/no-replay rule.

Required evidence: two issued concurrent operations with controlled 404 ordering;
first recovery succeeds and second stale 404 arrives later; session-2 remains
connected, only one reinitialize occurs, both original operations fail without
replay, and a subsequent explicit call works. Cover stale waiting deadlines and
failed recovery with deterministic scheduling, exact counters and owner cleanup.
Criteria: HTTP-AC-04, HTTP-AC-05, HTTP-AC-06, HTTP-AC-08.

### VAL-UP02B-003 — declared 2025 input-schema dialect

Validate each 2025 tool inputSchema according to its declared/default supported
dialect. Absent `$schema` uses JSON Schema 2020-12. Explicit supported 2020-12 is
validated correctly; invalid or unsupported declared dialects fail gracefully
with the fixed unsupported-schema outcome before catalog publication/call issuance.
Do not silently treat an unknown dialect as 2020-12, add dialects/dependencies,
fetch schema URIs, or change permissive 2024 defaults or accepted modern behavior.

Required evidence: absent/supported dialect success, malformed/unsupported declared
URI failure on later catalog pages with no partial or stale publication, zero
retrieval I/O for schema URIs, and preserved exact modern/2024 regression behavior. Preserve bounded schema/resource handling.
Criteria: HTTP-AC-01, HTTP-AC-04, HTTP-AC-10.

### VAL-UP02B-004 — dated metadata key grammar

Enforce the frozen 2025 `_meta` object/key grammar at selected received MCP
container boundaries, including Tool, Result and TextContent. Keep valid key values
opaque in this era; do not apply modern reserved-value schemas to 2025 metadata,
trust/forward tracing, recursively reinterpret user JSON data, or change 2024 defaults.
Reconcile all selected dated metadata-bearing fields with the frozen schema.

Required evidence: malformed prefix/slash/key forms rejected independently at
Tool, Result and TextContent boundaries, with fixed payload-free diagnostics;
valid prefixed/unprefixed/empty keys as allowed by the frozen grammar and opaque
values accepted; independent-boundary tests prevent one malformed field masking
another; failed metadata never becomes successful output. Preserve 2024 defaults
and modern metadata validation regressions.
Criteria: HTTP-AC-01, HTTP-AC-02, HTTP-AC-10.

## Verification and effects

Before edits validate board/start/granted/feature-branch alignment, approval and
all controlling hashes. Reuse the existing private sparse candidate/baseline,
Python 3.13 environment, pinned SDK/httpcore, private guard/HOME/cache/TMP and
original pre-inventoried effects. No dependency sync, public DNS/TCP, credentials,
user stores, real service, telemetry/provider changes, arbitrary subprocess or
publication. Only the originally approved synthetic literal-loopback peers and
existing cross/root fixtures may execute.

Turn every original independent reproducer into a meaningful regression. Run
focused finding coverage, then the complete original CD2 required profile on a
stable candidate: three HTTP files, four original client files, MCP package,
Runtime/Chat/Telemetry and root pytest; changed/new Python Ruff, exact baseline
root Ruff comparison, narrow and full MCP Mypy; board/docs/render/whitespace;
six-path delta, fourteen-path overall scope, unchanged dependency/artifact/control
hashes and complete dated criterion/clause reconciliation. Retain full argv/env/
guard and raw output, baseline comparisons and original reproducer outcomes.
Live-service skips remain distinct from deterministic proof. No new waiver/ignore.

The builder reports changes and evidence, never self-VERIFIED. Commit a stable
candidate, retain the failed report as superseded only for decision purposes,
and dispatch a fresh read-only finding-delta followed by full work-unit review.
Only VERIFIED permits proposing unit completion; maintainer acceptance and later
MCP units remain separate. Stop on authority/scope/effect/dependency drift,
violated requirements outside this bounded scope or new deterministic failures.
After two unsuccessful remediation cycles, return unresolved findings to maintainer.
