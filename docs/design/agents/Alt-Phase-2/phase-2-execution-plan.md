# Alt Phase 2 Execution Plan (AI-Executable Subphases)

**Status:** Proposed for Approval
**Date:** 2026-02-16
**Source Plan:** `docs/design/agents/Alt-Phase-2/phase-2-build-plan.md`
**Purpose:** Decompose the large Phase 2 build plan into discrete, low-context subphases that can be executed by AI agents without losing architectural intent.

---

## 1. Execution Model

This plan assumes one subphase is executed at a time with explicit handoff artifacts.

Subphase execution rules:

1. Each subphase has bounded scope and explicit inputs/outputs.
2. Each subphase must publish a handoff summary before the next begins.
3. No subphase may change architecture assumptions established by prior approved subphases.
4. Default compatibility constraints remain in force:
   - `single_agent` mode remains default,
   - no breaking interface signatures,
   - no forced `friday.py` migration,
   - policy no-expansion rules apply.

---

## 2. Context-Preservation Protocol

Every subphase MUST produce:

1. `subphase-summary.md`:
   - scope completed,
   - decisions made,
   - unresolved risks,
   - references to changed files.
2. `verification-summary.md`:
   - tests/checks run,
   - pass/fail status,
   - known gaps.
3. `next-subphase-brief.md`:
   - assumptions carried forward,
   - required inputs for next subphase,
   - blocked dependencies (if any).

---

## 3. Subphase Breakdown

## Subphase 0: Baseline and Guardrails

**Goal:** Lock non-negotiable constraints and baseline compatibility behavior.

Primary source sections:

1. `phase-2-build-plan.md` Step 1 and constraints sections.
2. `agent-contract.md` core rules and compatibility expectations.
3. `technical-specifications.md` compatibility and additive-interface constraints.

Execution scope:

1. Confirm baseline assumptions and non-breaking requirements.
2. Confirm default-mode behavior (`single_agent`) and `friday.py` no-change path.
3. Confirm runtime root model (`install_root`, `runtime_data_root`, `workspace_root`).

Deliverables:

1. Baseline constraint matrix.
2. Compatibility test baseline checklist.
3. Subphase handoff artifacts.

Exit criteria:

1. No unresolved ambiguity around compatibility/non-breaking constraints.

---

## Subphase 1: Multi-Agent Memory Core

**Goal:** Implement additive multi-agent memory module shape and namespace policy engine behavior.

Primary source sections:

1. `phase-2-build-plan.md` Step 2.
2. `technical-specifications.md` interfaces and namespace policy sections.

Execution scope:

1. Define/confirm multi-agent module components:
   - controller,
   - policy,
   - models,
   - journal,
   - coordinator.
2. Enforce policy boundaries at memory write/read surfaces.
3. Preserve single-agent memory behavior unchanged.

Deliverables:

1. Multi-agent memory component implementation checklist.
2. Namespace enforcement test checklist.
3. Subphase handoff artifacts.

Exit criteria:

1. Policy-aware read/write behavior defined and verifiable.
2. Single-agent no-regression path remains intact.

---

## Subphase 2: Arbitration, Promotion, and Recovery

**Goal:** Finalize shared-memory promotion semantics with journaled effective atomicity.

Primary source sections:

1. `phase-2-build-plan.md` Step 3.
2. `technical-specifications.md` arbitration/promotion schemas and state machines.

Execution scope:

1. Proposal submission and decision path.
2. Shared-write identity + capability enforcement.
3. Promotion journal lifecycle (`pending` -> terminal states).
4. Recovery/replay strategy for non-terminal journal records.

Deliverables:

1. Promotion lifecycle and failure-mode implementation checklist.
2. Anti-spoof enforcement test checklist.
3. Subphase handoff artifacts.

Exit criteria:

1. Shared truth visibility only after committed promotion.
2. Recovery semantics are deterministic and auditable.

---

## Subphase 3: Runtime Wiring and Compatibility Execution Path

**Goal:** Wire mode-aware runtime behavior and preserve backward compatibility.

Primary source sections:

1. `phase-2-build-plan.md` Step 4, Step 6, Step 7.
2. `phase-3-transition-plan.md` handshake requirements.

Execution scope:

1. Mode-aware DI wiring for `single_agent` vs `multi_agent`.
2. Arbitrator unavailable degraded mode behavior.
3. `friday.py` default-path compatibility validation.
4. Phase 3 handshake anchors (workflow/task-state compatibility and schema handshake notes).

