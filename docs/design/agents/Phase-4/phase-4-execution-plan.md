# Phase 4 Execution Plan (AI-Executable Subphases)

**Status:** Proposed for Approval  
**Date:** 2026-02-20  
**Source Plan:** `docs/design/agents/Phase-4/phase-4-build-plan.md`  
**Companion Inputs:**  
- `docs/design/agents/Phase-4/phase-4-build-plan-examples.md`  
- `docs/design/agents/Phase-4/phase-4-ai-agent-implementation-guide.md`  
**Purpose:** Decompose Phase 4 into bounded, low-context subphases that an AI implementation agent can execute continuously with deterministic validation and minimal architectural drift.
**Role:** Historical and canonical full-sequence execution reference retained for traceability.  
**Active Execution:** Use `docs/design/agents/Phase-4/phase-4-a-execution-plan.md` and `docs/design/agents/Phase-4/phase-4-b-execution-plan.md` for implementation runs.

Execution slicing companions (for lower-context implementation runs):

1. `docs/design/agents/Phase-4/phase-4-a-execution-plan.md`
2. `docs/design/agents/Phase-4/phase-4-b-execution-plan.md`

---

## 1. Execution Model

This execution plan is workflow-managed and context-preserving by design.

Execution rules:

1. One subphase executes at a time.
2. Every subphase has explicit inputs, outputs, dependencies, and gate checks.
3. Subphase completion is evidence-based, not narrative-based.
4. No subphase may violate non-negotiable constraints from the Phase 4 build plan.
5. Build-plan contracts are normative; companion docs are advisory and must remain coherent with the build plan.

Non-negotiable constraints carried forward:

1. YAML-first config is canonical; env override is globally gated by `allow_env_override`.
2. Unknown-key policy is hard-fail for runtime/agent/workflow/pipeline/task YAML.
3. `llm_pool` and per-agent `llm_service` binding are mandatory contracts.
4. Canonical execution hierarchy is `workflow -> pipeline -> task`.
5. Legacy workflow support is adapter-only and controlled by `config_policy.workflow_mode`.
6. `owner_role` resolution is allowed only through `agents.role_bindings`.
7. Artifacts are first-class and YAML-configured via runtime/workflow/pipeline/task contracts.
8. Runtime workflow paths must resolve agents through generic typed factory mapping, not concrete interactive/copilot class binding.
9. Workflow-selected ownership governs execution-time behavior via the selected owner profile and `agent_type`.
10. `InteractiveAgent` is the direct-runtime default; workflow dispatch must remain implementation-type-neutral.
11. Copilot naming/runtime convenience APIs are compatibility-only in Phase 4 and removed in Phase 5.

---

## 2. Context-Preservation Protocol

Every subphase MUST publish to `docs/design/agents/Phase-4/subphase-artifacts/phase-4/subphase-<n>/`:

1. `subphase-summary.md`
   - completed scope,
   - decisions made,
   - unresolved risks,
   - changed files.
2. `verification-summary.md`
   - full gate results,
   - targeted test results,
   - blocked checks and rationale.
3. `next-subphase-brief.md`
   - assumptions carried forward,
   - required inputs,
   - blockers and dependency notes.

Minimum gate cadence:

1. Run targeted gates for touched contracts before merge in each subphase.
2. Run full gate set after every subphase.
3. Record baseline debt separately from subphase regressions.
4. Do not proceed if a new regression is introduced.

Standard full gate command set:

1. `uv run pytest`
2. `uv run pytest tests/integration`
3. `uv run ruff check .`
4. `uv run mypy packages tests main.py`

---

## 3. Subphase Breakdown

## Subphase 0: Phase 4 Baseline Lock and Contract Handshake

**Goal:** Lock Phase 4 constraints, acceptance criteria, and execution assumptions before implementation.

Primary sources:

1. `phase-4-build-plan.md` sections 1, 2, 3, 4, 14, 15.2.
2. `phase-4-build-plan-examples.md` sections 2, 7, 8.
3. `phase-4-ai-agent-implementation-guide.md` sections 2, 5, 6.

Execution scope:

