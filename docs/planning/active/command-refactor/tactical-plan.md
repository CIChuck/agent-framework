# MAINT-001 — shared Memory pipeline revision in review

Execution phase: validation (documents only)
Validation state: in_review (revised specification and construction directive)

The revised [specification](maintenance-reorganization-specification.md) and
[directive](directives/CD-CMD-MAINT-001-reorganization-order.md) assign the complete
memory pipeline to friday-memory: stage policy/selection, provider assessments,
execution, lifecycle and postconditions. Chat invokes it once inside the existing
cross-store recovery envelope and adapts progress/results. Headless tests must
exercise the entire sequence without Chat imports.

[Version2 preparation](validation/maintenance/construction-preparation-v2.json)
binds the revised authority and unchanged product baseline. The earlier
specification council does not cover these revised bytes. Chuck Russell explicitly
requested fresh OpenAI-only review after the ownership revisions.

**Next gate:** Reconcile fresh OpenAI-only round2 review of the revised MAINT-001 specification and directive with Memory-owned pipeline execution. No product implementation approval; stop for human decision after review.

No product code or tests changed. Accepted MEMQ/UAT remain closed.

## Historical directive draft checkpoint — superseded for current readiness

# MAINT-001 — construction directive for human review

Branch: `feature/command-retirement`
Execution phase: planning (directive drafting only)
Validation state: not_ready (directive); specification readiness verified

[Proposed construction directive](directives/CD-CMD-MAINT-001-reorganization-order.md)
SHA256 `906e7ee6c717612247b2619c4c49bd1e9f0280aa6b940835956105736030d932` implements the reviewed specification and resolves its
three advisory groups. [Preparation pins](validation/maintenance/construction-preparation.json)
SHA256 `e06675197bb46b5ccdb1324dd12ba567ebee4366cdd7035031fee0d68a686e96` bind baseline source and authority.

Concrete choices include operation-scoped shared creation receipts, exact created
verification selection, final-judge counts, configuration-only verification
preflight, provider-free preview, and separate immutable run evidence while
retaining recovery journal/bundle version1. The file allowlist, test nodes,
commands, fixture relocation rules and later validation gates are explicit.

**Next gate:** Chuck Russell reviews proposed CD-CMD-MAINT-001 construction directive and preparation pins. No product implementation or council/sub-agent invocation until explicit direction after document review.

No product changes, fixture generation, runtime tests or agents were started.
Accepted MEMQ and its UAT remain closed. The earlier council verified the
specification, not this new directive or its concrete choices.

## Historical specification reconciliation checkpoint

# MAINT-001 — specification council VERIFIED; directive preparation next

Branch: `feature/command-retirement`
Execution phase: planning (documents only)
Validation state: verified (specification readiness only)

[Round1 reconciliation](validation/maintenance/specification/round1/report.md):
Sol9.0 and Astra9.2 independently VERIFIED candidate `2d0957f4`; all MS-01..08
pass and no mandatory findings remain. The reviewed specification is unchanged.
Three merged advisories become directive/test-planning inputs: preflight and
empty-stage semantics; migration-only synthesis; actual legacy recovery fixtures.
No proposed runtime evidence has been executed for this unit.

**Next gate:** Prepare the exact MAINT-001 construction directive for Chuck Russell to review, carrying the reconciled specification advisories. No implementation or further council/sub-agent invocation without explicit direction.

Accepted MEMQ remains closed. This council does not grant construction or
acceptance authority. No agents remain working on this review.

## Historical pre-council human-review checkpoint

# MAINT-001 — maintenance specification for human review

Branch: `feature/command-retirement`
Execution phase: planning (documents only)
Validation state: not_ready (draft; no council invoked)

The [maintenance reorganization specification](maintenance-reorganization-specification.md)
proposes verification of pending memories before synthesis, targeted verification
of this run's new meta insights afterward, per-stage verdict counts, and the
companion explicit `--full` correction. Accepted MEMQ and its UAT stay closed.

Chuck Russell directed continued drafting and requested document review before
council sub-agents are invoked. The primary agent prepares the draft directly;
no sub-agents or implementation are authorized by this preparation checkpoint.

**Next gate:** Chuck Russell reviews the MAINT-001 maintenance reorganization specification before any council or sub-agent invocation. Drafting only; no implementation approval. Accepted MEMQ remains closed; initiative stays started/local.

