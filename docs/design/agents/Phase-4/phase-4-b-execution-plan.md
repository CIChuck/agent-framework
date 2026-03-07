# Phase 4-B Execution Plan (Workflow and Governance Track)

**Status:** Proposed for Approval  
**Date:** 2026-03-01  
**Source Plan:** `docs/design/agents/Phase-4/phase-4-build-plan.md`  
**Depends On:** `docs/design/agents/Phase-4/phase-4-a-execution-plan.md` completion gate  
**Derived From:** `docs/design/agents/Phase-4/phase-4-execution-plan.md`  
**Purpose:** Execute canonical workflow delivery, governance, and release evidence after foundation contracts are locked in Phase 4-A.

---

## 1. Scope and Boundaries

In-scope workstreams:

1. Workstream E: Canonical Execution Path Unification
2. Workstream F: Legacy Workflow Adapter and Migration Governance
3. Workstream G: Owner Resolution and Assignment Governance
4. Workstream H: Observability and Cost Attribution
5. Workstream I: Documentation and Migration Coherence
6. Workstream J: Artifact Configuration and Output Binding

Acceptance criteria primarily covered:

1. AC 7-17

Regression guardrails (must remain true from Phase 4-A):

1. AC 1-6
2. AC 18-21

---

## 2. Prerequisites

Phase 4-B starts only when all are true:

1. Phase 4-A handoff package is published.
2. `phase-4-a-handoff-manifest.yaml` is present and valid against the 4-A exit contract.
3. Runtime generic typed factory behavior is validated.
4. Agent abstraction boundaries are locked and tested.
5. Full Phase 4 companion-set coherence status is recorded in the 4-A handoff package.
6. `regression_guardrails` status for AC 11, 14, 15, and 17 is present with evidence links.
7. Any remaining 4-A risks are explicitly limited to intake items that B0 must accept, mitigate, or convert into B-track blockers.

Subphase artifact location:

1. `docs/design/agents/Phase-4/subphase-artifacts/phase-4-b/subphase-b-<n>/`

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

## Subphase B0: 4-A Intake and Dependency Verification

Goal:

1. Confirm 4-A outputs are complete and usable for workflow/governance implementation.

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

1. Validate all 4-A prerequisites and unresolved-risk ownership.
2. Validate `phase-4-a-handoff-manifest.yaml` required keys and `ac_status` values (`complete|waived`).
3. Validate full companion-set coherence status and record any accepted downstream document drift entering 4-B.
4. Validate `regression_guardrails` states (`pass|risk|blocked`) for AC 11, 14, 15, and 17 and convert any unaccepted `risk` or `blocked` state into a B-track blocker.
5. Confirm workstream execution order for E-J.
6. Lock acceptance criteria mapping for AC 7-17.

Required checks:

1. Verify `phase-4-a-handoff-manifest.yaml` contains all required keys from the 4-A exit contract, including typed `regression_guardrails` and `document_coherence_status`.
2. Verify the full Phase 4 companion set status is `coherent` or `drift_accepted`; reject `blocked`.
3. Verify every `regression_guardrails.<ac_id>` entry contains `status` and at least one evidence path.

Exit criteria:

1. No prerequisite ambiguity remains for workflow/governance implementation.
2. All 4-A waivers and open risks are explicitly accepted, mitigated, or converted to B-track blockers.
3. 4-A coherence status and regression guardrails are explicitly accepted as the baseline for B-track execution.

---

## Subphase B1: Canonical Dispatch Core (Workstream E)

Goal:

1. Make canonical `workflow -> pipeline -> task` execution path default and deterministic.

Target files:

