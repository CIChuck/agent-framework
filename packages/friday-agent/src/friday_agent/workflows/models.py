"""
Data models for workflow task graphs.

TaskNode is an immutable definition of a task. All mutable runtime
state lives in TaskState, keyed by task ID inside WorkflowExecution.

Ref: docs/build-plan/to-do/dynamic-workflows-build-plan.md
Ref: Phase 1 Build Plan, Step 3
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from friday_agent.skills import is_valid_skill_ref


class TaskStatus(str, Enum):
    """Status of a workflow task."""

    PENDING = "pending"  # Not yet started
    RUNNING = "running"  # Currently executing
    WAITING_APPROVAL = "waiting_approval"  # Paused for human approval
    COMPLETED = "completed"  # Successfully finished
    FAILED = "failed"  # Failed with error
    SKIPPED = "skipped"  # Skipped (approval denied or dependency failed)


class HITLDecisionAction(str, Enum):
    """Decision actions supported by the HITL protocol."""

    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class TaskAssignmentStatus(str, Enum):
    """Status of task assignment/claim lifecycle."""

    ASSIGNED = "assigned"
    CLAIMED = "claimed"
    RUNNING = "running"
    AWAITING_HUMAN = "awaiting_human"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineExecutionStatus(str, Enum):
    """Status of pipeline dispatch/execution lifecycle."""

    CREATED = "created"
    RUNNING = "running"
    AWAITING_HUMAN = "awaiting_human"
    BLOCKED = "blocked"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ArtifactLifecycleState(str, Enum):
    """Lifecycle states for governed artifacts."""

    DRAFT = "draft"
    VALIDATED = "validated"
    FINAL = "final"
    ARCHIVED = "archived"


class HITLAuthorityPolicy(BaseModel):
    """Authority rules for resolving HITL requests."""

    allowed_roles: tuple[str, ...]
    decision_scope: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    delegated_approvers: tuple[str, ...] = Field(default_factory=tuple)
    conflict_of_interest_rules: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("allowed_roles", mode="before")
    @classmethod
    def coerce_allowed_roles(cls, v: Any) -> tuple[str, ...]:
        """Normalize allowed role list."""
        if isinstance(v, list):
            v = tuple(v)
        if not isinstance(v, tuple) or len(v) == 0:
            raise ValueError("allowed_roles must include at least one role")
        if not all(isinstance(item, str) and item.strip() for item in v):
            raise ValueError("allowed_roles entries must be non-empty strings")
        return tuple(item.strip() for item in v)

    @field_validator("decision_scope", mode="before")
    @classmethod
    def coerce_decision_scope(cls, v: Any) -> dict[str, tuple[str, ...]]:
        """Normalize decision-scope role mappings."""
        if not isinstance(v, dict):
            raise ValueError("decision_scope must be a mapping")
        normalized: dict[str, tuple[str, ...]] = {}
        for action_class, roles in v.items():
            if isinstance(roles, list):
                roles = tuple(roles)
            if not isinstance(action_class, str) or not action_class.strip():
                raise ValueError("decision_scope keys must be non-empty strings")
            if not isinstance(roles, tuple):
                raise ValueError(
                    "decision_scope values must be lists or tuples of role names"
                )
            if not all(isinstance(role, str) and role.strip() for role in roles):
                raise ValueError(
                    "decision_scope role entries must be non-empty strings"
                )
            normalized[action_class.strip()] = tuple(role.strip() for role in roles)
        return normalized


class HITLPolicy(BaseModel):
    """HITL policy controls for workflow task execution."""

    enabled: bool = True
    methods: tuple[
        Literal[
            "approval_gate",
            "decision_selection",
            "clarification_loop",
            "conflict_adjudication",
            "override_interrupt",
            "checkpoint_review",
        ],
        ...,
    ] = ("approval_gate",)
    timeout_seconds: int = 900
    default_action_on_timeout: Literal[
        "safe_abort", "defer", "constrained_continue"
    ] = "safe_abort"
    max_reminders: int = 2
    authority_policy: HITLAuthorityPolicy

    @field_validator("timeout_seconds")
    @classmethod
    def validate_timeout_seconds(cls, v: int) -> int:
        """Ensure timeout is non-negative."""
        if v < 0:
            raise ValueError("timeout_seconds must be >= 0")
        return v

    @field_validator("methods", mode="before")
    @classmethod
    def coerce_methods(cls, v: Any) -> tuple[str, ...]:
        """Normalize HITL methods and require at least one."""
        if isinstance(v, list):
            v = tuple(v)
        if not isinstance(v, tuple) or len(v) == 0:
            raise ValueError("methods must include at least one HITL method")
        if not all(isinstance(item, str) and item.strip() for item in v):
            raise ValueError("methods entries must be non-empty strings")
        return tuple(item.strip() for item in v)


class HITLRequest(BaseModel):
    """Structured HITL request payload."""

    request_id: str
    workflow_id: str
    execution_id: str
    task_id: str
    method: str
    action_class: str = "approval_gate"
    options: tuple[str, ...] = ("approved", "rejected", "cancelled")
    recommendation: Literal["approved", "rejected", "cancelled"] = "approved"
    deadline_at: datetime
    default_action_on_timeout: Literal["safe_abort", "defer", "constrained_continue"]
    created_at: datetime
    correlation_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class HITLDecision(BaseModel):
    """Structured HITL response payload."""

    request_id: str
    task_id: str
    decision: HITLDecisionAction
    approver_id: str
    approver_role: str
    reason: str | None = None
    responded_at: datetime

    @field_validator("approver_id", "approver_role")
    @classmethod
    def validate_non_empty_approver_fields(cls, v: str) -> str:
        """Require approver metadata."""
        if not isinstance(v, str) or not v.strip():
            raise ValueError("approver metadata must be non-empty")
        return v.strip()


class ArtifactPolicy(BaseModel):
    """Artifact lifecycle and publication governance policy."""

    lifecycle_states: tuple[ArtifactLifecycleState, ...] = (
        ArtifactLifecycleState.DRAFT,
        ArtifactLifecycleState.VALIDATED,
        ArtifactLifecycleState.FINAL,
        ArtifactLifecycleState.ARCHIVED,
    )
    publication_requires_approval: bool = False
    required_provenance_fields: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("lifecycle_states", mode="before")
    @classmethod
    def coerce_lifecycle_states(cls, v: Any) -> tuple[ArtifactLifecycleState, ...]:
        """Normalize lifecycle state list and enforce required states."""
        if isinstance(v, list):
            v = tuple(v)
        if not isinstance(v, tuple) or len(v) == 0:
            raise ValueError("lifecycle_states must include at least one state")

        normalized = tuple(
            state
            if isinstance(state, ArtifactLifecycleState)
            else ArtifactLifecycleState(str(state))
            for state in v
        )
        if ArtifactLifecycleState.DRAFT not in normalized:
            raise ValueError("lifecycle_states must include 'draft'")
        if ArtifactLifecycleState.FINAL not in normalized:
            raise ValueError("lifecycle_states must include 'final'")
        return normalized

    @field_validator("required_provenance_fields", mode="before")
    @classmethod
    def coerce_required_provenance_fields(cls, v: Any) -> tuple[str, ...]:
        """Normalize required provenance field names."""
        if isinstance(v, list):
            v = tuple(v)
        if not isinstance(v, tuple):
            raise ValueError(
                "required_provenance_fields must be a list or tuple of field names"
            )
        if not all(isinstance(item, str) and item.strip() for item in v):
            raise ValueError(
                "required_provenance_fields entries must be non-empty strings"
            )
        return tuple(item.strip() for item in v)


class ArtifactRecord(BaseModel):
    """Runtime artifact record with lifecycle/provenance metadata."""

    artifact_id: str
    lifecycle_state: ArtifactLifecycleState = ArtifactLifecycleState.DRAFT
    created_by: str
    provenance: dict[str, str] = Field(default_factory=dict)
    updated_at: datetime
    published_at: datetime | None = None


class TaskState(BaseModel):
    """
    Mutable runtime state for a single task execution.

    Separated from TaskNode so that workflow definitions remain
    immutable and reusable across concurrent executions.
    """

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
    started_at: datetime | None = Field(
        default=None,
        description="When the task started executing",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the task finished executing",
    )

    @property
    def duration_ms(self) -> int | None:
        """Calculate task duration in milliseconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() * 1000)
        return None

    def reset(self) -> None:
        """Reset state for retry, preserving retry_count."""
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None


