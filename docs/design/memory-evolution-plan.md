# Design: Friday Memory Evolution Plan

**Status:** Planned
**Context:** Synthesizing requirements from Orchestration, Lightweight Agents, and Tool Lifecycle designs into a coherent roadmap for `friday-memory`.

## 1. Executive Summary

We are evolving `friday-memory` from a single-agent monolith into a **Multi-Modal, Multi-Agent Knowledge System**. This evolution preserves backward compatibility while enabling:
*   **Scalability:** From in-memory scratchpads to persistent shared graphs.
*   **Multi-Tenancy:** Namespaced collections for private vs. shared memory.
*   **Provenance:** Strict author tracking for collaboration.
*   **Lifecycle:** Intelligent decay of tool outputs.

## 2. Architecture Changes

### 2.1 Storage Adapters ("The Scalable Backend")
We introduce a tiered adapter strategy.
*   **Current:** `ChromaVectorStore`, `ElementXGraphStore` (Persistent).
*   **New:** `SimpleVectorStore` (In-Memory, numpy-based), `VolatileGraphStore` (NetworkX only).
*   **New:** `NullVectorStore`, `NullGraphStore` (No-op for pure episodic agents).

### 2.2 Data Models
*   **`ToolResult`:** Updated to support `is_decayed` and `summary`.
*   **`ProvenanceMetadata`:** `author_id` becomes a semantic link to the Agent Registry (e.g., `agent:researcher`).
*   **`InteractionTurn`:** Added `agent_id` to support interleaved transcripts.

### 2.3 Controller Logic
*   **Namespacing:** `MemoryController` remains agnostic, but `FridayContainer` configures it with namespaced adapters.
*   **Orchestration Support:** The Controller must support "Ghost Writes" (writing to a buffer for HIL approval) in future phases.

## 3. Migration Strategy

### Phase 1: Adapters & Config
*   **Goal:** Enable "Lightweight Memory" without breaking CLI.
*   **Action:** Implement `Simple` and `Null` adapters. Update `FridayContainer` to accept `memory_profile`. Default remains "Persistent" (no breaking change).

### Phase 2: Tool Lifecycle
*   **Goal:** Fix "Tool Amnesia" and Bloat.
*   **Action:** Implement `ToolContentManager` and update `PromptArchitect`. This is purely additive/internal improvement.

### Phase 3: Provenance & Multi-Agent
*   **Goal:** Enable Orchestration.
*   **Action:** Update `friday-agent` to pass `agent_id` into `add_turn`. Update `MemoryController` to enforce `author_id` in shared modes.

## 4. Testing & Migration Strategy

### 4.1 `memory-chat-v2` Integration
The `memory-chat-v2` integration test is our primary validation tool. To ensure backward compatibility and validate new features:

1.  **Interface Stability:** New adapters (`SimpleVectorStore`, `NullVectorStore`) must strictly adhere to `VectorStoreAdapter`. This ensures `memory-chat-v2` *could* use them without code changes if injected.
2.  **Configuration Support:** We will update `memory-chat-v2` to accept a `--memory-profile` argument.
    *   `--memory-profile=persistent` (Default): Uses `ChromaVectorStore` (Current behavior, no regression).
    *   `--memory-profile=ephemeral`: Injects `SimpleVectorStore`. This allows us to use the existing chat harness to verify the new lightweight adapters.

### 4.2 Legacy Data Migration
*   **No Schema Breaks:** We are adding fields (`agent_id`, `is_decayed`) with default values (`None` / `False`). Existing database files (`chroma.sqlite3`) remain readable.
*   **Lazy Migration:** When an old record is accessed and saved, it gets the new fields. No "Stop the World" migration script is required for Phase 1/2.

## 5. Component Impact Analysis

| Component | Change | Risk | Mitigation |
|-----------|--------|------|------------|
| `friday_memory.adapters` | Add new modules | Low | New files, no impact on existing. |
| `friday_memory.models` | Add fields to Pydantic | Low | Default values maintain compat. |
| `friday_memory.context.layout` | Logic change (PromptArchitect) | Med | Integration tests required. |
| `friday_memory.controller` | None (mostly) | Low | Logic stays in adapters/container. |

## 6. Conclusion

We do **not** need a rewrite. The "Adapter Pattern" utilized in Batch 1 proves its worth here. We can swap backends and extend models without destabilizing the core "Recall -> Reason -> Act -> Store" loop.
