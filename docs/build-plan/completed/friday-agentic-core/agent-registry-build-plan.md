# Agent Registry Build Plan

**Status:** Planning
**Target:** Phase 2, Section 3.2 of Project Hive Master Plan
**Objective:** Implement central registry for agent profiles with capability-based lookup and instantiation

---

## 1. Problem Statement

No central registry exists for managing multiple agent profiles. The system needs:
- **Agent Discovery**: Orchestrator needs to find available agents
- **Capability Routing**: Match tasks to agents by capabilities
- **On-Demand Instantiation**: Create agent instances when needed
- **Centralized Management**: Single source of truth for agent definitions

Without a registry, the orchestrator cannot:
- Know which agents are available
- Route tasks to appropriate specialists
- Create agent instances with proper dependencies

---

## 2. Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      AgentLoader                             │
│  (From agent-configuration-build-plan)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      AgentRegistry                           │
├─────────────────────────────────────────────────────────────┤
│  Profiles:                                                  │
│    researcher → AgentProfile                                │
│    coder      → AgentProfile                                │
│    reviewer   → AgentProfile                                │
├─────────────────────────────────────────────────────────────┤
│  Capabilities Index:                                        │
│    research          → [researcher]                         │
│    coding            → [coder]                              │
│    code_review       → [reviewer, coder]                    │
├─────────────────────────────────────────────────────────────┤
│  Factory:                                                   │
│    (AgentProfile) → CopilotAgent                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FridayContainer                           │
│  - Provides agent_registry property                         │
│  - Configures factory with dependencies                     │
│  - Exposes get_team_agent(name) helper                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   AgentOrchestrator                          │
│  (Uses registry for routing and instantiation)              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Design Principles

1. **Separation of Concerns**: Registry manages profiles, factory creates instances
2. **Capability-Based Routing**: Find agents by what they can do
3. **Lazy Instantiation**: Agents created only when needed
4. **Pluggable Factory**: Container configures how agents are built
5. **Type Safety**: Strong typing for profiles and agents

---

## 3. Implementation

### 3.1 AgentRegistry Implementation

**Location:** `packages/friday-agent/src/friday_agent/registry.py`

