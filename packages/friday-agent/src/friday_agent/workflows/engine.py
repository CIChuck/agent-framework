"""
Workflow execution engine.

All mutable runtime state is tracked in WorkflowExecution.task_states.
TaskNode objects are never mutated — the same WorkflowDefinition can
be executed concurrently without state collision.

Ref: docs/build-plan/to-do/dynamic-workflows-build-plan.md
Ref: Phase 1 Build Plan, Step 3
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Literal

from friday_memory.multi_agent import ScratchPlanItemStatus

from friday_agent.workflows.models import (
    ArtifactLifecycleState,
    ArtifactPolicy,
    ArtifactRecord,
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
                assigned_agent_id=self._resolve_task_owner(task),
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

    def _resolve_task_owner(self, task: TaskDefinition) -> str:
        """Resolve deterministic assignment owner ID for a task."""
        if task.owner_agent_id is not None:
            return task.owner_agent_id
        if task.owner_role is None:
            raise PipelineDispatchError(f"task '{task.task_id}' missing owner selector")
        return f"role:{task.owner_role}"

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
