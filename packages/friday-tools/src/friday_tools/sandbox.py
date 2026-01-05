"""
Security sandboxing for filesystem and shell operations.

Ref: docs/specs/tool_specification.md - Section 5: Security

Provides path validation and command filtering to prevent
dangerous operations from tools.
"""

from __future__ import annotations

import os
import re
from pathlib import Path


class SecurityError(Exception):
    """Raised when a security violation is detected."""

    pass


class PathSecurityError(SecurityError):
    """Raised when a path access is not allowed."""

    pass


class CommandSecurityError(SecurityError):
    """Raised when a command is not allowed."""

    pass


class FilesystemSandbox:
    """
    Filesystem access sandbox with path validation.

    Restricts file operations to allowed directories and prevents
    access to sensitive system paths.

    Example:
        ```python
        sandbox = FilesystemSandbox(
            allowed_paths=["/home/user/workspace"],
            blocked_paths=["/home/user/workspace/.git"],
        )

        sandbox.validate_path("/home/user/workspace/file.txt")  # OK
        sandbox.validate_path("/etc/passwd")  # Raises PathSecurityError
        ```
    """

    # Default blocked paths that should never be accessed
    DEFAULT_BLOCKED_PATTERNS = [
        r"^/etc/",
        r"^/var/",
        r"^/usr/",
        r"^/bin/",
        r"^/sbin/",
        r"^/root/",
        r"^/proc/",
        r"^/sys/",
        r"^/dev/",
        r".*\.ssh/",
        r".*\.gnupg/",
        r".*\.aws/",
        r".*\.kube/",
        r".*\.env$",
        r".*\.env\..*",
        r".*/\.git/config$",
        r".*/\.git/credentials$",
    ]

    def __init__(
        self,
        allowed_paths: list[str | Path] | None = None,
        blocked_paths: list[str | Path] | None = None,
        blocked_patterns: list[str] | None = None,
        allow_home: bool = True,
        allow_temp: bool = True,
    ):
        """
        Initialize filesystem sandbox.

        Args:
            allowed_paths: Explicit list of allowed directory paths.
            blocked_paths: Explicit list of blocked paths (overrides allowed).
            blocked_patterns: Regex patterns for blocked paths.
            allow_home: Allow access to user's home directory.
            allow_temp: Allow access to temp directories.
        """
        self.allowed_paths: list[Path] = []
        self.blocked_paths: list[Path] = []
        self.blocked_patterns: list[re.Pattern] = []

        # Add default blocked patterns
        for pattern in self.DEFAULT_BLOCKED_PATTERNS:
            self.blocked_patterns.append(re.compile(pattern))

        # Add custom blocked patterns
        if blocked_patterns:
            for pattern in blocked_patterns:
                self.blocked_patterns.append(re.compile(pattern))

        # Add allowed paths
        if allowed_paths:
            for path in allowed_paths:
                self.allowed_paths.append(Path(path).resolve())

        # Add blocked paths
        if blocked_paths:
            for path in blocked_paths:
                self.blocked_paths.append(Path(path).resolve())

        # Add home directory if allowed
        if allow_home:
            home = Path.home()
            if home.exists():
                self.allowed_paths.append(home)

        # Add temp directories if allowed
        if allow_temp:
            import tempfile
            self.allowed_paths.append(Path(tempfile.gettempdir()).resolve())
            # Also add /tmp explicitly on Unix
            if os.name != "nt":
                self.allowed_paths.append(Path("/tmp").resolve())

    def validate_path(self, path: str | Path) -> Path:
        """
        Validate that a path is safe to access.

        Args:
            path: The path to validate.

        Returns:
            Resolved Path object if valid.

        Raises:
            PathSecurityError: If path is not allowed.
        """
        resolved = Path(path).resolve()
        path_str = str(resolved)

        # Check blocked patterns first
        for pattern in self.blocked_patterns:
            if pattern.search(path_str):
                raise PathSecurityError(
                    f"Path matches blocked pattern: {path}"
                )

        # Check explicit blocked paths
        for blocked in self.blocked_paths:
            if resolved == blocked or self._is_child_of(resolved, blocked):
                raise PathSecurityError(
                    f"Path is explicitly blocked: {path}"
                )

        # Check if path is within allowed paths
        if self.allowed_paths:
            allowed = False
            for allowed_path in self.allowed_paths:
                if resolved == allowed_path or self._is_child_of(resolved, allowed_path):
                    allowed = True
                    break

            if not allowed:
                raise PathSecurityError(
                    f"Path is not within allowed directories: {path}"
                )

        return resolved

    def _is_child_of(self, path: Path, parent: Path) -> bool:
        """Check if path is a child of parent."""
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    def is_path_allowed(self, path: str | Path) -> bool:
        """
        Check if a path is allowed without raising an error.

        Args:
            path: The path to check.

        Returns:
            True if path is allowed, False otherwise.
        """
        try:
            self.validate_path(path)
            return True
        except PathSecurityError:
            return False


