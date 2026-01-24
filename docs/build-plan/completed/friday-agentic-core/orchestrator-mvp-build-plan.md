# Orchestrator MVP Build Plan

**Status:** Planning
**Target:** Phase 3, Section 4.1 of Project Hive Master Plan
**Objective:** Enable multiple agents to exist and coordinate through a central orchestrator

---

## 1. Problem Statement

No mechanism exists for coordinating multiple agents. The current system supports only single-agent sessions. We need:
- **Task Routing**: Direct tasks to appropriate agents
- **Agent Switching**: Change active agent within a session
- **Shared Context**: Preserve conversation context across agents
- **Delegation**: One agent can request help from another

Without orchestration, the "Hive" cannot:
- Have a researcher gather info, then a coder implement it
- Allow users to switch between specialists mid-conversation
- Coordinate complex multi-agent workflows

---

## 2. Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User Input                              │
│  "Find info about X"  or  "@researcher find info about X"   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   AgentOrchestrator                          │
├─────────────────────────────────────────────────────────────┤
│  Routing:                                                   │
│    - Explicit: @agent_name message                          │
│    - Default: Use active agent                              │
│    - Future: Capability-based auto-routing                  │
├─────────────────────────────────────────────────────────────┤
│  State:                                                     │
│    - Active agent reference                                 │
│    - Agent instance cache                                   │
│    - Default agent configuration                            │
├─────────────────────────────────────────────────────────────┤
│  Operations:                                                │
│    - process(input) → response                              │
│    - switch_agent(name)                                     │
│    - delegate(agent, task)                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AgentRegistry                             │
│  (Provides profile lookup and agent instantiation)          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Agents                                 │
│  researcher  │  coder  │  reviewer  │  ...                  │
│  (All share the same MemoryController)                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Session Model

```
┌───────────────────────────────────────────────────────────────┐
│                    Orchestrator Session                        │
├───────────────────────────────────────────────────────────────┤
│  Memory (Shared):                                             │
│    - Graph Store     ← All agents read/write                  │
│    - Vector Store    ← All agents read/write                  │
│    - Transcript      ← Tracks which agent responded           │
├───────────────────────────────────────────────────────────────┤
│  Active Agent:                                                │
│    - Only one agent active at a time                          │
│    - Switching preserves memory context                       │
│    - Each agent has its own profile/persona                   │
├───────────────────────────────────────────────────────────────┤
│  Agent Cache:                                                 │
│    - Reuse agent instances (avoid re-initialization)          │
│    - Cleared on session end                                   │
└───────────────────────────────────────────────────────────────┘
```

### 2.3 Design Principles

1. **Single Active Agent**: Only one agent processes at a time (no concurrency in MVP)
2. **Shared Memory**: All agents share the same memory stores
3. **Explicit Routing First**: Start with `@agent_name` syntax, add auto-routing later
4. **Stateful Caching**: Agent instances cached for session duration
5. **Transparent Delegation**: Delegation returns result to user, not silent

---

## 3. Implementation

### 3.1 AgentOrchestrator Implementation

**Location:** `packages/friday-agent/src/friday_agent/orchestrator.py`

