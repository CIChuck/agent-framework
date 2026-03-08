# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""
Tests for AgentOrchestrator.

Tests cover:
- Explicit routing (@agent_name messages)
- Default agent fallback
- No agent error handling
- Agent switching
- Agent caching
- Delegation with return
- Delegation without return
- Unknown agent error
- Status and listing
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from friday_agent import (
    AgentOrchestrator,
    AgentProfile,
    AgentRegistry,
    OrchestratorError,
)


@pytest.fixture
def mock_agent():
    """Create a mock agent."""
    agent = AsyncMock()
    agent.run = AsyncMock(return_value="Agent response")
    agent.initialize_session = AsyncMock()
    return agent


@pytest.fixture
def sample_profile():
    """Create a sample agent profile."""
    return AgentProfile(
        name="researcher",
        role="Research Assistant",
        goal="Find and analyze information",
        system_prompt_template="You are {name}, a {role}.",
        tools=["search", "read"],
        _capabilities=["research", "analysis"],
    )


@pytest.fixture
def second_profile():
    """Create a second agent profile."""
    return AgentProfile(
        name="coder",
        role="Code Assistant",
        goal="Write and review code",
        system_prompt_template="You are {name}, a {role}.",
        tools=["write_file", "execute"],
        _capabilities=["coding", "review"],
    )


@pytest.fixture
def mock_registry(sample_profile, second_profile, mock_agent):
    """Create a mock registry with factory configured."""
    registry = MagicMock(spec=AgentRegistry)
    registry.has_factory.return_value = True
    registry.list_agents.return_value = ["researcher", "coder"]
    registry.exists.side_effect = lambda name: name in ["researcher", "coder"]
    registry.get.side_effect = lambda name: {
        "researcher": sample_profile,
        "coder": second_profile,
    }.get(name)
    registry.get_or_raise.side_effect = lambda name: {
        "researcher": sample_profile,
        "coder": second_profile,
    }[name]
    registry.resolve_agent_for_skill.side_effect = (
        lambda skill_ref, preferred_agent=None: (
            preferred_agent if preferred_agent in ["researcher", "coder"] else "coder"
        )
    )

    # Mock create_agent to raise KeyError for unknown agents
    def create_agent_mock(name):
        if name not in ["researcher", "coder"]:
            raise KeyError(f"Agent '{name}' not found")
        return mock_agent

    registry.create_agent.side_effect = create_agent_mock
    return registry


@pytest.fixture
def orchestrator(mock_registry):
    """Create an orchestrator with mock registry."""
    return AgentOrchestrator(
        registry=mock_registry,
        default_agent="researcher",
    )


class TestOrchestratorInitialization:
    """Tests for orchestrator initialization."""

    def test_init_with_factory(self, mock_registry):
        """Test initialization with properly configured registry."""
        orchestrator = AgentOrchestrator(
            registry=mock_registry,
            default_agent="researcher",
        )
        assert orchestrator.default_agent_name == "researcher"
        assert orchestrator.active_agent_name is None
        assert orchestrator.message_count == 0

    def test_init_without_factory_raises(self):
        """Test that init without factory raises error."""
        registry = MagicMock(spec=AgentRegistry)
        registry.has_factory.return_value = False

        with pytest.raises(OrchestratorError, match="must have a factory"):
            AgentOrchestrator(registry=registry)

    def test_init_without_default_agent(self, mock_registry):
        """Test initialization without default agent."""
        orchestrator = AgentOrchestrator(
            registry=mock_registry,
            default_agent=None,
        )
        assert orchestrator.default_agent_name is None


