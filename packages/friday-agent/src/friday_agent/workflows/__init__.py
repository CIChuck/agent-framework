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

from friday_agent.workflows.engine import (
    PipelineDispatchEngine,
    PipelineDispatchError,
    WorkflowEngine,
    WorkflowError,
)
from friday_agent.workflows.loader import WorkflowLoader, WorkflowLoadError
from friday_agent.workflows.models import (
    ArtifactLifecycleState,
    ArtifactPolicy,
    ArtifactRecord,
    DelegationHandoff,
    HITLAuthorityPolicy,
    HITLDecision,
    HITLDecisionAction,
    HITLPolicy,
    HITLRequest,
    PipelineDefinition,
    PipelineDispatch,
    PipelineExecutionState,
    PipelineExecutionStatus,
    PipelineLineageRecord,
    PipelineResult,
    TaskAssignment,
    TaskAssignmentStatus,
    TaskDefinition,
    TaskNode,
    TaskState,
    TaskStatus,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowPipelineDefinition,
)

__all__ = [
    # Models
    "ArtifactLifecycleState",
    "ArtifactPolicy",
    "ArtifactRecord",
    "DelegationHandoff",
    "HITLAuthorityPolicy",
    "HITLDecision",
    "HITLDecisionAction",
    "HITLPolicy",
    "HITLRequest",
    "PipelineDefinition",
    "PipelineDispatch",
    "PipelineExecutionState",
    "PipelineExecutionStatus",
    "PipelineLineageRecord",
    "PipelineResult",
    "TaskAssignment",
    "TaskAssignmentStatus",
    "TaskDefinition",
    "TaskNode",
    "TaskState",
    "TaskStatus",
    "WorkflowDefinition",
    "WorkflowExecution",
    "WorkflowPipelineDefinition",
    # Engine
    "PipelineDispatchEngine",
    "PipelineDispatchError",
    "WorkflowEngine",
    "WorkflowError",
    # Loader
    "WorkflowLoader",
    "WorkflowLoadError",
]
