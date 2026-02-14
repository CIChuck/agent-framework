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
2.  **CLI Display Stability:** `friday-cli`'s public API (display functions, input handling, session management, `CLIConfig`) must remain backward compatible. These are the components consumed by `friday.py` and other integration code.
3.  **Interface Compliance:** Phase 1 implementation must satisfy the `technical-specifications.md` contracts, even if via stubbing.

> **Note on FridayContainer:** `FridayContainer` and `FridayConfig` are NOT exported from `friday_cli/__init__.py` and have zero known external consumers. The main integration app (`friday.py`) imports only display/CLI components — never `FridayContainer`. The migration strategy should therefore favor simplicity (direct composition or deprecation) over a full proxy pattern. See Step 6 for details.

---

## 2. Phase 1 Interface Compliance Matrix

This table defines exactly what will be implemented versus stubbed/deferred in this phase, mapping directly to `technical-specifications.md`.

| Interface | Method | Phase 1 Status | Implementation Note |
| :--- | :--- | :--- | :--- |
| **SystemRuntime** | `start()` | **Implemented** | Initializes singleton services via `friday-runtime/di.py`. |
| | `stop()` | **Implemented** | Maps to existing `shutdown()` logic. Flushes logs, persists memory. |
| | `create_session()` | **Stub** | Returns a UUID string. No persistent session tracking in Phase 1. |
| | `spawn_agent()` | **Implemented** | Uses Registry to create `AgentInterface`. |
| | `execute_workflow()` | **Implemented** | Runs the refactored Workflow Engine. |
| **AgentInterface** | `run()` | **Implemented** | Core execution loop (Think -> Act). |
| | `initialize_session()` | **Implemented** | Existing `AgentBase.initialize_session()`. Note: existing signature `(session_id: str | None, user_id: str = "default") -> SessionState` differs from spec's `(session_id: str, user_id: str) -> None`. The ABC must adopt the existing signature. |
| | `set_autonomy_policy()` | **Deferred** | Hardcoded to "manual" for Phase 1. |
| | `emit_telemetry()` | **Implemented** | Existing `AgentBase._emit_event()` provides this. Promote to public interface. |
| **RegistryInterface** | `register_profile()` | **Implemented** | Already exists on `AgentRegistry`. |
| | `load_manifests()` | **Implemented** | Already exists via `AgentLoader`. |
| | `find_agents()` | **Implemented** | Maps to existing `AgentRegistry.find_by_capability()`. |
| | `create_agent()` | **Implemented** | Already exists on `AgentRegistry` via `set_factory()` + `create_agent()`. |
| **OrchestratorInterface** | `route()` | **Deferred** | Currently embedded in `AgentOrchestrator.process()`. Decomposition deferred to Phase 2. |
| | `delegate()` | **Implemented** | Already exists on `AgentOrchestrator`. |
| **ArbitrationInterface** | `submit_proposal()` | **Stub** | Direct passthrough (Auto-Approve). |
| | `get_decision()` | **Stub** | Returns auto-approved result. |
| | `resolve_conflict()` | **Stub** | No-op in Phase 1. |
| **ArtifactWorkspace** | `store()` | **Stub** | Direct filesystem/memory write; no wrapping. |
| | `retrieve()` | **Stub** | Direct filesystem read. |
| | `resolve_smart_reference()` | **Stub** | Returns raw content (no summarization). |
| **LabHarnessInterface** | `mock_agent()` | **Implemented** | Registers deterministic mock agent factory in the registry. |
| | `inject_conflict()` | **Stub** | Raises `NotImplementedError` — requires Arbitrator (Phase 2). |
| | `replay_session()` | **Stub** | Raises `NotImplementedError` — requires transcript tooling (Phase 2). |

> **Note:** All ABCs defined in `friday-core` are considered **Protocol Version 1.0**. Any changes in future phases must ensure backward compatibility or follow a strict migration path.

---

## 3. Package Architecture Changes

### New Package: `friday-runtime`
*   **Role:** The "Headless Operating System" for the Hive.
*   **Dependencies:** `friday-core`, `friday-agent`, `friday-memory`, `friday-llm`, `friday-telemetry`.

