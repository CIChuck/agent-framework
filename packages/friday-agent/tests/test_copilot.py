"""
Tests for CopilotAgent.

Tests the Re-Act loop and tool execution with mocked dependencies.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass

from friday_agent import AgentProfile, CopilotAgent, DefaultToolRegistry
from friday_core.interfaces import ChatCompletionResponse, ToolCall
from friday_core.telemetry import DebugTelemetryRecorder
from friday_memory.models import SessionState, ContextPayload


@pytest.fixture
def profile():
    """Create a test agent profile."""
    return AgentProfile(
        name="TestAgent",
        role="Test Assistant",
        goal="Help with testing",
        system_prompt_template="You are {name}, a {role}. Goal: {goal}",
        tools=["echo"],
        temperature=0.7,
    )


@pytest.fixture
def mock_memory():
    """Create a mock memory controller."""
    mock = MagicMock()
    mock.add_turn = AsyncMock(return_value=True)
    mock.recall = AsyncMock(return_value=ContextPayload(
        history=[],
        passages=[],
        entities=[],
        facts=[],
        recent_memories=[],
        debug_info={},
    ))
    return mock


@pytest.fixture
def mock_context_engine():
    """Create a mock context engine."""
    mock = MagicMock()
    mock.initialize_session = AsyncMock(return_value=SessionState(
        session_id="test-session",
        user_id="test-user",
    ))
    mock.assemble_context = AsyncMock(return_value=ContextPayload(
        history=[],
        passages=[],
        entities=[],
        facts=[],
        recent_memories=[],
        debug_info={},
    ))
    mock.format_prompt = AsyncMock(return_value=[
        {"role": "system", "content": "You are a test assistant."},
    ])
    mock.extract_context = AsyncMock()
    return mock


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    mock = MagicMock()
    mock.chat_completion = AsyncMock(return_value=ChatCompletionResponse(
        content="Hello! I'm here to help.",
        tool_calls=[],
    ))
    return mock


@pytest.fixture
def tool_registry():
    """Create a tool registry with a test tool."""
    registry = DefaultToolRegistry()

    async def echo_tool(message: str) -> str:
        return f"Echo: {message}"

    registry.register(
        name="echo",
        func=echo_tool,
        description="Echo a message",
        parameters={
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"],
        },
    )
    return registry


@pytest.fixture
def agent(profile, mock_memory, mock_context_engine, mock_llm, tool_registry):
    """Create a fully mocked CopilotAgent."""
    return CopilotAgent(
        profile=profile,
        memory=mock_memory,
        context_engine=mock_context_engine,
        llm=mock_llm,
        tool_registry=tool_registry,
    )


class TestCopilotAgent:
    """Tests for CopilotAgent."""

    @pytest.mark.asyncio
    async def test_basic_run(self, agent, mock_llm):
        """Test basic agent run without tool calls."""
        response = await agent.run("Hello!")

        assert response == "Hello! I'm here to help."
        mock_llm.chat_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_initialization(self, agent, mock_context_engine):
        """Test that session is initialized on first run."""
        await agent.run("Test")

        mock_context_engine.initialize_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_assembly(self, agent, mock_context_engine):
        """Test that context is assembled for each query."""
        await agent.run("What's the weather?")

        mock_context_engine.assemble_context.assert_called_once()
        call_args = mock_context_engine.assemble_context.call_args
        assert call_args[1]["query"] == "What's the weather?"

    @pytest.mark.asyncio
    async def test_tool_execution(self, agent, mock_llm, tool_registry):
        """Test that tools are executed when LLM requests them."""
        # First call returns tool call, second returns final response
        mock_llm.chat_completion.side_effect = [
            ChatCompletionResponse(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        name="echo",
                        arguments={"message": "test"},
                    )
                ],
            ),
            ChatCompletionResponse(
                content="The echo returned: Echo: test",
                tool_calls=[],
            ),
        ]

        response = await agent.run("Echo something")

        assert mock_llm.chat_completion.call_count == 2
        assert "Echo: test" in response

    @pytest.mark.asyncio
    async def test_max_iterations(self, agent, mock_llm):
        """Test that max iterations prevents infinite loops."""
        # Always return tool calls
        mock_llm.chat_completion.return_value = ChatCompletionResponse(
            content=None,
            tool_calls=[
                ToolCall(
                    id="call_1",
                    name="echo",
                    arguments={"message": "loop"},
                )
            ],
        )

        with pytest.raises(RuntimeError, match="exceeded maximum iterations"):
            await agent.run("Loop forever")

    @pytest.mark.asyncio
    async def test_turn_archiving(self, agent, mock_memory):
        """Test that turns are archived after completion."""
        await agent.run("Archive this")

        # Check that add_turn was called
        mock_memory.add_turn.assert_called()

    @pytest.mark.asyncio
    async def test_telemetry_integration(
        self, profile, mock_memory, mock_context_engine, mock_llm, tool_registry
    ):
        """Test that telemetry events are emitted."""
        recorder = DebugTelemetryRecorder()
        agent = CopilotAgent(
            profile=profile,
            memory=mock_memory,
            context_engine=mock_context_engine,
            llm=mock_llm,
            tool_registry=tool_registry,
            telemetry=recorder,
        )

        await agent.run("Test telemetry")

        # Should have some events
        assert len(recorder.events) > 0

    @pytest.mark.asyncio
    async def test_conversation_history(self, agent):
        """Test that conversation history is maintained."""
        await agent.run("First message")

        assert len(agent._conversation_history) >= 2  # user + assistant

    @pytest.mark.asyncio
    async def test_clear_history(self, agent):
        """Test clearing conversation history."""
        await agent.run("Message 1")
        agent.clear_history()

        assert len(agent._conversation_history) == 0


class TestAgentProfile:
    """Tests for AgentProfile."""

    def test_render_system_prompt(self, profile):
        """Test system prompt rendering."""
        prompt = profile.render_system_prompt()

        assert "TestAgent" in prompt
        assert "Test Assistant" in prompt
        assert "Help with testing" in prompt

    def test_render_with_extra_vars(self, profile):
        """Test system prompt rendering with extra variables."""
        profile.system_prompt_template = "Hello {name}, today is {date}"
        prompt = profile.render_system_prompt(date="Monday")

        assert "TestAgent" in prompt
        assert "Monday" in prompt

    def test_to_dict(self, profile):
        """Test profile serialization."""
        data = profile.to_dict()

        assert data["name"] == "TestAgent"
        assert data["role"] == "Test Assistant"
        assert data["tools"] == ["echo"]

    def test_from_dict(self):
        """Test profile deserialization."""
        data = {
            "name": "FromDict",
            "role": "Test",
            "goal": "Testing",
            "system_prompt_template": "You are {name}",
            "tools": ["tool1", "tool2"],
        }

        profile = AgentProfile.from_dict(data)

        assert profile.name == "FromDict"
        assert profile.tools == ["tool1", "tool2"]
