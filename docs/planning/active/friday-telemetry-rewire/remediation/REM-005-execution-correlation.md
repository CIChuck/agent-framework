# Approved REM-005: execution correlation and stream closure

Status: approved by Chuck Russell on2026-10-11. Prepared2026-10-09.
See [approval record](REM-005-approval-record.md). Initiative friday-telemetry-rewire;
work unit TELEM-04; branch feature/friday-telemetry-rewire.

Frozen product candidate:1547fae7cac6450ec9ad7440f19d1f1162598fe2.
Full unit base:e6209e3156216afde1655758e280690229f7d3e6.
Aggregate base:2155a0fc51f5b20dea4e35c6cfc70f1d52002735.
Finding authority: [VAL-009 original](../validation/VAL-009/raw/report.md.gz),
SHA2566368a6cb61b16d77fb145a5504cddb23db9fe3cc8e98c917ebb22877f6c15393.
[Original artifact manifest](../validation/VAL-009/original-artifact-manifest.json),
SHA256600ced2de3d81d78c6d98bd3dbbcaffb22176725c5887532beab32f31bc0e0e1.

## Authority and objective

Follow explicit maintainer direction, repository engineering/security and independent
validation policies, accepted TELEM-01–03/MCP contracts, approved build/tactical
plans, approved CD-004/execution contract/profile and this exact approved directive.
The [REM manifest](../authority-manifest-REM-005.yaml) pins those controls, the
unaltered independent finding authority and15 product targets. All15 are a subset
of CD-004's original29; no accepted specification or WVR-006 input is rewritten.

Repair every mandatory VAL-009 finding exactly once. Passing suites do not dispose
these independent behavioral findings. Preserve existing application behavior,
borrowed provider ownership, strict privacy and bounded metric semantics while
making causal lineage, rejection counts, version validation and stream cleanup true.

## Complete finding-to-fix contract

| Finding and severity | Required fix | Required regression |
| --- | --- | --- |
| VAL-009-F01 — High |Isolate detached/background/origin sink context from an active foreground SDK stack. Keep explicit legitimate active-owner parentage, copy context for independent child/sibling frames and restore caller context. Use private contextvars.Context for synchronous sink delivery; no SDK imports, sink-internal introspection, new interface method or background task/scheduling change. Bind before span start; close in the same binding before reset. |Fake ContextVar sinks and separate actual installed SDK/Debug/two-child Composite: active foreground scheduling, post-close handoff, nested/concurrent callers/siblings, correct event/span placement, preemption/requeue/resume/shutdown, restoration and zero leaked resources. |
| VAL-009-F02 — High |Distinguish an extraction item's explicit None origin from ordinary nested inheritance. Detach/rebind every item; None yields session-only facts. Valid mixed origins retain their own turn IDs; item objects, ordering and existing commit/cancellation/requeue behavior remain intact. |Mixed valid/None origins under a foreground scope, no-extractor/empty cases, retry, foreground preemption, resume and shutdown; inspect identities/accounting and restoration. |
| VAL-009-F03 — Medium |Derive native/MCP rejection counts from already computed trusted MCP membership. Preserve existing rejection reason/control flow, zero dispatches, provenance/redaction and ID repair. No extra registry/provider lookup. |Known disallowed MCP versus native, unknown/malformed calls and mixed selection; exact closed counts and no dispatch/success contribution. |
| VAL-009-F04 — High |Explicitly await closure of acquired close-capable iterators in TurnProcessor and both legacy/typed FrameworkChatModel wrapper chains on completion, callback failure, cancellation or early close. Use a declared typed closure capability; preserve the active primary exception if cleanup also fails/cancels. Retain chunk order, heartbeat, buffering and retry policy without prefetch or new tasks. |Strongly retained iterators through direct and adapter paths; callback failure/cancellation, cleanup failure/cancellation, normal exhaustion and public early close. Verify close attempts finish before terminal return, exact primary identity, one terminal, restored context and closed observation spans. |
| VAL-009-F05 — Medium |Require actual integer schema_version1 before normalization/record/delivery/aggregation, including forged-instance revalidation. Follow the accepted integer-version validation pattern; leave accepted LLM/MCP models unchanged. |Bool, float, string, wrong integer and forged-instance negatives through execution models and observer; no record/sink/metric contribution; omitted/default and exact integer1 remain valid. |