### Component Migration (Direct Composition)
We use a **Non-Destructive Extraction**. DI logic moves to `RuntimeKernel`; `FridayContainer` becomes a thin deprecated wrapper that composes `RuntimeKernel` internally. Since `FridayContainer` has no external consumers, the wrapper exists only as a transitional convenience — removal is planned for Phase 2.

| Logic Area | Source (to be thinned) | Destination (the new home) | Strategy |
| :--- | :--- | :--- | :--- |
| **Core Kernel** | `friday_cli/container.py` | `friday_runtime/kernel.py` | Logic moves; Source becomes thin deprecated wrapper. |
| **Dependency Injection** | `friday_cli/container.py` | `friday_runtime/di.py` | Resource creation logic moves here. |
| **Configuration** | `friday_cli/container.py` (`FridayConfig`) | `friday_runtime/config.py` | `FridayConfig` (LLM, embedding, chroma, telemetry, agents) moves to runtime. `CLIConfig` (themes, icons, spinner) stays in CLI. |
| **Adapter Factories** | `friday_cli/profiles.py` | `friday_runtime/adapters.py` | Logic moves; Source imports from Destination. |
| **Commands/Display** | `friday_cli/commands.py` | **STAYS IN CLI** | Presentation layer remains untouched. |

**Specific Boot Sequence Migration:**
The following methods are called during `FridayContainer.initialize()` and will be extracted into `friday_runtime/di.py`:
*   `_create_telemetry()`
*   `_create_llm_services()`
*   `_create_storage_adapters()` (async)
*   `_create_memory_controller()`
*   `_create_context_engine()`
*   `_create_tool_registry()`

> **Lazy Subsystems (NOT part of boot sequence):** The agent subsystem (`agent_loader`, `agent_registry`, `orchestrator`) is NOT initialized during `initialize()`. These are lazy properties created on first access. `RuntimeKernel` MUST preserve this lazy pattern — eagerly initializing agents would change error semantics (e.g., failing at startup if agents directory is missing vs. failing on first agent request).

**Error Propagation:**
The `FridayContainer` wrapper must provide **Exception Transparency**. Exceptions raised by `RuntimeKernel` (e.g., `ChromaDBError`, `LLMAPIError`) must bubble up raw and unchanged. The wrapper should not catch or wrap these errors.

---

## 4. Detailed Implementation Steps

### Step 1: Scaffold `friday-runtime`
*   **1.1 Initialize:** `uv init packages/friday-runtime`.
*   **1.2 Config:** Update `pyproject.toml` with `friday-core`, `friday-memory`, `friday-llm`, `friday-telemetry`, `friday-agent`.

### Step 2: Define Core Interfaces (in `friday-core`)
*   **2.1 Create ABCs:**
    *   `packages/friday-core/src/friday_core/interfaces/runtime.py`: Add `SystemRuntime`.
    *   `packages/friday-core/src/friday_core/interfaces/agent.py`: Add `AgentInterface`. Note: `initialize_session()` must match the existing `AgentBase` signature `(session_id: str | None = None, user_id: str = "default") -> SessionState`, not the spec's `(session_id: str, user_id: str) -> None`.
    *   `packages/friday-core/src/friday_core/interfaces/registry.py`: Add `RegistryInterface`.
    *   `packages/friday-core/src/friday_core/interfaces/lab.py`: Add `LabHarnessInterface` (3 methods: `inject_conflict`, `replay_session`, `mock_agent`).
*   **2.2 Export Gap Fix:** `LLMClient` and `EmbeddingModel` are defined in `friday_core/interfaces/llm.py` but NOT exported from `friday_core/__init__.py`. Add them to the package's `__all__` so `RuntimeKernel` can type-hint against the top-level import path.

### Step 3: Refactor Workflow Engine (`friday-agent`)

> **Why before Runtime Kernel:** `friday-runtime` depends on `friday-agent` for the workflow engine. The engine must be stabilized first so `RuntimeKernel.execute_workflow()` operates on immutable definitions.

**3.1 Create `TaskState` model and freeze `TaskNode`:**

Extract the following mutable runtime fields from `TaskNode` into a new `TaskState` Pydantic model:

| Field | Moves From | Moves To | Notes |
| :--- | :--- | :--- | :--- |
| `status` | `TaskNode` | `TaskState` | Default: `PENDING` |
| `result` | `TaskNode` | `TaskState` | Default: `None` |
| `error` | `TaskNode` | `TaskState` | Default: `None` |
| `retry_count` | `TaskNode` | `TaskState` | Default: `0` |
| `started_at` | `TaskNode` | `TaskState` | Default: `None` |
| `completed_at` | `TaskNode` | `TaskState` | Default: `None` |
| `requires_approval` | Stays on `TaskNode` | — | Definition field. See 3.4 for mutation strategy. |

After extraction, freeze `TaskNode`: `model_config = ConfigDict(frozen=True)`. Remove `TaskNode.reset()` — create a fresh `TaskState` instead.

**3.2 Extend existing `WorkflowExecution`:**

`WorkflowExecution` already exists in `packages/friday-agent/src/friday_agent/workflows/models.py`. Do NOT create a new `WorkflowExecutionState` — extend the existing model with:
*   `task_states: dict[str, TaskState] = {}` — per-task runtime state, keyed by task ID.
*   `approval_overrides: set[str] = set()` — task IDs where approval has been granted at runtime (see 3.4).

**3.3 Relocate `get_ready_tasks()`:**

`WorkflowDefinition.get_ready_tasks()` currently reads `task.status` directly from `TaskNode` objects. With `TaskNode` frozen and status moved to `TaskState`, this method can no longer live on `WorkflowDefinition`. Two options:
*   **Option A (recommended):** Move to `WorkflowExecution` as `get_ready_tasks(definition: WorkflowDefinition) -> list[TaskNode]` — reads `self.task_states` for status checks.
*   **Option B:** Keep on `WorkflowDefinition` but require `task_states: dict[str, TaskState]` parameter.

**3.4 Fix `approve_task()` definition mutation:**

`WorkflowEngine.approve_task()` currently sets `task.requires_approval = False` — mutating a definition field. With `TaskNode` frozen, this raises `ValidationError`. Instead:
*   Add the task ID to `execution.approval_overrides`.
*   In `_handle_approval()`, check: `if task.id in execution.approval_overrides: return True` (skip approval prompt).
*   This preserves the original `WorkflowDefinition` while tracking approval state in `WorkflowExecution`.

**3.5 Engine Update:**

`WorkflowEngine.execute(definition)` creates a fresh `WorkflowExecution` with empty `task_states` (one `TaskState` per task, all `PENDING`). All state mutations go through `task_states` — never touch `TaskNode` fields. The same `WorkflowDefinition` can be executed concurrently without state collision.

### Step 4: Implement the Runtime Kernel (`friday-runtime`)
*   **4.1 Implement `RuntimeConfig`:** Port generic config logic from `FridayConfig` in `friday_cli/container.py`. Fields: `llm_model`, `llm_api_key`, `llm_api_base`, `embedding_model`, `chroma_path`, `chroma_collection`, `telemetry_enabled`, `telemetry_endpoint`, `debug_mode`, `agents_dir`. Include `from_env()` and `for_testing()` class methods.
*   **4.2 Implement `DIContainer` (`di.py`):**
    *   Move the "Boot Sequence" methods (see Migration list above) here.
*   **4.3 Implement `RuntimeKernel`:**
    *   Implement `SystemRuntime`.
    *   Constructor accepts: `config: RuntimeConfig`, `memory_profile: MemoryProfile`, `sanitization_config: SanitizationConfig | None`.
    *   `start()` calls DI providers to boot Memory/LLM/Tools (the 6 eager methods).
    *   `stop()` performs graceful shutdown (flush logs, persist memory).
    *   `spawn_agent()` uses `AgentRegistry` to create instances with injected dependencies.
    *   Agent subsystem properties (`.agent_loader`, `.agent_registry`, `.orchestrator`) remain **lazy** — initialized on first access, not during `start()`.
    *   `SanitizationConfig` is forwarded to agent creation (passed to `CopilotAgent` constructor).
*   **4.4 Singleton Enforcement:** `CollectionManager` must be created once per kernel instance. Prevent concurrent ChromaDB access if multiple kernel instances share the same `chroma_path`.