```python
"""Central registry for agent profiles and instantiation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, TypeVar

from friday_agent.profile import AgentProfile
from friday_agent.loader import AgentLoader

if TYPE_CHECKING:
    from friday_agent.base import AgentBase


logger = logging.getLogger(__name__)

T = TypeVar("T", bound="AgentBase")


class AgentRegistryError(Exception):
    """Raised when registry operations fail."""

    pass


class AgentRegistry:
    """
    Central registry for agent profiles with capability-based lookup.

    The registry serves as the single source of truth for available agents.
    It supports:
    - Manual profile registration
    - Automatic loading from YAML files
    - Capability-based agent discovery
    - On-demand agent instantiation

    Usage:
        # Initialize with loader
        loader = AgentLoader(Path("agents/"))
        registry = AgentRegistry(loader)

        # Auto-load all agents
        registry.load_all_from_directory()

        # Find agents by capability
        researchers = registry.find_by_capability("research")

        # Configure factory (typically done by container)
        registry.set_factory(lambda profile: create_agent(profile))

        # Create agent instance
        agent = registry.create_agent("researcher")

    Note:
        The registry does NOT manage agent lifecycles. Once created,
        agents are owned by the caller (typically the orchestrator).
    """

    def __init__(self, loader: AgentLoader | None = None):
        """
        Initialize registry.

        Args:
            loader: Optional AgentLoader for file-based profiles.
                   If not provided, only manual registration is available.
        """
        self._profiles: dict[str, AgentProfile] = {}
        self._loader = loader
        self._factory: Callable[[AgentProfile], "AgentBase"] | None = None

        # Capability index for fast lookup
        self._capability_index: dict[str, set[str]] = {}  # capability -> agent names

        logger.debug("AgentRegistry initialized")

    @property
    def loader(self) -> AgentLoader | None:
        """Get the configured loader."""
        return self._loader

    # =========================================================================
    # Registration
    # =========================================================================

    def register(self, profile: AgentProfile) -> None:
        """
        Register an agent profile.

        Args:
            profile: AgentProfile to register

        Raises:
            AgentRegistryError: If agent with same name already registered
        """
        if profile.name in self._profiles:
            raise AgentRegistryError(f"Agent '{profile.name}' already registered")

        self._profiles[profile.name] = profile
        self._index_capabilities(profile)
        logger.info(f"Registered agent: {profile.name}")

    def register_from_yaml(self, name: str) -> AgentProfile:
        """
        Load and register agent from YAML file.

        Args:
            name: Agent name (filename without .yaml)

        Returns:
            Loaded AgentProfile

        Raises:
            AgentRegistryError: If no loader configured
            AgentConfigError: If file is invalid
        """
        if self._loader is None:
            raise AgentRegistryError("No AgentLoader configured")

        profile = self._loader.load(name)
        self.register(profile)
        return profile

    def load_all_from_directory(self) -> int:
        """
        Load all agent configs from loader's directory.

        Skips agents that are already registered (no error).

        Returns:
            Number of NEW agents loaded

        Raises:
            AgentRegistryError: If no loader configured
        """
        if self._loader is None:
            raise AgentRegistryError("No AgentLoader configured")

        profiles = self._loader.load_all()
        loaded = 0

        for profile in profiles.values():
            if profile.name not in self._profiles:
                self._profiles[profile.name] = profile
                self._index_capabilities(profile)
                loaded += 1
                logger.debug(f"Loaded agent from directory: {profile.name}")

        logger.info(f"Loaded {loaded} agents from directory")
        return loaded

    def unregister(self, name: str) -> bool:
        """
        Remove agent from registry.

        Args:
            name: Agent name to remove

        Returns:
            True if agent was removed, False if not found
        """
        if name not in self._profiles:
            return False

        profile = self._profiles[name]

        # Remove from capability index
        for capability in profile.capabilities:
            if capability in self._capability_index:
                self._capability_index[capability].discard(name)
                if not self._capability_index[capability]:
                    del self._capability_index[capability]

        del self._profiles[name]
        logger.info(f"Unregistered agent: {name}")
        return True

    def clear(self) -> None:
        """Remove all registered agents."""
        self._profiles.clear()
        self._capability_index.clear()
        logger.debug("Registry cleared")

    # =========================================================================
    # Lookup
    # =========================================================================

    def get(self, name: str) -> AgentProfile | None:
        """
        Get agent profile by name.

        Args:
            name: Agent name

        Returns:
            AgentProfile if found, None otherwise
        """
        return self._profiles.get(name)

    def get_or_raise(self, name: str) -> AgentProfile:
        """
        Get agent profile or raise error.

        Args:
            name: Agent name

        Returns:
            AgentProfile

        Raises:
            KeyError: If agent not found
        """
        profile = self.get(name)
        if profile is None:
            available = ", ".join(sorted(self._profiles.keys()))
            raise KeyError(f"Agent '{name}' not found. Available: {available}")
        return profile

    def exists(self, name: str) -> bool:
        """Check if agent is registered."""
        return name in self._profiles

    def list_agents(self) -> list[str]:
        """
        List all registered agent names.

        Returns:
            Sorted list of agent names
        """
        return sorted(self._profiles.keys())

    def list_profiles(self) -> list[AgentProfile]:
        """
        List all registered profiles.

        Returns:
            List of AgentProfile instances
        """
        return list(self._profiles.values())

    def count(self) -> int:
        """Return number of registered agents."""
        return len(self._profiles)

    # =========================================================================
    # Capability-Based Lookup
    # =========================================================================

    def find_by_capability(self, capability: str) -> list[AgentProfile]:
        """
        Find agents with a specific capability.

        Args:
            capability: Capability tag to search for

        Returns:
            List of matching profiles (may be empty)
        """
        agent_names = self._capability_index.get(capability, set())
        return [self._profiles[name] for name in agent_names]

    def find_by_capabilities(
        self,
        capabilities: list[str],
        match_all: bool = False,
    ) -> list[AgentProfile]:
        """
        Find agents matching capability requirements.

        Args:
            capabilities: List of required capabilities
            match_all: If True, agent must have ALL capabilities.
                      If False (default), agent must have ANY capability.

        Returns:
            List of matching profiles (may be empty)
        """
        if not capabilities:
            return []

        results: list[AgentProfile] = []

        for profile in self._profiles.values():
            agent_caps = set(profile.capabilities)
            required_caps = set(capabilities)

            if match_all:
                # Agent must have all required capabilities
                if required_caps.issubset(agent_caps):
                    results.append(profile)
            else:
                # Agent must have at least one required capability
                if required_caps & agent_caps:
                    results.append(profile)

        return results

    def list_capabilities(self) -> list[str]:
        """
        List all registered capabilities.

        Returns:
            Sorted list of capability tags
        """
        return sorted(self._capability_index.keys())

    def get_capability_stats(self) -> dict[str, int]:
        """
        Get count of agents per capability.

        Returns:
            Dict mapping capability to count of agents
        """
        return {cap: len(agents) for cap, agents in self._capability_index.items()}

    # =========================================================================
    # Agent Instantiation
    # =========================================================================

    def set_factory(
        self,
        factory: Callable[[AgentProfile], "AgentBase"],
    ) -> None:
        """
        Set the agent factory function.

        The factory takes an AgentProfile and returns an AgentBase instance.
        It should be configured by the container with all necessary dependencies.

        Args:
            factory: Function that creates AgentBase from AgentProfile

        Example:
            def create_agent(profile: AgentProfile) -> CopilotAgent:
                return CopilotAgent(
                    profile=profile,
                    memory=container.memory,
                    llm=container.llm,
                )
            registry.set_factory(create_agent)
        """
        self._factory = factory
        logger.debug("Agent factory configured")

    def has_factory(self) -> bool:
        """Check if factory is configured."""
        return self._factory is not None

    def create_agent(self, name: str) -> "AgentBase":
        """
        Create an agent instance by name.

        Uses the configured factory to instantiate the agent with
        all necessary dependencies.

        Args:
            name: Registered agent name

        Returns:
            Instantiated agent

        Raises:
            AgentRegistryError: If no factory configured
            KeyError: If agent not found
        """
        if self._factory is None:
            raise AgentRegistryError(
                "No agent factory configured. Call set_factory() first."
            )

        profile = self.get_or_raise(name)
        agent = self._factory(profile)
        logger.debug(f"Created agent instance: {name}")
        return agent

    # =========================================================================
    # Internal
    # =========================================================================

    def _index_capabilities(self, profile: AgentProfile) -> None:
        """Add profile's capabilities to the index."""
        for capability in profile.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = set()
            self._capability_index[capability].add(profile.name)

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, dict]:
        """
        Serialize registry to dictionary.

        Returns:
            Dict mapping agent name to profile dict
        """
        return {name: profile.to_dict() for name, profile in self._profiles.items()}

    def __repr__(self) -> str:
        """Debug representation."""
        return (
            f"AgentRegistry(agents={len(self._profiles)}, "
            f"capabilities={len(self._capability_index)}, "
            f"has_factory={self.has_factory()})"
        )
```

