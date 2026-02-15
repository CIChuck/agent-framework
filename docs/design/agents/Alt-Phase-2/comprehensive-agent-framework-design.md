# Friday Agent Framework: Comprehensive Design (Alt Phase 2)

**Status:** Proposed for Approval (Alternative Architecture)
**Date:** 2026-02-14
**Supersedes:** `docs/design/agents/Phase-2/comprehensive-agent-framework-design.md` for alternative planning path only
**Companion Docs:**
- `docs/design/agents/Alt-Phase-2/agent-contract.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-compliance-matrix.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-schema-spec.md`
- `docs/design/agents/Alt-Phase-2/agent-contract-test-strategy.md`
- `docs/design/agents/Alt-Phase-2/technical-specifications.md`
- `docs/design/agents/Alt-Phase-2/phase-2-build-plan.md`
- `docs/design/agents/Alt-Phase-2/phase-3-transition-plan.md`
- `docs/design/agents/Phase-2/codex-phase-2-build-plan-commentary.md`

---

## 1. Executive Summary

This alternate design introduces a **dual durable-memory model** plus a private **scratch pad memory** surface instead of retrofitting global namespace controls into all existing `friday-memory` code paths.

### Core Decision

1. Keep existing memory behavior as **Single-Agent Memory** (default).
2. Add a new **Multi-Agent Memory** mode that composes existing memory infrastructure and introduces:
   - namespace isolation,
   - proposal-based shared-memory promotion,
   - arbitrator-only shared writes,
   - effective atomicity across graph + vector promotion.

### Why This Direction

This design directly addresses major risks identified in `codex-phase-2-build-plan-commentary.md`:

1. Avoids breaking current interfaces (`AgentInterface`, `SystemRuntime`) for Phase 2.
2. Prevents forcing namespace migration into `friday.py`.
3. Reduces regression risk by making multi-agent memory opt-in.
4. Preserves Phase 1 compatibility promises while still enabling arbitration and truth boundaries.

---

## 2. Historical Perspective and Governance

### 2.1 Historical Evolution

1. Baseline path (`docs/design/agents/Phase-2/*`) assumed broad retrofit of namespace/arbitration behavior.
2. Commentary review identified backward-compatibility, enforcement-surface, and migration risk.
3. Alt Phase 2 pivots to additive multi-agent memory mode with single-agent default stability.
4. Agent Contract is now the normative governance model for future planning refinement.

### 2.2 Contract Adoption Milestone

1. `agent-contract.md` defines mandatory operational requirements for all agents.
2. `agent-contract-compliance-matrix.md` tracks clause-level coverage and upgrades across companion docs.
3. Phase 2 and Phase 3 plans must now be evaluated against contract-aligned exit gates.

### 2.3 Maturity Model

1. **Level A (Phase 2 minimum):** memory mode separation, arbitration/promotion integrity, compatibility guarantees, contract schema groundwork, and baseline tool/sandbox execution governance.
2. **Level B (Phase 3 completion):** execution-grade HITL protocol, authority-governed delegation/handoff, artifact governance, and contract KPI gates.
3. **Level C (post-Phase 3 hardening):** operational automation, advanced policy analytics, and long-term deprecation closure.

---

## 3. Design Principles

1. **Backward compatibility first:** Existing single-agent workloads must continue with no namespace requirements.
2. **Additive evolution:** New behavior enters as a mode and new interfaces, not disruptive signature changes.
3. **Single source of policy truth:** Namespace access policy is centralized, not scattered across ad hoc call sites.
4. **Defense in depth:** Shared write restrictions must be enforced below facade-level methods.
5. **Recoverable consistency:** Promotion is implemented as effectively atomic via journaled state transitions and idempotent operations.
6. **Controlled rollout:** Multi-agent memory is feature-flagged and can be enabled per runtime/profile.
7. **Capability modularity:** reusable skills are optional but contract-governed when declared.
8. **Operational memory separation:** execution scratch state remains separate from durable semantic memory.
9. **Deployment portability:** runtime state placement is install/runtime/workspace-root based and must not assume git-repository layouts.

