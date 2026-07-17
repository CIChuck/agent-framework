# Friday API - Product Requirement Document (PRD)

**Status:** Planning & Architectural Design
**Date:** January 27, 2026
**Target Phase:** Phase 1 (Memory & Chat Exposure)

## 1. Executive Summary

The **Friday API** is a RESTful interface designed to expose the advanced agentic capabilities of the Friday Framework to external applications, web frontends, and third-party integrations.

Currently, the Friday Framework's rich features—specifically its "Infinite Memory" architecture (Episodic, Semantic, and Associative memory) and Context Engineering—are accessible primarily through CLI tools. The Friday API aims to bridge this gap by providing a secure, session-oriented, and cloud-ready interface.

**Phase 1** focuses on parity with the capabilities demonstrated in `memory-chat-v2.py`. This includes persistent session management, authenticated chat interactions, and deep introspection into the agent's memory stores (History, Vector Facts, Graph Entities).

## 2. Technical Architecture

### 2.1 Technology Stack
- **Language:** Python 3.10+
- **Web Framework:** FastAPI (High performance, easy async support, auto-generated OpenAPI docs)
- **Server:** Uvicorn (ASGI) behind Nginx (Reverse Proxy/Load Balancer)
- **Containerization:** Docker & Docker Compose
- **Package Location:** `packages/friday-api`
- **Source of Truth:** Leverages existing logic in `friday-memory`, `friday-core`, and `friday-agent`.

### 2.2 Cloud-Enabled Persistence
To move from a local CLI to a cloud-ready service, the architecture must support robust persistence and multi-tenancy:

- **Session State:** Session metadata and state must be persisted in a relational database.
  - **Dev/Local:** SQLite (optional).
  - **Docker/Prod:** PostgreSQL.
- **Memory Backends:**
  - **Vector Store:** Support for client-server vector databases (e.g., ChromaDB HTTP client).
  - **Graph Store:** Abstraction over graph storage (e.g., ElementX persisting to DB).
  - **Transcripts:** Structured storage of interaction history (PostgreSQL/SQLAlchemy).

### 2.3 Database Exploration (Graph-Vector Options)
To address the limitations of the current in-memory NetworkX architecture (latency, scalability, and multi-tenancy), we will explore purpose-built open-source Graph-Vector databases. These unified engines could potentially replace separate Graph (ElementX) and Vector (Chroma) backends, simplifying the architecture and improving RAG performance.

**Candidates for Evaluation:**
- **HelixDB:** Rust-based, purpose-built graph-vector database designed for low-latency RAG.
- **CozoDB:** Transactional relational-graph-vector DB using Datalog for queries.
- **Weaviate:** AI-native vector DB with strong graph-like schema linking and semantic search.
- **Memgraph:** In-memory graph DB with added vector support (hybrid search).
- **Neo4j (Community):** Mature graph DB now supporting vector search capabilities.
- **Dgraph:** Distributed, native graph database with GraphQL support.
- **JanusGraph:** Scalable, distributed graph database (Apache 2 license).

### 2.3.1 Memgraph Migration Path (Unified Backend)
Based on initial analysis, **Memgraph** appears to be a strong candidate for unifying the Graph and Vector stores.

**1. Data Modeling Strategy**
-   **Unified Schema:** Instead of maintaining separate stores (`ElementX` for relationships, `Chroma` for embeddings), entities and documents will exist as Nodes in Memgraph.
-   **Vector Properties:** Embedding vectors (e.g., 1536-dim floats) will be stored directly as properties on nodes (e.g., `:Fact`, `:Document`).
-   **Indexing:** Use Memgraph's `CREATE VECTOR INDEX` to enable approximate nearest neighbor (ANN) search on these properties.

**2. Query & Access**
-   **Client:** Use `gqlalchemy` (Python OGM) for object mapping, dropping down to raw Cypher for vector operations (`CALL VECTOR_SEARCH`).
-   **Hybrid Search:** Perform vector similarity search (`CALL VECTOR_SEARCH`) and filter results using graph traversals (Cypher `MATCH`) in a single query.

**3. Multi-Tenancy (Community Edition)**
-   *Constraint:* Native multi-database isolation is an Enterprise-only feature.
-   *Solution:* **Label/Property Partitioning**.
    -   Every node must carry a `tenant_id` property.
    -   Row-Level Security (RLS) must be enforced at the API application layer (e.g., middleware that injects `{tenant_id: current_user}` into every Cypher `MATCH` clause).

