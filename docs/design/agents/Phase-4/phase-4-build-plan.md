# Alt Phase 4 Build Plan: Runtime Coherence, YAML Runtime Config, and Multi-LLM Service Pool

**Status:** Proposed for Approval
**Date:** 2026-02-19
**Depends On:**
- `docs/design/agents/Alt-Phase-2/phase-3-build-plan.md`
- `docs/design/agents/Alt-Phase-2/phase-3-transition-plan.md`

**References:**
- `docs/design/agents/Alt-Phase-2/technical-specifications.md`
- `docs/design/agents/Alt-Phase-2/comprehensive-agent-framework-design.md`
- `docs/design/agents/Alt-Phase-2/agent-contract.md`
- `docs/design/agents/Alt-Phase-2/runtime-config-dual-source-patch-plan.md`
- AgentSkills reference repository: `https://github.com/agentskills/agentskills/tree/main`
- Additional skills ecosystem reference: `https://github.com/anthropics/skills`

---

## 1. Executive Intent

Phase 4 closes the coherence gap between documented architecture and runtime behavior by defining one end-to-end execution contract for developers:

1. Runtime configuration is YAML-first, with controlled dual-source behavior.
2. Runtime can host a named LLM service pool.
3. Agents bind to LLM services by name.
4. Workflow execution is canonicalized to `workflow -> pipeline -> task` hierarchy.
5. Legacy task-graph workflows remain available via an explicit transitional adapter.
6. Assignment ownership, dispatch, and lineage behavior are deterministic and auditable.

This plan preserves backward compatibility guarantees while reducing ambiguity for implementation teams and AI execution agents.

---

## 2. No-Signal-Loss Commitment

This revision preserves all commitments from the prior Phase 4 document and expands detail without removing scope.

Preserved commitments:

1. YAML-first runtime config.
2. `allow_env_override` global policy.
3. Nested runtime sections.
4. Per-agent `llm_service` support.
5. Hard-fail semantics for invalid bindings.
6. Strict-mode requirement for `llm_service`.
7. Per-service resilience.
8. Global embedding policy.
9. Current YAML secret allowance plus future key-store direction.
10. Runtime validation semantics.
11. Workstreams A-F (retained and expanded).
12. Test/gate posture and compatibility guarantees.

Net-new depth added in this revision:

1. Canonical runtime-orchestrator-agent interaction model.
2. Pipeline-first execution model and legacy adapter contract.
3. Owner resolution policy for `owner_role` assignments.
4. Dispatch lifecycle and governance detail.
5. Observability evidence requirements for release gates.
6. Migration/rollout/rollback timeline.

---

## 3. Authoritative Locked Decisions

1. Environment variables never override YAML unless explicitly enabled.
2. Runtime configuration uses nested sections.
3. Secrets in YAML are allowed in this version.
4. Future direction: move secrets to external key-store/provider.
5. Invalid or missing agent `llm_service` binding fails hard.
6. Strict mode requires every agent to declare `llm_service`.
7. Resilience policy is configured per LLM service.
8. Embedding configuration remains global in Phase 4.
9. Environment override is global on/off only.

Coherence defaults ratified in this plan:

1. Canonical execution path is hierarchical: `workflow -> pipeline -> task`.
2. Legacy workflow model is compatibility-only during transition.
3. Assignment ownership must resolve to concrete agent IDs before claim/start.
4. Deterministic behavior is mandatory for dispatch, claim, retry, lease recovery, and cancellation.

---

## 4. Scope

## 4.1 In Scope

1. Expand `friday-runtime` config model to support nested YAML sections and deterministic dual-source loading policy.
2. Add runtime-managed `llm_pool` with named services and per-service resilience.
3. Add first-class agent profile `llm_service` binding behavior.
4. Enforce startup-time validation for runtime and all agent-to-service bindings.
5. Canonicalize workflow execution path to hierarchical workflow/pipeline/task dispatch.
6. Provide explicit adapter path for legacy workflow definitions.
7. Define deterministic owner resolution for `owner_agent_id` and `owner_role` task selectors.
8. Preserve env-only compatibility path and single-agent default behavior.
9. Add diagnostics for config source provenance and execution assignment evidence.
10. Update companion Alt-Phase-2 docs to maintain cross-document coherence.