```python
"""Multi-agent orchestration for the Hive system."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

from friday_agent.registry import AgentRegistry

if TYPE_CHECKING:
    from friday_agent.base import AgentBase


logger = logging.getLogger(__name__)


class OrchestratorError(Exception):
    """Raised when orchestration fails."""

    pass


class AgentOrchestrator:
    """
    Orchestrates multiple agents for complex tasks.

    The orchestrator manages:
    - Task routing to appropriate agents
    - Agent switching within a session
    - Delegation between agents
    - Agent instance lifecycle

    Routing Patterns:
    - Explicit: "@researcher find information about X"
    - Default: Route to active agent (or default if none)
    - Future: Capability-based auto-routing

    Session Model:
    - One active agent at a time
    - Shared memory across all agents
    - Agent switching preserves conversation context
    - Agent instances cached for session duration

    Usage:
        orchestrator = AgentOrchestrator(registry, default_agent="assistant")
        response = await orchestrator.process("@researcher find info about AI")
        await orchestrator.switch_agent("coder")
        response = await orchestrator.process("Implement that feature")

    Note:
        The orchestrator does not own the memory stores. It expects
        agents to be created with shared memory by the registry's factory.
    """

    # Pattern for explicit agent routing: @agent_name message
    ROUTING_PATTERN = re.compile(r"^@(\w+)\s+(.+)$", re.DOTALL)

    def __init__(
        self,
        registry: AgentRegistry,
        default_agent: str | None = None,
    ):
        """
        Initialize orchestrator.

        Args:
            registry: Agent registry for agent lookup/creation
            default_agent: Name of default agent (used when no agent is active
                          and no explicit routing is specified)
        """
        self._registry = registry
        self._default_agent = default_agent

        # Session state
        self._active_agent: AgentBase | None = None
        self._active_agent_name: str | None = None
        self._agent_cache: dict[str, AgentBase] = {}

        logger.debug(
            f"AgentOrchestrator initialized (default_agent={default_agent})"
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
        """Get the currently active agent (may be None)."""
        return self._active_agent

    @property
    def active_agent_name(self) -> str | None:
        """Get the name of the currently active agent (may be None)."""
        return self._active_agent_name

    @property
    def default_agent(self) -> str | None:
        """Get the default agent name."""
        return self._default_agent

    @default_agent.setter
    def default_agent(self, name: str | None) -> None:
        """Set the default agent name."""
        if name is not None and not self._registry.exists(name):
            raise OrchestratorError(f"Default agent '{name}' not in registry")
        self._default_agent = name

    # =========================================================================
    # Core Operations
    # =========================================================================

    async def process(self, user_input: str) -> str:
        """
        Process user input, routing to appropriate agent.

        Routing logic:
        1. Check for explicit routing (@agent_name message)
        2. Use active agent if one exists
        3. Fall back to default agent
        4. Error if no agent available

        Args:
            user_input: Raw user input

        Returns:
            Agent response string

        Raises:
            OrchestratorError: If no agent is available
        """
        # Check for explicit routing (@agent_name message)
        match = self.ROUTING_PATTERN.match(user_input.strip())

        if match:
            agent_name = match.group(1).lower()
            message = match.group(2).strip()
            logger.debug(f"Explicit routing to @{agent_name}")
            return await self._route_to_agent(agent_name, message)

        # Use active agent or default
        if self._active_agent is None:
            if self._default_agent:
                logger.debug(f"No active agent, using default: {self._default_agent}")
                await self.switch_agent(self._default_agent)
            else:
                raise OrchestratorError(
                    "No active agent and no default configured. "
                    "Use @agent_name or call switch_agent() first."
                )

        # Process with active agent
        return await self._active_agent.run(user_input)

    async def switch_agent(self, name: str) -> None:
        """
        Switch to a different agent.

        The new agent becomes active and will handle subsequent messages.
        If the agent was previously used in this session, the cached
        instance is reused.

        Args:
            name: Agent name to switch to

        Raises:
            KeyError: If agent not found in registry
        """
        # Normalize name
        name = name.lower()

        # Already active?
        if name == self._active_agent_name:
            logger.debug(f"Agent '{name}' already active")
            return

        # Get or create agent
        if name in self._agent_cache:
            logger.debug(f"Using cached agent: {name}")
            agent = self._agent_cache[name]
        else:
            logger.debug(f"Creating new agent: {name}")
            agent = self._registry.create_agent(name)
            self._agent_cache[name] = agent

        # Update active agent
        self._active_agent = agent
        self._active_agent_name = name
        logger.info(f"Switched to agent: {name}")

    async def delegate(
        self,
        agent_name: str,
        task: str,
        return_to_current: bool = True,
    ) -> str:
        """
        Delegate a task to another agent.

        This allows one agent to request help from a specialist.
        After delegation, control can return to the original agent.

        Args:
            agent_name: Agent to delegate to
            task: Task description/message for the delegate
            return_to_current: If True, switch back to current agent after
                              delegation completes

        Returns:
            Delegated agent's response

        Example:
            # From within an agent's tool or logic:
            result = await orchestrator.delegate(
                "researcher",
                "Find the latest statistics on AI adoption",
                return_to_current=True
            )
        """
        previous_agent = self._active_agent_name
        logger.debug(f"Delegating to @{agent_name}: {task[:50]}...")

        # Route to delegate
        result = await self._route_to_agent(agent_name, task)

        # Return to previous agent if requested
        if return_to_current and previous_agent:
            await self.switch_agent(previous_agent)
            logger.debug(f"Returned to agent: {previous_agent}")

        return result

    # =========================================================================
    # Agent Information
    # =========================================================================

    def list_agents(self) -> list[str]:
        """
        List available agents.

        Returns:
            Sorted list of agent names from registry
        """
        return self._registry.list_agents()

    def get_agent_info(self, name: str) -> dict[str, Any] | None:
        """
        Get information about an agent.

        Args:
            name: Agent name

        Returns:
            Dict with agent info or None if not found:
            - name: Agent name
            - role: Human-readable role
            - goal: Agent's primary objective
            - capabilities: List of capability tags
            - tools: List of enabled tools
            - is_active: Whether this agent is currently active
        """
        profile = self._registry.get(name)
        if profile is None:
            return None

        return {
            "name": profile.name,
            "role": profile.role,
            "goal": profile.goal,
            "capabilities": profile.capabilities,
            "tools": profile.tools,
            "tool_autonomy": profile.tool_autonomy,
            "is_active": name == self._active_agent_name,
        }

    def get_status(self) -> dict[str, Any]:
        """
        Get orchestrator status.

        Returns:
            Dict with:
            - active_agent: Name of active agent (or None)
            - default_agent: Name of default agent (or None)
            - cached_agents: List of cached agent names
            - available_agents: List of all available agents
        """
        return {
            "active_agent": self._active_agent_name,
            "default_agent": self._default_agent,
            "cached_agents": list(self._agent_cache.keys()),
            "available_agents": self.list_agents(),
        }

    # =========================================================================
    # Session Management
    # =========================================================================

    def clear_cache(self) -> None:
        """
        Clear agent instance cache.

        This releases all cached agent instances. The active agent
        will also be cleared. Use this at session end or when memory
        needs to be reclaimed.
        """
        self._agent_cache.clear()
        self._active_agent = None
        self._active_agent_name = None
        logger.debug("Agent cache cleared")

    async def shutdown(self) -> None:
        """
        Gracefully shutdown the orchestrator.

        Clears cache and performs any cleanup needed.
        """
        # Future: Could add agent-level shutdown hooks here
        self.clear_cache()
        logger.info("Orchestrator shutdown complete")

    # =========================================================================
    # Internal
    # =========================================================================

    async def _route_to_agent(self, agent_name: str, message: str) -> str:
        """
        Route message to specific agent.

        Args:
            agent_name: Target agent name
            message: Message to process

        Returns:
            Agent response

        Raises:
            OrchestratorError: If agent not found
        """
        # Validate agent exists
        if not self._registry.exists(agent_name):
            available = ", ".join(self._registry.list_agents())
            raise OrchestratorError(
                f"Unknown agent: @{agent_name}. Available: {available}"
            )

        # Switch if needed
        if agent_name != self._active_agent_name:
            await self.switch_agent(agent_name)

        # Process with agent
        return await self._active_agent.run(message)

    def __repr__(self) -> str:
        """Debug representation."""
        return (
            f"AgentOrchestrator("
            f"active={self._active_agent_name}, "
            f"default={self._default_agent}, "
            f"cached={len(self._agent_cache)})"
        )
```

