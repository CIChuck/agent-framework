"""
Agent Profile Definition.

Defines agent identity, capabilities, and configuration.
Serializable to YAML/JSON for config-driven agents.

Ref: Batch 3 Specification, Section 4.1
"""

from dataclasses import dataclass, field


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

    Example:
        profile = AgentProfile(
            name="Friday",
            role="Personal Assistant",
            goal="Help users with research and organization",
            system_prompt_template="You are {name}, a {role}. Your goal: {goal}",
            tools=["recall_memory", "scratchpad_write", "web_search"],
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

    def render_system_prompt(self, **kwargs) -> str:
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
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentProfile":
        """Deserialize profile from dictionary."""
        return cls(
            name=data["name"],
            role=data["role"],
            goal=data["goal"],
            system_prompt_template=data["system_prompt_template"],
            tools=data.get("tools", []),
            context_strategy=data.get("context_strategy", "standard"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens"),
        )