class DelegationHandoff(BaseModel):
    """Validated handoff contract for delegated task execution."""

    handoff_id: str = Field(..., description="Unique handoff identifier")
    ownership: str = Field(..., description="Delegated agent expected to own execution")
    acceptance_criteria: tuple[str, ...] = Field(
        ..., description="Completion criteria that define successful handoff"
    )
    memory_scope: str = Field(
        ...,
        description=(
            "Memory scope contract for delegated execution "
            "(for example private_only, private_plus_shared)"
        ),
    )
    deadline: datetime | None = Field(
        default=None, description="Optional execution deadline"
    )
    namespace: str | None = Field(
        default=None, description="Optional namespace/session scope hint"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional extension metadata"
    )

    @field_validator("handoff_id", "ownership", "memory_scope")
    @classmethod
    def validate_non_empty_str(cls, v: str) -> str:
        """Ensure required contract strings are non-empty."""
        if not isinstance(v, str) or not v.strip():
            raise ValueError("handoff contract fields must be non-empty strings")
        return v.strip()

    @field_validator("acceptance_criteria", mode="before")
    @classmethod
    def coerce_acceptance_criteria(cls, v: Any) -> tuple[str, ...]:
        """Accept list or tuple and enforce non-empty criteria."""
        if isinstance(v, list):
            v = tuple(v)
        if not isinstance(v, tuple) or len(v) == 0:
            raise ValueError("acceptance_criteria must contain at least one entry")
        if not all(isinstance(item, str) and item.strip() for item in v):
            raise ValueError("acceptance_criteria entries must be non-empty strings")
        return tuple(item.strip() for item in v)


