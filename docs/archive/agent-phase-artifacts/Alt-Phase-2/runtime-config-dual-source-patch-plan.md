# Runtime Config Dual-Source Patch Plan

## Objective

Add YAML runtime configuration support to `friday-runtime` while preserving existing env-based compatibility, with explicit policy control over whether environment variables can override YAML.

Locked decisions:

1. Environment variables do not override YAML unless explicitly enabled.
2. Runtime YAML uses nested sections.
3. Secrets in YAML are allowed for now, with a documented future migration to key-store based isolation.

## Patch Scope

1. `packages/friday-runtime/src/friday_runtime/config.py`
2. `packages/friday-runtime/tests_runtime/test_config.py`
3. `packages/friday-runtime/src/friday_runtime/kernel.py` (integration touchpoint only if needed)
4. `docs/archive/agent-phase-artifacts/Alt-Phase-2/technical-specifications.md`
5. `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-build-plan.md`
6. `docs/archive/agent-phase-artifacts/Alt-Phase-2/phase-3-transition-plan.md`
7. `docs/archive/agent-phase-artifacts/Alt-Phase-2/README.md`

## Design Contract

1. Add nested YAML runtime schema sections:
   - `llm`
   - `embedding`
   - `memory`
   - `telemetry`
   - `agents`
   - `runtime_paths`
   - `scratch`
   - `config_policy`
2. Add `config_policy.allow_env_override: false` default.
3. Define deterministic merge precedence:
   - `defaults -> yaml -> env (only if allow_env_override=true) -> explicit constructor args`.
4. Preserve `RuntimeConfig.from_env()` as a backward-compatible path.
5. Add `RuntimeConfig.from_yaml(path)` as YAML-first runtime entry point.
6. Add unified source merge behavior (conceptually `from_sources`) to keep loading deterministic and testable.

## Validation and Runtime Semantics

1. Run existing runtime validation after merge:
   - `memory_mode`
   - deployment profile constraints
   - runtime root overlap checks
   - scratch path placement checks
2. Resolve relative YAML paths from the YAML file directory.
3. Add strict-mode handling for unknown keys (failure mode defined in spec).
4. Track field provenance (source per field) for diagnostics.

## Security and Secrets

1. Accept secrets in YAML in current version.
2. Add an explicit documentation note:
   - secrets are currently permitted in YAML for compatibility,
   - future phase will migrate to external secret provider/key store,
   - plaintext secret usage will be deprecated in a later release.

## Test Plan

1. YAML-only load path.
2. Env-only legacy load path.
3. Mixed source with `allow_env_override=false`.
4. Mixed source with `allow_env_override=true`.
5. Invalid nested structure and unknown key behavior.
6. Relative path resolution from YAML directory.
7. Secret fields present in YAML (accepted; warning/notice behavior as specified).
8. Runtime kernel boots successfully using YAML-derived `RuntimeConfig`.

## Documentation Patch Plan

1. Update `technical-specifications.md` with:
   - nested runtime schema,
   - source precedence,
   - override policy.
2. Update `phase-3-build-plan.md` with explicit implementation tasks for YAML runtime config support.
3. Update `phase-3-transition-plan.md` with migration and compatibility guidance.
4. Update `README.md` with operator-facing precedence and secret policy summary.

## Acceptance Criteria

1. Env does not override YAML unless `allow_env_override=true`.
2. Nested YAML runtime config is fully supported and validated.
3. Env-only startup path remains functional and unchanged.
4. Runtime boot and single-agent execution remain backward compatible.
5. Documentation clearly states current secret policy and future key-store migration direction.