---

## 4. Current Baseline (Post Phase 1)

### Confirmed State

1. `RuntimeKernel` exists and exposes stable signatures for `create_session(user_id)` and `spawn_agent(name)`.
2. `AgentInterface.initialize_session()` preserves optional `session_id` semantics.
3. `MemoryController` and related memory services are heavily used by single-agent flows and `friday.py`.
4. `friday.py` performs manual DI and directly uses memory lifecycle services.
5. Workflow engine currently uses `TaskStatus` + `pending_approval` model.

### Constraint Derived from Baseline

Any Phase 2 design that requires immediate universal namespace plumbing across all memory paths will be high-risk and expensive. This alternate design avoids that coupling.

---

## 5. Target Architecture

## 5.1 Memory Modes

### A. Single-Agent Memory (Default)

- Existing `MemoryController` behavior remains primary default.
- No required namespace context.
- Used by `friday.py` and existing single-agent workflows.

### B. Multi-Agent Memory (New)

- New policy-governed facade using existing memory adapters/services.
- Enforces private/shared namespace boundaries.
- Introduces arbitrated promotion workflow for shared truth.
- Used by orchestrated multi-agent sessions.

### C. Scratch Pad Memory (New, Private Working Memory)

- Private per `(session_id, agent_id)`.
- Stores plan/checklist/notes/artifact references for execution management.
- TTL-governed and operational by design.
- Does not participate in semantic recall unless explicitly promoted.

---

## 5.2 Component Model

### Existing Components Reused

1. Vector/Graph/Episodic adapters.
2. `CollectionManager` lifecycle primitives.
3. Context extraction/consolidation and memory maintenance pipelines.
4. Runtime DI patterns from `friday-runtime`.

### New Components (Alt Phase 2)

1. `MultiAgentMemoryController` (new mode facade).
2. `NamespacePolicyEngine` (read/write permissions).
3. `ProposalJournal` (staging + promotion state).
4. `ArbitrationService` / `ArbitratorAgent` (promotion decision authority).
5. `PromotionCoordinator` (effective atomicity orchestration).
6. `NamespaceContext` propagation helpers (identity + active namespace metadata).

---

## 5.3 Namespace Model

### Namespace Types

1. Private namespace: `<agent_name>-<token>:/`
2. Shared namespace: `shared:/`
3. Arbitrator namespace: `arbitrator:/` (internal queue/audit namespace)

### Key Rules

1. Any non-arbitrator identity is blocked from direct writes to `shared:/`.
2. Private reads are owner-scoped (plus optional explicit allow-list in future phases).
3. Multi-agent reads are union-scoped by default: `[active_private, shared:/]`.
4. Single-agent memory mode does not require namespace and remains unchanged.

---

## 5.4 Shared Truth Promotion Model

### Proposal Flow

1. Agent writes candidate facts/insights into private namespace.
2. Agent submits `MemoryProposal` to arbitrator queue.
3. Arbitrator evaluates confidence/conflict evidence.
4. If promoted, `PromotionCoordinator` performs journaled write sequence for graph + vector shared records.

### Effective Atomicity Strategy

The system does not rely on a cross-store ACID transaction. It enforces effective atomicity via:

1. Durable promotion journal with state machine.
2. Idempotent writes keyed by `proposal_id`/`promotion_id`.
3. Commit visibility only after both graph and vector writes reach committed state.
4. Recovery worker that repairs incomplete promotions on startup.
5. Compensation paths where possible if terminal failure occurs.

---

## 5.5 `friday.py` Impact

### Explicit Goal

`friday.py` remains on Single-Agent Memory mode by default.

### Practical Outcome

1. No namespace plumbing required in `friday.py` to preserve current behavior.
2. No mandatory command-level namespace UX change required for legacy path.
3. Multi-agent namespace UX appears only when runtime is launched in multi-agent mode.
4. Existing manual DI in `friday.py` remains valid in Phase 2.

---

## 5.6 Skill Capability Layer