1. Confirm no open architectural decisions remain in Phase 4 contracts.
2. Confirm acceptance-criteria traceability matrix coverage is intact.
3. Confirm unknown-key scope and task-field typing contracts are frozen for implementation.
4. Classify current repo debt into:
   - blocking debt (must close before Subphase 1),
   - waiver-eligible debt (proceed with owner and mitigation date).

Deliverables:

1. Phase 4 baseline constraint matrix.
2. Acceptance-criteria readiness checklist.
3. Subphase artifact triad.

Exit criteria:

1. No unresolved ambiguity in Phase 4 contracts.
2. Debt classification is explicit with owner and mitigation timeline.

---

## Subphase 1: Runtime YAML Foundation and Dual-Source Policy

**Goal:** Implement and verify YAML-first runtime config contracts and merge behavior.

Primary sources:

1. `phase-4-build-plan.md` Workstream A, sections 6.1, 8, 11.1.
2. `phase-4-build-plan.md` section 10 (dual-source patch carry-forward).
3. `phase-4-build-plan-examples.md` section 3.

Execution scope:

1. Implement nested runtime YAML parsing.
2. Implement deterministic source precedence and provenance capture.
3. Enforce `allow_env_override` global behavior.
4. Enforce unknown-key hard-fail behavior.
5. Implement runtime `artifacts` policy parsing and validation.

Deliverables:

1. Runtime config parser/merge implementation checklist.
2. Runtime config validation tests (success/failure paths).
3. Subphase artifact triad.

Exit criteria:

1. YAML-only, env-only, and mixed-source policy behavior is deterministic and tested.

---

## Subphase 2: LLM Service Pool and Agent Binding Contracts

**Goal:** Deliver runtime LLM pool and strict agent-to-service binding behavior.

Primary sources:

1. `phase-4-build-plan.md` Workstream B and C, sections 6.2 and 6.3.
2. `phase-4-build-plan.md` sections 8 and 11.2.
3. `phase-4-build-plan-examples.md` sections 3, 4.1, and 5.2.

Execution scope:

1. Build runtime-managed `llm_pool` with per-service resilience policy.
2. Validate `default_service` and fail fast on invalid references.
3. Enforce strict/non-strict `llm_service` behavior for agent profiles.
4. Enforce startup-time rejection of unresolved service bindings.

Deliverables:

1. LLM pool resolver and validation checklist.
2. Agent binding conformance tests.
3. Subphase artifact triad.

Exit criteria:

1. Multi-service runtime resolves deterministically and invalid bindings fail preflight/startup.

---

## Subphase 3: Agent Abstraction and Runtime Factory Decoupling

**Goal:** Decouple runtime workflow execution from concrete interactive/copilot agent classes and lock abstraction boundaries.

Primary sources:

1. `phase-4-build-plan.md` Workstream D, section 6.8, section 7 (Feature 5), and section 11.3.
2. `phase-4-build-plan.md` sections 3 and 14 (agent abstraction acceptance criteria).
3. `phase-4-build-plan-examples.md` sections 4.1, 4.2, and 8.

Execution scope:

1. Establish and validate `AgentBase -> ReplAgentBase -> InteractiveAgent` hierarchy responsibilities.
2. Ensure runtime workflow execution paths resolve through generic typed factory mapping.
3. Ensure workflow-selected owner resolution drives execution behavior through selected profile `agent_type`.
4. Preserve direct-runtime interactive convenience path while keeping workflow dispatch type-neutral.
5. Document and validate compatibility aliases (`CopilotAgent`, `get_copilot_agent()`) with Phase 5 removal target.

Deliverables:

1. Agent abstraction/factory decoupling implementation checklist.
2. Targeted abstraction and compatibility conformance tests.
3. Subphase artifact triad.

Exit criteria:

1. No canonical workflow execution path instantiates concrete interactive/copilot agent classes directly.
2. Compatibility alias behavior is explicit, tested, and time-bounded.

---

## Subphase 4: Canonical Workflow/Pipeline/Task Dispatch Core

**Goal:** Make canonical hierarchical dispatch the default executable path.

Primary sources:

