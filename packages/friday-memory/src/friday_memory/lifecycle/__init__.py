# mypy: ignore-errors
"""
Memory Lifecycle Management Module.

Provides temporal decay, promotion scoring, lifecycle stage management,
migration utilities, and tool content lifecycle for the Friday memory system.

Ref: docs/build-plan/memory-lifecycle-staging-decay.md
Ref: docs/build-plan/to-do/tool-content-lifecycle-build-plan.md
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
from friday_memory.lifecycle.tool_content import (
    ToolContentConfig,
    ToolContentManager,
    TrackedToolOutput,
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
    "TrackedToolOutput",
    "ToolContentConfig",
    # Calculators/Scorers
    "DecayCalculator",
    "PromotionScorer",
    # Services
    "MemoryPromotionService",
    "MemoryMigrator",
    "ToolContentManager",
    # Functions
    "migrate_to_multi_collection",
]