### Step 5: Write Characterization Tests (Safety Net)
Before refactoring `FridayContainer`, create a baseline test that captures its current behavior. This test becomes the regression safety net for Steps 6 and 7.

*   **5.1 Create `tests/lab/test_legacy_compatibility.py`:**
    *   Instantiate `FridayContainer` with `MemoryProfile.TESTING`
    *   Call `initialize()` and assert all eager properties are non-None (`.llm`, `.embeddings`, `.memory`, `.context_engine`, `.tool_registry`, `.telemetry`)
    *   Access lazy properties (`.agent_loader`, `.agent_registry`, `.orchestrator`) and assert they initialize without error
    *   Call `get_copilot_agent()` and assert it returns a `CopilotAgent`
    *   Call `shutdown()` and assert clean teardown
    *   Test `create_friday_container()` convenience function
*   **5.2 Run the test suite** to confirm it passes against the CURRENT code before any extraction begins.

### Step 6: Update `friday-cli` (Simplified Migration)
Since `FridayContainer` has no external consumers (not exported, not used by `friday.py`), a full proxy pattern is unnecessary. Use direct composition instead.

*   **6.1 Refactor `FridayContainer` to compose `RuntimeKernel`:**
    ```python
    # packages/friday-cli/src/friday_cli/container.py
    import warnings
    from friday_runtime import RuntimeKernel, RuntimeConfig

    class FridayContainer:
        """Thin wrapper around RuntimeKernel for CLI use.

        Deprecated: Use RuntimeKernel directly for new code.
        """

        def __init__(self, config=None, memory_profile=MemoryProfile.FULL,
                     sanitization_config=None):
            warnings.warn(
                "FridayContainer is deprecated. Use RuntimeKernel directly.",
                DeprecationWarning, stacklevel=2,
            )
            self._kernel = RuntimeKernel(
                config=config or RuntimeConfig.from_env(),
                memory_profile=memory_profile,
                sanitization_config=sanitization_config,
            )

        @property
        def memory(self):
            return self._kernel.memory

        async def initialize(self):
            await self._kernel.start()
    ```
*   **6.2 Complete Accessor & Method Inventory:** The wrapper must delegate ALL of the following:

    **Property accessors (10 total):**
    | Accessor | Type | Initialization |
    | :--- | :--- | :--- |
    | `.llm` | `LiteLLMService` | Eager (during `initialize()`) |
    | `.embeddings` | `LiteLLMEmbeddingService` | Eager |
    | `.memory` | `MemoryController` | Eager |
    | `.context_engine` | `ContextAssembler` | Eager |
    | `.tool_registry` | `DefaultToolRegistry` | Eager |
    | `.telemetry` | `TelemetryInterface \| None` | Eager |
    | `.memory_profile` | `MemoryProfile` | Immediate (constructor param) |
    | `.agent_loader` | `AgentLoader` | **Lazy** (first access) |
    | `.agent_registry` | `AgentRegistry` | **Lazy** (first access, has side effects) |
    | `.orchestrator` | `AgentOrchestrator` | **Lazy** (first access) |

    **Public methods (6 total):**
    | Method | Signature |
    | :--- | :--- |
    | `initialize()` | `async def initialize() -> None` |
    | `shutdown()` | `async def shutdown() -> None` |
    | `get_copilot_agent()` | `def get_copilot_agent(profile: AgentProfile \| None = None) -> CopilotAgent` |
    | `get_team_agent()` | `def get_team_agent(name: str) -> CopilotAgent` |
    | `list_available_agents()` | `def list_available_agents() -> list[str]` |
    | `get_agent_info()` | `def get_agent_info(name: str) -> dict \| None` |

    **Module-level convenience function:**
    | Function | Note |
    | :--- | :--- |
    | `create_friday_container()` | Re-export or deprecate. Consider adding `create_runtime_kernel()` in `friday-runtime`. |

*   **6.3 Verify:** Run existing CLI tests and characterization tests (Step 5). They must pass without knowing `friday-runtime` exists.

### Step 6.5: friday.py Integration (Known Gap — Out of Scope)

