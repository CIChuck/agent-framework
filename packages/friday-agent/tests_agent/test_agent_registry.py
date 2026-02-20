"""
Unit tests for AgentRegistry.

Tests agent registration, capability-based lookup, and instantiation.
"""

import shutil
import tempfile
from pathlib import Path

import pytest
from friday_agent import (
    AgentLoader,
    AgentProfile,
    AgentRegistry,
    AgentRegistryError,
)


class TestAgentRegistry:
    """Tests for AgentRegistry functionality."""

    @pytest.fixture
    def sample_profile(self):
        """Create a sample agent profile."""
        return AgentProfile(
            name="test_agent",
            role="Test Agent",
            goal="Test the registry",
            system_prompt_template="You are a test agent.",
            tools=["tool_a", "tool_b"],
            _capabilities=["testing", "validation"],
            _skills=["planner.basic@1.0.0"],
        )

    @pytest.fixture
    def another_profile(self):
        """Create another sample profile."""
        return AgentProfile(
            name="another_agent",
            role="Another Agent",
            goal="Another test agent",
            system_prompt_template="You are another test agent.",
            tools=["tool_c"],
            _capabilities=["validation", "analysis"],
            _skills=["writer.advanced@2.1.0", "planner.basic@1.0.0"],
        )

    @pytest.fixture
    def registry(self):
        """Create an empty registry."""
        return AgentRegistry()

    def test_register_agent(self, registry, sample_profile):
        """Test registering an agent."""
        registry.register(sample_profile)
        assert registry.exists("test_agent")
        assert registry.count() == 1

    def test_register_duplicate_raises(self, registry, sample_profile):
        """Test registering duplicate raises error."""
        registry.register(sample_profile)
        with pytest.raises(AgentRegistryError, match="already registered"):
            registry.register(sample_profile)

    def test_get_agent(self, registry, sample_profile):
        """Test getting an agent by name."""
        registry.register(sample_profile)
        profile = registry.get("test_agent")
        assert profile is not None
        assert profile.name == "test_agent"

    def test_get_nonexistent_returns_none(self, registry):
        """Test getting nonexistent agent returns None."""
        assert registry.get("nonexistent") is None

    def test_get_or_raise(self, registry, sample_profile):
        """Test get_or_raise with existing agent."""
        registry.register(sample_profile)
        profile = registry.get_or_raise("test_agent")
        assert profile.name == "test_agent"

    def test_get_or_raise_missing(self, registry):
        """Test get_or_raise with missing agent."""
        with pytest.raises(KeyError, match="not found"):
            registry.get_or_raise("nonexistent")

    def test_unregister(self, registry, sample_profile):
        """Test unregistering an agent."""
        registry.register(sample_profile)
        assert registry.unregister("test_agent") is True
        assert not registry.exists("test_agent")

    def test_unregister_nonexistent(self, registry):
        """Test unregistering nonexistent agent returns False."""
        assert registry.unregister("nonexistent") is False

    def test_clear(self, registry, sample_profile):
        """Test clearing registry."""
        registry.register(sample_profile)
        registry.clear()
        assert registry.count() == 0

    def test_list_agents(self, registry, sample_profile, another_profile):
        """Test listing agent names."""
        registry.register(sample_profile)
        registry.register(another_profile)
        names = registry.list_agents()
        assert "test_agent" in names
        assert "another_agent" in names
        assert len(names) == 2

    def test_list_profiles(self, registry, sample_profile, another_profile):
        """Test listing all profiles."""
        registry.register(sample_profile)
        registry.register(another_profile)
        profiles = registry.list_profiles()
        assert len(profiles) == 2
        names = [p.name for p in profiles]
        assert "test_agent" in names
        assert "another_agent" in names


