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
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from friday_agent import (
    AgentLoader,
    AgentOrchestrator,
    AgentProfile,
    AgentRegistry,
    AutonomousAgent,
    CopilotAgent,
    DefaultToolRegistry,
    InteractiveAgent,
)
from friday_core.interfaces import ToolRegistry
from friday_core.interfaces.runtime import SystemRuntime
from friday_core.profiles import MemoryProfile
from friday_core.security import SanitizationConfig

from friday_runtime.config import RuntimeConfig
from friday_runtime.di import DIContainer
from friday_runtime.mcp_loading import RuntimeMCPProvider
from friday_runtime.tool_loading import (
    collect_profile_tool_references,
    validate_agent_tool_bindings,
)

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
        self._agent_factories: dict[str, Callable[[AgentProfile], Any]] = {
            "interactive": self._create_interactive_agent,
            "autonomous": self._create_autonomous_agent,
        }

    # --- SystemRuntime Implementation ---

    async def start(self) -> None:
        """
        Initialize all eager services (LLM, memory, tools, telemetry).

        Must be called before any other operations.
        """
        if self._initialized:
            return

        logger.info("Starting RuntimeKernel...")
        try:
            await self._di.boot()
            self._agent_registry = self._build_agent_registry()
        except BaseException:
            await self._di.shutdown()
            raise
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

        workflow_session_id = await self.create_session(user_id="workflow")
        await self.orchestrator.set_session(workflow_session_id, user_id="workflow")

        loader = WorkflowLoader(self._resolve_workflows_dir())
        scratchpad = ScratchPadStore()
        engine = WorkflowEngine(
            orchestrator=self.orchestrator,
            scratchpad=scratchpad,
            telemetry=self.telemetry,
            agent_info_resolver=self.get_agent_info,
        )

        if self._config.workflow_mode == "legacy":
            bundle = loader.load_legacy_as_canonical(workflow_name)
            self._emit_workflow_routing_event(
                workflow_name=workflow_name,
                requested_mode="legacy",
                resolved_mode="legacy_adapter",
            )
            return await engine.execute_canonical(
                bundle.workflow,
                bundle.pipelines,
                initial_inputs,
                role_bindings=self._config.agents_role_bindings,
                execution_id=workflow_session_id,
            )

        if self._config.workflow_mode == "canonical":
            bundle = loader.load_canonical(workflow_name)
            self._emit_workflow_routing_event(
                workflow_name=workflow_name,
                requested_mode="canonical",
                resolved_mode="canonical",
            )
            return await engine.execute_canonical(
                bundle.workflow,
                bundle.pipelines,
                initial_inputs,
                role_bindings=self._config.agents_role_bindings,
                execution_id=workflow_session_id,
            )

        # auto mode: attempt canonical first, then fall back to legacy path.
        try:
            bundle = loader.load_canonical(workflow_name)
        except Exception:
            bundle = loader.load_legacy_as_canonical(workflow_name)
            logger.warning(
                "Canonical workflow load failed for '%s'; using legacy adapter path",
                workflow_name,
            )
            self._emit_workflow_routing_event(
                workflow_name=workflow_name,
                requested_mode="auto",
                resolved_mode="legacy_adapter",
            )
            return await engine.execute_canonical(
                bundle.workflow,
                bundle.pipelines,
                initial_inputs,
                role_bindings=self._config.agents_role_bindings,
                execution_id=workflow_session_id,
            )

        self._emit_workflow_routing_event(
            workflow_name=workflow_name,
            requested_mode="auto",
            resolved_mode="canonical",
        )
        return await engine.execute_canonical(
            bundle.workflow,
            bundle.pipelines,
            initial_inputs,
            role_bindings=self._config.agents_role_bindings,
            execution_id=workflow_session_id,
        )

    # --- Eager Service Accessors ---

    @property
    def mcp_provider(self) -> RuntimeMCPProvider | None:
        """Inspect MCP lifetime and redacted diagnostics, including failed boot."""
        return self._di.mcp_provider

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
            self._agent_registry = self._build_agent_registry()

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

    def register_agent_factory(
        self,
        agent_type: str,
        factory: Callable[[AgentProfile], Any],
    ) -> None:
        """Register or override a runtime factory for a profile `agent_type`."""
        self._agent_factories[agent_type] = factory

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
            llm=self._get_llm_for_profile(profile),
            tool_registry=self._tool_registry_interface(),
            telemetry=self.telemetry,
            sanitization_config=self._sanitization_config,
        )

    def get_interactive_agent(
        self,
        profile: AgentProfile | None = None,
    ) -> InteractiveAgent:
        """
        Create an InteractiveAgent with all dependencies wired.

        Args:
            profile: Agent profile (uses default if not provided).

        Returns:
            Configured InteractiveAgent instance.
        """
        self._ensure_initialized()

        if profile is None:
            profile = self._default_profile()

        return InteractiveAgent(
            profile=profile,
            memory=self.memory,
            context_engine=self.context_engine,
            llm=self._get_llm_for_profile(profile),
            tool_registry=self._tool_registry_interface(),
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
        return cast(list[str], self.agent_registry.list_agents())

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
            "llm_service": self._resolve_llm_service_name(profile),
            "agent_type": profile.agent_type,
            "capabilities": profile.capabilities,
            "tools": profile.tools,
            "tool_autonomy": profile.tool_autonomy,
        }

    # --- Private Helpers ---

    def _ensure_initialized(self) -> None:
        """Raise if kernel not started."""
        if not self._initialized:
            raise RuntimeError("RuntimeKernel not started. Call start() first.")

    def _build_agent_registry(self) -> AgentRegistry:
        """Create and validate the registry against runtime LLM bindings."""
        registry = AgentRegistry(self.agent_loader)
        registry.set_factory(self._create_agent)

        if self.agent_loader.agents_dir.exists():
            registry.load_all_from_directory()
            self._validate_agent_profiles(registry.list_profiles())

        return registry

    def _resolve_workflows_dir(self) -> Path:
        """Resolve workflow bundle root for runtime workflow execution."""
        configured = self._config.workflows_dir
        if configured:
            raw = Path(configured).expanduser()
            if raw.is_absolute():
                return raw.resolve()
            install_root = Path(self._config.install_root or ".").expanduser().resolve()
            return (install_root / raw).resolve()

        agents_dir = Path(self._config.agents_dir or "agents")
        return (agents_dir / "workflows").resolve()

    def _validate_agent_profiles(self, profiles: list[AgentProfile]) -> None:
        """Fail startup deterministically on invalid agent/runtime bindings."""
        registry = self._di.tool_registry
        if registry is None:
            raise RuntimeError("Runtime tool registry not initialized during startup")

        available_tool_names = set(cast(list[str], registry.list_names()))
        for profile in profiles:
            resolved_service = self._resolve_llm_service_name(profile)
            self._resolve_agent_factory(profile.agent_type)
            validate_agent_tool_bindings(
                agent_name=profile.name,
                declared_tools=collect_profile_tool_references(profile),
                available_tool_names=available_tool_names,
            )
            logger.debug(
                "Validated agent '%s' LLM binding to service '%s' (agent_type=%s)",
                profile.name,
                resolved_service,
                profile.agent_type,
            )

    def _resolve_llm_service_name(self, profile: AgentProfile) -> str:
        """Resolve the effective runtime LLM service for a profile."""
        if profile.llm_service is not None:
            if profile.llm_service not in self._config.llm_pool.services:
                raise ValueError(
                    f"Agent '{profile.name}' references unknown llm_service "
                    f"'{profile.llm_service}'"
                )
            return cast(str, profile.llm_service)

        if self._config.strict_agent_llm_binding:
            raise ValueError(
                f"Agent '{profile.name}' must declare llm_service when "
                "strict_agent_llm_binding is enabled"
            )

        return cast(str, self._config.llm_pool.default_service)

    def _get_llm_for_profile(self, profile: AgentProfile) -> Any:
        """Return the configured runtime LLM client for the agent profile."""
        service_name = self._resolve_llm_service_name(profile)
        try:
            return self._di.llm_pool[service_name]
        except KeyError as exc:
            raise RuntimeError(
                f"Runtime LLM pool missing configured service '{service_name}'"
            ) from exc

    def _get_llm_service_config_for_profile(self, profile: AgentProfile) -> Any:
        """Return the resolved runtime LLM service config for the profile."""
        return self._config.get_llm_service_config(self._resolve_llm_service_name(profile))

    def _resolve_agent_factory(self, agent_type: str) -> Callable[[AgentProfile], Any]:
        """Resolve the runtime factory for the profile `agent_type`."""
        try:
            return self._agent_factories[agent_type]
        except KeyError as exc:
            raise ValueError(
                f"Unregistered agent_type '{agent_type}' for runtime factory mapping"
            ) from exc

    def _create_agent(self, profile: AgentProfile) -> Any:
        """
        Factory function for creating agents from profiles.

        Used by AgentRegistry when create_agent() is called.

        Args:
            profile: Agent profile to instantiate.

        Returns:
            Configured agent instance.
        """
        return self._resolve_agent_factory(profile.agent_type)(profile)

    def _tool_registry_interface(self) -> ToolRegistry:
        """Return the registry narrowed to the protocol expected by agents."""
        return cast(ToolRegistry, self.tool_registry)

    def _create_interactive_agent(self, profile: AgentProfile) -> InteractiveAgent:
        """Create the default interactive runtime agent."""
        llm_service_config = self._get_llm_service_config_for_profile(profile)
        return InteractiveAgent(
            profile=profile,
            memory=self.memory,
            context_engine=self.context_engine,
            llm=self._get_llm_for_profile(profile),
            tool_registry=self._tool_registry_interface(),
            telemetry=self.telemetry,
            sanitization_config=self._sanitization_config,
            runtime_base_system_prompt=self._config.prompting.base_system_prompt,
            resolved_llm_service_name=self._resolve_llm_service_name(profile),
            resolved_provider_name=llm_service_config.provider,
        )

    def _create_autonomous_agent(self, profile: AgentProfile) -> AutonomousAgent:
        """Create the autonomous runtime agent."""
        llm_service_config = self._get_llm_service_config_for_profile(profile)
        return AutonomousAgent(
            profile=profile,
            memory=self.memory,
            context_engine=self.context_engine,
            llm=self._get_llm_for_profile(profile),
            tool_registry=self._tool_registry_interface(),
            telemetry=self.telemetry,
            sanitization_config=self._sanitization_config,
            runtime_base_system_prompt=self._config.prompting.base_system_prompt,
            resolved_llm_service_name=self._resolve_llm_service_name(profile),
            resolved_provider_name=llm_service_config.provider,
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
            llm_service=self._config.llm_pool.default_service,
            agent_type="interactive",
        )

    def _emit_workflow_routing_event(
        self,
        *,
        workflow_name: str,
        requested_mode: str,
        resolved_mode: str,
    ) -> None:
        """Emit auditable workflow routing information when telemetry is enabled."""
        if self.telemetry is None:
            return
        self.telemetry.capture_event(
            "workflow_mode_selected",
            {
                "workflow_name": workflow_name,
                "requested_mode": requested_mode,
                "resolved_mode": resolved_mode,
            },
        )
