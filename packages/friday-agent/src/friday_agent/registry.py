"""
Agent Registry.

Central registry for agent profiles with capability-based lookup
and on-demand agent instantiation.

Ref: docs/archive/agent-phase-artifacts/completed-friday-agentic-core/agent-registry-build-plan.md
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

from friday_agent.loader import AgentLoader
from friday_agent.profile import AgentProfile

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
        self._factory: Callable[[AgentProfile], AgentBase] | None = None
        self._per_agent_factories: dict[str, Callable[[AgentProfile], AgentBase]] = {}

        # Capability index for fast lookup
        self._capability_index: dict[str, set[str]] = {}  # capability -> agent names
        self._skill_index: dict[str, set[str]] = {}  # skill_ref -> agent names

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
        self._index_skills(profile)
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
                self._index_skills(profile)
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
        for skill_ref in profile.skills:
            if skill_ref in self._skill_index:
                self._skill_index[skill_ref].discard(name)
                if not self._skill_index[skill_ref]:
                    del self._skill_index[skill_ref]

        del self._profiles[name]
        logger.info(f"Unregistered agent: {name}")
        return True

    def clear(self) -> None:
        """Remove all registered agents."""
        self._profiles.clear()
        self._capability_index.clear()
        self._skill_index.clear()
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
    # Skill-Based Lookup
    # =========================================================================

    def find_by_skill(self, skill_ref: str) -> list[AgentProfile]:
        """Find agents that declare a canonical skill reference."""
        agent_names = self._skill_index.get(skill_ref, set())
        return [self._profiles[name] for name in sorted(agent_names)]

    def list_skills(self) -> list[str]:
        """List all declared skill references."""
        return sorted(self._skill_index.keys())

    def get_skill_stats(self) -> dict[str, int]:
        """Get count of agents per skill reference."""
        return {skill: len(agents) for skill, agents in self._skill_index.items()}

    def resolve_agent_for_skill(
        self, skill_ref: str, preferred_agent: str | None = None
    ) -> str:
        """
        Resolve deterministic target agent for a required skill.

        Preferred agent is selected when it advertises the skill.
        Otherwise the first sorted matching agent is returned.
        """
        agent_names = sorted(self._skill_index.get(skill_ref, set()))
        if preferred_agent and preferred_agent in agent_names:
            return preferred_agent
        if not agent_names:
            raise AgentRegistryError(
                f"No registered agent declares required skill '{skill_ref}'"
            )
        return agent_names[0]

    # =========================================================================
    # Agent Instantiation
    # =========================================================================

    def set_factory(
        self,
        factory: Callable[[AgentProfile], AgentBase],
        agent_name: str | None = None,
    ) -> None:
        """
        Set an agent factory function.

        The factory takes an AgentProfile and returns an AgentBase instance.
        It should be configured by the container with all necessary dependencies.

        Args:
            factory: Function that creates AgentBase from AgentProfile.
            agent_name: If provided, this factory is used ONLY for this
                agent name. The global factory remains the fallback for
                all other agents.

        Example:
            # Global factory
            registry.set_factory(create_agent)

            # Per-agent override (e.g., for testing)
            registry.set_factory(mock_factory, agent_name="researcher")
        """
        if agent_name:
            self._per_agent_factories[agent_name] = factory
            logger.debug(f"Per-agent factory configured for '{agent_name}'")
        else:
            self._factory = factory
            logger.debug("Agent factory configured")

    def has_factory(self) -> bool:
        """Check if factory is configured."""
        return self._factory is not None

    def create_agent(self, name: str) -> AgentBase:
        """
        Create an agent instance by name.

        Checks per-agent factory overrides first, then falls back
        to the global factory.

        Args:
            name: Registered agent name

        Returns:
            Instantiated agent

        Raises:
            AgentRegistryError: If no factory configured
            KeyError: If agent not found
        """
        # Per-agent factory takes priority over global factory
        factory = self._per_agent_factories.get(name, self._factory)

        if factory is None:
            raise AgentRegistryError(
                "No agent factory configured. Call set_factory() first."
            )

        profile = self.get_or_raise(name)
        agent = factory(profile)
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

    def _index_skills(self, profile: AgentProfile) -> None:
        """Add profile's canonical skill references to the index."""
        for skill_ref in profile.skills:
            if skill_ref not in self._skill_index:
                self._skill_index[skill_ref] = set()
            self._skill_index[skill_ref].add(profile.name)

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
            f"skills={len(self._skill_index)}, "
            f"has_factory={self.has_factory()})"
        )
