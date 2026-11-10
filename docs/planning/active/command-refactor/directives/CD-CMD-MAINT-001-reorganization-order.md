# CD-CMD-MAINT-001 — reorganization ordering and verdict reporting

Status: **PROPOSED FOR HUMAN REVIEW; construction and council not authorized.**
Owner: Chuck Russell. Prepared 2026-11-10. Branch: `feature/command-retirement`.
Draft baseline: `06234fa8a56eaeff09266b4d20ed503dd71df1fa`.

This directive implements the proposed [MAINT-001 specification](../maintenance-reorganization-specification.md).
Its [OpenAI specification council](../validation/maintenance/specification/round1/report.md)
returned VERIFIED (Sol9.0/Astra9.2) for design readiness, not construction.
Chuck Russell authorized drafting this document and requires an opportunity to
review documents before council sub-agents are invoked. Stop at that review gate.
No product code, tests, providers or personal stores are changed by drafting.

## Authority, frozen inputs and boundaries

Apply AGENTS, repository engineering, lifecycle and independent-validation
policies, then the specification M-01..05/MT-01..09 and this bounded directive.
The [construction preparation](../validation/maintenance/construction-preparation.json)
pins the complete baseline revision, specification, council report, policies,
existing source/test bytes and package/lock metadata. Record its SHA256 together
with this directive's final SHA256 in any subsequent exact approval. Only
planning-only descendants with identical product bytes may precede construction.
Unexpected source drift requires reconciliation before implementation.

Primary immutable design inputs:

| Input relative to packet | SHA256 |
| --- | --- |
| `maintenance-reorganization-specification.md` | `e085d9fbad99b8cf59887db4590e41ee6f9af2cb963dd99e4fbbc7ee7f2332ab` |
| `validation/maintenance/construction-preparation.json` | `e06675197bb46b5ccdb1324dd12ba567ebee4366cdd7035031fee0d68a686e96` |

Scope is one bounded maintenance unit: pending verification before synthesis,
targeted verification of newly generated meta insights, per-stage verdict counts,
offline preview and the companion FU-011 explicit `--full` spelling. Accepted
MEMQ, its query contracts, shared repairs and closed UAT remain historical fact.
This approval, if granted, must explicitly permit the named shared Memory changes
rather than inheriting an exception from earlier Chat parity work.

No model/budget/batching/prompt-policy change, factual web research, automatic
approval of memories, fuzzy matching, new command family, TUI implementation,
general coordinator extraction, store migration, dependency/lock/config change,
ingestion/retrieval/eligibility-policy redesign or personal-store migration.
No live provider, network, secret, telemetry, cleanup, push, PR, merge or release.
Use deterministic local provider doubles and disposable stores for validation.
Preserve dirty example YAML, `.friday-old/`, exports, accepted evidence and every
unrelated local artifact. Never broadly stage or clean the checkout.

## D1 — shared typed contracts and scoped mutation

Keep new shared contracts in `friday_memory.maintenance.mutation`, using the
existing strict/frozen/extra-forbid Pydantic base and explicit exceptions.
Essential runtime validation must work under normal Python and `-O`.

### Exact additions

```python
class MemoryVerificationCounts(StrictMutationModel):
    selected: int
    verified: int
    rejected: int
    uncertain: int

class MemoryVerificationSelection(StrictMutationModel):
    mode: Literal["pending", "created"] = "pending"
    operation_id: str | None = None
    synthesis_plan_id: str | None = None
    references: tuple[VectorMemoryReference, ...] = ()
```

Counts are exact non-negative integers (reject bool, strings, floats) with
`selected == verified + rejected + uncertain`. Selection preserves immutable
ordered reference snapshots and rejects duplicate `(collection, memory_id)` keys.
Pending selection requires absent IDs and empty references. Created selection
requires operation ID matching 32 lowercase hex and synthesis-plan ID matching
64 lowercase hex; an empty reference tuple means no targets, never pending/all.
Keep the existing plan's capacity guards; do not add unbounded provider input.

