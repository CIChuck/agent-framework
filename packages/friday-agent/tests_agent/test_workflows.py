# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""
Unit tests for workflow system.

Tests cover:
- TaskNode creation and validation (frozen/immutable)
- TaskState mutable runtime state
- WorkflowDefinition graph validation
- Cycle detection
- Topological sorting
- WorkflowEngine execution (state in WorkflowExecution, not TaskNode)
- Variable passing
- Approval gate pausing
- Task retry logic
- Workflow reusability (same definition, concurrent executions)

Ref: docs/build-plan/to-do/dynamic-workflows-build-plan.md
Ref: Phase 1 Build Plan, Step 3
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from friday_agent.workflows import (
    ArtifactPolicy,
    DelegationHandoff,
    HITLAuthorityPolicy,
    HITLDecision,
    HITLDecisionAction,
    HITLPolicy,
    PipelineDefinition,
    PipelineExecutionStatus,
    TaskDefinition,
    TaskNode,
    TaskState,
    TaskStatus,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowError,
    WorkflowExecution,
    WorkflowLoader,
    WorkflowLoadError,
    WorkflowPipelineDefinition,
)
from friday_memory.multi_agent import ScratchPadStore, ScratchPlanItemStatus
from friday_telemetry.providers.debug import DebugTelemetryRecorder
from pydantic import ValidationError


class TestTaskNode:
    """Test TaskNode model (immutable definition)."""

    def test_valid_task(self):
        """Test creating valid task."""
        task = TaskNode(
            id="research",
            name="Research Topic",
            description="Research the topic",
            agent="researcher",
        )
        assert task.id == "research"

    def test_task_id_normalized(self):
        """Test task ID is normalized to lowercase."""
        task = TaskNode(
            id="RESEARCH",
            name="Test",
            description="Test",
            agent="test",
        )
        assert task.id == "research"

    def test_task_with_dependencies(self):
        """Test task with dependencies and inputs."""
        task = TaskNode(
            id="analyze",
            name="Analyze Data",
            description="Analyze the data",
            agent="analyzer",
            depends_on=["research"],
            inputs={"data": "$research_output"},
            outputs=["analysis_result"],
        )
        assert task.depends_on == ("research",)
        assert task.inputs == {"data": "$research_output"}
        assert task.outputs == ("analysis_result",)

    def test_frozen_task_node(self):
        """Test that TaskNode is immutable (frozen)."""
        task = TaskNode(
            id="test",
            name="Test",
            description="Test",
            agent="test",
        )
        with pytest.raises(ValidationError):
            task.id = "modified"

    def test_frozen_status_not_on_task(self):
        """Test that status, result, error are NOT on TaskNode."""
        task = TaskNode(
            id="test",
            name="Test",
            description="Test",
            agent="test",
        )
        assert not hasattr(task, "status")
        assert not hasattr(task, "result")
        assert not hasattr(task, "error")
        assert not hasattr(task, "retry_count")

    def test_approval_required(self):
        """Test task with approval required."""
        task = TaskNode(
            id="review",
            name="Review",
            description="Review step",
            agent="reviewer",
            requires_approval=True,
        )
        assert task.requires_approval is True

    def test_retry_configuration(self):
        """Test task with retry configuration."""
        task = TaskNode(
            id="flaky",
            name="Flaky Task",
            description="May fail",
            agent="flaky",
            max_retries=3,
        )
        assert task.max_retries == 3

    def test_lists_coerced_to_tuples(self):
        """Test that list inputs for outputs/depends_on become tuples."""
        task = TaskNode(
            id="test",
            name="Test",
            description="Test",
            agent="test",
            outputs=["a", "b"],
            depends_on=["c"],
        )
        assert isinstance(task.outputs, tuple)
        assert isinstance(task.depends_on, tuple)

    def test_task_with_handoff_contract(self):
        """Test task with validated handoff contract."""
        task = TaskNode(
            id="handoff_task",
            name="Handoff Task",
            description="Delegated work",
            agent="reviewer",
            handoff=DelegationHandoff(
                handoff_id="handoff_123",
                ownership="reviewer",
                acceptance_criteria=["return checklist", "include verdict"],
                memory_scope="private_plus_shared",
            ),
        )
        assert task.handoff is not None
        assert task.handoff.handoff_id == "handoff_123"
        assert task.handoff.ownership == "reviewer"

    def test_task_with_skill_reference(self):
        """Test task supports canonical skill reference."""
        task = TaskNode(
            id="skill_task",
            name="Skill Task",
            description="Execute via skill",
            agent="reviewer",
            skill_ref="planner.basic@1.0.0",
        )
        assert task.skill_ref == "planner.basic@1.0.0"

    def test_task_rejects_invalid_skill_reference(self):
        """Test invalid skill reference raises validation error."""
        with pytest.raises(ValidationError, match="skill_ref"):
            TaskNode(
                id="skill_task",
                name="Skill Task",
                description="Execute via skill",
                agent="reviewer",
                skill_ref="invalid ref",
            )


