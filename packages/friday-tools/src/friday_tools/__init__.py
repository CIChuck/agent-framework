"""
Friday Tools - Comprehensive tool library for AI agents.

This package provides a wide variety of tools for AI agents including
filesystem operations, web access, data format handling, git operations,
and more.

Ref: docs/specs/tool_specification.md
"""

from .base import FridayTool, ToolResult
from .definition import BaseTool, FunctionTool, create_tool
from .manifest import ToolManifest
from .protocols import ToolAdapter, ToolDefinition, ToolRegistry
from .registry import DefaultToolRegistry, get_default_registry, tool
from .sandbox import (
    CommandSecurityError,
    FilesystemSandbox,
    PathSecurityError,
    SecurityError,
    ShellSandbox,
)

# Utility tools
from .utility import EchoTool, GetCurrentDateTimeTool

# Smart file reading
from .filesystem.smart_read import SmartFileReadTool

__all__ = [
    # Protocols
    "ToolDefinition",
    "ToolAdapter",
    "ToolRegistry",
    # Base classes
    "BaseTool",
    "FunctionTool",
    "FridayTool",
    "ToolResult",
    # Registry
    "DefaultToolRegistry",
    "get_default_registry",
    # Manifest
    "ToolManifest",
    # Decorators
    "tool",
    "create_tool",
    # Security
    "FilesystemSandbox",
    "ShellSandbox",
    "SecurityError",
    "PathSecurityError",
    "CommandSecurityError",
    # Utility tools
    "GetCurrentDateTimeTool",
    "EchoTool",
    # Smart file reading
    "SmartFileReadTool",
]

__version__ = "0.1.0"
