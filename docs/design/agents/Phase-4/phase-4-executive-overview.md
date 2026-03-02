# Phase 4 Executive Overview: Runtime Coherence and Multi-Agent Execution Contracts

**Status:** Proposed for Approval  
**Date:** 2026-02-20  
**Audience:** Technical architects, platform engineers, runtime developers, workflow developers  
**Primary References:**  
- `docs/design/agents/Phase-4/phase-4-build-plan.md`  
- `docs/design/agents/Phase-4/phase-4-execution-plan.md`  
- `docs/design/agents/Phase-4/phase-4-build-plan-examples.md`

---

## 1. Executive Summary

Phase 4 upgrades the Friday framework from partially overlapping runtime patterns to one explicit execution model with deterministic contracts.

This phase introduces:

1. YAML-first runtime configuration with controlled environment override behavior.
2. Runtime-managed multi-LLM service pools and per-agent model binding.
3. Canonical workflow execution hierarchy: `workflow -> pipeline -> task`.
4. Deterministic ownership resolution and assignment governance.
5. First-class artifact contracts across runtime, workflow, pipeline, and task layers.
6. Explicit legacy workflow adapter routing for compatibility and migration.
7. Stronger observability, lineage, and release-evidence semantics.

The result is a platform that is more predictable to operate, easier to validate preflight, and safer to extend across multi-agent workloads.

---

## 2. Strategic Outcome for Architecture

Phase 4 resolves four architecture pain points from prior phases:

1. **Configuration ambiguity**  
One canonical source-of-truth model for runtime startup and policy behavior.
2. **Service-binding ambiguity**  
Agent-to-model selection becomes explicit and validated at startup.
3. **Execution-path ambiguity**  
Canonical hierarchical workflow dispatch becomes default; legacy paths are explicit and bounded.
4. **Artifact-output ambiguity**  
Task outputs and required artifacts are declarative and enforceable via YAML contracts.

These changes improve design-time clarity, reduce runtime surprise, and support auditable governance.

---

## 3. Features and Functions Added in Phase 4

## 3.1 YAML-First Runtime Configuration

Key additions:

1. Nested runtime config contracts in YAML.
2. Deterministic source precedence (`defaults -> YAML -> env (gated) -> constructor args`).
3. Global config policy controls including:
   - `allow_env_override`
   - `strict_agent_llm_binding`
   - `workflow_mode` (`canonical|legacy|auto`)
   - `unknown_key_policy=fail`
4. Hard-fail unknown-key validation for runtime/agent/workflow/pipeline/task YAML contracts.

Architectural effect:

1. Operators and platform teams can reason about startup behavior without source-order ambiguity.
2. Configuration drift becomes detectable earlier through strict validation.

## 3.2 Runtime LLM Service Pool

Key additions:

1. Runtime-level `llm_pool` with named services.
2. Required `default_service`.
3. Per-service provider/model/api-key/api-base/resilience contract.
4. Startup hard-fail for unresolved or malformed service definitions.

Functional effect:

1. One runtime instance can host heterogeneous model profiles for multiple agents.
2. Resilience policy can vary by service without introducing custom per-agent retry stacks.

## 3.3 Per-Agent LLM Binding

Key additions:

1. Agent profile `llm_service` field.
2. Strict mode enforcement for explicit agent binding.
3. Deterministic failure for unknown or invalid bindings.

Functional effect:

1. Agent behavior becomes reproducible and attributable at execution time.
2. Model attribution and cost analysis improve by design.

## 3.4 Canonical Workflow/Pipeline/Task Execution

Key additions:

1. Canonical execution hierarchy for all new workloads.
2. Workflow-to-pipeline and pipeline-to-task integrity checks.
3. Deterministic assignment lifecycle semantics:
   - assigned
   - claimed
   - running
   - awaiting_human
   - completed/failed/cancelled
4. Lease and heartbeat semantics for recovery/readiness behavior.

Functional effect:

1. Multi-agent orchestration behavior is predictable and testable.
2. Pipeline composition and dispatch outcomes are easier to diagnose.

## 3.5 Owner Resolution Governance

Key additions:

1. Task ownership selector constrained to exactly one of:
   - `owner_agent_id`
   - `owner_role`
2. `owner_role` resolution only through `agents.role_bindings`.
3. Fail-fast behavior for unresolved/ambiguous mappings.
4. Assignment evidence for audit and policy traceability.

Functional effect:

1. Task claim/start mismatches are prevented by contract, not manual convention.
2. Governance policy is encoded directly in configuration.

## 3.6 Artifact Contracts as First-Class Workflow Members

Key additions:

