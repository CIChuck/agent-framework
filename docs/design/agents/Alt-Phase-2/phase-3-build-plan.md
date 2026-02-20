# Alt Phase 3 Build Plan: Orchestration and Workflow Integration on Dual Memory Modes

**Status:** Proposed for Approval
**Date:** 2026-02-14
**Depends On:** Phase 2 build baseline (archived)
**Companion:** `docs/design/agents/Alt-Phase-2/phase-3-transition-plan.md`
**References:**
- `docs/design/agents/Alt-Phase-2/agent-contract.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-compliance-matrix.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-schema-spec.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-test-strategy.md`
- AgentSkills reference repository: `https://github.com/agentskills/agentskills/tree/main`
- Additional skill ecosystem reference: `https://github.com/anthropics/skills`

---

## 1. Goal

Implement Phase 3 orchestration and workflow capabilities on top of Alt Phase 2 dual-memory architecture, preserving single-agent defaults while enabling robust multi-agent execution.

---

## 2. Phase 3 Design Constraints

1. Preserve dual-mode runtime behavior (`single_agent` default, `multi_agent` opt-in).
2. Keep backward compatibility for existing orchestrator usage unless deprecation is explicitly approved.
3. Integrate arbitration escalation with existing task-state semantics.
4. Maintain `friday.py` default-path stability.
5. Enforce Agent Contract governance requirements for HITL, artifact lifecycle, and policy observability.
6. Complete skill orchestration semantics for routing, delegation, and auditability.
7. Preserve pinned skill-reference semantics (`skill_id@version`) while extending registry capabilities.
8. Integrate scratch pad memory into orchestration/workflow execution without changing durable memory semantics.
9. Preserve runtime filesystem-root separation in all orchestration/delegation flows.
10. Extend Phase 2 identity-capability and skill-approval authority controls into delegated workflows.

---

## 3. Workstreams

## Workstream A: Orchestrator Contract Completion

1. Decompose routing logic into explicit route stage while preserving current `process()` behavior.
2. Add internal namespace context propagation for multi-agent sessions.
3. Maintain compatibility with existing session management and delegation APIs.

Deliverables:

1. Route contract implementation and tests.
2. Multi-agent namespace handoff validation tests.

## Workstream B: Workflow-Arbitration Coupling

1. Map arbitration escalations to `TaskStatus.WAITING_APPROVAL` flows.
2. Add deterministic resume/resolve APIs for escalated tasks.
3. Maintain compatibility with existing workflow execution state shape.
4. Define and enforce a delegation/handoff payload contract (`handoff_id`, ownership, acceptance criteria, memory scope, deadlines).

Deliverables:

1. Workflow escalation integration tests.
2. Human-in-the-loop resolution coverage.
3. Delegation/handoff payload schema validation and compatibility tests.

## Workstream C: Multi-Agent Replay and Auditability

1. Implement replay for proposal/promotion timelines.
2. Correlate transcript entries with proposal and promotion IDs.
3. Support failure forensics for partially committed promotions.

Deliverables:

1. Replay engine updates.
2. Audit trace outputs.

## Workstream D: Operations Hardening

1. Add arbitration and promotion metrics.
2. Add recovery backlog alarms.
3. Add runbook docs for degraded arbitrator mode.
4. Define contract KPI/SLO thresholds:
   - HITL median response latency target,
   - HITL timeout-rate ceiling,
   - required-event completeness threshold.

Deliverables:

1. Metrics dashboards/specs.
2. Operational troubleshooting guide.
3. KPI/SLO threshold definitions and alert conditions.

## Workstream E: HITL Protocol and Authority Model

1. Implement HITL request/response payload schemas.
2. Implement `awaiting_human` lifecycle semantics with timeout/default actions.
3. Implement approver authority and scope validation (`HITLAuthorityPolicy`).

Deliverables:

1. HITL protocol contract implementation.
2. Authority enforcement and audit logging.
3. Deterministic timeout/resume/reject/cancel test coverage.

