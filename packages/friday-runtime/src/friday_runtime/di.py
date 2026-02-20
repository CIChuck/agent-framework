"""
Dependency Injection container for the Runtime Kernel.

Extracts the boot sequence from FridayContainer into reusable
factory methods. Each method creates a single service or group
of related services.

Ref: Phase 1 Build Plan, Step 4.2
"""

import logging
from typing import Any

from friday_agent import DefaultToolRegistry
from friday_core import TelemetryInterface
from friday_core.profiles import (
    MemoryProfile,
    create_graph_store,
    create_vector_store,
)
from friday_core.telemetry import DebugTelemetryRecorder, OpenTelemetryProvider
from friday_llm import LiteLLMEmbeddingService, LiteLLMService
from friday_memory import (
    CollectionConfig,
    CollectionManager,
    ContextAssembler,
    InMemoryEpisodicStore,
    MemoryController,
    MemoryExtractor,
    MultiAgentMemoryController,
    NamespacePolicyEngine,
    PromotionCoordinator,
    PromotionJournal,
)

from friday_runtime.config import RuntimeConfig

logger = logging.getLogger(__name__)


class DIContainer:
    """
    Dependency Injection container that holds all created services.

    The boot sequence mirrors the legacy FridayContainer.initialize()
    order: telemetry -> LLM -> storage -> memory -> context -> tools.
    """

    def __init__(
        self,
        config: RuntimeConfig,
        memory_profile: MemoryProfile,
    ) -> None:
        """
        Initialize the DI container.

        Args:
            config: Runtime configuration.
            memory_profile: Memory storage profile.
        """
        self._config = config
        self._memory_profile = memory_profile

        # Service slots (populated during boot)
        self.telemetry: TelemetryInterface | None = None
        self.llm: LiteLLMService | None = None
        self.embeddings: LiteLLMEmbeddingService | None = None
        self.vector_store: Any = None
        self.graph_store: Any = None
        self.episodic_store: InMemoryEpisodicStore | None = None
        self.memory: MemoryController | None = None
        self.multi_agent_memory: MultiAgentMemoryController | None = None
        self.multi_agent_journal: PromotionJournal | None = None
        self.multi_agent_coordinator: PromotionCoordinator | None = None
        self.context_engine: ContextAssembler | None = None
        self.tool_registry: DefaultToolRegistry | None = None

    async def boot(self) -> None:
        """
        Execute the full boot sequence.

        Creates all eager services in dependency order.
        Raises on failure — partial initialization is not supported.
        """
        self._create_telemetry()
        self._create_llm_services()
        await self._create_storage_adapters()
        self._create_memory_controller()
        self._create_multi_agent_stack()
        self._create_context_engine()
        self._create_tool_registry()
        logger.info("DI container boot complete")

    async def shutdown(self) -> None:
        """
        Gracefully shut down all services.

        Safe to call multiple times.
        """
        logger.info("Shutting down DI container...")
        # Currently ChromaDB handles its own cleanup.
        # Future: flush telemetry, persist memory, etc.
        logger.info("DI container shutdown complete")

    # --- Private Boot Methods ---

    def _create_telemetry(self) -> None:
        """Create telemetry interface based on config."""
        if self._config.debug_mode:
            self.telemetry = DebugTelemetryRecorder()
            logger.info("Using DebugTelemetryRecorder for telemetry")
        elif self._config.telemetry_enabled:
            self.telemetry = OpenTelemetryProvider(
                service_name="friday",
                endpoint=self._config.telemetry_endpoint,
            )
            logger.info("Using OpenTelemetryProvider for telemetry")
        else:
            self.telemetry = None
            logger.info("Telemetry disabled")

    def _create_llm_services(self) -> None:
        """Create LLM and embedding services."""
        self.llm = LiteLLMService(
            model_name=self._config.llm_model,
            api_key=self._config.llm_api_key,
            api_base=self._config.llm_api_base,
            telemetry=self.telemetry,
        )

        self.embeddings = LiteLLMEmbeddingService(
            model_name=self._config.embedding_model,
            api_key=self._config.llm_api_key,
            api_base=self._config.llm_api_base,
            telemetry=self.telemetry,
        )

        logger.info(f"LLM service configured with model: {self._config.llm_model}")

    async def _create_storage_adapters(self) -> None:
        """Create storage adapter instances based on memory profile."""
        self.vector_store = create_vector_store(
            profile=self._memory_profile,
            embedding_function=self.embeddings,
            path=self._config.chroma_path,
            collection_name=self._config.chroma_collection,
        )

        self.graph_store = create_graph_store(
            profile=self._memory_profile,
            storage_path=None,  # In-memory by default
        )

        self.episodic_store = InMemoryEpisodicStore()

        logger.info(
            f"Storage adapters initialized (profile: {self._memory_profile.value})"
        )

    def _create_memory_controller(self) -> None:
        """Create memory controller with lifecycle-aware collections."""
        base_name = self._config.chroma_collection
        collection_config = CollectionConfig(
            short_term_collection=f"{base_name}_short",
            long_term_collection=f"{base_name}_long",
            decayed_collection=f"{base_name}_decayed",
        )
        collection_manager = CollectionManager(
            embedding_function=self.embeddings,
            config=collection_config,
            path=self._config.chroma_path,
            telemetry=self.telemetry,
        )

        self.memory = MemoryController(
            vector_store=self.vector_store,
            graph_store=self.graph_store,
            episodic_store=self.episodic_store,
            telemetry=self.telemetry,
            collection_manager=collection_manager,
        )

        logger.info("Memory controller initialized with lifecycle collections")

    def _create_multi_agent_stack(self) -> None:
        """Create additive multi-agent memory stack when mode is enabled."""
        if self._config.memory_mode != "multi_agent":
            self.multi_agent_memory = None
            self.multi_agent_journal = None
            self.multi_agent_coordinator = None
            return

        self.multi_agent_journal = PromotionJournal()
        self.multi_agent_coordinator = PromotionCoordinator(self.multi_agent_journal)
        self.multi_agent_memory = MultiAgentMemoryController(
            memory=self.memory,
            session_id="runtime-default",
            agent_id="runtime",
            namespace="default",
            policy=NamespacePolicyEngine(
                session_id="runtime-default",
                actor_id="runtime",
                namespace="default",
            ),
            coordinator=self.multi_agent_coordinator,
        )
        logger.warning(
            "Multi-agent mode enabled without arbitrator service binding; "
            "shared promotion remains unavailable until arbitrator is attached."
        )

    def _create_context_engine(self) -> None:
        """Create context assembler and wire extractor."""
        self.context_engine = ContextAssembler(
            memory_controller=self.memory,
            telemetry=self.telemetry,
        )

        extractor = MemoryExtractor(
            memory_controller=self.memory,
            llm=self.llm,
            telemetry=self.telemetry,
        )
        self.context_engine.set_extractor(extractor)

        logger.info("Context engine initialized with extractor")

    def _create_tool_registry(self) -> None:
        """Create and configure tool registry."""
        self.tool_registry = DefaultToolRegistry()

        # Load decorated tools
        self.tool_registry.load_decorated_tools()

        # Bind dependencies to built-in tools
        self.tool_registry.bind_dependency(
            "recall_memory",
            memory=self.memory,
        )
        self.tool_registry.bind_dependency(
            "store_fact",
            memory=self.memory,
        )

        logger.info(
            f"Tool registry initialized with "
            f"{len(self.tool_registry.list_tools())} tools"
        )
