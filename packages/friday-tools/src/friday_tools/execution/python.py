# mypy: ignore-errors
"""Python code execution tool using friday-sandbox."""

from __future__ import annotations

from typing import Any

from ..definition import BaseTool


class PythonExecuteTool(BaseTool):
    """Execute Python code in a sandbox."""

    def __init__(self, sandbox=None):
        self._sandbox = sandbox

    @property
    def name(self) -> str:
        return "python_execute"

    @property
    def description(self) -> str:
        return "Execute Python code in an isolated sandbox environment."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"},
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds",
                    "default": 30,
                },
            },
            "required": ["code"],
        }

    async def execute(self, **kwargs: Any) -> str:
        code = kwargs["code"]
        timeout = kwargs.get("timeout", 30)

        if self._sandbox is None:
            # Try to import and use subprocess sandbox as fallback
            try:
                from friday_sandbox.subprocess import SubprocessSandbox

                self._sandbox = SubprocessSandbox()
            except ImportError:
                return "Error: friday-sandbox not installed or Docker not available"

        try:
            result = await self._sandbox.execute(code, timeout_seconds=timeout)
            output = result.stdout
            if result.stderr:
                output += f"\n--- stderr ---\n{result.stderr}"
            if result.return_value:
                output += f"\n--- return value ---\n{result.return_value}"
            return output or "(no output)"
        except Exception as e:
            return f"Error: {e}"


python_execute = PythonExecuteTool()
