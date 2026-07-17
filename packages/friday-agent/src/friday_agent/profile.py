"""
Agent Profile Definition.

Defines agent identity, capabilities, and configuration.
Serializable to YAML/JSON for config-driven agents.

Ref: Batch 3 Specification, Section 4.1
Ref: docs/archive/build-plans/completed/friday-core-legacy/tool-calling-build-plan.md, Phase 5
"""

from dataclasses import dataclass, field
from typing import Any, Literal

# Tool autonomy modes
ToolAutonomy = Literal["manual", "auto", "hybrid"]
AgentType = Literal["interactive", "autonomous", "custom"]


@dataclass
class AgentProfile:
    """
    Defines agent identity and capabilities.

    Attributes:
        name: Human-readable agent name
        role: Agent's role description (e.g., "Research Assistant")
        goal: Primary objective for the agent
        system_prompt_template: Template with placeholders for dynamic context
        tools: List of tool names (resolved via ToolRegistry)
        context_strategy: Context assembly strategy name
        temperature: LLM sampling temperature
        max_tokens: Maximum tokens for LLM response

        # Tool autonomy settings
        tool_autonomy: Tool selection mode ("manual", "auto", "hybrid")
        injected_tools: Tools always included (for manual/hybrid modes)
        available_tools: Pool of tools for auto-selection (for auto/hybrid modes)
        required_tools: Tools that must always be included regardless of selection

    Tool Autonomy Modes:
        - "manual": Tools must be injected at instantiation; agent cannot self-select
        - "auto": Agent self-selects tools via LLM reasoning; no injection needed
        - "hybrid": Injected tools + agent can expand with self-selection

    Example:
        profile = AgentProfile(
            name="Friday",
            role="Personal Assistant",
            goal="Help users with research and organization",
            system_prompt_template="You are {name}, a {role}. Your goal: {goal}",
            tools=["recall_memory", "scratchpad_write", "web_search"],
            tool_autonomy="hybrid",
            injected_tools=["recall_memory"],  # Always available
            available_tools=["web_search", "read_file"],  # Can be selected
        )
    """

    name: str
    role: str
    goal: str
    system_prompt_template: str

    # Tool names (resolved via ToolRegistry)
    tools: list[str] = field(default_factory=list)

    # Context strategy (maps to ContextEngineeringInterface implementations)
    context_strategy: str = "standard"

    # LLM parameters
    temperature: float = 0.7
    max_tokens: int | None = None
    llm_service: str | None = None
    agent_type: AgentType = "interactive"

    # Tool autonomy settings
    tool_autonomy: ToolAutonomy = "manual"
    injected_tools: list[str] = field(default_factory=list)
    available_tools: list[str] = field(default_factory=list)
    required_tools: list[str] = field(default_factory=list)

    # Registry integration fields (prefixed with _ to indicate internal use)
    _capabilities: list[str] = field(default_factory=list)
    _skills: list[str] = field(default_factory=list)
    _memory_config: dict[str, Any] = field(default_factory=dict)
    _metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def capabilities(self) -> list[str]:
        """Capability tags for orchestrator routing."""
        return self._capabilities

    @property
    def skills(self) -> list[str]:
        """Declared canonical skill references (`skill_id@version`)."""
        return self._skills

    @property
    def memory_config(self) -> dict[str, Any]:
        """Agent-specific memory settings."""
        return self._memory_config

    @property
    def metadata(self) -> dict[str, Any]:
        """Additional custom metadata."""
        return self._metadata

    def render_system_prompt(self, **kwargs: Any) -> str:
        """
        Render system prompt with variable substitution.

        Args:
            **kwargs: Additional variables for template substitution

        Returns:
            Rendered system prompt string

        Example:
            prompt = profile.render_system_prompt(
                current_date="2024-01-15",
                user_name="Alice"
            )
        """
        return self.system_prompt_template.format(
            name=self.name,
            role=self.role,
            goal=self.goal,
            **kwargs,
        )

    def to_dict(self) -> dict:
        """Serialize profile to dictionary for storage/transmission."""
        return {
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "system_prompt_template": self.system_prompt_template,
            "tools": self.tools,
            "context_strategy": self.context_strategy,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "llm_service": self.llm_service,
            "agent_type": self.agent_type,
            # Tool autonomy settings
            "tool_autonomy": self.tool_autonomy,
            "injected_tools": self.injected_tools,
            "available_tools": self.available_tools,
            "required_tools": self.required_tools,
            # Registry integration
            "capabilities": self._capabilities,
            "skills": self._skills,
            "memory_config": self._memory_config,
            "metadata": self._metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentProfile":
        """Deserialize profile from dictionary."""
        return cls(
            name=data["name"],
            role=data["role"],
            goal=data["goal"],
            system_prompt_template=data.get(
                "system_prompt_template", data.get("system_prompt", "")
            ),
            tools=data.get("tools", []),
            context_strategy=data.get("context_strategy", "standard"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens"),
            llm_service=data.get("llm_service"),
            agent_type=data.get("agent_type", "interactive"),
            # Tool autonomy settings
            tool_autonomy=data.get("tool_autonomy", "manual"),
            injected_tools=data.get("injected_tools", []),
            available_tools=data.get("available_tools", []),
            required_tools=data.get("required_tools", []),
            # Registry integration
            _capabilities=data.get("capabilities", []),
            _skills=data.get("skills", []),
            _memory_config=data.get("memory_config", {}),
            _metadata=data.get("metadata", {}),
        )
