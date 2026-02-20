"""
Tests for friday-cli session management.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from friday_cli import (
    SessionConfig,
    SessionContext,
    SessionManager,
    load_config,
    managed_session,
    validate_config,
)


class TestSessionConfig:
    """Test SessionConfig class."""

    def test_from_dict(self):
        data = {
            "llm": {"model": "gpt-4", "api_key": "test"},
            "chat": {"user_name": "Alice", "assistant_name": "Bot"},
            "memory": {"persist_directory": "./data"},
        }

        config = SessionConfig.from_dict(data)

        assert config.llm["model"] == "gpt-4"
        assert config.chat["user_name"] == "Alice"
        assert config.memory["persist_directory"] == "./data"

    def test_from_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
llm:
  model: gpt-4
  temperature: 0.7
chat:
  user_name: TestUser
  system_prompt: "You are helpful."
""")
            f.flush()

            config = SessionConfig.from_yaml(f.name)

            assert config.llm["model"] == "gpt-4"
            assert config.llm["temperature"] == 0.7
            assert config.chat["user_name"] == "TestUser"
            assert config.config_path == Path(f.name)

    def test_from_yaml_not_found(self):
        with pytest.raises(FileNotFoundError):
            SessionConfig.from_yaml("/nonexistent/config.yaml")

    def test_get_method(self):
        config = SessionConfig.from_dict({"llm": {"model": "gpt-4"}, "custom": "value"})

        assert config.get("custom") == "value"
        assert config.get("missing") is None
        assert config.get("missing", "default") == "default"

    def test_get_nested(self):
        data = {
            "memory": {
                "priming": {
                    "enabled": True,
                    "top_entities": 10,
                }
            }
        }
        config = SessionConfig.from_dict(data)

        assert config.get_nested("memory", "priming", "enabled") is True
        assert config.get_nested("memory", "priming", "top_entities") == 10
        assert config.get_nested("memory", "priming", "missing", default=5) == 5
        assert config.get_nested("missing", "path", default="none") == "none"

    def test_user_name_property(self):
        config = SessionConfig.from_dict({"chat": {"user_name": "Alice"}})
        assert config.user_name == "Alice"

        # Default
        config2 = SessionConfig.from_dict({})
        assert config2.user_name == "User"

    def test_assistant_name_property(self):
        config = SessionConfig.from_dict({"chat": {"assistant_name": "Friday"}})
        assert config.assistant_name == "Friday"

        # Default
        config2 = SessionConfig.from_dict({})
        assert config2.assistant_name == "Assistant"

    def test_system_prompt_property(self):
        config = SessionConfig.from_dict({"chat": {"system_prompt": "Be concise."}})
        assert config.system_prompt == "Be concise."

        # Default
        config2 = SessionConfig.from_dict({})
        assert "helpful" in config2.system_prompt.lower()

    def test_persist_dir_property(self):
        # With config path - should resolve relative to config
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("memory:\n  persist_directory: ./data")

            config = SessionConfig.from_yaml(config_path)
            assert config.persist_dir == Path(tmpdir) / "data"

        # Without config path
        config2 = SessionConfig.from_dict(
            {"memory": {"persist_directory": "/absolute/path"}}
        )
        assert config2.persist_dir == Path("/absolute/path")

        # No persist_directory
        config3 = SessionConfig.from_dict({})
        assert config3.persist_dir is None


class TestSessionContext:
    """Test SessionContext class."""

    def test_context_creation(self):
        session = MagicMock()
        config = SessionConfig.from_dict({"llm": {"model": "gpt-4"}})

        ctx = SessionContext(session=session, config=config)

        assert ctx.session is session
        assert ctx.config is config
        assert ctx.resources == {}

    def test_resource_management(self):
        ctx = SessionContext(
            session=MagicMock(),
            config=SessionConfig.from_dict({}),
        )

        ctx.set_resource("db", "database_connection")
        ctx.set_resource("cache", "cache_instance")

        assert ctx.get_resource("db") == "database_connection"
        assert ctx.get_resource("cache") == "cache_instance"
        assert ctx.get_resource("missing") is None


