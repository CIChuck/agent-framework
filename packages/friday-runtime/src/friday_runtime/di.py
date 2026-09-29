"""
Dependency Injection container for the Runtime Kernel.

Extracts the boot sequence from FridayContainer into reusable
factory methods. Each method creates a single service or group
of related services.

Ref: Phase 1 Build Plan, Step 4.2
"""

import logging
from typing import Any, cast

from friday_agent import DefaultToolRegistry
from friday_core import TelemetryInterface
from friday_core.interfaces import (
    EmbeddingModel,
    EpisodicStoreAdapter,
    LLMClient,
    TranscriptBackedEpisodicStore,
)
from friday_core.profiles import (
    MemoryProfile,
    create_graph_store,
    create_vector_store,
)
from friday_core.telemetry import DebugTelemetryRecorder, OpenTelemetryProvider
from friday_llm import LiteLLMEmbeddingService, LiteLLMService
from friday_llm.config import ResilienceConfig
from friday_memory import (
    CollectionConfig,
    CollectionManager,
    ContextAssembler,
    InMemoryEpisodicStore,
    MemoryController,
    MemoryExtractor,
    MultiAgentMemoryController,
    NamespacePolicyEngine,
    OntologyConfig,
    PromotionCoordinator,
    PromotionJournal,
)
from friday_transcript import SQLiteTranscriptStore

