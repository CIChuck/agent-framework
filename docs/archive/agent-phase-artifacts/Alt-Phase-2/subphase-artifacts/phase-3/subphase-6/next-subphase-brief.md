# Phase 3 Subphase 6 -> Subphase 7 Brief

## Assumptions Carried Forward

1. Runtime topology and path-governance helpers are now available for artifact/state path enforcement.
2. Deployment profile defaults are defined for local/container/cloud and can be overridden by environment configuration.
3. Existing baseline debt (full-repo lint + full-gate mypy command path) remains unchanged.

## Required Inputs for Subphase 7

1. `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-build-plan.md` Workstream K.
2. `docs/archive/agent-phase-artifacts/Alt-Phase-2/technical-specifications.md` section 4.11 and section 5.10.
3. Existing workflow runtime and orchestration contracts in `packages/friday-agent/src/friday_agent/workflows`.

## Subphase 7 Focus

1. Implement hierarchical workflow->pipeline->task schema models.
2. Implement assignment claim/lease/recovery semantics.
3. Implement typed cross-pipeline handoff validation and lineage recording.
4. Add deterministic dispatch behavior tests and hierarchy integrity coverage.

## Blockers

1. None.
2. Baseline quality debt waivers remain active and continue to be tracked independently from subphase regressions.
