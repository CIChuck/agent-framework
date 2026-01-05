"""
Sandbox protocols defining abstract interfaces for code execution.

Ref: docs/specs/sandbox_specifications.md - Section 2: SandboxProtocol
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .config import WorkspaceConfig
    from .models import ExecutionResult, Workspace


@runtime_checkable
class SandboxProtocol(Protocol):
    """
    Abstract interface for code execution sandboxes.

    Implementations include:
    - DockerSandbox: Full isolation via Docker containers
    - SubprocessSandbox: Local subprocess execution (development/fallback)
    - MockSandbox: Testing implementation with configurable responses
    """

    async def execute(
        self,
        code: str,
        *,
        language: str = "python",
        timeout_seconds: int = 30,
        workspace_id: str | None = None,
        environment: dict[str, str] | None = None,
        return_type: type[Any] | None = None,
    ) -> ExecutionResult:
        """
        Execute code in the sandbox.

        Args:
            code: Source code to execute.
            language: Programming language (currently only "python" supported).
            timeout_seconds: Maximum execution time before termination.
            workspace_id: Optional workspace ID for persistent file access.
            environment: Environment variables to set in the sandbox.
            return_type: Optional Pydantic model type for structured return
                        value validation.

        Returns:
            ExecutionResult with stdout, stderr, return_value, exit_code,
            execution_time, and files_created.

        Raises:
            SandboxTimeoutError: If execution exceeds timeout_seconds.
            SandboxExecutionError: If sandbox execution fails.
        """
        ...

    async def create_workspace(
        self,
        config: WorkspaceConfig | None = None,
        agent_id: str | None = None,
    ) -> Workspace:
        """
        Create a new workspace for persistent file storage across executions.

        Args:
            config: Optional configuration overriding defaults.
            agent_id: Optional agent identifier for workspace association.

        Returns:
            Workspace instance with unique ID and path.
        """
        ...

    async def get_workspace(self, workspace_id: str) -> Workspace | None:
        """
        Retrieve an existing workspace by ID.

        Args:
            workspace_id: The workspace identifier.

        Returns:
            Workspace if found, None otherwise.
        """
        ...

    async def cleanup_workspace(
        self,
        workspace_id: str,
        force: bool = False,
    ) -> bool:
        """
        Clean up a workspace and its resources.

        Args:
            workspace_id: The workspace identifier.
            force: If True, cleanup even if preserve=True.

        Returns:
            True if cleanup succeeded, False otherwise.
        """
        ...

    async def cleanup_expired_workspaces(self) -> int:
        """
        Clean up all workspaces that have exceeded their TTL.

        Returns:
            Number of workspaces cleaned up.
        """
        ...
