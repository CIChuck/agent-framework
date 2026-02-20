"""Tests for workflow->pipeline->task dispatch and assignment semantics."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from friday_agent.workflows import (
    PipelineDefinition,
    PipelineDispatch,
    PipelineDispatchEngine,
    PipelineDispatchError,
    PipelineExecutionStatus,
    TaskAssignmentStatus,
    TaskDefinition,
    WorkflowPipelineDefinition,
)
from pydantic import ValidationError


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _build_pipeline(
    pipeline_id: str,
    *,
    workflow_id: str = "wf_main",
    upstream_pipeline_ids: tuple[str, ...] = (),
) -> PipelineDefinition:
    return PipelineDefinition(
        pipeline_id=pipeline_id,
        version="1.0.0",
        workflow_id=workflow_id,
        goal=f"Goal for {pipeline_id}",
        upstream_pipeline_ids=upstream_pipeline_ids,
        tasks=[
            TaskDefinition(
                task_id="task_a",
                name="Task A",
                description="Start",
                owner_agent_id="agent_a",
                output_contract={"summary": "text/plain"},
                retry_policy={"max_attempts": "2"},
            ),
            TaskDefinition(
                task_id="task_b",
                name="Task B",
                description="Depends on A",
                owner_role="reviewer",
                dependencies=["task_a"],
                input_contract={"summary": "text/plain"},
                output_contract={"report": "text/markdown"},
            ),
        ],
        input_contract={"summary": "text/plain"},
        output_contract={"report": "text/markdown"},
    )


def _build_dispatch(
    *,
    workflow_id: str = "wf_main",
    pipeline_id: str = "pipe_a",
    dispatch_mode: str = "async",
) -> PipelineDispatch:
    return PipelineDispatch(
        dispatch_id="dispatch_001",
        workflow_id=workflow_id,
        pipeline_id=pipeline_id,
        session_id="sess_1",
        run_id="run_1",
        dispatch_mode=dispatch_mode,
        priority=10,
        requested_by="tester",
        started_at=_now(),
    )


def test_task_definition_requires_exactly_one_owner_selector() -> None:
    with pytest.raises(ValidationError, match="exactly one"):
        TaskDefinition(
            task_id="task",
            name="Bad",
            description="bad",
            owner_agent_id="agent",
            owner_role="role",
        )

    with pytest.raises(ValidationError, match="exactly one"):
        TaskDefinition(
            task_id="task",
            name="Bad",
            description="bad",
        )


def test_pipeline_definition_validates_dependency_graph() -> None:
    pipeline = _build_pipeline("pipe_a")
    assert pipeline.validate_graph() == []
    assert pipeline.get_task_order() == ["task_a", "task_b"]


def test_workflow_pipeline_reference_integrity_and_composition_order() -> None:
    workflow = WorkflowPipelineDefinition(
        workflow_id="wf_main",
        version="1.0.0",
        name="Main workflow",
        goal="Do work",
        pipeline_refs=["pipe_a", "pipe_b"],
        entry_pipeline_id="pipe_a",
    )
    pipe_a = _build_pipeline("pipe_a")
    pipe_b = _build_pipeline("pipe_b", upstream_pipeline_ids=("pipe_a",))
    pipelines = {"pipe_a": pipe_a, "pipe_b": pipe_b}

    assert workflow.validate_reference_integrity(pipelines) == []
    assert workflow.get_pipeline_order(pipelines) == ["pipe_a", "pipe_b"]


def test_validate_hierarchy_rejects_unknown_pipeline_reference() -> None:
    engine = PipelineDispatchEngine()
    workflow = WorkflowPipelineDefinition(
        workflow_id="wf_main",
        version="1.0.0",
        name="Main workflow",
        goal="Do work",
        pipeline_refs=["missing_pipe"],
        entry_pipeline_id="missing_pipe",
    )
    with pytest.raises(PipelineDispatchError, match="unknown pipelines"):
        engine.validate_hierarchy(workflow, pipelines={})


def test_initialize_dispatch_and_ready_assignments() -> None:
    engine = PipelineDispatchEngine()
    workflow = WorkflowPipelineDefinition(
        workflow_id="wf_main",
        version="1.0.0",
        name="Main workflow",
        goal="Do work",
        pipeline_refs=["pipe_a"],
        entry_pipeline_id="pipe_a",
    )
    pipeline = _build_pipeline("pipe_a")
    dispatch = _build_dispatch()

    state = engine.initialize_dispatch(workflow, pipeline, dispatch)
    ready = engine.assign_dependency_ready_tasks(pipeline, state)

    assert state.status == PipelineExecutionStatus.RUNNING
    assert [a.task_id for a in ready] == ["task_a"]
    assert ready[0].assigned_agent_id == "agent_a"


def test_claim_requires_dependencies_completed() -> None:
    engine = PipelineDispatchEngine()
    workflow = WorkflowPipelineDefinition(
        workflow_id="wf_main",
        version="1.0.0",
        name="Main workflow",
        goal="Do work",
        pipeline_refs=["pipe_a"],
        entry_pipeline_id="pipe_a",
    )
    pipeline = _build_pipeline("pipe_a")
    state = engine.initialize_dispatch(workflow, pipeline, _build_dispatch())

    with pytest.raises(PipelineDispatchError, match="dependencies"):
        engine.claim_task(
            pipeline=pipeline,
            state=state,
            task_id="task_b",
            agent_id="role:reviewer",
        )

    engine.claim_task(
        pipeline=pipeline,
        state=state,
        task_id="task_a",
        agent_id="agent_a",
    )
    engine.start_task(pipeline, state, "task_a")
    engine.mark_task_completed(pipeline, state, "task_a")

    claimed = engine.claim_task(
        pipeline=pipeline,
        state=state,
        task_id="task_b",
        agent_id="role:reviewer",
    )
    assert claimed.status == TaskAssignmentStatus.CLAIMED


def test_lease_heartbeat_and_recovery() -> None:
    engine = PipelineDispatchEngine()
    workflow = WorkflowPipelineDefinition(
        workflow_id="wf_main",
        version="1.0.0",
        name="Main workflow",
        goal="Do work",
        pipeline_refs=["pipe_a"],
        entry_pipeline_id="pipe_a",
    )
    pipeline = _build_pipeline("pipe_a")
    state = engine.initialize_dispatch(workflow, pipeline, _build_dispatch())

    claim_time = _now()
    claimed = engine.claim_task(
        pipeline=pipeline,
        state=state,
        task_id="task_a",
        agent_id="agent_a",
        lease_seconds=5,
        claimed_at=claim_time,
    )
    assert claimed.lease_expires_at == claim_time + timedelta(seconds=5)

    heartbeated = engine.heartbeat_claim(
        pipeline=pipeline,
        state=state,
        task_id="task_a",
        heartbeat_at=claim_time + timedelta(seconds=2),
        lease_seconds=8,
    )
    assert heartbeated.lease_expires_at == claim_time + timedelta(seconds=10)

    recovered = engine.recover_expired_claims(
        pipeline=pipeline,
        state=state,
        now=claim_time + timedelta(seconds=11),
    )
    assert recovered == ["task_a"]
    assert state.task_assignments["task_a"].status == TaskAssignmentStatus.ASSIGNED


def test_mark_failed_requeues_when_retry_budget_available() -> None:
    engine = PipelineDispatchEngine()
    workflow = WorkflowPipelineDefinition(
        workflow_id="wf_main",
        version="1.0.0",
        name="Main workflow",
        goal="Do work",
        pipeline_refs=["pipe_a"],
        entry_pipeline_id="pipe_a",
    )
    pipeline = _build_pipeline("pipe_a")
    state = engine.initialize_dispatch(workflow, pipeline, _build_dispatch())

    engine.claim_task(
        pipeline=pipeline,
        state=state,
        task_id="task_a",
        agent_id="agent_a",
    )
    engine.start_task(pipeline, state, "task_a")
    assignment = engine.mark_task_failed(
        pipeline=pipeline,
        state=state,
        task_id="task_a",
        failure_summary="transient failure",
    )
    assert assignment.status == TaskAssignmentStatus.ASSIGNED
    assert assignment.attempt_count == 1


def test_typed_cross_pipeline_handoff_records_lineage() -> None:
    engine = PipelineDispatchEngine()
    workflow = WorkflowPipelineDefinition(
        workflow_id="wf_main",
        version="1.0.0",
        name="Main workflow",
        goal="Do work",
        pipeline_refs=["pipe_a", "pipe_b"],
        entry_pipeline_id="pipe_a",
    )
    pipe_a = _build_pipeline("pipe_a")
    pipe_b = _build_pipeline("pipe_b", upstream_pipeline_ids=("pipe_a",))
    pipe_b.input_contract["summary"] = "text/markdown"
    state = engine.initialize_dispatch(
        workflow,
        pipe_a,
        _build_dispatch(pipeline_id="pipe_a"),
    )

    record = engine.validate_typed_handoff(
        workflow_id=workflow.workflow_id,
        from_pipeline=pipe_a,
        to_pipeline=pipe_b,
        output_name="report",
        input_name="summary",
        artifact_id="artifact_123",
        correlation_id="corr_1",
        state=state,
    )
    assert record.output_type == "text/markdown"
    assert len(state.lineage_records) == 1


def test_typed_cross_pipeline_handoff_rejects_type_mismatch() -> None:
    engine = PipelineDispatchEngine()
    workflow = WorkflowPipelineDefinition(
        workflow_id="wf_main",
        version="1.0.0",
        name="Main workflow",
        goal="Do work",
        pipeline_refs=["pipe_a", "pipe_b"],
        entry_pipeline_id="pipe_a",
    )
    pipe_a = _build_pipeline("pipe_a")
    pipe_b = _build_pipeline("pipe_b", upstream_pipeline_ids=("pipe_a",))
    pipe_b.input_contract["summary"] = "application/json"
    state = engine.initialize_dispatch(
        workflow,
        pipe_a,
        _build_dispatch(pipeline_id="pipe_a"),
    )

    with pytest.raises(PipelineDispatchError, match="Typed handoff mismatch"):
        engine.validate_typed_handoff(
            workflow_id=workflow.workflow_id,
            from_pipeline=pipe_a,
            to_pipeline=pipe_b,
            output_name="report",
            input_name="summary",
            artifact_id="artifact_123",
            correlation_id="corr_1",
            state=state,
        )


def test_finalize_pipeline_result_uses_failure_summary() -> None:
    engine = PipelineDispatchEngine()
    workflow = WorkflowPipelineDefinition(
        workflow_id="wf_main",
        version="1.0.0",
        name="Main workflow",
        goal="Do work",
        pipeline_refs=["pipe_a"],
        entry_pipeline_id="pipe_a",
    )
    pipeline = _build_pipeline("pipe_a")
    task_a = pipeline.get_task("task_a")
    assert task_a is not None
    task_a.retry_policy["max_attempts"] = "1"
    state = engine.initialize_dispatch(workflow, pipeline, _build_dispatch())
    engine.claim_task(
        pipeline=pipeline,
        state=state,
        task_id="task_a",
        agent_id="agent_a",
    )
    engine.start_task(pipeline, state, "task_a")
    engine.mark_task_failed(
        pipeline=pipeline,
        state=state,
        task_id="task_a",
        failure_summary="terminal failure",
    )

    result = engine.finalize_pipeline(state)
    assert result.status == "failed"
    assert result.failure_summary is not None
    assert "terminal failure" in result.failure_summary
