"""
Friday Agent - Orchestration Layer.

Provides agent abstractions and implementations for building
AI agents with memory, tools, and context management.

Components:
- AgentProfile: Defines agent identity and capabilities
- AgentBase: Abstract base class for all agents
- CopilotAgent: Interactive Re-Act agent with tool calling
- AutonomousAgent: Placeholder for autonomous task execution
- DefaultToolRegistry: Tool registration and resolution
- Built-in tools: scratchpad, recall_memory, store_fact

Ref: Batch 3 Specification, Section 4
"""

from friday_agent.autonomous import AutonomousAgent
from friday_agent.base import AgentBase
from friday_agent.copilot import CopilotAgent
from friday_agent.profile import AgentProfile
from friday_agent.tools import DefaultToolRegistry, tool

__all__ = [
    # Agent classes
    "AgentProfile",
    "AgentBase",
    "CopilotAgent",
    "AutonomousAgent",
    # Tool infrastructure
    "DefaultToolRegistry",
    "tool",
]
