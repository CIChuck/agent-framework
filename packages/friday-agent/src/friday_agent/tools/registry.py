"""
Default Tool Registry Implementation.

Implements the ToolRegistry protocol with decorator-based registration
and partial binding for dependency injection.

Ref: Batch 3 Specification, Section 5.1
"""

import inspect
import logging
from functools import partial
from typing import Any, Callable, get_type_hints

from friday_core.interfaces.tools import SchemaFormat, ToolDefinition

logger = logging.getLogger(__name__)

# Global registry for decorator-based tool registration
_GLOBAL_TOOL_REGISTRY: dict[str, dict[str, Any]] = {}


def tool(
    name: str | None = None,
    description: str = "",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to register a function as a tool.

    The decorator extracts parameter information from the function
    signature and docstring to generate OpenAI-compatible JSON schema.

    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)

    Returns:
        Decorated function (unchanged behavior)

    Example:
        @tool(name="search_web", description="Search the web for information")
        async def search_web(query: str, max_results: int = 10) -> str:
            '''
            Search the web.

            Args:
                query: The search query
                max_results: Maximum number of results to return
            '''
            # Implementation
            pass
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        tool_name = name or func.__name__
        tool_desc = description or (func.__doc__ or "").split("\n")[0].strip()

        # Extract parameters from signature
        sig = inspect.signature(func)
        parameters = _extract_parameters(func, sig)

        # Store in global registry
        _GLOBAL_TOOL_REGISTRY[tool_name] = {
            "func": func,
            "description": tool_desc,
            "parameters": parameters,
        }

        # Mark function as a registered tool
        func._tool_name = tool_name  # type: ignore

        return func

    return decorator


def _extract_parameters(
    func: Callable[..., Any], sig: inspect.Signature
) -> dict[str, Any]:
    """
    Extract OpenAI-compatible parameter schema from function signature.

    Args:
        func: The function to analyze
        sig: The function signature

    Returns:
        OpenAI-compatible parameters schema
    """
    properties: dict[str, Any] = {}
    required: list[str] = []

    # Get type hints if available
    try:
        hints = get_type_hints(func)
    except Exception:
        hints = {}

    # Parse docstring for parameter descriptions
    param_docs = _parse_docstring_params(func.__doc__ or "")

    for param_name, param in sig.parameters.items():
        # Skip special parameters (self, cls, injected dependencies)
        if param_name in ("self", "cls"):
            continue

        # Determine JSON Schema type from Python type hint
        python_type = hints.get(param_name, str)
        json_type = _python_type_to_json_schema(python_type)

        # Build parameter schema
        param_schema: dict[str, Any] = {
            "type": json_type,
        }

        # Add description if available
        if param_name in param_docs:
            param_schema["description"] = param_docs[param_name]

        # Handle default values
        if param.default is inspect.Parameter.empty:
            required.append(param_name)
        else:
            param_schema["default"] = param.default

        properties[param_name] = param_schema

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _python_type_to_json_schema(python_type: type) -> str:
    """Convert Python type to JSON Schema type string."""
    type_mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    # Handle Optional, Union, etc.
    origin = getattr(python_type, "__origin__", None)
    if origin is not None:
        # For Optional[X], get the first non-None type
        args = getattr(python_type, "__args__", ())
        for arg in args:
            if arg is not type(None):
                return _python_type_to_json_schema(arg)

    return type_mapping.get(python_type, "string")


def _parse_docstring_params(docstring: str) -> dict[str, str]:
    """
    Parse parameter descriptions from docstring.

    Supports Google-style docstrings with Args: section.

    Args:
        docstring: The function docstring

    Returns:
        Dict mapping parameter names to descriptions
    """
    params: dict[str, str] = {}

    lines = docstring.split("\n")
    in_args_section = False
    current_param = None
    current_desc: list[str] = []

    for line in lines:
        stripped = line.strip()

        # Check for Args: section
        if stripped.lower().startswith("args:"):
            in_args_section = True
            continue

        # Check for other sections (Returns:, Raises:, etc.)
        if stripped.endswith(":") and not stripped.startswith(" "):
            if in_args_section and current_param:
                params[current_param] = " ".join(current_desc).strip()
            in_args_section = False
            current_param = None
            continue

        if in_args_section:
            # Check for new parameter (name: description)
            if ":" in stripped and not stripped.startswith(" "):
                # Save previous parameter
                if current_param:
                    params[current_param] = " ".join(current_desc).strip()

                # Parse new parameter
                parts = stripped.split(":", 1)
                current_param = parts[0].strip()
                current_desc = [parts[1].strip()] if len(parts) > 1 else []
            elif current_param and stripped:
                # Continuation of description
                current_desc.append(stripped)

    # Don't forget the last parameter
    if in_args_section and current_param:
        params[current_param] = " ".join(current_desc).strip()

    return params


