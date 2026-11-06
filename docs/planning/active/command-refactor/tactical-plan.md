# Shared command refactor — tactical plan

Date: 2026-11-06
Branch: `feature/command-refactor`
Status: Foundation design approved; PAUSED before approval-sequence Step 3
Execution phase: planning
Validation state: not_ready

The [next-phase checkpoint](next-phase.md) is the main handoff and reading order.
Chuck Russell approved [CMD-DESIGN-001](approval/foundation-design.md) and paused
before resolving prerequisites for the first implementation unit. The table
below records existing partial outputs and future work; it is not permission
to resume that work. Step 3 in the approval sequence is distinct from phase P3.

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

## P0/P1 output checklist — paused

| Work area | Already exists | Open after resumption |
| --- | --- | --- |
| Source characterization | [PAR ledger](validation/par-coverage-ledger.md), source inventory and 50-name/three-alias matrix. | Per-case behavior assertions, transitive service/effect and failure-order mapping, exact fixtures and unresolved-case dispositions. Extend the ledger rather than creating a replacement. |
| Chat and CLI baselines | [Initial baseline](validation/p0-baseline.md), [failure controls](validation/p0-failure-disposition.md), and [local refresh](validation/local-2026-11-06/README.md). | Applicable installed entry-point/wheel and supported-environment proof, case-level evidence and limitation dispositions. Preserve existing receipts; write future results separately. |
| Product decisions | O-01–O-05 resolved in the decision register. | Apply the retained/retired policy to case ownership, guides/help and the retirement unit. Enhancements stay in the backlog. |
| Technical contract | Architecture proposal, API draft and approved foundation-only design. | Applicable current-design review evidence, family payload/capability schemas, service-owner mapping, compatible CLI reuse assessment, progress/cancellation and full-contract approval. |
| Unit readiness | Draft CD-CMD-FND-001 and required phase/test criteria. | Complete unit/scenario/environment maps and retirement ordering; bind the first unit to exact input revisions and baseline evidence; obtain explicit disposition for any foundation-only deferral. |

No new baseline, source inspection, contract drafting, scenario mapping or
readiness work was performed by the approval-recording continuation. P0/P1
remain incomplete. The broad board authority does not approve CD-CMD-FND-001.

## Construction and later phases

After explicit resumption, Step 3 produces a concise readiness summary for the
maintainer, linked to exact evidence and unresolved decisions. The maintainer
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
