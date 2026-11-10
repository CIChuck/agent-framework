# MAINT-001 — reorganization order and verification visibility

Status: **REVISED DRAFT — shared Memory pipeline ownership; no implementation approval.**
Prepared 2026-11-10 on `feature/command-retirement`, baseline `1093aff8`.
Owner: Chuck Russell. This is a proposed maintenance unit, separate from accepted
MEMQ-001 and its closed UAT records.

Chuck Russell requested a bounded specification for reorganization ordering and
subsequently required an opportunity to review the documents **before council
sub-agents are invoked**. The maintainer now authorizes document revision, local document checks and a
fresh OpenAI-only council on the revised documents. Product changes, live
provider calls and operations on personal stores remain unauthorized.

## Problem and intended result

Today a full run orders optional reembedding, dedupe, prune, synthesis,
verification, then lifecycle maintenance. Synthesis requires verified sources;
newly verified sources therefore cannot contribute until a later run. Generated
meta insights start unverified and currently enter the following verification
step. Moving that step earlier without an output check would remove this latter
protection. The [current-flow note](validation/memory-queries/acceptance/verification-flow.md)
describes the accepted behavior; it remains historical evidence.

The proposed full run verifies pending memories first, synthesizes from eligible
verified sources, and verifies only its newly generated meta insights afterward.
One successful run can thus both approve eligible sources and produce checked
meta insights. Approval of every source or generated insight is not guaranteed.

Companion defect FU-011: `/reorganize --full --execute` is rejected even though
full mode is the default and `/meta` recommends that spelling. This proposal
includes accepting `--full` as an explicit spelling of existing full mode.

## M-01 — execution sequence

Preserve preflight, capability checks, exclusive mutation admission, snapshots,
snapshot verification and durable recovery setup before mutations. Then:

1. Optional reembedding, in its existing position when requested.
2. Dedupe and prune, in that order, preserving their existing rules.
3. **Verify pending memories** (`verify_pending`). Select the same active,
   non-empty records that the current verification selector would select at
   this point, including eligible old meta records and records that are not
   synthesis inputs. Do not reduce this to non-meta source records. Already
   verified/rejected records remain excluded; uncertain records remain eligible.
4. **Synthesize** (`synthesize`). Re-plan from the successfully updated live
   state. Only records satisfying the existing verified-source, topic, group,
   confidence, fingerprint and limit rules may contribute. Do not reuse a
   pre-verification synthesis plan.
5. **Verify new meta insights** (`verify_generated`). Target exactly the
   `(collection, memory_id)` references successfully created by step 4 in this
   operation. Do not repeat verification of pending/uncertain source records,
   scan all pending records again, or include old meta records by timestamp.
6. Optional lifecycle maintenance, under existing rules.
7. Existing live postcondition and integrity verification, durable completion
   and cleanup of the operation's own temporary recovery resources.

Memory validates its own postconditions before returning pipeline success. The
outer application retains its aggregate recovery/integrity checks.

The two verification stages remain distinct from snapshot verification and
live storage-integrity checks. Each selected verification stage retains the
classifier → researcher → judge chain. Persist the judge's final verdicts.

## M-02 — run-local selection and shared ownership

The memory-maintenance pipeline belongs in `friday-memory`: mode/skip policy,
stage order, scoped planning, provider assessment, synthesis, generated-record
selection, verdict persistence/counts, lifecycle invocation and memory
postconditions. Chat invokes that shared pipeline once; it must not choose or
iterate domain stages itself. A future TUI or headless caller uses the same
pipeline and typed result, without importing Friday Chat.

The existing application safety envelope remains outside that memory pipeline:
writer quiescence, memory/transcript recovery snapshots, exclusive leases,
durable application journal, whole-operation rollback and runtime resumption.
Chat currently supplies that envelope and renders shared events/results. Its
callbacks may record progress, preserve atomic stage/cancellation boundaries or
abort safely; they cannot reorder, skip, substitute or broaden memory stages.
Extracting the complete cross-store recovery coordinator is outside this unit.
This separates domain orchestration from the existing application transaction;
it does not move transcript or UI dependencies into Memory.

Shared provider contracts and assessment/command-building logic needed by the
pipeline must also be reusable. Configuration lookup and provider construction
stay at the composition boundary, injected through Memory-owned protocols.
Existing Chat import locations may re-export the shared contracts for compatibility.
Merely moving the order list while keeping an essential stage engine in Chat
would not satisfy this specification.

Every execute path, including a headless caller without injected hooks, must
shield and drain each active stage/postcondition before propagating external
cancellation. An outer rollback transaction is still required where whole-run
restoration is promised; stage atomicity does not itself restore earlier stages.
No headless default may directly await a multi-write stage without that protection.