class DecoratedFunctionTool:
    """
    Wraps a @tool decorated function as a ToolDefinition.

    This class allows decorator-registered functions to conform to
    the unified ToolDefinition protocol while preserving the original
    function for dependency injection via bind_dependency.
    """

    def __init__(
        self,
        func: Callable[..., Any],
        name: str,
        description: str,
        parameters: dict[str, Any],
    ):
        """
        Create a tool from a decorated function.

        Args:
            func: The original function
            name: Tool name
            description: Tool description
            parameters: JSON Schema for parameters
        """
        self._func = func
        self._name = name
        self._description = description
        self._parameters = parameters

    @property
    def name(self) -> str:
        """Unique tool identifier."""
        return self._name

    @property
    def description(self) -> str:
        """Human-readable description for the LLM."""
        return self._description

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """JSON Schema for tool parameters."""
        return self._parameters

    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool with given arguments."""
        if inspect.iscoroutinefunction(self._func):
            result = await self._func(**kwargs)
        else:
            result = self._func(**kwargs)

        if isinstance(result, str):
            return result
        return str(result)

    def to_schema(self, format: str = "plain") -> dict[str, Any]:
        """
        Convert tool to JSON schema format for LLM function calling.

        Args:
            format: Output format - "plain" or "openai".

        Returns:
            Dictionary suitable for LLM function calling.
        """
        plain_schema = {
            "name": self._name,
            "description": self._description,
            "parameters": self._parameters,
        }

        if format == SchemaFormat.OPENAI or format == "openai":
            return {
                "type": "function",
                "function": plain_schema,
            }

        return plain_schema


class DefaultToolRegistry:
    """
    Default implementation of the ToolRegistry protocol.

    Features:
    - Decorator-based registration (@tool)
    - Manual registration via register()
    - Partial binding for dependency injection
    - OpenAI-compatible JSON schema generation

    Example:
        registry = DefaultToolRegistry()

        # Register using decorator
        @tool(name="greet", description="Greet someone")
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        # Load decorated tools
        registry.load_decorated_tools()

        # Or register a ToolDefinition
        registry.register(my_tool)

        # Get tool and execute
        tool = registry.get("greet")
        result = await tool.execute(name="World")
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._tools: dict[str, DecoratedFunctionTool] = {}

    def register(
        self,
        tool: ToolDefinition | str | None = None,
        func: Callable[..., Any] | None = None,
        description: str | None = None,
        parameters: dict[str, Any] | None = None,
        *,
        name: str | None = None,
    ) -> None:
        """
        Register a tool with the registry.

        Supports two call patterns for backward compatibility:
        1. register(tool: ToolDefinition) - preferred
        2. register(name, func, description, parameters) - legacy
        3. register(name=..., func=..., description=..., parameters=...) - legacy with kwargs

        Args:
            tool: ToolDefinition instance or tool name string (positional)
            func: Function to execute (only for legacy pattern)
            description: Tool description (only for legacy pattern)
            parameters: JSON Schema for parameters (only for legacy pattern)
            name: Tool name (keyword-only, alternative to first positional arg)

        Raises:
            ValueError: If tool with same name already registered.
        """
        # Handle keyword argument 'name' for backward compatibility
        if name is not None:
            tool_or_name = name
        elif tool is not None:
            tool_or_name = tool
        else:
            raise ValueError("Either 'tool' or 'name' must be provided")

        # Detect call pattern
        if isinstance(tool_or_name, str):
            # Legacy pattern: register(name, func, description, parameters)
            if func is None:
                raise ValueError("func is required when registering by name")
            tool_obj = DecoratedFunctionTool(
                func=func,
                name=tool_or_name,
                description=description or "",
                parameters=parameters or {"type": "object", "properties": {}},
            )
        else:
            # New pattern: register(tool)
            tool_obj = tool_or_name

        if tool_obj.name in self._tools:
            raise ValueError(f"Tool '{tool_obj.name}' is already registered")

        # Wrap in DecoratedFunctionTool if not already
        if isinstance(tool_obj, DecoratedFunctionTool):
            self._tools[tool_obj.name] = tool_obj
        else:
            # Create a wrapper for external ToolDefinition implementations
            self._tools[tool_obj.name] = DecoratedFunctionTool(
                func=tool_obj.execute,
                name=tool_obj.name,
                description=tool_obj.description,
                parameters=tool_obj.parameters_schema,
            )

        logger.debug(f"Registered tool: {tool_obj.name}")

    def register_function(
        self,
        name: str,
        func: Callable[..., Any],
        description: str,
        parameters: dict[str, Any],
    ) -> None:
        """
        Register a function as a tool manually.

        This is a convenience method for registering raw functions.

        Args:
            name: Unique tool name
            func: The executable function
            description: Human-readable description
            parameters: JSON Schema for parameters
        """
        tool = DecoratedFunctionTool(
            func=func,
            name=name,
            description=description,
            parameters=parameters,
        )
        self._tools[name] = tool
        logger.debug(f"Registered tool: {name}")

    def get(self, name: str) -> DecoratedFunctionTool | None:
        """
        Get a tool by name.

        Args:
            name: The tool's unique identifier.

        Returns:
            The tool if found, None otherwise.
        """
        return self._tools.get(name)

    def get_callable(self, name: str) -> Callable[..., Any]:
        """
        Get the executable callable for a tool.

        Args:
            name: The tool's unique identifier.

        Returns:
            Callable that can be invoked with tool arguments.

        Raises:
            KeyError: If tool not found.
        """
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"Tool '{name}' not found in registry")
        return tool._func

    def get_tool(self, name: str) -> Callable[..., Any]:
        """
        Get executable function for a tool.

        DEPRECATED: Use get_callable() instead.

        Args:
            name: Tool name

        Returns:
            The callable function

        Raises:
            KeyError: If tool not found
        """
        return self.get_callable(name)

    def list_tools(self) -> list[DecoratedFunctionTool]:
        """
        List all registered tools.

        Returns:
            List of all registered ToolDefinition instances.
        """
        return list(self._tools.values())

    def list_names(self) -> list[str]:
        """
        List all registered tool names.

        Returns:
            List of tool name strings.
        """
        return list(self._tools.keys())

    def get_schemas(self, format: str = "plain") -> list[dict[str, Any]]:
        """
        Get JSON schemas for all registered tools.

        Args:
            format: Output format - "plain" or "openai".

        Returns:
            List of tool schemas suitable for LLM function calling.
        """
        return [tool.to_schema(format) for tool in self._tools.values()]

    def get_schema(self, name: str, format: str = "plain") -> dict[str, Any] | None:
        """
        Get JSON schema for a specific tool.

        Args:
            name: The tool name.
            format: Output format - "plain" or "openai".

        Returns:
            Tool schema if found, None otherwise.
        """
        tool = self._tools.get(name)
        if tool is None:
            return None
        return tool.to_schema(format)

    def load_decorated_tools(self) -> int:
        """
        Load all tools registered via the @tool decorator.

        Returns:
            Number of tools loaded
        """
        loaded = 0
        for name, info in _GLOBAL_TOOL_REGISTRY.items():
            if name not in self._tools:
                tool = DecoratedFunctionTool(
                    func=info["func"],
                    name=name,
                    description=info["description"],
                    parameters=info["parameters"],
                )
                self._tools[name] = tool
                loaded += 1
        return loaded

    def bind_dependency(
        self,
        tool_name: str,
        **kwargs: Any,
    ) -> None:
        """
        Bind dependencies to a tool using partial application.

        This allows injecting services (like MemoryController) into
        tool functions without requiring them as runtime arguments.

        Args:
            tool_name: Name of the tool to bind
            **kwargs: Dependencies to inject

        Example:
            # Tool that needs memory controller
            @tool(name="recall_memory")
            async def recall_memory(
                memory: MemoryController,  # Injected
                query: str,  # Runtime arg
            ) -> str:
                ...

            # Bind the dependency
            registry.bind_dependency("recall_memory", memory=memory_controller)

            # Now callable with just runtime args
            tool_fn = registry.get_callable("recall_memory")
            result = await tool_fn(query="test")
        """
        if tool_name not in self._tools:
            raise KeyError(f"Tool '{tool_name}' not found in registry")

        tool = self._tools[tool_name]
        bound_func = partial(tool._func, **kwargs)

        # Update the tool's internal function and parameters
        new_parameters = tool._parameters.copy()
        properties = new_parameters.get("properties", {})
        required = new_parameters.get("required", [])

        # Remove bound parameters from schema
        for key in kwargs:
            properties.pop(key, None)
            if key in required:
                required.remove(key)

        # Create a new DecoratedFunctionTool with bound function
        self._tools[tool_name] = DecoratedFunctionTool(
            func=bound_func,
            name=tool._name,
            description=tool._description,
            parameters=new_parameters,
        )

        logger.debug(f"Bound dependencies to tool '{tool_name}': {list(kwargs.keys())}")

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    def __contains__(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)

    def unregister(self, name: str) -> bool:
        """
        Remove a tool from the registry.

        Args:
            name: Tool name to remove

        Returns:
            True if tool was removed, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def clear(self) -> None:
        """Remove all registered tools."""
        self._tools.clear()
        logger.debug("Cleared all tools from registry")
