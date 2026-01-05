"""
TOML tools.

Ref: docs/specs/tool_specification.md - Category 7: Data Formats - TOML
"""

from __future__ import annotations

import json
from typing import Any

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

try:
    import tomli_w
except ImportError:
    tomli_w = None  # type: ignore

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class TomlReadTool(BaseTool):
    """Read and parse a TOML file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "toml_read"

    @property
    def description(self) -> str:
        return "Read and parse a TOML file."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the TOML file",
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
            with validated_path.open("rb") as f:
                data = tomllib.load(f)
            return json.dumps(data, indent=2, default=str)
        except Exception as e:
            return f"Error: Failed to read TOML: {e}"


class TomlWriteTool(BaseTool):
    """Write data to a TOML file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "toml_write"

    @property
    def description(self) -> str:
        return "Write data to a TOML file."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to write the TOML file",
                },
                "data": {
                    "type": "object",
                    "description": "Data to write (must be a dictionary)",
                },
            },
            "required": ["path", "data"],
        }

    async def execute(self, **kwargs: Any) -> str:
        if tomli_w is None:
            return "Error: tomli_w not installed. Install with: pip install tomli-w"

        path = kwargs["path"]
        data = kwargs["data"]

        validated_path = self._sandbox.validate_path(path)

        try:
            validated_path.parent.mkdir(parents=True, exist_ok=True)
            with validated_path.open("wb") as f:
                tomli_w.dump(data, f)
            return f"Successfully wrote TOML to {path}"
        except Exception as e:
            return f"Error: Failed to write TOML: {e}"


# Convenience instances
toml_read = TomlReadTool()
toml_write = TomlWriteTool()
