# Alt Phase 2 Build Plan: Multi-Agent Memory as an Additive Mode

**Status:** Proposed for Approval
**Date:** 2026-02-14
**Target:** Implement namespace-isolated multi-agent memory with arbitrated shared promotion, while preserving single-agent behavior and avoiding forced `friday.py` migration.
**References:**
- `docs/design/agents/Alt-Phase-2/agent-contract.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-compliance-matrix.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-schema-spec.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-test-strategy.md`
- `docs/design/agents/Alt-Phase-2/comprehensive-agent-framework-design.md`
- `docs/design/agents/Alt-Phase-2/technical-specifications.md`
- `docs/design/agents/Phase-2/codex-phase-2-build-plan-commentary.md`
- `docs/design/agents/Phase-2/phase-1-build-plan.md`
- AgentSkills reference repository: `https://github.com/agentskills/agentskills/tree/main`
- Additional skill ecosystem reference: `https://github.com/anthropics/skills`

---

## 1. Objectives

1. Add a dedicated **Multi-Agent Memory** mode in `friday-memory`.
2. Keep existing **Single-Agent Memory** mode as default and fully backward compatible.
3. Enforce shared-write zero trust via arbitrator-only promotion.
4. Provide effective atomicity for shared promotion across graph + vector storage.
5. Preserve `friday.py` operation with no mandatory namespace migration.
6. Deliver a clean Phase 3 foundation for orchestration, workflow pause/resume, and replay tooling.
7. Establish Agent Contract compliance foundations required for execution-grade governance.
8. Establish Agent Skill contract foundations with optional declaration, local manifest registry, and strict validation when present.
9. Establish Scratch Pad Memory foundations for private plan/checklist/note/artifact-reference workflows.
10. Establish runtime filesystem topology configuration (`install_root`, `runtime_data_root`, `workspace_root`) and scratch-path placement rules.
11. Establish arbitrator shared-write anti-spoof enforcement via identity + runtime-issued capability validation.
12. Establish migration governance flow (`preflight`, `apply`, `rollback`) for operationally safe rollout.

---

## 2. Non-Negotiable Constraints

1. **No breaking signature changes** to existing core interfaces in Phase 2.
2. **Default behavior unchanged** for single-agent flows (`memory.mode=single_agent`).
3. **Policy enforcement depth** must include lower-level write paths, not only facade methods.
4. **Shared write blocked unless arbitrator path** in multi-agent mode.
5. **Promotion journal required** for effective atomicity and recovery.
6. **Deployment-accurate paths only** in implementation tasks (no source-repository assumptions).
7. **Contract compliance gate required** before Phase 2 exit.
8. **Shared-write authorization must require runtime capability validation**, not identity string alone.

---

## 3. Commentary-Driven Corrections Applied

This plan directly addresses previously identified Phase 2 issues.

1. Status corrected to Proposed for Approval.
2. Namespace rules normalized and scoped to multi-agent mode.
3. Interface-breaking changes removed.
4. Guard coverage widened to all relevant write surfaces.
5. Atomic promotion model made explicit (journaled state machine + recovery).
6. `friday.py` compatibility promoted to first-class acceptance criterion.
7. Phase 1 carryover items included as explicit Phase 2/3 handoff work items.

---

## 4. Scope and Deliverables

## 4.1 In Scope (Alt Phase 2)

1. Multi-agent memory facade and policy subsystem.
2. Arbitration interface/service and proposal staging/journal.
3. Promotion coordinator for graph+vector shared commits.
4. Multi-agent mode runtime wiring.
5. Test harness enhancements for conflicts and shared promotion verification.
6. Backward compatibility and no-regression coverage for single-agent mode and `friday.py`.
7. Contract schema, runtime validation, and compliance test scaffolding.
8. Tool/sandbox policy enforcement for high-impact execution paths.
9. Metadata migration/backfill strategy for multi-agent rollout.
10. Filesystem-backed skill manifest repository/registry baseline, schema, and lifecycle/event governance.
11. Scratch pad memory policy/schema baseline, runtime enforcement, and observability contracts.
12. Skill runtime-profile composition model (profile + task + artifact overlays) with no-expansion governance checks.

## 4.2 Out of Scope (Moved to Phase 3)