### 3.2 CLI Commands for Orchestration

**Location:** `tests/integration/memory/memory-chat-v2.py` (or appropriate CLI location)

Add commands for orchestration:

```python
"""CLI commands for agent orchestration."""

from friday_cli.commands import CommandRegistry, arg


def register_orchestration_commands(registry: CommandRegistry) -> None:
    """Register orchestration-related commands."""

    @registry.command("switch", aliases=["sw"], category="agents")
    async def cmd_switch(ctx, agent_name: str = None) -> str:
        """
        Switch to a different agent.

        Usage:
            /switch <agent_name>  - Switch to specified agent
            /switch               - Show current agent and available options
        """
        if not agent_name:
            status = ctx.orchestrator.get_status()
            current = status["active_agent"] or "none"
            available = ", ".join(status["available_agents"])
            return f"Current agent: {current}\nAvailable: {available}"

        try:
            await ctx.orchestrator.switch_agent(agent_name)
            info = ctx.orchestrator.get_agent_info(agent_name)
            return f"Switched to @{agent_name} ({info['role']})"
        except KeyError:
            available = ", ".join(ctx.orchestrator.list_agents())
            return f"Agent not found: {agent_name}\nAvailable: {available}"

    @registry.command("agents", aliases=["team"], category="agents")
    async def cmd_agents(ctx) -> str:
        """
        List available agents and their capabilities.

        Usage:
            /agents  - Show all available agents with details
        """
        lines = ["Available Agents:", ""]

        for name in ctx.orchestrator.list_agents():
            info = ctx.orchestrator.get_agent_info(name)
            active_marker = " (active)" if info["is_active"] else ""
            caps = ", ".join(info["capabilities"]) or "none"

            lines.append(f"  @{name}{active_marker}")
            lines.append(f"    Role: {info['role']}")
            lines.append(f"    Goal: {info['goal']}")
            lines.append(f"    Capabilities: {caps}")
            lines.append("")

        return "\n".join(lines)

    @registry.command("agent", category="agents")
    async def cmd_agent(ctx, agent_name: str = None) -> str:
        """
        Show detailed information about a specific agent.

        Usage:
            /agent <name>  - Show agent details
            /agent         - Show current agent details
        """
        name = agent_name or ctx.orchestrator.active_agent_name
        if not name:
            return "No agent specified and no active agent."

        info = ctx.orchestrator.get_agent_info(name)
        if not info:
            return f"Agent not found: {name}"

        lines = [
            f"Agent: @{info['name']}",
            f"Role: {info['role']}",
            f"Goal: {info['goal']}",
            f"",
            f"Capabilities: {', '.join(info['capabilities']) or 'none'}",
            f"Tools: {', '.join(info['tools']) or 'none'}",
            f"Tool Autonomy: {info['tool_autonomy']}",
            f"",
            f"Active: {'yes' if info['is_active'] else 'no'}",
        ]
        return "\n".join(lines)

    @registry.command("delegate", aliases=["ask"], category="agents")
    async def cmd_delegate(
        ctx,
        agent_name: str = None,
        task: str = None,
        extra_args: list = None,
    ) -> str:
        """
        Delegate a task to another agent.

        Usage:
            /delegate <agent> <task>  - Ask another agent for help

        Example:
            /delegate researcher Find the latest AI trends
        """
        if not agent_name or not task:
            # Combine extra_args into task if present
            if agent_name and extra_args:
                task = " ".join([agent_name] + extra_args)
                return (
                    "Usage: /delegate <agent_name> <task>\n"
                    "Example: /delegate researcher Find info about AI"
                )
            return (
                "Usage: /delegate <agent_name> <task>\n"
                "Example: /delegate researcher Find info about AI"
            )

        # Handle task that may have been split
        if extra_args:
            task = task + " " + " ".join(extra_args)

        try:
            result = await ctx.orchestrator.delegate(
                agent_name,
                task,
                return_to_current=True,
            )
            return f"[Response from @{agent_name}]\n\n{result}"
        except Exception as e:
            return f"Delegation failed: {e}"

    @registry.command("status", category="agents")
    async def cmd_status(ctx) -> str:
        """
        Show orchestrator status.

        Usage:
            /status  - Show current orchestration state
        """
        status = ctx.orchestrator.get_status()

        lines = [
            "Orchestrator Status:",
            f"  Active Agent: {status['active_agent'] or 'none'}",
            f"  Default Agent: {status['default_agent'] or 'none'}",
            f"  Cached Agents: {', '.join(status['cached_agents']) or 'none'}",
            f"  Available: {len(status['available_agents'])} agents",
        ]
        return "\n".join(lines)
```

