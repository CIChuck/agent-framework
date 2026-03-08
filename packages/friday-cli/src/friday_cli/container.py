"""
Dependency Injection Container.

Thin wrapper around RuntimeKernel for backward compatibility.
New code should use RuntimeKernel directly from friday-runtime.

.. deprecated::
    Use ``friday_runtime.RuntimeKernel`` and ``friday_runtime.RuntimeConfig``
    directly for new code. This wrapper exists only for backward
    compatibility and will be removed in Phase 2.

Ref: Phase 1 Build Plan, Step 6
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from friday_agent import (
    AgentLoader,
    AgentOrchestrator,
    AgentProfile,
    AgentRegistry,
    CopilotAgent,
    DefaultToolRegistry,
)
from friday_core import TelemetryInterface
from friday_core.profiles import MemoryProfile
from friday_core.security import SanitizationConfig
from friday_llm import LiteLLMEmbeddingService, LiteLLMService
from friday_memory import (
    ContextAssembler,
    MemoryController,
)
from friday_runtime import RuntimeConfig, RuntimeKernel

logger = logging.getLogger(__name__)


@dataclass
class FridayConfig:
    """
    Configuration for the Friday Framework.

    Loads from environment variables with sensible defaults.

    .. deprecated::
        Use ``friday_runtime.RuntimeConfig`` instead.
    """

    # LLM Configuration
    llm_model: str = field(
        default_factory=lambda: os.getenv("FRIDAY_LLM_MODEL", "gpt-4")
    )
    llm_api_key: str | None = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    llm_api_base: str | None = field(
        default_factory=lambda: os.getenv("FRIDAY_LLM_API_BASE")
    )

    # Embedding Configuration
    embedding_model: str = field(
        default_factory=lambda: os.getenv(
            "FRIDAY_EMBEDDING_MODEL", "text-embedding-3-small"
        )
    )

    # ChromaDB Configuration
    chroma_path: str = field(
        default_factory=lambda: os.getenv("FRIDAY_CHROMA_PATH", ".friday/chroma")
    )
    chroma_collection: str = field(
        default_factory=lambda: os.getenv("FRIDAY_CHROMA_COLLECTION", "friday_memory")
    )

    # Telemetry Configuration
    telemetry_enabled: bool = field(
        default_factory=lambda: os.getenv("FRIDAY_TELEMETRY_ENABLED", "false").lower()
        == "true"
    )
    telemetry_endpoint: str | None = field(
        default_factory=lambda: os.getenv("FRIDAY_OTEL_ENDPOINT")
    )
    debug_mode: bool = field(
        default_factory=lambda: os.getenv("FRIDAY_DEBUG", "false").lower() == "true"
    )

    # Agent Configuration
    agents_dir: str | None = field(
        default_factory=lambda: os.getenv("FRIDAY_AGENTS_DIR")
    )

    @classmethod
    def from_env(cls) -> "FridayConfig":
        """Create configuration from environment variables."""
        return cls()

    @classmethod
    def for_testing(cls) -> "FridayConfig":
        """Create configuration suitable for testing."""
        return cls(
            llm_model="gpt-3.5-turbo",
            debug_mode=True,
            telemetry_enabled=False,
            chroma_path=".friday/test_chroma",
        )

    def to_runtime_config(self) -> RuntimeConfig:
        """
        Convert to RuntimeConfig.

        Returns:
            Equivalent RuntimeConfig instance.
        """
        defaults = RuntimeConfig.deployment_profile_defaults("local", cwd=Path.cwd())
        runtime_data_root = Path(defaults["runtime_data_root"])
        if not runtime_data_root.parent.exists():
            runtime_data_root = Path(defaults["workspace_root"]).parent / ".friday-runtime"

        return RuntimeConfig(
            llm_model=self.llm_model,
            llm_api_key=self.llm_api_key,
            llm_api_base=self.llm_api_base,
            embedding_model=self.embedding_model,
            chroma_path=self.chroma_path,
            chroma_collection=self.chroma_collection,
            telemetry_enabled=self.telemetry_enabled,
            telemetry_endpoint=self.telemetry_endpoint,
            debug_mode=self.debug_mode,
            agents_dir=self.agents_dir,
            install_root=defaults["install_root"],
            runtime_data_root=str(runtime_data_root),
            workspace_root=defaults["workspace_root"],
        )


class FridayContainer:
    """
    Dependency Injection container for Friday Framework.

    Thin wrapper around RuntimeKernel that preserves the original
    API surface for backward compatibility.

    .. deprecated::
        Use ``friday_runtime.RuntimeKernel`` directly for new code.

    Example:
        container = FridayContainer(config)
        await container.initialize()

        agent = container.get_copilot_agent(profile)
        response = await agent.run("Hello!")

        await container.shutdown()
    """

    def __init__(
        self,
        config: FridayConfig | None = None,
        memory_profile: MemoryProfile = MemoryProfile.FULL,
        sanitization_config: SanitizationConfig | None = None,
    ) -> None:
        """
        Initialize container with configuration.

        Args:
            config: Framework configuration (defaults to env-based config)
            memory_profile: Memory storage profile
            sanitization_config: Optional output sanitization config
        """
        self.config = config or FridayConfig.from_env()
        self._kernel = RuntimeKernel(
            config=self.config.to_runtime_config(),
            memory_profile=memory_profile,
            sanitization_config=sanitization_config,
        )
        self._initialized = False

    async def initialize(self) -> None:
        """
        Initialize all components.

        Call this before using the container.
        """
        if self._initialized:
            return
        await self._kernel.start()
        self._initialized = True

    async def shutdown(self) -> None:
        """
        Cleanup and shutdown all components.

        Call this when done using the container.
        """
        await self._kernel.stop()
        self._initialized = False

    # --- Component Accessors (delegated to kernel) ---

    @property
    def memory_profile(self) -> MemoryProfile:
        """Get current memory profile."""
        return self._kernel.memory_profile

    @property
    def telemetry(self) -> TelemetryInterface | None:
        """Get telemetry interface."""
        return cast(TelemetryInterface | None, self._kernel.telemetry)

    @property
    def llm(self) -> LiteLLMService:
        """Get LLM service."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return cast(LiteLLMService, self._kernel.llm)

    @property
    def embeddings(self) -> LiteLLMEmbeddingService:
        """Get embedding service."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return cast(LiteLLMEmbeddingService, self._kernel.embeddings)

    @property
    def memory(self) -> MemoryController:
        """Get memory controller."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return cast(MemoryController, self._kernel.memory)

    @property
    def context_engine(self) -> ContextAssembler:
        """Get context assembler."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return cast(ContextAssembler, self._kernel.context_engine)

    @property
    def tool_registry(self) -> DefaultToolRegistry:
        """Get tool registry."""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._kernel.tool_registry

    @property
    def agent_loader(self) -> AgentLoader:
        """Get or create agent loader (lazy)."""
        return self._kernel.agent_loader

    @property
    def agent_registry(self) -> AgentRegistry:
        """Get or create agent registry (lazy)."""
        return self._kernel.agent_registry

    @property
    def orchestrator(self) -> AgentOrchestrator:
        """Get or create agent orchestrator (lazy)."""
        return self._kernel.orchestrator

    # --- Agent Factory Methods ---

    def get_copilot_agent(
        self,
        profile: AgentProfile | None = None,
    ) -> CopilotAgent:
        """
        Create a CopilotAgent with all dependencies wired.

        Args:
            profile: Agent profile (uses default if not provided)

        Returns:
            Configured CopilotAgent instance
        """
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return cast(CopilotAgent, self._kernel.get_copilot_agent(profile))

    def get_team_agent(self, name: str) -> CopilotAgent:
        """
        Get or create a named agent from the registry.

        Args:
            name: Agent name from registry

        Returns:
            Configured CopilotAgent instance
        """
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return cast(CopilotAgent, self._kernel.get_team_agent(name))

    def list_available_agents(self) -> list[str]:
        """
        List available agent names from the registry.

        Returns:
            Sorted list of agent names
        """
        return cast(list[str], self._kernel.list_available_agents())

    def get_agent_info(self, name: str) -> dict | None:
        """
        Get information about an agent.

        Args:
            name: Agent name

        Returns:
            Dict with agent info or None if not found
        """
        return cast(dict | None, self._kernel.get_agent_info(name))


# --- Convenience Functions ---


async def create_friday_container(
    config: FridayConfig | None = None,
    memory_profile: MemoryProfile = MemoryProfile.FULL,
) -> FridayContainer:
    """
    Create and initialize a Friday container.

    Convenience function for quick setup.

    Args:
        config: Optional configuration
        memory_profile: Memory storage profile

    Returns:
        Initialized FridayContainer
    """
    container = FridayContainer(config, memory_profile=memory_profile)
    await container.initialize()
    return container
