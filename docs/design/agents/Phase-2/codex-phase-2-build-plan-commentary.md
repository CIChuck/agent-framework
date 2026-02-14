# Codex Commentary: Phase 2 Build Plan Review

## Scope
This commentary reviews `docs/design/agents/Phase-2/phase-2-build-plan.md` against the implemented Phase 1 baseline and related design/spec docs, with focus on correctness, omissions, transition fidelity, and backward compatibility.

Primary references used:
`docs/design/agents/Phase-2/phase-2-build-plan.md`
`docs/design/agents/Phase-2/phase-1-build-plan.md`
`docs/design/agents/Phase-2/technical-specifications.md`
`packages/friday-runtime/src/friday_runtime/kernel.py`
`packages/friday-core/src/friday_core/interfaces/runtime.py`
`packages/friday-core/src/friday_core/interfaces/agent.py`
`packages/friday-agent/src/friday_agent/orchestrator.py`
`packages/friday-agent/src/friday_agent/workflows/models.py`
`packages/friday-agent/src/friday_agent/workflows/engine.py`
`packages/friday-memory/src/friday_memory/controller/memory_controller.py`
`packages/friday-memory/src/friday_memory/context/extractor.py`
`packages/friday-memory/src/friday_memory/ingestion/tool_ingester.py`
`packages/friday-memory/src/friday_memory/retrieval/collection_manager.py`
`packages/friday-cli/src/friday_cli/container.py`
`tests/lab/harness.py`
`tests/integration/memory/friday.py`

## Errors
1. Status labeling is inconsistent with project state.
`phase-2-build-plan.md` is marked `Status: Definitive` (`phase-2-build-plan.md:3`), but this effort is explicitly a draft review. This can miscommunicate implementation confidence and completeness.

2. Namespace format is internally inconsistent.
The plan defines private namespace regex as `agent_name-8hex:/` (`phase-2-build-plan.md:59`) but later defaults to `user-default:/` (`phase-2-build-plan.md:116-117,140`), which does not match the declared regex.

3. Proposed `AgentInterface.initialize_session` signature is backward-incompatible.
Phase 2 draft requires `(session_id, user_id, namespace)` (`phase-2-build-plan.md:40`), but current interface is optional session with two params and existing return semantics (`packages/friday-core/src/friday_core/interfaces/agent.py:40-44`). This also conflicts with Phase 1 explicit compatibility requirement (`phase-1-build-plan.md:37,102`).

4. Proposed `SystemRuntime.spawn_agent` change is not reconciled with current API and call patterns.
Phase 2 says `spawn_agent()` now accepts namespace (`phase-2-build-plan.md:35`), while current runtime contract and implementation are `spawn_agent(name)` (`packages/friday-core/src/friday_core/interfaces/runtime.py:66`, `packages/friday-runtime/src/friday_runtime/kernel.py:136`). No compatibility shim is specified.

5. `create_session()` is marked “Implemented” in plan language but currently remains a Phase 1 stub.
Current behavior is UUID generation only (`packages/friday-runtime/src/friday_runtime/kernel.py:115-134`) with no session metadata persistence. The plan should classify this as new work, not already implemented behavior.

6. Workflow model references do not match implemented workflow architecture.
Plan requires `ArbitrationStatus.ESCALATED` events and `WorkflowState.PAUSED` (`phase-2-build-plan.md:108-109`), but current workflow engine uses `TaskStatus` and `pending_approval` (`packages/friday-agent/src/friday_agent/workflows/models.py:20-29,312`; `packages/friday-agent/src/friday_agent/workflows/engine.py:142-145,317-318`). `WorkflowState` does not exist.

7. Memory write hardening scope is understated.
Plan calls out guardrails in `store_fact` and `store_insight` only (`phase-2-build-plan.md:53,78-83`), but current write paths also include batch/document methods and direct lower-level writes:
`store_insights_batch*` and document writes in `memory_controller.py` (`1761+`, `1801+`, `1872+`, `1924+`),
direct graph edge writes from extractor (`packages/friday-memory/src/friday_memory/context/extractor.py:553`),
direct collection writes from tool ingester (`packages/friday-memory/src/friday_memory/ingestion/tool_ingester.py:295`).
Without broader enforcement, `shared:/` protections are bypassable.

8. Path conventions are inconsistent in the plan.
Some paths are package shorthand (for example `friday-core/namespaces.py`) while actual repository conventions use `packages/<pkg>/src/...` (`phase-2-build-plan.md:52-56,69-70`). This will create implementation ambiguity.

## Omissions
1. Phase 1 deferred `OrchestratorInterface.route()` decomposition is not carried into Phase 2.
Phase 1 explicitly deferred route decomposition to Phase 2 (`phase-1-build-plan.md:44`), but Phase 2 draft does not address this transition item.

2. `FridayContainer` deprecation/removal decision is missing.
Phase 1 planned wrapper removal in Phase 2 (`phase-1-build-plan.md:67`), and current wrapper is still present with Phase 2 removal note (`packages/friday-cli/src/friday_cli/container.py:7-10`). Phase 2 draft does not include this migration decision.

3. Data migration strategy for existing memory records is missing.
Plan adds `namespace` to graph/vector schemas (`phase-2-build-plan.md:77`) but does not define backfill for existing persisted graph/vector data. Without migration, retrieval and enforcement behavior will be inconsistent.