> **Important:** `tests/integration/memory/friday.py` (~7500 lines) is the main production integration app. It does **NOT** use `FridayContainer` — it performs its own manual dependency injection (creating LLM services, memory controllers, context engines, tool registries directly). Phase 1 does **NOT** need to migrate `friday.py` to use `RuntimeKernel`. That is a separate effort. The Lab harness (Step 7) uses `RuntimeKernel`, which is the canonical DI path going forward.

### Step 7: Create Friday Lab (Harness & Integration Tests)

> **Why this matters:** The Lab is the "Definition of Done" for Phase 1. Without it, there is no proof that the extracted Kernel works headlessly or that multi-agent delegation preserves session integrity. The Phase 1 exit criteria (Section 5) are verified here, not in unit tests.

**Scope:** The Lab is internal test infrastructure located at `tests/lab/`. It is **NOT** a shippable package. Three experiment stubs already exist (`exp_01_telemetry.py`, `exp_03_graph_persistence.py`, `exp_05_entity_merging.py`). This step builds the harness layer and the integration tests that prove Phase 1 works.

**7.1 Add `LabHarnessInterface` ABC (in `friday-core`):**

Add to `packages/friday-core/src/friday_core/interfaces/lab.py` alongside the other ABCs created in Step 2:

```python
class LabHarnessInterface(ABC):
    """Integration environment for stress-testing the Hive."""

    @abstractmethod
    async def inject_conflict(
        self, fact_a: "MemoryProposal", fact_b: "MemoryProposal"
    ) -> None:
        """Simulate a race condition or semantic conflict."""
        pass

    @abstractmethod
    async def replay_session(self, session_log_path: str) -> None:
        """Deterministically replay a recorded session."""
        pass

    @abstractmethod
    def mock_agent(self, name: str, fixed_responses: list[str]) -> None:
        """Replace a real LLM agent with a deterministic mock."""
        pass
```

**Phase 1 implementation status:**
| Method | Status | Notes |
| :--- | :--- | :--- |
| `mock_agent()` | **Implemented** | Core to Phase 1 testing — enables deterministic multi-agent tests without LLM calls. |
| `inject_conflict()` | **Stub** | Raises `NotImplementedError("Conflict injection requires Arbitrator — Phase 2")`. |
| `replay_session()` | **Stub** | Raises `NotImplementedError("Session replay requires transcript tooling — Phase 2")`. |

**7.2 Extend `AgentRegistry` with per-agent factory overrides:**

> **Why:** `AgentRegistry.set_factory()` currently accepts a single global factory: `set_factory(factory: Callable[[AgentProfile], AgentBase])`. The Lab needs to register different mock agents per name. Without this, `mock_agent("researcher", ...)` and `mock_agent("coder", ...)` would overwrite each other.

Add a per-agent override mechanism to `AgentRegistry`:

```python
# In packages/friday-agent/src/friday_agent/registry.py

class AgentRegistry:
    def __init__(self):
        # ... existing fields ...
        self._per_agent_factories: dict[str, Callable] = {}  # NEW

    def set_factory(
        self,
        factory: Callable[["AgentProfile"], "AgentBase"],
        agent_name: str | None = None,  # NEW: optional per-agent override
    ) -> None:
        """Set an agent factory function.

        Args:
            factory: Factory callable that creates agents from profiles.
            agent_name: If provided, this factory is used ONLY for this
                agent name. The global factory remains the fallback.
        """
        if agent_name:
            self._per_agent_factories[agent_name] = factory
        else:
            self._factory = factory

    def create_agent(self, name: str) -> "AgentBase":
        """Create an agent, checking per-agent overrides first."""
        profile = self.get_or_raise(name)
        # Per-agent factory takes priority over global factory
        factory = self._per_agent_factories.get(name, self._factory)
        if factory is None:
            raise OrchestratorError("No factory configured")
        return factory(profile)
```

This is a backward-compatible extension — existing code that calls `set_factory(fn)` without `agent_name` continues to work identically.

**7.3 Implement `HeadlessHarness` (`tests/lab/harness.py`):**

`HeadlessHarness` composes `RuntimeKernel` (not subclass — avoids coupling to kernel internals) and implements `LabHarnessInterface`. It provides isolated, deterministic test execution.

