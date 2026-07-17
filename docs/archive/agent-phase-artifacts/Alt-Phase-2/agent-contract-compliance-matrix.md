# Agent Contract Compliance Matrix

**Status:** Proposed for Approval
**Date:** 2026-02-14
**Purpose:** Map `agent-contract.md` requirements to Alt Phase 2/3 planning artifacts, identify gaps, and define concrete upgrade actions.

**Primary Source Contract:** `docs/archive/agent-phase-artifacts/Alt-Phase-2/agent-contract.md`
**Mapped Planning Set:**
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/README.md`
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/comprehensive-agent-framework-design.md`
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/technical-specifications.md`
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-1-build-plan.md`
- Phase 2 build baseline (archived)
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-transition-plan.md`
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-build-plan.md`
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/agent-contract-schema-spec.md`
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/agent-contract-test-strategy.md`

---

## 1. Executive Assessment

Current state is **largely compliant with targeted precision work remaining**.

1. Strong coverage exists for memory mode strategy, namespace policy, arbitrator semantics, atomic promotion, backward compatibility posture, and `friday.py` reduced impact.
2. Planning coverage includes contract schemas, tool/sandbox governance, guardrail/escalation policy structure, skill contract structure, skill manifest/registry governance, scratch pad governance, filesystem-topology governance, HITL protocol workstreams, artifact governance, migration/backfill, observability contracts, and checklist-to-CI evidence mapping.
3. Remaining work is mostly calibration and operating-model refinement (threshold tuning and organization-specific authority templates).

Overall readiness classification:

- **Architecture intent:** Strong
- **Implementation planning completeness vs contract:** High
- **Execution-grade contract traceability:** Medium-High (requires threshold calibration in implementation)

---

## 2. Coverage Legend

- `Full`: requirement is concretely specified with implementation and verification intent.
- `Partial`: requirement is mentioned but not execution-grade or missing tests/ownership.
- `Missing`: no meaningful coverage in current planning set.

### Second-Pass Evidence Method

This pass used both:

1. section-by-section document comparison, and
2. targeted keyword scans across companion docs for contract-critical terms (`sandbox`, `tool policy`, `allowlist`, `model_policy`, `skills`, `skill_id@`, `manifest`, `registry`, `approval_id`, `approved_by`, `scratch`, `scratch_pad_policy`, `ttl`, `filesystem`, `runtime_data_root`, `workspace_root`, `install_root`, `capability`, `preflight`, `rollback_checkpoint`, `mandatory_approval`, `awaiting_human`, `request_id`, `default_action`).

If a requirement had no explicit section anchor and no relevant keyword hits, it remained `Missing`.

---

## 3. Requirement Compliance Matrix