1. Runtime artifact policy under `artifacts`:
   - enable/disable
   - root path
   - lineage requirement
   - publish-on-success policy
2. Workflow artifact obligations via `required_artifacts`.
3. Pipeline artifact contracts via `artifact_contract.produced` and `.consumed`.
4. Task-level artifact publication mapping via `output_artifacts`.
5. Deterministic failure when required artifacts are missing or type-incompatible.

Functional effect:

1. Agentic task outputs are promotable to governed workflow artifacts with explicit lineage.
2. Cross-pipeline data handoffs become contract-verified and auditable.

## 3.7 Legacy Workflow Adapter and Routing Policy

Key additions:

1. Adapter-based execution support for legacy workflow definitions.
2. Routing control via `workflow_mode`.
3. Compatibility warning and migration metadata emission.
4. Translation matrix requirement for supported/unsupported legacy constructs.

Functional effect:

1. Existing workloads can continue during migration windows.
2. Teams can phase migration without freezing delivery.

## 3.8 Observability and Compliance Evidence

Key additions:

1. Required event metadata for workflow/pipeline/task/assignment identifiers.
2. LLM attribution fields (`llm_service`, model, provider).
3. Typed handoff lineage records.
4. Artifact publication metadata and evidence requirements.
5. Phase-gate alignment with deterministic test and evidence outputs.

Functional effect:

1. Runtime behavior can be reconstructed for operations, compliance, and cost analysis.
2. Release decisions can be based on explicit evidence rather than inferred confidence.

---

## 4. Implementation Risks and Mitigations

| Risk | Likelihood | Impact | Why It Matters | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| Cross-document contract drift | Medium | High | Code may follow one contract while docs enforce another | Maintain acceptance-trace matrix and end-of-subphase documentation coherence checks |
| Config migration errors in YAML-first rollout | Medium | High | Startup regressions can block environments | Enforce strict validation, provide canonical examples, run dual-source compatibility tests early |
| Service-binding mismatch (`llm_service` vs pool names) | Medium | High | Agents can fail startup or bind unintentionally | Preflight startup hard-fail on unresolved bindings with explicit diagnostics |
| Legacy adapter divergence from canonical runtime path | Medium | High | Behavior parity gaps can break migrated workloads | Keep adapter behavior versioned, test `canonical|legacy|auto` routing deterministically |
| Artifact contract under-specification in implementation | Medium | High | Task outputs may not become governed artifacts reliably | Implement runtime/workflow/pipeline/task contract checks before dispatch completion |
| Ownership mapping misconfiguration | Medium | Medium-High | Tasks can stall or misassign in multi-agent pipelines | Enforce `owner_role -> role_bindings` deterministic resolution and fail-fast ambiguity handling |
| Observability fields emitted inconsistently | Medium | Medium-High | Forensics and release evidence become incomplete | Gate on metadata completeness and lineage/artifact publication evidence checks |
| Increased implementation coordination overhead | Medium | Medium | Workstream parallelism can introduce sequencing errors | Execute bounded subphases with artifact triads and mandatory gate cadence |

---

## 5. Developer Impact

## 5.1 Runtime and Platform Developers

1. Implement strict config parsing and deterministic merge behavior.
2. Implement service pool and agent binding preflight checks.
3. Implement adapter routing and dispatch lifecycle consistency.
4. Implement observability and evidence emission across runtime surfaces.

## 5.2 Workflow and Agent Developers

1. Author workflow/pipeline/task YAML using canonical contracts.
2. Explicitly define owner selectors and artifact contracts.
3. Use integer `retry_policy.max_attempts` in canonical YAML.
4. Treat unknown keys and contract mismatches as design-time errors.

## 5.3 Test and Verification Owners

1. Expand deterministic success/failure path testing for each contract boundary.
2. Validate compatibility routing and migration warning behavior.
3. Validate artifact publication and lineage evidence for release readiness.

---

## 6. Recommended Execution Priorities

1. Lock baseline contracts and acceptance traceability first.
2. Build runtime config and service-binding foundations before workflow dispatch changes.
3. Deliver artifact contracts before migration and closeout gates.
4. Delay release closeout until observability evidence is complete.

This ordering minimizes rework and reduces late-phase risk concentration.

---

## 7. Success Criteria for Phase 4 Upgrade

Phase 4 is successful when:

1. Runtime behavior is deterministic from config load through workflow completion.
2. Agent-to-model and task-to-owner binding failures are caught preflight or at deterministic dispatch boundaries.
3. Artifact outputs are contract-governed and lineage-backed.
4. Legacy workflows run through explicit adapter controls with migration evidence.
5. Acceptance criteria are fully mapped to verifiable test and evidence outputs.

