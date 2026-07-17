# mypy: ignore-errors
"""
Data models for sandbox execution.

Ref: docs/reference/specs/sandbox_specifications.md - Section 3: Data Models
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ExecutionResult(BaseModel):
    """
    Result of code execution in the sandbox.

    Contains all outputs from a sandbox execution including stdout, stderr,
    structured return values, and information about created files.
    """

    stdout: str = Field(default="", description="Standard output from execution")
    stderr: str = Field(default="", description="Standard error from execution")
    exit_code: int = Field(default=0, description="Process exit code")
    execution_time_ms: float = Field(
        default=0.0, description="Execution time in milliseconds"
    )
    return_value: Any = Field(
        default=None,
        description="Structured return value (if return_type was specified)",
    )
    return_value_raw: str | None = Field(
        default=None,
        description="Raw JSON string of return value before parsing",
    )
    files_created: list[str] = Field(
        default_factory=list,
        description="List of file paths created during execution",
    )
    timed_out: bool = Field(
        default=False, description="Whether execution was terminated due to timeout"
    )
    error: str | None = Field(
        default=None, description="Error message if execution failed"
    )

    @property
    def success(self) -> bool:
        """Check if execution completed successfully."""
        return self.exit_code == 0 and not self.timed_out and self.error is None


def _utc_now() -> datetime:
    """Return current UTC time with timezone awareness."""
    return datetime.now(timezone.utc)


def _ensure_utc(value: datetime) -> datetime:
    """Coerce naive datetimes to UTC and normalize aware values to UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class Workspace(BaseModel):
    """
    Represents a persistent workspace for sandbox file operations.

    Workspaces allow files to persist across multiple code executions,
    enabling multi-step workflows where code can read/write shared files.
    """

    id: str = Field(description="Unique workspace identifier (UUID)")
    path: Path = Field(description="Host filesystem path to workspace directory")
    agent_id: str | None = Field(
        default=None, description="Associated agent identifier"
    )
    created_at: datetime = Field(
        default_factory=_utc_now, description="Workspace creation timestamp"
    )
    last_accessed_at: datetime = Field(
        default_factory=_utc_now, description="Last access timestamp"
    )
    ttl_seconds: int = Field(
        default=3600, description="Time-to-live in seconds (default 1 hour)"
    )
    preserve: bool = Field(
        default=False,
        description="If True, workspace is not auto-cleaned by TTL",
    )
    execution_count: int = Field(
        default=0, description="Number of executions using this workspace"
    )

    model_config = {"arbitrary_types_allowed": True}

    @property
    def is_expired(self) -> bool:
        """Check if workspace has exceeded its TTL."""
        if self.preserve:
            return False
        elapsed = (_utc_now() - _ensure_utc(self.last_accessed_at)).total_seconds()
        return elapsed > self.ttl_seconds

    def touch(self) -> None:
        """Update last_accessed_at to current time."""
        self.last_accessed_at = _utc_now()

    def increment_execution(self) -> None:
        """Increment execution count and update access time."""
        self.execution_count += 1
        self.touch()


class SandboxError(Exception):
    """Base exception for sandbox errors."""

    pass


class SandboxTimeoutError(SandboxError):
    """Raised when code execution exceeds the timeout."""

    def __init__(self, timeout_seconds: int, message: str | None = None):
        self.timeout_seconds = timeout_seconds
        super().__init__(
            message or f"Execution timed out after {timeout_seconds} seconds"
        )


class SandboxExecutionError(SandboxError):
    """Raised when sandbox execution fails."""

    def __init__(self, message: str, exit_code: int | None = None):
        self.exit_code = exit_code
        super().__init__(message)


class WorkspaceNotFoundError(SandboxError):
    """Raised when a workspace cannot be found."""

    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        super().__init__(f"Workspace not found: {workspace_id}")


class WorkspaceExpiredError(SandboxError):
    """Raised when attempting to use an expired workspace."""

    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        super().__init__(f"Workspace has expired: {workspace_id}")
