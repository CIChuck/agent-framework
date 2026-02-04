"""
Unit tests for AgentLoader.

Tests YAML configuration loading, validation, and caching.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from friday_agent import AgentLoader, AgentConfigError, AgentProfile


class TestAgentLoader:
    """Tests for AgentLoader."""

    @pytest.fixture
    def temp_agents_dir(self):
        """Create a temporary agents directory with test configs."""
        temp_dir = tempfile.mkdtemp()
        agents_dir = Path(temp_dir) / "agents"
        agents_dir.mkdir()

        # Create valid test agent
        valid_config = """
name: test_agent
role: "Test Agent"
goal: "Test the loader functionality"
system_prompt: |
  You are a test agent.
  Your purpose is to test the configuration loading system.
tools:
  - test_tool
capabilities:
  - testing
  - validation
temperature: 0.5
tool_autonomy: auto
"""
        (agents_dir / "test_agent.yaml").write_text(valid_config)

        # Create another valid agent (yml extension)
        another_config = """
name: another_agent
role: "Another Test Agent"
goal: "Test .yml extension support"
system_prompt: |
  You are another test agent.
tools: []
capabilities:
  - testing
"""
        (agents_dir / "another_agent.yml").write_text(another_config)

        yield agents_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def loader(self, temp_agents_dir):
        """Create a loader with the temp directory."""
        return AgentLoader(temp_agents_dir)

    def test_load_valid_config(self, loader):
        """Test loading a valid agent configuration."""
        profile = loader.load("test_agent")

        assert profile.name == "test_agent"
        assert profile.role == "Test Agent"
        assert profile.goal == "Test the loader functionality"
        assert "test_tool" in profile.tools
        assert "testing" in profile.capabilities
        assert profile.temperature == 0.5
        assert profile.tool_autonomy == "auto"

    def test_load_yml_extension(self, loader):
        """Test loading agent with .yml extension."""
        profile = loader.load("another_agent")

        assert profile.name == "another_agent"
        assert profile.role == "Another Test Agent"

    def test_load_nonexistent_raises(self, loader):
        """Test that loading nonexistent agent raises error."""
        with pytest.raises(AgentConfigError, match="not found"):
            loader.load("nonexistent_agent")

    def test_load_all(self, loader):
        """Test loading all agents from directory."""
        profiles = loader.load_all()

        assert len(profiles) == 2
        assert "test_agent" in profiles
        assert "another_agent" in profiles

    def test_list_available(self, loader):
        """Test listing available agent names."""
        names = loader.list_available()

        assert len(names) == 2
        assert "test_agent" in names
        assert "another_agent" in names

    def test_caching(self, loader):
        """Test that profiles are cached."""
        profile1 = loader.load("test_agent")
        profile2 = loader.load("test_agent")

        # Should return same instance from cache
        assert profile1 is profile2

    def test_reload_bypasses_cache(self, loader):
        """Test that reload bypasses cache."""
        profile1 = loader.load("test_agent")
        profile2 = loader.reload("test_agent")

        # Should return different instance
        assert profile1 is not profile2
        # But with same data
        assert profile1.name == profile2.name

    def test_clear_cache(self, loader):
        """Test clearing the cache."""
        loader.load("test_agent")
        loader.clear_cache()
        # Should not have any cached profiles
        assert len(loader._cache) == 0


class TestAgentLoaderValidation:
    """Tests for configuration validation."""

    @pytest.fixture
    def temp_agents_dir(self):
        """Create a temporary agents directory."""
        temp_dir = tempfile.mkdtemp()
        agents_dir = Path(temp_dir) / "agents"
        agents_dir.mkdir()
        yield agents_dir
        shutil.rmtree(temp_dir)

    def test_missing_required_field(self, temp_agents_dir):
        """Test that missing required fields raise error."""
        invalid_config = """
name: invalid_agent
role: "Invalid Agent"
# Missing goal and system_prompt
"""
        (temp_agents_dir / "invalid_agent.yaml").write_text(invalid_config)

        loader = AgentLoader(temp_agents_dir)
        with pytest.raises(AgentConfigError, match="Missing required fields"):
            loader.load("invalid_agent")

    def test_name_filename_mismatch(self, temp_agents_dir):
        """Test that name must match filename."""
        config = """
