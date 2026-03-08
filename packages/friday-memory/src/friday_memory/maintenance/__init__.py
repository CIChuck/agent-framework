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
from friday_memory.maintenance.pruner import RedundancyPruner
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
]
