"""
Directory tools.

Ref: docs/specs/tool_specification.md - Category 1 & 3: Directory Operations
"""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from ..base import FridayTool, ToolResult
from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


def _format_size(size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f}{unit}" if unit != "B" else f"{size}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


class DirectoryListTool(FridayTool):
    """
    List the contents of a directory.

    Shows files and directories with size and type information.
    Supports filtering by pattern and sorting options.
    """

    name = "directory_list"
    description = "List the contents of a directory with file sizes and types."
    category = "filesystem"
    tags = ["directory", "list", "files", "ls"]

    class Input(BaseModel):
        path: str = Field(description="Path to the directory to list")
        pattern: str = Field(
            default="*", description="Filter pattern (glob-style, e.g., '*.py')"
        )
        show_hidden: bool = Field(
            default=False, description="Include hidden files (starting with .)"
        )
        sort_by: Literal["name", "size", "modified"] = Field(
            default="name", description="Sort by: name, size, or modified"
        )

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    async def run(self, args: Input) -> ToolResult:
        """Execute the directory list tool."""
        validated_path = self._sandbox.validate_path(args.path)

        if not validated_path.exists():
            return ToolResult(
                content=f"Error: Directory not found: {args.path}",
                error=f"Directory not found: {args.path}",
            )

        if not validated_path.is_dir():
            return ToolResult(
                content=f"Error: Not a directory: {args.path}",
                error=f"Not a directory: {args.path}",
            )

        try:
            entries = []
            for item in validated_path.iterdir():
                # Skip hidden files unless requested
                if not args.show_hidden and item.name.startswith("."):
                    continue

                # Apply pattern filter
                if not fnmatch.fnmatch(item.name, args.pattern):
                    continue

                # Get file info
                stat = item.stat()
                entry = {
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                }
                entries.append(entry)

            # Sort entries
            if args.sort_by == "size":
                entries.sort(key=lambda x: x["size"], reverse=True)
            elif args.sort_by == "modified":
                entries.sort(key=lambda x: x["modified"], reverse=True)
            else:
                entries.sort(key=lambda x: x["name"])

            # Format output
            lines = []
            for e in entries:
                type_indicator = "d" if e["type"] == "dir" else "-"
                size_str = _format_size(e["size"])
                lines.append(f"{type_indicator} {size_str:>10} {e['name']}")

            if not lines:
                content = f"Directory is empty (or no matches for '{args.pattern}')"
            else:
                content = "\n".join(lines)

            return ToolResult(
                content=content,
                data={"entries": entries, "count": len(entries)},
                metadata={"path": args.path, "pattern": args.pattern},
            )

        except PermissionError:
            return ToolResult(
                content=f"Error: Permission denied: {args.path}",
                error="Permission denied",
            )
        except Exception as e:
            return ToolResult(
                content=f"Error: Failed to list directory: {e}", error=str(e)
            )


