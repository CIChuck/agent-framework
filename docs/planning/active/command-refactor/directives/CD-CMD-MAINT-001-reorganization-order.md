# CD-CMD-MAINT-001 — reorganization ordering and verdict reporting

Status: **FIXED-VECTOR REVISION — construction conditional on the recorded review gate.**
Owner: Chuck Russell. Prepared 2026-11-10. Branch: `feature/command-retirement`.
Draft product baseline: `06234fa8a56eaeff09266b4d20ed503dd71df1fa`.
Ownership revision starts from documentation candidate `b41bd4e7` with identical
product bytes. The earlier specification verdict does not cover this revision.

This directive implements the proposed [MAINT-001 specification](../maintenance-reorganization-specification.md).
Its [OpenAI specification council](../validation/maintenance/specification/round1/report.md)
returned VERIFIED (Sol9.0/Astra9.2) for design readiness, not construction.
Chuck Russell authorized drafting this document and requires an opportunity to
review documents before council sub-agents are invoked. The maintainer has now explicitly requested ownership revision and an
OpenAI-only council on the revised documents; that authorization covers review,
not product implementation.
No product code, tests, providers or personal stores are changed by drafting.

## Authority, frozen inputs and boundaries

Apply AGENTS, repository engineering, lifecycle and independent-validation
policies, then the specification M-01..05/MT-01..09 and this bounded directive.
The [construction preparation](../validation/maintenance/construction-preparation-v4.json)
pins the complete baseline revision, specification, council report, policies,
existing source/test bytes and package/lock metadata. Record its SHA256 together
with this directive's final SHA256 in any subsequent exact approval. Only
planning-only descendants with identical product bytes may precede construction.
Unexpected source drift requires reconciliation before implementation.

Primary immutable design inputs:

| Input relative to packet | SHA256 |
| --- | --- |
| `maintenance-reorganization-specification.md` | `56e3cd5fc75b402ab4aeda46f80807873b79a3df96debadb83164c2c0debfdad` |
| `validation/maintenance/construction-preparation-v4.json` | `66e940efd0271b03bd3ae5c358c1320cf30e4d0d474d3c278be67d5e593f8f4d` |

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

Export these types along with the D1b pipeline contracts from the existing
Memory maintenance public surface.
The headless test must use these operations without importing `friday_chat` and
must demonstrate behavior, not just import absence.

## D1b — shared memory-maintenance pipeline

Add `friday_memory.maintenance.pipeline` and `provider_contracts` as the reusable
engine. Mode/skip selection and the entire memory stage loop must move here;
Chat `_planned_steps`, `_skipped_mutation_steps`, `_required_roles` and the
per-step execute loop cannot remain independent authorities. Preserve the
existing domain validation, prompts, bounds, fingerprints and diagnostics when
moving the provider assessment/command-building logic from Chat. No algorithm,
confidence, model or retry-policy changes are authorized by this relocation.

### Shared contracts and public call surface

In `pipeline.py`, use the existing strict/frozen model discipline:

- `MemoryMaintenanceMode`: `full`, `analyze`, `dedupe`, `prune`, `synthesize`,
  `verify`. Backup/recovery remain application-envelope operations, not memory
  pipeline modes.
- `MemoryMaintenanceRequest`: `mode`, plus exact bool fields `execute=False`,
  `skip_synthesis=False`, `skip_verify=False`, `skip_lifecycle=False`,
  `force_reembed=False`. Retain current analyze-execute/full-only flag refusals.
- `MemoryMaintenanceStage`: `analyze`, `reembed`, `dedupe`, `prune`,
  `verify_pending`, `synthesize`, `verify_generated`, `verify`, `lifecycle`.
- `MemoryMaintenanceStageReceipt`: `operation_id: str | None` (32 lowercase hex
  when present), `sequence: int` (exact non-negative stage ordinal),
  `stage: MemoryMaintenanceStage`, `plan_id: str | None` (64 lowercase hex),
  `selection_sha256: str | None` (64 lowercase hex). Frozen/strict; no documents,
  raw references, provider text or credentials. Execute receipts require the
  actual operation ID; provider-free preview uses None and cannot claim applied
  scope. See receipt lifecycle/canonicalization below.
