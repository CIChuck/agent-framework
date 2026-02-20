# Phase 3 Subphase 6 Deployment Profile Templates

## Profile Defaults

`RuntimeConfig.deployment_profile_defaults(...)` defines three topology templates:

1. `local`
   - `install_root`: current working directory
   - `runtime_data_root`: `~/.friday/runtime`
   - `workspace_root`: current working directory
2. `container`
   - `install_root`: `/opt/friday`
   - `runtime_data_root`: `/var/lib/friday/runtime`
   - `workspace_root`: `/workspace`
3. `cloud`
   - `install_root`: `/srv/friday/install`
   - `runtime_data_root`: `/srv/friday/runtime`
   - `workspace_root`: `/srv/friday/workspace`

## Path Policy Rules

1. Artifacts must resolve under `workspace_root` using `resolve_workspace_artifact_path(...)`.
2. Runtime internals (journals, indexes, scratch persistence) must resolve under `runtime_data_root` using `resolve_runtime_state_path(...)`.
3. Runtime paths must not overlap `workspace_root`.

## Operational Guidance

1. Treat template values as safe defaults; override with environment-specific paths when required.
2. In container/cloud deployments, keep `install_root` read-only and route mutable state to `runtime_data_root`.
3. Reject and log invalid path topology at startup rather than rewriting paths silently.
