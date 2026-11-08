# Shared command refactor — tactical plan

Branch: `feature/command-retirement`
Status: DIAG D1 test-only correction cycle1 frozen for fresh council round2
Execution phase: validation
Validation state: in_review (DIAG-001 D1 cycle1/round2); D2/D3 and acceptance pending

## Current DIAG-001 checkpoint

[Remediation](remediation/REM-CMD-DIAG-D1-001-test-coverage.md) addresses the two
mandatory gaps from the [round-one council](validation/diagnostics/implementation/d1/council-round1.json).
All200 DIAG cases now execute under the seven exact named gates, with a
[coverage map](validation/diagnostics/implementation/d1/test-coverage-map.json),
all38 binding identities and explicit standalone source-origin checks.

[Correction evidence](validation/diagnostics/implementation/d1/test-coverage-fix-evidence.json):
full478 and named200 pass; all five prior named-node survivors are now refused,
all14 original mutants are refused again. Candidate-export offline lock,
focused static/preservation checks pass. Only the new DIAG test changes outside
docs against the reviewed base; 24 retained helper assertion bodies are AST-equal.
Test source is `e2f514a66407bf5da9868e586ca6cdf30bdadefb`; runtime/models remain equal to `7cab1f0f`.

Next: fresh Sol/Astra/Claude delta plus full bounded D1 round2 and controller
reconciliation before D2. Findings are implemented pending independent closure.
D2 Chat wiring, D3 candidate installed proof, UAT and acceptance remain pending.
Existing acceptances and failed/unwaived root debt remain retained; initiative
stays started/local, without later-family/TUI/full-refactor or delivery approval.

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
