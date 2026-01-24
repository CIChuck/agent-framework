"""
Workflow system for multi-agent task orchestration.

This package provides a declarative workflow engine for executing
complex multi-agent tasks with:
- Task graphs with dependencies
- Input/output variable passing ($var syntax)
- Human-in-the-loop approval gates
- YAML workflow definitions

Ref: docs/build-plan/to-do/dynamic-workflows-build-plan.md
"""

from friday_agent.workflows.models import (
    TaskNode,
    TaskStatus,
    WorkflowDefinition,
    WorkflowExecution,
)
from friday_agent.workflows.engine import WorkflowEngine, WorkflowError
from friday_agent.workflows.loader import WorkflowLoader, WorkflowLoadError

__all__ = [
    # Models
    "TaskNode",
    "TaskStatus",
    "WorkflowDefinition",
    "WorkflowExecution",
    # Engine
    "WorkflowEngine",
    "WorkflowError",
    # Loader
    "WorkflowLoader",
    "WorkflowLoadError",
]
