# Next Subphase Brief (Subphase 2)

## Assumptions Carried Forward

1. Multi-agent implementation remains additive and wrapper-based.
2. Single-agent default behavior remains unchanged.
3. Shared writes stay blocked without capability-based authorization.
4. Proposal + journal scaffolding exists and will be hardened.

## Required Inputs

1. `docs/design/agents/Alt-Phase-2/phase-2-build-plan.md` Step 3.
2. `docs/design/agents/Alt-Phase-2/technical-specifications.md` arbitration and promotion state semantics.

## Subphase 2 Implementation Targets

1. Introduce arbitration decision path integration.
2. Implement journal state transitions (`pending -> graph_written -> vector_written -> committed|failed|compensated`).
3. Add deterministic recovery/replay for non-terminal journal entries.
4. Add anti-spoof/invalid capability rejection tests at shared-write boundaries.

## Blocked Dependencies

1. No code blockers.
2. Full quality gates continue to be partially blocked by baseline lint backlog and missing mypy binary.
