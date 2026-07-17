# Alt Phase 4 Build Plan: Runtime Coherence, YAML Runtime Config, and Multi-LLM Service Pool

**Status:** Proposed for Approval
**Date:** 2026-02-19
**Depends On:**
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-build-plan.md`
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-transition-plan.md`

**References:**
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/technical-specifications.md`
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/comprehensive-agent-framework-design.md`
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/agent-contract.md`
- `docs/archive/agent-phase-artifacts/Alt-Phase-2/runtime-config-dual-source-patch-plan.md`
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
11. Workstreams A-J (A-I retained and expanded, with inserted Workstream D for agent abstraction/runtime-factory decoupling).
12. Test/gate posture and compatibility guarantees.

Net-new depth added in this revision:

1. Canonical runtime-orchestrator-agent interaction model.
2. Pipeline-first execution model and legacy adapter contract.
3. Owner resolution policy for `owner_role` assignments.
4. Dispatch lifecycle and governance detail.
5. Observability evidence requirements for release gates.
6. Migration/rollout/rollback timeline.
7. Agent abstraction layering and runtime-factory decoupling for workflow execution paths.

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
10. Workflow routing mode is explicit via `config_policy.workflow_mode` with `canonical` default.
11. Unknown keys hard-fail in runtime/agent/workflow/pipeline/task YAML (`unknown_key_policy=fail`).
12. `owner_role` resolution is allowed only through explicit `agents.role_bindings`.
13. Artifact policy and task-output artifact bindings are YAML-defined and validated before dispatch.
14. Runtime workflow execution paths use a generic typed agent factory and must not hardcode concrete interactive/copilot agent classes.
15. `InteractiveAgent` is the direct-runtime interactive default; workflow execution resolves agent behavior via selected agent profile and factory mapping.
16. `CopilotAgent` naming/API remains compatibility-only for Phase 4 and is removed in Phase 5.
17. `agent_type` is a profile-level runtime contract with default `interactive` when omitted.

Coherence defaults ratified in this plan:

1. Canonical execution path is hierarchical: `workflow -> pipeline -> task`.
2. Legacy workflow model is compatibility-only during transition.
3. Assignment ownership must resolve to concrete agent IDs before claim/start.
4. Deterministic behavior is mandatory for dispatch, claim, retry, lease recovery, and cancellation.
5. Workflow chooses the execution owner; runtime resolves the selected owner's profile and instantiates by `agent_type` through generic factory mapping.
6. Convenience runtime entrypoints for interactive chat are separate from canonical workflow dispatch paths.

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
11. Add agent abstraction hierarchy (`AgentBase`, `ReplAgentBase`, `InteractiveAgent`) and runtime-factory decoupling in workflow execution paths.
12. Add one-phase compatibility aliases for copilot naming and runtime convenience APIs with explicit Phase 5 removal target.

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
   - Resolve each agent `agent_type` for factory mapping.
3. Session activation:
   - Create runtime session and bind orchestrator context.
4. Workflow dispatch:
   - Load workflow definition(s).
   - Resolve to canonical pipeline model.
   - Validate hierarchy and ownership references.
5. Task execution:
   - Assign dependency-ready tasks.
   - Enforce claim/lease/heartbeat semantics.
   - Resolve owner to agent profile, then instantiate via generic typed factory.
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
6. `agents` (including `role_bindings`)
7. `runtime_paths`
8. `scratch`
9. `artifacts`
10. `config_policy`

`config_policy` fields:

1. `allow_env_override: false` (default)
2. `strict_agent_llm_binding: true|false`
3. `workflow_mode: canonical|legacy|auto` (default `canonical`)
4. `unknown_key_policy: fail` (locked in Phase 4)

`artifacts` fields:

1. `enabled: true|false` (default `true`)
2. `root_dir: <path>` (relative paths resolve from `runtime_paths.runtime_data_root`)
3. `lineage_required: true|false` (default `true`)
4. `publish_on_task_success: true|false` (default `true`)

Deterministic source precedence:

1. Defaults
2. YAML
3. Env (only when `allow_env_override=true`)
4. Explicit constructor args

Workflow execution mode semantics:

1. `workflow_mode=canonical`: use canonical `workflow -> pipeline -> task` path only.
2. `workflow_mode=legacy`: route workflow execution through legacy adapter path.
3. `workflow_mode=auto`: attempt canonical first; if legacy schema is detected, route through adapter and emit migration warning metadata.

Unknown-key semantics (locked decisions for Phase 4):

1. Unknown keys in runtime YAML config fail startup.
2. Unknown keys in agent profile YAML fail profile load/startup.
3. Unknown keys in workflow/pipeline/task YAML fail load/dispatch.
4. No warn-only unknown-key mode is allowed in this phase.

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
5. Add `agent_type: interactive|autonomous|custom` (default `interactive` when omitted).
6. Unknown `agent_type` mapping fails startup/preflight.

## 6.4 Workflow/Pipeline/Task Contract

Canonical hierarchy:

1. Workflow contains one or more pipeline references.
2. Pipeline contains one or more task definitions.
3. Task ownership selector is exactly one of:
   - `owner_agent_id`
   - `owner_role`

Owner resolution policy:

1. `owner_agent_id` resolves directly to concrete agent ID.
2. `owner_role` resolves through `agents.role_bindings.<owner_role> -> <agent_id>`.
3. Missing role binding, mapped unknown agent, or ambiguous binding fails dispatch.
4. Concrete owner must be resolved before assignment claim/start.
5. Resolved owner profile determines runtime `agent_type` selection through the generic typed factory.

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

Artifact declaration policy:

1. Workflow may declare `required_artifacts`.
2. Pipeline may declare `artifact_contract.produced` and `artifact_contract.consumed`.
3. Task may declare `output_artifacts`.
4. Each `output_artifacts[].from_output` must reference a key in task `output_contract`.
5. Each consumed artifact must match produced artifact `artifact_id` and `type`.
6. Missing required artifact at completion fails pipeline/workflow deterministically.

## 6.5 Artifact Output Binding Contract

Required shape:

1. `workflow.required_artifacts[]`:
   - `artifact_id`
   - `type`
   - `produced_by_pipeline`
2. `pipeline.artifact_contract.produced[]`:
   - `artifact_id`
   - `type`
   - `producer_task_id`
3. `pipeline.artifact_contract.consumed[]`:
   - `artifact_id`
   - `type`
   - `from_pipeline`
4. `task.output_artifacts[]`:
   - `artifact_id`
   - `from_output`
   - `type`
   - `required`

Semantics:

1. Artifact declarations are configuration, not inferred behavior.
2. Artifact `type` must match task `output_contract` and pipeline/workflow artifact contracts.
3. Artifact identifiers are unique within a workflow execution scope.
4. Artifact emission and lineage are enforced by runtime `artifacts` policy.

## 6.6 Task Field Type Contract (Normative)

| Task Field | YAML Type | Validation / Notes |
| --- | --- | --- |
| `task_id` | string | Non-empty identifier; lowercase-normalized; alnum plus `_` / `-`. |
| `owner_agent_id` / `owner_role` | string | Exactly one selector must be present. |
| `agent_type` (profile-level) | string | Optional in profile; defaults to `interactive`; must resolve in runtime factory map. |
| `required_skills` | list[string] | Optional; non-empty unique skill refs when present. |
| `input_contract` | map[string,string] | Output/input type names must be non-empty strings. |
| `output_contract` | map[string,string] | Output/input type names must be non-empty strings. |
| `dependencies` | list[string] | Optional; entries must reference valid task IDs. |
| `retry_policy.max_attempts` | integer | Required to be integer `>=1` in canonical YAML; parsers may coerce numeric strings only for compatibility. |
| `output_artifacts` | list[object] | Each object requires `artifact_id`, `from_output`, `type`, and `required` (boolean). |

## 6.7 Legacy Compatibility Adapter Contract

1. Legacy `WorkflowDefinition` remains executable through an adapter.
2. Adapter output targets canonical pipeline runtime model.
3. Adapter path emits compatibility warning and migration metadata.
4. Adapter must publish a versioned translation matrix (supported legacy schema versions and field mappings).
5. Unsupported legacy constructs fail with deterministic adapter errors.
6. Adapter is transitional and subject to phased deprecation policy.
7. Adapter routing obeys `config_policy.workflow_mode`.

## 6.8 Agent Abstraction and Runtime Factory Contract

Abstraction hierarchy:

1. `AgentBase` owns shared infrastructure contracts:
   - session and memory lifecycle,
   - tool execution primitive and policy checks,
   - turn archiving and telemetry hooks.
2. `ReplAgentBase` derives from `AgentBase` and owns the generic LLM REPL/tool-calling loop.
3. `InteractiveAgent` derives from `ReplAgentBase` as the concrete interactive runtime default.
4. Other agent types may derive from `AgentBase` directly or from `ReplAgentBase` depending on execution strategy.

Runtime factory behavior:

1. Runtime must expose a generic typed factory for workflow execution paths.
2. Workflow dispatch paths must not instantiate concrete interactive/copilot classes directly.
3. Factory resolution inputs are the selected owner agent profile and its `agent_type`.
4. Unknown or unregistered `agent_type` fails startup/preflight deterministically.

Compatibility behavior:

1. `CopilotAgent` naming and `get_copilot_agent()` runtime convenience API remain compatibility aliases in Phase 4.
2. Compatibility aliases emit deprecation guidance toward `InteractiveAgent` and `get_interactive_agent()`.
3. Compatibility aliases are removed in Phase 5.

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

## Feature 5: Agent Abstraction Layer and Runtime Factory Decoupling

Purpose:

1. Ensure runtime infrastructure is decoupled from concrete agent behavior classes in workflow execution paths.

Requirements:

1. `AgentBase` remains the shared infrastructure contract.
2. `ReplAgentBase` owns generic LLM REPL/tool-calling loop behavior.
3. `InteractiveAgent` is the concrete direct-runtime interactive default.
4. Runtime workflow execution uses a generic typed factory keyed by resolved profile `agent_type`.
5. Workflow execution paths must not hardcode concrete interactive/copilot instantiation.
6. Compatibility alias behavior is explicit and time-bounded to Phase 4.

Definition of done:

1. Workflow execution paths resolve agent instances through factory mapping, not concrete class calls.
2. `CopilotAgent`/`get_copilot_agent()` compatibility aliases are documented with Phase 5 removal target.

## Feature 6: Pipeline-First Workflow Execution

Purpose:

1. Align runtime execution with documented hierarchical orchestration model.

Requirements:

1. Canonical runtime dispatch uses workflow/pipeline/task schemas.
2. Pipeline reference integrity checks run before dispatch.
3. Task assignment lifecycle is explicit and deterministic.
4. Retry, lease recovery, timeout, and cancellation semantics are enforced.
5. Task output artifact bindings are validated before task start.
6. Workflow/pipeline artifact contracts are enforced at handoff and completion.

Definition of done:

1. Runtime workflow execution path uses canonical model as default.
2. Deterministic dispatch traces are produced.

## Feature 7: Legacy Workflow Adapter

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

## Feature 8: Owner Resolution Governance

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

## Feature 9: Observability and Compliance Evidence

Purpose:

1. Provide operational and governance proof for release gates.

Requirements:

1. Event fields include workflow, pipeline, task, assignment, and `llm_service` metadata.
2. Typed handoff lineage records are persisted for cross-pipeline movement.
3. Compatibility mode usage (legacy adapter path) is traceable.
4. Compliance artifacts map to gate criteria.
5. Artifact publication records include artifact ID, type, producer task, and pipeline.

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
   - policy is locked to `unknown_key_policy=fail` in Phase 4.
8. Field-level source provenance capture.
9. Artifact policy schema integrity and artifact path-root validity.
10. Workflow/pipeline/task artifact declaration consistency.

Hard-fail cases:

1. Agent references nonexistent `llm_service`.
2. Strict mode enabled and agent omits `llm_service`.
3. `llm_pool.default_service` missing or unresolved.
4. Workflow references missing pipeline.
5. Pipeline references invalid task dependency.
6. Owner resolution fails or is ambiguous.
7. Typed handoff contract mismatch across pipeline boundary.
8. Unknown key detected in runtime/agent/workflow/pipeline/task YAML contracts.
9. `output_artifacts.from_output` references missing task output key.
10. Required artifact declared but not published by pipeline/workflow completion.

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
5. Add runtime `artifacts` policy parsing and validation.

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

## Workstream D: Agent Abstraction and Runtime Factory Decoupling

Target files:

1. `packages/friday-agent/src/friday_agent/base.py`
2. `packages/friday-agent/src/friday_agent/repl_base.py`
3. `packages/friday-agent/src/friday_agent/interactive.py`
4. `packages/friday-agent/src/friday_agent/profile.py`
5. `packages/friday-runtime/src/friday_runtime/kernel.py`
6. `packages/friday-runtime/tests_runtime/test_kernel.py`
7. `packages/friday-agent/tests_agent/test_base.py`
8. `packages/friday-agent/tests_agent/test_orchestrator.py`

Tasks:

1. Establish `AgentBase` as shared infrastructure layer and keep behavior-neutral execution contract.
2. Introduce `ReplAgentBase` for generic LLM REPL/tool-calling loop behavior.
3. Standardize `InteractiveAgent` as concrete interactive implementation.
4. Add profile `agent_type` contract and runtime validation for supported factory mappings.
5. Replace workflow-path concrete factory calls with generic typed factory resolution.
6. Keep direct-runtime interactive convenience path separate from canonical workflow dispatch.
7. Preserve compatibility aliases for `CopilotAgent` and `get_copilot_agent()` with deprecation warnings.
8. Document Phase 5 removal target for compatibility aliases.

Deliverables:

1. Decoupled runtime factory behavior for workflow execution paths.
2. Agent abstraction contracts and compatibility/deprecation policy tests.

Definition of done:

1. Workflow execution no longer depends on concrete interactive/copilot runtime binding.
2. Compatibility aliases exist in Phase 4 with explicit Phase 5 removal guidance.

## Workstream E: Canonical Execution Path Unification

Target files:

1. `packages/friday-runtime/src/friday_runtime/kernel.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `packages/friday-agent/src/friday_agent/workflows/models.py`