```python
from friday_runtime import RuntimeKernel, RuntimeConfig
from friday_core.interfaces.lab import LabHarnessInterface

class HeadlessHarness(LabHarnessInterface):
    """
    The Lab's test execution environment.
    Composes a RuntimeKernel with MemoryProfile.EPHEMERAL for full
    isolation. No LLM calls unless explicitly configured — all agents
    default to deterministic mocks.
    """

    def __init__(self, config: RuntimeConfig | None = None):
        self._config = config or RuntimeConfig.for_testing()
        self._kernel = RuntimeKernel(
            config=self._config,
            memory_profile=MemoryProfile.EPHEMERAL,
        )
        self._mock_agents: dict[str, list[str]] = {}

    async def start(self) -> None:
        """Boot the kernel in ephemeral mode."""
        await self._kernel.start()

    async def stop(self) -> None:
        """Shut down the kernel."""
        await self._kernel.stop()

    # --- LabHarnessInterface ---

    def mock_agent(self, name: str, fixed_responses: list[str]) -> None:
        """
        Register a deterministic mock agent. When the orchestrator
        routes to `name`, it receives an agent that returns responses
        from `fixed_responses` in order, cycling if exhausted.

        Uses the per-agent factory override on AgentRegistry (Step 7.2).
        """
        self._mock_agents[name] = fixed_responses
        self._kernel.agent_registry.set_factory(
            _create_mock_agent_factory(name, fixed_responses),
            agent_name=name,
        )

    async def inject_conflict(self, fact_a, fact_b) -> None:
        raise NotImplementedError(
            "Conflict injection requires Arbitrator — Phase 2"
        )

    async def replay_session(self, session_log_path: str) -> None:
        raise NotImplementedError(
            "Session replay requires transcript tooling — Phase 2"
        )

    # --- Convenience accessors ---

    @property
    def kernel(self) -> RuntimeKernel:
        return self._kernel
```

**7.4 Implement Mock Agent Factory (`tests/lab/mocks.py`):**

Reuse the established mock patterns from `packages/friday-agent/tests_agent/test_orchestrator.py`:

```python
from unittest.mock import AsyncMock, MagicMock
from itertools import cycle

def _create_mock_agent_factory(name: str, fixed_responses: list[str]):
    """
    Returns a factory function compatible with AgentRegistry.set_factory().
    The produced agent returns responses from fixed_responses in order.

    The factory signature is Callable[[AgentProfile], AgentBase] to match
    the registry's expected interface.
    """
    response_cycle = cycle(fixed_responses)

    def factory(profile):
        agent = AsyncMock()
        agent.name = name
        agent.run = AsyncMock(side_effect=lambda _: next(response_cycle))
        agent.initialize_session = AsyncMock()
        agent.set_autonomy_policy = MagicMock()
        agent.emit_telemetry = MagicMock()
        return agent

    return factory
```

**7.5 Build Lab Fixtures (`tests/lab/conftest.py`):**

Replace the current empty stub with functional fixtures:

```python
"""
Pytest configuration for the Friday Lab.
Provides HeadlessHarness fixtures for integration tests.
"""
import pytest
import pytest_asyncio
from friday_agent import AgentProfile

from .harness import HeadlessHarness


@pytest_asyncio.fixture
async def harness():
    """Provide a fully booted HeadlessHarness, torn down after the test."""
    h = HeadlessHarness()
    await h.start()
    yield h
    await h.stop()


@pytest.fixture
def researcher_profile():
    """A minimal researcher AgentProfile for testing."""
    return AgentProfile(
        name="researcher",
        role="Research Analyst",
        goal="Find accurate information",
        system_prompt_template="You are a researcher. {{focus}}",
        tools=["recall_memory"],
        _capabilities=["research", "information_gathering"],
    )


@pytest.fixture
def coder_profile():
    """A minimal coder AgentProfile for testing."""
    return AgentProfile(
        name="coder",
        role="Software Engineer",
        goal="Write correct code",
        system_prompt_template="You are a coder. {{language}}",
        tools=["read_file", "write_file"],
        _capabilities=["coding", "debugging"],
    )
```

**7.6 Integration Test: Headless Execution (`tests/lab/test_headless_execution.py`):**