class TaskNode(BaseModel):
    """
    Single task in the workflow graph (immutable definition).

    A task represents one unit of work to be performed by an agent.
    Tasks can:
    - Depend on other tasks (runs after dependencies complete)
    - Declare inputs (resolved from workflow variables)
    - Produce outputs (stored in workflow variables)
    - Require human approval before executing

    All mutable runtime state (status, result, error, timing) lives
    in TaskState, not here. This allows the same WorkflowDefinition
    to be executed concurrently without state collision.

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

    model_config = ConfigDict(frozen=True)

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
    outputs: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Output variable names to store result",
    )

    # Dependencies
    depends_on: tuple[str, ...] = Field(
        default_factory=tuple,
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
    handoff: DelegationHandoff | None = Field(
        default=None,
        description="Optional delegated handoff contract for this task",
    )
    skill_ref: str | None = Field(
        default=None,
        description=(
            "Optional canonical skill reference (`skill_id@version`) used to "
            "resolve delegated execution target dynamically"
        ),
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Ensure ID is valid identifier."""
        if not v or not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"Invalid task ID: {v}")
        return v.lower()

    @field_validator("outputs", mode="before")
    @classmethod
    def coerce_outputs(cls, v: Any) -> tuple[str, ...]:
        """Accept list or tuple for outputs, store as tuple."""
        if isinstance(v, list):
            return tuple(v)
        if isinstance(v, tuple):
            return v
        raise ValueError("outputs must be provided as a list or tuple")

    @field_validator("depends_on", mode="before")
    @classmethod
    def coerce_depends_on(cls, v: Any) -> tuple[str, ...]:
        """Accept list or tuple for depends_on, store as tuple."""
        if isinstance(v, list):
            return tuple(v)
        if isinstance(v, tuple):
            return v
        raise ValueError("depends_on must be provided as a list or tuple")

    @field_validator("skill_ref")
    @classmethod
    def validate_skill_ref(cls, v: str | None) -> str | None:
        """Validate optional canonical skill reference."""
        if v is None:
            return None
        normalized = v.strip()
        if not is_valid_skill_ref(normalized):
            raise ValueError("skill_ref must use canonical format skill_id@version")
        return normalized


class WorkflowDefinition(BaseModel):
    """
    Complete workflow definition (immutable).

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

    Tracks per-task state, variables, execution progress, and timing
    for a single workflow run. All mutable task state lives in
    ``task_states`` — the workflow definition is never mutated.
    """

    # Identity
    workflow_id: str
    execution_id: str
    status: TaskStatus = TaskStatus.PENDING

    # Per-task runtime state (keyed by task ID)
    task_states: dict[str, TaskState] = Field(
        default_factory=dict,
        description="Runtime state for each task, keyed by task ID",
    )

    # Approval overrides — task IDs where approval was granted at runtime
    approval_overrides: set[str] = Field(
        default_factory=set,
        description="Task IDs where approval has been granted",
    )

    # Variable store
    variables: dict[str, Any] = Field(
        default_factory=dict,
        description="Variable store for input/output passing",
    )

    # Execution state
    current_task_id: str | None = None
    pending_approval: str | None = None  # Task ID waiting for approval
    pending_hitl_request: HITLRequest | None = None

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # History
    hitl_history: list[dict[str, Any]] = Field(
        default_factory=list,
        description="HITL request/decision timeline",
    )
    artifacts: dict[str, ArtifactRecord] = Field(
        default_factory=dict,
        description="Artifact lifecycle records keyed by artifact ID",
    )
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

    def get_task_state(self, task_id: str) -> TaskState:
        """
        Get or create the runtime state for a task.

        Args:
            task_id: The task identifier.

        Returns:
            TaskState for the given task.
        """
        if task_id not in self.task_states:
            self.task_states[task_id] = TaskState()
        return self.task_states[task_id]

    def get_ready_tasks(self, definition: WorkflowDefinition) -> list[TaskNode]:
        """
        Get tasks that are ready to execute.

        A task is ready when:
        - Its runtime status is PENDING
        - All dependencies have COMPLETED status

        Args:
            definition: The workflow definition containing task nodes.

        Returns:
            List of TaskNode objects ready for execution.
        """
        completed_ids = {
            task_id
            for task_id, state in self.task_states.items()
            if state.status == TaskStatus.COMPLETED
        }
        return [
            t
            for t in definition.tasks
            if self.get_task_state(t.id).status == TaskStatus.PENDING
            and set(t.depends_on).issubset(completed_ids)
        ]

    def record_task(self, task: TaskNode) -> None:
        """
        Record task execution in history.

        Args:
            task: The task node whose state to record.
        """
        state = self.get_task_state(task.id)
        self.task_history.append(
            {
                "task_id": task.id,
                "status": state.status.value,
                "started_at": (
                    state.started_at.isoformat() if state.started_at else None
                ),
                "completed_at": (
                    state.completed_at.isoformat() if state.completed_at else None
                ),
                "duration_ms": state.duration_ms,
                "error": state.error,
            }
        )

    def init_task_states(self, definition: WorkflowDefinition) -> None:
        """
        Initialize task states for all tasks in the definition.

        Creates a fresh TaskState (status=PENDING) for each task.
        Idempotent — does not overwrite existing states.

        Args:
            definition: The workflow definition.
        """
        for task in definition.tasks:
            if task.id not in self.task_states:
                self.task_states[task.id] = TaskState()