## 4.2 Out of Scope

1. Key-store integration and secret-provider plugins.
2. Per-agent embedding service selection.
3. Dynamic hot-reload of runtime config in-process.
4. Remote config control plane.
5. Full retirement of legacy workflow definitions in this phase.

---

## 5. Canonical Runtime Interaction Model

This model is the developer frame of reference for single-agent and multi-agent workflows.

1. Runtime boot:
   - Load/merge config.
   - Validate runtime paths and config contracts.
   - Build service graph (LLM pool, embeddings, memory, telemetry, tools).
2. Agent initialization:
   - Load agent profiles.
   - Validate each profile against runtime policy.
   - Resolve each agent `llm_service` binding.
3. Session activation:
   - Create runtime session and bind orchestrator context.
4. Workflow dispatch:
   - Load workflow definition(s).
   - Resolve to canonical pipeline model.
   - Validate hierarchy and ownership references.
5. Task execution:
   - Assign dependency-ready tasks.
   - Enforce claim/lease/heartbeat semantics.
   - Execute via orchestrator on resolved agent runtime profile.
6. Completion:
   - Emit lineage, telemetry, and artifacts.
   - Produce pipeline and workflow result records.

Single-agent behavior:

1. Can execute one-agent pipeline/workflow with same canonical stack.
2. May use default single-agent memory mode.
3. Uses designated `llm_service` or policy fallback if strict mode is disabled.

Multi-agent behavior:

1. Runtime hosts multiple agent profiles bound to different LLM services.
2. Orchestrator delegates across agents per task ownership and skill constraints.
3. Workflow can span one or more pipelines with typed handoff and lineage capture.

---

## 6. Public Contracts and Interfaces

## 6.1 Runtime Config Contract

Top-level nested sections:

1. `llm_pool`
2. `llm` (legacy/global compatibility section)
3. `embedding`
4. `memory`
5. `telemetry`
6. `agents`
7. `runtime_paths`
8. `scratch`
9. `config_policy`

`config_policy` fields:

1. `allow_env_override: false` (default)
2. `strict_agent_llm_binding: true|false`
3. Unknown-key handling policy (strict failure behavior defined in specs)

Deterministic source precedence:

1. Defaults
2. YAML
3. Env (only when `allow_env_override=true`)
4. Explicit constructor args

Compatibility entry points:

1. Preserve `RuntimeConfig.from_env()`.
2. Add/standardize `RuntimeConfig.from_yaml(path)`.
3. Support unified merge path (`from_sources` contract).

## 6.2 LLM Pool Contract

Required structure:

1. `llm_pool.default_service`
2. `llm_pool.services.<service_name>.provider`
3. `llm_pool.services.<service_name>.model`
4. `llm_pool.services.<service_name>.api_key`
5. `llm_pool.services.<service_name>.api_base` (optional)
6. `llm_pool.services.<service_name>.resilience`

Semantics:

1. Service names are canonical runtime identifiers.
2. Each service config is independently validated.
3. Per-service resilience policies are independently applied.
4. Missing/invalid default-service reference fails startup.

## 6.3 Agent Profile Contract Addition

1. Add `llm_service: <service_name>` to agent runtime profile schema.
2. Strict mode enabled:
   - every agent must declare `llm_service`.
3. Strict mode disabled:
   - unresolved declaration may fallback to `llm_pool.default_service`.
4. Unknown `llm_service` always fails startup.

## 6.4 Workflow/Pipeline/Task Contract

Canonical hierarchy:

1. Workflow contains one or more pipeline references.
2. Pipeline contains one or more task definitions.
3. Task ownership selector is exactly one of:
   - `owner_agent_id`
   - `owner_role`

Dispatch lifecycle:

1. Assignment creation
2. Claim
3. Running
4. Awaiting human (if required)
5. Completed / failed / cancelled
6. Lease recovery where applicable

Typed handoff policy:

1. Cross-pipeline artifact transfer requires type contract match.
2. Contract mismatch causes deterministic dispatch failure.
3. Lineage records must be emitted for successful handoffs.

