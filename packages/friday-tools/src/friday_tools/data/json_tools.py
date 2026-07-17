# mypy: ignore-errors
"""
JSON tools.

Ref: docs/reference/specs/tool_specification.md - Category 7: Data Formats - JSON
"""

from __future__ import annotations

import json
from typing import Any

from jsonpath_ng import parse as jsonpath_parse

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class JsonReadTool(BaseTool):
    """Read and parse a JSON file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "json_read"

    @property
    def description(self) -> str:
        return "Read and parse a JSON file."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the JSON file",
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: File not found: {path}"

        try:
            with validated_path.open() as f:
                data = json.load(f)
            return json.dumps(data, indent=2)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON: {e}"
        except Exception as e:
            return f"Error: Failed to read file: {e}"


class JsonWriteTool(BaseTool):
    """Write data to a JSON file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "json_write"

    @property
    def description(self) -> str:
        return "Write data to a JSON file."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to write the JSON file",
                },
                "data": {
                    "description": "Data to write (object, array, or primitive)",
                },
                "indent": {
                    "type": "integer",
                    "description": "Indentation level for pretty printing",
                    "default": 2,
                },
            },
            "required": ["path", "data"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        data = kwargs["data"]
        indent = kwargs.get("indent", 2)

        validated_path = self._sandbox.validate_path(path)

        try:
            validated_path.parent.mkdir(parents=True, exist_ok=True)
            with validated_path.open("w") as f:
                json.dump(data, f, indent=indent)
            return f"Successfully wrote JSON to {path}"
        except Exception as e:
            return f"Error: Failed to write file: {e}"


class JsonQueryTool(BaseTool):
    """Query JSON data using JSONPath."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "json_query"

    @property
    def description(self) -> str:
        return "Query JSON data using JSONPath expressions."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the JSON file",
                },
                "query": {
                    "type": "string",
                    "description": "JSONPath expression (e.g., '$.store.book[*].title')",  # noqa: E501
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
            with validated_path.open() as f:
                data = json.load(f)

            jsonpath_expr = jsonpath_parse(query)
            matches = jsonpath_expr.find(data)

            if not matches:
                return "No matches found"

            results = [match.value for match in matches]

            if len(results) == 1:
                return json.dumps(results[0], indent=2)
            return json.dumps(results, indent=2)

        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON: {e}"
        except Exception as e:
            return f"Error: Query failed: {e}"


# Convenience instances
json_read = JsonReadTool()
json_write = JsonWriteTool()
json_query = JsonQueryTool()
