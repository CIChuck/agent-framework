# mypy: ignore-errors
"""
YAML tools.

Ref: docs/reference/specs/tool_specification.md - Category 7: Data Formats - YAML
"""

from __future__ import annotations

import json
from typing import Any

import yaml

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class YamlReadTool(BaseTool):
    """Read and parse a YAML file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "yaml_read"

    @property
    def description(self) -> str:
        return "Read and parse a YAML file."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the YAML file",
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
                data = yaml.safe_load(f)
            return json.dumps(data, indent=2)
        except yaml.YAMLError as e:
            return f"Error: Invalid YAML: {e}"
        except Exception as e:
            return f"Error: Failed to read file: {e}"


class YamlWriteTool(BaseTool):
    """Write data to a YAML file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "yaml_write"

    @property
    def description(self) -> str:
        return "Write data to a YAML file."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to write the YAML file",
                },
                "data": {
                    "description": "Data to write",
                },
            },
            "required": ["path", "data"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        data = kwargs["data"]

        validated_path = self._sandbox.validate_path(path)

        try:
            validated_path.parent.mkdir(parents=True, exist_ok=True)
            with validated_path.open("w") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            return f"Successfully wrote YAML to {path}"
        except Exception as e:
            return f"Error: Failed to write file: {e}"


# Convenience instances
yaml_read = YamlReadTool()
yaml_write = YamlWriteTool()