- `MemoryMaintenanceStageResult`: `stage`, required
  `receipt: MemoryMaintenanceStageReceipt`,
  `status: Literal["previewed","completed","skipped","failed"]`, nullable
  non-negative exact `scanned_count`, `candidate_count`, `changed_count`,
  optional shared `verification_counts`,
  `selection_state: Literal["known","deferred"]="known"`, warning strings and
  `MemoryMutationError` members. Mirror the result invariants specified below
  without importing any Chat result/error type.
- `MemoryMaintenancePreflight`: `supported: bool`, `stages: tuple[Stage,...]`,
  `warnings`, `errors`; `supported` cannot coexist with errors. Stage references
  in these signatures mean the shared `MemoryMaintenanceStage` enum.
- `MemoryMaintenanceRunResult`: `operation_id` (32 hex), `succeeded: bool`,
  `stages: tuple[MemoryMaintenanceStageResult,...]`,
  `postconditions: MemoryMutationVerification | None`, `warnings`, `errors`.
  Every execute stage receipt must match operation_id and its unique ordered
  stage ordinal; result.stage must equal receipt.stage. Success requires verified
  postconditions and no failed stage/errors; failure
  cannot report committed success. Do not turn cancellation into a success result.

`MemoryMaintenancePipeline` is constructed from the shared mutation participant,
explicit providers, lifecycle runner, and unchanged synthesis guidance. Expose:

```python
def planned_stages(self, request: MemoryMaintenanceRequest) -> tuple[MemoryMaintenanceStage, ...]: ...
async def preflight(self, request: MemoryMaintenanceRequest) -> MemoryMaintenancePreflight: ...
async def preview(self, request: MemoryMaintenanceRequest) -> tuple[MemoryMaintenanceStageResult, ...]: ...
async def execute(
    self, request: MemoryMaintenanceRequest, *, operation_id: str,
    observer: MemoryMaintenanceObserver | None = None,
    boundary: MemoryMaintenanceBoundary | None = None,
) -> MemoryMaintenanceRunResult: ...
```

Preview/preflight do not open an operation. Execute requires `execute=True`,
opens the shared operation, selects and executes stages itself, checks memory
postconditions, and closes operation/receipt state in `finally`. Reject overlap.
The stage list is derived from request policy once; each data-dependent stage
uses a fresh plan. Shared execution returns failed domain results or propagates
exceptions/cancellation without initiating application restore itself. The outer
transaction must treat any failure as unsuccessful and roll back.

`MemoryMaintenanceObserver` has async `before_stage(receipt)`,
`stage_planned(receipt)`, `after_stage(result)`, `before_postconditions()` and
`after_postconditions(verification)` hooks. The two receipt arguments use
`MemoryMaintenanceStageReceipt`; after_stage receives the shared stage result.
Hooks receive content-safe facts, never control the next stage, and may abort.
Hook failure aborts the pipeline and outer transaction; missing observer is no-op.

### Shared scope-receipt lifecycle (R2-SOL-M02 / MAINT-R2-ASTRA-01)

For execute, before_stage gets the operation/stage ordinal identity with null
plan/digest before planning. After the fresh shared plan is built, Memory emits
stage_planned before provider assessments or apply writes. Memory stages carry
that actual plan ID; verification stages also require a non-null selection digest,
including valid zero pending/created selections. The pipeline copies the planned
receipt unchanged into its completed or post-plan failed result. Planning failure
retains null plan/digest; a skipped stage has null plan/digest; deferred preview
has null operation/digest and no assertion of executed scope. Lifecycle has no
MemoryMutationPlan, so its plan/digest are null. Other planned mutation stages
have a plan ID but no verification selection digest. No later observer may
substitute an unrelated well-formed receipt.

Memory alone computes SHA256 of UTF-8 canonical JSON with `sort_keys=True`,
`separators=(",", ":")`, `ensure_ascii=True`, `allow_nan=False`, containing exactly:
`operation_id`, `sequence`, `stage` (enum value), `plan_id`, `selection` (normalized
MemoryVerificationSelection serialized in JSON mode), and `references` (the actual
fresh-plan provider-record keys, sorted lexicographically by collection then
memory_id, encoded as objects with those two keys). Reject duplicates before
hashing. Thus pending mode binds the actual selected records as well as the
selector; an exact-empty created batch remains a meaningful bound selection.
The plan ID also binds record content under the existing shared plan hash.
Do not return the raw references or content in observer receipts.

