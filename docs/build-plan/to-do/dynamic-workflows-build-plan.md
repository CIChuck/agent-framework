# Dynamic Workflows Build Plan

**Status:** Planning
**Target:** Phase 4, Section 5.2 of Project Hive Master Plan
**Objective:** Implement task graphs with input/output matching and human-in-the-loop approval gates

---

## 1. Problem Statement

Complex tasks require multiple steps across multiple agents. Currently:
- **No Task Decomposition**: Cannot break complex tasks into steps
- **No Dependencies**: Cannot specify which tasks depend on others
- **No Data Flow**: Cannot pass outputs from one task to inputs of another
- **No Approval Gates**: Cannot pause for human review before proceeding
- **No Workflow Persistence**: Cannot resume interrupted workflows

Without workflows:
- Multi-agent collaboration is ad-hoc
- Complex tasks require manual orchestration
- No human oversight at critical decision points
- Cannot build repeatable, reliable processes

---

## 2. Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Workflow Definition (YAML)                  │
│  - Task nodes with dependencies                             │
│  - Input/output variable mappings                           │
│  - Human approval gates                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     WorkflowLoader                           │
│  - Parse YAML workflow definitions                          │
│  - Validate task graph (no cycles, valid deps)              │
│  - Return WorkflowDefinition                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     WorkflowEngine                           │
├─────────────────────────────────────────────────────────────┤
│  Execution:                                                 │
│    - Topological task ordering                              │
│    - Variable resolution ($var syntax)                      │
│    - Agent delegation via orchestrator                      │
├─────────────────────────────────────────────────────────────┤
│  Control:                                                   │
│    - Approval gates (pause for human)                       │
│    - Timeout handling                                       │
│    - Retry on failure                                       │
├─────────────────────────────────────────────────────────────┤
│  State:                                                     │
│    - Variable store                                         │
│    - Task status tracking                                   │
│    - Execution history                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   AgentOrchestrator                          │
│  (Delegates tasks to appropriate agents)                    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Workflow Execution Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    Workflow Execution                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐   │
│  │ Task A  │────►│ Task B  │────►│ Approval│────►│ Task C  │   │
│  │(research)│    │(analyze)│     │  Gate   │     │(write)  │   │
│  └─────────┘     └─────────┘     └─────────┘     └─────────┘   │
│       │               │               │               │          │
│       ▼               ▼               ▼               ▼          │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐   │
│  │ Output: │     │ Output: │     │ Human   │     │ Output: │   │
│  │ $data   │────►│ $summary│────►│ Reviews │────►│ $result │   │
│  └─────────┘     └─────────┘     └─────────┘     └─────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 2.3 Design Principles

1. **Declarative**: Workflows defined in YAML, not code
2. **Typed I/O**: Tasks declare inputs and outputs explicitly
3. **Human-in-the-Loop**: Built-in approval gates
4. **Resumable**: Workflows can pause and resume
5. **Observable**: Full execution history and state visibility

---

## 3. Implementation

### 3.1 Workflow Data Models

**Location:** `packages/friday-agent/src/friday_agent/workflows/models.py`

```python
"""Data models for workflow task graphs."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TaskStatus(str, Enum):
    """Status of a workflow task."""

    PENDING = "pending"              # Not yet started
    RUNNING = "running"              # Currently executing
    WAITING_APPROVAL = "waiting_approval"  # Paused for human approval
    COMPLETED = "completed"          # Successfully finished
    FAILED = "failed"               # Failed with error
    SKIPPED = "skipped"             # Skipped (approval denied or dependency failed)


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
        completed_ids = {
            t.id for t in self.tasks if t.status == TaskStatus.COMPLETED
        }
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
                    errors.append(f"Task '{task.id}' depends on unknown task '{dep_id}'")

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
        self.task_history.append({
            "task_id": task.id,
            "status": task.status.value,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "duration_ms": task.duration_ms,
            "error": task.error,
        })
```

### 3.2 Workflow Engine

