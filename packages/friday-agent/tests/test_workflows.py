"""
Unit tests for workflow system.

Tests cover:
- TaskNode creation and validation
- WorkflowDefinition graph validation
- Cycle detection
- Topological sorting
- WorkflowEngine execution
- Variable passing
- Approval gate pausing
- Task retry logic

Ref: docs/build-plan/to-do/dynamic-workflows-build-plan.md
"""

import tempfile
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, MagicMock

from friday_agent.workflows import (
    TaskNode,
    TaskStatus,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowEngine,
    WorkflowError,
    WorkflowLoader,
    WorkflowLoadError,
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
        assert task.depends_on == ["research"]
        assert task.inputs == {"data": "$research_output"}
        assert task.outputs == ["analysis_result"]

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
        task.result = "Some result"
        task.reset()

        assert task.status == TaskStatus.PENDING
        assert task.error is None
        assert task.result is None

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
        assert task.retry_count == 0


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
                TaskNode(id="b", name="B", description="Branch 1", agent="x", depends_on=["a"]),
                TaskNode(id="c", name="C", description="Branch 2", agent="x", depends_on=["a"]),
                TaskNode(id="d", name="D", description="Join", agent="x", depends_on=["b", "c"]),
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

    def test_get_ready_tasks_initial(self, simple_workflow):
        """Test getting ready tasks at start."""
        ready = simple_workflow.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == "task_a"

    def test_get_ready_tasks_after_completion(self, simple_workflow):
        """Test getting ready tasks after task completion."""
        # Complete first task
        simple_workflow.tasks[0].status = TaskStatus.COMPLETED
        ready = simple_workflow.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == "task_b"

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
        task.status = TaskStatus.COMPLETED

        execution.record_task(task)

        assert len(execution.task_history) == 1
        assert execution.task_history[0]["task_id"] == "task"
        assert execution.task_history[0]["status"] == "completed"


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
        assert workflow.get_task("approval_task").status == TaskStatus.SKIPPED

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
                TaskNode(id="a", name="A", description="A", agent="x", depends_on=["b"]),
                TaskNode(id="b", name="B", description="B", agent="x", depends_on=["a"]),
            ],
        )

        with pytest.raises(WorkflowError) as exc_info:
            await engine.execute(workflow)

        assert "invalid workflow" in str(exc_info.value).lower()


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

    def test_load_workflow_yml_extension(self, temp_workflows_dir, sample_workflow_yaml):
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
        workflow_path.write_text(sample_workflow_yaml.replace("Sample Workflow", "Updated Workflow"))

        workflow2 = loader.reload("sample")

        assert workflow1 is not workflow2
        assert workflow2.name == "Updated Workflow"