Extend `MemoryMutationPlan` and `MemoryMutationCommand` with
`verification_selection: MemoryVerificationSelection | None = None`. Non-VERIFY
steps require None. VERIFY normalizes None to pending selection consistently;
include the normalized selection in canonical plan hashing and command binding.

Extend `MemoryMutationResult` with:

```python
created_references: tuple[VectorMemoryReference, ...] | None = None
verification_counts: MemoryVerificationCounts | None = None
```

A successful SYNTHESIZE result must report the exact additions actually persisted,
in command order, including `()` for no additions or migration-only synthesis.
Failed synthesis and other steps report None. Never derive references from
`changed_count`: migrations also change records. Validate uniqueness and existing
maximum-output bounds. A successful VERIFY returns counts from persisted final
judge updates, including zero counts for an empty plan; other/failed steps return
None. Counts are published only after all relevant writes succeed. Historical
results lacking new fields can still be read as unavailable evidence; a newly
executed successful verification must not omit its summary.

### Protocol and operation identity

Add the following synchronous operation-scoped methods to the participant
protocol and `ExplicitMemoryMutationParticipant`:

```python
def begin_operation(self, operation_id: str) -> None: ...
def end_operation(self, operation_id: str) -> None: ...
def verification_selection_for(
    self, synthesis_result: MemoryMutationResult,
) -> MemoryVerificationSelection: ...

async def plan(
    self, step: MemoryMutationStep, *,
    verification_selection: MemoryVerificationSelection | None = None,
) -> MemoryMutationPlan: ...
```

`apply` and `verify_postconditions` keep their signatures. Original unscoped
`plan(step)` and direct operations remain compatible. Created-selection planning
requires an active operation. The participant keeps only instance-local receipts
for successful synthesis applications within that operation, keyed by plan ID;
the receipt binds returned references and the full successful result. A repeated
synthesis plan ID must not overwrite a different receipt. `verification_selection_for`
accepts only the matching successful synthesis receipt from this participant's
current operation, including its explicit empty batch. Reject altered results,
wrong steps, failed results, foreign/prior-operation receipts and absent receipts.
No caller-supplied timestamps or scans can establish created scope.

`begin_operation` rejects an already active operation; `end_operation` checks
identity and clears receipts/consumption state. Do not retain operation state on
any terminal path. No module-global cache. A created batch is consumable once:
successful created verification marks its receipt consumed; repeated execution
is refused. Planning and apply's pre-write revalidation do not consume it.

In `apply`, re-plan with the original normalized selection, compare plan identity
and command selection, then retain all existing freshness/payload checks. Created
scope must equal the registered batch, with every requested record present,
active and still an unverified maintenance-generated meta insight. Pending mode
retains the existing selector, including uncertain/old-meta/non-source records.
Do not change source eligibility or re-verify pending uncertain records in the
second pass. Shared postconditions must check the final status for generated
records as well as preceding source updates; no overwrite of earlier commands.

Export the two new types from the existing Memory maintenance public surface.
The headless test must use these operations without importing `friday_chat` and
must demonstrate behavior, not just import absence.

## D2 — Chat sequencing, preflight and presentation

Add `VERIFY_PENDING="verify_pending"` and `VERIFY_GENERATED="verify_generated"`
to Chat `MutationStep`. Preserve `VERIFY="verify"` for standalone mode and old
records. Both new stages map to shared `MemoryMutationStep.VERIFY`; they retain
the current classifier/researcher/judge chain and exact-coverage validation.

Full order is optional REEMBED, DEDUPE, PRUNE, VERIFY_PENDING, SYNTHESIZE,
VERIFY_GENERATED, optional LIFECYCLE, then existing live postconditions. Apply
the specification's complete skip/mode matrix. Verify-only remains one pending
pass; synthesize-only does not implicitly verify its outputs.