## 6.5 Legacy Compatibility Adapter Contract

1. Legacy `WorkflowDefinition` remains executable through an adapter.
2. Adapter output targets canonical pipeline runtime model.
3. Adapter path emits compatibility warning and migration metadata.
4. Adapter is transitional and subject to phased deprecation policy.

---

## 7. Feature Definitions (In-Depth)

## Feature 1: Canonical Runtime-Orchestrator-Agent Contract

Purpose:

1. Eliminate ambiguity on which component controls execution lifecycle.

Requirements:

1. Runtime owns dependency graph and service lifecycle.
2. Registry factory resolves dependencies per agent profile.
3. Orchestrator performs routing, delegation, and active-agent coordination.
4. Workflow engine consumes orchestrator consistently for task execution.

Definition of done:

1. One documented execution sequence for single and multi-agent flows.
2. No competing or contradictory runtime entry models in docs.

## Feature 2: YAML-First Config with Controlled Env Override

Purpose:

1. Make runtime startup deterministic and deployment-portable.

Requirements:

1. YAML file supports nested runtime contracts.
2. Env override is globally gated.
3. Relative paths resolve from YAML location.
4. Unknown-key policy is explicit and testable.
5. Source provenance is available for diagnostics.

Definition of done:

1. Precedence is implemented and tested.
2. Docs explain operator behavior without ambiguity.

## Feature 3: LLM Service Pool

Purpose:

1. Support shared runtime with heterogeneous model/provider usage across agents.

Requirements:

1. Named service catalog loaded at boot.
2. Default service defined and validated.
3. Per-service resilience fields applied independently.
4. Startup fails if pool is inconsistent.

Definition of done:

1. Multiple agents can resolve different configured services in one runtime.
2. Runtime validation catches all unresolved service references.

## Feature 4: Per-Agent LLM Binding

Purpose:

1. Give each agent an explicit execution-model binding.

Requirements:

1. `llm_service` field in agent profile schema and loader validation.
2. Strict/non-strict behavior follows policy.
3. Clear failures for missing/invalid bindings.
4. Binding evidence emitted in telemetry.

Definition of done:

1. Agent creation path deterministically resolves one runtime LLM service.
2. Binding failures are fail-fast at startup/preflight, not mid-run.

## Feature 5: Pipeline-First Workflow Execution

Purpose:

1. Align runtime execution with documented hierarchical orchestration model.

Requirements:

1. Canonical runtime dispatch uses workflow/pipeline/task schemas.
2. Pipeline reference integrity checks run before dispatch.
3. Task assignment lifecycle is explicit and deterministic.
4. Retry, lease recovery, timeout, and cancellation semantics are enforced.

Definition of done:

1. Runtime workflow execution path uses canonical model as default.
2. Deterministic dispatch traces are produced.

## Feature 6: Legacy Workflow Adapter

Purpose:

1. Preserve backward compatibility while moving to canonical model.

Requirements:

1. Legacy definitions are transformed to canonical runtime dispatch shape.
2. Adapter emits warning and migration context.
3. Adapter behavior is documented and tested.
4. Deprecation timeline is specified.

Definition of done:

1. Legacy workflows run without breaking existing users.
2. Migration guidance is clear and measurable.

## Feature 7: Owner Resolution Governance

Purpose:

1. Ensure `owner_role`-based tasks resolve safely and deterministically.

Requirements:

1. Resolve `owner_agent_id` directly when provided.
2. Resolve `owner_role` via deterministic resolver policy.
3. Ambiguous or unresolved role mapping fails dispatch.
4. Assignment record includes resolved owner evidence.

Definition of done:

1. Owner resolution contract is explicit in specs and tests.
2. Claim operations reject agent mismatch deterministically.

## Feature 8: Observability and Compliance Evidence

Purpose:

1. Provide operational and governance proof for release gates.

Requirements:

1. Event fields include workflow, pipeline, task, assignment, and `llm_service` metadata.
2. Typed handoff lineage records are persisted for cross-pipeline movement.
3. Compatibility mode usage (legacy adapter path) is traceable.
4. Compliance artifacts map to gate criteria.

Definition of done:

1. Gate evidence bundle can prove deterministic execution and policy compliance.

---

## 8. Validation and Failure Semantics

Post-merge runtime validation includes:

1. Memory mode validity.
2. Deployment profile validity.
3. Runtime root overlap checks.
4. Scratch path placement checks.
5. LLM pool schema integrity.
6. Agent-to-service binding integrity.
7. Unknown-key handling per policy.
8. Field-level source provenance capture.

Hard-fail cases:

1. Agent references nonexistent `llm_service`.
2. Strict mode enabled and agent omits `llm_service`.
3. `llm_pool.default_service` missing or unresolved.
4. Workflow references missing pipeline.
5. Pipeline references invalid task dependency.
6. Owner resolution fails or is ambiguous.
7. Typed handoff contract mismatch across pipeline boundary.

---

## 9. Workstreams

## Workstream A: Runtime Config Dual-Source Foundation

Target files:

1. `packages/friday-runtime/src/friday_runtime/config.py`
2. `packages/friday-runtime/tests_runtime/test_config.py`

Tasks:

1. Implement nested YAML config parsing and policy merge.
2. Implement `allow_env_override` gate behavior.
3. Implement deterministic precedence and provenance tracking.
4. Preserve env-only path compatibility.

Deliverables:

1. Runtime config parser/merger behavior.
2. Config validation and precedence test coverage.

Definition of done:

1. All precedence and strict/override scenarios pass.

## Workstream B: LLM Service Pool in Runtime DI

Target files:

1. `packages/friday-runtime/src/friday_runtime/di.py`
2. `packages/friday-runtime/src/friday_runtime/kernel.py`
3. `packages/friday-runtime/tests_runtime/test_di.py`

Tasks:

1. Build named pool of LLM services.
2. Validate pool structure and default service.
3. Apply per-service resilience options.

Deliverables:

1. Runtime LLM resolver by service name.
2. Startup validation behavior and tests.

Definition of done:

1. Service pool supports multi-service runtime without ambiguous fallback.

## Workstream C: Agent Runtime Binding Model

Target files:

1. `packages/friday-agent/src/friday_agent/profile.py`
2. `packages/friday-agent/src/friday_agent/loader.py`
3. `packages/friday-agent/src/friday_agent/registry.py`
4. `packages/friday-agent/tests_agent/test_loader.py`

Tasks:

1. Add `llm_service` schema/loader support.
2. Enforce strict-mode required binding.
3. Enforce fail-fast behavior on invalid service references.

Deliverables:

1. Agent profile binding contract.
2. Validation errors with deterministic diagnostics.

Definition of done:

1. Agent instantiation cannot proceed with unresolved LLM binding in strict mode.

## Workstream D: Canonical Execution Path Unification

Target files:

1. `packages/friday-runtime/src/friday_runtime/kernel.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `packages/friday-agent/src/friday_agent/workflows/models.py`

Tasks:

1. Route runtime workflow execution through canonical pipeline dispatch path.
2. Preserve existing single-agent path compatibility.
3. Produce deterministic dispatch state transitions and traces.

Deliverables:

1. Unified runtime workflow execution behavior.
2. Regression safety for existing single-agent defaults.

Definition of done:

1. Canonical path is default and documented.

## Workstream E: Legacy Workflow Adapter and Migration Governance

Target files:

1. `packages/friday-agent/src/friday_agent/workflows/loader.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. Compatibility docs under `docs/design/agents/Alt-Phase-2`

Tasks:

1. Define adapter from legacy workflow schema to canonical pipeline runtime model.
2. Emit compatibility warnings and migration metadata.
3. Define release-phase deprecation policy.

Deliverables:

1. Adapter behavior contract and tests.
2. Migration guidance and warning lifecycle.

Definition of done:

1. Legacy workloads run through adapter with explicit signal for migration.

## Workstream F: Owner Resolution and Assignment Governance

Target files:

1. Workflow dispatch/assignment modules in `friday-agent`.
2. Tests for role-owner and direct-owner resolution.

Tasks:

1. Implement deterministic resolver for `owner_role`.
2. Enforce one-resolved-owner requirement before claim.
3. Enforce mismatch rejection in claim path.
4. Record assignment evidence for audit.