Tasks:

1. Route runtime workflow execution through canonical pipeline dispatch path.
2. Preserve existing single-agent path compatibility.
3. Produce deterministic dispatch state transitions and traces.
4. Enforce task `output_artifacts` mapping to emitted task outputs.

Deliverables:

1. Unified runtime workflow execution behavior.
2. Regression safety for existing single-agent defaults.

Definition of done:

1. Canonical path is default and documented.

## Workstream F: Legacy Workflow Adapter and Migration Governance

Target files:

1. `packages/friday-agent/src/friday_agent/workflows/loader.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `packages/friday-runtime/src/friday_runtime/kernel.py`
4. `packages/friday-agent/tests_agent/test_workflows.py`
5. Compatibility docs under `docs/architecture/agents/Alt-Phase-2`

Tasks:

1. Define adapter from legacy workflow schema to canonical pipeline runtime model.
2. Emit compatibility warnings and migration metadata.
3. Define and document translation matrix (legacy fields -> canonical fields, including unsupported constructs).
4. Route adapter usage through `config_policy.workflow_mode`.
5. Define release-phase deprecation policy.

Deliverables:

1. Adapter behavior contract and tests.
2. Migration guidance and warning lifecycle.

Definition of done:

1. Legacy workloads run through adapter with explicit signal for migration.

## Workstream G: Owner Resolution and Assignment Governance

Target files:

1. `packages/friday-agent/src/friday_agent/workflows/engine.py`
2. `packages/friday-agent/src/friday_agent/workflows/models.py`
3. `packages/friday-agent/tests_agent/test_pipeline_dispatch.py`

Tasks:

1. Implement deterministic resolver for `owner_role`.
2. Enforce one-resolved-owner requirement before claim.
3. Enforce mismatch rejection in claim path.
4. Record assignment evidence for audit.
5. Resolve `owner_role` only through `agents.role_bindings`.

Deliverables:

1. Owner resolution policy implementation.
2. Assignment lifecycle governance tests.

Definition of done:

1. No task can start without concrete, validated ownership.

## Workstream H: Observability and Cost Attribution

Target files:

1. `packages/friday-agent/src/friday_agent/workflows/engine.py`
2. `packages/friday-runtime/src/friday_runtime/kernel.py`
3. `packages/friday-telemetry/src/friday_telemetry/models/llm.py`
4. `packages/friday-transcript/src/friday_transcript/models/transcript.py`

Tasks:

1. Emit `llm_service`, model, provider metadata.
2. Emit workflow/pipeline/task/assignment identity fields.
3. Emit typed handoff lineage entries.
4. Emit compatibility mode flag and migration metadata when adapter path is used.
5. Emit artifact publication metadata and output-to-artifact mapping evidence.
6. Emit canonical workflow telemetry events from the execution stack:
   - `workflow_execution_started|completed|failed`
   - `pipeline_execution_started|completed|failed|blocked`
   - `workflow_task_started|completed|failed`
   - `workflow_typed_handoff_validated`
   - `workflow_artifact_published`
7. Emit `workflow_mode_selected` from runtime routing whenever `workflow_mode` resolves to canonical, legacy-adapter, or auto-selected adapter behavior.
8. Ensure per-task `llm_service` attribution is attached before orchestrator delegation so compliance and cost evidence can be joined to assignment/task identity.

Deliverables:

1. Queryable event metadata for operations and compliance.
2. Evidence bundle for release gates.

Definition of done:

1. Gate artifacts can prove execution lineage and model-service attribution.

## Workstream I: Documentation and Migration Coherence

Target docs:

1. `docs/archive/agent-phase-artifacts/Alt-Phase-2/technical-specifications.md`
2. `docs/archive/agent-phase-artifacts/Alt-Phase-2/comprehensive-agent-framework-design.md`
3. `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-transition-plan.md`
4. `docs/archive/agent-phase-artifacts/Alt-Phase-2/README.md`
5. `docs/archive/agent-phase-artifacts/Phase-4/phase-4-build-plan.md`
6. `docs/archive/agent-phase-artifacts/Phase-4/phase-4-build-plan-examples.md`
7. `docs/archive/agent-phase-artifacts/Phase-4/phase-4-ai-agent-implementation-guide.md`

Tasks:

1. Align all docs to the canonical runtime execution model.
2. Document compatibility adapter semantics.
3. Add developer-facing single-agent and multi-agent execution reference flows.

Deliverables:

1. Cross-document consistency with no contradictory runtime guidance.

Definition of done:

1. An implementation agent can execute from docs without unresolved design decisions.

## Workstream J: Artifact Configuration and Output Binding

Target files:

1. `packages/friday-runtime/src/friday_runtime/config.py`
2. `packages/friday-agent/src/friday_agent/workflows/models.py`
3. `packages/friday-agent/src/friday_agent/workflows/loader.py`
4. `packages/friday-agent/src/friday_agent/workflows/engine.py`
5. `packages/friday-runtime/tests_runtime/test_config.py`
6. `packages/friday-agent/tests_agent/test_workflows.py`
7. `packages/friday-agent/tests_agent/test_pipeline_dispatch.py`

Tasks:

1. Add schema support for runtime `artifacts` policy and validate defaults.
2. Add workflow/pipeline/task artifact configuration schema and loader validation.
3. Enforce artifact type compatibility across task, pipeline, and workflow contracts.
4. Bind successful task outputs to configured artifacts and emit lineage metadata.
5. Fail dispatch/completion deterministically when required artifacts are missing.

Deliverables:

1. YAML-first artifact configuration contract across runtime/workflow/pipeline/task.
2. Deterministic artifact output binding behavior with test coverage.

Definition of done:

1. Artifact declarations are validated at load time and enforced at runtime completion.

---

## 10. Integrated Dual-Source Patch Plan (Carried Forward)

This Phase 4 plan formally subsumes `runtime-config-dual-source-patch-plan.md`.

Carried scope:

1. `packages/friday-runtime/src/friday_runtime/config.py`
2. `packages/friday-runtime/tests_runtime/test_config.py`
3. `packages/friday-runtime/src/friday_runtime/kernel.py` (integration touchpoint as needed)
4. `docs/archive/agent-phase-artifacts/Alt-Phase-2/technical-specifications.md`
5. `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-build-plan.md` (compatibility addendum if needed)
6. `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-transition-plan.md`
7. `docs/archive/agent-phase-artifacts/Alt-Phase-2/README.md`

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
5. Unknown-key strict behavior (hard-fail).
6. Relative-path resolution from YAML location.
7. YAML-secret acceptance with warning/note policy.

## 11.2 LLM Pool and Agent Binding Tests

1. Default service resolution.
2. Per-agent service resolution by `llm_service`.
3. Hard fail on missing/invalid service mapping.
4. Strict-mode binding requirement.
5. Per-service resilience behavior.

## 11.3 Agent Abstraction and Runtime Factory Tests

1. `AgentBase` infrastructure behavior remains reusable and behavior-neutral.
2. `ReplAgentBase` implements generic LLM REPL/tool-calling loop contracts.
3. `InteractiveAgent` behavior matches direct-runtime interactive expectations.
4. Runtime typed factory resolves instances from profile `agent_type`.
5. Workflow execution paths do not instantiate concrete interactive/copilot classes directly.
6. Compatibility aliases (`CopilotAgent`, `get_copilot_agent()`) emit deprecation guidance and map to interactive behavior in Phase 4.

## 11.4 Workflow/Pipeline/Task Runtime Tests

1. Workflow-to-pipeline reference integrity.
2. Pipeline task-graph integrity.
3. Dependency-ready deterministic assignment order.
4. Claim/heartbeat/start/complete transitions.
5. Awaiting-human transitions and deterministic resume behavior.
6. Lease-expiry recovery and reassignment readiness.
7. Retry-policy behavior and terminal failure conditions.

## 11.5 Owner Resolution and Assignment Tests

1. Direct `owner_agent_id` resolution.
2. Deterministic `owner_role` resolution via `agents.role_bindings`.
3. Ambiguous role mapping failure behavior.
4. Claim rejection when claimant is not assigned owner.
5. Missing role binding failure behavior.
6. Role binding points to unknown agent failure behavior.

## 11.6 Cross-Pipeline Handoff and Lineage Tests

1. Typed handoff success and lineage creation.
2. Typed contract mismatch failure.
3. Pipeline result generation with failure summaries.
4. Artifact contract validation for produced/consumed declarations.
5. Deterministic failure when required workflow artifact is missing.

## 11.7 Legacy Adapter Compatibility Tests

1. Legacy workflow definition conversion and execution.
2. Compatibility warning emission.
3. No regressions in existing single-agent default path.

## 11.8 Observability and Gate Evidence

1. Event completeness validation for required IDs and LLM metadata.
2. Cost/usage attribution by `llm_service`.
3. Gate artifact publication for compliance review.

## 11.9 Phase Gates

1. Subphase-local pytest/ruff/mypy gates pass.
2. Full repository gate set runs per execution governance policy.
3. Required evidence artifacts are generated and reviewable.

## 11.10 Canonical Gate Commands

1. `uv run pytest`
2. `uv run pytest tests/integration`
3. `uv run ruff check .`
4. `uv run mypy packages tests main.py`

## 11.11 Artifact Configuration and Publication Tests

1. Runtime `artifacts` policy load and defaulting behavior.
2. `task.output_artifacts.from_output` must map to task `output_contract`.
3. Pipeline `artifact_contract.consumed` must match upstream produced contract.
4. Workflow `required_artifacts` must be satisfied before final success.
5. Artifact publication metadata includes workflow/pipeline/task and artifact IDs.

---

## 12. Rollout, Migration, and Rollback

Rollout model:

1. Release N:
   - Canonical pipeline-first runtime path introduced and defaulted via `config_policy.workflow_mode=canonical`.
   - `workflow_mode=legacy|auto` remains available for compatibility and migration.
   - Legacy adapter enabled with warning-only migration signals.
2. Release N+1:
   - Migration signals elevated to CI warning gates for workflows using `workflow_mode=legacy`.
   - Compatibility aliases (`CopilotAgent`, `get_copilot_agent()`) remain available with deprecation warnings.
3. Release N+2 / Phase 5:
   - Remove compatibility aliases for copilot naming/runtime convenience API.
   - Legacy path retirement decision evaluated using migration evidence.

Rollback model:

1. Runtime rollback is executed by setting `config_policy.workflow_mode=legacy`.
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
6. Risk: runtime remains coupled to concrete interactive agent behavior in workflow paths.
   Mitigation: generic typed factory in runtime workflow paths plus abstraction conformance tests.
7. Risk: delayed migration from copilot compatibility aliases causes downstream breakage at removal.
   Mitigation: one-phase warning policy and explicit Phase 5 removal timeline in docs and tests.

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
13. `owner_role` resolution is enforced through `agents.role_bindings` with deterministic failures for missing/invalid mappings.
14. Unknown keys in runtime/agent/workflow/pipeline/task YAML contracts fail hard.
15. `config_policy.workflow_mode` behavior (`canonical|legacy|auto`) is deterministic and fully tested.
16. This plan includes canonical YAML examples for runtime config, agent profile, workflow definition, and pipeline/task definitions.
17. Artifacts are first-class and configurable via YAML across runtime/workflow/pipeline/task contracts, with deterministic validation and output binding.
18. Runtime workflow execution paths instantiate agents through generic typed factory mapping and do not hardcode concrete interactive/copilot classes.
19. Workflow-selected owner resolution governs execution-time agent behavior by selecting the owner profile and its `agent_type`.
20. Direct-runtime interactive defaults are explicit (`InteractiveAgent`) and isolated from canonical workflow dispatch policy.
21. Copilot naming/runtime convenience aliases remain compatibility-only in Phase 4 and are scheduled for removal in Phase 5.

---

## 15. Appendix: Implementation Companions

Phase 4 implementation includes two companion guides:

1. `docs/archive/agent-phase-artifacts/Phase-4/phase-4-build-plan-examples.md`
2. `docs/archive/agent-phase-artifacts/Phase-4/phase-4-ai-agent-implementation-guide.md`

Execution-plan companions:

1. `docs/archive/agent-phase-artifacts/Phase-4/phase-4-execution-plan.md` (full historical decomposition)
2. `docs/archive/agent-phase-artifacts/Phase-4/phase-4-a-execution-plan.md` (foundation slice)
3. `docs/archive/agent-phase-artifacts/Phase-4/phase-4-b-execution-plan.md` (workflow/governance slice)

Companion scope requirements:

1. Show workflow/pipeline/task creation for single-agent and multi-agent use cases.
2. Show how task ownership binds to agents (`owner_agent_id`, `owner_role`).
3. Show how agent profiles bind to runtime services (`llm_service`, strict-mode expectations).
4. Show how profile `agent_type` maps to runtime factory behavior.
5. Show how runtime configuration binds execution environment (`llm_pool`, memory mode, paths, scratch, policy).
6. Show dispatch lifecycle behavior (assign, claim, run, awaiting human, complete/fail, lease recovery).
7. Show typed handoff and lineage expectations across pipelines.
8. Show artifact policy and output artifact binding behavior in runtime/workflow/pipeline/task YAML.
9. Show compatibility adapter behavior and migration posture for legacy workflows.
10. Map examples and implementation tasks back to this plan's acceptance criteria.

## 15.1 Canonical YAML File Examples (Normative)

The following examples are canonical reference shapes for Phase 4 configuration and execution contracts.
These examples are intentionally explicit so implementation teams can build and validate without schema ambiguity.

### 15.1.1 Runtime Config Example (`runtime.yaml`)

```yaml
config_policy:
  allow_env_override: false
  strict_agent_llm_binding: true
  workflow_mode: canonical
  unknown_key_policy: fail

