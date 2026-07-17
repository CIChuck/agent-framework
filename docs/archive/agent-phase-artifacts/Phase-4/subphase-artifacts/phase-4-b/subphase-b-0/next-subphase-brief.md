# Phase 4-B B1 Brief

## Next Execution Target

1. Subphase B1: canonical dispatch core.

## Required Focus

1. Use the existing `WorkflowPipelineDefinition` and `PipelineDispatchEngine` foundation rather than rebuilding hierarchy models.
2. Route `RuntimeKernel.execute_workflow()` through the canonical workflow/pipeline/task path.
3. Keep owner-resolution governance explicit and deterministic so B2 can tighten policy rather than redesign flow.
4. Do not regress the legacy workflow path until `workflow_mode` routing is implemented in B4.

## Inputs

1. `packages/friday-runtime/src/friday_runtime/kernel.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `packages/friday-agent/src/friday_agent/workflows/models.py`
4. `packages/friday-agent/src/friday_agent/workflows/loader.py`
5. `packages/friday-agent/tests_agent/test_workflows.py`
6. `packages/friday-agent/tests_agent/test_pipeline_dispatch.py`