| Contract Requirement | Contract Reference | Current Coverage | Evidence in Alt Docs | Gaps / Deficiencies | Required Upgrade Action | Target Phase | Owner |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Agent identity and role model | `agent-contract.md` sec 3, items 1-4 | Full | `AgentContract` schema fields defined in technical specs and schema spec | None material | Keep schema-validation gate mandatory in Phase 2 | Phase 2 | `friday-core` |
| Goals/objectives/success/stop conditions | sec 3, items 5-8 | Full | Runtime contract schema and validation interface include mission fields | Objective-quality thresholds still tuned per domain | Keep objective/stop-condition test fixtures in contract suite | Phase 2 | `friday-core` + `friday-agent` |
| Mode (autonomous/semi/copilot) | sec 2, sec 3 item 9 | Full | Mode field and mode-dependent invariants/tests are specified | Mode heuristics may evolve | Keep mode-policy mismatch tests in schema suite | Phase 2 | `friday-agent` |
| Workspace policy | sec 3 item 10, sec 8 | Full | Agent contract schemas now include workspace roots and Phase 2 includes workspace-boundary enforcement/testing | Cross-package implementation details may evolve | Keep workspace-boundary tests as required exit gate | Phase 2 | `friday-tools` + `friday-runtime` |
| Runtime filesystem topology (`install_root`, `runtime_data_root`, `workspace_root`) | sec 8.1 | Full | Technical specs and phase plans define three-root runtime model and startup path-validation behavior | Deployment profile defaults still need calibration by environment class | Keep filesystem-topology validation tests mandatory in Phase 2/3 gates | Phase 2+3 | `friday-runtime` + ops owner |
| Tool policy | sec 3 item 11, sec 5 | Full | Policy schemas are specified and Phase 2 includes tool/sandbox governance workstream | Threshold defaults and policy tuning guidance remain implementation-specific | Keep policy contract in technical specs and validate in Phase 2 tests | Phase 2 | `friday-tools` + `friday-agent` |
| Model policy | sec 3 item 12 | Full | `ModelPolicy` schema and contract validation are included in technical specs and Phase 2 schema workstream | Runtime selection heuristics may need future optimization guidance | Keep fallback/cost/latency policy validation in Phase 2 gates | Phase 2 | `friday-llm` + `friday-core` |
| Memory policy | sec 3 item 13, sec 9 | Full | Dual memory mode architecture and runtime config are explicit | None material | Keep as baseline and link to contract schema | Phase 2 | `friday-memory` + `friday-runtime` |
| Arbitrator shared-write anti-spoof enforcement | sec 9.2 | Partial | Arbitrator-only write policy exists, but identity+capability anti-spoof detail is newly added and requires full test hardening | Capability issuance/validation flow needs full gate evidence | Add capability enforcement tests and evidence artifacts as required gate | Phase 2+3 | `friday-runtime` + `friday-memory` |
| Scratch pad policy and scope isolation | sec 3 item 21, sec 9.1 | Full | Scratch pad policy and `(session_id, agent_id)` scope isolation are defined in contract/spec/phase plans | Cross-agent sharing policy extensions are future scope | Keep scope-isolation and access-denial tests mandatory | Phase 2 | `friday-memory` + `friday-runtime` |
| Scratch pad retention and quotas | sec 9.1 | Full | TTL/quota semantics are represented in schema/spec/build docs | Workload-specific default tuning may evolve | Keep TTL/quota validation in Phase 2 gates | Phase 2 | `friday-memory` |
| Scratch-to-durable promotion governance | sec 9.1 | Full | Explicit promotion-only policy and allow/deny behavior are documented | Policy tuning by agent class may evolve | Keep promotion allow/deny tests mandatory | Phase 2+3 | `friday-memory` + `friday-agent` |
| Scratch pad observability | sec 11 | Full | Required scratch lifecycle/mutation events are specified and mapped to evidence artifacts | Event schema versions may evolve | Keep scratch event completeness checks in CI | Phase 2+3 | `friday-telemetry` + `friday-memory` |
| Scratch persisted-path placement (outside workspace) | sec 9.1 | Full | Scratch placement rules and runtime config constraints are specified in contract/spec/build docs | Test-mode exception policy needs consistent fixture profile docs | Keep scratch path-placement validation mandatory in Phase 2/3 gates | Phase 2+3 | `friday-memory` + `friday-runtime` |
| Guardrails | sec 3 item 14, sec 7 | Full | `GuardrailPolicy` schema and cross-domain enforcement/testing are now explicit in specs and plans | Rule libraries may expand over time | Keep guardrail policy coverage in Phase 2 compliance tests | Phase 2 | `friday-core` + `friday-agent` |
| Escalation policy | sec 3 item 15, sec 10 | Full | Escalation policy schema and trigger taxonomy are specified and mapped to implementation/test workstreams | Organization-specific escalation profiles may need tuning | Keep escalation-trigger and default-action tests in Phase 3 suites | Phase 3 | `friday-agent/workflows` |
| Skill definition and schema | sec 3 item 20, sec 5.3 | Full | `skills` field plus `SkillRef`/manifest schema are specified in contract/schema/spec docs | Skill catalog governance will evolve per team | Keep skill-schema validation mandatory when skills are declared | Phase 2 | `friday-core` + `friday-agent` |
| Skill manifest repository definition | sec 5.4 | Full | Local filesystem-backed repository layout and registry index are specified in contract/spec/build-plan docs | Remote/federated extension remains Phase 3 scope | Keep local manifest/registry validation as Phase 2 required gate | Phase 2 | `friday-agent` + `friday-runtime` |
| Canonical `SKILL.md` conformance and validator gating | sec 5.3, sec 5.4 | Partial | Skill governance and lifecycle are defined; explicit AgentSkills reference validation and schema/layout/mapping CI evidence need hard-gating language | Canonical format conformance can drift without mandatory validator/CI artifacts | Add mandatory `skills-ref validate` pre-approval/release gate, canonical schema/layout/mapping CI checks, and evidence artifacts | Phase 2+3 | `friday-agent` + `friday-runtime` + governance owner |
| Skill runtime-profile composition governance | sec 5.3, sec 5.5 | Partial | Skills are documented as runtime profile overlays; composition precedence and no-expansion intent are represented | Composition behavior and approval-impact class enforcement need explicit CI/evidence hard gates | Add deterministic composition tests, policy-diff classifier gates, no-expansion assertions, and impact-class approval enforcement artifacts | Phase 2+3 | `friday-agent` + `friday-runtime` + governance owner |
| Skill reference pinning (`skill_id@version`) | sec 5.3, sec 5.4 | Full | Pinned-reference rule is now explicit in contract/schema/spec/build docs | None material | Keep unpinned-reference rejection tests mandatory | Phase 2 | `friday-core` + `friday-agent` |
| Skill lifecycle-state execution gate | sec 5.3, sec 5.4 | Full | `approved`-state execution gate and deprecation/retirement handling are documented | Organization-specific override policy may vary | Keep lifecycle-state gating tests mandatory in Phase 2/3 | Phase 2+3 | `friday-agent` + `friday-runtime` |
| Skill approval-authority metadata enforcement | sec 5.4 | Partial | Registry lifecycle states and review metadata exist; explicit mandatory fields for `proposed -> approved` need dedicated gate coverage | Approval authority transitions need stricter conformance artifacts | Add approval-authority metadata validation suite and release artifact requirements | Phase 2+3 | `friday-agent` + governance owner |
| Skill tool-chain policy compatibility | sec 5.3 | Full | Skill invariants and tool-chain subset checks are defined in technical specs and tests | Tool taxonomy may expand over time | Keep tool-chain policy compatibility checks in Phase 2 gates | Phase 2 | `friday-agent` + `friday-runtime` |
| Skill lifecycle observability | sec 5.3, sec 11 | Full | Skill lifecycle states and required telemetry events are specified and mapped to evidence artifacts | Event field evolution may require versioned schema updates | Keep skill lifecycle event completeness checks in CI | Phase 2+3 | `friday-telemetry` + `friday-agent` |
| Skill delegation/handoff behavior | sec 5.3, sec 13 | Partial | Handoff semantics are specified and linked to Phase 3 workflow/delegation workstreams | Execution depth for dynamic skill routing is Phase 3 scoped | Complete advanced skill routing/delegation suites in Phase 3 | Phase 3 | `friday-agent/workflows` |
| HITL policy | sec 3 item 16, sec 10.1-10.8 | Full | Technical specs include HITL state machine/semantics and Phase 3 includes implementation workstream | KPI thresholds and operational runbook depth can be tightened | Keep HITL protocol as explicit Phase 3 gate | Phase 3 | `friday-agent` + `friday-runtime` |
| HITL authority model (who can approve what) | sec 10.3, sec 10.6 | Full | `HITLAuthorityPolicy` is now specified and Phase 3 includes authority enforcement work | Authority delegation policy templates may need org-specific variants | Validate authority scope coverage in Phase 3 tests | Phase 3 | `friday-agent/workflows` + governance owner |
| Artifact policy | sec 3 item 17, sec 8 | Full | `ArtifactPolicy` schema and Phase 3 artifact governance workstream are defined | Concrete package ownership finalization may still evolve | Keep artifact lifecycle/provenance as Phase 3 gate | Phase 3 | artifact/workspace layer |
| Logging policy | sec 3 item 18, sec 11 | Full | Observability event contract and completeness checks are now planned in Phase 2/3 | Event versioning and retention policy details can be expanded | Keep event-schema compliance in CI gates | Phase 2+3 | `friday-telemetry` |
| Failure policy | sec 3 item 19, sec 12 | Partial | `FailurePolicy` schema and generalized failure domains are specified with tests/workstreams | Domain-specific rollback/compensation runbook details still need package-level completion | Add domain runbooks and failure-threshold tuning in implementation | Phase 2+3 | `friday-agent` + `friday-runtime` |
| Core bounded execution rules | sec 4 | Full | Unified bounded-execution startup gate and required policy domains are specified in Phase 2 and technical specs | None material | Keep bounded-execution validation as required Phase 2 exit gate | Phase 2 | `friday-runtime` |
| Tool call audit trail | sec 5.2 | Full | Phase 2 observability event contract now includes tool-call event requirements | Per-tool custom fields may need later standardization | Keep tool-event schema tests in Phase 2 | Phase 2 | `friday-telemetry` + `friday-tools` |
| Code execution lifecycle | sec 6.1 | Full | Explicit execution lifecycle state model and stage-enforcement tests are now specified | None material | Keep lifecycle stage checks as required gate in Phase 2 | Phase 2 | `friday-tools` + `friday-runtime` |
| Sandbox requirements | sec 6.2 | Full | `SandboxPolicy` schema and Phase 2 enforcement workstream are defined | Sandbox profile presets may need environment-specific refinement | Keep privileged-exec escalation checks in Phase 2 tests | Phase 2 | `friday-tools` + `friday-runtime` |
| Execution result integrity | sec 6.3 | Full | Technical specs now define execution-result integrity requirements and Phase 2 includes integrity acceptance gates/tests | Hashing depth and artifact retention policy may need future refinement | Keep claim-to-output traceability tests as required gate | Phase 2 | `friday-agent` + `friday-telemetry` |
| Memory namespace + arbitration | sec 9 | Full | Detailed in design/spec/build plan | None material | Maintain and test against bypass matrix | Phase 2 | `friday-memory` |
| Metadata migration/backfill strategy | sec 9, sec 12 | Full | Technical specs and Phase 2 now define migration/backfill strategy and validation goals | Operational sizing/playbook detail can be expanded | Keep migration correctness and rollback readiness as Phase 2 exit gate | Phase 2 | `friday-memory` + runtime ops |
| Migration governance (`preflight`, `apply`, `rollback`) | sec 9.3, sec 12 | Partial | Migration/backfill exists, but preflight gating and checkpoint strictness need explicit evidence enforcement | Preflight-ready gate and rollback checkpoint artifacts need hard gating | Add migration governance suite and artifacts for preflight/apply/rollback | Phase 2+3 | `friday-memory` + runtime ops |
| HITL request/response payload contract | sec 10.6 | Full | HITL payload requirements are now specified and mapped to Phase 3 implementation | Payload versioning strategy may need extension | Validate payload compatibility via workflow/HITL tests | Phase 3 | `friday-agent/workflows` |
| HITL timeout/default behavior | sec 10.7 | Full | Technical specs define timeout/default semantics and Phase 3 includes implementation gates | Environment-specific timeout profiles may need additional tuning | Keep deterministic timeout tests as required gate | Phase 3 | `friday-runtime` + `friday-agent` |
| HITL metrics | sec 10.8 | Full | HITL KPI set and SLO defaults are included in plans/specs and test strategy | Threshold tuning may continue after pilot runs | Keep KPI thresholds as release gates | Phase 3 | `friday-telemetry` |
| Multi-agent coordination handoff | sec 13 | Full | Delegation/handoff payload contract and compatibility validation are now specified | None material | Keep handoff-schema verification in workflow gates | Phase 3 | `friday-agent` |
| Workflow/pipeline/task schema completeness | sec 13 | Full | Canonical workflow/pipeline/task schemas and dispatch semantics are now specified in technical specifications and Phase 3 workstreams | Implementation quality depends on deterministic enforcement and test rigor | Keep workflow cardinality and reference-integrity gates mandatory | Phase 3 | `friday-agent/workflows` + `friday-runtime` |
| Pipeline composition and typed handoff governance | sec 13, sec 14 | Full | Reusable pipeline composition and typed cross-pipeline contract expectations are now specified with lineage evidence requirements | Operational tuning still required for large-scale compositions | Keep typed handoff and lineage evidence mandatory in release gates | Phase 3 | `friday-agent/workflows` + `friday-telemetry` |
| Quality/evaluation KPIs | sec 14 | Partial | KPI gate framework and baseline targets are present | Agent-class specific thresholds still require calibration | Finalize per-agent-class numeric thresholds in operational baseline | Phase 3 | `tests/lab` + telemetry |
| Approval checklist enforcement | sec 16 | Full | Checklist-to-CI evidence mapping is explicit in specs/test strategy and phase plans | None material | Keep checklist artifact bundle mandatory at release checkpoint | Phase 2+3 | Program-level documentation owner |