1. Full transcript replay integration.
2. Deep operational dashboarding for arbitration metrics.
3. Broad orchestrator UX enhancements beyond minimum integration hooks.

---

## 5. Implementation Plan

## Step 1: Foundation and Config (friday-core + friday-runtime)

### 1.1 Define mode/config contracts

- Add memory mode config (`single_agent`/`multi_agent`) in runtime config model.
- Default to `single_agent`.

### 1.2 Define runtime filesystem topology contracts

- Add required runtime roots:
  - `install_root`,
  - `runtime_data_root`,
  - `workspace_root`.
- Add optional `cache_root`.
- Define startup validation rules for invalid root overlap and non-writable runtime roots.
- Define scratch-path placement rule: persistent scratch storage MUST live under `runtime_data_root`, not `workspace_root` (except test fixture mode).

### 1.3 Add namespace/policy/arbitration interface contracts

- Add additive interfaces in `friday-core` for:
  - namespace policy,
  - multi-agent memory,
  - arbitration contracts.

### 1.4 Preserve existing core ABCs

- No required signature change to:
  - `AgentInterface.initialize_session(...)`
  - `SystemRuntime.spawn_agent(...)`
  - `SystemRuntime.create_session(...)`

Deliverables:

1. Updated interface package exports.
2. Updated runtime config docs.
3. Compatibility tests proving old call patterns still work.
4. Filesystem-topology schema and startup validation tests.

---

## Step 2: Multi-Agent Memory Mode (friday-memory)

### 2.1 Create `multi_agent` module

Target path pattern:

- `packages/friday-memory/src/friday_memory/multi_agent/`

Core components:

1. `controller.py` (MultiAgentMemoryController)
2. `policy.py` (NamespacePolicyEngine)
3. `models.py` (proposal/journal/arbitration models)
4. `journal.py` (durable promotion journal)
5. `coordinator.py` (PromotionCoordinator)

### 2.2 Reuse existing infrastructure

- Compose existing adapters and `CollectionManager`.
- Do not fork lifecycle logic unnecessarily.

### 2.3 Enforce policy at critical write boundaries

In multi-agent mode, enforce namespace/shared-write restrictions at:

1. Facade write methods.
2. Vector collection writes used by ingestion/batch/document paths.
3. Graph edge/node write paths.
4. Promotion coordinator commit path.

### 2.4 Union-read in multi-agent mode

Default retrieval scope in multi-agent mode:

1. active private namespace
2. shared namespace

Single-agent mode retains current retrieval behavior.

Deliverables:

1. Multi-agent module with policy-aware read/write APIs.
2. Namespaced metadata conventions.
3. No-regression for single-agent `MemoryController` tests.

---

## Step 3: Arbitration and Promotion Semantics (friday-agent + friday-memory)

### 3.1 Implement arbitrator service/agent path

- Formalize proposal submission and decision retrieval.
- Add conflict detection strategy hooks.

### 3.1.1 Shared-write capability enforcement

- Require runtime-issued shared-write capability token for arbitrator shared writes.
- Validate capability token scope (`session_id`, `run_id`) and TTL at shared-write boundaries.
- Reject missing/invalid/replayed capabilities and emit structured security/audit events.

### 3.2 Build promotion journal

Journal states:

1. `pending`
2. `graph_written`
3. `vector_written`
4. `committed`
5. `failed`
6. `compensated`

### 3.3 Effective atomicity implementation

Promotion algorithm:

1. Write journal `pending`.
2. Upsert graph shared record idempotently.
3. Upsert vector shared record idempotently.
4. Mark journal `committed`.
5. Expose promoted fact via shared queries only when committed.

### 3.4 Recovery worker

- On startup and scheduled intervals, scan non-terminal journal records and repair.

Deliverables:

1. Arbitration and journal services.
2. Recovery mechanism and idempotency protections.
3. Integration tests for crash/restart promotion recovery.
4. Shared-write anti-spoof tests for identity+capability enforcement.

---

## Step 4: Runtime Wiring (friday-runtime)

### 4.1 Mode-aware memory wiring

- `memory.mode=single_agent` wires existing `MemoryController`.
- `memory.mode=multi_agent` wires MultiAgentMemory stack.

### 4.2 Agent wiring

- Spawn paths stay signature-compatible.
- Multi-agent namespace context is injected through runtime context objects and internal metadata, not required new spawn signature.

