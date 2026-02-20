# Alt Phase 3 File Impact Manifest (Pre-Implementation)

**Status:** Proposed for Approval  
**Date:** 2026-02-18  
**Source Plan:** `docs/design/agents/Alt-Phase-2/phase-3-execution-plan.md`  
**Build Source:** `docs/design/agents/Alt-Phase-2/phase-3-build-plan.md`

---

## 1. Usage

This manifest is a scope-control artifact for Phase 3 execution.

Use it to:

1. pre-approve likely file touch points by subphase,
2. reduce context loss for implementation agents,
3. flag high-coupling files before edits begin,
4. constrain implementation to approved impact surfaces.

---

## 2. Impact Categories

1. `Create`: new files/directories expected.
2. `Modify`: existing files likely to change.
3. `Conditional`: depends on implementation approach or adapter choice.

---

## 3. Subphase File Impact

## Subphase 0: Phase 3 Baseline Lock and Transition Handshake

Create:

1. `docs/design/agents/Alt-Phase-2/subphase-artifacts/phase-3/subphase-0/`

Modify:

1. `docs/design/agents/Alt-Phase-2/phase-3-execution-plan.md` (if approved clarifications are folded in)
2. `docs/design/agents/Alt-Phase-2/phase-3-file-impact-manifest.md` (scope-lock refinements)

Conditional:

1. `docs/design/agents/Alt-Phase-2/README.md` (cross-reference updates)

---

## Subphase 1: Orchestrator Route Completion and Workflow-Arbitration Coupling

Modify:

1. `packages/friday-agent/src/friday_agent/orchestrator.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `packages/friday-agent/src/friday_agent/workflows/models.py`
4. `packages/friday-agent/src/friday_agent/workflows/loader.py`
5. `packages/friday-runtime/src/friday_runtime/kernel.py`
6. `packages/friday-runtime/src/friday_runtime/di.py`

Create/Modify tests:

1. `packages/friday-agent/tests_agent/test_orchestrator.py`
2. `packages/friday-agent/tests_agent/test_workflows.py`
3. `tests/lab/test_headless_execution.py`

---

## Subphase 2: HITL Protocol, Authority Enforcement, and Artifact Governance

Modify:

1. `packages/friday-agent/src/friday_agent/workflows/models.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `packages/friday-runtime/src/friday_runtime/kernel.py`
4. `packages/friday-runtime/src/friday_runtime/di.py`
5. `packages/friday-core/src/friday_core/interfaces/runtime.py` (additive only, if needed)

Conditional (artifact layer ownership-dependent):

1. `packages/friday-tools/src/friday_tools/` (artifact publication/policy helpers)
2. `tests/integration/` artifact governance suites

Create/Modify tests:

1. `packages/friday-agent/tests_agent/test_workflows.py`
2. `tests/lab/` HITL authority and timeout suites

---

## Subphase 3: Replay, Transcript Correlation, and Operations Hardening

Modify:

1. `packages/friday-transcript/` store/correlation modules
2. `packages/friday-telemetry/src/friday_telemetry/` event schemas/interfaces
3. `packages/friday-memory/src/friday_memory/multi_agent/` replay/correlation hooks
4. `packages/friday-agent/src/friday_agent/workflows/engine.py`

Conditional:

1. `docs/` ops runbook locations (if centralized outside Alt-Phase-2 docs)
2. `tests/integration/` replay/forensics suites

---

## Subphase 4: Skill Orchestration, Delegation, and Federation Compatibility

Modify:

1. `packages/friday-agent/src/friday_agent/registry.py`
2. `packages/friday-agent/src/friday_agent/loader.py`
3. `packages/friday-agent/src/friday_agent/workflows/engine.py`
4. `packages/friday-runtime/src/friday_runtime/kernel.py`
5. `packages/friday-runtime/src/friday_runtime/di.py`

Conditional (if repository-managed local skill catalog remains in-repo):

1. `skills/registry/index.yaml`
2. `skills/manifests/`
3. `skills/<skill_id>/<version>/SKILL.md`

Create/Modify tests:

1. `packages/friday-agent/tests_agent/` skill delegation and compatibility tests
2. `tests/lab/` skill federation and no-expansion governance tests

---

## Subphase 5: Scratch Pad Orchestration and Workflow State Mapping

Modify:

1. `packages/friday-memory/src/friday_memory/multi_agent/` scratch/workflow mapping hooks
2. `packages/friday-agent/src/friday_agent/workflows/models.py`
3. `packages/friday-agent/src/friday_agent/workflows/engine.py`
4. `packages/friday-runtime/src/friday_runtime/config.py`
5. `packages/friday-runtime/src/friday_runtime/di.py`

Create/Modify tests:

1. `packages/friday-memory/tests_memory/` scratch integration suites
2. `packages/friday-agent/tests_agent/test_workflows.py`
3. `tests/lab/` workflow-to-scratch mapping suites

---

## Subphase 6: Filesystem Topology Governance and Deployment Profiles

Modify:

1. `packages/friday-runtime/src/friday_runtime/config.py`
2. `packages/friday-runtime/src/friday_runtime/di.py`
3. `packages/friday-runtime/src/friday_runtime/kernel.py`
4. `packages/friday-sandbox/` path-policy enforcement modules (if needed)

Conditional:

1. deployment profile docs under `docs/`.
2. container/cloud configuration templates.

Create/Modify tests:

1. `packages/friday-runtime/tests_runtime/` topology/path validation suites
2. `tests/integration/` workspace contamination and runtime path conformance suites

---

## Subphase 7: Pipeline/Task Model Completion and Dispatch Semantics

Modify:

1. `packages/friday-agent/src/friday_agent/workflows/models.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `packages/friday-agent/src/friday_agent/workflows/loader.py`
4. `packages/friday-runtime/src/friday_runtime/kernel.py`
5. `packages/friday-core/src/friday_core/interfaces/runtime.py` (additive if required)

Create/Modify tests:

1. `packages/friday-agent/tests_agent/test_workflows.py`
2. `tests/lab/` dispatch/lease/recovery suites
3. `tests/integration/` cross-pipeline typed handoff and lineage validation suites

---

## Subphase 8: Compliance Gates, Release Evidence, and Phase-3 Closeout Decisions

Modify:

1. `docs/design/agents/Alt-Phase-2/agent-contract-test-strategy.md` (if gate details are tightened)
2. `docs/design/agents/Alt-Phase-2/agent-contract-compliance-matrix.md` (if residual gaps are closed)
3. `docs/design/agents/Alt-Phase-2/phase-3-transition-plan.md` (closeout annotations)
4. `docs/design/agents/Alt-Phase-2/README.md` (artifact references)

Conditional:

1. CI workflow definitions for checklist-to-evidence enforcement.
2. release checklist templates under docs or operations folder.

---

## 4. Cross-Subphase High-Probability Files

These files are likely to be touched in multiple subphases:

1. `packages/friday-agent/src/friday_agent/workflows/models.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `packages/friday-runtime/src/friday_runtime/config.py`
4. `packages/friday-runtime/src/friday_runtime/di.py`
5. `packages/friday-runtime/src/friday_runtime/kernel.py`
6. `packages/friday-memory/src/friday_memory/multi_agent/`
7. `tests/lab/`

---

## 5. Pre-Execution Risk Notes

1. Highest coupling risk: workflow-state semantics (`models.py`) and dispatch behavior (`engine.py`).
2. Highest compatibility risk: `friday.py` default-path stability during runtime/orchestrator changes.
3. Highest governance risk: skill federation extension accidentally weakening strict compatibility and no-expansion checks.
4. Highest operational risk: filesystem topology drift in container/cloud profiles.

---

## 6. Scope-Lock Approval Checklist

1. Confirm all `Conditional` directories are in approved scope before execution.
2. Confirm cross-subphase high-probability files are reviewed before each subphase.
3. Confirm per-subphase artifact triad is mandatory and enforced.
4. Confirm full gates run after each subphase and baseline debt is tracked separately.
5. Confirm Phase 3 closeout requires checklist-to-evidence bundle and explicit decision records.
