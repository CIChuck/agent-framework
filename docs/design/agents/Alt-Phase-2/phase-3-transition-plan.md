# Phase 3 Transition Plan (From Alt Phase 2 Multi-Agent Memory)

**Status:** Proposed for Approval
**Date:** 2026-02-14
**Purpose:** Define how Phase 3 should build on the Alt Phase 2 additive multi-agent memory foundation.
**References:**
- `docs/design/agents/Alt-Phase-2/agent-contract.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-compliance-matrix.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-schema-spec.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-test-strategy.md`
- `docs/design/agents/Alt-Phase-2/phase-2-build-plan.md`

---

## 1. Transition Summary

Alt Phase 2 establishes two stable memory modes:

1. `single_agent` (default, backward compatible)
2. `multi_agent` (namespace + arbitrator + journaled promotion)

Phase 3 should focus on orchestration and workflow evolution on top of these modes, without destabilizing single-agent behavior.

---

## 2. Phase 3 Objectives

1. Complete orchestrator route decomposition and context propagation.
2. Integrate arbitration escalation with workflow execution and approval UX.
3. Add operational tooling (replay/observability) for multi-agent sessions.
4. Resolve deferred architectural decisions from Phase 1 and Alt Phase 2.
5. Standardize delegation/handoff contracts and contract-evidence governance for release decisions.
6. Complete advanced skill orchestration and delegation governance.
7. Integrate scratch pad operational memory into orchestration and workflow governance.
8. Ensure deployment-grade filesystem topology governance across local, container, and cloud runtimes.
9. Carry forward identity-capability shared-write security and skill-approval authority controls into delegated workflows.

---

## 3. Required Inputs from Alt Phase 2

Before starting Phase 3, these must be complete:

1. Multi-agent memory policy enforcement and bypass resistance tests.
2. Promotion journal + recovery worker with deterministic behavior.
3. Runtime mode wiring and documented default path.
4. `friday.py` default-path compatibility confirmation.
5. Documented additive interface contracts and config schema.
6. Agent contract schemas and load-time validation foundations.
7. Tool/sandbox policy enforcement for high-impact execution paths.
8. Metadata migration/backfill readiness for multi-agent fields.
9. Code execution lifecycle contract and integrity checks implemented.
10. Checklist-to-CI evidence mapping artifacts available for Phase 3 release gates.
11. Skill schema validation and baseline skill lifecycle event contract implemented in Phase 2.
12. Local filesystem-backed skill manifest repository and registry index baseline established with pinned `skill_id@version` references.
13. Scratch pad contract baseline (scope, TTL, quotas, promotion policy, required events) implemented in Phase 2.
14. Runtime filesystem topology baseline (`install_root`, `runtime_data_root`, `workspace_root`) and scratch-path placement rules implemented in Phase 2.
15. Shared-write anti-spoof controls (arbitrator identity + runtime capability enforcement) implemented in Phase 2.
16. Migration governance baseline (`preflight`, `apply`, `rollback`) and reporting artifacts implemented in Phase 2.
17. Skill approval-authority metadata enforcement for `proposed -> approved` transitions implemented in Phase 2.

---

## 4. Phase 3 Workstreams

## 4.1 Orchestrator Contract Completion

1. Extract/define explicit route stage (`route()` decomposition) while preserving existing behavior.
2. Propagate namespace context through orchestration chain for multi-agent sessions.
3. Ensure session/user context invariants continue to hold across delegation.

## 4.2 Workflow + Arbitration Integration

1. Map arbitration escalations to existing `TaskStatus.WAITING_APPROVAL` flow.
2. Implement resume/reject paths with clear audit trails.
3. Avoid introducing conflicting workflow state models unless full migration is planned.
4. Define a stable delegation/handoff payload schema with ownership, acceptance criteria, and deadline semantics.
5. Integrate skill scope-boundary delegation behavior with workflow handoff semantics.

## 4.3 Replay and Transcript-Backed Analysis

1. Implement replay support for multi-agent proposal timelines.
2. Correlate proposal/promotion IDs with transcript/session events.
3. Add forensic tooling for conflict history and resolution outcomes.

## 4.4 Operations and Observability

1. Add metrics for:
   - proposal volume,
   - promotion latency,
   - conflict rates,
   - recovery retries,
   - compensation events.
2. Add alerts for sustained arbitrator degradation or recovery backlog growth.

## 4.5 Contract Governance Completion

