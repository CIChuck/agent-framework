"""Tool schema helpers for FridayV2."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from friday_core.mcp import MCPToolCallProvenance


@dataclass(frozen=True)
class ToolDefinition:
    """Runtime-neutral tool definition used by FridayV2 fake services."""

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    category: str = "utility"


@dataclass(frozen=True)
class ToolCallRecord:
    """Recorded tool call used by deterministic tests."""

    name: str
    arguments: dict[str, Any]
    result: str
    call_id: str | None = None
    mcp_provenance: MCPToolCallProvenance | None = None
