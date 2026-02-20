"""
Base tool implementation.

Ref: docs/specs/tool_specification.md - Section 3: BaseTool

Provides the BaseTool class that implements ToolDefinition protocol,
making it easy to create new tools by subclassing.
"""

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, get_type_hints

from friday_core.interfaces.tools import SchemaFormat


class BaseTool(ABC):
    """
    Base class for implementing Friday tools.

    Subclass this to create new tools. Override the execute method
    and optionally customize name, description, and parameter schema.

    Example:
        ```python
        class MyTool(BaseTool):
            @property
            def name(self) -> str:
                return "my_tool"

            @property
            def description(self) -> str:
                return "Does something useful"

            @property
            def category(self) -> str:
                return "utility"

            @property
            def parameters_schema(self) -> dict[str, Any]:
                return {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string", "description": "Input value"}
                    },
                    "required": ["input"]
                }

            async def execute(self, **kwargs) -> str:
                return f"Processed: {kwargs['input']}"
        ```
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description for the LLM."""
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> dict[str, Any]:
        """JSON Schema for tool parameters."""
        pass

    @property
    def category(self) -> str:
        """
        Tool category for grouping and filtering.

        Standard categories: filesystem, shell, web, git, code, data, text, utility.
        Override this property to set a specific category.

        Returns:
            Category string, defaults to "uncategorized".
        """
        return "uncategorized"

    @property
    def tags(self) -> list[str]:
        """
        Optional tags for fine-grained filtering.

        Override this property to add tags like ["read-only", "async", "idempotent"].

        Returns:
            List of tag strings, empty list by default.
        """
        return []

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool with given arguments."""
        pass

    def to_schema(self, format: str = "plain") -> dict[str, Any]:
        """
        Convert tool to JSON schema format for LLM function calling.

        Args:
            format: Output format - "plain" or "openai".
                   "plain": {"name": ..., "description": ..., "parameters": ..., "category": ..., "tags": ...}
                   "openai": {"type": "function", "function": {...}}

        Returns:
            Dictionary suitable for LLM function calling.
        """  # noqa: E501
        plain_schema = {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
            "category": self.category,
            "tags": self.tags,
        }

        if format == SchemaFormat.OPENAI or format == "openai":
            # OpenAI format doesn't include category/tags in the function spec
            # but we include them at the top level for filtering
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

        return plain_schema


class FunctionTool(BaseTool):
    """
    Tool that wraps a Python function.

    Automatically generates schema from function signature and docstring.

    Example:
        ```python
        async def greet(name: str, greeting: str = "Hello") -> str:
            '''Greet someone by name.

            Args:
                name: The person's name.
                greeting: The greeting to use.
            '''
            return f"{greeting}, {name}!"

        tool = FunctionTool(greet, category="utility", tags=["greeting"])
        ```
    """

    def __init__(
        self,
        func: Callable,
        name: str | None = None,
        description: str | None = None,
        category: str = "uncategorized",
        tags: list[str] | None = None,
    ):
        """
        Create a tool from a function.

        Args:
            func: The function to wrap (async or sync).
            name: Override the function name.
            description: Override the function docstring.
            category: Tool category (filesystem, shell, web, etc.).
            tags: Optional list of tags for filtering.
        """
        self._func = func
        self._name = name or func.__name__
        self._description = description or func.__doc__ or f"Execute {self._name}"
        self._category = category
        self._tags = tags or []
        self._schema = self._generate_schema()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def category(self) -> str:
        return self._category

    @property
    def tags(self) -> list[str]:
        return self._tags

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return self._schema

    async def execute(self, **kwargs: Any) -> str:
        """Execute the wrapped function."""
        if inspect.iscoroutinefunction(self._func):
            result = await self._func(**kwargs)
        else:
            result = self._func(**kwargs)

        if isinstance(result, str):
            return result
        return str(result)

    def _generate_schema(self) -> dict[str, Any]:
        """Generate JSON schema from function signature."""
        sig = inspect.signature(self._func)
        hints = (
            get_type_hints(self._func) if hasattr(self._func, "__annotations__") else {}
        )

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            prop = self._type_to_schema(hints.get(param_name, str))
            prop["description"] = self._extract_param_doc(param_name)
            properties[param_name] = prop

            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }

    def _type_to_schema(self, type_hint: type) -> dict[str, Any]:
        """Convert Python type hint to JSON Schema type."""
        type_map = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            list: {"type": "array"},
            dict: {"type": "object"},
        }
        return type_map.get(type_hint, {"type": "string"})

    def _extract_param_doc(self, param_name: str) -> str:
        """Extract parameter description from docstring."""
        if not self._func.__doc__:
            return f"Parameter {param_name}"

        # Simple parsing of Google-style docstrings
        lines = self._func.__doc__.split("\n")
        in_args = False
        for line in lines:
            stripped = line.strip()
            if stripped.lower().startswith("args:"):
                in_args = True
                continue
            if in_args:
                if stripped.startswith(f"{param_name}:"):
                    return stripped[len(param_name) + 1 :].strip()
                if (
                    stripped
                    and not stripped.startswith(" ")
                    and ":" not in stripped[:20]
                ):
                    in_args = False

        return f"Parameter {param_name}"


def create_tool(
    name: str | None = None,
    description: str | None = None,
    category: str = "uncategorized",
    tags: list[str] | None = None,
) -> Callable[[Callable], FunctionTool]:
    """
    Decorator to create a tool from a function.

    Example:
        ```python
        @create_tool(name="greet", description="Greet a person", category="utility")
        async def greet(name: str) -> str:
            return f"Hello, {name}!"
        ```
    """

    def decorator(func: Callable) -> FunctionTool:
        return FunctionTool(
            func, name=name, description=description, category=category, tags=tags
        )

    return decorator
