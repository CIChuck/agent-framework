# mypy: ignore-errors
"""
Friday Sandbox - Docker-based code execution for AI agents.

This package provides secure, isolated code execution environments
for AI agents to run dynamically generated code safely.

Ref: docs/specs/sandbox_specifications.md
"""

from .config import DockerConfig, SandboxConfig, WorkspaceConfig
from .models import (
    ExecutionResult,
    SandboxError,
    SandboxExecutionError,
    SandboxTimeoutError,
    Workspace,
    WorkspaceExpiredError,
    WorkspaceNotFoundError,
)
from .protocols import SandboxProtocol
from .workspace import WorkspaceManager


# Lazy imports for sandbox implementations to avoid import errors
# when Docker SDK is not installed
def get_docker_sandbox():
    """Get DockerSandbox class (requires docker SDK)."""
    from .docker import DockerSandbox

    return DockerSandbox


def get_subprocess_sandbox():
    """Get SubprocessSandbox class."""
    from .subprocess import SubprocessSandbox

    return SubprocessSandbox


def get_mock_sandbox():
    """Get MockSandbox class."""
    from .mock import MockSandbox

    return MockSandbox


def get_mock_sandbox_builder():
    """Get MockSandboxBuilder class."""
    from .mock import MockSandboxBuilder

    return MockSandboxBuilder


__all__ = [
    # Protocols
    "SandboxProtocol",
    # Models
    "ExecutionResult",
    "Workspace",
    # Errors
    "SandboxError",
    "SandboxTimeoutError",
    "SandboxExecutionError",
    "WorkspaceNotFoundError",
    "WorkspaceExpiredError",
    # Config
    "SandboxConfig",
    "WorkspaceConfig",
    "DockerConfig",
    # Manager
    "WorkspaceManager",
    # Sandbox implementations (lazy loaded)
    "get_docker_sandbox",
    "get_subprocess_sandbox",
    "get_mock_sandbox",
    "get_mock_sandbox_builder",
]

__version__ = "0.1.0"