### 3.2 FridayContainer Integration

**Location:** `apps/friday-cli/src/friday_cli/container.py`

Add agent registry support:

```python
# Add to imports
from friday_agent import AgentLoader, AgentProfile, AgentRegistry
from friday_agent.copilot import CopilotAgent

class FridayContainer:
    """
    Dependency injection container for Friday components.

    Provides lazy initialization of all major components.
    """

    def __init__(self, config: FridayConfig, memory_profile: MemoryProfile = MemoryProfile.FULL):
        self._config = config
        self._memory_profile = memory_profile

        # Lazy-initialized components
        self._agent_registry: AgentRegistry | None = None
        self._agent_loader: AgentLoader | None = None
        # ... other components ...

    # =========================================================================
    # Agent Registry
    # =========================================================================

    @property
    def agent_loader(self) -> AgentLoader:
        """Get or create agent loader."""
        if self._agent_loader is None:
            agents_dir = self._config.agents_dir or Path("agents")
            self._agent_loader = AgentLoader(agents_dir)
        return self._agent_loader

    @property
    def agent_registry(self) -> AgentRegistry:
        """
        Get or create agent registry.

        The registry is auto-configured with:
        - AgentLoader for YAML loading
        - Factory for agent instantiation
        - All agents from the agents directory
        """
        if self._agent_registry is None:
            # Create registry with loader
            self._agent_registry = AgentRegistry(self.agent_loader)

            # Configure factory
            self._agent_registry.set_factory(self._create_agent)

            # Auto-load agents from directory (if it exists)
            try:
                self._agent_registry.load_all_from_directory()
            except Exception as e:
                logger.warning(f"Could not load agents from directory: {e}")

        return self._agent_registry

    def _create_agent(self, profile: AgentProfile) -> CopilotAgent:
        """
        Factory function for creating agents.

        Configures agent with all necessary dependencies from the container.

        Args:
            profile: Agent profile

        Returns:
            Configured CopilotAgent instance
        """
        return CopilotAgent(
            profile=profile,
            memory=self.memory,
            context_engine=self.context_engine,
            llm=self.llm,
            tool_registry=self.tool_registry,
            telemetry=self.telemetry,
            transcript_store=self.transcript_store,
        )

    def get_team_agent(self, name: str) -> CopilotAgent:
        """
        Get or create a named agent.

        Convenience method for getting agent by name.

        Args:
            name: Agent name from registry

        Returns:
            Configured CopilotAgent instance

        Raises:
            KeyError: If agent not found
            AgentRegistryError: If registry not configured
        """
        return self.agent_registry.create_agent(name)

    def list_available_agents(self) -> list[str]:
        """
        List available agent names.

        Returns:
            Sorted list of agent names
        """
        return self.agent_registry.list_agents()

    def get_agent_info(self, name: str) -> dict | None:
        """
        Get information about an agent.

        Args:
            name: Agent name

        Returns:
            Dict with agent info or None if not found
        """
        profile = self.agent_registry.get(name)
        if profile is None:
            return None

        return {
            "name": profile.name,
            "role": profile.role,
            "goal": profile.goal,
            "capabilities": profile.capabilities,
            "tools": profile.tools,
            "tool_autonomy": profile.tool_autonomy,
        }
```

