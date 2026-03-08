# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
import warnings
from unittest.mock import MagicMock

from friday_agent import (
    AgentBase,
    AgentProfile,
    CopilotAgent,
    InteractiveAgent,
    ReplAgentBase,
)


def _profile() -> AgentProfile:
    return AgentProfile(
        name="assistant",
        role="Assistant",
        goal="Help the user",
        system_prompt_template="You are {name}, a {role}.",
    )


def test_interactive_agent_hierarchy():
    agent = InteractiveAgent(
        profile=_profile(),
        memory=MagicMock(),
        context_engine=MagicMock(),
        llm=MagicMock(),
        tool_registry=MagicMock(),
    )

    assert isinstance(agent, InteractiveAgent)
    assert isinstance(agent, ReplAgentBase)
    assert isinstance(agent, AgentBase)


def test_copilot_agent_is_compatibility_alias():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        agent = CopilotAgent(
            profile=_profile(),
            memory=MagicMock(),
            context_engine=MagicMock(),
            llm=MagicMock(),
            tool_registry=MagicMock(),
        )

    assert isinstance(agent, CopilotAgent)
    assert isinstance(agent, InteractiveAgent)
    assert isinstance(agent, ReplAgentBase)
    assert any("interactiveagent" in str(w.message).lower() for w in caught)