### 4.3 Arbitrator availability behavior

In `multi_agent` mode when arbitrator is unavailable:

1. Shared promotion blocked.
2. Private writes remain enabled.
3. Degraded-mode warning/telemetry emitted.

Deliverables:

1. Mode-aware DI composition.
2. Runtime degraded-mode safety behavior.
3. Unit tests for mode switch behavior.

---

## Step 5: Friday Lab Evolution (tests/lab)

### 5.1 Implement real `inject_conflict()` for multi-agent mode

- Update harness to seed contradictory proposals and assert arbitration outcomes.

### 5.2 Security tests

1. Shared-write spoofing blocked.
2. Private namespace leakage blocked.
3. Union-read returns shared + own private only.

### 5.3 Atomicity tests

1. Graph-write success + vector-write failure is non-visible until recovery.
2. Recovery converges to committed or compensated terminal state.

### 5.4 Compatibility tests

1. Existing headless tests pass unchanged in single-agent mode.
2. Existing `FridayContainer` characterization tests remain green.

Deliverables:

1. New multi-agent lab tests.
2. Explicit regression matrix for both modes.

---

## Step 6: `friday.py` Compatibility Track (No Forced Migration)

### 6.1 Keep default mode single-agent

- `friday.py` continues operating against current memory semantics.
- No required namespace parameters or command behavior changes in default path.

### 6.2 Optional future opt-in path

- Document optional future migration to multi-agent mode for specialized deployments.
- Not required for Alt Phase 2 completion.

### 6.3 Validate operational invariants

Regression checks in `friday.py` flows include:

1. session initialization,
2. recall/store loops,
3. extractor behavior,
4. lifecycle/collection-manager operations,
5. ingest command flows.

Deliverables:

1. `friday.py` compatibility verification report.
2. Optional migration notes (non-blocking).

---

## Step 7: Phase 1 Carryover Closure and Phase 3 Handshake

### 7.1 Route decomposition planning hook

- Add explicit Phase 3 backlog entry and design contract for `OrchestratorInterface.route()` decomposition.

### 7.2 FridayContainer disposition decision

- Preserve wrapper in Phase 2 for compatibility.
- Defer final removal decision to Phase 3 transition criteria based on usage telemetry and migration readiness.

### 7.3 Workflow integration contract

- Align arbitration escalation handling with existing `TaskStatus.WAITING_APPROVAL` model.
- Avoid introducing incompatible workflow state enums in Phase 2.
- Define explicit Phase 3 handshake requirement for canonical workflow schema:
  - `WorkflowDefinition` MUST reference one-or-more pipelines,
  - each pipeline MUST define one-or-more tasks.

Deliverables:

1. Phase 3 handoff section completed.
2. No unresolved architectural ambiguity from Phase 1 deferred items.
3. Workflow schema handshake requirements are documented for Phase 3 implementation.

---

## Step 8: Tooling and Sandboxed Execution Governance (friday-tools + friday-runtime)

### 8.1 Tool policy contracts

- Define tool allowlist/denylist/approval/rate-limit policy contracts for agent execution.
- Enforce policy checks before tool invocation.

### 8.2 Sandbox policy contracts

- Define sandbox policy contracts for writable roots, network mode, command allowlist, and limits.
- Require HITL escalation for privileged execution paths.

### 8.3 Enforcement and tests

- Add runtime enforcement hooks and deterministic tests for blocked/approved execution paths.

### 8.4 Workspace boundary enforcement

- Map workspace-policy enforcement points to runtime/tooling layers.
- Add explicit ownership and tests for out-of-scope write rejection.

### 8.5 Code execution lifecycle enforcement

- Enforce execution lifecycle stages (`plan`, `generate`, `precheck`, `execute`, `capture`, `interpret`) in runtime/tooling contracts.
- Require policy-gated transition into `execute` and structured evidence capture before result interpretation.

Deliverables:

1. Tool policy schema and enforcement wiring.
2. Sandbox policy schema and enforcement wiring.
3. Integration tests for privileged execution gating and policy denials.
4. Workspace boundary enforcement map and rejection tests.
5. Code execution lifecycle contract and stage-transition tests.

---

## Step 9: Agent Contract Schema and Runtime Validation (friday-core + friday-agent + friday-runtime)

