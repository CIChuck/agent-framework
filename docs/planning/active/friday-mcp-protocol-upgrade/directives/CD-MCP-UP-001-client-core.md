# CD-MCP-UP-001: modern client core and stdio compatibility

Status: Approved by Chuck Russell on 2026-10-12. Prepared 2026-10-12.
Initiative: `friday-mcp-protocol-upgrade`; work slice: `MCP-UP-02A`.

## Controlling authority

Apply [AGENTS.md](../../../../../AGENTS.md), repository engineering/lifecycle/
independent validation policies, accepted earlier MCP safety contracts and
accepted TELEM-01 through04. Then apply the [build plan](../build-plan.md),
[protocol contract](../protocol-contract.md), [tactical plan](../tactical-plan.md)
and this exact directive. The [authority manifest](../authority-manifest.json)
pins baseline and current controls; [approval evidence](../approval.json) records
the original approved proposal hashes and exact maintainer statement.

This slice must match applicable MCP **2026-07-28** client-core/stdio rules and
the dated schema, with explicit 2024-11-05 compatibility. Apply the
[conformance mapping](../conformance-matrix.md), capture/hash complete dated
normative sources before edits, and map mandatory clauses to CD-AC-01 through08.
Broader HTTP/runtime/server conformance belongs to the later declared slices.

Baseline: `46005353046553477417a730f05ff21ead64a00d`.
Construction branch after approval: `feature/friday-mcp-protocol-upgrade`.
Board must be `started`, authority `granted`, on that branch before editing.
Preparation on the telemetry branch supplies no source authority.

## Exact product paths

Existing paths may be changed only for the behaviors below:

- `packages/friday-mcp/src/friday_mcp/client/base.py`
- `packages/friday-mcp/src/friday_mcp/client/stdio.py`
- `packages/friday-mcp/tests_mcp/client/test_execution.py`
- `packages/friday-mcp/tests_mcp/client/test_lifecycle.py`
- `packages/friday-mcp/pyproject.toml`
- `packages/friday-mcp/README.md`
- `uv.lock`

New paths:

- `packages/friday-mcp/src/friday_mcp/client/protocol.py`
- `packages/friday-mcp/tests_mcp/client/test_modern_protocol.py`
- `packages/friday-mcp/tests_mcp/client/test_stdio_interop.py`
- `packages/friday-mcp/tests_mcp/fixtures/modern_sdk_server.py`
- `packages/friday-mcp/tests_mcp/fixtures/legacy_protocol_server.py`

Exactly twelve product/documentation/metadata paths. The controller's board,
packet relocation, authority/approval, execution report/log and validation/evidence
records are separate process paths and cannot expand product scope. No edits to
Runtime, Chat, Core, Telemetry, config examples, manager/config modules, existing
SSE transport or Friday server. No new source ignores/casts as a contract fix.

Metadata permits only direct `jsonschema==4.25.1` and `referencing==0.37.0`
(already locked), development `mcp==2.3.0` and necessary new transitive edges/artifacts. Preserve all unrelated
existing dependency versions; stop on a resolver conflict requiring their change.
SDK imports belong only in the synthetic interoperability fixture/tests.

## Required behavior

| Criterion | Required outcome and evidence |
| --- | --- |
| CD-AC-01 | Add typed bounded protocol models/limits and explicit legacy/modern/auto stdio modes; unchanged callers retain legacy behavior |
| CD-AC-02 | Modern discovery and every-request metadata match 2026-07-28; capability declarations match actual handlers in both eras; validate the negotiated legacy version |
| CD-AC-03 | Enforce envelope, ID and safe-error rules; recognized modern version rejection never becomes a legacy fallback; late discovery/error responses cannot settle another request |
| CD-AC-04 | Complete bounded tools/list pagination; cyclic/endless/malformed/oversized catalogs fail safely with no successful partial list |
| CD-AC-05 | Typed complete/input-required disposition, bounded text/structured result preservation, output-schema validation and fixed unsupported-content/input outcomes; no automatic mutation replay |
| CD-AC-06 | Single deadlines cover send+wait, handshake/probe+fallback and all catalog pages; concurrency/byte/depth caps hold under adversarial input; stdio cancellation sends bounded notification only for issued cancellable requests |
| CD-AC-07 | Accepted partial-start, reaping, retained cleanup-owner, cancellation/EOF and primary-failure semantics remain intact; no payload log/telemetry leakage or global tracing/provider changes |
| CD-AC-08 | Real wire interoperability with official SDK 2.3.0 stdio server and deterministic 2024-11-05 peer; positive/negative/regression checks, docs and dependency receipt pass |

