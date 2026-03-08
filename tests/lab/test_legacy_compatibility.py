# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""
Characterization tests for FridayContainer.

These tests capture the current behavior of FridayContainer as a
regression safety net. They must pass against both the original
implementation and the refactored version (which composes RuntimeKernel).

Exit Criterion #1: Characterization Tests Pass.

Ref: Phase 1 Build Plan, Step 5
"""

import pytest
from friday_cli.container import FridayConfig, FridayContainer
from friday_core.profiles import MemoryProfile


@pytest.fixture
def testing_config():
    """Config suitable for unit tests (no real LLM calls needed)."""
    return FridayConfig.for_testing()


@pytest.mark.asyncio
async def test_container_initialize_and_eager_properties(testing_config):
    """
    FridayContainer.initialize() creates all eager services.

    After initialize(), all eager properties must be non-None:
    .llm, .embeddings, .memory, .context_engine, .tool_registry.
    """
    container = FridayContainer(
        config=testing_config,
        memory_profile=MemoryProfile.TESTING,
    )
    await container.initialize()

    try:
        assert container.llm is not None
        assert container.embeddings is not None
        assert container.memory is not None
        assert container.context_engine is not None
        assert container.tool_registry is not None
        assert container.memory_profile == MemoryProfile.TESTING
    finally:
        await container.shutdown()


@pytest.mark.asyncio
async def test_container_lazy_agent_properties(testing_config):
    """
    Agent subsystem properties are lazy-initialized on first access.

    .agent_loader, .agent_registry, .orchestrator should all
    initialize without error.
    """
    container = FridayContainer(
        config=testing_config,
        memory_profile=MemoryProfile.TESTING,
    )
    await container.initialize()

    try:
        # These should initialize lazily without raising
        loader = container.agent_loader
        assert loader is not None

        registry = container.agent_registry
        assert registry is not None

        orchestrator = container.orchestrator
        assert orchestrator is not None
    finally:
        await container.shutdown()


@pytest.mark.asyncio
async def test_container_get_copilot_agent(testing_config):
    """
    get_copilot_agent() returns a CopilotAgent with default profile.
    """
    from friday_agent import CopilotAgent

    container = FridayContainer(
        config=testing_config,
        memory_profile=MemoryProfile.TESTING,
    )
    await container.initialize()

    try:
        agent = container.get_copilot_agent()
        assert isinstance(agent, CopilotAgent)
    finally:
        await container.shutdown()


@pytest.mark.asyncio
async def test_container_shutdown(testing_config):
    """
    shutdown() completes without error and resets initialized flag.

    Note: The current implementation sets _initialized=False but does
    NOT clear cached service references. Eager property accessors
    still return the cached objects. This test captures that behavior.
    """
    container = FridayContainer(
        config=testing_config,
        memory_profile=MemoryProfile.TESTING,
    )
    await container.initialize()
    await container.shutdown()

    # Shutdown resets _initialized flag
    assert container._initialized is False


@pytest.mark.asyncio
async def test_container_double_initialize(testing_config):
    """
    Calling initialize() twice is idempotent.
    """
    container = FridayContainer(
        config=testing_config,
        memory_profile=MemoryProfile.TESTING,
    )
    await container.initialize()
    await container.initialize()  # Should not raise

    try:
        assert container.llm is not None
    finally:
        await container.shutdown()


@pytest.mark.asyncio
async def test_create_friday_container_convenience(testing_config):
    """
    create_friday_container() convenience function works.
    """
    from friday_cli.container import create_friday_container

    container = await create_friday_container(
        config=testing_config,
        memory_profile=MemoryProfile.TESTING,
    )

    try:
        assert container.llm is not None
        assert container.memory is not None
    finally:
        await container.shutdown()
