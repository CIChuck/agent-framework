"""
Data models for workflow task graphs.

Ref: docs/build-plan/to-do/dynamic-workflows-build-plan.md
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TaskStatus(str, Enum):
    """Status of a workflow task."""

    PENDING = "pending"  # Not yet started
    RUNNING = "running"  # Currently executing
    WAITING_APPROVAL = "waiting_approval"  # Paused for human approval
    COMPLETED = "completed"  # Successfully finished
    FAILED = "failed"  # Failed with error
    SKIPPED = "skipped"  # Skipped (approval denied or dependency failed)


class TaskNode(BaseModel):
    """
    Single task in the workflow graph.

    A task represents one unit of work to be performed by an agent.
    Tasks can:
    - Depend on other tasks (runs after dependencies complete)
    - Declare inputs (resolved from workflow variables)
    - Produce outputs (stored in workflow variables)
    - Require human approval before executing

    Example YAML:
        - id: research
          name: "Research Topic"
          description: "Research the given topic"
          agent: researcher
          inputs:
            topic: "$user_topic"
          outputs:
            - research_results
          requires_approval: false
    """

    # Identity
    id: str = Field(..., description="Unique task identifier")
    name: str = Field(..., description="Human-readable task name")
    description: str = Field(..., description="Task description/prompt for agent")
    agent: str = Field(..., description="Agent name to execute this task")

    # Input/Output
    inputs: dict[str, str] = Field(
        default_factory=dict,
        description="Input mappings: name -> source ($var or literal)",
    )
    outputs: list[str] = Field(
        default_factory=list,
        description="Output variable names to store result",
    )

    # Dependencies
    depends_on: list[str] = Field(
        default_factory=list,
        description="Task IDs that must complete before this task",
    )

    # Control
    requires_approval: bool = Field(
        default=False,
        description="Whether task requires human approval before executing",
    )
    timeout_seconds: int | None = Field(
        default=None,
        description="Task-specific timeout (overrides workflow default)",
    )
    max_retries: int = Field(
        default=0,
        description="Maximum retry attempts on failure",
    )

    # Runtime state (updated during execution)
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current task status",
    )
    result: Any = Field(
        default=None,
        description="Task result (agent response)",
    )
    error: str | None = Field(
        default=None,
        description="Error message if failed",
    )
    retry_count: int = Field(
        default=0,
        description="Current retry attempt",
    )

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Ensure ID is valid identifier."""
        if not v or not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"Invalid task ID: {v}")
        return v.lower()

    @property
    def duration_ms(self) -> int | None:
        """Calculate task duration in milliseconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() * 1000)
        return None

    def reset(self) -> None:
        """Reset task state for retry."""
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None


class WorkflowDefinition(BaseModel):
    """
    Complete workflow definition.

    A workflow is a directed acyclic graph (DAG) of tasks that can be
    executed to accomplish a complex goal. Tasks are executed in
    topological order based on dependencies.

    Example YAML:
        id: newsletter_generation
        name: "Newsletter Generation"
        description: "Research a topic and generate a newsletter"
        tasks:
          - id: research
            name: "Research Topic"
            ...
        timeout_seconds: 3600
        max_retries: 2
    """

    # Identity
    id: str = Field(..., description="Unique workflow identifier")
    name: str = Field(..., description="Human-readable workflow name")
    description: str = Field(..., description="Workflow description")

    # Tasks
    tasks: list[TaskNode] = Field(
        ...,
        description="List of tasks in the workflow",
        min_length=1,
    )

    # Configuration
    timeout_seconds: int = Field(
        default=3600,
        description="Overall workflow timeout (1 hour default)",
    )
    max_retries: int = Field(
        default=1,
        description="Default max retries for tasks",
    )

    # Metadata
    version: str = Field(default="1.0.0", description="Workflow version")
    author: str | None = Field(default=None, description="Workflow author")
    tags: list[str] = Field(default_factory=list, description="Tags for organization")

    def get_task(self, task_id: str) -> TaskNode | None:
        """Get task by ID."""
        return next((t for t in self.tasks if t.id == task_id), None)

    def get_ready_tasks(self) -> list[TaskNode]:
        """
        Get tasks that are ready to execute.

        A task is ready when:
        - Status is PENDING
        - All dependencies are COMPLETED
        """
        completed_ids = {t.id for t in self.tasks if t.status == TaskStatus.COMPLETED}
        return [
            t
            for t in self.tasks
            if t.status == TaskStatus.PENDING
            and set(t.depends_on).issubset(completed_ids)
        ]

    def get_task_order(self) -> list[str]:
        """
        Get topologically sorted task order.

        Returns task IDs in execution order.
        """
        # Simple topological sort via Kahn's algorithm
        in_degree = {t.id: len(t.depends_on) for t in self.tasks}
        queue = [tid for tid, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            task_id = queue.pop(0)
            order.append(task_id)

            for task in self.tasks:
                if task_id in task.depends_on:
                    in_degree[task.id] -= 1
                    if in_degree[task.id] == 0:
                        queue.append(task.id)

        if len(order) != len(self.tasks):
            raise ValueError("Workflow contains cycles")

        return order

    def validate_graph(self) -> list[str]:
        """
        Validate workflow graph.

        Returns list of validation errors (empty if valid).
        """
        errors = []

        # Check for duplicate IDs
        ids = [t.id for t in self.tasks]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate task IDs found")

        # Check dependencies exist
        for task in self.tasks:
            for dep_id in task.depends_on:
                if dep_id not in ids:
                    errors.append(
                        f"Task '{task.id}' depends on unknown task '{dep_id}'"
                    )

        # Check for cycles
        try:
            self.get_task_order()
        except ValueError:
            errors.append("Workflow contains dependency cycles")

        return errors


class WorkflowExecution(BaseModel):
    """
    Runtime state of a workflow execution.

    Tracks variables, execution progress, and timing for a single
    workflow run.
    """

    # Identity
    workflow_id: str
    execution_id: str
    status: TaskStatus = TaskStatus.PENDING

    # Variable store
    variables: dict[str, Any] = Field(
        default_factory=dict,
        description="Variable store for input/output passing",
    )

    # Execution state
    current_task_id: str | None = None
    pending_approval: str | None = None  # Task ID waiting for approval

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # History
    task_history: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Execution history for each task",
    )

    @property
    def duration_ms(self) -> int | None:
        """Calculate execution duration in milliseconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() * 1000)
        return None

    def record_task(self, task: TaskNode) -> None:
        """Record task execution in history."""
        self.task_history.append(
            {
                "task_id": task.id,
                "status": task.status.value,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": (
                    task.completed_at.isoformat() if task.completed_at else None
                ),
                "duration_ms": task.duration_ms,
                "error": task.error,
            }
        )
