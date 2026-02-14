# Friday Agent Framework: Comprehensive Design & Gap Analysis

**Date:** February 10, 2026
**Status:** Definitive Design Document
**Scope:** `packages/friday-agent` and its integration with the broader Friday ecosystem.

---

## 1. Executive Summary

The Friday Agent Framework constitutes the "Body" and "Nervous System" of the Friday AI architecture. It executes tasks by leveraging the "Mind" (Memory System) and is designed around the core philosophy of **"One Mind, Many Bodies."**

In this architecture, specialized agents (e.g., Researcher, Coder) operate as distinct entities within a shared semantic environment. To prevent chaos, their collaboration is strictly governed: an **Orchestrator** manages the flow of work, an **Arbitrator** manages the flow of truth, and a **Friday Kernel** provides the stable execution environment.

This document serves as the authoritative architectural blueprint, validating the current codebase against the "Project Hive" vision and defining the roadmap to a robust, production-ready system.

### Core Philosophy
1.  **Protocol-First:** Agents are defined by typed contracts (Input/Output/Tools/Artifacts), not just natural language prompts.
2.  **Governed Collaboration:** Multi-agent interaction is mediated to prevent race conditions, semantic conflicts, and hallucination loops.
3.  **Separation of Powers:**
    *   **Orchestration:** Management of *Action* (Task routing, Workflow execution).
    *   **Arbitration:** Management of *Truth* (Fact validation, Memory promotion).
4.  **Artifact-Centric:** Output is structured. Agents produce "Artifacts" (Code, Docs, Data) managed by a central Workspace, not just chat streams.
5.  **Headless Kernel:** The intelligence engine is decoupled from the user interface (CLI/API), enabling portable deployment.
6.  **Continuous Validation:** A dedicated testing harness evolves alongside the framework to ensure multi-agent stability.
7.  **Ecosystem Integration (No Reinventing the Wheel):** The framework MUST utilize the existing Friday supportive packages. This is a hard constraint. All agent activities, memory operations, and LLM interactions must leverage:
    *   `friday-core`: Shared protocols, security, and utilities.
    *   `friday-memory`: Semantic, episodic, and associative storage.
    *   `friday-llm`: Standardized model interface and cost tracking.
    *   `friday-telemetry`: Unified tracing and observability.
    *   `friday-tools`: Protocol-driven tool ecosystem.
    *   `friday-transcript`: Standardized session recording.

---

## 2. Architectural Pillars

### 2.1 The Agent Core (`AgentBase`)
The `AgentBase` serves as the fundamental abstraction for all "Bodies" within the Hive. It is not merely a wrapper around an LLM client, but a stateful runtime entity that encapsulates a specific Persona (Role, Goal, Voice) and its capabilities. It manages the immediate execution loop—perceiving input, selecting tools via an autonomy strategy (`manual`, `auto`, or `hybrid`), executing those tools, and synthesizing a response.

Crucially, the Agent Core isolates the business logic of an agent from the underlying infrastructure. It handles the "dirty work" of session state management, sanitizing tool outputs, and emitting structured telemetry for every thought and action. This abstraction allows us to swap underlying LLM providers or update memory adapters without rewriting the agent's logic, ensuring that specialized agents like the "Researcher" or "Coder" remain stable even as the infrastructure evolves.

> **Current State:** `AgentBase` and `CopilotAgent` already exist in `packages/friday-agent/src/friday_agent/`. `AgentBase` implements a Re-Act loop (max 10 iterations), tool autonomy modes (`manual`/`auto`/`hybrid`), session management via `initialize_session()`, and tool lifecycle methods (`set_tools_for_task()`, `expand_tools()`, `clear_tools()`). `CopilotAgent` extends this with context assembly and memory archival. This design evolves these existing classes, not creating them from scratch.

### 2.2 The Registry (`AgentRegistry`)
The Registry acts as the system's "Talent Pool" and "Class Loader," responsible for the discovery, configuration, and instantiation of agents. It decouples the *definition* of an agent (typically a lightweight YAML manifest describing roles and required capabilities) from its *instantiation* (the creation of heavy Python objects with dependency injection). This allows the system to remain lightweight, loading only the agents required for the current task.

Beyond simple lookup by name, the Registry provides a Capability Index (e.g., "Find all agents capable of `web-browsing`"). This enables dynamic team formation, where the Orchestrator can request resources based on the nature of the problem rather than hardcoded agent names. It utilizes a Factory Pattern to inject runtime dependencies (LLM, Memory, Tools) into the agent at the moment of creation, ensuring that every agent is born connected to the correct session context.

> **Current State:** `AgentRegistry` already exists in `packages/friday-agent/src/friday_agent/registry.py` with capability lookup (`find_by_capability()`), factory pattern (`set_factory()`/`create_agent()`), profile registration (`register_profile()`), and YAML manifest loading via `AgentLoader` (`load_manifests()`). This design extends the existing registry with enhanced discovery and team formation capabilities.

