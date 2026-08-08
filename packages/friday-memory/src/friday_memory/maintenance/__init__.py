# mypy: ignore-errors
"""
Friday Memory Maintenance Utilities.

A maintenance utility for organizing, pruning, and synthesizing memories
across the three memory stores (Graph, Vector, Episodic).

Usage:
    python -m friday_memory.maintenance backup --dir ./memory
    python -m friday_memory.maintenance analyze --dir ./memory
    python -m friday_memory.maintenance prune --dir ./memory --dry-run
    python -m friday_memory.maintenance synthesize --dir ./memory --dry-run
    python -m friday_memory.maintenance verify --dir ./memory --dry-run
    python -m friday_memory.maintenance reorganize --dir ./memory --backup-first
"""

from friday_memory.maintenance.analyzer import ConsistencyAnalyzer
from friday_memory.maintenance.backup import BackupManager
from friday_memory.maintenance.compactor import InSessionCompactor
from friday_memory.maintenance.fact_checker import FactChecker
from friday_memory.maintenance.incremental import (
    IncrementalGraphMaintainer,
    IncrementalMaintenanceConfig,
    MaintenanceResult,
)
from friday_memory.maintenance.logger import ReorganizationLogger
from friday_memory.maintenance.models import (
    ActionLogEntry,
    ActionType,
    BackupManifest,
    ClaimType,
    ClassifiedFact,
    ConsistencyIssue,
    ConsistencyReport,
    DuplicateGroup,
    EmbeddingConfig,
    FactCheckConfig,
    IssueSeverity,
    IssueType,
    KnowledgeGap,
    LifecycleReport,
    LogConfig,
    LogFormat,
    LogVerbosity,
    MaintenanceConfig,
    OptimizationReport,
    PromptsConfig,
    PruneConfig,
    PrunedItem,
    PruneReport,
    ReorganizationReport,
    SynthesisConfig,
    SynthesisReport,
    SynthesizedMemory,
    TopicCluster,
    VerificationReport,
    VerificationVerdict,
    VerifiedClaim,
)
from friday_memory.maintenance.mutation import (
    DuplicateMemoryGroup,
    ExplicitMemoryMutationParticipant,
    GraphEdgeReference,
    GraphEmbeddingUpdate,
    MemoryEmbeddingUpdate,
    MemoryMetadataUpdate,
    MemoryMutationCommand,
    MemoryMutationError,
    MemoryMutationErrorCode,
    MemoryMutationParticipant,
    MemoryMutationPlan,
    MemoryMutationResult,
    MemoryMutationStep,
    MemoryMutationVerification,
    MemoryVectorAddition,
    MemoryVerificationStatus,
    MemoryVerificationUpdate,
    VectorCollectionDimension,
    VectorMemoryRecord,
    VectorMemoryReference,
)
from friday_memory.maintenance.pruner import RedundancyPruner
from friday_memory.maintenance.recovery import (
    DrainedAccessBuffer,
    MemoryLayoutError,
    MemoryMaintenanceParticipant,
    MemoryPreflightError,
    MemoryQuiescenceError,
    MemoryQuiescenceToken,
    MemoryRecoveryError,
    MemoryRecoveryParticipant,
    MemorySnapshotError,
)
from friday_memory.maintenance.recovery_models import (
    CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT,
    AccessBufferRecoveryStrategy,
    AccessBufferSnapshotManifest,
    ChromaCollectionManifest,
    ChromaCollectionSnapshot,
    ChromaLogicalSnapshot,
    GraphSnapshotManifest,
    LegacySingleRootLayoutAdapter,
    MemoryDiscoveryReport,
    MemoryMaintenanceLayout,
    MemoryOperationResult,
    MemoryOperationStatus,
    MemoryRecoveryErrorCode,
    MemoryRecoveryErrorDetail,
    MemoryRecoveryOperation,
    MemorySnapshotManifest,
    MemorySnapshotStrategy,
    MemoryStoreKind,
    StoreDiscovery,
    StoreDiscoveryState,
    VectorRecordSnapshot,
    VectorSnapshotManifest,
)
from friday_memory.maintenance.reorganizer import MemoryReorganizer
from friday_memory.maintenance.synthesizer import MemorySynthesizer

__all__ = [
    # Main classes
    "BackupManager",
    "ConsistencyAnalyzer",
    "RedundancyPruner",
    "MemorySynthesizer",
    "FactChecker",
    "MemoryReorganizer",
    "ReorganizationLogger",
    # Incremental maintenance
    "IncrementalGraphMaintainer",
    "IncrementalMaintenanceConfig",
    "MaintenanceResult",
    # In-session compaction
    "InSessionCompactor",
    # Config
    "MaintenanceConfig",
    "PromptsConfig",
    "PruneConfig",
    "SynthesisConfig",
    "FactCheckConfig",
    "LogConfig",
    "EmbeddingConfig",
    # Enums
    "IssueSeverity",
    "IssueType",
    "ClaimType",
    "VerificationVerdict",
    "LogVerbosity",
    "LogFormat",
    "ActionType",
    # Backup
    "BackupManifest",
    # Analysis
    "ConsistencyIssue",
    "ConsistencyReport",
    "DuplicateGroup",
    # Pruning
    "PrunedItem",
    "PruneReport",
    # Synthesis
    "TopicCluster",
    "KnowledgeGap",
    "SynthesizedMemory",
    "SynthesisReport",
    # Fact Checking
    "ClassifiedFact",
    "VerifiedClaim",
    "VerificationReport",
    # Lifecycle
    "LifecycleReport",
    "OptimizationReport",
    # Full Report
    "ReorganizationReport",
    # Logging
    "ActionLogEntry",
    # Explicit graph/vector mutation contracts
    "DuplicateMemoryGroup",
    "ExplicitMemoryMutationParticipant",
    "GraphEdgeReference",
    "GraphEmbeddingUpdate",
    "MemoryEmbeddingUpdate",
    "MemoryMetadataUpdate",
    "MemoryMutationCommand",
    "MemoryMutationError",
    "MemoryMutationErrorCode",
    "MemoryMutationParticipant",
    "MemoryMutationPlan",
    "MemoryMutationResult",
    "MemoryMutationStep",
    "MemoryMutationVerification",
    "MemoryVerificationStatus",
    "MemoryVerificationUpdate",
    "MemoryVectorAddition",
    "VectorMemoryRecord",
    "VectorMemoryReference",
    "VectorCollectionDimension",
    # Recovery contracts
    "CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT",
    "AccessBufferRecoveryStrategy",
    "AccessBufferSnapshotManifest",
    "ChromaCollectionManifest",
    "ChromaCollectionSnapshot",
    "ChromaLogicalSnapshot",
    "GraphSnapshotManifest",
    "LegacySingleRootLayoutAdapter",
    "MemoryDiscoveryReport",
    "MemoryMaintenanceLayout",
    "MemoryOperationResult",
    "MemoryOperationStatus",
    "MemoryRecoveryErrorCode",
    "MemoryRecoveryErrorDetail",
    "MemoryRecoveryOperation",
    "MemorySnapshotManifest",
    "MemorySnapshotStrategy",
    "MemoryStoreKind",
    "StoreDiscovery",
    "StoreDiscoveryState",
    "VectorRecordSnapshot",
    "VectorSnapshotManifest",
    "DrainedAccessBuffer",
    "MemoryLayoutError",
    "MemoryMaintenanceParticipant",
    "MemoryRecoveryParticipant",
    "MemoryPreflightError",
    "MemoryQuiescenceError",
    "MemoryQuiescenceToken",
    "MemoryRecoveryError",
    "MemorySnapshotError",
]
