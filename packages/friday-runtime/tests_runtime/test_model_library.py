"""Runtime model-library file-policy tests."""

from pathlib import Path

import pytest
from friday_core.profiles import MemoryProfile
from friday_runtime.config import RuntimeConfig
from friday_runtime.di import DIContainer
from friday_runtime.model_library import ModelLibraryLoadError, load_model_library


def _write_catalog(path: Path, *, marker: str = "local") -> None:
    path.write_text(
        f"""
schema: friday.model-library/v1
endpoints:
  {marker}:
    api_base: http://127.0.0.1:1234/v1
    provider: openai_compatible
profiles:
  chat:
    kind: chat
    endpoint: {marker}
    dialect: openai_chat_completions
    model: openai/qwen3.8
    model_target:
      model_id: qwen3.8
      family: qwen3_8
      revision: exact
""".strip()
    )


def test_relative_catalog_path_is_resolved_against_runtime_yaml(tmp_path: Path) -> None:
    config_dir = tmp_path / "configuration"
    config_dir.mkdir()
    runtime_path = config_dir / "config.yaml"
    runtime_path.write_text("model_library:\n  path: models-config.yaml\n")
    catalog_path = config_dir / "models-config.yaml"
    _write_catalog(catalog_path)

    loaded = load_model_library(
        "models-config.yaml",
        runtime_config_path=runtime_path,
        environment={},
        allow_env_override=False,
    )

    assert loaded.path == catalog_path.resolve()
    assert "chat" in loaded.library.profiles


def test_environment_path_override_requires_policy_opt_in(tmp_path: Path) -> None:
    runtime_path = tmp_path / "config.yaml"
    default_path = tmp_path / "default.yaml"
    override_path = tmp_path / "override.yaml"
    _write_catalog(default_path, marker="default")
    _write_catalog(override_path, marker="override")
    environment = {"FRIDAY_MODELS_CONFIG": str(override_path)}

    disabled = load_model_library(
        str(default_path),
        runtime_config_path=runtime_path,
        environment=environment,
        allow_env_override=False,
    )
    enabled = load_model_library(
        str(default_path),
        runtime_config_path=runtime_path,
        environment=environment,
        allow_env_override=True,
    )

    assert disabled.path == default_path.resolve()
    assert enabled.path == override_path.resolve()


@pytest.mark.parametrize(
    "document",
    (
        "schema: friday.model-library/v1\nschema: friday.model-library/v1\n",
        "schema: &schema friday.model-library/v1\ncopy: *schema\n",
        "schema: friday.model-library/v1\nvalue: !custom tagged\n",
        "schema: friday.model-library/v1\nbase: &base {provider: openai}\nmerged: {<<: *base}\n",
    ),
)
def test_strict_loader_rejects_ambiguous_yaml(
    tmp_path: Path,
    document: str,
) -> None:
    catalog_path = tmp_path / "models.yaml"
    catalog_path.write_text(document)

    with pytest.raises(ModelLibraryLoadError):
        load_model_library(
            str(catalog_path),
            runtime_config_path=tmp_path / "config.yaml",
            environment={},
            allow_env_override=False,
        )


def test_remote_catalog_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ModelLibraryLoadError, match="local file"):
        load_model_library(
            "https://example.test/models.yaml",
            runtime_config_path=tmp_path / "config.yaml",
            environment={},
            allow_env_override=False,
        )


def test_runtime_resolves_canonical_pools_and_di_uses_factories(
    tmp_path: Path,
) -> None:
    install_root = tmp_path / "install"
    runtime_parent = tmp_path / "runtime"
    workspace_root = tmp_path / "workspace"
    install_root.mkdir()
    runtime_parent.mkdir()
    workspace_root.mkdir()
    catalog_path = tmp_path / "models-config.yaml"
    catalog_path.write_text(
        """
schema: friday.model-library/v1
credentials:
  local_key:
    env: FRIDAY_TEST_LLM_KEY
endpoints:
  local:
    api_base: http://127.0.0.1:1234/v1
    provider: openai_compatible
    serving_engine: lm_studio
    default_credential: local_key
profiles:
  chat:
    kind: chat
    endpoint: local
    dialect: openai_chat_completions
    model: openai/qwen3.8
    model_target:
      model_id: qwen3.8
      family: qwen3_8
      revision: exact
  embedding:
    kind: embedding
    endpoint: local
    dialect: openai_embeddings
    model: openai/nomic-embed
    model_target:
      model_id: nomic-embed
      family: nomic_embed
      revision: exact
""".strip()
    )
    runtime_path = tmp_path / "config.yaml"
    runtime_path.write_text(
        f"""
model_library:
  path: ./models-config.yaml
runtime_paths:
  install_root: {install_root}
  runtime_data_root: {runtime_parent / "friday"}
  workspace_root: {workspace_root}
llm_pool:
  default_service: default
  services:
    default:
      profile: chat
embedding_pool:
  default_service: default
  services:
    default:
      profile: embedding
""".strip()
    )

    config = RuntimeConfig.from_sources(
        yaml_path=runtime_path,
        env={"FRIDAY_TEST_LLM_KEY": "redacted-local-key"},
    )
    container = DIContainer(config, MemoryProfile.FULL)
    container._create_llm_services()

    assert config.model_library_path == str(catalog_path.resolve())
    assert config.llm_api_key is None
    assert container.llm is not None
    assert container.llm.model == "openai/qwen3.8"
    assert container.llm.api_key == "redacted-local-key"
    assert container.llm.execution_target is not None
    assert container.embeddings is not None
    assert container.embeddings.execution_target is not None
