"""Contract tests for the frontend-independent application YAML loader."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from friday_runtime.application_config import (
    ApplicationConfig,
    ApplicationConfigError,
    ConfigDiagnosticRules,
    load_application_config,
)


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_legacy_fields_and_diagnostic_order_match_before_code(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "runtime.yaml",
        "llm:\n  model: openai/test\n  temperature: 0.2\n"
        "chat:\n  name: Friday\n"
        "memory:\n  persist_directory: ./memory\n"
        "transcript:\n  export_directory: ./exports\n"
        "zzz:\n  enabled: true\n",
    )
    rules = ConfigDiagnosticRules(
        deprecated_keys={"llm.temperature": "Use llm.generation.sampling.temperature."},
        renamed_keys={"chat.name": "chat.assistant_name"},
    )

    config = load_application_config(path, env={}, diagnostic_rules=rules)

    assert isinstance(config, ApplicationConfig)
    assert config.llm.model == "openai/test"
    assert config.memory.persist_directory == "./memory"
    assert config.transcript.export_directory == "./exports"
    assert [(item.kind, item.path) for item in config.diagnostics] == [
        ("renamed_key", "chat.name"),
        ("deprecated_key", "llm.temperature"),
        ("unknown_key", "zzz"),
        ("deprecated_key", "llm"),
    ]
    assert "zzz" not in config.model_dump()
    assert path.read_text(encoding="utf-8").endswith("zzz:\n  enabled: true\n")


def test_diagnostic_rules_snapshot_and_default(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "runtime.yaml",
        "llm:\n  model: openai/test\n  temperature: 0.2\n",
    )
    deprecated = {"llm.temperature": "original"}
    renamed: dict[str, str] = {}
    rules = ConfigDiagnosticRules(deprecated, renamed)
    deprecated["llm.temperature"] = "changed"
    renamed["llm.temperature"] = "new.place"
    with pytest.raises(TypeError):
        rules.deprecated_keys["new"] = "value"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        rules.renamed_keys = {}  # type: ignore[misc]

    selected = load_application_config(path, env={}, diagnostic_rules=rules)
    default = load_application_config(path, env={})

    assert selected.diagnostics[0].message == (
        "Config key llm.temperature is deprecated: original"
    )
    assert default.diagnostics[0].message == (
        "Config key llm.temperature is deprecated: "
        "Use llm.generation.sampling.temperature."
    )


@pytest.mark.parametrize(
    ("name", "body", "message", "cause"),
    [
        ("missing", None, "Config file not found:", None),
        ("malformed", "llm: [\n", "Invalid YAML in config file:", "ParserError"),
        ("non_mapping", "- item\n", "Config root must be a mapping.", None),
        ("empty", "", "Missing required config: llm.model", None),
        (
            "missing_env",
            "llm:\n  model: openai/test\nunknown:\n  value: ${MISSING}\n",
            "Environment variable MISSING is required by config.",
            None,
        ),
    ],
)
def test_existing_failure_shapes(
    tmp_path: Path, name: str, body: str | None, message: str, cause: str | None
) -> None:
    path = tmp_path / f"{name}.yaml"
    if body is not None:
        _write(path, body)

    with pytest.raises(ApplicationConfigError) as caught:
        load_application_config(path, env={})

    assert message in str(caught.value)
    assert (
        type(caught.value.__cause__).__name__ if caught.value.__cause__ else None
    ) == cause


def test_native_read_failure_propagates(tmp_path: Path) -> None:
    directory = tmp_path / "runtime.yaml"
    directory.mkdir()

    with pytest.raises(IsADirectoryError):
        load_application_config(directory, env={})


def test_canonical_catalog_follows_symlink_target_and_ignores_override(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    link = tmp_path / "link"
    target.mkdir()
    link.mkdir()
    _write(
        target / "models.yaml",
        """schema: friday.model-library/v1
credentials:
  local:
    env: FRIDAY_TEST_LLM_KEY
endpoints:
  local:
    api_base: http://127.0.0.1:1234/v1
    provider: openai_compatible
    serving_engine: lm_studio
    default_credential: local
profiles:
  chat:
    kind: chat
    endpoint: local
    dialect: openai_chat_completions
    model: openai/test
    model_target:
      model_id: test
      family: test
      revision: exact
  embedding:
    kind: embedding
    endpoint: local
    dialect: openai_embeddings
    model: openai/embed
    model_target:
      model_id: embed
      family: embed
      revision: exact
""",
    )
    wrong_catalog = _write(link / "models.yaml", "not: a model library\n")
    runtime_file = _write(
        target / "runtime.yaml",
        """model_library:
  path: ./models.yaml
llm_pool:
  default_service: chat
  services:
    chat:
      profile: chat
embedding_pool:
  default_service: memory
  services:
    memory:
      profile: embedding
""",
    )
    selected = link / "runtime.yaml"
    selected.symlink_to(runtime_file)

    loaded = load_application_config(
        selected,
        env={
            "FRIDAY_TEST_LLM_KEY": "synthetic-key",
            "FRIDAY_MODELS_CONFIG": str(wrong_catalog),
        },
    )

    assert loaded.llm_service_specs["chat"].model == "openai/test"
    assert loaded.embedding_service_specs["memory"].model == "openai/embed"
    assert loaded.diagnostics == []
    assert "synthetic-key" not in repr(loaded)
    assert wrong_catalog.read_text(encoding="utf-8") == "not: a model library\n"


def test_neutral_import_has_no_frontend_modules(tmp_path: Path) -> None:
    check = (
        "import sys; import friday_runtime.application_config; "
        "assert not any(name == 'friday_chat' or name.startswith('friday_chat.') "
        "or name == 'friday_cli' or name.startswith('friday_cli.') "
        "for name in sys.modules)"
    )
    result = subprocess.run(
        [sys.executable, "-c", check],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
