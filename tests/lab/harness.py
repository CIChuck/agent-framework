"""
Headless test harness for the Friday Agent Framework.

HeadlessHarness composes a RuntimeKernel with MemoryProfile.EPHEMERAL
for full isolation. Implements LabHarnessInterface for deterministic
mock agent registration and integration testing.

Ref: Phase 1 Build Plan, Step 7.3
"""

from __future__ import annotations

import logging
from typing import Any

from friday_agent import AgentProfile
from friday_core.interfaces.lab import LabHarnessInterface
from friday_core.profiles import MemoryProfile
from friday_runtime import RuntimeConfig, RuntimeKernel

from tests.lab.mocks import create_mock_agent_factory

logger = logging.getLogger(__name__)


class HeadlessHarness(LabHarnessInterface):
    """
    The Lab's test execution environment.

    Composes a RuntimeKernel with MemoryProfile.EPHEMERAL for full
    isolation. No LLM calls unless explicitly configured — all agents
    default to deterministic mocks.
    """

    def __init__(self, config: RuntimeConfig | None = None) -> None:
        """
        Initialize the harness.

        Args:
            config: Optional runtime config. Defaults to
                RuntimeConfig.for_testing().
        """
        self._config = config or RuntimeConfig.for_testing()
        self._kernel = RuntimeKernel(
            config=self._config,
            memory_profile=MemoryProfile.EPHEMERAL,
        )
        self._mock_agents: dict[str, list[str]] = {}

    async def start(self) -> None:
        """Boot the kernel in ephemeral mode."""
        await self._kernel.start()

    async def stop(self) -> None:
        """Shut down the kernel."""
        await self._kernel.stop()

    # --- LabHarnessInterface ---

    def mock_agent(
        self,
        name: str,
        fixed_responses: list[str],
        profile: AgentProfile | None = None,
    ) -> None:
        """
        Register a deterministic mock agent.

        When the orchestrator routes to ``name``, it receives an agent
        that returns responses from ``fixed_responses`` in order,
        cycling if exhausted.

        If no profile with ``name`` is already registered, one is
        created automatically (or the provided ``profile`` is used).
        Uses the per-agent factory override on AgentRegistry.

        Args:
            name: Agent name to mock.
            fixed_responses: Ordered list of responses.
            profile: Optional AgentProfile. If not provided and the
                agent is not already registered, a minimal profile
                is created automatically.
        """
        self._mock_agents[name] = fixed_responses
        registry = self._kernel.agent_registry

        # Ensure a profile exists for this agent name
        if not registry.exists(name):
            if profile is None:
                profile = AgentProfile(
                    name=name,
                    role=f"Mock {name}",
                    goal=f"Deterministic mock for {name}",
                    system_prompt_template="You are {name}.",
                )
            registry.register(profile)

        registry.set_factory(
            create_mock_agent_factory(name, fixed_responses),
            agent_name=name,
        )

    async def inject_conflict(self, fact_a: Any, fact_b: Any) -> None:
        """
        Simulate a race condition or semantic conflict.

        Raises:
            NotImplementedError: Requires Arbitrator (Phase 2).
        """
        raise NotImplementedError("Conflict injection requires Arbitrator — Phase 2")

    async def replay_session(self, session_log_path: str) -> None:
        """
        Deterministically replay a recorded session.

        Raises:
            NotImplementedError: Requires transcript tooling (Phase 2).
        """
        raise NotImplementedError(
            "Session replay requires transcript tooling — Phase 2"
        )

    # --- Convenience accessors ---

    @property
    def kernel(self) -> RuntimeKernel:
        """Access the underlying RuntimeKernel."""
        return self._kernel
