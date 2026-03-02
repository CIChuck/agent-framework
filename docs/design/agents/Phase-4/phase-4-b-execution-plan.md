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
5. No open blocking risks remain in 4-A handoff register.

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

---

## 3. Subphase Breakdown

## Subphase B0: 4-A Intake and Dependency Verification

Goal:

1. Confirm 4-A outputs are complete and usable for workflow/governance implementation.

Execution scope:

1. Validate all 4-A prerequisites and unresolved-risk ownership.
2. Validate `phase-4-a-handoff-manifest.yaml` required keys and `ac_status` values (`complete|waived`).
3. Confirm workstream execution order for E-J.
4. Lock acceptance criteria mapping for AC 7-17.

Exit criteria:

1. No prerequisite ambiguity remains for workflow/governance implementation.
2. All 4-A waivers and open risks are explicitly accepted, mitigated, or converted to B-track blockers.

---

## Subphase B1: Canonical Dispatch Core (Workstream E)

Goal:

1. Make canonical `workflow -> pipeline -> task` execution path default and deterministic.

Execution scope:

1. Route runtime workflow execution through canonical dispatch.
2. Validate workflow/pipeline/task integrity and dependency behavior.
3. Enforce deterministic lifecycle transitions and task typing contracts.

Exit criteria:

1. Canonical dispatch path is default, deterministic, and test-complete.

---

## Subphase B2: Owner Resolution Governance (Workstream G)

Goal:

1. Enforce deterministic ownership selection and assignment claim governance.

Execution scope:

1. Resolve `owner_agent_id` directly.
2. Resolve `owner_role` only via `agents.role_bindings`.
3. Reject ambiguous/unknown owner mappings deterministically.
4. Emit assignment governance evidence.

Exit criteria:

1. No task can claim/start without a concrete validated owner.

---

## Subphase B3: Artifact Contracts and Output Binding (Workstream J)

Goal:

1. Enforce first-class artifact contracts across runtime/workflow/pipeline/task.

Execution scope:

1. Validate runtime `artifacts` policy and workflow required artifacts.
2. Validate produced/consumed pipeline contracts.
3. Validate task `output_artifacts.from_output` mappings.
4. Fail deterministically on missing required artifacts.

Exit criteria:

1. Artifact publication is deterministic, contract-validated, and evidence-emitting.

---

## Subphase B4: Legacy Adapter and Migration Governance (Workstream F)

Goal:

1. Preserve compatibility via explicit legacy adapter routing and migration signals.

Execution scope:

1. Implement legacy-to-canonical translation for supported schemas.
2. Enforce `workflow_mode` routing behavior.
3. Emit compatibility warnings and migration metadata.
4. Produce deterministic errors for unsupported legacy constructs.

Exit criteria:

1. Legacy workloads run through explicit adapter path with auditable migration signals.

---

## Subphase B5: Observability and Compliance Evidence (Workstream H)

Goal:

1. Emit operations-grade evidence for execution lineage and governance gates.

Execution scope:

1. Emit workflow/pipeline/task/assignment identity metadata.
2. Emit `llm_service`, model, provider attribution.
3. Emit typed handoff lineage and artifact publication metadata.
4. Emit compatibility mode/migration metadata for adapter path usage.

Exit criteria:

1. Required gate evidence proves deterministic execution and policy compliance.

---

## Subphase B6: Documentation and Migration Coherence (Workstream I)

Goal:

1. Keep all Phase-4 documents and examples coherent with implemented behavior.

Execution scope:

1. Align contracts across build plan, examples, and implementation guide.
2. Validate acceptance traceability references and section numbering.
3. Ensure examples remain canonical for current parser/runtime behavior.

Exit criteria:

1. No cross-document contradictions remain.

---

## Subphase B7: Phase 4-B and Phase 4 Closeout

Goal:

1. Close Phase 4-B and publish final Phase 4 evidence package.

Execution scope:

1. Run full repository gates.
2. Validate AC 7-17 completion with explicit evidence links.
3. Confirm regression guardrails for AC 1-6 and 18-21.
4. Publish final closeout report and rollback readiness note.

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
