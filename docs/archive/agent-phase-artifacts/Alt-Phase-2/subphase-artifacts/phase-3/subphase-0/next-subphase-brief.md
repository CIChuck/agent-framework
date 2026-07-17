# Phase 3 Subphase 0 -> Subphase 1 Brief

## Assumptions Carried Forward

1. `single_agent` default behavior remains unchanged.
2. `multi_agent` remains explicit opt-in.
3. Orchestrator/arbitrator separation remains intact.
4. Global lint/type-check debt is baseline and must not be worsened by Subphase 1 changes.

## Required Inputs for Subphase 1

1. `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-build-plan.md` Workstreams A and B.
2. `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-transition-plan.md` sections 4.1 and 4.2.
3. Existing orchestrator/workflow implementation under:
   - `packages/friday-agent/src/friday_agent/orchestrator.py`
   - `packages/friday-agent/src/friday_agent/workflows/models.py`
   - `packages/friday-agent/src/friday_agent/workflows/engine.py`

## Subphase 1 Focus

1. Add route-stage decomposition as additive API (`route()`), preserving `process()` behavior.
2. Add deterministic approval resolution path for waiting tasks.
3. Add delegation/handoff payload contract enforcement.
4. Validate through targeted orchestrator/workflow tests plus full gates.

## Blockers

1. None.
