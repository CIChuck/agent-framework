# Command refactor — next-phase checkpoint

Date: 2026-11-06
Branch: `feature/command-refactor`
Status: CMD-DESIGN-001 approved; PAUSED before Step 3 for maintainer review
Execution phase: planning
Validation state: not_ready

This is the main next-step document. The [packet index](README.md) maps the
supporting files. Current planning lives in Agent Framework; earlier TUI-folder
directions and imported receipts retain their historical provenance.

## Recorded decision and exact pause

Chuck Russell approved [CMD-DESIGN-001](approval/foundation-design.md) on
2026-11-06 and instructed: “pause before, starting step 3 for review.”

Step 3 refers to the approval sequence below: **resolving prerequisites for the
first implementation unit**. It does not mean tactical task 3 or phase P3.
Do not begin or continue that engineering work until the maintainer resumes it.

The foundation approval covers API-01–API-06 and neutral types/registry semantics
in the exact [API document](shared-command-api.md) pinned by the approval record.
It does not approve the whole contract, the construction directive or P0/P1 exit.

## Approval sequence

| Step | Action | Current state |
| --- | --- | --- |
| 1 | Reconcile navigation and freeze the design inputs; obtain required independent design-readiness evidence. | Navigation reconciled and approved API input pinned. No fresh independent verdict for current design bytes is recorded; earlier reports remain historical. |
| 2 | Maintainer decides CMD-DESIGN-001. | APPROVED on 2026-11-06 by direct instruction. This decision does not fabricate independent review evidence. |
| 3 | Resolve applicable P0/P1 prerequisites for the first implementation unit. | PAUSED BEFORE START/CONTINUATION, for maintainer review. Existing partial work predates this pause. |
| 4 | Maintainer approves the exact CD-CMD-FND-001 directive, execution base and readiness disposition. | Draft; not approved. |
| 5 | Execute separately approved units, verify frozen candidates, then obtain feature acceptance. | Future work; product construction unauthorized. |

## Existing work and remaining obligations

This table reconciles existing artifacts; it does not start Step 3 or close gaps.

| Item | Existing record | Remaining after explicit resumption |
| --- | --- | --- |
| Product scope and ownership | [Scope decisions](scope-decisions.md), O-01–O-05: nine complete removals, tools retained, 41 names/three aliases, neutral shared owner, preserved separate CLI and retained quirks. | Apply these decisions to the detailed unit map; do not reopen them implicitly. |
| Source map | [PAR ledger](validation/par-coverage-ledger.md) and frozen 50-name/three-alias matrix exist. | Complete per-case positive/invalid/unavailable/error/effect evidence and owning-unit assignments. A source map is not behavioral signoff. |
| Baseline receipts | [Local continuation](validation/local-2026-11-06/README.md) records matching inventoried hashes, 826 controlled Chat tests and 155 CLI tests. | Close applicable installed-client, environment and case-level evidence gaps. These stored results were not rerun for this approval recording. |
| Foundation contract | [CMD-DESIGN-001](approval/foundation-design.md) approves the limited foundation input. | Resolve applicable independent-review/readiness obligations; family capabilities, service ownership, progress/cancellation and the complete contract remain open. |
| Unit/scenario/environment map | [Phase plan](phase-plan.md) and [tactical plan](tactical-plan.md) describe required outputs. | Complete assignments, dependencies, retirement order and supported scenarios/environments before affected construction. |
| First construction unit | [CD-CMD-FND-001](directives/CD-CMD-FND-001-neutral-foundation.md) exists as a draft. | Pin the execution base, approved API and applicable readiness evidence; obtain separate construction approval. Any foundation-only deferral requires explicit disposition. |

## Reading order at this pause

1. This checkpoint: confirm where the work is paused.
2. [Phase plan](phase-plan.md), P0/P1: review what readiness requires.
3. [Tactical plan](tactical-plan.md): review existing outputs versus remaining work.
4. [Test strategy](test-strategy.md): review the required evidence classes.
5. [Draft foundation directive](directives/CD-CMD-FND-001-neutral-foundation.md),
   especially entry conditions, allowed paths, checks and stop conditions.

These are review inputs before resuming Step 3, not a request to approve
unfinished evidence. No new document, investigation, baseline run, family
contract, exemption or implementation is authorized by this pause checkpoint.

The initiative remains started/planning; completion, acceptance and delivery
are separate decisions. TUI construction remains gated on command-refactor
acceptance and separate authorization.
