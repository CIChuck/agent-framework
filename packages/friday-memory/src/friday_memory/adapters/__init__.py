# mypy: ignore-errors
"""
Concrete implementations of Storage Adapters.

These classes implement the abstract protocols defined in friday-core:
- InMemoryEpisodicStore: In-memory episodic store (EpisodicStoreAdapter)
- ElementXGraphStore: NetworkX-based graph store (GraphStoreAdapter)
- ChromaVectorStore: ChromaDB-based vector store (VectorStoreAdapter)
- SimpleVectorStore: In-memory vector store for ephemeral/testing (VectorStoreAdapter)
- NullGraphStore: No-op graph store for vector-only deployments (GraphStoreAdapter)
"""

from friday_memory.adapters.episodic import InMemoryEpisodicStore
from friday_memory.adapters.graph import ElementXGraphStore
from friday_memory.adapters.null_graph import NullGraphStore
from friday_memory.adapters.simple_vector import SimpleVectorStore
from friday_memory.adapters.vector import ChromaVectorStore

__all__ = [
    "InMemoryEpisodicStore",
    "ElementXGraphStore",
    "ChromaVectorStore",
    "SimpleVectorStore",
    "NullGraphStore",
]
