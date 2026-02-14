# Phase 2 Build Plan: The Conscience (Arbitration & Namespaces)

**Status:** Definitive
**Target:** Establish "One Mind, Many Bodies" integrity through gated memory promotion and strict namespace isolation.
**Reference:** `comprehensive-agent-framework-design.md`, `technical-specifications.md`

---

## 1. Objectives & Constraints

### Objectives
1.  **Establish Truth Boundaries:** Transition from a "global-write" memory model to a "gated-promotion" model where agents cannot pollute shared knowledge.
2.  **Enforce Namespace Isolation:** Implement strict read/write boundaries (`agent_name-uuid:/`) to prevent cross-agent state leakage and race conditions.
3.  **Implement the Arbitrator:** Create a specialized system agent responsible for validating, deduplicating, and promoting facts to Shared Memory.
4.  **Enable Conflict Resolution:** Provide a mechanism for semantic conflict detection and human-in-the-loop escalation.
5.  **Bulletproof Verification:** Evolve the Friday Lab with "Conflict Injection," "Identity Spoofing," and "Truth Convergence" integration tests.

### Mandatory Constraints
1.  **Backward Compatibility:** Existing `MemoryController` consumers must default to a private namespace if none is specified, ensuring current agents continue to function.
2.  **Zero-Trust Shared Write:** Direct writes to `shared:/` must be physically blocked at the `MemoryController` level for all identities except the `Arbitrator`.
3.  **Ecosystem Integration:** Utilize `friday-core` for shared models and `friday-memory` for underlying storage. No raw database calls.
4.  **Atomic Promotion:** Fact promotion to Shared Memory must be atomic (or effectively atomic) across both Graph (associative) and Vector (semantic) stores.

---

## 2. Phase 2 Interface Compliance Matrix

This table defines exactly what will be implemented in Phase 2, mapping directly to `technical-specifications.md`.

| Interface | Method | Phase 2 Status | Implementation Note |
| :--- | :--- | :--- | :--- |
| **ArbitrationInterface** | `submit_proposal()` | **Implemented** | Async submission of `MemoryProposal`. Returns `ArbitrationResult`. |
| | `get_decision()` | **Implemented** | Poll for the status of an escalated or pending proposal. |
| | `resolve_conflict()` | **Implemented** | Forces a decision (Promote/Reject) on an escalated proposal. |
| **SystemRuntime** | `spawn_agent()` | **Updated** | Now accepts `namespace` and injects it into the agent instance. |
| | `create_session()` | **Implemented** | Full implementation with session metadata support. |
| **MemoryController** | `store_fact()` | **Hardened** | Enforces namespace write permissions. Blocks `shared:/` for non-arbitrators. |
| | `recall()` | **Updated** | Implements "Union Read" (Private + Shared scopes). |
| | `set_author()` | **Updated** | Automatically derived from namespace context. |
| **AgentInterface** | `initialize_session()`| **Updated** | Signature: `(session_id: str, user_id: str, namespace: str)`. |
| **LabHarnessInterface** | `inject_conflict()` | **Implemented** | Feeds contradictory proposals to the Arbitrator for testing. |
| | `replay_session()` | **Deferred** | Moved to Phase 3 (Transcript-heavy). |

---

## 3. Package Architecture Changes

### Logic Distribution (Namespace Enforcement)

| Logic Area | Location | Strategy |
| :--- | :--- | :--- |
| **Namespace Logic** | `friday-core/namespaces.py` | Centralized regex validation and parsing. |
| **Permission Check** | `friday-memory/controller/memory_controller.py` | Guardrails in `store_fact` and `store_insight`. |
| **Staging Store** | `friday-memory/staging/` | Temporary storage for unverified proposals (SQLite or Chroma). |
| **Arbitration Agent** | `friday-agent/system/arbitrator.py` | Implementation of the "Conscience" agent logic. |
| **Kernel Wiring** | `friday-runtime/di.py` | Dependency injection for the Arbitrator service. |

### Namespace Protocol Specification
*   **Format:** `^(?P<agent_name>[a-z][a-z0-9_]*)-(?P<short_uuid>[a-f0-9]{8}):\/$`
*   **Regex Example:** `researcher-a1b2c3d4:/`
*   **Shared Namespace:** `shared:/`

---

## 4. Detailed Implementation Steps

### Step 1: Foundation (Core Definitions)

*   **1.1 Namespace Logic:** Create `packages/friday-core/src/friday_core/namespaces.py` with `is_valid_namespace`, `is_shared_namespace`, and `get_namespace_owner` functions.
*   **1.2 Arbitration ABC:** Implement `ArbitrationInterface` in `packages/friday-core/src/friday_core/interfaces/arbitration.py`.
*   **1.3 Data Models:**
    *   `MemoryProposal`: (id, source_agent_id, session_id, entity_name, attribute, value, confidence, evidence, scope).
    *   `ArbitrationResult`: (proposal_id, status: `promoted`|`rejected`|`escalated`, ticket_id, reason).

### Step 2: Memory Hardening (Infrastructure)