name: wrong_name
role: "Test Agent"
goal: "Test name mismatch"
system_prompt: "You are a test."
"""
        (temp_agents_dir / "correct_name.yaml").write_text(config)

        loader = AgentLoader(temp_agents_dir)
        with pytest.raises(AgentConfigError, match="must match filename"):
            loader.load("correct_name")

    def test_invalid_tool_autonomy(self, temp_agents_dir):
        """Test that invalid tool_autonomy raises error."""
        config = """
name: bad_autonomy
role: "Test Agent"
goal: "Test invalid autonomy"
system_prompt: "You are a test."
tool_autonomy: invalid_value
"""
        (temp_agents_dir / "bad_autonomy.yaml").write_text(config)

        loader = AgentLoader(temp_agents_dir)
        with pytest.raises(AgentConfigError, match="tool_autonomy"):
            loader.load("bad_autonomy")

    def test_invalid_context_strategy(self, temp_agents_dir):
        """Test that invalid context_strategy raises error."""
        config = """
name: bad_strategy
role: "Test Agent"
goal: "Test invalid strategy"
system_prompt: "You are a test."
context_strategy: invalid_value
"""
        (temp_agents_dir / "bad_strategy.yaml").write_text(config)

        loader = AgentLoader(temp_agents_dir)
        with pytest.raises(AgentConfigError, match="context_strategy"):
            loader.load("bad_strategy")

    def test_temperature_out_of_range(self, temp_agents_dir):
        """Test that temperature out of range raises error."""
        config = """
name: bad_temp
role: "Test Agent"
goal: "Test invalid temperature"
system_prompt: "You are a test."
temperature: 5.0
"""
        (temp_agents_dir / "bad_temp.yaml").write_text(config)

        loader = AgentLoader(temp_agents_dir)
        with pytest.raises(AgentConfigError, match="temperature"):
            loader.load("bad_temp")

    def test_invalid_yaml(self, temp_agents_dir):
        """Test that invalid YAML raises error."""
        (temp_agents_dir / "bad_yaml.yaml").write_text("invalid: yaml: content:")

        loader = AgentLoader(temp_agents_dir)
        with pytest.raises(AgentConfigError, match="Invalid YAML"):
            loader.load("bad_yaml")

    def test_invalid_type(self, temp_agents_dir):
        """Test that invalid field type raises error."""
        config = """
name: bad_type
role: "Test Agent"
goal: "Test invalid type"
system_prompt: "You are a test."
tools: "should be a list"
"""
        (temp_agents_dir / "bad_type.yaml").write_text(config)

        loader = AgentLoader(temp_agents_dir)
        with pytest.raises(AgentConfigError, match="must be a list"):
            loader.load("bad_type")


class TestAgentLoaderDefaults:
    """Tests for default value handling."""

    @pytest.fixture
    def temp_agents_dir(self):
        """Create a temporary agents directory."""
        temp_dir = tempfile.mkdtemp()
        agents_dir = Path(temp_dir) / "agents"
        agents_dir.mkdir()
        yield agents_dir
        shutil.rmtree(temp_dir)

    def test_defaults_applied(self, temp_agents_dir):
        """Test that defaults are applied for optional fields."""
        minimal_config = """
name: minimal_agent
role: "Minimal Agent"
goal: "Test minimal configuration"
system_prompt: "You are a minimal agent."
"""
        (temp_agents_dir / "minimal_agent.yaml").write_text(minimal_config)

        loader = AgentLoader(temp_agents_dir)
        profile = loader.load("minimal_agent")

        # Check defaults
        assert profile.tools == []
        assert profile.tool_autonomy == "manual"
        assert profile.capabilities == []
        assert profile.temperature == 0.7
        assert profile.max_tokens is None
        assert profile.context_strategy == "standard"
        assert profile.memory_config == {}
        assert profile.metadata == {}


class TestEmptyDirectory:
    """Tests for empty or missing directory."""

    def test_missing_directory_list(self):
        """Test listing from nonexistent directory."""
        loader = AgentLoader(Path("/nonexistent/path"))
        names = loader.list_available()
        assert names == []

    def test_missing_directory_load_all(self):
        """Test load_all from nonexistent directory."""
        loader = AgentLoader(Path("/nonexistent/path"))
        profiles = loader.load_all()
        assert profiles == {}
