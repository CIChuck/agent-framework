# Friday Memory - Developer Guide

**Version:** 0.1.0
**Audience:** Developers and Architects
**Last Updated:** December 2024

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Dependencies](#installation--dependencies)
4. [Core Concepts](#core-concepts)
5. [API Reference](#api-reference)
6. [Integration Guide](#integration-guide)
7. [Best Practices](#best-practices)

---

## Overview

`friday-memory` is a context engineering library for building LLM-powered agents with persistent, structured memory. It provides a tri-store architecture (episodic, semantic, associative) with intelligent retrieval, token budgeting, and memory consolidation.

### Key Capabilities

- **Multi-store Memory**: Conversation history, vector embeddings, and knowledge graphs
- **Unified Retrieval**: Single `recall()` method queries all stores in parallel
- **Token Budgeting**: Knapsack algorithm for optimal context window utilization
- **Memory Consolidation**: Automatic deduplication, summarization, and conflict resolution
- **Provenance Tracking**: Full lineage metadata for all stored information
- **Hebbian Learning**: Access-frequency reinforcement for graph entities

### Package Structure

```
friday-memory/
├── src/friday_memory/
│   ├── models/           # Data transfer objects (DTOs)
│   ├── adapters/         # Storage implementations
│   ├── controller/       # Orchestration facade
│   ├── context/          # Context engineering pipeline
│   └── ingestion/        # Document processing
├── tests/
├── examples/
└── docs/
```

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                           │
│              (Your Agent / Chat Application)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ContextAssembler                               │
│  Orchestrates the complete context engineering lifecycle        │
│  ├─ initialize_session()    Session management                  │
│  ├─ extract_context()       Triggers MemoryExtractor            │
│  ├─ consolidate_memory()    Triggers MemoryConsolidator         │
│  ├─ assemble_context()      Token-budgeted retrieval            │
│  └─ format_prompt()         Delegates to PromptArchitect        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MemoryController                              │
│  Unified facade for all memory operations                       │
│  ├─ recall()             Parallel multi-store retrieval         │
│  ├─ store_fact()         Write to graph store                   │
│  ├─ store_insight()      Write to vector store                  │
│  └─ add_turn()           Write to episodic store                │
└───────────┬───────────────────┬───────────────────┬─────────────┘
            │                   │                   │
            ▼                   ▼                   ▼
┌───────────────────┐  ┌────────────────┐  ┌──────────────────┐
│   VectorStore     │  │   GraphStore   │  │  EpisodicStore   │
│   (ChromaDB)      │  │  (NetworkX)    │  │  (In-Memory)     │
│                   │  │                │  │                  │
│ Semantic search   │  │ Entity/relation│  │ Conversation     │
│ via embeddings    │  │ knowledge base │  │ history          │
└───────────────────┘  └────────────────┘  └──────────────────┘
```

### Data Flow

```
                    INGESTION                         RETRIEVAL
                    ─────────                         ─────────
                        │                                 │
   Documents ──────────►│                                 │◄────── User Query
                        │                                 │
                        ▼                                 ▼
┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│  DocumentIngestionPipeline      │    │  MemoryController.recall()      │
│  - Chunk text                   │    │  - Query episodic (history)     │
│  - Attach provenance            │    │  - Query vector (semantic)      │
│  - Prepare for vector store     │    │  - Query graph (associative)    │
└─────────────┬───────────────────┘    └─────────────┬───────────────────┘
              │                                      │
              ▼                                      ▼
┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│  VectorStore.add_documents()    │    │  ContextPayload                 │
│  - Embed via LiteLLM            │    │  - history: []                  │
│  - Store in ChromaDB            │    │  - passages: []                 │
└─────────────────────────────────┘    │  - entities: []                 │
                                       │  - facts: []                    │
                                       └─────────────┬───────────────────┘
                                                     │
     EXTRACTION                                      ▼
     ──────────                        ┌─────────────────────────────────┐
         │                             │  PromptArchitect.format_prompt()│
         │◄────── InteractionTurn      │  - Apply token budget           │
         │                             │  - Arrange for attention        │
         ▼                             │  - Output OpenAI messages       │
┌─────────────────────────────────┐    └─────────────────────────────────┘
│  MemoryExtractor.extract()      │
│  - LLM-based entity extraction  │
│  - Fact identification          │
│  - Relationship discovery       │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  Store to Graph + Vector        │
│  - GraphNode (entities)         │
│  - GraphEdge (relationships)    │
│  - Vector (summaries)           │
└─────────────────────────────────┘
```

### Third-Party Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `friday-core` | workspace | Abstract interfaces, telemetry |
| `chromadb` | latest | Vector database for semantic search |
| `networkx` | latest | Graph library for knowledge graph |
| `litellm` | latest | LLM abstraction (embeddings, completions) |
| `tiktoken` | latest | Token counting for context budgeting |
| `numpy` | latest | Numerical operations |
| `pydantic` | >=2.0 | Data validation and serialization |

---

## Installation & Dependencies

### From Workspace (Development)

```bash
# Clone the repository
git clone <repo-url>
cd agent-framework

# Install with uv
uv sync

# Or install specific packages
uv pip install -e packages/friday-core -e packages/friday-memory
```

### Dependencies in pyproject.toml

```toml
[project]
dependencies = [
    "friday-core",
    "chromadb",
    "networkx",
    "litellm",
    "numpy",
    "tiktoken",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]
```

---

## Core Concepts

### 1. Tri-Store Architecture

Friday Memory uses three complementary storage systems:

| Store | Type | Purpose | Implementation |
|-------|------|---------|----------------|
| **Episodic** | Temporal | Conversation history, turn-by-turn | `InMemoryEpisodicStore` |
| **Semantic** | Vector | Document chunks, summaries | `ChromaVectorStore` |
| **Associative** | Graph | Entities, relationships, facts | `ElementXGraphStore` |

### 2. Provenance Tracking

Every piece of stored data requires provenance metadata:

```python
from friday_memory import ProvenanceMetadata

provenance = ProvenanceMetadata(
    source_id="doc_abc123",           # Origin UUID
    source_type="document",            # 'interaction', 'document', 'inference'
    confidence=0.95,                   # 0.0-1.0 confidence score
    author_id="ingestion_pipeline"     # Creator identifier
)
```

This enables:
- **Auditing**: Track where information came from
- **Conflict Resolution**: Compare timestamps and sources
- **Trust Scoring**: Weight results by confidence

### 3. Hebbian Learning

Graph nodes implement "neurons that fire together, wire together":

```python
node = GraphNode(
    id="entity_alice",
    type="Person",
    label="Alice",
    properties={"role": "engineer"},
    provenance=provenance,
    hit_count=0,           # Access frequency
    last_accessed=datetime.now()
)

# Each time the node is retrieved:
node.touch()  # Increments hit_count, updates last_accessed
```

High `hit_count` nodes are prioritized in retrieval and protected during token budgeting.

### 4. Token Budgeting (Knapsack Algorithm)

Context assembly uses a priority hierarchy:

```
Priority (lowest to highest):
─────────────────────────────
1. Deep history (turns 10+)      → Dropped first
2. Weak matches (similarity<0.5) → Dropped second
3. Recent history (turns 3-10)   → Dropped if needed
4. Last 2 turns, user: vars      → PROTECTED (never dropped)
```

The assembler calculates:
- **Fixed Cost**: System prompt + tools + output buffer
- **Dynamic Limit**: Model max tokens - fixed cost
- **Budget**: What remains for retrieved context

### 5. Scoped Variables

Session state supports three-tier variable scoping:

```python
state = SessionState(session_id="...", user_id="...")

# User preferences (persist across sessions)
state.set_var("user:theme", "dark")
state.set_var("user:timezone", "America/New_York")

# Session-specific (cleared on session end)
state.set_var("session:current_task", "debugging")

# Global app config
state.set_var("app:version", "1.0.0")

# Retrieve variables
theme = state.get_var("user:theme")

# Clear session-specific variables
state.clear_session_vars()
```

### 6. Consolidation Cycle

Periodic maintenance to prevent context fragmentation:

1. **Fetch**: Get unconsolidated turns from episodic store
2. **Deduplicate**: Merge duplicate graph entities (fuzzy matching)
3. **Summarize**: Compress conversation history via LLM
4. **Resolve**: Handle contradictory facts with timestamps
5. **Mark**: Flag turns as consolidated (prevents re-extraction)

---

## API Reference

### Data Models

#### ProvenanceMetadata

Tracks lineage and origin of stored data.

```python
class ProvenanceMetadata(BaseModel):
    source_id: str              # UUID of originating document/turn
    source_type: str            # 'interaction', 'document', 'inference'
    confidence: float           # 0.0 to 1.0
    created_at: datetime        # Auto-populated
    author_id: str | None       # Creator identifier
```

#### GraphNode

Represents entities in the knowledge graph.

```python
class GraphNode(BaseModel):
    id: str                     # Unique identifier
    type: str                   # 'Entity', 'Concept', 'Event'
    label: str                  # Human-readable name
    properties: dict[str, Any]  # Flexible attributes
    provenance: ProvenanceMetadata
    hit_count: int = 0          # Access frequency (Hebbian)
    last_accessed: datetime

    def touch(self) -> None:
        """Increment hit_count for Hebbian learning."""
```

#### GraphEdge

Represents relationships between nodes.

```python
class GraphEdge(BaseModel):
    source_id: str              # Source node ID
    target_id: str              # Target node ID
    relation: str               # Relationship type (e.g., 'works_for')
    properties: dict[str, Any]  # Edge attributes
    provenance: ProvenanceMetadata
    weight: float = 1.0         # Edge weight for algorithms
```

#### InteractionTurn

Single conversation turn with tool tracking.

```python
class InteractionTurn(BaseModel):
    id: str
    session_id: str
    user_message: str | None
    assistant_message: str | None
    tool_calls: list[ToolCall]
    tool_results: list[ToolResult]
    metadata: dict[str, Any]
    timestamp: datetime
    consolidated: bool = False
```

#### SessionState

Session continuity and scoped variables.

```python
class SessionState(BaseModel):
    session_id: str
    user_id: str
    turn_count: int = 0
    start_time: datetime
    active_goals: list[str] = []
    scoped_vars: dict[str, Any] = {}

    def get_var(self, key: str, default: Any = None) -> Any
    def set_var(self, key: str, value: Any) -> None
    def delete_var(self, key: str) -> bool
    def clear_session_vars(self) -> int
    def increment_turn(self) -> int
```

#### ContextPayload

Container for retrieved context from all stores.

```python
class ContextPayload(BaseModel):
    history: list[InteractionTurn]      # Episodic memory
    passages: list[dict[str, Any]]      # Semantic memory (vector)
    entities: list[GraphNode]           # Associative memory (nodes)
    facts: list[GraphEdge]              # Associative memory (edges)
    recent_memories: list[str]          # Transparency block
    debug_info: dict[str, Any]

    def total_items(self) -> int
    def is_empty(self) -> bool
```

#### ConsolidationReport

Telemetry from consolidation cycles.

```python
class ConsolidationReport(BaseModel):
    session_id: str
    turns_processed: int
    nodes_created: int
    nodes_merged: int
    edges_created: int
    conflicts_resolved: int
    tokens_condensed: int
    errors: list[str]
    duration_ms: float
```

---

### Storage Adapters

#### InMemoryEpisodicStore

In-memory conversation history storage.

```python
from friday_memory import InMemoryEpisodicStore

store = InMemoryEpisodicStore()

# Add a turn
await store.add_turn(session_id, turn)

# Retrieve history
turns = await store.get_turns(session_id, limit=10, offset=0)

# Get unconsolidated turns
pending = await store.get_unconsolidated_turns(session_id)

# Mark as processed
await store.mark_consolidated([turn.id for turn in pending])

# Rewind history (delete turns after target)
await store.rewind_history(session_id, target_turn_id)

# Utility methods
sessions = await store.get_session_ids()
count = await store.get_turn_count(session_id)
await store.clear_session(session_id)
```

#### ChromaVectorStore

ChromaDB-based semantic search.

```python
from friday_memory import ChromaVectorStore

store = ChromaVectorStore(
    collection_name="my_collection",
    persist_directory="./chroma_db",      # None for ephemeral
    embedding_model="text-embedding-3-small",
    telemetry=telemetry                    # Optional
)

# Add documents
await store.add_documents(
    texts=["Document 1 content", "Document 2 content"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
)

# Semantic search
results = await store.query(
    query_text="search query",
    n_results=5,
    where={"source": "doc1"},  # Metadata filter
    rerank=False,
    hybrid=False
)
# Returns: [{"id", "text", "metadata", "similarity", "distance"}]

# Delete by ID or filter
await store.delete(["id1", "id2"])
deleted_count = await store.delete_where({"source": "old_docs"})

# Utility
count = await store.count()
doc = await store.get_by_id("id1")
```

#### ElementXGraphStore

NetworkX-based knowledge graph with persistence.

```python
from friday_memory import ElementXGraphStore

store = ElementXGraphStore(
    storage_path="./graph.gpickle",  # .gpickle or .json
    telemetry=telemetry               # Optional
)

# CRUD Operations
await store.add_node(node)
await store.add_edge(edge)
await store.remove_node(node_id)

# Traversal
neighbors = await store.get_neighbors(node_id, depth=2)
path = await store.find_path(start_id, end_id, max_depth=5)

# Maintenance
await store.merge_nodes(primary_id, secondary_id)  # Entity resolution

# Search & Ranking
matches = await store.fuzzy_search("alice", threshold=0.8)
ranked = await store.rank_nodes(algorithm="pagerank")  # or "hits"

# Utility
node = await store.get_node(node_id)
all_nodes = await store.get_all_nodes()
node_count = await store.node_count()
edge_count = await store.edge_count()
```

---

### MemoryController

Unified facade for all memory operations.

```python
from friday_memory import MemoryController

controller = MemoryController(
    vector_store=vector_store,
    graph_store=graph_store,
    episodic_store=episodic_store,
    telemetry=telemetry  # Optional
)

# Unified retrieval (queries all stores in parallel)
payload = await controller.recall(
    query="What do we know about the API?",
    session_id="session_123",
    token_limit=2000,
    include_history=True,
    history_limit=10,
    vector_results=5,
    graph_depth=1
)

# Store a fact (entity + optional relationship)
await controller.store_fact(node, edge)

# Store semantic insight
await controller.store_insight(
    text="Summary of the discussion...",
    metadata=provenance
)

# Episodic operations
await controller.add_turn(session_id, turn)
await controller.rewind_session(session_id, target_turn_id)

# Consolidation support
unconsolidated = await controller.fetch_unconsolidated_events(session_id)
await controller.mark_events_consolidated(event_ids)

# Entity resolution
await controller.merge_identities(primary_id, secondary_id)

# Direct store access
controller.vector    # VectorStoreAdapter
controller.graph     # GraphStoreAdapter
controller.episodic  # EpisodicStoreAdapter
```

---

### Context Engineering

#### MemoryExtractor

LLM-based extraction from conversation turns.

```python
from friday_memory import MemoryExtractor

extractor = MemoryExtractor(
    memory_controller=controller,
    extraction_model="gpt-4-turbo",
    telemetry=telemetry
)

# Full extraction (stores results automatically)
result = await extractor.extract(turn)
# Returns: {"extracted": {...}, "stats": {...}}

# Quick entity extraction
entities = await extractor.extract_entities_only("Alice works at Acme Corp")
# Returns: ["Alice", "Acme Corp"]
```

#### MemoryConsolidator

Memory maintenance and summarization.

```python
from friday_memory import MemoryConsolidator

consolidator = MemoryConsolidator(
    memory_controller=controller,
    consolidation_model="gpt-4-turbo",
    min_turns_to_consolidate=5,
    max_turns_per_summary=10,
    telemetry=telemetry
)

# Full consolidation cycle
report = await consolidator.consolidate(session_id)
print(f"Merged {report.nodes_merged} duplicate entities")

# Resolve conflicting facts
resolution = await consolidator.resolve_conflict(conflicting_facts)

# Get recent memories for transparency
memories = await consolidator.get_recent_memories(session_id, limit=5)
```

#### ContextAssembler

Orchestrator implementing `ContextEngineeringInterface`.

```python
from friday_memory import ContextAssembler

assembler = ContextAssembler(
    memory_controller=controller,
    prompt_architect=architect,  # Optional, created if not provided
    model_name="gpt-4",
    max_tokens=8192,
    telemetry=telemetry
)

# Session management
state = await assembler.initialize_session(session_id, user_id)
state = await assembler.restore_checkpoint(session_id, turn_id)

# Ingestion cycle
await assembler.extract_context(turn, async_execution=True)

# Maintenance cycle
report = await assembler.consolidate_memory(session_id)

# Retrieval cycle (with token budgeting)
payload = await assembler.assemble_context(query, state, budget_limit)

# Formatting cycle
messages = await assembler.format_prompt(system_prompt, payload)
```

#### PromptArchitect

Layout engine for optimal model attention.

```python
from friday_memory import PromptArchitect

architect = PromptArchitect(
    model_name="gpt-4",
    max_tokens=8192,
    output_buffer=1024
)

# Calculate token budget
fixed_cost = architect.calculate_fixed_costs(system_prompt, tool_definitions)
dynamic_limit = architect.calculate_dynamic_limit(system_prompt, tool_definitions)

# Format prompt with optimal layout
messages = architect.format_prompt(
    system_prompt=system_prompt,
    user_query=query,
    payload=payload,
    state=state,
    tool_definitions=tools
)

# Token counting
tokens = architect.count_tokens(text)
```

**Message Layout Order:**
1. System Block (identity & guardrails)
2. Transparency Block (recent auto-archived memories)
3. Semantic Memory (vector passages)
4. Associative Memory (entities and facts)
5. State Memory (scoped variables)
6. Episodic Memory (conversation history)
7. User Query

---

### Document Ingestion

#### DocumentIngestionPipeline

```python
from friday_memory import DocumentIngestionPipeline

pipeline = DocumentIngestionPipeline(
    chunk_size=500,      # Characters per chunk
    overlap=50,          # Overlap between chunks
    author_id="pipeline"
)

# Ingest text
doc = pipeline.ingest_text(
    text="Long document content...",
    source_id="doc_123",
    source_name="readme",
    additional_metadata={"category": "documentation"}
)

# Ingest file
doc = pipeline.ingest_file(
    path="./docs/guide.md",
    additional_metadata={"version": "1.0"}
)

# Prepare for vector store
texts, metadatas, ids = pipeline.prepare_for_vector_store(doc)
await vector_store.add_documents(texts, metadatas, ids)

# Supported file types
# .txt, .md, .py, .json, .yaml, .yml, .html, .css, .js, .ts
```

---

## Integration Guide

### Basic Setup

```python
import asyncio
from friday_memory import (
    InMemoryEpisodicStore,
    ChromaVectorStore,
    ElementXGraphStore,
    MemoryController,
    ContextAssembler,
    PromptArchitect,
)
from friday_core import DebugTelemetryRecorder

async def main():
    # 1. Initialize telemetry (optional but recommended)
    telemetry = DebugTelemetryRecorder()

    # 2. Create storage adapters
    episodic = InMemoryEpisodicStore()
    vector = ChromaVectorStore(
        collection_name="my_app",
        persist_directory="./data/chroma"
    )
    graph = ElementXGraphStore(
        storage_path="./data/graph.gpickle"
    )

    # 3. Create memory controller
    controller = MemoryController(
        vector_store=vector,
        graph_store=graph,
        episodic_store=episodic,
        telemetry=telemetry
    )

    # 4. Create context assembler
    assembler = ContextAssembler(
        memory_controller=controller,
        model_name="gpt-4",
        max_tokens=8192,
        telemetry=telemetry
    )

    # 5. Initialize session
    state = await assembler.initialize_session(
        session_id="session_001",
        user_id="user_123"
    )

    # 6. Store user preference
    state.set_var("user:name", "Alice")

    # Ready to use!
    return assembler, state

asyncio.run(main())
```

### Chat Application Integration

```python
async def handle_user_message(
    assembler: ContextAssembler,
    state: SessionState,
    user_message: str,
    system_prompt: str
) -> str:
    """Process a user message and generate response."""

    # 1. Assemble context with token budgeting
    architect = assembler._prompt_architect
    budget = architect.calculate_dynamic_limit(system_prompt)

    payload = await assembler.assemble_context(
        query=user_message,
        state=state,
        budget_limit=budget
    )

    # 2. Format prompt
    messages = await assembler.format_prompt(system_prompt, payload)

    # 3. Call LLM (using your preferred client)
    response = await llm_client.chat(messages=messages)
    assistant_message = response.content

    # 4. Record the turn
    turn = InteractionTurn(
        id=str(uuid.uuid4()),
        session_id=state.session_id,
        user_message=user_message,
        assistant_message=assistant_message,
        timestamp=datetime.now()
    )
    await assembler._memory_controller.add_turn(state.session_id, turn)

    # 5. Trigger async extraction
    await assembler.extract_context(turn, async_execution=True)

    # 6. Increment turn counter
    state.increment_turn()

    # 7. Periodic consolidation (every 10 turns)
    if state.turn_count % 10 == 0:
        report = await assembler.consolidate_memory(state.session_id)
        logger.info(f"Consolidated: {report.turns_processed} turns")

    return assistant_message
```

### Document Ingestion Workflow

```python
from pathlib import Path

async def ingest_knowledge_base(
    controller: MemoryController,
    docs_directory: str
):
    """Ingest all documents from a directory."""

    pipeline = DocumentIngestionPipeline(
        chunk_size=400,
        overlap=50,
        author_id="kb_ingestion"
    )

    supported = {".txt", ".md", ".py", ".json"}
    docs_path = Path(docs_directory)

    for file_path in docs_path.rglob("*"):
        if file_path.suffix in supported:
            try:
                # Ingest file
                doc = pipeline.ingest_file(
                    str(file_path),
                    additional_metadata={
                        "directory": str(file_path.parent),
                        "filename": file_path.name
                    }
                )

                # Store in vector database
                texts, metadatas, ids = pipeline.prepare_for_vector_store(doc)
                await controller.vector.add_documents(texts, metadatas, ids)

                print(f"Ingested {file_path.name}: {doc.total_chunks} chunks")

            except Exception as e:
                print(f"Failed to ingest {file_path}: {e}")
```

### Testing with Telemetry

```python
import pytest
from friday_core import DebugTelemetryRecorder

@pytest.fixture
def telemetry():
    return DebugTelemetryRecorder()

@pytest.fixture
async def memory_controller(telemetry):
    episodic = InMemoryEpisodicStore()
    vector = ChromaVectorStore(collection_name="test")
    graph = ElementXGraphStore()

    return MemoryController(
        vector_store=vector,
        graph_store=graph,
        episodic_store=episodic,
        telemetry=telemetry
    )

async def test_recall_captures_telemetry(memory_controller, telemetry):
    """Test that recall emits proper telemetry."""

    # Execute recall
    payload = await memory_controller.recall(
        query="test query",
        session_id="test_session"
    )

    # Assert on telemetry
    recall_span = telemetry.get_span_by_name("memory_recall")
    assert recall_span is not None
    assert recall_span.duration_ms > 0

    # Check events
    assert telemetry.get_event("recall_started") is not None
    assert telemetry.get_event("recall_completed") is not None
```

---

## Best Practices

### 1. Always Populate Provenance

```python
# Good
provenance = ProvenanceMetadata(
    source_id=str(uuid.uuid4()),
    source_type="document",
    confidence=0.95,
    author_id="ingestion_service"
)
node = GraphNode(..., provenance=provenance)

# Bad - will raise ValueError
node = GraphNode(..., provenance=None)
await controller.store_fact(node)  # Raises!
```

### 2. Use Scoped Variables Appropriately

```python
# User preferences (persist across sessions)
state.set_var("user:language", "en")

# Session state (cleared on new session)
state.set_var("session:draft_email", "...")

# App config (global)
state.set_var("app:feature_flags", {"new_ui": True})
```

### 3. Configure Token Budget

```python
# Calculate available budget BEFORE assembling context
architect = PromptArchitect(model_name="gpt-4", max_tokens=8192)

fixed = architect.calculate_fixed_costs(system_prompt, tools)
budget = architect.calculate_dynamic_limit(system_prompt, tools)

# Pass budget to assembly
payload = await assembler.assemble_context(query, state, budget_limit=budget)
```

### 4. Periodic Consolidation

```python
# Consolidate every N turns
if state.turn_count % 10 == 0:
    report = await assembler.consolidate_memory(session_id)

    if report.errors:
        logger.warning(f"Consolidation errors: {report.errors}")
```

### 5. Entity Resolution

```python
# When you detect duplicates
matches = await graph.fuzzy_search("Alice Smith", threshold=0.85)

if len(matches) > 1:
    # Keep the one with highest hit_count (Hebbian)
    primary = max(matches, key=lambda n: n.hit_count)
    for secondary in matches:
        if secondary.id != primary.id:
            await controller.merge_identities(primary.id, secondary.id)
```

### 6. Handle Empty Results

```python
payload = await controller.recall(query, session_id)

if payload.is_empty():
    # Fall back to just the query, no retrieved context
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
else:
    messages = architect.format_prompt(system_prompt, query, payload, state)
```

### 7. Telemetry for Debugging

```python
# In development
telemetry = DebugTelemetryRecorder()
controller = MemoryController(..., telemetry=telemetry)

# After operations
for span_id, span in telemetry.spans.items():
    print(f"{span.name}: {span.duration_ms:.2f}ms")

for event in telemetry.events:
    print(f"{event.name}: {event.data}")
```

---

## Further Resources

- **Examples**: `packages/friday-memory/examples/`
- **Tests**: `packages/friday-memory/tests_memory/`
- **Core Interfaces**: `packages/friday-core/src/friday_core/interfaces/`

---

*This guide is part of the Friday Framework documentation.*