class TestTaskState:
    """Test TaskState mutable runtime model."""

    def test_default_state(self):
        """Test default TaskState values."""
        state = TaskState()
        assert state.status == TaskStatus.PENDING
        assert state.result is None
        assert state.error is None
        assert state.retry_count == 0
        assert state.started_at is None
        assert state.completed_at is None

    def test_reset(self):
        """Test TaskState reset."""
        state = TaskState()
        state.status = TaskStatus.FAILED
        state.error = "Some error"
        state.result = "Some result"
        state.retry_count = 2
        state.reset()

        assert state.status == TaskStatus.PENDING
        assert state.error is None
        assert state.result is None
        # retry_count is preserved
        assert state.retry_count == 2

    def test_mutable(self):
        """Test that TaskState is mutable."""
        state = TaskState()
        state.status = TaskStatus.RUNNING
        assert state.status == TaskStatus.RUNNING


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

    @pytest.fixture
    def diamond_workflow(self):
        """Create diamond-shaped dependency workflow."""
        return WorkflowDefinition(
            id="diamond",
            name="Diamond Workflow",
            description="A -> B,C -> D",
            tasks=[
                TaskNode(id="a", name="A", description="Start", agent="x"),
                TaskNode(
                    id="b",
                    name="B",
                    description="Branch 1",
                    agent="x",
                    depends_on=["a"],
                ),
                TaskNode(
                    id="c",
                    name="C",
                    description="Branch 2",
                    agent="x",
                    depends_on=["a"],
                ),
                TaskNode(
                    id="d",
                    name="D",
                    description="Join",
                    agent="x",
                    depends_on=["b", "c"],
                ),
            ],
        )

    def test_get_task(self, simple_workflow):
        """Test getting task by ID."""
        task = simple_workflow.get_task("task_a")
        assert task is not None
        assert task.name == "Task A"

    def test_get_task_not_found(self, simple_workflow):
        """Test getting non-existent task."""
        task = simple_workflow.get_task("unknown")
        assert task is None

    def test_get_task_order(self, simple_workflow):
        """Test topological sort."""
        order = simple_workflow.get_task_order()
        assert order == ["task_a", "task_b"]

    def test_get_task_order_diamond(self, diamond_workflow):
        """Test topological sort with diamond."""
        order = diamond_workflow.get_task_order()
        # a must come first, d must come last
        assert order[0] == "a"
        assert order[-1] == "d"
        # b and c in middle (order may vary)
        assert set(order[1:3]) == {"b", "c"}

    def test_validate_graph_valid(self, simple_workflow):
        """Test validation passes for valid graph."""
        errors = simple_workflow.validate_graph()
        assert len(errors) == 0

    def test_validate_graph_duplicate_ids(self):
        """Test validation catches duplicate IDs."""
        workflow = WorkflowDefinition(
            id="dup",
            name="Duplicate",
            description="Has duplicates",
            tasks=[
                TaskNode(id="task", name="Task 1", description="A", agent="x"),
                TaskNode(id="task", name="Task 2", description="B", agent="x"),
            ],
        )
        errors = workflow.validate_graph()
        assert any("duplicate" in e.lower() for e in errors)

    def test_validate_graph_missing_dependency(self):
        """Test validation catches missing dependencies."""
        workflow = WorkflowDefinition(
            id="missing",
            name="Missing Dep",
            description="Has missing dep",
            tasks=[
                TaskNode(
                    id="b",
                    name="B",
                    description="B",
                    agent="x",
                    depends_on=["nonexistent"],
                ),
            ],
        )
        errors = workflow.validate_graph()
        assert any("unknown task" in e.lower() for e in errors)

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


