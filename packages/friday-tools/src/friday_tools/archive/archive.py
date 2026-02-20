"""Archive tools."""

from __future__ import annotations

import shutil
import tarfile
import zipfile
from typing import Any

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class ArchiveCreateTool(BaseTool):
    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "archive_create"

    @property
    def description(self) -> str:
        return "Create a zip or tar archive."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "source": {"type": "string"},
                "destination": {"type": "string"},
                "format": {
                    "type": "string",
                    "enum": ["zip", "tar", "tar.gz"],
                    "default": "zip",
                },
            },
            "required": ["source", "destination"],
        }

    async def execute(self, **kwargs: Any) -> str:
        src = self._sandbox.validate_path(kwargs["source"])
        dst = self._sandbox.validate_path(kwargs["destination"])
        fmt = kwargs.get("format", "zip")
        try:
            if fmt == "zip":
                shutil.make_archive(str(dst).replace(".zip", ""), "zip", src)
            elif fmt in ("tar", "tar.gz"):
                mode = "w:gz" if fmt == "tar.gz" else "w"
                with tarfile.open(dst, mode) as tar:
                    tar.add(src, arcname=src.name)
            return f"Created: {dst}"
        except Exception as e:
            return f"Error: {e}"


class ArchiveExtractTool(BaseTool):
    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "archive_extract"

    @property
    def description(self) -> str:
        return "Extract an archive."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "archive": {"type": "string"},
                "destination": {"type": "string"},
            },
            "required": ["archive", "destination"],
        }

    async def execute(self, **kwargs: Any) -> str:
        arc = self._sandbox.validate_path(kwargs["archive"])
        dst = self._sandbox.validate_path(kwargs["destination"])
        try:
            if str(arc).endswith(".zip"):
                with zipfile.ZipFile(arc) as zf:
                    zf.extractall(dst)
            else:
                with tarfile.open(arc) as tf:
                    tf.extractall(dst)
            return f"Extracted to: {dst}"
        except Exception as e:
            return f"Error: {e}"


class ArchiveListTool(BaseTool):
    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "archive_list"

    @property
    def description(self) -> str:
        return "List contents of an archive."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"archive": {"type": "string"}},
            "required": ["archive"],
        }

    async def execute(self, **kwargs: Any) -> str:
        arc = self._sandbox.validate_path(kwargs["archive"])
        try:
            if str(arc).endswith(".zip"):
                with zipfile.ZipFile(arc) as zf:
                    return "\n".join(zf.namelist())
            else:
                with tarfile.open(arc) as tf:
                    return "\n".join(tf.getnames())
        except Exception as e:
            return f"Error: {e}"


archive_create = ArchiveCreateTool()
archive_extract = ArchiveExtractTool()
archive_list = ArchiveListTool()
