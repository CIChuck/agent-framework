from pathlib import Path

import pytest
from friday_runtime.config import RuntimeConfig


def _make_roots(tmp_path: Path) -> tuple[Path, Path, Path]:
    install_root = tmp_path / "install"
    runtime_data_root = tmp_path / "runtime-data" / "friday"
    workspace_root = tmp_path / "workspace"
    install_root.mkdir(parents=True)
    runtime_data_root.parent.mkdir(parents=True)
    workspace_root.mkdir(parents=True)
    return install_root, runtime_data_root, workspace_root


def test_default_memory_mode_is_single_agent(tmp_path: Path):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)

    cfg = RuntimeConfig(
        install_root=str(install_root),
        runtime_data_root=str(runtime_data_root),
        workspace_root=str(workspace_root),
    )
    assert cfg.memory_mode == "single_agent"


def test_invalid_memory_mode_rejected(tmp_path: Path):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)

    with pytest.raises(ValueError, match="memory_mode"):
        RuntimeConfig(
            memory_mode="invalid",
            install_root=str(install_root),
            runtime_data_root=str(runtime_data_root),
            workspace_root=str(workspace_root),
        )


def test_invalid_deployment_profile_rejected(tmp_path: Path):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)

    with pytest.raises(ValueError, match="deployment_profile"):
        RuntimeConfig(
            deployment_profile="invalid",  # type: ignore[arg-type]
            install_root=str(install_root),
            runtime_data_root=str(runtime_data_root),
            workspace_root=str(workspace_root),
        )


def test_runtime_and_workspace_overlap_rejected(tmp_path: Path):
    install_root = tmp_path / "install"
    shared_root = tmp_path / "shared"
    install_root.mkdir(parents=True)
    shared_root.mkdir(parents=True)

    with pytest.raises(ValueError, match="must not overlap"):
        RuntimeConfig(
            install_root=str(install_root),
            runtime_data_root=str(shared_root / "runtime"),
            workspace_root=str(shared_root),
        )


def test_sqlite_scratch_must_live_under_runtime_root(tmp_path: Path):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)
    scratch_path = runtime_data_root / "scratchpad.sqlite3"

    cfg = RuntimeConfig(
        install_root=str(install_root),
        runtime_data_root=str(runtime_data_root),
        workspace_root=str(workspace_root),
        scratch_backend="sqlite",
        scratch_path=str(scratch_path),
    )
    assert cfg.scratch_backend == "sqlite"


def test_sqlite_scratch_in_workspace_rejected(tmp_path: Path):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)

    with pytest.raises(ValueError, match="runtime_data_root"):
        RuntimeConfig(
            install_root=str(install_root),
            runtime_data_root=str(runtime_data_root),
            workspace_root=str(workspace_root),
            scratch_backend="sqlite",
            scratch_path=str(workspace_root / "scratchpad.sqlite3"),
        )


def test_deployment_profile_defaults_container():
    defaults = RuntimeConfig.deployment_profile_defaults("container")
    assert defaults["install_root"] == "/opt/friday"
    assert defaults["runtime_data_root"] == "/var/lib/friday/runtime"
    assert defaults["workspace_root"] == "/workspace"


def test_workspace_artifact_path_resolution_and_rejection(tmp_path: Path):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)
    cfg = RuntimeConfig(
        install_root=str(install_root),
        runtime_data_root=str(runtime_data_root),
        workspace_root=str(workspace_root),
    )
    artifact_path = cfg.resolve_workspace_artifact_path("artifacts/result.md")
    assert artifact_path == (workspace_root / "artifacts" / "result.md").resolve()

    with pytest.raises(ValueError, match="workspace_root"):
        cfg.resolve_workspace_artifact_path(str(runtime_data_root / "bad.txt"))


def test_runtime_state_path_resolution_and_rejection(tmp_path: Path):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)
    cfg = RuntimeConfig(
        install_root=str(install_root),
        runtime_data_root=str(runtime_data_root),
        workspace_root=str(workspace_root),
    )
    state_path = cfg.resolve_runtime_state_path("journals/promotions.jsonl")
    assert state_path == (runtime_data_root / "journals" / "promotions.jsonl").resolve()

    with pytest.raises(ValueError, match="runtime_data_root"):
        cfg.resolve_runtime_state_path(str(workspace_root / "bad.jsonl"))
