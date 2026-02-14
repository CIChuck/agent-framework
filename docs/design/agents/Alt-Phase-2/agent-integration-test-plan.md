# Agent Integration Test Plan

**Status:** Proposed for Approval  
**Date:** 2026-02-14  
**Purpose:** Define end-to-end integration test planning for solitary-agent and multi-agent workflows, including environment construction strategy and release-gate alignment.

**References:**
- `docs/design/agents/Alt-Phase-2/agent-contract.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-test-strategy.md`
- `docs/design/agents/Alt-Phase-2/phase-2-build-plan.md`
- `docs/design/agents/Alt-Phase-2/phase-3-build-plan.md`
- `docs/design/agents/Alt-Phase-2/technical-specifications.md`

---

## 1. Scope and Outcomes

This plan defines:

1. Integration test tracks for:
   - solitary-agent execution,
   - multi-agent workflow execution.
2. Two to three concrete use cases for each track.
3. Construction plans for test environments that can execute those use cases reliably.
4. Readiness gates for when each class of end-to-end test can be considered:
   - development-ready,
   - release-gate-ready.

---

## 2. Readiness Milestones

## 2.1 Solitary-Agent End-to-End Readiness

1. **Development-ready point:** Alt Phase 2 completion through runtime wiring and `friday.py` compatibility validation.
2. **Release-gate-ready point:** Alt Phase 2 acceptance and exit criteria complete (policy enforcement, contract validation, observability completeness, integrity checks).

## 2.2 Multi-Agent Workflow End-to-End Readiness

1. **Development-ready point:** Alt Phase 3 Workstream A+B complete (route/context + workflow/arbitration coupling).
2. **Release-gate-ready point:** Alt Phase 3 verification gates and exit criteria complete for HITL authority, artifact governance, KPI/checklist evidence, and handoff contract validation.

---

## 3. Test Tracks and Use Cases

## 3.1 Track A: Solitary-Agent Integration

### Use Case SA-1: Single-Agent REPL Task with Sandboxed Execution

Goal:

1. Validate that a single agent can plan, generate code, execute in sandbox, and produce an artifact inside workspace boundaries.

Primary assertions:

1. `single_agent` mode remains default.
2. Workspace boundaries are enforced.
3. Execution-result integrity and required telemetry events are recorded.
4. `friday.py` behavior remains stable with no namespace requirements.

### Use Case SA-2: Single-Agent Memory Recall/Store Loop

Goal:

1. Validate memory write/read lifecycle for a solitary agent without multi-agent namespace plumbing.

Primary assertions:

1. Existing `MemoryController` semantics remain compatible.
2. Recall quality and persistence behavior are unchanged in default mode.
3. Contract validation does not introduce regressions in single-agent startup/load.

### Use Case SA-3: Semi-Autonomous Solitary Agent with HITL Approval Gate

Goal:

1. Validate solitary-agent escalation to human review for high-impact action in a non-multi-agent session.

Primary assertions:

1. `awaiting_human` pause behavior is deterministic.
2. Timeout/default action behavior is deterministic and auditable.
3. Unauthorized approval attempts are rejected when authority policy is enforced.

---

## 3.2 Track B: Multi-Agent Workflow Integration

### Use Case MA-1: Collaborative Draft + Arbitration Promotion

Goal:

1. Validate two-worker-agent collaboration where private findings are promoted to shared memory through arbitrator-only write path.

Primary assertions:

1. Cross-agent private reads are denied.
2. Non-arbitrator shared writes are denied.
3. Promoted facts become visible only after journal commit.
4. Recovery worker handles interrupted promotions without duplicate shared truth.

### Use Case MA-2: Conflict Escalation and Human Adjudication

Goal:

1. Validate multi-agent conflict where promotion is escalated to HITL and resolved through approval workflow.

Primary assertions:

1. Escalation trigger taxonomy is honored.
2. HITL request payload and response payload are schema-valid.
3. Approve/reject/timeout paths are replayable and auditable.
4. Workflow resumes or terminates deterministically by decision outcome.

### Use Case MA-3: Delegation/Handoff with Artifact Finalization

Goal:

1. Validate end-to-end delegation from coordinator agent to specialist agent with explicit handoff contract and artifact lifecycle controls.

Primary assertions:

1. Handoff payload includes ownership, acceptance criteria, memory scope, and deadline.
2. Artifact lifecycle transitions (`draft` to `validated` to `final`) follow policy.
3. Publication approval controls are enforced when configured.
4. Checklist-to-CI evidence bundle includes handoff and artifact compliance reports.

---

## 4. Integration Test Environment Construction

## 4.1 Environment Blueprint

Define four reusable integration environments:

1. `IE-SA-BASE`:
   - single-agent default runtime,
   - sandbox enabled,
   - telemetry sink enabled,
   - no multi-agent features required.
2. `IE-SA-HITL`:
   - `IE-SA-BASE` plus HITL simulator and authority policy fixtures.