### 2.3.2 HelixDB Evaluation (Rust-Native Option)
**Overview:** HelixDB is a high-performance, Rust-based engine that natively unifies Graph and Vector data. It distinguishes itself with `HelixQL`, a type-safe query language, and built-in embedding generation.

**Key Findings:**
-   **License:** AGPL-3.0 (Open Source, Copyleft).
-   **Unified Engine:** Eliminates the need for separate Vector/Graph stores. Uses LMDB for ultra-low latency.
-   **AI-Native:** Can vectorize text directly upon ingestion, simplifying the "Think" loop pipeline.
-   **Python Support:** `helix-py` SDK offers a PyTorch-like API for defining graph/vector operations, which may be more intuitive for ML-focused developers than SQL/Cypher.
-   **Transcript Storage:** While not a relational DB, transcripts could be modeled as a time-series graph (Linked List of Turns), allowing for semantic search over conversation history ("Find the turn where I mentioned 'Project X'").

**Assessment:** HelixDB is a strong contender for high-performance, low-latency deployments. However, its AGPL license and unique `HelixQL` DSL present a steeper learning curve compared to Memgraph's standard Cypher support. It will be evaluated alongside Memgraph in Phase 2.

### 2.4 Security
- **Authentication:** Mandatory for all endpoints.
  - **Mechanism:** API Key or OAuth2 (Bearer Token).
  - **User Isolation:** All memory retrieval and session operations must be strictly scoped to the authenticated `user_id`.

## 3. Core Features (Phase 1)

### 3.1 Session Management
The API is fundamentally session-oriented. A user must establish or resume a session to interact with the agent.

- **Create Session:** Initialize a new chat session with a specific configuration (system prompt, agent persona).
- **List Sessions:** Retrieve a list of past sessions for the authenticated user (supporting "Resume" functionality).
- **Get Session State:** Retrieve metadata, current variable state, and usage statistics for a specific session.
- **Delete Session:** Archive or remove a session.

### 3.2 Interactive Chat
The primary mechanism for intelligence.

- **Send Message:** `POST /sessions/{session_id}/chat`
  - Accepts user input.
  - Triggers the `Observe -> Think -> Act` loop.
  - Returns the agent's response, including executed tool calls and context usage metrics.
- **Streaming:** Support Server-Sent Events (SSE) or WebSocket for real-time token streaming and "Thinking" indicator updates.

### 3.3 Memory Introspection
Expose the "Mind" of the agent, allowing developers/users to see what the agent knows.

- **Get History:** Retrieve the episodic transcript of a session (or across sessions).
- **Get Facts (Vector):** Query the semantic memory store (ingested documents, insights).
- **Get Entities (Graph):** Query the associative graph (nodes and edges representing relationships).
- **Get Context:** Debug endpoint to view the exact context payload assembled for the last turn (Token usage, included memories).

### 3.4 Operational Commands
Expose maintenance and tool capabilities previously available as CLI slash-commands.

- **Ingest Document:** Upload/Text endpoint to add knowledge to the Vector store (`/ingest`).
- **Reorganize Memory:** Trigger background tasks for pruning, synthesis, and reflection (`/reorganize`).
- **Lifecycle Management:** Trigger memory promotion/decay cycles.

## 4. Component Outline

### 4.1 Application Structure
```text
packages/friday-api/
├── src/
│   └── friday_api/
│       ├── main.py             # App entry point
│       ├── config.py           # Environment configuration
│       ├── dependencies.py     # DI (Database, Auth, MemoryController)
│       ├── auth/               # Authentication logic
│       ├── routers/
│       │   ├── sessions.py     # Session CRUD
│       │   ├── chat.py         # Interaction endpoints
│       │   ├── memory.py       # Introspection (Graph, Vector, History)
│       │   └── admin.py        # System/Maintenance tasks
│       ├── models/             # Pydantic DTOs (Request/Response)
│       └── services/
│           ├── session_manager.py  # Hydrates "MemoryChatSession" from DB
│           └── chat_service.py     # Orchestrates the agent loop
```

### 4.2 Key Models (DTOs)

*   **SessionCreateRequest**: `system_prompt`, `agent_name`, `temperature`
*   **ChatRequest**: `message`, `tools_enabled`
*   **ChatResponse**: `content`, `tool_calls`, `metrics` (tokens, latency)
*   **MemoryQuery**: `query_text`, `limit`, `min_similarity`

