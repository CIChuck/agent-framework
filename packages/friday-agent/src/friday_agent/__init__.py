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
- AgentLoader: YAML-based agent configuration loading
- AgentRegistry: Central registry for agent profiles
- AgentOrchestrator: Multi-agent coordination
- Workflows: Task graph execution with approval gates
- Built-in tools: scratchpad, recall_memory, store_fact

Ref: Batch 3 Specification, Section 4
Ref: docs/build-plan/to-do/dynamic-workflows-build-plan.md
"""

from friday_agent.autonomous import AutonomousAgent
from friday_agent.base import AgentBase
from friday_agent.copilot import CopilotAgent
from friday_agent.interactive import InteractiveAgent
from friday_agent.loader import AgentConfigError, AgentLoader
from friday_agent.orchestrator import AgentOrchestrator, OrchestratorError
from friday_agent.profile import AgentProfile
from friday_agent.registry import AgentRegistry, AgentRegistryError
from friday_agent.repl_base import ReplAgentBase
from friday_agent.skills import SkillCatalog, SkillCatalogEntry, validate_skill_ref
from friday_agent.tools import DefaultToolRegistry, tool
from friday_agent.workflows import (
    TaskNode,
    TaskStatus,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowError,
    WorkflowExecution,
    WorkflowLoader,
    WorkflowLoadError,
)

__all__ = [
    # Agent classes
    "AgentProfile",
    "AgentBase",
    "ReplAgentBase",
    "InteractiveAgent",
    "CopilotAgent",
    "AutonomousAgent",
    # Configuration
    "AgentLoader",
    "AgentConfigError",
    # Registry
    "AgentRegistry",
    "AgentRegistryError",
    "SkillCatalog",
    "SkillCatalogEntry",
    "validate_skill_ref",
    # Orchestration
    "AgentOrchestrator",
    "OrchestratorError",
    # Workflows
    "TaskNode",
    "TaskStatus",
    "WorkflowDefinition",
    "WorkflowExecution",
    "WorkflowEngine",
    "WorkflowError",
    "WorkflowLoader",
    "WorkflowLoadError",
    # Tool infrastructure
    "DefaultToolRegistry",
    "tool",
]
