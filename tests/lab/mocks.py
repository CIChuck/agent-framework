# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""
Mock agent factory for deterministic testing.

Creates mock agents that return fixed responses in order,
cycling back to the start when exhausted.

Ref: Phase 1 Build Plan, Step 7.4
"""

from __future__ import annotations

from itertools import cycle
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

if TYPE_CHECKING:
    from friday_agent.profile import AgentProfile


def create_mock_agent_factory(name: str, fixed_responses: list[str]):
    """
    Create a factory function compatible with AgentRegistry.set_factory().

    The produced agent returns responses from fixed_responses in order,
    cycling back to the start if exhausted.

    Args:
        name: Agent name for the mock.
        fixed_responses: Ordered list of responses to return.

    Returns:
        Factory callable with signature (AgentProfile) -> AgentBase.
    """
    response_cycle = cycle(fixed_responses)

    def factory(profile: AgentProfile):
        """Create a deterministic mock agent."""
        agent = AsyncMock()
        agent.name = name
        agent.run = AsyncMock(side_effect=lambda _: next(response_cycle))
        agent.initialize_session = AsyncMock()
        agent.set_autonomy_policy = MagicMock()
        agent.emit_telemetry = MagicMock()
        return agent

    return factory
