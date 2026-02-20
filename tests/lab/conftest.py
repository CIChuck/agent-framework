"""
Pytest configuration for the Friday Lab.

Provides fixtures for headless harness testing, mock agent profiles,
and ephemeral runtime bootstrapping.

Ref: Phase 1 Build Plan, Step 7.5
"""

from __future__ import annotations

import pytest
from friday_agent import AgentProfile
from friday_core.profiles import MemoryProfile
from friday_runtime import RuntimeConfig, RuntimeKernel


@pytest.fixture
def testing_config() -> RuntimeConfig:
    """RuntimeConfig suitable for unit tests (no real LLM calls)."""
    return RuntimeConfig.for_testing()


@pytest.fixture
def researcher_profile() -> AgentProfile:
    """
    Mock researcher agent profile.

    Has 'research' capability for capability-based routing tests.
    """
    return AgentProfile(
        name="researcher",
        role="Research Specialist",
        goal="Find and synthesize information",
        system_prompt_template="You are {name}, a {role}.",
        _capabilities=["research", "summarization"],
    )


@pytest.fixture
def coder_profile() -> AgentProfile:
    """
    Mock coder agent profile.

    Has 'coding' capability for capability-based routing tests.
    """
    return AgentProfile(
        name="coder",
        role="Software Engineer",
        goal="Write clean, tested code",
        system_prompt_template="You are {name}, a {role}.",
        _capabilities=["coding", "debugging"],
    )


@pytest.fixture
async def ephemeral_kernel(testing_config) -> RuntimeKernel:
    """
    RuntimeKernel with EPHEMERAL memory profile.

    Boots the kernel, yields it for test use, and shuts it down on teardown.
    """
    kernel = RuntimeKernel(
        config=testing_config,
        memory_profile=MemoryProfile.EPHEMERAL,
    )
    await kernel.start()
    yield kernel
    await kernel.stop()
