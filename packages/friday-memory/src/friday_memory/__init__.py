"""
Friday Memory Package.
Contains the 'Brain' logic: MemoryController, ContextEngine, and DB Adapters.

Ref: Batch 1 & 2 Specifications

This package provides:
- Models: Data structures for memory operations (Pydantic models)
- Adapters: Concrete implementations of storage interfaces
- Controller: Unified facade for memory operations
- Context: Context engineering components
- Ingestion: Document processing pipeline
"""

# Models
from friday_memory.models import (
    ConflictResolutionResponse,
    ConsolidationReport,
    ContextPayload,
    GraphEdge,
    GraphNode,
    InteractionTurn,
    ProvenanceMetadata,
    SessionState,
    SummarizationResponse,
    ToolCall,
    ToolResult,
)

# Adapters
from friday_memory.adapters import (
    ChromaVectorStore,
    ElementXGraphStore,
    InMemoryEpisodicStore,
    SimpleVectorStore,
    NullGraphStore,
)

# Controller
from friday_memory.controller import MemoryController

# Context Engineering
from friday_memory.context import (
    ContextAssembler,
    MemoryConsolidator,
    MemoryExtractor,
    PromptArchitect,
)

# Ingestion
from friday_memory.ingestion import DocumentIngestionPipeline

# Retrieval (Phase 2, 3 & 5)
from friday_memory.retrieval import (
    AccessBuffer,
    AccessBufferConfig,
    CollectionConfig,
    CollectionManager,
    FactorComputeResult,
    FactorComputerConfig,
    FlushResult,
    GraphPathScorer,
    GraphPathScorerConfig,
    InclusionScorerConfig,
    LongTermInclusionScorer,
    RetrievalFactorComputer,
    ScoredPath,
    calculate_inclusion_score_fast,
)

# Lifecycle (Phase 1 & 4)
from friday_memory.lifecycle import (
    DecayCalculator,
    DecayConfig,
    MemoryLifecycleMetadata,
    MemoryMigrator,
    MemoryPromotionService,
    MemoryStage,
    MigrationReport,
    PromotionResult,
    PromotionScorer,
    PromotionState,
)

__all__ = [
    # Models
    "ProvenanceMetadata",
    "GraphNode",
    "GraphEdge",
    "ToolCall",
    "ToolResult",
    "InteractionTurn",
    "SessionState",
    "ConsolidationReport",
    "ContextPayload",
    "SummarizationResponse",
    "ConflictResolutionResponse",
    # Adapters
    "InMemoryEpisodicStore",
    "ElementXGraphStore",
    "ChromaVectorStore",
    "SimpleVectorStore",
    "NullGraphStore",
    # Controller
    "MemoryController",
    # Context Engineering
    "PromptArchitect",
    "ContextAssembler",
    "MemoryExtractor",
    "MemoryConsolidator",
    # Ingestion
    "DocumentIngestionPipeline",
    # Retrieval (Phase 2, 3 & 5)
    "CollectionConfig",
    "CollectionManager",
    "InclusionScorerConfig",
    "LongTermInclusionScorer",
    "GraphPathScorerConfig",
    "GraphPathScorer",
    "ScoredPath",
    # Latency Optimization (Phase 5)
    "AccessBufferConfig",
    "AccessBuffer",
    "FlushResult",
    "FactorComputerConfig",
    "RetrievalFactorComputer",
    "FactorComputeResult",
    "calculate_inclusion_score_fast",
    # Lifecycle (Phase 1 & 4)
    "MemoryStage",
    "PromotionState",
    "MemoryLifecycleMetadata",
    "DecayConfig",
    "DecayCalculator",
    "PromotionScorer",
    "PromotionResult",
    "MemoryPromotionService",
    # Migration (Phase 9)
    "MemoryMigrator",
    "MigrationReport",
]