runtime_paths:
  install_root: /opt/friday
  runtime_data_root: /var/lib/friday/runtime
  workspace_root: /workspace

memory:
  mode: multi_agent

scratch:
  backend: sqlite
  path: scratch/scratch.db

artifacts:
  enabled: true
  root_dir: artifacts
  lineage_required: true
  publish_on_task_success: true

llm_pool:
  default_service: fast_openai
  services:
    fast_openai:
      provider: openai
      model: gpt-4o-mini
      api_key: ${OPENAI_API_KEY}
      resilience:
        timeout_seconds: 30
        max_retries: 3
    reasoning_openai:
      provider: openai
      model: o3
      api_key: ${OPENAI_API_KEY}
      resilience:
        timeout_seconds: 90
        max_retries: 2

embedding:
  model: text-embedding-3-small

agents:
  dir: agents
  role_bindings:
    synthesis: synthesizer
    research: researcher
```

### 15.1.2 Agent Profile Example (`agents/researcher.yaml`)

```yaml
name: researcher
role: Research Specialist
goal: Build evidence set from trusted sources
system_prompt: |
  You gather evidence and cite sources.
llm_service: fast_openai
agent_type: interactive
tool_autonomy: hybrid
injected_tools:
  - recall_memory
required_tools:
  - store_fact
