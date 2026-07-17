# Friday Agent Framework
## Core Concepts & Architecture

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24

---

## Overview

This section builds your mental model of Friday's architecture before diving into specific features. Whether you're a project leader evaluating Friday for your team, an IT leader planning deployment, or a developer building agents, understanding these core concepts will clarify how Friday works and why it's designed this way.

**For Project Leaders:** This section explains the architectural decisions that make Friday production-ready and vendor-independent, helping you understand the strategic value and long-term maintainability of the framework.

**For IT Leaders:** You'll learn the technical architecture, deployment patterns, and integration points that matter for enterprise adoption—from scaling considerations to security boundaries to operational observability.

**For Users:** Understanding Friday's architecture helps you make better design decisions when building agents, choose the right tools for your use case, and troubleshoot issues effectively.

---

## 3.1 The Intelligence Plane & Control Plane Architecture

### Conceptual Model

Friday separates concerns into two distinct planes, inspired by distributed systems architecture:

**The Intelligence Plane:**
- Memory systems (remembering and learning)
- Context engineering (what to think about)
- Decision-making (reasoning and planning)
- Knowledge representation (how information is structured)

**The Control Plane:**
- Tools (interacting with the world)
- Actions (executing commands and operations)
- Sensors (gathering information)
- Outputs (producing results)

This separation isn't just conceptual—it's architectural. The Intelligence Plane handles *what to do and why*, while the Control Plane handles *how to do it and with what*. This clean separation enables:

- **Independent scaling**: Scale memory systems separately from tool execution
- **Security boundaries**: Restrict tool access without limiting intelligence
- **Testing isolation**: Test reasoning logic without external side effects
- **Modular replacement**: Swap execution mechanisms without rewriting logic

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                           FRIDAY AGENT                           │
│                                                                  │
│  ┌──────────────── INTELLIGENCE PLANE ────────────────────────┐  │
│  │                                                            │  │
│  │  ┌──────────────┐         ┌──────────────┐                 │  │
│  │  │   Memory     │         │    Context   │                 │  │
│  │  │  Controller  │◄────────┤   Assembler  │                 │  │
│  │  │              │         │              │                 │  │
│  │  │ - Vector DB  │         │ - Retrieval  │                 │  │
│  │  │ - Graph DB   │         │ - Budgeting  │                 │  │
│  │  │ - Transcripts│         │ - Formatting │                 │  │
│  │  └──────┬───────┘         └───────┬──────┘                 │  │
│  │         │                         │                        │  │
│  │         │    ┌────────────────────┴────────────┐          │  │
│  │         │    │   Prompt Architect              │          │  │
│  │         │    │  - Token budgeting              │          │  │
│  │         │    │  - Lost-in-middle mitigation    │          │  │
│  │         │    │  - Format optimization          │          │  │
│  │         │    └────────────┬────────────────────┘          │  │
│  │         │                 │                                │  │
│  └─────────┼─────────────────┼────────────────────────────────┘  │
│            │                 │                                    │
│            │    ┌────────────▼────────────┐                      │
│            │    │      LLM Service        │                      │
│            │    │  (Provider-agnostic)    │                      │
│            │    └────────────┬────────────┘                      │
│            │                 │                                    │
│  ┌─────────┼─────────────────┼────────── CONTROL PLANE ──────┐  │
│  │         │                 │                                │  │
│  │         │                 ▼                                │  │
│  │         │    ┌──────────────────────┐                     │  │
│  │         │    │   Tool Execution     │                     │  │
│  │         │    │   - Filesystem       │                     │  │
│  │         │    │   - Shell commands   │                     │  │
│  │         │    │   - Web/API calls    │                     │  │
│  │         │    │   - Code execution   │                     │  │
│  │         │    │   - Git operations   │                     │  │
│  │         │    └──────────┬───────────┘                     │  │
│  │         │               │                                  │  │
│  │         │               ▼                                  │  │
│  │         │    ┌──────────────────────┐                     │  │
│  │         └───►│  Memory Extraction   │                     │  │
│  │              │  - Entities          │                     │  │
│  │              │  - Relationships     │                     │  │
│  │              │  - Insights          │                     │  │
│  │              └──────────────────────┘                     │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Data Flow: A Single Turn

Let's trace a single conversation turn through the architecture:

```
1. USER INPUT
   "What Python libraries should I use for my web API?"
   │
   ▼
2. CONTEXT ASSEMBLY (Intelligence Plane)
   ├─ Query memory stores in parallel:
   │  ├─ Episodic: Recent conversation history
   │  ├─ Semantic: Relevant insights about Python/APIs
   │  └─ Associative: User's prior mentions of Python, FastAPI, etc.
   |. |_ Possible tool call - web search, memory_recall
   │
   ├─ Context Engineering - Token budgeting with knapsack optimization:
   │  └─ Fit maximum relevant context within LLM window
   │
   └─ Result: Assembled context payload
   │
   ▼
3. PROMPT ARCHITECTURE (Intelligence Plane)
   ├─ Structure messages for LLM:
   │  ├─ System: Base prompt + identity
   │  ├─ History: Prior conversation turns
   │  ├─ Context: Retrieved memories (tail injection)
   │  └─ Query: User's question
   │
   └─ Result: Optimized prompt with "lost-in-middle" mitigation
   │
   ▼
4. LLM INFERENCE
   ├─ Send formatted messages to LLM (OpenAI/Anthropic/etc.)
   ├─ Include tool schemas if agent has tool access
   └─ Result: Response text + optional tool calls
   │
   ▼
5. TOOL EXECUTION (Control Plane) [If tool calls present]
   ├─ For each tool call:
   │  ├─ Validate parameters
   │  ├─ Execute tool (read file, web search, git status, etc.)
   │  ├─ Capture result + metadata (latency, status)
   │  └─ Return to LLM for processing
   │
   └─ Re-Act loop continues until no more tool calls
   │
   ▼
6. MEMORY EXTRACTION (Background, Intelligence Plane)
   ├─ LLM analyzes conversation for entities:
   │  └─ "Python", "web API", "FastAPI" → Technology entities
   │
   ├─ LLM identifies relationships:
   │  └─ User INTERESTED_IN Python, Python USED_FOR web API
   │
   └─ LLM generates insights:
      └─ "User prefers Python for backend development"
   │
   ▼
7. MEMORY STORAGE (Intelligence Plane)
   ├─ Entities → Graph store (NetworkX + JSON)
   ├─ Insights → Vector store (ChromaDB with embeddings)
   ├─ Full turn → Transcript store (SQLite)
   └─ Hebbian learning: Increment hit counts for accessed entities
   │
   ▼
8. RESPONSE DELIVERY
   "For a Python web API, I recommend FastAPI or Flask.
    FastAPI offers automatic documentation and async support..."
```

This flow happens for **every turn**, building memory incrementally.

### Why This Separation Matters

**For Project Leaders:**
The Intelligence Plane / Control Plane separation is a strategic architectural decision that provides:
- **Vendor independence**: Swap LLM providers or storage backends without rewriting application logic
- **Security compliance**: Restrict tool execution (Control Plane) while maintaining intelligence (Intelligence Plane)
- **Cost optimization**: Scale memory systems (expensive) separately from tool execution (cheap)
- **Future-proofing**: As AI capabilities evolve, upgrade the Intelligence Plane without touching the Control Plane

**For IT Leaders:**
This architecture enables:
- **Horizontal scaling**: Deploy multiple Control Plane instances (tool executors) behind a single Intelligence Plane (memory system)
- **Security boundaries**: Run tools in sandboxed containers while Intelligence Plane operates in trusted environment
- **Observability**: Instrument Intelligence Plane (reasoning) and Control Plane (actions) independently with different telemetry
- **Resource allocation**: High-memory nodes for Intelligence Plane (ChromaDB, graph), CPU-optimized nodes for Control Plane (tools)

**For Users:**
This means:
- **Flexible tool sets**: Add/remove tools without affecting memory or reasoning
- **Consistent intelligence**: Agent's memory and learning persist even when tools change
- **Clear debugging**: Separate Intelligence Plane issues (bad context retrieval) from Control Plane issues (tool failure)
- **Modular development**: Test reasoning logic without running actual tools (use mocks)

---

## 3.2 Protocol-First Design Philosophy

### The Problem: Vendor Lock-In

Most AI frameworks suffer from **tight coupling**—if you start with OpenAI, migrating to Anthropic requires code rewrites. If you use Pinecone, switching to Weaviate means architectural changes. This creates strategic risk: you're dependent on vendor pricing, availability, and feature decisions.

Friday solves this with **protocol-first design**: every major component is defined as an abstract interface (protocol), with implementations being swappable modules.

### How Protocols Work

Think of protocols as **contracts**. A protocol says "any component implementing me must provide these methods with these signatures." Implementations can vary—ChromaDB, Pinecone, or a custom database—but they all satisfy the same contract.

**Example: The VectorStoreAdapter Protocol**

```python
from typing import Protocol, List, Dict, Any

class VectorStoreAdapter(Protocol):
    """Contract for any vector storage backend."""

    async def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        """Store documents with embeddings."""
        ...

    async def similarity_search(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        ...

    async def delete_documents(
        self,
        ids: List[str],
    ) -> None:
        """Remove documents by ID."""
        ...
```

**Any** vector database that implements these three methods can be used by Friday. The framework doesn't care if it's ChromaDB, Pinecone, or a SQL database with pgvector—as long as it satisfies the protocol.

### Friday's Core Protocols

| Protocol | Purpose | Example Implementations |
|----------|---------|-------------------------|
| **LLMClient** | Chat completion inference | LiteLLMService (100+ providers), custom clients |
| **EmbeddingModel** | Text → vector embeddings | LiteLLM embeddings, local models, custom |
| **VectorStoreAdapter** | Semantic search storage | ChromaDB, Pinecone, Weaviate, Qdrant, pgvector |
| **GraphStoreAdapter** | Relationship storage | NetworkX+JSON, Neo4j, ArangoDB, AWS Neptune |
| **TranscriptStoreAdapter** | Conversation logging | SQLite, PostgreSQL, MySQL, MongoDB |
| **ToolDefinition** | Tool schema & execution | BaseTool subclasses, @tool decorator functions |
| **ContextEngineeringInterface** | Context assembly | ContextAssembler (default), custom strategies |
| **TelemetryInterface** | Observability hooks | Debug recorder, OpenTelemetry, DataDog |