**Location:** `packages/friday-agent/src/friday_agent/workflows/engine.py`

```python
"""Workflow execution engine."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from friday_agent.workflows.models import (
    TaskNode,
    TaskStatus,
    WorkflowDefinition,
    WorkflowExecution,
)

if TYPE_CHECKING:
    from friday_agent.orchestrator import AgentOrchestrator


logger = logging.getLogger(__name__)


class WorkflowError(Exception):
    """Raised when workflow execution fails."""

    def __init__(self, message: str, task_id: str | None = None):
        self.task_id = task_id
        super().__init__(message)


class WorkflowEngine:
    """
    Executes workflow task graphs.

    The engine processes a workflow definition by:
    1. Resolving task dependencies (topological order)
    2. Executing tasks via the orchestrator
    3. Passing outputs to inputs via variables
    4. Pausing at approval gates for human review
    5. Handling failures and retries

    Usage:
        engine = WorkflowEngine(
            orchestrator=orchestrator,
            approval_callback=ask_user_approval,
        )

        execution = await engine.execute(
            workflow=workflow,
            initial_inputs={"user_topic": "AI trends"},
        )

        # If paused for approval:
        if execution.pending_approval:
            # Show task to user, get approval
            execution = await engine.approve_task(
                workflow, execution, task_id
            )
    """

    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        approval_callback: Callable[[TaskNode], Awaitable[bool]] | None = None,
    ):
        """
        Initialize workflow engine.

        Args:
            orchestrator: Agent orchestrator for task execution
            approval_callback: Optional async function to request human approval.
                              Takes a TaskNode, returns True if approved.
                              If None, approval gates will pause execution.
        """
        self._orchestrator = orchestrator
        self._approval_callback = approval_callback

    async def execute(
        self,
        workflow: WorkflowDefinition,
        initial_inputs: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """
        Execute a workflow.

        Args:
            workflow: Workflow definition to execute
            initial_inputs: Initial variable values

        Returns:
            WorkflowExecution with final state

        Note:
            If a task requires approval and no callback is configured,
            execution will pause. Check execution.pending_approval and
            call approve_task() to continue.
        """
        # Validate workflow
        errors = workflow.validate_graph()
        if errors:
            raise WorkflowError(f"Invalid workflow: {errors}")

        # Create execution state
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            execution_id=f"{workflow.id}_{int(datetime.utcnow().timestamp())}",
            variables=initial_inputs or {},
            started_at=datetime.utcnow(),
        )

        logger.info(f"Starting workflow: {workflow.name} ({execution.execution_id})")

        try:
            await self._run_workflow(workflow, execution)
            execution.status = TaskStatus.COMPLETED
            logger.info(f"Workflow completed: {workflow.name}")
        except WorkflowError as e:
            if execution.pending_approval:
                # Paused for approval - not an error
                execution.status = TaskStatus.WAITING_APPROVAL
                logger.info(f"Workflow paused for approval: {e.task_id}")
            else:
                execution.status = TaskStatus.FAILED
                logger.error(f"Workflow failed: {e}")
                raise
        finally:
            execution.completed_at = datetime.utcnow()

        return execution

    async def _run_workflow(
        self,
        workflow: WorkflowDefinition,
        execution: WorkflowExecution,
    ) -> None:
        """Run workflow until completion or pause."""
        execution.status = TaskStatus.RUNNING

        while True:
            ready_tasks = workflow.get_ready_tasks()

            if not ready_tasks:
                # Check if all tasks complete
                all_done = all(
                    t.status
                    in (TaskStatus.COMPLETED, TaskStatus.SKIPPED, TaskStatus.FAILED)
                    for t in workflow.tasks
                )
                if all_done:
                    break

                # Check for waiting approval
                waiting = next(
                    (t for t in workflow.tasks if t.status == TaskStatus.WAITING_APPROVAL),
                    None,
                )
                if waiting:
                    execution.pending_approval = waiting.id
                    raise WorkflowError(
                        f"Task '{waiting.id}' waiting for approval",
                        task_id=waiting.id,
                    )

                # Check for failed tasks blocking progress
                failed = [t for t in workflow.tasks if t.status == TaskStatus.FAILED]
                if failed:
                    raise WorkflowError(
                        f"Workflow blocked by failed tasks: {[t.id for t in failed]}"
                    )

                # Unexpected state
                raise WorkflowError("Workflow stuck: no ready tasks and not complete")

            # Execute ready tasks sequentially (could parallelize in future)
            for task in ready_tasks:
                await self._execute_task(task, workflow, execution)

    async def _execute_task(
        self,
        task: TaskNode,
        workflow: WorkflowDefinition,
        execution: WorkflowExecution,
    ) -> None:
        """Execute a single task."""
        logger.info(f"Executing task: {task.name} ({task.id})")
        execution.current_task_id = task.id

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()

        try:
            # Check approval gate
            if task.requires_approval:
                approved = await self._handle_approval(task)
                if not approved:
                    task.status = TaskStatus.SKIPPED
                    task.completed_at = datetime.utcnow()
                    execution.record_task(task)
                    logger.info(f"Task skipped (not approved): {task.id}")
                    return

            # Resolve inputs from variables
            resolved_inputs = self._resolve_inputs(task, execution.variables)

            # Build prompt from task description and inputs
            prompt = self._build_prompt(task, resolved_inputs)

            # Execute via orchestrator
            result = await self._orchestrator.delegate(
                task.agent,
                prompt,
                return_to_current=True,
            )

            # Store result in task
            task.result = result

            # Store outputs in variables
            for output_name in task.outputs:
                execution.variables[output_name] = result
                logger.debug(f"Set variable ${output_name}")

            task.status = TaskStatus.COMPLETED
            logger.info(f"Task completed: {task.id}")

        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            task.error = str(e)

            # Retry if allowed
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.reset()
                logger.info(f"Retrying task {task.id} ({task.retry_count}/{task.max_retries})")
                return

            task.status = TaskStatus.FAILED
            raise WorkflowError(f"Task '{task.id}' failed: {e}", task_id=task.id)

        finally:
            task.completed_at = datetime.utcnow()
            execution.record_task(task)
            execution.current_task_id = None

    async def _handle_approval(self, task: TaskNode) -> bool:
        """
        Handle approval gate.

        Returns:
            True if approved, False if denied
        """
        if self._approval_callback is None:
            # No callback - pause execution
            task.status = TaskStatus.WAITING_APPROVAL
            raise WorkflowError(
                f"Task '{task.id}' requires approval",
                task_id=task.id,
            )

        # Ask for approval
        logger.info(f"Requesting approval for task: {task.id}")
        return await self._approval_callback(task)

    def _resolve_inputs(
        self,
        task: TaskNode,
        variables: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Resolve task inputs from variable store.

        Input values starting with $ are variable references.
        Other values are literal.

        Args:
            task: Task with input definitions
            variables: Variable store

        Returns:
            Dict of resolved input values
        """
        resolved = {}

        for input_name, source in task.inputs.items():
            if source.startswith("$"):
                var_name = source[1:]
                if var_name not in variables:
                    raise WorkflowError(
                        f"Missing variable: ${var_name} (required by task '{task.id}')",
                        task_id=task.id,
                    )
                resolved[input_name] = variables[var_name]
            else:
                resolved[input_name] = source  # Literal value

        return resolved

    def _build_prompt(
        self,
        task: TaskNode,
        inputs: dict[str, Any],
    ) -> str:
        """
        Build agent prompt from task and inputs.

        Args:
            task: Task definition
            inputs: Resolved input values

        Returns:
            Prompt string for agent
        """
        parts = [task.description]

        if inputs:
            parts.append("\n\nInputs:")
            for name, value in inputs.items():
                # Truncate long values for readability
                value_str = str(value)
                if len(value_str) > 500:
                    value_str = value_str[:500] + "..."
                parts.append(f"- {name}: {value_str}")

        return "\n".join(parts)

    async def approve_task(
        self,
        workflow: WorkflowDefinition,
        execution: WorkflowExecution,
        task_id: str,
    ) -> WorkflowExecution:
        """
        Approve a waiting task and continue execution.

        Args:
            workflow: Workflow definition
            execution: Current execution state
            task_id: ID of task to approve

        Returns:
            Updated execution state
        """
        task = workflow.get_task(task_id)
        if task is None:
            raise WorkflowError(f"Task not found: {task_id}")

        if task.status != TaskStatus.WAITING_APPROVAL:
            raise WorkflowError(f"Task '{task_id}' not waiting for approval")

        # Mark as approved (reset to pending for execution)
        task.status = TaskStatus.PENDING
        execution.pending_approval = None

        logger.info(f"Task approved: {task_id}")

        # Continue execution
        await self._run_workflow(workflow, execution)

        return execution

    async def skip_task(
        self,
        workflow: WorkflowDefinition,
        execution: WorkflowExecution,
        task_id: str,
    ) -> WorkflowExecution:
        """
        Skip a waiting task and continue execution.

        Args:
            workflow: Workflow definition
            execution: Current execution state
            task_id: ID of task to skip

        Returns:
            Updated execution state
        """
        task = workflow.get_task(task_id)
        if task is None:
            raise WorkflowError(f"Task not found: {task_id}")

        task.status = TaskStatus.SKIPPED
        task.completed_at = datetime.utcnow()
        execution.pending_approval = None
        execution.record_task(task)

        logger.info(f"Task skipped: {task_id}")

        # Continue execution
        await self._run_workflow(workflow, execution)

        return execution
```