### 9.1 Schema formalization

- Add `AgentContract` and sub-policy schemas (`ModelPolicy`, `ToolPolicy`, `SandboxPolicy`, `GuardrailPolicy`, `EscalationPolicy`, `HITLPolicy`, `ArtifactPolicy`, `LoggingPolicy`, `FailurePolicy`, `SkillRef`, `SkillManifest`, `SkillRegistryEntry`).

### 9.2 Validation enforcement

- Validate contracts on agent registration/load.
- Fail fast on missing required fields.
- Add mode-aware validation logic.

### 9.3 Compliance test scaffolding

- Add contract schema validation tests and negative-case fixtures.

### 9.4 Unified bounded execution gate

- Enforce startup/runtime validation that required contract domains are present (`workspace`, `tool`, `sandbox`, `guardrail`, `failure`, and HITL when required).
- Fail fast when mandatory policy domains are absent for the selected agent mode.

### 9.5 Skill baseline validation

- Treat `skills` as optional contract field; if declared, require pinned references (`skill_id@version`) and registry resolution.
- Enforce that resolved skill manifests are semver-valid and policy-compatible with agent tool/sandbox/HITL constraints.
- Validate that skill lifecycle events are emitted for skill-enabled agents.

### 9.6 Local filesystem-backed skill manifest repository baseline

- Define canonical local storage paths:
  - `skills/<skill_id>/<version>/SKILL.md`
  - `skills/manifests/<skill_id>/<version>.yaml`
  - `skills/registry/index.yaml`
- Define registry lifecycle states and transitions: `proposed -> approved -> deprecated -> retired`.
- Enforce production-like execution gate: only `approved` skills are executable.
- Define fail-fast behavior for unknown refs, missing versions, and status-policy conflicts.
- Define required approval metadata for `proposed -> approved` transitions:
  - `approval_id`,
  - `approved_by`,
  - `approved_at`,
  - `change_reason`.

### 9.7 Canonical skill conformance validation and CI gates

- Require `skills-ref validate` for each canonical `SKILL.md` at pre-approval and production-like release checkpoints.
- Add CI checks for:
  - `SKILL.md` frontmatter/schema validity,
  - canonical skill directory and naming conventions,
  - deterministic `SKILL.md -> manifest/registry` field mapping validity.
- Require validator/CI outputs as release evidence artifacts.

### 9.8 Skill profile composition and approval-impact gating

- Implement runtime composition pipeline:
  - load Agent Contract baseline,
  - apply skill profile/task/artifact overlays,
  - compute restrictive effective governance envelope.
- Implement policy-diff classifier for skill changes:
  - `content_only`,
  - `behavioral`,
  - `governance_touching`.
- Enforce approval path by impact class and reject policy-expansion attempts.
- Emit composition and classification telemetry for auditability.

### 9.9 AI-Agent Implementation Readiness (Decision-Complete Build Packet)

This plan is intended to be executable by an implementation agent without additional architecture decisions.

Required implementation inputs:

1. Canonical schema contracts from `agent-contract-schema-spec.md`.
2. Technical invariants and failure codes from `technical-specifications.md`.
3. Compliance and evidence gates from `agent-contract-test-strategy.md`.
4. AgentSkills schema-validation reference from `https://github.com/agentskills/agentskills/tree/main`.
5. Skills compatibility profile from `skills-compatibility-profile.md`.

Required implementation outputs:

1. Runtime resolver path that validates canonical `SKILL.md` artifacts before activation.
2. CI gate implementations for skill schema/layout/mapping checks.
3. Release evidence artifacts for validator output and conformance reports.
4. Deterministic failure-path handling for invalid refs, schema violations, layout drift, and mapping conflicts.
5. Deterministic composition engine outputs for profile/task/artifact overlays.
6. Deterministic impact-classification and approval-gate enforcement outputs.

No-open-decision defaults for implementation agents:

1. Canonical skill artifact path: `skills/<skill_id>/<version>/SKILL.md`.
2. Governance overlay paths:
   - `skills/manifests/<skill_id>/<version>.yaml`
   - `skills/registry/index.yaml`
3. Compatibility mode default in production-like profiles: `strict`.
4. Compatibility mode policy by environment:
   - `strict` mandatory in non-development environments (`staging`, `preprod`, `production`),
   - `advisory` allowed only in explicit development/test profiles.
