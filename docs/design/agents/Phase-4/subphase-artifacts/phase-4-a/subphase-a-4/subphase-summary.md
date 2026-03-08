# Phase 4-A Subphase A4 Summary

## Status

Completed.

## Delivered

1. Runtime YAML/config-policy foundation was implemented and verified.
2. Named `llm_pool` service wiring and strict/non-strict agent `llm_service` validation were implemented and verified.
3. Generic typed runtime factory mapping was implemented with `InteractiveAgent` as the direct runtime default and `CopilotAgent` retained as a Phase 4 compatibility alias.
4. Agent/runtime startup now fails deterministically on invalid `llm_service` bindings and unregistered `agent_type` mappings before dispatch.

## Scope Notes

1. Phase 4-A completed Workstreams A-D only.
2. Cross-layer workflow/pipeline/task artifact contracts remain deferred to Phase 4-B Workstream J.
3. Canonical `workflow -> pipeline -> task` dispatch behavior remains deferred to Phase 4-B Workstream E.

## Outputs

1. `packages/friday-runtime/src/friday_runtime/config.py`
2. `packages/friday-runtime/src/friday_runtime/di.py`
3. `packages/friday-runtime/src/friday_runtime/kernel.py`
4. `packages/friday-agent/src/friday_agent/profile.py`
5. `packages/friday-agent/src/friday_agent/loader.py`
6. `packages/friday-agent/src/friday_agent/repl_base.py`
7. `packages/friday-agent/src/friday_agent/interactive.py`
8. `packages/friday-agent/src/friday_agent/copilot.py`
9. `packages/friday-cli/src/friday_cli/container.py`

## Handoff Position

1. Phase 4-B may consume the typed factory seam and strict startup validation immediately.
2. Full companion-set coherence is recorded as `drift_accepted` because `phase-4-execution-plan.md` remains stale and non-authoritative relative to the active split plans.