1. `packages/friday-runtime/src/friday_runtime/kernel.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `packages/friday-agent/src/friday_agent/workflows/models.py`
4. `packages/friday-agent/tests_agent/test_workflows.py`
5. `packages/friday-agent/tests_agent/test_pipeline_dispatch.py`

Execution scope:

1. Consume the generic typed factory seam and locked abstraction boundaries established in 4-A before changing canonical dispatch behavior.
2. Route runtime workflow execution through canonical dispatch.
3. Validate workflow/pipeline/task integrity and dependency behavior.
4. Enforce deterministic lifecycle transitions and task typing contracts.

Required checks:

1. `uv run pytest packages/friday-agent/tests_agent/test_workflows.py packages/friday-agent/tests_agent/test_pipeline_dispatch.py`
2. `uv run ruff check packages/friday-runtime/src/friday_runtime/kernel.py packages/friday-agent/src/friday_agent/workflows/engine.py packages/friday-agent/src/friday_agent/workflows/models.py`
3. `uv run mypy packages/friday-runtime/src/friday_runtime/kernel.py packages/friday-agent/src/friday_agent/workflows/engine.py packages/friday-agent/src/friday_agent/workflows/models.py`

Exit criteria:

1. Canonical dispatch path is default, deterministic, and test-complete.

---

## Subphase B2: Owner Resolution Governance (Workstream G)

Goal:

1. Enforce deterministic ownership selection and assignment claim governance.

Target files:

1. `packages/friday-agent/src/friday_agent/workflows/engine.py`
2. `packages/friday-agent/src/friday_agent/workflows/models.py`
3. `packages/friday-agent/tests_agent/test_pipeline_dispatch.py`

Execution scope:

1. Resolve `owner_agent_id` directly.
2. Resolve `owner_role` only via `agents.role_bindings`.
3. Reject ambiguous/unknown owner mappings deterministically.
4. Emit assignment governance evidence.

Required checks:

1. `uv run pytest packages/friday-agent/tests_agent/test_pipeline_dispatch.py`
2. `uv run ruff check packages/friday-agent/src/friday_agent/workflows/engine.py packages/friday-agent/src/friday_agent/workflows/models.py`
3. `uv run mypy packages/friday-agent/src/friday_agent/workflows/engine.py packages/friday-agent/src/friday_agent/workflows/models.py`

Exit criteria:

1. No task can claim/start without a concrete validated owner.

---

## Subphase B3: Artifact Contracts and Output Binding (Workstream J)

Goal:

1. Enforce first-class artifact contracts across runtime/workflow/pipeline/task.

Target files:

1. `packages/friday-runtime/src/friday_runtime/config.py`
2. `packages/friday-agent/src/friday_agent/workflows/models.py`
3. `packages/friday-agent/src/friday_agent/workflows/loader.py`
4. `packages/friday-agent/src/friday_agent/workflows/engine.py`
5. `packages/friday-runtime/tests_runtime/test_config.py`
6. `packages/friday-agent/tests_agent/test_workflows.py`
7. `packages/friday-agent/tests_agent/test_pipeline_dispatch.py`

Execution scope:

1. Consume the runtime `artifacts` policy foundation delivered in 4-A and preserve its path/default validation behavior.
2. Validate workflow `required_artifacts` definitions.
3. Validate pipeline `artifact_contract.produced/consumed` contracts.
4. Validate task `output_artifacts.from_output` mappings.
5. Fail deterministically on missing required artifacts.

Required checks:

1. `uv run pytest packages/friday-runtime/tests_runtime/test_config.py packages/friday-agent/tests_agent/test_workflows.py packages/friday-agent/tests_agent/test_pipeline_dispatch.py`
2. `uv run ruff check packages/friday-runtime/src/friday_runtime/config.py packages/friday-agent/src/friday_agent/workflows/models.py packages/friday-agent/src/friday_agent/workflows/loader.py packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `uv run mypy packages/friday-runtime/src/friday_runtime/config.py packages/friday-agent/src/friday_agent/workflows/models.py packages/friday-agent/src/friday_agent/workflows/loader.py packages/friday-agent/src/friday_agent/workflows/engine.py`

Exit criteria:

1. Artifact publication is deterministic, contract-validated, and evidence-emitting.

---

## Subphase B4: Legacy Adapter and Migration Governance (Workstream F)

Goal:

1. Preserve compatibility via explicit legacy adapter routing and migration signals.

Target files:

1. `packages/friday-agent/src/friday_agent/workflows/loader.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `packages/friday-runtime/src/friday_runtime/kernel.py`
4. `packages/friday-agent/tests_agent/test_workflows.py`
5. Compatibility docs under `docs/design/agents/Alt-Phase-2`

Execution scope:

1. Implement legacy-to-canonical translation for supported schemas.
2. Enforce `workflow_mode` routing behavior.
3. Emit compatibility warnings and migration metadata.
4. Produce deterministic errors for unsupported legacy constructs.

Required checks:

1. `uv run pytest packages/friday-agent/tests_agent/test_workflows.py`
2. `uv run ruff check packages/friday-agent/src/friday_agent/workflows/loader.py packages/friday-agent/src/friday_agent/workflows/engine.py packages/friday-runtime/src/friday_runtime/kernel.py`
3. `uv run mypy packages/friday-agent/src/friday_agent/workflows/loader.py packages/friday-agent/src/friday_agent/workflows/engine.py packages/friday-runtime/src/friday_runtime/kernel.py`

Exit criteria:

1. Legacy workloads run through explicit adapter path with auditable migration signals.

---

## Subphase B5: Observability and Compliance Evidence (Workstream H)

Goal:

1. Emit operations-grade evidence for execution lineage and governance gates.

Target files:

1. `packages/friday-agent/src/friday_agent/workflows/engine.py`
2. `packages/friday-runtime/src/friday_runtime/kernel.py`
3. `packages/friday-telemetry/src/friday_telemetry/models/llm.py`
4. `packages/friday-transcript/src/friday_transcript/models/transcript.py`

Execution scope:

1. Emit workflow/pipeline/task/assignment identity metadata.
2. Emit `llm_service`, model, provider attribution.
3. Emit typed handoff lineage and artifact publication metadata.
4. Emit compatibility mode/migration metadata for adapter path usage.

Required checks:

1. `uv run pytest packages/friday-agent/tests_agent/test_workflows.py packages/friday-agent/tests_agent/test_pipeline_dispatch.py tests/integration`
2. `uv run ruff check packages/friday-agent/src/friday_agent/workflows/engine.py packages/friday-runtime/src/friday_runtime/kernel.py packages/friday-telemetry/src/friday_telemetry/models/llm.py packages/friday-transcript/src/friday_transcript/models/transcript.py`
3. `uv run mypy packages/friday-agent/src/friday_agent/workflows/engine.py packages/friday-runtime/src/friday_runtime/kernel.py packages/friday-telemetry/src/friday_telemetry/models/llm.py packages/friday-transcript/src/friday_transcript/models/transcript.py`

Exit criteria:

1. Required gate evidence proves deterministic execution and policy compliance.

---

## Subphase B6: Documentation and Migration Coherence (Workstream I)

Goal:

1. Keep all Phase-4 documents and examples coherent with implemented behavior.

Target files:

1. `docs/design/agents/Phase-4/phase-4-build-plan.md`
2. `docs/design/agents/Phase-4/phase-4-execution-plan.md`
3. `docs/design/agents/Phase-4/phase-4-a-execution-plan.md`
4. `docs/design/agents/Phase-4/phase-4-b-execution-plan.md`
5. `docs/design/agents/Phase-4/phase-4-build-plan-examples.md`
6. `docs/design/agents/Phase-4/phase-4-ai-agent-implementation-guide.md`
7. `docs/design/agents/Phase-4/phase-4-executive-overview.md`

Execution scope:

1. Re-validate and finish coherence across the full Phase 4 companion set after workflow/governance implementation.
2. Align contracts across build plan, examples, and implementation guide.
3. Validate acceptance traceability references and section numbering.
4. Ensure examples remain canonical for current parser/runtime behavior.
5. Ensure the executive overview does not contradict active execution-plan boundaries or document-role definitions.

Required checks:

1. Verify the full Phase 4 companion set has no contradictory execution-boundary, artifact-scope, or factory-scope guidance.
2. Verify cross-document references and section numbering remain valid after updates.
3. Verify executive-overview references remain consistent with active execution-plan ownership.

Exit criteria:

1. No cross-document contradictions remain.

---

## Subphase B7: Phase 4-B and Phase 4 Closeout

Goal:

1. Close Phase 4-B and publish final Phase 4 evidence package.

Target files:

1. `docs/design/agents/Phase-4/subphase-artifacts/phase-4-b/`
2. `docs/design/agents/Phase-4/phase-4-b-execution-plan.md`
3. `docs/design/agents/Phase-4/phase-4-execution-plan.md`

Execution scope:

1. Run full repository gates.
2. Validate AC 7-17 completion with explicit evidence links.
3. Confirm carry-forward foundation contracts for AC 1-6 and 18-21 remain satisfied and close regression guardrails for AC 11, 14, 15, and 17.
4. Publish final closeout report and rollback readiness note.

Required checks:

1. `uv run pytest`
2. `uv run pytest tests/integration`
3. `uv run ruff check .`
4. `uv run mypy packages tests main.py`

Exit criteria:

1. All Phase 4 acceptance criteria (1-21) are evidenced with no blocking risks open.

---

## 4. Mapping to Build-Plan Workstreams

| Phase 4-B Subphase | Build-Plan Coverage |
| :--- | :--- |
| B0 | 4-A handoff intake and dependency lock |
| B1 | Workstream E |
| B2 | Workstream G |
| B3 | Workstream J |
| B4 | Workstream F |
| B5 | Workstream H |
| B6 | Workstream I |
| B7 | Phase closeout gates and evidence rollup |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Dispatch behavior diverges from canonical contracts | Medium | High | B1 lifecycle and type-contract tests |
| Owner resolution gaps create nondeterministic claims | Medium | High | B2 strict resolver and failure-path tests |
| Artifact wiring incomplete across layers | Medium | High | B3 contract enforcement + deterministic failure gates |
| Legacy adapter diverges from canonical execution | Medium | High | B4 translation/routing tests + migration metadata |
| Evidence fields insufficient at release gate | Medium | High | B5 completeness checks before B7 closeout |

---

## 6. Phase 4 Umbrella Alignment

To preserve historical context:

1. `phase-4-build-plan.md` remains the umbrella/normative document.
2. `phase-4-execution-plan.md` remains the full historical execution decomposition.
3. Phase 4-A/4-B plans are implementation slices optimized for AI-agent context continuity.