class TestCapabilityLookup:
    """Tests for capability-based lookup."""

    @pytest.fixture
    def registry_with_agents(self):
        """Create a registry with multiple agents."""
        registry = AgentRegistry()

        # Agent with testing and validation capabilities
        registry.register(
            AgentProfile(
                name="tester",
                role="Tester",
                goal="Test things",
                system_prompt_template="You are a tester.",
                _capabilities=["testing", "validation"],
                _skills=["planner.basic@1.0.0"],
            )
        )

        # Agent with coding and debugging capabilities
        registry.register(
            AgentProfile(
                name="coder",
                role="Coder",
                goal="Write code",
                system_prompt_template="You are a coder.",
                _capabilities=["coding", "debugging"],
                _skills=["coder.repair@1.2.0"],
            )
        )

        # Agent with validation and analysis capabilities
        registry.register(
            AgentProfile(
                name="analyst",
                role="Analyst",
                goal="Analyze things",
                system_prompt_template="You are an analyst.",
                _capabilities=["validation", "analysis"],
                _skills=["planner.basic@1.0.0", "analyst.review@1.0.0"],
            )
        )

        return registry

    def test_find_by_capability(self, registry_with_agents):
        """Test finding agents by single capability."""
        results = registry_with_agents.find_by_capability("testing")
        assert len(results) == 1
        assert results[0].name == "tester"

    def test_find_by_capability_multiple_matches(self, registry_with_agents):
        """Test finding when multiple agents have capability."""
        results = registry_with_agents.find_by_capability("validation")
        assert len(results) == 2
        names = [p.name for p in results]
        assert "tester" in names
        assert "analyst" in names

    def test_find_by_capability_no_matches(self, registry_with_agents):
        """Test finding with no matches."""
        results = registry_with_agents.find_by_capability("nonexistent")
        assert len(results) == 0

    def test_find_by_capabilities_any(self, registry_with_agents):
        """Test finding by any capability (OR logic)."""
        results = registry_with_agents.find_by_capabilities(
            ["testing", "coding"], match_all=False
        )
        assert len(results) == 2
        names = [p.name for p in results]
        assert "tester" in names
        assert "coder" in names

    def test_find_by_capabilities_all(self, registry_with_agents):
        """Test finding by all capabilities (AND logic)."""
        # Should match tester (has both testing and validation)
        results = registry_with_agents.find_by_capabilities(
            ["testing", "validation"], match_all=True
        )
        assert len(results) == 1
        assert results[0].name == "tester"

    def test_find_by_capabilities_all_no_match(self, registry_with_agents):
        """Test finding by all capabilities with no match."""
        # No agent has both testing and coding
        results = registry_with_agents.find_by_capabilities(
            ["testing", "coding"], match_all=True
        )
        assert len(results) == 0

    def test_list_capabilities(self, registry_with_agents):
        """Test listing all capabilities."""
        caps = registry_with_agents.list_capabilities()
        assert "testing" in caps
        assert "validation" in caps
        assert "coding" in caps
        assert "debugging" in caps
        assert "analysis" in caps

    def test_get_capability_stats(self, registry_with_agents):
        """Test getting capability statistics."""
        stats = registry_with_agents.get_capability_stats()
        assert stats["validation"] == 2  # tester and analyst
        assert stats["testing"] == 1
        assert stats["coding"] == 1

    def test_find_by_skill(self, registry_with_agents):
        """Test finding agents by canonical skill reference."""
        results = registry_with_agents.find_by_skill("planner.basic@1.0.0")
        assert len(results) == 2
        names = [profile.name for profile in results]
        assert "tester" in names
        assert "analyst" in names

    def test_resolve_agent_for_skill_prefers_requested_agent(
        self, registry_with_agents
    ):
        """Test deterministic skill resolution with preferred agent override."""
        resolved = registry_with_agents.resolve_agent_for_skill(
            "planner.basic@1.0.0",
            preferred_agent="analyst",
        )
        assert resolved == "analyst"

    def test_resolve_agent_for_skill_falls_back_sorted(self, registry_with_agents):
        """Test deterministic fallback skill resolution order."""
        resolved = registry_with_agents.resolve_agent_for_skill("planner.basic@1.0.0")
        assert resolved == "analyst"

    def test_resolve_agent_for_missing_skill_raises(self, registry_with_agents):
        """Test missing skill resolution raises registry error."""
        with pytest.raises(AgentRegistryError, match="declares required skill"):
            registry_with_agents.resolve_agent_for_skill("missing.skill@1.0.0")