### Real-World Example: Swapping Vector Stores

Let's say you start with ChromaDB locally, then need to migrate to Pinecone for production:

**Before (ChromaDB):**
```python
from friday_memory import ChromaVectorStore

vector_store = ChromaVectorStore(
    persist_directory="./data/vector",
    collection_name="memories",
)
```

**After (Pinecone):**
```python
from friday_memory import PineconeVectorStore  # Your custom implementation

vector_store = PineconeVectorStore(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment="us-west1-gcp",
    index_name="friday-memories",
)
```

**That's it.** The rest of your Friday agent code is unchanged. MemoryController doesn't care—it just uses the `VectorStoreAdapter` protocol.

### Implementing Custom Protocols

You can bring your own implementations for any protocol. Here's a minimal example:

```python
from typing import List, Dict, Any
import psycopg2
from pgvector.psycopg2 import register_vector

class PostgresVectorStore:
    """Custom vector store using PostgreSQL + pgvector."""

    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        register_vector(self.conn)
        self._ensure_schema()

    def _ensure_schema(self):
        """Create tables if needed."""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    embedding vector(1536),
                    metadata JSONB
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS embedding_idx
                ON documents USING ivfflat (embedding vector_cosine_ops)
            """)
        self.conn.commit()

    async def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        """Implement VectorStoreAdapter.add_documents."""
        # Generate embeddings (using your embedding model)
        embeddings = await self._embed(documents)

        with self.conn.cursor() as cur:
            for doc, meta, id_, emb in zip(documents, metadatas, ids, embeddings):
                cur.execute(
                    "INSERT INTO documents (id, content, embedding, metadata) VALUES (%s, %s, %s, %s)",
                    (id_, doc, emb, json.dumps(meta))
                )
        self.conn.commit()

    async def similarity_search(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Implement VectorStoreAdapter.similarity_search."""
        query_embedding = await self._embed([query])

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, content, metadata,
                       1 - (embedding <=> %s) as similarity
                FROM documents
                WHERE 1 - (embedding <=> %s) > %s
                ORDER BY embedding <=> %s
                LIMIT %s
            """, (query_embedding[0], query_embedding[0], threshold, query_embedding[0], limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "metadata": json.loads(row[2]),
                    "similarity": row[3],
                })
            return results

    # ... implement other required methods
```

**Now use it with Friday:**
```python
vector_store = PostgresVectorStore("postgresql://localhost/friday")
controller = MemoryController(
    vector_store=vector_store,  # ✓ Works because it implements the protocol
    graph_store=graph_store,
    transcript_store=transcript_store,
)
```

### Benefits: Strategic & Tactical

**For Project Leaders:**
- **No vendor lock-in**: Preserve optionality as technology landscape evolves
- **Risk mitigation**: If a vendor raises prices or sunsets a product, you can migrate
- **Competitive leverage**: Negotiate better terms knowing you're not dependent
- **Long-term maintainability**: Architecture outlives any specific implementation

**For IT Leaders:**
- **Gradual migration**: Swap components one at a time, validate in stages
- **Multi-cloud strategy**: Use different providers in different regions/environments
- **Compliance flexibility**: Route sensitive data to approved storage (on-prem PostgreSQL) while using cloud for general data (Pinecone)
- **Cost optimization**: Mix free/cheap providers (Ollama, ChromaDB) with premium services where justified

**For Users:**
- **Technology experimentation**: Try new vector databases without rewriting agents
- **Local development**: Use lightweight local stores (SQLite, ChromaDB) in development, production stores (Postgres, Pinecone) in staging/prod
- **Testing**: Mock protocols for fast unit tests without external dependencies
- **Learning**: Study different implementations to understand trade-offs

---

## 3.3 Monorepo Package Structure

### The Fifteen Packages

Friday is structured as a **monorepo**—multiple packages in a single repository, with clear dependency relationships. The framework uses **uv** (a modern, high-performance Python package manager) for workspace management, enabling 10-100x faster installations than traditional tools while maintaining full PyPI compatibility. This enables independent development, selective installation, and fine-grained versioning.

```
friday-agent-framework/
├── packages/
│   ├── friday-core/           # Foundation (protocols, config, logging)
│   ├── friday-memory/         # Memory system (3-tier architecture)
│   ├── friday-llm/            # LLM client (provider-agnostic)
│   ├── friday-agent/          # Agent implementations (Re-Act, orchestration)
│   ├── friday-tools/          # Tool catalog (50+ built-in tools)
│   ├── friday-transcript/     # Conversation logging (SQLite)
│   ├── friday-mcp/            # Model Context Protocol integration
│   ├── friday-optimization/   # Algorithms (knapsack, token budgeting)
│   ├── friday-cli/            # Interactive terminal interface
│   ├── friday-runtime/        # Agent execution loop and lifecycle
│   ├── friday-sandbox/        # Isolated tool execution environment
│   ├── friday-telemetry/      # Observability, metrics, cost tracking
│   ├── friday-speech/         # Voice I/O (see speech.md)
│   │
│   ├── Application packages:
│   ├── friday-finance/        # Finance application built on Friday
│   └── friday-moltbook/       # Moltbook application built on Friday
│
├── tests/                     # Integration tests
├── workflows/                 # Example YAML workflows
├── docs/                      # Documentation (you're reading it!)
└── pyproject.toml             # Workspace configuration
```

