# Gemini Framework Context

This document provides a comprehensive overview of the "Friday Framework" project, intended to be used as instructional context for Gemini.

## Project Overview

The "Friday Framework" is a Python-based agentic framework designed to provide a modular and extensible architecture for building AI agents. The framework is in the early stages of development, with a focus on defining the core components and their interactions.

The architecture is designed around the concept of a "Mind" (intelligence layer) and a "Body" (execution layer), with a central "Memory Loop" for context retrieval, learning, and decision-making.

### Key Architectural Components:

*   **Data Layer:** Handles data ingestion, storage, and retrieval.
    *   **IO Adapter Protocols:** Abstract interfaces for input/output, ensuring swappability.
    *   **GraphDB Wrapper (ElementX):** Manages structured knowledge and relationships.
    *   **Vector/Data Store Adapters:** For semantic search and unstructured data, using technologies like ChromaDB.
    *   **Document Ingestion Pipeline:** A robust system for parsing, chunking, and embedding files.
*   **Intelligence Layer:** The "Brain" of the agent.
    *   **Memory Controller Logic:** Routes information between the data layer and the context engine, and decides what to memorize.
    *   **Context Engineering Framework:** Gathers and structures the context necessary for the LLM to make decisions.
*   **Execution Layer:** The "Body" and "Voice" of the agent.
    *   **LLM Framework (LiteLLM):** Manages interactions with Large Language Models.
    *   **Tooling Interface (Pydantic):** A system for defining and using tools.
    *   **Agent Base Class:** The main orchestrator that runs the "Observe -> Think -> Act -> Reflect" loop.
*   **Supporting Components:**
    *   **Telemetry Adapter (OpenTelemetry):** For observability and tracing.
    *   **Guardrails Framework:** For input/output validation and safety.
    *   **Event Bus:** For asynchronous operations.

### Core Concepts:

*   **Auto-Memorize:** The framework automatically decides whether to store new information as a structured fact (in the graph database) or as an unstructured document (in the vector store).
*   **Hebbian Learning:** The system reinforces frequently accessed knowledge by increasing a `hit_count` on graph nodes, making that knowledge "stronger" and more likely to be retrieved in the future.

## Building and Running

The project is currently in the specification and initial development phase. There are no explicit build or run commands defined yet. The `pyproject.toml` file is minimal and does not yet list the full dependencies.

To run the project, you would typically execute the main Python file:

```bash
python main.py
```

However, given the current state of `main.py`, this will only print a "Hello World" message.

### TODO: Define Build and Run Commands

*   [ ] Define the project dependencies in `pyproject.toml`.
*   [ ] Create a `Makefile` or add scripts to `pyproject.toml` for common tasks like installing dependencies, running tests, and starting the application.

## Development Conventions

While not explicitly stated, the documentation suggests a strong emphasis on the following principles:

*   **Modularity and Swappability:** Components are designed to be independent and replaceable, facilitated by the use of Abstract Base Classes (ABCs) as protocols.
*   **Strong Typing:** Pydantic is used to enforce data schemas, particularly in the GraphDB, to maintain data integrity.
*   **Dependency-Driven Development:** The project follows a clear roadmap where components are built in a logical order based on their dependencies.
*   **Observability:** Telemetry and tracing are considered a core part of the architecture, to be integrated from the early stages.
