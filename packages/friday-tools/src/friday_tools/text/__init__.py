# mypy: ignore-errors
"""
Text processing tools.

Ref: docs/reference/specs/tool_specification.md - Category 9: Text Processing

Provides 8 tools for text manipulation, search, and conversion.
"""

from .convert import html_to_markdown, markdown_to_text
from .search import text_extract, text_search
from .transform import text_join, text_replace, text_split, text_template

__all__ = [
    "text_search",
    "text_extract",
    "text_replace",
    "text_split",
    "text_join",
    "text_template",
    "markdown_to_text",
    "html_to_markdown",
]