---

## 4. Error, Omission, and Deficiency Summary

## 4.1 Errors

1. No material structural planning errors remain in the Alt document set after this pass.
2. Remaining issues are calibration-level (threshold tuning and runbook depth), not contract-shape omissions.

## 4.2 Omissions

1. Agent-class specific KPI threshold calibration remains to be finalized during implementation.
2. Authority-policy templates and remote-registry governance ownership models need final standardization for broader adoption.
3. Scratch pad default TTL/quota values need workload-specific calibration.
4. Deployment-profile defaults for filesystem roots and scratch backend selection need environment-class calibration.
5. Migration governance artifacts (`preflight`, `apply`, `rollback`) need strict release gating.
6. Skill approval-authority transition controls need final governance-owner assignment and policy ratification.

## 4.3 Other Deficiencies

1. Domain-specific failure/rollback runbooks still require package-level operational detail.
2. Ownership mapping is improved but should be enforced consistently in release-review templates.
3. KPI baselines are now present; calibration by workload class is the remaining precision gap.

## 4.4 Second-Pass Precision Findings

1. HITL protocol, authority model, and payload semantics are now represented in technical specifications and phase plans.
2. Contract-critical policy schemas are now represented in technical specifications.
3. Skill manifest repository semantics (filesystem-backed) and pinned-reference semantics are now represented across contract/spec/build docs.
4. Scratch pad scope/retention/promotion governance is now represented across contract/spec/build docs.
5. Remaining precision gap: per-agent KPI calibration, authority-policy template standardization, scratch default tuning, filesystem-profile default tuning, and Phase 3 skill/scratch orchestration depth.

