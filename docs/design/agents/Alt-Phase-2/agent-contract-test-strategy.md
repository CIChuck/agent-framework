# Agent Contract Test Strategy

**Status:** Proposed for Approval
**Date:** 2026-02-14
**Purpose:** Define verification strategy and CI gates for Agent Contract compliance.
**Primary References:**
- `docs/design/agents/Alt-Phase-2/agent-contract.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-schema-spec.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-compliance-matrix.md`

---

## 1. Test Objectives

1. Prove required contract fields are enforced.
2. Prove policy-bound execution behavior for tools/sandbox/HITL.
3. Prove observability and audit requirements are satisfied.
4. Prove backward compatibility (`single_agent`, `friday.py` default path).
5. Prove skill manifest resolution and execution behavior are policy-compatible and auditable.
6. Prove scratch pad scope/retention/promotion behavior is policy-compatible and auditable.
7. Prove runtime filesystem topology and scratch-path placement policies are enforced across deployment profiles.

---

## 2. Test Layers

## 2.1 Schema Validation Tests

1. Valid contract accepted.
2. Missing required fields rejected.
3. Mode-policy mismatch rejected.
4. Version compatibility rules enforced.

## 2.2 Policy Enforcement Tests

1. Tool allowlist/denylist/approval behavior.
2. Sandbox restrictions (path/network/timeout/resource).
3. Workspace boundary violations rejected.
4. Privileged execution requires HITL approval where configured.

## 2.3 HITL Protocol Tests

1. Request/response payload schema validation.
2. State transitions (`running` -> `awaiting_human` -> terminal/resume paths).
3. Timeout/default action determinism.
4. Authority policy enforcement for approver roles/scope.

## 2.4 Artifact Governance Tests

1. Lifecycle transition validity.
2. Required provenance metadata presence.
3. Publication approval gates.

## 2.5 Observability and Integrity Tests

1. Required event completeness threshold.
2. Correlation ID propagation across task/tool/HITL/sandbox events.
3. Execution-result integrity (claim-to-output traceability).
4. Failure classification and remediation metadata.

## 2.6 Compatibility and Migration Tests

1. `single_agent` mode backward compatibility.
2. `friday.py` unchanged default behavior.
3. Metadata migration/backfill correctness and rollback readiness.

## 2.7 Skill Contract and Lifecycle Tests

1. Skill reference format validation (`skill_id@version`) when `skills` are declared.
2. Skill manifest resolution from local registry index.
3. Skill lifecycle-state gating (`approved` allowed; `retired` blocked; `deprecated` policy-controlled).
4. Skill-to-tool policy compatibility (`tool_chain` subset of `allowed_tools`).
5. Skill invariant enforcement and failure-path handling.
6. Out-of-scope skill handoff/escalation behavior.
7. Skill lifecycle event completeness and transition correctness.

## 2.8 Scratch Pad Policy and Lifecycle Tests

1. Scratch pad scope isolation (`session_id + agent_id`) and cross-agent access denial.
2. Typed task-board behavior (`plan`, `plan_item`, `note`, `artifact_ref`, `event_log`).
3. Plan-item state transition correctness (`pending`, `running`, `completed`, `blocked`).
4. TTL expiration behavior and purge semantics.
5. Quota enforcement (`max_entries`, `max_note_bytes`).
6. Scratch-to-durable promotion allow/deny behavior.
7. Scratch lifecycle event completeness and schema correctness.

## 2.9 Filesystem Topology and Path Governance Tests

1. Root topology validation (`install_root`, `runtime_data_root`, `workspace_root`) with overlap rejection.
2. Scratch persisted-path placement validation (under `runtime_data_root`, not `workspace_root` except test fixtures).
3. Startup behavior validation for non-writable runtime roots.
4. Deployment profile validation (local install, container read-only install root, cloud runtime volume).
5. Fallback behavior verification (`fail_fast` vs `disable_scratch`) on backend/path failures.

---

## 3. CI Gate Model

## 3.1 Mandatory Gates (Phase 2)