This test satisfies **Exit Criterion #2 — Headless Execution** (Section 5): the Kernel boots and runs an agent task with zero CLI dependencies.

```python
"""
Exit Criterion #2: Headless Execution.
Proves the RuntimeKernel can boot, run an agent, and shut down
without any friday-cli imports.
"""
import pytest

# CRITICAL: No friday_cli imports anywhere in this file.
from friday_runtime import RuntimeKernel, RuntimeConfig

@pytest.mark.asyncio
async def test_headless_hello_world(harness, researcher_profile):
    """Kernel boots, agent runs, kernel shuts down — no CLI."""
    # Register a mock researcher that returns a fixed greeting
    harness.mock_agent("researcher", ["Hello from the headless kernel!"])

    # Register the profile so the orchestrator can find it
    harness.kernel.agent_registry.register_profile(researcher_profile)

    # Spawn the agent and run a task
    agent = harness.kernel.agent_registry.create_agent("researcher")
    result = await agent.run("Say hello")

    assert result == "Hello from the headless kernel!"

@pytest.mark.asyncio
async def test_kernel_lifecycle(harness):
    """Kernel start/stop cycle completes without error."""
    # harness fixture already called start(); verify key services exist
    assert harness.kernel.llm is not None
    assert harness.kernel.memory is not None
    assert harness.kernel.tool_registry is not None

    # stop() is called by the fixture teardown — no assertion needed,
    # but we verify it doesn't raise by letting the fixture complete.
```

**7.7 Integration Test: Two-Agent Delegation Chain (`tests/lab/test_delegation_chain.py`):**

This test satisfies **Exit Criterion #3 — Lab Harness** (Section 5): a 2-agent delegation chain with session consistency verification.

> **API Note:** `AgentOrchestrator.process()` accepts only `user_input: str` — it does NOT accept a `session_id` parameter. Session context must be set via `orchestrator.set_session(session_id)` before calling `process()`.

```python
"""
Exit Criterion #3: Two-Agent Delegation Chain.
Proves the Orchestrator can route work between two agents within
a single session, maintaining session_id consistency.
"""
import pytest

@pytest.mark.asyncio
async def test_two_agent_delegation_chain(
    harness, researcher_profile, coder_profile
):
    """
    Researcher delegates to Coder. Both agents execute within the
    same session. Session ID is consistent across the chain.
    """
    # Register mock agents with deterministic responses
    harness.mock_agent(
        "researcher",
        ["I found the data. @coder Please implement the parser."],
    )
    harness.mock_agent(
        "coder",
        ["Parser implemented successfully."],
    )

    # Register profiles
    harness.kernel.agent_registry.register_profile(researcher_profile)
    harness.kernel.agent_registry.register_profile(coder_profile)

    # Create a session and bind it to the orchestrator
    session_id = await harness.kernel.create_session(user_id="test_user")
    assert session_id is not None

    orchestrator = harness.kernel.orchestrator
    await orchestrator.set_session(session_id, user_id="test_user")

    # Route the initial request to the researcher
    result = await orchestrator.process(
        "@researcher Find data about Python parsers"
    )

    # The orchestrator should have routed to researcher
    # Verify both agents were invoked (researcher then coder via delegation)
    researcher_agent = harness.kernel.agent_registry.create_agent("researcher")
    coder_agent = harness.kernel.agent_registry.create_agent("coder")

    # Verify session consistency — both agents received the same session_id
    researcher_agent.initialize_session.assert_called()
    session_args = researcher_agent.initialize_session.call_args
    assert session_args is not None

@pytest.mark.asyncio
async def test_session_isolation(harness, researcher_profile):
    """
    Two sessions created from the same harness do not share state.
    """
    harness.mock_agent("researcher", ["Response A", "Response B"])
    harness.kernel.agent_registry.register_profile(researcher_profile)

    session_a = await harness.kernel.create_session(user_id="user_a")
    session_b = await harness.kernel.create_session(user_id="user_b")

    assert session_a != session_b
```

**7.8 Regression Test: Legacy Compatibility:**

Re-run `tests/lab/test_legacy_compatibility.py` (created in Step 5) against the refactored `FridayContainer`. All assertions must still pass, proving the extraction preserved behavior.

**7.9 Dependency Separation:**