---

## 5. Upgrade Plan to Align Build Planning with Agent Contract

## 5.1 Planning Artifacts Added

1. Keep this matrix as the top-level compliance tracker.
2. Added: `agent-contract-schema-spec.md` defining canonical schemas.
3. Added: `agent-contract-test-strategy.md` mapping requirements to test suites and CI gates.

## 5.2 Update Status Across Existing Alt Docs

1. Completed: `technical-specifications.md` now includes Agent Contract schemas, HITL lifecycle semantics, HITL authority rules, sandbox/tool policy models, contract-compliance tests, and migration/backfill strategy.
2. Completed: Phase 2 build baseline (archived) now includes tooling/sandbox governance, contract schema validation, metadata migration/backfill, observability event contract, and expanded contract-linked exit gates.
3. Completed: `phase-3-build-plan.md` now includes HITL protocol/authority, artifact governance, and contract compliance gate workstreams.
4. Completed: `phase-3-transition-plan.md` now includes contract-governance prerequisites and additional phase-exit requirements.
5. Completed: `README.md` now clarifies `phase-1-build-plan.md` as historical baseline and indexes the compliance matrix.
6. Remaining precision work: per-agent KPI calibration, authority-policy/registry template standardization, scratch default tuning, filesystem-profile default tuning, migration-governance gate hardening, and package-level failure runbook depth.

