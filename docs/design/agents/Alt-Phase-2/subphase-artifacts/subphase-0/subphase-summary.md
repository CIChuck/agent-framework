# Subphase 0 Summary

## Scope Completed

1. Re-validated baseline constraints from the execution plan and encoded Step 1 additive contracts.
2. Added runtime config contracts for:
   - memory mode (`single_agent` default, `multi_agent` opt-in),
   - runtime filesystem roots (`install_root`, `runtime_data_root`, `workspace_root`, optional `cache_root`),
   - scratch backend/path validation constraints.
3. Added additive multi-agent interface contracts in `friday-core`:
   - `NamespacePolicyInterface`,
   - `MultiAgentMemoryInterface`,
   - `ArbitrationInterface`,
   - proposal/capability/decision contract types.
4. Fixed baseline interface test drift for `EpisodicStoreAdapter.mark_compacted`.
5. Added runtime config unit tests for memory mode + root/scratch validation behavior.

## Decisions Made

1. Backward compatibility preserved via additive-only interfaces and config fields.
2. Default mode remains `single_agent`.
3. Persistent scratch paths are validated against runtime root topology.
4. Runtime root overlap between `runtime_data_root` and `workspace_root` is denied at config validation.

## Unresolved Risks

1. Global `ruff` backlog remains high and unrelated to this subphase.
2. `mypy` binary is missing from `.venv`; type gate not executable yet.
3. `uv` binary remains unstable in this environment (panic observed previously), so `.venv` tooling was used for gate execution.

## Changed Files

1. `packages/friday-core/tests_core/test_interfaces.py`
2. `packages/friday-core/src/friday_core/interfaces/memory.py`
3. `packages/friday-core/src/friday_core/interfaces/__init__.py`
4. `packages/friday-core/src/friday_core/__init__.py`
5. `packages/friday-runtime/src/friday_runtime/config.py`
6. `packages/friday-runtime/tests_runtime/test_config.py`
