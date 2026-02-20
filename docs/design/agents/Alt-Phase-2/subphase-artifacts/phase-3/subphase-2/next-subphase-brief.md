# Phase 3 Subphase 2 -> Subphase 3 Brief

## Assumptions Carried Forward

1. Structured HITL request/decision payloads and authority validation are now available and additive.
2. `awaiting_human` timeout handling is deterministic for `safe_abort`, `constrained_continue`, and `defer`.
3. Artifact lifecycle/publication controls are policy-driven and auditable.
4. Legacy approval interfaces remain backward compatible and route through structured decision logic.

## Required Inputs for Subphase 3

1. `docs/design/agents/Alt-Phase-2/phase-3-build-plan.md` Workstreams C and D.
2. `docs/design/agents/Alt-Phase-2/phase-3-transition-plan.md` sections 4.3 and 4.4.
3. Existing workflow/orchestrator integration behavior from Subphase 1 and HITL/artifact controls from Subphase 2.

## Subphase 3 Focus

1. Implement replay for proposal/promotion timeline forensics.
2. Correlate transcripts with proposal/promotion IDs for end-to-end diagnosability.
3. Add operations-grade metrics and alert scaffolding for arbitration/recovery/degraded mode.
4. Publish degraded-mode/remediation runbook artifacts.

## Blockers

1. None.
2. Baseline quality debt waivers remain active and must continue to be tracked independently of subphase regressions.
