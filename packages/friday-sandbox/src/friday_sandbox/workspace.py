"""
Workspace management with TTL-based lifecycle.

Ref: docs/specs/sandbox_specifications.md - Section 5: Workspace Management
"""

from __future__ import annotations

import asyncio
import logging
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .config import WorkspaceConfig
from .models import Workspace, WorkspaceExpiredError, WorkspaceNotFoundError

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    """Return current UTC time with timezone awareness."""
    return datetime.now(timezone.utc)


def _ensure_utc(value: datetime) -> datetime:
    """Coerce naive datetimes to UTC and normalize aware values to UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class WorkspaceManager:
    """
    Manages workspace lifecycle including creation, access, and cleanup.

    Implements TTL-based automatic cleanup with soft and hard limits:
    - Soft limit: Logs warning, allows continued use
    - Hard limit: Forces cleanup regardless of activity

    Thread-safe for concurrent access from multiple agents.
    """

    def __init__(
        self,
        config: WorkspaceConfig | None = None,
        base_path: Path | None = None,
    ):
        """
        Initialize workspace manager.

        Args:
            config: Workspace configuration. If None, uses defaults.
            base_path: Base directory for workspaces. If None, uses /tmp.
        """
        self.config = config or WorkspaceConfig()
        self.base_path = base_path or Path("/tmp/friday-workspaces")
        self._workspaces: dict[str, Workspace] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: asyncio.Task | None = None
        self._on_cleanup_callbacks: list[Callable[[str], None]] = []

    async def start_cleanup_loop(self) -> None:
        """Start the background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.debug("Started workspace cleanup loop")

    async def stop_cleanup_loop(self) -> None:
        """Stop the background cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.debug("Stopped workspace cleanup loop")

    async def _cleanup_loop(self) -> None:
        """Background loop that periodically cleans up expired workspaces."""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval_seconds)
                count = await self.cleanup_expired()
                if count > 0:
                    logger.info(f"Cleaned up {count} expired workspaces")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def create(
        self,
        agent_id: str | None = None,
        ttl_seconds: int | None = None,
        preserve: bool = False,
    ) -> Workspace:
        """
        Create a new workspace.

        Args:
            agent_id: Optional agent identifier for association.
            ttl_seconds: Custom TTL, or use config default.
            preserve: If True, workspace won't be auto-cleaned.

        Returns:
            Newly created Workspace instance.
        """
        workspace_id = str(uuid.uuid4())
        workspace_path = self.base_path / workspace_id

        # Create directory
        workspace_path.mkdir(parents=True, exist_ok=True)

        workspace = Workspace(
            id=workspace_id,
            path=workspace_path,
            agent_id=agent_id,
            ttl_seconds=ttl_seconds or self.config.ttl_seconds,
            preserve=preserve,
        )

        async with self._lock:
            self._workspaces[workspace_id] = workspace

        logger.debug(
            f"Created workspace {workspace_id} for agent {agent_id}, "
            f"TTL={workspace.ttl_seconds}s, preserve={preserve}"
        )

        return workspace

    async def get(
        self,
        workspace_id: str,
        check_expired: bool = True,
    ) -> Workspace:
        """
        Get a workspace by ID.

        Args:
            workspace_id: The workspace identifier.
            check_expired: If True, raises error for expired workspaces.

        Returns:
            The Workspace instance.

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist.
            WorkspaceExpiredError: If workspace has expired (and check_expired=True).
        """
        async with self._lock:
            workspace = self._workspaces.get(workspace_id)

        if workspace is None:
            raise WorkspaceNotFoundError(workspace_id)

        if check_expired:
            # Check soft limit (warning)
            elapsed = (_utc_now() - _ensure_utc(workspace.last_accessed_at)).total_seconds()
            if elapsed > self.config.ttl_soft_limit_seconds and not workspace.preserve:
                logger.warning(
                    f"Workspace {workspace_id} approaching TTL limit "
                    f"(elapsed: {elapsed:.0f}s, soft limit: "
                    f"{self.config.ttl_soft_limit_seconds}s)"
                )

            # Check hard limit (error)
            if (
                elapsed > self.config.ttl_hard_limit_seconds
                and not workspace.preserve
            ):
                raise WorkspaceExpiredError(workspace_id)

            if workspace.is_expired:
                raise WorkspaceExpiredError(workspace_id)

        return workspace

    async def touch(self, workspace_id: str) -> None:
        """
        Update workspace last_accessed_at timestamp.

        Args:
            workspace_id: The workspace identifier.

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist.
        """
        workspace = await self.get(workspace_id, check_expired=False)
        workspace.touch()

    async def record_execution(self, workspace_id: str) -> None:
        """
        Record an execution in the workspace.

        Updates last_accessed_at and increments execution_count.

        Args:
            workspace_id: The workspace identifier.

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist.
        """
        workspace = await self.get(workspace_id, check_expired=False)
        workspace.increment_execution()

    async def set_preserve(self, workspace_id: str, preserve: bool) -> None:
        """
        Set the preserve flag on a workspace.

        Args:
            workspace_id: The workspace identifier.
            preserve: Whether to preserve the workspace.

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist.
        """
        workspace = await self.get(workspace_id, check_expired=False)
        workspace.preserve = preserve
        logger.debug(f"Set preserve={preserve} for workspace {workspace_id}")

    async def cleanup(
        self,
        workspace_id: str,
        force: bool = False,
    ) -> bool:
        """
        Clean up a workspace and delete its files.

        Args:
            workspace_id: The workspace identifier.
            force: If True, cleanup even if preserve=True.

        Returns:
            True if cleanup succeeded, False otherwise.
        """
        async with self._lock:
            workspace = self._workspaces.get(workspace_id)

        if workspace is None:
            return False

        if workspace.preserve and not force:
            logger.debug(
                f"Skipping cleanup of preserved workspace {workspace_id}"
            )
            return False

        # Delete directory
        try:
            if workspace.path.exists():
                shutil.rmtree(workspace.path)
        except Exception as e:
            logger.error(f"Error deleting workspace directory: {e}")
            return False

        # Remove from registry
        async with self._lock:
            self._workspaces.pop(workspace_id, None)

        # Notify callbacks
        for callback in self._on_cleanup_callbacks:
            try:
                callback(workspace_id)
            except Exception as e:
                logger.error(f"Error in cleanup callback: {e}")

        logger.debug(f"Cleaned up workspace {workspace_id}")
        return True

    async def cleanup_expired(self) -> int:
        """
        Clean up all expired workspaces.

        Returns:
            Number of workspaces cleaned up.
        """
        now = _utc_now()
        expired_ids = []

        async with self._lock:
            for workspace_id, workspace in self._workspaces.items():
                if workspace.preserve:
                    continue

                elapsed = (now - _ensure_utc(workspace.last_accessed_at)).total_seconds()

                # Force cleanup if past hard limit
                if elapsed > self.config.ttl_hard_limit_seconds:
                    expired_ids.append(workspace_id)
                elif workspace.is_expired:
                    expired_ids.append(workspace_id)

        count = 0
        for workspace_id in expired_ids:
            if await self.cleanup(workspace_id, force=True):
                count += 1

        return count

    async def list_workspaces(
        self,
        agent_id: str | None = None,
        include_expired: bool = False,
    ) -> list[Workspace]:
        """
        List all workspaces, optionally filtered by agent.

        Args:
            agent_id: Filter by agent ID if provided.
            include_expired: Include expired workspaces.

        Returns:
            List of Workspace instances.
        """
        async with self._lock:
            workspaces = list(self._workspaces.values())

        if agent_id is not None:
            workspaces = [w for w in workspaces if w.agent_id == agent_id]

        if not include_expired:
            workspaces = [w for w in workspaces if not w.is_expired]

        return workspaces

    async def get_workspace_files(self, workspace_id: str) -> list[str]:
        """
        List all files in a workspace.

        Args:
            workspace_id: The workspace identifier.

        Returns:
            List of relative file paths within the workspace.

        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist.
        """
        workspace = await self.get(workspace_id)

        files = []
        for path in workspace.path.rglob("*"):
            if path.is_file():
                files.append(str(path.relative_to(workspace.path)))

        return files

    def on_cleanup(self, callback: Callable[[str], None]) -> None:
        """
        Register a callback to be called when a workspace is cleaned up.

        Args:
            callback: Function taking workspace_id as argument.
        """
        self._on_cleanup_callbacks.append(callback)

    async def cleanup_all(self, force: bool = False) -> int:
        """
        Clean up all workspaces.

        Args:
            force: If True, cleanup even preserved workspaces.

        Returns:
            Number of workspaces cleaned up.
        """
        async with self._lock:
            workspace_ids = list(self._workspaces.keys())

        count = 0
        for workspace_id in workspace_ids:
            if await self.cleanup(workspace_id, force=force):
                count += 1

        return count

    async def __aenter__(self) -> WorkspaceManager:
        """Async context manager entry - starts cleanup loop."""
        await self.start_cleanup_loop()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - stops cleanup loop."""
        await self.stop_cleanup_loop()
