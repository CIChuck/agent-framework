"""
Memory Lifecycle Management Module.

Provides temporal decay, promotion scoring, lifecycle stage management,
and migration utilities for the Friday memory system.

Ref: docs/build-plan/memory-lifecycle-staging-decay.md
"""

from friday_memory.lifecycle.decay import (
    DecayCalculator,
    DecayConfig,
)
from friday_memory.lifecycle.migration import (
    MemoryMigrator,
    MigrationReport,
    migrate_to_multi_collection,
)
from friday_memory.lifecycle.promotion import (
    MemoryPromotionService,
    PromotionResult,
    PromotionScorer,
)
from friday_memory.lifecycle.stages import (
    MemoryLifecycleMetadata,
    MemoryStage,
    PromotionState,
)

__all__ = [
    # Enums
    "MemoryStage",
    "PromotionState",
    # Models
    "MemoryLifecycleMetadata",
    "DecayConfig",
    "PromotionResult",
    "MigrationReport",
    # Calculators/Scorers
    "DecayCalculator",
    "PromotionScorer",
    # Services
    "MemoryPromotionService",
    "MemoryMigrator",
    # Functions
    "migrate_to_multi_collection",
]
