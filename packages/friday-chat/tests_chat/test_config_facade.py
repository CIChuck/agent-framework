"""Public Chat configuration compatibility over the neutral Runtime owner."""

from __future__ import annotations

import pickle
import re
from pathlib import Path

import friday_chat.config as chat
import friday_runtime.application_config as neutral
import pytest
import yaml

EXPECTED_CHAT_EXPORTS = (
    "CONFIG_TRACEABILITY",
    "DEPRECATED_CONFIG_KEYS",
    "HIGH_VALUE_NESTED_CONFIG_SECTIONS",
    "RENAMED_CONFIG_KEYS",
    "TOP_LEVEL_CONFIG_SECTIONS",
    "TRACEABILITY_KEYS",
    "ChatConfig",
    "ConfigDiagnostic",
    "EmbeddingConfig",
    "ExtractionConfig",
    "FinanceConfig",
    "FridayChatConfig",
    "FridayChatConfigError",
    "GenerationConfigInput",
    "LangfuseConfig",
    "LegacyLLMExecutionConfig",
    "LifecycleConfig",
    "LLMConfig",
    "LMStudioQwenOptionsInput",
    "LoggingConfig",
    "MaintenanceConfig",
    "MemoryConfig",
    "ModelTargetInput",
    "PrimaryLLMExecutionConfig",
    "ReasoningConfigInput",
    "SamplingConfigInput",
    "SecurityConfig",
    "SessionConfig",
    "SmartFileConfig",
    "SpeechConfig",
    "ToolsConfig",
    "TranscriptConfig",
    "TransportTargetInput",
    "TypedLLMExecutionConfig",
    "WebConfig",
    "get_config_traceability",
    "load_friday_py_config",
)


def test_chat_public_exports_and_class_identity() -> None:
    assert tuple(chat.__all__) == EXPECTED_CHAT_EXPORTS
    for name in EXPECTED_CHAT_EXPORTS + (
        "ChatTelemetryConfig",
        "FlexibleConfigSection",
        "ProviderConfig",
        "ENV_PATTERN",
        "ChatServicePoolConfig",
        "EmbeddingServicePoolConfig",
        "ModelLibraryReference",
    ):
        assert hasattr(chat, name)
        if hasattr(neutral, name):
            assert getattr(chat, name) is getattr(neutral, name)
    assert chat.FridayChatConfig is neutral.ApplicationConfig
    assert chat.FridayChatConfigError is neutral.ApplicationConfigError
    assert chat.FridayChatConfig.__name__ == "FridayChatConfig"
    assert chat.FridayChatConfigError.__name__ == "FridayChatConfigError"
    assert chat.FridayChatConfig.__module__ == "friday_runtime.application_config"


def test_historical_chat_pickle_global_lookup() -> None:
    for name in (
        "FridayChatConfig",
        "FridayChatConfigError",
        "ChatTelemetryConfig",
        "LLMConfig",
    ):
        old_global = f"cfriday_chat.config\n{name}\n.".encode()
        assert pickle.loads(old_global) is getattr(chat, name)


def test_chat_traceability_map_stays_chat_owned_and_copying() -> None:
    traceability = chat.get_config_traceability()
    assert traceability["chat"] == "friday_chat.app.session_identity"
    traceability["chat"] = "modified"
    assert chat.get_config_traceability()["chat"] != "modified"
    assert not hasattr(neutral, "CONFIG_TRACEABILITY")


def test_chat_rule_replacement_and_in_place_edit_apply_on_each_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "runtime.yaml"
    path.write_text(
        "llm:\n  model: openai/test\n"
        "chat:\n  legacy_prompt: text\n  old_name: Friday\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(chat, "DEPRECATED_CONFIG_KEYS", {"chat.legacy_prompt": "first"})
    monkeypatch.setattr(chat, "RENAMED_CONFIG_KEYS", {"chat.old_name": "chat.name"})

    first = chat.load_friday_py_config(path, env={})
    chat.DEPRECATED_CONFIG_KEYS["chat.legacy_prompt"] = "second"
    second = chat.load_friday_py_config(path, env={})
    independent = neutral.load_application_config(path, env={})

    assert [(item.kind, item.path) for item in first.diagnostics[:2]] == [
        ("deprecated_key", "chat.legacy_prompt"),
        ("renamed_key", "chat.old_name"),
    ]
    assert first.diagnostics[0].message.endswith("first")
    assert second.diagnostics[0].message.endswith("second")
    assert [(item.kind, item.path) for item in independent.diagnostics] == [
        ("deprecated_key", "llm")
    ]


def test_legacy_and_example_files_match_neutral_loader(tmp_path: Path) -> None:
    legacy = tmp_path / "legacy.yaml"
    legacy.write_text(
        "llm:\n  model: openai/test\n  api_key: ${TEST_KEY}\n"
        "memory:\n  persist_directory: ./memory\n"
        "unrecognized:\n  value: retained-for-interpolation\n",
        encoding="utf-8",
    )
    _compare_loaders(legacy, {"TEST_KEY": "synthetic-key"})

    example = Path("packages/friday-chat/config.example.yaml")
    catalog = Path("packages/friday-chat/models-config.example.yaml")
    env = {
        name: f"synthetic-{name.lower()}"
        for name in re.findall(r"\$\{([A-Z0-9_]+)\}", example.read_text())
    }
    catalog_data = yaml.safe_load(catalog.read_text())
    for credential in catalog_data.get("credentials", {}).values():
        if isinstance(credential, dict) and isinstance(credential.get("env"), str):
            env[credential["env"]] = "synthetic-provider-key"
    _compare_loaders(example, env)


def _compare_loaders(path: Path, env: dict[str, str]) -> None:
    old_path = chat.load_friday_py_config(path, env=env)
    neutral_path = neutral.load_application_config(path, env=env)
    assert type(old_path) is type(neutral_path)
    assert old_path.model_dump() == neutral_path.model_dump()
    assert old_path.llm_service_specs == neutral_path.llm_service_specs
    assert old_path.embedding_service_specs == neutral_path.embedding_service_specs


@pytest.mark.parametrize(
    "body",
    [
        None,
        "llm: [\n",
        "- item\n",
        "",
        "llm:\n  model: openai/test\nunknown:\n  value: ${MISSING}\n",
        "model_library:\n  path: ./missing.yaml\n",
    ],
)
def test_chat_and_neutral_errors_have_same_type_message_and_chaining(
    tmp_path: Path, body: str | None
) -> None:
    path = tmp_path / "runtime.yaml"
    if body is not None:
        path.write_text(body, encoding="utf-8")

    with pytest.raises(neutral.ApplicationConfigError) as neutral_caught:
        neutral.load_application_config(path, env={})
    with pytest.raises(chat.FridayChatConfigError) as chat_caught:
        chat.load_friday_py_config(path, env={})

    for attribute in ("__cause__", "__context__"):
        chat_inner = getattr(chat_caught.value, attribute)
        neutral_inner = getattr(neutral_caught.value, attribute)
        assert type(chat_inner) is type(neutral_inner)
    assert type(chat_caught.value) is type(neutral_caught.value)
    assert str(chat_caught.value) == str(neutral_caught.value)
