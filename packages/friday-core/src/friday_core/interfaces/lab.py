"""
Lab Harness Interface.

Defines the LabHarnessInterface for integration testing the
agent framework in a controlled, deterministic environment.

Ref: Phase 1 Build Plan, Section 7
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LabHarnessInterface(ABC):
    """
    Integration environment for stress-testing the agent hive.

    Provides deterministic test execution by replacing LLM agents
    with mock implementations and enabling controlled conflict
    injection and session replay.
    """

    @abstractmethod
    def mock_agent(self, name: str, fixed_responses: list[str]) -> None:
        """
        Replace a real LLM agent with a deterministic mock.

        The mock agent returns responses from `fixed_responses` in
        order, cycling back to the start if exhausted.

        Args:
            name: Agent name to mock.
            fixed_responses: Ordered list of responses the mock
                will return.
        """
        ...

    @abstractmethod
    async def inject_conflict(self, fact_a: Any, fact_b: Any) -> None:
        """
        Simulate a race condition or semantic conflict.

        Args:
            fact_a: First conflicting memory proposal.
            fact_b: Second conflicting memory proposal.

        Raises:
            NotImplementedError: In Phase 1 (requires Arbitrator).
        """
        ...

    @abstractmethod
    async def replay_session(self, session_log_path: str) -> None:
        """
        Deterministically replay a recorded session.

        Args:
            session_log_path: Path to session transcript log.

        Raises:
            NotImplementedError: In Phase 1 (requires transcript tooling).
        """
        ...
