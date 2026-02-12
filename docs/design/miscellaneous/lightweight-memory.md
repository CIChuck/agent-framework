# Design: Lightweight Memory Configurations

**Status:** Exploratory
**Context:** Enabling "Scratchpad" agents and reducing overhead for simple workflows.

## 1. The Need for Lightweight Memory

Not all agents need the full weight of the Friday Memory System (Vector + Graph + Episodic).
*   **Scratchpad Agents:** Short-lived tasks where long-term retention is noise.
*   **Simple Tools:** CLI utilities that just need conversation history.
*   **Performance:** Avoiding embedding API calls and database IO for trivial interactions.

## 2. Architecture: "Scalable Adapters"

Instead of "Null" (No-op) adapters which paint us into a corner, we implement **Lightweight In-Memory Adapters**. This preserves functionality (agents can still use semantic search) without the operational overhead of heavy databases (ChromaDB/persistence).

### 2.1 SimpleVectorStore (The "Lite" Option)
Implements `VectorStoreAdapter` using in-memory structures.
*   **Storage:** A Python list `[{embedding: ..., text: ...}]`.
*   **Search:** Computes cosine similarity using `numpy` or pure Python.
*   **Pros:** Fast start-up, zero external dependencies, fully functional semantic search for small datasets (< 1000 items).
*   **Use Case:** Agent Scratchpads, Orchestrator Task State.

### 2.2 VolatileGraphStore
Implements `GraphStoreAdapter` using `networkx` but disables disk persistence.
*   **Storage:** In-memory `DiGraph`.
*   **Pros:** Full graph traversal capability, zero disk I/O.

## 3. Implementation Strategy

### 3.1 New Components
Create `packages/friday-memory/src/friday_memory/adapters/simple.py`:

```python
class SimpleVectorStore(VectorStoreAdapter):
    def __init__(self, embedding_model):
        self.docs = []
        self.model = embedding_model

    async def add_documents(self, texts, metadatas, ids):
        embeddings = await self.model.embed_documents(texts)
        # Store in self.docs
        
    async def query(self, query_text, n_results, ...):
        q_embed = await self.model.embed_query(query_text)
        # Scan self.docs, compute similarity, return top N
```

### 3.2 Container Integration
Update `FridayContainer` to support a `memory_profile`.

```python
class FridayContainer:
    async def _create_storage_adapters(self) -> None:
        match self.config.memory_profile:
            case "persistent":
                self._vector_store = ChromaVectorStore(...)
            case "ephemeral":
                self._vector_store = SimpleVectorStore(...)
            case "none":
                # Only for strict turn-history agents
                self._vector_store = NoOpVectorStore()
```

## 4. Evolution & Scaling

This approach prevents the "Null Trap".
*   **Start:** An agent starts with `SimpleVectorStore`.
*   **Grow:** If the agent's task is long-running, we can seamlessly swap the adapter implementation to `ChromaVectorStore` in the Container configuration. The Agent code (`MemoryController`) remains untouched.

## 5. Use Cases

1.  **The "Coder" Agent:**
    *   Needs to remember the file it just read (Episodic).
    *   Doesn't need to recall "Bob's favorite color" (Graph).
    *   *Config:* `memory_mode="episodic_only"`.

2.  **The "Researcher" Agent:**
    *   Needs massive storage for web pages (Vector).
    *   Needs history (Episodic).
    *   Graph might be overkill.
    *   *Config:* `memory_mode="vector_only"`.

3.  **The "Orchestrator":**
    *   Needs full context to route tasks intelligently.
    *   *Config:* `memory_mode="full"`.
