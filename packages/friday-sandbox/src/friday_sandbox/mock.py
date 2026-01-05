"""
Mock sandbox implementation for testing.

Ref: docs/specs/sandbox_specifications.md - Section 8: Alternative Implementations

Provides a configurable mock sandbox that returns predefined results
without actually executing any code. Useful for unit testing tools
that depend on sandbox execution.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .config import SandboxConfig, WorkspaceConfig
from .models import ExecutionResult, Workspace, WorkspaceNotFoundError


class MockSandbox:
    """
    Mock sandbox for testing purposes.

    Allows configuring predetermined responses for execute() calls,
    enabling unit tests for code that depends on sandbox execution
    without actually running any code.

    Example:
        ```python
        sandbox = MockSandbox()
        sandbox.set_response(
            ExecutionResult(stdout="Hello, World!", exit_code=0)
        )

        result = await sandbox.execute("print('Hello, World!')")
        assert result.stdout == "Hello, World!"
        ```
    """

    def __init__(self, config: SandboxConfig | None = None):
        """
        Initialize mock sandbox.

        Args:
            config: Optional configuration (mostly ignored in mock).
        """
        self.config = config or SandboxConfig()
        self._workspaces: dict[str, Workspace] = {}
        self._default_response = ExecutionResult(
            stdout="",
            stderr="",
            exit_code=0,
            execution_time_ms=1.0,
        )
        self._response_queue: list[ExecutionResult] = []
        self._response_callback: Callable[[str], ExecutionResult] | None = None
        self._execution_history: list[dict[str, Any]] = []

    def set_response(self, response: ExecutionResult) -> None:
        """
        Set the default response for all execute() calls.

        Args:
            response: ExecutionResult to return.
        """
        self._default_response = response

    def queue_response(self, response: ExecutionResult) -> None:
        """
        Queue a response to be returned for the next execute() call.

        Queued responses are consumed in FIFO order. When the queue
        is empty, the default response is used.

        Args:
            response: ExecutionResult to queue.
        """
        self._response_queue.append(response)

    def set_response_callback(
        self,
        callback: Callable[[str], ExecutionResult],
    ) -> None:
        """
        Set a callback to generate responses based on input code.

        The callback receives the code string and returns an ExecutionResult.
        This allows dynamic responses based on the code being "executed".

        Args:
            callback: Function (code: str) -> ExecutionResult
        """
        self._response_callback = callback

    def get_execution_history(self) -> list[dict[str, Any]]:
        """
        Get the history of all execute() calls.

        Returns:
            List of dicts with keys: code, language, timeout_seconds,
            workspace_id, environment, return_type
        """
        return self._execution_history.copy()

    def clear_history(self) -> None:
        """Clear the execution history."""
        self._execution_history.clear()

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
        Mock execute that returns configured responses.

        Args:
            code: Code string (not actually executed).
            language: Language (logged but not used).
            timeout_seconds: Timeout (logged but not used).
            workspace_id: Workspace ID (logged but not used).
            environment: Environment vars (logged but not used).
            return_type: Return type (logged but not used).

        Returns:
            Configured ExecutionResult.
        """
        # Record the call
        self._execution_history.append({
            "code": code,
            "language": language,
            "timeout_seconds": timeout_seconds,
            "workspace_id": workspace_id,
            "environment": environment,
            "return_type": return_type,
        })

        # Return response based on priority:
        # 1. Response callback
        # 2. Queued responses
        # 3. Default response

        if self._response_callback is not None:
            return self._response_callback(code)

        if self._response_queue:
            return self._response_queue.pop(0)

        return self._default_response

    async def create_workspace(
        self,
        config: WorkspaceConfig | None = None,
        agent_id: str | None = None,
    ) -> Workspace:
        """Create a mock workspace."""
        workspace_id = str(uuid.uuid4())
        workspace = Workspace(
            id=workspace_id,
            path=Path(f"/mock/workspaces/{workspace_id}"),
            agent_id=agent_id,
            ttl_seconds=config.ttl_seconds if config else 3600,
        )
        self._workspaces[workspace_id] = workspace
        return workspace

    async def get_workspace(self, workspace_id: str) -> Workspace | None:
        """Get a mock workspace by ID."""
        return self._workspaces.get(workspace_id)

    async def cleanup_workspace(
        self,
        workspace_id: str,
        force: bool = False,
    ) -> bool:
        """Clean up a mock workspace."""
        if workspace_id in self._workspaces:
            workspace = self._workspaces[workspace_id]
            if workspace.preserve and not force:
                return False
            del self._workspaces[workspace_id]
            return True
        return False

    async def cleanup_expired_workspaces(self) -> int:
        """Clean up expired mock workspaces."""
        now = datetime.utcnow()
        expired = [
            wid
            for wid, w in self._workspaces.items()
            if w.is_expired
        ]
        for wid in expired:
            del self._workspaces[wid]
        return len(expired)

    async def __aenter__(self) -> MockSandbox:
        """Async context manager entry (no-op for mock)."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit (no-op for mock)."""
        pass


class MockSandboxBuilder:
    """
    Builder for creating configured MockSandbox instances.

    Example:
        ```python
        sandbox = (
            MockSandboxBuilder()
            .with_success_response("output", return_value={"key": "value"})
            .with_error_response("error message", exit_code=1)
            .build()
        )
        ```
    """

    def __init__(self):
        self._sandbox = MockSandbox()

    def with_response(self, response: ExecutionResult) -> MockSandboxBuilder:
        """Queue a response."""
        self._sandbox.queue_response(response)
        return self

    def with_success_response(
        self,
        stdout: str = "",
        return_value: Any = None,
        files_created: list[str] | None = None,
    ) -> MockSandboxBuilder:
        """Queue a successful execution response."""
        self._sandbox.queue_response(
            ExecutionResult(
                stdout=stdout,
                stderr="",
                exit_code=0,
                return_value=return_value,
                files_created=files_created or [],
            )
        )
        return self

    def with_error_response(
        self,
        error_message: str,
        exit_code: int = 1,
        stderr: str = "",
    ) -> MockSandboxBuilder:
        """Queue an error execution response."""
        self._sandbox.queue_response(
            ExecutionResult(
                stdout="",
                stderr=stderr or error_message,
                exit_code=exit_code,
                error=error_message,
            )
        )
        return self

    def with_timeout_response(
        self,
        timeout_seconds: int = 30,
    ) -> MockSandboxBuilder:
        """Queue a timeout response."""
        self._sandbox.queue_response(
            ExecutionResult(
                stdout="",
                stderr="",
                exit_code=-1,
                timed_out=True,
                error=f"Execution timed out after {timeout_seconds} seconds",
            )
        )
        return self

    def with_callback(
        self,
        callback: Callable[[str], ExecutionResult],
    ) -> MockSandboxBuilder:
        """Set a response callback."""
        self._sandbox.set_response_callback(callback)
        return self

    def build(self) -> MockSandbox:
        """Build and return the configured MockSandbox."""
        return self._sandbox
