"""
Filesystem writing tools.

Ref: docs/specs/tool_specification.md - Category 2: Filesystem - Writing
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class FileWriteTool(BaseTool):
    """Write content to a file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_write"

    @property
    def description(self) -> str:
        return "Write content to a file, creating it if it doesn't exist or overwriting if it does."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding (default: utf-8)",
                    "default": "utf-8",
                },
                "create_dirs": {
                    "type": "boolean",
                    "description": "Create parent directories if they don't exist",
                    "default": True,
                },
            },
            "required": ["path", "content"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        content = kwargs["content"]
        encoding = kwargs.get("encoding", "utf-8")
        create_dirs = kwargs.get("create_dirs", True)

        validated_path = self._sandbox.validate_path(path)

        try:
            if create_dirs:
                validated_path.parent.mkdir(parents=True, exist_ok=True)

            validated_path.write_text(content, encoding=encoding)
            return f"Successfully wrote {len(content)} bytes to {path}"

        except Exception as e:
            return f"Error: Failed to write file: {e}"


class FileAppendTool(BaseTool):
    """Append content to a file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_append"

    @property
    def description(self) -> str:
        return "Append content to the end of a file."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file",
                },
                "content": {
                    "type": "string",
                    "description": "Content to append",
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding (default: utf-8)",
                    "default": "utf-8",
                },
            },
            "required": ["path", "content"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        content = kwargs["content"]
        encoding = kwargs.get("encoding", "utf-8")

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: File not found: {path}"

        try:
            with validated_path.open("a", encoding=encoding) as f:
                f.write(content)
            return f"Successfully appended {len(content)} bytes to {path}"

        except Exception as e:
            return f"Error: Failed to append to file: {e}"


class FileInsertTool(BaseTool):
    """Insert content at a specific line."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_insert"

    @property
    def description(self) -> str:
        return "Insert content at a specific line number in a file."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file",
                },
                "line_number": {
                    "type": "integer",
                    "description": "Line number to insert at (1-indexed, content inserted before this line)",
                    "minimum": 1,
                },
                "content": {
                    "type": "string",
                    "description": "Content to insert",
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding (default: utf-8)",
                    "default": "utf-8",
                },
            },
            "required": ["path", "line_number", "content"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        line_number = kwargs["line_number"]
        content = kwargs["content"]
        encoding = kwargs.get("encoding", "utf-8")

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: File not found: {path}"

        try:
            with validated_path.open(encoding=encoding) as f:
                lines = f.readlines()

            # Insert at the specified position
            insert_idx = min(line_number - 1, len(lines))

            # Ensure content ends with newline if inserting in middle
            if not content.endswith("\n") and insert_idx < len(lines):
                content += "\n"

            lines.insert(insert_idx, content)

            with validated_path.open("w", encoding=encoding) as f:
                f.writelines(lines)

            return f"Successfully inserted content at line {line_number}"

        except Exception as e:
            return f"Error: Failed to insert into file: {e}"


class FileReplaceTool(BaseTool):
    """Find and replace in a file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_replace"

    @property
    def description(self) -> str:
        return "Find and replace text in a file using a pattern."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file",
                },
                "pattern": {
                    "type": "string",
                    "description": "Pattern to search for (regex or literal)",
                },
                "replacement": {
                    "type": "string",
                    "description": "Replacement text",
                },
                "regex": {
                    "type": "boolean",
                    "description": "Treat pattern as regex (default: false)",
                    "default": False,
                },
                "count": {
                    "type": "integer",
                    "description": "Maximum replacements (0 = all)",
                    "default": 0,
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding (default: utf-8)",
                    "default": "utf-8",
                },
            },
            "required": ["path", "pattern", "replacement"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        pattern = kwargs["pattern"]
        replacement = kwargs["replacement"]
        use_regex = kwargs.get("regex", False)
        count = kwargs.get("count", 0)
        encoding = kwargs.get("encoding", "utf-8")

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: File not found: {path}"

        try:
            content = validated_path.read_text(encoding=encoding)

            if use_regex:
                if count > 0:
                    new_content = re.sub(pattern, replacement, content, count=count)
                else:
                    new_content = re.sub(pattern, replacement, content)
            else:
                if count > 0:
                    new_content = content.replace(pattern, replacement, count)
                else:
                    new_content = content.replace(pattern, replacement)

            # Count replacements
            if use_regex:
                num_replacements = len(re.findall(pattern, content))
                if count > 0:
                    num_replacements = min(num_replacements, count)
            else:
                num_replacements = content.count(pattern)
                if count > 0:
                    num_replacements = min(num_replacements, count)

            validated_path.write_text(new_content, encoding=encoding)
            return f"Made {num_replacements} replacement(s) in {path}"

        except re.error as e:
            return f"Error: Invalid regex pattern: {e}"
        except Exception as e:
            return f"Error: Failed to replace in file: {e}"


class FilePatchTool(BaseTool):
    """Apply a diff/patch to a file."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_patch"

    @property
    def description(self) -> str:
        return "Apply a unified diff patch to a file."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to patch",
                },
                "patch": {
                    "type": "string",
                    "description": "Unified diff patch content",
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding (default: utf-8)",
                    "default": "utf-8",
                },
            },
            "required": ["path", "patch"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        patch_content = kwargs["patch"]
        encoding = kwargs.get("encoding", "utf-8")

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: File not found: {path}"

        try:
            # Simple patch application - parse unified diff
            lines = validated_path.read_text(encoding=encoding).splitlines(keepends=True)
            new_lines = self._apply_patch(lines, patch_content)

            validated_path.write_text("".join(new_lines), encoding=encoding)
            return f"Successfully applied patch to {path}"

        except Exception as e:
            return f"Error: Failed to apply patch: {e}"

    def _apply_patch(self, lines: list[str], patch: str) -> list[str]:
        """Apply a simple unified diff patch."""
        result = list(lines)
        patch_lines = patch.splitlines()

        i = 0
        while i < len(patch_lines):
            line = patch_lines[i]

            # Find hunk header
            if line.startswith("@@"):
                # Parse hunk header: @@ -start,count +start,count @@
                match = re.match(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
                if match:
                    old_start = int(match.group(1)) - 1
                    new_start = int(match.group(2)) - 1

                    i += 1
                    offset = 0

                    while i < len(patch_lines) and not patch_lines[i].startswith("@@"):
                        pline = patch_lines[i]
                        if pline.startswith("-"):
                            # Remove line
                            if old_start + offset < len(result):
                                result.pop(old_start + offset)
                        elif pline.startswith("+"):
                            # Add line
                            content = pline[1:] + "\n"
                            result.insert(old_start + offset, content)
                            offset += 1
                        else:
                            # Context line
                            offset += 1
                        i += 1
                    continue

            i += 1

        return result


# Convenience instances for direct use
file_write = FileWriteTool()
file_append = FileAppendTool()
file_insert = FileInsertTool()
file_replace = FileReplaceTool()
file_patch = FilePatchTool()
