from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Type

from pydantic import BaseModel, Field
from friday_core.interfaces import ToolDefinition


class ToolResult(BaseModel):
    """
    Standardized return object for all Friday Tools.
    
    Attributes:
        content: The human-readable string representation (for LLM context).
        data: The raw structured data (for Memory/Code analysis).
        metadata: Additional context (e.g., execution time, source IDs).
        error: Optional error message if execution failed.
    """
    content: str
    data: Any | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None

    def __str__(self) -> str:
        """String representation prioritizes content or error."""
        if self.error:
            return f"Error: {self.error}"
        return self.content


class FridayTool(ToolDefinition, ABC):
    """
    Abstract base class for Friday Tools with automatic Pydantic Schema generation.

    Subclasses must:
    1. Define `name` and `description`.
    2. Define `Input` (a Pydantic BaseModel) as a class attribute.
    3. Implement `run(self, args: Input) -> ToolResult`.

    Optional:
    - Define `category` (default: "uncategorized")
    - Define `tags` (default: [])
    """

    name: str
    description: str
    category: str = "uncategorized"
    tags: list[str] = []
    Input: Type[BaseModel]

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Generate JSON Schema from the Input Pydantic model."""
        return self.Input.model_json_schema()

    def to_schema(self, format: str = "plain") -> dict[str, Any]:
        """
        Convert tool to JSON schema format.

        Args:
            format: "plain" (default) or "openai".
        """
        base_schema = {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
            "category": self.category,
            "tags": self.tags,
        }

        if format == "openai":
            return {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": self.description,
                    "parameters": self.parameters_schema,
                },
                "category": self.category,
                "tags": self.tags,
            }
        return base_schema

    async def execute(self, **kwargs: Any) -> str:
        """
        Execute the tool. This is the entry point for Agents.
        
        It handles:
        1. Validation (converting kwargs -> Input model).
        2. Execution (calling run()).
        3. Serialization (converting ToolResult -> str).
        """
        try:
            # Validate input
            validated_args = self.Input(**kwargs)
            
            # Run implementation
            result = await self.run(validated_args)
            
            # Return string content for LLM
            return str(result)
            
        except Exception as e:
            # Catch validation or execution errors
            return f"Error executing tool '{self.name}': {str(e)}"

    @abstractmethod
    async def run(self, args: BaseModel) -> ToolResult:
        """
        Implementation logic for the tool.
        
        Args:
            args: The validated Input model.
            
        Returns:
            A ToolResult object containing structured data.
        """
        pass
