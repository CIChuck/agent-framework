"""
Dependency Injection Container.

Wires configuration to all Friday Framework components including:
- LLM services (chat completion, embeddings)
- Memory stores (vector, graph, episodic)
- Memory controller
- Context engine
- Tool registry
- Agent instances

Ref: Batch 3 Specification, Section 6
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any

from friday_core import TelemetryInterface
from friday_core.telemetry import DebugTelemetryRecorder, OpenTelemetryProvider

from friday_memory import (
    ChromaVectorStore,
    ContextAssembler,
    ElementXGraphStore,
    InMemoryEpisodicStore,
    MemoryController,
    MemoryExtractor,
)
from friday_cli.profiles import (
    MemoryProfile,
    create_vector_store,
    create_graph_store,
)

from friday_llm import LiteLLMEmbeddingService, LiteLLMService

from friday_agent import (
    AgentConfigError,
    AgentLoader,
    AgentOrchestrator,
    AgentProfile,
    AgentRegistry,
    AgentRegistryError,
    CopilotAgent,
    DefaultToolRegistry,
    OrchestratorError,
)
from friday_agent.tools.builtins import (
    recall_memory,
    scratchpad_clear,
    scratchpad_list,
    scratchpad_read,
    scratchpad_write,
    store_fact,
)

logger = logging.getLogger(__name__)


@dataclass
class FridayConfig:
    """
    Configuration for the Friday Framework.

    Loads from environment variables with sensible defaults.
    """

    # LLM Configuration
    llm_model: str = field(
        default_factory=lambda: os.getenv("FRIDAY_LLM_MODEL", "gpt-4")
    )
    llm_api_key: str | None = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
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


class FridayContainer:
    """
    Dependency Injection container for Friday Framework.

    Creates and wires all components with proper dependency injection.
    Implements lazy initialization for expensive resources.

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
    ) -> None:
        """
        Initialize container with configuration.

        Args:
            config: Framework configuration (defaults to env-based config)
            memory_profile: Memory storage profile (FULL, EPHEMERAL, VECTOR_ONLY, TESTING)
        """
        self.config = config or FridayConfig.from_env()
        self._memory_profile = memory_profile

        # Lazy-initialized components
        self._telemetry: TelemetryInterface | None = None
        self._llm: LiteLLMService | None = None
        self._embeddings: LiteLLMEmbeddingService | None = None
        self._vector_store: ChromaVectorStore | None = None
        self._graph_store: ElementXGraphStore | None = None
        self._episodic_store: InMemoryEpisodicStore | None = None
        self._memory_controller: MemoryController | None = None
        self._context_assembler: ContextAssembler | None = None
        self._tool_registry: DefaultToolRegistry | None = None

        # Agent configuration (lazy-initialized)
        self._agent_loader: AgentLoader | None = None
        self._agent_registry: AgentRegistry | None = None
        self._orchestrator: AgentOrchestrator | None = None

        self._initialized = False

    async def initialize(self) -> None:
        """
        Initialize all components.

        Call this before using the container.
        """
        if self._initialized:
            return

        logger.info("Initializing Friday container...")

        # Create telemetry first (needed by other components)
        self._create_telemetry()

        # Create LLM services
        self._create_llm_services()

        # Create storage adapters
        await self._create_storage_adapters()

        # Create memory controller
        self._create_memory_controller()

        # Create context engine
        self._create_context_engine()

        # Create tool registry
        self._create_tool_registry()

        self._initialized = True
        logger.info("Friday container initialized successfully")

    async def shutdown(self) -> None:
        """
        Cleanup and shutdown all components.

        Call this when done using the container.
        """
        logger.info("Shutting down Friday container...")

        # Cleanup resources as needed
        if self._vector_store:
            # ChromaDB handles its own cleanup
            pass

        self._initialized = False
        logger.info("Friday container shutdown complete")

    # --- Component Accessors ---

    @property
    def memory_profile(self) -> MemoryProfile:
        """Get current memory profile."""
        return self._memory_profile

    @property
    def telemetry(self) -> TelemetryInterface | None:
        """Get telemetry interface."""
        return self._telemetry

    @property
    def llm(self) -> LiteLLMService:
        """Get LLM service."""
        if not self._llm:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._llm

    @property
    def embeddings(self) -> LiteLLMEmbeddingService:
        """Get embedding service."""
        if not self._embeddings:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._embeddings

    @property
    def memory(self) -> MemoryController:
        """Get memory controller."""
        if not self._memory_controller:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._memory_controller

    @property
    def context_engine(self) -> ContextAssembler:
        """Get context assembler."""
        if not self._context_assembler:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._context_assembler

    @property
    def tool_registry(self) -> DefaultToolRegistry:
        """Get tool registry."""
        if not self._tool_registry:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._tool_registry

    @property
    def agent_loader(self) -> AgentLoader:
        """
        Get or create agent loader.

        The loader is created lazily on first access.
        """
        if self._agent_loader is None:
            from pathlib import Path

            agents_dir = Path(self.config.agents_dir) if self.config.agents_dir else Path("agents")
            self._agent_loader = AgentLoader(agents_dir)
        return self._agent_loader

    @property
    def agent_registry(self) -> AgentRegistry:
        """
        Get or create agent registry.

        The registry is auto-configured with:
        - AgentLoader for YAML loading
        - Factory for agent instantiation
        - All agents from the agents directory (if it exists)
        """
        if self._agent_registry is None:
            # Create registry with loader
            self._agent_registry = AgentRegistry(self.agent_loader)

            # Configure factory for creating agents
            self._agent_registry.set_factory(self._create_agent)

            # Auto-load agents from directory (if it exists)
            try:
                self._agent_registry.load_all_from_directory()
            except Exception as e:
                logger.warning(f"Could not load agents from directory: {e}")

        return self._agent_registry

    @property
    def orchestrator(self) -> AgentOrchestrator:
        """
        Get or create the agent orchestrator.

        The orchestrator is configured with:
        - The container's agent registry
        - Default agent (first registered agent, if any)

        Returns:
            Configured AgentOrchestrator instance
        """
        if self._orchestrator is None:
            # Determine default agent (first available agent)
            default_agent = None
            available_agents = self.agent_registry.list_agents()
            if available_agents:
                default_agent = available_agents[0]
                logger.debug(f"Using '{default_agent}' as default orchestrator agent")

            self._orchestrator = AgentOrchestrator(
                registry=self.agent_registry,
                default_agent=default_agent,
            )
            logger.info("Agent orchestrator initialized")

        return self._orchestrator

    # --- Agent Factory ---

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

        if profile is None:
            profile = self._default_profile()

        return CopilotAgent(
            profile=profile,
            memory=self.memory,
            context_engine=self.context_engine,
            llm=self.llm,
            tool_registry=self.tool_registry,
            telemetry=self.telemetry,
        )

    def get_team_agent(self, name: str) -> CopilotAgent:
        """
        Get or create a named agent from the registry.

        Convenience method for getting an agent by name. The agent is
        created with all necessary dependencies from the container.

        Args:
            name: Agent name from registry

        Returns:
            Configured CopilotAgent instance

        Raises:
            KeyError: If agent not found in registry
            AgentRegistryError: If registry not configured properly
        """
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")

        return self.agent_registry.create_agent(name)

    def list_available_agents(self) -> list[str]:
        """
        List available agent names from the registry.

        Returns:
            Sorted list of agent names
        """
        return self.agent_registry.list_agents()

    def get_agent_info(self, name: str) -> dict | None:
        """
        Get information about an agent.

        Args:
            name: Agent name

        Returns:
            Dict with agent info or None if not found
        """
        profile = self.agent_registry.get(name)
        if profile is None:
            return None

        return {
            "name": profile.name,
            "role": profile.role,
            "goal": profile.goal,
            "capabilities": profile.capabilities,
            "tools": profile.tools,
            "tool_autonomy": profile.tool_autonomy,
        }

    def _create_agent(self, profile: AgentProfile) -> CopilotAgent:
        """
        Factory function for creating agents from profiles.

        This is used by AgentRegistry when create_agent() is called.
        Configures agent with all necessary dependencies from the container.

        Args:
            profile: Agent profile to instantiate

        Returns:
            Configured CopilotAgent instance
        """
        return CopilotAgent(
            profile=profile,
            memory=self.memory,
            context_engine=self.context_engine,
            llm=self.llm,
            tool_registry=self.tool_registry,
            telemetry=self.telemetry,
        )

    # --- Private Initialization Methods ---

    def _create_telemetry(self) -> None:
        """Create telemetry interface."""
        if self.config.debug_mode:
            self._telemetry = DebugTelemetryRecorder()
            logger.info("Using DebugTelemetryRecorder for telemetry")
        elif self.config.telemetry_enabled:
            self._telemetry = OpenTelemetryProvider(
                service_name="friday",
                endpoint=self.config.telemetry_endpoint,
            )
            logger.info("Using OpenTelemetryProvider for telemetry")
        else:
            self._telemetry = None
            logger.info("Telemetry disabled")

    def _create_llm_services(self) -> None:
        """Create LLM and embedding services."""
        self._llm = LiteLLMService(
            model_name=self.config.llm_model,
            api_key=self.config.llm_api_key,
            api_base=self.config.llm_api_base,
            telemetry=self._telemetry,
        )

        self._embeddings = LiteLLMEmbeddingService(
            model_name=self.config.embedding_model,
            api_key=self.config.llm_api_key,
            api_base=self.config.llm_api_base,
            telemetry=self._telemetry,
        )

        logger.info(f"LLM service configured with model: {self.config.llm_model}")

    async def _create_storage_adapters(self) -> None:
        """Create storage adapter instances based on memory profile."""
        # Vector store based on profile
        self._vector_store = create_vector_store(
            profile=self._memory_profile,
            embedding_function=self._embeddings,
            path=self.config.chroma_path,
            collection_name=self.config.chroma_collection,
        )

        # Graph store based on profile
        self._graph_store = create_graph_store(
            profile=self._memory_profile,
            storage_path=None,  # In-memory by default
        )

        # Episodic store (always in-memory)
        self._episodic_store = InMemoryEpisodicStore()

        logger.info(f"Storage adapters initialized (profile: {self._memory_profile.value})")

    def _create_memory_controller(self) -> None:
        """Create memory controller."""
        self._memory_controller = MemoryController(
            vector_store=self._vector_store,
            graph_store=self._graph_store,
            episodic_store=self._episodic_store,
            telemetry=self._telemetry,
        )

        logger.info("Memory controller initialized")

    def _create_context_engine(self) -> None:
        """Create context assembler and wire extractor."""
        # Create context assembler
        self._context_assembler = ContextAssembler(
            memory_controller=self._memory_controller,
            telemetry=self._telemetry,
        )

        # Create and wire extractor with LLM client
        extractor = MemoryExtractor(
            memory_controller=self._memory_controller,
            llm=self._llm,
            telemetry=self._telemetry,
        )
        self._context_assembler.set_extractor(extractor)

        logger.info("Context engine initialized with extractor")

    def _create_tool_registry(self) -> None:
        """Create and configure tool registry."""
        self._tool_registry = DefaultToolRegistry()

        # Load decorated tools
        self._tool_registry.load_decorated_tools()

        # Bind dependencies to built-in tools
        # Note: session_state is bound at agent runtime
        self._tool_registry.bind_dependency(
            "recall_memory",
            memory=self._memory_controller,
        )
        self._tool_registry.bind_dependency(
            "store_fact",
            memory=self._memory_controller,
        )

        logger.info(f"Tool registry initialized with {len(self._tool_registry.list_tools())} tools")

    def _default_profile(self) -> AgentProfile:
        """Create default agent profile."""
        return AgentProfile(
            name="Friday",
            role="Personal Assistant",
            goal="Help users accomplish their tasks efficiently and accurately",
            system_prompt_template="""You are {name}, a {role}.

Your goal: {goal}

You have access to a persistent memory system. Use the available tools to:
- Remember important information with store_fact
- Recall relevant context with recall_memory
- Save working notes with scratchpad_write

Be helpful, accurate, and concise in your responses.""",
            tools=[
                "recall_memory",
                "store_fact",
                "scratchpad_write",
                "scratchpad_read",
                "scratchpad_list",
            ],
            temperature=0.7,
        )


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
        memory_profile: Memory storage profile (FULL, EPHEMERAL, VECTOR_ONLY, TESTING)

    Returns:
        Initialized FridayContainer
    """
    container = FridayContainer(config, memory_profile=memory_profile)
    await container.initialize()
    return container
