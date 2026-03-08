# mypy: ignore-errors
"""
Filesystem reading tools.

Ref: docs/specs/tool_specification.md - Category 1: Filesystem - Reading
Ref: docs/build-plan/tool-improvement-build-plan.md - Enhanced file reading
"""

from __future__ import annotations

import re
import stat
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ..base import FridayTool, ToolResult
from ..definition import BaseTool
from ..sandbox import FilesystemSandbox
from .readers import read_with_smart_encoding


class FileReadTool(FridayTool):
    """
    Read the contents of a text file with smart encoding detection.

    Reads and returns the contents of a file with automatic encoding detection.
    Supports pagination with start_line and max_lines for efficient handling of
    large files. Uses streaming to avoid loading entire file into memory.

    Useful for examining configuration files, source code, logs, and other
    text-based files.
    """

    name = "file_read"
    description = "Read the contents of a text file with smart encoding detection."
    category = "filesystem"
    tags = ["file", "read", "text", "cat"]

    class Input(BaseModel):
        path: str = Field(description="Path to the file to read")
        encoding: str = Field(
            default="auto",
            description="File encoding. Use 'auto' for automatic detection, or specify explicitly (utf-8, latin-1, etc.)",  # noqa: E501
        )
        start_line: int = Field(
            default=1, ge=1, description="Starting line number (1-indexed, default: 1)"
        )
        max_lines: int | None = Field(
            default=None, description="Maximum number of lines to read (None for all)"
        )

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    async def run(self, args: Input) -> ToolResult:
        """Execute the file read tool."""
        validated_path = self._sandbox.validate_path(args.path)

        if not validated_path.exists():
            return ToolResult(
                content=f"Error: File not found: {args.path}",
                error=f"File not found: {args.path}",
            )

        if not validated_path.is_file():
            return ToolResult(
                content=f"Error: Not a file: {args.path}",
                error=f"Not a file: {args.path}",
            )

        try:
            # Use smart encoding detection
            explicit_encoding = None if args.encoding == "auto" else args.encoding
            full_content, encoding_result = read_with_smart_encoding(
                validated_path,
                explicit_encoding=explicit_encoding,
            )

            # Get file stats for metadata
            stat_info = validated_path.stat()

            # Count total lines
            all_lines = full_content.splitlines(keepends=True)
            total_lines = len(all_lines)

            # Apply line range using efficient slicing
            # start_line is 1-indexed, so subtract 1 for 0-indexed array
            start_idx = args.start_line - 1
            truncated = False
            truncated_at_line = None

            if start_idx >= total_lines:
                return ToolResult(
                    content=f"Error: Start line {args.start_line} exceeds file length ({total_lines} lines)",  # noqa: E501
                    error="Start line out of range",
                )

            if args.max_lines is not None:
                end_idx = min(start_idx + args.max_lines, total_lines)
                selected_lines = all_lines[start_idx:end_idx]
                if end_idx < total_lines:
                    truncated = True
                    truncated_at_line = end_idx
            else:
                selected_lines = all_lines[start_idx:]

            content = "".join(selected_lines)

            # Add truncation notice if applicable
            if truncated:
                content += f"\n... (showing lines {args.start_line}-{truncated_at_line} of {total_lines})"  # noqa: E501

            # Count lines in returned content
            line_count = len(selected_lines)

            return ToolResult(
                content=content,
                data={
                    "path": str(validated_path),
                    "size_bytes": stat_info.st_size,
                    "line_count": line_count,
                    "total_lines": total_lines,
                    "encoding": encoding_result.encoding,
                    "encoding_confidence": encoding_result.confidence,
                    "encoding_method": encoding_result.method,
                },
                metadata={
                    "path": args.path,
                    "encoding": encoding_result.encoding,
                    "truncated": truncated,
                    "truncated_at_line": truncated_at_line,
                    "start_line": args.start_line,
                },
            )

        except UnicodeDecodeError as e:
            msg = f"Failed to decode file: {e}"
            return ToolResult(content=f"Error: {msg}", error=f"Encoding error: {e}")
        except PermissionError:
            return ToolResult(
                content=f"Error: Permission denied: {args.path}",
                error="Permission denied",
            )
        except Exception as e:
            return ToolResult(content=f"Error: Failed to read file: {e}", error=str(e))


class FileReadLinesTool(BaseTool):
    """Read specific lines from a file.

    .. deprecated::
        Use FileReadTool with start_line and max_lines parameters instead.
        This tool is kept for backward compatibility.
    """

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
                return f"Error: Start line {start_line} exceeds file length ({len(lines)} lines)"  # noqa: E501

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
        return "Get metadata about a file including size, modification time, and permissions."  # noqa: E501

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
                    "description": "Number of context lines to show before/after matches",  # noqa: E501
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
                            context_block.append(
                                f"{prefix}{j + 1}: {lines[j].rstrip()}"
                            )
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
