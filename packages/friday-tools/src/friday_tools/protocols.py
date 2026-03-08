# mypy: ignore-errors
"""
Tool protocols defining abstract interfaces for Friday tools.

Ref: docs/specs/tool_specification.md - Section 2: Protocols

All protocols are imported from friday-core for unified definitions.
This module re-exports them for backward compatibility.
"""

from friday_core.interfaces.tools import (
    SchemaFormat,
    ToolAdapter,
    ToolDefinition,
    ToolRegistry,
)

__all__ = [
    "SchemaFormat",
    "ToolDefinition",
    "ToolAdapter",
    "ToolRegistry",
]