Deliverables:

1. Owner resolution policy implementation.
2. Assignment lifecycle governance tests.

Definition of done:

1. No task can start without concrete, validated ownership.

## Workstream G: Observability and Cost Attribution

Target files:

1. Runtime/agent telemetry and transcript surfaces.
2. Compliance artifact emitters.

Tasks:

1. Emit `llm_service`, model, provider metadata.
2. Emit workflow/pipeline/task/assignment identity fields.
3. Emit typed handoff lineage entries.

Deliverables:

1. Queryable event metadata for operations and compliance.
2. Evidence bundle for release gates.

Definition of done:

1. Gate artifacts can prove execution lineage and model-service attribution.

## Workstream H: Documentation and Migration Coherence

Target docs:

1. `docs/design/agents/Alt-Phase-2/technical-specifications.md`
2. `docs/design/agents/Alt-Phase-2/comprehensive-agent-framework-design.md`
3. `docs/design/agents/Alt-Phase-2/phase-3-transition-plan.md`
4. `docs/design/agents/Alt-Phase-2/README.md`
5. `docs/design/agents/Phase-4/phase-4-build-plan.md`

Tasks:

1. Align all docs to the canonical runtime execution model.
2. Document compatibility adapter semantics.
3. Add developer-facing single-agent and multi-agent execution reference flows.

Deliverables:

1. Cross-document consistency with no contradictory runtime guidance.

Definition of done:

1. An implementation agent can execute from docs without unresolved design decisions.

---

## 10. Integrated Dual-Source Patch Plan (Carried Forward)

This Phase 4 plan formally subsumes `runtime-config-dual-source-patch-plan.md`.

Carried scope:

1. `packages/friday-runtime/src/friday_runtime/config.py`
2. `packages/friday-runtime/tests_runtime/test_config.py`
3. `packages/friday-runtime/src/friday_runtime/kernel.py` (integration touchpoint as needed)
4. `docs/design/agents/Alt-Phase-2/technical-specifications.md`
5. `docs/design/agents/Alt-Phase-2/phase-3-build-plan.md` (compatibility addendum if needed)
6. `docs/design/agents/Alt-Phase-2/phase-3-transition-plan.md`
7. `docs/design/agents/Alt-Phase-2/README.md`

Carried acceptance requirements:

1. Env does not override YAML unless `allow_env_override=true`.
2. Nested YAML config is validated.
3. Env-only startup remains functional.
4. Runtime boot and single-agent path remain backward compatible.
5. Secret policy and future key-store direction remain explicit.

---

## 11. Test and Verification Plan

## 11.1 Runtime Config Tests

1. YAML-only load path.
2. Env-only legacy load path.
3. Mixed-source with `allow_env_override=false`.
4. Mixed-source with `allow_env_override=true`.
5. Unknown-key strict behavior.
6. Relative-path resolution from YAML location.
7. YAML-secret acceptance with warning/note policy.

## 11.2 LLM Pool and Agent Binding Tests

1. Default service resolution.
2. Per-agent service resolution by `llm_service`.
3. Hard fail on missing/invalid service mapping.
4. Strict-mode binding requirement.
5. Per-service resilience behavior.

## 11.3 Workflow/Pipeline/Task Runtime Tests

1. Workflow-to-pipeline reference integrity.
2. Pipeline task-graph integrity.
3. Dependency-ready deterministic assignment order.
4. Claim/heartbeat/start/complete transitions.
5. Awaiting-human transitions and deterministic resume behavior.
6. Lease-expiry recovery and reassignment readiness.
7. Retry-policy behavior and terminal failure conditions.

## 11.4 Owner Resolution and Assignment Tests

1. Direct `owner_agent_id` resolution.
2. Deterministic `owner_role` resolution.
3. Ambiguous role mapping failure behavior.
4. Claim rejection when claimant is not assigned owner.

## 11.5 Cross-Pipeline Handoff and Lineage Tests

1. Typed handoff success and lineage creation.
2. Typed contract mismatch failure.
3. Pipeline result generation with failure summaries.

## 11.6 Legacy Adapter Compatibility Tests

