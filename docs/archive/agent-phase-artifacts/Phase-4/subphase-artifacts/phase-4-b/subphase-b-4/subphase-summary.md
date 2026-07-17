# Subphase B4 Summary

Status: complete

Implemented the explicit legacy adapter path and auditable workflow-mode routing.

Key outcomes:
- Legacy flat workflows are translated into a canonical single-pipeline bundle.
- `workflow_mode=legacy` routes through the adapter into canonical execution.
- `workflow_mode=auto` prefers canonical and falls back to the legacy adapter path.
- Runtime emits `workflow_mode_selected` for auditable routing decisions.

Primary files:
- `packages/friday-agent/src/friday_agent/workflows/loader.py`
- `packages/friday-agent/src/friday_agent/workflows/engine.py`
- `packages/friday-runtime/src/friday_runtime/kernel.py`
- `packages/friday-agent/tests_agent/test_workflows.py`
- `packages/friday-runtime/tests_runtime/test_kernel.py`
