# Next Subphase Brief (Subphase 1)

## Assumptions Carried Forward

1. `single_agent` remains default behavior.
2. Multi-agent capabilities remain additive and opt-in.
3. No core method signature breaks are allowed.
4. Runtime root topology constraints are enforced before multi-agent/scratch persistence features expand.

## Required Inputs

1. `docs/design/agents/Alt-Phase-2/phase-2-build-plan.md` Step 2 sections.
2. `docs/design/agents/Alt-Phase-2/technical-specifications.md` memory namespace/policy sections.
3. Current `friday-memory` controller/retrieval implementations for reuse instead of fork.

## Subphase 1 Implementation Targets

1. Create `friday_memory/multi_agent/` module with:
   - controller,
   - policy engine,
   - models,
   - journal,
   - coordinator.
2. Wire policy checks at critical write/read boundaries.
3. Preserve single-agent memory behavior unchanged.
4. Add subphase-focused tests for namespace isolation and union-read rules.

## Blocked Dependencies

1. None for code implementation.
2. Quality-gate reporting must continue to annotate known `ruff` and `mypy` baseline blockers.
