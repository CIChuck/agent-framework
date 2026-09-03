"""Typed primary-LLM configuration and compatibility regression tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from friday_chat.config import (
    FridayChatConfig,
    FridayChatConfigError,
    LegacyLLMExecutionConfig,
    TypedLLMExecutionConfig,
    load_friday_py_config,
)
from friday_llm import ReasoningMode
from pydantic import ValidationError


def _typed_llm(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "model": "openai/qwen3.8-27b-mlx",
        "transport_target": {
            "provider": "openai_compatible",
            "dialect": "openai_chat_completions",
            "serving_engine": "lm_studio",
        },
        "model_target": {
            "model_id": "qwen3.8-27b-mlx",
            "family": "qwen3_8",
            "revision": "lmstudio-community/Qwen3.8-27B-MLX-8bit",
        },
    }
    values.update(overrides)
    return values


def _config(llm: dict[str, object]) -> FridayChatConfig:
    return FridayChatConfig.model_validate({"llm": llm})


def test_legacy_defaults_select_legacy_execution_without_explicit_thinking() -> None:
    execution = _config({"model": "openai/test"}).llm.resolve_execution()

    assert execution == LegacyLLMExecutionConfig(
        temperature=0.7,
        max_tokens=None,
        thinking_enabled=None,
    )


@pytest.mark.parametrize("thinking", [True, False])
def test_explicit_legacy_thinking_is_preserved(thinking: bool) -> None:
    execution = _config(
        {"model": "openai/test", "thinking": thinking}
    ).llm.resolve_execution()

    assert isinstance(execution, LegacyLLMExecutionConfig)
    assert execution.thinking_enabled is thinking


def test_typed_defaults_preserve_legacy_temperature_and_disabled_reasoning() -> None:
    execution = _config(_typed_llm()).llm.resolve_execution()

    assert isinstance(execution, TypedLLMExecutionConfig)
    assert execution.generation.sampling is not None
    assert execution.generation.sampling.temperature == 0.7
    assert execution.generation.reasoning is not None
    assert execution.generation.reasoning.mode is ReasoningMode.DISABLED


def test_explicit_nested_reasoning_auto_is_not_replaced_by_legacy_default() -> None:
    execution = _config(
        _typed_llm(generation={"reasoning": {"mode": "auto"}})
    ).llm.resolve_execution()

    assert isinstance(execution, TypedLLMExecutionConfig)
    assert execution.generation.reasoning is not None
    assert execution.generation.reasoning.mode is ReasoningMode.AUTO


def test_targeted_flat_controls_resolve_to_typed_generation() -> None:
    execution = _config(
        _typed_llm(
            temperature=0.2,
            top_p=0.91,
            top_k=32,
            max_tokens=4096,
            thinking=True,
        )
    ).llm.resolve_execution()

    assert isinstance(execution, TypedLLMExecutionConfig)
    assert execution.generation.sampling is not None
    assert execution.generation.sampling.temperature == 0.2
    assert execution.generation.sampling.top_p == 0.91
    assert execution.generation.sampling.top_k == 32
    assert execution.generation.max_tokens == 4096
    assert execution.generation.reasoning is not None
    assert execution.generation.reasoning.mode is ReasoningMode.ENABLED


def test_equal_legacy_and_nested_controls_are_accepted() -> None:
    execution = _config(
        _typed_llm(
            top_p=0.9,
            thinking=True,
            generation={
                "sampling": {"top_p": 0.9},
                "reasoning": {"mode": "enabled"},
            },
        )
    ).llm.resolve_execution()

    assert isinstance(execution, TypedLLMExecutionConfig)
    assert execution.generation.sampling is not None
    assert execution.generation.sampling.top_p == 0.9


@pytest.mark.parametrize(
    ("legacy", "generation", "match"),
    [
        ({"temperature": 0.2}, {"sampling": {"temperature": 0.3}}, "temperature"),
        ({"top_p": 0.8}, {"sampling": {"top_p": 0.9}}, "top_p"),
        ({"top_k": 20}, {"sampling": {"top_k": 40}}, "top_k"),
        ({"max_tokens": 100}, {"max_tokens": 200}, "max_tokens"),
        ({"thinking": False}, {"reasoning": {"mode": "enabled"}}, "thinking"),
    ],
)
def test_conflicting_legacy_and_nested_controls_fail(
    legacy: dict[str, object],
    generation: dict[str, object],
    match: str,
) -> None:
    with pytest.raises(ValidationError, match=match):
        _config(_typed_llm(**legacy, generation=generation))


@pytest.mark.parametrize(
    "llm",
    [
        {
            "model": "openai/test",
            "generation": {"sampling": {"temperature": 0.2}},
        },
        {"model": "openai/test", "provider_options": {"namespace": "lm_studio.qwen3_8"}},
        {
            "model": "openai/test",
            "transport_target": {
                "provider": "openai_compatible",
                "dialect": "openai_chat_completions",
            },
        },
    ],
)
def test_typed_inputs_require_both_explicit_targets(llm: dict[str, object]) -> None:
    with pytest.raises(ValidationError, match="target"):
        _config(llm)


def test_model_family_and_revision_are_required() -> None:
    with pytest.raises(ValidationError, match="family.*revision"):
        _config(
            _typed_llm(
                model_target={
                    "model_id": "qwen3.8-27b-mlx",
                    "family": "qwen3_8",
                }
            )
        )


def test_route_and_target_model_identity_must_match() -> None:
    with pytest.raises(ValidationError, match="routing identity"):
        _config(_typed_llm(model="openai/a-different-model"))


def test_unknown_nested_llm_key_fails() -> None:
    with pytest.raises(ValidationError, match="extra_forbidden"):
        _config({"model": "openai/test", "mystery_option": True})


def test_bounded_provider_options_parse_on_typed_path() -> None:
    execution = _config(
        _typed_llm(
            provider_options={
                "namespace": "lm_studio.qwen3_8",
                "enable_thinking": True,
                "reasoning_effort": "medium",
            }
        )
    ).llm.resolve_execution()

    assert isinstance(execution, TypedLLMExecutionConfig)
    assert execution.provider_options is not None
    assert execution.provider_options.namespace == "lm_studio.qwen3_8"


def test_loader_reports_legacy_path_and_field_diagnostics(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text(
        "llm:\n"
        "  model: openai/test\n"
        "  top_p: 0.9\n"
        "  top_k: 40\n",
        encoding="utf-8",
    )

    config = load_friday_py_config(path)

    paths = {diagnostic.path for diagnostic in config.diagnostics}
    assert paths == {"llm", "llm.top_p", "llm.top_k"}


def test_loader_reports_all_inline_auxiliary_provider_paths(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text(
        """
