# mypy: ignore-errors
"""
Docker-based sandbox implementation.

Ref: docs/specs/sandbox_specifications.md - Section 7: Docker Implementation

Provides secure, isolated code execution in Docker containers with:
- Memory and CPU limits
- Network isolation (disabled by default)
- Non-root user execution
- Read-only root filesystem
- Workspace volume mounting
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from .config import SandboxConfig, WorkspaceConfig
from .models import ExecutionResult, SandboxTimeoutError, Workspace
from .serialization import (
    extract_return_value,
    validate_return_type,
    wrap_code_for_return_capture,
)
from .workspace import WorkspaceManager

logger = logging.getLogger(__name__)


class DockerSandbox:
    """
    Docker-based sandbox for secure code execution.

    Executes Python code in isolated Docker containers with configurable
    resource limits and security settings.
    """

    def __init__(
        self,
        config: SandboxConfig | None = None,
    ):
        """
        Initialize Docker sandbox.

        Args:
            config: Sandbox configuration. If None, loads from environment.
        """
        self.config = config or SandboxConfig.from_environment()
        self._docker_client = None
        self._workspace_manager = WorkspaceManager(
            config=self.config.workspace,
            base_path=self.config.docker.workspace_base_path,
        )

    @property
    def docker_client(self):
        """Lazy-load Docker client."""
        if self._docker_client is None:
            try:
                import docker

                self._docker_client = docker.from_env()
            except ImportError:
                raise RuntimeError(  # noqa: B904
                    "Docker SDK not installed. Install with: pip install docker"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to connect to Docker: {e}")  # noqa: B904
        return self._docker_client

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
        Execute code in a Docker container.

        Args:
            code: Python source code to execute.
            language: Programming language (only "python" supported).
            timeout_seconds: Execution timeout (uses config default if None).
            workspace_id: Optional workspace for file persistence.
            environment: Environment variables for the container.
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
        if workspace_id:
            workspace = await self._workspace_manager.get(workspace_id)
            await self._workspace_manager.record_execution(workspace_id)

        # Wrap code for return value capture
        wrapped_code = wrap_code_for_return_capture(code)

        # Execute in container
        start_time = time.time()
        try:
            result = await self._run_in_container(
                code=wrapped_code,
                timeout=timeout,
                workspace=workspace,
                environment=environment,
            )
        except asyncio.TimeoutError:
            raise SandboxTimeoutError(timeout)  # noqa: B904

        execution_time_ms = (time.time() - start_time) * 1000

        # Parse return value from stdout
        cleaned_stdout, return_value, raw_json = extract_return_value(result.stdout)

        # Validate return type if specified
        if return_type is not None and return_value is not None:
            try:
                return_value = validate_return_type(return_value, return_type)
            except Exception as e:
                logger.warning(f"Return type validation failed: {e}")
                result.error = f"Return type validation failed: {e}"

        # Update result with parsed values
        result.stdout = cleaned_stdout
        result.return_value = return_value
        result.return_value_raw = raw_json
        result.execution_time_ms = execution_time_ms

        # List created files if workspace was used
        if workspace:
            result.files_created = await self._workspace_manager.get_workspace_files(
                workspace_id
            )

        return result

    async def _run_in_container(
        self,
        code: str,
        timeout: int,
        workspace: Workspace | None = None,
        environment: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """
        Run code in a Docker container.

        This method handles the actual container execution including:
        - Volume mounting for workspaces
        - Resource limits
        - Timeout handling
        - Output capture
        """
        docker_config = self.config.docker

        # Build container configuration
        container_config = {
            "image": docker_config.image,
            "command": ["python", "-c", code],
            "detach": True,
            "mem_limit": docker_config.memory_limit,
            "nano_cpus": int(docker_config.cpu_limit * 1e9),
            "network_disabled": not docker_config.network_enabled,
            "read_only": docker_config.read_only_rootfs,
            "user": docker_config.user,
            "environment": environment or {},
        }

        # Add workspace volume mount
        volumes = {}
        if workspace:
            volumes[str(workspace.path)] = {
                "bind": "/workspace",
                "mode": "rw",
            }
            container_config["working_dir"] = "/workspace"

        # Add tmpfs for writable directories when root is read-only
        if docker_config.read_only_rootfs:
            container_config["tmpfs"] = {
                "/tmp": "size=64M,mode=1777",
            }

        if volumes:
            container_config["volumes"] = volumes

        # Run container
        loop = asyncio.get_event_loop()
        container = await loop.run_in_executor(
            None,
            lambda: self.docker_client.containers.run(**container_config),
        )

        try:
            # Wait for completion with timeout
            exit_code = await asyncio.wait_for(
                loop.run_in_executor(None, container.wait),
                timeout=timeout,
            )

            # Get logs
            stdout = await loop.run_in_executor(
                None,
                lambda: container.logs(stdout=True, stderr=False).decode("utf-8"),
            )
            stderr = await loop.run_in_executor(
                None,
                lambda: container.logs(stdout=False, stderr=True).decode("utf-8"),
            )

            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code.get("StatusCode", 1),
            )

        except asyncio.TimeoutError:
            # Kill container on timeout
            await loop.run_in_executor(None, container.kill)
            raise

        finally:
            # Always remove container
            await loop.run_in_executor(
                None,
                lambda: container.remove(force=True),
            )

    async def create_workspace(
        self,
        config: WorkspaceConfig | None = None,
        agent_id: str | None = None,
    ) -> Workspace:
        """
        Create a new workspace for persistent file storage.

        Args:
            config: Optional workspace configuration overrides.
            agent_id: Optional agent identifier.

        Returns:
            New Workspace instance.
        """
        # Merge config if provided
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

    async def check_docker_available(self) -> bool:
        """
        Check if Docker is available and the sandbox image exists.

        Returns:
            True if Docker is available and image exists.
        """
        try:
            self.docker_client.ping()

            # Check if image exists
            try:
                self.docker_client.images.get(self.config.docker.image)
                return True
            except Exception:
                # Image doesn't exist - try to pull if policy allows
                if self.config.docker.pull_policy in ("always", "if-not-present"):
                    try:
                        self.docker_client.images.pull(self.config.docker.image)
                        return True
                    except Exception as e:
                        logger.warning(f"Failed to pull image: {e}")
                        return False
                return False

        except Exception as e:
            logger.warning(f"Docker not available: {e}")
            return False

    async def __aenter__(self) -> DockerSandbox:
        """Async context manager entry - starts workspace cleanup loop."""
        await self._workspace_manager.start_cleanup_loop()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - stops cleanup loop."""
        await self._workspace_manager.stop_cleanup_loop()