### 3.3 Package Exports Update

**Location:** `packages/friday-agent/src/friday_agent/__init__.py`

```python
"""Friday Agent package."""

from friday_agent.profile import AgentProfile
from friday_agent.loader import AgentLoader, AgentConfigError
from friday_agent.registry import AgentRegistry, AgentRegistryError
from friday_agent.orchestrator import AgentOrchestrator, OrchestratorError
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
    # Orchestration
    "AgentOrchestrator",
    "OrchestratorError",
    # Agents
    "AgentBase",
    "CopilotAgent",
]
```

---

## 4. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `packages/friday-agent/src/friday_agent/orchestrator.py` | Create | AgentOrchestrator implementation |
| `packages/friday-agent/src/friday_agent/__init__.py` | Modify | Export AgentOrchestrator, OrchestratorError |
| `tests/integration/memory/memory-chat-v2.py` | Modify | Add /switch, /agents, /delegate, /status commands |
| `packages/friday-agent/tests/test_orchestrator.py` | Create | Unit tests |

---

## 5. Dependencies

### 5.1 Internal Dependencies
- `AgentRegistry` from agent-registry-build-plan
- `AgentBase` and `CopilotAgent` from friday-agent package

### 5.2 No New External Dependencies

---

## 6. Verification

### 6.1 Unit Tests

