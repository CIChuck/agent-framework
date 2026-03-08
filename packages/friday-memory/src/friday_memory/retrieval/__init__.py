# mypy: ignore-errors
"""
Retrieval Module for Memory Lifecycle Management.

This module provides multi-collection architecture for staged memory retrieval:
- CollectionManager: Manages short-term, long-term, and decayed collections
- LongTermInclusionScorer: Relevancy-aware scoring for long-term memories
- GraphPathScorer: Relevancy scoring for graph node-edge-node paths
- AccessBuffer: Lazy access tracking for latency optimization
- RetrievalFactorComputer: Pre-computed retrieval factors

Ref: docs/build-plan/memory-lifecycle-staging-decay.md, Phase 2, 3 & 5
"""

from friday_memory.retrieval.access_buffer import (
    AccessBuffer,
    AccessBufferConfig,
    FlushResult,
)
from friday_memory.retrieval.collection_manager import (
    CollectionConfig,
    CollectionManager,
)
from friday_memory.retrieval.factor_computer import (
    FactorComputerConfig,
    FactorComputeResult,
    RetrievalFactorComputer,
    calculate_inclusion_score_fast,
)
from friday_memory.retrieval.graph_scorer import (
    GraphPathScorer,
    GraphPathScorerConfig,
    ScoredPath,
    cosine_similarity,
)
from friday_memory.retrieval.inclusion_scorer import (
    InclusionScorerConfig,
    LongTermInclusionScorer,
)

__all__ = [
    # Collection management
    "CollectionConfig",
    "CollectionManager",
    # Long-term inclusion scoring
    "InclusionScorerConfig",
    "LongTermInclusionScorer",
    # Graph path scoring
    "GraphPathScorerConfig",
    "GraphPathScorer",
    "ScoredPath",
    "cosine_similarity",
    # Access buffer (Phase 5)
    "AccessBufferConfig",
    "AccessBuffer",
    "FlushResult",
    # Factor computer (Phase 5)
    "FactorComputerConfig",
    "RetrievalFactorComputer",
    "FactorComputeResult",
    "calculate_inclusion_score_fast",
]
