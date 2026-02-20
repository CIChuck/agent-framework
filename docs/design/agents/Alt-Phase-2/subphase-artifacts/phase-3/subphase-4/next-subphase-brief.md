# Phase 3 Subphase 4 -> Subphase 5 Brief

## Assumptions Carried Forward

1. Canonical skill reference validation (`skill_id@version`) is now enforced at profile/task boundaries.
2. Registry/orchestrator/workflow engine support additive skill-driven routing/delegation.
3. Federated skill catalog structure is available without changing runtime reference semantics.
4. Existing non-negotiables remain intact (`single_agent` default, strict compatibility boundaries).

## Required Inputs for Subphase 5

1. `docs/design/agents/Alt-Phase-2/phase-3-build-plan.md` Workstream I.
2. `docs/design/agents/Alt-Phase-2/phase-3-transition-plan.md` section 4.5 items for scratch/workflow/HITL mapping.
3. Scratch pad contracts in:
   - `docs/design/agents/Alt-Phase-2/technical-specifications.md`
   - `docs/design/agents/Alt-Phase-2/agent-contract-schema-spec.md`

## Subphase 5 Focus

1. Map workflow task-state transitions to scratch plan-item lifecycle updates.
2. Record HITL pause/resume checkpoints into scratch event logs for replay-grade traceability.
3. Enforce scratch scope isolation, TTL, and quota behavior under orchestration load.
4. Add workflow-history and scratch-event replay correlation coverage.

## Blockers

1. None.
2. Baseline quality debt waivers remain active and must continue to be tracked independently from subphase regressions.
