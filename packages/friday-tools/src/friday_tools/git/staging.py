# mypy: ignore-errors
"""
Git staging tools.

Ref: docs/specs/tool_specification.md - Category 10: Git Operations - Staging
"""

from __future__ import annotations

from typing import Any

import git

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class GitAddTool(BaseTool):
    """Stage files for commit."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "git_add"

    @property
    def description(self) -> str:
        return "Add file contents to the staging area."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Files to add",
                },
                "all": {
                    "type": "boolean",
                    "description": "Add all changes",
                    "default": False,
                },
            },
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs.get("path", ".")
        files = kwargs.get("files", [])
        add_all = kwargs.get("all", False)

        validated = self._sandbox.validate_path(path)

        try:
            repo = git.Repo(validated, search_parent_directories=True)
            if add_all:
                repo.git.add("-A")
                return "Staged all changes"
            elif files:
                repo.git.add(*files)
                return f"Staged: {', '.join(files)}"
            else:
                return "Error: Specify files or use all=true"
        except git.InvalidGitRepositoryError:
            return f"Error: Not a git repository: {path}"
        except Exception as e:
            return f"Error: {e}"


class GitCommitTool(BaseTool):
    """Create a commit."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "git_commit"

    @property
    def description(self) -> str:
        return "Record changes to the repository."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "message": {"type": "string", "description": "Commit message"},
            },
            "required": ["message"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs.get("path", ".")
        message = kwargs["message"]

        validated = self._sandbox.validate_path(path)

        try:
            repo = git.Repo(validated, search_parent_directories=True)
            repo.git.commit("-m", message)
            return f"Created commit: {message[:50]}..."
        except git.InvalidGitRepositoryError:
            return f"Error: Not a git repository: {path}"
        except Exception as e:
            return f"Error: {e}"


class GitStashTool(BaseTool):
    """Stash changes."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "git_stash"

    @property
    def description(self) -> str:
        return "Stash the changes in a dirty working directory."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "action": {
                    "type": "string",
                    "enum": ["push", "pop", "list"],
                    "default": "push",
                },
                "message": {"type": "string", "description": "Stash message"},
            },
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs.get("path", ".")
        action = kwargs.get("action", "push")
        message = kwargs.get("message")

        validated = self._sandbox.validate_path(path)

        try:
            repo = git.Repo(validated, search_parent_directories=True)
            if action == "push":
                args = ["push"]
                if message:
                    args.extend(["-m", message])
                repo.git.stash(*args)
                return "Stashed changes"
            elif action == "pop":
                repo.git.stash("pop")
                return "Applied and removed top stash"
            elif action == "list":
                return repo.git.stash("list") or "(no stashes)"
            return f"Unknown action: {action}"
        except git.InvalidGitRepositoryError:
            return f"Error: Not a git repository: {path}"
        except Exception as e:
            return f"Error: {e}"


git_add = GitAddTool()
git_commit = GitCommitTool()
git_stash = GitStashTool()
