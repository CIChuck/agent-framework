"""
Tests for FridayBaseSettings configuration management.

Tests cover:
- Default values
- Environment variable loading
- .env file loading
- Configuration isolation (no implicit state)

Ref: Batch 0 Acceptance Criteria #3, #5
"""

import os

import pytest

from friday_core import FridayBaseSettings


class TestFridayBaseSettings:
    """Tests for FridayBaseSettings configuration."""

    def test_default_values(self, clean_env):
        """Test that default values are correctly set."""
        settings = FridayBaseSettings()

        assert settings.APP_ENV == "development"
        assert settings.LOG_LEVEL == "INFO"
        assert settings.DEFAULT_MODEL == "gpt-4-turbo"
        assert settings.OPENAI_API_KEY is None

    def test_env_variable_override(self, clean_env):
        """Test that environment variables override defaults."""
        os.environ["APP_ENV"] = "production"
        os.environ["LOG_LEVEL"] = "ERROR"
        os.environ["DEFAULT_MODEL"] = "gpt-3.5-turbo"
        os.environ["OPENAI_API_KEY"] = "sk-test-key"

        settings = FridayBaseSettings()

        assert settings.APP_ENV == "production"
        assert settings.LOG_LEVEL == "ERROR"
        assert settings.DEFAULT_MODEL == "gpt-3.5-turbo"
        assert settings.OPENAI_API_KEY == "sk-test-key"

    def test_env_file_loading(self, temp_env_file, clean_env):
        """Test loading configuration from .env file."""
        # Create settings with explicit env_file path
        settings = FridayBaseSettings(_env_file=temp_env_file)

        assert settings.APP_ENV == "testing"
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.DEFAULT_MODEL == "gpt-4"
        assert settings.OPENAI_API_KEY == "test-key-12345"

    def test_extra_fields_ignored(self, clean_env):
        """Test that extra/unknown environment variables are ignored."""
        os.environ["UNKNOWN_SETTING"] = "should_be_ignored"
        os.environ["APP_ENV"] = "testing"

        # Should not raise an error
        settings = FridayBaseSettings()

        assert settings.APP_ENV == "testing"
        # Verify no UNKNOWN_SETTING attribute exists
        assert not hasattr(settings, "UNKNOWN_SETTING")

    def test_configuration_isolation(self, clean_env):
        """Test that settings can be created with mock values for testing."""
        # This verifies Batch 0 requirement: components can be tested
        # without relying on real .env files

        # Create settings with explicit values (simulating DI)
        settings = FridayBaseSettings(
            APP_ENV="testing",
            LOG_LEVEL="DEBUG",
            DEFAULT_MODEL="test-model",
            OPENAI_API_KEY="mock-key",
        )

        assert settings.APP_ENV == "testing"
        assert settings.DEFAULT_MODEL == "test-model"
        assert settings.OPENAI_API_KEY == "mock-key"

    def test_case_insensitive_env_vars(self, clean_env):
        """Test that environment variables work regardless of case."""
        os.environ["app_env"] = "staging"

        settings = FridayBaseSettings()

        # Pydantic settings should handle case-insensitive matching
        assert settings.APP_ENV == "staging"


class TestConfigurationInjection:
    """Tests demonstrating proper dependency injection pattern."""

    def test_component_accepts_config_values(self, clean_env):
        """Test that components can accept config values via constructor."""

        # Example component that uses DI pattern (as specified in Batch 0)
        class MockComponent:
            def __init__(self, model_name: str, api_key: str | None = None):
                self.model_name = model_name
                self.api_key = api_key

        # Application layer creates config and injects values
        settings = FridayBaseSettings(
            DEFAULT_MODEL="injected-model",
            OPENAI_API_KEY="injected-key",
        )

        component = MockComponent(
            model_name=settings.DEFAULT_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )

        assert component.model_name == "injected-model"
        assert component.api_key == "injected-key"

    def test_component_testable_without_env(self, clean_env):
        """Test that components can be tested with mock values, no .env needed."""

        class MockComponent:
            def __init__(self, model_name: str):
                self.model_name = model_name

        # Direct injection without any config object
        component = MockComponent(model_name="test-model")

        assert component.model_name == "test-model"