5. Lifecycle execution default: only `approved` skills are executable.
6. Validation tool default: `skills-ref validate`.
7. Composition default: skills may replace profile/task/artifact soft fields but cannot expand contract hard-governance envelope.
8. Classifier default on ambiguity: escalate to higher-impact class.

### 9.8 Scratch pad policy and schema baseline

- Define `ScratchPadPolicy` schema and optional `scratch_pad_policy` contract field.
- Define typed scratch entries (`plan`, `plan_item`, `note`, `artifact_ref`, `event_log`).
- Enforce scratch scope identity `(session_id, agent_id)` and private access semantics.
- Enforce TTL/retention and quota policy checks (`max_entries`, `max_note_bytes`).
- Enforce explicit promotion gate for scratch-to-durable memory operations.
- Define backend semantics and policy:
  - `in_memory` for ephemeral/dev,
  - `sqlite` for production-like restart continuity.
- Define runtime scratch config knobs:
  - `backend`,
  - `path`,
  - `purge_interval_seconds`,
  - `fallback_mode`.

Deliverables:

1. Contract schemas and validator interfaces.
2. Runtime contract validation on agent load.
3. Compliance tests for invalid/partial contract definitions.
4. Unified bounded-execution startup gate and regression tests.
5. Skill schema and policy-compatibility validation for skill-enabled agents.
6. Local filesystem-backed skill manifest repository + registry index contract and validation checks.
7. Canonical skill conformance validation gates (`skills-ref`, schema/layout/mapping CI checks) and evidence artifacts.
8. Scratch pad policy/schema contract and validation checks.
9. Scratch backend/path validation checks with runtime-root placement enforcement.

---

## Step 10: Metadata Migration and Backfill (friday-memory + runtime ops)

### 10.1 Migration strategy

- Define migration plan for legacy records lacking multi-agent metadata fields.
- Include reversible rollout and rollback criteria.
- Define mandatory preflight stage with:
  - legacy inventory counts by store/domain,
  - namespace-stamping policy validation,
  - rollback checkpoint validation,
  - readiness/blocking outcome report.
- Block apply stage unless preflight status is `ready`.

### 10.2 Validation and observability

- Validate query correctness in mixed migrated/unmigrated datasets.
- Emit structured migration events for auditability.

Deliverables:

1. Migration/backfill plan document.
2. Migration preflight report contract and sample outputs.
3. Query correctness test suite for migrated data.
4. Rollback and operational runbook entries.

---

## Step 11: Observability Event Contract (friday-telemetry)

### 11.1 Required event schema

- Define mandatory events for tool calls, sandbox execution, policy checks, HITL transitions, and failure outcomes.
- Define mandatory events for skill lifecycle transitions where `skills` are enabled, including resolved `skill_ref` and manifest version metadata.
- Define mandatory events for scratch pad lifecycle/mutations (`scratchpad_created`, `scratchpad_plan_updated`, `scratchpad_item_status_changed`, `scratchpad_note_added`, `scratchpad_artifact_ref_added`, `scratchpad_expired`, `scratchpad_promoted`).
- Define mandatory events for filesystem/scratch configuration validation failures.
- Define mandatory events for shared-write anti-spoof rejections and capability validation outcomes.
- Define mandatory migration governance events for `preflight`, `apply`, `validate`, and `rollback` stages.

### 11.2 Completeness gates

- Add log-completeness validation thresholds and CI checks.

Deliverables:

1. Event schema contract and field definitions.
2. Log-completeness tests linked to phase exit criteria.

---

## 6. Verification Strategy

## 6.1 Acceptance Criteria

