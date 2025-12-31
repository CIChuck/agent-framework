"""
Memory Orchestration Layer.

The MemoryController provides a unified facade for all memory operations,
sitting between the Data Layer (Batch 1 Adapters) and Context Strategies (Batch 2a).
"""

from friday_memory.controller.memory_controller import MemoryController

__all__ = ["MemoryController"]