**Mandatory independent fixed-vector requirement (Astra A-01).** The immutable
[selection digest vectors](../validation/maintenance/selection-digest-vectors.json)
contain literal canonical UTF-8 JSON and SHA256 expectations for unsorted pending
references with Unicode values and an exact-empty created selection. In
`test_selection_digest_fixed_vectors` (the new Memory pipeline test file), load
an exact package-local copy of this fixture, pass each input through the production
receipt/canonicalization path, and assert both canonical bytes and digest equal
the literal expectations. No expected value may be computed using a production
helper, hash wrapper or receipt serializer. Fixture bytes are pinned by preparation;
copy them unchanged and never regenerate the expected values to match the code.

The planning vectors were authored independently of the future implementation
and their hashes cross-checked with two standard tools. This is reference-data
validation only, not a product-test pass. Keep separate mutation/behavior tests:
wrong Unicode escaping, unsorted keys/references or a trailing newline must fail
these literal assertions; changing operation/stage/plan or an effective reference
must change the digest, while duplicate/invalid references are refused. Headless
and installed probes must exercise the same vectors. Installed probes take a
hash-verified fixture copy from the clean export/private scratch as input and
exercise installed production modules; no source-tree imports or extra runtime
packaging/dependency change is permitted. Runtime tests read only
the package-local fixture, never the active planning packet.


Correlate before/planned/after by operation_id + stage sequence + stage. Validate
that planned/result plan ID and digest match the pipeline's own applied plan and
selection, not merely the shape of supplied strings. Stage evidence from a prior
operation or another plan is rejected. If provider/apply failure occurs after
planning, retain known scope evidence without inventing successful verdicts.
If a stage_planned evidence hook fails, stop before assessments/writes; outer
rollback handles any earlier completed stages. Successful verification may never
persist null scope evidence. This public channel remains usable after the
participant's private receipts are cleared; no Chat access to private state.

### Shared cancellation boundary (R2-SOL-M01)

`MemoryMaintenanceBoundary` exposes generic async
`run_atomic(operation: Callable[[], Awaitable[T]]) -> T`. The pipeline invokes it
for each complete stage (including planning, assessments and apply) and final
memory postconditions. The default is a Memory-owned
`ShieldedMemoryMaintenanceBoundary`, not a direct await: start exactly one owned
stage task, await it through shielding, and on caller cancellation keep draining
that same shielded task until it settles. Repeated caller cancellations must not
cancel the worker or escape the drain early. Do not start/retry the stage again.
If the worker fails, propagate its failure as primary; if it succeeds with
cancellation pending, propagate cancellation at that boundary without starting
the next stage. A worker-originated cancellation also aborts; never report it
as success. Clear operation/selection state only after the worker has settled.

Chat's injected boundary must delegate to this shared behavior or demonstrate
the same shield-and-drain semantics; the existing helper is not assumed to
satisfy repeated-cancellation behavior merely because it shields once. Preserve
existing cancellation notifications and safe fault hooks. Do not shield the
entire pipeline. Headless consumers requiring whole-run restoration must supply
an outer snapshot/rollback transaction; the shared atomic boundary prevents
mid-stage interruption but does not itself roll back earlier completed stages.

A boundary may protect or abort the supplied operation, never replace a result
or run another stage. Validate the returned result against the actual result
produced inside the supplied operation, including receipt, counts and identity.
Default and injected boundary tests must cancel after a write while a graph or
lifecycle await is suspended, then release it and prove drain, no next stage,
propagated cancellation, cleanup and outer restoration. Also cover worker failure
while cancellation is pending, repeated cancellation and observer-hook failure.

Full order and skips are owned here: optional REEMBED, DEDUPE, PRUNE,
VERIFY_PENDING, SYNTHESIZE, VERIFY_GENERATED, optional LIFECYCLE, then memory
postconditions. Verify-only remains one pending pass; synthesize-only does not
implicitly verify. Generated selection comes from the successful shared synthesis
receipt, not the frontend. No receipt is an error; a valid empty/migration-only
receipt yields known zero counts and no assessment call. Keep all command receipts
until shared postconditions finish; clear them on every terminal path.