1. `phase-4-build-plan.md` Workstream E, sections 6.4 and 11.4.
2. `phase-4-build-plan.md` section 6.6 (task field typing).
3. `phase-4-build-plan-examples.md` sections 4.2, 4.3, 5.3, 5.4, 5.5.

Execution scope:

1. Route workflow execution through canonical pipeline dispatch path.
2. Validate workflow/pipeline/task reference integrity and dependency graph behavior.
3. Enforce deterministic assignment, claim, start, heartbeat, completion, failure, and cancellation transitions.
4. Enforce task field typing expectations, including canonical integer `retry_policy.max_attempts`.

Deliverables:

1. Canonical dispatch implementation checklist.
2. Dispatch lifecycle test coverage.
3. Subphase artifact triad.

Exit criteria:

1. Canonical workflow path is default, deterministic, and test-complete.

---

## Subphase 5: Owner Resolution and Assignment Governance

**Goal:** Enforce deterministic ownership selection and claim governance.

Primary sources:

1. `phase-4-build-plan.md` Workstream G, sections 6.4 and 11.5.
2. `phase-4-build-plan-examples.md` sections 5.1, 5.6, 7, 8.

Execution scope:

1. Resolve `owner_agent_id` directly.
2. Resolve `owner_role` only via `agents.role_bindings`.
3. Reject missing/ambiguous/unknown role mappings deterministically.
4. Enforce claimant mismatch rejection and assignment audit evidence.

Deliverables:

1. Owner-resolution policy implementation checklist.
2. Assignment-governance failure-path test suite.
3. Subphase artifact triad.

Exit criteria:

1. No task can be claimed or started without a concrete validated owner.

---

## Subphase 6: Artifact YAML Contracts and Output Binding

**Goal:** Implement first-class artifact configuration and publication across runtime/workflow/pipeline/task.

Primary sources:

1. `phase-4-build-plan.md` Workstream J, sections 6.5, 8, and 11.11.
2. `phase-4-build-plan.md` canonical YAML examples section 15.1.
3. `phase-4-build-plan-examples.md` sections 3, 4, 5, 7, and 8.

Execution scope:

1. Enforce runtime `artifacts` policy contract.
2. Validate workflow `required_artifacts` definitions.
3. Validate pipeline `artifact_contract.produced/consumed` contracts.
4. Validate task `output_artifacts` and `from_output -> output_contract` mapping.
5. Publish artifact metadata and fail deterministically when required artifacts are missing.

Deliverables:

1. Artifact contract enforcement implementation checklist.
2. Artifact output-binding and completion-validation tests.
3. Subphase artifact triad.

Exit criteria:

1. Artifact publication is deterministic, contract-validated, and evidence-emitting.

---

## Subphase 7: Legacy Workflow Adapter and Routing Governance

**Goal:** Preserve compatibility through explicit adapter routing and migration signals.

Primary sources:

1. `phase-4-build-plan.md` Workstream F, section 6.7, sections 11.7 and 12.
2. `phase-4-build-plan-examples.md` section 6.

Execution scope:

1. Implement legacy-to-canonical translation for supported schemas.
2. Route legacy workloads through the explicit adapter path into canonical workflow execution.
3. Emit compatibility warnings and migration metadata.
4. Emit `workflow_mode_selected` audit events when runtime resolves `config_policy.workflow_mode` (`canonical|legacy|auto`).
5. Document unsupported legacy constructs with deterministic errors.

Deliverables:

1. Adapter translation matrix and routing checklist.
2. Compatibility tests and warning/audit evidence.
3. Subphase artifact triad.

Exit criteria:

1. Legacy workloads execute through explicit adapter path with auditable migration signals.

---

## Subphase 8: Observability, Lineage, and Compliance Evidence

**Goal:** Emit operations-grade telemetry for policy, lineage, and release evidence.

Primary sources:

1. `phase-4-build-plan.md` Workstream H, sections 7 (Feature 9) and 11.8.
2. `phase-4-build-plan.md` sections 6.4, 6.5, 11.6, and 11.11.
3. `phase-4-build-plan-examples.md` section 7.

Execution scope:

1. Emit workflow/pipeline/task/assignment identity metadata.
2. Emit `llm_service`, model, provider attribution.
3. Emit typed handoff lineage records and `workflow_typed_handoff_validated` evidence.
4. Emit artifact publication metadata (`artifact_id`, type, producer task, pipeline, workflow) through explicit `workflow_artifact_published` evidence.
5. Emit compatibility mode and migration metadata when adapter path is used, including `workflow_mode_selected`.
6. Emit canonical engine telemetry events for workflow, pipeline, and task lifecycle:
   - `workflow_execution_started|completed|failed`
   - `pipeline_execution_started|completed|failed|blocked`
   - `workflow_task_started|completed|failed`

Deliverables:

1. Observability field-completeness checklist.
2. Lineage and artifact publication evidence tests.
3. Subphase artifact triad.

Exit criteria:

1. Required gate evidence can prove deterministic execution and policy compliance.

---

## Subphase 9: Documentation and Companion Coherence Sweep

**Goal:** Ensure all Phase 4 docs remain consistent with implemented behavior.

Primary sources:

1. `phase-4-build-plan.md` Workstream I, sections 15.1 and 15.2.
2. `phase-4-build-plan-examples.md` full document.
3. `phase-4-ai-agent-implementation-guide.md` full document.

Execution scope:

1. Align runtime/workflow/pipeline/task/artifact contracts across all Phase 4 docs.
2. Validate acceptance-criteria traceability matrix references.
3. Ensure examples stay canonical with current parser/runtime behavior.
4. Ensure advisory AI guide remains subordinate and coherent with build-plan norms.

Deliverables:

1. Cross-doc coherence checklist.
2. Updated traceability and reviewer notes.
3. Subphase artifact triad.

Exit criteria:

1. No contradictions remain across Phase 4 documentation set.

---

## Subphase 10: Phase 4 Closeout Gates and Release Evidence Bundle

**Goal:** Finalize phase gates and publish closeout evidence package.

Primary sources:

1. `phase-4-build-plan.md` sections 11, 12, 13, and 14.
2. `phase-4-build-plan.md` section 15.2.

Execution scope:

1. Run full repository gate commands.
2. Validate acceptance criteria 1-21 with explicit evidence links.
3. Publish phase-level release evidence bundle and unresolved-risk register.
4. Execute rollback-readiness verification for `workflow_mode=legacy`.

Deliverables:

1. Final Phase 4 evidence bundle index.
2. Acceptance-criteria closeout report.
3. Rollback readiness note.
4. Subphase artifact triad.

Exit criteria:

1. All Phase 4 acceptance criteria are evidenced and no blocking risks remain open.

---

## 4. Mapping Back to Phase 4 Workstreams

| Execution Subphase | Phase 4 Build Workstream Coverage |
| :--- | :--- |
| Subphase 0 | Preconditions + constraints + acceptance-trace lock |
| Subphase 1 | Workstream A |
| Subphase 2 | Workstream B, Workstream C |
| Subphase 3 | Workstream D |
| Subphase 4 | Workstream E (+ section 6.6 task typing enforcement) |
| Subphase 5 | Workstream G |
| Subphase 6 | Workstream J |
| Subphase 7 | Workstream F |
| Subphase 8 | Workstream H |
| Subphase 9 | Workstream I |
| Subphase 10 | Phase-level gate closure and release evidence rollup |

---

## 5. Cross-Document Validation Matrix (Phase-4 Set)

This execution plan was validated for consistency against the current Phase-4 documentation set and declared upstream dependencies.

| Document | Required Signal | Preservation in Phase 4 Execution Plan |
| :--- | :--- | :--- |
| `phase-4-build-plan.md` | Workstreams A-J, acceptance criteria, gates | Subphases 1-10 map to workstreams and closeout gates |
| `phase-4-build-plan-examples.md` | Canonical YAML examples and failure conditions | Subphases 1-9 reference example-backed validation and failure paths |
| `phase-4-ai-agent-implementation-guide.md` (advisory) | Implementation order, deterministic failures, evidence expectations | Subphase sequence and gate evidence align to advisory guidance |
| `Alt-Phase-2/technical-specifications.md` | Canonical runtime/workflow invariants | Subphases 0-5 enforce hierarchy, factory, and dispatch invariants |
| `Alt-Phase-2/phase-3-build-plan.md` | Phase 3 compatibility commitments | Subphase 0 and Subphase 7 preserve transitional guarantees |
| `Alt-Phase-2/phase-3-transition-plan.md` | Migration and rollback continuity | Subphase 7 and Subphase 10 include routing and rollback evidence |