`protocol.py` owns typed immutable discovery/result/limit models and JSON boundary
validation. Dynamic dictionaries may remain only at existing public JSON APIs;
validate them once, retain typed internals and return fresh snapshots. New limits
are keyword-only constructor inputs, with validated positive values and ceilings
from the contract; they do not alter accepted runtime admission or configuration.

Reject oversized stdio frames before decode, bound outgoing encoding and total
catalog bytes, and bound outstanding requests before allocating waiters. Keep
stdio's owned child/stderr/drain/reap semantics. Unknown server requests without
implemented handlers receive safe method/capability errors where applicable;
unsolicited notifications cannot authorize effects or leak payloads.

Output-schema validation uses JSON Schema 2020-12 with a reference registry that
refuses external retrieval. Reject unsupported dialects or nonlocal references
before evaluation, and cap schema bytes/depth. Never fetch `$ref`, `$id`, URLs or
resource links. Invalid output/schema yields a fixed safe failure. Validate
structured JSON scalars/arrays/objects/null; distinguish absent from null.
Bounds also apply to validation work: reject cyclic references and unsupported
schema features that cannot be evaluated within the chosen resource budget.
Include adversarial reference/composition/pattern cases and report a fixed
unsupported-schema outcome; byte/depth caps alone do not prove bounded evaluation.
Record the supported schema-feature profile in the package documentation.

Keep local safe exceptions separate from peer wire codes and use fixed public
messages without raw exception chaining. Preserve existing `tool_error` and
`invalid_result` failure identifiers. Add fixed unsupported/input/protocol codes
without changing Chat's result safety path. Legacy content compatibility remains
covered by existing tests; modern schema/tag validation must not accept legacy
string blocks merely because the old API did.

## Tests and effects

Apply the [exact verification profile](../tactical-plan.md#verification-profile-for-up-02a).
For each criterion, include at least one positive and one failure/edge case when
the behavior can fail. Include modern-only, explicit legacy and auto fallback,
unsupported modern versions, malformed/late IDs, duplicate results, concurrent
requests, send stalls, all deadline paths, invalid/missing result tags, structured
output schema errors, scalar/null results, unsupported content, catalog cycles/
caps, cancellation during discovery/call and disconnect after partial start.

The official SDK fixture runs as a real stdio child, not its in-process shortcut.
Record pinned release/artifact hashes and synthetic tool execution counts; prove
an ambiguous tools/call failure issues exactly one call. A deterministic legacy
fixture proves the exact older revision and original text API. Cleanup assertions
must inspect owned tasks/process exit, not only `is_connected`.

Only the [fixture effects](../tactical-plan.md#permitted-fixture-effects-under-the-approved-first-directive)
and bounded dependency resolution/install in the tactical plan are authorized
by the recorded approval of this directive.
No live MCP/model/exporter calls, credential reads or user workspace state writes.
The builder cannot substitute a live peer for failed deterministic evidence.

## Non-goals and stops

HTTP bindings, remote runtime/YAML trust changes, modern server behavior,
subscriptions/caching, automatic MRTR, resource/prompt expansion, SDK runtime
adoption, Langfuse, tool continuity, delivery/publication and parity cleanup are
outside scope. Preserve legacy SSE and its default initialization while client
core changes land. An unsupported server interaction is a safe outcome, not
permission to add a handler or expose model/root data.

Stop on authority/branch/hash disagreement, required scope outside twelve paths,
dependency churn, an unexpected external effect, a new source suppression,
new lint/type/test failure, unbounded input handling or inability to preserve
accepted safety/lifecycle contracts. Do not waive checks or repair unrelated
root debt. Record exact blocker and the smallest needed adjustment.

## Reporting and handoff

Record the exact candidate commit, twelve-path diff, criterion-to-test mapping,
commands/exits/raw artifacts, SDK/dependency versions and hashes, effects/guard
inventory, baseline debt comparison and limitations. Preserve complete raw check
evidence. Commit the stable candidate before the policy-required fresh read-only
validator; no self-verification verdict, automatic acceptance or push/merge.
