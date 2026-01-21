"""
Context Engineering Logic.

This module contains the core context engineering components that implement
the "Brain" of the Friday Framework:

- PromptArchitect: Layout engine for optimal prompt structuring
- ContextAssembler: Main implementation of ContextEngineeringInterface
- MemoryExtractor: Harvests memories from conversation turns
- MemoryConsolidator: Synthesizes fragmented memories into coherent blocks
- ToolContextManager: Manages tool selection and context integration
"""

from friday_memory.context.assembler import ContextAssembler
from friday_memory.context.consolidator import MemoryConsolidator
from friday_memory.context.extractor import MemoryExtractor
from friday_memory.context.layout import PromptArchitect
from friday_memory.context.tool_manager import ToolContextManager

__all__ = [
    "PromptArchitect",
    "ContextAssembler",
    "MemoryExtractor",
    "MemoryConsolidator",
    "ToolContextManager",
]
