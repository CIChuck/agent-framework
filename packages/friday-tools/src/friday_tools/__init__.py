"""
Friday Tools - Comprehensive tool library for AI agents.

This package provides a wide variety of tools for AI agents including
filesystem operations, web access, data format handling, git operations,
and more.

Ref: docs/specs/tool_specification.md
"""

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

__all__ = [
    # Protocols
    "ToolDefinition",
    "ToolAdapter",
    "ToolRegistry",
    # Base classes
    "BaseTool",
    "FunctionTool",
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
]

__version__ = "0.1.0"
