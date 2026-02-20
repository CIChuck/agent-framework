"""
Git branch tools.

Ref: docs/specs/tool_specification.md - Category 10: Git Operations - Branches
"""

from __future__ import annotations

from typing import Any

import git

from ..definition import BaseTool
from ..sandbox import FilesystemSandbox


class GitBranchListTool(BaseTool):
    """List git branches."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "git_branch_list"

    @property
    def description(self) -> str:
        return "List all branches in the repository."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "all": {
                    "type": "boolean",
                    "description": "Include remote branches",
                    "default": False,
                },
            },
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs.get("path", ".")
        show_all = kwargs.get("all", False)

        validated = self._sandbox.validate_path(path)

        try:
            repo = git.Repo(validated, search_parent_directories=True)
            args = ["-a"] if show_all else []
            return repo.git.branch(*args)
        except git.InvalidGitRepositoryError:
            return f"Error: Not a git repository: {path}"
        except Exception as e:
            return f"Error: {e}"


class GitBranchCreateTool(BaseTool):
    """Create a new branch."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "git_branch_create"

    @property
    def description(self) -> str:
        return "Create a new branch."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "name": {"type": "string", "description": "Branch name"},
                "start_point": {
                    "type": "string",
                    "description": "Start from this commit/branch",
                },
            },
            "required": ["name"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs.get("path", ".")
        name = kwargs["name"]
        start_point = kwargs.get("start_point")

        validated = self._sandbox.validate_path(path)

        try:
            repo = git.Repo(validated, search_parent_directories=True)
            args = [name]
            if start_point:
                args.append(start_point)
            repo.git.branch(*args)
            return f"Created branch: {name}"
        except git.InvalidGitRepositoryError:
            return f"Error: Not a git repository: {path}"
        except Exception as e:
            return f"Error: {e}"


class GitCheckoutTool(BaseTool):
    """Switch branches or restore files."""

    def __init__(self, sandbox: FilesystemSandbox | None = None):
        self._sandbox = sandbox or FilesystemSandbox()

    @property
    def name(self) -> str:
        return "git_checkout"

    @property
    def description(self) -> str:
        return "Switch branches or restore working tree files."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "."},
                "target": {
                    "type": "string",
                    "description": "Branch, tag, or commit to checkout",
                },
                "create": {
                    "type": "boolean",
                    "description": "Create branch if it doesn't exist",
                    "default": False,
                },
            },
            "required": ["target"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = kwargs.get("path", ".")
        target = kwargs["target"]
        create = kwargs.get("create", False)

        validated = self._sandbox.validate_path(path)

        try:
            repo = git.Repo(validated, search_parent_directories=True)
            args = []
            if create:
                args.append("-b")
            args.append(target)
            repo.git.checkout(*args)
            return f"Switched to: {target}"
        except git.InvalidGitRepositoryError:
            return f"Error: Not a git repository: {path}"
        except Exception as e:
            return f"Error: {e}"


git_branch_list = GitBranchListTool()
git_branch_create = GitBranchCreateTool()
git_checkout = GitCheckoutTool()
