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
| **Configuration** | `friday_cli/container.py` (`FridayConfig`) | `friday_runtime/config.py` | `FridayConfig` (LLM, embedding, chroma, telemetry, agents) moves to runtime. `CLIConfig` (themes, icons, spinner) stays in CLI. |
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
*   **4.1 Immutable Definition:** `TaskNode` currently has mutable runtime fields: `status`, `result`, `error`, `retry_count`, `started_at`, `completed_at`. Move these to a new `TaskState` model. `WorkflowDefinition` should be frozen (`model_config = ConfigDict(frozen=True)`) after removing mutable fields. Remove `TaskNode.reset()`.
*   **4.2 Stateful Execution:** Create `WorkflowExecutionState` with `task_states: dict[str, TaskState]` to hold per-task runtime data separately from the definition.
*   **4.3 Engine Update:** `WorkflowEngine.run(definition)` creates a fresh `WorkflowExecutionState` and returns it. The same `WorkflowDefinition` can be executed concurrently without state collision.

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
*   **5.2 Preserve Lazy Accessors:** The proxy must preserve all lazy property accessors that downstream code depends on: `.llm`, `.memory`, `.context_engine`, `.tool_registry`, `.orchestrator`, `.agent_registry`. Each must delegate to `self._kernel`.
*   **5.3 Verify:** Run existing CLI tests. They must pass without knowing `friday-runtime` exists.

### Step 5.5: friday.py Integration (Known Gap — Out of Scope)

> **Important:** `tests/integration/memory/friday.py` (~7500 lines) is the main production integration app. It does **NOT** use `FridayContainer` — it performs its own manual dependency injection (creating LLM services, memory controllers, context engines, tool registries directly). Phase 1 does **NOT** need to migrate `friday.py` to use `RuntimeKernel`. That is a separate effort. The Lab harness (Step 6) uses `FridayContainer`/`RuntimeKernel`, which is the canonical DI path going forward.

### Step 6: Create Friday Lab (Harness)
*   **Scope:** The "Lab" is internal test infrastructure located at `tests/lab/`. It is **NOT** a shippable package.
*   **6.1 Scaffold:** `tests/lab/harness.py`.
*   **6.2 Implement `HeadlessHarness`:** Subclass of `RuntimeKernel` using `MemoryProfile.EPHEMERAL`.
*   **6.3 Regression Test:** Create `tests/lab/test_legacy_compatibility.py` that specifically imports `FridayContainer` and mimics `Friday.py` usage to prove stability.

---

## 5. Verification Strategy

### Exit Criteria Checks
1.  **Legacy Compatibility:** `FridayContainer` import and initialization behaves identically to before. The Lab's `test_legacy_compatibility.py` (Step 6.3) validates this. The existing integration app (`tests/integration/memory/friday.py`) is out of scope for Phase 1 migration.
2.  **Headless Execution:** A script using *only* `friday_runtime` can boot the kernel and run a "Hello World" agent task.
3.  **Workflow Reusability:** A test proves the same `WorkflowDefinition` object can be executed twice in parallel without state collision.
4.  **Interface Adherence:** All methods marked **[Implemented]** in the Compliance Matrix exist and function.

---

## 6. Execution Order

1.  `friday-core`: Add Interfaces (`SystemRuntime`, `AgentInterface`, `RegistryInterface`).
2.  `friday-agent`: Refactor Workflows (immutable `TaskNode`, extract `TaskState`).
3.  `friday-runtime`: Implement Kernel & DI (depends on `friday-agent` for workflow engine).
4.  `friday-cli`: Refactor `FridayContainer` to Proxy (delegates to `RuntimeKernel`).
5.  `friday-lab`: Build Harness (depends on `friday-runtime` for `HeadlessHarness`).