In `provider_contracts.py`, relocate the existing strict response models,
`MaintenanceLlmRole`, response error classes and diagnostics, LLM/embedding
protocols and explicit provider-registry type without Chat imports. Keep existing
Chat names as aliases/re-exports of those shared types where callers depend on
identity. Specifically extract the strict finish-reason/enclosing-JSON/schema
decoder currently in LiteLlmMaintenanceProvider.complete_model into a reusable
Memory helper taking the existing shared completion response and typed role/model.
Chat provider objects retain transport construction and delegate decoding; no
copy of the response-validation policy remains required in another frontend. Move schema/coverage validation, payload construction, three-role
chaining and synthesis/reembedding command construction into the Memory engine.
Chat-specific config reading and LiteLLM service construction remain injected
composition code; response validation is shared, not reimplemented per UI.

The lifecycle runner protocol and its strict report must be shared and use
Memory errors. The report retains `succeeded`, nullable non-negative exact
scanned/candidate/changed counts, warnings and typed Memory errors, with the
existing success/error invariants; adapt old Chat error construction explicitly. Relocate the bounded promotion/decay adapter for the existing public
`MemoryPromotionService` here as `PromotionLifecycleMaintenanceRunner`; preserve
its count/warning/error rules. Existing Chat lifecycle methods become delegation
wrappers and retain their action instrumentation. Do not move or redesign other
maintenance, background extraction or runtime lifecycle behavior.

Export the shared request/mode/stage/results/preflight/run-result, pipeline,
observer/boundary protocols, stage receipt, default shielded boundary and provider contracts from the existing Memory
maintenance surface. No dependency on `friday_chat` or `friday_commands` may be
introduced into Memory. The headless proof must execute the complete sequence,
not just call low-level selection helpers.

## D2 — Chat integration and application safety envelope

Chat parses input, maps it once to `MemoryMaintenanceRequest`, constructs/injects
Memory-owned provider/lifecycle capabilities and invokes the shared pipeline.
The existing application wrapper retains writer quiescence, leases, memory and
transcript snapshots, durable recovery journal, rollback and runtime resumption.
No transcript/application dependency moves into Memory.

Replace the coordinator's domain per-step loop with one adapter pipeline call
inside the existing mutation transaction. Before it starts, all required verified
snapshots/journal boundaries must already exist. Adapt the injected
`MaintenanceMutationAdapter` to expose
`execute_pipeline(request, *, run_id: str, observer: MemoryMaintenanceObserver,
boundary: MemoryMaintenanceBoundary) -> MemoryMaintenanceRunResult`; replace
its policy-bearing `execute_step` use. Its preflight/preview delegate to the
shared pipeline; returned shared stage lists are authoritative, mapped to Chat
presentation enums. Backup/recovery preserve their current outer paths.

Chat observer hooks translate domain events to existing fault/progress points
and immutable stage evidence. Chat never computes order, skips, scope, verdicts
or required provider roles. Map domain results field-for-field into Chat presentation, including the shared
receipt without hashing or reconstructing references. Preserve error message/store
and safe diagnostics, with explicit category adaptation: shared STORE_UNAVAILABLE
or INVALID_COMMAND in preflight becomes PREFLIGHT_FAILED; stage planning/apply
errors become MUTATION_FAILED; final STORE_INTEGRITY_FAILED or POSTCONDITION_FAILED
becomes INTEGRITY_FAILED. Missing configured capabilities remain
CAPABILITY_UNAVAILABLE. Never turn failure into an empty success result. The aggregate final-live-check path consumes the already computed
shared postcondition result without reapplying commands or recomputing stage
policy. Preserve distinct outer snapshot/live-integrity progress and every
rollback/recovery failure distinction. Retain `VERIFY="verify"` for old records;
new Chat stage enum entries merely mirror shared names for presentation.

All fake/injected adapter signature changes must be named and bounded in tests.
A Chat integration spy must prove exactly one pipeline execute call, request/run
identity and unchanged observer/boundary wiring. A separate headless run must
show identical domain order and results without any Chat module being imported.

### Shared pipeline preflight policy — council advisory A01

