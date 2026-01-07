"""
Tests for PromptArchitect (Layout Engine).

Tests cover:
- Token counting
- Prompt formatting with layout blocks
- Dynamic budget calculation
"""

import pytest

from friday_memory import ContextPayload, PromptArchitect, SessionState
from datetime import datetime


@pytest.fixture
def architect() -> PromptArchitect:
    """Create a PromptArchitect instance."""
    return PromptArchitect(
        model_name="gpt-4",
        max_tokens=8192,
        output_buffer=1024,
    )


@pytest.fixture
def empty_payload() -> ContextPayload:
    """Create an empty context payload."""
    return ContextPayload(
        history=[],
        passages=[],
        entities=[],
        facts=[],
        recent_memories=[],
        debug_info={},
    )


class TestTokenCounting:
    """Tests for token counting functionality."""

    def test_count_tokens_simple(self, architect: PromptArchitect):
        """Test counting tokens in simple text."""
        text = "Hello, world!"
        tokens = architect.count_tokens(text)
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_count_tokens_empty(self, architect: PromptArchitect):
        """Test counting tokens in empty string."""
        tokens = architect.count_tokens("")
        assert tokens == 0

    def test_count_tokens_long_text(self, architect: PromptArchitect):
        """Test counting tokens in longer text."""
        text = "This is a longer piece of text. " * 100
        tokens = architect.count_tokens(text)
        assert tokens > 100  # Should be many tokens


class TestBudgetCalculation:
    """Tests for context budget calculations."""

    def test_calculate_fixed_costs_basic(self, architect: PromptArchitect):
        """Test calculating fixed costs with just system prompt."""
        system_prompt = "You are a helpful assistant."
        fixed = architect.calculate_fixed_costs(system_prompt)

        # Should include prompt tokens + output buffer
        assert fixed > architect.output_buffer

    def test_calculate_fixed_costs_with_tools(self, architect: PromptArchitect):
        """Test calculating fixed costs with tool definitions."""
        system_prompt = "You are a helpful assistant."
        tools = [
            {"name": "search", "description": "Search for information"},
            {"name": "calculate", "description": "Perform calculations"},
        ]

        fixed_without = architect.calculate_fixed_costs(system_prompt)
        fixed_with = architect.calculate_fixed_costs(system_prompt, tools)

        # With tools should be higher
        assert fixed_with > fixed_without

    def test_calculate_dynamic_limit(self, architect: PromptArchitect):
        """Test calculating available dynamic budget."""
        system_prompt = "You are a helpful assistant."
        dynamic = architect.calculate_dynamic_limit(system_prompt)

        # Should be less than max tokens
        assert dynamic < architect.max_tokens
        assert dynamic > 0


class TestPromptFormatting:
    """Tests for prompt formatting."""

    def test_format_prompt_basic(
        self, architect: PromptArchitect, empty_payload: ContextPayload
    ):
        """Test basic prompt formatting."""
        messages = architect.format_prompt(
            system_prompt="You are a helpful assistant.",
            user_query="Hello!",
            payload=empty_payload,
        )

        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        # Speaker name prefix is added by PromptArchitect (default: "User")
        assert messages[-1]["content"] == "[User]: Hello!"

    def test_format_prompt_with_transparency_block(self, architect: PromptArchitect):
        """Test formatting with recent memories (transparency block)."""
        payload = ContextPayload(
            history=[],
            passages=[],
            entities=[],
            facts=[],
            recent_memories=["User prefers dark mode", "User works with Python"],
            debug_info={},
        )

        messages = architect.format_prompt(
            system_prompt="You are a helpful assistant.",
            user_query="What do you know about me?",
            payload=payload,
        )

        system_content = messages[0]["content"]
        assert "Recent Memories" in system_content
        assert "dark mode" in system_content

    def test_format_prompt_with_passages(self, architect: PromptArchitect):
        """Test formatting with semantic memory passages."""
        payload = ContextPayload(
            history=[],
            passages=[
                {"text": "Python is a programming language.", "similarity": 0.95, "metadata": {"source_name": "docs"}},
                {"text": "Python was created by Guido.", "similarity": 0.85, "metadata": {"source_name": "wiki"}},
            ],
            entities=[],
            facts=[],
            recent_memories=[],
            debug_info={},
        )

        messages = architect.format_prompt(
            system_prompt="You are a helpful assistant.",
            user_query="Tell me about Python",
            payload=payload,
        )

        system_content = messages[0]["content"]
        assert "Relevant Documentation" in system_content
        assert "Python is a programming language" in system_content

    def test_format_prompt_with_session_state(self, architect: PromptArchitect):
        """Test formatting with session state variables."""
        payload = ContextPayload(
            history=[],
            passages=[],
            entities=[],
            facts=[],
            recent_memories=[],
            debug_info={},
        )
        state = SessionState(
            session_id="test",
            user_id="user1",
            turn_count=5,
            start_time=datetime.now(),
            active_goals=[],
            scoped_vars={
                "user:theme": "dark",
                "user:language": "python",
                "session:step": "debugging",
                "app:version": "1.0",
            },
        )

        messages = architect.format_prompt(
            system_prompt="You are a helpful assistant.",
            user_query="What are my preferences?",
            payload=payload,
            state=state,
        )

        system_content = messages[0]["content"]
        assert "Session Context" in system_content
        assert "User Preferences" in system_content
        assert "dark" in system_content