**Location:** `packages/friday-agent/tests/test_orchestrator.py`

```python
"""Unit tests for AgentOrchestrator."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from friday_agent import (
    AgentProfile,
    AgentRegistry,
    AgentOrchestrator,
    OrchestratorError,
)


class TestAgentOrchestrator:
    """Test AgentOrchestrator functionality."""

    @pytest.fixture
    def mock_registry(self):
        """Create mock registry with test agents."""
        registry = MagicMock(spec=AgentRegistry)

        # Configure test profiles
        profiles = {
            "researcher": AgentProfile(
                name="researcher",
                role="Research Analyst",
                goal="Find information",
                system_prompt_template="You research.",
                _capabilities=["research"],
            ),
            "coder": AgentProfile(
                name="coder",
                role="Developer",
                goal="Write code",
                system_prompt_template="You code.",
                _capabilities=["coding"],
            ),
        }

        registry.exists.side_effect = lambda n: n in profiles
        registry.get.side_effect = lambda n: profiles.get(n)
        registry.list_agents.return_value = list(profiles.keys())

        # Mock agent creation
        def create_agent(name):
            agent = AsyncMock()
            agent.run = AsyncMock(return_value=f"Response from {name}")
            return agent

        registry.create_agent.side_effect = create_agent

        return registry

    @pytest.fixture
    def orchestrator(self, mock_registry):
        """Create orchestrator with mock registry."""
        return AgentOrchestrator(mock_registry, default_agent="researcher")

    @pytest.mark.asyncio
    async def test_process_with_explicit_routing(self, orchestrator):
        """Test @agent_name routing."""
        response = await orchestrator.process("@coder Write a function")
        assert "Response from coder" in response
        assert orchestrator.active_agent_name == "coder"

    @pytest.mark.asyncio
    async def test_process_with_default_agent(self, orchestrator):
        """Test routing to default agent."""
        response = await orchestrator.process("Find information")
        assert "Response from researcher" in response
        assert orchestrator.active_agent_name == "researcher"

    @pytest.mark.asyncio
    async def test_process_no_agent_raises(self, mock_registry):
        """Test error when no agent available."""
        orchestrator = AgentOrchestrator(mock_registry, default_agent=None)
        with pytest.raises(OrchestratorError, match="No active agent"):
            await orchestrator.process("Hello")

    @pytest.mark.asyncio
    async def test_switch_agent(self, orchestrator):
        """Test switching agents."""
        await orchestrator.switch_agent("coder")
        assert orchestrator.active_agent_name == "coder"

        await orchestrator.switch_agent("researcher")
        assert orchestrator.active_agent_name == "researcher"

    @pytest.mark.asyncio
    async def test_switch_to_same_agent_noop(self, orchestrator):
        """Test switching to same agent is no-op."""
        await orchestrator.switch_agent("researcher")
        agent1 = orchestrator.active_agent

        await orchestrator.switch_agent("researcher")
        agent2 = orchestrator.active_agent

        assert agent1 is agent2  # Same instance

    @pytest.mark.asyncio
    async def test_agent_caching(self, orchestrator):
        """Test agents are cached."""
        await orchestrator.switch_agent("coder")
        agent1 = orchestrator.active_agent

        await orchestrator.switch_agent("researcher")
        await orchestrator.switch_agent("coder")
        agent2 = orchestrator.active_agent

        assert agent1 is agent2  # Cached instance

    @pytest.mark.asyncio
    async def test_delegate(self, orchestrator):
        """Test delegation to another agent."""
        await orchestrator.switch_agent("coder")
        result = await orchestrator.delegate(
            "researcher",
            "Find AI statistics",
            return_to_current=True,
        )

        assert "Response from researcher" in result
        # Should return to coder
        assert orchestrator.active_agent_name == "coder"

    @pytest.mark.asyncio
    async def test_delegate_no_return(self, orchestrator):
        """Test delegation without returning."""
        await orchestrator.switch_agent("coder")
        await orchestrator.delegate(
            "researcher",
            "Find info",
            return_to_current=False,
        )

        # Should stay on researcher
        assert orchestrator.active_agent_name == "researcher"

    @pytest.mark.asyncio
    async def test_unknown_agent_error(self, orchestrator):
        """Test routing to unknown agent."""
        with pytest.raises(OrchestratorError, match="Unknown agent"):
            await orchestrator.process("@unknown Do something")

    def test_list_agents(self, orchestrator):
        """Test listing agents."""
        agents = orchestrator.list_agents()
        assert "researcher" in agents
        assert "coder" in agents

    def test_get_agent_info(self, orchestrator):
        """Test getting agent info."""
        info = orchestrator.get_agent_info("researcher")
        assert info["name"] == "researcher"
        assert info["role"] == "Research Analyst"
        assert "research" in info["capabilities"]

    def test_get_status(self, orchestrator):
        """Test getting orchestrator status."""
        status = orchestrator.get_status()
        assert status["default_agent"] == "researcher"
        assert "researcher" in status["available_agents"]

    def test_clear_cache(self, orchestrator):
        """Test clearing cache."""
        orchestrator._agent_cache["test"] = MagicMock()
        orchestrator.clear_cache()

        assert len(orchestrator._agent_cache) == 0
        assert orchestrator.active_agent is None
```

