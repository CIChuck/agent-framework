# Build Plan: Tool Liberation (Phase 1)

**Objective:** Extract embedded logic from `tests/integration/memory/memory-chat.py` and refactor it into reusable, safe Tool classes within `packages/friday-tools`.

**Why:** Autonomous agents (Janitor, Sentinel) and the CLI (`friday-cli`) both need access to these capabilities. Currently, they are trapped in a monolithic test script.

## 1. Directory Structure Setup

We will organize `friday-tools` by domain:

```
packages/friday-tools/src/friday_tools/
├── __init__.py
├── base.py                 # Abstract base class for all tools
├── memory/
│   ├── __init__.py
│   ├── inspection.py       # Read-only tools (Stats, Graph, Vector)
│   ├── maintenance.py      # Write tools (Prune, Reset, Reorganize)
│   └── lifecycle.py        # Lifecycle tools (Promote, Decay)
├── system/
│   ├── __init__.py
│   ├── health.py           # System health checks (RAM/Disk) - New for Sentinel
│   └── transcript.py       # Transcript export/reading
└── web/                    # Future: WebMonitorTool
```

## 2. Implementation Steps

### Step 2.0: Design Principles (Dependency Injection)
All tools must adhere to **Strict Dependency Injection**:
*   **Constructors (`__init__`)**: Tools must accept their heavy dependencies (e.g., `MemoryController`, `TranscriptStore`) as arguments.
*   **No Global State**: Do not instantiate `MemoryController` inside the tool.
*   **Type Hinting**: Use protocols or base classes from `friday-core` where possible.

*Example:*
```python
class GraphInspectionTool(FridayTool):
    def __init__(self, controller: MemoryController):
        self.controller = controller
```

### Step 2.1: Define Base Tool Protocol
Create `friday_tools.base.FridayTool` implementing `friday_core.interfaces.ToolDefinition`.

*   **Pydantic Integration:** The class should inherit from `pydantic.BaseModel` (or use a nested `InputModel`) to define arguments.
*   **Automatic Schema Generation:** It must implement `parameters_schema` by reflecting on the Pydantic fields.
*   **Protocol Compliance:** It must implement `name`, `description`, `execute`, and `to_schema` as defined in `friday_core`.
*   **Output:** Must return a **Typed Pydantic Model** (e.g., `ToolResult` with `content`, `data`, `metadata`). Do not return raw dicts.

*Example:*
```python
class ToolResult(BaseModel):
    content: str
    data: Any
    metadata: dict[str, Any] = {}

class MyTool(FridayTool):
    name = "my_tool"
    class Input(BaseModel): ...
    async def run(self, args: Input) -> ToolResult: ...
```

### Step 2.2: Port Inspection Logic (Read-Only)
Migrate logic from `cmd_entities`, `cmd_facts`, `cmd_memory`.

*   **`GraphInspectionTool`**:
    *   `list_nodes(limit, type_filter)`
    *   `list_edges(limit)`
    *   `get_stats()`
*   **`VectorInspectionTool`**:
    *   `search(query, type_filter)`
    *   `list_documents(limit, type_filter)`

### Step 2.3: Port Maintenance Logic (Destructive)
Migrate logic from `cmd_reorganize`, `cmd_reset`.

*   **`MemoryMaintenanceTool`**:
    *   `prune_graph(dry_run=True)`
    *   `consolidate_memory(dry_run=True)`
    *   *Safety:* Hard-code `backup_first=True` by default.
*   **`MemoryResetTool`**:
    *   `reset_all()`: Requires strict confirmation flag.

### Step 2.4: Port Lifecycle Logic
Migrate logic from `cmd_lifecycle`.

*   **`LifecycleTool`**:
    *   `run_promotion_cycle()`
    *   `get_lifecycle_stats()`

### Step 2.5: Create System Health Tool (New)
For Sentinel Mode.

*   **`SystemHealthTool`**:
    *   `check_resources()`: Returns CPU, RAM, Disk usage.

## 3. Verification Plan

### Step 3.1: Unit Testing (Mandatory)
We will create specific test files in `packages/friday-tools/tests_tools/` for each domain. These tests must mock the dependencies (`MemoryController`, `psutil`) to verify logic in isolation.

*   `tests/test_base.py`: Verify Pydantic validation and error handling of the base `FridayTool`.
*   `tests/test_memory_tools.py`: Verify `GraphInspectionTool`, `MemoryMaintenanceTool`, etc.
*   `tests/test_system_tools.py`: Verify `SystemHealthTool`.

### Step 3.2: Integration Testing
We will create a new test script: `tests/integration/tools/test_tool_liberation.py`.

**Scenario:**
1.  Initialize `MemoryController` (using existing test fixtures).
2.  Instantiate `GraphInspectionTool`.
3.  Add a dummy node to memory.
4.  Run `GraphInspectionTool.list_nodes()` and assert it returns the node.
5.  Instantiate `MemoryMaintenanceTool`.
6.  Run `prune_graph(dry_run=True)` and verify it generates a report.

### Step 3.5: Create Reference Implementation (`tool-chat.py`)
We will create `tests/integration/tools/tool-chat.py`. This will be a clone of `memory-chat.py` refactored to use `friday-tools` for all its commands instead of direct controller access.

**Critical Goal: Continuity of Memory**
*   This script will be configured to use the **same persistence directory** as `memory-chat.py`.
*   This validates that the new Tools can seamlessly read, modify, and reorganize existing memory created by the legacy script, ensuring no data is lost during the architectural migration.

## 4. Dependencies
*   `friday-memory` (for Controller access)
*   `friday-core` (for Interfaces)
*   `psutil` (new dependency for SystemHealthTool)

## 5. Exit Criteria
*   All identified commands in `memory-chat.py` have a corresponding Tool class.
*   `friday-tools` builds and passes unit tests.
*   A "Headless" script can perform memory maintenance without user input.