## 5. Roadmap & Considerations

### 5.1 Immediate Next Steps
1.  **Scaffold Package:** Create `packages/friday-api` structure.
2.  **Define API Spec:** Draft the OpenAPI schema (or define Pydantic models).
3.  **Refactor Session Logic:** Extract `MemoryChatSession` from `memory-chat-v2.py` into a reusable, stateless-friendly service class within `friday-agent` or `friday-core` to be shared by both CLI and API.

### 5.2 Questions / Decisions
- **Async Workers:**
  - **Phase 1:** Use FastAPI `BackgroundTasks` for simpler implementation while architecting interfaces that allow offloading.
  - **Phase 2:** Introduce a proper task queue (Celery/Redis) for heavy workloads (Ingestion, Reorganization) to ensure scalability.
- **Deployment:** Initial build will target a containerized Docker environment (Docker Compose).

## 6. Refactoring Strategy (Planning)

To ensure consistency between the existing CLI and the new REST API, a decision on session orchestration logic is required:

### Option 1: "Refactor First" (Shared Core)
- **Concept:** Extract the orchestration logic from `memory-chat-v2.py` into a new, pure-logic `FridaySession` or `AgentSession` class within `packages/friday-agent`.
- **Pros:** Single source of truth; no logic duplication; easier testing; immediate architectural clean-up.
- **Cons:** Requires modifying a stable integration test/CLI tool during Phase 1.

### Option 2: "Parallel Implementation" (API-Specific)
- **Concept:** Implement a new `SessionService` within `packages/friday-api` that mirrors the CLI's logic but is optimized for stateless REST calls.
- **Pros:** Faster initial API delivery; zero risk to existing CLI stability.
- **Cons:** Duplicate logic for context assembly and memory handling; higher long-term maintenance debt.

**Recommendation:** Option 1 is preferred to maintain the project's standards of modularity and to ensure the API and CLI don't diverge in their memory handling behavior.

## 7. Critical Technical Challenges & Solutions

Implementing "Friday Memory" in a multi-tenant, low-latency web environment presents specific challenges distinct from the single-user CLI.

### 7.1 Latency vs. Persistence
**Challenge:** Context assembly (Vector Search + Graph Traversal) and Memory Ingestion (LLM extraction + Graph updates) are computationally expensive. Blocking the HTTP response for the "Write/Memorize" phase is unacceptable for user experience.

**Solution: "Read-Fast, Write-Async" Architecture**
1.  **Fast Path (The "Read" Loop):**
    -   User sends message.
    -   Retrieve *cached* hot-context (recent turns, active graph subgraph).
    -   Perform light Vector Search (Semantic Memory).
    -   Stream LLM response immediately.
2.  **Slow Path (The "Write" Loop):**
    -   *After* the response is sent (via `BackgroundTasks` in Phase 1), trigger the "Memorization" step.
    -   Extract entities/facts.
    -   Update Vector Store and Graph Store.
    -   This "Eventual Consistency" is acceptable for memory updates.

### 7.2 Multi-Tenant Graph Store (ElementX)
**Challenge:** `ElementX` is currently backed by a single in-memory `NetworkX` graph persisted to a file. Loading a massive, monolithic graph for all users is not scalable or secure.

**Solution: User-Partitioned Graphs**
-   **Storage:** Each user is assigned a distinct graph file (e.g., `users/{user_id}/graph.gpickle`) stored in Blob Storage (S3/MinIO) or local disk.
-   **Runtime:** The API maintains an **LRU Cache of Active Graph Stores**.
    -   When a request arrives for `user_123`, the system checks the cache.
    -   **Hit:** Use the already loaded `ElementXGraphStore` instance (Microsecond latency).
    -   **Miss:** Load the user's specific graph from disk (Milliseconds/Seconds latency).
    -   **Eviction:** Unused user graphs are unloaded from memory after a timeout.
-   **Security:** This physically isolates user data in memory and storage.

### 7.3 Multi-Tenant Vector Store
**Challenge:** Creating a separate Vector Collection for every user is inefficient in many Vector DBs (e.g., Chroma, Qdrant).

**Solution: Metadata Filtering**
-   **Single Collection:** All users share a single `friday_memory_facts` collection.
-   **Strict Partitioning:** Every document *must* have a `user_id` metadata field.
-   **Enforcement:** The `MemoryController` or API Service Layer must inject `where={"user_id": current_user.id}` into **every** query and deletion operation. This filter is never exposed to the client.
