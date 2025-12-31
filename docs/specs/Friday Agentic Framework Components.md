# **Friday Agentic Framework Components**

This document defines the comprehensive architecture for the Friday application. It includes the core Agent abstractions (Blue), the supporting Frameworks (Red), and the technological Infrastructure (Orange), along with the newly added Governance and Observability layers.

## **Component Definitions**

| Component Group | Component Name | Classification | Proposed Tech Stack | Core Responsibilities & Architecture |
| :---- | :---- | :---- | :---- | :---- |
| **Agent Core** | **Agent** | Blue (Abstraction) | Python Base Class (AgentBase) | The central orchestrator. Holds references to Memory, Tools, and LLM. Manages the lifecycle of an interaction loop. |
|  | **Copilot** | Blue (Abstraction) | Python Subclass | Specialized "human-in-the-loop" agent. Halts for user verification after key steps. |
|  | **Semi-Autonomous** | Blue (Abstraction) | Python Subclass | Agents authorized for short chains of tasks (3-5 steps) but require authorization for high-stakes actions. |
|  | **Autonomous** | Blue (Abstraction) | Python Subclass | Independent agents running event loops or schedules without direct user intervention. |
|  | **Multi-Turn Session** | Blue (Abstraction) | Session Object / State Machine | Tracks immediate conversation state (conversation\_id). Separates the "thread" from long-term memory. |
| **Capability** | **Tools** | Blue (Abstraction) | **Pydantic** Models | Interface for external capabilities. Defines schema for LLM understanding and execute() method. |
|  | **Tasks** | Blue (Abstraction) | Python Class / Task Queue Item | Discrete unit of work. For Copilots, it's the user prompt. For Autonomous, it's a structured objective. |
|  | **Event Bus** | **Orange (Comp)** | **Internal asyncio Queue / Redis** | **Sits between Agents and Tasks.** Manages async handoffs, allowing agents to react to events (e.g., "FileUploaded") rather than synchronous calls. |
| **Intelligence** | **LLM Framework** | Red (Framework) | **litellm** | Unified gateway for inference. Abstracts provider differences (OpenAI/Anthropic), retries, and rate limits. |
|  | **LLM** | Blue (Abstraction) | Configuration Object | Model profile (e.g., "gpt-4o-coding"). Allows agents to hot-swap "brains" depending on task difficulty. |
|  | **Guardrails** | **Red (Framework)** | **Wrapper / Nemo Guardrails** | **Wraps the LLM Framework.** Acts as a firewall, sanitizing inputs/outputs (PII, topic safety, dangerous commands) *before* execution. |
| **Context & Memory** | **Context Eng. Framework** | Red (Framework) | Custom Python Logic | **The Brain.** Intercepts the Session, queries Memory/Graph, and constructs the final System Prompt \+ Context. |
|  | **Context** | Blue (Abstraction) | Data Object (DTO) | The actual payload sent to the LLM (the assembled state of the window). |
|  | **Memory** | Blue (Abstraction) | Memory Controller Class | The IO Router. Decides if data goes to Short Term (RAM), Graph (Relationships), or Vector (Semantic). |
|  | **Episodic** | Blue (Type) | Chronological Log (JSON/SQL) | Sequential history ("User said X"). Essential for debugging and recall. |
|  | **Short Term** | Blue (Type) | In-Memory / Redis | "Scratchpad" variables for the active task only. Wiped after session. |
|  | **Long Term** | Blue (Type) | **Chroma** \+ **GraphDB** | Persistent knowledge base. Facts and code patterns that survive across sessions. |
| **Infrastructure** | **IO Adapter Layer** | **Red (Framework)** | **Python Protocol / ABCs** | **The "Swappability" Layer.** Defines strict interfaces (e.g., VectorStoreInterface). Allows swapping DBs without rewriting Agent code. |
|  | **GraphDB** | Orange (Comp) | **ElementX** / NetworkX (wrapped) | Stores relationships. Wrapped by IO Adapter to provide persistence and specific traversal logic. |
|  | **Vector Store** | Orange (Comp) | **Chroma DB** | Stores semantic embeddings. Accessed *only* via the IO Adapter. |
|  | **Data Store** | Orange (Comp) | **Convex** (or SQL) | Source of Truth for structured data (User Profiles, Configs). Accessed via IO Adapter. |
|  | **Embedding Model** | Orange (Comp) | sentence-transformers / OpenAI | The model used to turn text into vectors for the *Vector Store*. |
|  | **Telemetry** | **Red (Framework)** | **OpenTelemetry Wrapper** | **Permeates every block.** Wraps abstractions to emit traces (Start/End times, Inputs/Outputs) for debugging and cost tracking. |

