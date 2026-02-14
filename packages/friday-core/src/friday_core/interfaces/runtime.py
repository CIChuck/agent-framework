"""
Runtime Interface.

Defines the SystemRuntime contract for the headless runtime kernel.
The runtime manages service lifecycle, agent spawning, and workflow
execution without requiring a presentation layer.

Ref: Phase 1 Build Plan, Section 2 - Interface Compliance Matrix
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from friday_core.interfaces.agent import AgentInterface


class SystemRuntime(ABC):
    """
    Core runtime contract for the Friday Agent Framework.

    Manages the lifecycle of framework services (LLM, memory, tools,
    telemetry) and provides agent spawning and workflow execution
    capabilities. Implementations should support both headless and
    CLI-attached operation modes.
    """

    @abstractmethod
    async def start(self) -> None:
        """
        Initialize all eager services (LLM, memory, tools, telemetry).

        Must be called before any other operations. Raises on failure
        to initialize required services.
        """
        ...

    @abstractmethod
    async def stop(self) -> None:
        """
        Gracefully shut down all services.

        Flushes logs, persists memory state, and releases resources.
        Safe to call multiple times.
        """
        ...

    @abstractmethod
    async def create_session(
        self, user_id: str = "default"
    ) -> str:
        """
        Create a new session identifier.

        Args:
            user_id: User identifier for the session.

        Returns:
            A unique session ID string.
        """
        ...

    @abstractmethod
    def spawn_agent(self, name: str) -> AgentInterface:
        """
        Create an agent instance by name from the registry.

        Args:
            name: Registered agent name.

        Returns:
            Configured AgentInterface instance ready for execution.

        Raises:
            KeyError: If no agent profile exists with the given name.
            RuntimeError: If no agent factory is configured.
        """
        ...

    @abstractmethod
    async def execute_workflow(
        self, workflow_name: str, initial_inputs: dict[str, Any] | None = None
    ) -> Any:
        """
        Load and execute a named workflow definition.

        Args:
            workflow_name: Name of the workflow to execute.
            initial_inputs: Optional initial variable bindings.

        Returns:
            Workflow execution result.
        """
        ...
