"""
Memory profile configuration for different deployment scenarios.

Provides factory functions to create appropriate storage adapters
based on deployment profile requirements. Moved from friday-cli
to friday-core to enable use by friday-runtime without circular
dependency.

Ref: Phase 1 - Scalable Adapters Build Plan
"""

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from friday_core.interfaces.memory import (
        GraphStoreAdapter,
        VectorStoreAdapter,
    )
    from friday_core.interfaces import EmbeddingModel


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
        """
        Parse profile from string, defaulting to FULL.

        Args:
            value: Profile name (case-insensitive)

        Returns:
            Matching MemoryProfile, or FULL if not found
        """
        try:
            return cls(value.lower())
        except ValueError:
            return cls.FULL


def create_vector_store(
    profile: MemoryProfile,
    embedding_function: "EmbeddingModel",
    path: str | None = None,
    collection_name: str = "friday_memory",
) -> "VectorStoreAdapter":
    """
    Create vector store based on profile.

    Args:
        profile: Memory profile determining store type
        embedding_function: Embedding model for vectors
        path: Directory for persistent storage (FULL/VECTOR_ONLY)
        collection_name: Collection name for persistent storage

    Returns:
        Configured VectorStoreAdapter instance
    """
    if profile in (MemoryProfile.EPHEMERAL, MemoryProfile.TESTING):
        from friday_memory.adapters.simple_vector import SimpleVectorStore

        return SimpleVectorStore(embedding_function=embedding_function)
    else:
        # FULL or VECTOR_ONLY - use ChromaDB
        from friday_memory.adapters.vector import ChromaVectorStore

        return ChromaVectorStore(
            collection_name=collection_name,
            embedding_function=embedding_function,
            path=path,
        )


def create_graph_store(
    profile: MemoryProfile,
    storage_path: str | None = None,
) -> "GraphStoreAdapter":
    """
    Create graph store based on profile.

    Args:
        profile: Memory profile determining store type
        storage_path: Path for persistent storage (FULL only)

    Returns:
        Configured GraphStoreAdapter instance
    """
    if profile in (
        MemoryProfile.EPHEMERAL,
        MemoryProfile.VECTOR_ONLY,
        MemoryProfile.TESTING,
    ):
        from friday_memory.adapters.null_graph import NullGraphStore

        return NullGraphStore()
    else:
        # FULL - use NetworkX-based graph store
        from friday_memory.adapters.graph import ElementXGraphStore

        return ElementXGraphStore(storage_path=storage_path)