class TestWorkflowExecution:
    """Test WorkflowExecution model."""

    def test_create_execution(self):
        """Test creating execution state."""
        execution = WorkflowExecution(
            workflow_id="test",
            execution_id="test_123",
            variables={"input": "value"},
        )
        assert execution.status == TaskStatus.PENDING
        assert execution.variables["input"] == "value"

    def test_get_task_state_creates_default(self):
        """Test get_task_state creates default state if missing."""
        execution = WorkflowExecution(
            workflow_id="test",
            execution_id="test_123",
        )
        state = execution.get_task_state("task_a")
        assert state.status == TaskStatus.PENDING
        assert "task_a" in execution.task_states

    def test_get_ready_tasks(self):
        """Test get_ready_tasks with task_states."""
        workflow = WorkflowDefinition(
            id="test",
            name="Test",
            description="Test",
            tasks=[
                TaskNode(
                    id="a",
                    name="A",
                    description="A",
                    agent="x",
                    outputs=["out"],
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
        execution = WorkflowExecution(
            workflow_id="test",
            execution_id="test_123",
        )
        execution.init_task_states(workflow)

        # Initially only A is ready
        ready = execution.get_ready_tasks(workflow)
        assert len(ready) == 1
        assert ready[0].id == "a"

        # Complete A, then B is ready
        execution.get_task_state("a").status = TaskStatus.COMPLETED
        ready = execution.get_ready_tasks(workflow)
        assert len(ready) == 1
        assert ready[0].id == "b"

    def test_record_task(self):
        """Test recording task in history."""
        execution = WorkflowExecution(
            workflow_id="test",
            execution_id="test_123",
        )
        task = TaskNode(
            id="task",
            name="Task",
            description="Test",
            agent="x",
        )
        state = execution.get_task_state("task")
        state.status = TaskStatus.COMPLETED

        execution.record_task(task)

        assert len(execution.task_history) == 1
        assert execution.task_history[0]["task_id"] == "task"
        assert execution.task_history[0]["status"] == "completed"

    def test_approval_overrides(self):
        """Test approval_overrides tracking."""
        execution = WorkflowExecution(
            workflow_id="test",
            execution_id="test_123",
        )
        execution.approval_overrides.add("task_a")
        assert "task_a" in execution.approval_overrides


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
    async def test_execute_with_dependencies(self, engine, mock_orchestrator):
        """Test workflow with dependencies."""
        mock_orchestrator.delegate = AsyncMock(
            side_effect=["First result", "Second result"]
        )

        workflow = WorkflowDefinition(
            id="test",
            name="Test",
            description="Test",
            tasks=[
                TaskNode(
                    id="first",
                    name="First",
                    description="First task",
                    agent="agent",
                    outputs=["first_output"],
                ),
                TaskNode(
                    id="second",
                    name="Second",
                    description="Second task",
                    agent="agent",
                    depends_on=["first"],
                    inputs={"data": "$first_output"},
                ),
            ],
        )

        execution = await engine.execute(workflow)

        assert execution.status == TaskStatus.COMPLETED
        assert mock_orchestrator.delegate.call_count == 2
        assert execution.variables["first_output"] == "First result"

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
    async def test_approval_callback_auto_approves(self, mock_orchestrator):
        """Test approval callback that auto-approves."""

        async def auto_approve(task):
            return True

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

        engine = WorkflowEngine(mock_orchestrator, approval_callback=auto_approve)
        execution = await engine.execute(workflow)

        assert execution.status == TaskStatus.COMPLETED

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
        execution = await engine.approve_task(workflow, execution, "approval_task")

        assert execution.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_approve_task_uses_overrides(self, mock_orchestrator):
        """Test that approve_task records in approval_overrides."""
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

        execution = await engine.approve_task(workflow, execution, "approval_task")

        # Approval override should be recorded
        assert "approval_task" in execution.approval_overrides

    @pytest.mark.asyncio
    async def test_skip_task(self, mock_orchestrator):
        """Test skipping a task."""
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

        # Skip the task
        execution = await engine.skip_task(workflow, execution, "approval_task")

        assert execution.status == TaskStatus.COMPLETED
        state = execution.get_task_state("approval_task")
        assert state.status == TaskStatus.SKIPPED

    @pytest.mark.asyncio
    async def test_resolve_task_reject(self, mock_orchestrator):
        """Test resolving a waiting task with reject decision."""
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
        execution = await engine.resolve_task(
            workflow, execution, "approval_task", decision="reject"
        )

        assert execution.status == TaskStatus.COMPLETED
        state = execution.get_task_state("approval_task")
        assert state.status == TaskStatus.SKIPPED
        assert state.error == "Rejected during approval"

    @pytest.mark.asyncio
    async def test_hitl_request_payload_created_on_pause(self, mock_orchestrator):
        """Test paused workflow includes structured HITL request payload."""
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
        hitl_policy = HITLPolicy(
            enabled=True,
            methods=["approval_gate"],
            timeout_seconds=60,
            default_action_on_timeout="safe_abort",
            authority_policy=HITLAuthorityPolicy(allowed_roles=["owner"]),
        )

        engine = WorkflowEngine(
            mock_orchestrator, approval_callback=None, hitl_policy=hitl_policy
        )
        execution = await engine.execute(workflow)

        assert execution.status == TaskStatus.WAITING_APPROVAL
        assert execution.pending_hitl_request is not None
        assert execution.pending_hitl_request.task_id == "approval_task"
        assert execution.pending_hitl_request.default_action_on_timeout == "safe_abort"
        assert execution.pending_hitl_request.request_id.startswith("hitl_")

    @pytest.mark.asyncio
    async def test_hitl_authority_rejects_unauthorized_approver(
        self, mock_orchestrator
    ):
        """Test authority policy blocks unauthorized HITL decisions."""
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
        hitl_policy = HITLPolicy(
            enabled=True,
            methods=["approval_gate"],
            timeout_seconds=60,
            default_action_on_timeout="safe_abort",
            authority_policy=HITLAuthorityPolicy(
                allowed_roles=["owner"],
                decision_scope={"approval_gate": ["owner"]},
            ),
        )

        engine = WorkflowEngine(
            mock_orchestrator, approval_callback=None, hitl_policy=hitl_policy
        )
        execution = await engine.execute(workflow)
        assert execution.pending_hitl_request is not None

        with pytest.raises(WorkflowError, match="not authorized"):
            await engine.decide_task(
                workflow=workflow,
                execution=execution,
                decision=HITLDecision(
                    request_id=execution.pending_hitl_request.request_id,
                    task_id="approval_task",
                    decision=HITLDecisionAction.APPROVED,
                    approver_id="user_1",
                    approver_role="viewer",
                    reason="attempted",
                    responded_at=execution.pending_hitl_request.created_at,
                ),
            )

    @pytest.mark.asyncio
    async def test_hitl_timeout_default_constrained_continue(self, mock_orchestrator):
        """Test timeout default action can deterministically continue execution."""
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
        hitl_policy = HITLPolicy(
            enabled=True,
            methods=["approval_gate"],
            timeout_seconds=0,
            default_action_on_timeout="constrained_continue",
            authority_policy=HITLAuthorityPolicy(allowed_roles=["owner"]),
        )
        engine = WorkflowEngine(
            mock_orchestrator, approval_callback=None, hitl_policy=hitl_policy
        )
        execution = await engine.execute(workflow)
        assert execution.status == TaskStatus.WAITING_APPROVAL

        execution = await engine.apply_pending_timeouts(workflow, execution)

        assert execution.status == TaskStatus.COMPLETED
        assert execution.pending_approval is None
        assert execution.pending_hitl_request is None

    @pytest.mark.asyncio
    async def test_hitl_timeout_default_safe_abort(self, mock_orchestrator):
        """Test timeout default safe_abort transitions workflow to failed."""
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
        hitl_policy = HITLPolicy(
            enabled=True,
            methods=["approval_gate"],
            timeout_seconds=0,
            default_action_on_timeout="safe_abort",
            authority_policy=HITLAuthorityPolicy(allowed_roles=["owner"]),
        )
        engine = WorkflowEngine(
            mock_orchestrator, approval_callback=None, hitl_policy=hitl_policy
        )
        execution = await engine.execute(workflow)
        assert execution.status == TaskStatus.WAITING_APPROVAL

        execution = await engine.apply_pending_timeouts(workflow, execution)
        assert execution.status == TaskStatus.FAILED
        assert execution.get_task_state("approval_task").status == TaskStatus.FAILED

    def test_artifact_lifecycle_and_publication_controls(self, mock_orchestrator):
        """Test artifact lifecycle validity, provenance checks, and publication approval."""  # noqa: E501
        hitl_policy = HITLPolicy(
            enabled=True,
            methods=["approval_gate"],
            timeout_seconds=60,
            default_action_on_timeout="safe_abort",
            authority_policy=HITLAuthorityPolicy(allowed_roles=["publisher"]),
        )
        artifact_policy = ArtifactPolicy(
            lifecycle_states=["draft", "validated", "final", "archived"],
            publication_requires_approval=True,
            required_provenance_fields=["correlation_id", "created_by"],
        )
        engine = WorkflowEngine(
            mock_orchestrator,
            hitl_policy=hitl_policy,
            artifact_policy=artifact_policy,
        )
        execution = WorkflowExecution(workflow_id="w", execution_id="e")

        with pytest.raises(WorkflowError, match="provenance missing"):
            engine.register_artifact(
                execution=execution,
                artifact_id="artifact_1",
                created_by="agent_1",
                provenance={"correlation_id": "corr_1"},
            )

        engine.register_artifact(
            execution=execution,
            artifact_id="artifact_1",
            created_by="agent_1",
            provenance={"correlation_id": "corr_1", "created_by": "agent_1"},
        )
        engine.transition_artifact(execution, "artifact_1", "validated")

        with pytest.raises(WorkflowError, match="requires approver identity"):
            engine.transition_artifact(execution, "artifact_1", "final")

        with pytest.raises(WorkflowError, match="not authorized for publication"):
            engine.transition_artifact(
                execution,
                "artifact_1",
                "final",
                approver_id="user_1",
                approver_role="viewer",
            )

        engine.transition_artifact(
            execution,
            "artifact_1",
            "final",
            approver_id="user_2",
            approver_role="publisher",
        )
        assert execution.artifacts["artifact_1"].lifecycle_state.value == "final"
        assert execution.artifacts["artifact_1"].published_at is not None

    @pytest.mark.asyncio
    async def test_task_handoff_payload_passed_to_delegate(self, mock_orchestrator):
        """Test handoff contract is passed as delegation payload."""
        workflow = WorkflowDefinition(
            id="test",
            name="Test",
            description="Test",
            tasks=[
                TaskNode(
                    id="handoff_task",
                    name="Handoff",
                    description="Delegated task",
                    agent="agent",
                    handoff=DelegationHandoff(
                        handoff_id="handoff_001",
                        ownership="agent",
                        acceptance_criteria=["emit summary"],
                        memory_scope="private_only",
                    ),
                ),
            ],
        )

        engine = WorkflowEngine(mock_orchestrator)
        execution = await engine.execute(workflow)

        assert execution.status == TaskStatus.COMPLETED
        _, kwargs = mock_orchestrator.delegate.call_args
        assert kwargs["handoff_payload"]["handoff_id"] == "handoff_001"
        assert kwargs["handoff_payload"]["ownership"] == "agent"

    @pytest.mark.asyncio
    async def test_task_skill_ref_routes_delegate_agent(self, mock_orchestrator):
        """Test task skill_ref resolves target agent dynamically."""
        mock_orchestrator.resolve_agent_for_skill = MagicMock(
            return_value="skill_agent"
        )
        workflow = WorkflowDefinition(
            id="test",
            name="Test",
            description="Test",
            tasks=[
                TaskNode(
                    id="skill_task",
                    name="Skill Task",
                    description="Delegated via skill",
                    agent="fallback_agent",
                    skill_ref="planner.basic@1.0.0",
                ),
            ],
        )

        engine = WorkflowEngine(mock_orchestrator)
        execution = await engine.execute(workflow)

        assert execution.status == TaskStatus.COMPLETED
        mock_orchestrator.resolve_agent_for_skill.assert_called_once_with(
            "planner.basic@1.0.0",
            preferred_agent="fallback_agent",
        )
        args, kwargs = mock_orchestrator.delegate.call_args
        assert args[0] == "skill_agent"
        assert kwargs["skill_ref"] == "planner.basic@1.0.0"

    @pytest.mark.asyncio
    async def test_scratchpad_tracks_task_statuses(self, mock_orchestrator):
        """Test workflow task statuses map to scratch pad plan item lifecycle."""
        scratchpad = ScratchPadStore(ttl_seconds=300, max_entries=100)
        workflow = WorkflowDefinition(
            id="scratch",
            name="Scratch Workflow",
            description="scratch mapping",
            tasks=[
                TaskNode(
                    id="task_a",
                    name="Task A",
                    description="Do A",
                    agent="agent",
                ),
            ],
        )
        engine = WorkflowEngine(mock_orchestrator, scratchpad=scratchpad)
        execution = await engine.execute(workflow)
        scope = f"{execution.workflow_id}:{execution.execution_id}"
        pad = scratchpad.get_pad(scope)

        assert execution.status == TaskStatus.COMPLETED
        assert pad is not None
        assert pad.plan_items["task_a"].status == ScratchPlanItemStatus.COMPLETED
        event_types = [event.event_type for event in pad.events]
        assert "workflow_started" in event_types
        assert "task_started" in event_types
        assert "task_completed" in event_types
        assert "workflow_completed" in event_types

    @pytest.mark.asyncio
    async def test_scratchpad_records_hitl_pause_resume(self, mock_orchestrator):
        """Test HITL pause/resume checkpoints are written to scratch event log."""
        scratchpad = ScratchPadStore(ttl_seconds=300, max_entries=100)
        workflow = WorkflowDefinition(
            id="hitl_scratch",
            name="HITL Scratch",
            description="hitl + scratch",
            tasks=[
                TaskNode(
                    id="review",
                    name="Review",
                    description="Needs approval",
                    agent="agent",
                    requires_approval=True,
                ),
            ],
        )
        engine = WorkflowEngine(mock_orchestrator, scratchpad=scratchpad)
        paused = await engine.execute(workflow)

        assert paused.status == TaskStatus.WAITING_APPROVAL
        assert paused.pending_hitl_request is not None

        decision = HITLDecision(
            request_id=paused.pending_hitl_request.request_id,
            task_id="review",
            decision=HITLDecisionAction.APPROVED,
            approver_id="user_1",
            approver_role="reviewer",
            reason="approved",
            responded_at=paused.pending_hitl_request.created_at,
        )
        resumed = await engine.decide_task(workflow, paused, decision)
        scope = f"{resumed.workflow_id}:{resumed.execution_id}"
        pad = scratchpad.get_pad(scope)

        assert resumed.status == TaskStatus.COMPLETED
        assert pad is not None
        assert pad.plan_items["review"].status == ScratchPlanItemStatus.COMPLETED
        event_types = [event.event_type for event in pad.events]
        assert "hitl_waiting" in event_types
        assert "hitl_decision" in event_types
        assert "workflow_resumed" in event_types

    @pytest.mark.asyncio
    async def test_missing_variable_error(self, engine):
        """Test error when variable is missing."""
        workflow = WorkflowDefinition(
            id="test",
            name="Test",
            description="Test",
            tasks=[
                TaskNode(
                    id="task",
                    name="Task",
                    description="Test",
                    agent="agent",
                    inputs={"data": "$missing_variable"},
                ),
            ],
        )

        with pytest.raises(WorkflowError) as exc_info:
            await engine.execute(workflow)

        assert "missing variable" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_invalid_workflow_error(self, engine):
        """Test error with invalid workflow."""
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

        with pytest.raises(WorkflowError) as exc_info:
            await engine.execute(workflow)

        assert "invalid workflow" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_workflow_reusability(self, mock_orchestrator):
        """
        Test that the same WorkflowDefinition can be executed
        concurrently without state collision.

        Exit Criterion #5: Workflow Reusability.
        """
        call_count = 0

        async def slow_delegate(agent_name, prompt, return_to_current=True):
            nonlocal call_count
            call_count += 1
            count = call_count
            await asyncio.sleep(0.01)
            return f"Result {count}"

        mock_orchestrator.delegate = AsyncMock(side_effect=slow_delegate)

        # Same definition, two engines (or same engine, doesn't matter)
        workflow = WorkflowDefinition(
            id="reuse",
            name="Reusable",
            description="Test reusability",
            tasks=[
                TaskNode(
                    id="task_a",
                    name="Task A",
                    description="Do A",
                    agent="agent",
                    outputs=["out"],
                ),
            ],
        )

        engine = WorkflowEngine(mock_orchestrator)

        # Execute the same definition concurrently
        exec1, exec2 = await asyncio.gather(
            engine.execute(workflow),
            engine.execute(workflow),
        )

        # Both should complete independently
        assert exec1.status == TaskStatus.COMPLETED
        assert exec2.status == TaskStatus.COMPLETED

        # They should have different execution IDs
        assert exec1.execution_id != exec2.execution_id

        # Each has its own task state
        assert exec1.get_task_state("task_a").status == TaskStatus.COMPLETED
        assert exec2.get_task_state("task_a").status == TaskStatus.COMPLETED

    def test_task_node_immutability(self):
        """
        Test that TaskNode cannot be mutated.

        Exit Criterion #6: Workflow Immutability.
        """
        task = TaskNode(
            id="test",
            name="Test",
            description="Test",
            agent="test",
        )
        with pytest.raises(ValidationError):
            task.name = "Modified"
        with pytest.raises(ValidationError):
            task.requires_approval = True


class TestWorkflowLoader:
    """Test WorkflowLoader."""

    @pytest.fixture
    def temp_workflows_dir(self):
        """Create temporary workflows directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_workflow_yaml(self):
        """Sample workflow YAML content."""
        return """
id: sample
name: "Sample Workflow"
description: "A sample workflow for testing"
tasks:
  - id: task_a
    name: "Task A"
    description: "First task"
    agent: agent1
    outputs:
      - result_a

  - id: task_b
    name: "Task B"
    description: "Second task"
    agent: agent2
    depends_on:
      - task_a
    inputs:
      data: "$result_a"
"""

    def test_load_workflow(self, temp_workflows_dir, sample_workflow_yaml):
        """Test loading workflow from YAML."""
        # Write sample workflow
        workflow_path = temp_workflows_dir / "sample.yaml"
        workflow_path.write_text(sample_workflow_yaml)

        loader = WorkflowLoader(temp_workflows_dir)
        workflow = loader.load("sample")

        assert workflow.id == "sample"
        assert workflow.name == "Sample Workflow"
        assert len(workflow.tasks) == 2

    def test_load_workflow_yml_extension(
        self, temp_workflows_dir, sample_workflow_yaml
    ):
        """Test loading workflow with .yml extension."""
        workflow_path = temp_workflows_dir / "sample.yml"
        workflow_path.write_text(sample_workflow_yaml)

        loader = WorkflowLoader(temp_workflows_dir)
        workflow = loader.load("sample")

        assert workflow.id == "sample"

    def test_load_workflow_not_found(self, temp_workflows_dir):
        """Test error when workflow not found."""
        loader = WorkflowLoader(temp_workflows_dir)

        with pytest.raises(WorkflowLoadError) as exc_info:
            loader.load("nonexistent")

        assert "not found" in str(exc_info.value).lower()

    def test_load_workflow_invalid_yaml(self, temp_workflows_dir):
        """Test error with invalid YAML."""
        workflow_path = temp_workflows_dir / "invalid.yaml"
        workflow_path.write_text("not: valid: yaml: [")

        loader = WorkflowLoader(temp_workflows_dir)

        with pytest.raises(WorkflowLoadError) as exc_info:
            loader.load("invalid")

        assert "yaml" in str(exc_info.value).lower()

    def test_load_workflow_missing_fields(self, temp_workflows_dir):
        """Test error with missing required fields."""
        workflow_path = temp_workflows_dir / "incomplete.yaml"
        workflow_path.write_text("id: test\nname: Test")

        loader = WorkflowLoader(temp_workflows_dir)

        with pytest.raises(WorkflowLoadError) as exc_info:
            loader.load("incomplete")

        assert "missing" in str(exc_info.value).lower()

    def test_load_all_workflows(self, temp_workflows_dir, sample_workflow_yaml):
        """Test loading all workflows."""
        # Write multiple workflows
        (temp_workflows_dir / "workflow1.yaml").write_text(
            sample_workflow_yaml.replace("sample", "workflow1")
        )
        (temp_workflows_dir / "workflow2.yml").write_text(
            sample_workflow_yaml.replace("sample", "workflow2")
        )

        loader = WorkflowLoader(temp_workflows_dir)
        workflows = loader.load_all()

        assert len(workflows) == 2
        assert "workflow1" in workflows
        assert "workflow2" in workflows

    def test_list_workflows(self, temp_workflows_dir, sample_workflow_yaml):
        """Test listing available workflows."""
        (temp_workflows_dir / "alpha.yaml").write_text(
            sample_workflow_yaml.replace("sample", "alpha")
        )
        (temp_workflows_dir / "beta.yml").write_text(
            sample_workflow_yaml.replace("sample", "beta")
        )

        loader = WorkflowLoader(temp_workflows_dir)
        names = loader.list_workflows()

        assert names == ["alpha", "beta"]

    def test_workflow_caching(self, temp_workflows_dir, sample_workflow_yaml):
        """Test workflow caching."""
        workflow_path = temp_workflows_dir / "sample.yaml"
        workflow_path.write_text(sample_workflow_yaml)

        loader = WorkflowLoader(temp_workflows_dir)

        # Load twice
        workflow1 = loader.load("sample")
        workflow2 = loader.load("sample")

        # Should be same object (cached)
        assert workflow1 is workflow2

    def test_reload_bypasses_cache(self, temp_workflows_dir, sample_workflow_yaml):
        """Test reload bypasses cache."""
        workflow_path = temp_workflows_dir / "sample.yaml"
        workflow_path.write_text(sample_workflow_yaml)

        loader = WorkflowLoader(temp_workflows_dir)

        workflow1 = loader.load("sample")

        # Modify file
        workflow_path.write_text(
            sample_workflow_yaml.replace("Sample Workflow", "Updated Workflow")
        )

        workflow2 = loader.reload("sample")

        assert workflow1 is not workflow2
        assert workflow2.name == "Updated Workflow"

    def test_load_canonical_workflow_bundle(self, temp_workflows_dir):
        """Test loading canonical workflow and pipeline YAML bundle."""
        workflow_dir = temp_workflows_dir / "wf_analysis"
        pipelines_dir = workflow_dir / "pipelines"
        pipelines_dir.mkdir(parents=True)
        (workflow_dir / "workflow.yaml").write_text(
            """
workflow_id: wf_analysis
version: 1.0.0
name: Analysis
goal: Analyze input
pipeline_refs:
  - pl_analysis
entry_pipeline_id: pl_analysis
required_artifacts:
  - artifact_id: summary_artifact
    type: markdown
    produced_by_pipeline: pl_analysis
""".strip()
        )
        (pipelines_dir / "pl_analysis.yaml").write_text(
            """
pipeline_id: pl_analysis
version: 1.0.0
workflow_id: wf_analysis
goal: Analyze input
upstream_pipeline_ids: []
input_contract:
  source_paths: list[str]
output_contract:
  summary_artifact: markdown
artifact_contract:
  produced:
    - artifact_id: summary_artifact
      type: markdown
      producer_task_id: write_summary
  consumed: []
tasks:
  - task_id: write_summary
    name: Write Summary
    description: Create summary.
    owner_agent_id: analyst
    input_contract:
      source_paths: list[str]
    output_contract:
      summary_artifact: markdown
    output_artifacts:
      - artifact_id: summary_artifact
        from_output: summary_artifact
        type: markdown
        required: true
    dependencies: []
    retry_policy:
      max_attempts: 1
""".strip()
        )

        loader = WorkflowLoader(temp_workflows_dir)
        bundle = loader.load_canonical("wf_analysis")

        assert bundle.workflow.workflow_id == "wf_analysis"
        assert isinstance(bundle.workflow, WorkflowPipelineDefinition)
        assert set(bundle.pipelines) == {"pl_analysis"}
        assert bundle.pipelines["pl_analysis"].artifact_contract.produced[0].artifact_id == (
            "summary_artifact"
        )

    def test_list_workflows_includes_canonical_workflow_dirs(self, temp_workflows_dir):
        """Test list_workflows includes canonical workflow directories."""
        workflow_dir = temp_workflows_dir / "wf_dir"
        workflow_dir.mkdir()
        (workflow_dir / "workflow.yaml").write_text(
            """
workflow_id: wf_dir
version: 1.0.0
name: Workflow Dir
goal: Example
pipeline_refs:
  - pl_one
""".strip()
        )

        loader = WorkflowLoader(temp_workflows_dir)
        assert loader.list_workflows() == ["wf_dir"]

    def test_load_legacy_workflow_as_canonical_bundle(self, temp_workflows_dir):
        """Test adapting a legacy flat workflow into a canonical bundle."""
        (temp_workflows_dir / "legacy.yaml").write_text(
            """
id: legacy
name: Legacy Workflow
description: Legacy workflow path
tasks:
  - id: research
    name: Research
    description: Gather input.
    agent: researcher
    inputs:
      source_paths: $source_paths
      mode: deep
    outputs:
      - evidence_bundle
  - id: synthesize
    name: Synthesize
    description: Create report.
    agent: synthesizer
    depends_on:
      - research
    inputs:
      evidence_bundle: $evidence_bundle
    outputs:
      - final_report
""".strip()
        )

        loader = WorkflowLoader(temp_workflows_dir)
        bundle = loader.load_legacy_as_canonical("legacy")

        assert bundle.workflow.workflow_id == "legacy"
        assert bundle.workflow.pipeline_refs == ("legacy_legacy_pipeline",)
        pipeline = bundle.pipelines["legacy_legacy_pipeline"]
        assert pipeline.entrypoints == ("research",)
        assert pipeline.input_contract == {"source_paths": "any"}
        assert pipeline.output_contract == {"final_report": "any"}
        assert pipeline.tasks[0].input_bindings == {
            "source_paths": "$source_paths",
            "mode": "deep",
        }
        assert pipeline.tasks[1].dependencies == ("research",)


class TestCanonicalWorkflowEngine:
    """Tests for canonical workflow -> pipeline -> task execution."""

    @pytest.mark.asyncio
    async def test_execute_canonical_workflow_resolves_owner_role_and_outputs(self):
        mock_orchestrator = MagicMock()
        mock_orchestrator.delegate = AsyncMock(
            side_effect=[
                {"evidence_bundle": {"sources": 3}},
                {"recommendation_report": "# Final"},
            ]
        )
        telemetry = DebugTelemetryRecorder()
        agent_info = {
            "researcher": {"llm_service": "research-tier"},
            "synthesizer": {"llm_service": "synthesis-tier"},
        }
        engine = WorkflowEngine(
            mock_orchestrator,
            telemetry=telemetry,
            agent_info_resolver=agent_info.get,
        )

        workflow = WorkflowPipelineDefinition(
            workflow_id="wf_research",
            version="1.0.0",
            name="Research",
            goal="Produce report",
            pipeline_refs=("pl_research", "pl_synthesis"),
            entry_pipeline_id="pl_research",
            required_artifacts=[
                {
                    "artifact_id": "recommendation_report",
                    "type": "markdown",
                    "produced_by_pipeline": "pl_synthesis",
                }
            ],
        )

        pipelines = {
            "pl_research": PipelineDefinition(
                pipeline_id="pl_research",
                version="1.0.0",
                workflow_id="wf_research",
                goal="Research",
                upstream_pipeline_ids=(),
                input_contract={"source_paths": "list[str]"},
                output_contract={"evidence_bundle": "json"},
                artifact_contract={
                    "produced": [
                        {
                            "artifact_id": "evidence_bundle",
                            "type": "json",
                            "producer_task_id": "collect_sources",
                        }
                    ],
                    "consumed": [],
                },
                tasks=[
                    TaskDefinition(
                        task_id="collect_sources",
                        name="Collect Sources",
                        description="Collect sources.",
                        owner_agent_id="researcher",
                        input_contract={"source_paths": "list[str]"},
                        output_contract={"evidence_bundle": "json"},
                        output_artifacts=[
                            {
                                "artifact_id": "evidence_bundle",
                                "from_output": "evidence_bundle",
                                "type": "json",
                                "required": True,
                            }
                        ],
                    )
                ],
            ),
            "pl_synthesis": PipelineDefinition(
                pipeline_id="pl_synthesis",
                version="1.0.0",
                workflow_id="wf_research",
                goal="Synthesize",
                upstream_pipeline_ids=("pl_research",),
                input_contract={"evidence_bundle": "json"},
                output_contract={"recommendation_report": "markdown"},
                artifact_contract={
                    "produced": [
                        {
                            "artifact_id": "recommendation_report",
                            "type": "markdown",
                            "producer_task_id": "produce_recommendations",
                        }
                    ],
                    "consumed": [
                        {
                            "artifact_id": "evidence_bundle",
                            "type": "json",
                            "from_pipeline": "pl_research",
                        }
                    ],
                },
                tasks=[
                    TaskDefinition(
                        task_id="produce_recommendations",
                        name="Produce Recommendations",
                        description="Produce recommendation report.",
                        owner_role="synthesis",
                        input_contract={"evidence_bundle": "json"},
                        output_contract={"recommendation_report": "markdown"},
                        output_artifacts=[
                            {
                                "artifact_id": "recommendation_report",
                                "from_output": "recommendation_report",
                                "type": "markdown",
                                "required": True,
                            }
                        ],
                    )
                ],
            ),
        }

        execution = await engine.execute_canonical(
            workflow,
            pipelines,
            {"source_paths": ["a.md", "b.md"]},
            role_bindings={"synthesis": "synthesizer"},
        )

        assert execution.status == PipelineExecutionStatus.COMPLETED
        assert execution.variables["evidence_bundle"] == {"sources": 3}
        assert execution.variables["recommendation_report"] == "# Final"
        assert execution.pipeline_results["pl_research"].status == "completed"
        assert execution.pipeline_results["pl_synthesis"].status == "completed"
        assert execution.pipeline_results["pl_synthesis"].output_artifacts == [
            "recommendation_report"
        ]
        assert "recommendation_report" in execution.published_artifacts
        assert (
            execution.published_artifacts["recommendation_report"].provenance[
                "output_ref"
            ]
            == "# Final"
        )
        assert mock_orchestrator.delegate.call_args_list[1].args[0] == "synthesizer"
        assert execution.pipeline_states["pl_synthesis"].lineage_records[0].artifact_id == (
            "evidence_bundle"
        )
        task_events = telemetry.get_all_events("workflow_task_completed")
        assert len(task_events) == 2
        assert task_events[0]["llm_service"] == "research-tier"
        assert task_events[1]["llm_service"] == "synthesis-tier"
        assert telemetry.get_event("workflow_typed_handoff_validated") is not None
        assert telemetry.get_event("workflow_artifact_published") is not None

    @pytest.mark.asyncio
    async def test_execute_canonical_workflow_supports_legacy_input_bindings(self):
        """Test canonical execution resolves explicit input bindings for adapted legacy tasks."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.delegate = AsyncMock(
            side_effect=[
                {"evidence_bundle": {"sources": 2, "mode": "deep"}},
                {"final_report": "# Report"},
            ]
        )
        engine = WorkflowEngine(mock_orchestrator)

        workflow = WorkflowPipelineDefinition(
            workflow_id="legacy",
            version="1.0.0",
            name="Legacy",
            goal="Legacy adapted workflow",
            pipeline_refs=("legacy_pipeline",),
        )
        pipelines = {
            "legacy_pipeline": PipelineDefinition(
                pipeline_id="legacy_pipeline",
                version="1.0.0",
                workflow_id="legacy",
                goal="Legacy pipeline",
                input_contract={"source_paths": "any"},
                output_contract={"final_report": "any"},
                tasks=[
                    TaskDefinition(
                        task_id="research",
                        name="Research",
                        description="Gather sources.",
                        owner_agent_id="researcher",
                        input_contract={"source_paths": "any", "mode": "any"},
                        input_bindings={"source_paths": "$source_paths", "mode": "deep"},
                        output_contract={"evidence_bundle": "any"},
                    ),
                    TaskDefinition(
                        task_id="synthesize",
                        name="Synthesize",
                        description="Write report.",
                        owner_agent_id="synthesizer",
                        input_contract={"evidence_bundle": "any"},
                        input_bindings={"evidence_bundle": "$evidence_bundle"},
                        output_contract={"final_report": "any"},
                        dependencies=("research",),
                    ),
                ],
            )
        }

        execution = await engine.execute_canonical(
            workflow,
            pipelines,
            {"source_paths": ["a.md"]},
        )

        assert execution.status == PipelineExecutionStatus.COMPLETED
        first_prompt = mock_orchestrator.delegate.call_args_list[0].args[1]
        assert "- mode: deep" in first_prompt
        assert execution.variables["final_report"] == "# Report"

    @pytest.mark.asyncio
    async def test_execute_canonical_workflow_fails_when_required_artifact_missing(self):
        mock_orchestrator = MagicMock()
        mock_orchestrator.delegate = AsyncMock(return_value={"result": "ok"})
        engine = WorkflowEngine(mock_orchestrator)

        workflow = WorkflowPipelineDefinition(
            workflow_id="wf_missing_artifact",
            version="1.0.0",
            name="Missing Artifact",
            goal="Test failure",
            pipeline_refs=("pl_one",),
            required_artifacts=[
                {
                    "artifact_id": "required_artifact",
                    "type": "markdown",
                    "produced_by_pipeline": "pl_one",
                }
            ],
        )
        pipelines = {
            "pl_one": PipelineDefinition(
                pipeline_id="pl_one",
                version="1.0.0",
                workflow_id="wf_missing_artifact",
                goal="Only pipeline",
                output_contract={"result": "markdown"},
                tasks=[
                    TaskDefinition(
                        task_id="task_one",
                        name="Task One",
                        description="Do work.",
                        owner_agent_id="agent",
                        output_contract={"result": "markdown"},
                    )
                ],
            )
        }

        with pytest.raises(WorkflowError, match="missing required artifact"):
            await engine.execute_canonical(workflow, pipelines)