class TestExplicitRouting:
    """Tests for explicit @agent_name routing."""

    @pytest.mark.asyncio
    async def test_explicit_routing(self, orchestrator, mock_agent):
        """Test routing with @agent_name prefix."""
        response = await orchestrator.process(
            "@researcher Find information about memory"
        )

        # Should create agent and process message
        assert response == "Agent response"
        mock_agent.run.assert_called_once_with("Find information about memory")

    @pytest.mark.asyncio
    async def test_explicit_routing_unknown_agent(self, orchestrator):
        """Test routing to unknown agent raises error."""
        with pytest.raises(OrchestratorError, match="not found"):
            await orchestrator.process("@unknown_agent Do something")

    @pytest.mark.asyncio
    async def test_routing_pattern_case_insensitive(self, orchestrator, mock_agent):
        """Test that agent name in routing is case-insensitive."""
        response = await orchestrator.process("@RESEARCHER Find info")

        # Should normalize to lowercase
        assert response == "Agent response"
        mock_agent.run.assert_called_once()


class TestDefaultAgentFallback:
    """Tests for default agent fallback."""

    @pytest.mark.asyncio
    async def test_fallback_to_default_agent(self, orchestrator, mock_agent):
        """Test fallback to default agent when no routing specified."""
        response = await orchestrator.process("What is the weather?")

        assert response == "Agent response"
        mock_agent.run.assert_called_once_with("What is the weather?")

    @pytest.mark.asyncio
    async def test_no_default_agent_raises(self, mock_registry):
        """Test error when no default agent and no active agent."""
        orchestrator = AgentOrchestrator(
            registry=mock_registry,
            default_agent=None,
            auto_initialize=False,
        )

        with pytest.raises(OrchestratorError, match="No agent available"):
            await orchestrator.process("Hello")


class TestAgentSwitching:
    """Tests for agent switching."""

    @pytest.mark.asyncio
    async def test_switch_agent(self, orchestrator):
        """Test switching to a different agent."""
        await orchestrator.switch_agent("coder")

        assert orchestrator.active_agent_name == "coder"

    @pytest.mark.asyncio
    async def test_switch_to_unknown_agent(self, orchestrator):
        """Test switching to unknown agent raises error."""
        with pytest.raises(OrchestratorError, match="not found"):
            await orchestrator.switch_agent("unknown")

    @pytest.mark.asyncio
    async def test_switch_preserves_previous_in_cache(
        self, orchestrator, mock_registry, mock_agent
    ):
        """Test that switching preserves previous agent in cache."""
        # First use researcher
        await orchestrator.process("Hello")
        assert "researcher" in orchestrator.list_cached_agents()

        # Switch to coder
        await orchestrator.switch_agent("coder")
        assert "researcher" in orchestrator.list_cached_agents()
        assert "coder" in orchestrator.list_cached_agents()


class TestAgentCaching:
    """Tests for agent caching."""

    @pytest.mark.asyncio
    async def test_agent_cached_after_use(self, orchestrator, mock_registry):
        """Test that agent is cached after first use."""
        await orchestrator.process("Hello")

        assert "researcher" in orchestrator.list_cached_agents()
        # Should have been created once
        mock_registry.create_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_cached_agent_reused(self, orchestrator, mock_registry):
        """Test that cached agent is reused."""
        await orchestrator.process("First message")
        await orchestrator.process("Second message")

        # Should still have been created only once
        mock_registry.create_agent.assert_called_once()

    def test_clear_cache(self, orchestrator):
        """Test clearing the agent cache."""
        # Manually populate cache for testing
        orchestrator._agent_cache["test"] = MagicMock()
        orchestrator._active_agent = MagicMock()
        orchestrator._active_agent_name = "test"

        count = orchestrator.clear_cache()

        assert count == 1
        assert orchestrator._agent_cache == {}
        assert orchestrator.active_agent is None
        assert orchestrator.active_agent_name is None