Validation conclusion:

1. No contradictions detected with current Phase 4 contracts.
2. All Phase 4 workstreams are represented with executable boundaries.
3. Artifact YAML contracts are explicitly integrated into execution sequencing.
4. Agent abstraction/runtime-factory decoupling is explicitly sequenced before canonical dispatch implementation.

---

## 6. Risk Assessment for Executing This Decomposed Phase 4 Plan

## 6.1 Overall Risk Posture

1. Feasibility: High
2. Coordination Risk: Medium-High
3. Contract Drift Risk: Medium
4. Compatibility Regression Risk (legacy and single-agent path): Medium

## 6.2 Primary Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Runtime config/contract drift across docs and code | Medium | High | Subphase 0 lock + Subphase 9 coherence sweep + AC traceability matrix |
| LLM binding failures introduced late in pipeline work | Medium | High | Subphase 2 hard-fail tests before dispatch changes |
| Agent abstraction/runtime-factory coupling remains in workflow path | Medium | High | Dedicated Subphase 3 abstraction conformance and factory-path checks before canonical dispatch changes |
| Artifact wiring incomplete across workflow/pipeline/task layers | Medium | High | Dedicated Subphase 6 with deterministic failure-path coverage |
| Legacy adapter path divergence from canonical path | Medium | High | Subphase 7 routing tests + migration metadata evidence |
| Observability evidence insufficient for release gates | Medium | High | Subphase 8 evidence completeness checklist before closeout |
| Final gate failures create rollback ambiguity | Medium | High | Subphase 10 rollback readiness validation against `workflow_mode=legacy` |

## 6.3 Phase Gates (Must Pass)

1. Gate A (after Subphase 0): Baseline constraints and acceptance traceability locked.
2. Gate B (after Subphase 3): Runtime config + LLM pool + agent binding + abstraction/factory contracts deterministic.
3. Gate C (after Subphase 6): Canonical dispatch + owner resolution + artifact contracts deterministic.
4. Gate D (after Subphase 8): Legacy routing and observability evidence complete.
5. Gate E (after Subphase 10): All Phase 4 acceptance criteria are evidenced and approved.

---

## 7. AI-Agent Assignment Pattern (Recommended)

For each subphase, keep ownership bounded:

1. Contract owner: schema/policy invariants.
2. Runtime owner: orchestration and execution semantics.
3. Verification owner: tests, evidence, and gate reporting.
4. Documentation owner: examples, advisory guide coherence, and traceability updates.

Handoff order per subphase:

1. Contract owner publishes `subphase-summary.md`.
2. Runtime owner updates implementation and validates constraints.
3. Verification owner publishes `verification-summary.md`.
4. Documentation owner publishes `next-subphase-brief.md` with carry-forward assumptions.

---

## 8. Assumptions and Locked Defaults

Assumptions used:

1. Phase 4 build plan remains the normative contract baseline.
2. Companion Phase-4 docs remain synchronized as implementation progresses.
3. Existing Phase 3 compatibility guarantees remain in effect unless explicitly superseded in Phase 4.

Locked defaults:

1. Canonical workflow execution mode remains `config_policy.workflow_mode=canonical`.
2. Unknown-key handling remains hard-fail with no warn-only mode.
3. Canonical YAML examples use integer `retry_policy.max_attempts`.
4. Artifact contracts are required for release-grade workflow outputs.
5. Subphase artifacts are stored under `docs/design/agents/Phase-4/subphase-artifacts/phase-4/`.
6. Gate E closeout does not require a fixed named approver roster.
7. Workflow execution paths remain generic-factory-driven and do not bind concrete interactive/copilot classes directly.
8. Copilot compatibility aliases are accepted only for Phase 4 and tracked for Phase 5 removal readiness.

---
