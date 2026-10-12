# mypy: ignore-errors
"""
OS Command Executor with configurable blocklist safety.

Ref: docs/reference/specs/tool_specification.md - Category 4: Shell Execution

Provides a more permissive command execution tool compared to ShellSandbox.
Allows pipes, command chaining, and redirects (within cwd) while blocking
destructive commands via a configurable blocklist.
"""

from __future__ import annotations

import asyncio
import os
import re
import shlex
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

from ..base import FridayTool, ToolResult

# =============================================================================
# DEFAULT BLOCKED COMMANDS
# =============================================================================
# Commands that are blocked by default. Users can override with custom blocklist.
# These commands are considered destructive or dangerous for agent execution.
# =============================================================================

DEFAULT_BLOCKED_COMMANDS: set[str] = {
    # Privilege escalation
    "sudo",
    "su",
    "doas",
    # Destructive file operations
    "rm",
    "rmdir",
    "shred",
    "unlink",
    # Dangerous system operations
    "mkfs",
    "dd",
    "fdisk",
    "parted",
    "shutdown",
    "reboot",
    "poweroff",
    "halt",
    "init",
    # Process/service manipulation
    "kill",
    "killall",
    "pkill",
    "systemctl",
    "service",
    "launchctl",
    # Permission changes
    "chmod",
    "chown",
    "chgrp",
    # Mount operations
    "mount",
    "umount",
    # Package managers (can modify system)
    "apt",
    "apt-get",
    "yum",
    "dnf",
    "pacman",
    "brew",
    "pip",
    "npm",
    "cargo",
    # File manipulation (blocked for safety)
    "mv",  # Can overwrite/move files
    "cp",  # Can overwrite files
}


# =============================================================================
# DEFAULT BLOCKED PATTERNS
# =============================================================================
# Regex patterns for dangerous command sequences.
# =============================================================================

DEFAULT_BLOCKED_PATTERNS: list[str] = [
    r":\(\)\{.*\}",  # Fork bomb pattern
]


# =============================================================================
# COMMAND SAFETY VALIDATOR
# =============================================================================


class CommandSafetyValidator:
    """
    Validates commands are safe to execute using a blocklist approach.

    Unlike ShellSandbox which blocks pipes and chaining, this validator
    allows complex shell expressions while blocking specific dangerous commands.
    """

    def __init__(
        self,
        blocked_commands: set[str] | None = None,
        blocked_patterns: list[str] | None = None,
    ):
        """
        Initialize validator with configurable blocklists.

        Args:
            blocked_commands: Commands to block (uses DEFAULT_BLOCKED_COMMANDS if None)
            blocked_patterns: Regex patterns to block (uses DEFAULT_BLOCKED_PATTERNS if None)
        """  # noqa: E501
        self.blocked_commands = blocked_commands or DEFAULT_BLOCKED_COMMANDS.copy()
        self.blocked_patterns = [
            re.compile(p) for p in (blocked_patterns or DEFAULT_BLOCKED_PATTERNS)
        ]

    def validate(self, command: str, cwd: Path) -> tuple[bool, str | None]:
        """
        Validate command is safe to execute.

        Args:
            command: The command line to validate.
            cwd: The working directory for redirect validation.

        Returns:
            Tuple of (is_safe, error_message). error_message is None if safe.
        """
        # 1. Check for blocked patterns first (e.g., fork bombs)
        for pattern in self.blocked_patterns:
            if pattern.search(command):
                return False, "Command matches blocked pattern"

        # 2. Extract and check all commands in the command line
        commands = self._extract_commands(command)
        for cmd in commands:
            if cmd in self.blocked_commands:
                return False, f"Blocked command: {cmd}"

        # 3. Validate redirects (cwd-only)
        is_valid, redirect_error = self._validate_redirects(command, cwd)
        if not is_valid:
            return False, redirect_error

        return True, None

    def _extract_commands(self, command_line: str) -> list[str]:
        """
        Extract individual command names from a command line.

        Handles:
        - Pipes: cmd1 | cmd2
        - Chaining: cmd1 && cmd2, cmd1 || cmd2, cmd1 ; cmd2
        - Subshells: $(cmd), `cmd`
        - Command prefixes: /usr/bin/cmd -> cmd

        Args:
            command_line: The full command line string.

        Returns:
            List of base command names found in the command line.
        """
        commands: list[str] = []

        # Replace subshell markers with semicolon-separated content
        # This ensures subshell commands are treated as separate commands
        normalized = command_line
        # Replace $(...) with semicolon-separated content (so it splits as a separate segment)  # noqa: E501
        normalized = re.sub(r"\$\(([^)]+)\)", r"; \1 ;", normalized)
        # Replace `...` with semicolon-separated content
        normalized = re.sub(r"`([^`]+)`", r"; \1 ;", normalized)

        # Split on shell operators: |, &&, ||, ;
        # Also handle && and || before single & and |
        segments = re.split(r"\s*(?:\|\||&&|[|;&])\s*", normalized)

        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            # Handle command with arguments
            # Try to get the first word (the command)
            try:
                # Use shlex for proper parsing when possible
                parts = shlex.split(segment)
                if parts:
                    cmd = parts[0]
                    # Strip path prefix: /usr/bin/cat -> cat
                    if "/" in cmd:
                        cmd = cmd.rsplit("/", 1)[-1]
                    commands.append(cmd)
            except ValueError:
                # shlex failed (unbalanced quotes, etc.)
                # Fall back to simple split
                parts = segment.split()
                if parts:
                    cmd = parts[0]
                    if "/" in cmd:
                        cmd = cmd.rsplit("/", 1)[-1]
                    commands.append(cmd)

        return commands

    def _validate_redirects(self, command: str, cwd: Path) -> tuple[bool, str | None]:
        """
        Validate redirects target only relative paths within cwd.

        Redirects (`>`, `>>`) are allowed but must:
        - Be relative paths (not absolute)
        - Not use path traversal (..)
        - Not target home directory (~)
        - Resolve within the working directory

        Args:
            command: The command line to check.
            cwd: The working directory.

        Returns:
            Tuple of (is_valid, error_message). error_message is None if valid.
        """
        # Pattern to extract redirect targets
        # Matches: >, >>, 2>, 2>>, &>, etc.
        # Captures the target path after the redirect operator
        redirect_pattern = r"(?:>>?|[12]>>?|&>>?)\s*([^\s|;&]+)"
        targets = re.findall(redirect_pattern, command)

        resolved_cwd = cwd.resolve()

        for target in targets:
            target = target.strip()

            # Skip if target is /dev/null (common pattern)
            if target == "/dev/null":
                continue

            target_path = Path(target)

            # Block absolute paths
            if target_path.is_absolute():
                return False, f"Redirect to absolute path not allowed: {target}"

            # Block path traversal (..)
            if ".." in target:
                return False, f"Path traversal in redirect not allowed: {target}"

            # Block home directory (~)
            if target.startswith("~"):
                return False, f"Redirect to home directory not allowed: {target}"

            # Resolve and verify within cwd
            try:
                resolved = (cwd / target_path).resolve()
                if not str(resolved).startswith(str(resolved_cwd)):
                    return False, f"Redirect target escapes working directory: {target}"
            except (OSError, ValueError) as e:
                return False, f"Invalid redirect target: {target} ({e})"

        return True, None


