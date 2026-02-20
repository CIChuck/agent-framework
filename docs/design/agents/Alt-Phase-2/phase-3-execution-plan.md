# Alt Phase 3 Execution Plan (AI-Executable Subphases)

**Status:** Proposed for Approval  
**Date:** 2026-02-18  
**Source Plan:** `docs/design/agents/Alt-Phase-2/phase-3-build-plan.md`  
**Companion Input:** `docs/design/agents/Alt-Phase-2/phase-3-transition-plan.md`  
**Purpose:** Decompose the large Phase 3 build plan into bounded, low-context subphases that an AI implementation agent can execute continuously without architectural signal loss.

---

## 1. Execution Model

This execution plan is workflow-managed and context-preserving by design.

Execution rules:

1. One subphase executes at a time.
2. Every subphase has explicit inputs, outputs, dependencies, and gate checks.
3. Subphase completion is evidence-based, not narrative-based.
4. No subphase may violate non-negotiable constraints from the Phase 3 build and transition plans.
5. All compatibility assumptions from Alt Phase 2 remain active unless explicitly superseded by approved Phase 3 policy.

Non-negotiable constraints carried forward:

1. `single_agent` remains default runtime mode.
2. `multi_agent` remains explicit opt-in mode.
3. No mandatory `friday.py` migration path in default mode.
4. Orchestrator/arbitrator separation remains intact.
5. Skill validation and no-governance-expansion semantics remain enforced.
6. Scratch pad remains operational/private memory, not ungoverned durable memory.

---

## 2. Context-Preservation Protocol

Every subphase MUST publish to `docs/design/agents/Alt-Phase-2/subphase-artifacts/subphase-<n>/`:

1. `subphase-summary.md`
   - completed scope,
   - decisions made,
   - unresolved risks,
   - changed files.
2. `verification-summary.md`
   - full gate results,
   - targeted test results,
   - blocked checks and rationale.
3. `next-subphase-brief.md`
   - assumptions carried forward,
   - required inputs,
   - blockers and dependency notes.

Minimum gate cadence:

1. Run full gates after every subphase.
2. Record baseline debt separately from subphase regressions.
3. Do not proceed to next subphase if new regression is introduced.

Standard full gate command set:

1. `.venv/bin/pytest -q`
2. `ruff check .`
3. `if [ -x .venv/bin/mypy ]; then .venv/bin/mypy packages apps tests; else echo "MYPY_MISSING"; fi`

---

## 3. Subphase Breakdown

## Subphase 0: Phase 3 Baseline Lock and Transition Handshake

**Goal:** Lock Phase 3 constraints, inherited invariants, and transition prerequisites before implementation.

Primary sources:

1. `phase-3-build-plan.md` sections 1, 2, 6, 7, 8.
2. `phase-3-transition-plan.md` sections 1, 2, 3, 8, 9.
3. `technical-specifications.md` sections 4.11, 5.3, 5.4.

Execution scope:

1. Confirm all required Phase 2 inputs are available.
2. Confirm workflow/pipeline/task schema baseline is canonical.
3. Confirm no-open-decision defaults for skill governance, HITL, and mode behavior.
4. Classify Phase 2 residual debt into:
   - blocking debt (must be closed before Phase 3 implementation),
   - waiver-eligible debt (can proceed with explicit waiver note and mitigation owner).

Deliverables:

1. Phase 3 baseline constraint matrix.
2. Transition-input readiness checklist.
3. Subphase artifact triad.

Exit criteria:

1. No unresolved ambiguity in transition prerequisites.
2. Any Phase 2 residual debt is explicitly classified as blocking or waiver-eligible with documented owner and mitigation timeline.

---

## Subphase 1: Orchestrator Route Completion and Workflow-Arbitration Coupling

**Goal:** Complete orchestrator route decomposition and arbitration pause/resume integration.

Primary sources:

1. `phase-3-build-plan.md` Workstream A and B.
2. `phase-3-transition-plan.md` sections 4.1 and 4.2.
3. `technical-specifications.md` section 5.3.

Execution scope:

1. Implement route-stage decomposition while preserving existing processing compatibility.
2. Propagate namespace/session context through orchestrator handoff chain.
3. Map arbitration escalations to `TaskStatus.WAITING_APPROVAL` semantics.
4. Implement deterministic resume/reject/resolve flows for escalated tasks.
5. Implement delegation/handoff payload contract enforcement.

Deliverables:

1. Route decomposition implementation checklist.
2. Workflow-arbitration integration tests.
3. Delegation/handoff payload validation tests.
4. Subphase artifact triad.

Exit criteria:

1. Escalated tasks pause/resume deterministically with auditable transitions.

---

## Subphase 2: HITL Protocol, Authority Enforcement, and Artifact Governance

**Goal:** Implement execution-grade HITL contract behavior and artifact lifecycle controls.

Primary sources:

1. `phase-3-build-plan.md` Workstream E and F.
2. `phase-3-transition-plan.md` section 4.5.
3. `agent-contract.md`, `agent-contract-schema-spec.md`, `agent-contract-test-strategy.md`.

Execution scope:

1. Implement HITL request/response payload contract.
2. Enforce `awaiting_human` lifecycle with timeout/default actions.
3. Enforce approver scope/authority model (`HITLAuthorityPolicy`).
4. Enforce artifact lifecycle states and publication controls.

Deliverables:

1. HITL state-machine conformance tests.
2. Authority-validation and audit-event tests.
3. Artifact lifecycle governance tests.
4. Subphase artifact triad.

Exit criteria:

1. HITL and artifact policy behavior is deterministic and auditable.

---

## Subphase 3: Replay, Transcript Correlation, and Operations Hardening

**Goal:** Make multi-agent execution replayable, diagnosable, and production-operable.

Primary sources:

1. `phase-3-build-plan.md` Workstream C and D.
2. `phase-3-transition-plan.md` sections 4.3 and 4.4.

Execution scope:

1. Implement replay for proposal/promotion timeline forensics.
2. Correlate transcripts with proposal/promotion IDs.
3. Add metrics/alerts for arbitration/recovery and degraded mode.
4. Publish degraded-mode and remediation runbook artifacts.

Deliverables:

1. Replay/audit trace implementation and tests.
2. Metrics and alert contract checklist.
3. Degraded-mode runbook updates.
4. Subphase artifact triad.

Exit criteria:

1. Failure and recovery paths are reconstructable end-to-end from emitted evidence.

---

## Subphase 4: Skill Orchestration, Delegation, and Federation Compatibility

**Goal:** Complete dynamic skill routing/delegation while preserving strict compatibility semantics.

Primary sources:

1. `phase-3-build-plan.md` Workstream H.
2. `phase-3-transition-plan.md` section 4.5.
3. `skills-compatibility-profile.md`.

Execution scope:

1. Implement dynamic skill routing against declared contract skills.
2. Enforce scope-boundary delegation and handoff behavior.
3. Enforce federated/remote registry extension without changing `skill_id@version` runtime reference semantics.
4. Preserve canonical AgentSkills validation gates (`skills-ref validate`, schema/layout/mapping checks).
5. Preserve no-governance-expansion composition semantics in delegated/federated flows.

Deliverables:

1. Skill routing/delegation implementation checklist.
2. Federation compatibility and policy-control test suite.
3. Canonical skill conformance evidence requirements.
4. Subphase artifact triad.

Exit criteria:

1. Delegated and federated skill activation cannot bypass local governance controls.

---

## Subphase 5: Scratch Pad Orchestration and Workflow State Mapping

**Goal:** Integrate scratch pad operational memory with orchestration, workflow, and HITL transitions.

Primary sources:

1. `phase-3-build-plan.md` Workstream I.
2. `phase-3-transition-plan.md` sections 4.5 and 8.
3. `technical-specifications.md` sections 4.8 and 5.4.

Execution scope:

1. Map workflow task states to scratch `plan_item` status transitions.
2. Persist HITL pause/resume checkpoints into scratch `event_log`.
3. Enforce scope isolation, TTL, quota behavior under orchestration load.
4. Implement replay correlation between workflow history and scratch events.
5. Validate persistent-backend recovery and fallback behavior.

Deliverables:

