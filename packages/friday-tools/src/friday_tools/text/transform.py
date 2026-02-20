"""
Text transformation tools.

Ref: docs/specs/tool_specification.md - Category 9: Text Processing - Transform
"""

from __future__ import annotations

import re
from typing import Any

from jinja2 import Template

from ..definition import BaseTool


class TextReplaceTool(BaseTool):
    """Replace text with regex."""

    @property
    def name(self) -> str:
        return "text_replace"

    @property
    def description(self) -> str:
        return "Replace text using a regular expression pattern."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input text"},
                "pattern": {"type": "string", "description": "Regex pattern"},
                "replacement": {"type": "string", "description": "Replacement string"},
            },
            "required": ["text", "pattern", "replacement"],
        }

    async def execute(self, **kwargs: Any) -> str:
        try:
            return re.sub(kwargs["pattern"], kwargs["replacement"], kwargs["text"])
        except re.error as e:
            return f"Error: Invalid regex: {e}"


class TextSplitTool(BaseTool):
    """Split text by delimiter."""

    @property
    def name(self) -> str:
        return "text_split"

    @property
    def description(self) -> str:
        return "Split text by a delimiter or pattern."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to split"},
                "delimiter": {"type": "string", "description": "Delimiter or regex"},
                "regex": {"type": "boolean", "default": False},
            },
            "required": ["text", "delimiter"],
        }

    async def execute(self, **kwargs: Any) -> str:
        text = kwargs["text"]
        delimiter = kwargs["delimiter"]
        use_regex = kwargs.get("regex", False)

        try:
            parts = re.split(delimiter, text) if use_regex else text.split(delimiter)
            return str(parts)
        except re.error as e:
            return f"Error: Invalid regex: {e}"


class TextJoinTool(BaseTool):
    """Join text parts."""

    @property
    def name(self) -> str:
        return "text_join"

    @property
    def description(self) -> str:
        return "Join a list of strings with a delimiter."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "parts": {"type": "array", "items": {"type": "string"}},
                "delimiter": {"type": "string", "default": ""},
            },
            "required": ["parts"],
        }

    async def execute(self, **kwargs: Any) -> str:
        parts = kwargs["parts"]
        delimiter = kwargs.get("delimiter", "")
        return delimiter.join(parts)


class TextTemplateTool(BaseTool):
    """Render a Jinja2 template."""

    @property
    def name(self) -> str:
        return "text_template"

    @property
    def description(self) -> str:
        return "Render a Jinja2 template with variables."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "template": {"type": "string", "description": "Jinja2 template string"},
                "variables": {"type": "object", "description": "Template variables"},
            },
            "required": ["template", "variables"],
        }

    async def execute(self, **kwargs: Any) -> str:
        template_str = kwargs["template"]
        variables = kwargs.get("variables", {})

        try:
            template = Template(template_str)
            return template.render(**variables)
        except Exception as e:
            return f"Error: Template rendering failed: {e}"


text_replace = TextReplaceTool()
text_split = TextSplitTool()
text_join = TextJoinTool()
text_template = TextTemplateTool()
