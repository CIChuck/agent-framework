# mypy: ignore-errors
"""
Subprocess-based sandbox implementation.

Ref: docs/reference/specs/sandbox_specifications.md - Section 8: Alternative
Implementations

Provides local subprocess execution as a fallback when Docker is unavailable.
WARNING: This is less secure than Docker - use only for development/testing.
"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from .config import SandboxConfig, WorkspaceConfig
from .models import (
    ExecutionResult,
    SandboxExecutionError,
    SandboxTimeoutError,
    Workspace,
)
from .serialization import (
    extract_return_value,
    validate_return_type,
    wrap_code_for_return_capture,
)
from .workspace import WorkspaceManager

logger = logging.getLogger(__name__)


class SubprocessSandbox:
    """
    Subprocess-based sandbox for local code execution.

    Uses Python subprocess to execute code locally. This provides basic
    isolation but is NOT as secure as Docker containers.

    Use cases:
    - Development and testing
    - Fallback when Docker is unavailable
    - Environments where Docker cannot run
    """

    def __init__(
        self,
        config: SandboxConfig | None = None,
    ):
        """
        Initialize subprocess sandbox.

        Args:
            config: Sandbox configuration. If None, loads from environment.
        """
        self.config = config or SandboxConfig.from_environment()
        self._workspace_manager = WorkspaceManager(
            config=self.config.workspace,
            base_path=Path(tempfile.gettempdir()) / "friday-workspaces",
        )

    async def execute(
        self,
        code: str,
        *,
        language: str = "python",
        timeout_seconds: int | None = None,
        workspace_id: str | None = None,
        environment: dict[str, str] | None = None,
        return_type: type[Any] | None = None,
    ) -> ExecutionResult:
        """
        Execute code in a subprocess.

        Args:
            code: Python source code to execute.
            language: Programming language (only "python" supported).
            timeout_seconds: Execution timeout.
            workspace_id: Optional workspace for file persistence.
            environment: Environment variables for the subprocess.
            return_type: Optional Pydantic model for return value validation.

        Returns:
            ExecutionResult with stdout, stderr, return_value, etc.

        Raises:
            SandboxTimeoutError: If execution exceeds timeout.
            ValueError: If language is not supported.
        """
        if language != "python":
            raise ValueError(
                f"Unsupported language: {language}. Only 'python' is supported."
            )

        # Resolve timeout
        timeout = timeout_seconds or self.config.docker.default_timeout_seconds
        timeout = min(timeout, self.config.docker.max_timeout_seconds)

        # Get or create workspace
        workspace = None
        cwd = None
        if workspace_id:
            workspace = await self._workspace_manager.get(workspace_id)
            await self._workspace_manager.record_execution(workspace_id)
            cwd = str(workspace.path)

        # Wrap code for return value capture
        wrapped_code = wrap_code_for_return_capture(code)

        # Prepare environment
        env = os.environ.copy()
        if environment:
            env.update(environment)

        # Execute in subprocess
        start_time = time.time()

        try:
            loop = asyncio.get_event_loop()
            process = await loop.run_in_executor(
                None,
                lambda: subprocess.Popen(
                    ["python", "-c", wrapped_code],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cwd,
                    env=env,
                ),
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: process.communicate(),
                    ),
                    timeout=timeout,
                )
            except TimeoutError:
                process.kill()
                process.wait()
                raise SandboxTimeoutError(timeout)  # noqa: B904

        except SandboxTimeoutError:
            raise
        except Exception as e:
            raise SandboxExecutionError(f"Failed to execute code: {e}")  # noqa: B904

        execution_time_ms = (time.time() - start_time) * 1000

        # Decode output
        stdout_str = stdout.decode("utf-8", errors="replace")
        stderr_str = stderr.decode("utf-8", errors="replace")

        # Parse return value from stdout
        cleaned_stdout, return_value, raw_json = extract_return_value(stdout_str)

        # Validate return type if specified
        error = None
        if return_type is not None and return_value is not None:
            try:
                return_value = validate_return_type(return_value, return_type)
            except Exception as e:
                logger.warning(f"Return type validation failed: {e}")
                error = f"Return type validation failed: {e}"

        # List created files if workspace was used
        files_created = []
        if workspace:
            files_created = await self._workspace_manager.get_workspace_files(
                workspace_id
            )

        return ExecutionResult(
            stdout=cleaned_stdout,
            stderr=stderr_str,
            exit_code=process.returncode,
            execution_time_ms=execution_time_ms,
            return_value=return_value,
            return_value_raw=raw_json,
            files_created=files_created,
            timed_out=False,
            error=error,
        )

    async def create_workspace(
        self,
        config: WorkspaceConfig | None = None,
        agent_id: str | None = None,
    ) -> Workspace:
        """Create a new workspace for persistent file storage."""
        ttl = None
        if config:
            ttl = config.ttl_seconds

        return await self._workspace_manager.create(
            agent_id=agent_id,
            ttl_seconds=ttl,
        )

    async def get_workspace(self, workspace_id: str) -> Workspace | None:
        """Get an existing workspace by ID."""
        try:
            return await self._workspace_manager.get(workspace_id)
        except Exception:
            return None

    async def cleanup_workspace(
        self,
        workspace_id: str,
        force: bool = False,
    ) -> bool:
        """Clean up a workspace."""
        return await self._workspace_manager.cleanup(workspace_id, force=force)

    async def cleanup_expired_workspaces(self) -> int:
        """Clean up all expired workspaces."""
        return await self._workspace_manager.cleanup_expired()

    async def __aenter__(self) -> SubprocessSandbox:
        """Async context manager entry."""
        await self._workspace_manager.start_cleanup_loop()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self._workspace_manager.stop_cleanup_loop()