## 5.3 Concrete New Workstreams

### Workstream A (Phase 2): Contract Schema and Runtime Validation

1. Implement schema definitions and contract parser/validator.
2. Enforce required fields at agent registration/load time.
3. Add tests for contract invalidation behavior.

### Workstream B (Phase 2): Tool and Sandbox Governance

1. Implement allowlist/approval/rate policy contracts.
2. Implement sandbox policy contract and privileged-exec escalation gate.
3. Add deterministic tests for blocked/approved execution paths.

### Workstream C (Phase 2): Observability Event Contract

1. Define mandatory event fields for tools, sandbox execution, guardrails, and failures.
2. Add log-completeness validation tests.

### Workstream D (Phase 3): HITL Protocol Execution Model

1. Implement request/response payload schema.
2. Implement `awaiting_human` state transitions, timeout defaults, resume/reject/cancel handling.
3. Add deterministic replay and audit tests.

### Workstream E (Phase 3): Artifact Governance

1. Define artifact lifecycle states and provenance fields.
2. Enforce publication approval gates where configured.
3. Add artifact policy compliance tests.

### Workstream F (Phase 2): Metadata Migration and Backfill

1. Define migration strategy for legacy records lacking multi-agent metadata fields.
2. Add compatibility validation checks and rollback criteria.
3. Add data-integrity and query-correctness tests across migrated/unmigrated datasets.

