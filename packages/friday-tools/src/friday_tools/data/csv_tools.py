"""
CSV tools.

Ref: docs/specs/tool_specification.md - Category 7-8: Data Formats - CSV
"""

from __future__ import annotations

import csv
import json
from typing import Any

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class CsvReadTool(BaseTool):
    """Read and parse a CSV file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "csv_read"

    @property
    def description(self) -> str:
        return "Read and parse a CSV file."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the CSV file",
                },
                "delimiter": {
                    "type": "string",
                    "description": "Field delimiter",
                    "default": ",",
                },
                "has_header": {
                    "type": "boolean",
                    "description": "First row is header",
                    "default": True,
                },
                "max_rows": {
                    "type": "integer",
                    "description": "Maximum rows to read",
                    "default": 1000,
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        delimiter = kwargs.get("delimiter", ",")
        has_header = kwargs.get("has_header", True)
        max_rows = kwargs.get("max_rows", 1000)

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: File not found: {path}"

        try:
            with validated_path.open(newline="", encoding="utf-8") as f:
                if has_header:
                    reader = csv.DictReader(f, delimiter=delimiter)
                    rows = []
                    for i, row in enumerate(reader):
                        if i >= max_rows:
                            break
                        rows.append(dict(row))
                else:
                    reader = csv.reader(f, delimiter=delimiter)
                    rows = []
                    for i, row in enumerate(reader):
                        if i >= max_rows:
                            break
                        rows.append(row)

            return json.dumps(rows, indent=2)

        except Exception as e:
            return f"Error: Failed to read CSV: {e}"


class CsvWriteTool(BaseTool):
    """Write data to a CSV file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "csv_write"

    @property
    def description(self) -> str:
        return "Write data to a CSV file."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to write the CSV file",
                },
                "data": {
                    "type": "array",
                    "description": "Array of objects or arrays to write",
                },
                "delimiter": {
                    "type": "string",
                    "description": "Field delimiter",
                    "default": ",",
                },
            },
            "required": ["path", "data"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        data = kwargs["data"]
        delimiter = kwargs.get("delimiter", ",")

        validated_path = self._sandbox.validate_path(path)

        if not data:
            return "Error: No data to write"

        try:
            validated_path.parent.mkdir(parents=True, exist_ok=True)

            with validated_path.open("w", newline="", encoding="utf-8") as f:
                if isinstance(data[0], dict):
                    fieldnames = list(data[0].keys())
                    writer = csv.DictWriter(
                        f, fieldnames=fieldnames, delimiter=delimiter
                    )
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    writer = csv.writer(f, delimiter=delimiter)
                    writer.writerows(data)

            return f"Successfully wrote {len(data)} rows to {path}"

        except Exception as e:
            return f"Error: Failed to write CSV: {e}"


# Convenience instances
csv_read = CsvReadTool()
csv_write = CsvWriteTool()