## Workstream F: Artifact Governance and Publication Controls

1. Define artifact lifecycle states (`draft`, `validated`, `final`, `archived`) as enforceable policy.
2. Enforce provenance requirements and publication approval gates where configured.

Deliverables:

1. Artifact lifecycle and provenance policy implementation.
2. Artifact governance test coverage.

## Workstream G: Contract Compliance Gates

1. Add contract KPI and checklist gates to phase verification.
2. Add contract-linked CI checks for required telemetry/event completeness.
3. Add explicit checklist-to-evidence artifact mapping in release workflows.
4. Standardize authority-policy templates for approver scope governance.

Deliverables:

1. Compliance gate definitions in CI/test harness.
2. Reporting outputs for contract compliance at release checkpoints.
3. Checklist evidence bundle and release review template.
4. Authority-policy template set and validation rules.

## Workstream H: Skill Orchestration and Delegation

1. Implement dynamic skill selection/routing against declared `skills`.
2. Integrate skill transitions with HITL pause/resume behavior for privileged steps.
3. Enforce skill scope-boundary delegation and handoff behavior in workflow execution.
4. Add skill-level replay and audit traceability requirements.
5. Extend local skill registry model to optional remote/federated registry synchronization without changing contract reference format.
6. Define deprecation and retirement rollout policies for shared skill catalogs across teams.
7. Add delegated approval-policy model for skill lifecycle transitions in production governance workflows.
8. Preserve canonical AgentSkills conformance gates (`skills-ref validate`, schema/layout/mapping CI checks) during federation and delegation flows.
9. Preserve Phase 2 runtime profile-composition and no-expansion governance semantics in delegated/federated execution paths.

Deliverables:

1. Skill routing and execution-state implementation.
2. Skill delegation/handoff conformance tests.
3. Skill replay and audit evidence outputs.
4. Registry federation strategy and compatibility specification.
5. Deprecation/retirement operational runbook for skill versions.
6. Delegated skill-approval authority model and validation suite.
7. Canonical skill conformance evidence bundle requirements for federated catalogs.
8. Composed-profile determinism and no-expansion enforcement for delegated skill activation.

## Workstream I: Scratch Pad Orchestration and Workflow Integration

1. Integrate scratch pad updates into orchestrator flow for plan creation and checklist progression.
2. Integrate workflow task-state transitions (`pending`, `running`, `completed`, `failed`, `skipped`, `waiting_approval`) with scratch `plan_item` status mappings.
3. Record HITL pause/resume checkpoints to scratch `event_log`.
4. Enforce scratch scope isolation and TTL behavior under orchestration load.
5. Add replay correlation between workflow history and scratch pad event stream.
6. Validate persistent scratch backend behavior under restart and recovery workflows.

Deliverables:

1. Scratch-aware orchestration integration tests.
2. Workflow-to-scratch state-mapping compatibility tests.
3. Scratch lifecycle replay/audit evidence outputs.
4. Scratch backend recovery and fallback-mode conformance tests.

## Workstream J: Deployment Filesystem Topology and Runtime Path Governance

1. Validate three-root runtime topology (`install_root`, `runtime_data_root`, `workspace_root`) across orchestrated runs.
2. Ensure agent workflow execution writes artifacts only to `workspace_root`.
3. Ensure runtime internals (journals, scratch persistence, state indexes) remain under `runtime_data_root`.
4. Add explicit container/cloud profile guidance where `install_root` is read-only.
5. Add path-overlap rejection and remediation behavior to operations runbooks.

Deliverables:

1. Filesystem-topology conformance tests in orchestration suites.
2. Deployment profile templates (local/container/cloud) with path defaults.
3. Path-governance runbook updates for production operations.

## Workstream K: Pipeline and Task Model Completion

