"""
Shared Protocol Definitions.

This module exports all abstract base classes (protocols) that define
the contracts for swappable components in the Friday Framework.

Storage Adapters (Batch 1):
- EpisodicStoreAdapter: Short-term conversation history
- VectorStoreAdapter: Semantic search storage
- GraphStoreAdapter: Relationship graph storage

Context Engineering (Batch 2a):
- ContextEngineeringInterface: Context strategy lifecycle
"""

from friday_core.interfaces.context import ContextEngineeringInterface
from friday_core.interfaces.memory import (
    EpisodicStoreAdapter,
    GraphStoreAdapter,
    VectorStoreAdapter,
)

__all__ = [
    # Storage Adapters
    "EpisodicStoreAdapter",
    "VectorStoreAdapter",
    "GraphStoreAdapter",
    # Context Engineering
    "ContextEngineeringInterface",
]