Extend `MaintenanceMutationAdapter.begin_run` and the concrete implementation to
`begin_run(request, *, run_id: str) -> None`. The coordinator supplies the actual
operation run ID already used for recovery evidence. The adapter invokes shared
`begin_operation(run_id)` and `end_operation(run_id)` on its matching lifecycle,
including rollback, cancellation and failure. Adapt injected test doubles only
where this explicit interface changes. Request equality alone is not run identity.
If shared begin fails, do not leave the Chat adapter marked active. End/cleanup
errors must preserve the primary operation failure and recovery evidence.

The adapter obtains the generated selection through the shared receipt method
after successful synthesis and passes it unchanged to shared planning. It may
retain the typed result/selection only for that run; it must not reconstruct
references. A full run reaching generated verification without its synthesis
receipt is an error. A valid empty batch reports completed/no candidates, zero
counts and no verification assessment. Migration-only synthesis is a required
fixture: metadata backfill must not cause old records to enter the second stage.

### Council advisory A01: exact provider-call policy

Preview performs local layout/store/shape inspection only. It neither requires
configured providers nor calls any LLM/embedding `probe`, `complete_model` or
embed method. Re-plan locally for observable current eligibility, but report
downstream verdict/output-dependent candidates as deferred/unknown. Preview
must not begin a shared mutation operation or create recovery bundles.

Execute preflight retains store checks, limits, static provider/configuration
availability and existing synthesizer/reembedding readiness checks when those
capabilities may be used. For verification roles, use **configuration checks
only**, not LLM `probe()` calls. Actual readiness is established by the existing
three assessment calls when a non-empty fresh verification plan executes; any
failure follows whole-operation rollback. This intentionally removes the current
verification readiness completion before mutation. No validation is weakened.

If pending selection is empty and synthesis is skipped or has no possible new
outputs, missing verification providers must not fail that operation. If future
generated verification may be needed, check its configuration before mutations,
even if synthesis later abstains. Do not run verification probes for that potential
need. Both verification stages with empty actual selections cause zero role
probe/completion calls. Distinguish static availability, other provider readiness
and actual assessments in receipts; count no readiness response as a verdict.

### Exact result additions and rendering

Add a strict/frozen Chat `VerificationCounts` model with the same four fields and
invariants as the shared counts. Convert returned shared facts field-for-field;
do not recalculate verdicts in Chat. Add to `MutationStepResult`:

```python
verification_counts: VerificationCounts | None = None
selection_state: Literal["known", "deferred"] = "known"
```

Deferred is allowed only for PREVIEWED with candidate/changed/count summary None.
New completed verification stages require a count summary matching candidate
count. Skipped/failed stages carry no success summary. Preserve old `VERIFY`
result deserialization with missing counts as unavailable, not fabricated zeros.
No-candidate is displayed from known zero candidates and zero summary, without
inventing a new terminal success status. Standalone newly executed VERIFY also
reports its summary. Counts describe final judge decisions, not three-role totals.

Keep per-stage `Step verify_pending` / `Step verify_generated` labels distinct
from snapshot/live-integrity checks. Display selected/verified/rejected/uncertain
counts and explicit skipped/deferred/no-candidate/failure status. If the run
rolls back, show any preceding completed-stage results as attempted and rolled
back; never claim retained verdict updates. Existing safe role/model/finish/field
diagnostics and primary-versus-rollback error precedence remain unchanged.

FU-011: admit `--full` as a mode flag equivalent to implicit FULL. It conflicts
with any other explicit mode; retain duplicate, unknown, full-only and recovery
argument validation. Update the one reorganize help/metadata entry and usage.
No global parser change. Existing `/meta` guidance can keep its text because the
recommended spelling becomes supported. Other commands and argument rules stay
unchanged.

## Durable evidence and legacy compatibility — chosen route

Keep `RecoveryJournal.schema_version == 1`, its fields, transition rules and
coarse completed ProgressStep semantics unchanged. Keep aggregate recovery-bundle
schemas, checksums, ownership/path restrictions and restore behavior unchanged.
Recovery rolls back interrupted operations; it does not resume at a new stage.
Do not add generated selections/counts to these existing recovery schemas.