### 2.3 The Orchestrator (`AgentOrchestrator`)
The Orchestrator functions as the "Nervous System" of the framework, managing the flow of control and data between agents. It is responsible for Task Routing—determining whether a user's request should be handled by the current active agent, routed to a specialist (e.g., `@researcher`), or delegated to a sub-routine. It enforces the "Laws of Physics" for the session, guaranteeing that all agents in a delegation chain share the same `session_id`, `user_context`, and security boundaries.

In advanced scenarios, the Orchestrator acts as the Workflow Engine, executing directed acyclic graphs (DAGs) of tasks. It manages the lifecycle of these workflows, handling state persistence, error recovery (retries), and human-in-the-loop suspension points. By centralizing control flow, the Orchestrator prevents "Agent Loops" (where two agents endlessly delegation to each other) and ensures that the system always converges toward a resolution.

> **Current State:** `AgentOrchestrator` already exists in `packages/friday-agent/src/friday_agent/orchestrator.py` with `@name` routing via regex pattern (`ROUTING_PATTERN = re.compile(r"^@(\w+)\s+(.+)$")`), agent delegation (`delegate()`), and agent caching. The current `process()` method handles routing internally. Semantic routing (intent-based rather than explicit `@name` mentions) is a Phase 2+ enhancement.

### 2.4 The Arbitrator (`ArbitratorAgent`)
The Arbitrator is the "Conscience" of the Hive, a specialized System Agent responsible for Truth Maintenance. In a multi-agent system, allowing every agent to write directly to the Global Shared Memory creates race conditions and "Truth Pollution" (where low-confidence hallucinations override high-confidence facts). The Arbitrator implements a **Gateway Pattern**: agents write to their own private namespaces (`researcher-uuid:/`), and only the Arbitrator has write access to the `shared:/` namespace.

This component validates "Memory Proposals" submitted by agents against existing ground truth and confidence thresholds. If a conflict is detected (e.g., Agent A says "X is True" and Agent B says "X is False"), the Arbitrator escalates the decision to a human or triggers a resolution protocol. This ensures that the Shared Memory remains a trusted source of truth, curated and consistent, rather than a dumping ground for raw agent outputs.

### 2.5 The Workspace (`ArtifactManager`)
The Workspace is the "Shared Table" where agents exchange tangible outputs, or "Artifacts," such as code files, datasets, and documents. Because passing massive blobs of text through an LLM's context window is inefficient and expensive, the Workspace manages these objects via **Smart References** (e.g., `workspace://session_123/file_abc`).

When an agent needs to use an artifact created by another, the Workspace intelligently resolves the reference—injecting a summary, a specific snippet, or the full content based on the recipient's context window limits. It also handles the physical storage lifecycle (ephemeral memory vs. durable S3/Disk storage) and access control, ensuring that sensitive artifacts are not leaked to unauthorized agents.

### 2.6 The Friday Kernel (`SystemRuntime`)
The Friday Kernel is the "Operating System" that hosts the entire Hive. Currently, much of the system's wiring is tightly coupled to the CLI (`friday-cli`), which prevents the framework from being embedded in other applications (like a REST API or a Desktop GUI). The Kernel formalizes this wiring into a standalone `friday-runtime` package.

It serves as the centralized Dependency Injection container, initializing singleton services (Memory, Workspace, Telemetry) and providing a stable Execution Facade (`Kernel.process()`). It manages the global event bus, streaming structured events (Tokens, Status Updates, Artifacts) to any connected client. This separation ensures that the Friday Agent Framework is portable, testable, and capable of running "Headless."

### 2.7 The Friday Lab (Testing Harness)
The Friday Lab is a first-class component designed to be the "Gymnasium" for the Hive. It is an evolving Integration Testing Harness that allows developers to stress-test multi-agent dynamics in a controlled environment. Unlike standard unit tests, the Lab is designed to simulate complex interaction patterns, such as "Conflict Injection" (feeding opposing facts to the Arbitrator to test resolution) or "Latency Simulation."

The Lab grows with the framework: starting as a harness for Headless Kernel verification, evolving to simulate "Hive Minds" for the Arbitrator, and finally testing complex Artifact pipelines. It provides the "Definition of Done" for every phase, offering a reproducible environment where race conditions, resource leaks, and logic loops can be identified and fixed before deployment.

---

## 3. Current Codebase State

The following inventory documents what already exists in the codebase. References in this design document build on these foundations — new components are extensions or extractions, not greenfield implementations.

