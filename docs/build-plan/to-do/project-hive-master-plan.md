# Project Hive: Master Build Plan

**Status:** Planning
**Goal:** Evolve Friday from a single-agent framework into a multi-agent "Hive" system with shared memory and orchestration.

## 1. Executive Summary

**Project Hive** implements the "One Mind, Many Bodies" architecture.
*   **The Mind:** A shared, resilient Memory System (Graph + Vector).
*   **The Bodies:** Specialized Agents (Researcher, Coder) orchestrated to solve complex tasks.

This plan breaks the execution into 4 de-risked phases, prioritizing stability and regression testing.

---

## 2. Phase 1: Foundation (Memory Health)
**Goal:** Fix existing bugs ("Tool Amnesia") and modularize the Memory System to support lightweight agents.
**Risk:** Low (Internal refactoring).

### 2.1 Tool Amnesia Fix
*   **Task:** Update `PromptArchitect` to render tool calls/results using native message roles.
*   **Verification:** `memory-chat-v2` shows tool output in `/prompt` history after reloading context.
*   **See:** `tool-content-lifecycle-build-plan.md` (Phase 1)

### 2.2 Scalable Adapters
*   **Task:** Implement `SimpleVectorStore` (In-Memory) and `NullGraphStore`.
*   **Task:** Update `FridayContainer` to accept `memory_profile`.
*   **Verification:** Run `memory-chat-v2 --memory-profile=ephemeral`. It should work without ChromaDB files.
*   **See:** `scalable-adapters-build-plan.md`

**Exit Criteria:** Existing CLI works 100%. `memory-chat-v2` passes regression. 


---

## 3. Phase 2: Cells (Agent Definition)
**Goal:** Define agents as data (YAML) and manage them via a Registry.
**Risk:** Medium (New components).

### 3.1 Agent Configuration
*   **Task:** Define YAML schema (`agent.schema.yaml`).
*   **Task:** Implement `AgentLoader` to parse YAML into `AgentProfile`.
*   **See:** `agent-configuration-build-plan.md`

### 3.2 Agent Registry
*   **Task:** Implement `AgentRegistry` to store profiles + capabilities tags.
*   **Task:** Update `FridayContainer` to expose `get_team_agent(name)` factory.
*   **See:** `agent-registry-build-plan.md`

**Exit Criteria:** A unit test can load `agents/test.yaml` and instantiate a working `CopilotAgent` from it.

---

## 4. Phase 3: The Mind (Orchestration)
**Goal:** Enable multiple agents to exist and share information.
**Risk:** High (Concurrency & Complexity).

### 4.1 Orchestrator MVP
*   **Task:** Implement `AgentOrchestrator`.
*   **Task:** Implement simple routing ("@researcher do this").
*   **See:** `orchestrator-mvp-build-plan.md`

### 4.2 Shared Memory Provenance
*   **Task:** Update `MemoryController` to enforce `author_id` in shared writes.
*   **Task:** Update `TranscriptStore` to track `agent_id` per turn.
*   **See:** `shared-memory-provenance-build-plan.md`

**Exit Criteria:** Integration test where Agent A writes a fact, and Agent B reads it.

---

## 5. Phase 4: Optimization (Lifecycle)
**Goal:** Advanced workflows and self-cleaning memory.
**Risk:** Medium (Optimization).

### 5.1 Tool Content Lifecycle
*   **Task:** Implement `ToolContentManager` (Reference-based decay).
*   **Task:** Implement "Summarization" replacement strategy.
*   **See:** `tool-content-lifecycle-build-plan.md`

### 5.2 Dynamic Workflows
*   **Task:** Implement Task Graphs (Inputs/Outputs matching).
*   **Task:** Implement Human-in-the-Loop nodes.
*   **See:** `dynamic-workflows-build-plan.md`

**Exit Criteria:** Long-running task (10+ turns) shows stable token usage.

---

## 6. Testing Strategy

### 6.1 The "Gatekeeper": `memory-chat-v2`
This existing tool is our primary integration test bench.
*   **Phase 1:** Must run unchanged (Regression). Must run with `--memory-profile=ephemeral` (New Feature).
*   **Phase 2:** Must be able to load an agent definition from YAML.
*   **Phase 3:** Must support "switching" agents (`/switch researcher`) to test shared memory.

### 6.2 Unit Tests
*   Every new component (`AgentRegistry`, `SimpleVectorStore`) requires 90% coverage.

### 6.3 Manual Validation
*   "The Newsletter Test": Can the Hive generate a newsletter by delegating Research -> Writing?

### 6.4 Risk Mitigation & Verification Plan
Given the "Gatekeeper" status of `memory-chat-v2`, specific validation checks are required to prevent regression during the `friday-memory` evolution:

1.  **Constructor Compatibility Check:**
    *   Verify `MemoryController.__init__` accepts legacy arguments without error.
    *   Ensure all new parameters (e.g., `access_buffer`) have safe defaults (`None`).

2.  **Schema Validation Check:**
    *   Verify `InteractionTurn` instantiation works without providing `agent_id`.
    *   Verify `ToolResult` instantiation works without providing `summary`/`is_decayed`.

3.  **Behavioral Regression:**
    *   Run `memory-chat-v2` in default mode.
    *   Execute a standard "Store/Recall" loop.
    *   Confirm no `ValidationError` or `TypeError` is raised during standard operations.

### 6.5 Key Manual Validation Steps
To validate deep functionality beyond simple regressions:

1.  **The "Recall" Test (Persistence Check):**
    *   Start `memory-chat-v2`.
    *   Store a unique fact (e.g., "The code word is 'Blueberry'").
    *   **Restart** the application.
    *   Ask: "What is the code word?" -> Must retrieve "Blueberry".
    *   *Purpose:* Verifies that Adapter changes didn't break persistence.

2.  **The "Tool Context" Test (Amnesia Fix):**
    *   Start `memory-chat-v2`.
    *   Run `/tool file_read path="README.md"`.
    *   Run `/prompt` -> Verify the *content* of README.md is visible in the messages list.
    *   **Restart** the application.
    *   Run `/prompt` again -> Verify the tool output is *still* visible in the restored history.
    *   *Purpose:* Verifies `PromptArchitect` logic.

3.  **The "Dual Memory" Test (Orchestration):**
    *   (Phase 3+) Run with Orchestrator.
    *   As Agent A: Store "Secret=A".
    *   Switch to Agent B (Private Mode).
    *   Ask: "What is the Secret?" -> Should NOT find "A".
    *   *Purpose:* Verifies Namespace isolation.

4.  **The "Hive Mind" Test (Shared Memory):**
    *   (Phase 3+) Run with Orchestrator.
    *   As Agent A: Store "Project Status is Green".
    *   Switch to Agent B (Shared Mode).
    *   Ask: "What is the Project Status?" -> Must retrieve "Green".
    *   Check Provenance -> Author should be "Agent A".
    *   *Purpose:* Verifies Shared Memory access and Provenance tracking.
