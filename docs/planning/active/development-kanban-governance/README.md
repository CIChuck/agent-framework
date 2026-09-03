# Development Kanban Governance

---
title: Development Kanban Governance
initiative: development-kanban-governance
document_type: initiative-index
status: started
work_state: started
condition: normal
created: 2026-09-03
updated: 2026-09-03
branch: feature/development-kanban-governance
next_gate: freeze and independently validate the documentation candidate
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
