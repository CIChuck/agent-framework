"""Additive multi-agent memory module."""

from friday_memory.multi_agent.controller import MultiAgentMemoryController
from friday_memory.multi_agent.coordinator import PromotionCoordinator
from friday_memory.multi_agent.journal import PromotionJournal
from friday_memory.multi_agent.models import (
    PRIVATE_VISIBILITY,
    SHARED_NAMESPACE,
    SHARED_VISIBILITY,
    PromotionJournalEntry,
    PromotionJournalEvent,
    PromotionJournalState,
    SharedPromotionProposal,
)
from friday_memory.multi_agent.observability import build_promotion_ops_snapshot
from friday_memory.multi_agent.policy import NamespacePolicyEngine
from friday_memory.multi_agent.scratchpad import (
    ScratchEvent,
    ScratchPad,
    ScratchPadStore,
    ScratchPlanItem,
    ScratchPlanItemStatus,
)

__all__ = [
    "MultiAgentMemoryController",
    "NamespacePolicyEngine",
    "PromotionCoordinator",
    "PromotionJournal",
    "PromotionJournalEvent",
    "PromotionJournalEntry",
    "PromotionJournalState",
    "ScratchPadStore",
    "ScratchPad",
    "ScratchPlanItem",
    "ScratchPlanItemStatus",
    "ScratchEvent",
    "SharedPromotionProposal",
    "build_promotion_ops_snapshot",
    "PRIVATE_VISIBILITY",
    "SHARED_VISIBILITY",
    "SHARED_NAMESPACE",
]
