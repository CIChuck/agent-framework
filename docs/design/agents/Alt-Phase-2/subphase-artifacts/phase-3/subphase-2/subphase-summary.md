# Phase 3 Subphase 2 Summary

## Scope Completed

1. Implemented structured HITL contract models for request/decision payloads, authority policy, and artifact policy controls.
2. Extended workflow execution state with `pending_hitl_request`, `hitl_history`, and governed `artifacts` tracking.
3. Implemented execution-grade HITL handling in workflow engine:
   - structured HITL request creation,
   - callback normalization (`bool` or structured decision),
   - authority validation,
   - timeout default actions (`safe_abort`, `constrained_continue`, `defer`),
   - deterministic decision application via `decide_task(...)`.
4. Preserved compatibility for existing approval APIs (`approve_task`, `reject_task`, `skip_task`, `resolve_task`) while routing through structured decision handling.
5. Implemented artifact lifecycle governance:
   - registration with provenance validation,
   - lifecycle transition controls (`draft -> validated -> final -> archived`),
   - publication approval enforcement when configured.
6. Added workflow tests for HITL payload creation, authority enforcement, timeout behavior, and artifact lifecycle/publication controls.

## Decisions Made

1. Kept all HITL and artifact controls additive and policy-driven; defaults remain backward compatible.
2. Retained legacy approval callback support while introducing structured HITL callback support.
3. Mapped timeout `safe_abort` to deterministic failed-task state and workflow-level failed completion.
4. Required artifact provenance fields only when artifact policy is configured.

## Changed Files

1. `packages/friday-agent/src/friday_agent/workflows/models.py`
2. `packages/friday-agent/src/friday_agent/workflows/engine.py`
3. `packages/friday-agent/src/friday_agent/workflows/__init__.py`
4. `packages/friday-agent/tests_agent/test_workflows.py`

## Unresolved Risks

1. Full-repo `ruff` backlog remains inherited baseline debt and is out of Subphase 2 scope.
2. Full-gate `mypy packages apps tests` command path issue remains baseline gate debt (`apps` has no top-level `.py` files).
