"""
Agent Base Abstract Class.

Defines the shared foundation for all agent implementations.
Handles memory integration, tool resolution, and telemetry.

Tool Selection Integration (Phase 5):
- Supports tool_autonomy modes: "manual", "auto", "hybrid"
- Manages _active_tools state for task-scoped tool selection
- Integrates with context_engine for tool context management
- Provides set_tools_for_task(), expand_tools(), clear_tools()

Ref: Batch 3 Specification, Section 4.2
Ref: docs/build-plan/tool-calling-build-plan.md, Phase 5
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any

from friday_core import TelemetryInterface
from friday_core.interfaces import (
    ChatCompletionResponse,
    ContextEngineeringInterface,
    LLMClient,
    ToolRegistry,
)

from friday_memory import InteractionTurn, MemoryController, SessionState

from .profile import AgentProfile

logger = logging.getLogger(__name__)


class AgentBase(ABC):
    """
    Abstract base class for all Friday agents.

    Provides common infrastructure for:
    - Session management
    - Tool schema resolution
    - Tool execution with async support
    - Memory integration (archiving turns)
    - Telemetry instrumentation

    Subclasses implement the `run()` method with their specific
    execution strategy (e.g., Re-Act loop, autonomous planning).

    Example:
        class MyAgent(AgentBase):
            async def run(self, input_signal: str) -> str:
                # Implement agent logic
                pass
    """

    def __init__(
        self,
        profile: AgentProfile,
        memory: MemoryController,
        context_engine: ContextEngineeringInterface,
        llm: LLMClient,
        tool_registry: ToolRegistry,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        """
        Initialize the agent base.

        Args:
            profile: Agent identity and configuration
            memory: MemoryController for memory operations
            context_engine: Context assembly strategy
            llm: LLM client for inference
            tool_registry: Registry for tool resolution
            telemetry: Optional telemetry recorder
        """
        self.profile = profile
        self.memory = memory
        self.context_engine = context_engine
        self.llm = llm
        self.tool_registry = tool_registry
        self.telemetry = telemetry

        # Session state (initialized on first run or via initialize_session)
        self.session_id: str = str(uuid.uuid4())
        self.session_state: SessionState | None = None

        # Conversation history for the current session
        self._conversation_history: list[dict[str, Any]] = []

        # Active tools for the current task (tool selection integration)
        # When populated, _get_tool_schemas() uses these instead of profile.tools
        self._active_tools: list[dict[str, Any]] = []
        self._active_tool_names: set[str] = set()

    @abstractmethod
    async def run(self, input_signal: Any) -> Any:
        """
        Execute the agent's main logic.

        This is the primary entry point for agent execution.
        Subclasses implement their specific execution strategy here.

        Args:
            input_signal: The input to process (typically user message)

        Returns:
            The agent's response (type depends on implementation)
        """
        pass

    # --- Session Management ---

    async def initialize_session(
        self, session_id: str | None = None, user_id: str = "default"
    ) -> SessionState:
        """
        Initialize or restore a session.

        Args:
            session_id: Optional session ID (generates new if not provided)
            user_id: User identifier

        Returns:
            Initialized SessionState
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.session_state = await self.context_engine.initialize_session(
            self.session_id, user_id
        )
        self._conversation_history = []
        return self.session_state

    # --- Tool Selection Management ---

    def set_tools_for_task(self, tool_names: list[str]) -> None:
        """
        Set the active tools for the current task.

        Resolves tool names to schemas and updates the context engine.
        Used at the start of a task to select which tools are available.

        Args:
            tool_names: List of tool names to activate.

        Example:
            agent.set_tools_for_task(["read_file", "write_file", "list_directory"])
        """
        schemas = []
        for name in tool_names:
            try:
                schema = self.tool_registry.get_schema(name)
                schemas.append(schema)
            except (KeyError, AttributeError):
                logger.warning(f"Tool '{name}' not found in registry, skipping")

        self._active_tools = schemas
        self._active_tool_names = {s.get("name", "") for s in schemas}

        # Notify context engine of active tools
        if hasattr(self.context_engine, "set_active_tools"):
            self.context_engine.set_active_tools(schemas)

        self._emit_event(
            "tools_set_for_task",
            {"tool_count": len(schemas), "tool_names": list(self._active_tool_names)},
        )
        logger.debug(f"Set {len(schemas)} active tools for task: {list(self._active_tool_names)}")

    def expand_tools(self, additional_tool_names: list[str]) -> int:
        """
        Expand active tools with additional ones.

        Used in hybrid mode when an agent needs to add more tools
        mid-task without replacing the existing set.

        Args:
            additional_tool_names: Tool names to add to the active set.

        Returns:
            Number of tools actually added.
        """
        added = 0
        for name in additional_tool_names:
            if name in self._active_tool_names:
                continue  # Already active

            try:
                schema = self.tool_registry.get_schema(name)
                self._active_tools.append(schema)
                self._active_tool_names.add(name)
                added += 1
            except (KeyError, AttributeError):
                logger.warning(f"Tool '{name}' not found in registry, skipping")

        if added > 0:
            # Update context engine
            if hasattr(self.context_engine, "set_active_tools"):
                self.context_engine.set_active_tools(self._active_tools)

            self._emit_event(
                "tools_expanded",
                {"tools_added": added, "total_tools": len(self._active_tools)},
            )
            logger.debug(f"Expanded tools by {added}, total: {len(self._active_tools)}")

        return added

    def clear_tools(self) -> None:
        """
        Clear all active tools.

        Should be called at the end of a task to reset tool state.
        """
        self._active_tools = []
        self._active_tool_names = set()

        # Notify context engine
        if hasattr(self.context_engine, "clear_tools"):
            self.context_engine.clear_tools()

        self._emit_event("tools_cleared", {})
        logger.debug("Cleared all active tools")

    def get_active_tool_names(self) -> list[str]:
        """Get list of currently active tool names."""
        return list(self._active_tool_names)

    def _initialize_tools_for_autonomy_mode(self) -> None:
        """
        Initialize tools based on the profile's tool_autonomy setting.

        Called at the start of a task to set up initial tools.

        Modes:
        - manual: Use injected_tools (or profile.tools as fallback)
        - auto: Don't pre-populate; agent will select via select_tools_for_task()
        - hybrid: Start with injected_tools; agent can expand later
        """
        autonomy = self.profile.tool_autonomy

        if autonomy == "manual":
            # Use injected tools, fallback to profile.tools
            tool_names = self.profile.injected_tools or self.profile.tools
            if tool_names:
                self.set_tools_for_task(tool_names)

        elif autonomy == "hybrid":
            # Start with injected + required tools
            initial_tools = set(self.profile.injected_tools)
            initial_tools.update(self.profile.required_tools)
            if initial_tools:
                self.set_tools_for_task(list(initial_tools))

        elif autonomy == "auto":
            # Only set required tools; agent will select rest
            if self.profile.required_tools:
                self.set_tools_for_task(self.profile.required_tools)
            # Agent should call select_tools_for_task() after analyzing the task

    # --- Tool Infrastructure ---

    def _get_tool_schemas(self) -> list[dict[str, Any]]:
        """
        Get tool schemas for LLM.

        If _active_tools is populated (via set_tools_for_task), returns those.
        Otherwise falls back to resolving profile.tools from the registry.

        Returns:
            List of OpenAI-compatible tool schemas
        """
        # Prefer active tools if set (tool selection integration)
        if self._active_tools:
            return self._active_tools

        # Fallback to profile.tools (legacy behavior)
        schemas = []
        for tool_name in self.profile.tools:
            try:
                schema = self.tool_registry.get_schema(tool_name)
                schemas.append(schema)
            except KeyError:
                logger.warning(f"Tool '{tool_name}' not found in registry")
        return schemas

    async def _execute_tool_call(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> str:
        """
        Execute a tool and return the result as a string.

        Handles both sync and async tool functions.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool

        Returns:
            String representation of the tool result

        Raises:
            KeyError: If tool not found in registry
            Exception: If tool execution fails
        """
        span_id = None
        if self.telemetry:
            span_id = self.telemetry.start_span(
                "tool_execution", parent_id=None
            )
            self.telemetry.capture_event(
                "tool_call_started",
                {"tool": tool_name, "arguments": str(arguments)[:200]},
            )

        try:
            func = self.tool_registry.get_tool(tool_name)

            # Execute (supports both sync and async)
            if asyncio.iscoroutinefunction(func):
                result = await func(**arguments)
            else:
                result = func(**arguments)

            result_str = str(result)

            if self.telemetry:
                self.telemetry.capture_event(
                    "tool_call_completed",
                    {
                        "tool": tool_name,
                        "result_length": len(result_str),
                        "success": True,
                    },
                )

            return result_str

        except Exception as e:
            error_msg = f"Tool execution failed: {e}"
            logger.error(f"Error executing tool '{tool_name}': {e}")

            if self.telemetry:
                self.telemetry.capture_event(
                    "tool_call_failed",
                    {"tool": tool_name, "error": str(e)},
                )

            return error_msg

        finally:
            if span_id and self.telemetry:
                self.telemetry.end_span(span_id)

    # --- Memory Integration ---

    async def _archive_turn(
        self,
        user_message: str | None = None,
        assistant_message: str | None = None,
        tool_calls: list[dict[str, Any]] | None = None,
        tool_results: list[dict[str, Any]] | None = None,
    ) -> None:
        """
        Archive an interaction turn to episodic memory.

        Also triggers async context extraction for learning.

        Args:
            user_message: The user's input message
            assistant_message: The assistant's response
            tool_calls: List of tool calls made
            tool_results: List of tool results
        """
        from friday_memory.models import (
            ToolCall as MemoryToolCall,
            ToolResult as MemoryToolResult,
        )

        # Create turn record
        turn = InteractionTurn(
            id=str(uuid.uuid4()),
            session_id=self.session_id,
            user_message=user_message,
            assistant_message=assistant_message,
            tool_calls=[
                MemoryToolCall(**tc) for tc in (tool_calls or [])
            ],
            tool_results=[
                MemoryToolResult(**tr) for tr in (tool_results or [])
            ],
        )

        # Store in episodic memory
        success = await self.memory.add_turn(self.session_id, turn)
        if not success:
            logger.error(f"Failed to persist turn {turn.id} to memory")

        # Trigger async extraction (non-blocking)
        # This allows the agent to continue while extraction happens in background
        asyncio.create_task(
            self._safe_extract_context(turn)
        )

        if self.telemetry:
            self.telemetry.capture_event(
                "turn_archived",
                {
                    "session_id": self.session_id,
                    "has_user_message": user_message is not None,
                    "has_assistant_message": assistant_message is not None,
                    "tool_calls_count": len(tool_calls or []),
                },
            )

    async def _safe_extract_context(self, turn: InteractionTurn) -> None:
        """
        Safely execute context extraction, logging any errors.

        This runs in the background and should not fail the main flow.
        """
        try:
            await self.context_engine.extract_context(turn, async_execution=True)
        except Exception as e:
            logger.warning(f"Context extraction failed: {e}")

    # --- Conversation Management ---

    def _add_to_history(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self._conversation_history.append({"role": role, "content": content})

    def _add_tool_call_to_history(
        self,
        tool_calls: list[dict[str, Any]],
        tool_results: list[str],
    ) -> None:
        """
        Add tool call and results to conversation history.

        Formats tool interactions for LLM context.
        """
        # Add assistant message with tool calls
        self._conversation_history.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": str(tc["arguments"]),
                    },
                }
                for tc in tool_calls
            ],
        })

        # Add tool results
        for tc, result in zip(tool_calls, tool_results):
            self._conversation_history.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result,
            })

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self._conversation_history = []

    # --- Telemetry Helpers ---

    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event if configured."""
        if self.telemetry:
            self.telemetry.capture_event(event_name, data)
