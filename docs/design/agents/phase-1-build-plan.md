# Phase 1 Build Plan: Stabilization & Extraction

**Status:** Definitive
**Target:** Decouple the "Brain" (Kernel) from the "Body" (CLI) and stabilize execution.
**Reference:** `comprehensive-agent-framework-design.md`, `technical-specifications.md`

---

## 1. Objectives & Constraints

### Objectives
1.  **Extract the Kernel:** Establish `packages/friday-runtime` as the central orchestration library, moving core logic out of `friday-cli`.
2.  **Stabilize Workflows:** Refactor `WorkflowEngine` to ensure `WorkflowDefinition` objects are immutable and reusable.
3.  **Establish Friday Lab:** Create the initial integration harness to verify "Headless" execution without the CLI.

### Mandatory Constraints
1.  **Ecosystem Integration:** All development MUST utilize existing ancillary Friday packages (`friday-llm`, `friday-core`, `friday-memory`, etc.). No reinventing logic.
2.  **Legacy Stability (Friday.py):** `friday-cli` MUST remain 100% backward compatible. Scripts dependent on `FridayContainer` and `FridayConfig` must run without modification.
3.  **Interface Compliance:** Phase 1 implementation must satisfy the `technical-specifications.md` contracts, even if via stubbing.

---

## 2. Phase 1 Interface Compliance Matrix

This table defines exactly what will be implemented versus stubbed/deferred in this phase, mapping directly to `technical-specifications.md`.

| Interface | Method | Phase 1 Status | Implementation Note |
| :--- | :--- | :--- | :--- |
| **SystemRuntime** | `start()` | **Implemented** | Initializes singleton services via `friday-runtime/di.py`. |
| | `spawn_agent()` | **Implemented** | Uses Registry to create `AgentInterface`. |
| | `execute_workflow()` | **Implemented** | Runs the refactored Workflow Engine. |
| **AgentInterface** | `run()` | **Implemented** | Core execution loop (Think -> Act). |
| | `set_autonomy_policy` | **Deferred** | Hardcoded to "manual" for Phase 1. |
| **RegistryInterface** | `load_manifests()` | **Implemented** | Required for agent loading. |
| **ArbitrationInterface** | `submit_proposal()` | **Stub** | Direct passthrough (Auto-Approve). |
| **ArtifactWorkspace** | `store()` | **Stub** | Direct filesystem/memory write; no wrapping. |

> **Note:** All ABCs defined in `friday-core` are considered **Protocol Version 1.0**. Any changes in future phases must ensure backward compatibility or follow a strict migration path.

---

## 3. Package Architecture Changes

### New Package: `friday-runtime`
*   **Role:** The "Headless Operating System" for the Hive.
*   **Dependencies:** `friday-core`, `friday-agent`, `friday-memory`, `friday-llm`, `friday-telemetry`.

### Component Migration (The Proxy Pattern)
To ensure stability, we use a **Non-Destructive Extraction**. `FridayContainer` becomes a shell that delegates to `RuntimeKernel`.

| Logic Area | Source (to be thinned) | Destination (the new home) | Strategy |
| :--- | :--- | :--- | :--- |
| **Core Kernel** | `friday_cli/container.py` | `friday_runtime/kernel.py` | Logic moves; Source becomes a Delegate. |
| **Dependency Injection** | `friday_cli/container.py` | `friday_runtime/di.py` | Resource creation logic moves here. |
| **Configuration** | `friday_cli/cli_config.py` | `friday_runtime/config.py` | Base config moves; CLI extends it. |
| **Adapter Factories** | `friday_cli/profiles.py` | `friday_runtime/adapters.py` | Logic moves; Source imports from Destination. |
| **Commands/Display** | `friday_cli/commands.py` | **STAYS IN CLI** | Presentation layer remains untouched. |

**Specific Boot Sequence Migration:**
The following specific methods (or their logic) will be extracted from `FridayContainer` into `friday_runtime/di.py`:
*   `_create_telemetry()`
*   `_create_llm_services()`
*   `_create_storage_adapters()`
*   `_create_memory_controller()`
*   `_create_context_engine()`
*   `_create_tool_registry()`
*   `_create_agent_registry()`

