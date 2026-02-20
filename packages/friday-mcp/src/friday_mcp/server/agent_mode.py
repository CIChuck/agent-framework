"""
Agent Mode MCP Server.

Exposes a Friday agent as an MCP server.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Protocol, runtime_checkable

from friday_mcp.config import MCPServerSettings
from friday_mcp.server.base import MCPServerBase

logger = logging.getLogger(__name__)


@runtime_checkable
class AgentLike(Protocol):
    """Protocol for agent compatibility."""

    async def run(self, input_signal: str) -> str:
        """Execute a task and return the result."""
        ...


@runtime_checkable
class AgentProfileLike(Protocol):
    """Protocol for agent profile compatibility."""

    @property
    def name(self) -> str:
        """Agent name."""
        ...

    @property
    def role(self) -> str:
        """Agent role."""
        ...

    @property
    def goal(self) -> str:
        """Agent goal."""
        ...

    def render_system_prompt(self, **kwargs: Any) -> str:
        """Render the system prompt template."""
        ...


def configure_agent_mode(
    server: MCPServerBase,
    agent: AgentLike,
    profile: AgentProfileLike,
    settings: MCPServerSettings,
) -> None:
    """
    Configure an MCP server for agent mode.

    Registers:
    - Main agent tool (calls agent.run())
    - Agent prompts (if expose_prompts=True)
    - Context resources (if expose_resources=True)

    Args:
        server: MCP server instance
        agent: Friday agent instance (implements AgentLike)
        profile: Agent profile (implements AgentProfileLike)
        settings: Server settings

    Example:
        from friday_mcp import StdioMCPServer, MCPServerSettings
        from friday_mcp.server.agent_mode import configure_agent_mode

        server = StdioMCPServer()
        configure_agent_mode(server, agent, profile, MCPServerSettings())
        await server.start()
    """

    # Register main agent tool
    async def agent_handler(task: str) -> str:
        """Execute a task using the Friday agent."""
        logger.info(f"Agent executing task: {task[:50]}...")
        result = await agent.run(task)
        logger.info("Agent completed task")
        return result

    server.register_tool(
        name=settings.agent_tool_name,
        description=settings.agent_tool_description,
        input_schema={
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task or question for the agent to process",
                },
            },
            "required": ["task"],
        },
        handler=agent_handler,
    )

    # Register prompts
    if settings.expose_prompts:
        _register_prompts(server, profile)

    # Register resources
    if settings.expose_resources:
        _register_resources(server, profile)

    logger.info(f"Configured agent mode for: {profile.name}")


def _register_prompts(
    server: MCPServerBase,
    profile: AgentProfileLike,
) -> None:
    """Register agent prompts."""

    def get_system_prompt(**kwargs: Any) -> dict[str, Any]:
        """Get the agent's system prompt."""
        try:
            prompt_text = profile.render_system_prompt(**kwargs)
        except Exception:
            # Fallback if render_system_prompt fails
            prompt_text = f"You are {profile.name}, a {profile.role}. Your goal is: {profile.goal}"  # noqa: E501

        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": {
                        "type": "text",
                        "text": prompt_text,
                    },
                },
            ],
        }

    server.register_prompt(
        name="system_prompt",
        description=f"System prompt for {profile.name}",
        arguments=[
            {
                "name": "context",
                "description": "Additional context variables for prompt rendering",
                "required": False,
            },
        ],
        handler=get_system_prompt,
    )

    def get_agent_info() -> dict[str, Any]:
        """Get basic information about the agent."""
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": {
                        "type": "text",
                        "text": f"Agent: {profile.name}\nRole: {profile.role}\nGoal: {profile.goal}",  # noqa: E501
                    },
                },
            ],
        }

    server.register_prompt(
        name="agent_info",
        description="Basic information about this agent",
        arguments=None,
        handler=get_agent_info,
    )


def _register_resources(
    server: MCPServerBase,
    profile: AgentProfileLike,
) -> None:
    """Register agent resources."""

    def get_agent_profile() -> dict[str, Any]:
        """Get the agent's profile as a resource."""
        profile_data = {
            "name": profile.name,
            "role": profile.role,
            "goal": profile.goal,
        }
        return {
            "contents": [
                {
                    "uri": "friday://agent/profile",
                    "mimeType": "application/json",
                    "text": json.dumps(profile_data, indent=2),
                },
            ],
        }

    server.register_resource(
        uri="friday://agent/profile",
        name="Agent Profile",
        description="The agent's profile configuration",
        mime_type="application/json",
        handler=get_agent_profile,
    )


def create_simple_profile(
    name: str,
    role: str,
    goal: str,
) -> AgentProfileLike:
    """
    Create a simple agent profile for testing.

    Args:
        name: Agent name
        role: Agent role
        goal: Agent goal

    Returns:
        Simple profile implementing AgentProfileLike
    """

    class SimpleProfile:
        def __init__(self, name: str, role: str, goal: str):
            self._name = name
            self._role = role
            self._goal = goal

        @property
        def name(self) -> str:
            return self._name

        @property
        def role(self) -> str:
            return self._role

        @property
        def goal(self) -> str:
            return self._goal

        def render_system_prompt(self, **kwargs: Any) -> str:
            context = kwargs.get("context", "")
            base = f"You are {self._name}, a {self._role}. Your goal is: {self._goal}"
            if context:
                base += f"\n\nAdditional context: {context}"
            return base

    return SimpleProfile(name, role, goal)
