"""Pytest configuration and fixtures for friday-sandbox tests."""

import tempfile
from pathlib import Path

import pytest

from friday_sandbox import SandboxConfig, WorkspaceConfig, WorkspaceManager
from friday_sandbox.mock import MockSandbox


@pytest.fixture
def temp_workspace_path(tmp_path):
    """Create a temporary path for workspaces."""
    workspace_dir = tmp_path / "workspaces"
    workspace_dir.mkdir()
    return workspace_dir


@pytest.fixture
def workspace_config():
    """Create a test workspace configuration with short TTL."""
    return WorkspaceConfig(
        ttl_seconds=60,
        ttl_soft_limit_seconds=60,
        ttl_hard_limit_seconds=3600,
        cleanup_interval_seconds=60,
    )


@pytest.fixture
def sandbox_config(workspace_config):
    """Create a test sandbox configuration."""
    return SandboxConfig(
        workspace=workspace_config,
        sandbox_type="mock",
    )


@pytest.fixture
async def workspace_manager(temp_workspace_path, workspace_config):
    """Create a workspace manager for testing."""
    manager = WorkspaceManager(
        config=workspace_config,
        base_path=temp_workspace_path,
    )
    yield manager
    # Cleanup
    await manager.cleanup_all(force=True)


@pytest.fixture
def mock_sandbox(sandbox_config):
    """Create a mock sandbox for testing."""
    return MockSandbox(config=sandbox_config)