### Workstream G (Phase 2+3): Skill Contract and Orchestration Governance

1. Implement `SkillRef` pinning and skill manifest/registry validation with tool-chain compatibility checks.
2. Add skill lifecycle observability requirements and CI evidence artifacts.
3. Complete advanced skill routing/delegation behavior and replay-grade validation in Phase 3.
4. Define local-to-federated registry extension governance without changing contract reference format.
5. Add mandatory canonical `SKILL.md` conformance gates using AgentSkills reference validator (`skills-ref validate`) at pre-approval and release checkpoints.
6. Add CI checks for canonical skill schema/frontmatter validity, directory/layout conformance, and deterministic `SKILL.md -> manifest/registry` mapping.
7. Require validator/CI outputs in release evidence bundles.
8. Add skill runtime-profile composition gates with no-expansion assertions and impact-class approval enforcement.

### Workstream H (Phase 2+3): Scratch Pad Governance and Orchestration

1. Implement scratch pad schema/policy with scope isolation and TTL/quota enforcement.
2. Add scratch lifecycle event requirements and CI evidence artifacts.
3. Integrate scratch plan/task/event updates with workflow and HITL state transitions in Phase 3.

### Workstream I (Phase 2+3): Filesystem Topology and Path Governance

1. Implement and validate runtime filesystem-root model (`install_root`, `runtime_data_root`, `workspace_root`, optional `cache_root`).
2. Enforce scratch persisted-path placement under `runtime_data_root` (workspace disallowed except test fixtures).
3. Add deployment-profile templates (local/container/cloud) and conformance tests.
4. Add release evidence artifact for filesystem layout compliance.

### Workstream J (Phase 2+3): Arbitrator Identity and Capability Hardening

1. Implement shared-write anti-spoof model requiring identity + runtime-issued capability.
2. Enforce capability scope/TTL validation at all shared-write boundaries.
3. Add capability replay/spoof rejection tests and mandatory evidence artifacts.

### Workstream K (Phase 2+3): Migration Governance Hardening

1. Implement mandatory migration preflight gating before apply.
2. Enforce rollback checkpoint requirement and integrity-validation gates.
3. Add mandatory preflight/apply/rollback artifacts to release evidence requirements.

### Workstream L (Phase 2+3): Skill Approval-Authority Governance

1. Enforce required authority metadata for `proposed -> approved` transitions.
2. Add approver-authority validation and immutable review-history checks.
3. Add dedicated skill-approval authority evidence artifact to release gates.

### Workstream M (Phase 3): Workflow, Pipeline, and Task Contract Hardening

1. Add canonical pipeline/task schema contracts and DAG validation rules.
2. Add deterministic dispatch/assignment/lease-recovery behavior requirements.
3. Add typed cross-pipeline handoff contract validation and lineage evidence requirements.

---

## 6. Exit Gates (Contract-Aligned)

## 6.1 Phase 2 Exit Gate Additions