| Package / Location | Key Components | Notes |
| :--- | :--- | :--- |
| `packages/friday-agent/` | `AgentBase`, `CopilotAgent`, `AgentProfile`, `AgentRegistry`, `AgentOrchestrator`, `WorkflowEngine`, `DefaultToolRegistry`, `AgentLoader` | Core agent infrastructure. Re-Act loop, tool autonomy, YAML manifest loading, `@name` routing, DAG workflow execution all exist. |
| `packages/friday-cli/` | `FridayContainer`, `FridayConfig`, `MemoryProfile`, `CommandRegistry`, display components | DI container with lazy property accessors (`.llm`, `.memory`, `.context_engine`, `.tool_registry`, `.orchestrator`). `MemoryProfile` enum (FULL, EPHEMERAL, VECTOR_ONLY, TESTING). |
| `packages/friday-telemetry/` | Telemetry interfaces, providers, models | Unified tracing and observability layer. |
| `packages/friday-core/interfaces/` | `LLMClient`, `ToolRegistry`, `ToolDefinition`, `EpisodicStoreAdapter`, `VectorStoreAdapter`, `GraphStoreAdapter`, `ContextEngineeringInterface` | Protocol-first contracts that all packages depend on. |
| `tests/lab/` | `conftest.py`, `dashboard/`, `experiments/` | Existing lab scaffold — provides the foundation for the Friday Lab harness described in Section 2.7. |
| `tests/integration/memory/friday.py` | Monolithic integration app (~7500 lines) | **Does NOT use `FridayContainer`.** Performs its own manual DI. Migrating this to `RuntimeKernel` is a separate effort outside Phase 1 scope. |

---

## 4. Detailed Component Specifications

*(Refer to `technical-specifications.md` for Interface, Schema, and State Machine details.)*

---

## 5. Gap Analysis

| Component | Priority | Status | Gap Description |
| :--- | :--- | :--- | :--- |
| **Friday Kernel** | **Critical** | Exists, Needs Extraction | DI logic exists in `friday-cli/container.py` (`FridayContainer`) with lazy property accessors. Needs extraction to `friday-runtime` as `RuntimeKernel` to decouple from CLI. |
| **Arbitrator** | **Critical** | Missing | No enforcement of Shared Memory integrity. |
| **Friday Lab** | **Critical** | Scaffold Exists | Lab scaffold exists in `tests/lab/` (`conftest.py`, `dashboard/`, `experiments/`). Needs build-out into a full multi-agent testing harness. |
| **Workspace** | **High** | Missing | No standard way to handle files/code. |
| **Workflow Engine** | **High** | Exists, Needs Refactor | `WorkflowDefinition` contains `TaskNode` objects with mutable runtime fields (`status`, `result`, `error`, `retry_count`, `started_at`, `completed_at`). `WorkflowExecution` exists as separate state, but task-level runtime state leaks into the definition. `TaskNode.reset()` method enables mutation. Needs separation of definition from execution state. |
| **Namespace Logic** | **High** | Missing | No enforcement of `agent-uuid:/` scopes. |
| **friday.py Integration** | **Medium** | Known Gap | The main production app (`tests/integration/memory/friday.py`, ~7500 lines) performs its own manual DI, not via `FridayContainer`. Migrating it to use `RuntimeKernel` is a separate effort outside Phase 1 scope. |

---

## 6. Implementation Roadmap

### Phase 1: Stabilization & Extraction (The Foundation)
*Goal: Decouple the Brain from the Body (CLI).*

1.  **Extract Kernel:** Create `packages/friday-runtime`.
2.  **Fix Workflows:** Refactor for immutability.
3.  **Initiate Friday Lab:** Build the base harness for Headless Kernel verification and Session stability.

#### Definition of Done (Exit Criteria)
*   **Headless Execution:** Kernel runs "Hello World" without CLI dependencies.
*   **Harness Base:** The Lab can execute a 2-agent delegation chain and verify session consistency.

### Phase 2: The Conscience (Arbitration)
1.  **Implement Namespaces:** Enforce `agent_name-uuid:/` scopes.
2.  **Build Arbitrator:** Implement Proposal Protocol and Truth Promotion.
3.  **Evolve Friday Lab:** Add **Conflict Injection** capabilities to test Arbitration thresholds.

#### Definition of Done (Exit Criteria)
*   **Conflict Resolution:** The Lab successfully injects a collision and asserts that the Arbitrator escalates to Human Review.

### Phase 3: The Artifact & Workspace Upgrade
1.  **Build Workspace:** Implement `ArtifactManager`.
2.  **Define Protocol:** Implement `FridayArtifact` schema.
3.  **Evolve Friday Lab:** Add **Artifact Tracing** to verify data passing between tools and agents.

#### Definition of Done (Exit Criteria)
*   **Round-Trip Validation:** The Lab verifies a complete data pipeline (Agent A -> Artifact -> Agent B) with 100% data integrity.
