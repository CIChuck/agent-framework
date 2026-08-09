# FridayV2 Framework Upgrade Log

This document records framework package changes discovered while building
FridayV2. During the first FridayV2 parity pass, existing framework packages are
frozen so FridayV2 can be compared against the reference CLI at
`tests/integration/memory/friday.py` without moving the baseline.

## Freeze Directive

FridayV2 must be implemented as an app layer over the existing framework
packages. Do not modify existing framework package source or tests during the
FridayV2 parity implementation pass.

Frozen packages:

- `packages/friday-agent`
- `packages/friday-cli`
- `packages/friday-core`
- `packages/friday-finance`
- `packages/friday-llm`
- `packages/friday-mcp`
- `packages/friday-memory`
- `packages/friday-moltbook`
- `packages/friday-runtime`
- `packages/friday-sandbox`
- `packages/friday-speech`
- `packages/friday-telemetry`
- `packages/friday-tools`
- `packages/friday-transcript`

Allowed implementation targets:

- `packages/friday-chat/`
- `packages/friday-chat/tests_chat/`
- Workspace metadata required to register and run `packages/friday-chat`.
- FridayV2 planning documents under `docs/planning/`.

If FridayV2 exposes a missing capability, bug, type contract problem, or
awkward interface in a frozen framework package, do not patch that package
during the parity pass. Record the requested framework change below with source
evidence, impact, the FridayV2 workaround, and suggested follow-up tests. A
secondary framework-upgrade pass can then improve the framework package content
without weakening the FridayV2-to-`friday.py` comparison.

## Entry Template

```text
## FU-000: Short Title

Status: proposed | accepted | deferred | resolved
Discovered During: FridayV2 phase or test
Framework Package: packages/friday-...
Requested Change:
Reason:
Impact If Not Changed:
FridayV2 Workaround:
Compatibility Risk:
Suggested Follow-Up Tests:
Source Evidence:
```

## Upgrade Items

## FU-001: Align Graph Store Protocol With Runtime Graph Consumers

Status: proposed
Discovered During: FridayV2 real-runtime adapter validation
Framework Package: `packages/friday-memory`
Requested Change: Add the graph operations used by runtime diagnostics to the
declared graph-store interface, or provide a typed diagnostic/listing facade.
Reason: FridayV2 needs `/entities` parity with `friday.py`, which calls graph
lookup/list operations. The concrete graph stores expose `find_by_label()` and
`get_all_nodes()`, but the public `GraphStoreAdapter` protocol does not.
Impact If Not Changed: App-layer integrations must cast at the framework
boundary even when using supported concrete graph stores.
FridayV2 Workaround: `FrameworkMemoryAdapter.list_entities()` casts the graph
store to `Any` only at the protocol boundary and keeps the rest of the adapter
typed.
Compatibility Risk: Low behavior risk, but medium type-safety risk because
future graph-store implementations may not provide the diagnostic methods.
Suggested Follow-Up Tests: Add framework-level protocol conformance tests for
entity listing and label lookup, then remove the FridayV2 boundary cast.
Source Evidence: `uv run mypy packages tests main.py` reported
`packages/friday-chat/src/friday_chat/adapters.py` errors for missing
`find_by_label` and `get_all_nodes` on `GraphStoreAdapter` before the local
adapter cast was added.

## FU-002: Restore Repository-Wide Validation Gates Outside FridayV2

Status: proposed
Discovered During: FridayV2 release-gate validation
Framework Package: `packages/friday-agent`, `packages/friday-runtime`,
`packages/friday-sandbox`, `packages/friday-tools`, and legacy integration
fixtures under `tests/integration`
Requested Change: Repair existing repository-wide pytest, Ruff, and mypy
failures that are outside `packages/friday-chat`.
Reason: FridayV2 package-level gates pass, but repository-wide gates currently
fail in frozen framework packages and legacy prototype/test files.
Impact If Not Changed: FridayV2 can be validated in isolation, but the root
repository cannot use its standard all-repo commands as a clean release signal.
FridayV2 Workaround: Scope FridayV2 validation to
`packages/friday-chat/tests_chat`, `uv run ruff check packages/friday-chat`,
`uv run mypy packages/friday-chat`, compatibility tests, and CLI startup smoke.
Compatibility Risk: Medium operational risk because unrelated framework
failures can obscure FridayV2 regressions in CI.
Suggested Follow-Up Tests: After a framework-upgrade pass, rerun
`uv run pytest`, `uv run ruff check .`, and `uv run mypy packages tests main.py`
as required root release gates.
Source Evidence: `uv run pytest` reported 11 failures outside Friday Chat
(`friday-agent` CopilotAgent tests and `friday-runtime` DI tests);
`uv run ruff check .` reported 12 existing issues outside Friday Chat;
`uv run mypy packages tests main.py` still exits 1 with no remaining
`packages/friday-chat` errors.