1. Scratch-aware orchestration integration tests.
2. Workflow-to-scratch mapping conformance tests.
3. Scratch replay/audit evidence outputs.
4. Subphase artifact triad.

Exit criteria:

1. Scratch integration is deterministic, isolated, and policy-compliant under load/recovery.

---

## Subphase 6: Filesystem Topology Governance and Deployment Profiles

**Goal:** Enforce runtime path governance across local, container, and cloud execution modes.

Primary sources:

1. `phase-3-build-plan.md` Workstream J.
2. `phase-3-transition-plan.md` sections 4.5 and 8.
3. `technical-specifications.md` section 2.2.

Execution scope:

1. Validate three-root topology (`install_root`, `runtime_data_root`, `workspace_root`) in orchestrated runs.
2. Enforce artifact writes to `workspace_root` only.
3. Enforce runtime state writes (journals, indexes, scratch persistence) to `runtime_data_root`.
4. Validate path-overlap rejection and remediation behavior.
5. Add deployment templates and profile defaults.

Deliverables:

1. Topology conformance test suite.
2. Deployment profile templates.
3. Path-governance runbook updates.
4. Subphase artifact triad.

Exit criteria:

1. No policy-compliant run can contaminate workspace/runtime roots.

---

## Subphase 7: Pipeline/Task Model Completion and Dispatch Semantics

**Goal:** Complete executable workflow hierarchy contracts and dispatch behavior.

Primary sources:

1. `phase-3-build-plan.md` Workstream K.
2. `technical-specifications.md` section 4.11.

Execution scope:

1. Implement canonical `workflow -> pipeline -> task` hierarchy validation.
2. Implement dispatch semantics for dependency-ready tasks.
3. Implement assignment claim/lease/recovery semantics.
4. Implement reusable pipeline composition semantics.
5. Enforce typed cross-pipeline handoff contract validation.

Deliverables:

1. Workflow/pipeline/task schema and cardinality conformance tests.
2. Dispatch determinism and lease recovery test suite.
3. Cross-pipeline typed handoff and lineage evidence outputs.
4. Subphase artifact triad.

Exit criteria:

1. Hierarchy integrity, dispatch determinism, and typed handoff validation are all green.

---

## Subphase 8: Compliance Gates, Release Evidence, and Phase-3 Closeout Decisions

**Goal:** Finalize contract gates, release evidence, and deferred policy decisions.

Primary sources:

1. `phase-3-build-plan.md` sections 4, 5, 6, 8.
2. `phase-3-transition-plan.md` sections 5, 6, 8.
3. `agent-contract-compliance-matrix.md`.

Execution scope:

1. Implement contract KPI/checklist release gates.
2. Publish checklist-to-evidence release bundle requirements.
3. Validate `friday.py` default-path stability.
4. Execute `FridayContainer` decision gate with migration/rollback evidence.
5. Validate exit criteria across dual-mode, skills, scratch, HITL, and pipeline contracts.

Deliverables:

1. Final Phase 3 evidence bundle template and required artifact list.
2. `friday.py` compatibility report.
3. `FridayContainer` disposition decision record.
4. Subphase artifact triad.

Exit criteria:

1. Phase 3 exit criteria are satisfied with auditable evidence and no open governance blockers.

---

## 4. Mapping Back to Phase 3 Workstreams

| Execution Subphase | Phase 3 Build Workstream Coverage |
| :--- | :--- |
| Subphase 0 | Preconditions + Constraints + Transition Handshake |
| Subphase 1 | Workstream A, Workstream B |
| Subphase 2 | Workstream E, Workstream F |
| Subphase 3 | Workstream C, Workstream D |
| Subphase 4 | Workstream H |
| Subphase 5 | Workstream I |
| Subphase 6 | Workstream J |
| Subphase 7 | Workstream K |
| Subphase 8 | Workstream G + `friday.py` policy + FridayContainer decision gate |

---

## 5. Cross-Document Validation Matrix (Alt-Phase-2 Set)

This execution plan was validated for consistency against the current Alt-Phase-2 documents.