Deliverables:

1. Runtime mode-switch behavior checklist.
2. `friday.py` compatibility report template.
3. Subphase handoff artifacts.

Exit criteria:

1. Default runtime behavior unchanged for existing users.
2. Multi-agent mode remains explicit opt-in.

---

## Subphase 4: Governance Policies and Contract Validation

**Goal:** Establish contract-enforced tool/sandbox/guardrail/failure policy surface.

Primary source sections:

1. `phase-2-build-plan.md` Step 8 and Step 9.
2. `agent-contract-schema-spec.md`.
3. `agent-contract-test-strategy.md`.

Execution scope:

1. Policy schema enforcement at load/register time.
2. Tool/sandbox/workspace boundary governance.
3. Code-execution lifecycle stage contract.
4. Unified bounded-execution gate.

Deliverables:

1. Contract validation suite checklist.
2. Policy enforcement and denial-path checklist.
3. Subphase handoff artifacts.

Exit criteria:

1. Fail-fast behavior for invalid contract/policy combinations.
2. Deterministic policy denial behavior in runtime.

---

## Subphase 5: Skills, Scratch Pad, and Filesystem Governance

**Goal:** Finalize skill runtime-profile model and scratch/FS policy surfaces.

Primary source sections:

1. `phase-2-build-plan.md` Step 9.5 through Step 9.9.
2. `skills-compatibility-profile.md`.
3. `agent-contract.md` skill composition and approval classes.
4. `technical-specifications.md` skill/scratch schemas.

Execution scope:

1. `SKILL.md` canonical resolution and validator gating.
2. Profile/task/artifact overlay composition with no-expansion enforcement.
3. Skill impact-class approval gating (`content_only`, `behavioral`, `governance_touching`).
4. Scratch-pad policy/schema/runtime behavior.
5. Runtime filesystem topology/path-placement enforcement.

Deliverables:

1. Skill conformance + composition enforcement checklist.
2. Scratch policy and lifecycle checklist.
3. Filesystem topology compliance checklist.
4. Subphase handoff artifacts.

Exit criteria:

1. Skill activation governed by strict compatibility in non-dev.
2. Scratch remains operational memory, not ungoverned durable memory.

---

## Subphase 6: Migration and Observability

**Goal:** Complete migration governance and event-contract coverage.

Primary source sections:

1. `phase-2-build-plan.md` Step 10 and Step 11.
2. `technical-specifications.md` migration lifecycle and evidence mapping.

Execution scope:

1. Migration `preflight` / `apply` / `rollback` governance.
2. Rollback checkpoint requirement and integrity checks.
3. Required event schema coverage for memory/policy/HITL/skills/scratch/migration.

Deliverables:

1. Migration governance implementation checklist.
2. Observability completeness checklist.
3. Subphase handoff artifacts.

Exit criteria:

1. Apply blocked when preflight readiness is not satisfied.
2. Required event completeness gates defined and measurable.

---

## Subphase 7: Verification, Release Evidence, and Phase-3 Handoff

**Goal:** Consolidate acceptance criteria, CI evidence, and release-readiness posture.

Primary source sections:

1. `phase-2-build-plan.md` verification strategy, execution order, exit checklist.
2. `agent-contract-test-strategy.md`.
3. `agent-contract-compliance-matrix.md`.

Execution scope:

1. Execute/validate full Phase 2 acceptance matrix.
2. Produce checklist-to-evidence artifact bundle.
3. Confirm Phase 3 handoff prerequisites are satisfied.

Deliverables:

1. Phase 2 release candidate evidence bundle.
2. Phase 3 handoff packet.
3. Final subphase handoff artifacts.

Exit criteria:

1. All Phase 2 exit criteria green.
2. Phase 3 entry assumptions explicitly documented.

---

## 4. Suggested AI-Agent Assignment Pattern

For each subphase, use one agent with bounded ownership:

1. Contract owner (schema/policy invariants).
2. Runtime owner (wiring/mode behavior).
3. Verification owner (tests/evidence).

Handoff sequence:

1. Contract owner publishes `subphase-summary.md`.
2. Runtime owner validates constraints and updates `verification-summary.md`.
3. Verification owner publishes `next-subphase-brief.md`.

---

## 5. Mapping Back to Original Phase 2 Steps

