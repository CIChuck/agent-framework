"""
Workflow execution engine.

Ref: docs/build-plan/to-do/dynamic-workflows-build-plan.md
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
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


def _utc_now() -> datetime:
    """Return current UTC time with timezone awareness."""
    return datetime.now(timezone.utc)


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
        orchestrator: "AgentOrchestrator",
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
            execution_id=f"{workflow.id}_{int(_utc_now().timestamp())}",
            variables=initial_inputs or {},
            started_at=_utc_now(),
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
            if execution.status != TaskStatus.WAITING_APPROVAL:
                execution.completed_at = _utc_now()

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
                    (
                        t
                        for t in workflow.tasks
                        if t.status == TaskStatus.WAITING_APPROVAL
                    ),
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
        task.started_at = _utc_now()

        try:
            # Check approval gate
            if task.requires_approval:
                approved = await self._handle_approval(task, execution)
                if not approved:
                    task.status = TaskStatus.SKIPPED
                    task.completed_at = _utc_now()
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
            task.completed_at = _utc_now()
            execution.record_task(task)
            logger.info(f"Task completed: {task.id}")

        except WorkflowError:
            # Re-raise workflow errors (approval pausing)
            # Note: pending_approval was set in _handle_approval
            raise
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            task.error = str(e)

            # Retry if allowed
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.reset()
                logger.info(
                    f"Retrying task {task.id} ({task.retry_count}/{task.max_retries})"
                )
                return

            task.status = TaskStatus.FAILED
            task.completed_at = _utc_now()
            execution.record_task(task)
            raise WorkflowError(f"Task '{task.id}' failed: {e}", task_id=task.id)

        finally:
            execution.current_task_id = None

    async def _handle_approval(
        self, task: TaskNode, execution: WorkflowExecution
    ) -> bool:
        """
        Handle approval gate.

        Args:
            task: Task requiring approval
            execution: Current execution state

        Returns:
            True if approved, False if denied
        """
        if self._approval_callback is None:
            # No callback - pause execution
            task.status = TaskStatus.WAITING_APPROVAL
            execution.pending_approval = task.id
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

        # Mark as approved - clear approval requirement so it doesn't trigger again
        task.status = TaskStatus.PENDING
        task.requires_approval = False  # Already approved, don't ask again
        execution.pending_approval = None

        logger.info(f"Task approved: {task_id}")

        # Continue execution
        try:
            await self._run_workflow(workflow, execution)
            execution.status = TaskStatus.COMPLETED
            execution.completed_at = _utc_now()
        except WorkflowError as e:
            if execution.pending_approval:
                execution.status = TaskStatus.WAITING_APPROVAL
            else:
                raise

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
        task.completed_at = _utc_now()
        execution.pending_approval = None
        execution.record_task(task)

        logger.info(f"Task skipped: {task_id}")

        # Continue execution
        try:
            await self._run_workflow(workflow, execution)
            execution.status = TaskStatus.COMPLETED
            execution.completed_at = _utc_now()
        except WorkflowError as e:
            if execution.pending_approval:
                execution.status = TaskStatus.WAITING_APPROVAL
            else:
                raise

        return execution

    def get_workflow_status(
        self, workflow: WorkflowDefinition, execution: WorkflowExecution
    ) -> dict[str, Any]:
        """
        Get detailed workflow status.

        Args:
            workflow: Workflow definition
            execution: Current execution state

        Returns:
            Status dictionary with task details
        """
        task_statuses = {}
        for task in workflow.tasks:
            task_statuses[task.id] = {
                "name": task.name,
                "status": task.status.value,
                "agent": task.agent,
                "duration_ms": task.duration_ms,
                "error": task.error,
            }

        return {
            "workflow_id": execution.workflow_id,
            "execution_id": execution.execution_id,
            "status": execution.status.value,
            "pending_approval": execution.pending_approval,
            "current_task": execution.current_task_id,
            "variables": list(execution.variables.keys()),
            "duration_ms": execution.duration_ms,
            "tasks": task_statuses,
        }
