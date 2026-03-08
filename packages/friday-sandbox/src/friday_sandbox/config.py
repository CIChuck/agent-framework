# mypy: ignore-errors
"""
Configuration models for sandbox and workspace management.

Ref: docs/specs/sandbox_specifications.md - Section 4: Configuration

Configuration follows a layered approach:
1. Package defaults (defined here)
2. Environment variables (FRIDAY_SANDBOX_*)
3. Agent profile settings
4. Per-execution overrides
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class WorkspaceConfig(BaseModel):
    """
    Configuration for workspace lifecycle management.

    Controls TTL, cleanup behavior, and resource limits for workspaces.
    """

    # TTL Configuration
    ttl_seconds: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Default workspace TTL in seconds (1 hour default)",
    )
    ttl_soft_limit_seconds: int = Field(
        default=3600,
        ge=60,
        description="Soft limit before warning (1 hour)",
    )
    ttl_hard_limit_seconds: int = Field(
        default=86400,
        ge=3600,
        description="Hard limit - force cleanup (24 hours)",
    )

    # Cleanup Configuration
    cleanup_interval_seconds: int = Field(
        default=300,
        ge=60,
        description="Interval between cleanup sweeps (5 minutes)",
    )
    preserve_on_error: bool = Field(
        default=True,
        description="Preserve workspace if execution fails (for debugging)",
    )

    # Resource Limits
    max_workspace_size_mb: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Maximum workspace size in MB",
    )
    max_files_per_workspace: int = Field(
        default=1000,
        ge=10,
        description="Maximum number of files in workspace",
    )

    @classmethod
    def from_environment(cls) -> WorkspaceConfig:
        """Create config from environment variables."""
        return cls(
            ttl_seconds=int(os.getenv("FRIDAY_SANDBOX_WORKSPACE_TTL", "3600")),
            ttl_soft_limit_seconds=int(
                os.getenv("FRIDAY_SANDBOX_WORKSPACE_TTL_SOFT", "3600")
            ),
            ttl_hard_limit_seconds=int(
                os.getenv("FRIDAY_SANDBOX_WORKSPACE_TTL_HARD", "86400")
            ),
            cleanup_interval_seconds=int(
                os.getenv("FRIDAY_SANDBOX_CLEANUP_INTERVAL", "300")
            ),
            preserve_on_error=os.getenv(
                "FRIDAY_SANDBOX_PRESERVE_ON_ERROR", "true"
            ).lower()
            == "true",
            max_workspace_size_mb=int(
                os.getenv("FRIDAY_SANDBOX_MAX_WORKSPACE_SIZE_MB", "100")
            ),
            max_files_per_workspace=int(os.getenv("FRIDAY_SANDBOX_MAX_FILES", "1000")),
        )


class DockerConfig(BaseModel):
    """
    Configuration for Docker sandbox execution.

    Controls container resources, networking, and security settings.
    """

    # Image Configuration
    image: str = Field(
        default="friday-sandbox-python:latest",
        description="Docker image to use for execution",
    )
    pull_policy: str = Field(
        default="if-not-present",
        description="Image pull policy: always, if-not-present, never",
    )

    # Resource Limits
    memory_limit: str = Field(
        default="512m",
        description="Container memory limit",
    )
    cpu_limit: float = Field(
        default=1.0,
        ge=0.1,
        le=4.0,
        description="CPU core limit",
    )

    # Execution Limits
    default_timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Default execution timeout",
    )
    max_timeout_seconds: int = Field(
        default=300,
        ge=30,
        le=600,
        description="Maximum allowed timeout",
    )

    # Security
    network_enabled: bool = Field(
        default=False,
        description="Enable network access in container",
    )
    read_only_rootfs: bool = Field(
        default=True,
        description="Mount root filesystem as read-only",
    )
    user: str = Field(
        default="sandbox:sandbox",
        description="User:group to run as in container",
    )

    # Paths
    workspace_base_path: Path = Field(
        default=Path("/tmp/friday-workspaces"),
        description="Base path for workspace directories",
    )

    @field_validator("pull_policy")
    @classmethod
    def validate_pull_policy(cls, v: str) -> str:
        valid = {"always", "if-not-present", "never"}
        if v not in valid:
            raise ValueError(f"pull_policy must be one of: {valid}")
        return v

    @classmethod
    def from_environment(cls) -> DockerConfig:
        """Create config from environment variables."""
        return cls(
            image=os.getenv("FRIDAY_SANDBOX_IMAGE", "friday-sandbox-python:latest"),
            pull_policy=os.getenv("FRIDAY_SANDBOX_PULL_POLICY", "if-not-present"),
            memory_limit=os.getenv("FRIDAY_SANDBOX_MEMORY_LIMIT", "512m"),
            cpu_limit=float(os.getenv("FRIDAY_SANDBOX_CPU_LIMIT", "1.0")),
            default_timeout_seconds=int(
                os.getenv("FRIDAY_SANDBOX_DEFAULT_TIMEOUT", "30")
            ),
            max_timeout_seconds=int(os.getenv("FRIDAY_SANDBOX_MAX_TIMEOUT", "300")),
            network_enabled=os.getenv("FRIDAY_SANDBOX_NETWORK_ENABLED", "false").lower()
            == "true",
            read_only_rootfs=os.getenv(
                "FRIDAY_SANDBOX_READ_ONLY_ROOTFS", "true"
            ).lower()
            == "true",
            workspace_base_path=Path(
                os.getenv("FRIDAY_SANDBOX_WORKSPACE_PATH", "/tmp/friday-workspaces")
            ),
        )


class SandboxConfig(BaseModel):
    """
    Top-level sandbox configuration combining all settings.
    """

    workspace: WorkspaceConfig = Field(default_factory=WorkspaceConfig)
    docker: DockerConfig = Field(default_factory=DockerConfig)

    # Sandbox Selection
    sandbox_type: str = Field(
        default="docker",
        description="Sandbox type: docker, subprocess, mock",
    )
    fallback_to_subprocess: bool = Field(
        default=True,
        description="Fall back to subprocess if Docker unavailable",
    )

    @field_validator("sandbox_type")
    @classmethod
    def validate_sandbox_type(cls, v: str) -> str:
        valid = {"docker", "subprocess", "mock"}
        if v not in valid:
            raise ValueError(f"sandbox_type must be one of: {valid}")
        return v

    @classmethod
    def from_environment(cls) -> SandboxConfig:
        """Create complete config from environment variables."""
        return cls(
            workspace=WorkspaceConfig.from_environment(),
            docker=DockerConfig.from_environment(),
            sandbox_type=os.getenv("FRIDAY_SANDBOX_TYPE", "docker"),
            fallback_to_subprocess=os.getenv(
                "FRIDAY_SANDBOX_FALLBACK_SUBPROCESS", "true"
            ).lower()
            == "true",
        )

    def merge_overrides(self, overrides: dict[str, Any]) -> SandboxConfig:
        """
        Create a new config with overrides applied.

        Args:
            overrides: Dictionary of override values.

        Returns:
            New SandboxConfig with overrides merged.
        """
        data = self.model_dump()
        for key, value in overrides.items():
            if "." in key:
                # Handle nested keys like "workspace.ttl_seconds"
                parts = key.split(".")
                current = data
                for part in parts[:-1]:
                    current = current.setdefault(part, {})
                current[parts[-1]] = value
            else:
                data[key] = value
        return SandboxConfig.model_validate(data)
