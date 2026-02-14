"""
Agent Interface.

Defines the AgentInterface contract that all agent implementations
must satisfy. The interface matches the existing AgentBase signatures
to ensure backward compatibility.

Ref: Phase 1 Build Plan, Section 2 - Interface Compliance Matrix
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AgentInterface(ABC):
    """
    Abstract interface for all Friday agents.

    Defines the minimal contract for agent lifecycle management
    and execution. The signatures intentionally match AgentBase
    to ensure existing implementations comply without modification.
    """

    @abstractmethod
    async def run(self, input_signal: str) -> str:
        """
        Execute the agent's core logic on the given input.

        Args:
            input_signal: User or orchestrator input to process.

        Returns:
            Agent response string.
        """
        ...

    @abstractmethod
    async def initialize_session(
        self,
        session_id: str | None = None,
        user_id: str = "default",
    ) -> Any:
        """
        Initialize or resume a session for this agent.

        Args:
            session_id: Existing session ID to resume, or None
                to create a new session.
            user_id: User identifier for the session.

        Returns:
            SessionState instance for the initialized session.

        Note:
            This signature matches AgentBase.initialize_session(),
            not the original spec's (session_id: str, user_id: str) -> None.
        """
        ...

    @abstractmethod
    def emit_telemetry(self, event_type: str, data: dict[str, Any]) -> None:
        """
        Emit a telemetry event.

        Args:
            event_type: Type of event to emit.
            data: Event payload data.
        """
        ...