### 3.3 Workflow Loader

**Location:** `packages/friday-agent/src/friday_agent/workflows/loader.py`

```python
"""YAML workflow loader."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from friday_agent.workflows.models import TaskNode, WorkflowDefinition


logger = logging.getLogger(__name__)


class WorkflowLoadError(Exception):
    """Raised when workflow loading fails."""

    pass


class WorkflowLoader:
    """
    Load workflow definitions from YAML files.

    Usage:
        loader = WorkflowLoader(Path("workflows/"))
        workflow = loader.load("newsletter")
        all_workflows = loader.load_all()
    """

    def __init__(self, workflows_dir: Path | str | None = None):
        """
        Initialize loader.

        Args:
            workflows_dir: Directory containing workflow YAML files.
                          Defaults to ./workflows/ relative to cwd.
        """
        if workflows_dir is None:
            self._workflows_dir = Path.cwd() / "workflows"
        else:
            self._workflows_dir = Path(workflows_dir)

        self._cache: dict[str, WorkflowDefinition] = {}

    def load(self, name: str) -> WorkflowDefinition:
        """
        Load workflow by name.

        Args:
            name: Workflow name (filename without .yaml)

        Returns:
            WorkflowDefinition

        Raises:
            WorkflowLoadError: If file not found or invalid
        """
        if name in self._cache:
            return self._cache[name]

        path = self._workflows_dir / f"{name}.yaml"
        if not path.exists():
            path = self._workflows_dir / f"{name}.yml"
            if not path.exists():
                raise WorkflowLoadError(f"Workflow not found: {name}")

        workflow = self._parse_yaml(path)

        # Validate
        errors = workflow.validate_graph()
        if errors:
            raise WorkflowLoadError(f"Invalid workflow '{name}': {errors}")

        self._cache[name] = workflow
        logger.info(f"Loaded workflow: {name}")
        return workflow

    def load_all(self) -> dict[str, WorkflowDefinition]:
        """Load all workflows from directory."""
        if not self._workflows_dir.exists():
            return {}

        workflows = {}
        for path in self._workflows_dir.glob("*.yaml"):
            name = path.stem
            try:
                workflows[name] = self.load(name)
            except WorkflowLoadError as e:
                logger.error(f"Failed to load workflow {name}: {e}")
                raise

        for path in self._workflows_dir.glob("*.yml"):
            name = path.stem
            if name not in workflows:
                try:
                    workflows[name] = self.load(name)
                except WorkflowLoadError as e:
                    logger.error(f"Failed to load workflow {name}: {e}")
                    raise

        return workflows

    def _parse_yaml(self, path: Path) -> WorkflowDefinition:
        """Parse YAML file into WorkflowDefinition."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise WorkflowLoadError(f"Invalid YAML in {path}: {e}")

        if not isinstance(data, dict):
            raise WorkflowLoadError(f"Workflow must be a YAML object: {path}")

        # Required fields
        required = ["id", "name", "description", "tasks"]
        missing = [f for f in required if f not in data]
        if missing:
            raise WorkflowLoadError(f"Missing required fields: {missing}")

        # Parse tasks
        tasks = []
        for task_data in data["tasks"]:
            tasks.append(TaskNode(**task_data))

        return WorkflowDefinition(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            tasks=tasks,
            timeout_seconds=data.get("timeout_seconds", 3600),
            max_retries=data.get("max_retries", 1),
            version=data.get("version", "1.0.0"),
            author=data.get("author"),
            tags=data.get("tags", []),
        )

    def reload(self, name: str) -> WorkflowDefinition:
        """Force reload workflow (bypass cache)."""
        self._cache.pop(name, None)
        return self.load(name)

    def clear_cache(self) -> None:
        """Clear workflow cache."""
        self._cache.clear()
```

