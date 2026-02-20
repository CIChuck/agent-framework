"""
Runtime Kernel — the headless operating system for Friday.

RuntimeKernel implements SystemRuntime and manages the full lifecycle
of framework services. It can be used without the CLI presentation
layer for headless execution, testing, and embedding.

Agent subsystem properties (agent_loader, agent_registry, orchestrator)
are lazy-initialized on first access, preserving the existing error
semantics from FridayContainer.

Ref: Phase 1 Build Plan, Step 4.3
"""

import logging
import uuid
from pathlib import Path
from typing import Any

from friday_agent import (
    AgentLoader,
    AgentOrchestrator,
    AgentProfile,
    AgentRegistry,
    CopilotAgent,
    DefaultToolRegistry,
)
from friday_core.interfaces.runtime import SystemRuntime
from friday_core.profiles import MemoryProfile
from friday_core.security import SanitizationConfig

from friday_runtime.config import RuntimeConfig
from friday_runtime.di import DIContainer

logger = logging.getLogger(__name__)


class RuntimeKernel(SystemRuntime):
    """
    Headless runtime kernel for the Friday Agent Framework.

    Manages service lifecycle (LLM, memory, tools, telemetry) and
    provides agent spawning and workflow execution. Does not depend
    on any CLI or presentation layer.

    Usage:
        kernel = RuntimeKernel(
            config=RuntimeConfig.from_env(),
            memory_profile=MemoryProfile.FULL,
        )
        await kernel.start()

        agent = kernel.spawn_agent("researcher")
        result = await agent.run("Find data about Python parsers")

        await kernel.stop()
    """

    def __init__(
        self,
        config: RuntimeConfig | None = None,
        memory_profile: MemoryProfile = MemoryProfile.FULL,
        sanitization_config: SanitizationConfig | None = None,
    ) -> None:
        """
        Initialize the runtime kernel.

        Args:
            config: Runtime configuration (defaults to env-based).
            memory_profile: Memory storage profile.
            sanitization_config: Optional output sanitization config,
                forwarded to CopilotAgent on creation.
        """
        self._config = config or RuntimeConfig.from_env()
        self._memory_profile = memory_profile
        self._sanitization_config = sanitization_config

        self._di = DIContainer(self._config, self._memory_profile)
        self._initialized = False

        # Lazy agent subsystem
        self._agent_loader: AgentLoader | None = None
        self._agent_registry: AgentRegistry | None = None
        self._orchestrator: AgentOrchestrator | None = None

    # --- SystemRuntime Implementation ---

    async def start(self) -> None:
        """
        Initialize all eager services (LLM, memory, tools, telemetry).

        Must be called before any other operations.
        """
        if self._initialized:
            return

        logger.info("Starting RuntimeKernel...")
        await self._di.boot()
        self._initialized = True
        logger.info("RuntimeKernel started successfully")

    async def stop(self) -> None:
        """
        Gracefully shut down all services.

        Flushes logs, persists memory state, and releases resources.
        Safe to call multiple times.
        """
        logger.info("Stopping RuntimeKernel...")
        await self._di.shutdown()
        self._initialized = False
        logger.info("RuntimeKernel stopped")

    async def create_session(self, user_id: str = "default") -> str:
        """
        Create a new session identifier.

        Phase 1 stub: returns a UUID string without persistent
        session tracking.

        Args:
            user_id: User identifier for the session.

        Returns:
            A unique session ID string.
        """
        session_id = str(uuid.uuid4())
        logger.debug(f"Created session {session_id} for user {user_id}")
        return session_id

    def spawn_agent(self, name: str) -> Any:
        """
        Create an agent instance by name from the registry.

        Args:
            name: Registered agent name.

        Returns:
            Configured agent instance.

        Raises:
            KeyError: If no agent profile exists with the given name.
            RuntimeError: If kernel not started or no factory configured.
        """
        self._ensure_initialized()
        return self.agent_registry.create_agent(name)

    async def execute_workflow(
        self,
        workflow_name: str,
        initial_inputs: dict[str, Any] | None = None,
    ) -> Any:
        """
        Load and execute a named workflow definition.

        Args:
            workflow_name: Name of the workflow to execute.
            initial_inputs: Optional initial variable bindings.

        Returns:
            WorkflowExecution with final state.
        """
        self._ensure_initialized()
        from friday_agent.workflows import WorkflowEngine, WorkflowLoader
        from friday_memory import ScratchPadStore

        loader = WorkflowLoader(Path(self._config.agents_dir or "agents") / "workflows")
        workflow = loader.load(workflow_name)

        scratchpad = ScratchPadStore()
        engine = WorkflowEngine(
            orchestrator=self.orchestrator,
            scratchpad=scratchpad,
        )
        return await engine.execute(workflow, initial_inputs)

    # --- Eager Service Accessors ---

    @property
    def config(self) -> RuntimeConfig:
        """Get runtime configuration."""
        return self._config

    @property
    def memory_profile(self) -> MemoryProfile:
        """Get current memory profile."""
        return self._memory_profile

    @property
    def telemetry(self) -> Any:
        """Get telemetry interface (may be None if disabled)."""
        return self._di.telemetry

    @property
    def llm(self) -> Any:
        """Get LLM service."""
        self._ensure_initialized()
        return self._di.llm

    @property
    def embeddings(self) -> Any:
        """Get embedding service."""
        self._ensure_initialized()
        return self._di.embeddings

    @property
    def memory(self) -> Any:
        """Get memory controller."""
        self._ensure_initialized()
        return self._di.memory

    @property
    def context_engine(self) -> Any:
        """Get context assembler."""
        self._ensure_initialized()
        return self._di.context_engine

    @property
    def multi_agent_memory(self) -> Any:
        """Get multi-agent memory facade when multi-agent mode is enabled."""
        self._ensure_initialized()
        return self._di.multi_agent_memory

    @property
    def tool_registry(self) -> DefaultToolRegistry:
        """Get tool registry."""
        self._ensure_initialized()
        assert self._di.tool_registry is not None
        return self._di.tool_registry

    # --- Lazy Agent Subsystem ---

    @property
    def agent_loader(self) -> AgentLoader:
        """
        Get or create the agent loader (lazy).

        Created on first access. Raises if agents_dir is missing.
        """
        if self._agent_loader is None:
            agents_dir = (
                Path(self._config.agents_dir)
                if self._config.agents_dir
                else Path("agents")
            )
            self._agent_loader = AgentLoader(agents_dir)
        return self._agent_loader

    @property
    def agent_registry(self) -> AgentRegistry:
        """
        Get or create the agent registry (lazy).

        Auto-configured with:
        - AgentLoader for YAML loading
        - Factory for agent instantiation
        - All agents from the agents directory (if it exists)
        """
        if self._agent_registry is None:
            self._agent_registry = AgentRegistry(self.agent_loader)
            self._agent_registry.set_factory(self._create_agent)

            try:
                self._agent_registry.load_all_from_directory()
            except Exception as e:
                logger.warning(f"Could not load agents from directory: {e}")

        return self._agent_registry

    @property
    def orchestrator(self) -> AgentOrchestrator:
        """
        Get or create the agent orchestrator (lazy).

        Configured with the agent registry and first available agent
        as the default.
        """
        if self._orchestrator is None:
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
            profile: Agent profile (uses default if not provided).

        Returns:
            Configured CopilotAgent instance.
        """
        self._ensure_initialized()

        if profile is None:
            profile = self._default_profile()

        return CopilotAgent(
            profile=profile,
            memory=self.memory,
            context_engine=self.context_engine,
            llm=self.llm,
            tool_registry=self.tool_registry,
            telemetry=self.telemetry,
            sanitization_config=self._sanitization_config,
        )

    def get_team_agent(self, name: str) -> Any:
        """
        Get or create a named agent from the registry.

        Args:
            name: Agent name from registry.

        Returns:
            Configured agent instance.
        """
        self._ensure_initialized()
        return self.agent_registry.create_agent(name)

    def list_available_agents(self) -> list[str]:
        """
        List available agent names from the registry.

        Returns:
            Sorted list of agent names.
        """
        return self.agent_registry.list_agents()

    def get_agent_info(self, name: str) -> dict | None:
        """
        Get information about an agent.

        Args:
            name: Agent name.

        Returns:
            Dict with agent info or None if not found.
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

    # --- Private Helpers ---

    def _ensure_initialized(self) -> None:
        """Raise if kernel not started."""
        if not self._initialized:
            raise RuntimeError("RuntimeKernel not started. Call start() first.")

    def _create_agent(self, profile: AgentProfile) -> CopilotAgent:
        """
        Factory function for creating agents from profiles.

        Used by AgentRegistry when create_agent() is called.

        Args:
            profile: Agent profile to instantiate.

        Returns:
            Configured CopilotAgent instance.
        """
        return CopilotAgent(
            profile=profile,
            memory=self.memory,
            context_engine=self.context_engine,
            llm=self.llm,
            tool_registry=self.tool_registry,
            telemetry=self.telemetry,
            sanitization_config=self._sanitization_config,
        )

    def _default_profile(self) -> AgentProfile:
        """Create default agent profile."""
        return AgentProfile(
            name="Friday",
            role="Personal Assistant",
            goal="Help users accomplish their tasks efficiently and accurately",
            system_prompt_template=(
                "You are {name}, a {role}.\n\n"
                "Your goal: {goal}\n\n"
                "You have access to a persistent memory system. "
                "Use the available tools to:\n"
                "- Remember important information with store_fact\n"
                "- Recall relevant context with recall_memory\n"
                "- Save working notes with scratchpad_write\n\n"
                "Be helpful, accurate, and concise in your responses."
            ),
            tools=[
                "recall_memory",
                "store_fact",
                "scratchpad_write",
                "scratchpad_read",
                "scratchpad_list",
            ],
            temperature=0.7,
        )