class TestDelegation:
    """Tests for task delegation."""

    @pytest.mark.asyncio
    async def test_delegate_to_agent(self, orchestrator, mock_agent):
        """Test delegating a task to another agent."""
        # First activate an agent
        await orchestrator.switch_agent("researcher")

        # Delegate to coder
        response = await orchestrator.delegate("coder", "Review this code")

        assert response == "Agent response"
        mock_agent.run.assert_called_with("Review this code")

    @pytest.mark.asyncio
    async def test_delegate_with_return(self, orchestrator, mock_agent):
        """Test delegation with return to original agent."""
        # First activate researcher
        await orchestrator.switch_agent("researcher")

        # Delegate to coder with return
        await orchestrator.delegate("coder", "Task", return_to_current=True)

        # Should return to researcher
        assert orchestrator.active_agent_name == "researcher"

    @pytest.mark.asyncio
    async def test_delegate_without_return(self, orchestrator, mock_agent):
        """Test delegation without returning to original."""
        # First activate researcher
        await orchestrator.switch_agent("researcher")

        # Delegate to coder without return
        await orchestrator.delegate("coder", "Task", return_to_current=False)

        # Should stay on coder
        assert orchestrator.active_agent_name == "coder"

    @pytest.mark.asyncio
    async def test_delegate_to_unknown_agent(self, orchestrator):
        """Test delegation to unknown agent raises error."""
        with pytest.raises(OrchestratorError, match="not found"):
            await orchestrator.delegate("unknown", "Task")

    @pytest.mark.asyncio
    async def test_delegate_validates_handoff_payload(self, orchestrator):
        """Test invalid handoff payload is rejected before execution."""
        await orchestrator.switch_agent("researcher")

        with pytest.raises(OrchestratorError, match="missing required fields"):
            await orchestrator.delegate(
                "coder",
                "Task",
                handoff_payload={"handoff_id": "h1"},
            )

    @pytest.mark.asyncio
    async def test_delegate_records_handoff_payload(self, orchestrator):
        """Test valid handoff payload is normalized and recorded."""
        await orchestrator.switch_agent("researcher")

        await orchestrator.delegate(
            "coder",
            "Task",
            handoff_payload={
                "handoff_id": "handoff_1",
                "ownership": "coder",
                "acceptance_criteria": ["return summary", "include sources"],
                "memory_scope": "private_plus_shared",
            },
        )

        history = orchestrator.get_delegation_history()
        assert len(history) == 1
        assert history[0]["handoff"]["handoff_id"] == "handoff_1"
        assert history[0]["handoff"]["target_agent"] == "coder"

    @pytest.mark.asyncio
    async def test_delegate_resolves_agent_from_skill_reference(
        self, orchestrator, mock_registry
    ):
        """Test skill-ref delegation resolution uses registry skill routing."""
        await orchestrator.switch_agent("researcher")

        await orchestrator.delegate(
            "researcher",
            "Skill-routed task",
            skill_ref="planner.basic@1.0.0",
        )

        mock_registry.resolve_agent_for_skill.assert_called_once_with(
            "planner.basic@1.0.0",
            preferred_agent="researcher",
        )
        history = orchestrator.get_delegation_history()
        assert history[0]["skill_ref"] == "planner.basic@1.0.0"


class TestStatusAndListing:
    """Tests for status and listing methods."""

    def test_list_agents(self, orchestrator, mock_registry):
        """Test listing available agents."""
        agents = orchestrator.list_agents()

        assert agents == ["researcher", "coder"]
        mock_registry.list_agents.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_cached_agents(self, orchestrator):
        """Test listing cached agents."""
        await orchestrator.process("Hello")

        cached = orchestrator.list_cached_agents()
        assert "researcher" in cached

    def test_get_agent_info(self, orchestrator, mock_registry, sample_profile):
        """Test getting agent information."""
        info = orchestrator.get_agent_info("researcher")

        assert info["name"] == "researcher"
        assert info["role"] == "Research Assistant"
        assert info["capabilities"] == ["research", "analysis"]
        assert info["is_active"] is False  # Not yet activated

    def test_get_status(self, orchestrator):
        """Test getting orchestrator status."""
        status = orchestrator.get_status()

        assert status["active_agent"] is None
        assert status["default_agent"] == "researcher"
        assert status["cached_agents"] == []
        assert "researcher" in status["registered_agents"]
        assert status["message_count"] == 0