**Error Propagation:**
The `FridayContainer` Proxy must provide **Exception Transparency**. Exceptions raised by `RuntimeKernel` (e.g., `ChromaDBError`, `LLMAPIError`) must bubble up raw and unchanged to `friday-cli`. The Proxy should not catch or wrap these errors, ensuring existing CLI error handlers continue to function.

---

## 4. Detailed Implementation Steps

### Step 1: Scaffold `friday-runtime`
*   **1.1 Initialize:** `uv init packages/friday-runtime`.
*   **1.2 Config:** Update `pyproject.toml` with `friday-core`, `friday-memory`, `friday-llm`, `friday-telemetry`, `friday-agent`.

### Step 2: Define Core Interfaces (in `friday-core`)
*   **2.1 Create ABCs:**
    *   `packages/friday-core/src/friday_core/interfaces/runtime.py`: Add `SystemRuntime`.
    *   `packages/friday-core/src/friday_core/interfaces/agent.py`: Add `AgentInterface`.
    *   `packages/friday-core/src/friday_core/interfaces/registry.py`: Add `RegistryInterface`.

### Step 3: Implement the Runtime Kernel (`friday-runtime`)
*   **3.1 Implement `RuntimeConfig`:** Port generic config logic from `friday_cli`.
*   **3.2 Implement `DIContainer` (`di.py`):**
    *   Move the "Boot Sequence" methods (see Migration list above) here.
*   **3.3 Implement `RuntimeKernel`:**
    *   Implement `SystemRuntime`.
    *   `start()` calls DI providers to boot Memory/LLM.
    *   `spawn_agent()` uses `AgentRegistry` to create instances with injected dependencies.

### Step 4: Refactor Workflow Engine (`friday-agent`)
*   **4.1 Immutable Definition:** Ensure `WorkflowDefinition` models are frozen/immutable.
*   **4.2 Stateful Execution:** Create `WorkflowExecutionState` to hold runtime data.
*   **4.3 Engine Update:** `WorkflowEngine.run(definition)` returns `WorkflowExecutionState`.

### Step 5: Update `friday-cli` (The Proxy Refactor)
**Critical Stability Step:** Preserve `FridayContainer` API.

*   **5.1 Refactor `FridayContainer`:**
    ```python
    # packages/friday-cli/src/friday_cli/container.py
    from friday_runtime import RuntimeKernel, RuntimeConfig
    
    class FridayContainer:
        def __init__(self, config=None):
            # Delegate to the Headless Kernel
            self._kernel = RuntimeKernel(config or RuntimeConfig.from_env())
            
        @property
        def memory(self):
            return self._kernel.memory  # Proxy access
            
        async def initialize(self):
            await self._kernel.start()  # Proxy lifecycle
    ```
*   **5.2 Verify:** Run existing CLI tests. They must pass without knowing `friday-runtime` exists.

### Step 6: Create Friday Lab (Harness)
*   **Scope:** The "Lab" is internal test infrastructure located at `tests/lab/`. It is **NOT** a shippable package.
*   **6.1 Scaffold:** `tests/lab/harness.py`.
*   **6.2 Implement `HeadlessHarness`:** Subclass of `RuntimeKernel` using `MemoryProfile.EPHEMERAL`.
*   **6.3 Regression Test:** Create `tests/lab/test_legacy_compatibility.py` that specifically imports `FridayContainer` and mimics `Friday.py` usage to prove stability.

---

## 5. Verification Strategy

### Exit Criteria Checks
1.  **Legacy Compatibility:** `scripts/memory-chat-v2.py` runs successfully. `FridayContainer` behaves identical to before.
2.  **Headless Execution:** A script using *only* `friday_runtime` can boot the kernel and run a "Hello World" agent task.
3.  **Workflow Reusability:** A test proves the same `WorkflowDefinition` object can be executed twice in parallel without state collision.
4.  **Interface Adherence:** All methods marked **[Implemented]** in the Compliance Matrix exist and function.

---

## 6. Execution Order

1.  `friday-core`: Add Interfaces.
2.  `friday-runtime`: Implement Kernel & DI.
3.  `friday-agent`: Refactor Workflows.
4.  `friday-lab`: Build Harness.
5.  `friday-cli`: Refactor `FridayContainer` to Proxy.