# Phase 3 Subphase 5 -> Subphase 6 Brief

## Assumptions Carried Forward

1. Workflow/HITL transitions now map deterministically into scratch plan-item and event-log records.
2. Scratch events include correlation linkage for replay/forensics.
3. Scratch pad integration is additive and default-safe (in-memory baseline path).

## Required Inputs for Subphase 6

1. `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-build-plan.md` Workstream J.
2. `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-transition-plan.md` filesystem-topology requirements.
3. Runtime path contracts in `packages/friday-runtime/src/friday_runtime/config.py`.

## Subphase 6 Focus

1. Enforce runtime path-governance across install/runtime/workspace roots in orchestration paths.
2. Validate deployment-profile conformance (local/container/cloud) for runtime and scratch placement.
3. Add path-overlap rejection/remediation behavior and supporting verification coverage.

## Blockers

1. None.
2. Baseline quality debt waivers remain active and must continue to be tracked independently from subphase regressions.