1. Skills define reusable intent-to-execution patterns over policy-gated tool orchestration.
2. Skills are optional at contract level, preserving backward compatibility for existing agents.
3. Agent contracts reference skills by pinned identifiers (`skill_id@version`), not inline capability definitions.
4. Resolved skills must satisfy tool/sandbox/guardrail/HITL and observability contracts.
5. Skill scope boundaries and handoff behavior align with Phase 3 delegation/handoff architecture.

### Skill Plane Architecture (Phase 2 Baseline)

1. **Local filesystem-backed manifest repository:** `skills/manifests/<skill_id>/<version>.yaml`.
2. **Registry index:** `skills/registry/index.yaml` provides authoritative discovery metadata.
3. **Lifecycle governance:** `proposed -> approved -> deprecated -> retired`.
4. **Execution gate:** production-like execution permits only `approved` skill versions.
5. **Policy boundary:** shared skill catalog with per-agent contract allowlists.

---

## 5.7 Scratch Pad Memory Layer

1. Scratch pad memory is a third memory surface for operational state, distinct from durable single-agent and multi-agent memory.
2. Primary use cases: orchestrator planning, task checklist progression, temporary notes, artifact references, and HITL checkpoint breadcrumbs.
3. Scratch pad retention is TTL-based and policy-governed.
4. Scratch pad access is private by default and denied cross-agent.
5. Promotion into durable memory is explicit and policy-gated.
6. Persistent scratch storage lives in runtime state roots, not task workspaces.

---

## 5.8 Runtime Filesystem Topology Layer

1. The framework defines three required roots:
   - `install_root` (code/package location),
   - `runtime_data_root` (internal writable state),
   - `workspace_root` (agent artifact/intermediary outputs).
2. Optional `cache_root` supports rebuildable caches.
3. Scratch pad persistence and runtime journals are part of internal state and belong under `runtime_data_root`.
4. Workspace remains artifact-centric and MUST NOT be used as a generic runtime-state store.
5. This model is explicitly git-agnostic and supports local installs, containers, and cloud service deployments.

---

## 6. Interface Strategy

## 6.1 Preserve Existing ABC Contracts

The following signatures remain unchanged in Phase 2:

1. `AgentInterface.initialize_session(session_id: str | None = None, user_id: str = "default")`
2. `SystemRuntime.spawn_agent(name: str)`
3. `SystemRuntime.create_session(user_id: str = "default")`

## 6.2 Additive Extensions

New capabilities are introduced through additive interfaces/services, for example:

1. `MultiAgentMemoryInterface`
2. `ArbitrationInterface` (formalized)
3. `NamespacePolicyInterface`

No required breaking changes to existing external contracts in Alt Phase 2.

---

## 7. Commentary Alignment Matrix

This section maps key commentary findings to alternate design responses.

1. Namespace regex/default mismatch:
   - Resolved by keeping namespace policy in multi-agent mode only, with one canonical format.
2. Backward-incompatible interface changes:
   - Avoided in Phase 2. Existing signatures preserved.
3. Guard coverage gaps:
   - Addressed by centralizing enforcement at policy + storage boundary layers, not only `store_fact/store_insight`.
4. Workflow model mismatch (`WorkflowState.PAUSED` vs `TaskStatus`):
   - Alt approach aligns with existing `TaskStatus` and approval pause mechanics.
5. Missing Phase 1 carryover items:
   - Addressed in Alt Phase 2 build plan and Phase 3 transition plan.
6. `friday.py` compatibility under-scoped:
   - Explicitly scoped as no-forced-change in default mode.
7. Atomicity under-specified:
   - Explicit journaled promotion model defined.

---

## 8. Roadmap Alignment

### Phase 2 (Alt): Multi-Agent Memory as Additive Mode