## FU-003: Scoped Reorganization Recovery Contract Exception

Status: resolved
Discovered During: Reorganization Remediation 1
Framework Package: `packages/friday-memory` and `packages/friday-transcript`
Requested Change: Authorize the smallest public, typed store-owned mutation,
snapshot, integrity, and restore boundaries needed by the Friday Chat
coordinator while preserving Friday Memory and Friday Transcript independence.
Reason: Safe coordinated reorganization cannot be implemented in the app layer
by guessing paths or copying live Chroma and WAL-mode SQLite files. Each package
must own its persistence invariants; Friday Chat must own the aggregate bundle,
journal, exclusion, rollback, and recovery policy.
Impact If Not Changed: Manual and exit reorganization would remain fail-closed
because no complete Transcript-inclusive recovery bundle or verified rollback
could be assembled.
FridayV2 Workaround: None. The approved construction directive granted a scoped
freeze exception for explicit Friday Memory layout/recovery/mutation contracts,
the public graph adapter operations they require, and a narrow Friday Transcript
WAL-safe snapshot participant. Friday Chat composes those public contracts
without private cross-package access.
Compatibility Risk: Medium persistence risk, controlled by schema-versioned
strict models, owner-only artifacts, operation-time path/lease revalidation,
mandatory verified snapshots, postcondition checks, and disposable rollback and
restart-recovery drills. Existing state is not moved or rewritten merely to
adopt the contracts.
Suggested Follow-Up Tests: Retain the focused package recovery/mutation suites,
the provider-free PTY test, the real-participant full pipeline drill, and the
rollback-failure/restart/recovery drill as release gates. Do not delete retained
recovery evidence automatically without a separately approved retention policy.
Source Evidence: Gate B independently validated Chroma public-API logical export
and rebuild plus SQLite online backup/restore. Gate C independently validated the
shared coordinator, durable journal/bundle, fault boundaries, rollback, and
restart recovery. Gate D focused evidence covers the explicit provider matrix,
real mutation participant, nested typed results, owner-only categorical logs,
Transcript live-integrity preflight, operation-time alias revalidation, and
bounded PTY progress. Final enablement uses one typed, request-specific
coordinator capability: backup and recovery remain available without the
mutation adapter, while mutating manual/exit modes require it. Synthesized
`meta_insight` records retain bounded source lineage, and no-error unfinished
journals remain inspectable and explicitly terminalizable. Final package/root
validation remains recorded in the construction directive's supervised
execution record.
Cleanup Point: This exception is complete when the supervising maintainer closes
Gate D. Future maintenance must use these public contracts or receive separate
authority; the deprecated app paths through `MemoryReorganizer` are not an
authorized recovery-policy bypass.

## FU-004: Preserve Archived Status In Transcript Session Reads

Status: proposed
Discovered During: Friday Chat command remediation Gate C
Framework Package: `packages/friday-transcript`
Requested Change: Make `SQLiteTranscriptStore.get_session()` and
`list_sessions(include_archived=True)` reliably return
`TranscriptSession.archived=True` for archived rows, and align the public store
protocol with the concrete archived/context-log query arguments used by clients.
Reason: The SQLite filter correctly excludes archived rows when
`include_archived=False`, but row-to-model conversion currently returns
`archived=False` after a successful public `archive_session()` call.
Impact If Not Changed: App adapters cannot trust the public session model to
render an explicit archived state for a selected session.
FridayV2 Workaround: `FrameworkTranscriptAdapter` compares public paginated
non-archived session listings with the public exact-ID result and maps the
Friday Chat-owned view without reading private store fields or issuing SQL.
Compatibility Risk: Low behavior risk; the workaround adds bounded public read
queries and can be removed after the model mapping is corrected.
Suggested Follow-Up Tests: Archive one session, assert exact-ID and
include-archived list results retain `archived=True`, assert the default list
still excludes it, and add declared-protocol conformance for archived and
context-log reads.
Source Evidence: Gate C production-adapter coverage observed a successful
`archive_session()` followed by `get_session()` returning a false archived flag,
while `list_sessions(include_archived=False)` excluded the same session.

## FU-005: Idempotent And Retrieval-Safe Synthesis Contract