1. Agent contract schema validation implemented for core required fields.
2. Tool/sandbox policy enforcement implemented for high-impact operations.
3. Logging event contract implemented for tool/sandbox/guardrail/failure events.
4. Existing backward compatibility gates remain green (`single_agent`, `friday.py` unchanged by default).
5. Filesystem-backed skill manifest repository and pinned-reference validation gates are green when skills are declared.
6. Scratch pad policy/scope/retention/promotion validation gates are green when scratch pad is enabled.
7. Filesystem-topology and scratch-placement validation gates are green.
8. Shared-write anti-spoof (identity+capability) gates are green.
9. Migration preflight/apply/rollback governance gates are green.
10. Skill approval-authority metadata gates are green.
11. Canonical `SKILL.md` validator and schema/layout/mapping CI gates are green when skills are declared.
12. Skill runtime-profile composition and no-expansion gates are green when skills are declared.

## 6.2 Phase 3 Exit Gate Additions

1. HITL protocol fully implemented with timeout/default behavior and auditability.
2. Workflow escalation integrates with HITL state machine deterministically.
3. Artifact governance lifecycle and approval controls implemented.
4. Contract KPI reporting included in verification gates.
5. HITL authority policy is implemented and validated for approval scope correctness.
6. Skill routing/delegation and registry-extension compatibility evidence are included in release gates.
7. Scratch orchestration/workflow integration and replay correlation evidence are included in release gates.
8. Filesystem-topology conformance evidence is included for local/container/cloud deployment profiles.
9. Shared-write anti-spoof enforcement remains green in orchestrated multi-agent suites.
10. Migration governance artifacts (`preflight`, `apply`, `rollback`) are required in release evidence.
11. Skill approval-authority transition evidence is required in release evidence.
12. Canonical skill conformance evidence (`skills-ref` + schema/layout/mapping reports) is required in release evidence.
13. Workflow/pipeline/task schema and dispatch evidence is required in release evidence.
14. Cross-pipeline typed handoff and lineage evidence is required in release evidence.
15. Skill runtime-profile composition evidence (`policy-diff`, impact class, no-expansion assertions) is required in release evidence.

---

## 7. Ownership and Sequence Recommendation

| Sequence | Deliverable | Owner | Dependency |
| :--- | :--- | :--- | :--- |
| 1 | Contract schema spec + validator | `friday-core` + `friday-agent` | None |
| 2 | Tool/sandbox governance | `friday-tools` + `friday-runtime` | 1 |
| 3 | Observability event contract | `friday-telemetry` | 1, 2 |
| 4 | HITL protocol implementation | `friday-agent/workflows` + `friday-runtime` | 1, 3 |
| 5 | Artifact governance | workspace/artifact layer | 1, 4 |
| 6 | Metadata migration/backfill readiness | `friday-memory` + runtime ops | 1, 2 |
| 7 | Skill contract/manifest/registry governance | `friday-agent` + `friday-runtime` | 1, 2, 3 |
| 8 | Scratch pad governance and observability | `friday-memory` + `friday-telemetry` | 1, 3 |
| 9 | Filesystem topology and path governance | `friday-runtime` + ops owner | 1, 2, 3 |
| 10 | Arbitrator identity/capability hardening | `friday-runtime` + `friday-memory` | 1, 2, 3 |
| 11 | Migration governance hardening | `friday-memory` + runtime ops | 1, 2, 3 |
| 12 | Skill approval-authority governance | `friday-agent` + governance owner | 1, 2, 3 |
| 13 | Workflow/pipeline/task contract hardening | `friday-agent/workflows` + `friday-runtime` | 1, 3, 4 |
| 14 | Contract compliance CI gate | `tests/lab` + docs owner | 1-13 |

---

## 8. Recommended Immediate Next Actions

1. Approve this matrix as the canonical compliance baseline.
2. Finalize concrete KPI/SLO numeric thresholds for HITL latency, timeout rate, and event completeness.
3. Add CI artifact mapping for contract checklist evidence at release checkpoints.
4. Standardize authority-policy templates and governance-owner assignments for approver scopes.
5. Ratify governance owners for skill approval-authority transitions and migration preflight sign-off.