class TestSessionManager:
    """Test SessionManager class."""

    def test_requires_config_source(self):
        with pytest.raises(ValueError, match="Either config or config_path"):
            SessionManager()

    def test_cannot_provide_both_config_sources(self):
        config = SessionConfig.from_dict({})
        with pytest.raises(ValueError, match="Cannot provide both"):
            SessionManager(config=config, config_path="some/path.yaml")

    def test_config_property_before_enter(self):
        config = SessionConfig.from_dict({"llm": {"model": "test"}})
        manager = SessionManager(config=config)

        # Config should be accessible before entering context
        assert manager.config.llm["model"] == "test"

    def test_context_property_before_enter(self):
        config = SessionConfig.from_dict({})
        manager = SessionManager(config=config)

        with pytest.raises(RuntimeError, match="Session not started"):
            _ = manager.context

    @pytest.mark.asyncio
    async def test_context_manager_basic(self):
        config = SessionConfig.from_dict({"llm": {"model": "test"}})
        manager = SessionManager(config=config)

        async with manager as ctx:
            assert ctx.config is config
            assert ctx.session is None  # No factory provided

    @pytest.mark.asyncio
    async def test_context_manager_with_factory(self):
        config = SessionConfig.from_dict({"llm": {"model": "test"}})
        session_obj = MagicMock()

        async def factory(cfg):
            return session_obj

        manager = SessionManager(config=config, session_factory=factory)

        async with manager as ctx:
            assert ctx.session is session_obj
            assert ctx.config is config

    @pytest.mark.asyncio
    async def test_context_manager_with_sync_factory(self):
        config = SessionConfig.from_dict({})
        session_obj = MagicMock()

        def factory(cfg):
            return session_obj

        manager = SessionManager(config=config, session_factory=factory)

        async with manager as ctx:
            assert ctx.session is session_obj

    @pytest.mark.asyncio
    async def test_on_shutdown_called(self):
        config = SessionConfig.from_dict({})
        shutdown_called = []

        async def on_shutdown(ctx):
            shutdown_called.append(ctx)

        manager = SessionManager(config=config, on_shutdown=on_shutdown)

        async with manager as ctx:
            pass

        assert len(shutdown_called) == 1
        assert shutdown_called[0] is ctx

    @pytest.mark.asyncio
    async def test_on_shutdown_sync(self):
        config = SessionConfig.from_dict({})
        shutdown_called = []

        def on_shutdown(ctx):
            shutdown_called.append(ctx)

        manager = SessionManager(config=config, on_shutdown=on_shutdown)

        async with manager:
            pass

        assert len(shutdown_called) == 1

    @pytest.mark.asyncio
    async def test_loads_config_from_path(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("llm:\n  model: from-file\n")
            f.flush()

            manager = SessionManager(config_path=f.name)

            async with manager as ctx:
                assert ctx.config.llm["model"] == "from-file"

    def test_shutdown_requested_default(self):
        config = SessionConfig.from_dict({})
        manager = SessionManager(config=config)

        assert manager.shutdown_requested is False


class TestManagedSession:
    """Test managed_session context manager."""

    @pytest.mark.asyncio
    async def test_managed_session_basic(self):
        config = SessionConfig.from_dict({"llm": {"model": "test"}})

        async with managed_session(config=config) as ctx:
            assert ctx.config.llm["model"] == "test"

    @pytest.mark.asyncio
    async def test_managed_session_with_factory(self):
        config = SessionConfig.from_dict({})
        session_obj = MagicMock()

        async with managed_session(
            config=config,
            session_factory=lambda cfg: session_obj,
        ) as ctx:
            assert ctx.session is session_obj


class TestLoadConfig:
    """Test load_config function."""

    def test_load_config(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("llm:\n  model: loaded\n")
            f.flush()

            config = load_config(f.name)

            assert config.llm["model"] == "loaded"


class TestValidateConfig:
    """Test validate_config function."""

    def test_validate_valid_config(self):
        config = SessionConfig.from_dict({"llm": {"model": "gpt-4"}})

        errors = validate_config(config)

        assert errors == []

    def test_validate_missing_llm(self):
        config = SessionConfig.from_dict({})

        errors = validate_config(config)

        assert len(errors) == 1
        assert "llm" in errors[0]

    def test_validate_missing_model(self):
        config = SessionConfig.from_dict(
            {"llm": {"api_key": "test"}}
        )  # llm present but no model

        errors = validate_config(config)

        assert len(errors) == 1
        assert "model" in errors[0]

    def test_validate_custom_required_sections(self):
        config = SessionConfig.from_dict({"llm": {"model": "test"}})

        errors = validate_config(config, required_sections=["llm", "memory"])

        assert len(errors) == 1
        assert "memory" in errors[0]
