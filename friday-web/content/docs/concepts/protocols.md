---
title: "Protocol-First Design"
description: "Abstract protocols that let you swap any component without lock-in."
weight: 3
---

Friday defines abstract protocols for every major component so you can swap LLM providers, storage backends, or tool registries without changing application code.

---

## The Problem: Vendor Lock-In

Most AI frameworks suffer from **tight coupling**—if you start with OpenAI, migrating to Anthropic requires code rewrites. If you use Pinecone, switching to Weaviate means architectural changes. This creates strategic risk: you're dependent on vendor pricing, availability, and feature decisions.

Friday solves this with **protocol-first design**: every major component is defined as an abstract interface (protocol), with implementations being swappable modules.

---

## How Protocols Work

Think of protocols as **contracts**. A protocol says "any component implementing me must provide these methods with these signatures." Implementations can vary—ChromaDB, Pinecone, or a custom database—but they all satisfy the same contract.

### Example: The VectorStoreAdapter Protocol

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

---

## Friday's Core Protocols

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

---

## Real-World Example: Swapping Vector Stores

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

That's it. The rest of your Friday agent code is unchanged. `MemoryController` doesn't care—it just uses the `VectorStoreAdapter` protocol.

---

## Implementing Custom Protocols

You can bring your own implementations for any protocol. Here's a minimal example using PostgreSQL + pgvector:

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
        self.conn.commit()

    async def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        """Implement VectorStoreAdapter.add_documents."""
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
            """, (query_embedding[0], query_embedding[0], threshold,
                  query_embedding[0], limit))

            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "metadata": json.loads(row[2]),
                    "similarity": row[3],
                })
            return results
```

**Now use it with Friday:**

```python
vector_store = PostgresVectorStore("postgresql://localhost/friday")
controller = MemoryController(
    vector_store=vector_store,  # Works because it implements the protocol
    graph_store=graph_store,
    transcript_store=transcript_store,
)
```

---

## Benefits: Strategic & Tactical

**No vendor lock-in:** Preserve optionality as technology landscape evolves. If a vendor raises prices or sunsets a product, you can migrate.

**Gradual migration:** Swap components one at a time, validate in stages.

**Multi-cloud strategy:** Use different providers in different regions/environments.

**Compliance flexibility:** Route sensitive data to approved storage (on-prem PostgreSQL) while using cloud for general data (Pinecone).

**Cost optimization:** Mix free/cheap providers (Ollama, ChromaDB) with premium services where justified.

**Technology experimentation:** Try new vector databases without rewriting agents.

**Local development:** Use lightweight local stores (SQLite, ChromaDB) in development, production stores (Postgres, Pinecone) in staging/prod.

**Testing:** Mock protocols for fast unit tests without external dependencies.

---

## friday-core: The Protocol Package

All protocols live in `friday-core/interfaces/`:

```python
from friday_core import TelemetryRecorder, DebugTelemetryRecorder
from friday_core.interfaces import VectorStoreAdapter

# Use the debug recorder for development
telemetry = DebugTelemetryRecorder()

# All adapters implement the protocol
class MyCustomVectorStore(VectorStoreAdapter):
    async def similarity_search(self, query: str, limit: int) -> list[dict]:
        ...
```

**Every other Friday package depends on `friday-core`.** This is what makes swappability possible at every layer—the protocols are defined once, implemented many times, and consumed everywhere.
