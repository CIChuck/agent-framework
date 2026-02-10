# Scalable Adapters Build Plan

**Status:** Planning
**Target:** Phase 1, Section 2.2 of Project Hive Master Plan
**Objective:** Implement lightweight memory adapters for ephemeral, testing, and edge deployments

---

## 1. Problem Statement

Friday currently requires ChromaDB and NetworkX for all deployments. This creates barriers for:
- **Ephemeral agents**: Short-lived agents that don't need persistent storage
- **Testing**: Unit tests require full database setup
- **Edge deployments**: Resource-constrained environments can't run heavy dependencies
- **Rapid prototyping**: Quick experiments shouldn't require database configuration

We need simpler alternatives that implement the same protocols without external dependencies.

---

## 2. Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Memory Profile System                     │
├─────────────────────────────────────────────────────────────┤
│  MemoryProfile.FULL       → ChromaDB + NetworkX (default)   │
│  MemoryProfile.EPHEMERAL  → SimpleVectorStore + NullGraph   │
│  MemoryProfile.VECTOR_ONLY→ ChromaDB + NullGraph            │
│  MemoryProfile.TESTING    → SimpleVectorStore + NullGraph   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Protocol Implementations                  │
├────────────────────────────┬────────────────────────────────┤
│     VectorStoreAdapter     │      GraphStoreAdapter         │
├────────────────────────────┼────────────────────────────────┤
│  ChromaVectorStore (full)  │  ElementXGraphStore (full)     │
│  SimpleVectorStore (light) │  NullGraphStore (no-op)        │
└────────────────────────────┴────────────────────────────────┘
```

### 2.2 Design Principles

1. **Protocol Compliance**: All adapters implement `friday-core` protocols exactly
2. **Zero External Dependencies**: Lightweight adapters use only stdlib + numpy
3. **Drop-in Replacement**: Switching profiles requires no code changes
4. **Semantic Equivalence**: Same API behavior, different storage backends

---

## 3. Implementation

### 3.1 SimpleVectorStore (In-Memory)

**Location:** `packages/friday-memory/src/friday_memory/adapters/simple_vector.py`

**Interface:** Implements `VectorStoreAdapter` protocol from `friday-core/interfaces/memory.py`

```python
"""In-memory vector store for ephemeral and testing scenarios."""

import asyncio
import uuid
from typing import Any

import numpy as np

from friday_core.interfaces.memory import VectorStoreAdapter


class VectorDocument:
    """Internal document representation."""

    def __init__(
        self,
        id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ):
        self.id = id
        self.text = text
        self.embedding = np.array(embedding)
        self.metadata = metadata or {}


