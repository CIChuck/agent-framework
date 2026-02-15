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
12. `SkillRef`
13. `SkillManifest`
14. `SkillRegistryEntry`
15. `ScratchPadPolicy`
16. `ScratchPadEntry` (`PlanEntry`, `PlanItemEntry`, `NoteEntry`, `ArtifactRefEntry`, `ScratchEventEntry`)
17. Runtime filesystem topology schema (`FilesystemTopologyConfig`) for deployment-safe storage placement

---

## 2. Schema Baseline

Canonical field definitions follow `technical-specifications.md` section `4.6` and are normative for Phase 2/3 planning.

### 2.1 Required Top-Level Fields

1. Identity: `agent_id`, `name`, `role`, `backstory`
2. Mission: `goals`, `objectives`, `success_criteria`, `stop_conditions`
3. Mode: `mode`, `memory_mode`
4. Governance: `model_policy`, `tool_policy`, `sandbox_policy`, `guardrail_policy`, `escalation_policy`, `hitl_policy`, `artifact_policy`, `logging_policy`, `failure_policy`
5. Skills (optional): `skills`
6. Scratch pad (optional): `scratch_pad_policy`

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
10. `ScratchPadPolicy.enabled`, `retention_ttl_seconds`, `max_entries`, `max_note_bytes`, `allow_promotion`

### 2.3 Skill-Specific Required Fields (When `skills` Are Declared)

1. `AgentContract.skills` entries MUST be `SkillRef` values in `skill_id@version` format.
2. `SkillManifest.skill_id`
3. `SkillManifest.version`
4. `SkillManifest.status` (`proposed`, `approved`, `deprecated`, `retired`)
5. `SkillManifest.owner`
6. `SkillManifest.triggers`
7. `SkillManifest.goal_state`
8. `SkillManifest.tool_chain`
9. `SkillManifest.context_requirements`
10. `SkillManifest.invariants`
11. `SkillManifest.outputs`
12. `SkillManifest.scope_boundary`
13. `SkillManifest.handoff_policy`
14. `SkillRegistryEntry.manifest_path`
15. `SkillRegistryEntry.review_metadata`

### 2.4 Runtime Filesystem Topology Fields (Runtime Config Domain)

1. `filesystem.install_root`
2. `filesystem.runtime_data_root`
3. `filesystem.workspace_root`
4. `filesystem.cache_root` (optional)
5. `memory.scratch_pad.backend`
6. `memory.scratch_pad.path` (required when backend is persistent)
7. `memory.scratch_pad.fallback_mode`
8. `memory.scratch_pad.purge_interval_seconds`

---

## 3. Validation Invariants

1. `semi_autonomous` and `copilot` agents MUST have `hitl_policy.enabled == true`.
2. Agents that execute generated code MUST have `sandbox_policy.required == true`.
3. `ArtifactPolicy.lifecycle_states` MUST include `draft` and `final`.
4. `LoggingPolicy.required_events` MUST include tool, sandbox, policy, and HITL events.
5. `ToolPolicy.approval_required_tools` MUST include privileged execution classes where applicable.
6. `HITLAuthorityPolicy.allowed_roles` MUST be non-empty when HITL is enabled.
7. `EscalationPolicy.trigger_classes` MUST include low-confidence, policy-ambiguity, and high-impact triggers.
8. If `skills` are declared, every `SkillRef` MUST be pinned and semver-valid (`skill_id@major.minor.patch`).
9. Every `SkillRef` MUST resolve to an existing `SkillManifest` via `SkillRegistryEntry`.
10. Runtime execution in production-like environments MUST require `SkillManifest.status == approved`.
11. If `skills` are declared, every tool in `SkillManifest.tool_chain` MUST be present in `ToolPolicy.allowed_tools`.
12. Skill outputs that produce artifacts MUST satisfy `ArtifactPolicy` and workspace boundary rules.
13. Skill steps classified as privileged execution MUST honor HITL approval requirements when configured.
14. `retired` skill versions MUST be rejected at resolution time.
15. Skill lifecycle transitions MUST follow `proposed -> approved -> deprecated -> retired`.
16. If scratch pad is enabled, scope identity MUST include both `session_id` and `agent_id`.
17. If scratch pad is enabled, cross-agent scratch access MUST be denied by default.
18. `ScratchPadPolicy.retention_ttl_seconds` MUST be > 0.
19. `ScratchPadPolicy.max_entries` and `max_note_bytes` MUST be positive.
20. Scratch promotion to durable memory MUST be blocked when `ScratchPadPolicy.allow_promotion == false`.
21. Runtime config MUST define `filesystem.runtime_data_root` and `filesystem.workspace_root` as distinct roots.
22. Scratch persisted path MUST resolve under `filesystem.runtime_data_root` when backend is persistent.
23. Scratch persisted path MUST NOT resolve under `filesystem.workspace_root` except explicit test-mode fixture configuration.
24. Runtime config MUST be deployment-git-agnostic (no requirement for source-repository presence).

---

## 4. Versioning and Compatibility

1. Schema versioning MUST use semantic versioning (`major.minor.patch`).
2. Backward-compatible additions increment `minor`.
3. Breaking field/semantic changes increment `major` and require migration notes.
4. Runtime MUST reject unknown major versions unless explicitly compatibility-mapped.
5. `SkillManifest.version` MUST follow semantic versioning.

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
| Skill schema semantics | `friday-agent` + `friday-core` | Phase 2+3 |
| Skill manifest and registry semantics | `friday-agent` + `friday-runtime` | Phase 2+3 |
| Scratch pad schema semantics | `friday-memory` + `friday-core` | Phase 2+3 |
| Runtime filesystem topology semantics | `friday-runtime` + `friday-core` | Phase 2+3 |

---

## 7. Acceptance Criteria

1. Schema definitions are published and referenced by technical specs.
2. Runtime validation is enabled at agent load.
3. Contract validation test suite covers positive and negative cases.
4. Schema-version compatibility behavior is documented and tested.
5. Skill manifest resolution, lifecycle-state gating, and tool-chain compatibility behavior are documented and tested when `skills` are declared.
6. Scratch pad scope/retention/promotion policy behavior is documented and tested when scratch pad is enabled.
7. Filesystem-root topology and scratch-path placement behavior are documented and tested in runtime validation suites.
