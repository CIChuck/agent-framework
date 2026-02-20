# Alt Phase 2 File Impact Manifest (Pre-Implementation)

**Status:** Proposed for Approval  
**Date:** 2026-02-16  
**Source Plans:**  
- `docs/design/agents/Alt-Phase-2/phase-2-build-plan.md`  
- `docs/design/agents/Alt-Phase-2/phase-2-execution-plan.md`  

**Purpose:** Provide a strict, reviewable file-impact checklist (by subphase) before executing implementation work.

---

## 1. Usage

1. Treat this as a preflight scope-control artifact.
2. Before starting each subphase, confirm intended edits are within listed files.
3. If a subphase requires files outside this manifest, add them first via doc update and approval.

---

## 2. Impact Categories

1. `MODIFY`: existing files expected to change.
2. `CREATE`: new files/directories expected to be added.
3. `MAYBE`: conditional files depending on implementation strategy.

---

## 3. Subphase File Impact

## Subphase 0: Baseline and Guardrails

`MODIFY`:
1. `packages/friday-core/src/friday_core/config.py`
2. `packages/friday-core/src/friday_core/profiles.py`
3. `packages/friday-runtime/src/friday_runtime/config.py`

`MAYBE`:
1. `packages/friday-core/src/friday_core/interfaces/runtime.py`
2. `packages/friday-runtime/src/friday_runtime/__init__.py`

---

## Subphase 1: Multi-Agent Memory Core

`CREATE`:
1. `packages/friday-memory/src/friday_memory/multi_agent/__init__.py`
2. `packages/friday-memory/src/friday_memory/multi_agent/controller.py`
3. `packages/friday-memory/src/friday_memory/multi_agent/policy.py`
4. `packages/friday-memory/src/friday_memory/multi_agent/models.py`
5. `packages/friday-memory/src/friday_memory/multi_agent/journal.py`
6. `packages/friday-memory/src/friday_memory/multi_agent/coordinator.py`

`MODIFY`:
1. `packages/friday-memory/src/friday_memory/__init__.py`
2. `packages/friday-core/src/friday_core/interfaces/memory.py`
3. `packages/friday-memory/src/friday_memory/controller/memory_controller.py`

`MAYBE`:
1. `packages/friday-memory/src/friday_memory/context/assembler.py`
2. `packages/friday-memory/src/friday_memory/context/consolidator.py`
3. `packages/friday-memory/src/friday_memory/context/extractor.py`

---

## Subphase 2: Arbitration, Promotion, and Recovery

`MODIFY`:
1. `packages/friday-agent/src/friday_agent/orchestrator.py`
2. `packages/friday-core/src/friday_core/interfaces/agent.py`
3. `packages/friday-core/src/friday_core/interfaces/memory.py`
4. `packages/friday-runtime/src/friday_runtime/kernel.py`
5. `packages/friday-memory/src/friday_memory/multi_agent/journal.py`
6. `packages/friday-memory/src/friday_memory/multi_agent/coordinator.py`
7. `packages/friday-memory/src/friday_memory/multi_agent/models.py`

`MAYBE`:
1. `packages/friday-agent/src/friday_agent/registry.py`
2. `packages/friday-agent/src/friday_agent/base.py`

---

## Subphase 3: Runtime Wiring and Compatibility Execution Path

`MODIFY`:
1. `packages/friday-runtime/src/friday_runtime/di.py`
2. `packages/friday-runtime/src/friday_runtime/kernel.py`
3. `packages/friday-runtime/src/friday_runtime/config.py`
4. `packages/friday-cli/src/friday_cli/container.py`

`MAYBE`:
1. `packages/friday-cli/src/friday_cli/repl.py`
2. `packages/friday-cli/src/friday_cli/commands.py`

---

## Subphase 4: Governance Policies and Contract Validation