### Dependency Flow

The dependency graph is **directed and acyclic**—packages only depend on layers below them:

```
friday-core
│
┌───────────┼───────────┬──────────────────┐
│           │           │                  │
friday-memory  friday-llm  friday-optimization  friday-telemetry
│           │
└─────┬─────┘
      │
friday-agent
│
┌─────────┼──────────┬───────────┬──────────────┐
│         │          │           │              │
friday-tools  friday-  friday-  friday-sandbox  friday-runtime
          transcript  mcp
│
┌─────────┴──────────┐
│                    │
friday-cli       friday-speech
```

Application packages (`friday-finance`, `friday-moltbook`) sit above the framework layer and depend on `friday-agent` and its siblings—never the reverse.

**Why this matters:**
- **Independent evolution**: Changes in `friday-tools` don't affect `friday-memory`
- **Selective installation**: Use only what you need (e.g., just `friday-memory` for custom agents)
- **Clear boundaries**: Circular dependencies are impossible by design
- **Modular testing**: Test each package in isolation

### Package Management with uv

Friday uses **uv** as its package manager and build tool. uv is a modern, high-performance Python package manager written in Rust that dramatically improves the developer experience compared to traditional tools.

#### What is uv?

[uv](https://github.com/astral-sh/uv) is an "extremely fast Python package installer and resolver" from Astral (creators of Ruff). It's designed as a drop-in replacement for `pip`, `pip-tools`, and `virtualenv`, but with:

- **10-100x faster installation** compared to pip
- **Deterministic dependency resolution** (like Poetry, but faster)
- **Workspace support** for monorepos (critical for Friday's monorepo structure)
- **Compatible with pip** (uses PyPI, respects requirements.txt)
- **Single binary** installation (no bootstrapping issues)

#### Why Friday Uses uv

**For Project Leaders:**
- **Developer productivity**: Faster installs mean faster iteration cycles (seconds vs. minutes for full environment setup)
- **Reproducible builds**: Deterministic resolution prevents "works on my machine" issues
- **Future-proof tooling**: Modern, actively developed tool with strong backing (Astral)
- **Lower barrier to contribution**: Single `uv sync` command to get development environment ready

**For IT Leaders:**
- **CI/CD performance**: Dramatically faster pipeline execution (dependency installation is often the slowest step)
- **Disk space efficiency**: uv uses global cache, reducing redundant package downloads across projects
- **Security**: Faster security patch application (quick environment rebuilds)
- **Docker optimization**: Smaller image build times and better layer caching

**For Users:**
- **Faster iteration**: Install packages in seconds, not minutes
- **Less friction**: Single command (`uv sync`) handles all dependencies across all 15 packages
- **Better errors**: Clear, actionable error messages for dependency conflicts
- **pip compatibility**: Can still use `pip install friday-agent` from PyPI

#### uv Workspace Configuration

Friday's monorepo is configured as a uv workspace via `pyproject.toml`:

```toml
[tool.uv.workspace]
members = [
    "packages/friday-core",
    "packages/friday-memory",
    "packages/friday-llm",
    "packages/friday-agent",
    "packages/friday-tools",
    "packages/friday-transcript",
    "packages/friday-mcp",
    "packages/friday-optimization",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]
```

**What this enables:**
- **Single virtual environment** for all packages (no juggling multiple venvs)
- **Shared dependencies** across packages (install once, use everywhere)
- **Editable installs** (changes in one package immediately visible to others)
- **Unified testing** (run tests across all packages with one command)

#### Common uv Commands

```bash
# Install all workspace dependencies (one command for entire Friday framework)
uv sync

# Add a dependency to a specific package
uv add --package friday-memory chromadb

# Run tests across all packages
uv run pytest

# Update dependencies
uv lock --upgrade

# Create a new virtual environment
uv venv

# Install from PyPI (pip-compatible)
uv pip install friday-agent
```

#### Comparison to Other Tools

| Feature | uv | pip | Poetry | pdm |
|---------|----|----|--------|-----|
| **Speed** | ⚡ Fastest | Slow | Moderate | Fast |
| **Workspace support** | ✅ Native | ❌ No | ⚠️ Plugins | ✅ Yes |
| **Dependency resolution** | ✅ Fast | ⚠️ Basic | ✅ Good | ✅ Good |
| **PyPI compatibility** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Installation** | Single binary | System Python | Poetry install | pip install |
| **Lock files** | ✅ uv.lock | ❌ No | ✅ poetry.lock | ✅ pdm.lock |

**Why not pip?**
- No native workspace support (requires manual coordination across packages)
- Slow dependency resolution (can take minutes for large dependency trees)
- No deterministic locking (different environments may resolve differently)

**Why not Poetry?**
- Slower than uv (still Python-based, not Rust)
- Workspace support requires plugins (not first-class)
- More complex setup (Poetry install, then poetry shell, then poetry install packages)

**Why not pdm?**
- Good tool, but smaller ecosystem and less tooling integration
- uv has momentum and backing from Astral (proven track record with Ruff)

#### Using uv with Friday

**Development workflow:**
```bash
# Clone repository
git clone <repo>
cd friday-agent-framework

# Single command to set up entire development environment
uv sync

# All packages are now installed in editable mode
# Changes in friday-memory immediately visible to friday-agent

# Run tests
uv run pytest

# Format code
uv run ruff format .

# Type check
uv run mypy packages/friday-core
```

**Production deployment:**
```bash
# Install Friday from PyPI (uv is pip-compatible)
uv pip install friday-agent

# Or specify version
uv pip install friday-agent==0.1.0

# Or install from lock file for reproducibility
uv pip sync requirements.lock
```

#### Migration from pip/Poetry

If you're already using pip or Poetry, migrating to uv is straightforward:

**From pip:**
```bash
# Instead of:
pip install -r requirements.txt

# Use:
uv pip install -r requirements.txt

# Or for workspace development:
uv sync
```

**From Poetry:**
```bash
# Instead of:
poetry install

# Use:
uv sync  # uv reads pyproject.toml automatically
```

**Compatibility:** uv respects existing `requirements.txt`, `pyproject.toml`, and can generate Poetry-compatible lock files if needed.

#### Performance Benchmarks

Real-world Friday framework installation times:

| Tool | Cold install | Cached install |
|------|-------------|----------------|
| **uv** | 12s | 3s |
| **pip** | 245s | 180s |
| **Poetry** | 89s | 45s |
| **pdm** | 34s | 15s |

*Test environment: M2 MacBook Pro, installing all Friday packages + dependencies (~150 packages total)*

**Result:** uv is **20x faster** than pip for cold installs, **7x faster** than Poetry.

### Package Details

#### friday-core
**Purpose:** Foundation layer with abstract protocols and shared utilities.

**Contents:**
- `interfaces/` - Abstract protocols for all major components
- `config/` - Configuration management (YAML parsing, validation)
- `logging/` - Structured logging setup
- `exceptions/` - Framework-level exceptions

**Who uses it:** All other packages depend on `friday-core`

**When to use directly:** Building custom Friday-compatible components from scratch

#### friday-memory
**Purpose:** Three-tier memory system with lifecycle management.

**Contents:**
- `controller/` - MemoryController (unified facade)
- `stores/` - Vector, graph, episodic store implementations
- `context/` - ContextAssembler, PromptArchitect
- `lifecycle/` - Memory promotion, decay, reactivation
- `extraction/` - Entity and insight extraction
- `maintenance/` - Memory reorganization, pruning

**Dependencies:** `friday-core`, `friday-llm` (for extraction)

**When to use directly:** Building agents with custom memory strategies

#### friday-llm
**Purpose:** Provider-agnostic LLM client with resilience patterns.

**Contents:**
- `service/` - LiteLLMService (wraps litellm library)
- `resilience/` - Retry logic, circuit breakers, timeouts
- `embeddings/` - Embedding model abstraction
- `telemetry/` - LLM call instrumentation

**Dependencies:** `friday-core`

**When to use directly:** Using Friday's LLM client in non-Friday projects

#### friday-agent
**Purpose:** Agent implementations and orchestration.

**Contents:**
- `copilot.py` - CopilotAgent (Re-Act loop with tools)
- `autonomous.py` - AutonomousAgent (planned)
- `orchestrator.py` - Multi-agent coordination
- `profile.py` - AgentProfile (identity and capabilities)
- `registry.py` - AgentRegistry (discovery and instantiation)
- `loader.py` - AgentLoader (YAML-based configuration)
- `workflows/` - Workflow engine, task graphs

**Dependencies:** `friday-core`, `friday-memory`, `friday-llm`

**When to use directly:** This is the primary package for most users

#### friday-tools
**Purpose:** Tool catalog and execution infrastructure.

**Contents:**
- `base.py` - BaseTool abstract class
- `filesystem/` - File operations (read, write, search)
- `shell/` - Command execution (subprocess, scripts)
- `web/` - HTTP requests, scraping, search
- `git/` - Version control operations
- `data/` - Parsing (JSON, YAML, CSV, XML)
- `text/` - Text manipulation (regex, formatting)
- `code/` - Code execution, linting, analysis
- `integrations/` - External APIs (future: Slack, GitHub, etc.)

**Dependencies:** `friday-core`

**When to use directly:** Using Friday tools in non-Friday projects, or building custom tools

#### friday-transcript
**Purpose:** Conversation logging with export capabilities.

**Contents:**
- `store.py` - SQLiteTranscriptStore (default implementation)
- `models.py` - Data models (Session, Turn, ToolCall)
- `exporter.py` - Export to JSONL, Markdown, training format

**Dependencies:** `friday-core`

**When to use directly:** Custom transcript storage or analysis

#### friday-mcp
**Purpose:** Model Context Protocol client and server implementations.

**Contents:**
- `client.py` - MCP client (consume external MCP servers)
- `server.py` - MCP server (expose Friday resources)
- `transport/` - SSE, stdio transports
- `adapters/` - Friday tool → MCP tool adapter

**Dependencies:** `friday-core`, `friday-tools`

**When to use directly:** Integrating Friday with MCP ecosystem

#### friday-optimization
**Purpose:** Optimization algorithms for context engineering.

**Contents:**
- `knapsack.py` - 0/1 knapsack solver for token budgeting
- `scoring.py` - Relevance scoring functions
- `utils.py` - Mathematical utilities

**Dependencies:** `friday-core`

**When to use directly:** Custom context assembly strategies

### Installation Patterns

**Full Stack (Most Common):**
```bash
# Using pip (traditional)
pip install friday-agent

# Or using uv (10-100x faster)
uv pip install friday-agent
```
Installs all core packages (`friday-core`, `friday-memory`, `friday-llm`, `friday-agent`, `friday-tools`, `friday-transcript`)

**Memory Only:**
```bash
# Using pip
pip install friday-memory

# Or using uv
uv pip install friday-memory
```
Installs just the memory system + dependencies (`friday-core`, `friday-llm`)
Use case: Building custom agents with Friday's memory but your own execution logic

**Tools Only:**
```bash
# Using pip
pip install friday-tools

# Or using uv
uv pip install friday-tools
```
Installs just the tool catalog + dependencies (`friday-core`)
Use case: Using Friday's tools in a non-Friday project

**Development Install (Recommended: uv):**
```bash
# Clone repository
git clone <repo>
cd friday-agent-framework

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# One command installs all packages in editable mode (seconds, not minutes)
uv sync

# Verify installation
uv run python -c "from friday_agent import CopilotAgent; print('✓ Ready')"
```

**Why uv for development?**
- **Speed**: 12s for full Friday install vs. 245s with pip
- **Workspace support**: Single command for all 15 packages
- **Reproducibility**: Lock files ensure consistent environments
- **pip-compatible**: Can still use `pip install` commands

### Practical Implications

**For Project Leaders:**
- **Cost control**: Only install and pay for what you need (e.g., skip `friday-mcp` if not using MCP)
- **Risk distribution**: Issues in one package don't affect others (blast radius containment)
- **Vendor evaluation**: Each package can use different vendors (ChromaDB for vector, Neo4j for graph)
- **Team organization**: Different teams can own different packages

**For IT Leaders:**
- **Deployment flexibility**: Deploy packages on different infrastructure (memory on high-RAM nodes, tools on CPU-optimized)
- **Security boundaries**: Run tools in sandboxed containers while memory stays in trusted environment
- **Update strategy**: Update packages independently (patch `friday-tools` without touching `friday-memory`)
- **License compliance**: Each package can have different licensing if needed

**For Users:**
- **Learning curve**: Study packages in dependency order (core → memory → llm → agent)
- **Debugging**: Package boundaries help isolate issues (memory retrieval vs. tool execution vs. LLM calls)
- **Extension**: Implement protocols in any package to customize behavior
- **Performance**: Profile packages separately to identify bottlenecks

---

## 3.4 The Memory Loop: Context → Action → Learning

### The Cognitive Cycle

Friday agents operate in a continuous loop that mimics human learning:

```
    ┌──────────────────────────────────────────┐
    │                                          │
    ▼                                          │
┌────────────┐                                │
│  CONTEXT   │  Retrieve relevant memories    │
│  ASSEMBLY  │  Budget tokens optimally       │
│            │  Format for LLM                │
└─────┬──────┘                                │
      │                                       │
      ▼                                       │
┌────────────┐                                │
│   ACTION   │  LLM generates response        │
│ GENERATION │  Optionally calls tools        │
│            │  Produces output                │
└─────┬──────┘                                │
      │                                       │
      ▼                                       │
┌────────────┐                                │
│  LEARNING  │  Extract entities               │
│  (MEMORY)  │  Identify relationships         │
│            │  Store insights                │
└─────┬──────┘                                │
      │                                       │
      │  Memory informs next context          │
      └───────────────────────────────────────┘
```

**This loop runs for every conversation turn**, continuously building knowledge.

### Phase 1: Context Assembly

**Goal:** Gather relevant information from memory stores to inform the LLM's response.

**Process:**
1. **Parallel Retrieval** - Query all three stores simultaneously:
   - **Episodic**: Last N conversation turns (default 10)
   - **Semantic**: Similarity search for relevant insights (embedding-based)
   - **Associative**: Entities and relationships from knowledge graph

2. **Scoring & Ranking** - Each memory gets a relevance score based on:
   - **Semantic similarity** to current query (cosine distance)
   - **Recency** (newer memories score higher)
   - **Importance** (Hebbian hit_count for entities)
   - **Stage** (long-term memories score higher than short-term)

3. **Token Budgeting** - Use knapsack algorithm to select optimal subset:
   - Each memory has a **token cost** (estimated by character count / 4)
   - Each memory has a **value** (relevance score)
   - Problem: Maximize value while staying within token budget
   - Solution: Dynamic programming 0/1 knapsack solver

4. **Result**: `ContextPayload` containing:
   - System prompt
   - Conversation history (episodic)
   - Retrieved insights (semantic)
   - Loaded entities (associative)
   - Injected tools (if any)
   - Scoped variables

**Performance Target:** <200ms for context assembly

**Example:**
```python
# User asks: "What was that library I mentioned for web APIs?"

# Context assembly retrieves:
# - Episodic: Last 10 conversation turns (includes mention of FastAPI)
# - Semantic: Insights about "web API", "Python libraries"
# - Associative: Entity "FastAPI" with relationship: User MENTIONED FastAPI

# Result: LLM has context to answer accurately without guessing
```

### Phase 2: Action Generation

**Goal:** Generate a response, optionally calling tools if needed.

**Process:**
1. **Prompt Architecture** - Structure messages for LLM:
   ```
   System: Base identity + capabilities
   History: Prior conversation (chronological)
   Context: Retrieved memories (tail injection - "lost in middle" mitigation)
   Tools: Available tool schemas (if agent has tools)
   Query: User's current message
   ```

2. **LLM Inference** - Send to LLM provider:
   - Uses resilience patterns (retry, timeout, circuit breaker)
   - Handles tool calling formats (OpenAI vs. Anthropic)
   - Captures token usage, latency, model version

3. **Tool Execution** (Re-Act Loop if tools called):
   ```
   While has_tool_calls and iterations < max_iterations:
       For each tool call:
           Validate parameters
           Execute tool (async)
           Capture result + metadata
       Add tool results to message history
       Call LLM again with results
   ```

4. **Result**: Final response text + execution metadata

**Performance Target:** 1-5s for LLM inference (provider-dependent), <100ms per tool execution (tool-dependent)

**Example:**
```python
# User asks: "What's in my config.yaml file?"

# Action generation:
# 1. LLM decides to call read_file tool
# 2. Tool executes: read_file(file_path="config.yaml")
# 3. Tool returns file contents
# 4. LLM receives contents, generates summary
# 5. Response: "Your config.yaml contains LLM settings (gpt-4o-mini),
#              memory configuration (8000 token budget), and..."
```

### Phase 3: Learning (Memory Storage)

**Goal:** Extract structured knowledge from the conversation and store for future retrieval.

**Process:**
1. **Extraction** (runs asynchronously, doesn't block response):
   - **Entity Extraction**: LLM identifies entities with types
     ```json
     {
       "entities": [
         {"name": "FastAPI", "type": "Technology", "description": "Python web framework"},
         {"name": "Alice", "type": "Person", "description": "User working on Python project"}
       ]
     }
     ```

   - **Relationship Extraction**: LLM identifies semantic connections
     ```json
     {
       "relationships": [
         {"source": "Alice", "verb": "INTERESTED_IN", "target": "FastAPI"},
         {"source": "FastAPI", "verb": "USED_FOR", "target": "web APIs"}
       ]
     }
     ```

   - **Insight Generation**: LLM generates actionable knowledge
     ```json
     {
       "insights": [
         {
           "content": "User prefers FastAPI over Flask for Python web APIs",
           "confidence": 0.85,
           "type": "preference"
         }
       ]
     }
     ```

2. **Storage**:
   - **Entities & Relationships** → Graph store
     - Merge with existing entities (avoid duplicates)
     - Increment hit counts (Hebbian learning)
     - Persist to JSON

   - **Insights** → Vector store
     - Generate embeddings using embedding model
     - Store in `memories_short_term` collection initially
     - Include metadata (confidence, type, provenance)

   - **Full Turn** → Transcript store
     - User message, assistant response, tool calls, tool results
     - Token usage, latency, timestamps
     - Provenance (which agent, if multi-agent)

3. **Lifecycle Management** (runs after each turn or on schedule):
   - **Promotion**: Short-term memories with high access + age → long-term
   - **Decay**: Long-term memories with no recent access → decayed
   - **Reactivation**: Decayed memories accessed again → back to long-term

**Performance Target:** Extraction runs in background (1-3s), doesn't block next turn

**Example:**
```python
# After user says: "I prefer FastAPI over Flask for web development"

# Learning phase extracts:
# Entities: FastAPI, Flask (both Technology)
# Relationships: User PREFERS FastAPI OVER Flask
# Insights: "User has strong preference for FastAPI" (confidence: 0.9)

# Next time user asks about web frameworks, this preference
# is retrieved from memory and influences the response
```

### The Full Cycle in Action

Let's trace a complete cycle with a realistic example:

**User:** "Can you help me write a Python function to validate email addresses?"

**Turn 1 - First Message:**

1. **Context Assembly:**
   - Episodic: Empty (first turn)
   - Semantic: Empty (no prior knowledge)
   - Associative: Empty (clean slate)
   - Result: Minimal context (just system prompt)

2. **Action Generation:**
   - LLM generates: "I can help with that. Here's a Python function using regex..."
   - No tools called (direct response)

3. **Learning:**
   - Entities: "Python" (Technology), "email validation" (Concept)
   - Relationships: User WORKING_ON email validation, email validation IMPLEMENTED_IN Python
   - Insights: "User needs Python code for email validation"

**Turn 2 - Follow-up:**

**User:** "Can you write unit tests for that function?"

1. **Context Assembly:**
   - Episodic: Turn 1 (email validation function discussion)
   - Semantic: Insight about "email validation" (retrieved by similarity)
   - Associative: "Python" entity with WORKING_ON relationship
   - Result: Rich context including the function from Turn 1

2. **Action Generation:**
   - LLM has context of the function from Turn 1
   - Generates unit tests for that specific function
   - Optionally calls write_file tool to save tests

3. **Learning:**
   - Entities: "unit testing" (Concept), "pytest" (Technology - if mentioned)
   - Relationships: email validation TESTED_BY unit testing
   - Insights: "User follows test-driven development practices"
   - Hebbian: Increment hit_count for "Python" entity (accessed again)

**Turn 3 - Days Later, New Session:**

**User:** "What was that email validation code you helped me with?"

1. **Context Assembly (with priming):**
   - Episodic: None (old session, not loaded by default)
   - **Semantic: Retrieves insight "User needs Python code for email validation"** (embedding similarity)
   - **Associative: "email validation" entity with high hit_count** (primed on session start)
   - Result: Friday **remembers** the prior context

2. **Action Generation:**
   - LLM response: "I helped you with a Python email validation function using regex. Here's the code..." (reconstructs from memory)

3. **Learning:**
   - **Reactivation**: If the old insights had decayed, this access reactivates them
   - Hebbian: Increment hit_count again (reinforces importance)

**This demonstrates the full power of the Memory Loop: genuine learning and recall across time.**

### Why the Loop Matters

**For Project Leaders:**
- **Compound learning effect**: Agents get smarter over time, not just within conversations
- **ROI improvement**: Investment in agent development yields increasing returns as memory builds
- **Competitive moat**: Accumulated knowledge becomes a strategic asset
- **Quality consistency**: Agents apply learned patterns across all interactions

**For IT Leaders:**
- **Observable at every phase**: Instrument context retrieval, LLM calls, tool execution, and memory storage separately
- **Scalable components**: Context assembly can be cached, learning can run async, stores can be distributed
- **Failure isolation**: Issues in one phase don't cascade (extraction failure doesn't block response)
- **Performance tuning**: Optimize each phase independently (faster retrieval, cheaper extraction model)

**For Users:**
- **Predictable behavior**: Understanding the loop helps debug unexpected responses (check context assembly)
- **Effective training**: Structure conversations to maximize learning (explicit preferences, clear relationships)
- **Trust building**: See what Friday learned via `/entities`, `/facts`, `/insights` commands
- **Workflow design**: Design agent interactions that leverage the loop (research → synthesis → application)

---

## Putting It All Together

Friday's architecture is built on four foundational principles:

1. **Intelligence Plane / Control Plane Separation** - Intelligence (memory, reasoning) is independent of execution (tools, actions)
2. **Protocol-First Design** - Every component is swappable via abstract interfaces (zero vendor lock-in)
3. **Modular Packages** - Thirteen framework packages with clear dependencies (selective installation, isolated testing)
4. **Memory Loop** - Continuous learning through Context → Action → Learning cycle (compound knowledge growth)

These principles combine to create a framework that is:
- **Production-ready** - Observable, resilient, scalable
- **Vendor-independent** - Swap any component without code changes
- **Future-proof** - Architecture outlives specific implementations
- **Genuinely adaptive** - Agents that learn and improve over time

**You now understand Friday's core architecture.** The remaining sections dive deep into specific capabilities built on this foundation.

---

## What's Next?

With this mental model established, you're ready to explore Friday's capabilities in depth:

**For Memory Details:**
→ **[Section 4: Adaptive Memory](04-adaptive-memory.md)** - Deep dive into the three-tier memory system, lifecycle management, and context engineering

**For Practical Usage:**
→ **[Section 5: Tools](05-tools.md)** - Comprehensive tool catalog and custom tool creation
→ **[Section 9: CLI Reference](09-cli-reference.md)** - Command-by-command documentation

**For Multi-Agent:**
→ **[Section 7: Multi-Agent Orchestration](07-multi-agent.md)** - Building collaborative agent teams

**For Deployment:**
→ **[Section 10: Configuration Guide](10-configuration.md)** - Complete YAML reference
→ **[Section 11: Advanced Topics](11-advanced-topics.md)** - Production deployment patterns

---

## Quick Reference

### Architecture Layers
```
Intelligence Plane          Control Plane
├─ Memory stores            ├─ Tool execution
├─ Context assembly         ├─ Action results
├─ Prompt architecture      └─ Sensor inputs
└─ Decision-making
```

### Core Protocols
- **LLMClient** - LLM inference
- **VectorStoreAdapter** - Semantic search
- **GraphStoreAdapter** - Relationship storage
- **TranscriptStoreAdapter** - Conversation logs
- **ToolDefinition** - Tool schemas

### Memory Loop Phases
1. **Context** - Retrieve relevant memories
2. **Action** - Generate response + call tools
3. **Learning** - Extract entities, relationships, insights

### Package Dependencies
```
Core → Memory/LLM → Agent → Tools/Transcript/MCP
```

---

*Continue to [Section 4: Adaptive Memory](04-adaptive-memory.md) for the deep dive into Friday's memory system.*