### 3.4 Example Workflow

**Location:** `workflows/newsletter.yaml`

```yaml
# Newsletter Generation Workflow
# Researches a topic and generates a newsletter article

id: newsletter_generation
name: "Newsletter Generation"
description: "Research a topic and generate a newsletter article with human review"
version: "1.0.0"
author: "friday-team"
tags: ["content", "research", "writing"]

tasks:
  - id: research
    name: "Research Topic"
    description: |
      Research the given topic and gather key information.
      Focus on:
      - Recent developments
      - Key statistics
      - Expert opinions
      - Relevant examples

      Provide a comprehensive research summary.
    agent: researcher
    inputs:
      topic: "$user_topic"
    outputs:
      - research_results
    requires_approval: false

  - id: review_research
    name: "Review Research Results"
    description: |
      Review the research results for accuracy and completeness.

      Research to review:
      {{research}}

      Provide feedback or approve to continue.
    agent: researcher
    inputs:
      research: "$research_results"
    outputs:
      - approved_research
    depends_on:
      - research
    requires_approval: true

  - id: write_draft
    name: "Write Newsletter Draft"
    description: |
      Write a newsletter article based on the approved research.

      Guidelines:
      - Engaging headline
      - Clear introduction
      - Key points with supporting details
      - Call to action
      - 500-800 words
    agent: coder
    inputs:
      research: "$approved_research"
    outputs:
      - newsletter_draft
    depends_on:
      - review_research
    requires_approval: false

  - id: final_review
    name: "Final Newsletter Review"
    description: |
      Review the final newsletter draft.

      Check for:
      - Accuracy
      - Clarity
      - Tone
      - Grammar

      Approve to publish or provide feedback.
    agent: coder
    inputs:
      draft: "$newsletter_draft"
    outputs:
      - final_newsletter
    depends_on:
      - write_draft
    requires_approval: true

timeout_seconds: 7200
max_retries: 2
```

