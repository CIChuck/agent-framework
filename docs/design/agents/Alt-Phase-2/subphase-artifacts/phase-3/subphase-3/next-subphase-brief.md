# Phase 3 Subphase 3 -> Subphase 4 Brief

## Assumptions Carried Forward

1. Promotion replay events now provide deterministic state-transition timelines.
2. Transcript metadata correlation (`correlation_id`, `proposal_id`, `promotion_id`) is available for forensics.
3. Promotion operations snapshot now emits warning-level degraded/backlog/failure alerts.
4. Existing runtime compatibility constraints remain unchanged (`single_agent` default, strict governance boundaries).

## Required Inputs for Subphase 4

1. `docs/design/agents/Alt-Phase-2/phase-3-build-plan.md` Workstream H.
2. `docs/design/agents/Alt-Phase-2/phase-3-transition-plan.md` section 4.5 and sequence rows 5-6.
3. Skill compatibility references:
   - `https://github.com/agentskills/agentskills/tree/main`
   - `https://github.com/anthropics/skills`

## Subphase 4 Focus

1. Implement dynamic skill routing against contract-declared skill references.
2. Enforce scope-boundary delegation and no-governance-expansion behavior for delegated skill activation.
3. Add federated skill catalog compatibility without changing runtime `skill_id@version` resolution semantics.
4. Add delegated skill lifecycle replay/audit evidence requirements.

## Blockers

1. None.
2. Baseline quality debt waivers remain active and must continue to be tracked separately from subphase regressions.