| Subphase | Original Step Coverage |
| :--- | :--- |
| 0 | Step 1 + constraints |
| 1 | Step 2 |
| 2 | Step 3 |
| 3 | Step 4, Step 6, Step 7 |
| 4 | Step 8 + Step 9.1-9.4 |
| 5 | Step 9.5-9.9 |
| 6 | Step 10 + Step 11 |
| 7 | Section 6, 7, 9 (verification/ordering/exit) |

---

## 6. Signal-Preservation Matrix

This matrix ensures no critical intent from `phase-2-build-plan.md` is dropped in decomposition.

| Source Signal | Preservation in Execution Plan |
| :--- | :--- |
| Multi-agent memory is additive; single-agent remains default | Subphase 0, 1, 3 exit criteria and compatibility constraints |
| No breaking interface signatures | Subphase 0 baseline constraints and Subphase 3 runtime compatibility checks |
| Shared-write zero trust via arbitrator path | Subphase 2 scope and anti-spoof tests |
| Effective atomicity and recovery required | Subphase 2 promotion lifecycle + recovery exit criteria |
| `friday.py` no forced migration | Subphase 0 and Subphase 3 explicit compatibility tracks |
| Tool/sandbox/workspace governance required | Subphase 4 policy scope and fail-fast criteria |
| Skill governance (`SKILL.md`, strict non-dev, no policy expansion) | Subphase 5 composition and approval-impact gating |
| Scratch pad operational memory controls | Subphase 5 scratch policy/lifecycle scope |
| Filesystem topology and path-placement governance | Subphase 0 and Subphase 5 scope |
| Migration governance (`preflight`, `apply`, `rollback`) | Subphase 6 scope and exit criteria |
| Observability/event completeness gates | Subphase 6 coverage and Subphase 7 release evidence |
| Phase 3 handshake readiness | Subphase 3 and Subphase 7 handoff criteria |

Signal-preservation checks required at each subphase close:

1. Confirm mapped source signals were addressed with evidence links.
2. Confirm no newly introduced behavior violates non-negotiable constraints.
3. Confirm unresolved risks are explicitly carried to `next-subphase-brief.md`.

---

## 7. Risk Assessment for Executing This Decomposed Plan

This section assesses execution risk only; it does not authorize execution.

## 7.1 Overall Risk Posture

1. **Feasibility:** High
2. **Coordination Risk:** Medium
3. **Architecture Drift Risk:** Medium-Low (with strict handoff artifacts)
4. **Regression Risk (single-agent/default path):** Medium

## 7.2 Primary Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Cross-subphase context loss | Medium | High | Mandatory handoff artifact triad (`subphase-summary`, `verification-summary`, `next-subphase-brief`) |
| Policy or compatibility drift | Medium | High | Subphase 0 baseline lock + no-open-decision defaults carried forward |
| Hidden coupling between memory/runtime/governance work | Medium | Medium | Fixed subphase order and explicit dependency mapping |
| Late discovery of validation gaps | Medium | Medium | Subphase 4 and 5 shift validation/governance left before final consolidation |
| Incomplete migration readiness | Low-Medium | High | Dedicated Subphase 6 with preflight gate and rollback evidence |
| Phase 3 handoff ambiguity | Medium | Medium | Subphase 3 handshake anchors + Subphase 7 release packet requirement |

## 7.3 Risk Gates (Must Pass Before Advancing)

1. **Gate A (after Subphase 0):** compatibility/non-breaking baseline approved.
2. **Gate B (after Subphase 3):** runtime mode behavior and `friday.py` compatibility evidence approved.
3. **Gate C (after Subphase 5):** skill/scratch/filesystem governance evidence approved.
4. **Gate D (after Subphase 6):** migration and observability gates approved.
5. **Gate E (after Subphase 7):** full exit checklist and release evidence bundle complete.

## 7.4 Residual Risks at Plan Close

1. KPI/SLO numeric threshold tuning remains implementation-environment specific.
2. Operational runbook depth may need package-level expansion during build execution.
3. Governance owner responsiveness may impact approval throughput for high-impact skill changes.

---

## 8. Feasibility Assessment

This decomposition is accomplishable and appropriate for AI-agent execution.

Why this works:

1. Scope is segmented by stable architectural boundaries.
2. Dependencies are explicit and linearized where possible.
3. Context is preserved via required handoff artifacts.
4. Each subphase has measurable exit criteria to prevent drift.