def _utc_now() -> datetime:
    """Return current UTC time for assignment and dispatch state updates."""
    return datetime.now(timezone.utc)


class WorkflowPipelineDefinition(BaseModel):
    """Workflow schema for hierarchical workflow -> pipeline execution."""

    workflow_id: str
    version: str
    name: str
    goal: str
    pipeline_refs: tuple[str, ...]
    entry_pipeline_id: str | None = None
    completion_criteria: tuple[str, ...] = Field(default_factory=tuple)
    required_artifacts: list[WorkflowRequiredArtifact] = Field(default_factory=list)
    timeout_seconds: int | None = None

    @field_validator("pipeline_refs", mode="before")
    @classmethod
    def coerce_pipeline_refs(cls, v: Any) -> tuple[str, ...]:
        """Normalize pipeline refs and enforce one-or-more cardinality."""
        if isinstance(v, list):
            v = tuple(v)
        if not isinstance(v, tuple) or len(v) == 0:
            raise ValueError("pipeline_refs must contain one or more pipeline IDs")
        normalized = tuple(str(item).strip() for item in v if str(item).strip())
        if len(normalized) != len(v):
            raise ValueError("pipeline_refs entries must be non-empty strings")
        if len(set(normalized)) != len(normalized):
            raise ValueError("pipeline_refs must be unique")
        return normalized

    @field_validator("completion_criteria", mode="before")
    @classmethod
    def coerce_completion_criteria(cls, v: Any) -> tuple[str, ...]:
        """Normalize completion criteria list/tuple values."""
        if isinstance(v, list):
            v = tuple(v)
        if v is None:
            return tuple()
        if not isinstance(v, tuple):
            raise ValueError("completion_criteria must be a list or tuple")
        normalized = tuple(str(item).strip() for item in v if str(item).strip())
        if len(normalized) != len(v):
            raise ValueError("completion_criteria entries must be non-empty strings")
        return normalized

    def validate_reference_integrity(
        self, pipelines: dict[str, PipelineDefinition]
    ) -> list[str]:
        """Validate workflow->pipeline hierarchy integrity."""
        errors: list[str] = []
        missing = [pid for pid in self.pipeline_refs if pid not in pipelines]
        if missing:
            errors.append(f"Workflow references unknown pipelines: {missing}")

        if self.entry_pipeline_id is not None and self.entry_pipeline_id not in set(
            self.pipeline_refs
        ):
            errors.append("entry_pipeline_id must reference one of pipeline_refs")

        for pipeline_id in self.pipeline_refs:
            pipeline = pipelines.get(pipeline_id)
            if pipeline is None:
                continue
            if pipeline.workflow_id != self.workflow_id:
                errors.append(
                    f"Pipeline '{pipeline_id}' workflow_id mismatch: "
                    f"{pipeline.workflow_id} != {self.workflow_id}"
                )
            for dep_id in pipeline.upstream_pipeline_ids:
                if dep_id not in set(self.pipeline_refs):
                    errors.append(
                        f"Pipeline '{pipeline_id}' has upstream dependency "
                        f"'{dep_id}' outside workflow pipeline_refs"
                    )
        for artifact in self.required_artifacts:
            if artifact.produced_by_pipeline not in set(self.pipeline_refs):
                errors.append(
                    f"Required artifact '{artifact.artifact_id}' references unknown "
                    f"producer pipeline '{artifact.produced_by_pipeline}'"
                )
        return errors

    def get_pipeline_order(self, pipelines: dict[str, PipelineDefinition]) -> list[str]:
        """Return topological order of pipeline refs based on composition deps."""
        in_degree = {pid: 0 for pid in self.pipeline_refs}
        adjacency: dict[str, list[str]] = {pid: [] for pid in self.pipeline_refs}
        for pid in self.pipeline_refs:
            pipeline = pipelines.get(pid)
            if pipeline is None:
                continue
            for dep_id in pipeline.upstream_pipeline_ids:
                if dep_id not in in_degree:
                    continue
                in_degree[pid] += 1
                adjacency[dep_id].append(pid)

        queue = sorted(pid for pid, degree in in_degree.items() if degree == 0)
        order: list[str] = []
        while queue:
            current = queue.pop(0)
            order.append(current)
            for downstream in sorted(adjacency[current]):
                in_degree[downstream] -= 1
                if in_degree[downstream] == 0:
                    queue.append(downstream)

        if len(order) != len(self.pipeline_refs):
            raise ValueError("Pipeline composition graph contains a cycle")
        return order


