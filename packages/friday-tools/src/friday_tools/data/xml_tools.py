"""
XML tools.

Ref: docs/specs/tool_specification.md - Category 7: Data Formats - XML
"""

from __future__ import annotations

from typing import Any

from lxml import etree

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class XmlReadTool(BaseTool):
    """Read and parse an XML file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "xml_read"

    @property
    def description(self) -> str:
        return "Read and parse an XML file, returning a formatted text representation."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the XML file",
                },
                "pretty": {
                    "type": "boolean",
                    "description": "Pretty print the output",
                    "default": True,
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        pretty = kwargs.get("pretty", True)

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: File not found: {path}"

        try:
            tree = etree.parse(str(validated_path))
            if pretty:
                return etree.tostring(tree, pretty_print=True, encoding="unicode")
            return etree.tostring(tree, encoding="unicode")

        except etree.XMLSyntaxError as e:
            return f"Error: Invalid XML: {e}"
        except Exception as e:
            return f"Error: Failed to read XML: {e}"


class XmlQueryTool(BaseTool):
    """Query XML using XPath."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "xml_query"

    @property
    def description(self) -> str:
        return "Query XML data using XPath expressions."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the XML file",
                },
                "query": {
                    "type": "string",
                    "description": "XPath expression",
                },
            },
            "required": ["path", "query"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        query = kwargs["query"]

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: File not found: {path}"

        try:
            tree = etree.parse(str(validated_path))
            results = tree.xpath(query)

            if not results:
                return "No matches found"

            output_lines = []
            for result in results:
                if isinstance(result, etree._Element):
                    output_lines.append(
                        etree.tostring(result, pretty_print=True, encoding="unicode")
                    )
                else:
                    output_lines.append(str(result))

            return "\n".join(output_lines)

        except etree.XPathError as e:
            return f"Error: Invalid XPath: {e}"
        except Exception as e:
            return f"Error: Query failed: {e}"


# Convenience instances
xml_read = XmlReadTool()
xml_query = XmlQueryTool()
