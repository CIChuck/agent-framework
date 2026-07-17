"""
Workflow execution engine.

All mutable runtime state is tracked in WorkflowExecution.task_states.
TaskNode objects are never mutated — the same WorkflowDefinition can
be executed concurrently without state collision.

Ref: docs/archive/agent-phase-artifacts/completed-friday-agentic-core/dynamic-workflows-build-plan.md
Ref: Phase 1 Build Plan, Step 3
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Literal, cast

from friday_memory.multi_agent import ScratchPlanItemStatus
from friday_telemetry.interface import TelemetryInterface

from friday_agent.workflows.models import (
    ArtifactLifecycleState,
    ArtifactPolicy,
    ArtifactRecord,
    CanonicalWorkflowExecution,
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

if TYPE_CHECKING:
    from friday_agent.orchestrator import AgentOrchestrator


logger = logging.getLogger(__name__)

ApprovalCallback = Callable[[TaskNode], Awaitable[bool]]
HITLCallback = Callable[[HITLRequest], Awaitable[bool | HITLDecision]]


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

    All mutable state is stored in WorkflowExecution — TaskNode objects
    are never modified.

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
        approval_callback: ApprovalCallback | None = None,
        hitl_callback: HITLCallback | None = None,
        hitl_policy: HITLPolicy | None = None,
        artifact_policy: ArtifactPolicy | None = None,
        scratchpad: Any | None = None,
        telemetry: TelemetryInterface | None = None,
        agent_info_resolver: Callable[[str], dict[str, Any] | None] | None = None,
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
        self._hitl_callback = hitl_callback
        self._hitl_policy = hitl_policy
        self._artifact_policy = artifact_policy
        self._scratchpad = scratchpad
        self._telemetry = telemetry
        self._agent_info_resolver = agent_info_resolver

    async def execute(
        self,
        workflow: WorkflowDefinition,
        initial_inputs: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """
        Execute a workflow.

        Creates a fresh WorkflowExecution with empty task_states,
        then runs until completion or pause. The workflow definition
        is never mutated.

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

        # Create execution state with fresh task states
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            execution_id=f"{workflow.id}_{uuid.uuid4().hex[:8]}",
            variables=initial_inputs or {},
            started_at=_utc_now(),
        )
        execution.init_task_states(workflow)
        self._initialize_scratch_plan(workflow=workflow, execution=execution)
        self._append_scratch_event(
            execution=execution,
            event_type="workflow_started",
            details={"workflow_name": workflow.name},
        )

        logger.info(f"Starting workflow: {workflow.name} ({execution.execution_id})")

        try:
            await self._run_workflow(workflow, execution)
            if self._has_failed_tasks(execution):
                execution.status = TaskStatus.FAILED
                logger.error(f"Workflow completed with failed tasks: {workflow.name}")
                self._append_scratch_event(
                    execution=execution,
                    event_type="workflow_failed",
                    details={"reason": "failed_tasks_present"},
                )
            else:
                execution.status = TaskStatus.COMPLETED
                logger.info(f"Workflow completed: {workflow.name}")
                self._append_scratch_event(
                    execution=execution,
                    event_type="workflow_completed",
                )
        except WorkflowError as e:
            if execution.pending_approval:
                # Paused for approval - not an error
                execution.status = TaskStatus.WAITING_APPROVAL
                logger.info(f"Workflow paused for approval: {e.task_id}")
                self._append_scratch_event(
                    execution=execution,
                    event_type="workflow_paused_waiting_approval",
                    task_id=e.task_id,
                )
            else:
                execution.status = TaskStatus.FAILED
                logger.error(f"Workflow failed: {e}")
                self._append_scratch_event(
                    execution=execution,
                    event_type="workflow_failed",
                    task_id=e.task_id,
                    details={"error": str(e)},
                )
                raise
        finally:
            if execution.status != TaskStatus.WAITING_APPROVAL:
                execution.completed_at = _utc_now()

        return execution

    async def execute_canonical(
        self,
        workflow: WorkflowPipelineDefinition,
        pipelines: dict[str, PipelineDefinition],
        initial_inputs: dict[str, Any] | None = None,
        *,
        role_bindings: dict[str, str] | None = None,
        execution_id: str | None = None,
    ) -> CanonicalWorkflowExecution:
        """
        Execute a canonical workflow -> pipeline -> task hierarchy.

        Args:
            workflow: Canonical workflow definition
            pipelines: Resolved pipeline definitions keyed by pipeline_id
            initial_inputs: Initial variable values
            role_bindings: Runtime role->agent binding map

        Returns:
            Canonical workflow execution state/result bundle
        """
        dispatch_engine = PipelineDispatchEngine()
        dispatch_engine.validate_hierarchy(workflow, pipelines)

        execution = CanonicalWorkflowExecution(
            workflow_id=workflow.workflow_id,
            execution_id=execution_id or f"{workflow.workflow_id}_{uuid.uuid4().hex[:8]}",
            variables=dict(initial_inputs or {}),
            started_at=_utc_now(),
            status=PipelineExecutionStatus.CREATED,
        )
        workflow_span_id = self._start_span(
            "workflow_execution",
            {
                "workflow_id": workflow.workflow_id,
                "execution_id": execution.execution_id,
                "pipeline_count": len(workflow.pipeline_refs),
            },
        )

        try:
            for pipeline_id in workflow.get_pipeline_order(pipelines):
                pipeline = pipelines[pipeline_id]
                dispatch = PipelineDispatch(
                    dispatch_id=f"{execution.execution_id}:{pipeline_id}",
                    workflow_id=workflow.workflow_id,
                    pipeline_id=pipeline_id,
                    session_id=execution.execution_id,
                    run_id=execution.execution_id,
                    requested_by="runtime",
                    started_at=_utc_now(),
                )
                state = dispatch_engine.initialize_dispatch(
                    workflow,
                    pipeline,
                    dispatch,
                    role_bindings=role_bindings,
                )
                execution.pipeline_states[pipeline_id] = state
                self._validate_pipeline_consumed_artifacts(
                    workflow=workflow,
                    pipeline=pipeline,
                    pipelines=pipelines,
                    state=state,
                    execution=execution,
                    dispatch_engine=dispatch_engine,
                )
                await self._run_pipeline(
                    workflow=workflow,
                    pipeline=pipeline,
                    state=state,
                    execution=execution,
                    dispatch_engine=dispatch_engine,
                )
                execution.pipeline_results[pipeline_id] = dispatch_engine.finalize_pipeline(
                    state,
                    output_artifacts=self._pipeline_artifact_ids(execution, pipeline_id),
                    trace_ids=(
                        [state.dispatch_id]
                        if self._telemetry is not None
                        else []
                    ),
                )

            self._validate_required_artifacts(workflow, execution)
            execution.status = PipelineExecutionStatus.COMPLETED
            self._capture_event(
                "workflow_execution_completed",
                {
                    "workflow_id": workflow.workflow_id,
                    "execution_id": execution.execution_id,
                    "status": execution.status.value,
                    "pipeline_count": len(execution.pipeline_results),
                    "artifact_count": len(execution.published_artifacts),
                },
            )
        except Exception:
            execution.status = PipelineExecutionStatus.FAILED
            self._capture_event(
                "workflow_execution_failed",
                {
                    "workflow_id": workflow.workflow_id,
                    "execution_id": execution.execution_id,
                    "status": execution.status.value,
                },
            )
            raise
        finally:
            execution.completed_at = _utc_now()
            self._end_span(
                workflow_span_id,
                {
                    "status": execution.status.value,
                    "pipeline_count": len(execution.pipeline_results),
                    "artifact_count": len(execution.published_artifacts),
                },
            )

        return execution

    async def _run_workflow(
        self,
        workflow: WorkflowDefinition,
        execution: WorkflowExecution,
    ) -> None:
        """Run workflow until completion or pause."""
        execution.status = TaskStatus.RUNNING

        while True:
            ready_tasks = execution.get_ready_tasks(workflow)

            if not ready_tasks:
                # Check if all tasks complete
                all_done = all(
                    state.status
                    in (TaskStatus.COMPLETED, TaskStatus.SKIPPED, TaskStatus.FAILED)
                    for state in execution.task_states.values()
                )
                if all_done:
                    break

                # Check for waiting approval
                waiting = next(
                    (
                        task_id
                        for task_id, state in execution.task_states.items()
                        if state.status == TaskStatus.WAITING_APPROVAL
                    ),
                    None,
                )
                if waiting:
                    execution.pending_approval = waiting
                    if self._apply_hitl_timeout_default_if_due(
                        workflow=workflow,
                        execution=execution,
                        task_id=waiting,
                    ):
                        continue
                    raise WorkflowError(
                        f"Task '{waiting}' waiting for approval",
                        task_id=waiting,
                    )

                # Check for failed tasks blocking progress
                failed = [
                    task_id
                    for task_id, state in execution.task_states.items()
                    if state.status == TaskStatus.FAILED
                ]
                if failed:
                    raise WorkflowError(f"Workflow blocked by failed tasks: {failed}")

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
        """Execute a single task, updating state in execution.task_states."""
        logger.info(f"Executing task: {task.name} ({task.id})")
        execution.current_task_id = task.id
        state = execution.get_task_state(task.id)

        state.status = TaskStatus.RUNNING
        state.started_at = _utc_now()
        self._update_scratch_task_status(
            execution=execution,
            task=task,
            status=TaskStatus.RUNNING,
        )
        self._append_scratch_event(
            execution=execution,
            event_type="task_started",
            task_id=task.id,
            details={"agent": task.agent},
        )

        try:
            # Check approval gate
            if task.requires_approval:
                approved = await self._handle_approval(task, state, execution)
                if not approved:
                    state.status = TaskStatus.SKIPPED
                    state.completed_at = _utc_now()
                    execution.record_task(task)
                    self._update_scratch_task_status(
                        execution=execution,
                        task=task,
                        status=TaskStatus.SKIPPED,
                        details={"reason": "approval_denied_or_cancelled"},
                    )
                    self._append_scratch_event(
                        execution=execution,
                        event_type="task_skipped",
                        task_id=task.id,
                        details={"reason": "approval_denied_or_cancelled"},
                    )
                    logger.info(f"Task skipped (not approved): {task.id}")
                    return

            # Resolve inputs from variables
            resolved_inputs = self._resolve_inputs(task, execution.variables)

            # Build prompt from task description and inputs
            prompt = self._build_prompt(task, resolved_inputs)

            # Execute via orchestrator
            delegate_agent = task.agent
            if task.skill_ref:
                if not hasattr(self._orchestrator, "resolve_agent_for_skill"):
                    raise WorkflowError(
                        "Orchestrator does not support skill-based delegation",
                        task_id=task.id,
                    )
                try:
                    delegate_agent = self._orchestrator.resolve_agent_for_skill(
                        task.skill_ref,
                        preferred_agent=task.agent,
                    )
                except Exception as e:
                    raise WorkflowError(
                        f"Failed skill-based agent resolution: {e}",
                        task_id=task.id,
                    ) from e

            handoff_payload = self._build_handoff_payload(task, execution)
            delegate_kwargs: dict[str, Any] = {"return_to_current": True}
            if task.skill_ref is not None:
                delegate_kwargs["skill_ref"] = task.skill_ref
            if handoff_payload is None:
                result = await self._orchestrator.delegate(
                    delegate_agent,
                    prompt,
                    **delegate_kwargs,
                )
            else:
                result = await self._orchestrator.delegate(
                    delegate_agent,
                    prompt,
                    handoff_payload=handoff_payload,
                    **delegate_kwargs,
                )

            # Store result in state
            state.result = result

            # Store outputs in variables
            for output_name in task.outputs:
                execution.variables[output_name] = result
                logger.debug(f"Set variable ${output_name}")

            state.status = TaskStatus.COMPLETED
            state.completed_at = _utc_now()
            execution.record_task(task)
            self._update_scratch_task_status(
                execution=execution,
                task=task,
                status=TaskStatus.COMPLETED,
            )
            self._append_scratch_event(
                execution=execution,
                event_type="task_completed",
                task_id=task.id,
            )
            logger.info(f"Task completed: {task.id}")

        except WorkflowError:
            # Re-raise workflow errors (approval pausing)
            raise
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            state.error = str(e)

            # Retry if allowed
            if state.retry_count < task.max_retries:
                state.retry_count += 1
                state.reset()
                logger.info(
                    f"Retrying task {task.id} ({state.retry_count}/{task.max_retries})"
                )
                return

            state.status = TaskStatus.FAILED
            state.completed_at = _utc_now()
            execution.record_task(task)
            self._update_scratch_task_status(
                execution=execution,
                task=task,
                status=TaskStatus.FAILED,
                details={"error": str(e)},
            )
            self._append_scratch_event(
                execution=execution,
                event_type="task_failed",
                task_id=task.id,
                details={"error": str(e)},
            )
            raise WorkflowError(f"Task '{task.id}' failed: {e}", task_id=task.id) from e

        finally:
            execution.current_task_id = None

    async def _handle_approval(
        self,
        task: TaskNode,
        state: TaskState,
        execution: WorkflowExecution,
    ) -> bool:
        """
        Handle approval gate.

        Checks approval_overrides first (for previously approved tasks),
        then falls back to the approval callback or pauses.

        Args:
            task: Task requiring approval
            state: Mutable runtime state for this task
            execution: Current execution state

        Returns:
            True if approved, False if denied
        """
        # Check if already approved via approve_task()
        if task.id in execution.approval_overrides:
            return True

        request = self._create_hitl_request(task=task, execution=execution)
        execution.pending_hitl_request = request

        if self._hitl_callback is not None:
            logger.info(f"Requesting HITL decision for task: {task.id}")
            decision_or_bool = await self._hitl_callback(request)
            return self._resolve_hitl_callback_result(
                decision_or_bool=decision_or_bool,
                request=request,
                task=task,
                state=state,
                execution=execution,
            )

        if self._approval_callback is not None:
            logger.info(f"Requesting approval for task: {task.id}")
            approved = await self._approval_callback(task)
            if approved:
                execution.pending_hitl_request = None
            return approved

        # No callback - pause execution
        state.status = TaskStatus.WAITING_APPROVAL
        execution.pending_approval = task.id
        self._update_scratch_task_status(
            execution=execution,
            task=task,
            status=TaskStatus.WAITING_APPROVAL,
        )
        self._append_scratch_event(
            execution=execution,
            event_type="hitl_waiting",
            task_id=task.id,
            details={
                "request_id": request.request_id,
                "deadline_at": request.deadline_at.isoformat(),
            },
        )
        raise WorkflowError(
            f"Task '{task.id}' requires approval",
            task_id=task.id,
        )

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

    def _resolve_pipeline_inputs(
        self,
        task: TaskDefinition,
        variables: dict[str, Any],
    ) -> dict[str, Any]:
        """Resolve canonical pipeline-task inputs from execution variables."""
        resolved: dict[str, Any] = {}
        bindings = task.input_bindings or {
            input_name: f"${input_name}" for input_name in task.input_contract
        }
        for input_name in task.input_contract:
            binding = bindings.get(input_name, f"${input_name}")
            if binding.startswith("$"):
                variable_name = binding[1:]
                if variable_name not in variables:
                    raise WorkflowError(
                        f"Missing canonical input '{variable_name}' for task '{task.task_id}'",
                        task_id=task.task_id,
                    )
                resolved[input_name] = variables[variable_name]
            else:
                resolved[input_name] = binding
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

    def _build_pipeline_prompt(
        self,
        task: TaskDefinition,
        inputs: dict[str, Any],
    ) -> str:
        """Build agent prompt from canonical task definition and resolved inputs."""
        parts = [task.description]
        if inputs:
            parts.append("\n\nInputs:")
            for name, value in inputs.items():
                value_str = str(value)
                if len(value_str) > 500:
                    value_str = value_str[:500] + "..."
                parts.append(f"- {name}: {value_str}")
        if task.completion_criteria:
            parts.append("\n\nCompletion criteria:")
            for criterion in task.completion_criteria:
                parts.append(f"- {criterion}")
        return "\n".join(parts)

    def _normalize_pipeline_outputs(
        self,
        task: TaskDefinition,
        result: Any,
    ) -> dict[str, Any]:
        """Map orchestrator result into declared canonical output keys."""
        if not task.output_contract:
            return {}
        if isinstance(result, dict):
            missing = [key for key in task.output_contract if key not in result]
            if missing:
                raise WorkflowError(
                    f"Task '{task.task_id}' result missing output keys {missing}",
                    task_id=task.task_id,
                )
            return {key: result[key] for key in task.output_contract}
        output_keys = list(task.output_contract)
        if len(output_keys) == 1:
            return {output_keys[0]: result}
        raise WorkflowError(
            f"Task '{task.task_id}' must return a mapping for multi-output contracts",
            task_id=task.task_id,
        )

    async def _run_pipeline(
        self,
        *,
        workflow: WorkflowPipelineDefinition,
        pipeline: PipelineDefinition,
        state: PipelineExecutionState,
        execution: CanonicalWorkflowExecution,
        dispatch_engine: PipelineDispatchEngine,
    ) -> list[str]:
        """Run a canonical pipeline to completion."""
        produced_artifacts: list[str] = []
        pipeline_span_id = self._start_span(
            "pipeline_execution",
            {
                "workflow_id": workflow.workflow_id,
                "execution_id": execution.execution_id,
                "pipeline_id": pipeline.pipeline_id,
                "dispatch_id": state.dispatch_id,
            },
        )
        self._capture_event(
            "pipeline_execution_started",
            {
                "workflow_id": workflow.workflow_id,
                "execution_id": execution.execution_id,
                "pipeline_id": pipeline.pipeline_id,
                "dispatch_id": state.dispatch_id,
            },
        )
        while True:
            ready_assignments = dispatch_engine.assign_dependency_ready_tasks(
                pipeline, state
            )
            if not ready_assignments:
                if state.status == PipelineExecutionStatus.COMPLETED:
                    self._capture_event(
                        "pipeline_execution_completed",
                        {
                            "workflow_id": workflow.workflow_id,
                            "execution_id": execution.execution_id,
                            "pipeline_id": pipeline.pipeline_id,
                            "dispatch_id": state.dispatch_id,
                            "artifact_count": len(produced_artifacts),
                            "lineage_count": len(state.lineage_records),
                        },
                    )
                    self._end_span(
                        pipeline_span_id,
                        {
                            "status": state.status.value,
                            "artifact_count": len(produced_artifacts),
                            "lineage_count": len(state.lineage_records),
                        },
                    )
                    return produced_artifacts
                if state.status == PipelineExecutionStatus.FAILED:
                    self._capture_event(
                        "pipeline_execution_failed",
                        {
                            "workflow_id": workflow.workflow_id,
                            "execution_id": execution.execution_id,
                            "pipeline_id": pipeline.pipeline_id,
                            "dispatch_id": state.dispatch_id,
                            "status": state.status.value,
                        },
                    )
                    self._end_span(
                        pipeline_span_id,
                        {"status": state.status.value},
                    )
                    raise WorkflowError(
                        f"Pipeline '{pipeline.pipeline_id}' failed during canonical execution"
                    )
                if state.status == PipelineExecutionStatus.BLOCKED:
                    self._capture_event(
                        "pipeline_execution_blocked",
                        {
                            "workflow_id": workflow.workflow_id,
                            "execution_id": execution.execution_id,
                            "pipeline_id": pipeline.pipeline_id,
                            "dispatch_id": state.dispatch_id,
                            "status": state.status.value,
                        },
                    )
                    self._end_span(
                        pipeline_span_id,
                        {"status": state.status.value},
                    )
                    raise WorkflowError(
                        f"Pipeline '{pipeline.pipeline_id}' blocked with no runnable tasks"
                    )
                self._end_span(
                    pipeline_span_id,
                    {"status": state.status.value},
                )
                return produced_artifacts

            for assignment in ready_assignments:
                task = pipeline.get_task(assignment.task_id)
                if task is None:
                    raise WorkflowError(
                        f"Task '{assignment.task_id}' not found in pipeline '{pipeline.pipeline_id}'"
                    )
                owner_agent_id = assignment.assigned_agent_id
                agent_info = self._resolve_agent_info(owner_agent_id)
                llm_service = agent_info.get("llm_service") if agent_info else None
                dispatch_engine.claim_task(
                    pipeline,
                    state,
                    task.task_id,
                    owner_agent_id,
                )
                dispatch_engine.start_task(pipeline, state, task.task_id)
                try:
                    self._capture_event(
                        "workflow_task_started",
                        {
                            "workflow_id": workflow.workflow_id,
                            "execution_id": execution.execution_id,
                            "pipeline_id": pipeline.pipeline_id,
                            "task_id": task.task_id,
                            "assigned_agent_id": owner_agent_id,
                            "owner_role": task.owner_role,
                            "llm_service": llm_service,
                        },
                    )
                    resolved_inputs = self._resolve_pipeline_inputs(
                        task,
                        execution.variables,
                    )
                    prompt = self._build_pipeline_prompt(task, resolved_inputs)
                    delegate_kwargs: dict[str, Any] = {"return_to_current": True}
                    result = await self._orchestrator.delegate(
                        owner_agent_id,
                        prompt,
                        **delegate_kwargs,
                    )
                    outputs = self._normalize_pipeline_outputs(task, result)
                    execution.variables.update(outputs)
                    produced_artifacts.extend(
                        self._publish_task_artifacts(
                            workflow=workflow,
                            pipeline=pipeline,
                            task=task,
                            outputs=outputs,
                            execution=execution,
                        )
                    )
                    dispatch_engine.mark_task_completed(pipeline, state, task.task_id)
                    self._capture_event(
                        "workflow_task_completed",
                        {
                            "workflow_id": workflow.workflow_id,
                            "execution_id": execution.execution_id,
                            "pipeline_id": pipeline.pipeline_id,
                            "task_id": task.task_id,
                            "assigned_agent_id": owner_agent_id,
                            "owner_role": task.owner_role,
                            "llm_service": llm_service,
                            "output_keys": sorted(outputs),
                        },
                    )
                except Exception as e:
                    dispatch_engine.mark_task_failed(
                        pipeline,
                        state,
                        task.task_id,
                        failure_summary=str(e),
                    )
                    self._capture_event(
                        "workflow_task_failed",
                        {
                            "workflow_id": workflow.workflow_id,
                            "execution_id": execution.execution_id,
                            "pipeline_id": pipeline.pipeline_id,
                            "task_id": task.task_id,
                            "assigned_agent_id": owner_agent_id,
                            "owner_role": task.owner_role,
                            "llm_service": llm_service,
                            "error": str(e),
                        },
                    )
                    raise

    def _publish_task_artifacts(
        self,
        *,
        workflow: WorkflowPipelineDefinition,
        pipeline: PipelineDefinition,
        task: TaskDefinition,
        outputs: dict[str, Any],
        execution: CanonicalWorkflowExecution,
    ) -> list[str]:
        """Publish task output artifacts into canonical execution state."""
        published: list[str] = []
        produced_contracts = {
            artifact.artifact_id: artifact for artifact in pipeline.artifact_contract.produced
        }
        for output_artifact in task.output_artifacts:
            contract = produced_contracts.get(output_artifact.artifact_id)
            if contract is None:
                raise WorkflowError(
                    f"Task '{task.task_id}' publishes undeclared artifact "
                    f"'{output_artifact.artifact_id}'"
                )
            if contract.producer_task_id != task.task_id:
                raise WorkflowError(
                    f"Artifact '{output_artifact.artifact_id}' is bound to "
                    f"producer_task_id '{contract.producer_task_id}', not '{task.task_id}'"
                )
            if contract.type != output_artifact.type:
                raise WorkflowError(
                    f"Artifact '{output_artifact.artifact_id}' type mismatch between "
                    "task output_artifacts and pipeline artifact_contract"
                )
            if output_artifact.from_output not in outputs:
                raise WorkflowError(
                    f"Task '{task.task_id}' did not emit required output "
                    f"'{output_artifact.from_output}' for artifact publication"
                )

            output_value = outputs[output_artifact.from_output]
            provenance = {
                "workflow_id": workflow.workflow_id,
                "pipeline_id": pipeline.pipeline_id,
                "task_id": task.task_id,
                "from_output": output_artifact.from_output,
                "type": output_artifact.type,
            }
            if isinstance(output_value, (str, int, float, bool)):
                provenance["output_ref"] = str(output_value)

            execution.published_artifacts[output_artifact.artifact_id] = ArtifactRecord(
                artifact_id=output_artifact.artifact_id,
                lifecycle_state=ArtifactLifecycleState.FINAL,
                created_by=task.task_id,
                provenance=provenance,
                updated_at=_utc_now(),
                published_at=_utc_now(),
            )
            published.append(output_artifact.artifact_id)
            self._capture_event(
                "workflow_artifact_published",
                {
                    "workflow_id": workflow.workflow_id,
                    "execution_id": execution.execution_id,
                    "pipeline_id": pipeline.pipeline_id,
                    "task_id": task.task_id,
                    "artifact_id": output_artifact.artifact_id,
                    "artifact_type": output_artifact.type,
                },
            )
        return published

    def _validate_pipeline_consumed_artifacts(
        self,
        *,
        workflow: WorkflowPipelineDefinition,
        pipeline: PipelineDefinition,
        pipelines: dict[str, PipelineDefinition],
        state: PipelineExecutionState,
        execution: CanonicalWorkflowExecution,
        dispatch_engine: PipelineDispatchEngine,
    ) -> None:
        """Validate that consumed artifacts are available before pipeline execution."""
        for consumed in pipeline.artifact_contract.consumed:
            artifact = execution.published_artifacts.get(consumed.artifact_id)
            if artifact is None:
                raise WorkflowError(
                    f"Pipeline '{pipeline.pipeline_id}' missing required consumed "
                    f"artifact '{consumed.artifact_id}'"
                )
            if artifact.provenance.get("pipeline_id") != consumed.from_pipeline:
                raise WorkflowError(
                    f"Artifact '{consumed.artifact_id}' was not produced by "
                    f"expected pipeline '{consumed.from_pipeline}'"
                )
            if artifact.provenance.get("type") != consumed.type:
                raise WorkflowError(
                    f"Artifact '{consumed.artifact_id}' type mismatch for pipeline "
                    f"'{pipeline.pipeline_id}'"
                )
            producer_pipeline = pipelines.get(consumed.from_pipeline)
            if producer_pipeline is None:
                raise WorkflowError(
                    f"Producer pipeline '{consumed.from_pipeline}' not found for "
                    f"artifact '{consumed.artifact_id}'"
                )
            output_name = self._resolve_contract_key(
                producer_pipeline.output_contract,
                artifact_id=consumed.artifact_id,
                type_name=consumed.type,
            )
            input_name = self._resolve_contract_key(
                pipeline.input_contract,
                artifact_id=consumed.artifact_id,
                type_name=consumed.type,
            )
            record = dispatch_engine.validate_typed_handoff(
                workflow_id=workflow.workflow_id,
                from_pipeline=producer_pipeline,
                to_pipeline=pipeline,
                output_name=output_name,
                input_name=input_name,
                artifact_id=consumed.artifact_id,
                correlation_id=execution.execution_id,
                state=state,
            )
            self._capture_event(
                "workflow_typed_handoff_validated",
                {
                    "workflow_id": record.workflow_id,
                    "execution_id": execution.execution_id,
                    "from_pipeline_id": record.from_pipeline_id,
                    "to_pipeline_id": record.to_pipeline_id,
                    "artifact_id": record.artifact_id,
                    "output_name": record.output_name,
                    "input_name": record.input_name,
                },
            )

    def _validate_required_artifacts(
        self,
        workflow: WorkflowPipelineDefinition,
        execution: CanonicalWorkflowExecution,
    ) -> None:
        """Validate workflow-level required artifacts before final success."""
        for required in workflow.required_artifacts:
            artifact = execution.published_artifacts.get(required.artifact_id)
            if artifact is None:
                raise WorkflowError(
                    f"Workflow '{workflow.workflow_id}' missing required artifact "
                    f"'{required.artifact_id}'"
                )
            if artifact.provenance.get("pipeline_id") != required.produced_by_pipeline:
                raise WorkflowError(
                    f"Required artifact '{required.artifact_id}' was not produced by "
                    f"expected pipeline '{required.produced_by_pipeline}'"
                )
            if artifact.provenance.get("type") != required.type:
                raise WorkflowError(
                    f"Required artifact '{required.artifact_id}' type mismatch"
                )

    def _pipeline_artifact_ids(
        self,
        execution: CanonicalWorkflowExecution,
        pipeline_id: str,
    ) -> list[str]:
        """Return published artifact IDs for a specific pipeline."""
        return sorted(
            artifact_id
            for artifact_id, artifact in execution.published_artifacts.items()
            if artifact.provenance.get("pipeline_id") == pipeline_id
        )

    def _resolve_contract_key(
        self,
        contract: dict[str, str],
        *,
        artifact_id: str,
        type_name: str,
    ) -> str:
        """Resolve a contract key for lineage/correlation by artifact ID or type."""
        if artifact_id in contract:
            return artifact_id
        matches = [key for key, declared_type in contract.items() if declared_type == type_name]
        if len(matches) == 1:
            return matches[0]
        raise WorkflowError(
            f"Unable to resolve contract key for artifact '{artifact_id}' ({type_name})"
        )

    def _resolve_agent_info(self, agent_name: str) -> dict[str, Any] | None:
        """Resolve runtime metadata for an assigned agent when available."""
        if self._agent_info_resolver is None:
            return None
        try:
            return self._agent_info_resolver(agent_name)
        except Exception:
            logger.debug("Failed to resolve agent info for '%s'", agent_name)
            return None

    def _capture_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event when a recorder is configured."""
        if self._telemetry is not None:
            self._telemetry.capture_event(event_name, data)

    def _start_span(self, name: str, data: dict[str, Any]) -> str | None:
        """Start a telemetry span and emit a matching start event when enabled."""
        if self._telemetry is None:
            return None
        span_id = cast(str, self._telemetry.start_span(name))
        self._telemetry.capture_event(f"{name}_started", {**data, "span_id": span_id})
        return span_id

    def _end_span(self, span_id: str | None, data: dict[str, Any]) -> None:
        """End a telemetry span when enabled."""
        if span_id is not None and self._telemetry is not None:
            self._telemetry.end_span(span_id, data)

    def _build_handoff_payload(
        self, task: TaskNode, execution: WorkflowExecution
    ) -> dict[str, Any] | None:
        """Build validated handoff payload for delegated tasks."""
        if task.handoff is None:
            return None

        payload: dict[str, Any] = {
            "handoff_id": task.handoff.handoff_id,
            "ownership": task.handoff.ownership,
            "acceptance_criteria": list(task.handoff.acceptance_criteria),
            "memory_scope": task.handoff.memory_scope,
            "workflow_id": execution.workflow_id,
            "execution_id": execution.execution_id,
            "task_id": task.id,
        }
        if task.handoff.deadline is not None:
            payload["deadline"] = task.handoff.deadline.isoformat()
        if task.handoff.namespace is not None:
            payload["namespace"] = task.handoff.namespace
        if task.handoff.metadata:
            payload["metadata"] = dict(task.handoff.metadata)
        if task.skill_ref is not None:
            payload["skill_ref"] = task.skill_ref
        return payload

    def _create_hitl_request(
        self, task: TaskNode, execution: WorkflowExecution
    ) -> HITLRequest:
        """Create a structured HITL request payload for a waiting task."""
        now = _utc_now()
        timeout_seconds = (
            self._hitl_policy.timeout_seconds if self._hitl_policy is not None else 900
        )
        default_action = (
            self._hitl_policy.default_action_on_timeout
            if self._hitl_policy is not None
            else "safe_abort"
        )
        method = (
            self._hitl_policy.methods[0]
            if self._hitl_policy is not None and self._hitl_policy.methods
            else "approval_gate"
        )
        return HITLRequest(
            request_id=f"hitl_{uuid.uuid4().hex[:12]}",
            workflow_id=execution.workflow_id,
            execution_id=execution.execution_id,
            task_id=task.id,
            method=method,
            action_class="approval_gate",
            options=("approved", "rejected", "cancelled"),
            recommendation="approved",
            deadline_at=now + timedelta(seconds=timeout_seconds),
            default_action_on_timeout=default_action,
            created_at=now,
            correlation_id=execution.execution_id,
            metadata={
                "task_name": task.name,
                "agent": task.agent,
                "description": task.description,
            },
        )

    def _resolve_hitl_callback_result(
        self,
        decision_or_bool: bool | HITLDecision,
        request: HITLRequest,
        task: TaskNode,
        state: TaskState,
        execution: WorkflowExecution,
    ) -> bool:
        """
        Normalize callback result into approved/denied decision.

        Returns True to proceed, False to skip.
        """
        if isinstance(decision_or_bool, bool):
            if decision_or_bool:
                self._record_hitl_event(
                    execution=execution,
                    request=request,
                    decision="approved",
                    approver_id="callback",
                    approver_role="callback",
                    reason="boolean_callback",
                )
                execution.pending_hitl_request = None
                return True
            self._record_hitl_event(
                execution=execution,
                request=request,
                decision="rejected",
                approver_id="callback",
                approver_role="callback",
                reason="boolean_callback",
            )
            execution.pending_hitl_request = None
            return False

        self._validate_hitl_decision_authority(request, decision_or_bool)
        self._record_hitl_event(
            execution=execution,
            request=request,
            decision=decision_or_bool.decision.value,
            approver_id=decision_or_bool.approver_id,
            approver_role=decision_or_bool.approver_role,
            reason=decision_or_bool.reason,
        )
        execution.pending_hitl_request = None

        if decision_or_bool.decision == HITLDecisionAction.APPROVED:
            return True

        state.error = decision_or_bool.reason
        if decision_or_bool.decision == HITLDecisionAction.CANCELLED:
            state.error = state.error or "Cancelled by HITL approver"
        return False

    def _validate_hitl_decision_authority(
        self, request: HITLRequest, decision: HITLDecision
    ) -> None:
        """Validate decision authority against HITL policy."""
        if self._hitl_policy is None:
            return

        authority = self._hitl_policy.authority_policy
        delegated = decision.approver_id in authority.delegated_approvers

        if not delegated and decision.approver_role not in authority.allowed_roles:
            raise WorkflowError(
                f"Approver role '{decision.approver_role}' not authorized",
                task_id=decision.task_id,
            )

        scoped_roles = authority.decision_scope.get(request.action_class)
        if (
            scoped_roles
            and not delegated
            and decision.approver_role not in scoped_roles
        ):
            raise WorkflowError(
                "Approver role is outside decision scope for action class",
                task_id=decision.task_id,
            )

    def _record_hitl_event(
        self,
        execution: WorkflowExecution,
        request: HITLRequest,
        decision: str,
        approver_id: str,
        approver_role: str,
        reason: str | None,
    ) -> None:
        """Append a HITL event entry to execution history."""
        execution.hitl_history.append(
            {
                "request_id": request.request_id,
                "task_id": request.task_id,
                "decision": decision,
                "approver_id": approver_id,
                "approver_role": approver_role,
                "reason": reason,
                "action_class": request.action_class,
                "default_action_on_timeout": request.default_action_on_timeout,
                "deadline_at": request.deadline_at.isoformat(),
                "responded_at": _utc_now().isoformat(),
            }
        )

    def _apply_hitl_timeout_default_if_due(
        self, workflow: WorkflowDefinition, execution: WorkflowExecution, task_id: str
    ) -> bool:
        """Apply default timeout behavior if a pending HITL request is overdue."""
        request = execution.pending_hitl_request
        if request is None or request.task_id != task_id:
            return False

        now = _utc_now()
        if now < request.deadline_at:
            return False

        task = workflow.get_task(task_id)
        if task is None:
            raise WorkflowError(f"Task not found for timeout handling: {task_id}")

        state = execution.get_task_state(task_id)
        action = request.default_action_on_timeout

        if action == "defer":
            # Keep waiting; timeout is logged for auditability.
            self._record_hitl_event(
                execution=execution,
                request=request,
                decision="timed_out",
                approver_id="system",
                approver_role="system",
                reason="defer",
            )
            request.deadline_at = now + timedelta(
                seconds=max(
                    self._hitl_policy.timeout_seconds if self._hitl_policy else 1, 1
                )
            )
            execution.pending_hitl_request = request
            return False

        if action == "constrained_continue":
            execution.approval_overrides.add(task_id)
            state.status = TaskStatus.PENDING
            state.error = "HITL timeout resolved with constrained_continue"
            execution.pending_approval = None
            self._record_hitl_event(
                execution=execution,
                request=request,
                decision="timed_out",
                approver_id="system",
                approver_role="system",
                reason="constrained_continue",
            )
            execution.pending_hitl_request = None
            self._append_scratch_event(
                execution=execution,
                event_type="hitl_timeout_default",
                task_id=task_id,
                details={"action": "constrained_continue"},
            )
            return True

        # safe_abort default
        state.status = TaskStatus.FAILED
        state.completed_at = now
        state.error = "HITL timeout resolved with safe_abort"
        execution.pending_approval = None
        execution.pending_hitl_request = None
        execution.record_task(task)
        self._record_hitl_event(
            execution=execution,
            request=request,
            decision="timed_out",
            approver_id="system",
            approver_role="system",
            reason="safe_abort",
        )
        self._update_scratch_task_status(
            execution=execution,
            task=task,
            status=TaskStatus.FAILED,
            details={"reason": "hitl_timeout_safe_abort"},
        )
        self._append_scratch_event(
            execution=execution,
            event_type="hitl_timeout_default",
            task_id=task_id,
            details={"action": "safe_abort"},
        )
        return True

    async def apply_pending_timeouts(
        self, workflow: WorkflowDefinition, execution: WorkflowExecution
    ) -> WorkflowExecution:
        """
        Evaluate pending HITL timeout actions and continue execution when applicable.

        This is intended for runtime polling loops while an execution is paused.
        """
        if execution.pending_approval is None:
            return execution

        if not self._apply_hitl_timeout_default_if_due(
            workflow=workflow,
            execution=execution,
            task_id=execution.pending_approval,
        ):
            return execution

        try:
            return await self._resume_execution(workflow, execution)
        except WorkflowError:
            execution.status = TaskStatus.FAILED
            execution.completed_at = _utc_now()
            return execution

    async def approve_task(
        self,
        workflow: WorkflowDefinition,
        execution: WorkflowExecution,
        task_id: str,
    ) -> WorkflowExecution:
        """
        Approve a waiting task and continue execution.

        Records the approval in execution.approval_overrides so the
        task won't trigger the approval gate again. The original
        WorkflowDefinition is never mutated.

        Args:
            workflow: Workflow definition
            execution: Current execution state
            task_id: ID of task to approve

        Returns:
            Updated execution state
        """
        decision = HITLDecision(
            request_id=(
                execution.pending_hitl_request.request_id
                if execution.pending_hitl_request is not None
                else f"legacy_{task_id}"
            ),
            task_id=task_id,
            decision=HITLDecisionAction.APPROVED,
            approver_id="system",
            approver_role="system",
            reason="legacy_approve_task",
            responded_at=_utc_now(),
        )
        return await self.decide_task(workflow, execution, decision)

    async def reject_task(
        self,
        workflow: WorkflowDefinition,
        execution: WorkflowExecution,
        task_id: str,
        reason: str = "Rejected during approval",
    ) -> WorkflowExecution:
        """
        Reject a waiting task and continue execution.

        Args:
            workflow: Workflow definition
            execution: Current execution state
            task_id: ID of task to reject
            reason: Audit reason stored on task state

        Returns:
            Updated execution state
        """
        decision = HITLDecision(
            request_id=(
                execution.pending_hitl_request.request_id
                if execution.pending_hitl_request is not None
                else f"legacy_{task_id}"
            ),
            task_id=task_id,
            decision=HITLDecisionAction.REJECTED,
            approver_id="system",
            approver_role="system",
            reason=reason,
            responded_at=_utc_now(),
        )
        return await self.decide_task(workflow, execution, decision)

    async def skip_task(
        self,
        workflow: WorkflowDefinition,
        execution: WorkflowExecution,
        task_id: str,
    ) -> WorkflowExecution:
        """
        Skip a waiting task and continue execution.

        This is retained as a compatibility alias for reject_task().
        """
        return await self.reject_task(
            workflow=workflow,
            execution=execution,
            task_id=task_id,
            reason="Skipped during approval",
        )

    async def resolve_task(
        self,
        workflow: WorkflowDefinition,
        execution: WorkflowExecution,
        task_id: str,
        decision: Literal["approve", "reject", "skip"] = "approve",
    ) -> WorkflowExecution:
        """
        Deterministically resolve a waiting approval task.

        Args:
            workflow: Workflow definition
            execution: Current execution state
            task_id: ID of waiting task
            decision: approve, reject, or skip
        """
        if decision == "approve":
            return await self.approve_task(workflow, execution, task_id)
        if decision in ("reject", "skip"):
            reason = (
                "Rejected during approval"
                if decision == "reject"
                else "Skipped during approval"
            )
            return await self.reject_task(workflow, execution, task_id, reason=reason)
        raise WorkflowError(f"Unsupported approval decision '{decision}'")

    async def decide_task(
        self,
        workflow: WorkflowDefinition,
        execution: WorkflowExecution,
        decision: HITLDecision,
    ) -> WorkflowExecution:
        """Resolve a waiting task using a structured HITL decision payload."""
        task = workflow.get_task(decision.task_id)
        if task is None:
            raise WorkflowError(f"Task not found: {decision.task_id}")

        state = execution.get_task_state(decision.task_id)
        if state.status != TaskStatus.WAITING_APPROVAL:
            raise WorkflowError(f"Task '{decision.task_id}' not waiting for approval")

        request = execution.pending_hitl_request
        if request is None:
            request = HITLRequest(
                request_id=decision.request_id,
                workflow_id=execution.workflow_id,
                execution_id=execution.execution_id,
                task_id=decision.task_id,
                method="approval_gate",
                action_class="approval_gate",
                options=("approved", "rejected", "cancelled"),
                recommendation="approved",
                deadline_at=decision.responded_at,
                default_action_on_timeout="safe_abort",
                created_at=decision.responded_at,
                correlation_id=execution.execution_id,
            )
        elif decision.request_id != request.request_id:
            raise WorkflowError(
                "HITL decision request_id does not match pending request",
                task_id=decision.task_id,
            )

        self._validate_hitl_decision_authority(request, decision)
        self._record_hitl_event(
            execution=execution,
            request=request,
            decision=decision.decision.value,
            approver_id=decision.approver_id,
            approver_role=decision.approver_role,
            reason=decision.reason,
        )

        if decision.decision == HITLDecisionAction.APPROVED:
            execution.approval_overrides.add(decision.task_id)
            state.status = TaskStatus.PENDING
            state.error = None
        elif decision.decision in (
            HITLDecisionAction.REJECTED,
            HITLDecisionAction.CANCELLED,
            HITLDecisionAction.TIMED_OUT,
        ):
            state.status = TaskStatus.SKIPPED
            state.completed_at = _utc_now()
            state.error = decision.reason or f"{decision.decision.value} by HITL"
            execution.record_task(task)
        else:
            raise WorkflowError(
                f"Unsupported HITL decision '{decision.decision.value}'",
                task_id=decision.task_id,
            )

        execution.pending_approval = None
        execution.pending_hitl_request = None
        self._append_scratch_event(
            execution=execution,
            event_type="hitl_decision",
            task_id=decision.task_id,
            details={
                "request_id": decision.request_id,
                "decision": decision.decision.value,
                "approver_id": decision.approver_id,
                "approver_role": decision.approver_role,
            },
        )
        if decision.decision == HITLDecisionAction.APPROVED:
            self._update_scratch_task_status(
                execution=execution,
                task=task,
                status=TaskStatus.PENDING,
            )
        else:
            self._update_scratch_task_status(
                execution=execution,
                task=task,
                status=TaskStatus.SKIPPED,
                details={"reason": decision.reason or decision.decision.value},
            )
        logger.info(f"HITL decision applied for task: {decision.task_id}")
        return await self._resume_execution(workflow, execution)

    def register_artifact(
        self,
        execution: WorkflowExecution,
        artifact_id: str,
        created_by: str,
        provenance: dict[str, str] | None = None,
    ) -> None:
        """Register an artifact in lifecycle state `draft` with provenance checks."""
        if self._artifact_policy is None:
            raise WorkflowError("Artifact policy is not configured")
        if artifact_id in execution.artifacts:
            raise WorkflowError(f"Artifact '{artifact_id}' already registered")

        provenance_data = provenance or {}
        self._validate_artifact_provenance(provenance_data)
        execution.artifacts[artifact_id] = ArtifactRecord(
            artifact_id=artifact_id,
            lifecycle_state=ArtifactLifecycleState.DRAFT,
            created_by=created_by,
            provenance=provenance_data,
            updated_at=_utc_now(),
            published_at=None,
        )

    def transition_artifact(
        self,
        execution: WorkflowExecution,
        artifact_id: str,
        target_state: Literal["draft", "validated", "final", "archived"],
        approver_id: str | None = None,
        approver_role: str | None = None,
    ) -> None:
        """Apply governed artifact lifecycle transitions and publication controls."""
        if self._artifact_policy is None:
            raise WorkflowError("Artifact policy is not configured")
        if artifact_id not in execution.artifacts:
            raise WorkflowError(f"Artifact '{artifact_id}' not registered")

        artifact = execution.artifacts[artifact_id]
        current = artifact.lifecycle_state
        desired = ArtifactLifecycleState(target_state)

        allowed_transitions = {
            ArtifactLifecycleState.DRAFT: {
                ArtifactLifecycleState.VALIDATED,
                ArtifactLifecycleState.ARCHIVED,
            },
            ArtifactLifecycleState.VALIDATED: {
                ArtifactLifecycleState.FINAL,
                ArtifactLifecycleState.ARCHIVED,
            },
            ArtifactLifecycleState.FINAL: {ArtifactLifecycleState.ARCHIVED},
            ArtifactLifecycleState.ARCHIVED: set(),
        }
        if desired not in allowed_transitions[current]:
            raise WorkflowError(
                f"Invalid artifact lifecycle transition: {current.value} -> {desired.value}"  # noqa: E501
            )

        if desired == ArtifactLifecycleState.FINAL:
            if self._artifact_policy.publication_requires_approval:
                if not approver_id or not approver_role:
                    raise WorkflowError(
                        "Artifact publication requires approver identity and role"
                    )
                if self._hitl_policy is not None:
                    authority = self._hitl_policy.authority_policy
                    delegated = approver_id in authority.delegated_approvers
                    if not delegated and approver_role not in authority.allowed_roles:
                        raise WorkflowError(
                            f"Approver role '{approver_role}' not authorized for publication"  # noqa: E501
                        )
            self._validate_artifact_provenance(artifact.provenance)
            artifact.published_at = _utc_now()

        artifact.lifecycle_state = desired
        artifact.updated_at = _utc_now()
        execution.artifacts[artifact_id] = artifact

    def _validate_artifact_provenance(self, provenance: dict[str, str]) -> None:
        """Validate required provenance fields from artifact policy."""
        if self._artifact_policy is None:
            return
        missing = [
            field
            for field in self._artifact_policy.required_provenance_fields
            if field not in provenance or not str(provenance[field]).strip()
        ]
        if missing:
            raise WorkflowError(
                f"Artifact provenance missing required fields: {', '.join(missing)}"
            )

    async def _resume_execution(
        self, workflow: WorkflowDefinition, execution: WorkflowExecution
    ) -> WorkflowExecution:
        """Resume workflow execution after manual approval decision."""

        try:
            await self._run_workflow(workflow, execution)
            execution.status = (
                TaskStatus.FAILED
                if self._has_failed_tasks(execution)
                else TaskStatus.COMPLETED
            )
            execution.completed_at = _utc_now()
            self._append_scratch_event(
                execution=execution,
                event_type="workflow_resumed",
                details={"status": execution.status.value},
            )
        except WorkflowError:
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
            state = execution.get_task_state(task.id)
            task_statuses[task.id] = {
                "name": task.name,
                "status": state.status.value,
                "agent": task.agent,
                "duration_ms": state.duration_ms,
                "error": state.error,
            }

        return {
            "workflow_id": execution.workflow_id,
            "execution_id": execution.execution_id,
            "status": execution.status.value,
            "awaiting_human": execution.status == TaskStatus.WAITING_APPROVAL,
            "pending_approval": execution.pending_approval,
            "pending_hitl_request": (
                execution.pending_hitl_request.model_dump()
                if execution.pending_hitl_request is not None
                else None
            ),
            "current_task": execution.current_task_id,
            "variables": list(execution.variables.keys()),
            "duration_ms": execution.duration_ms,
            "hitl_history_count": len(execution.hitl_history),
            "artifact_count": len(execution.artifacts),
            "tasks": task_statuses,
        }

    def _has_failed_tasks(self, execution: WorkflowExecution) -> bool:
        """Return True when any task has failed state."""
        return any(
            state.status == TaskStatus.FAILED
            for state in execution.task_states.values()
        )

    def _scratch_scope_id(self, execution: WorkflowExecution) -> str:
        return f"{execution.workflow_id}:{execution.execution_id}"

    def _initialize_scratch_plan(
        self, workflow: WorkflowDefinition, execution: WorkflowExecution
    ) -> None:
        if self._scratchpad is None:
            return
        scope_id = self._scratch_scope_id(execution)
        for task in workflow.tasks:
            self._scratchpad.upsert_plan_item(
                scope_id=scope_id,
                task_id=task.id,
                title=task.name,
                status=ScratchPlanItemStatus.PENDING,
                metadata={"agent": task.agent},
            )

    def _to_scratch_status(self, status: TaskStatus) -> ScratchPlanItemStatus:
        mapping = {
            TaskStatus.PENDING: ScratchPlanItemStatus.PENDING,
            TaskStatus.RUNNING: ScratchPlanItemStatus.RUNNING,
            TaskStatus.COMPLETED: ScratchPlanItemStatus.COMPLETED,
            TaskStatus.FAILED: ScratchPlanItemStatus.FAILED,
            TaskStatus.SKIPPED: ScratchPlanItemStatus.SKIPPED,
            TaskStatus.WAITING_APPROVAL: ScratchPlanItemStatus.WAITING_APPROVAL,
        }
        return mapping[status]

    def _update_scratch_task_status(
        self,
        execution: WorkflowExecution,
        task: TaskNode,
        status: TaskStatus,
        details: dict[str, Any] | None = None,
    ) -> None:
        if self._scratchpad is None:
            return
        scope_id = self._scratch_scope_id(execution)
        scratch_status = self._to_scratch_status(status)
        try:
            self._scratchpad.update_plan_item_status(
                scope_id=scope_id,
                task_id=task.id,
                status=scratch_status,
                metadata=details or {},
            )
        except KeyError:
            self._scratchpad.upsert_plan_item(
                scope_id=scope_id,
                task_id=task.id,
                title=task.name,
                status=scratch_status,
                metadata=details or {},
            )

    def _append_scratch_event(
        self,
        execution: WorkflowExecution,
        event_type: str,
        *,
        task_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        if self._scratchpad is None:
            return
        scope_id = self._scratch_scope_id(execution)
        self._scratchpad.append_event(
            scope_id=scope_id,
            event_type=event_type,
            workflow_id=execution.workflow_id,
            execution_id=execution.execution_id,
            task_id=task_id,
            correlation_id=execution.execution_id,
            details=details or {},
        )


class PipelineDispatchError(Exception):
    """Raised when pipeline/task dispatch lifecycle operations fail."""


class PipelineDispatchEngine:
    """
    Deterministic pipeline/task dispatch engine for hierarchical workflows.

    This engine is additive to the existing WorkflowEngine and is used for
    `workflow -> pipeline -> task` hierarchy contracts, async lease handling,
    and cross-pipeline typed handoff lineage recording.
    """

    def validate_hierarchy(
        self,
        workflow: WorkflowPipelineDefinition,
        pipelines: dict[str, PipelineDefinition],
    ) -> None:
        """Validate workflow/pipeline cardinality and reference integrity."""
        errors = workflow.validate_reference_integrity(pipelines)
        for pipeline_id in workflow.pipeline_refs:
            pipeline = pipelines.get(pipeline_id)
            if pipeline is None:
                continue
            for error in pipeline.validate_graph():
                errors.append(f"{pipeline_id}: {error}")
        if errors:
            raise PipelineDispatchError("; ".join(errors))

    def initialize_dispatch(
        self,
        workflow: WorkflowPipelineDefinition,
        pipeline: PipelineDefinition,
        dispatch: PipelineDispatch,
        *,
        role_bindings: dict[str, str] | None = None,
    ) -> PipelineExecutionState:
        """Initialize assignment and dispatch state for a pipeline run."""
        if pipeline.pipeline_id != dispatch.pipeline_id:
            raise PipelineDispatchError(
                "dispatch.pipeline_id does not match target pipeline definition"
            )
        if workflow.workflow_id != dispatch.workflow_id:
            raise PipelineDispatchError(
                "dispatch.workflow_id does not match workflow definition"
            )
        if pipeline.pipeline_id not in set(workflow.pipeline_refs):
            raise PipelineDispatchError(
                "cannot dispatch pipeline not referenced by active workflow"
            )

        assignments: dict[str, TaskAssignment] = {}
        for task in pipeline.tasks:
            assignments[task.task_id] = TaskAssignment(
                assignment_id=f"{dispatch.dispatch_id}:{task.task_id}",
                workflow_id=workflow.workflow_id,
                pipeline_id=pipeline.pipeline_id,
                task_id=task.task_id,
                assigned_agent_id=self._resolve_task_owner(
                    task, role_bindings=role_bindings
                ),
                assigned_at=dispatch.started_at,
                status=TaskAssignmentStatus.ASSIGNED,
            )

        state = PipelineExecutionState(
            workflow_id=workflow.workflow_id,
            pipeline_id=pipeline.pipeline_id,
            dispatch_id=dispatch.dispatch_id,
            status=PipelineExecutionStatus.CREATED,
            task_assignments=assignments,
            last_transition_at=dispatch.started_at,
        )
        state.refresh_views(pipeline)
        if state.status == PipelineExecutionStatus.BLOCKED and state.runnable_tasks:
            state.status = PipelineExecutionStatus.RUNNING
        return state

    def assign_dependency_ready_tasks(
        self,
        pipeline: PipelineDefinition,
        state: PipelineExecutionState,
    ) -> list[TaskAssignment]:
        """
        Return assignments for dependency-ready tasks in deterministic order.

        Determinism guarantee: task IDs are sorted lexicographically.
        """
        state.refresh_views(pipeline)
        ready_ids = sorted(state.runnable_tasks)
        return [state.task_assignments[task_id] for task_id in ready_ids]

    def claim_task(
        self,
        pipeline: PipelineDefinition,
        state: PipelineExecutionState,
        task_id: str,
        agent_id: str,
        *,
        lease_seconds: int = 300,
        claimed_at: datetime | None = None,
    ) -> TaskAssignment:
        """Claim assigned task with explicit lease semantics for async mode."""
        assignment = self._get_assignment(state, task_id=task_id)
        if assignment.status != TaskAssignmentStatus.ASSIGNED:
            raise PipelineDispatchError(
                f"task '{task_id}' must be in assigned status before claim"
            )
        if assignment.assigned_agent_id != agent_id:
            raise PipelineDispatchError(
                f"task '{task_id}' assigned to {assignment.assigned_agent_id}, "
                f"cannot claim as {agent_id}"
            )
        if lease_seconds <= 0:
            raise PipelineDispatchError("lease_seconds must be > 0")

        if not self._dependencies_completed(
            pipeline=pipeline,
            state=state,
            task_id=task_id,
        ):
            raise PipelineDispatchError(
                f"task '{task_id}' cannot be claimed before dependencies complete"
            )

        now = claimed_at or _utc_now()
        assignment.status = TaskAssignmentStatus.CLAIMED
        assignment.claimed_agent_id = agent_id
        assignment.claimed_at = now
        assignment.last_heartbeat_at = now
        assignment.lease_expires_at = now + timedelta(seconds=lease_seconds)
        state.task_assignments[task_id] = assignment
        state.refresh_views(pipeline)
        return assignment

    def heartbeat_claim(
        self,
        pipeline: PipelineDefinition,
        state: PipelineExecutionState,
        task_id: str,
        *,
        heartbeat_at: datetime | None = None,
        lease_seconds: int = 300,
    ) -> TaskAssignment:
        """Heartbeat and lease extension for claimed/running tasks."""
        assignment = self._get_assignment(state, task_id=task_id)
        if assignment.status not in (
            TaskAssignmentStatus.CLAIMED,
            TaskAssignmentStatus.RUNNING,
            TaskAssignmentStatus.AWAITING_HUMAN,
        ):
            raise PipelineDispatchError(
                f"task '{task_id}' cannot heartbeat from status {assignment.status.value}"  # noqa: E501
            )
        if lease_seconds <= 0:
            raise PipelineDispatchError("lease_seconds must be > 0")

        now = heartbeat_at or _utc_now()
        assignment.last_heartbeat_at = now
        assignment.lease_expires_at = now + timedelta(seconds=lease_seconds)
        state.task_assignments[task_id] = assignment
        state.refresh_views(pipeline)
        return assignment

    def start_task(
        self,
        pipeline: PipelineDefinition,
        state: PipelineExecutionState,
        task_id: str,
    ) -> TaskAssignment:
        """Transition claimed task to running."""
        assignment = self._get_assignment(state, task_id=task_id)
        if assignment.status != TaskAssignmentStatus.CLAIMED:
            raise PipelineDispatchError(
                f"task '{task_id}' must be claimed before start"
            )
        assignment.status = TaskAssignmentStatus.RUNNING
        state.task_assignments[task_id] = assignment
        state.refresh_views(pipeline)
        return assignment

    def mark_task_awaiting_human(
        self,
        pipeline: PipelineDefinition,
        state: PipelineExecutionState,
        task_id: str,
    ) -> TaskAssignment:
        """Transition running task into awaiting_human state."""
        assignment = self._get_assignment(state, task_id=task_id)
        if assignment.status != TaskAssignmentStatus.RUNNING:
            raise PipelineDispatchError(
                f"task '{task_id}' must be running before awaiting_human"
            )
        assignment.status = TaskAssignmentStatus.AWAITING_HUMAN
        state.task_assignments[task_id] = assignment
        state.refresh_views(pipeline)
        return assignment

    def mark_task_completed(
        self,
        pipeline: PipelineDefinition,
        state: PipelineExecutionState,
        task_id: str,
    ) -> TaskAssignment:
        """Mark task as completed and release downstream dependencies."""
        assignment = self._get_assignment(state, task_id=task_id)
        if assignment.status not in (
            TaskAssignmentStatus.RUNNING,
            TaskAssignmentStatus.AWAITING_HUMAN,
            TaskAssignmentStatus.CLAIMED,
        ):
            raise PipelineDispatchError(
                f"task '{task_id}' cannot complete from status {assignment.status.value}"  # noqa: E501
            )
        assignment.status = TaskAssignmentStatus.COMPLETED
        assignment.failure_summary = None
        assignment.lease_expires_at = None
        state.task_assignments[task_id] = assignment
        state.refresh_views(pipeline)
        return assignment

    def mark_task_failed(
        self,
        pipeline: PipelineDefinition,
        state: PipelineExecutionState,
        task_id: str,
        *,
        failure_summary: str,
    ) -> TaskAssignment:
        """Mark task failed, applying retry policy when configured."""
        assignment = self._get_assignment(state, task_id=task_id)
        if assignment.status not in (
            TaskAssignmentStatus.RUNNING,
            TaskAssignmentStatus.AWAITING_HUMAN,
            TaskAssignmentStatus.CLAIMED,
        ):
            raise PipelineDispatchError(
                f"task '{task_id}' cannot fail from status {assignment.status.value}"
            )
        task = pipeline.get_task(task_id)
        if task is None:
            raise PipelineDispatchError(f"task '{task_id}' not found in pipeline")

        assignment.attempt_count += 1
        max_attempts = self._retry_max_attempts(task)
        assignment.failure_summary = failure_summary
        if assignment.attempt_count < max_attempts:
            assignment.status = TaskAssignmentStatus.ASSIGNED
            assignment.claimed_agent_id = None
            assignment.claimed_at = None
            assignment.last_heartbeat_at = None
            assignment.lease_expires_at = None
        else:
            assignment.status = TaskAssignmentStatus.FAILED

        state.task_assignments[task_id] = assignment
        state.refresh_views(pipeline)
        return assignment

    def cancel_task(
        self,
        pipeline: PipelineDefinition,
        state: PipelineExecutionState,
        task_id: str,
        *,
        reason: str,
    ) -> TaskAssignment:
        """Cancel a task assignment deterministically with audit reason."""
        assignment = self._get_assignment(state, task_id=task_id)
        if assignment.status in (
            TaskAssignmentStatus.COMPLETED,
            TaskAssignmentStatus.FAILED,
            TaskAssignmentStatus.CANCELLED,
        ):
            raise PipelineDispatchError(
                f"task '{task_id}' cannot be cancelled from status {assignment.status.value}"  # noqa: E501
            )
        assignment.status = TaskAssignmentStatus.CANCELLED
        assignment.failure_summary = reason
        assignment.lease_expires_at = None
        state.task_assignments[task_id] = assignment
        state.refresh_views(pipeline)
        return assignment

    def recover_expired_claims(
        self,
        pipeline: PipelineDefinition,
        state: PipelineExecutionState,
        *,
        now: datetime | None = None,
    ) -> list[str]:
        """Return stale claimed/running tasks to assigned status."""
        check_time = now or _utc_now()
        recovered: list[str] = []
        for task_id, assignment in state.task_assignments.items():
            if assignment.status not in (
                TaskAssignmentStatus.CLAIMED,
                TaskAssignmentStatus.RUNNING,
                TaskAssignmentStatus.AWAITING_HUMAN,
            ):
                continue
            if not assignment.is_lease_expired(check_time):
                continue
            assignment.status = TaskAssignmentStatus.ASSIGNED
            assignment.claimed_agent_id = None
            assignment.claimed_at = None
            assignment.last_heartbeat_at = None
            assignment.lease_expires_at = None
            state.task_assignments[task_id] = assignment
            recovered.append(task_id)
        state.refresh_views(pipeline)
        return sorted(recovered)

    def validate_typed_handoff(
        self,
        *,
        workflow_id: str,
        from_pipeline: PipelineDefinition,
        to_pipeline: PipelineDefinition,
        output_name: str,
        input_name: str,
        artifact_id: str,
        correlation_id: str,
        state: PipelineExecutionState,
    ) -> PipelineLineageRecord:
        """Validate cross-pipeline typed handoff and append lineage record."""
        produced_type = from_pipeline.output_contract.get(output_name)
        if produced_type is None:
            raise PipelineDispatchError(
                f"Pipeline '{from_pipeline.pipeline_id}' has no output contract for "
                f"'{output_name}'"
            )
        expected_type = to_pipeline.input_contract.get(input_name)
        if expected_type is None:
            raise PipelineDispatchError(
                f"Pipeline '{to_pipeline.pipeline_id}' has no input contract for "
                f"'{input_name}'"
            )
        if produced_type != expected_type:
            raise PipelineDispatchError(
                f"Typed handoff mismatch: {from_pipeline.pipeline_id}.{output_name}="
                f"{produced_type} != {to_pipeline.pipeline_id}.{input_name}={expected_type}"  # noqa: E501
            )

        record = PipelineLineageRecord(
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            from_pipeline_id=from_pipeline.pipeline_id,
            to_pipeline_id=to_pipeline.pipeline_id,
            output_name=output_name,
            output_type=produced_type,
            input_name=input_name,
            expected_input_type=expected_type,
            artifact_id=artifact_id,
            created_at=_utc_now(),
        )
        state.lineage_records.append(record)
        state.last_transition_at = _utc_now()
        return record

    def finalize_pipeline(
        self,
        state: PipelineExecutionState,
        *,
        output_artifacts: list[str] | None = None,
        trace_ids: list[str] | None = None,
    ) -> PipelineResult:
        """Create terminal pipeline result payload from execution state."""
        if state.status == PipelineExecutionStatus.COMPLETED:
            final_status: Literal["completed", "failed", "cancelled"] = "completed"
        elif state.status == PipelineExecutionStatus.CANCELLED:
            final_status = "cancelled"
        else:
            final_status = "failed"

        failure_summary = None
        if final_status != "completed":
            failed_entries = [
                f"{task_id}:{assignment.failure_summary or assignment.status.value}"
                for task_id, assignment in sorted(state.task_assignments.items())
                if assignment.status
                in (TaskAssignmentStatus.FAILED, TaskAssignmentStatus.CANCELLED)
            ]
            failure_summary = "; ".join(failed_entries) if failed_entries else None

        return PipelineResult(
            workflow_id=state.workflow_id,
            pipeline_id=state.pipeline_id,
            dispatch_id=state.dispatch_id,
            status=final_status,
            output_artifacts=output_artifacts or [],
            failure_summary=failure_summary,
            trace_ids=trace_ids or [],
        )

    def _resolve_task_owner(
        self,
        task: TaskDefinition,
        *,
        role_bindings: dict[str, str] | None = None,
    ) -> str:
        """Resolve deterministic assignment owner ID for a task."""
        if task.owner_agent_id is not None:
            return task.owner_agent_id
        if task.owner_role is None:
            raise PipelineDispatchError(f"task '{task.task_id}' missing owner selector")
        if role_bindings is None:
            raise PipelineDispatchError(
                f"task '{task.task_id}' uses owner_role without runtime role_bindings"
            )
        resolved = role_bindings.get(task.owner_role)
        if resolved is None or not resolved.strip():
            raise PipelineDispatchError(
                f"task '{task.task_id}' owner_role '{task.owner_role}' "
                "does not resolve through agents.role_bindings"
            )
        return resolved.strip()

    def _get_assignment(
        self, state: PipelineExecutionState, *, task_id: str
    ) -> TaskAssignment:
        """Get assignment by task ID or raise deterministic error."""
        assignment = state.task_assignments.get(task_id)
        if assignment is None:
            raise PipelineDispatchError(f"assignment not found for task '{task_id}'")
        return assignment

    def _dependencies_completed(
        self,
        *,
        pipeline: PipelineDefinition,
        state: PipelineExecutionState,
        task_id: str,
    ) -> bool:
        """Check whether all dependencies are completed for target task."""
        task = pipeline.get_task(task_id)
        if task is None:
            raise PipelineDispatchError(f"task '{task_id}' not found in pipeline")
        for dep_id in task.dependencies:
            dep_assignment = state.task_assignments.get(dep_id)
            if dep_assignment is None:
                raise PipelineDispatchError(
                    f"missing dependency assignment '{dep_id}' for task '{task_id}'"
                )
            if dep_assignment.status != TaskAssignmentStatus.COMPLETED:
                return False
        return True

    def _retry_max_attempts(self, task: TaskDefinition) -> int:
        """Read retry max attempts from retry policy with safe defaults."""
        raw_value = task.retry_policy.get("max_attempts", "1")
        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            return 1
        return max(value, 1)
