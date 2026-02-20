# Phase 4 AI Synthetic Developer Implementation Guide

**Status:** Proposed for Approval  
**Date:** 2026-02-20  
**Companion To:** `docs/design/agents/Phase-4/phase-4-build-plan.md`

---

## 1. Purpose

This guide is for AI software development agents (for example Codex or Claude Code) implementing the Friday framework in Phase 4.

Goals:

1. Define the canonical runtime/workflow model to prevent ambiguous implementation.
2. Provide deterministic implementation order and stop conditions.
3. Define required tests, artifacts, and acceptance gates.

---

## 2. Canonical Assumptions (Do Not Deviate)

1. Runtime config is YAML-first.
2. Env override is disabled unless explicitly enabled by policy.
3. Runtime supports named `llm_pool` services.
4. Agent profiles bind to runtime services with `llm_service`.
5. Strict mode requires each agent to define `llm_service`.
6. Embeddings remain globally configured.
7. Canonical execution hierarchy is `workflow -> pipeline -> task`.
8. Legacy `WorkflowDefinition` is compatibility-only and must be adapter-backed.
9. Ownership must resolve to one concrete agent before task claim/start.
10. Typed handoff mismatch is terminal for that dispatch path.

---

## 3. Required Read Order

1. `docs/design/agents/Phase-4/phase-4-build-plan.md`
2. `docs/design/agents/Alt-Phase-2/technical-specifications.md`
3. `docs/design/agents/Alt-Phase-2/comprehensive-agent-framework-design.md`
4. `docs/design/agents/Phase-4/phase-4-build-plan-examples.md`
5. `docs/design/agents/Alt-Phase-2/runtime-config-dual-source-patch-plan.md`

---

## 4. Implementation Order (Workstream-Aligned)

Implement in this order to reduce rework and contract drift:

1. Runtime config dual-source and validation contracts.
2. LLM pool construction and service resolution.
3. Agent profile `llm_service` schema and strict validation behavior.
4. Runtime factory/orchestrator binding to resolved agent LLM service.
5. Canonical workflow/pipeline/task execution path unification.
6. Legacy adapter implementation and migration warning behavior.
7. Owner resolution policy implementation for `owner_role`.
8. Observability and gate artifact completion.
9. Documentation and cross-reference coherence updates.

Do not reorder unless a blocking dependency is discovered and documented.

---

## 5. Binding Model Checklist for AI Implementers

Before implementing workflow execution, confirm all binding contracts are present:

1. Runtime binding:
   - `llm_pool.services` is loaded.
   - `llm_pool.default_service` is validated.
2. Agent binding:
   - each agent has resolved `llm_service` (strict mode semantics applied).
3. Workflow binding:
   - workflow references valid pipelines.
4. Pipeline binding:
   - pipeline references valid tasks and dependencies.
5. Task binding:
   - each task resolves ownership by `owner_agent_id` or `owner_role`.

If any binding cannot be validated, fail fast and stop implementation progression.

---

## 6. Deterministic Failure Rules

Treat these as non-recoverable for the current run unless explicitly routed through recovery logic:

1. Missing or invalid `llm_service` under strict mode.
2. Missing referenced service in `llm_pool`.
3. Unknown workflow pipeline reference.
4. Invalid pipeline task dependency graph.
5. Ambiguous or unresolved `owner_role`.
6. Typed handoff contract mismatch.

Implementation requirement:

1. Failure mode must return explicit reason and object identifiers.
2. Failure must be represented in test fixtures and acceptance evidence.

---

## 7. Task/Pipeline/Workflow Implementation Expectations

AI implementers must ensure all of the following are observable and testable:

1. Workflow contains one or more pipelines.
2. Pipeline contains one or more tasks.
3. Dispatch lifecycle transitions are deterministic:
   - assigned
   - claimed
   - running
   - awaiting_human (when required)
   - completed / failed / cancelled
4. Lease heartbeat and expiration recovery semantics are deterministic.
5. Cross-pipeline handoff validation enforces typed contracts.
6. Lineage records are captured for successful typed handoffs.

---

## 8. Patch Boundaries and Scope Discipline

1. Do not expand Phase 4 scope without explicit approval.
2. Keep embeddings global and unchanged.
3. Keep secret handling in YAML (with documented warning posture) for this phase.
4. Keep legacy adapter transitional; do not silently remove compatibility path.
5. Preserve single-agent defaults and env-only backward-compatible startup path.

If scope expansion is required:

1. Stop.
2. Produce explicit impact note.
3. Wait for approval.

---

## 9. Required Test Gates Per Subphase

Each subphase must include:

1. Targeted unit tests for new contracts.
2. Integration tests for runtime-agent-workflow bindings.
3. Regression tests for single-agent default compatibility.
4. Failure-path tests for deterministic rejection conditions.
5. Gate command results (`pytest`, `ruff`, `mypy`) per execution policy.

---

## 10. Required Evidence Artifacts

For each subphase, produce artifacts proving:

1. Contract validation outcomes.
2. Dispatch/assignment state transition traces.
3. Typed handoff lineage behavior.
4. Runtime-to-agent service binding evidence (`llm_service`, model, provider).
5. Compatibility adapter warning behavior (where exercised).

Evidence must map clearly to the Phase 4 acceptance criteria.

---

## 11. Done Criteria for AI Implementers

A subphase is done only when:

1. Code path aligns to the canonical model.
2. Tests for success and failure paths pass.
3. Gate outputs are captured and attached.
4. No unresolved design decisions remain in changed areas.
5. Companion documentation remains coherent with implementation.

Phase 4 is done only when:

1. All acceptance criteria in `phase-4-build-plan.md` are demonstrably satisfied.
2. Developer examples and AI guide still match actual runtime behavior.

---

## 12. Human Escalation Triggers

Escalate and stop when any of the following occurs:

1. A required contract is missing or contradictory across docs.
2. Multiple plausible ownership resolution policies exist with different behavior.
3. Legacy adapter behavior conflicts with canonical dispatch semantics.
4. Required gates cannot run in current environment.
5. Scope change is needed to satisfy acceptance criteria.

Escalation output must include:

1. Blocker summary.
2. Affected files.
3. Proposed resolution options.
4. Recommended default option.
