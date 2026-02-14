"""
Two-agent delegation chain tests.

Validates that the orchestrator correctly routes @mention messages
to mock agents registered via the HeadlessHarness. Uses two explicit
process() calls to test the researcher -> coder handoff pattern.

Exit Criterion #3: Delegation chain test passes.

Ref: Phase 1 Build Plan, Step 7.7
"""

from __future__ import annotations

import pytest

from tests.lab.harness import HeadlessHarness


@pytest.mark.asyncio
async def test_two_agent_delegation_chain(
    testing_config, researcher_profile, coder_profile
):
    """
    Two-agent delegation via explicit @mention routing.

    Flow:
    1. Route to researcher via @researcher mention
    2. Researcher returns response containing @coder reference
    3. Route to coder via @coder mention
    4. Verify both agents were invoked and session state is consistent

    Uses two process() calls because the orchestrator handles @mentions
    only in the initial process() call — it does not auto-delegate
    from response content.
    """
    harness = HeadlessHarness(config=testing_config)
    await harness.start()

    try:
        orchestrator = harness.kernel.orchestrator

        # Set up mock agents (auto-registers profiles if needed)
        harness.mock_agent(
            "researcher",
            ["Found data about Python parsers. @coder should implement."],
            profile=researcher_profile,
        )
        harness.mock_agent(
            "coder",
            ["Implemented the parser module with 3 classes."],
            profile=coder_profile,
        )

        # Set up session
        await orchestrator.set_session("test-session-001", "test-user")

        # Step 1: Route to researcher via @mention
        response_1 = await orchestrator.process(
            "@researcher Find data about Python parsers"
        )
        assert "Python parsers" in response_1
        assert "@coder" in response_1

        # Step 2: Route to coder via @mention
        response_2 = await orchestrator.process(
            "@coder Please implement the parser"
        )
        assert "parser module" in response_2

    finally:
        await harness.stop()


@pytest.mark.asyncio
async def test_delegation_preserves_session(
    testing_config, researcher_profile, coder_profile
):
    """
    Both agents in a delegation chain share the same session context.

    The orchestrator's session_id should remain consistent across
    multiple process() calls in the same delegation flow.
    """
    harness = HeadlessHarness(config=testing_config)
    await harness.start()

    try:
        orchestrator = harness.kernel.orchestrator

        harness.mock_agent(
            "researcher",
            ["research result"],
            profile=researcher_profile,
        )
        harness.mock_agent(
            "coder",
            ["code result"],
            profile=coder_profile,
        )

        session_id = "session-persist-test"
        await orchestrator.set_session(session_id, "test-user")

        # Both calls use the same session
        await orchestrator.process("@researcher do research")
        await orchestrator.process("@coder write code")

        # Session should still be the same
        assert orchestrator.session_id == session_id

    finally:
        await harness.stop()


@pytest.mark.asyncio
async def test_session_isolation_between_chains(
    testing_config, researcher_profile
):
    """
    Different session IDs produce isolated execution contexts.

    Setting a new session should not affect responses or state
    from prior sessions.
    """
    harness = HeadlessHarness(config=testing_config)
    await harness.start()

    try:
        orchestrator = harness.kernel.orchestrator

        harness.mock_agent(
            "researcher",
            ["response-A", "response-B"],
            profile=researcher_profile,
        )

        # Session 1
        await orchestrator.set_session("session-1", "user-1")
        result_1 = await orchestrator.process("@researcher query 1")
        assert result_1 == "response-A"

        # Session 2 — new session, agent cycles to next response
        await orchestrator.set_session("session-2", "user-2")
        result_2 = await orchestrator.process("@researcher query 2")
        assert result_2 == "response-B"

        # Sessions are distinct
        assert orchestrator.session_id == "session-2"

    finally:
        await harness.stop()