The shared pipeline implements this policy; Chat delegates to it. Preview
performs local layout/store/shape inspection only. It neither requires
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
receipt: MemoryMaintenanceStageReceipt | None = None
```

Deferred is allowed only for PREVIEWED with candidate/changed/count summary None.
New executed verification stages copy the shared receipt; legacy results may
read missing receipt as unavailable evidence. New completed verification stages
require non-null operation/plan/selection binding and a count summary matching candidate
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
non-negative artifact-event ordinal), `state: Literal["started","planned",
"completed","failed","skipped"]`,
`receipt: MemoryMaintenanceStageReceipt`, `result: MutationStepResult | None`.
Run ID must equal receipt.operation_id; execute evidence cannot use a preview
receipt. Started/planned require no result; terminal states require a matching
result/status and the same receipt facts. The artifact ordinal increases for
all events; receipt.sequence identifies the stage and stays fixed across its
started/planned/terminal events. Chat stores the Memory-produced receipt, without
computing its digest. A planned verification requires plan/digest; successful
verification cannot have null scope evidence. Failed pre-plan stages can retain
nulls as specified. No memory text, raw reference lists, provider response, prompt
or credentials in this evidence. Recovery journal/bundle v1 stays unchanged.

Persist immutable numbered stage receipts under that run's existing recovery
directory, using `MaintenanceArtifactStore` and the existing safe atomic JSON
writer with its limits/permissions/confinement. Add
`write_run_evidence(evidence: MaintenanceRunEvidence) -> DurableArtifact`.
Keep `durability.py` unchanged. Include sequence and state in filenames; refuse
overwrite. Write started before planning, planned when the shared stage_planned event
arrives, and the terminal receipt after the stage settles. Persist
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
| `packages/friday-memory/src/friday_memory/maintenance/__init__.py` | Add D1/D1b public imports/exports only; no existing suppression expansion. |
| `packages/friday-memory/src/friday_memory/maintenance/pipeline.py` (new) | Shared complete pipeline, policy, assessments, command orchestration, lifecycle adapter and postconditions. |
| `packages/friday-memory/src/friday_memory/maintenance/provider_contracts.py` (new) | Shared strict provider/response/lifecycle contracts and validation diagnostics, relocated without policy changes. |
| `packages/friday-chat/src/friday_chat/reorganization/contracts.py` | Two stage enum entries, the three D2 evidence/result additions and validators; keep journal/bundle schemas unchanged. |
| `packages/friday-chat/src/friday_chat/reorganization/mutation.py` | Delegate to pipeline, re-export relocated types, retain config/provider construction and map shared facts. Remove relocated domain loop/assessment policy. |
| `packages/friday-chat/src/friday_chat/reorganization/coordinator.py` | One pipeline invocation with progress/atomic hooks and run identity; remove local domain order/skips. Preserve recovery/lease/snapshot transaction mechanics. |
| `packages/friday-chat/src/friday_chat/adapters.py` | Only two reorganization lifecycle methods delegate to shared promotion runner; preserve action instrumentation. |
| `packages/friday-chat/src/friday_chat/runtime.py` | Only lifecycle report imports/annotations and corresponding fake methods adapt to shared contracts. |
| `packages/friday-chat/src/friday_chat/reorganization/artifacts.py` | New evidence writer using existing safe store; no snapshot/journal rewriting. |
| `packages/friday-chat/src/friday_chat/commands/registry.py` | Reorganize parser, usage, its metadata/help entry and result formatting only. |
| `packages/friday-chat/tests_chat/test_maintenance_order.py` (new) | Exact mode/order/preflight/count/preview/scope and negative-control tests. |
| `packages/friday-memory/tests_memory/test_maintenance/fixtures/selection-digest-vectors.json` (new) | Exact byte copy of the pinned independent reference vectors; no regeneration. |
| `packages/friday-memory/tests_memory/test_maintenance/test_pipeline.py` (new) | Complete shared order/modes/providers/lifecycle/postconditions/observer/cancellation behavior. |
| `packages/friday-memory/tests_memory/test_maintenance/test_verification_selection.py` (new) | Shared strict models, receipts, planning/apply/postcondition tests. |
| `tests/integration/reorganization/test_maintenance_headless.py` (new) | No-Chat shared consumer, real disposable-store flow and origin checks. |
| `packages/friday-chat/tests_chat/test_reorganization_coordinator.py` | Add new proofs; revise only order, pipeline-call protocol/fakes and intentional preview-readiness expectations. |
| `packages/friday-chat/tests_chat/test_reorganization_mutation.py` | Add proofs and narrowly adapt mapping, signatures, counts and verification-preflight assertions. |
| `packages/friday-chat/tests_chat/test_reorganization_contracts.py` | New strict models; retain v1 journal rejection/round-trip assertions. |
| `packages/friday-chat/tests_chat/test_reorganization_terminal.py` | Exact stage and verdict-count output expectations and rollback labelling. |
| `packages/friday-chat/tests_chat/test_maintenance_commands.py` | Explicit-full parser/help/result and unchanged other-mode assertions. |
| `packages/friday-chat/tests_chat/test_reorganization_foundations.py` | Only directly impacted mode metadata/help expectations, with baseline comparison. |
| `packages/friday-memory/tests_memory/test_maintenance/test_mutation_participant.py` | New result/interface proofs and compatibility assertions; retain all prior behavior assertions. |
| `packages/friday-chat/tests_chat/test_reorganization_response_diagnostics.py` | Preserve relocated response-validation/error-identity behavior; imports/aliases only where necessary. |
| `packages/friday-chat/tests_chat/test_command_production_adapters.py` | Targeted lifecycle delegation and unchanged action/count assertions only. |
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
parser edits. The two named runtime lifecycle report/fake adaptations above do
not authorize runtime assembly or other lifecycle policy changes. If a direct integration seam cannot fit these paths, stop and name
it rather than broadening the allowlist.

## Required named tests and rejection witnesses

Keep these nodes meaningful; equivalent parametrization may expand each node.
Async tests use explicit markers, bounded event-controlled waits and task cleanup.

| Node (new files unless stated) | Mandatory proof |
| --- | --- |
| `test_selection_models_and_operation_receipts` (Memory) | Strict counts/selection fields, exact empty, duplicate/foreign/changed/stale receipt, missing record, old operation, one consumption, begin/end cleanup. |
| `test_scoped_apply_and_postconditions` (Memory) | Same selection bound through fresh re-plan/apply; source drift refused before writes; exact coverage, persisted judge counts, created reference order and empty migration-only result. |
| `test_selection_digest_fixed_vectors` (Memory pipeline/headless/installed) | Literal canonical JSON and hashes, Unicode values, unsorted pending inputs and exact-empty created scope; no production-derived expectations. |
| `test_full_order_and_same_run_synthesis` (Memory pipeline) | Full order and all skip combinations; newly verified source used immediately; old meta/non-source coverage retained; rejected/uncertain remain ineligible. |
| `test_generated_scope_is_exact` (Memory pipeline) | Only returned new references; no uncertain source retry; no counts/timestamp inference; migration-only/abstention empty; repeated runs, errors and cancellation clean state. |
| `test_preview_and_verification_call_policy` (Memory pipeline) | Missing providers and tripwire probe/complete/embed methods; zero calls in preview and empty verification; conditional configuration checks and fresh assessment failures roll back. |
| `test_stage_counts_and_failure_rendering` (Chat) | Mixed/empty/rejected/uncertain counts, no triple-counting; skipped/deferred/failed unknowns; attempted-versus-retained rollback output. |
| `test_explicit_full_and_unchanged_modes` (Chat) | Implicit/explicit equivalence, duplicate/conflicting flags, quoted/unknown/recovery arguments, help and other-mode behavior. |
| `test_default_and_injected_cancellation_boundaries` (Memory pipeline/headless) | Cancel after a preceding write during suspended graph/lifecycle work; repeated cancel, worker error, drain, no next stage, cleanup and outer rollback on both paths. |
| `test_scope_receipts_reach_durable_evidence` (Memory/Chat/headless) | Both verification stages, pending/exact-empty/migration-only selections, before/planned/after correlation, matching Memory and persisted digests, foreign/substituted/omitted evidence refused, hook-write failure rollback and repeat-run isolation. |
| `test_headless_created_verification_flow` (headless) | Real disposable graph/Chroma and local provider/embedding doubles; complete full/skip/standalone pipeline, chain/selection/counts/lifecycle/postconditions and no `friday_chat` import before/after execution. |
| `test_chat_delegates_pipeline_once` (Chat) | One pipeline execute call; no local order/skip/provider-role policy; request/run identity, safe hooks, typed result consumption and whole-run rollback. |
| Existing recovery suite plus new cases | Persisted baseline completed/interrupted v1 fixtures, installed recovery, whole-run rollback restoring verdicts/removing new insights, unknown journal versions, failed sidecar writes and new-stage interruptions. |

In private product copies demonstrate named **call-phase assertion** failures for
old order, broad generated selection, modified selection at re-plan, missing
receipt clearing, fabricated/three-role counts, provider-backed preview, migration
count used as creation scope, missing second pass, a Chat-local order fallback, callback result substitution
omitted/substituted planned/result scope receipts, unsafe direct-await default
and weakened response coverage.
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
2. **D1/D2:** implement shared contracts and complete Memory pipeline first, then Chat
   delegation and the retained application safety envelope. Run meaningful
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
"$MAINT_PYTHON" -B "$MAINT_RUNNER" focused-memory python -B -m pytest -p no:cacheprovider -q packages/friday-memory/tests_memory/test_maintenance/test_mutation_participant.py packages/friday-memory/tests_memory/test_maintenance/test_verification_selection.py packages/friday-memory/tests_memory/test_maintenance/test_pipeline.py
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
Include Memory mutation/pipeline/provider_contracts and Chat
contracts/mutation/coordinator/artifacts/registry plus the two named lifecycle
adaptation paths. Include the fourth new test file in formatting/lint checks.
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
"$MAINT_PYTHON" -B "$MAINT_RUNNER" lint ruff check --no-cache packages/friday-memory/src/friday_memory/maintenance/mutation.py packages/friday-memory/src/friday_memory/maintenance/pipeline.py packages/friday-memory/src/friday_memory/maintenance/provider_contracts.py packages/friday-chat/src/friday_chat/reorganization packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/tests_chat/test_maintenance_order.py packages/friday-memory/tests_memory/test_maintenance/test_verification_selection.py tests/integration/reorganization/test_maintenance_headless.py packages/friday-chat/src/friday_chat/adapters.py packages/friday-chat/src/friday_chat/runtime.py packages/friday-memory/tests_memory/test_maintenance/test_pipeline.py packages/friday-memory/src/friday_memory/maintenance/__init__.py
"$MAINT_PYTHON" -B "$MAINT_RUNNER" types mypy --cache-dir "$MAINT_SCRATCH/mypy" packages/friday-memory/src/friday_memory/maintenance/mutation.py packages/friday-memory/src/friday_memory/maintenance/pipeline.py packages/friday-memory/src/friday_memory/maintenance/provider_contracts.py packages/friday-chat/src/friday_chat/reorganization/contracts.py packages/friday-chat/src/friday_chat/reorganization/mutation.py packages/friday-chat/src/friday_chat/reorganization/coordinator.py packages/friday-chat/src/friday_chat/reorganization/artifacts.py packages/friday-chat/src/friday_chat/commands/registry.py packages/friday-chat/src/friday_chat/adapters.py packages/friday-chat/src/friday_chat/runtime.py
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

Run new-file formatting on the two new Memory source files, all four new Python
test files and the new installed
probe. Existing-file format comparisons use the immutable baseline profile and
exact same formatter/config; preserve pre-existing debt. The allowlisted Memory
`__init__` and all modified tests must also be linted. Record any
whole-file type/lint baseline findings separately, never add suppressions.

Create `validation/maintenance/installed_probe.py`: deterministic headless and
Chat command flows on disposable real stores; complete shared pipeline and one-call Chat delegation; normal `-I -B` and optimized
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

**Current gate:** The maintainer requested the shared-ownership revisions and
fresh Astra/Sol review of both revised documents. This is document review only;
the [conditional approval](../approval/maintenance-reorganization-conditional.md)
allows advancement only after both fresh Astra/Sol reviewers independently return
VERIFIED with scores at least9.5/10 each and no mandatory findings. Missing scores,
BLOCKED, any lower score or unresolved mandatory findings mean stop and return
the result to Chuck Russell. Do not average scores, round up, selectively omit
findings, add reviewers to override a failing seat or loop to chase the threshold.
The controller must verify the exact approved hashes and gate before code edits. The earlier specification verdict does
not validate this newly drafted directive or its new concrete choices.
