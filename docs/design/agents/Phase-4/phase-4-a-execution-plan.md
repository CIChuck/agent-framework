# Phase 4-A Execution Plan (Foundation Track)

**Status:** Proposed for Approval  
**Date:** 2026-03-01  
**Source Plan:** `docs/design/agents/Phase-4/phase-4-build-plan.md`  
**Derived From:** `docs/design/agents/Phase-4/phase-4-execution-plan.md`  
**Purpose:** Execute the Phase 4 foundation slice with bounded context for AI implementation agents.

---

## 1. Scope and Boundaries

Phase 4-A implements the platform foundation required before canonical workflow delivery work begins.

In-scope workstreams:

1. Workstream A: Runtime Config Dual-Source Foundation
2. Workstream B: LLM Service Pool in Runtime DI
3. Workstream C: Agent Runtime Binding Model
4. Workstream D: Agent Abstraction and Runtime Factory Decoupling

Acceptance criteria primarily covered:

1. AC 1-6
2. AC 18-21

Secondary regression guardrails observed and reported in handoff:

1. AC 11
2. AC 14
3. AC 15
4. AC 17

Out of scope (deferred to Phase 4-B):

1. Canonical workflow/pipeline/task dispatch implementation
2. Owner resolution governance
3. Workflow/pipeline/task artifact contract enforcement, including `required_artifacts`, `artifact_contract`, and `output_artifacts` validation and dispatch-time enforcement
4. Legacy adapter routing, observability evidence rollup, and final phase closeout

---

## 2. Execution Model

Execution rules:

1. One subphase executes at a time.
2. Subphase completion requires explicit evidence artifacts.
3. No subphase may violate locked contracts in `phase-4-build-plan.md`.
4. Unknown-key hard-fail policy remains enforced; foundation work must not regress runtime/agent/workflow YAML validation behavior.
5. Workflow execution paths must remain generic-factory-driven and must not bind concrete copilot/interactive classes directly.

Subphase artifact location:

1. `docs/design/agents/Phase-4/subphase-artifacts/phase-4-a/subphase-a-<n>/`

Required artifact set per subphase:

1. `subphase-summary.md`
2. `verification-summary.md`
3. `next-subphase-brief.md`

Standard gates:

1. `uv run pytest`
2. `uv run pytest tests/integration`
3. `uv run ruff check .`
4. `uv run mypy packages tests main.py`

For this plan, the full Phase 4 companion set means:

1. `docs/design/agents/Phase-4/phase-4-build-plan.md`
2. `docs/design/agents/Phase-4/phase-4-execution-plan.md`
3. `docs/design/agents/Phase-4/phase-4-a-execution-plan.md`
4. `docs/design/agents/Phase-4/phase-4-b-execution-plan.md`
5. `docs/design/agents/Phase-4/phase-4-build-plan-examples.md`
6. `docs/design/agents/Phase-4/phase-4-ai-agent-implementation-guide.md`
7. `docs/design/agents/Phase-4/phase-4-executive-overview.md`

---

## 3. Subphase Breakdown

## Subphase A0: Baseline Lock and Contract Handshake

Goal:

1. Freeze implementation assumptions and acceptance traceability for the foundation slice.

Target files:

1. `docs/design/agents/Phase-4/phase-4-a-execution-plan.md`
2. `docs/design/agents/Phase-4/phase-4-build-plan.md`
3. `docs/design/agents/Phase-4/phase-4-execution-plan.md`
4. `docs/design/agents/Phase-4/phase-4-b-execution-plan.md`
5. `docs/design/agents/Phase-4/phase-4-build-plan-examples.md`
6. `docs/design/agents/Phase-4/phase-4-ai-agent-implementation-guide.md`
7. `docs/design/agents/Phase-4/phase-4-executive-overview.md`

Execution scope:

1. Confirm locked decisions for config precedence, LLM bindings, and agent abstraction hierarchy.
2. Confirm Workstreams A-D dependency order.
3. Verify the full Phase 4 companion set remains coherent for foundation-scope contracts across the build plan, historical execution plan, split execution plans, examples, AI guide, and executive overview.
4. Classify blocking debt versus waiver-eligible debt for foundation implementation, including whether any document drift must be corrected before A1 or can be carried forward explicitly.

Required checks:

1. Verify AC mapping table in this document covers AC 1-6 and 18-21 without gaps.
2. Verify 4-A/4-B dependency boundaries have no contradictory statements.
3. Verify the full Phase 4 companion set contains no contradictory Workstream A-D guidance.

Exit criteria:

1. No unresolved architectural ambiguity remains for Workstreams A-D.

---

## Subphase A1: Runtime YAML Foundation (Workstream A)

Goal:

1. Deliver deterministic runtime config loading and validation behavior.

Target files:

1. `packages/friday-runtime/src/friday_runtime/config.py`
2. `packages/friday-runtime/tests_runtime/test_config.py`

Execution scope:

1. Implement nested YAML parsing and deterministic precedence.
2. Enforce `allow_env_override` and unknown-key hard-fail behavior.
3. Parse and validate runtime-level `artifacts` policy fields, defaults, and path constraints.
4. Do not implement workflow/pipeline/task artifact contract parsing or enforcement in this subphase.

Required checks:

1. `uv run pytest packages/friday-runtime/tests_runtime/test_config.py`
2. `uv run ruff check packages/friday-runtime/src/friday_runtime/config.py packages/friday-runtime/tests_runtime/test_config.py`
3. `uv run mypy packages/friday-runtime/src/friday_runtime/config.py`

Exit criteria:

1. YAML-only, env-only, and mixed-source behavior is deterministic and tested.

---

## Subphase A2: LLM Pool and Agent Binding (Workstreams B-C)

Goal:

1. Deliver runtime LLM service pool and strict agent binding contracts.

Target files:

1. `packages/friday-runtime/src/friday_runtime/di.py`
2. `packages/friday-runtime/src/friday_runtime/kernel.py`
3. `packages/friday-runtime/tests_runtime/test_di.py`
4. `packages/friday-agent/src/friday_agent/profile.py`
5. `packages/friday-agent/src/friday_agent/loader.py`
6. `packages/friday-agent/src/friday_agent/registry.py`
7. `packages/friday-agent/tests_agent/test_loader.py`

Execution scope:

1. Implement named `llm_pool` with per-service resilience.
2. Enforce strict/non-strict `llm_service` behavior.
3. Fail preflight/startup on unresolved service references.
4. Preserve compatibility with profile `agent_type` field while deferring ownership of factory-mapping enforcement to Subphase A3.

Required checks:

1. `uv run pytest packages/friday-runtime/tests_runtime/test_di.py`
2. `uv run pytest packages/friday-agent/tests_agent/test_loader.py`
3. `uv run ruff check packages/friday-runtime/src/friday_runtime/di.py packages/friday-runtime/src/friday_runtime/kernel.py packages/friday-agent/src/friday_agent/profile.py packages/friday-agent/src/friday_agent/loader.py packages/friday-agent/src/friday_agent/registry.py`
4. `uv run mypy packages/friday-runtime/src/friday_runtime/di.py packages/friday-runtime/src/friday_runtime/kernel.py packages/friday-agent/src/friday_agent/profile.py packages/friday-agent/src/friday_agent/loader.py packages/friday-agent/src/friday_agent/registry.py`

Exit criteria:

1. Runtime resolves configured services deterministically and rejects invalid bindings before dispatch.

---

## Subphase A3: Agent Abstraction and Factory Decoupling (Workstream D)

Goal:

1. Decouple workflow execution from concrete copilot/interactive binding.

Target files (expected additions or modifications):

1. `packages/friday-agent/src/friday_agent/base.py`
2. `packages/friday-agent/src/friday_agent/repl_base.py`
3. `packages/friday-agent/src/friday_agent/interactive.py`
4. `packages/friday-agent/src/friday_agent/profile.py`
5. `packages/friday-runtime/src/friday_runtime/kernel.py`
6. `packages/friday-runtime/tests_runtime/test_kernel.py`
7. `packages/friday-agent/tests_agent/test_base.py`
8. `packages/friday-agent/tests_agent/test_orchestrator.py`

Execution scope:

1. Lock hierarchy responsibilities: `AgentBase -> ReplAgentBase -> InteractiveAgent`.
2. Ensure runtime workflow paths instantiate via generic typed factory mapping.
3. Own and enforce profile-level `agent_type` contract semantics for runtime factory mapping.
4. Validate factory contract hooks for workflow-selected owner execution; full owner-resolution enforcement remains in Phase 4-B (Subphase B2).
5. Keep compatibility aliases for Phase 4 with explicit Phase 5 removal policy.
6. Do not implement canonical `workflow -> pipeline -> task` dispatch behavior, lifecycle transition enforcement, or workflow routing behavior in this subphase.

Required checks:

1. `uv run pytest packages/friday-runtime/tests_runtime/test_kernel.py`
2. `uv run pytest packages/friday-agent/tests_agent/test_base.py packages/friday-agent/tests_agent/test_orchestrator.py`
3. `uv run ruff check packages/friday-agent/src/friday_agent/base.py packages/friday-agent/src/friday_agent/repl_base.py packages/friday-agent/src/friday_agent/interactive.py packages/friday-runtime/src/friday_runtime/kernel.py`
4. `uv run mypy packages/friday-agent/src/friday_agent/base.py packages/friday-agent/src/friday_agent/repl_base.py packages/friday-agent/src/friday_agent/interactive.py packages/friday-runtime/src/friday_runtime/kernel.py`

Exit criteria:

1. No workflow-path agent instantiation depends on direct concrete copilot/interactive binding.
2. Canonical dispatch implementation remains reserved for Phase 4-B.

---

## Subphase A4: 4-A Gate and Handoff Package

Goal:

1. Produce a clean, machine-consumable handoff for Phase 4-B.

Target files:

1. `docs/design/agents/Phase-4/subphase-artifacts/phase-4-a/subphase-a-4/`
2. `docs/design/agents/Phase-4/phase-4-a-execution-plan.md`
3. `docs/design/agents/Phase-4/phase-4-b-execution-plan.md`
4. `docs/design/agents/Phase-4/phase-4-build-plan.md`
5. `docs/design/agents/Phase-4/phase-4-execution-plan.md`
6. `docs/design/agents/Phase-4/phase-4-build-plan-examples.md`
7. `docs/design/agents/Phase-4/phase-4-ai-agent-implementation-guide.md`
8. `docs/design/agents/Phase-4/phase-4-executive-overview.md`

Execution scope:

1. Validate primary AC coverage for AC 1-6 and 18-21.
2. Re-validate that the full Phase 4 companion set remains coherent after 4-A completion.
3. Publish foundation evidence bundle, unresolved-risk register, and any accepted downstream document drift.
4. Publish explicit Phase 4-B prerequisites, blocked items, and the statement that runtime artifact policy foundation is complete while workflow/pipeline/task artifact contract enforcement remains pending for Phase 4-B.
5. Publish `phase-4-a-handoff-manifest.yaml` conforming to the contract in section 7, including regression guardrail status.

Required checks:

1. Run full gate command set defined in section 2.
2. Verify `phase-4-a-handoff-manifest.yaml` contains all required keys and non-empty values.
3. Verify each primary AC in the 4-A set is marked `complete` or `waived` with owner/date.
4. Verify regression guardrails for AC 11, 14, 15, and 17 are marked `pass`, `risk`, or `blocked` with evidence links.

Exit criteria:

1. Foundation contracts are stable and ready for workflow/governance implementation.

---

## 4. AC Traceability for Phase 4-A

| Phase 4-A Subphase | Primary AC Coverage |
| :--- | :--- |
| A0 | AC 1-6, 18-21 baseline lock |
| A1 | AC 1, 2, 6 |
| A2 | AC 3, 4, 5 |
| A3 | AC 18, 19, 20, 21 |
| A4 | AC 1-6, 18-21 completion/waiver validation |

Secondary regression criteria observed during 4-A execution and handoff:

1. AC 11: existing env-only startup and single-agent defaults remain functional
2. AC 14: unknown keys in runtime/agent/workflow/pipeline/task YAML contracts fail hard
3. AC 15: `config_policy.workflow_mode` behavior does not regress where exercised by foundation work
4. AC 17: runtime-level artifact configuration foundation is established without claiming cross-layer artifact completion

---

## 5. Mapping to Build-Plan Workstreams

| Phase 4-A Subphase | Build-Plan Coverage |
| :--- | :--- |
| A0 | Preconditions and traceability lock |
| A1 | Workstream A |
| A2 | Workstream B, Workstream C |
| A3 | Workstream D |
| A4 | 4-A evidence and handoff gate |

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Config contract drift during fast iteration | Medium | High | A0 lock + A1 strict validation tests |
| Service-binding failures discovered too late | Medium | High | A2 startup/preflight hard-fail gates |
| Runtime remains coupled to concrete agent class | Medium | High | A3 abstraction conformance + factory-path tests |
| Compatibility alias ambiguity | Medium | Medium | A3 explicit deprecation policy and evidence checks |

---

## 7. Exit Contract for Phase 4-B

Phase 4-B may begin only after:

1. Workstreams A-D are complete and evidenced.
2. Generic typed factory behavior is validated in workflow paths.
3. AC 1-6 and 18-21 are either complete or explicitly waived with owner/date.
4. Regression guardrails for AC 11, 14, 15, and 17 are reported with evidence and any `risk` or `blocked` status is explicitly accepted as a B-track blocker or mitigation item.
5. Runtime artifact policy foundation is complete and cross-layer artifact contract enforcement is explicitly carried forward to Phase 4-B.
6. Handoff package contains unresolved risks, mitigation ownership, and any accepted downstream document drift.
7. Full Phase 4 companion-set coherence status is recorded in the handoff package.
8. `phase-4-a-handoff-manifest.yaml` is present and includes:
   - `phase: phase-4-a`
   - `completed_workstreams: [A, B, C, D]`
   - `ac_status` map for AC 1-6 and 18-21 (`complete|waived`)
   - `regression_guardrails` object keyed by `AC11`, `AC14`, `AC15`, and `AC17`
   - each `regression_guardrails.<ac_id>` entry is an object with:
     - `status: pass|risk|blocked`
     - `evidence: [<path>, ...]`
     - `notes: <string>` (optional)
   - `waivers` list with `ac_id`, `owner`, `expiration_date`, `mitigation_plan`
   - `open_risks` list with `risk_id`, `owner`, `severity`, `mitigation`
   - `document_coherence_status` object with:
     - `companion_set: [<path>, ...]`
     - `status: coherent|drift_accepted|blocked`
     - `verified_in_subphase: A0|A4`
     - `accepted_downstream_drift: [ { document, issue, disposition, owner } ]`
   - `blocking_items_for_4b` list
   - `required_inputs_for_4b` list
   - `evidence_index` path list