### 3.3 Package Exports Update

**Location:** `packages/friday-agent/src/friday_agent/__init__.py`

```python
"""Friday Agent package."""

from friday_agent.profile import AgentProfile
from friday_agent.loader import AgentLoader, AgentConfigError
from friday_agent.registry import AgentRegistry, AgentRegistryError
from friday_agent.base import AgentBase
from friday_agent.copilot import CopilotAgent

__all__ = [
    # Profile
    "AgentProfile",
    # Loading
    "AgentLoader",
    "AgentConfigError",
    # Registry
    "AgentRegistry",
    "AgentRegistryError",
    # Agents
    "AgentBase",
    "CopilotAgent",
]
```

---

## 4. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `packages/friday-agent/src/friday_agent/registry.py` | Create | AgentRegistry implementation |
| `packages/friday-agent/src/friday_agent/__init__.py` | Modify | Export AgentRegistry, AgentRegistryError |
| `apps/friday-cli/src/friday_cli/container.py` | Modify | Add agent_registry, get_team_agent, _create_agent |
| `packages/friday-agent/tests/test_registry.py` | Create | Unit tests for AgentRegistry |

---

## 5. Dependencies

### 5.1 Internal Dependencies
- `AgentLoader` from agent-configuration-build-plan
- `AgentProfile` from friday-agent package
- `CopilotAgent` for factory instantiation

### 5.2 No New External Dependencies

---

## 6. Verification

### 6.1 Unit Tests

**Location:** `packages/friday-agent/tests/test_registry.py`