class TaskDefinition(BaseModel):
    """Task schema for pipeline-contained task definitions."""

    task_id: str
    name: str
    description: str
    owner_agent_id: str | None = None
    owner_role: str | None = None
    required_skills: tuple[str, ...] = Field(default_factory=tuple)
    input_contract: dict[str, str] = Field(default_factory=dict)
    input_bindings: dict[str, str] = Field(default_factory=dict)
    output_contract: dict[str, str] = Field(default_factory=dict)
    output_artifacts: list[TaskOutputArtifact] = Field(default_factory=list)
    dependencies: tuple[str, ...] = Field(default_factory=tuple)
    retry_policy: dict[str, str] = Field(default_factory=dict)
    hitl_policy_ref: str | None = None
    completion_criteria: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("required_skills", mode="before")
    @classmethod
    def coerce_required_skills(cls, v: Any) -> tuple[str, ...]:
        """Normalize required skill list/tuple values."""
        if isinstance(v, list):
            v = tuple(v)
        if v is None:
            return tuple()
        if not isinstance(v, tuple):
            raise ValueError("required_skills must be a list or tuple")
        normalized = tuple(str(item).strip() for item in v if str(item).strip())
        if len(normalized) != len(v):
            raise ValueError("required_skills entries must be non-empty strings")
        return normalized

    @field_validator("dependencies", mode="before")
    @classmethod
    def coerce_dependencies(cls, v: Any) -> tuple[str, ...]:
        """Normalize dependency task IDs."""
        if isinstance(v, list):
            v = tuple(v)
        if v is None:
            return tuple()
        if not isinstance(v, tuple):
            raise ValueError("dependencies must be a list or tuple")
        normalized = tuple(str(item).strip() for item in v if str(item).strip())
        if len(normalized) != len(v):
            raise ValueError("dependencies entries must be non-empty strings")
        if len(set(normalized)) != len(normalized):
            raise ValueError("dependencies must be unique")
        return normalized

    @field_validator("completion_criteria", mode="before")
    @classmethod
    def coerce_completion_criteria(cls, v: Any) -> tuple[str, ...]:
        """Normalize completion criteria list/tuple values."""
        if isinstance(v, list):
            v = tuple(v)
        if v is None:
            return tuple()
        if not isinstance(v, tuple):
            raise ValueError("completion_criteria must be a list or tuple")
        normalized = tuple(str(item).strip() for item in v if str(item).strip())
        if len(normalized) != len(v):
            raise ValueError("completion_criteria entries must be non-empty strings")
        return normalized

    @field_validator("owner_agent_id", "owner_role")
    @classmethod
    def normalize_owner_fields(cls, v: str | None) -> str | None:
        """Normalize optional owner selector fields."""
        if v is None:
            return None
        normalized = v.strip()
        if not normalized:
            raise ValueError("owner selectors must be non-empty when provided")
        return normalized

    @field_validator("input_contract", "output_contract", "input_bindings")
    @classmethod
    def validate_contract_types(cls, v: dict[str, str]) -> dict[str, str]:
        """Require type contract entries to be non-empty string pairs."""
        for key, type_name in v.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("contract keys must be non-empty strings")
            if not isinstance(type_name, str) or not type_name.strip():
                raise ValueError("contract type names must be non-empty strings")
        return v

    @field_validator("output_artifacts")
    @classmethod
    def validate_output_artifacts_list(
        cls, v: list[TaskOutputArtifact]
    ) -> list[TaskOutputArtifact]:
        """Require artifact mappings to be unique per artifact_id."""
        artifact_ids = [artifact.artifact_id for artifact in v]
        if len(artifact_ids) != len(set(artifact_ids)):
            raise ValueError("output_artifacts must not contain duplicate artifact_id values")
        return v

    @field_validator("retry_policy", mode="before")
    @classmethod
    def validate_retry_policy(cls, v: Any) -> dict[str, str]:
        """Validate retry policy field values when present."""
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError("retry_policy must be a mapping")
        normalized: dict[str, str] = {}
        for key, value in v.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("retry_policy keys must be non-empty strings")
            value_str = str(value).strip()
            if not value_str:
                raise ValueError("retry_policy values must be non-empty strings")
            normalized[key.strip()] = value_str
        return normalized

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        """Validate task IDs used in pipeline graphs."""
        normalized = v.strip().lower()
        if not normalized or not normalized.replace("_", "").replace("-", "").isalnum():
            raise ValueError("task_id must be a valid identifier")
        return normalized

    @model_validator(mode="after")
    def validate_owner_selector_constraint(self) -> TaskDefinition:
        """Enforce exactly one owner selector field."""
        has_agent = self.owner_agent_id is not None
        has_role = self.owner_role is not None
        if has_agent == has_role:
            raise ValueError("exactly one of owner_agent_id or owner_role must be set")
        if self.input_bindings and not set(self.input_bindings).issubset(self.input_contract):
            raise ValueError(
                "input_bindings keys must reference declared input_contract keys"
            )
        output_keys = set(self.output_contract)
        for artifact in self.output_artifacts:
            if artifact.from_output not in output_keys:
                raise ValueError(
                    "output_artifacts.from_output must reference a declared output_contract key"
                )
        return self