class ShellSandbox:
    """
    Shell command sandbox with command filtering.

    Restricts which shell commands can be executed and validates
    command arguments for safety.

    Example:
        ```python
        sandbox = ShellSandbox(
            allowed_commands=["ls", "cat", "grep"],
            blocked_commands=["rm", "sudo"],
        )

        sandbox.validate_command("ls -la")  # OK
        sandbox.validate_command("rm -rf /")  # Raises CommandSecurityError
        ```
    """

    # Commands that are always blocked
    DEFAULT_BLOCKED_COMMANDS = {
        "sudo",
        "su",
        "chmod",
        "chown",
        "chgrp",
        "mount",
        "umount",
        "fdisk",
        "mkfs",
        "dd",
        "shutdown",
        "reboot",
        "halt",
        "poweroff",
        "init",
        "systemctl",
        "service",
        "kill",
        "killall",
        "pkill",
    }

    # Dangerous argument patterns
    DANGEROUS_PATTERNS = [
        r";\s*",  # Command chaining with ;
        r"\|\s*",  # Pipes
        r"&&",  # AND chaining
        r"\|\|",  # OR chaining
        r"\$\(",  # Command substitution
        r"`",  # Backtick command substitution
        r">\s*/",  # Redirect to root paths
        r"<\s*/etc/",  # Read from sensitive paths
        r"\.\./\.\./",  # Path traversal
    ]

    def __init__(
        self,
        allowed_commands: list[str] | None = None,
        blocked_commands: list[str] | None = None,
        allow_dangerous_patterns: bool = False,
    ):
        """
        Initialize shell sandbox.

        Args:
            allowed_commands: Whitelist of allowed commands (if set, only these allowed).
            blocked_commands: Additional blocked commands.
            allow_dangerous_patterns: If True, allow shell metacharacters.
        """
        self.allowed_commands: set[str] | None = None
        if allowed_commands:
            self.allowed_commands = set(allowed_commands)

        self.blocked_commands = self.DEFAULT_BLOCKED_COMMANDS.copy()
        if blocked_commands:
            self.blocked_commands.update(blocked_commands)

        self.allow_dangerous_patterns = allow_dangerous_patterns
        self.dangerous_patterns = [
            re.compile(p) for p in self.DANGEROUS_PATTERNS
        ]

    def validate_command(self, command: str) -> str:
        """
        Validate that a command is safe to execute.

        Args:
            command: The shell command to validate.

        Returns:
            The validated command string.

        Raises:
            CommandSecurityError: If command is not allowed.
        """
        # Extract base command
        parts = command.strip().split()
        if not parts:
            raise CommandSecurityError("Empty command")

        base_command = parts[0]

        # Remove any path prefix to get just the command name
        if "/" in base_command:
            base_command = base_command.split("/")[-1]

        # Check if command is blocked
        if base_command in self.blocked_commands:
            raise CommandSecurityError(
                f"Command is blocked: {base_command}"
            )

        # Check if command is in allowed list (if whitelist is set)
        if self.allowed_commands is not None:
            if base_command not in self.allowed_commands:
                raise CommandSecurityError(
                    f"Command is not in allowed list: {base_command}"
                )

        # Check for dangerous patterns
        if not self.allow_dangerous_patterns:
            for pattern in self.dangerous_patterns:
                if pattern.search(command):
                    raise CommandSecurityError(
                        f"Command contains dangerous pattern: {command}"
                    )

        return command

    def is_command_allowed(self, command: str) -> bool:
        """
        Check if a command is allowed without raising an error.

        Args:
            command: The command to check.

        Returns:
            True if command is allowed, False otherwise.
        """
        try:
            self.validate_command(command)
            return True
        except CommandSecurityError:
            return False
