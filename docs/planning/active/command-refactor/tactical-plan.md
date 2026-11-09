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
