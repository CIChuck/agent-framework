# Development Kanban Governance

---
title: Development Kanban Governance
initiative: development-kanban-governance
document_type: initiative-index
status: completed
work_state: completed
condition: normal
created: 2026-09-03
updated: 2026-09-03
branch: feature/development-kanban-governance
next_gate: maintainer review and acceptance
implementation_authority: closed
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
- [Canonical board](../../board.yaml)

## Boundaries

- Preserve the lifecycle-oriented documentation structure.
- Do not change Friday package runtime behavior.
- Do not modify `docs/guides/`.
- Keep maintainer approval and acceptance as explicit human-controlled gates.
- Track delivery separately from work state.

## Completion

The canonical board, rendered dashboard, transition controls, integration checks,
and repository-local skill are implemented and validated. `AGENTS.md` now defines
the canonical operational authority chain for code generation. The work is
awaiting maintainer review and acceptance; it has not been self-accepted.