| Document | Required Signal | Preservation in Phase 3 Execution Plan |
| :--- | :--- | :--- |
| `phase-3-build-plan.md` | All workstreams A-K represented and sequenced | Subphases 1-8 map one-to-one/one-to-many to A-K |
| `phase-3-transition-plan.md` | Transition prerequisites and sequencing honored | Subphase 0 lock + dependency ordering throughout |
| `technical-specifications.md` | Canonical workflow/pipeline/task + state-machine semantics | Subphase 1/2/5/7 enforce section 4.11 + 5.x alignment |
| `agent-contract.md` | HITL, artifact, governance, bounded execution semantics | Subphase 2 and Subphase 8 gate on contract evidence |
| `agent-contract-schema-spec.md` | Schema/version/validation invariants preserved | Subphase 2/4/5/7 include schema conformance coverage |
| `agent-contract-test-strategy.md` | Verification layering and gate evidence model | Context-preservation protocol + per-subphase gates |
| `agent-contract-compliance-matrix.md` | Identified precision gaps addressed in execution | Subphase 4/5/6/8 explicitly carry remaining gaps |
| `skills-compatibility-profile.md` | Strict compatibility + canonical skill validation | Subphase 4 enforces `skills-ref` and no-expansion policy |
| `phase-2-build-plan.md` + `phase-2-execution-plan.md` | Phase 2 decisions/invariants remain intact | Non-negotiable constraints section + gated carryover |

Validation conclusion:

1. No contradictions detected with the current Alt-Phase-2 architecture/governance baseline.
2. All Phase 3 build workstreams are represented with executable boundaries.
3. Transition-plan prerequisites are explicitly carried forward as Subphase 0 gate requirements.

---

## 6. Risk Assessment for Executing This Decomposed Phase 3 Plan

## 6.1 Overall Risk Posture

1. Feasibility: High
2. Coordination Risk: Medium-High
3. Architecture Drift Risk: Medium
4. Compatibility Regression Risk (`single_agent` default path): Medium

## 6.2 Primary Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Cross-subphase contract drift | Medium | High | Mandatory artifact triad + cross-doc validation matrix at every close |
| Workflow/state model divergence | Medium | High | Anchor to `technical-specifications.md` section 4.11 + 5.x invariants |
| Skill federation bypass of governance | Medium | High | Subphase 4 strict conformance gates + no-expansion checks |
| Scratch pad misuse as durable memory | Medium | Medium | Subphase 5 TTL/quota/promotion gates + replay checks |
| Deployment path contamination | Medium | High | Subphase 6 topology tests + overlap rejection gates |
| Exit criteria not evidence-backed | Medium | High | Subphase 8 release evidence bundle and checklist enforcement |

## 6.3 Phase Gates (Must Pass)

1. Gate A (after Subphase 0): Transition prerequisites and baseline constraints locked.
2. Gate B (after Subphase 2): HITL/authority/artifact governance deterministic and auditable.
3. Gate C (after Subphase 4): Skill delegation/federation cannot bypass validation/governance.
4. Gate D (after Subphase 7): Workflow/pipeline/task contracts and dispatch semantics are deterministic.
5. Gate E (after Subphase 8): All Phase 3 exit criteria are evidenced and approved.

---

## 7. AI-Agent Assignment Pattern (Recommended)

For each subphase, keep ownership bounded:

1. Contract owner: schema/policy invariants.
2. Runtime owner: orchestration and execution semantics.
3. Verification owner: tests, evidence, and gate reporting.

Handoff order per subphase:

1. Contract owner publishes `subphase-summary.md`.
2. Runtime owner updates implementation + validates constraints.
3. Verification owner publishes `verification-summary.md` and `next-subphase-brief.md`.

---

## 8. Assumptions and Locked Defaults

Assumptions used:

1. All Phase 2 baseline contracts are treated as required dependencies for Phase 3 implementation.
2. Execution remains non-destructive for default single-agent path unless explicitly flagged.
3. Skill federation is compatibility-preserving extension, not a replacement for local canonical contracts.

Locked defaults:

1. Subphase 8 does not require a formal approver roster for `FridayContainer` disposition signoff.
2. Federated skill catalogs are enabled in the first Phase 3 release candidate.
3. Phase-level KPI thresholds are warning-only for the first release cycle.
