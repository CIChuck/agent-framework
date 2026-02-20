# Next Subphase Brief (Subphase 3)

## Assumptions Carried Forward

1. Multi-agent memory remains additive and opt-in.
2. Single-agent default behavior remains unchanged.
3. Arbitration and journal semantics now exist at module level and are ready for runtime wiring.

## Required Inputs

1. `docs/design/agents/Alt-Phase-2/phase-2-build-plan.md` Step 4, Step 6, Step 7.
2. Runtime package wiring (`friday-runtime/config.py`, `friday-runtime/di.py`, `friday-runtime/kernel.py`).

## Subphase 3 Implementation Targets

1. Wire mode-aware memory composition (`single_agent` vs `multi_agent`) in runtime DI.
2. Define arbitrator-unavailable degraded behavior in multi-agent mode.
3. Validate default-path compatibility for existing `friday.py` and runtime flows.

## Blocked Dependencies

1. No code blockers.
2. Type gate remains blocked by missing mypy executable.
