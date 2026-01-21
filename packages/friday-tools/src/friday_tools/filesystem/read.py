"""
Filesystem reading tools.

Ref: docs/specs/tool_specification.md - Category 1: Filesystem - Reading
"""

from __future__ import annotations

import os
import re
import stat
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from ..base import FridayTool, ToolResult
from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class FileReadTool(FridayTool):
    """
    Read the contents of a text file.

    Reads and returns the full contents of a file with configurable encoding.
    Useful for examining configuration files, source code, logs, and other
    text-based files.
    """

    name = "file_read"
    description = "Read the contents of a text file."
    category = "filesystem"
    tags = ["file", "read", "text", "cat"]

    class Input(BaseModel):
        path: str = Field(
            description="Path to the file to read"
        )
        encoding: str = Field(
            default="utf-8",
            description="File encoding (e.g., utf-8, latin-1, ascii)"
        )
        max_lines: int | None = Field(
            default=None,
            description="Maximum number of lines to read (None for all)"
        )

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    async def run(self, args: Input) -> ToolResult:
        """Execute the file read tool."""
        validated_path = self._sandbox.validate_path(args.path)

        if not validated_path.exists():
            return ToolResult(
                content=f"Error: File not found: {args.path}",
                error=f"File not found: {args.path}"
            )

        if not validated_path.is_file():
            return ToolResult(
                content=f"Error: Not a file: {args.path}",
                error=f"Not a file: {args.path}"
            )

        try:
            content = validated_path.read_text(encoding=args.encoding)

            # Apply line limit if specified
            truncated = False
            total_lines = 0
            if args.max_lines is not None:
                lines = content.splitlines(keepends=True)
                total_lines = len(lines)
                if total_lines > args.max_lines:
                    content = "".join(lines[:args.max_lines])
                    content += f"\n... ({args.max_lines}/{total_lines} lines)"
                    truncated = True

            # Get file stats for metadata
            stat_info = validated_path.stat()

            # Count lines in content
            line_count = content.count("\n")
            if content and not content.endswith("\n"):
                line_count += 1

            return ToolResult(
                content=content,
                data={
                    "path": str(validated_path),
                    "size_bytes": stat_info.st_size,
                    "line_count": line_count,
                    "encoding": args.encoding,
                },
                metadata={
                    "path": args.path,
                    "encoding": args.encoding,
                    "truncated": truncated,
                }
            )

        except UnicodeDecodeError as e:
            msg = f"Failed to decode with encoding {args.encoding}: {e}"
            return ToolResult(
                content=f"Error: {msg}",
                error=f"Encoding error: {e}"
            )
        except PermissionError:
            return ToolResult(
                content=f"Error: Permission denied: {args.path}",
                error="Permission denied"
            )
        except Exception as e:
            return ToolResult(
                content=f"Error: Failed to read file: {e}",
                error=str(e)
            )


class FileReadLinesTool(BaseTool):
    """Read specific lines from a file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_read_lines"

    @property
    def description(self) -> str:
        return "Read a specific range of lines from a file."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file",
                },
                "start_line": {
                    "type": "integer",
                    "description": "Starting line number (1-indexed)",
                    "minimum": 1,
                },
                "end_line": {
                    "type": "integer",
                    "description": "Ending line number (inclusive)",
                    "minimum": 1,
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding (default: utf-8)",
                    "default": "utf-8",
                },
            },
            "required": ["path", "start_line", "end_line"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        start_line = kwargs["start_line"]
        end_line = kwargs["end_line"]
        encoding = kwargs.get("encoding", "utf-8")

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: File not found: {path}"

        try:
            with validated_path.open(encoding=encoding) as f:
                lines = f.readlines()

            # Adjust for 1-indexed lines
            start_idx = start_line - 1
            end_idx = end_line

            if start_idx >= len(lines):
                return f"Error: Start line {start_line} exceeds file length ({len(lines)} lines)"

            selected_lines = lines[start_idx:end_idx]
            return "".join(selected_lines)

        except Exception as e:
            return f"Error: Failed to read file: {e}"


class FileInfoTool(BaseTool):
    """Get file metadata."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_info"

    @property
    def description(self) -> str:
        return "Get metadata about a file including size, modification time, and permissions."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file",
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: Path not found: {path}"

        try:
            stat_info = validated_path.stat()

            # Determine file type
            if validated_path.is_file():
                file_type = "file"
            elif validated_path.is_dir():
                file_type = "directory"
            elif validated_path.is_symlink():
                file_type = "symlink"
            else:
                file_type = "other"

            # Format permissions
            mode = stat_info.st_mode
            perms = stat.filemode(mode)

            # Format times
            mtime = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
            ctime = datetime.fromtimestamp(stat_info.st_ctime).isoformat()
            atime = datetime.fromtimestamp(stat_info.st_atime).isoformat()

            info = {
                "path": str(validated_path),
                "type": file_type,
                "size_bytes": stat_info.st_size,
                "permissions": perms,
                "mode_octal": oct(stat_info.st_mode)[-3:],
                "owner_uid": stat_info.st_uid,
                "group_gid": stat_info.st_gid,
                "modified": mtime,
                "created": ctime,
                "accessed": atime,
            }

            # Format as readable output
            lines = [f"{k}: {v}" for k, v in info.items()]
            return "\n".join(lines)

        except Exception as e:
            return f"Error: Failed to get file info: {e}"


class FileGrepTool(BaseTool):
    """Search file contents with regex."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_grep"

    @property
    def description(self) -> str:
        return "Search for a pattern in a file using regular expressions."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to search",
                },
                "pattern": {
                    "type": "string",
                    "description": "Regular expression pattern to search for",
                },
                "case_insensitive": {
                    "type": "boolean",
                    "description": "Perform case-insensitive search",
                    "default": False,
                },
                "context_lines": {
                    "type": "integer",
                    "description": "Number of context lines to show before/after matches",
                    "default": 0,
                },
            },
            "required": ["path", "pattern"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        pattern = kwargs["pattern"]
        case_insensitive = kwargs.get("case_insensitive", False)
        context_lines = kwargs.get("context_lines", 0)

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: File not found: {path}"

        try:
            flags = re.IGNORECASE if case_insensitive else 0
            regex = re.compile(pattern, flags)

            with validated_path.open(encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            matches = []
            for i, line in enumerate(lines, 1):
                if regex.search(line):
                    # Collect context
                    start = max(0, i - 1 - context_lines)
                    end = min(len(lines), i + context_lines)

                    if context_lines > 0:
                        context_block = []
                        for j in range(start, end):
                            prefix = ">" if j == i - 1 else " "
                            context_block.append(f"{prefix}{j+1}: {lines[j].rstrip()}")
                        matches.append("\n".join(context_block))
                    else:
                        matches.append(f"{i}: {line.rstrip()}")

            if not matches:
                return f"No matches found for pattern: {pattern}"

            separator = "\n---\n" if context_lines > 0 else "\n"
            return separator.join(matches)

        except re.error as e:
            return f"Error: Invalid regex pattern: {e}"
        except Exception as e:
            return f"Error: Failed to search file: {e}"


# Convenience instances for direct use
file_read = FileReadTool()
file_read_lines = FileReadLinesTool()
file_info = FileInfoTool()
file_grep = FileGrepTool()
