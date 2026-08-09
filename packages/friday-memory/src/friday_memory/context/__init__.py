# mypy: ignore-errors
"""
Context Engineering Logic.

This module contains the core context engineering components that implement
the "Brain" of the Friday Framework:

- PromptArchitect: Layout engine for optimal prompt structuring
- ContextAssembler: Main implementation of ContextEngineeringInterface
- MemoryExtractor: Harvests memories from conversation turns
- MemoryConsolidator: Synthesizes fragmented memories into coherent blocks
- ToolContextManager: Manages tool selection and context integration
- PromptCacheConfig: Configuration for LLM provider prompt caching
"""

from friday_memory.context.assembler import ContextAssembler
from friday_memory.context.budget_monitor import ContextBudgetMonitor
from friday_memory.context.cache_config import (
    CacheBreakpoint,
    CacheProvider,
    PromptCacheConfig,
)
from friday_memory.context.consolidator import MemoryConsolidator
from friday_memory.context.extraction_filter import (
    ExtractionFilter,
    configure_rejection_logging,
)
from friday_memory.context.extractor import (
    ExtractionCommitCompletedUnderCancellation,
    MemoryExtractor,
)
from friday_memory.context.layout import PromptArchitect, SupportingContextConfig
from friday_memory.context.ontology import NodeTypeConfig, OntologyConfig
from friday_memory.context.passage_router import (
    PassageRouter,
    PassageRouterConfig,
    PassageRoutingDecision,
)
from friday_memory.context.tool_manager import ToolContextManager

__all__ = [
    "PromptArchitect",
    "SupportingContextConfig",
    "ContextAssembler",
    "MemoryExtractor",
    "ExtractionCommitCompletedUnderCancellation",
    "MemoryConsolidator",
    "ToolContextManager",
    "PassageRouter",
    "PassageRouterConfig",
    "PassageRoutingDecision",
    "PromptCacheConfig",
    "CacheProvider",
    "CacheBreakpoint",
    "OntologyConfig",
    "NodeTypeConfig",
    "ExtractionFilter",
    "configure_rejection_logging",
    "ContextBudgetMonitor",
]
