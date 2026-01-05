"""Tests for workspace management."""

import asyncio
from datetime import datetime, timedelta

import pytest

from friday_sandbox import Workspace, WorkspaceExpiredError, WorkspaceNotFoundError
from friday_sandbox.workspace import WorkspaceManager


class TestWorkspaceManager:
    """Test suite for WorkspaceManager."""

    async def test_create_workspace(self, workspace_manager):
        """Test workspace creation."""
        workspace = await workspace_manager.create(agent_id="test-agent")

        assert workspace.id is not None
        assert workspace.agent_id == "test-agent"
        assert workspace.path.exists()
        assert workspace.execution_count == 0

    async def test_create_workspace_with_custom_ttl(self, workspace_manager):
        """Test workspace creation with custom TTL."""
        workspace = await workspace_manager.create(ttl_seconds=120)

        assert workspace.ttl_seconds == 120

    async def test_create_workspace_with_preserve(self, workspace_manager):
        """Test workspace creation with preserve flag."""
        workspace = await workspace_manager.create(preserve=True)

        assert workspace.preserve is True
        assert workspace.is_expired is False

    async def test_get_workspace(self, workspace_manager):
        """Test workspace retrieval."""
        created = await workspace_manager.create()
        retrieved = await workspace_manager.get(created.id)

        assert retrieved.id == created.id
        assert retrieved.path == created.path

    async def test_get_nonexistent_workspace(self, workspace_manager):
        """Test retrieval of non-existent workspace raises error."""
        with pytest.raises(WorkspaceNotFoundError):
            await workspace_manager.get("nonexistent-id")

    async def test_touch_updates_access_time(self, workspace_manager):
        """Test that touch updates last_accessed_at."""
        workspace = await workspace_manager.create()
        original_time = workspace.last_accessed_at

        await asyncio.sleep(0.1)
        await workspace_manager.touch(workspace.id)

        updated = await workspace_manager.get(workspace.id, check_expired=False)
        assert updated.last_accessed_at > original_time

    async def test_record_execution(self, workspace_manager):
        """Test recording execution increments count."""
        workspace = await workspace_manager.create()
        assert workspace.execution_count == 0

        await workspace_manager.record_execution(workspace.id)
        updated = await workspace_manager.get(workspace.id, check_expired=False)
        assert updated.execution_count == 1

    async def test_cleanup_workspace(self, workspace_manager):
        """Test workspace cleanup."""
        workspace = await workspace_manager.create()
        assert workspace.path.exists()

        result = await workspace_manager.cleanup(workspace.id)
        assert result is True
        assert not workspace.path.exists()

        with pytest.raises(WorkspaceNotFoundError):
            await workspace_manager.get(workspace.id)

    async def test_cleanup_preserved_workspace_without_force(self, workspace_manager):
        """Test cleanup skips preserved workspaces without force."""
        workspace = await workspace_manager.create(preserve=True)

        result = await workspace_manager.cleanup(workspace.id, force=False)
        assert result is False
        assert workspace.path.exists()

    async def test_cleanup_preserved_workspace_with_force(self, workspace_manager):
        """Test cleanup removes preserved workspaces with force."""
        workspace = await workspace_manager.create(preserve=True)

        result = await workspace_manager.cleanup(workspace.id, force=True)
        assert result is True
        assert not workspace.path.exists()

    async def test_set_preserve(self, workspace_manager):
        """Test setting preserve flag."""
        workspace = await workspace_manager.create()
        assert workspace.preserve is False

        await workspace_manager.set_preserve(workspace.id, True)
        updated = await workspace_manager.get(workspace.id, check_expired=False)
        assert updated.preserve is True

    async def test_list_workspaces(self, workspace_manager):
        """Test listing workspaces."""
        await workspace_manager.create(agent_id="agent-1")
        await workspace_manager.create(agent_id="agent-2")
        await workspace_manager.create(agent_id="agent-1")

        all_workspaces = await workspace_manager.list_workspaces()
        assert len(all_workspaces) == 3

        agent1_workspaces = await workspace_manager.list_workspaces(agent_id="agent-1")
        assert len(agent1_workspaces) == 2

    async def test_get_workspace_files(self, workspace_manager):
        """Test listing files in workspace."""
        workspace = await workspace_manager.create()

        # Create some test files
        (workspace.path / "test.txt").write_text("hello")
        (workspace.path / "subdir").mkdir()
        (workspace.path / "subdir" / "nested.txt").write_text("world")

        files = await workspace_manager.get_workspace_files(workspace.id)
        assert "test.txt" in files
        assert "subdir/nested.txt" in files

    async def test_cleanup_all(self, workspace_manager):
        """Test cleaning up all workspaces."""
        await workspace_manager.create()
        await workspace_manager.create()
        await workspace_manager.create(preserve=True)

        # Without force, preserved workspace remains
        count = await workspace_manager.cleanup_all(force=False)
        assert count == 2

        # With force, all workspaces cleaned
        await workspace_manager.create(preserve=True)
        count = await workspace_manager.cleanup_all(force=True)
        assert count == 2  # The one that remained + the new one


class TestWorkspaceModel:
    """Test suite for Workspace model."""

    def test_workspace_is_expired(self):
        """Test is_expired property."""
        workspace = Workspace(
            id="test",
            path="/tmp/test",
            ttl_seconds=1,
            last_accessed_at=datetime.utcnow() - timedelta(seconds=2),
        )
        assert workspace.is_expired is True

        workspace.preserve = True
        assert workspace.is_expired is False

    def test_workspace_touch(self):
        """Test touch method updates timestamp."""
        workspace = Workspace(
            id="test",
            path="/tmp/test",
            last_accessed_at=datetime.utcnow() - timedelta(hours=1),
        )
        old_time = workspace.last_accessed_at

        workspace.touch()
        assert workspace.last_accessed_at > old_time

    def test_workspace_increment_execution(self):
        """Test increment_execution method."""
        workspace = Workspace(id="test", path="/tmp/test")
        assert workspace.execution_count == 0

        workspace.increment_execution()
        assert workspace.execution_count == 1

    def test_workspace_success_property(self):
        """Test success property on ExecutionResult."""
        from friday_sandbox import ExecutionResult

        success = ExecutionResult(exit_code=0)
        assert success.success is True

        failure = ExecutionResult(exit_code=1)
        assert failure.success is False

        timeout = ExecutionResult(exit_code=0, timed_out=True)
        assert timeout.success is False

        error = ExecutionResult(exit_code=0, error="Something went wrong")
        assert error.success is False