class WorkflowRequiredArtifact(BaseModel):
    """Workflow-level final artifact obligation."""

    artifact_id: str
    type: str
    produced_by_pipeline: str

    @field_validator("artifact_id", "type", "produced_by_pipeline")
    @classmethod
    def validate_non_empty_fields(cls, v: str) -> str:
        """Require non-empty string fields."""
        normalized = v.strip()
        if not normalized:
            raise ValueError("workflow artifact fields must be non-empty strings")
        return normalized


class PipelineProducedArtifact(BaseModel):
    """Pipeline-produced artifact contract entry."""

    artifact_id: str
    type: str
    producer_task_id: str

    @field_validator("artifact_id", "type", "producer_task_id")
    @classmethod
    def validate_non_empty_fields(cls, v: str) -> str:
        """Require non-empty string fields."""
        normalized = v.strip()
        if not normalized:
            raise ValueError("produced artifact fields must be non-empty strings")
        return normalized


class PipelineConsumedArtifact(BaseModel):
    """Pipeline-consumed artifact contract entry."""

    artifact_id: str
    type: str
    from_pipeline: str

    @field_validator("artifact_id", "type", "from_pipeline")
    @classmethod
    def validate_non_empty_fields(cls, v: str) -> str:
        """Require non-empty string fields."""
        normalized = v.strip()
        if not normalized:
            raise ValueError("consumed artifact fields must be non-empty strings")
        return normalized


class PipelineArtifactContract(BaseModel):
    """Produced/consumed artifact contract for a pipeline."""

    produced: list[PipelineProducedArtifact] = Field(default_factory=list)
    consumed: list[PipelineConsumedArtifact] = Field(default_factory=list)


class TaskOutputArtifact(BaseModel):
    """Task-level output-to-artifact publication mapping."""

    artifact_id: str
    from_output: str
    type: str
    required: bool = True

    @field_validator("artifact_id", "from_output", "type")
    @classmethod
    def validate_non_empty_fields(cls, v: str) -> str:
        """Require non-empty string fields."""
        normalized = v.strip()
        if not normalized:
            raise ValueError("task output artifact fields must be non-empty strings")
        return normalized


class TaskAssignment(BaseModel):
    """Assignment/claim state for a task under pipeline dispatch."""

    assignment_id: str
    workflow_id: str
    pipeline_id: str
    task_id: str
    assigned_agent_id: str
    assigned_at: datetime
    lease_expires_at: datetime | None = None
    status: TaskAssignmentStatus = TaskAssignmentStatus.ASSIGNED
    claimed_agent_id: str | None = None
    claimed_at: datetime | None = None
    last_heartbeat_at: datetime | None = None
    attempt_count: int = 0
    failure_summary: str | None = None

    def is_lease_expired(self, now: datetime | None = None) -> bool:
        """Return True when assignment lease is expired."""
        if self.lease_expires_at is None:
            return False
        check_time = now or _utc_now()
        return check_time >= self.lease_expires_at