1. Single-agent mode remains default and backward compatible.
2. `friday.py` runs unchanged in default mode.
3. Non-arbitrator shared writes are blocked in multi-agent mode.
4. Cross-agent private reads are blocked.
5. Shared promotion is visible only post-commit.
6. Recovery converges interrupted promotions.
7. Existing Phase 1 lab and compatibility tests still pass.
8. New multi-agent tests pass with deterministic outcomes.
9. Agent contracts are validated at load time with fail-fast behavior.
10. Tool/sandbox policy enforcement is verified for high-impact operations.
11. Metadata migration/backfill passes correctness and rollback checks.
12. Required observability events meet completeness thresholds.
13. Workspace boundary enforcement is validated for out-of-scope operations.
14. Execution-result integrity checks pass for sandboxed runs.
15. Contract checklist-to-CI evidence artifact mapping is published for release candidates.
16. Skill-enabled agents pass pinned-reference validation, manifest resolution checks, and lifecycle event completeness checks.
17. Scratch pad-enabled agents pass scope/TTL/quota/promotion validation and event completeness checks.
18. Runtime filesystem topology and scratch path placement validation pass in startup/runtime checks.
19. Shared-write anti-spoof checks pass (identity + capability required).
20. Migration apply is blocked without successful preflight and rollback checkpoint readiness.
21. Skill `proposed -> approved` transitions enforce required approval metadata.
22. Skill-enabled release candidates include successful `skills-ref validate` outputs for canonical `SKILL.md` artifacts.
23. Skill-enabled release candidates pass canonical `SKILL.md` schema/layout/mapping CI gates.
24. Skill validation outputs are present in checklist-to-CI evidence bundles.
25. Skill composition no-expansion checks pass for tool/sandbox/HITL/workspace governance envelopes.
26. Skill impact classification and approval-path enforcement checks pass for changed skill versions.

## 6.2 Test Matrix

| Category | Single-Agent Mode | Multi-Agent Mode |
| :--- | :--- | :--- |
| Existing `MemoryController` behavior | Must pass unchanged | N/A (wrapped/adapted) |
| `friday.py` regression suite | Must pass unchanged | Optional future work |
| Namespace isolation | N/A | Required |
| Shared-write gating | N/A | Required |
| Promotion atomicity/recovery | N/A | Required |
| Workflow escalation mapping | Existing behavior | Must map to current task-status model |
| Agent contract schema validation | Optional | Required |
| Tool policy enforcement | Optional | Required |
| Sandbox policy enforcement | Optional | Required |
| Metadata migration/backfill validation | N/A | Required |
| Observability event completeness | Optional | Required |
| Workspace boundary enforcement | Existing behavior | Required |
| Execution-result integrity | Optional | Required |
| Code execution lifecycle stage enforcement | Optional | Required |
| Checklist-to-CI evidence artifact set | Optional | Required |
| Skill reference and manifest resolution (`skill_id@version`) | Optional | Required (when skills declared) |
| Skill schema and tool-chain compatibility | Optional | Required (when skills declared) |
| Skill lifecycle event completeness | Optional | Required (when skills declared) |
| Canonical `SKILL.md` reference validation (`skills-ref validate`) | Optional | Required (when skills declared) |
| Canonical `SKILL.md` schema/layout/mapping CI conformance | Optional | Required (when skills declared) |
| Scratch pad scope/retention/quota enforcement | Optional | Required (when scratch pad enabled) |
| Scratch pad lifecycle event completeness | Optional | Required (when scratch pad enabled) |
| Filesystem-root topology validation | Optional | Required |
| Scratch persisted-path placement validation | Optional | Required (when scratch backend is persistent) |
| Shared-write anti-spoof (identity + capability) | N/A | Required |
| Migration preflight/apply/rollback governance | N/A | Required |
| Skill approval-authority metadata validation | Optional | Required (when skills declared) |

---

## 7. Execution Order

| Order | Package/Area | Action | Depends On |
| :--- | :--- | :--- | :--- |
| 1 | `friday-core`, `friday-runtime` | Add mode/config and additive interfaces | — |
| 2 | `friday-memory` | Add multi-agent module and policy engine | 1 |
| 3 | `friday-memory`, `friday-agent` | Add arbitration and promotion journal/coordinator | 2 |
| 4 | `friday-runtime` | Wire mode-aware DI and degraded-mode behavior | 3 |
| 5 | `tests/lab` | Add conflict/security/atomicity tests | 4 |
| 6 | `tests/integration/memory/friday.py` validation | Confirm no-change compatibility path | 4 |
| 7 | `friday-tools`, `friday-runtime` | Add tool/sandbox governance contracts and enforcement | 4 |
| 8 | `friday-core`, `friday-agent`, `friday-runtime` | Add agent-contract schema and runtime validation | 7 |
| 9 | `friday-agent`, `friday-runtime` | Add skill schema validation, canonical `SKILL.md` conformance gating, manifest registry baseline, and lifecycle enforcement | 8 |
| 10 | `friday-memory`, `friday-agent`, `friday-runtime` | Add scratch pad contracts, scope/TTL enforcement, and promotion gating | 8 |
| 11 | `friday-runtime`, `friday-memory` | Add filesystem-topology config and scratch-path placement validation | 8, 10 |
| 12 | `friday-agent`, `friday-runtime`, `friday-memory` | Add arbitrator identity+capability enforcement and anti-spoof tests | 3, 4 |
| 13 | `friday-memory`, runtime ops | Add migration preflight/apply/rollback strategy and checks | 8 |
| 14 | `friday-telemetry` | Add observability event contract and completeness checks | 8, 9, 10, 11, 12, 13 |
| 15 | Docs/handoff | Finalize Phase 3 transition contracts and compliance gates | 5, 6, 14 |

