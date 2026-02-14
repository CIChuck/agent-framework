"""
Agent Registry Interface.

Defines the RegistryInterface contract for agent profile management
and agent instantiation.

Ref: Phase 1 Build Plan, Section 2 - Interface Compliance Matrix
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from friday_core.interfaces.agent import AgentInterface


class RegistryInterface(ABC):
    """
    Abstract interface for agent registration and discovery.

    Manages agent profiles, capability-based lookup, and agent
    instantiation via configurable factory functions.
    """

    @abstractmethod
    def register_profile(self, profile: Any) -> None:
        """
        Register an agent profile with the registry.

        Args:
            profile: AgentProfile instance to register.

        Raises:
            ValueError: If a profile with the same name already exists.
        """
        ...

    @abstractmethod
    def load_manifests(self, directory: str) -> None:
        """
        Load agent manifests from a directory.

        Scans the directory for agent definition files and registers
        discovered profiles.

        Args:
            directory: Path to directory containing agent manifests.
        """
        ...

    @abstractmethod
    def find_agents(self, capability: str) -> list[Any]:
        """
        Find agents matching a given capability.

        Args:
            capability: Capability string to search for.

        Returns:
            List of AgentProfile instances with the requested capability.
        """
        ...

    @abstractmethod
    def create_agent(self, name: str) -> AgentInterface:
        """
        Create an agent instance by name.

        Args:
            name: Registered agent name.

        Returns:
            Configured agent instance.

        Raises:
            KeyError: If no profile exists with the given name.
            RuntimeError: If no factory is configured.
        """
        ...