## Preserved accepted MEMQ checkpoint

# MEMQ-001 — accepted; UAT closed

Branch: `feature/command-retirement`
Execution phase: closeout
Validation state: verified; acceptance: accepted by Chuck Russell,2026-11-10

Both [MEMQ UAT](uat/memq-user-acceptance-plan.md) and the
[combined retest](uat/memq-repair-retest.md) are successful and closed per the
maintainer. [Acceptance](approval/memory-queries-acceptance.md) records source,
review evidence and limits. Full reorganization on exit produces positive `/meta`
results, maintainer-reported. No additional provider/store execution was performed.

The separate command-syntax defect FU-011 rejects `/reorganize --full --execute`;
source inspection and isolated pure-parser evidence confirm full is the default
and `/reorganize --execute` selects it. The `/meta` guidance recommends an
unsupported explicit flag. [Open defect](../../backlog/friday-chat-framework-followups/upgrade-log.md#fu-011-reorganize-rejects-the-explicit-full-mode-flag).
The [verification flow note](validation/memory-queries/acceptance/verification-flow.md)
explains the three model roles, structural checks, ordering and failure signals.

**Next gate:** MEMQ and both UAT records are accepted/closed. FU-011 explicit --full argument defect is recorded separately; await maintainer priority and bounded scope for further work. Initiative remains started/local.

The parent initiative stays started/local. No subsequent code, TUI, delivery or
whole-refactor acceptance is inferred. Known baseline debt remains unwaived.

# Historical pre-acceptance MEMQ checkpoint — superseded by acceptance above

# MEMQ-001 — shared entity/ingestion UAT repairs

Branch: `feature/command-retirement`
Execution phase: closeout
Validation state: verified (shared quote/ingest repair; combined human retest pending); prior D3 verified at bab16757

Chat source `3ed1d58ad8cc1e79522495da5cf19091185402d8` implements the six delegated queries and approved
option R persisted listing. [Builder evidence](validation/memory-queries/implementation/d2/README.md)
records Chat1390, Commands/cohort599, CLI155, fast lanes616/117, all52 new
MQ-T07..14 cases,20 assertion-witnessed mutants and exact current observations.
The [round1 council](validation/memory-queries/implementation/d2/council-round1/report.md) reproduced those runtime checks. Sol9.6 and Claude9.4 VERIFIED; Astra9.3 CHANGES_REQUESTED for stale authority prose. [Round2](validation/memory-queries/implementation/d2/council-round2/report.md) resolves ASTRA-001 but identifies a frozen backlog scope breach. The exact approved bytes are restored and [round3](validation/memory-queries/implementation/d2/verified-report.md) is unanimously VERIFIED9.5, no mandatory findings. [D3](validation/memory-queries/implementation/d3/README.md) has completed builder builds/replay, actual installed proof and controls at sourcee4c0b9a2; [final council](validation/memory-queries/implementation/d3/verified-report.md) is unanimously VERIFIED (Sol9.5/Astra9.4/Claude9.5), with no mandatory findings. Original reports remain scoped to their candidates.

**Next gate:** Maintainer combined retest of entity quoting, ingestion without descriptions and verification diagnostics using uat/memq-repair-retest.md. Capture any verification role/model/finish/field error; remaining dependent UAT and acceptance stay pending.

The original MEMQ contract/directive/approval remain byte-exact historical
technical inputs. Current shared Commands and ingestion changes are authorized by
[REM-CMD-MEMQ-UAT-003](remediation/REM-CMD-MEMQ-UAT-003-shared-quote-ingest.md)
and its [approval](approval/memory-queries-shared-uat-repair.md). Prior verification
diagnostics are separately governed by REM-CMD-MEMQ-UAT-002 and remain verified.
The shared quote/ingestion repair at47134ad6 has passed runtime, real-store and
installed checks; its current-status documentation correction is independently verified.
Human UAT is stopped after reported failures; the original
[plan](uat/memq-user-acceptance-plan.md) is preserved and the
[combined retest](uat/memq-repair-retest.md) covers all3 issues. Ingestion without
a description is repaired in code; human confirmation remains pending. The actual
verification-response failure is unresolved. Root/format and dirty-example debt
remain failed/unwaived. Historical checkpoints below describe their own freezes.

# Historical D1 reconciliation checkpoint — superseded for current execution state

Branch: `feature/command-retirement`
Execution phase: implementation
Validation state: not_ready (D2); D1 verified at 9ce71581

Guarded D0 reproduction and bounded neutral D1 are complete in source commit
`0f809207984143f88fbe971b761035d6ea7b11d0`. The [D1 reconciliation](validation/memory-queries/implementation/d1/verified-report.md)
records Sol9.7, Astra9.6 and Claude9.6 VERIFIED, with no mandatory findings.
The builder record and evidence bind the source, tests and preservation checks. Commands/cohort
599, Chat 1,338 and CLI 155 pass; all 101 new neutral cases are included. The
unchanged control passes and 14 mutants are rejected by test-call assertions.

**Next gate:** Implement bounded MEMQ D2 Chat integration and approved option R persisted listing under the existing exact approval; freeze and obtain fresh D2 Sol/Astra/Claude council before D3. D1 VERIFIED at 9ce71581; UAT NOT RUN; no acceptance or delivery.

The [MEMQ UAT plan](uat/memq-user-acceptance-plan.md) sits alongside the earlier
roadmap. Every case remains NOT RUN pending D2/D3 and installed readiness.
The exact contract/directive and option R technical approval are unchanged.
D2 Chat integration, D3 installed proof and maintainer acceptance remain future
gates. Root/format baseline debt is failed and unwaived; the initiative remains
started/local. Preserved historical checkpoints below describe their own freezes.

# Historical directive-readiness closeout — superseded for current execution state

Branch: `feature/command-retirement`
Execution phase: planning (existing approved D0/D1 sequence is next)
Validation state: verified for directive/design readiness only

[Round4 reconciliation](validation/memory-queries/directive-review/round4/report.md)
records three fresh VERIFIED results at `be15dca1b37364748e1fcf9ef5d062a920a8d250`:
Sol9.6, Astra9.5, Claude9.6. CR01..08 and MR01..10 pass; no mandatory findings.
The [additional authorization](approval/memory-queries-directive-additional-pass.md)
was explicit after the earlier escalation. The old Sol BLOCKED receipt and
external locator remain preserved; no past violation was waived. Fresh current
seats independently satisfied isolation.

**Next gate:** Reproduce MEMQ D0 baseline and preservation under the existing option R technical approval, then bounded neutral D1 with fresh D1 council before D2. Directive/design readiness VERIFIED at be15dca1; product implementation unstarted; no acceptance or delivery.

The existing [option R technical approval](approval/memory-queries-directive-correction2.md)
continues to bind exact contract/directive bytes. This review clears design
readiness only; it creates no new product authority and proves no implementation.
D0 baseline reproduction and bounded neutral D1 are unstarted, with D1 council
before D2 and later D2/D3/installed/acceptance gates still required. No user
approval is inferred from scores or the controller's recording.

The contract, directive, verifier, format profile and original evidence retain
the reviewed hashes. This closeout changes status/history and preserves review
evidence only; the reviewed candidate is be15dca1, not an invented new verdict
for administrative descendants. Current README semantics have been assessed by
all three seats; the regex helper remains only a syntactic control.

The umbrella remains started/local; baseline root/format debt stays
failed/unwaived. Product files, dirty examples, ignored exports and the known
external locator are preserved. No product implementation, UAT, acceptance,
next-family or external delivery was performed by this readiness workflow.

### Preserved DIAG acceptance checkpoint

## DIAG-001 — accepted; next-unit preparation checkpoint

Branch: `feature/command-retirement`
Execution phase: planning (next unit); DIAG-001 closeout complete
Validation state: verified (accepted DIAG-001); broader initiative remains started/local

Chuck Russell reported successful manual UAT and [accepted DIAG-001](approval/diagnostics-acceptance.md)
(“the uat was successful - all approved, proceed to next steps”) after Sol/Astra/Claude independently VERIFIED candidate
`be72a1e8` at 9.7 each with no mandatory findings. Product/test/probe and
artifact source `28c544fa` is unchanged. The [UAT register](uat/friday-chat-user-acceptance-roadmap.md)
records maintainer-reported results without inferred per-case detail.

**Next gate:** Prepare proposed MEMQ-001 contract and directive (planning only) after accepted DIAG-001; construction requires their exact approval. No delivery follows automatically.

The [proposed unit order](validation/step3/unit-map.json) places MEMQ-001
(`/memory`, `/insights`, `/summaries`, `/meta`, `/entities`, `/list-ingested`)
after DIAG-001. Preparation may add proposed documents, current status and
guarded characterization only; no product/test/config/dependency/lock change.
PILOT, SESSION and DIAG are accepted internal units. Remaining families, P0/P1,
TUI and full-refactor acceptance stay open; delivery stays local. Root Ruff 534,
the test_display collection conflict and registry format remain failed/unwaived.
Both dirty example files and ignored exports stay untouched.

### Preserved DIAG verified-completion checkpoint

## DIAG-001 — verified completion and human acceptance checkpoint

Branch: `feature/command-retirement`
Execution phase: closeout
Validation state: verified (bounded DIAG D1–D3 and complete aggregate)

[Final verification](validation/diagnostics/implementation/d3/verified-report.md)
reconciles all three fresh round-3 results: VERIFIED9.7 each, no mandatory findings.
Reviewed candidate `be72a1e8b5904436ec3b9eb844a5db4f71ed95c9`; corrected source/probe/artifacts `28c544fa67e934f03c212aed39ba20802b500b13`.
The runtime order finding and both documentation findings are independently
closed. Current1,991-suite/build/install receipts retain exact provenance; all
review inputs and protected local state were rechecked before closeout metadata.

**Next gate:** Chuck Russell's bounded DIAG-001 acceptance decision; manual UAT remains unrun. No next unit or delivery follows automatically.

Read the [acceptance handoff](validation/diagnostics/implementation/d3/acceptance-handoff.md)
and [17-case UAT roadmap](uat/friday-chat-user-acceptance-roadmap.md). The latter
remains NOT RUN; the handoff contains the exact installed launch command and
records fake versus real runtime limits. No acceptance is inferred from reviews
or previous amendment approval. Stop for the bounded maintainer decision.

The command-refactor umbrella remains started/local, with its active packet.
Later families, P0/P1, full-refactor/TUI and all delivery need separate authority.
Root Ruff534, the6,929-test collection conflict and registry format remain failed/
unwaived. Keep both dirty example files and ignored exports untouched. No new
product/test/probe/approved contract/build change or review loop is introduced by
this closeout record.

### Preserved round-3 validation checkpoint

# DIAG-001 — documentation correction validation checkpoint

Branch: `feature/command-retirement`
Execution phase: validation
Validation state: in_review (documentation cycle 2 / council round 3)

[Round-2 reconciliation](validation/diagnostics/implementation/d3/council-round2-reconciliation.md):
all three independently closed DIAG-D3-ASTRA-001. Sol 9.6 and Claude 9.4 requested
only current-status corrections; Astra returned VERIFIED 9.6. The amendment is
approved and the runtime correction is complete. Current product/test/probe
source remains `28c544fa67e934f03c212aed39ba20802b500b13`.

[REM-CMD-DIAG-D3-002](remediation/REM-CMD-DIAG-D3-002-status-reconciliation.md)
corrects the README next gate and PAR header/six DIAG cells, with associated
lifecycle/evidence updates only. No product/test/probe/configuration/lock or
approved authority bytes change. Existing actual 1,991-suite/build/install
receipts must be hash-verified against unchanged runtime; new runtime execution
is not required solely for prose. Every current aggregate criterion still needs
independent evidence and a fresh conformance decision.

Next: reconcile fresh Sol/Astra/Claude docs-delta then complete bounded aggregate
review, and only then propose bounded human DIAG acceptance. UAT remains unrun;
root Ruff 534, test_display collection conflict and registry format remain
failed/unwaived. Dirty examples and ignored exports stay preserved. Later
families, P0/P1, full-refactor/TUI and delivery remain separate gates.

### Preserved correction-cycle1 checkpoint

# DIAG-001 — D3 context evaluation correction validation checkpoint

Branch: `feature/command-retirement`
Execution phase: validation
Validation state: in_review (D3 correction cycle1; fresh council pending)

Chuck Russell approved [REM-CMD-DIAG-D3-001](remediation/REM-CMD-DIAG-D3-001-context-evaluation-order.md)
(SHA-256 `3078bb19…a865`) in the [exact approval record](approval/diagnostics-context-evaluation.md).
Corrected product/test/probe source is `28c544fa67e934f03c212aed39ba20802b500b13`:
one typed `context_debug_snapshot()` capability is used only for exact `--debug`;
Chat formats the selected text once, then measures the original value, and shared
code never re-measures. [Correction evidence](validation/diagnostics/implementation/d3/correction-evidence.json)
binds 12/12 legacy-equal characterization rows (9 diverged before the fix), the
unfixed-candidate call-assertion failures, nine rejected mutants with an
unchanged 539 control, 1,991 source tests (1,971 + 20 new DG-T04 cases), DIAG
68+4/SESSION 25/pilot 196 captures, two identical 154-artifact closed builds,
eight installed probes, 50+4+10 refusals, 2 source refusals, 8 restored copies
and round-1 artifacts rejected by the new installed assertions.

Next: fresh Sol/Astra/Claude remediation-delta review, then complete bounded
D3/DIAG aggregate review. The Claude seat must be a fresh context: the session
that implemented this correction also served as the Claude D2 round-2 reviewer.
Reconcile all mandatory findings before human DIAG acceptance. Root Ruff 534,
test_display collection conflict and registry format remain failed/unwaived.
UAT, acceptance, later families, P0/P1, full-refactor/TUI and delivery remain
pending or separately governed. Dirty examples and ignored exports are preserved.

### Preserved round-1 decision checkpoint (superseded by the approval above)

Branch: `feature/command-retirement`
Execution phase: remediation
Validation state: changes_requested (D3 and complete bounded aggregate, round 1)

[Council reconciliation](validation/diagnostics/implementation/d3/council-round1-reconciliation.md)
records Sol/Claude VERIFIED 9.7 and Astra CHANGES_REQUESTED 8.7. The reproduced
mandatory finding DIAG-D3-ASTRA-001 prevents aggregate verification. Stateful
accepted strings expose changed count, exception and export behavior.

Read the [proposed amendment](remediation/REM-CMD-DIAG-D3-001-context-evaluation-order.md).
It adds one typed host debug snapshot capability to preserve legacy format-then-
length evaluation while shared code retains flags/export ownership. It changes
an exact approved port/algorithm, so maintainer approval of these exact proposed
bytes is required. No implementation under the proposal is started.

Prior product/probe/build inputs and evidence remain unchanged. After approval,
a bounded remediator must correct only this finding, refresh tests and actual
installed normal/optimized proof, rebuild/replay corrected committed source and
obtain fresh Sol/Astra/Claude delta then complete bounded aggregate review.
Preserve dirty examples and ignored exports; no cleanup. Root Ruff 534,
test_display collection conflict and registry format remain failed/unwaived.
UAT, human acceptance, later families, P0/P1, full-refactor/TUI and delivery remain
pending or separately governed. No further council is launched pending decision.

### Preserved prior planning checkpoint

The following describes the preapproval preparation and is superseded by the
exact subsequent approval above.

# Shared command refactor — tactical plan

Date: 2026-11-08
Branch: `feature/command-retirement`
Status: DIAG-001 contract/directive prepared; exact approval pending
Execution phase: planning
Validation state: not_ready (DIAG-001; accepted SESSION-001 retained)

## Current DIAG-001 preparation checkpoint

The maintainer authorized preparation after the next-step proposal. The
[contract](diagnostics-command-contract.md) and
[directive](directives/CD-CMD-DIAG-001-context-diagnostics.md) define only six
diagnostics, shared typed outcomes, host projection/rendering/file ownership,
compatibility decisions, exact paths and D1–D3 gates. Approval of both exact
bytes precedes any implementation. [Preparation](validation/diagnostics/preparation.json)
contains 72 repeatable source cases, six metadata records and guarded controls;
244 related Chat and 278 Commands/cohort cases pass. Product bytes stay unchanged.

After approval: reproduce D0 inputs/inventories, implement D1 neutral handlers
and models, reconcile Sol/Astra/Claude council; then D2 Chat adapters and its
council; then D3 full regression/build/installed proof and complete bounded
aggregate council. Stop for human DIAG acceptance. No step is credited early.

SESSION-001 remains [accepted](approval/session-acceptance.md), following its
[independent aggregate verification](validation/session/implementation/d3/verified-report.md).
The [next-phase checkpoint](next-phase.md), board and authority own current
state. Later families, P0/P1, TUI and external delivery remain separate.


## Historical Step 3 planning checkpoint

The following original date, branch, pending labels and checklist describe
their earlier Step 3 state and are superseded for current execution by the
board, exact subsequent approvals and checkpoint above.

Date: 2026-11-06
Branch: `feature/command-refactor`
Status: Authorized Step 3 corrections; fresh validation pending; Step 4 not approved
Execution phase: planning
Validation state: in_review

The [next-phase checkpoint](next-phase.md) is the main handoff and reading order.
Chuck Russell approved [CMD-DESIGN-001](approval/foundation-design.md) and paused
before prerequisite work, then explicitly resumed Step 3 on 2026-11-06 and
requested the three-provider council. Its CHANGES_REQUESTED result led to
maintainer-authorized [bounded corrections](remediation/REM-CMD-STEP3-001.md).
[readiness-review.md](readiness-review.md) is the corrected assessment, awaiting
fresh independent validation. Step 3 is distinct from phase P3; no product
construction or prerequisite exception is approved.

## Governing documents

The [board](../../board.yaml) controls task state. The [build plan](build-plan.md)
sets initiative scope; [scope decisions](scope-decisions.md) record O-01–O-05.
The [phase plan](phase-plan.md) sets exits, the
[architecture](shared-command-architecture.md) defines candidate boundaries,
the [API](shared-command-api.md) contains the approved limited foundation input
and deferred contract material, and the [test strategy](test-strategy.md) sets
evidence classes.

The original [intent](command_refactor.md), [inventory](command-inventory.md)
and [matrix](command-matrix.md) remain product-intent inputs. The recorded
decisions control nine removals, tools retention, 41 names/three aliases, neutral
command ownership, separate CLI preservation and retained-command quirks.

## P0/P1 output checklist — readiness assessment

| Work area | Already exists | Outstanding beyond the proposed foundation-only amendment |
| --- | --- | --- |
| Source characterization | [PAR ledger](validation/par-coverage-ledger.md), source inventory and 50-name/three-alias matrix. | Per-case behavior assertions, transitive service/effect and failure-order mapping, exact fixtures and unresolved-case dispositions. Extend the ledger rather than creating a replacement. |
| Chat and CLI baselines | [Initial baseline](validation/p0-baseline.md), [failure controls](validation/p0-failure-disposition.md), and [local refresh](validation/local-2026-11-06/README.md). | Applicable installed entry-point/wheel and supported-environment proof, case-level evidence and limitation dispositions. Preserve existing receipts; write future results separately. |
| Product decisions | O-01–O-05 resolved in the decision register. | Apply the retained/retired policy to case ownership, guides/help and the retirement unit. Enhancements stay in the backlog. |
| Technical contract | Architecture proposal, API draft and approved foundation-only design. | Applicable current-design review evidence, family payload/capability schemas, service-owner mapping, compatible CLI reuse assessment, progress/cancellation and full-contract approval. |
| Unit readiness | Draft CD-CMD-FND-001 and required phase/test criteria. | Complete unit/scenario/environment maps and retirement ordering; bind the first unit to exact input revisions and baseline evidence; obtain explicit disposition for any foundation-only deferral. |

The earlier approval-recording continuation performed no engineering. The later
Step 3 continuation has added isolated wheel profiles, a source-backed CLI reuse
assessment and a proposed complete unit/scenario/environment map. Per-case
behavioral signoff and full family/P1 obligations remain open. Readiness RD-01
and RD-02 require explicit Step 4 disposition; broad board authority does not
approve CD-CMD-FND-001.

## Construction and later phases

Step 3 has produced a concise readiness summary with evidence and unresolved
decisions. The completed council remains historical for candidate `95fdeadc`.
Corrected evidence and draft scope require fresh validation; the maintainer
then separately approves the construction directive and execution base (Step 4).
No source generation follows from CMD-DESIGN-001 alone.

The [phase plan](phase-plan.md) retains the detailed P2–P5 sequence: foundation,
retained-family migration and nine-name retirement, cross-family/installed
integration, aggregate review and maintainer acceptance. Each source unit needs
its own approved directive, assigned PAR cases, applicable baseline receipts,
allowed files, checks, stop conditions and fresh independent review.

Keep candidate/diff identities, test receipts, deviations and review outcomes
in the [execution log](execution-log.md) and unit evidence. A changed candidate
or authority requires fresh validation. TUI integration and terminal UAT remain
separate later acceptance work.