available_tools:
  - scratchpad_write
  - scratchpad_read
tools:
  - recall_memory
  - store_fact
skills:
  - research_foundation@1.2.0
```

### 15.1.3 Workflow Definition Example (`workflows/wf_research_synthesis/workflow.yaml`)

```yaml
workflow_id: wf_research_synthesis
version: 1.0.0
name: Research To Synthesis
goal: Produce final recommendation package
pipeline_refs:
  - pl_research
  - pl_synthesis
entry_pipeline_id: pl_research
completion_criteria:
  - recommendation report delivered
required_artifacts:
  - artifact_id: recommendation_report
    type: markdown
    produced_by_pipeline: pl_synthesis
timeout_seconds: 7200
```

### 15.1.4 Pipeline Definition Example (`workflows/wf_research_synthesis/pipelines/pl_research.yaml`)

```yaml
pipeline_id: pl_research
version: 1.0.0
workflow_id: wf_research_synthesis
goal: Gather evidence
upstream_pipeline_ids: []
input_contract: {}
output_contract:
  evidence_bundle: json
artifact_contract:
  produced:
    - artifact_id: evidence_bundle
      type: json
      producer_task_id: collect_sources
  consumed: []
tasks:
  - task_id: collect_sources
    name: Collect Sources
    description: Collect and rank source material.
    owner_agent_id: researcher
    required_skills:
      - research_foundation@1.2.0
    input_contract: {}
    output_contract:
      evidence_bundle: json
    output_artifacts:
      - artifact_id: evidence_bundle
        from_output: evidence_bundle
        type: json
        required: true
    dependencies: []
    retry_policy:
      max_attempts: 2
