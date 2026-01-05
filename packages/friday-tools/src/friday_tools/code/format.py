"""
Code formatting and linting tools.

Ref: docs/specs/tool_specification.md - Category 11: Code Tools - Format
"""

from __future__ import annotations

import subprocess
from typing import Any

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class CodeFormatTool(BaseTool):
    """Format code using external tools."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "code_format"

    @property
    def description(self) -> str:
        return "Format code using ruff, black, or prettier."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File or directory to format"},
                "formatter": {"type": "string", "enum": ["ruff", "black", "prettier"], "default": "ruff"},
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        formatter = kwargs.get("formatter", "ruff")
        validated = self._sandbox.validate_path(path)

        try:
            if formatter == "ruff":
                result = subprocess.run(
                    ["ruff", "format", str(validated)],
                    capture_output=True, text=True, timeout=60
                )
            elif formatter == "black":
                result = subprocess.run(
                    ["black", str(validated)],
                    capture_output=True, text=True, timeout=60
                )
            elif formatter == "prettier":
                result = subprocess.run(
                    ["prettier", "--write", str(validated)],
                    capture_output=True, text=True, timeout=60
                )
            else:
                return f"Unknown formatter: {formatter}"

            if result.returncode == 0:
                return f"Formatted: {path}"
            return f"Error: {result.stderr}"
        except FileNotFoundError:
            return f"Error: {formatter} not found. Install it first."
        except Exception as e:
            return f"Error: {e}"


class CodeLintTool(BaseTool):
    """Lint code and return issues."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "code_lint"

    @property
    def description(self) -> str:
        return "Lint code and report issues."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File or directory to lint"},
                "linter": {"type": "string", "enum": ["ruff", "pylint", "eslint"], "default": "ruff"},
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        linter = kwargs.get("linter", "ruff")
        validated = self._sandbox.validate_path(path)

        try:
            if linter == "ruff":
                result = subprocess.run(
                    ["ruff", "check", str(validated)],
                    capture_output=True, text=True, timeout=60
                )
            elif linter == "pylint":
                result = subprocess.run(
                    ["pylint", str(validated)],
                    capture_output=True, text=True, timeout=60
                )
            elif linter == "eslint":
                result = subprocess.run(
                    ["eslint", str(validated)],
                    capture_output=True, text=True, timeout=60
                )
            else:
                return f"Unknown linter: {linter}"

            return result.stdout or "(no issues found)"
        except FileNotFoundError:
            return f"Error: {linter} not found. Install it first."
        except Exception as e:
            return f"Error: {e}"


code_format = CodeFormatTool()
code_lint = CodeLintTool()
