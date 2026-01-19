# Friday Framework Context

This document provides a comprehensive overview of the "Friday Framework" project, intended to be used as instructional context for Gemini.

## Project Overview

The "Friday Framework" is a Python-based agentic framework designed to provide a modular and extensible architecture for building AI agents. It distinguishes itself by separating the agent's "Mind" (intelligence/memory) from its "Body" (execution/tools), allowing for sophisticated context management and long-term learning.

### Architecture: Mind & Body

The architecture revolves around a central "Memory Loop":

1.  **The Mind (Intelligence Layer):**
    *   **Memory Controller:** The central "brain" that decides how to store information (structured vs. unstructured) and retrieves relevant context.
    *   **Context Engine:** Assembles the necessary context for the LLM and extracts new knowledge from interactions.
    *   **Data Layer:** Manages persistence via:
        *   **GraphDB (ElementX):** For structured facts and relationships (using Pydantic models).
        *   **Vector Store:** For unstructured semantic search (e.g., via ChromaDB).
        *   **IO Adapters:** Abstract protocols ensuring storage technologies can be swapped.

2.  **The Body (Execution Layer):**
    *   **Agent Base Class (`AgentBase`):** The orchestrator that implements the `Observe -> Think -> Act -> Reflect` loop.
    *   **Tool Registry:** Manages tools (Python functions) and resolves their schemas for the LLM.
    *   **LLM Interface:** Abstracts interactions with Large Language Models (using LiteLLM).
    *   **Telemetery:** Instrumentation for tracing and observability.

### Core Concepts

*   **Auto-Memorize:** The framework automatically classifies input as "Facts" (GraphDB) or "Documents" (Vector Store) without manual intervention.
*   **Hebbian Learning:** Knowledge retrieval is reinforced; frequently accessed graph nodes gain a higher "hit count," increasing their retrieval priority.
*   **Swappability:** Components like storage backends and LLM providers are hidden behind abstract base classes (Protocols), making them easily replaceable.

## Project Structure (Monorepo)

The project is a monorepo managed by `uv`.

*   `packages/`
    *   `friday-core`: Shared utilities, logging, and base interfaces.
    *   `friday-memory`: The "Mind" - Memory controller, ingestion, adapters, and graph/vector logic.
    *   `friday-agent`: The "Body" - Agent base classes, copilot implementation, and tool orchestration.
    *   `friday-llm`: LLM service wrappers and configuration.
    *   `friday-tools`: Standard tool definitions.
    *   `friday-sandbox`: Secure execution environment for agent code.
    *   `friday-mcp`: Model Context Protocol implementation.
    *   `friday-transcript`: Transcript management.
*   `docs/`: Extensive architectural documentation and specifications.
*   `apps/`: Application-level implementations (e.g., `friday-cli`).

## Development & Usage

### Prerequisites
*   Python 3.10+
*   `uv` (Universal Python Package Manager)

### Build and Run
This project uses `uv` workspaces. You do not need to install packages individually.

**1. Install Dependencies:**
```bash
uv sync
```

**2. Run Tests:**
```bash
uv run pytest
```
*   To run specific tests: `uv run pytest packages/friday-memory/tests`

**3. Run Examples:**
Scripts in the `examples` directories demonstrate usage.
```bash
uv run python packages/friday-core/examples/01_introductory.py
```

### Key Commands (Inferred)

*   **Linting:** `uv run ruff check .`
*   **Formatting:** `uv run ruff format .`
*   **Type Checking:** `uv run mypy .`

## Conventions

*   **Strong Typing:** Heavy use of **Pydantic** models to enforce data schemas, especially for GraphDB nodes/edges and Tool definitions.
*   **Interfaces:** Reliance on Abstract Base Classes (ABCs) in `friday-core` to define component contracts.
*   **Async First:** The agent and IO operations are designed to be asynchronous (`async`/`await`).
*   **Dependency Injection:** Components are typically passed into constructors (e.g., passing `MemoryController` into `AgentBase`), enabling easy testing and modularity.
