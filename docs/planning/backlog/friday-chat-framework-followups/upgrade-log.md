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

## FU-008: Export The Bounded Provider Options Union

Status: proposed
Discovered During: Friday Chat typed LLM configuration migration
Framework Package: `packages/friday-llm`
Requested Change: Export a stable public `ProviderOptions` discriminated union,
protocol, or parser from the `friday_llm` package root when a second bounded
provider-options type is introduced.
Reason: Friday LLM `0.1.0a1` root-exports `LMStudioQwenOptions`, but its
`ProviderOptions` union is available only from an implementation submodule.
Downstream configuration packages should not import incidental internals or
accept `dict[str, Any]` merely to remain extensible.
Impact If Not Changed: Friday Chat must extend its own closed union each time a
new root-exported concrete provider-options model is added.
FridayV2 Workaround: Friday Chat `0.1.0a1` accepts only the root-exported
`LMStudioQwenOptions | None`. Normalized generation remains provider-independent,
and arbitrary provider keyword mappings remain prohibited.
Compatibility Risk: Low for the current single concrete type; medium once
multiple provider option models exist because downstream union definitions can
drift.
Suggested Follow-Up Tests: Add root-export coverage, discriminated parsing for
each bounded namespace, rejection of unknown namespaces and extra keys, and a
downstream type-check fixture that imports no internal Friday LLM modules.
Source Evidence: The Friday Chat configuration migration uses only public root
exports and records provider options separately from normalized generation.


## FU-009: Omit Absent Ingestion Description Metadata

Status: CLOSED — shared repair and combined retest accepted by Chuck Russell,2026-11-10
Discovered During: MEMQ-001 D2 persisted-listing validation, 2026-11-09
Framework Package: `packages/friday-memory` / public Chroma metadata boundary;
the caller constructing this metadata is Friday Chat's FrameworkMemoryAdapter.
Requested Change: Separately approve a bounded repair that omits the optional
description key when no description is supplied, covering both single-document
and batch-ingestion branches. Preserve explicit descriptions and listing groups.
Reason: The real `/ingest FILE` handler produces description=None; the adapter
includes that value in metadata and Chroma rejects it with TypeError. Paired
clean pre-D2/candidate controls reproduce identical messages through the adapter
and real command. The ingest code is unchanged in MEMQ.
Impact If Not Changed: Users who omit a description cannot ingest through the
real adapter; fake-adapter behavior can conceal this limitation.
FridayV2 Workaround: Supply a non-empty description, such as
`/ingest /path/document.txt project notes`. Use prepared absent-description
persisted records to assess listing; listing already accepts a missing key.
Compatibility Risk: Review absent versus empty descriptions and both ingest
branches before approval. No repair or waiver is included in MEMQ-001.
Suggested Follow-Up Tests: Real-adapter command and direct single/batch calls
with missing, empty and explicit descriptions; persisted metadata and listing
groups/counts; regression against explicit-description ingestion.
Source Evidence: [MEMQ D2 round1 reconciliation](../../active/command-refactor/validation/memory-queries/implementation/d2/council-round1/report.md),
including all three independently reproduced paired controls; [CMD-F05](../friday-tui-command-followups/README.md).


Current repair: reusable Friday Memory metadata builder; Chat calls it in both
branches. Real disposable Chroma command tests cover omitted/empty/explicit
descriptions, counts/protection/listing/re-ingest; human UAT is accepted/closed.
[Repair evidence](../../active/command-refactor/validation/memory-queries/uat-shared-repair/README.md).

## FU-010: Preserve Maintenance Verification Response Diagnostics

Status: CLOSED — diagnostic implementation and combined retest accepted by Chuck
Russell,2026-11-10; full reorganization on exit yields positive /meta per maintainer.
Discovered During: MEMQ populated-meta UAT,2026-11-09.
Requested Change: Preserve shared completion metadata and safe role/model/schema/
finish/validation-field evidence without exposing provider content. Distinguish
incomplete enclosing JSON from recovered nested objects.
Source Evidence: Actual full run failed_rolled_back during234-record verification;
synthesis had0 candidates with156 quarantined sources. A synthetic truncated
response reproduces the generic schema-error mechanism, not the actual provider
reply. REM-CMD-MEMQ-UAT-002 implements the bounded shared diagnostic boundary;
[implementation/evidence](../../active/command-refactor/validation/memory-queries/uat-diagnostics/README.md).
Compatibility: Legacy parsing default and callers retain behavior; maintenance
uses strict enclosing-object parsing and fails closed on explicit length output.
Model/config/budget, batching, quarantine, order and rollback remain unchanged.
Resolution: The maintainer reports the combined retest successful and positive
/meta after full reorganization on exit. MEMQ UAT is accepted/closed. The earlier
error cause is not retrospectively asserted; the separate explicit --full syntax
issue remains FU-011, not an open verification-response blocker.

## FU-011: Reorganize Rejects The Explicit Full Mode Flag

Status: OPEN — documented command-syntax defect; implementation not started.
Discovered During: Maintainer MEMQ UAT acceptance,2026-11-10.
Owner: Friday Chat command argument handling; later shared MAINT-001 migration
must preserve or deliberately repair its grammar under approved scope.

