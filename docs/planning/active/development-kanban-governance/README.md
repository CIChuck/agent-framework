# Development Kanban Governance

---
title: Development Kanban Governance
initiative: development-kanban-governance
document_type: initiative-index
status: started; REM-003 validation pending
work_state: started
condition: normal
created: 2026-09-03
updated: 2026-09-04
branch: feature/development-kanban-governance
next_gate: freeze the REM-003 candidate and dispatch VAL-004
implementation_authority: granted
execution_phase: validation
validation_state: pending
construction_directive: exempt
---

## Objective

Create one repository-visible development board that a maintainer can review and
an agent can execute from without treating directory placement, stale plan text,
or an agent skill as hidden authority.

## Authority

The repository maintainer approved the proposed board model and authorized work
to proceed after the documentation information-architecture refactor merged.

- [Build plan](build-plan.md)
- [Tactical plan](tactical-plan.md)
- [Execution log](execution-log.md)
- [Development task lifecycle policy](../../../reference/policies/development-task-lifecycle.md)
- [Independent validation policy](../../../reference/policies/independent-validation-policy.md)
- [Canonical board](../../board.yaml)

## Lightweight-Change Exemption

The repository maintainer authorized this amendment on 2026-09-03 as a
documentation and process update only. It may change `AGENTS.md`, planning and
reference documents, repository-local dev-skill guidance, and board process
metadata, but it may not change package source, tests, runtime behavior, or
automation scripts. Documentation validation, board validation, protected-guide
comparison, changed-file scope inspection, and an independent cold review are
required.

The board automation on this branch predates adoption of the mandatory
construction-directive gate. Its build plan, tactical plan, and execution log
remain the recorded implementation authority under the policy's adoption
exception. The complete branch must receive an aggregate independent review
before maintainer acceptance.

## Boundaries

- Preserve the lifecycle-oriented documentation structure.
- Do not change Friday package runtime behavior.
- Do not modify `docs/guides/`.
- Keep maintainer approval and acceptance as explicit human-controlled gates.
- Track delivery separately from work state.
- Require construction directives for future code-generating work while keeping
  this documentation-only amendment under the recorded exemption.
- Keep final acceptance human-controlled even when a validation subagent returns
  `VERIFIED`.

## Completion

The original canonical board, rendered dashboard, transition controls,
integration checks, and repository-local board skill are implemented. The
maintainer reopened the packet before acceptance to add the independent
validation policy and post-generation workflow. This amendment remains in
progress until the frozen documentation candidate receives an independent cold
review.

`VAL-001` returned `BLOCKED` because stable plan IDs were absent and the
aggregate diff check found one documentation whitespace defect. `REM-001` is
limited to those findings and is complete. The initiative remains `started`
while the corrected candidate awaits a fresh aggregate review.

`VAL-002` resolved both prior findings and passed every required command, but
returned `CHANGES_REQUESTED` for a delivery-history defect in previously
generated board automation. The current documentation-only authority forbids
the required source and test changes. At that review gate, `REM-002` was proposed
but not authorized and the packet was blocked pending a maintainer decision.

The maintainer approved REM-002 on 2026-09-03. Implementation authority is
limited to the two files and validation artifacts named by that directive.
The bounded change and focused regression coverage are implemented; the work
remains `started` pending a fresh aggregate review.

`VAL-003` confirmed the behavioral fix and all deterministic gates but found the
required backward-delivery negative regression absent. Because VAL-003 follows
the second remediation cycle, proposed REM-003 is not authorized and the packet
was blocked for maintainer disposition.

On 2026-09-04, the maintainer explicitly authorized REM-003 as an exception to
the two-cycle limit. Authority is limited to the focused test, the inaccurate
implementation-report statement, and validation closeout artifacts.
The test and report correction are implemented; the work remains `started`
pending a fresh aggregate review.