Memory produces a content-safe stage receipt binding operation, stage ordinal,
plan identity and the digest of the normalized selection plus actual selected
references. Observer events/results carry this receipt. Started-before-planning,
skipped and deferred states may lack a plan/digest; a successfully planned
verification, even an empty selection, must expose both before assessment/writes.
Completed or post-plan failed verification results retain the same receipt. Chat
copies it into durable evidence and never recomputes the selection digest.

The implementation design must define typed shared contracts for:

- an explicit verification selection: existing pending scope versus an exact
  set of record references; empty exact selection means no targets, never all;
- a successful synthesis result that returns exact created references, not an
  inferred count, timestamp scan, document-text match or difference of totals;
- stage identity, selection identity and verification outcome counts.

Bind scoped plans and commands to their selection and existing plan identity.
Reject duplicate, missing, foreign or unexpected references. Validate persisted
records against the fresh plan and preserve existing apply/postcondition checks.
Missing/corrupt generated-reference evidence fails the operation; it must not
silently fall back to broad verification. A failed synthesis step cannot publish
its proposed additions as successfully created records.

Generated references are operation-local, recorded with the same durable run
identity when needed for recovery/reporting, and cleared on completion, rollback
or a new invocation. No mutable process-global selection cache is permitted.
A headless consumer must exercise scoped verification and generated-reference
handling using `friday-memory` without importing `friday_chat`.

## M-03 — outcomes and counts

Each verification stage reports its own selected, verified, rejected and
uncertain counts. After successful exact coverage and persistence:

`selected = verified + rejected + uncertain`

Counts are non-negative exact integers and describe final judge decisions for
that stage, not the sum of classifier/researcher/judge responses. Empty selection
reports zero counts and requires no verification-model call. Stage output must
distinguish completed, skipped, no candidates and failed. On failure, unavailable
verdict counts must not be displayed as zero or as a successful result.

Persist counts alongside stage identity and show them in the command result and
normal terminal reporting. For example, one completed stage may report
`selected=12; verified=8; rejected=1; uncertain=3`. Use per-stage counts rather
than a misleading unique-record total: old records may be checked in the first
stage, while only newly created records enter the second.

Rejected and uncertain decisions are valid outcomes, not malformed-response
failures. They remain stored under the existing quarantine/eligibility policy;
do not automatically approve, delete or retry them within this operation. New
meta insights with those verdicts remain ineligible as synthesis sources under
the existing policy. This unit does not change `/meta` query filtering or promise
that every displayed insight is verified.

Verification remains LLM assessment of supplied text. It does not gain web
research, independent factual certification or a new confidence policy.

## M-04 — modes, skips and preview

| Request | Proposed behavior |
| --- | --- |
| No mode flag or explicit `--full` | Same full mode; order follows M-01. |
| Full with `--skip-synthesis` | Run `verify_pending` unless skipped; skip synthesis and `verify_generated`. |
| Full with `--skip-verify` | Skip both verification stages. Synthesize only from already verified eligible sources; newly generated records retain their existing unverified status. Report verification was deliberately skipped. |
| Both skip flags | Skip both verification stages and synthesis; retain other selected steps. |
| Full with `--skip-lifecycle` | Skip lifecycle only. |
| Full with `--force-reembed` | Preserve reembedding before dedupe/prune. |
| Standalone `--verify` | Preserve pending-record verification selection and three-role behavior; no implicit synthesis or second pass. |
| Standalone `--synthesize` | Preserve existing synthesis-only semantics and verified-source restriction; no implicit verification. |
| Analyze/backup/dedupe/prune/recovery | Preserve existing semantics and admission rules. |

`--full` conflicts with other explicit mode flags, including combinations that
could otherwise be mistaken for the default. Keep existing duplicate/unknown
flag policy and full-only flag validation. No global parser redesign. Update
help/metadata for this one mode spelling; retain unrelated help and dispatch.

Dry-run must show the proposed order and scopes without mutating state or
invoking LLMs/embeddings. Synthesis/output-verification candidates that depend
on future verdicts or generated records are **deferred/unknown**, not predicted
as zero. Distinguish current eligibility observations from an execution forecast.
No provider should be required solely to compute preview counts.

## M-05 — failure, cancellation and recovery

Preserve strict complete-JSON extraction, schema validation, confidence bounds,
exact decision coverage and sanitized response diagnostics. Do not introduce
batching, budget changes, model substitution or lenient response repair here.
Large-batch/provider capacity remains a separate follow-up if it fails.

Failure of `verify_pending` prevents synthesis. Failure of synthesis prevents
`verify_generated`. Failure of either verification stage, persistence, lifecycle
or postconditions follows the existing whole-operation rollback/recovery path.
This includes undoing newly generated insights and preceding verdict changes;
no partially committed success is reported. Preserve existing cancellation safe
boundaries, durable journals, exclusive leases, verified backups and rollback
integrity checks. An uncertain/rejected verdict alone does not trigger rollback.