llm:
  model: openai/primary
extraction:
  model: openai/extractor
embedding:
  model: openai/embed
memory:
  passage_router:
    model: openai/router
maintenance:
  llm:
    synthesizer:
      model: openai/synthesizer
  embedding:
    model: openai/maintenance-embed
smart_file:
  llm:
    summarizer:
      model: openai/summarizer
""".strip(),
        encoding="utf-8",
    )

    config = load_friday_py_config(path)

    paths = {diagnostic.path for diagnostic in config.diagnostics}
    assert {
        "extraction",
        "embedding",
        "memory.passage_router",
        "maintenance.llm.synthesizer",
        "maintenance.embedding",
        "smart_file.llm.summarizer",
    }.issubset(paths)


def test_canonical_loader_has_no_legacy_diagnostics(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text(
        "llm:\n"
        "  model: openai/qwen3.8-27b-mlx\n"
        "  generation:\n"
        "    sampling:\n"
        "      top_p: 0.9\n"
        "  transport_target:\n"
        "    provider: openai_compatible\n"
        "    dialect: openai_chat_completions\n"
        "    serving_engine: lm_studio\n"
        "  model_target:\n"
        "    model_id: qwen3.8-27b-mlx\n"
        "    family: qwen3_8\n"
        "    revision: test-revision\n",
        encoding="utf-8",
    )

    config = load_friday_py_config(path)

    assert config.diagnostics == []


def test_loader_validation_error_does_not_echo_unknown_secret(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    secret = "canary-private-provider-value"
    path.write_text(
        "llm:\n"
        "  model: openai/test\n"
        f"  unexpected_secret: {secret}\n",
        encoding="utf-8",
    )

    with pytest.raises(FridayChatConfigError) as captured:
        load_friday_py_config(path)

    assert secret not in str(captured.value)
    assert "llm.unexpected_secret" in str(captured.value)


def test_loader_resolves_canonical_model_library_without_warnings(
    tmp_path: Path,
) -> None:
    (tmp_path / "models-config.yaml").write_text(
        """
schema: friday.model-library/v1
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
    model: openai/qwen3.8
    model_target:
      model_id: qwen3.8
      family: qwen3_8
      revision: exact
    generation:
      reasoning:
        mode: disabled
      sampling:
        temperature: 0.2
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
    path = tmp_path / "config.yaml"
    path.write_text(
        """
model_library:
  path: ./models-config.yaml
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
""".strip()
    )

    config = load_friday_py_config(
        path,
        env={"FRIDAY_TEST_LLM_KEY": "redacted-test-key"},
    )

    assert config.diagnostics == []
    assert config.llm_service_specs["chat"].model == "openai/qwen3.8"
    assert config.embedding_service_specs["memory"].model == "openai/nomic-embed"
    assert "redacted-test-key" not in repr(config)


def test_loader_names_missing_selected_credential_without_echoing_secrets(
    tmp_path: Path,
) -> None:
    (tmp_path / "models-config.yaml").write_text(
        """
schema: friday.model-library/v1
credentials:
  selected:
    env: FRIDAY_SELECTED_PROVIDER_KEY
endpoints:
  local:
    api_base: http://127.0.0.1:1234/v1
    provider: openai_compatible
    serving_engine: lm_studio
    default_credential: selected
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
      family: test_embed
      revision: exact
""".strip()
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
model_library:
  path: ./models-config.yaml
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
""".strip()
    )

    with pytest.raises(FridayChatConfigError) as captured:
        load_friday_py_config(config_path, env={})

    message = str(captured.value)
    assert "FRIDAY_SELECTED_PROVIDER_KEY" in message
    assert "credential environment variable" in message
