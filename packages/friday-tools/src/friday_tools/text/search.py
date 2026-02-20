"""
Text search tools.

Ref: docs/specs/tool_specification.md - Category 9: Text Processing - Search
"""

from __future__ import annotations

import re
from typing import Any

from ..definition import BaseTool


class TextSearchTool(BaseTool):
    """Search text with regex."""

    @property
    def name(self) -> str:
        return "text_search"

    @property
    def description(self) -> str:
        return "Search for a pattern in text using regular expressions."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to search in"},
                "pattern": {"type": "string", "description": "Regex pattern"},
                "case_insensitive": {"type": "boolean", "default": False},
            },
            "required": ["text", "pattern"],
        }

    async def execute(self, **kwargs: Any) -> str:
        text = kwargs["text"]
        pattern = kwargs["pattern"]
        flags = re.IGNORECASE if kwargs.get("case_insensitive") else 0

        try:
            matches = list(re.finditer(pattern, text, flags))
            if not matches:
                return "No matches found"
            results = [
                f"Match {i + 1}: '{m.group()}' at position {m.start()}"
                for i, m in enumerate(matches)
            ]
            return "\n".join(results)
        except re.error as e:
            return f"Error: Invalid regex: {e}"


class TextExtractTool(BaseTool):
    """Extract regex groups from text."""

    @property
    def name(self) -> str:
        return "text_extract"

    @property
    def description(self) -> str:
        return "Extract regex capture groups from text."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to extract from"},
                "pattern": {
                    "type": "string",
                    "description": "Regex with capture groups",
                },
            },
            "required": ["text", "pattern"],
        }

    async def execute(self, **kwargs: Any) -> str:
        text = kwargs["text"]
        pattern = kwargs["pattern"]

        try:
            matches = re.findall(pattern, text)
            if not matches:
                return "No matches found"
            return str(matches)
        except re.error as e:
            return f"Error: Invalid regex: {e}"


text_search = TextSearchTool()
text_extract = TextExtractTool()
