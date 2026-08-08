"""Compatibility scaffolding for FridayV2 safety defaults."""

from __future__ import annotations

import re
from importlib.resources import files
from pathlib import Path

import pytest
import yaml
from friday_chat.config import FridayChatConfig

CONFIG_TEMPLATE_PACKAGE = "friday_chat.config_templates"


def test_shell_service_is_not_implemented_as_enabled_by_default() -> None:
    from friday_chat import shell

    service_type = getattr(shell, "ShellService", None)
    if service_type is None:
        pytest.xfail("FridayV2 shell service is not implemented yet.")

    service = service_type()

    assert service.enabled is False


def test_example_config_contains_no_literal_provider_secrets() -> None:
    example_config = Path("packages/friday-chat/config.example.yaml")
    text = example_config.read_text()
    secret_patterns = [
        r"sk-[A-Za-z0-9_-]{12,}",
        r"sk_[A-Za-z0-9_-]{12,}",
        r"pk-lf-[A-Za-z0-9_-]{12,}",
        r"sk-lf-[A-Za-z0-9_-]{12,}",
    ]

    assert example_config.exists()
    assert not any(re.search(pattern, text) for pattern in secret_patterns)


def test_exit_reorganization_defaults_disabled_in_typed_config() -> None:
    config = FridayChatConfig.model_validate(
        {"llm": {"model": "openai/synthetic-chat-model"}}
    )

    assert config.session.reorganize_on_exit is False


def test_exit_reorganization_defaults_disabled_in_both_examples() -> None:
    source_example = yaml.safe_load(
        Path("packages/friday-chat/config.example.yaml").read_text()
    )
    packaged_example = yaml.safe_load(
        files(CONFIG_TEMPLATE_PACKAGE).joinpath("config.example.yaml").read_text()
    )

    assert source_example["session"]["reorganize_on_exit"] is False
    assert packaged_example["session"]["reorganize_on_exit"] is False