class SimpleVectorStore(VectorStoreAdapter):
    """
    In-memory vector store using numpy for similarity search.

    Features:
    - Cosine similarity search
    - Metadata filtering
    - Thread-safe with asyncio.Lock
    - No persistence (ephemeral by design)

    Use Cases:
    - Unit testing without ChromaDB
    - Ephemeral agent sessions
    - Resource-constrained deployments
    - Rapid prototyping
    """

    def __init__(self, embedding_model: "EmbeddingModel"):
        """
        Initialize in-memory vector store.

        Args:
            embedding_model: Model for generating embeddings
        """
        self._embedding_model = embedding_model
        self._documents: dict[str, VectorDocument] = {}
        self._lock = asyncio.Lock()

    async def add_documents(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> list[str]:
        """
        Add documents to the store.

        Args:
            texts: Document texts to add
            metadatas: Optional metadata for each document
            ids: Optional IDs (generated if not provided)

        Returns:
            List of document IDs
        """
        async with self._lock:
            # Generate IDs if not provided
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in texts]

            # Normalize metadatas
            if metadatas is None:
                metadatas = [{} for _ in texts]

            # Generate embeddings
            embeddings = await self._embedding_model.embed_batch(texts)

            # Store documents
            for i, (text, embedding, metadata, doc_id) in enumerate(
                zip(texts, embeddings, metadatas, ids)
            ):
                self._documents[doc_id] = VectorDocument(
                    id=doc_id,
                    text=text,
                    embedding=embedding,
                    metadata=metadata,
                )

            return ids

    async def query(
        self,
        query_text: str,
        n_results: int = 10,
        where: dict[str, Any] | None = None,
        rerank: bool = False,
        hybrid: bool = False,
    ) -> list["QueryResult"]:
        """
        Query for similar documents.

        Args:
            query_text: Query text
            n_results: Maximum results to return
            where: Metadata filter conditions
            rerank: Ignored (no reranking in simple store)
            hybrid: Ignored (no hybrid search in simple store)

        Returns:
            List of QueryResult ordered by similarity
        """
        from friday_memory.models.vector import QueryResult

        if not self._documents:
            return []

        # Generate query embedding
        query_embedding = await self._embedding_model.embed(query_text)
        query_vec = np.array(query_embedding)

        # Calculate similarities
        results = []
        for doc in self._documents.values():
            # Apply metadata filter
            if where and not self._matches_filter(doc.metadata, where):
                continue

            # Cosine similarity
            similarity = self._cosine_similarity(query_vec, doc.embedding)

            results.append(
                QueryResult(
                    id=doc.id,
                    text=doc.text,
                    score=float(similarity),
                    metadata=doc.metadata,
                )
            )

        # Sort by similarity (descending) and limit
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:n_results]

    async def delete(self, ids: list[str]) -> None:
        """Delete documents by ID."""
        async with self._lock:
            for doc_id in ids:
                self._documents.pop(doc_id, None)

    async def delete_where(self, where: dict[str, Any]) -> int:
        """
        Delete documents matching filter.

        Returns:
            Number of documents deleted
        """
        async with self._lock:
            to_delete = [
                doc_id
                for doc_id, doc in self._documents.items()
                if self._matches_filter(doc.metadata, where)
            ]
            for doc_id in to_delete:
                del self._documents[doc_id]
            return len(to_delete)

    async def count(self) -> int:
        """Return total document count."""
        return len(self._documents)

    async def get(self, ids: list[str]) -> list["VectorDocument"]:
        """Get documents by ID."""
        from friday_memory.models.vector import VectorDocument as VecDoc

        results = []
        for doc_id in ids:
            if doc_id in self._documents:
                doc = self._documents[doc_id]
                results.append(
                    VecDoc(
                        id=doc.id,
                        text=doc.text,
                        metadata=doc.metadata,
                    )
                )
        return results

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def _matches_filter(
        self,
        metadata: dict[str, Any],
        where: dict[str, Any],
    ) -> bool:
        """
        Check if metadata matches filter conditions.

        Supports simple equality matching.
        """
        for key, value in where.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False
        return True

    async def clear(self) -> None:
        """Clear all documents."""
        async with self._lock:
            self._documents.clear()
```

### 3.2 NullGraphStore (No-Op)

**Location:** `packages/friday-memory/src/friday_memory/adapters/null_graph.py`

**Interface:** Implements `GraphStoreAdapter` protocol from `friday-core/interfaces/memory.py`

```python
"""No-op graph store for vector-only and testing scenarios."""

from typing import Any

from friday_core.interfaces.memory import GraphStoreAdapter
from friday_memory.models.graph import GraphNode, GraphEdge