class PipelineDefinition(BaseModel):
    """Pipeline schema containing one-or-more task definitions."""

    pipeline_id: str
    version: str
    workflow_id: str
    goal: str
    tasks: list[TaskDefinition]
    entrypoints: tuple[str, ...] = Field(default_factory=tuple)
    exit_conditions: tuple[str, ...] = Field(default_factory=tuple)
    timeout_seconds: int | None = None
    upstream_pipeline_ids: tuple[str, ...] = Field(default_factory=tuple)
    input_contract: dict[str, str] = Field(default_factory=dict)
    output_contract: dict[str, str] = Field(default_factory=dict)
    artifact_contract: PipelineArtifactContract = Field(default_factory=PipelineArtifactContract)

    @field_validator("tasks")
    @classmethod
    def validate_tasks_non_empty(cls, v: list[TaskDefinition]) -> list[TaskDefinition]:
        """Require one-or-more task definitions per pipeline."""
        if len(v) == 0:
            raise ValueError("PipelineDefinition.tasks must contain one or more tasks")
        return v

    @field_validator("entrypoints", "exit_conditions", mode="before")
    @classmethod
    def coerce_tuple_fields(cls, v: Any) -> tuple[str, ...]:
        """Normalize list/tuple string fields."""
        if isinstance(v, list):
            v = tuple(v)
        if v is None:
            return tuple()
        if not isinstance(v, tuple):
            raise ValueError("entrypoints/exit_conditions must be list or tuple")
        normalized = tuple(str(item).strip() for item in v if str(item).strip())
        if len(normalized) != len(v):
            raise ValueError(
                "entrypoints/exit_conditions entries must be non-empty strings"
            )
        return normalized

    @field_validator("upstream_pipeline_ids", mode="before")
    @classmethod
    def coerce_upstream_ids(cls, v: Any) -> tuple[str, ...]:
        """Normalize upstream pipeline references for composition."""
        if isinstance(v, list):
            v = tuple(v)
        if v is None:
            return tuple()
        if not isinstance(v, tuple):
            raise ValueError("upstream_pipeline_ids must be a list or tuple")
        normalized = tuple(str(item).strip() for item in v if str(item).strip())
        if len(normalized) != len(v):
            raise ValueError("upstream_pipeline_ids entries must be non-empty strings")
        if len(set(normalized)) != len(normalized):
            raise ValueError("upstream_pipeline_ids must be unique")
        return normalized

    @field_validator("input_contract", "output_contract")
    @classmethod
    def validate_pipeline_contracts(cls, v: dict[str, str]) -> dict[str, str]:
        """Require non-empty string key/type contract mappings."""
        for key, type_name in v.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("pipeline contract keys must be non-empty strings")
            if not isinstance(type_name, str) or not type_name.strip():
                raise ValueError("pipeline contract values must be non-empty strings")
        return v

    def get_task(self, task_id: str) -> TaskDefinition | None:
        """Get a task by task_id."""
        return next((task for task in self.tasks if task.task_id == task_id), None)

    def validate_graph(self) -> list[str]:
        """Validate task dependency graph and pipeline invariants."""
        errors: list[str] = []
        task_ids = [task.task_id for task in self.tasks]
        if len(task_ids) != len(set(task_ids)):
            errors.append("Pipeline contains duplicate task_id values")

        valid_ids = set(task_ids)
        for task in self.tasks:
            for dep_id in task.dependencies:
                if dep_id not in valid_ids:
                    errors.append(
                        f"Task '{task.task_id}' depends on unknown task '{dep_id}'"
                    )
                if dep_id == task.task_id:
                    errors.append(f"Task '{task.task_id}' cannot depend on itself")

        if self.entrypoints:
            for entry_task_id in self.entrypoints:
                if entry_task_id not in valid_ids:
                    errors.append(
                        f"Pipeline entrypoint '{entry_task_id}' does not exist in tasks"
                    )

        try:
            self.get_task_order()
        except ValueError as e:
            errors.append(str(e))

        valid_task_ids = set(task_ids)
        produced_artifacts = set()
        for artifact in self.artifact_contract.produced:
            produced_artifacts.add(artifact.artifact_id)
            if artifact.producer_task_id not in valid_task_ids:
                errors.append(
                    f"artifact_contract.produced '{artifact.artifact_id}' references "
                    f"unknown producer_task_id '{artifact.producer_task_id}'"
                )

        for task in self.tasks:
            for output_artifact in task.output_artifacts:
                if output_artifact.artifact_id in produced_artifacts:
                    continue
                errors.append(
                    f"task '{task.task_id}' output artifact "
                    f"'{output_artifact.artifact_id}' "
                    "is not declared in pipeline artifact_contract.produced"
                )
        return errors

    def get_task_order(self) -> list[str]:
        """Return topological order for task graph execution."""
        tasks_by_id = {task.task_id: task for task in self.tasks}
        in_degree = {task_id: 0 for task_id in tasks_by_id}
        adjacency: dict[str, list[str]] = {task_id: [] for task_id in tasks_by_id}

        for task in self.tasks:
            in_degree[task.task_id] += len(task.dependencies)
            for dep_id in task.dependencies:
                adjacency.setdefault(dep_id, []).append(task.task_id)

        queue = sorted(task_id for task_id, degree in in_degree.items() if degree == 0)
        order: list[str] = []
        while queue:
            current = queue.pop(0)
            order.append(current)
            for downstream in sorted(adjacency.get(current, [])):
                in_degree[downstream] -= 1
                if in_degree[downstream] == 0:
                    queue.append(downstream)

        if len(order) != len(tasks_by_id):
            raise ValueError("Pipeline task graph contains a cycle")
        return order