`MODIFY`:
1. `packages/friday-core/src/friday_core/interfaces/agent.py`
2. `packages/friday-core/src/friday_core/interfaces/runtime.py`
3. `packages/friday-agent/src/friday_agent/loader.py`
4. `packages/friday-agent/src/friday_agent/registry.py`
5. `packages/friday-runtime/src/friday_runtime/kernel.py`
6. `packages/friday-runtime/src/friday_runtime/di.py`

`MAYBE`:
1. `packages/friday-tools/src/friday_tools/memory/inspection.py`
2. `packages/friday-tools/src/friday_tools/memory/maintenance.py`
3. `packages/friday-agent/src/friday_agent/tools/registry.py`

---

## Subphase 5: Skills, Scratch Pad, and Filesystem Governance

`MODIFY`:
1. `packages/friday-agent/src/friday_agent/loader.py`
2. `packages/friday-agent/src/friday_agent/registry.py`
3. `packages/friday-runtime/src/friday_runtime/config.py`
4. `packages/friday-runtime/src/friday_runtime/kernel.py`
5. `packages/friday-core/src/friday_core/interfaces/agent.py`
6. `packages/friday-core/src/friday_core/interfaces/runtime.py`

`CREATE`:
1. `skills/registry/index.yaml` (if repository-managed bootstrap is part of implementation)
2. `skills/manifests/` directory structure (if repository-managed bootstrap is part of implementation)

`MAYBE`:
1. `packages/friday-memory/src/friday_memory/multi_agent/` files for scratch integration details
2. `packages/friday-agent/src/friday_agent/workflows/models.py` (if skill impact-class checks are wired through workflow state)

---

## Subphase 6: Migration and Observability

`MODIFY`:
1. `packages/friday-memory/src/friday_memory/multi_agent/models.py`
2. `packages/friday-memory/src/friday_memory/multi_agent/journal.py`
3. `packages/friday-runtime/src/friday_runtime/kernel.py`
4. `packages/friday-core/src/friday_core/telemetry.py`

`MAYBE`:
1. `packages/friday-telemetry/src/friday_telemetry/interface.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`

---

## Subphase 7: Verification, Release Evidence, and Phase-3 Handoff

`MODIFY`:
1. `tests/lab/harness.py`
2. `tests/lab/test_headless_execution.py`
3. `tests/lab/test_legacy_compatibility.py`
4. `packages/friday-memory/tests_memory/test_controller.py`
5. `packages/friday-agent/tests_agent/test_workflows.py`
6. `tests/integration/memory/friday.py`

`MAYBE`:
1. `tests/lab/test_delegation_chain.py`
2. `tests/integration/memory/friday_chat/commands/workflow_cmds.py`

---

## 4. Cross-Subphase High-Probability Files

These files are expected to be touched across multiple subphases:

1. `packages/friday-runtime/src/friday_runtime/kernel.py`
2. `packages/friday-runtime/src/friday_runtime/config.py`
3. `packages/friday-runtime/src/friday_runtime/di.py`
4. `packages/friday-core/src/friday_core/interfaces/agent.py`
5. `packages/friday-core/src/friday_core/interfaces/memory.py`
6. `packages/friday-agent/src/friday_agent/registry.py`
7. `packages/friday-agent/src/friday_agent/workflows/models.py`

---

## 5. Pre-Execution Risk Notes

1. The highest drift risk is unplanned edits in `packages/friday-runtime/src/friday_runtime/kernel.py` because many subphases converge there.
2. The highest regression risk is broad edits in `packages/friday-cli/src/friday_cli/container.py` and `tests/integration/memory/friday.py`.
3. The highest coupling risk is between skill governance and workflow state changes (`packages/friday-agent/src/friday_agent/workflows/models.py` and `packages/friday-agent/src/friday_agent/workflows/engine.py`).

---

## 6. Approval Checklist for Scope Lock

Before implementation begins, confirm:

1. This file-impact manifest is approved as execution scope guard.
2. Any file not listed here requires explicit addendum before editing.
3. Subphase owners understand `MODIFY` vs `MAYBE` semantics.
4. Verification owner is assigned to enforce scope adherence per subphase.
