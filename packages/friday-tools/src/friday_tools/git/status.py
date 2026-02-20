"""
Git status tools.

Ref: docs/specs/tool_specification.md - Category 10: Git Operations - Status
"""

from __future__ import annotations

from typing import Any

import git

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class GitStatusTool(BaseTool):
    """Get git repository status."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "git_status"

    @property
    def description(self) -> str:
        return "Show the working tree status of a git repository."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Repository path",
                    "default": ".",
                },
            },
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs.get("path", ".")
        validated = self._sandbox.validate_path(path)

        try:
            repo = git.Repo(validated, search_parent_directories=True)
            return repo.git.status()
        except git.InvalidGitRepositoryError:
            return f"Error: Not a git repository: {path}"
        except Exception as e:
            return f"Error: {e}"


class GitDiffTool(BaseTool):
    """Show git diff."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "git_diff"

    @property
    def description(self) -> str:
        return "Show changes between commits, commit and working tree, etc."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "staged": {
                    "type": "boolean",
                    "description": "Show staged changes",
                    "default": False,
                },
                "file": {"type": "string", "description": "Specific file to diff"},
            },
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs.get("path", ".")
        staged = kwargs.get("staged", False)
        file_path = kwargs.get("file")

        validated = self._sandbox.validate_path(path)

        try:
            repo = git.Repo(validated, search_parent_directories=True)
            args = []
            if staged:
                args.append("--staged")
            if file_path:
                args.append("--")
                args.append(file_path)
            return repo.git.diff(*args) or "(no changes)"
        except git.InvalidGitRepositoryError:
            return f"Error: Not a git repository: {path}"
        except Exception as e:
            return f"Error: {e}"


class GitLogTool(BaseTool):
    """Show git commit log."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "git_log"

    @property
    def description(self) -> str:
        return "Show commit logs."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "count": {
                    "type": "integer",
                    "description": "Number of commits",
                    "default": 10,
                },
                "oneline": {"type": "boolean", "default": True},
            },
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs.get("path", ".")
        count = kwargs.get("count", 10)
        oneline = kwargs.get("oneline", True)

        validated = self._sandbox.validate_path(path)

        try:
            repo = git.Repo(validated, search_parent_directories=True)
            args = [f"-n{count}"]
            if oneline:
                args.append("--oneline")
            return repo.git.log(*args)
        except git.InvalidGitRepositoryError:
            return f"Error: Not a git repository: {path}"
        except Exception as e:
            return f"Error: {e}"


class GitShowTool(BaseTool):
    """Show commit details."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "git_show"

    @property
    def description(self) -> str:
        return "Show details of a specific commit."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "commit": {
                    "type": "string",
                    "description": "Commit hash or ref",
                    "default": "HEAD",
                },
            },
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs.get("path", ".")
        commit = kwargs.get("commit", "HEAD")

        validated = self._sandbox.validate_path(path)

        try:
            repo = git.Repo(validated, search_parent_directories=True)
            return repo.git.show(commit, "--stat")
        except git.InvalidGitRepositoryError:
            return f"Error: Not a git repository: {path}"
        except Exception as e:
            return f"Error: {e}"


git_status = GitStatusTool()
git_diff = GitDiffTool()
git_log = GitLogTool()
git_show = GitShowTool()