Status: resolved
Discovered During: Post-UAT synthesis evaluation
Framework Package: `packages/friday-memory`
Requested Change: Extend the public typed mutation plan and command with
topic-bound synthesis groups, deterministic source/document fingerprints,
configured policy thresholds, legacy metadata migration, and complete generated
record metadata. Exclude unverified maintenance-generated synthesis from normal
retrieval while retaining it for explicit diagnostics and maintenance.
Reason: Source validation and transactional rollback protected one mutation,
but did not prevent unchanged repeat runs from creating more semantically
similar vectors, did not isolate synthesis by topic, and allowed newly generated
unverified records into ordinary recall.
Impact If Not Changed: Repeated full or synthesis-only maintenance could grow
memory indefinitely and reinforce unverified generated conclusions in later
chat context.
FridayV2 Workaround: None. The user authorized this narrowly scoped Friday
Memory contract and retrieval change after UAT. Friday Chat owns provider
prompting, payload bounds, abstention, and embeddings; Friday Memory owns the
fresh plan, stable fingerprint, mutation validation, metadata migration,
postconditions, and retrieval eligibility rule.
Compatibility Risk: Medium memory-behavior risk. Existing source records are
not rewritten. Legacy maintenance-generated `meta_insight` records are preserved
and receive only deterministic synthesis metadata when their bounded lineage
maps to a current topic group. Ordinary non-maintenance records retain existing
retrieval behavior.
Suggested Follow-Up Tests: Retain focused synthesis planning/mutation/retrieval
tests and the disposable two-run full-reorganization integration drill. In UAT,
repeat `/reorganize --synthesize --execute` and `/reorganize --execute` against
the same unchanged state and require the repeated synthesis step to report
`changed=0` without another synthesis LLM or embedding call.
Source Evidence: Focused tests cover verified source and topic isolation,
configured thresholds and semantic prompt guidance, bounded per-group provider
payloads, empty/low-confidence/exact-duplicate abstention, legacy lineage
migration, generated-record metadata/postconditions, retrieval quarantine, and
an unchanged second full execute with stable vector count and zero additional
synthesis provider work.

## FU-006: Cancellation-Safe Live Extraction Commit Contract

Status: resolved
Discovered During: Post-UAT extraction and manual-reorganization concurrency
Framework Package: `packages/friday-memory`
Requested Change: Add stable vector upsert operations and make the live
extractor defer cancellation only after it crosses into memory mutation.
Reason: Friday Chat must cancel a running extraction before foreground inference
or exclusive maintenance, but the former extractor wrote graph and vector state
incrementally. Cancelling during those writes could requeue the current turn
after a partial commit and then duplicate insights, summaries, or graph access
evidence on retry.
Impact If Not Changed: Manual reorganization could complete while leaving
extraction permanently paused, or a resumed extraction could duplicate durable
memory after cancellation at an unsafe point.
FridayV2 Workaround: None. The user authorized the narrow Friday Memory change.
Friday Chat assigns one stable identity to each buffered turn, distinguishes
normally buffered work from an actively preempted extractor, and resumes only
the latter after exclusive admission is released. Friday Memory shields the
current mutation phase to a safe commit boundary and upserts insight/summary
slots under deterministic turn-derived identifiers.
Compatibility Risk: Low-to-medium memory-write risk. Existing additive vector
APIs are unchanged; idempotent upsert is an explicit new path used by live
extraction. Provider analysis remains cancellable, and no active `.friday`
state is used by automated validation.
Suggested Follow-Up Tests: Retain the extraction commit-cancellation test, the
same-turn cardinality test, stable adapter requeue tests, and manual-maintenance
resume tests as package gates. UAT should start a real extractor, execute
`/reorganize --synthesize --execute`, and verify that only unfinished work is
resumed once after the maintenance terminal result.
Source Evidence: Focused provider-free tests prove cancellation waits for the
current commit, a committed cancelled turn is not requeued, later turns retain
their stable identities, repeated extraction of the same turn leaves two vector
records (one insight and one summary), and post-maintenance resume occurs after
the exclusive gate on completion, preflight failure, and verified rollback.

## FU-007: Mixed-Timezone Lifecycle Compatibility

Status: resolved
Discovered During: Post-UAT exit lifecycle processing
Framework Package: `packages/friday-memory`
Requested Change: Normalize timezone-aware UTC and legacy timezone-naive local
datetimes before lifecycle and retrieval elapsed-time calculations.
Reason: Reorganization synthesis correctly persists timezone-aware UTC
`created_at` metadata, while legacy lifecycle code used a naive local `now`.
Exit promotion therefore raised `TypeError` when it encountered a synthesized
short-term record.
Impact If Not Changed: One incompatible record aborts the remainder of the
short-term promotion scan. Friday Chat also previously ignored the returned
lifecycle error and recorded the shutdown action as successful.
FridayV2 Workaround: None. Friday Memory now performs non-mutating compatibility
normalization for promotion, decay, inclusion, and retrieval-factor elapsed-time
calculations. Friday Chat rejects a lifecycle result containing errors.
Compatibility Risk: Low. Stored timestamps are not migrated or rewritten;
legacy naive values retain local-wall-time semantics and aware values retain
their declared offset.
Suggested Follow-Up Tests: Retain mixed-aware/naive scorer coverage and a full
promotion-cycle test containing a verified synthesis-style record.
Source Evidence: The original exception was reproduced without provider or
active runtime data. Focused tests prove mixed timestamps produce the expected
24/25-hour calculations and that lifecycle result errors cross the Friday Chat
adapter boundary.
