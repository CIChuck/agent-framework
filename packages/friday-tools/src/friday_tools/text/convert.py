"""
Text conversion tools.

Ref: docs/specs/tool_specification.md - Category 9: Text Processing - Convert
"""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from ..definition import BaseTool


class MarkdownToTextTool(BaseTool):
    """Strip markdown to plain text."""

    @property
    def name(self) -> str:
        return "markdown_to_text"

    @property
    def description(self) -> str:
        return "Convert markdown to plain text by stripping formatting."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "markdown": {"type": "string", "description": "Markdown text"},
            },
            "required": ["markdown"],
        }

    async def execute(self, **kwargs: Any) -> str:
        text = kwargs["markdown"]

        # Remove code blocks
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"`[^`]+`", "", text)

        # Remove links but keep text
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

        # Remove images
        text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", "", text)

        # Remove headers
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)

        # Remove bold/italic
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)

        # Remove horizontal rules
        text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)

        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()


class HtmlToMarkdownTool(BaseTool):
    """Convert HTML to markdown."""

    @property
    def name(self) -> str:
        return "html_to_markdown"

    @property
    def description(self) -> str:
        return "Convert HTML to markdown format."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "html": {"type": "string", "description": "HTML content"},
                "strip_tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "HTML tags to strip (e.g., ['script', 'style'])",
                },
            },
            "required": ["html"],
        }

    async def execute(self, **kwargs: Any) -> str:
        html = kwargs["html"]
        strip_tags = kwargs.get("strip_tags", ["script", "style"])

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Remove specified tags
            for tag in strip_tags:
                for element in soup.find_all(tag):
                    element.decompose()

            markdown = md(str(soup))

            # Clean up
            markdown = re.sub(r"\n{3,}", "\n\n", markdown)
            return markdown.strip()

        except Exception as e:
            return f"Error: Conversion failed: {e}"


markdown_to_text = MarkdownToTextTool()
html_to_markdown = HtmlToMarkdownTool()
