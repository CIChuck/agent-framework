# **Friday Framework \- Component Specifications \- Batch 0**

**Focus:** Project Scaffolding, Architecture, & Operational Fundamentals

Context:  
Before implementing the Data (Batch 1\) or Intelligence (Batch 2\) layers, we must establish the physical and logical environment. This specification defines the Workspace-based Monorepo strategy, enabling modularity and reusability while maintaining a cohesive developer experience.

## **1\. Architectural Strategy: The Workspace Monorepo**

We will use a **Monorepo** structure managed by **uv Workspaces**. This allows us to develop distinct, publishable packages side-by-side with the main application.

### **1.1. Why this approach?**

* **Modularity:** friday-memory can be used by *other* apps without importing the entire Friday CLI.  
* **Testability:** Each package has its own test suite and dependencies.  
* **Speed:** uv handles dependency resolution across the workspace instantly.

### **1.2. Package Breakdown**

1. **packages/friday-core**: The foundational "glue."  
   * *Contains:* Shared Protocol Interfaces (ABCs), Custom Exceptions, **Telemetry/Logging Interfaces**, Configuration Logic.  
   * *Dependencies:* pydantic, pydantic-settings.  
2. **packages/friday-memory**: The Brain (Batch 1 & 2).  
   * *Contains:* MemoryController, ContextEngine, Graph/Vector Adapters.  
   * *Dependencies:* friday-core, chromadb, networkx, litellm (Critical for auto-classification/summarization logic).  
3. **apps/friday-cli**: The Application (Batch 3+).  
   * *Contains:* The REPL, FastAPI server, Agent Orchestrator.  
   * *Dependencies:* friday-memory, typer, fastapi, uvicorn.

## **2\. Directory Structure (The Skeleton)**

The AI Builder must strictly adhere to this file tree.

friday-monorepo/  
├── pyproject.toml              \# Workspace root definition  
├── uv.lock                     \# Locked dependencies for the whole workspace  
├── .env.example                \# Template for environment variables  
├── .gitignore  
├── README.md  
│  
├── packages/  
│   ├── friday-core/            \# \[Package\] Foundation  
│   │   ├── pyproject.toml  
│   │   ├── src/  
│   │   │   └── friday\_core/  
│   │   │       ├── \_\_init\_\_.py  
│   │   │       ├── interfaces.py   \# Protocol definitions  
│   │   │       ├── telemetry.py    \# \<--- NEW: Telemetry Interfaces  
│   │   │       ├── exceptions.py   \# Base error classes  
│   │   │       ├── logging.py      \# Structured logging adapter  
│   │   │       └── config.py       \# Base settings logic  
│   │   └── tests/  
│   │  
│   └── friday-memory/          \# \[Package\] Intelligence Layer  
│       ├── pyproject.toml  
│       ├── src/  
│       │   └── friday\_memory/  
│       │       ├── controllers/    \# MemoryController  
│       │       ├── adapters/       \# Graph/Vector wrappers  
│       │       └── context/        \# Context Engineering logic  
│       └── tests/  
│  
└── apps/  
    └── friday-cli/             \# \[App\] The Friday Assistant  
        ├── pyproject.toml  
        ├── src/  
        │   └── friday\_cli/  
        │       ├── main.py         \# Entry point  
        │       └── repl.py  
        └── tests/

## **3\. Configuration Management (friday-core)**

We strictly avoid hardcoded paths. All configuration flows through Pydantic Settings.

### **3.1. Base Settings Class**

* **Location:** packages/friday-core/src/friday\_core/config.py  
* **Tech:** pydantic-settings  
* **Requirement:** Must support loading from .env file and Environment Variables.

from pydantic\_settings import BaseSettings, SettingsConfigDict

class FridayBaseSettings(BaseSettings):  
    """Global settings inherited by all packages."""  
    APP\_ENV: str \= "development" \# development | production | testing  
    LOG\_LEVEL: str \= "INFO"  
      
    \# LLM Settings (needed by Memory components)  
    DEFAULT\_MODEL: str \= "gpt-4-turbo"  
    OPENAI\_API\_KEY: str | None \= None  
      
    model\_config \= SettingsConfigDict(  
        env\_file=".env",   
        env\_file\_encoding="utf-8",   
        extra="ignore"  
    )

### **3.2. Configuration Injection Strategy (Dependency Injection)**

**Strict Rule:** Inner components (like MemoryController, ContextEngine) **MUST NOT** instantiate FridayBaseSettings or read environment variables internally.

Instead, the **Application** (e.g., friday-cli or a test runner) is responsible for loading the configuration and passing specific values or the config object into the constructors.

* **Bad Pattern (Forbidden):**  
  class ContextEngine:  
      def \_\_init\_\_(self):  
          \# VIOLATION: Implicit state, hard to test, tightly coupled to env files  
          self.config \= FridayBaseSettings()   
          self.model \= self.config.DEFAULT\_MODEL