```

### 15.1.5 Pipeline Definition Example (`workflows/wf_research_synthesis/pipelines/pl_synthesis.yaml`)

```yaml
pipeline_id: pl_synthesis
version: 1.0.0
workflow_id: wf_research_synthesis
goal: Build final recommendations
upstream_pipeline_ids:
  - pl_research
input_contract:
  evidence_bundle: json
output_contract:
  recommendation_report: markdown
artifact_contract:
  produced:
    - artifact_id: recommendation_report
      type: markdown
      producer_task_id: produce_recommendations
  consumed:
    - artifact_id: evidence_bundle
      type: json
      from_pipeline: pl_research
tasks:
  - task_id: produce_recommendations
    name: Produce Recommendations
    description: Produce final recommendations from evidence bundle.
    owner_role: synthesis
    input_contract:
      evidence_bundle: json
    output_contract:
      recommendation_report: markdown
    output_artifacts:
      - artifact_id: recommendation_report
        from_output: recommendation_report
        type: markdown
        required: true
    dependencies: []
    retry_policy:
      max_attempts: 1
```

## 15.2 Acceptance Criteria Traceability Matrix

The matrix below maps each acceptance criterion to exact sections in the three Phase 4 documents.

| AC | Build Plan (`phase-4-build-plan.md`) | Examples (`phase-4-build-plan-examples.md`) | AI Guide (`phase-4-ai-agent-implementation-guide.md`) |
| --- | --- | --- | --- |
| 1 | 6.1, 11.1, 15.1.1 | 3 | 2, 5 |
| 2 | 3, 6.1, 10, 11.1 | 3 | 2, 5 |
| 3 | 6.2, 11.2, 15.1.1 | 3, 5.1 | 2, 5 |
| 4 | 6.3, 11.2, 15.1.2 | 4.1, 5.2 | 2, 5 |
| 5 | 3, 6.3, 8, 11.2 | 8 | 6 |
| 6 | 3, 4.2, 11.1 | 3 | 2, 8 |
| 7 | 6.4, 7 Feature 6, 11.4 | 2, 4, 5 | 2, 7 |
| 8 | 6.7, 7 Feature 7, 11.7, 12 | 6 | 2, 4, 8 |
| 9 | 6.4, 7 Feature 8, 11.5 | 5.6, 7, 8 | 2, 5, 6 |
| 10 | 6.4, 6.5, 11.6 | 5.6, 7, 8 | 2, 6, 7 |
| 11 | 4.1, 10, 12 | 3, 4.4 | 8 |
| 12 | 3, 10, 13 | 3 | 8 |
| 13 | 3, 6.4, 11.5 | 5.1, 5.6, 7, 8 | 2, 5, 6 |
| 14 | 3, 6.1, 8, 14 | 3, 7, 8 | 2, 5, 6 |
| 15 | 3, 6.1, 11.7, 12, 14 | 6, 7 | 2, 4 |
| 16 | 15.1 | 3, 4, 5 | 3 |
| 17 | 3, 6.1, 6.5, 7 Feature 6, 11.11, 14, 15.1 | 3, 4, 5, 7, 8 | 2, 5, 6, 7, 10 |
| 18 | 3, 6.8, 7 Feature 5, 9 Workstream D, 11.3 | 4.1, 4.2, 8 | 2, 5, 6 |
| 19 | 3, 6.4, 6.8, 7 Feature 5, 11.3, 14 | 4.2, 5.3, 8 | 2, 5, 6 |
| 20 | 3, 6.8, 11.3, 14 | 4.1, 8 | 2, 5 |
| 21 | 3, 6.8, 11.3, 12, 14 | 4.1, 8 | 2, 4, 8 |

Reviewer guidance:

1. Validate that every acceptance criterion has at least one corresponding implementation or verification path in this appendix and companion docs.
2. Validate that no workflow model ambiguity remains between canonical pipeline-first execution and legacy compatibility flow.
3. Validate that runtime, agent, workflow, and artifact bindings are explicit and testable before code implementation begins.

---

## 16. Implementation Readiness Statement

This Phase 4 plan is decision-complete for implementing runtime configuration coherence, multi-LLM service pooling, per-agent model binding, agent abstraction/runtime-factory decoupling, and canonical hierarchical workflow execution with compatibility migration support.

No unresolved architectural choices should remain for implementation teams if this plan is accepted as written.
