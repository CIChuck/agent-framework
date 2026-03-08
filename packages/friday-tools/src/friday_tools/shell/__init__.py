# mypy: ignore-errors
"""
Shell and system tools.

Ref: docs/specs/tool_specification.md - Category 4: Shell/System Tools

Provides 7 tools for shell command execution and system information.
"""

from .command import (
    DEFAULT_BLOCKED_COMMANDS,
    DEFAULT_BLOCKED_PATTERNS,
    CommandExecuteTool,
    CommandSafetyValidator,
    command_execute,
)
from .execute import shell_execute, shell_script
from .system import environment_get, process_kill, process_list, system_info

__all__ = [
    # New permissive command executor
    "CommandExecuteTool",
    "CommandSafetyValidator",
    "DEFAULT_BLOCKED_COMMANDS",
    "DEFAULT_BLOCKED_PATTERNS",
    "command_execute",
    # Legacy shell tools (restrictive sandbox)
    "shell_execute",
    "shell_script",
    # System tools
    "process_list",
    "process_kill",
    "environment_get",
    "system_info",
]
