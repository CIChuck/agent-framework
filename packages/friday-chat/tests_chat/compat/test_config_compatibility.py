"""Compatibility scaffolding for Friday-py config loading."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import friday_chat.config as config_module
import pytest
import yaml
from friday_chat.config import (
    HIGH_VALUE_NESTED_CONFIG_SECTIONS,
    TOP_LEVEL_CONFIG_SECTIONS,
    FridayChatConfigError,
    get_config_traceability,
    load_friday_py_config,
)

FIXTURE = Path(__file__).parent / "fixtures" / "friday_py_config_sanitized.yaml"
EXAMPLE_CONFIG = Path("packages/friday-chat/config.example.yaml")
FRIDAY_PY_CONFIG = Path("tests/integration/memory/config.yaml")

TOP_LEVEL_SECTIONS = set(TOP_LEVEL_CONFIG_SECTIONS)
HIGH_VALUE_NESTED_SECTIONS = {
    tuple(section.split(".", maxsplit=1))
    for section in HIGH_VALUE_NESTED_CONFIG_SECTIONS
}


def _load_fixture() -> dict[str, Any]:
    data = yaml.safe_load(FIXTURE.read_text())
    if not isinstance(data, dict):
        raise TypeError("Sanitized config fixture must be a mapping.")
    return data


def _load_mapping(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise TypeError(f"{path} must be a mapping.")
    return data


def _config_paths(data: dict[str, Any], prefix: str = "") -> set[str]:
    paths: set[str] = set()
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        paths.add(path)
        if isinstance(value, dict):
            paths.update(_config_paths(value, path))
    return paths


def _set_placeholder_env(path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for env_name in sorted(set(re.findall(r"\$\{([A-Z0-9_]+)\}", path.read_text()))):
        monkeypatch.setenv(env_name, f"test-{env_name.lower()}")


@pytest.fixture
def config_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_placeholder_env(FIXTURE, monkeypatch)


def test_sanitized_config_fixture_has_required_top_level_sections() -> None:
    data = _load_fixture()

    assert TOP_LEVEL_SECTIONS - set(data) == set()


def test_sanitized_config_fixture_matches_friday_py_option_shape() -> None:
    source = _load_mapping(FRIDAY_PY_CONFIG)
    fixture = _load_fixture()

    assert _config_paths(fixture) == _config_paths(source)


def test_example_config_matches_friday_py_option_shape() -> None:
    source = _load_mapping(FRIDAY_PY_CONFIG)
    example = _load_mapping(EXAMPLE_CONFIG)

    assert _config_paths(example) == _config_paths(source)


def test_sanitized_config_fixture_has_high_value_nested_sections() -> None:
    data = _load_fixture()

    missing = {
        f"{parent}.{child}"
        for parent, child in HIGH_VALUE_NESTED_SECTIONS
        if child not in data.get(parent, {})
    }

    assert missing == set()


def test_sanitized_config_fixture_contains_no_literal_provider_secrets() -> None:
    text = FIXTURE.read_text()

    secret_patterns = [
        r"sk-[A-Za-z0-9_-]{12,}",
        r"sk_[A-Za-z0-9_-]{12,}",
        r"pk-lf-[A-Za-z0-9_-]{12,}",
        r"sk-lf-[A-Za-z0-9_-]{12,}",
    ]

    assert not any(re.search(pattern, text) for pattern in secret_patterns)


def test_example_config_contains_no_literal_provider_secrets() -> None:
    text = EXAMPLE_CONFIG.read_text()
    secret_patterns = [
        r"sk-[A-Za-z0-9_-]{12,}",
        r"sk_[A-Za-z0-9_-]{12,}",
        r"pk-lf-[A-Za-z0-9_-]{12,}",
        r"sk-lf-[A-Za-z0-9_-]{12,}",
    ]

    assert not any(re.search(pattern, text) for pattern in secret_patterns)


def test_friday_v2_loads_example_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_placeholder_env(EXAMPLE_CONFIG, monkeypatch)

    loaded = load_friday_py_config(EXAMPLE_CONFIG)

    assert loaded.llm.model == "moonshot/kimi-k3"
    assert loaded.memory.priming["previous_sessions"] == 2
    assert loaded.transcript.capture_raw_prompts is True


def test_friday_v2_loads_sanitized_friday_py_config(config_env: None) -> None:
    loaded = load_friday_py_config(FIXTURE)

    assert loaded.llm.model == "moonshot/kimi-k3"
    assert loaded.llm.api_key == "test-friday_llm_api_key"
    assert loaded.memory.priming["previous_sessions"] == 2
    assert loaded.transcript.capture_raw_prompts is True


def test_friday_v2_loads_minimal_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("llm:\n  model: openai/test-chat-model\n")

    loaded = load_friday_py_config(config_path)

    assert loaded.llm.model == "openai/test-chat-model"
    assert loaded.chat.assistant_name == "Friday"


def test_missing_required_llm_config_fails_before_runtime(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("chat:\n  assistant_name: Friday\n")

    with pytest.raises(FridayChatConfigError, match="llm"):
        load_friday_py_config(config_path)


def test_missing_environment_placeholder_fails(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "llm:\n"
        "  model: openai/test-chat-model\n"
        "  api_key: ${FRIDAY_TEST_MISSING_KEY}\n"
    )

    with pytest.raises(FridayChatConfigError, match="FRIDAY_TEST_MISSING_KEY"):
        load_friday_py_config(config_path)


def test_unknown_top_level_key_reports_diagnostic(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "llm:\n"
        "  model: openai/test-chat-model\n"
        "unexpected_section:\n"
        "  enabled: true\n"
    )

    loaded = load_friday_py_config(config_path)

    assert [diagnostic.path for diagnostic in loaded.diagnostics] == [
        "unexpected_section"
    ]
    assert loaded.diagnostics[0].kind == "unknown_key"


def test_deprecated_key_reports_diagnostic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        config_module,
        "DEPRECATED_CONFIG_KEYS",
        {"chat.legacy_prompt": "Use chat.system_prompt."},
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "llm:\n"
        "  model: openai/test-chat-model\n"
        "chat:\n"
        "  legacy_prompt: hello\n"
    )

    loaded = load_friday_py_config(config_path)

    assert loaded.diagnostics[0].kind == "deprecated_key"
    assert loaded.diagnostics[0].path == "chat.legacy_prompt"


def test_renamed_key_reports_diagnostic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        config_module,
        "RENAMED_CONFIG_KEYS",
        {"chat.name": "chat.assistant_name"},
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "llm:\n"
        "  model: openai/test-chat-model\n"
        "chat:\n"
        "  name: Friday\n"
    )

    loaded = load_friday_py_config(config_path)

    assert loaded.diagnostics[0].kind == "renamed_key"
    assert loaded.diagnostics[0].path == "chat.name"


def test_config_traceability_covers_required_keys() -> None:
    traceability = get_config_traceability()
    required = TOP_LEVEL_SECTIONS | set(HIGH_VALUE_NESTED_CONFIG_SECTIONS)

    missing = {key for key in required if key not in traceability}

    assert missing == set()


def test_traceability_check_would_fail_for_unmapped_supported_key() -> None:
    traceability = get_config_traceability()
    required = set(traceability) | {"future.unmapped"}

    missing = {key for key in required if key not in traceability}

    assert missing == {"future.unmapped"}