The original report supplies exact source lines, violated AC04 criteria, raw
reproduction and risk for each row. F04 also reproduces at the unit base: it is an
inherited gap, not a new callback regression, and remains mandatory under CD-004.

Delivery contexts are private active-frame state, never part of ExecutionContext,
TurnResult, PendingExtractionTurn, event attributes or diagnostics. Child contexts
must not share a mutable provider stack. Outside-scope accepted event behavior and
all three TelemetryInterface call signatures/defaults remain unchanged. Ordinary
sink/schema failures stay locally diagnosed and cannot replace application results,
primary exceptions or cancellation. No raw exception/model/tool/endpoint/path/content
data or dynamic metric labels may be introduced.

## Exact product scope

Seven sources:

- packages/friday-telemetry/src/friday_telemetry/helpers/correlation.py
- packages/friday-telemetry/src/friday_telemetry/models/execution.py
- packages/friday-chat/src/friday_chat/telemetry.py
- packages/friday-chat/src/friday_chat/turns/telemetry.py
- packages/friday-chat/src/friday_chat/adapters.py
- packages/friday-chat/src/friday_chat/tools/loop.py
- packages/friday-chat/src/friday_chat/turns/processor.py

Six regression modules:

- packages/friday-telemetry/tests_telemetry/test_execution_events.py
- packages/friday-telemetry/tests_telemetry/test_correlation.py
- packages/friday-chat/tests_chat/test_turn_telemetry.py
- packages/friday-chat/tests_chat/test_tool_telemetry.py
- packages/friday-chat/tests_chat/test_memory_telemetry.py
- packages/friday-chat/tests_chat/test_telemetry_diagnostics.py

Documentation: packages/friday-telemetry/README.md and packages/friday-chat/README.md.
Reconcile event allowlist, strict-version, context-isolation and stream-closure claims.
Changed paths may be a subset, never a superset. Adapter edits are limited to the
per-item extraction boundary and actual streaming wrapper cleanup; no factory,
memory-store, retrieval, persistence coordination or unrelated adapter refactoring.

## Non-goals, effects and verification

No source/test paths outside this15-file manifest. No accepted TelemetryInterface,
LLM/MCP schemas/provider/history/pricing/usage, shared OTel/Composite implementation,
factory/config/template/dependency/lock, storage/database, queue/scheduling, tool
authorization/selection/retry or persisted-ID edits. No new raw-capture surface,
global state/SDK registration, vendor callback, listener, task or SDK worker.

New tests remain fake-only and in memory. The separate owned actual SDK probe and
the same13 existing synthetic loopback nodes remain within CD-004's already approved
effect limits, after independent fixture/import/helper preflight. No credentials,
live/remote/paid service, original runtime state, install/sync/download, push/merge,
release, deployment or publication. WVR-006 remains separately approved for its
exact327 identities until TELEM-04 acceptance or input drift; do not broaden it or
request the same approval again when its actual inputs remain unchanged.

Run the [complete REM verification profile](../verification-profile-REM-005.md),
including all CD-004 acceptance criteria and required gates. Preserve the original
failed candidate/VAL-009 evidence. Source generation starts only after maintainer
approval is recorded and exact approved authority/branch/board are reconciled.

## Execution and stop conditions

Use a separate remediator for this execution-context architecture correction under
the [independent-validation policy](../../../../reference/policies/independent-validation-policy.md).
The controller supplies this exact scope and findings; no opportunistic refactoring.
Keep the initiative started/local and validation_state changes_requested through
approval/preparation, then pending/in_review for the new stable candidate.

Stop for extra paths/effects, controlling input or accepted-authority drift, new
lint identities/skips/suppressions, primary/return/default/chunk/order/ownership drift,
unresolved interface conflicts or failed mandatory evidence. Report raw failures
and reruns separately. Do not expand scope automatically.

Commit a new stable candidate. Mark VAL-009 superseded for decision purposes only
when reviewing that new candidate; retain it unchanged as history. A new
fresh-context read-only validator must examine the five fixes, full TELEM-04 unit
and complete aggregate with all required checks. Supply frozen authority/candidate/
requirements without builder private reasoning. Require VERIFIED before proposing
completion; maintainer acceptance and delivery remain separate decisions.
