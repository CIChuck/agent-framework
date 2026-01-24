# Phase II Build Plan: `packages/friday-memory` (Batch 2 & 2a)

This document outlines the build and verification plan for Batch 2 (Memory Controller) and Batch 2a (Context Engineering).

## 1. Status Analysis

Based on a review of the codebase against `docs/specs/Friday Framework - Component Specifications - Batch 2.md` and `docs/specs/Friday Framework - Component Specifications - Batch 2a.md`, the core components have been drafted.

### Batch 2: Memory Controller (The Unified Data Facade)

| Component | Spec Section | Implementation File | Status |
|-----------|--------------|---------------------|--------|
| `ContextPayload` | 1.1 | `packages/friday-memory/src/friday_memory/models/payload.py` | ✅ Constructed |
| `MemoryController` | 2.0 | `packages/friday-memory/src/friday_memory/controller/memory_controller.py` | ✅ Constructed |

**Gap Analysis:**
- `ContextPayload` correctly includes `history`, `passages`, `entities`, `facts`, and `recent_memories`.
- `MemoryController` implements `recall`, `store_fact`, `store_insight`, and consolidation proxies.
- **Verification Needed:** Ensure `store_fact` and `store_insight` rigorously enforce provenance metadata as per spec.

### Batch 2a: Context Engineering (The Brain)

| Component | Spec Section | Implementation File | Status |
|-----------|--------------|---------------------|--------|
| `ContextEngineeringInterface` | 1.1 | `packages/friday-core/src/friday_core/interfaces/context.py` | ✅ Constructed |
| `SessionState` | 1.2 | `packages/friday-memory/src/friday_memory/models/session.py` | ✅ Constructed |
| `ContextAssembler` | 2.0 | `packages/friday-memory/src/friday_memory/context/assembler.py` | ✅ Constructed |
| `MemoryExtractor` | 3.0 | `packages/friday-memory/src/friday_memory/context/extractor.py` | ✅ Constructed |
| `MemoryConsolidator` | 4.0 | `packages/friday-memory/src/friday_memory/context/consolidator.py` | ✅ Constructed |
| `PromptArchitect` | 5.0 | `packages/friday-memory/src/friday_memory/context/layout.py` | ✅ Constructed |

**Gap Analysis:**
- `SessionState` includes required scoped variables logic (`user:`, `app:`, `session:`).
- `ContextAssembler` implements the "Knapsack" budgeting and priority hierarchy.
- `MemoryExtractor` and `MemoryConsolidator` have placeholder LLM calls using `litellm`.
- **Verification Needed:** Validate token budgeting logic (`_apply_budget`) and prompt layout structure.

---

## 2. Build & Verification Plan

Since the code is already drafted, the focus is on verification and acceptance testing.

### Step 1: Core Interface Verification
**Goal:** Ensure `friday-core` correctly exports the protocols needed by `friday-memory`.
- [ ] Verify `ContextEngineeringInterface` is importable from `friday_core`.
- [ ] Check circular dependency handling (type checking imports).

### Step 2: Batch 2 Verification (Memory Controller)
**Goal:** Validate the Unified Data Facade.

- [ ] **Test 2.1: Provenance Enforcement**
    - *Spec:* `store_insight` / `store_fact` must raise error if metadata is missing.
    - *Target:* `tests/test_memory_controller.py`
- [ ] **Test 2.2: The Consolidation Bridge**
    - *Spec:* `fetch_unconsolidated_events` returns items -> `mark_events_consolidated` -> fetch returns empty.
    - *Target:* `tests/test_memory_controller.py`
- [ ] **Test 2.3: Unified Recall**
    - *Spec:* `recall()` returns populated `ContextPayload`.
    - *Target:* `tests/test_memory_controller.py`

### Step 3: Batch 2a Verification (Context Engineering)
**Goal:** Validate the Context Strategies.

- [ ] **Test 2a.1: Scoped State**
    - *Spec:* `state.set_var` validates prefixes (`user:`, `app:`, `session:`).
    - *Target:* `tests/test_models.py`
- [ ] **Test 2a.2: Checkpoint Restoration**
    - *Spec:* `restore_checkpoint` correctly truncates history and resets state.
    - *Target:* `tests/test_context/test_assembler.py`
- [ ] **Test 2a.3: Token Budgeting ("The Knapsack")**
    - *Spec:* `assemble_context` respects `budget_limit`, dropping items in correct priority order (Deep History < Scoped Vars < Weak Matches < Recent History < Immediate Context).
    - *Target:* `tests/test_context/test_assembler.py`
- [ ] **Test 2a.4: Extraction Trigger**
    - *Spec:* `extract_context` fires and generates `GraphNode` with provenance.
    - *Target:* `tests/test_context/test_extractor.py`

## 3. Execution Order

1.  **Dependencies:** Ensure `friday-core` is installed and up-to-date in the environment.
2.  **Unit Tests:** Run existing tests in `packages/friday-memory/tests/` to assess current pass rate.
    ```bash
    uv run pytest packages/friday-memory
    ```
3.  **Fixes:** Address any failures found in existing tests.
4.  **New Tests:** Implement any missing acceptance criteria tests defined in Step 2 & 3.
