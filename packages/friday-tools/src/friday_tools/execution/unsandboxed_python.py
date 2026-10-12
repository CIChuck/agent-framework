# mypy: ignore-errors
"""Unsandboxed Python code execution tool.

Executes Python code directly in Friday's process without sandbox isolation.
Use with caution - code has full access to the Python environment.
"""

from __future__ import annotations

import asyncio
import io
import traceback
from contextlib import redirect_stderr, redirect_stdout
from typing import Any

from ..definition import BaseTool


class UnsandboxedPythonExecuteTool(BaseTool):
    """Execute Python code directly in Friday's process (unsandboxed).

    This tool runs code in the same Python environment as Friday,
    with access to all installed packages and system resources.

    Use cases:
    - Quick calculations and data processing
    - Accessing Friday's installed packages
    - Code that needs to interact with the local environment

    Warning:
        Code runs without isolation. Use the sandboxed version
        for untrusted code.
    """

    @property
    def name(self) -> str:
        return "python_execute_unsandboxed"

    @property
    def description(self) -> str:
        return (
            "Execute Python code directly in Friday's environment without "
            "sandbox isolation. Has full access to installed packages and "
            "the local environment. Set __result__ variable to return a value."
        )

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30)",
                    "default": 30,
                },
            },
            "required": ["code"],
        }

    async def execute(self, **kwargs: Any) -> str:
        """Execute Python code with captured stdout/stderr."""
        code = kwargs["code"]
        timeout = kwargs.get("timeout", 30)

        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(self._execute_code, code),
                timeout=timeout,
            )
            return result
        except TimeoutError:
            return f"Error: Execution timed out after {timeout} seconds"
        except Exception as e:
            return f"Error: {e}"

    def _execute_code(self, code: str) -> str:
        """Execute code synchronously with output capture."""
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # Create execution namespace with common imports available
        namespace: dict[str, Any] = {
            "__builtins__": __builtins__,
            "__name__": "__main__",
        }

        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, namespace)

            # Build output
            output_parts = []

            stdout_val = stdout_capture.getvalue()
            if stdout_val:
                output_parts.append(stdout_val.rstrip())

            stderr_val = stderr_capture.getvalue()
            if stderr_val:
                output_parts.append(f"--- stderr ---\n{stderr_val.rstrip()}")

            # Check for explicit return value
            if "__result__" in namespace:
                result_val = namespace["__result__"]
                output_parts.append(f"--- return value ---\n{result_val}")

            return "\n".join(output_parts) if output_parts else "(no output)"

        except Exception:
            # Capture the exception traceback
            stderr_val = stderr_capture.getvalue()
            tb = traceback.format_exc()

            output_parts = []
            stdout_val = stdout_capture.getvalue()
            if stdout_val:
                output_parts.append(stdout_val.rstrip())
            if stderr_val:
                output_parts.append(f"--- stderr ---\n{stderr_val.rstrip()}")
            output_parts.append(f"--- exception ---\n{tb.rstrip()}")

            return "\n".join(output_parts)


# Default instance for easy import
python_execute_unsandboxed = UnsandboxedPythonExecuteTool()
