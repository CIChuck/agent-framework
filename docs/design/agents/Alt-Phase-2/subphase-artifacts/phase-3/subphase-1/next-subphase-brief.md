# Phase 3 Subphase 1 -> Subphase 2 Brief

## Assumptions Carried Forward

1. Route-stage decomposition is now available and backward compatible.
2. Workflow WAITING_APPROVAL semantics are preserved and now have deterministic resolve/reject paths.
3. Delegation/handoff payload contract is additive and validated only when present.
4. Status enum compatibility is preserved (`reject` mapped to `skipped` plus reason).

## Required Inputs for Subphase 2

1. `docs/design/agents/Alt-Phase-2/phase-3-build-plan.md` Workstreams E and F.
2. `docs/design/agents/Alt-Phase-2/phase-3-transition-plan.md` section 4.5.
3. Contract docs:
   - `docs/design/agents/Alt-Phase-2/agent-contract.md`
   - `docs/design/agents/Alt-Phase-2/agent-contract-schema-spec.md`
   - `docs/design/agents/Alt-Phase-2/agent-contract-test-strategy.md`

## Subphase 2 Focus

1. Implement execution-grade HITL protocol payloads and authority-policy enforcement.
2. Enforce `awaiting_human` timeout/default action behavior.
3. Implement artifact lifecycle governance and publication controls.
4. Add deterministic policy/audit tests for HITL and artifact governance.

## Blockers

1. None.
2. Quality debt waivers remain active and must continue to be tracked separately from subphase regressions.
