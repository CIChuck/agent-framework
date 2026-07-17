# Phase 4-A to 4-B Brief

## Ready Inputs for 4-B

1. Runtime typed factory mapping by `agent_type` is available in `friday_runtime.kernel`.
2. Runtime startup preflight rejects unknown `llm_service` and unregistered `agent_type`.
3. Runtime `artifacts` policy/schema/path validation is available in `friday_runtime.config`.
4. Agent YAML unknown-key hard-fail and profile schema updates are available in `friday_agent.loader` and `friday_agent.profile`.

## Deferred Work for 4-B

1. Canonical `workflow -> pipeline -> task` dispatch path activation.
2. Owner resolution through `agents.role_bindings`.
3. Cross-layer artifact contracts: `required_artifacts`, `artifact_contract`, `output_artifacts`.
4. `workflow_mode`-driven legacy adapter routing and migration governance.
5. Execution evidence plumbing for workflow/pipeline/task lineage.

## Intake Warning

1. `phase-4-execution-plan.md` remains stale and should be treated as a historical, non-authoritative reference during 4-B execution.