* **Good Pattern (Required):**  
  class ContextEngine:  
      def \_\_init\_\_(self, model\_name: str, api\_key: str):  
          \# CLEAN: State is explicit. Can be easily mocked for tests.  
          self.model\_name \= model\_name  
          self.api\_key \= api\_key

  \# Usage in App:  
  \# settings \= FridayBaseSettings()  
  \# engine \= ContextEngine(model\_name=settings.DEFAULT\_MODEL, api\_key=settings.OPENAI\_API\_KEY)

## **4\. Operational Utilities (friday-core)**

### **4.1. Structured Logging Interface**

We do not use bare print or standard logging directly in business logic. We wrap it to allow future injection of OpenTelemetry/Structuring without refactoring.

* **Goal:** Provide a get\_logger(name) factory.  
* **Format:** JSON in production, colored text in development (using structlog or loguru as the implementation detail, but exposed via a stable interface).

### **4.2. Error Taxonomy**

Define the base exceptions so integration tests can catch specific failure modes.

* **Location:** packages/friday-core/src/friday\_core/exceptions.py  
* **Classes:**  
  * FridayError(Exception): Root class.  
  * MemoryError(FridayError): Base for DB failures.  
  * ContextOverflowError(FridayError): Raised when Context Budget is impossible to satisfy.  
  * ProviderAPIError(FridayError): LLM provider failures.

### **4.3. Telemetry & Inspection Hooks (New)**

We must be able to inspect the internal decision-making process of the Agent (e.g., "Why did you recall X?") during tests without breaking encapsulation.

* **Location:** packages/friday-core/src/friday\_core/telemetry.py  
* **Interface:** TelemetryInterface (Protocol)  
  class TelemetryInterface(ABC):  
      @abstractmethod  
      def capture\_event(self, event\_name: str, data: Dict\[str, Any\]):  
          """Records a discrete event (e.g., 'memory\_recall', 'tool\_usage')."""  
          pass

      @abstractmethod  
      def start\_span(self, name: str, parent\_id: Optional\[str\] \= None):  
          """Starts a trace span for duration tracking."""  
          pass

* **Test Implementation:** DebugTelemetryRecorder  
  * This class simply appends events to a list self.events.  
  * **Usage in Tests:**  
    def test\_recall\_flow():  
        recorder \= DebugTelemetryRecorder()  
        controller \= MemoryController(..., telemetry=recorder)  
        await controller.recall("test")

        \# White-box assertion on internal logic  
        assert "graph\_search\_skipped" in recorder.events  
        assert recorder.get\_event("vector\_search")\["latency"\] \< 0.5

## **5\. Development Tooling & Standards**

### **5.1. Package Manager: uv**

* **Workspace Config (/pyproject.toml):**  
  \[tool.uv.workspace\]  
  members \= \["packages/\*", "apps/\*"\]

* **Workflow:**  
  * Add dependency: uv add pydantic \--package friday-core  
  * Run tests: uv run pytest  
  * Sync environment: uv sync

### **5.2. Linting & Formatting**

* **Tool:** ruff (Managed via uv).  
* **Policy:**  
  * Strict Line Length: 88 (Black compatible).  
  * Import Sorting: Enforced.  
  * Unused Imports: Error.

### **5.3. Type Checking**

* **Tool:** mypy (Managed via uv).  
* **Policy:** Strict mode enabled. All public interfaces must have type hints.

## **6\. Test Strategy**

We adopt a "Pyramid" strategy, enabled by the package structure.

### **6.1. Unit Tests (Per Package)**

* **Scope:** Individual classes (e.g., ContextAssembler, PydanticGraphNode).  
* **Location:** packages/\*/tests/unit/  
* **Constraint:** **NO** external I/O. DBs must be mocked (or use in-memory variants like NetworkX / Chroma-Ephemeral).  
* **Execution:** Fast (\< 1s per test).

### **6.2. Integration Tests (Per Package)**

* **Scope:** Adapter interactions (e.g., GraphStoreAdapter writing to disk).  
* **Location:** packages/\*/tests/integration/  
* **Constraint:** Allowed to touch file system or local containers.

### **6.3. Functional Tests (App Level)**

* **Scope:** Full Agent loop (CLI Input \-\> Thought \-\> Action).  
* **Location:** apps/friday-cli/tests/  
* **Tooling:** pytest-asyncio.

## **7\. Acceptance Criteria for Batch 0**

1. **Repo Setup:** Running uv sync in the root successfully creates the virtual environment and installs all workspace members in editable mode.  
2. **Import Test:** friday-cli can import MemoryController from friday-memory without path hacking.  
3. **Config Test:** Creating a .env file with LOG\_LEVEL=DEBUG is correctly reflected when initializing FridayBaseSettings.  
4. **Lint Check:** Running uv run ruff check . passes on the skeleton code.  
5. **Injection Test:** Verify MemoryController can be initialized with a mock config object for testing, proving no dependency on a real .env file exists in the core logic.  
6. **Telemetry Test:** A unit test must successfully inject a DebugTelemetryRecorder into a core component and verify that an event is recorded when a method is called.