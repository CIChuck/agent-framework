"""
Headless execution tests for the Friday Lab.

Validates that the HeadlessHarness can boot an ephemeral RuntimeKernel,
register deterministic mock agents, and execute them end-to-end without
any CLI or LLM dependencies.

Exit Criterion #2: HeadlessHarness boots and passes agent execution tests.

Ref: Phase 1 Build Plan, Step 7.6
"""

from __future__ import annotations

import pytest

from friday_core.profiles import MemoryProfile

from tests.lab.harness import HeadlessHarness


@pytest.mark.asyncio
async def test_harness_boots_ephemeral_kernel(testing_config):
    """
    HeadlessHarness.start() boots a kernel with EPHEMERAL memory profile.

    The kernel should be fully operational after start() completes,
    with all eager services initialized.
    """
    harness = HeadlessHarness(config=testing_config)
    await harness.start()

    try:
        kernel = harness.kernel
        assert kernel is not None
        assert kernel.memory_profile == MemoryProfile.EPHEMERAL
        assert kernel.llm is not None
        assert kernel.memory is not None
    finally:
        await harness.stop()


@pytest.mark.asyncio
async def test_mock_agent_returns_fixed_responses(
    testing_config, researcher_profile
):
    """
    mock_agent() registers a deterministic agent that returns
    fixed responses through the registry's per-agent factory override.
    """
    harness = HeadlessHarness(config=testing_config)
    await harness.start()

    try:
        # Set up mock with fixed responses (auto-registers if needed)
        harness.mock_agent(
            "researcher",
            ["Result A", "Result B"],
            profile=researcher_profile,
        )

        # Create agent through registry (uses per-agent factory)
        agent = harness.kernel.agent_registry.create_agent("researcher")
        assert agent.name == "researcher"

        # Agent returns responses in order
        response_1 = await agent.run("query 1")
        assert response_1 == "Result A"

        response_2 = await agent.run("query 2")
        assert response_2 == "Result B"
    finally:
        await harness.stop()


@pytest.mark.asyncio
async def test_mock_agent_cycles_responses(
    testing_config, researcher_profile
):
    """
    When fixed_responses are exhausted, the mock agent cycles back
    to the beginning.
    """
    harness = HeadlessHarness(config=testing_config)
    await harness.start()

    try:
        harness.mock_agent(
            "researcher",
            ["only-response"],
            profile=researcher_profile,
        )

        agent = harness.kernel.agent_registry.create_agent("researcher")

        # Cycle through multiple times
        assert await agent.run("q1") == "only-response"
        assert await agent.run("q2") == "only-response"
        assert await agent.run("q3") == "only-response"
    finally:
        await harness.stop()


@pytest.mark.asyncio
async def test_multiple_mock_agents(
    testing_config, researcher_profile, coder_profile
):
    """
    Multiple mock agents can coexist with independent response sequences.
    """
    harness = HeadlessHarness(config=testing_config)
    await harness.start()

    try:
        harness.mock_agent(
            "researcher",
            ["research data"],
            profile=researcher_profile,
        )
        harness.mock_agent(
            "coder",
            ["code output"],
            profile=coder_profile,
        )

        researcher = harness.kernel.agent_registry.create_agent("researcher")
        coder = harness.kernel.agent_registry.create_agent("coder")

        assert await researcher.run("find data") == "research data"
        assert await coder.run("write code") == "code output"
    finally:
        await harness.stop()


@pytest.mark.asyncio
async def test_harness_stop_is_idempotent(testing_config):
    """
    Calling stop() multiple times should not raise.
    """
    harness = HeadlessHarness(config=testing_config)
    await harness.start()
    await harness.stop()
    await harness.stop()  # Should not raise


@pytest.mark.asyncio
async def test_inject_conflict_not_implemented(testing_config):
    """
    inject_conflict() raises NotImplementedError (Phase 2 feature).
    """
    harness = HeadlessHarness(config=testing_config)
    await harness.start()

    try:
        with pytest.raises(NotImplementedError, match="Phase 2"):
            await harness.inject_conflict("fact A", "fact B")
    finally:
        await harness.stop()


@pytest.mark.asyncio
async def test_replay_session_not_implemented(testing_config):
    """
    replay_session() raises NotImplementedError (Phase 2 feature).
    """
    harness = HeadlessHarness(config=testing_config)
    await harness.start()

    try:
        with pytest.raises(NotImplementedError, match="Phase 2"):
            await harness.replay_session("/path/to/session.log")
    finally:
        await harness.stop()