Reproduction: Enter `/reorganize --full --execute` at the Chat prompt.
Expected: Explicit full mode is accepted and invokes the same full maintenance
request as `/reorganize --execute`, preserving execute/recovery/rollback safeguards.
Actual: The parser rejects --full as an unknown argument before maintenance starts.
The maintainer reports this error; exact source-AST execution reproduces
`Unknown argument '--full'.` No live maintenance/provider/store operation was run.

Cause: `_REORGANIZE_MODE_FLAGS` in commands/registry.py omits --full, while its
no-mode default is full. The `/meta` empty-state guidance in commands/memory_queries.py
recommends `/reorganize --full --execute`, producing an application guidance/parser
mismatch. Exit maintenance bypasses slash-command parsing and constructs a typed
FULL request directly for session full/deep modes. That is consistent with the
maintainer's successful full reorganization on exit and positive `/meta` results.
Current accepted syntax: `/reorganize --execute` selects full execution;
`/reorganize` alone is a full dry run. This syntax observation does not attest a
new full production run. The spelling `-- full` is not proposed as valid syntax.

Impact: The advertised explicit command blocks an on-demand Meta Insight refresh.
It is separate from the accepted read-only `/meta` query and the closed MEMQ UAT.
A successful verification step alone does not generate Meta Insights: synthesis
requires previously verified sources, and current full mode synthesizes before
verification. Model review, JSON/schema validation, quarantine and rollback can
also explain generation delays; see the flow note below. No external fact-checking
is supplied by the current verifier role names alone.

Bounded follow-up: reconcile the explicit --full grammar and user guidance; test
parity with default full mode, dry-run/--execute, duplicate/conflicting modes,
recovery exclusions and coordinator dispatch. Preserve pipeline, verification,
quarantine, model/budget/config and backup/rollback policy. No implementation,
policy change or broader migration is authorized by this defect registration.
Source evidence: [acceptance](../../active/command-refactor/approval/memory-queries-acceptance.md),
[pure-parser evidence](../../active/command-refactor/validation/memory-queries/acceptance/reorganize-argument-evidence.json),
[verification flow](../../active/command-refactor/validation/memory-queries/acceptance/verification-flow.md).


### FU-011 — MAINT-001 implementation checkpoint (2026-11-10T17:05:42.159818+00:00)

Explicit `/reorganize --full` admission/help is implemented locally under the
exact MAINT-001 directive. Duplicate/conflicting modes remain refused. Full
installed proof and independent implementation validation are still pending;
this is not acceptance or closure of unrelated follow-ups.


## FU-012: Extract Actual PDF/DOCX/XLSX/PPTX Text Before Ingestion

Status: PROPOSED — four-format extraction, shared ingestion chunking/embedding guards and Tools adoption; no code yet
Discovered During: Maintainer report and guarded source inspection,2026-11-10;
maintainer subsequently expanded scope to XLSX and PPTX.
Framework Package: Friday Tools shared extraction; Friday Commands file arguments;
Friday Chat delegation/default document dependencies; shared Memory ingestion policy,
LLM capability/limit enforcement and minimal Core contracts. Engine replacement is excluded;
narrow durable store-identity/query-envelope and role handoffs are proposed exceptions.
The correction draft also covers identity-preserving snapshot/restore/direct-client
admission and Runtime/Core/CLI composition. No recovery ordering changes. The
maintainer explicitly selected fresh-store-required behavior: preserve existing
files and /read, with no legacy mode, migration or reset.
Requested Change: Use one pinned Docling pipeline for PDF/DOCX/XLSX/PPTX extraction,
with local PDF OCR, quoted paths, explicit format coverage and dependency/model
requirements. Upgrade named Tools consumers through the companion adoption plan.
Proposed format defaults cover visible worksheets/slides, saved formula values
without recalculation and labeled speaker notes. All ingestion sources use
document/512-token defaults with document/recursive/fixed overrides. Existing
text/web fetching stays; token/dimension guards are shared. Qwen4B is illustrative
only; fresh test stores require no legacy migration. No unrelated format rollout.
Reason: SmartFileReader returns placeholders for PDF/DOCX/XLSX and does not admit
PPTX. Old PDF page failures can become successful diagnostic content. Existing
Tools consumers also require explicit routing, beyond adding a shared helper.
Compatibility Risk: Exact read/ingest format/help and default closure change;
shared tokenizer preserves unrelated commands. Freeze all four format policies
and Tools XLSX selections/pagination before construction. No historical record
cleanup, storage-engine replacement, formula calculation or slide rendering.
Round1 source inspection found absent maintained web/automatic-tool ingestion
routes, direct smart_read storage/cache bypass and undeclared model preparation.
The corrected plan classifies those routes and binds fresh stores explicitly.
A separate parser follow-up remains: malformed text `--lines*` silently selects
100 lines. This unit preserves that text compatibility but reports effective
limits/truncation; document inputs refuse it and the new literal `--` suffix is opaque.
Suggested Follow-Up Tests: Genuine PDF/DOCX/scanned/multi-sheet/multi-slide fixtures
through registry, shared extraction, public Tools and disposable Chroma. Inspect
late markers in stored chunks, notes/tables/order and exact coverage. Refuse
missing dependencies/models, corrupt/partial/empty output, uncached formula
results and malformed paths; prove installed normal/optimized behavior and the
mandatory certifi>=2026.10.19 floor.
Source Evidence: [Historical source assessment](../../active/command-refactor/validation/document-ingestion/assessment.md),
[scope expansion](../../active/command-refactor/validation/document-ingestion/format-expansion.json)
and [proposed remediation](../../active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md).
