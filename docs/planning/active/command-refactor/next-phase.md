# Command refactor — next-phase checkpoint

Date: 2026-11-06
Branch: `feature/command-refactor`
Status: CMD-FND-001 implemented; frozen-candidate independent review pending
Execution phase: validation
Validation state: in_review

This is the main next-step document. The [packet index](README.md) maps supporting
files; the [board](../../board.yaml) owns initiative state. Work remains started
and local. The current authorized unit is CMD-FND-001 only.

The [foundation unit report](validation/CMD-FND-001-report.md) records completed
builder tests, static checks, controlled lock and isolated artifact proof.
The next action is fresh independent implementation validation, not a later
migration or a new construction unit. Builder evidence is not acceptance.

## Recorded approvals

- CMD-DESIGN-001: API-01–API-06 and neutral foundation types/registry semantics.
- RD-01: Chuck Russell approved the foundation-first sequencing amendment.
- CD-CMD-FND-001: Chuck Russell approved the exact directive and proposed reviewed
  source base `d003c4db31cc9b1e3d143fd8c0d8b930db50ab30`.
- [Approval record](approval/foundation-readiness.md) and [authority](authority.json)
  bind the exact directive/API hashes and accepted readiness evidence. Their
  human decisions supersede old draft/unapproved labels in frozen review inputs.

The approved API hash remains
`e5ba883fb246967320243e1dbc9c2a70fcf6189c05540a45961388f2b6466b74`.
Approval/evidence-only preparation descendants must preserve all product bytes
and exact directive/API from the approved source base before construction.
Record their actual starting HEAD and equality check in the unit receipt.

## Current execution order

1. Confirm board/branch, approved input hashes and protected dirty-file hashes.
2. Implement only [CD-CMD-FND-001](directives/CD-CMD-FND-001-neutral-foundation.md):
   stdlib models, registry/parsing and injected-handler dispatch; no defaults.
3. Add the required minimal cohort/root/artifact integration and meaningful
   constructor, registry, parsing, one-execution and import-boundary tests.
4. Run the directive's controlled lock, focused/static/regression, artifact
   rejection and isolated wheel checks. Disclose known broad-check baselines.
5. Commit a frozen foundation candidate and obtain fresh independent read-only
   implementation validation. Stop for findings or maintainer acceptance;
   do not automatically migrate commands or execute later units.

## Reading order for this unit

1. [Exact approved directive](directives/CD-CMD-FND-001-neutral-foundation.md).
2. [Pinned foundation API](shared-command-api.md), API-01–API-06 only.
3. [Human approvals](approval/foundation-readiness.md).
4. [Test strategy](test-strategy.md) and [execution log](execution-log.md) for
   evidence classes, baseline constraints and actual progress.

The [phase plan](phase-plan.md), [tactical plan](tactical-plan.md),
[scope decisions](scope-decisions.md) and proposed case/unit map remain broader
references; they cannot widen this unit's approved paths or behavior.

## Resolved packaging issues and remaining gates

Legacy framework CLI launcher retirement is [VERIFIED](validation/legacy-cli-removal/report.md)
at `06285ae4`. Required tools-to-finance dependency is
[VERIFIED](validation/required-finance/report.md) at `d003c4db`: default installation
imports tools/finance/SDK, preserves 50/3 and Chat help, and installs no retired
launcher. RD-02 records these resolutions, not a deferred defect waiver.

RD-01 permits only the isolated foundation before full family/P1 closure. All
foundation tests, neutral-import/wheel proof and fresh review remain mandatory.
Detailed family contracts, per-case behavioral signoff, service ownership,
progress/cancellation, supported client/platform scenarios, nine retirements,
client/TUI wiring, aggregate implementation review and feature acceptance
remain required before their affected later units. They are not approved here.
No push, PR, merge, release or deployment is authorized.
