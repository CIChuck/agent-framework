"""
Tool Manifest for Code Generation.

Generates a manifest of available Friday tools that can be used
by the CodeGenerationTool to inform LLM-based code generation.

Ref: Code Generation Tool specification
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .protocols import ToolDefinition, ToolRegistry


# Mapping of tool name prefixes to their import modules
TOOL_MODULE_MAP: dict[str, str] = {
    # Filesystem tools
    "file_": "friday_tools.filesystem",
    "directory_": "friday_tools.filesystem",
    # Shell tools
    "shell_": "friday_tools.shell",
    # Web tools
    "web_": "friday_tools.web",
    # Git tools
    "git_": "friday_tools.git",
    # Data format tools
    "json_": "friday_tools.data",
    "yaml_": "friday_tools.data",
    "csv_": "friday_tools.data",
    "toml_": "friday_tools.data",
    "xml_": "friday_tools.data",
    # Text tools
    "text_": "friday_tools.text",
    # Code tools
    "code_": "friday_tools.code",
    # Execution tools
    "python_execute": "friday_tools.execution",
    # System tools
    "process_": "friday_tools.system",
    "environment_": "friday_tools.system",
    "system_": "friday_tools.system",
    # Integration tools
    "email_": "friday_tools.integrations",
    "slack_": "friday_tools.integrations",
    "calendar_": "friday_tools.integrations",
    "database_": "friday_tools.integrations",
    "webhook_": "friday_tools.integrations",
}


def get_import_path(tool_name: str) -> str:
    """
    Determine the import path for a tool based on its name.

    Args:
        tool_name: The tool's name (e.g., "file_read")

    Returns:
        Import module path (e.g., "friday_tools.filesystem")
    """
    # Check exact matches first
    if tool_name in TOOL_MODULE_MAP:
        return TOOL_MODULE_MAP[tool_name]

    # Check prefix matches
    for prefix, module in TOOL_MODULE_MAP.items():
        if tool_name.startswith(prefix):
            return module

    # Default fallback
    return "friday_tools"


def generate_usage_example(tool: "ToolDefinition") -> str:
    """
    Generate a usage example for a tool.

    Args:
        tool: The tool definition

    Returns:
        Example code string
    """
    params = tool.parameters_schema.get("properties", {})
    required = tool.parameters_schema.get("required", [])

    # Build example arguments
    example_args: list[str] = []
    for param_name, param_schema in params.items():
        param_type = param_schema.get("type", "string")

        # Generate example value based on type
        if param_type == "string":
            if "path" in param_name.lower():
                example_val = '"/path/to/file"'
            elif "url" in param_name.lower():
                example_val = '"https://example.com"'
            elif "query" in param_name.lower():
                example_val = '"search term"'
            else:
                example_val = '"example"'
        elif param_type == "integer":
            example_val = "10"
        elif param_type == "boolean":
            example_val = "True"
        elif param_type == "array":
            example_val = "[]"
        elif param_type == "object":
            example_val = "{}"
        else:
            example_val = '"value"'

        # Only include required params in example
        if param_name in required:
            example_args.append(f"{param_name}={example_val}")

    args_str = ", ".join(example_args)
    return f'result = await {tool.name}.execute({args_str})'


class ToolManifest:
    """
    Generates a manifest of available Friday tools for code generation.

    The manifest provides:
    - Tool names and descriptions
    - Import paths for each tool
    - Parameter schemas
    - Usage examples

    Example:
        registry = get_default_registry()
        manifest = ToolManifest(registry)

        # Get manifest as dict
        data = manifest.get_manifest()

        # Get as LLM-ready prompt context
        context = manifest.to_prompt_context()
    """

    def __init__(self, registry: "ToolRegistry"):
        """
        Initialize manifest with a tool registry.

        Args:
            registry: The tool registry to generate manifest from
        """
        self._registry = registry

    def get_manifest(self) -> dict[str, Any]:
        """
        Generate the full tool manifest.

        Returns:
            Dictionary containing all tool metadata
        """
        tools = []
        for tool in self._registry.list_tools():
            tool_info = {
                "name": tool.name,
                "description": tool.description,
                "import_module": get_import_path(tool.name),
                "import_statement": f"from {get_import_path(tool.name)} import {tool.name}",
                "parameters": tool.parameters_schema,
                "usage_example": generate_usage_example(tool),
            }
            tools.append(tool_info)

        return {
            "version": "1.0",
            "tool_count": len(tools),
            "tools": tools,
        }

    def get_tool_info(self, tool_name: str) -> dict[str, Any] | None:
        """
        Get manifest info for a specific tool.

        Args:
            tool_name: The tool name to look up

        Returns:
            Tool info dict or None if not found
        """
        tool = self._registry.get(tool_name)
        if tool is None:
            return None

        return {
            "name": tool.name,
            "description": tool.description,
            "import_module": get_import_path(tool.name),
            "import_statement": f"from {get_import_path(tool.name)} import {tool.name}",
            "parameters": tool.parameters_schema,
            "usage_example": generate_usage_example(tool),
        }

    def to_prompt_context(self, max_tools: int | None = None) -> str:
        """
        Format manifest as context for LLM prompting.

        Args:
            max_tools: Maximum number of tools to include (None for all)

        Returns:
            Formatted string suitable for LLM prompt
        """
        manifest = self.get_manifest()
        tools = manifest["tools"]

        if max_tools is not None:
            tools = tools[:max_tools]

        lines = ["# Available Friday Tools\n"]
        lines.append(f"You have access to {len(tools)} tools:\n")

        for tool in tools:
            lines.append(f"## {tool['name']}")
            lines.append(f"**Import:** `{tool['import_statement']}`")
            lines.append(f"**Description:** {tool['description']}")

            # Format parameters
            params = tool["parameters"].get("properties", {})
            required = tool["parameters"].get("required", [])
            if params:
                lines.append("**Parameters:**")
                for param_name, param_schema in params.items():
                    req_marker = " (required)" if param_name in required else ""
                    param_type = param_schema.get("type", "any")
                    param_desc = param_schema.get("description", "")
                    lines.append(f"  - `{param_name}`: {param_type}{req_marker} - {param_desc}")

            lines.append(f"**Example:** `{tool['usage_example']}`")
            lines.append("")

        return "\n".join(lines)

    def list_tool_names(self) -> list[str]:
        """Get list of all tool names in the manifest."""
        return [tool.name for tool in self._registry.list_tools()]

    def __len__(self) -> int:
        """Return number of tools in manifest."""
        return len(self._registry.list_tools())
