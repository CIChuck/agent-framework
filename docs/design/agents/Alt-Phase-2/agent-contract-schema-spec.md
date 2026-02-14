# Agent Contract Schema Specification

**Status:** Proposed for Approval
**Date:** 2026-02-14
**Purpose:** Define canonical schema contracts and validation invariants for `AgentContract` and policy submodels.
**Primary References:**
- `docs/design/agents/Alt-Phase-2/agent-contract.md`
- `docs/design/agents/Alt-Phase-2/technical-specifications.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-compliance-matrix.md`

---

## 1. Scope

This specification standardizes schema definitions for:

1. `AgentContract`
2. `ModelPolicy`
3. `ToolPolicy`
4. `SandboxPolicy`
5. `HITLPolicy`
6. `HITLAuthorityPolicy`
7. `GuardrailPolicy`
8. `EscalationPolicy`
9. `ArtifactPolicy`
10. `LoggingPolicy`
11. `FailurePolicy`

---

## 2. Schema Baseline

Canonical field definitions follow `technical-specifications.md` section `4.6` and are normative for Phase 2/3 planning.

### 2.1 Required Top-Level Fields

1. Identity: `agent_id`, `name`, `role`, `backstory`
2. Mission: `goals`, `objectives`, `success_criteria`, `stop_conditions`
3. Mode: `mode`, `memory_mode`
4. Governance: `model_policy`, `tool_policy`, `sandbox_policy`, `guardrail_policy`, `escalation_policy`, `hitl_policy`, `artifact_policy`, `logging_policy`, `failure_policy`

### 2.2 Policy-Specific Required Fields

1. `ToolPolicy.allowed_tools`
2. `SandboxPolicy.required`, `writable_roots`, `network_mode`, `timeout_seconds`
3. `GuardrailPolicy.scope_rules`, `safety_rules`, `data_rules`, `execution_rules`, `authority_rules`
4. `EscalationPolicy.trigger_classes`, `mandatory_approval_actions`, `default_escalation_method`
5. `HITLPolicy.methods`, `timeout_seconds`, `default_action_on_timeout`, `authority_policy`
6. `HITLAuthorityPolicy.allowed_roles`
7. `ArtifactPolicy.lifecycle_states`
8. `LoggingPolicy.required_events`
9. `FailurePolicy.max_retries`, `backoff_strategy`

---

## 3. Validation Invariants

1. `semi_autonomous` and `copilot` agents MUST have `hitl_policy.enabled == true`.
2. Agents that execute generated code MUST have `sandbox_policy.required == true`.
3. `ArtifactPolicy.lifecycle_states` MUST include `draft` and `final`.
4. `LoggingPolicy.required_events` MUST include tool, sandbox, policy, and HITL events.
5. `ToolPolicy.approval_required_tools` MUST include privileged execution classes where applicable.
6. `HITLAuthorityPolicy.allowed_roles` MUST be non-empty when HITL is enabled.
7. `EscalationPolicy.trigger_classes` MUST include low-confidence, policy-ambiguity, and high-impact triggers.

---

## 4. Versioning and Compatibility

1. Schema versioning MUST use semantic versioning (`major.minor.patch`).
2. Backward-compatible additions increment `minor`.
3. Breaking field/semantic changes increment `major` and require migration notes.
4. Runtime MUST reject unknown major versions unless explicitly compatibility-mapped.

---

## 5. Validation Failure Behavior

1. Agent registration/load fails fast on missing required fields.
2. Validation errors MUST include:
   - field path,
   - failed rule,
   - remediation hint.
3. Validation failures MUST emit structured telemetry events.

---

## 6. Ownership and Lifecycle

| Area | Owner | Phase |
| :--- | :--- | :--- |
| Core schema contract | `friday-core` | Phase 2 |
| Runtime enforcement | `friday-runtime` | Phase 2 |
| HITL policy semantics | `friday-agent/workflows` | Phase 3 |
| Tool/sandbox policy semantics | `friday-tools` + `friday-runtime` | Phase 2 |
| Guardrail/escalation policy semantics | `friday-agent` + `friday-runtime` | Phase 2+3 |
| Artifact policy semantics | workspace/artifact layer | Phase 3 |

---

## 7. Acceptance Criteria

1. Schema definitions are published and referenced by technical specs.
2. Runtime validation is enabled at agent load.
3. Contract validation test suite covers positive and negative cases.
4. Schema-version compatibility behavior is documented and tested.