class TestAgentInstantiation:
    """Tests for agent instantiation via factory."""

    @pytest.fixture
    def sample_profile(self):
        """Create a sample profile."""
        return AgentProfile(
            name="test_agent",
            role="Test Agent",
            goal="Test instantiation",
            system_prompt_template="You are a test agent.",
        )

    @pytest.fixture
    def registry(self, sample_profile):
        """Create registry with a profile."""
        registry = AgentRegistry()
        registry.register(sample_profile)
        return registry

    def test_create_agent_no_factory(self, registry):
        """Test creating agent without factory raises."""
        with pytest.raises(AgentRegistryError, match="No agent factory"):
            registry.create_agent("test_agent")

    def test_create_agent_with_factory(self, registry):
        """Test creating agent with factory."""
        created = []

        def mock_factory(profile):
            created.append(profile)
            return f"agent:{profile.name}"

        registry.set_factory(mock_factory)
        result = registry.create_agent("test_agent")

        assert result == "agent:test_agent"
        assert len(created) == 1
        assert created[0].name == "test_agent"

    def test_has_factory(self, registry):
        """Test has_factory check."""
        assert registry.has_factory() is False
        registry.set_factory(lambda p: p)
        assert registry.has_factory() is True

    def test_create_nonexistent_agent(self, registry):
        """Test creating nonexistent agent raises KeyError."""
        registry.set_factory(lambda p: p)
        with pytest.raises(KeyError, match="not found"):
            registry.create_agent("nonexistent")


class TestRegistryWithLoader:
    """Tests for registry integration with AgentLoader."""

    @pytest.fixture
    def temp_agents_dir(self):
        """Create a temporary agents directory with configs."""
        temp_dir = tempfile.mkdtemp()
        agents_dir = Path(temp_dir) / "agents"
        agents_dir.mkdir()

        # Create test agent
        (agents_dir / "test_agent.yaml").write_text("""
name: test_agent
role: "Test Agent"
goal: "Test registry-loader integration"
system_prompt: "You are a test agent."
capabilities:
  - testing
""")

        (agents_dir / "another_agent.yaml").write_text("""
name: another_agent
role: "Another Agent"
goal: "Test another agent"
system_prompt: "You are another agent."
capabilities:
  - analysis
""")

        yield agents_dir
        shutil.rmtree(temp_dir)

    def test_register_from_yaml(self, temp_agents_dir):
        """Test registering agent from YAML file."""
        loader = AgentLoader(temp_agents_dir)
        registry = AgentRegistry(loader)

        profile = registry.register_from_yaml("test_agent")

        assert profile.name == "test_agent"
        assert registry.exists("test_agent")

    def test_register_from_yaml_no_loader(self):
        """Test register_from_yaml without loader raises."""
        registry = AgentRegistry()
        with pytest.raises(AgentRegistryError, match="No AgentLoader"):
            registry.register_from_yaml("test_agent")

    def test_load_all_from_directory(self, temp_agents_dir):
        """Test loading all agents from directory."""
        loader = AgentLoader(temp_agents_dir)
        registry = AgentRegistry(loader)

        count = registry.load_all_from_directory()

        assert count == 2
        assert registry.exists("test_agent")
        assert registry.exists("another_agent")

    def test_load_all_skips_existing(self, temp_agents_dir):
        """Test that load_all skips already registered agents."""
        loader = AgentLoader(temp_agents_dir)
        registry = AgentRegistry(loader)

        # Pre-register one agent
        registry.register(
            AgentProfile(
                name="test_agent",
                role="Pre-registered",
                goal="Test",
                system_prompt_template="Test",
            )
        )

        count = registry.load_all_from_directory()

        # Should only load the other agent
        assert count == 1
        # Pre-registered agent should have original role
        profile = registry.get("test_agent")
        assert profile.role == "Pre-registered"


class TestSerialization:
    """Tests for registry serialization."""

    @pytest.fixture
    def registry(self):
        """Create a registry with agents."""
        registry = AgentRegistry()
        registry.register(
            AgentProfile(
                name="agent1",
                role="Role 1",
                goal="Goal 1",
                system_prompt_template="Prompt 1",
                _capabilities=["cap1"],
            )
        )
        registry.register(
            AgentProfile(
                name="agent2",
                role="Role 2",
                goal="Goal 2",
                system_prompt_template="Prompt 2",
                _capabilities=["cap2"],
            )
        )
        return registry

    def test_to_dict(self, registry):
        """Test serializing registry to dict."""
        data = registry.to_dict()

        assert "agent1" in data
        assert "agent2" in data
        assert data["agent1"]["name"] == "agent1"
        assert data["agent1"]["role"] == "Role 1"
        assert data["agent2"]["name"] == "agent2"

    def test_repr(self, registry):
        """Test string representation."""
        repr_str = repr(registry)
        assert "agents=2" in repr_str
        assert "capabilities=2" in repr_str