Add `MaintenanceRunEvidence` in Chat contracts, strict/frozen/extra-forbid:
`schema_version: Literal[1]=1`, `run_id: str` (32 hex), `sequence: int` (exact,
non-negative), `stage: MutationStep`, `state: Literal["started","completed",
"failed","skipped"]`, `selection_sha256: str | None` (64 hex),
`result: MutationStepResult | None`. Started requires no result; other states
require a matching result/status. Selection digest is computed from the canonical
typed shared selection, never raw documents. No memory text, provider response,
prompt or credentials in this evidence.

Persist immutable numbered stage receipts under that run's existing recovery
directory, using `MaintenanceArtifactStore` and the existing safe atomic JSON
writer with its limits/permissions/confinement. Add
`write_run_evidence(evidence: MaintenanceRunEvidence) -> DurableArtifact`.
Keep `durability.py` unchanged. Include sequence and state in filenames; refuse
overwrite. Write started before a stage and its result after completion. Persist
all success receipts before the terminal-success journal transition. Missing
success receipt/write failure before success causes ordinary rollback.

Rollback/recovery must never depend on these new receipts. Failure to write a
failure receipt must not prevent rollback, restore or the existing durable journal
record of recovery-required state. Preserve the original failure and separately
surface evidence-write failure. Unknown/malformed sidecar versions must fail
reporting closed (unavailable evidence), but cannot block restoration from a
valid existing v1 journal and bundle. Do not guess counts from them.

Do not edit old journals, fabricate old stage summaries, scan personal recovery
directories or automatically migrate stores. Before edits, persist real v1
completed and interrupted journals/bundles using the baseline coordinator against
disposable stores; preserve exact fixture bytes and hashes. After implementation,
recover the interrupted baseline bundle through the installed new code, and read
the completed historical record without inventing two verification stages.
Also test unknown/malformed v1 journals, new-stage interruptions, corrupted new
receipts and rollback failure. Existing v1 checks continue to reject unknown
journal versions and extra fields. This resolves the journal-fixture advisory
without a recovery-schema migration.

Baseline fixture generation uses a clean pinned old-source export, never the new
contracts. Preserve raw generated fixture bytes and their source/provenance hashes.
Where absolute scratch paths prevent portable replay, test-only relocation may
rewrite the root/path/fingerprint fields and dependent manifest checksums through
an audited JSON-pointer mapping with original/new hashes. It must preserve schema
version, journal state/history, safe boundary, progress, record contents and
verdicts. Exercise ordinary installed v1 readers and recovery on the relocated
copy. This permission is only for synthetic test copies, never user journals.

## Exact file allowlist

All paths are repository-relative. No unlisted product/test path may change.