1. Contract schema validation suite passes.
2. Tool/sandbox/workspace enforcement suite passes.
3. Migration/backfill suite passes.
4. Observability event completeness suite passes.
5. Backward compatibility suite passes.
6. Code execution lifecycle stage-enforcement suite passes.
7. Skill contract validation, manifest resolution, and lifecycle compliance suite passes (when skills are enabled).
8. Scratch pad policy/lifecycle suite passes (when scratch pad is enabled).
9. Filesystem topology and scratch-path placement suite passes.

## 3.2 Mandatory Gates (Phase 3)

1. HITL protocol + authority suite passes.
2. Artifact governance suite passes.
3. Contract KPI/checklist gate passes.
4. Replay/audit consistency suite passes.
5. Advanced skill orchestration/delegation suite passes.
6. Scratch orchestration/workflow integration suite passes.
7. Deployment-profile filesystem conformance suite passes.

---

## 4. KPI/SLO Validation Targets

Targets are defined as release-gating thresholds and can be tightened over time.

1. HITL median response latency: must be <= configured target.
2. HITL timeout rate: must be <= configured ceiling.
3. Required-event completeness: must be >= configured threshold.
4. Contract validation success rate for registered agents: 100%.
5. Goal completion rate: must meet program threshold by agent class.
6. Policy compliance rate: must meet program threshold with no critical-severity violations.

---

## 5. Evidence Artifacts

Each release candidate MUST produce:

1. Contract validation report.
2. Policy enforcement report.
3. HITL protocol report (Phase 3).
4. Observability completeness report.
5. Compatibility and migration report.
6. Contract checklist sign-off artifact.
7. Skill contract validation report.
8. Skill execution compliance report.
9. Skill registry and manifest validation report.
10. Scratch pad compliance report.
11. Filesystem topology compliance report.

Checklist-to-evidence mapping:

| Checklist Item | Required Artifact |
| :--- | :--- |
| Contract fields complete and validated | `contract-validation-report.json` |
| Guardrails enforceable in runtime | `policy-enforcement-report.json` |
| Tool and sandbox policies tested | `execution-governance-report.json` |
| Logging completeness verified | `observability-completeness-report.json` |
| HITL methods/triggers/approval matrix validated | `hitl-protocol-report.json` |
| HITL timeout/default behavior validated | `hitl-protocol-report.json` |
| Failure and escalation paths validated | `failure-policy-report.json` |
| Artifact and workspace boundaries verified | `artifact-workspace-compliance-report.json` |
| Memory mode/provenance behavior verified | `memory-compatibility-migration-report.json` |
| Skill schema and lifecycle behavior verified | `skill-execution-compliance-report.json` |
| Skill registry/manifest resolution and state gating verified | `skill-registry-validation-report.json` |
| Scratch pad scope/retention/promotion behavior verified | `scratchpad-compliance-report.json` |
| Filesystem topology and scratch-placement behavior verified | `filesystem-layout-compliance-report.json` |

---

## 6. Ownership

| Suite | Primary Owner | Secondary Owner |
| :--- | :--- | :--- |
| Contract schema validation | `friday-core` | `friday-runtime` |
| Tool/sandbox/workspace enforcement | `friday-tools` | `friday-runtime` |
| HITL protocol/authority | `friday-agent/workflows` | `friday-runtime` |
| Artifact governance | workspace/artifact layer | `friday-agent` |
| Skill contract/lifecycle/registry | `friday-agent` | `friday-runtime` |
| Scratch pad policy/lifecycle | `friday-memory` | `friday-runtime` |
| Filesystem topology/path governance | `friday-runtime` | runtime ops |
| Observability/integrity | `friday-telemetry` | `tests/lab` |
| Compatibility/migration | `friday-memory` | integration test owners |

---

## 7. Exit Criteria Linkage

1. Phase 2 and Phase 3 build-plan exit criteria MUST reference this strategy.
2. Compliance matrix status updates MUST include test evidence outcomes from this strategy.
