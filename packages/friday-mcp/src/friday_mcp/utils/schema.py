"""
Schema conversion utilities.

Converts between MCP and Friday tool schema formats.
"""

from __future__ import annotations

from typing import Any


def mcp_to_friday_schema(mcp_schema: dict[str, Any]) -> dict[str, Any]:
    """
    Convert MCP inputSchema to Friday parameters_schema.

    MCP uses 'inputSchema', Friday uses 'parameters_schema'.
    Both follow JSON Schema, so most fields map directly.

    Args:
        mcp_schema: MCP tool inputSchema

    Returns:
        Friday-compatible parameters_schema
    """
    return {
        "type": mcp_schema.get("type", "object"),
        "properties": mcp_schema.get("properties", {}),
        "required": mcp_schema.get("required", []),
        # Preserve additional JSON Schema fields
        **{
            k: v
            for k, v in mcp_schema.items()
            if k not in ("type", "properties", "required")
        },
    }


def friday_to_mcp_schema(friday_schema: dict[str, Any]) -> dict[str, Any]:
    """
    Convert Friday parameters_schema to MCP inputSchema.

    Args:
        friday_schema: Friday tool parameters_schema

    Returns:
        MCP-compatible inputSchema
    """
    return {
        "type": friday_schema.get("type", "object"),
        "properties": friday_schema.get("properties", {}),
        "required": friday_schema.get("required", []),
        # Preserve additional JSON Schema fields
        **{
            k: v
            for k, v in friday_schema.items()
            if k not in ("type", "properties", "required")
        },
    }


def extract_text_content(mcp_response: dict[str, Any]) -> str:
    """
    Extract text content from MCP tool call response.

    MCP responses contain a 'content' array with typed content blocks.
    This extracts and concatenates all text blocks.

    Args:
        mcp_response: Response from tools/call

    Returns:
        Concatenated text content
    """
    content = mcp_response.get("content", [])
    if not content:
        return ""

    text_parts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            text_parts.append(block.get("text", ""))
        elif isinstance(block, str):
            text_parts.append(block)

    return "\n".join(text_parts)