# =============================================================================
# COMMAND EXECUTE TOOL
# =============================================================================


class CommandExecuteTool(FridayTool):
    """
    Execute OS commands with safety restrictions.

    Allows useful commands like curl, ls, grep, pipes, and command chaining
    while blocking destructive operations via a configurable blocklist.

    This is more permissive than ShellExecuteTool (which uses ShellSandbox)
    but still prevents dangerous operations.

    Features:
        - Configurable blocklist for commands
        - Pattern-based blocking (e.g., fork bombs)
        - Redirect validation (cwd-only)
        - Timeout support
        - Environment variable passthrough

    Examples:
        Allowed:
        - curl -s https://api.example.com/health
        - ls -la /tmp
        - echo "hello" | grep "ell"
        - cat /etc/hosts
        - curl ... | jq '.data'

        Blocked:
        - rm -rf /
        - sudo whoami
        - chmod 777 file
        - echo "test" > /etc/passwd
    """

    name = "command_execute"
    description = (
        "Execute OS command line. Blocks destructive commands (rm, sudo, etc.) "
        "but allows curl, ls, grep, pipes, command chaining, etc."
    )
    category = "shell"
    tags = ["command", "shell", "execute", "curl", "system"]

    class Input(BaseModel):
        """Input parameters for command execution."""

        command: str = Field(description="Command line to execute")
        cwd: str | None = Field(
            default=None, description="Working directory (defaults to current)"
        )
        timeout: int = Field(default=30, ge=1, le=300, description="Timeout in seconds")
        env: dict[str, str] | None = Field(
            default=None, description="Additional environment variables"
        )

    def __init__(
        self,
        blocked_commands: set[str] | None = None,
        blocked_patterns: list[str] | None = None,
    ):
        """
        Initialize with optional custom blocklists.

        Args:
            blocked_commands: Commands to block (merges with defaults if None)
            blocked_patterns: Regex patterns to block (uses defaults if None)
        """
        super().__init__()
        self.validator = CommandSafetyValidator(blocked_commands, blocked_patterns)

    async def run(self, args: Input) -> ToolResult:
        """
        Execute the command and return results.

        Args:
            args: Validated input parameters.

        Returns:
            ToolResult with stdout, stderr, and return code.
        """
        # Resolve working directory
        cwd = Path(args.cwd) if args.cwd else Path.cwd()
        if not cwd.exists():
            return ToolResult(
                content=f"Working directory does not exist: {cwd}",
                error=f"Working directory does not exist: {cwd}",
            )
        if not cwd.is_dir():
            return ToolResult(
                content=f"Path is not a directory: {cwd}",
                error=f"Path is not a directory: {cwd}",
            )

        # Validate command safety
        is_safe, error = self.validator.validate(args.command, cwd)
        if not is_safe:
            return ToolResult(
                content=f"Command blocked: {error}",
                error=f"Command blocked: {error}",
            )

        # Build environment
        env = {**os.environ}
        if args.env:
            env.update(args.env)

        # Execute via subprocess using shell
        try:
            loop = asyncio.get_event_loop()

            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: subprocess.run(
                        args.command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=str(cwd),
                        env=env,
                    ),
                ),
                timeout=args.timeout,
            )

            # Build content string
            output_parts = []
            if result.stdout:
                output_parts.append(result.stdout.rstrip())
            if result.stderr:
                output_parts.append(f"--- stderr ---\n{result.stderr.rstrip()}")
            if result.returncode != 0:
                output_parts.append(f"\nExit code: {result.returncode}")

            content = "\n".join(output_parts) if output_parts else "(no output)"

            return ToolResult(
                content=content,
                data={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                },
                error=result.stderr if result.returncode != 0 else None,
            )

        except TimeoutError:
            return ToolResult(
                content=f"Command timed out after {args.timeout}s",
                error=f"Command timed out after {args.timeout}s",
            )
        except Exception as e:
            return ToolResult(
                content=f"Command execution failed: {e}",
                error=str(e),
            )


# Convenience instance
command_execute = CommandExecuteTool()