3. `IE-MA-CORE`:
   - multi-agent mode enabled,
   - namespace policy engine and arbitrator path enabled,
   - durable proposal journal and recovery worker enabled.
4. `IE-MA-HITL`:
   - `IE-MA-CORE` plus workflow approval/HITL adapter, handoff validation hooks, and artifact policy enforcement.

## 4.2 Shared Environment Components

All environments should include:

1. Deterministic fixture loader for tasks, memory records, and expected artifact outputs.
2. Ephemeral but reproducible storage layout for vector, graph, and journal state.
3. Sandboxed execution harness with explicit policy profiles.
4. Structured event capture and correlation IDs across runtime, tools, sandbox, HITL, and memory events.
5. Failure injection hooks for crash/restart, timeout, and policy-denial scenarios.

## 4.3 Isolation and Repeatability Rules

1. Each test run uses unique session IDs and workspace roots.
2. Test data is seeded at run start and cleaned at run end.
3. Journal replay/recovery tests must run against persisted state snapshots, not in-memory-only mocks.
4. Flaky-test risk is reduced via deterministic clocks/timeouts in HITL and promotion workflows.

---

## 5. Use Case to Environment Mapping

| Use Case | Primary Environment | Secondary Environment | Earliest Phase Gate |
| :--- | :--- | :--- | :--- |
| SA-1 | `IE-SA-BASE` | `IE-SA-HITL` | Phase 2 Step 6 |
| SA-2 | `IE-SA-BASE` | `IE-SA-HITL` | Phase 2 Step 5/6 |
| SA-3 | `IE-SA-HITL` | `IE-SA-BASE` | Phase 3 Workstream E |
| MA-1 | `IE-MA-CORE` | `IE-MA-HITL` | Phase 3 Workstream A+B |
| MA-2 | `IE-MA-HITL` | `IE-MA-CORE` | Phase 3 Workstream E |
| MA-3 | `IE-MA-HITL` | `IE-MA-CORE` | Phase 3 Workstream B+F |

---

## 6. Test Construction Plan

## 6.1 Wave 1 (Phase 2): Solitary-Agent E2E Baseline

1. Build `IE-SA-BASE` and integrate with existing single-agent regression suite.
2. Add SA-1 and SA-2 scenario fixtures with pass/fail contracts.
3. Add evidence artifact outputs required by contract checklist mapping.
4. Publish baseline reliability and runtime-performance metrics.

Exit condition:

1. Solitary-agent end-to-end suite is stable and release-gate-ready for Phase 2 criteria.

## 6.2 Wave 2 (Phase 3 Early): Multi-Agent Core Workflow E2E

1. Build `IE-MA-CORE` with arbitration, journal, and recovery enabled.
2. Add MA-1 scenario and failure-injection variants.
3. Validate namespace and shared-write guardrails under stress/concurrency tests.

Exit condition:

1. Multi-agent core flow is development-ready with deterministic promotion/recovery behavior.

## 6.3 Wave 3 (Phase 3 Mid/Late): HITL and Artifact Governance E2E

1. Build `IE-SA-HITL` and `IE-MA-HITL`.
2. Add SA-3 and MA-2/MA-3 scenarios.
3. Add handoff payload contract validation and artifact lifecycle enforcement checks.
4. Add release-grade KPI/checklist evidence bundling and CI gating.

Exit condition:

1. Multi-agent workflow suite is release-gate-ready against full Phase 3 verification and exit criteria.

---

## 7. CI and Evidence Strategy

Each integration run must emit contract-aligned artifacts:

1. `contract-validation-report.json`
2. `policy-enforcement-report.json`
3. `execution-governance-report.json`
4. `observability-completeness-report.json`
5. `memory-compatibility-migration-report.json`
6. `hitl-protocol-report.json` (when HITL scenarios are executed)
7. `artifact-workspace-compliance-report.json` (when artifact lifecycle scenarios are executed)
8. `failure-policy-report.json`

Release candidates must include checklist sign-off linked to these artifacts.

---

## 8. Risks and Mitigations

1. Risk: early multi-agent E2E attempts before workflow coupling is stable.
   - Mitigation: gate MA scenarios behind Phase 3 A+B readiness.
2. Risk: flaky HITL timeout tests.
   - Mitigation: deterministic timeout clocks and controlled HITL simulators.
3. Risk: observability drift between scenarios.
   - Mitigation: event-schema contract checks in every integration run.
4. Risk: divergence between solitary and multi-agent harnesses.
   - Mitigation: shared fixture framework and shared assertion library where possible.

---

## 9. Approval and Governance

This plan should be approved alongside:

1. Alt Phase 2 build plan,
2. Alt Phase 3 build plan,
3. Agent Contract compliance matrix,
4. Agent Contract test strategy.

Any change to required policies, HITL semantics, handoff schema, or artifact lifecycle must trigger a review/update of this plan.
