# Phase 3 Subphase 6 Summary

## Scope Completed

1. Extended runtime configuration with explicit deployment profile support:
   - `local`, `container`, `cloud`.
2. Added profile-default topology templates via `RuntimeConfig.deployment_profile_defaults(...)`.
3. Added explicit path-policy helpers:
   - `resolve_workspace_artifact_path(...)` enforces artifact output under `workspace_root`,
   - `resolve_runtime_state_path(...)` enforces runtime state under `runtime_data_root` and outside `workspace_root`.
4. Added runtime config validation coverage for:
   - invalid deployment profile rejection,
   - workspace artifact-path governance,
   - runtime-state path governance.
5. Added deployment-profile template and path-governance runbook artifacts for operations usage.

## Decisions Made

1. Kept path-policy enforcement additive in runtime config helper APIs to avoid breaking existing call sites.
2. Treated path-policy violations as deterministic configuration/runtime errors rather than silent path rewriting.
3. Kept deployment templates as defaults + documentation artifacts, allowing environment-specific overrides.

## Changed Files

1. `packages/friday-runtime/src/friday_runtime/config.py`
2. `packages/friday-runtime/tests_runtime/test_config.py`
3. `docs/design/agents/Alt-Phase-2/subphase-artifacts/phase-3/subphase-6/deployment-profile-templates.md`
4. `docs/design/agents/Alt-Phase-2/subphase-artifacts/phase-3/subphase-6/path-governance-runbook.md`

## Unresolved Risks

1. Enforcement currently depends on consumers adopting new path-resolution helpers where file writes occur.
2. Full-repo lint backlog remains inherited baseline debt.
3. Full-gate mypy command/path issue (`packages apps tests`) remains inherited baseline debt.