```python
"""Unit tests for AgentRegistry."""

import pytest
from pathlib import Path

from friday_agent import AgentProfile, AgentLoader, AgentRegistry, AgentRegistryError


class TestAgentRegistry:
    """Test AgentRegistry functionality."""

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
        """Test unregistering nonexistent agent."""
        assert registry.unregister("nonexistent") is False

    def test_clear(self, registry, sample_profile):
        """Test clearing registry."""
        registry.register(sample_profile)
        registry.clear()
        assert registry.count() == 0

    def test_list_agents(self, registry, sample_profile):
        """Test listing agent names."""
        registry.register(sample_profile)
        names = registry.list_agents()
        assert "test_agent" in names

    def test_find_by_capability(self, registry, sample_profile):
        """Test finding agents by capability."""
        registry.register(sample_profile)
        results = registry.find_by_capability("testing")
        assert len(results) == 1
        assert results[0].name == "test_agent"

    def test_find_by_capability_empty(self, registry, sample_profile):
        """Test finding with no matches."""
        registry.register(sample_profile)
        results = registry.find_by_capability("nonexistent")
        assert len(results) == 0

    def test_find_by_capabilities_any(self, registry, sample_profile):
        """Test finding by any capability."""
        registry.register(sample_profile)
        results = registry.find_by_capabilities(["testing", "unknown"])
        assert len(results) == 1

    def test_find_by_capabilities_all(self, registry, sample_profile):
        """Test finding by all capabilities."""
        registry.register(sample_profile)
        # Has both
        results = registry.find_by_capabilities(
            ["testing", "validation"], match_all=True
        )
        assert len(results) == 1
        # Missing one
        results = registry.find_by_capabilities(
            ["testing", "unknown"], match_all=True
        )
        assert len(results) == 0

    def test_list_capabilities(self, registry, sample_profile):
        """Test listing all capabilities."""
        registry.register(sample_profile)
        caps = registry.list_capabilities()
        assert "testing" in caps
        assert "validation" in caps

    def test_create_agent_no_factory(self, registry, sample_profile):
        """Test creating agent without factory raises."""
        registry.register(sample_profile)
        with pytest.raises(AgentRegistryError, match="No agent factory"):
            registry.create_agent("test_agent")

    def test_create_agent_with_factory(self, registry, sample_profile):
        """Test creating agent with factory."""
        registry.register(sample_profile)

        created = []
        def mock_factory(profile):
            created.append(profile)
            return f"agent:{profile.name}"

        registry.set_factory(mock_factory)
        result = registry.create_agent("test_agent")

        assert result == "agent:test_agent"
        assert len(created) == 1
        assert created[0].name == "test_agent"

    def test_to_dict(self, registry, sample_profile):
        """Test serialization."""
        registry.register(sample_profile)
        data = registry.to_dict()
        assert "test_agent" in data
        assert data["test_agent"]["name"] == "test_agent"
```

### 6.2 Integration Test

```python
# Test with container
from friday_cli.container import FridayContainer, FridayConfig

config = FridayConfig()
container = FridayContainer(config)

# List available agents
agents = container.list_available_agents()
print(f"Available agents: {agents}")

# Get agent by name
if "researcher" in agents:
    agent = container.get_team_agent("researcher")
    print(f"Created agent: {agent}")

# Find by capability
researchers = container.agent_registry.find_by_capability("research")
print(f"Researchers: {[p.name for p in researchers]}")
```

### 6.3 Test Commands

```bash
# Run unit tests
pytest packages/friday-agent/tests/test_registry.py -v

# Test with real agents directory
python -c "
from pathlib import Path
from friday_agent import AgentLoader, AgentRegistry

loader = AgentLoader(Path('agents'))
registry = AgentRegistry(loader)
count = registry.load_all_from_directory()
print(f'Loaded {count} agents')
print(f'Available: {registry.list_agents()}')
print(f'Capabilities: {registry.list_capabilities()}')
"
```

---

## 7. Exit Criteria

1. `AgentRegistry` can register and retrieve profiles
2. Capability-based lookup finds correct agents
3. Factory integration creates agent instances
4. `FridayContainer` exposes `agent_registry` and `get_team_agent()`
5. Unit tests achieve 90%+ coverage
6. Integration with `AgentLoader` works end-to-end
7. Error messages are clear and actionable
