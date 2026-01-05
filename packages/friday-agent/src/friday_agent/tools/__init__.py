"""
Friday Agent Tools Package.

Provides tool registration infrastructure and built-in tools
for agent workflows.

Components:
- DefaultToolRegistry: Implementation of ToolRegistry protocol
- tool: Decorator for registering functions as tools
- Built-in tools: scratchpad_write, scratchpad_read, recall_memory, store_fact

Ref: Batch 3 Specification, Section 5
"""

from friday_agent.tools.builtins import (
    recall_memory,
    scratchpad_read,
    scratchpad_write,
    store_fact,
)
from friday_agent.tools.registry import DefaultToolRegistry, tool

__all__ = [
    "DefaultToolRegistry",
    "tool",
    # Built-in tools
    "scratchpad_write",
    "scratchpad_read",
    "recall_memory",
    "store_fact",
]
