# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
from friday_agent import AgentProfile
from friday_agent.prompting import compose_system_prompt


def _profile() -> AgentProfile:
    return AgentProfile(
        name="memory_probe",
        role="technical validation agent",
        goal="Validate transcript capture",
        system_prompt_template="You are {name}. Role: {role}. Goal: {goal}.",
    )


def test_compose_system_prompt_without_runtime_base_prompt():
    composition = compose_system_prompt(_profile())

    assert composition.runtime_base_prompt is None
    assert (
        composition.agent_prompt
        == "You are memory_probe. Role: technical validation agent. Goal: Validate transcript capture."
    )
    assert composition.composed_system_prompt == composition.agent_prompt


def test_compose_system_prompt_with_runtime_base_prompt():
    composition = compose_system_prompt(
        _profile(),
        runtime_base_prompt="Runtime base prompt",
    )

    assert composition.runtime_base_prompt == "Runtime base prompt"
    assert "Runtime base prompt" in composition.composed_system_prompt
    assert composition.agent_prompt in composition.composed_system_prompt
