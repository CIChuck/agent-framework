# Friday Framework Context

This document provides a comprehensive overview of the "Friday Framework" project, intended to be used as instructional context for Gemini.

## Project Overview

The "Friday Framework" is a production-ready Python-based agentic framework designed to provide a modular and extensible architecture for building AI agents. It distinguishes itself by separating the agent's "Mind" (intelligence/memory) from its "Body" (execution/tools), allowing for sophisticated context management, long-term learning, and genuine multi-agent collaboration.

### Architecture: Mind & Body

The architecture revolves around a central "Memory Loop":

1.  **The Mind (Intelligence Plane):**
    *   **Memory Controller:** The central "brain" that decides how to store information (structured vs. unstructured) and retrieves relevant context.
    *   **Context Engine:** Assembles the necessary context for the LLM using knapsack optimization algorithms.
    *   **Data Layer:** Manages persistence via:
        *   **GraphDB (ElementX/NetworkX):** For structured facts and relationships (using Pydantic models).
        *   **Vector Store (ChromaDB):** For unstructured semantic search.
        *   **Episodic Store (SQLite):** For raw chronological records (transcripts).

2.  **The Body (Control Plane):**
    *   **Agent Base Class (`AgentBase`):** The orchestrator that implements the `Observe -> Think -> Act -> Reflect` loop.
    *   **Tool Registry:** Manages tools (Python functions) and resolves their schemas for the LLM.
    *   **LLM Interface:** Abstracts interactions with Large Language Models (using LiteLLM).
    *   **Telemetery:** Instrumentation for tracing and observability.

### Core Concepts

*   **Protocol-First Design:** Heavy reliance on Abstract Base Classes (Protocols) to define component contracts, ensuring swappability (e.g., swapping ChromaDB for Pinecone without code changes).
*   **Three-Tier Memory:**
    1.  **Episodic:** Raw history.
    2.  **Semantic:** Searchable insights.
    3.  **Associative:** Knowledge graph of entities and relationships.
*   **Hebbian Learning:** Knowledge retrieval is reinforced; frequently accessed graph nodes gain a higher "hit count," increasing their retrieval priority.
*   **Auto-Memorize:** The framework automatically classifies input as "Facts" or "Documents" without manual intervention.

## Project Structure (Monorepo)

The project is a monorepo managed by `uv`.

*   `packages/`
    *   `friday-core`: Shared utilities, logging, configuration, and base interfaces (Protocols).
    *   `friday-memory`: The "Mind" - Memory controller, ingestion, adapters, and graph/vector logic.
    *   `friday-agent`: The "Body" - Agent base classes, copilot implementation, and tool orchestration.
    *   `friday-llm`: LLM service wrappers (LiteLLM) and configuration.
    *   `friday-tools`: Standard tool definitions (Filesystem, Web, Git, etc.).
    *   `friday-sandbox`: Secure execution environment for agent code.
    *   `friday-mcp`: Model Context Protocol implementation.
    *   `friday-transcript`: Transcript management and export.
    *   `friday-optimization`: Algorithms for token budgeting (knapsack).
    *   `friday-cli`: CLI interface components.
*   `apps/`
    *   `friday-copilot`: The main CLI application implementing a full-featured AI assistant.
*   `docs/`: Extensive architectural documentation and specifications.

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

**3. Run The Copilot App:**
```bash
uv run friday-copilot
```
*   Config location: `~/.config/friday/config.yaml` (Linux), `~/Library/Application Support/friday/config.yaml` (macOS).

**4. Key Commands:**
*   **Linting:** `uv run ruff check .`
*   **Formatting:** `uv run ruff format .`
*   **Type Checking:** `uv run mypy .`

## Conventions

*   **Strong Typing:** Heavy use of **Pydantic** models to enforce data schemas, especially for GraphDB nodes/edges and Tool definitions.
*   **Interfaces:** Reliance on `typing.Protocol` in `friday-core` to define component contracts.
*   **Async First:** The agent and IO operations are designed to be asynchronous (`async`/`await`).
*   **Dependency Injection:** Components are passed into constructors (e.g., passing `MemoryController` into `AgentBase`), enabling easy testing and modularity.
*   **Monorepo Management:** Always use `uv` for dependency management. Do not use `pip` directly unless testing `pip` compatibility.
