# mypy: ignore-errors
"""
Filesystem operation tools.

Ref: docs/reference/specs/tool_specification.md - Category 3: Filesystem - Operations
"""

from __future__ import annotations

import os
import shutil
from typing import Any

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class FileCopyTool(BaseTool):
    """Copy files or directories."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_copy"

    @property
    def description(self) -> str:
        return "Copy a file or directory to a new location."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Source path to copy",
                },
                "destination": {
                    "type": "string",
                    "description": "Destination path",
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Overwrite if destination exists",
                    "default": False,
                },
            },
            "required": ["source", "destination"],
        }

    async def execute(self, **kwargs: Any) -> str:
        source = kwargs["source"]
        destination = kwargs["destination"]
        overwrite = kwargs.get("overwrite", False)

        src_path = self._sandbox.validate_path(source)
        dst_path = self._sandbox.validate_path(destination)

        if not src_path.exists():
            return f"Error: Source not found: {source}"

        if dst_path.exists() and not overwrite:
            return f"Error: Destination already exists: {destination}"

        try:
            if src_path.is_dir():
                if dst_path.exists() and overwrite:
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                return f"Successfully copied directory {source} to {destination}"
            else:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
                return f"Successfully copied file {source} to {destination}"

        except Exception as e:
            return f"Error: Failed to copy: {e}"


class FileMoveTool(BaseTool):
    """Move or rename files or directories."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_move"

    @property
    def description(self) -> str:
        return "Move or rename a file or directory."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Source path",
                },
                "destination": {
                    "type": "string",
                    "description": "Destination path",
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Overwrite if destination exists",
                    "default": False,
                },
            },
            "required": ["source", "destination"],
        }

    async def execute(self, **kwargs: Any) -> str:
        source = kwargs["source"]
        destination = kwargs["destination"]
        overwrite = kwargs.get("overwrite", False)

        src_path = self._sandbox.validate_path(source)
        dst_path = self._sandbox.validate_path(destination)

        if not src_path.exists():
            return f"Error: Source not found: {source}"

        if dst_path.exists() and not overwrite:
            return f"Error: Destination already exists: {destination}"

        try:
            if dst_path.exists() and overwrite:
                if dst_path.is_dir():
                    shutil.rmtree(dst_path)
                else:
                    dst_path.unlink()

            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dst_path))
            return f"Successfully moved {source} to {destination}"

        except Exception as e:
            return f"Error: Failed to move: {e}"


class FileDeleteTool(BaseTool):
    """Delete files or directories."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_delete"

    @property
    def description(self) -> str:
        return "Delete a file or directory."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to delete",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Delete directories recursively",
                    "default": False,
                },
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        recursive = kwargs.get("recursive", False)

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: Path not found: {path}"

        try:
            if validated_path.is_dir():
                if recursive:
                    shutil.rmtree(validated_path)
                    return f"Successfully deleted directory {path} and its contents"
                else:
                    # Check if directory is empty
                    if any(validated_path.iterdir()):
                        return f"Error: Directory not empty. Use recursive=true to delete: {path}"  # noqa: E501
                    validated_path.rmdir()
                    return f"Successfully deleted empty directory {path}"
            else:
                validated_path.unlink()
                return f"Successfully deleted file {path}"

        except Exception as e:
            return f"Error: Failed to delete: {e}"


class FileChmodTool(BaseTool):
    """Change file permissions."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "file_chmod"

    @property
    def description(self) -> str:
        return "Change file or directory permissions using octal mode."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file or directory",
                },
                "mode": {
                    "type": "string",
                    "description": "Octal permission mode (e.g., '755', '644')",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Apply to directory contents recursively",
                    "default": False,
                },
            },
            "required": ["path", "mode"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs["path"]
        mode_str = kwargs["mode"]
        recursive = kwargs.get("recursive", False)

        validated_path = self._sandbox.validate_path(path)

        if not validated_path.exists():
            return f"Error: Path not found: {path}"

        try:
            # Parse octal mode
            mode = int(mode_str, 8)
        except ValueError:
            return f"Error: Invalid octal mode: {mode_str}"

        try:
            if recursive and validated_path.is_dir():
                count = 0
                for item in validated_path.rglob("*"):
                    os.chmod(item, mode)
                    count += 1
                os.chmod(validated_path, mode)
                return f"Successfully changed permissions to {mode_str} for {count + 1} items"  # noqa: E501
            else:
                os.chmod(validated_path, mode)
                return f"Successfully changed permissions of {path} to {mode_str}"

        except Exception as e:
            return f"Error: Failed to change permissions: {e}"


# Convenience instances for direct use
file_copy = FileCopyTool()
file_move = FileMoveTool()
file_delete = FileDeleteTool()
file_chmod = FileChmodTool()
