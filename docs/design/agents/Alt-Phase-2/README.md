# Alt Phase 2 Documentation Set

This folder contains an alternate planning track for Phase 2 that introduces **Multi-Agent Memory as an additive mode**, **Scratch Pad Memory** as private operational memory, and a **deployment-agnostic runtime filesystem topology** while preserving default single-agent behavior.

## Approval State

This document set is currently marked **Proposed for Approval**.

## Documents

1. `phase-1-build-plan.md`
   - Historical baseline copied from `docs/design/agents/Phase-2/phase-1-build-plan.md` for transition context.
2. `comprehensive-agent-framework-design.md`
   - Architectural rationale and component model.
3. `technical-specifications.md`
   - Additive interfaces, schemas, state machines, policy rules, and runtime path/topology requirements.
4. `phase-2-build-plan.md`
   - Detailed implementation plan for Alt Phase 2.
5. `phase-3-transition-plan.md`
   - Transition contract from Alt Phase 2 to Phase 3.
6. `phase-3-build-plan.md`
   - Updated Phase 3 build direction aligned to dual-memory architecture.
7. `agent-contract.md`
   - Standard contract for agent goals, guardrails, scratch-pad and skill governance, tool usage, sandboxed code execution, logging, and escalation.
8. `agent-contract-compliance-matrix.md`
   - Clause-by-clause compliance analysis and upgrade plan for the Alt document set.
9. `agent-contract-schema-spec.md`
   - Canonical schema and validation specification for Agent Contract governance.
10. `agent-contract-test-strategy.md`
   - Verification and CI gate strategy for contract compliance.
11. `agent-integration-test-plan.md`
   - End-to-end integration test planning for solitary-agent and multi-agent workflows, including environment construction.

## Source Inputs

This alt track incorporates findings from:

- `docs/design/agents/Phase-2/codex-phase-2-build-plan-commentary.md`
- Existing Phase 2 docs under `docs/design/agents/Phase-2/`

## Compliance Posture

Per `agent-contract-compliance-matrix.md`, this document set is now broadly contract-aligned with remaining precision work focused on:

1. Agent-class KPI/SLO calibration.
2. Authority-policy template standardization.
3. Package-level failure/rollback runbook depth.
4. Phase 3 depth for dynamic skill routing/delegation governance.
5. Phase 3 extension strategy for optional federated/remote skill registry operations.
6. Scratch pad TTL/quota defaults and workflow integration depth calibration.
7. Deployment-profile defaults for runtime filesystem roots and scratch backend selection.