1. Legacy workflow definition conversion and execution.
2. Compatibility warning emission.
3. No regressions in existing single-agent default path.

## 11.7 Observability and Gate Evidence

1. Event completeness validation for required IDs and LLM metadata.
2. Cost/usage attribution by `llm_service`.
3. Gate artifact publication for compliance review.

## 11.8 Phase Gates

1. Subphase-local pytest/ruff/mypy gates pass.
2. Full repository gate set runs per execution governance policy.
3. Required evidence artifacts are generated and reviewable.

---

## 12. Rollout, Migration, and Rollback

Rollout model:

1. Release N:
   - Canonical pipeline-first runtime path introduced.
   - Legacy adapter enabled with warning-only migration signals.
2. Release N+1:
   - Migration signals elevated to CI warning gates for new workflows.
3. Release N+2:
   - Legacy path retirement decision evaluated using migration evidence.

Rollback model:

1. Feature flag or compatibility toggle to route runtime workflow execution back to legacy path when needed.
2. Preserve adapter and legacy loader until migration gates are formally cleared.
3. Keep single-agent default path stable throughout rollout.

---

## 13. Risks and Mitigations

1. Risk: configuration complexity increases.
   Mitigation: strict schema, deterministic precedence, provenance diagnostics.
2. Risk: service-name drift between agent profiles and runtime pool.
   Mitigation: startup preflight validation and fail-fast behavior.
3. Risk: ambiguity between canonical and legacy workflow paths.
   Mitigation: explicit adapter contract, warning semantics, phased deprecation policy.
4. Risk: ambiguous role-based assignment behavior.
   Mitigation: deterministic owner resolver and hard-fail ambiguity policy.
5. Risk: plaintext secret exposure in YAML.
   Mitigation: explicit warning posture and future key-store migration commitment.

---

## 14. Acceptance Criteria

1. Runtime supports YAML-first nested config as first-class input.
2. Env override is globally controlled and disabled by default.
3. Runtime supports a named LLM service pool with per-service resilience.
4. Agents bind to LLM services by `llm_service`.
5. Invalid or missing bindings fail hard according to strict policy.
6. Embedding config remains global and backward compatible.
7. Canonical runtime workflow execution uses hierarchical workflow/pipeline/task model.
8. Legacy workflow definitions execute via explicit adapter path during transition.
9. Owner resolution and assignment governance are deterministic and auditable.
10. Typed cross-pipeline handoff and lineage validations are enforced.
11. Existing env-only startup and single-agent defaults remain functional.
12. Documentation explicitly captures current YAML secret policy and future secret isolation direction.

---

## 15. Appendix: Implementation Companions

Phase 4 implementation includes two companion guides:

1. `docs/design/agents/Phase-4/phase-4-build-plan-examples.md`
2. `docs/design/agents/Phase-4/phase-4-ai-agent-implementation-guide.md`

Companion scope requirements:

1. Show workflow/pipeline/task creation for single-agent and multi-agent use cases.
2. Show how task ownership binds to agents (`owner_agent_id`, `owner_role`).
3. Show how agent profiles bind to runtime services (`llm_service`, strict-mode expectations).
4. Show how runtime configuration binds execution environment (`llm_pool`, memory mode, paths, scratch, policy).
5. Show dispatch lifecycle behavior (assign, claim, run, awaiting human, complete/fail, lease recovery).
6. Show typed handoff and lineage expectations across pipelines.
7. Show compatibility adapter behavior and migration posture for legacy workflows.
8. Map examples and implementation tasks back to this plan's acceptance criteria.

Reviewer guidance:

1. Validate that every acceptance criterion has at least one corresponding implementation or verification path in the companion docs.
2. Validate that no workflow model ambiguity remains between canonical pipeline-first execution and legacy compatibility flow.
3. Validate that runtime, agent, and workflow bindings are explicit and testable before code implementation begins.

---

## 16. Implementation Readiness Statement

This Phase 4 plan is decision-complete for implementing runtime configuration coherence, multi-LLM service pooling, per-agent model binding, and canonical hierarchical workflow execution with compatibility migration support.

No unresolved architectural choices should remain for implementation teams if this plan is accepted as written.
