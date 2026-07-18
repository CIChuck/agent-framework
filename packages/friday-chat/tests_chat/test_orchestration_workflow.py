"""Orchestration and workflow tests for FridayV2."""

from __future__ import annotations

from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import build_runtime


def _context() -> RegistryCommandContext:
    config = FridayChatConfig.model_validate(
        {"llm": {"model": "openai/test-chat-model"}}
    )
    registry = build_default_registry()
    return RegistryCommandContext(runtime=build_runtime(config), registry=registry)


async def test_at_agent_routing_success_and_unknown_agent() -> None:
    output = ListOutputSink()
    app = FridayChatApp(
        input_source=ListInputSource(
            ["@researcher summarize this", "@missing do work"]
        ),
        output_sink=output,
    )

    await app.run()

    assert output.values[0] == "researcher: summarize this"
    assert "Unknown agent: missing" in output.values[1]


async def test_switch_agents_agent_and_status_commands() -> None:
    registry = build_default_registry()
    context = _context()

    _, current = await registry.execute("/switch", context)
    _, switched = await registry.execute("/switch coder", context)
    _, agents = await registry.execute("/agents", context)
    _, agent = await registry.execute("/agent coder", context)
    _, status = await registry.execute("/status", context)

    assert current is not None and current.output == "Active agent: friday"
    assert switched is not None and switched.output == "Switched to agent: coder"
    assert agents is not None and "* coder" in agents.output
    assert agent is not None and agent.output == "coder (active): code, review"
    assert status is not None and "active_agent: coder" in status.output


async def test_delegate_restores_prior_active_agent_on_success_and_failure() -> None:
    registry = build_default_registry()
    context = _context()
    assert context.runtime is not None
    context.runtime.orchestrator.switch("coder")

    _, success = await registry.execute("/delegate researcher investigate", context)
    _, failure = await registry.execute("/delegate missing investigate", context)

    assert success is not None
    assert "Delegated to researcher" in success.output
    assert context.runtime.orchestrator.active_agent == "coder"
    assert failure is not None
    assert "Unknown agent: missing" in failure.output
    assert context.runtime.orchestrator.active_agent == "coder"


async def test_workflow_list_run_status_approve_and_skip() -> None:
    registry = build_default_registry()
    context = _context()

    _, listed = await registry.execute("/workflow list", context)
    _, run = await registry.execute(
        "/workflow run newsletter user_topic=AI",
        context,
    )
    _, status = await registry.execute("/workflow status", context)
    _, approved = await registry.execute("/workflow approve", context)
    _, skipped_none = await registry.execute("/workflow skip", context)
    await registry.execute("/workflow run research user_topic=memory", context)
    _, skipped = await registry.execute("/workflow skip custom-id", context)

    assert listed is not None and "newsletter" in listed.output
    assert run is not None and run.output == "workflow newsletter complete"
    assert status is not None and "Pending approval: newsletter:approval" in status.output
    assert approved is not None and approved.output == "Approved newsletter:approval."
    assert skipped_none is not None and skipped_none.output == "No pending approval."
    assert skipped is not None and skipped.output == "Skipped custom-id."


async def test_workflow_disabled_and_usage_messages() -> None:
    registry = build_default_registry()

    _, disabled = await registry.execute("/workflow list", RegistryCommandContext())
    _, usage = await registry.execute("/workflow", _context())
    _, unknown = await registry.execute("/workflow run missing", _context())

    assert disabled is not None and disabled.output == "Workflow engine is not enabled."
    assert usage is not None and usage.output == (
        "Usage: /workflow list|run|status|approve|skip"
    )
    assert unknown is not None and "Unknown workflow: missing" in unknown.output