| Path | Permitted edits |
| --- | --- |
| `packages/friday-memory/src/friday_memory/maintenance/mutation.py` | D1 typed additions, operation receipts, selection-bound planning/apply, counts/references and postconditions only. |
| `packages/friday-memory/src/friday_memory/maintenance/__init__.py` | Add two public type imports/exports only; no existing suppression expansion. |
| `packages/friday-chat/src/friday_chat/reorganization/contracts.py` | Two stage enum entries, the three D2 evidence/result additions and validators; keep journal/bundle schemas unchanged. |
| `packages/friday-chat/src/friday_chat/reorganization/mutation.py` | Stage mapping, operation wiring, exact selection consumption, preflight/preview policy and count adaptation only. |
| `packages/friday-chat/src/friday_chat/reorganization/coordinator.py` | Stage order/skips, run ID wiring, lifecycle-safe cleanup and immutable stage evidence; preserve recovery/lease/snapshot mechanics. |
| `packages/friday-chat/src/friday_chat/reorganization/artifacts.py` | New evidence writer using existing safe store; no snapshot/journal rewriting. |
| `packages/friday-chat/src/friday_chat/commands/registry.py` | Reorganize parser, usage, its metadata/help entry and result formatting only. |
| `packages/friday-chat/tests_chat/test_maintenance_order.py` (new) | Exact mode/order/preflight/count/preview/scope and negative-control tests. |
| `packages/friday-memory/tests_memory/test_maintenance/test_verification_selection.py` (new) | Shared strict models, receipts, planning/apply/postcondition tests. |
| `tests/integration/reorganization/test_maintenance_headless.py` (new) | No-Chat shared consumer, real disposable-store flow and origin checks. |
| `packages/friday-chat/tests_chat/test_reorganization_coordinator.py` | Add new proofs; revise only order, new begin_run keyword/fakes and intentional preview-readiness expectations. |
| `packages/friday-chat/tests_chat/test_reorganization_mutation.py` | Add proofs and narrowly adapt mapping, signatures, counts and verification-preflight assertions. |
| `packages/friday-chat/tests_chat/test_reorganization_contracts.py` | New strict models; retain v1 journal rejection/round-trip assertions. |
| `packages/friday-chat/tests_chat/test_reorganization_terminal.py` | Exact stage and verdict-count output expectations and rollback labelling. |
| `packages/friday-chat/tests_chat/test_maintenance_commands.py` | Explicit-full parser/help/result and unchanged other-mode assertions. |
| `packages/friday-chat/tests_chat/test_reorganization_foundations.py` | Only directly impacted mode metadata/help expectations, with baseline comparison. |
| `packages/friday-memory/tests_memory/test_maintenance/test_mutation_participant.py` | New result/interface proofs and compatibility assertions; retain all prior behavior assertions. |
| `tests/integration/reorganization/test_reorganization_recovery.py` | Add v1 and new evidence recovery cases; narrow fake signature adaptations. |
| `packages/friday-chat/tests_chat/fixtures/maintenance-v1/` (new) | Baseline-generated synthetic persisted journal/bundle fixture bytes and provenance; no personal store data. |
| `packages/friday-chat/README.md`, `packages/friday-memory/README.md` | Describe this behavior and public shared boundary only. |
| `docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md` | Append FU-011 status/evidence only; preserve other entries. |
| Current packet planning/approval/directive/status/log, `validation/maintenance/`, `uat/maintenance-reorganization-uat.md` | Bounded approvals, freeze/evidence, installed probe, human test plan and review records. |
| `docs/planning/board.yaml`, generated `docs/planning/README.md` | Reconcile current gate/state/evidence only. |

Do not remove old tests/assertions, add skips/xfails, weaken typing or suppressions,
or rewrite accepted evidence. Where an old expected order/output is intentionally
changed, record the exact assertion delta and new equivalent stronger coverage.
No `friday-commands`, runtime assembly, config, metadata/dependency/lock or global
parser edits. If a direct integration seam cannot fit these paths, stop and name
it rather than broadening the allowlist.

## Required named tests and rejection witnesses

Keep these nodes meaningful; equivalent parametrization may expand each node.
Async tests use explicit markers, bounded event-controlled waits and task cleanup.

| Node (new files unless stated) | Mandatory proof |
| --- | --- |
| `test_selection_models_and_operation_receipts` (Memory) | Strict counts/selection fields, exact empty, duplicate/foreign/changed/stale receipt, missing record, old operation, one consumption, begin/end cleanup. |
| `test_scoped_apply_and_postconditions` (Memory) | Same selection bound through fresh re-plan/apply; source drift refused before writes; exact coverage, persisted judge counts, created reference order and empty migration-only result. |
| `test_full_order_and_same_run_synthesis` (Chat) | Full order and all skip combinations; newly verified source used immediately; old meta/non-source coverage retained; rejected/uncertain remain ineligible. |
| `test_generated_scope_is_exact` (Chat) | Only returned new references; no uncertain source retry; no counts/timestamp inference; migration-only/abstention empty; repeated runs, errors and cancellation clean state. |
| `test_preview_and_verification_call_policy` (Chat) | Missing providers and tripwire probe/complete/embed methods; zero calls in preview and empty verification; conditional configuration checks and fresh assessment failures roll back. |
| `test_stage_counts_and_failure_rendering` (Chat) | Mixed/empty/rejected/uncertain counts, no triple-counting; skipped/deferred/failed unknowns; attempted-versus-retained rollback output. |
| `test_explicit_full_and_unchanged_modes` (Chat) | Implicit/explicit equivalence, duplicate/conflicting flags, quoted/unknown/recovery arguments, help and other-mode behavior. |
| `test_headless_created_verification_flow` (headless) | Real disposable graph/Chroma and local provider/embedding doubles; exact shared behavior and no `friday_chat` import before/after execution. |
| Existing recovery suite plus new cases | Persisted baseline completed/interrupted v1 fixtures, installed recovery, whole-run rollback restoring verdicts/removing new insights, unknown journal versions, failed sidecar writes and new-stage interruptions. |

