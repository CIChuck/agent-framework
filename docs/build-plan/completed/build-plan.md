# Friday Framework Build Plan

This document outlines the incremental build and testing plan for the Friday Agentic Framework, based on the component specifications.

## 1. Guiding Principles

- **Incremental Build:** Components will be built in a logical order based on their dependencies, starting from the core and moving outward.
- **Inside-Out Development:** The plan follows the "inside-out" approach requested, starting with foundational packages (`friday-core`) and progressively building towards the application layer (`friday-cli`).
- **Test-Driven Approach:** Each component's implementation will be accompanied by a corresponding suite of tests. The testing strategy is integral to verifying the correctness of each build phase.

## 2. Build Order

The implementation is divided into four main phases, corresponding to the packages in the monorepo.

### Phase 1: `packages/friday-core` (The Foundation)

This phase implements the cross-cutting concerns and shared interfaces that all other packages depend on. It directly corresponds to **Batch 0** and parts of **Batch 1** specifications.

1.  **`config.py`:** Implement `FridayBaseSettings` for environment-aware configuration.
2.  **`exceptions.py`:** Define the custom exception hierarchy (`FridayError`, `MemoryError`, etc.).
3.  **`logging.py`:** Implement the structured logging adapter.
4.  **`telemetry.py`:** Implement the `TelemetryInterface` protocol and the `DebugTelemetryRecorder` for testing.
5.  **`interfaces/` module:**
    -   `memory.py`: Define the data storage protocols: `EpisodicStoreAdapter`, `VectorStoreAdapter`, `GraphStoreAdapter`.
    -   `context.py`: Define the `ContextEngineeringInterface`.

### Phase 2: `packages/friday-memory` (The Intelligence Core)

This phase builds the framework's memory and context management capabilities, implementing **Batch 1, 2, and 2a** specifications.

1.  **`models/` module:** Implement the Pydantic data models.
    -   `graph.py`: `ProvenanceMetadata`, `GraphNode`, `GraphEdge`.
    -   `session.py`: `SessionState`, `ConsolidationReport`.
    -   `payload.py`: `ContextPayload`.
2.  **`adapters/` module:** Implement the concrete storage adapters that adhere to the `friday-core` interfaces.
    -   `graph.py`: `ElementXGraphStore` (using NetworkX).
    -   `vector.py`: `ChromaVectorStore` (using ChromaDB).
    -   `episodic.py`: A simple JSON or in-memory implementation of `EpisodicStoreAdapter`.
3.  **`ingestion/pipeline.py`:** Implement the `DocumentIngestionPipeline` for file parsing and chunking.
4.  **`controller/memory_controller.py`:** Implement the `MemoryController`, which acts as a facade over the adapters.
5.  **`context/` module:** Implement the context engineering components.
    -   `assembler.py`: `ContextAssembler` with token budgeting logic.
    -   `extractor.py`: `MemoryExtractor`.
    -   `consolidator.py`: `MemoryConsolidator`.
    -   `layout.py`: `PromptArchitect`.

### Phase 3: `packages/friday-optimization` (Performance)

With the core memory system in place, this phase focuses on LLM-specific optimizations.

1.  **`signatures/` module:** Define dspy-like signatures for tasks such as summarization and query generation.
2.  **`compilers/` module:** Implement logic to optimize prompts or component chains (e.g., `optimize_context`).

### Phase 4: `apps/friday-cli` (The Application)

The final phase builds the user-facing application that integrates all the framework packages.

1.  **`main.py`:** The main entry point for the CLI application, responsible for initializing settings, the memory controller, and the context engine.
2.  **`container.py`:** A dependency injection container to manage and assemble the framework components.
3.  **`repl.py`:** The Read-Eval-Print Loop for interactive chat.
4.  **`server/api.py`:** A FastAPI server to potentially expose the agent's capabilities over an API.

## 3. Testing Strategy

The testing strategy follows the "pyramid" model defined in the Batch 0 specification.

### `friday-core`
- **Strategy:** Primarily **Unit Tests**.
- **Details:**
    - Test `FridayBaseSettings` loading from environment variables and `.env` files.
    - Verify that custom exceptions can be raised and caught correctly.
    - Test the `DebugTelemetryRecorder` to ensure it captures events and spans as expected.
    - Since the `interfaces` contain only protocols, they won't have dedicated tests, but they serve as the contract for integration tests in other packages.

### `friday-memory`
- **Strategy:** A mix of **Unit Tests** and **Integration Tests**.
- **Unit Tests:**
    - Test `MemoryController` logic with mocked adapter dependencies. Verify that `recall()` calls the correct methods on the mock adapters.
    - Test `ContextAssembler`'s budgeting logic by providing it with oversized mock data and asserting that it prunes content according to the priority hierarchy.
    - Test Pydantic `models` for validation errors (e.g., creating a `GraphNode` without `provenance`).
- **Integration Tests:**
    - Test `ElementXGraphStore` by having it write to and read from a temporary `.gpickle` file on disk.
    - Test `ChromaVectorStore` against a non-persistent, in-memory ChromaDB instance (`chromadb.EphemeralClient`).
    - Test the full "consolidation loop": `add_turn` -> `fetch_unconsolidated_events` -> `mark_events_consolidated`.

### Ancillary Components for Testing

To support the testing strategy, the following components will be necessary:

1.  **Test Runner:** `pytest` will be the primary test runner, along with `pytest-asyncio` for testing async code.
2.  **Mocking Library:** `unittest.mock` (part of the standard library) for creating mock objects in unit tests.
3.  **Shared Fixtures (`conftest.py`):**
    - A project-wide `tests/lab/conftest.py` can define fixtures available to all test suites.
    - **Example Fixtures:**
        - A `settings()` fixture that provides a clean `FridayBaseSettings` instance for tests.
        - A `telemetry_recorder()` fixture that yields an instance of `DebugTelemetryRecorder`.
        - An `ephemeral_chroma_client()` fixture that sets up and tears down an ephemeral ChromaDB client.
4.  **Test Datasets:** A `tests/lab/datasets` directory can hold sample text files, documents, or logs to be used during ingestion pipeline testing.
