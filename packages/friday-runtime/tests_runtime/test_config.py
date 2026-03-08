# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
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
    assert cfg.config_policy.allow_env_override is False
    assert cfg.unknown_key_policy == "fail"


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


def test_artifacts_root_dir_resolves_under_runtime_root(tmp_path: Path):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)
    cfg = RuntimeConfig(
        install_root=str(install_root),
        runtime_data_root=str(runtime_data_root),
        workspace_root=str(workspace_root),
        artifacts_root_dir="artifacts",
    )
    assert cfg.resolve_artifacts_root_path("artifacts") == (
        runtime_data_root / "artifacts"
    ).resolve()


def test_artifacts_root_dir_outside_runtime_root_rejected(tmp_path: Path):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)
    with pytest.raises(ValueError, match="artifacts.root_dir"):
        RuntimeConfig(
            install_root=str(install_root),
            runtime_data_root=str(runtime_data_root),
            workspace_root=str(workspace_root),
            artifacts_root_dir=str(workspace_root / "artifacts"),
        )


def test_yaml_unknown_key_rejected(tmp_path: Path):
    config_path = tmp_path / "runtime.yaml"
    config_path.write_text(
        """
config_policy:
  allow_env_override: false
unexpected: true
""".strip()
    )

    with pytest.raises(ValueError, match="Unknown runtime config keys"):
        RuntimeConfig.from_yaml(config_path)


def test_yaml_env_override_disabled_keeps_yaml_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)
    config_path = tmp_path / "runtime.yaml"
    config_path.write_text(
        f"""
config_policy:
  allow_env_override: false
runtime_paths:
  install_root: {install_root}
  runtime_data_root: {runtime_data_root}
  workspace_root: {workspace_root}
llm:
  model: yaml-model
""".strip()
    )
    monkeypatch.setenv("FRIDAY_LLM_MODEL", "env-model")

    cfg = RuntimeConfig.from_sources(yaml_path=config_path)
    assert cfg.llm_model == "yaml-model"


def test_yaml_env_override_enabled_applies_env_values(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)
    config_path = tmp_path / "runtime.yaml"
    config_path.write_text(
        f"""
config_policy:
  allow_env_override: true
runtime_paths:
  install_root: {install_root}
  runtime_data_root: {runtime_data_root}
  workspace_root: {workspace_root}
llm:
  model: yaml-model
""".strip()
    )
    monkeypatch.setenv("FRIDAY_LLM_MODEL", "env-model")

    cfg = RuntimeConfig.from_sources(yaml_path=config_path)
    assert cfg.llm_model == "env-model"
    assert cfg.get_llm_service_config().model == "env-model"


def test_explicit_overrides_win_over_yaml_and_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)
    config_path = tmp_path / "runtime.yaml"
    config_path.write_text(
        f"""
config_policy:
  allow_env_override: true
runtime_paths:
  install_root: {install_root}
  runtime_data_root: {runtime_data_root}
  workspace_root: {workspace_root}
llm:
  model: yaml-model
""".strip()
    )
    monkeypatch.setenv("FRIDAY_LLM_MODEL", "env-model")

    cfg = RuntimeConfig.from_sources(
        yaml_path=config_path,
        overrides={"llm_model": "override-model"},
    )
    assert cfg.llm_model == "override-model"


def test_from_env_synthesizes_default_llm_pool_from_legacy_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    install_root, runtime_data_root, workspace_root = _make_roots(tmp_path)
    monkeypatch.setenv("FRIDAY_INSTALL_ROOT", str(install_root))
    monkeypatch.setenv("FRIDAY_RUNTIME_DATA_ROOT", str(runtime_data_root))
    monkeypatch.setenv("FRIDAY_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("FRIDAY_LLM_MODEL", "env-only-model")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    cfg = RuntimeConfig.from_env()
    assert cfg.llm_pool.default_service == "default"
    assert cfg.get_llm_service_config("default").model == "env-only-model"