1. Implement execution-grade HITL protocol (payload, state transitions, timeout/default behavior).
2. Implement HITL authority policy for approver role/scope enforcement.
3. Implement artifact governance lifecycle and publication approval controls.
4. Add contract KPI and checklist gates to release validation.
5. Publish authority-policy templates and checklist evidence bundle requirements for release governance.
6. Complete skill-routing and skill-lifecycle governance for production release readiness.
7. Define Phase 3 extension path for optional remote/federated skill registry while preserving pinned reference semantics.
8. Integrate workflow and HITL transitions with scratch pad plan/item/event updates for replay-grade traceability.
9. Validate path-governance controls so runtime state remains in `runtime_data_root` and artifacts remain in `workspace_root`.
10. Extend skill approval-authority controls from human-only baseline to delegated governance where approved by policy.
11. Preserve migration-governance controls and artifacts for upgrade/cutover workflows in Phase 3 operations.

---

## 5. `friday.py` Strategy in Phase 3

1. Maintain default `single_agent` mode path unchanged unless explicit migration is approved.
2. Provide optional experimental launch path for multi-agent mode (opt-in only).
3. Keep command-level behavior stable by default; multi-agent UX additions should be gated behind mode checks.

---

## 6. FridayContainer Decision Gate

Phase 3 must explicitly resolve the `FridayContainer` lifecycle:

1. If compatibility/usage data still justifies wrapper retention, keep with deprecation notice.
2. If usage is negligible and migration path is complete, schedule controlled removal in later phase.
3. Document decision with migration and rollback plans.

---

## 7. Risks for Phase 3

1. Risk: orchestration changes accidentally assume multi-agent mode.
   - Mitigation: dual-mode test matrix required for every orchestration change.
2. Risk: replay tooling increases coupling to transient data formats.
   - Mitigation: stable event schema and versioned proposal lifecycle events.
3. Risk: accumulating deprecations become permanent debt.
   - Mitigation: explicit decision milestones and sunset criteria.

---

## 8. Phase 3 Exit Criteria (Transition-Focused)

1. Route decomposition is complete and backward-compatible.
2. Workflow arbitration pauses/resumes are deterministic and tested.
3. Proposal lifecycle is observable end-to-end.
4. Dual-mode runtime behavior is stable under integration load.
5. `friday.py` default mode remains unaffected unless explicit migration flag is enabled.
6. `FridayContainer` disposition is explicitly decided and documented.
7. HITL authority and timeout/default semantics are validated end-to-end.
8. Artifact governance lifecycle and approval controls are operational.
9. Contract KPI/checklist gates are included in phase verification.
10. Contract KPI/SLO thresholds are defined and enforced in release decisions.
11. Delegation/handoff payload compatibility is validated across workflow boundaries.
12. Checklist evidence bundle is required at transition readiness review.
13. Skill routing/delegation behavior is validated with replay/audit evidence.
14. Registry-extension strategy (local to federated/remote) is documented with backward-compatible `skill_id@version` resolution.
15. Scratch pad orchestration/workflow integration is validated with scope isolation and TTL compliance evidence.
16. Filesystem-topology conformance is validated for non-git deployments and container/cloud profiles.
17. Shared-write anti-spoof controls remain effective under Phase 3 orchestration/delegation workflows.
18. Migration governance artifacts (`preflight`, `apply`, `rollback`) are required in transition readiness review.
19. Skill approval-authority transitions are auditable with required metadata and policy-conformant delegation behavior.

---

## 9. Recommended Phase 3 Sequencing

| Order | Area | Outcome |
| :--- | :--- | :--- |
| 1 | Orchestrator decomposition | explicit routing contracts + namespace context handoff |
| 2 | Workflow integration | arbitration escalation mapped to approval lifecycle |
| 3 | Replay/transcript integration | deterministic event replay and forensic traceability |
| 4 | Observability hardening | operational metrics/alerts for production confidence |
| 5 | Contract governance completion | HITL protocol, authority policy, artifact lifecycle, skill governance, KPI gates, and checklist evidence governance |
| 6 | Skill orchestration completion | routing, delegation, replay, policy-bound lifecycle controls, and registry-extension compatibility |
| 7 | Scratch pad integration completion | orchestrator/workflow/HITL state mapping and replay correlation for private scratch pads |
| 8 | Filesystem topology hardening | deployment-profile path governance and workspace contamination prevention |
| 9 | Authority/control hardening | shared-write anti-spoof controls and skill approval-authority delegation governance |
| 10 | Deprecation decisions | `FridayContainer` and long-term mode defaults clarified |