class NullGraphStore(GraphStoreAdapter):
    """
    No-op graph store that accepts but discards all data.

    All write operations succeed silently.
    All read operations return empty results.

    Use Cases:
    - Vector-only deployments
    - Testing without graph complexity
    - Minimal memory footprint scenarios
    - Agents that don't need relationship tracking
    """

    async def add_node(self, node: GraphNode) -> str:
        """Accept node but don't store it."""
        return node.id

    async def add_nodes(self, nodes: list[GraphNode]) -> list[str]:
        """Accept nodes but don't store them."""
        return [n.id for n in nodes]

    async def get_node(self, node_id: str) -> GraphNode | None:
        """Always returns None (no storage)."""
        return None

    async def get_nodes(self, node_ids: list[str]) -> list[GraphNode]:
        """Always returns empty list."""
        return []

    async def update_node(self, node: GraphNode) -> bool:
        """Accept update but do nothing."""
        return True

    async def delete_node(self, node_id: str) -> bool:
        """Accept delete but do nothing."""
        return True

    async def add_edge(self, edge: GraphEdge) -> str:
        """Accept edge but don't store it."""
        return f"{edge.source_id}->{edge.target_id}"

    async def add_edges(self, edges: list[GraphEdge]) -> list[str]:
        """Accept edges but don't store them."""
        return [f"{e.source_id}->{e.target_id}" for e in edges]

    async def get_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str | None = None,
    ) -> GraphEdge | None:
        """Always returns None."""
        return None

    async def get_edges(
        self,
        node_id: str,
        direction: str = "both",
        edge_type: str | None = None,
    ) -> list[GraphEdge]:
        """Always returns empty list."""
        return []

    async def delete_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str | None = None,
    ) -> bool:
        """Accept delete but do nothing."""
        return True

    async def get_neighbors(
        self,
        node_id: str,
        depth: int = 1,
        edge_types: list[str] | None = None,
    ) -> list[GraphNode]:
        """Always returns empty list."""
        return []

    async def fuzzy_search(
        self,
        query: str,
        node_type: str | None = None,
        threshold: float = 0.8,
        limit: int = 10,
    ) -> list[GraphNode]:
        """Always returns empty list."""
        return []

    async def get_subgraph(
        self,
        node_ids: list[str],
        depth: int = 1,
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        """Always returns empty graph."""
        return [], []

    async def count_nodes(self, node_type: str | None = None) -> int:
        """Always returns 0."""
        return 0

    async def count_edges(self, edge_type: str | None = None) -> int:
        """Always returns 0."""
        return 0

    async def clear(self) -> None:
        """No-op (nothing to clear)."""
        pass

    async def increment_hit_count(self, node_id: str) -> int:
        """Accept but return 0."""
        return 0

    async def get_by_hit_count(
        self,
        min_hits: int = 1,
        limit: int = 100,
    ) -> list[GraphNode]:
        """Always returns empty list."""
        return []
```

### 3.3 Memory Profile System

**Location:** `apps/friday-cli/src/friday_cli/profiles.py` (new file)

```python
"""Memory profile configuration for different deployment scenarios."""

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from friday_core.interfaces.memory import (
        VectorStoreAdapter,
        GraphStoreAdapter,
        EmbeddingModel,
    )


class MemoryProfile(str, Enum):
    """
    Predefined memory configurations for different scenarios.

    Profiles:
        FULL: ChromaDB + NetworkX (default, full persistence)
        EPHEMERAL: SimpleVectorStore + NullGraphStore (no persistence)
        VECTOR_ONLY: ChromaDB + NullGraphStore (vector persistence only)
        TESTING: SimpleVectorStore + NullGraphStore (fast unit tests)
    """

    FULL = "full"
    EPHEMERAL = "ephemeral"
    VECTOR_ONLY = "vector"
    TESTING = "testing"

    @classmethod
    def from_string(cls, value: str) -> "MemoryProfile":
        """Parse profile from string, defaulting to FULL."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.FULL


def create_vector_store(
    profile: MemoryProfile,
    embedding_model: "EmbeddingModel",
    persist_dir: str | None = None,
    collection_name: str = "friday_vectors",
) -> "VectorStoreAdapter":
    """
    Create vector store based on profile.

    Args:
        profile: Memory profile
        embedding_model: Embedding model for vectors
        persist_dir: Directory for persistent storage (FULL/VECTOR_ONLY)
        collection_name: Collection name for persistent storage

    Returns:
        Configured VectorStoreAdapter
    """
    if profile in (MemoryProfile.EPHEMERAL, MemoryProfile.TESTING):
        from friday_memory.adapters.simple_vector import SimpleVectorStore

        return SimpleVectorStore(embedding_model)
    else:
        from friday_memory.adapters.vector import ChromaVectorStore

        return ChromaVectorStore(
            embedding_model=embedding_model,
            persist_directory=persist_dir,
            collection_name=collection_name,
        )


def create_graph_store(
    profile: MemoryProfile,
    persist_path: str | None = None,
) -> "GraphStoreAdapter":
    """
    Create graph store based on profile.

    Args:
        profile: Memory profile
        persist_path: Path for persistent storage (FULL only)

    Returns:
        Configured GraphStoreAdapter
    """
    if profile in (
        MemoryProfile.EPHEMERAL,
        MemoryProfile.VECTOR_ONLY,
        MemoryProfile.TESTING,
    ):
        from friday_memory.adapters.null_graph import NullGraphStore

        return NullGraphStore()
    else:
        from friday_memory.adapters.graph import ElementXGraphStore

        return ElementXGraphStore(persist_path=persist_path)
```

### 3.4 FridayContainer Updates

**Location:** `apps/friday-cli/src/friday_cli/container.py`

Add memory profile support to container:

```python
# Add to imports
from friday_cli.profiles import (
    MemoryProfile,
    create_vector_store,
    create_graph_store,
)

# Update FridayContainer.__init__
class FridayContainer:
    def __init__(
        self,
        config: FridayConfig,
        memory_profile: MemoryProfile = MemoryProfile.FULL,
    ):
        self._config = config
        self._memory_profile = memory_profile
        # ... rest of initialization

    @property
    def memory_profile(self) -> MemoryProfile:
        """Current memory profile."""
        return self._memory_profile

    @property
    def vector_store(self) -> VectorStoreAdapter:
        """Get or create vector store based on profile."""
        if self._vector_store is None:
            self._vector_store = create_vector_store(
                profile=self._memory_profile,
                embedding_model=self.embeddings,
                persist_dir=self._config.vector_persist_dir,
                collection_name=self._config.vector_collection,
            )
        return self._vector_store

    @property
    def graph_store(self) -> GraphStoreAdapter:
        """Get or create graph store based on profile."""
        if self._graph_store is None:
            self._graph_store = create_graph_store(
                profile=self._memory_profile,
                persist_path=self._config.graph_persist_path,
            )
        return self._graph_store
```

### 3.5 CLI Argument

**Location:** `apps/friday-cli/src/friday_cli/main.py`

Add `--memory-profile` argument:

```python
import argparse
from friday_cli.profiles import MemoryProfile

def parse_args():
    parser = argparse.ArgumentParser(description="Friday CLI")
    parser.add_argument(
        "--memory-profile",
        type=str,
        choices=["full", "ephemeral", "vector", "testing"],
        default="full",
        help="Memory profile: full (default), ephemeral, vector, or testing",
    )
    # ... other arguments
    return parser.parse_args()

def main():
    args = parse_args()
    profile = MemoryProfile.from_string(args.memory_profile)
    container = FridayContainer(config, memory_profile=profile)
    # ...
```

---

## 4. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `packages/friday-memory/src/friday_memory/adapters/simple_vector.py` | Create | In-memory vector store |
| `packages/friday-memory/src/friday_memory/adapters/null_graph.py` | Create | No-op graph store |
| `packages/friday-memory/src/friday_memory/adapters/__init__.py` | Modify | Export new adapters |
| `apps/friday-cli/src/friday_cli/profiles.py` | Create | MemoryProfile enum and factory functions |
| `apps/friday-cli/src/friday_cli/container.py` | Modify | Add memory_profile parameter and property |
| `apps/friday-cli/src/friday_cli/main.py` | Modify | Add --memory-profile CLI argument |
| `packages/friday-memory/tests_memory/test_simple_vector.py` | Create | Unit tests for SimpleVectorStore |
| `packages/friday-memory/tests_memory/test_null_graph.py` | Create | Unit tests for NullGraphStore |

---

## 5. Dependencies

### 5.1 Required (Already in project)
- `numpy` - For cosine similarity calculation

### 5.2 No New Dependencies
The lightweight adapters intentionally avoid adding new dependencies.

---

## 6. Verification

### 6.1 Unit Tests

```bash
# Test SimpleVectorStore
pytest packages/friday-memory/tests_memory/test_simple_vector.py -v

# Test NullGraphStore
pytest packages/friday-memory/tests_memory/test_null_graph.py -v
```

### 6.2 Integration Test

```bash
# Start with ephemeral profile (no ChromaDB required)
memory-chat-v2 --memory-profile=ephemeral

# Verify it starts without database files
# Verify basic conversation works
# Verify vector search returns results
# Verify graph queries return empty (expected)
```

### 6.3 Regression Test

```bash
# Verify default profile still works
memory-chat-v2  # Should use full profile

# Verify existing tests pass
pytest tests/integration/memory/ -v
```

---

## 7. Exit Criteria

1. `SimpleVectorStore` implements `VectorStoreAdapter` protocol completely
2. `NullGraphStore` implements `GraphStoreAdapter` protocol completely
3. `memory-chat-v2 --memory-profile=ephemeral` starts without ChromaDB
4. All existing tests pass with default (full) profile
5. New unit tests achieve 90%+ coverage
