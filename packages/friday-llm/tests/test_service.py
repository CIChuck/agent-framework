"""
Tests for LiteLLM Service.

Tests chat completion functionality with mocked LiteLLM responses.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from friday_llm import LiteLLMService
from friday_core.telemetry import DebugTelemetryRecorder


class MockChoice:
    """Mock LiteLLM response choice."""

    def __init__(self, content: str = None, tool_calls: list = None):
        self.message = MagicMock()
        self.message.content = content
        self.message.tool_calls = tool_calls or []


class MockResponse:
    """Mock LiteLLM response."""

    def __init__(self, content: str = None, tool_calls: list = None):
        self.choices = [MockChoice(content, tool_calls)]
        self.model = "gpt-4"
        self.usage = MagicMock()
        self.usage.prompt_tokens = 10
        self.usage.completion_tokens = 20
        self.usage.total_tokens = 30


class MockToolCall:
    """Mock tool call from LiteLLM."""

    def __init__(self, id: str, name: str, arguments: str):
        self.id = id
        self.function = MagicMock()
        self.function.name = name
        self.function.arguments = arguments


@pytest.fixture
def service():
    """Create LiteLLM service instance."""
    return LiteLLMService(
        model_name="gpt-4",
        api_key="test-key",
    )


@pytest.fixture
def service_with_telemetry():
    """Create LiteLLM service with telemetry."""
    recorder = DebugTelemetryRecorder()
    return LiteLLMService(
        model_name="gpt-4",
        api_key="test-key",
        telemetry=recorder,
    ), recorder


class TestLiteLLMService:
    """Tests for LiteLLMService."""

    @pytest.mark.asyncio
    async def test_basic_chat_completion(self, service):
        """Test basic chat completion without tools."""
        mock_response = MockResponse(content="Hello! How can I help?")

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_response

            response = await service.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert response.content == "Hello! How can I help?"
            assert not response.has_tool_calls
            assert response.model == "gpt-4"
            mock_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_completion_with_tool_calls(self, service):
        """Test chat completion that returns tool calls."""
        tool_call = MockToolCall(
            id="call_123",
            name="search_web",
            arguments='{"query": "python tutorials"}',
        )
        mock_response = MockResponse(tool_calls=[tool_call])

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_response

            response = await service.chat_completion(
                messages=[{"role": "user", "content": "Search for python tutorials"}],
                tools=[{"type": "function", "function": {"name": "search_web"}}],
            )

            assert response.has_tool_calls
            assert len(response.tool_calls) == 1
            assert response.tool_calls[0].name == "search_web"
            assert response.tool_calls[0].arguments == {"query": "python tutorials"}

    @pytest.mark.asyncio
    async def test_telemetry_events(self, service_with_telemetry):
        """Test that telemetry events are emitted."""
        service, recorder = service_with_telemetry
        mock_response = MockResponse(content="Test response")

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_response

            await service.chat_completion(
                messages=[{"role": "user", "content": "Test"}],
            )

            assert "llm_completion_success" in recorder.event_names

    @pytest.mark.asyncio
    async def test_usage_tracking(self, service):
        """Test that token usage is tracked."""
        mock_response = MockResponse(content="Response")

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_response

            response = await service.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert response.usage.get("prompt_tokens") == 10
            assert response.usage.get("completion_tokens") == 20
            assert response.usage.get("total_tokens") == 30

    @pytest.mark.asyncio
    async def test_invalid_json_arguments(self, service):
        """Test handling of invalid JSON in tool arguments."""
        tool_call = MockToolCall(
            id="call_123",
            name="some_tool",
            arguments="not valid json",
        )
        mock_response = MockResponse(tool_calls=[tool_call])

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_response

            response = await service.chat_completion(
                messages=[{"role": "user", "content": "Test"}],
                tools=[{"type": "function", "function": {"name": "some_tool"}}],
            )

            # Should store raw arguments in a dict
            assert response.tool_calls[0].arguments == {"raw": "not valid json"}
