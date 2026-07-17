# Phase 3 Subphase 6 Path Governance Runbook

## Objective

Prevent workspace contamination and ensure runtime-state isolation across deployment profiles.

## Enforcement Points

1. Validate topology at configuration load:
   - `install_root`, `runtime_data_root`, and `workspace_root` must be distinct where required by profile.
2. Validate artifact writes through `resolve_workspace_artifact_path(...)`.
3. Validate runtime-state writes through `resolve_runtime_state_path(...)`.

## Failure Modes and Actions

1. Artifact path outside workspace root
   - Signal: `ValueError("artifact path must be under workspace_root")`
   - Action: block write, correct producer path mapping.
2. Runtime-state path outside runtime data root
   - Signal: `ValueError("runtime state path must be under runtime_data_root")`
   - Action: block write, redirect state writer to runtime-data path helper.
3. Runtime-state path under workspace root
   - Signal: `ValueError("runtime state path must not be under workspace_root")`
   - Action: block write, remediate topology configuration.

## Verification Checklist

1. Profile defaults resolve expected paths for local/container/cloud.
2. Workspace artifact writes pass for in-root paths and fail for out-of-root paths.
3. Runtime-state writes pass for runtime-data-root paths and fail for workspace-root paths.
4. Full gate results recorded in subphase verification artifacts.