# Legacy BaseTool version for backwards compatibility
class DirectoryListToolLegacy(BaseTool):
    """List directory contents (legacy BaseTool version)."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "directory_list"

    @property
    def description(self) -> str:
        return "List the contents of a directory."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory",
                },
                "pattern": {
                    "type": "string",
                    "description": "Filter pattern (glob-style, e.g., '*.py')",
                    "default": "*",
                },
                "show_hidden": {
                    "type": "boolean",
                    "description": "Include hidden files (starting with .)",
                    "default": False,
                },
                "sort_by": {
                    "type": "string",
                    "description": "Sort by: name, size, modified",
                    "enum": ["name", "size", "modified"],
                    "default": "name",
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        pattern = kwargs.get("pattern", "*")
        show_hidden = kwargs.get("show_hidden", False)
        sort_by = kwargs.get("sort_by", "name")

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: Directory not found: {path}"

        if not validated_path.is_dir():
            return f"Error: Not a directory: {path}"

        try:
            entries = []
            for item in validated_path.iterdir():
                if not show_hidden and item.name.startswith("."):
                    continue
                if not fnmatch.fnmatch(item.name, pattern):
                    continue
                stat = item.stat()
                entry = {
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                }
                entries.append(entry)

            if sort_by == "size":
                entries.sort(key=lambda x: x["size"], reverse=True)
            elif sort_by == "modified":
                entries.sort(key=lambda x: x["modified"], reverse=True)
            else:
                entries.sort(key=lambda x: x["name"])

            lines = []
            for e in entries:
                type_indicator = "d" if e["type"] == "dir" else "-"
                size_str = _format_size(e["size"])
                lines.append(f"{type_indicator} {size_str:>10} {e['name']}")

            if not lines:
                return f"Directory is empty (or no matches for pattern '{pattern}')"

            return "\n".join(lines)

        except Exception as e:
            return f"Error: Failed to list directory: {e}"


class DirectoryTreeTool(BaseTool):
    """Display directory tree."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "directory_tree"

    @property
    def description(self) -> str:
        return "Display a directory tree structure."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Root directory path",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth to traverse",
                    "default": 3,
                },
                "show_hidden": {
                    "type": "boolean",
                    "description": "Include hidden files",
                    "default": False,
                },
                "dirs_only": {
                    "type": "boolean",
                    "description": "Show only directories",
                    "default": False,
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        max_depth = kwargs.get("max_depth", 3)
        show_hidden = kwargs.get("show_hidden", False)
        dirs_only = kwargs.get("dirs_only", False)

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: Directory not found: {path}"

        if not validated_path.is_dir():
            return f"Error: Not a directory: {path}"

        try:
            lines = [validated_path.name + "/"]
            self._build_tree(
                validated_path, lines, "", max_depth, 0, show_hidden, dirs_only
            )
            return "\n".join(lines)

        except Exception as e:
            return f"Error: Failed to build tree: {e}"

    def _build_tree(
        self,
        path: Path,
        lines: list[str],
        prefix: str,
        max_depth: int,
        current_depth: int,
        show_hidden: bool,
        dirs_only: bool,
    ) -> None:
        """Recursively build tree structure."""
        if current_depth >= max_depth:
            return

        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            return

        # Filter entries
        filtered = []
        for entry in entries:
            if not show_hidden and entry.name.startswith("."):
                continue
            if dirs_only and not entry.is_dir():
                continue
            filtered.append(entry)

        for i, entry in enumerate(filtered):
            is_last = i == len(filtered) - 1
            connector = "└── " if is_last else "├── "
            new_prefix = prefix + ("    " if is_last else "│   ")

            if entry.is_dir():
                lines.append(f"{prefix}{connector}{entry.name}/")
                self._build_tree(
                    entry,
                    lines,
                    new_prefix,
                    max_depth,
                    current_depth + 1,
                    show_hidden,
                    dirs_only,
                )
            else:
                lines.append(f"{prefix}{connector}{entry.name}")


class DirectoryCreateTool(BaseTool):
    """Create a directory."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "directory_create"

    @property
    def description(self) -> str:
        return "Create a new directory, including any necessary parent directories."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the directory to create",
                },
                "parents": {
                    "type": "boolean",
                    "description": "Create parent directories as needed",
                    "default": True,
                },
                "exist_ok": {
                    "type": "boolean",
                    "description": "Don't error if directory already exists",
                    "default": True,
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        parents = kwargs.get("parents", True)
        exist_ok = kwargs.get("exist_ok", True)

        validated_path = self._sandbox.validate_path(path)

        try:
            validated_path.mkdir(parents=parents, exist_ok=exist_ok)
            return f"Successfully created directory: {path}"

        except FileExistsError:
            return f"Error: Directory already exists: {path}"
        except Exception as e:
            return f"Error: Failed to create directory: {e}"


class FileSearchTool(BaseTool):
    """Search for files by pattern."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_search"

    @property
    def description(self) -> str:
        return "Search for files matching a glob pattern."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Root directory to search in",
                },
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern to match (e.g., '**/*.py')",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 100,
                },
                "type": {
                    "type": "string",
                    "description": "Filter by type: file, dir, or any",
                    "enum": ["file", "dir", "any"],
                    "default": "any",
                },
            },
            "required": ["path", "pattern"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        pattern = kwargs["pattern"]
        max_results = kwargs.get("max_results", 100)
        file_type = kwargs.get("type", "any")

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: Directory not found: {path}"

        if not validated_path.is_dir():
            return f"Error: Not a directory: {path}"

        try:
            results = []
            for match in validated_path.glob(pattern):
                # Type filter
                if file_type == "file" and not match.is_file():
                    continue
                if file_type == "dir" and not match.is_dir():
                    continue

                # Security check
                if not self._sandbox.is_path_allowed(match):
                    continue

                results.append(str(match.relative_to(validated_path)))

                if len(results) >= max_results:
                    break

            if not results:
                return f"No files found matching pattern: {pattern}"

            output = "\n".join(results)
            if len(results) >= max_results:
                output += f"\n\n(Showing first {max_results} results)"

            return output

        except Exception as e:
            return f"Error: Failed to search: {e}"


# Convenience instances for direct use
directory_list = DirectoryListTool()
directory_tree = DirectoryTreeTool()
directory_create = DirectoryCreateTool()
file_search = FileSearchTool()