class TestSessionManagement:
    """Tests for session management."""

    @pytest.mark.asyncio
    async def test_set_session(self, orchestrator, mock_agent):
        """Test setting session context."""
        # First process a message to cache the agent
        await orchestrator.process("Hello")

        # Set new session
        await orchestrator.set_session("new_session", "user_123")

        assert orchestrator.session_id == "new_session"
        # Agent should be re-initialized
        mock_agent.initialize_session.assert_called()

    @pytest.mark.asyncio
    async def test_shutdown(self, orchestrator):
        """Test orchestrator shutdown."""
        # Process some messages
        await orchestrator.process("Hello")
        assert orchestrator.message_count == 1

        # Shutdown
        await orchestrator.shutdown()

        assert orchestrator._agent_cache == {}
        assert orchestrator.message_count == 0
        assert orchestrator.session_id is None


class TestRoutingParser:
    """Tests for the routing pattern parser."""

    def test_parse_valid_routing(self, orchestrator):
        """Test parsing valid @mention routing."""
        agent, message = orchestrator._parse_routing("@researcher Find info")

        assert agent == "researcher"
        assert message == "Find info"

    def test_parse_no_routing(self, orchestrator):
        """Test parsing message without routing."""
        agent, message = orchestrator._parse_routing("Regular message")

        assert agent is None
        assert message == "Regular message"

    def test_parse_multiline_message(self, orchestrator):
        """Test parsing multiline message after @mention."""
        agent, message = orchestrator._parse_routing("@coder Write code\nfor this task")

        assert agent == "coder"
        assert message == "Write code\nfor this task"

    def test_parse_at_symbol_in_message(self, orchestrator):
        """Test that @ in middle of message doesn't trigger routing."""
        agent, message = orchestrator._parse_routing("Email user@example.com")

        assert agent is None
        assert message == "Email user@example.com"


class TestRouteStage:
    """Tests for route-stage decomposition."""

    def test_route_explicit_target(self, orchestrator):
        """Test explicit route returns correct decision."""
        decision = orchestrator.route("@researcher Find info")
        assert decision.target_agent == "researcher"
        assert decision.message == "Find info"
        assert decision.source == "explicit"

    @pytest.mark.asyncio
    async def test_route_active_target(self, orchestrator):
        """Test active agent route path."""
        await orchestrator.switch_agent("coder")
        decision = orchestrator.route("Continue work")
        assert decision.target_agent == "coder"
        assert decision.message == "Continue work"
        assert decision.source == "active"

    def test_route_default_target(self, orchestrator):
        """Test default route path when no active agent."""
        decision = orchestrator.route("Do the thing")
        assert decision.target_agent == "researcher"
        assert decision.message == "Do the thing"
        assert decision.source == "default"


class TestMessageTracking:
    """Tests for message count tracking."""

    @pytest.mark.asyncio
    async def test_message_count_increments(self, orchestrator):
        """Test that message count increments with each process call."""
        assert orchestrator.message_count == 0

        await orchestrator.process("First")
        assert orchestrator.message_count == 1

        await orchestrator.process("Second")
        assert orchestrator.message_count == 2

    @pytest.mark.asyncio
    async def test_delegation_increments_count(self, orchestrator):
        """Test that delegation also increments message count."""
        await orchestrator.switch_agent("researcher")
        await orchestrator.delegate("coder", "Task")

        assert orchestrator.message_count == 1


class TestRepr:
    """Tests for string representation."""

    @pytest.mark.asyncio
    async def test_repr(self, orchestrator):
        """Test repr method."""
        await orchestrator.process("Hello")

        repr_str = repr(orchestrator)
        assert "active=researcher" in repr_str
        assert "cached=1" in repr_str
        assert "messages=1" in repr_str