In private product copies demonstrate named **call-phase assertion** failures for
old order, broad generated selection, modified selection at re-plan, missing
receipt clearing, fabricated/three-role counts, provider-backed preview, migration
count used as creation scope, missing second pass and weakened response coverage.
Run unchanged controls with the same harness; record canonical origins and file
hashes before testing, at session finish and afterward. Import/setup/collection
failures earn no mutation credit. No supplied installation is mutated.

## Execution, commands and evidence gates (future; not run by drafting)

One implementation unit/candidate plus one OpenAI implementation council is
planned; no automatic three-deliverable or repeated readiness-council workflow.

1. **D0 before edits:** verify approval/directive/preparation hashes and baseline
   product equality. Record actual tests/debt, AST/assertion inventories and all
   protected dirty/personal/export metadata. Generate disposable v1 fixtures using
   the pinned old implementation. Establish offline guard and source origins.
2. **D1/D2:** implement shared contracts first, then Chat wiring. Run meaningful
   focused tests and rejection controls, retaining baseline assertions/deltas.
3. **D3:** freeze product source; full regressions, clean build/replay and installed
   normal/optimized proof. Freeze administrative evidence afterward; distinguish
   artifact source from candidate. Verify product/probe bytes match both.
4. **Independent review:** only after explicit authorization, fresh Astra/Sol
   read-only review of the implementation delta and bounded aggregate. Private
   scratch; exact logical index before status; no builder transcript or nested
   agents. Reconcile mandatory findings, not scores. Two unsuccessful bounded
   correction cycles return unresolved findings to Chuck Russell.
5. Stop for targeted human UAT and separate acceptance. No delivery follows.

Use the existing Python3.13.10 uv environment and pinned pilot harness preparation
and eight-wheel wheelhouse (validated hashes), never sync/upgrade/download Python.
Create new external scratch. Materialize nothing into a supplied evidence lane.
The runner supplies offline/frozen/no-sync flags, audit guard and private caches.
An absolute `--cache-dir` must also point into this new scratch.