---

## 8. Risk Register

1. Risk: policy bypass via lower-level write paths.
   - Mitigation: enforce at storage-boundary adapters and add bypass tests.
2. Risk: promotion journal complexity.
   - Mitigation: start with minimal deterministic state machine and strong observability.
3. Risk: dual-mode maintenance burden.
   - Mitigation: shared primitives + strict boundaries + mode-specific wrappers only.
4. Risk: ambiguity about `FridayContainer` lifecycle.
   - Mitigation: explicit Phase 3 decision gate and telemetry-backed disposition.
5. Risk: contract drift between architecture/spec/build docs.
   - Mitigation: contract-linked exit gates and compliance-matrix reviews at each phase checkpoint.
6. Risk: legacy data incompatibility during multi-agent rollout.
   - Mitigation: reversible migration/backfill strategy with rollback validation.
7. Risk: skill sprawl without governance.
   - Mitigation: local manifest registry baseline with lifecycle-state governance and pinned-reference enforcement.
8. Risk: scratch pad misuse as de facto durable memory.
   - Mitigation: TTL/quotas, explicit promotion-only durability, and policy-denial telemetry.
9. Risk: workspace clutter from runtime-state storage.
   - Mitigation: enforce runtime-data/workspace root separation and startup path validation.
10. Risk: identity spoofing for arbitrator shared writes.
   - Mitigation: runtime-issued capability requirement and scope/TTL validation at every shared-write boundary.
11. Risk: migration apply starts with incomplete readiness validation.
   - Mitigation: mandatory preflight-ready gate with rollback checkpoint requirement.

---

## 9. Exit Criteria Checklist

1. Multi-agent mode is implemented and disabled by default.
2. Single-agent mode remains default and stable.
3. `friday.py` requires no namespace changes in default path.
4. Shared write restrictions are enforced and tested in multi-agent mode.
5. Promotion journal and recovery logic are verified under failure scenarios.
6. Phase 1 deferred transition items are documented with concrete Phase 3 handoff.
7. Phase 3 transition document is complete and consistent with this plan.
8. Agent contract schema validation and load-time enforcement are implemented.
9. Tool and sandbox policy governance is implemented for high-impact execution paths.
10. Metadata migration/backfill plan is validated with rollback readiness.
11. Observability event contract is implemented and tested for completeness.
12. Workspace boundary policy enforcement is implemented and tested.
13. Execution-result integrity validation is implemented for sandboxed operations.
14. Code execution lifecycle semantics are implemented and verified.
15. Checklist-to-CI evidence artifact set is produced and reviewed at release checkpoint.
16. Optional `skills` contract behavior is implemented with strict pinned-reference and registry validation when present.
17. Skill lifecycle event contract is implemented for skill-enabled agents.
18. Local filesystem-backed skill manifest repository and lifecycle-state governance are documented and validated.
19. Scratch pad scope/TTL/quota/promotion policy controls are implemented and validated.
20. Scratch pad lifecycle/mutation observability contract is implemented and tested.
21. Runtime filesystem topology (`install_root`, `runtime_data_root`, `workspace_root`) is implemented and validated.
22. Scratch persistent path placement rules are implemented and validated (workspace disallowed except test fixture mode).
23. Shared-write anti-spoof enforcement is implemented and validated.
24. Migration preflight/apply/rollback governance is implemented and validated.
25. Skill approval-authority metadata enforcement is implemented and validated.