from friday_runtime.config import (
    EmbeddingServiceConfig,
    LLMServiceConfig,
    RuntimeConfig,
)
from friday_runtime.mcp_loading import RuntimeMCPProvider
from friday_runtime.tool_loading import register_runtime_tools

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
        self.llm_pool: dict[str, LiteLLMService] = {}
        self.embedding_pool: dict[str, LiteLLMEmbeddingService] = {}
        self.embeddings: LiteLLMEmbeddingService | None = None
        self.vector_store: Any = None
        self.graph_store: Any = None
        self.episodic_store: EpisodicStoreAdapter | None = None
        self.transcript_store: SQLiteTranscriptStore | None = None
        self.memory: MemoryController | None = None
        self.multi_agent_memory: MultiAgentMemoryController | None = None
        self.multi_agent_journal: PromotionJournal | None = None
        self.multi_agent_coordinator: PromotionCoordinator | None = None
        self.context_engine: ContextAssembler | None = None
        self.tool_registry: DefaultToolRegistry | None = None
        self.mcp_provider: RuntimeMCPProvider | None = None
        self._booted = False

    async def boot(self) -> None:
        """
        Execute the full boot sequence.

        Creates all eager services in dependency order.
        Raises on failure — partial initialization is not supported.
        """
        if self._booted:
            return
        self._create_telemetry()
        self._create_llm_services()
        await self._create_storage_adapters()
        self._create_memory_controller()
        self._create_multi_agent_stack()
        self._create_context_engine()
        self._create_tool_registry()
        if self._config.tools.providers.mcp.enabled:
            if self._config.workspace_root is None:
                raise RuntimeError("Runtime workspace root not initialized")
            # Failed boot may leave cleanup pending. Reuse its explicit owner
            # so provider startup and public shutdown can reach every client.
            if self.mcp_provider is None:
                self.mcp_provider = RuntimeMCPProvider(
                    self._config.tools.providers.mcp, self._config.workspace_root,
                    telemetry=self.telemetry,
                )
            await self.mcp_provider.start()
            if self.tool_registry is None:
                raise RuntimeError("Runtime tool registry not initialized")
            try:
                await self.mcp_provider.register_tools(self.tool_registry)
            except BaseException:
                await self.mcp_provider.stop()
                raise
        self._booted = True
        logger.info("DI container boot complete")

    async def shutdown(self) -> None:
        """
        Gracefully shut down all services.

        Safe to call multiple times.
        """
        logger.info("Shutting down DI container...")
        if self.mcp_provider is not None:
            await self.mcp_provider.stop()
        self._booted = False
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
        self.llm_pool = {}
        for service_name, service_config in self._config.llm_pool.services.items():
            chat_spec = self._config.llm_service_specs.get(service_name)
            if chat_spec is not None:
                self.llm_pool[service_name] = LiteLLMService.from_spec(
                    chat_spec,
                    telemetry=self.telemetry,
                )
            else:
                if not isinstance(service_config, LLMServiceConfig):
                    raise RuntimeError(
                        f"LLM service {service_name!r} has no resolved specification"
                    )
                self.llm_pool[service_name] = LiteLLMService(
                    model_name=service_config.model,
                    api_key=service_config.api_key,
                    api_base=service_config.api_base,
                    telemetry=self.telemetry,
                    resilience=ResilienceConfig(
                        max_retries=service_config.resilience.max_retries,
                        timeout_seconds=float(
                            service_config.resilience.timeout_seconds
                        ),
                    ),
                )

        self.llm = self.llm_pool[self._config.llm_pool.default_service]

        self.embedding_pool = {}
        for (
            service_name,
            embedding_service_config,
        ) in self._config.embedding_pool.services.items():
            embedding_spec = self._config.embedding_service_specs.get(service_name)
            if embedding_spec is not None:
                self.embedding_pool[service_name] = (
                    LiteLLMEmbeddingService.from_spec(
                        embedding_spec,
                        telemetry=self.telemetry,
                    )
                )
            else:
                if not isinstance(
                    embedding_service_config,
                    EmbeddingServiceConfig,
                ):
                    raise RuntimeError(
                        f"Embedding service {service_name!r} has no resolved "
                        "specification"
                    )
                self.embedding_pool[service_name] = LiteLLMEmbeddingService(
                    model_name=embedding_service_config.model,
                    api_key=embedding_service_config.api_key,
                    api_base=embedding_service_config.api_base,
                    telemetry=self.telemetry,
                    resilience=ResilienceConfig(
                        max_retries=(
                            embedding_service_config.resilience.max_retries
                        ),
                        timeout_seconds=float(
                            embedding_service_config.resilience.timeout_seconds
                        ),
                    ),
                )

        self.embeddings = self.embedding_pool[self._config.embedding_pool.default_service]
        logger.info(
            "LLM pool configured with default service '%s' (%s) across %d services; "
            "embedding pool default '%s' (%s) across %d services",
            self._config.llm_pool.default_service,
            self.llm.model,
            len(self.llm_pool),
            self._config.embedding_pool.default_service,
            self.embeddings.model,
            len(self.embedding_pool),
        )

    async def _create_storage_adapters(self) -> None:
        """Create storage adapter instances based on memory profile."""
        assert self.embeddings is not None
        graph_storage_path = self._config.resolve_runtime_state_path("memory/graph.json")
        graph_storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.vector_store = create_vector_store(
            profile=self._memory_profile,
            embedding_function=cast(EmbeddingModel, self.embeddings),
            path=self._config.chroma_path,
            collection_name=self._config.chroma_collection,
        )

        self.graph_store = create_graph_store(
            profile=self._memory_profile,
            storage_path=str(graph_storage_path),
        )

        if self._config.transcript.enabled:
            transcript_path = self._config.resolve_transcript_path(
                self._config.transcript.path
            )
            transcript_path.parent.mkdir(parents=True, exist_ok=True)
            self.transcript_store = SQLiteTranscriptStore(transcript_path)
            self.episodic_store = TranscriptBackedEpisodicStore(
                transcript_store=self.transcript_store,
                model_name=self._config.get_llm_service_config().model,
                system_prompt=self._config.prompting.base_system_prompt,
                capture_context_log=self._config.transcript.capture_context_log,
            )
        else:
            self.transcript_store = None
            self.episodic_store = InMemoryEpisodicStore()

        logger.info(
            f"Storage adapters initialized (profile: {self._memory_profile.value})"
        )

    def _create_memory_controller(self) -> None:
        """Create memory controller with lifecycle-aware collections."""
        assert self.embeddings is not None
        assert self.episodic_store is not None
        base_name = self._config.chroma_collection
        collection_config = CollectionConfig(
            short_term_collection=f"{base_name}_short",
            long_term_collection=f"{base_name}_long",
            decayed_collection=f"{base_name}_decayed",
        )
        collection_manager = CollectionManager(
            embedding_function=cast(EmbeddingModel, self.embeddings),
            config=collection_config,
            path=self._config.chroma_path,
            telemetry=self.telemetry,
        )

        self.memory = MemoryController(
            vector_store=self.vector_store,
            graph_store=self.graph_store,
            episodic_store=cast(EpisodicStoreAdapter, self.episodic_store),
            telemetry=self.telemetry,
            collection_manager=collection_manager,
            transcript_store=self.transcript_store,
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
        assert self.memory is not None
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
        assert self.memory is not None
        self.context_engine = ContextAssembler(
            memory_controller=self.memory,
            telemetry=self.telemetry,
        )

        if self._config.memory_extraction.enabled:
            assert self.llm is not None
            extraction_llm = self.llm_pool[self._config.memory_extraction.llm_service or self._config.llm_pool.default_service]
            extraction_embeddings: EmbeddingModel | None = None
            extraction_embedding_service = (
                self._config.memory_extraction.embedding_service
            )
            if extraction_embedding_service is not None:
                extraction_embeddings = cast(
                    EmbeddingModel,
                    self.embedding_pool[extraction_embedding_service],
                )

            ontology = self._config.memory_extraction.ontology
            extractor = MemoryExtractor(
                memory_controller=self.memory,
                llm=cast(LLMClient, extraction_llm),
                telemetry=self.telemetry,
                prompt_template=self._config.memory_extraction.prompt,
                user_name=self._config.memory_extraction.user_name,
                assistant_name=self._config.memory_extraction.assistant_name,
                embedding_model=extraction_embeddings,
                max_tokens=self._config.memory_extraction.max_tokens,
                ontology_config=(
                    OntologyConfig.from_dict(ontology) if ontology is not None else None
                ),
                rejection_log_path=self._config.memory_extraction.rejection_log,
            )
            self.context_engine.set_extractor(extractor)
            logger.info(
                "Context engine initialized with extractor service '%s'",
                self._config.memory_extraction.llm_service,
            )
        else:
            logger.info("Context engine initialized without archive extractor")

    def _create_tool_registry(self) -> None:
        """Create and configure tool registry."""
        self.tool_registry = DefaultToolRegistry()
        register_runtime_tools(self.tool_registry, self._config.tools)

        # Bind dependencies to built-in tools
        if self.tool_registry.has_tool("recall_memory"):
            self.tool_registry.bind_dependency(
                "recall_memory",
                memory=self.memory,
            )
        if self.tool_registry.has_tool("store_fact"):
            self.tool_registry.bind_dependency(
                "store_fact",
                memory=self.memory,
            )

        logger.info(
            f"Tool registry initialized with "
            f"{len(self.tool_registry.list_tools())} tools"
        )
