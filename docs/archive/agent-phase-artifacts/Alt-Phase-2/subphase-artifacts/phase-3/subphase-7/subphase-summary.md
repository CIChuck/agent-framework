# Phase 3 Subphase 7 Summary

## Scope Completed

1. Added hierarchical workflow/pipeline/task contract models for dispatch-oriented orchestration:
   - `WorkflowPipelineDefinition`
   - `TaskDefinition`
   - `TaskAssignment`
   - `PipelineDefinition`
   - `PipelineDispatch`
   - `PipelineExecutionState`
   - `PipelineResult`
   - `PipelineLineageRecord`
2. Added assignment and execution lifecycle enums:
   - `TaskAssignmentStatus`
   - `PipelineExecutionStatus`
3. Implemented `PipelineDispatchEngine` with deterministic lifecycle operations:
   - hierarchy validation,
   - dispatch initialization,
   - dependency-ready assignment resolution,
   - claim/start/awaiting-human/complete/fail/cancel transitions,
   - lease heartbeat and stale-claim recovery,
   - typed cross-pipeline handoff validation,
   - lineage record capture,
   - pipeline result finalization.
4. Exported new Subphase 7 contracts from workflow package API.
5. Added focused test coverage for hierarchy integrity, claim/lease semantics, retry behavior, typed handoff validation, and result finalization.

## Decisions Made

1. Implemented Subphase 7 as additive contracts and engine behavior to preserve existing `WorkflowEngine` compatibility.
2. Kept deterministic ordering by sorting runnable task IDs for assignment resolution.
3. Enforced typed cross-pipeline handoff via explicit pipeline input/output contract maps and lineage records.
4. Kept retry semantics local to assignment lifecycle with explicit `max_attempts` policy parsing.

## Changed Files

1. `packages/friday-agent/src/friday_agent/workflows/models.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `packages/friday-agent/src/friday_agent/workflows/__init__.py`
4. `packages/friday-agent/tests_agent/test_pipeline_dispatch.py`

## Unresolved Risks

1. Workflow-level orchestration that executes composed multi-pipeline runs end-to-end remains for subsequent subphase integration.
2. Compensation-policy runbook coverage for composed pipelines remains to be expanded in closeout.
3. Full-repo lint backlog remains inherited baseline debt.
4. Full-gate mypy command/path issue (`packages apps tests`) remains inherited baseline debt.