1. Build `MultiAgentMemory` stack and arbitration/promotion path.
2. Keep existing single-agent path stable and default.
3. Add lab tests for namespace isolation, shared write blocking, conflict resolution, and promotion recovery.
4. Add contract schema validation, tool/sandbox governance, and observability event contracts.
5. Add local filesystem-backed skill manifest repository + registry index with pinned reference validation.
6. Add optional skill schema and baseline skill-lifecycle event governance.
7. Add scratch pad memory contracts (scope/TTL/promotion), typed task-board semantics, and observability events.
8. Add runtime filesystem topology contracts and path-validation gates for scratch placement.

### Phase 3 (Direction)

1. Integrate orchestrator-level namespace context with minimal friction.
2. Complete route decomposition and workflow-level arbitration pause/resume integration.
3. Expand observability, replay, and operational tooling on top of stable multi-agent memory foundation.
4. Implement full HITL protocol execution model, approver authority policy, and artifact governance lifecycle.
5. Implement dynamic skill routing/delegation and replay-grade skill auditability.
6. Extend Phase 2 local skill registry to optional remote/federated registry operations.
7. Expand scratch pad integration with workflow replay/analytics and orchestration diagnostics.
8. Harden deployment profiles (local/container/cloud) against path-misconfiguration and workspace contamination.

---

## 9. Risks and Mitigations

1. Risk: two memory modes increase maintenance overhead.
   - Mitigation: shared core services and strict boundary contracts to avoid logic fork.
2. Risk: policy bypass through legacy direct writes.
   - Mitigation: storage-boundary enforcement and explicit multi-agent-only adapters.
3. Risk: promotion inconsistencies across graph/vector stores.
   - Mitigation: durable journal + idempotent writes + startup recovery.
4. Risk: ambiguous rollout behavior.
   - Mitigation: clear config defaults (`single_agent`) and explicit opt-in (`multi_agent`).
5. Risk: contract drift between design/spec/build docs.
   - Mitigation: keep compliance matrix as binding review artifact and add contract-linked exit gates.
6. Risk: skill sprawl and inconsistent capability definitions.
   - Mitigation: registry-governed manifest lifecycle, pinned references, and mandatory policy compatibility checks.
7. Risk: scratch pad grows into ungoverned long-term store.
   - Mitigation: TTL enforcement, explicit promotion-only durability, and quota controls.
8. Risk: runtime state and workspace paths are mixed, causing clutter and governance drift.
   - Mitigation: three-root topology, startup path validation, and workspace contamination tests.

---

## 10. Gap Snapshot (Current Precision Gaps)

The original high-risk omissions identified by the compliance matrix are now represented in this document set:

1. Formal contract schemas and validation references are defined.
2. HITL protocol, authority semantics, and timeout/default behavior are documented.
3. Tool and sandbox governance workstreams are explicit in Phase 2 planning.
4. Metadata migration/backfill strategy is included for multi-agent rollout.
5. Contract KPI/checklist gates are included in Phase 2/3 verification strategy.
6. Skill contract schema, local filesystem-backed manifest repository, and baseline lifecycle governance are represented in Phase 2 planning.
7. Scratch pad scope/retention/promotion governance is represented in Phase 2 planning.
8. Runtime filesystem topology and scratch-path placement governance are represented in specs and phase plans.

Remaining precision work is now narrower:

1. Calibrate and ratify KPI/SLO thresholds by workload class for release gating.
2. Standardize authority-policy templates for organization-level approver models.
3. Keep checklist-to-CI evidence mapping explicit at every release checkpoint.
4. Complete Phase 3 depth for dynamic skill routing/delegation governance and remote-registry federation strategy.
5. Calibrate scratch pad TTL/quota defaults by workload class after pilot runs.
6. Finalize deployment-profile defaults for filesystem roots and scratch backend selection by environment class.

---

## 11. Exit Criteria (Design-Level)

1. Phase 2 docs no longer require breaking interface changes to enable multi-agent memory.
2. `friday.py` remains compatible in default mode with no required namespace migration.
3. Arbitration and promotion semantics are specified with recoverable effective atomicity.
4. Phase 3 transition is explicitly documented and dependent on this additive foundation.
5. Agent Contract and compliance matrix are integrated as normative governance references.
