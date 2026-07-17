"""
Agent Orchestrator.

Coordinates multiple agents within a session, handling:
- Explicit routing (@agent_name messages)
- Agent switching and context preservation
- Task delegation between agents
- Single active agent at a time (MVP model)

Ref: docs/archive/agent-phase-artifacts/completed-friday-agentic-core/orchestrator-mvp-build-plan.md
Ref: docs/archive/agent-phase-artifacts/completed-friday-agentic-core/phase-3-execution-plan.md
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from friday_agent.base import AgentBase
    from friday_agent.registry import AgentRegistry


logger = logging.getLogger(__name__)


class OrchestratorError(Exception):
    """Raised when orchestration operations fail."""

    pass


@dataclass(frozen=True)
class RoutingDecision:
    """Resolved route target for a user input."""

    target_agent: str
    message: str
    source: str  # explicit | active | default


class AgentOrchestrator:
    """
    Coordinates multiple agents within a conversation.

    The orchestrator manages agent lifecycle and routing:
    - Explicit routing via @agent_name prefix
    - Default agent fallback when no routing specified
    - Agent switching with context preservation
    - Task delegation between agents

    MVP Design:
    - Single active agent at a time (no concurrent execution)
    - Agent instances cached for session duration
    - Explicit routing first, then default agent fallback

    Usage:
        from friday_agent import AgentOrchestrator, AgentRegistry

        # Initialize with registry
        orchestrator = AgentOrchestrator(
            registry=registry,
            default_agent="assistant",
        )

        # Process messages (auto-routes @mentions)
        response = await orchestrator.process("@researcher Find info on memory systems")
        response = await orchestrator.process("What did you find?")  # Uses last active agent

        # Manual switching
        orchestrator.switch_agent("coder")
        response = await orchestrator.process("Implement this feature")

        # Delegation
        result = await orchestrator.delegate("reviewer", "Review this code", return_to_current=True)

    Note:
        The orchestrator owns agent instances once created. Use clear_cache()
        to release agents when done with a session.
    """  # noqa: E501

    # Routing pattern: @agent_name followed by message
    ROUTING_PATTERN = re.compile(r"^@(\w+)\s+(.+)$", re.DOTALL)

    def __init__(
        self,
        registry: AgentRegistry,
        default_agent: str | None = None,
        auto_initialize: bool = True,
    ):
        """
        Initialize orchestrator.

        Args:
            registry: AgentRegistry for agent lookup and creation
            default_agent: Name of default agent (used when no routing specified)
            auto_initialize: If True, initialize default agent on first use
        """
        if not registry.has_factory():
            raise OrchestratorError(
                "AgentRegistry must have a factory configured. "
                "Call registry.set_factory() before creating orchestrator."
            )

        self._registry = registry
        self._default_agent_name = default_agent
        self._auto_initialize = auto_initialize

        # Active agent state
        self._active_agent: AgentBase | None = None
        self._active_agent_name: str | None = None

        # Agent cache (name -> instance)
        self._agent_cache: dict[str, AgentBase] = {}

        # Session tracking
        self._session_id: str | None = None
        self._user_id: str = "default"
        self._message_count = 0
        self._delegation_history: list[dict[str, Any]] = []

        logger.debug(
            f"AgentOrchestrator initialized with default_agent={default_agent}, "
            f"auto_initialize={auto_initialize}"
        )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def registry(self) -> AgentRegistry:
        """Get the agent registry."""
        return self._registry

    @property
    def active_agent(self) -> AgentBase | None:
        """Get the currently active agent instance."""
        return self._active_agent

    @property
    def active_agent_name(self) -> str | None:
        """Get the name of the currently active agent."""
        return self._active_agent_name

    @property
    def default_agent_name(self) -> str | None:
        """Get the default agent name."""
        return self._default_agent_name

    @property
    def session_id(self) -> str | None:
        """Get the current session ID."""
        return self._session_id

    @property
    def message_count(self) -> int:
        """Get total messages processed."""
        return self._message_count

    # =========================================================================
    # Core Processing
    # =========================================================================

    async def process(self, user_input: str) -> str:
        """
        Process user input with automatic routing.

        Routes message based on:
        1. Explicit @mention -> target agent
        2. Active agent if set -> current agent
        3. Default agent if configured -> default agent
        4. Error if no agent available

        Args:
            user_input: User message (may include @agent_name prefix)

        Returns:
            Agent's response

        Raises:
            OrchestratorError: If no agent available to handle message
        """
        decision = self.route(user_input)

        if decision.source in ("explicit", "default"):
            await self._ensure_agent(decision.target_agent)
            logger.debug(
                f"Routing source={decision.source} to @{decision.target_agent}"
            )
        elif self._active_agent is None:
            await self._ensure_agent(decision.target_agent)
            logger.debug(
                f"Routing source=active required cache restore for @{decision.target_agent}"  # noqa: E501
            )

        # Process with active agent
        if self._active_agent is None:
            raise OrchestratorError("No active agent available after routing decision")

        self._message_count += 1
        response = await self._active_agent.run(decision.message)

        return str(response)

    def route(self, user_input: str) -> RoutingDecision:
        """
        Resolve routing without mutating orchestrator state.

        This is an additive route stage used by process().
        """
        target_agent, message = self._parse_routing(user_input)

        if target_agent:
            if not self._registry.exists(target_agent):
                available = ", ".join(self._registry.list_agents())
                raise OrchestratorError(
                    f"Agent '{target_agent}' not found in registry. Available: {available}"  # noqa: E501
                )
            return RoutingDecision(
                target_agent=target_agent, message=message, source="explicit"
            )

        if self._active_agent_name:
            return RoutingDecision(
                target_agent=self._active_agent_name,
                message=user_input,
                source="active",
            )

        if self._default_agent_name and self._auto_initialize:
            if not self._registry.exists(self._default_agent_name):
                available = ", ".join(self._registry.list_agents())
                raise OrchestratorError(
                    f"Default agent '{self._default_agent_name}' not found in registry. "  # noqa: E501
                    f"Available: {available}"
                )
            return RoutingDecision(
                target_agent=self._default_agent_name,
                message=user_input,
                source="default",
            )

        raise OrchestratorError(
            "No agent available to handle message. "
            "Either specify @agent_name, call switch_agent(), or configure default_agent."  # noqa: E501
        )

    async def switch_agent(self, name: str) -> None:
        """
        Switch to a different agent.

        The previous agent remains cached for potential return.
        The new agent is initialized with the same session.

        Args:
            name: Name of agent to switch to

        Raises:
            OrchestratorError: If agent not found in registry
        """
        if not self._registry.exists(name):
            available = ", ".join(self._registry.list_agents())
            raise OrchestratorError(
                f"Agent '{name}' not found in registry. Available: {available}"
            )

        await self._ensure_agent(name)
        logger.info(f"Switched to agent: {name}")

    async def delegate(
        self,
        agent_name: str,
        task: str,
        return_to_current: bool = True,
        handoff_payload: dict[str, Any] | None = None,
        skill_ref: str | None = None,
    ) -> str:
        """
        Delegate a task to another agent.

        The delegated agent handles the task, and control optionally
        returns to the original agent.

        Args:
            agent_name: Agent to delegate to
            task: Task description/message
            return_to_current: If True, switch back to original agent after

        Returns:
            Response from the delegated agent

        Raises:
            OrchestratorError: If target agent not found
        """
        resolved_agent_name = agent_name
        if skill_ref:
            resolved_agent_name = self.resolve_agent_for_skill(
                skill_ref=skill_ref,
                preferred_agent=agent_name,
            )

        if not self._registry.exists(resolved_agent_name):
            available = ", ".join(self._registry.list_agents())
            raise OrchestratorError(
                f"Agent '{resolved_agent_name}' not found for delegation. "
                f"Available: {available}"
            )

        # Remember current agent
        previous_agent = self._active_agent_name
        normalized_handoff = self._normalize_handoff_payload(
            agent_name=resolved_agent_name,
            payload=handoff_payload,
            source_agent=previous_agent,
        )

        # Switch to delegate
        await self._ensure_agent(resolved_agent_name)
        if normalized_handoff is None:
            logger.info(f"Delegating to {resolved_agent_name}: {task[:50]}...")
        else:
            logger.info(
                f"Delegating to {resolved_agent_name} with handoff_id="
                f"{normalized_handoff['handoff_id']}: {task[:50]}..."
            )

        # Execute task
        if self._active_agent is None:
            raise OrchestratorError("No active agent available for delegation")

        self._message_count += 1
        response = await self._active_agent.run(task)
        self._delegation_history.append(
            {
                "source_agent": previous_agent,
                "target_agent": resolved_agent_name,
                "skill_ref": skill_ref,
                "task_preview": task[:120],
                "handoff": normalized_handoff,
                "message_count": self._message_count,
            }
        )

        # Return to previous agent if requested
        if return_to_current and previous_agent:
            await self._ensure_agent(previous_agent)
            logger.debug(f"Returned to previous agent: {previous_agent}")

        return str(response)

    def resolve_agent_for_skill(
        self, skill_ref: str, preferred_agent: str | None = None
    ) -> str:
        """Resolve deterministic target agent for a required skill."""
        try:
            return self._registry.resolve_agent_for_skill(
                skill_ref,
                preferred_agent=preferred_agent,
            )
        except Exception as e:
            raise OrchestratorError(str(e)) from e

    # =========================================================================
    # Agent Management
    # =========================================================================

    def list_agents(self) -> list[str]:
        """
        List all available agents.

        Returns:
            Sorted list of agent names from registry
        """
        return self._registry.list_agents()

    def list_cached_agents(self) -> list[str]:
        """
        List agents currently in cache.

        Returns:
            List of cached agent names
        """
        return list(self._agent_cache.keys())

    def get_agent_info(self, name: str) -> dict:
        """
        Get information about an agent.

        Args:
            name: Agent name

        Returns:
            Dict with agent profile information

        Raises:
            KeyError: If agent not found
        """
        profile = self._registry.get_or_raise(name)
        return {
            "name": profile.name,
            "role": profile.role,
            "goal": profile.goal,
            "capabilities": profile.capabilities,
            "tools": profile.tools,
            "is_cached": name in self._agent_cache,
            "is_active": name == self._active_agent_name,
        }

    def get_status(self) -> dict:
        """
        Get orchestrator status.

        Returns:
            Dict with current state information
        """
        return {
            "active_agent": self._active_agent_name,
            "default_agent": self._default_agent_name,
            "cached_agents": list(self._agent_cache.keys()),
            "registered_agents": self._registry.list_agents(),
            "session_id": self._session_id,
            "user_id": self._user_id,
            "message_count": self._message_count,
            "delegation_count": len(self._delegation_history),
        }

    def get_delegation_history(self) -> list[dict[str, Any]]:
        """Return recorded delegation metadata for this orchestrator session."""
        return list(self._delegation_history)

    # =========================================================================
    # Session Management
    # =========================================================================

    async def set_session(self, session_id: str, user_id: str = "default") -> None:
        """
        Set the session context for all agents.

        Args:
            session_id: Session identifier
            user_id: User identifier
        """
        self._session_id = session_id
        self._user_id = user_id

        # Re-initialize any cached agents with new session
        for name, agent in self._agent_cache.items():
            await agent.initialize_session(session_id, user_id)
            logger.debug(f"Re-initialized agent {name} with session {session_id}")

    def clear_cache(self) -> int:
        """
        Clear the agent cache.

        This releases all cached agent instances.
        The active agent is also cleared.

        Returns:
            Number of agents cleared
        """
        count = len(self._agent_cache)
        self._agent_cache.clear()
        self._active_agent = None
        self._active_agent_name = None
        logger.info(f"Cleared {count} cached agents")
        return count

    async def shutdown(self) -> None:
        """
        Shutdown the orchestrator.

        Clears cache and releases resources.
        """
        self.clear_cache()
        self._message_count = 0
        self._session_id = None
        self._delegation_history.clear()
        logger.info("Orchestrator shutdown complete")

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _parse_routing(self, user_input: str) -> tuple[str | None, str]:
        """
        Parse routing information from input.

        Args:
            user_input: Raw user input

        Returns:
            Tuple of (agent_name or None, message)
        """
        match = self.ROUTING_PATTERN.match(user_input.strip())
        if match:
            agent_name = match.group(1).lower()
            message = match.group(2).strip()
            return agent_name, message
        return None, user_input

    async def _ensure_agent(self, name: str) -> AgentBase:
        """
        Ensure agent is cached and set as active.

        Args:
            name: Agent name

        Returns:
            Agent instance

        Raises:
            OrchestratorError: If agent creation fails
        """
        # Check cache first
        if name in self._agent_cache:
            agent = self._agent_cache[name]
        else:
            # Create new agent instance
            try:
                agent = self._registry.create_agent(name)
            except Exception as e:
                raise OrchestratorError(f"Failed to create agent '{name}': {e}") from e

            # Initialize session if we have one
            if self._session_id:
                await agent.initialize_session(self._session_id, self._user_id)

            self._agent_cache[name] = agent
            logger.debug(f"Cached new agent: {name}")

        # Set as active
        self._active_agent = agent
        self._active_agent_name = name

        return agent

    def _normalize_handoff_payload(
        self,
        agent_name: str,
        payload: dict[str, Any] | None,
        source_agent: str | None = None,
    ) -> dict[str, Any] | None:
        """Validate and normalize handoff payload metadata."""
        if payload is None:
            return None

        required = ("handoff_id", "ownership", "acceptance_criteria", "memory_scope")
        missing = [key for key in required if key not in payload]
        if missing:
            raise OrchestratorError(
                f"Handoff payload missing required fields: {', '.join(missing)}"
            )

        handoff_id = payload["handoff_id"]
        if not isinstance(handoff_id, str) or not handoff_id.strip():
            raise OrchestratorError(
                "Handoff payload field 'handoff_id' must be non-empty"
            )

        ownership = payload["ownership"]
        if ownership != agent_name:
            raise OrchestratorError(
                "Handoff payload 'ownership' must match delegated agent name"
            )

        criteria = payload["acceptance_criteria"]
        if not isinstance(criteria, (list, tuple)) or not criteria:
            raise OrchestratorError(
                "Handoff payload 'acceptance_criteria' must be a non-empty list"
            )
        if not all(isinstance(item, str) and item.strip() for item in criteria):
            raise OrchestratorError(
                "Handoff payload 'acceptance_criteria' entries must be non-empty strings"  # noqa: E501
            )

        memory_scope = payload["memory_scope"]
        if not isinstance(memory_scope, str) or not memory_scope.strip():
            raise OrchestratorError(
                "Handoff payload field 'memory_scope' must be non-empty"
            )

        session_id = payload.get("session_id", self._session_id)
        if self._session_id and session_id and session_id != self._session_id:
            raise OrchestratorError(
                "Handoff payload session_id does not match orchestrator session"
            )

        normalized = dict(payload)
        normalized["handoff_id"] = handoff_id.strip()
        normalized["acceptance_criteria"] = [item.strip() for item in criteria]
        normalized["memory_scope"] = memory_scope.strip()
        normalized["session_id"] = session_id
        normalized["user_id"] = payload.get("user_id", self._user_id)
        normalized["source_agent"] = payload.get("source_agent", source_agent)
        normalized["target_agent"] = payload.get("target_agent", agent_name)
        return normalized

    def __repr__(self) -> str:
        """Debug representation."""
        return (
            f"AgentOrchestrator("
            f"active={self._active_agent_name}, "
            f"cached={len(self._agent_cache)}, "
            f"messages={self._message_count})"
        )