1. Define and implement `WorkflowDefinition` schemas with one-or-more pipeline references.
2. Define and implement workflow-contained pipeline schemas and task-assignment schemas.
3. Implement orchestrator dispatch semantics for dependency-ready tasks.
4. Implement assignment claim/lease/recovery semantics for async execution.
5. Implement pipeline composition semantics for reusable pipelines in higher-order workflows.
6. Enforce typed task input/output contract validation across pipeline boundaries.
7. Enforce hierarchy integrity checks (`workflow -> pipeline -> task`) at dispatch time.

Deliverables:

1. Pipeline/task schema contracts and compatibility tests.
2. Dispatch/assignment deterministic behavior suite.
3. Cross-pipeline contract-validation and lineage evidence outputs.
4. Composition semantics and rollback/compensation policy runbook.
5. Workflow-to-pipeline reference integrity validation suite.

---

## 4. `friday.py` Policy in Phase 3

1. Default behavior remains `single_agent` and unchanged.
2. Any multi-agent enablement in `friday.py` is optional and explicitly gated.
3. No namespace command UX changes are mandatory for default path.

---

## 5. FridayContainer Decision Milestone

Phase 3 must include a formal decision checkpoint:

1. Retain wrapper with deprecation if still required by integration users.
2. Schedule sunset only with migration evidence and rollback plan.

---

## 6. Verification Gates

1. Existing orchestration tests remain green.
2. New route decomposition tests pass.
3. Multi-agent escalation/resume tests pass.
4. Replay consistency tests pass under failure/recovery scenarios.
5. `friday.py` default integration behavior remains unchanged.
6. HITL authority and timeout/default semantics pass deterministic tests.
7. Artifact lifecycle/provenance policy tests pass.
8. Contract KPI/checklist gates pass.
9. KPI/SLO thresholds are measured and reported in acceptance runs, warning-only for the first Phase 3 release cycle.
10. Delegation/handoff payload schema compatibility tests pass.
11. Release artifacts include checklist-to-CI evidence bundle.
12. Skill routing/delegation and skill lifecycle observability tests pass.
13. Pinned skill-reference compatibility is preserved under registry federation scenarios.
14. Scratch pad orchestration/workflow integration tests pass with scope and TTL guarantees.
15. Filesystem-topology and workspace-contamination tests pass for orchestration workflows.
16. Delegated skill-approval authority tests pass with audit evidence.
17. Shared-write identity+capability enforcement remains green under orchestrated multi-agent load.
18. Migration governance artifacts (`preflight`, `apply`, `rollback`) are present for release readiness where migration paths are exercised.
19. Canonical `SKILL.md` conformance gates (`skills-ref`, schema/layout/mapping) remain green under orchestration and federation scenarios.
20. Delegated/federated skill activation preserves profile/task/artifact composition semantics and rejects governance expansion.
21. Pipeline/task schema conformance gates pass for workflow-contained execution.
22. Dispatch/claim/lease/recovery semantics are deterministic and auditable.
23. Cross-pipeline typed handoff validation and lineage checks are green.
24. Workflow schema cardinality and pipeline-reference integrity gates are green.

## 6.1 AI-Agent Implementation Readiness for Compatibility Codebase

Phase 3 compatibility work is decision-complete when implemented with the defaults and outputs below.

Required implementation inputs:

1. Phase 2 canonical skill and validation contracts.
2. Delegation/handoff policy contracts and HITL authority constraints.
3. Federation and approval-governance invariants from contract/spec/compliance docs.
4. AgentSkills schema reference implementation (`https://github.com/agentskills/agentskills/tree/main`).
5. Skill profile composition and impact-class approval rules from Phase 2 compatibility docs.

Required implementation outputs:

1. Delegated workflow execution that preserves canonical skill validation and governance gates.
2. Federation paths that do not bypass `skills-ref` validation and local policy checks.
3. Evidence bundle generation for orchestration/federation compatibility runs.
4. Deterministic rejection/audit behavior for conformance failures in delegated and federated flows.
5. Deterministic composed-profile outputs and no-expansion proofs across delegation boundaries.
6. Deterministic workflow->pipeline->task dispatch traces with hierarchy integrity proofs.