### 6.2 Integration Test

```python
# Test with real agents
from friday_cli.container import FridayContainer, FridayConfig
from friday_agent import AgentOrchestrator

# Setup
config = FridayConfig()
container = FridayContainer(config)

# Create orchestrator
orchestrator = AgentOrchestrator(
    registry=container.agent_registry,
    default_agent="researcher",
)

# Test explicit routing
response = await orchestrator.process("@researcher Find info about Python")
print(f"Researcher: {response[:100]}...")

# Test switch
await orchestrator.switch_agent("coder")
response = await orchestrator.process("Write a hello world function")
print(f"Coder: {response[:100]}...")

# Test delegation
response = await orchestrator.delegate(
    "researcher",
    "What are the best practices for Python functions?",
)
print(f"Delegated: {response[:100]}...")

# Status
print(orchestrator.get_status())
```

### 6.3 CLI Test

```bash
# Start memory-chat-v2
python tests/integration/memory/memory-chat-v2.py

# Test commands
/agents                          # List all agents
/switch researcher               # Switch to researcher
/agent                           # Show current agent details
@coder Write a function          # Explicit routing
/delegate researcher Find X      # Delegation
/status                          # Show orchestrator status
```

---

## 7. Exit Criteria

1. `AgentOrchestrator` routes explicit `@agent_name` messages correctly
2. Default agent is used when no explicit routing
3. Agent switching works and preserves context
4. Delegation returns result and optionally switches back
5. CLI commands (`/switch`, `/agents`, `/delegate`, `/status`) work
6. Error messages are clear when agent not found
7. Agent instances are cached for session duration
8. Unit tests achieve 90%+ coverage
