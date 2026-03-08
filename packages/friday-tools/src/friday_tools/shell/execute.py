# mypy: ignore-errors
"""
Shell execution tools.

Ref: docs/specs/tool_specification.md - Category 4: Shell Execution
"""

from __future__ import annotations

import asyncio
import subprocess
from typing import Any

from ..definition import BaseTool
from ..sandbox import ShellSandbox


class ShellExecuteTool(BaseTool):
    """Execute a shell command."""

    def __init__(self, sandbox: ShellSandbox | None = None):
        self._sandbox = sandbox or ShellSandbox()

    @property
    def name(self) -> str:
        return "shell_execute"

    @property
    def description(self) -> str:
        return "Execute a shell command and return the output."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute",
                },
                "cwd": {
                    "type": "string",
                    "description": "Working directory for the command",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds",
                    "default": 30,
                },
                "capture_stderr": {
                    "type": "boolean",
                    "description": "Include stderr in output",
                    "default": True,
                },
            },
            "required": ["command"],
        }

    async def execute(self, **kwargs: Any) -> str:
        command = kwargs["command"]
        cwd = kwargs.get("cwd")
        timeout = kwargs.get("timeout", 30)
        capture_stderr = kwargs.get("capture_stderr", True)

        # Validate command through sandbox
        try:
            self._sandbox.validate_command(command)
        except Exception as e:
            return f"Security Error: {e}"

        try:
            loop = asyncio.get_event_loop()

            # Run command in executor
            process = await loop.run_in_executor(
                None,
                lambda: subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE if capture_stderr else subprocess.DEVNULL,
                    cwd=cwd,
                    text=True,
                ),
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    loop.run_in_executor(None, process.communicate),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                return f"Error: Command timed out after {timeout} seconds"

            output = stdout
            if capture_stderr and stderr:
                output += f"\n--- stderr ---\n{stderr}"

            if process.returncode != 0:
                output += f"\n\nExit code: {process.returncode}"

            return output if output.strip() else "(no output)"

        except Exception as e:
            return f"Error: Failed to execute command: {e}"


class ShellScriptTool(BaseTool):
    """Execute a multi-line shell script."""

    def __init__(self, sandbox: ShellSandbox | None = None):
        self._sandbox = sandbox or ShellSandbox()

    @property
    def name(self) -> str:
        return "shell_script"

    @property
    def description(self) -> str:
        return "Execute a multi-line shell script."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "Shell script content (multi-line)",
                },
                "shell": {
                    "type": "string",
                    "description": "Shell to use (bash, sh, zsh)",
                    "default": "bash",
                    "enum": ["bash", "sh", "zsh"],
                },
                "cwd": {
                    "type": "string",
                    "description": "Working directory for the script",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds",
                    "default": 60,
                },
            },
            "required": ["script"],
        }

    async def execute(self, **kwargs: Any) -> str:
        script = kwargs["script"]
        shell = kwargs.get("shell", "bash")
        cwd = kwargs.get("cwd")
        timeout = kwargs.get("timeout", 60)

        # Validate each line of the script
        for line in script.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                # Skip validation for comments and empty lines
                # This is a simple heuristic; real validation would be more complex
                if not any(
                    line.startswith(kw)
                    for kw in [
                        "if",
                        "then",
                        "else",
                        "fi",
                        "for",
                        "do",
                        "done",
                        "while",
                        "case",
                        "esac",
                    ]
                ):
                    self._sandbox.validate_command(line)
            except Exception as e:
                return f"Security Error in script: {e}"

        try:
            loop = asyncio.get_event_loop()

            # Run script
            process = await loop.run_in_executor(
                None,
                lambda: subprocess.Popen(
                    [shell, "-c", script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cwd,
                    text=True,
                ),
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    loop.run_in_executor(None, process.communicate),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                return f"Error: Script timed out after {timeout} seconds"

            output = stdout
            if stderr:
                output += f"\n--- stderr ---\n{stderr}"

            if process.returncode != 0:
                output += f"\n\nExit code: {process.returncode}"

            return output if output.strip() else "(no output)"

        except Exception as e:
            return f"Error: Failed to execute script: {e}"


# Convenience instances
shell_execute = ShellExecuteTool()
shell_script = ShellScriptTool()