### 3.5 Package Structure

**Location:** `packages/friday-agent/src/friday_agent/workflows/__init__.py`

```python
"""Workflow system for multi-agent task orchestration."""

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
```

---

## 4. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `packages/friday-agent/src/friday_agent/workflows/__init__.py` | Create | Workflows package exports |
| `packages/friday-agent/src/friday_agent/workflows/models.py` | Create | TaskNode, WorkflowDefinition, WorkflowExecution |
| `packages/friday-agent/src/friday_agent/workflows/engine.py` | Create | WorkflowEngine implementation |
| `packages/friday-agent/src/friday_agent/workflows/loader.py` | Create | YAML workflow loader |
| `workflows/newsletter.yaml` | Create | Example workflow |
| `packages/friday-agent/tests/test_workflows.py` | Create | Unit tests |

---

## 5. Dependencies

### 5.1 Internal Dependencies
- `AgentOrchestrator` from orchestrator-mvp-build-plan
- `pyyaml` for YAML parsing (already in project)

### 5.2 No New External Dependencies

---

## 6. Verification

### 6.1 Unit Tests

**Location:** `packages/friday-agent/tests/test_workflows.py`

```python
"""Unit tests for workflow system."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from friday_agent.workflows import (
    TaskNode,
    TaskStatus,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowEngine,
    WorkflowError,
)


class TestTaskNode:
    """Test TaskNode model."""

    def test_valid_task(self):
        """Test creating valid task."""
        task = TaskNode(
            id="research",
            name="Research Topic",
            description="Research the topic",
            agent="researcher",
        )
        assert task.status == TaskStatus.PENDING
        assert task.id == "research"

    def test_reset(self):
        """Test task reset."""
        task = TaskNode(
            id="test",
            name="Test",
            description="Test",
            agent="test",
        )
        task.status = TaskStatus.FAILED
        task.error = "Some error"
        task.reset()

        assert task.status == TaskStatus.PENDING
        assert task.error is None


class TestWorkflowDefinition:
    """Test WorkflowDefinition model."""

    @pytest.fixture
    def simple_workflow(self):
        """Create simple workflow."""
        return WorkflowDefinition(
            id="test",
            name="Test Workflow",
            description="Test",
            tasks=[
                TaskNode(
                    id="task_a",
                    name="Task A",
                    description="First task",
                    agent="agent1",
                    outputs=["result_a"],
                ),
                TaskNode(
                    id="task_b",
                    name="Task B",
                    description="Second task",
                    agent="agent2",
                    depends_on=["task_a"],
                    inputs={"data": "$result_a"},
                ),
            ],
        )

    def test_get_task(self, simple_workflow):
        """Test getting task by ID."""
        task = simple_workflow.get_task("task_a")
        assert task is not None
        assert task.name == "Task A"

    def test_get_ready_tasks(self, simple_workflow):
        """Test getting ready tasks."""
        ready = simple_workflow.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == "task_a"

    def test_get_task_order(self, simple_workflow):
        """Test topological sort."""
        order = simple_workflow.get_task_order()
        assert order == ["task_a", "task_b"]

    def test_validate_graph_valid(self, simple_workflow):
        """Test validation passes for valid graph."""
        errors = simple_workflow.validate_graph()
        assert len(errors) == 0

    def test_validate_graph_cycle(self):
        """Test validation catches cycles."""
        workflow = WorkflowDefinition(
            id="cyclic",
            name="Cyclic",
            description="Has cycle",
            tasks=[
                TaskNode(
                    id="a",
                    name="A",
                    description="A",
                    agent="x",
                    depends_on=["b"],
                ),
                TaskNode(
                    id="b",
                    name="B",
                    description="B",
                    agent="x",
                    depends_on=["a"],
                ),
            ],
        )
        errors = workflow.validate_graph()
        assert any("cycle" in e.lower() for e in errors)


class TestWorkflowEngine:
    """Test WorkflowEngine."""

    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock orchestrator."""
        orchestrator = MagicMock()
        orchestrator.delegate = AsyncMock(return_value="Task result")
        return orchestrator

    @pytest.fixture
    def engine(self, mock_orchestrator):
        """Create workflow engine."""
        return WorkflowEngine(mock_orchestrator)

    @pytest.fixture
    def simple_workflow(self):
        """Create simple workflow."""
        return WorkflowDefinition(
            id="test",
            name="Test",
            description="Test workflow",
            tasks=[
                TaskNode(
                    id="task_a",
                    name="Task A",
                    description="Do A",
                    agent="agent1",
                    outputs=["result"],
                ),
            ],
        )

    @pytest.mark.asyncio
    async def test_execute_simple(self, engine, simple_workflow):
        """Test executing simple workflow."""
        execution = await engine.execute(simple_workflow)

        assert execution.status == TaskStatus.COMPLETED
        assert "result" in execution.variables

    @pytest.mark.asyncio
    async def test_execute_with_inputs(self, engine, mock_orchestrator):
        """Test workflow with initial inputs."""
        workflow = WorkflowDefinition(
            id="test",
            name="Test",
            description="Test",
            tasks=[
                TaskNode(
                    id="task",
                    name="Task",
                    description="Use input",
                    agent="agent",
                    inputs={"data": "$input_value"},
                ),
            ],
        )

        execution = await engine.execute(
            workflow,
            initial_inputs={"input_value": "test data"},
        )

        assert execution.status == TaskStatus.COMPLETED
        # Verify input was passed to orchestrator
        mock_orchestrator.delegate.assert_called_once()

    @pytest.mark.asyncio
    async def test_approval_gate_pauses(self, mock_orchestrator):
        """Test approval gate pauses execution."""
        workflow = WorkflowDefinition(
            id="test",
            name="Test",
            description="Test",
            tasks=[
                TaskNode(
                    id="approval_task",
                    name="Needs Approval",
                    description="Approve me",
                    agent="agent",
                    requires_approval=True,
                ),
            ],
        )

        engine = WorkflowEngine(mock_orchestrator, approval_callback=None)
        execution = await engine.execute(workflow)

        assert execution.status == TaskStatus.WAITING_APPROVAL
        assert execution.pending_approval == "approval_task"

    @pytest.mark.asyncio
    async def test_approve_task_continues(self, mock_orchestrator):
        """Test approving task continues execution."""
        workflow = WorkflowDefinition(
            id="test",
            name="Test",
            description="Test",
            tasks=[
                TaskNode(
                    id="approval_task",
                    name="Needs Approval",
                    description="Approve me",
                    agent="agent",
                    requires_approval=True,
                ),
            ],
        )

        engine = WorkflowEngine(mock_orchestrator, approval_callback=None)
        execution = await engine.execute(workflow)

        # Approve the task
        execution = await engine.approve_task(
            workflow, execution, "approval_task"
        )

        assert execution.status == TaskStatus.COMPLETED
```