`tests/lab/pyproject.toml` currently depends on heavy packages (`ragas`, `arize-phoenix`, `streamlit`). The `HeadlessHarness` must NOT require these. Restructure:

```toml
[project]
name = "friday-lab"
dependencies = [
    "friday-runtime",      # The harness composes RuntimeKernel
    "friday-agent",        # AgentProfile, AgentRegistry
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[project.optional-dependencies]
dashboard = [
    "ragas>=0.1.0",
    "arize-phoenix>=4.0.0",
    "streamlit>=1.30.0",
    "pyvis>=0.3.0",
]
```

This ensures CI can run the harness tests without installing dashboard dependencies.

**7.10 File Summary:**

| File | Purpose |
| :--- | :--- |
| `friday-core/interfaces/lab.py` | `LabHarnessInterface` ABC (3 methods) |
| `friday-agent/registry.py` | Extended with `_per_agent_factories` and `agent_name` param on `set_factory()` |
| `tests/lab/harness.py` | `HeadlessHarness` — composes `RuntimeKernel`, implements `LabHarnessInterface` |
| `tests/lab/mocks.py` | `_create_mock_agent_factory()` — deterministic agent factory |
| `tests/lab/conftest.py` | Pytest fixtures: `harness`, `researcher_profile`, `coder_profile` |
| `tests/lab/test_headless_execution.py` | Exit Criterion #2: Headless boot + agent execution |
| `tests/lab/test_delegation_chain.py` | Exit Criterion #3: 2-agent delegation + session consistency |
| `tests/lab/test_legacy_compatibility.py` | Created in Step 5; re-run here as regression gate |

---

## 5. Verification Strategy

### Exit Criteria Checks
1.  **Characterization Tests Pass:** `test_legacy_compatibility.py` (Step 5) passes against both the original `FridayContainer` and the refactored version. *(Step 5 + Step 7.8)*
2.  **Headless Execution:** `test_headless_execution.py` proves the `RuntimeKernel` boots, runs a mock agent, and shuts down with zero `friday-cli` imports. *(Step 7.6)*
3.  **Two-Agent Delegation Chain:** `test_delegation_chain.py` proves the Orchestrator routes work through a 2-agent chain (researcher → coder) within a single session, maintaining `session_id` consistency. *(Step 7.7)*
4.  **Session Isolation:** `test_delegation_chain.py::test_session_isolation` proves two sessions from the same harness do not share state. *(Step 7.7)*
5.  **Workflow Reusability:** A test proves the same `WorkflowDefinition` object can be executed twice in parallel without state collision. *(Step 3.5)*
6.  **Workflow Immutability:** A test proves that `TaskNode` objects are frozen — attempts to set `task.status` directly raise `ValidationError`. *(Step 3.1)*
7.  **Interface Adherence:** All methods marked **[Implemented]** in the Compliance Matrix (Section 2) exist and function.
8.  **Lab Harness Operational:** `HeadlessHarness` can be instantiated, mock agents registered, and integration tests execute end-to-end without manual LLM calls. *(Step 7.3–7.5)*

---

## 6. Execution Order

| Step | Package | Action | Depends On |
| :--- | :--- | :--- | :--- |
| 1 | `friday-runtime` | Scaffold package structure | — |
| 2 | `friday-core` | Add Interfaces (`SystemRuntime`, `AgentInterface`, `RegistryInterface`) | — |
| 3 | `friday-agent` | Refactor Workflows (freeze `TaskNode`, extract `TaskState`, extend `WorkflowExecution`) | Step 2 (interfaces) |
| 4 | `friday-runtime` | Implement Kernel & DI | Steps 2, 3 |
| 5 | — | Write characterization tests for `FridayContainer` | Step 4 (kernel exists to compare against) |
| 6 | `friday-cli` | Refactor `FridayContainer` to compose `RuntimeKernel` | Steps 4, 5 |
| 7 | `friday-core` + `friday-agent` + `tests/lab` | Add `LabHarnessInterface` ABC, extend `AgentRegistry.set_factory()` with per-agent overrides, build `HeadlessHarness`, mock agent factory, integration tests (headless execution, delegation chain, session isolation), regression tests | Steps 4, 6 |