```sh
export GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1
MAINT_ROOT="$PWD"
MAINT_PYTHON="$MAINT_ROOT/.venv/bin/python"
MAINT_HARNESS="$MAINT_ROOT/docs/planning/active/command-refactor/validation/pilot/harness"
MAINT_SCRATCH="$(mktemp -d /tmp/friday-maint-build.XXXXXX)"
# MAINT_WHEELHOUSE: supplied eight-wheel input directory, verified by prepare.py.
"$MAINT_PYTHON" -B "$MAINT_HARNESS/prepare.py" "$MAINT_SCRATCH/prepared" --wheelhouse "$MAINT_WHEELHOUSE"
MAINT_RUNNER="$MAINT_SCRATCH/prepared/pilot_run.py"
"$MAINT_PYTHON" -B "$MAINT_RUNNER" guard python -B "$MAINT_HARNESS/guard_selftest.py"
"$MAINT_PYTHON" -B "$MAINT_RUNNER" focused-memory python -B -m pytest -p no:cacheprovider -q packages/friday-memory/tests_memory/test_maintenance/test_mutation_participant.py packages/friday-memory/tests_memory/test_maintenance/test_verification_selection.py
"$MAINT_PYTHON" -B "$MAINT_RUNNER" focused-chat python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat/test_maintenance_order.py packages/friday-chat/tests_chat/test_reorganization_contracts.py packages/friday-chat/tests_chat/test_reorganization_coordinator.py packages/friday-chat/tests_chat/test_reorganization_mutation.py packages/friday-chat/tests_chat/test_reorganization_terminal.py packages/friday-chat/tests_chat/test_maintenance_commands.py packages/friday-chat/tests_chat/test_reorganization_foundations.py
"$MAINT_PYTHON" -B "$MAINT_RUNNER" recovery-headless python -B -m pytest -p controls -p no:cacheprovider -q tests/integration/reorganization
"$MAINT_PYTHON" -B "$MAINT_RUNNER" full-memory python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-memory/tests_memory
"$MAINT_PYTHON" -B "$MAINT_RUNNER" full-chat python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-chat/tests_chat --ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py
"$MAINT_PYTHON" -B "$MAINT_RUNNER" commands python -B -m pytest -p no:cacheprovider -q packages/friday-commands/tests_commands tests/integration/test_package_cohort_metadata.py
"$MAINT_PYTHON" -B "$MAINT_RUNNER" cli python -B -m pytest -p controls -p no:cacheprovider -q packages/friday-cli/tests_cli
```

At D0 omit only future new files, recording their absence rather than claiming a
pass. Do not deselect failures discovered in existing suites to manufacture green
results; reconcile pre-existing debt versus new regressions. Retain root Ruff,
root pytest collection/execution and legacy formatting as explicit baseline debt
where reproduced. Prior counts/scores are not current executions.

Run changed-source/test `ruff check --no-cache`, new/changed-file format checks,
and explicit-source mypy with both `MYPY_CACHE_DIR` and `--cache-dir` private.
Include Memory mutation, Chat contracts/mutation/coordinator/artifacts/registry.
Compare old-file formatting debt to the pinned baseline with the retained
no-new-format-debt helper; do not reformat entire legacy files. Run package
metadata, offline lock on an exact clean candidate export, board validate,
dashboard check, documentation lifecycle and staged/unit whitespace checks.

Build from a clean `git archive` of the recorded product source using pinned
`bundle.py`, the supplied locked artifact set and `--require-pilot-edge`; use a
second independent output directory for replay. Never rebuild in supplied old
bundles. Compare actual artifact hashes, source inventories and default/neutral
profiles. Require exact installed byte/member/origin evidence, dependency checks
and the retained full closure. No new extras or executable.

Representative exact static/build argv after the named paths exist (D0 runs the
same checks on existing paths and records all baseline failures):