### 6.2 Integration Test

```python
"""Integration test for workflows."""

from friday_agent.workflows import (
    WorkflowLoader,
    WorkflowEngine,
)
from friday_cli.container import FridayContainer


async def test_newsletter_workflow():
    """Test newsletter workflow end-to-end."""
    container = FridayContainer(config)
    orchestrator = AgentOrchestrator(
        container.agent_registry,
        default_agent="researcher",
    )

    # Load workflow
    loader = WorkflowLoader()
    workflow = loader.load("newsletter")

    # Create engine with auto-approval for testing
    engine = WorkflowEngine(
        orchestrator,
        approval_callback=lambda task: True,  # Auto-approve
    )

    # Execute
    execution = await engine.execute(
        workflow,
        initial_inputs={"user_topic": "AI in Healthcare 2025"},
    )

    assert execution.status == TaskStatus.COMPLETED
    assert "final_newsletter" in execution.variables
```

---

## 7. Exit Criteria

1. `TaskNode` and `WorkflowDefinition` models validate correctly
2. `WorkflowEngine` executes tasks in dependency order
3. Variables pass correctly between tasks ($var syntax)
4. Approval gates pause execution when no callback
5. `approve_task()` and `skip_task()` continue execution
6. `WorkflowLoader` parses YAML workflows
7. Newsletter example workflow executes successfully
8. Unit tests achieve 90%+ coverage
9. Cycle detection catches invalid workflows