*   **2.1 Model Updates:** Update `GraphNode`, `GraphEdge`, and Vector metadata schemas to include a `namespace` field.
*   **2.2 Write Guardrails:**
    ```python
    # In MemoryController.store_fact()
    if target_namespace == "shared:/" and self.current_identity != "arbitrator":
        raise NamespaceAccessError("Direct write to shared memory is forbidden.")
    ```
*   **2.3 Union-Read Implementation:** Update `MemoryController.recall()` to modify retrieval queries:
    ```python
    # Query logic (simplified)
    where_clause = {
        "$or": [
            {"namespace": self.active_namespace},
            {"namespace": "shared:/"}
        ]
    }
    ```

### Step 3: Implement the Arbitrator Agent (Logic)

*   **3.1 Agent Structure:** Create `ArbitratorAgent` as a specialized implementation of `AgentBase`. It consumes `MemoryProposal` objects.
*   **3.2 Staging Manager:** Implement a staging area (SQLite or a dedicated Chroma collection) for proposals awaiting review.
*   **3.3 Semantic Collision Detection:**
    *   The Arbitrator searches `shared:/` for entities matching the proposal's `entity_name`.
    *   Prompt logic: "Given existing fact {X} and proposed fact {Y}, are they: A) Complementary B) Contradictory C) Duplicate?"
*   **3.4 Automatic Promotion:** Implement high-confidence auto-promotion logic (>0.9 confidence with no semantic collision).

### Step 4: Kernel Integration & Workflow Extensions

*   **4.1 Runtime Wiring:** Update `RuntimeKernel` to instantiate the `ArbitratorAgent` and provide the `ArbitrationInterface` to all spawned agents.
*   **4.2 Workflow Interruption:**
    *   Update `WorkflowEngine` to listen for `ArbitrationStatus.ESCALATED` events.
    *   Implement `WorkflowState.PAUSED` for tasks requiring human resolution of memory conflicts.

### Step 5: Legacy App Reconciliation (friday.py)

To ensure the production-like `friday.py` integration remains functional, Phase 2 includes a specific migration path for single-user apps.

*   **5.1 Default Namespace Assignment:**
    *   When `MemoryController` is initialized without an explicit agent identity (as in `friday.py`), it must default to a `user-default:/` namespace.
    *   **Vector Query Safety:** The `MemoryController` will automatically inject the `user-default:/` + `shared:/` Union Filter for all internal vector queries.
*   **5.2 Command Updates in friday.py:**
    *   Update `/insights`, `/summaries`, and `/entities` to display a `[Namespace]` tag for each result.
    *   The `/ingest` command will default to writing to the `user-default:/` namespace.
*   **5.3 Subroutine Alignment:**
    *   `MemoryReorganizer` and `InSessionCompactor` will be restricted to operating within a single namespace scope to prevent cross-contamination.
    *   `MemoryExtractor` will tag all newly discovered entities with the active namespace context.

### Step 6: Friday Lab Evolution (Verification)

*   **6.1 Conflict Injection:** Implement `LabHarness.inject_conflict()` in `tests/lab/harness.py`.
*   **6.2 Identity Spoofing Test:** Create `tests/lab/test_security_namespaces.py` to verify `NamespaceAccessError` when a non-arbitrator tries to write to `shared:/`.
*   **6.3 Truth Convergence Test:** Verify that when Agent A's proposal is promoted, Agent B (in a different private namespace) can immediately see the new fact in `shared:/`.

---

## 7. Verification Strategy (Exit Criteria)

### Exit Criteria Checks
1.  **Identity Spoofing Blocked:** A test proves that a standard agent attempting to write directly to `shared:/` triggers a `NamespaceAccessError`. *(Step 2.2 + Step 6.2)*
2.  **Namespace Leakage Prevention:** A test proves that Agent A cannot see Agent B's private memories even within the same session. *(Step 2.3 + Step 6.3)*
3.  **Conflict Detection:** The Lab successfully injects a contradictory fact pair (e.g., "Sky is Blue" vs "Sky is Red") and verifies the Arbitrator marks them as `ESCALATED`. *(Step 3.3 + Step 6.1)*
4.  **Automatic Promotion:** A high-confidence proposal with no conflicts is automatically promoted to `shared:/` and becomes visible to all agents. *(Step 3.4 + Step 6.3)*
5.  **Legacy Stability (friday.py):** Verify that `friday.py` continues to operate correctly in a single-user mode, with all data correctly isolated to the `user-default:/` namespace. *(Step 5)*

---

## 8. Execution Order

| Step | Package | Action | Depends On |
| :--- | :--- | :--- | :--- |
| 1 | `friday-core` | Define `MemoryProposal` models, `ArbitrationInterface` ABC, and Namespace logic. | — |
| 2 | `friday-memory` | Harden `MemoryController` with permission checks and Union-Read logic. | Step 1 |
| 3 | `friday-agent` | Implement `ArbitratorAgent` and semantic collision detection logic. | Step 2 |
| 4 | `friday-runtime` | Wire the Arbitrator into the Kernel and DI container. | Step 3 |
| 5 | `friday-agent` | Extend `WorkflowEngine` with conflict-aware pause/resume logic. | Step 4 |
| 6 | `friday.py` | Reconcile the integration app with new namespace defaults. | Step 4 |
| 7 | `tests/lab` | Build conflict injection harness and execute all exit criteria tests. | Step 6 |