4. Namespace propagation strategy is incomplete.
No end-to-end definition exists for how namespace is carried through orchestrator, agent lifecycle, extractor, ingestion, maintenance, and lifecycle services, including defaults for system/background jobs.

5. Read policy is under-specified for graph and vector retrieval paths.
Plan references union-read at `recall()` (`phase-2-build-plan.md:38,84-93`) but does not include all retrieval methods and filters such as author queries and summary/insight fetches (`packages/friday-memory/src/friday_memory/controller/memory_controller.py:302-326,726,764,992,1160`).

6. `friday.py` compatibility scope is too narrow.
Draft only mentions command UX and namespace defaults (`phase-2-build-plan.md:118-123`) but `friday.py` has extensive manual DI and direct lifecycle operations (`tests/integration/memory/friday.py:7154-7230`, `3455+`, `3477+`, `3491+`, `3502+`, `5595+`). Compatibility needs explicit operational coverage beyond command-level behavior.

7. Failure modes from technical specs are not reflected.
The technical spec includes “Arbitrator Down” behavior and policy semantics (`technical-specifications.md:488,505-506`), but the Phase 2 plan does not encode those runtime fallback requirements.

8. Atomic promotion mechanism across graph plus vector is not concretely designed.
The objective demands effectively atomic promotion (`phase-2-build-plan.md:22`) but no concrete sequence, idempotency design, compensation logic, or recovery model is specified.

## Areas For Improvement
1. Add a dedicated “Protocol Migration” section.
Define API evolution from Phase 1 interface contracts to Phase 2 with explicit compatibility window, adapter shims, and deprecation schedule.

2. Normalize namespace policy before implementation.
Pick one canonical private namespace format and align defaults, regex, and examples. If single-user fallback is required, define a compliant format and explicit mapping rules.

3. Move enforcement deeper than facade methods.
Add namespace guards at storage abstraction boundaries (graph/vector adapter and collection manager entry points), not only selected `MemoryController` methods.

4. Specify namespace context plumbing as a first-class runtime concern.
Define a single source of truth for active namespace and identity, and enforce propagation across orchestrator, agent session initialization, extractor, ingestion, compactor, reorganizer, and maintenance services.

5. Define an explicit “effective atomicity” flow for arbitration promotions.
A practical model can reuse existing promotion-state style patterns (`packages/friday-memory/src/friday_memory/retrieval/collection_manager.py:394-446,546-584`) with idempotent writes and recovery jobs.

6. Expand verification criteria to include regression and compatibility gates.
Add explicit tests for:
`AgentInterface`/`SystemRuntime` old call patterns still working.
`friday.py` core workflows under namespace constraints.
no direct-path shared write bypass through extractor/ingester/lifecycle jobs.
namespace backfill migration correctness for pre-existing data.

7. Clarify package/file targets using repository-accurate paths.
Use full repository paths in every step to reduce implementation ambiguity and PR churn.

## Phase 1 To Phase 2 Transition Assessment
1. Deferred from Phase 1 and expected in Phase 2:
`OrchestratorInterface.route()` decomposition (`phase-1-build-plan.md:44`) is not represented in Phase 2 draft.

2. Transitional component expected to be resolved in Phase 2:
`FridayContainer` removal/deprecation decision (`phase-1-build-plan.md:67`, `packages/friday-cli/src/friday_cli/container.py:7-10`) is not represented in Phase 2 draft.

3. Phase 1 interface compatibility promise:
Phase 1 established a compatibility requirement for interface evolution (`phase-1-build-plan.md:56`). Phase 2 draft currently proposes signature changes without migration path.

## Backward Compatibility Evaluation
1. `AgentInterface.initialize_session` change is high risk.
Current orchestrator and tests rely on two-arg usage and optional session initialization semantics (`packages/friday-agent/src/friday_agent/orchestrator.py:355,432`; `packages/friday-core/src/friday_core/interfaces/agent.py:40-44`).

2. `SystemRuntime.spawn_agent` change is high risk.
Current runtime contract is one-argument spawn (`packages/friday-core/src/friday_core/interfaces/runtime.py:66`; `packages/friday-runtime/src/friday_runtime/kernel.py:136`) and lacks migration layer for namespace argument.

3. `SystemRuntime.create_session` enhancement is medium risk if done additively.
Metadata support can be backward compatible if optional and default behavior remains intact.

4. Memory namespace defaults in `MemoryController` are medium to high risk without migration.
Existing consumers currently provide no namespace context (`tests/integration/memory/friday.py:7213-7225`). Safe defaults and strict read/write filters require careful rollout and legacy data backfill.

5. `friday.py` operational compatibility is high risk unless subroutines are fully scoped.
Manual lifecycle and retrieval operations mean compatibility cannot be validated only via command rendering updates.

## Recommended Priority Fixes To The Plan (Before Implementation)
1. Correct namespace contract and examples, including single-user fallback.
2. Add explicit API migration strategy for `initialize_session`, `spawn_agent`, and `create_session`.
3. Add Phase 1 carryover items: `route()` decomposition and `FridayContainer` disposition.
4. Expand namespace enforcement surface to all write/read paths and maintenance pipelines.
5. Add concrete migration/backfill strategy for existing graph/vector records.
6. Replace workflow-state terminology with current `TaskStatus`/`pending_approval` model or define the migration explicitly.
7. Define concrete atomic promotion protocol with recovery and idempotency rules.
