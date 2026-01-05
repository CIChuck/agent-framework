"""
Agent Base Abstract Class.

Defines the shared foundation for all agent implementations.
Handles memory integration, tool resolution, and telemetry.

Ref: Batch 3 Specification, Section 4.2
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

    # --- Tool Infrastructure ---

    def _get_tool_schemas(self) -> list[dict[str, Any]]:
        """
        Resolve profile.tools to JSON schemas for LLM.

        Returns:
            List of OpenAI-compatible tool schemas
        """
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
        await self.memory.add_turn(self.session_id, turn)

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