Do not overwrite the primary failure with rollback details. Preserve run ID,
stage, safe role/model/finish-reason/validation-field diagnostics and final
`failed_rolled_back` versus `recovery_required` status. Rolled-back counts must
be labelled as attempted results, not retained storage updates.

Any new stage/scope/count fields need an explicit journal/result compatibility
design before construction. Historical journals and recovery tests remain
readable through a versioned reader or remain recoverable by an explicitly
documented compatible path; do not relabel old `verify` history as two stages.
Malformed/unknown versions fail closed with actionable recovery guidance.

## Bounded implementation surface and exclusions

Anticipated seams, to be narrowed to exact files and typed signatures in the
construction directive after specification review:

- `friday_memory/maintenance/{mutation,pipeline,provider_contracts}.py`: scoped
  mutation, shared pipeline sequencing/execution, provider contracts, assessment
  validation, run-local references, counts, lifecycle and memory postconditions.
- `friday_chat/reorganization/{contracts,mutation,coordinator}.py`: one pipeline
  invocation, typed capability/configuration wiring, progress/result adaptation
  and the existing cross-store recovery envelope; no domain stage-order policy.
- `friday_chat/commands/registry.py` and existing terminal/result rendering:
  `--full` admission/help and distinct stage summaries.
- Focused package tests, a headless shared-capability test, installed proof and
  maintenance-specific documentation/UAT instructions.

No new command family, TUI implementation, general coordinator extraction,
ingestion/storage schema migration, source-validation design, retrieval policy,
provider configuration, models, credentials, dependency/lock changes or personal
store migration. Accepted MEMQ contracts, frozen evidence and historical UAT
observations remain unchanged. Any narrowly changed MEMQ expectation must be
named in the future directive rather than silently regenerating its baseline.

## Required acceptance evidence

| ID | Required proof |
| --- | --- |
| MT-01 | Exact ordered calls on full/skip/standalone modes; a source verified in the first stage contributes to synthesis in the same run. Existing pending non-source/old-meta coverage is retained. |
| MT-02 | The second stage sees only exact newly persisted references; uncertain sources are not reviewed twice. Empty, duplicate, missing, foreign and stale references are tested, including repeated runs and rollback. Both verification stages must expose identical Memory-produced and persisted operation/plan/selection receipts; include empty and migration-only generated selections and substituted evidence refusals. |
| MT-03 | Headless shared consumer imports no Chat code and executes the complete pipeline across full/skip/standalone modes, provider assessments, creation scope, lifecycle and postconditions. Chat makes one pipeline call and only adapts progress/results and the application recovery envelope. |
| MT-04 | Final judge counts are exact across mixed/zero/all-rejected/all-uncertain verdicts. Failed/skipped/deferred counts cannot masquerade as successful zeros. Preview causes no mutation/provider call. |
| MT-05 | Inject failures/cancellation before/after both verification stages, synthesis and persistence. Cancel during a suspended graph/lifecycle write after a preceding write, in both default-headless and injected-boundary paths: drain, no next stage, propagated cancellation and receipt cleanup. Real disposable stores prove outer rollback removes new outputs/restores prior metadata; recovery-required and old-journal handling remain valid. |
| MT-06 | Implicit full equals explicit `--full`; conflicting/duplicate modes follow specified admission. Help is accurate; unrelated parser and command behavior remain unchanged. |
| MT-07 | Complete scoped suites and current Chat/Memory/recovery integration regressions pass; meaningful negative controls reject old order, broad second selection, fake counts and weakened validation through call-phase assertions. Record existing root debt separately. |
| MT-08 | Offline build/install probes exercise normal and optimized Python, canonical installed origins, a disposable real store and deterministic local provider doubles. Record exact artifacts, source, command exits and limits; no personal/live-provider run is implied. |
| MT-09 | Human UAT later confirms stage order, visible counts, one-run source-to-meta progression, skips and understandable failure/recovery output. Record actual observations; no automatic UAT pass or acceptance. |

No tests or proof in this table have been executed for the proposed behavior.
Current source inspection establishes the baseline, not implementation readiness.

## Document review and stop gate

1. Chuck Russell reviews this draft first. Resolve ordering, skip, ownership,
   reporting and compatibility choices in the document.
2. Prepare the bounded construction directive with exact signatures/files,
   journal migration strategy, safe commands and baseline pins. Present it for
   maintainer review before invoking any council sub-agent.
3. Only upon explicit direction to invoke review, use the current **GPT-6 Astra
   and GPT-6.1 Sol only** roster, with fresh read-only contexts. Do not launch
   reviews merely because documents have been written or locally checked.
4. Product construction requires explicit approval of its exact scope/directive;
   a review result does not supply that approval. Independent implementation
   verification and human acceptance remain separate later gates.

The maintainer explicitly requested revision and a fresh OpenAI-only council on
the revised documents. That authorizes this design/directive review only. No
product construction or acceptance follows from the request or a review verdict.