```sh
export MYPY_CACHE_DIR="$MAINT_SCRATCH/mypy"
"$MAINT_PYTHON" -B "$MAINT_RUNNER" lint ruff check --no-cache packages/friday-memory/src/friday_memory/maintenance/mutation.py packages/friday-chat/src/friday_chat/reorganization packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/tests_chat/test_maintenance_order.py packages/friday-memory/tests_memory/test_maintenance/test_verification_selection.py tests/integration/reorganization/test_maintenance_headless.py
"$MAINT_PYTHON" -B "$MAINT_RUNNER" types mypy --cache-dir "$MAINT_SCRATCH/mypy" packages/friday-memory/src/friday_memory/maintenance/mutation.py packages/friday-chat/src/friday_chat/reorganization/contracts.py packages/friday-chat/src/friday_chat/reorganization/mutation.py packages/friday-chat/src/friday_chat/reorganization/coordinator.py packages/friday-chat/src/friday_chat/reorganization/artifacts.py packages/friday-chat/src/friday_chat/commands/registry.py
# MAINT_REVISION is the frozen committed product-source revision.
# MAINT_ARTIFACTS is the supplied locked-input directory, with its inventory verified.
git archive --format=tar --output "$MAINT_SCRATCH/source.tar" "$MAINT_REVISION"
mkdir "$MAINT_SCRATCH/source"
tar -xf "$MAINT_SCRATCH/source.tar" -C "$MAINT_SCRATCH/source"
"$MAINT_PYTHON" -B "$MAINT_RUNNER" bundle python -B "$MAINT_HARNESS/bundle.py" "$MAINT_SCRATCH/source" "$MAINT_SCRATCH/bundle" "$MAINT_SCRATCH/prepared" --revision "$MAINT_REVISION" --artifacts "$MAINT_ARTIFACTS" --require-pilot-edge
"$MAINT_PYTHON" -B "$MAINT_RUNNER" replay python -B "$MAINT_HARNESS/bundle.py" "$MAINT_SCRATCH/source" "$MAINT_SCRATCH/replay" "$MAINT_SCRATCH/prepared" --revision "$MAINT_REVISION" --artifacts "$MAINT_ARTIFACTS" --require-pilot-edge
"$MAINT_PYTHON" -B "$MAINT_RUNNER" lock uv lock --check --offline --project "$MAINT_SCRATCH/source"
"$MAINT_PYTHON" -B "$MAINT_RUNNER" metadata python -B scripts/check-package-metadata.py
"$MAINT_PYTHON" -B "$MAINT_RUNNER" board python -B scripts/friday-dev-board.py validate
"$MAINT_PYTHON" -B "$MAINT_RUNNER" dashboard python -B scripts/friday-dev-board.py render --check
"$MAINT_PYTHON" -B "$MAINT_RUNNER" docs python -B scripts/check-documentation-lifecycle.py
```

Run new-file formatting on all three new Python test files and the new installed
probe. Existing-file format comparisons use the immutable baseline profile and
exact same formatter/config; preserve pre-existing debt. The allowlisted Memory
`__init__` and all modified tests must also be linted. Record any
whole-file type/lint baseline findings separately, never add suppressions.

Create `validation/maintenance/installed_probe.py`: deterministic headless and
Chat command flows on disposable real stores; normal `-I -B` and optimized
`-I -B -O`, explicit guard preload, installed canonical module origins; implicit/
explicit full, shared receipt scopes/counts, no-provider preview, migration-only
synthesis, v1 restart recovery and induced rollback. Use explicit require/raise,
not assert-only runtime validation. Prove old-order/broad-scope/counterfeit-count
substitutions are refused for their intended reasons in private copies.

Frozen earlier probes/captures remain unchanged. Adding `--full` intentionally
changes reorganize help/metadata and the permitted maintenance output only.
Record exact before/after cells for that command; preserve every other retained
pilot/SESSION/DIAG/MEMQ observation. If an immutable earlier probe rejects this
approved delta, keep that result failed with the precise reason and supply a
separate bounded comparison/probe proving the exception and unchanged remainder;
never monkeypatch its API, suppress arbitrary rows or call it a passing run.

## Reporting, human review and stop conditions

Deliver exact approval/base/product/candidate/probe/artifact hashes; original and
current inventories; named suite counts/exits; negative-control assertion witnesses;
provider-call traces; source/installed origins; v1 fixture provenance/recovery;
rollback state; real-store reference/count evidence; executed-versus-inspected
receipts; baseline failures and residual platform limits. Record skipped versus
unexecuted future evidence honestly. Draft UAT using disposable state, showing
order/counts/same-run progression/skips and one understandable induced failure.

Stop for scope mismatch, protected-state drift, missing offline inputs, an
unexplained new regression, or a required schema/package/policy change outside
this allowlist. Do not silently broaden the unit or relax verification safety.

**Current stop:** Chuck Russell reviews this proposed directive and its exact
preparation pins. No council/sub-agent invocation is authorized until he directs
it after reviewing these documents. No implementation is authorized without
subsequent exact construction approval. The earlier specification verdict does
not validate this newly drafted directive or its new concrete choices.