class PipelineDispatch(BaseModel):
    """Dispatch request/metadata for pipeline execution."""

    dispatch_id: str
    workflow_id: str
    pipeline_id: str
    session_id: str
    run_id: str
    dispatch_mode: Literal["sync", "async"] = "async"
    priority: int = 100
    requested_by: str
    started_at: datetime

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: int) -> int:
        """Restrict dispatch priority to non-negative values."""
        if v < 0:
            raise ValueError("priority must be >= 0")
        return v


class PipelineLineageRecord(BaseModel):
    """Typed handoff lineage record for cross-pipeline contracts."""

    correlation_id: str
    workflow_id: str
    from_pipeline_id: str
    to_pipeline_id: str
    output_name: str
    output_type: str
    input_name: str
    expected_input_type: str
    artifact_id: str
    created_at: datetime


class PipelineExecutionState(BaseModel):
    """Runtime state of a pipeline dispatch."""

    workflow_id: str
    pipeline_id: str
    dispatch_id: str
    status: PipelineExecutionStatus = PipelineExecutionStatus.CREATED
    runnable_tasks: list[str] = Field(default_factory=list)
    blocked_tasks: list[str] = Field(default_factory=list)
    completed_tasks: list[str] = Field(default_factory=list)
    failed_tasks: list[str] = Field(default_factory=list)
    last_transition_at: datetime = Field(default_factory=_utc_now)
    task_assignments: dict[str, TaskAssignment] = Field(default_factory=dict)
    lineage_records: list[PipelineLineageRecord] = Field(default_factory=list)

    def refresh_views(self, pipeline: PipelineDefinition) -> None:
        """Refresh runnable/blocked/completed/failed views from assignments."""
        runnable: list[str] = []
        blocked: list[str] = []
        completed: list[str] = []
        failed: list[str] = []

        completed_set = {
            task_id
            for task_id, assignment in self.task_assignments.items()
            if assignment.status == TaskAssignmentStatus.COMPLETED
        }

        for task in pipeline.tasks:
            assignment = self.task_assignments.get(task.task_id)
            if assignment is None:
                continue
            status = assignment.status
            if status == TaskAssignmentStatus.COMPLETED:
                completed.append(task.task_id)
                continue
            if status in (
                TaskAssignmentStatus.FAILED,
                TaskAssignmentStatus.CANCELLED,
            ):
                failed.append(task.task_id)
                continue

            deps_done = set(task.dependencies).issubset(completed_set)
            if status == TaskAssignmentStatus.ASSIGNED and deps_done:
                runnable.append(task.task_id)
            else:
                blocked.append(task.task_id)

        self.runnable_tasks = sorted(runnable)
        self.blocked_tasks = sorted(blocked)
        self.completed_tasks = sorted(completed)
        self.failed_tasks = sorted(failed)
        self.last_transition_at = _utc_now()

        if failed:
            self.status = PipelineExecutionStatus.FAILED
        elif len(completed) == len(pipeline.tasks):
            self.status = PipelineExecutionStatus.COMPLETED
        elif any(
            assignment.status == TaskAssignmentStatus.AWAITING_HUMAN
            for assignment in self.task_assignments.values()
        ):
            self.status = PipelineExecutionStatus.AWAITING_HUMAN
        elif runnable:
            self.status = PipelineExecutionStatus.RUNNING
        else:
            self.status = PipelineExecutionStatus.BLOCKED


class CanonicalWorkflowExecution(BaseModel):
    """Runtime execution state for canonical workflow -> pipeline -> task runs."""

    workflow_id: str
    execution_id: str
    status: PipelineExecutionStatus = PipelineExecutionStatus.CREATED
    pipeline_states: dict[str, PipelineExecutionState] = Field(default_factory=dict)
    pipeline_results: dict[str, PipelineResult] = Field(default_factory=dict)
    variables: dict[str, Any] = Field(default_factory=dict)
    published_artifacts: dict[str, ArtifactRecord] = Field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class PipelineResult(BaseModel):
    """Terminal pipeline result payload."""

    workflow_id: str
    pipeline_id: str
    dispatch_id: str
    status: Literal["completed", "failed", "cancelled"]
    output_artifacts: list[str] = Field(default_factory=list)
    failure_summary: str | None = None
    trace_ids: list[str] = Field(default_factory=list)