No-open-decision defaults for implementation agents:

1. Canonical artifact remains `SKILL.md`; federation sync cannot replace this contract.
2. `skill_id@version` remains the only supported runtime reference format.
3. Production-like execution remains `strict` compatibility mode.
4. Non-development environments (`staging`, `preprod`, `production`) enforce mandatory `strict` compatibility mode.
5. Delegated approval workflows cannot grant execution to non-`approved` skills.

---

## 7. Execution Order

| Order | Area | Action | Depends On |
| :--- | :--- | :--- | :--- |
| 1 | `friday-agent` | Route decomposition + context propagation | Alt Phase 2 complete |
| 2 | `friday-agent/workflows` | Arbitration escalation integration | 1 |
| 3 | `friday-transcript` + integration | Replay and correlation | 2 |
| 4 | telemetry/ops docs | Metrics and degraded-mode runbooks | 3 |
| 5 | `friday-agent/workflows`, `friday-runtime` | HITL protocol + authority model | 2, 4 |
| 6 | artifact/workspace layer | Artifact governance and publication controls | 5 |
| 7 | `tests/lab`, telemetry | Contract KPI/checklist and CI compliance gates | 5, 6 |
| 8 | `friday-agent`, `friday-runtime` | Skill orchestration, delegation, and registry-federation enforcement | 5, 7 |
| 9 | `friday-memory`, `friday-agent/workflows` | Scratch pad orchestration/workflow integration and replay correlation | 2, 5, 7 |
| 10 | `friday-runtime`, ops docs | Filesystem-topology governance and deployment profile conformance | 4, 7, 9 |
| 11 | `friday-agent`, governance ops | Delegated skill-approval authority workflows and audit controls | 8, 10 |
| 12 | `friday-agent/workflows`, `friday-runtime` | Pipeline/task schemas, dispatch semantics, and composition validation | 2, 5, 8 |
| 13 | CLI/runtime policy | `FridayContainer` and `friday.py` decisions | 8, 9, 10, 11, 12 |

---

## 8. Exit Criteria

1. Route decomposition complete and compatible.
2. Workflow arbitration escalation/resume stable.
3. Replay and audit paths operational.
4. Dual-memory mode behavior validated end-to-end.
5. `friday.py` default-path unchanged unless explicitly opted into multi-agent mode.
6. `FridayContainer` lifecycle decision documented.
7. HITL protocol payload/state/authority semantics are implemented and validated.
8. Artifact lifecycle/provenance and publication controls are implemented.
9. Contract KPI/checklist gates are operational in verification pipeline.
10. Contract KPI/SLO thresholds are defined and measured in release gating, warning-only for the first Phase 3 release cycle and hard-gated beginning in the subsequent release cycle.
11. Delegation/handoff payload contract is implemented and verified across workflow boundaries.
12. Checklist-to-CI evidence bundle is mandatory and reviewed at release decision points.
13. Skill routing, scope-boundary delegation, and lifecycle observability are implemented and validated.
14. Registry federation/remote-extension behavior preserves `skill_id@version` compatibility and governance controls.
15. Federated skill catalogs are enabled in the first Phase 3 release candidate with strict compatibility and no-expansion governance controls.
15. Scratch pad workflow mapping, HITL checkpoint logging, and replay correlation are implemented and validated.
16. Runtime filesystem topology remains policy-compliant across local, container, and cloud deployment profiles.
17. Delegated skill-approval authority model is implemented with auditable transition controls.
18. Identity+capability shared-write enforcement remains valid under Phase 3 orchestration/delegation paths.
19. Migration governance controls remain enforceable in Phase 3 rollout and upgrade workflows.
20. Pipeline/task contracts are implemented and verified for workflow-contained orchestration.
21. Reusable pipeline composition is implemented with typed handoff validation and lineage evidence.
