# Friday Framework - Sandbox Specification

## 0. Introduction: The Isolation Layer

**Status:** Ready for Implementation
**Role:** Secure Code Execution Environment
**Package:** `packages/friday-sandbox` (NEW - Standalone)

This specification defines `friday-sandbox`, a secure execution environment that enables agents to run generated code in isolation. The package provides Docker-based sandboxing with configurable resource limits, structured return values, and workspace lifecycle management.

### 0.1. Design Principles

1. **Isolation First:** All code executes in Docker containers with no access to host filesystem or network by default.
2. **Structured Returns:** Code execution can return typed Python objects via Pydantic validation.
3. **Workspace Management:** File artifacts are accessible via volume mapping with configurable TTL.
4. **Layered Configuration:** Settings flow from package defaults → environment → agent profile → per-execution.
5. **Graceful Degradation:** Falls back to subprocess sandbox for development/testing when Docker unavailable.

### 0.2. Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Isolation Technology | Docker containers | Good balance of isolation and practicality |
| Language Support | Python only (initially) | Focus on primary use case |
| Execution Model | One-shot (stateless) | Simpler security model; no persistent kernels |
| Return Serialization | JSON only | Security; avoid pickle deserialization risks |
| Workspace Storage | Host volume mapping | Enables file artifact inspection |

### 0.3. Relationship to Existing Codebase

**Dependencies:**
- `friday-sandbox` is standalone; no dependencies on other Friday packages
- `friday-tools` depends on `friday-sandbox` for code execution tools

**No Conflicts Identified:**
- This is a net-new package with no overlap with existing code

---

## 1. Protocol Definitions

### 1.1. SandboxProtocol

**Path:** `src/friday_sandbox/protocols.py`

The abstract interface for sandbox implementations.

```python
from typing import Protocol
from .models import ExecutionResult, WorkspaceConfig

class SandboxProtocol(Protocol):
    """Abstract interface for code execution sandboxes."""

    async def execute(
        self,
        code: str,
        language: str = "python",
        timeout_seconds: int = 30,
        memory_limit_mb: int = 512,
        capture_return: bool = False,
        return_model: type | None = None,
        workspace_config: WorkspaceConfig | None = None,
    ) -> ExecutionResult:
        """
        Execute code in isolated environment.

        Args:
            code: Source code to execute
            language: Programming language (currently only "python")
            timeout_seconds: Maximum execution time
            memory_limit_mb: Memory limit for container
            capture_return: Whether to capture function return value
            return_model: Optional Pydantic model for return value validation
            workspace_config: Override workspace settings

        Returns:
            ExecutionResult with stdout, stderr, return value, and file artifacts
        """
        ...

    async def create_workspace(
        self,
        config: WorkspaceConfig | None = None,
        agent_id: str | None = None,
    ) -> "Workspace":
        """Create a managed workspace for file artifacts."""
        ...

    async def release_workspace(self, workspace_id: str) -> None:
        """Explicitly release a workspace (immediate cleanup)."""
        ...

    async def extend_workspace(self, workspace_id: str, additional_seconds: int) -> None:
        """Extend workspace TTL (up to hard limit)."""
        ...

    async def cleanup_expired(self) -> int:
        """Clean up expired workspaces. Returns count cleaned."""
        ...
```

### 1.2. ExecutionResult Model

**Path:** `src/friday_sandbox/models.py`

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

@dataclass
class FileArtifact:
    """File created during execution."""
    sandbox_path: str          # Path inside container (/workspace/plot.png)
    local_path: Path           # Mapped host path
    size_bytes: int
    mime_type: str
    created_at: datetime

@dataclass
class ExecutionResult:
    """Result of code execution in sandbox."""

    # Standard output
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    timed_out: bool
    error: str | None = None

    # Structured return (when capture_return=True)
    return_value: Any | None = None
    return_value_json: str | None = None
    return_type: str | None = None

    # File artifacts
    files_created: list[FileArtifact] = field(default_factory=list)
    workspace_path: Path | None = None
    workspace_id: str | None = None

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and not self.timed_out and self.error is None
```

### 1.3. Workspace Model

**Path:** `src/friday_sandbox/models.py`

```python
@dataclass
class Workspace:
    """Managed workspace for execution file artifacts."""

    id: str
    path: Path
    config: "WorkspaceConfig"
    created_at: datetime
    expires_at: datetime
    agent_id: str | None = None

    # Preservation flags
    preserve: bool = False
    preserve_reason: str | None = None

    @property
    def is_expired(self) -> bool:
        """Check if workspace has exceeded TTL."""
        if self.preserve:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def metadata_path(self) -> Path:
        return self.path / ".friday-workspace.json"

    def save_metadata(self) -> None:
        """Persist metadata for cleanup process."""
        import json
        self.metadata_path.write_text(json.dumps({
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "preserve": self.preserve,
            "preserve_reason": self.preserve_reason,
            "agent_id": self.agent_id,
        }))

    @classmethod
    def load_metadata(cls, path: Path) -> "Workspace":
        """Load workspace from metadata file."""
        ...
```

---

## 2. Configuration

### 2.1. WorkspaceConfig Model

**Path:** `src/friday_sandbox/config.py`

```python
from dataclasses import dataclass, field
from pathlib import Path
import os

@dataclass
class WorkspaceConfig:
    """Configuration for workspace lifecycle."""

    # Soft TTL - default expiration (can be extended)
    ttl_seconds: int = 3600              # 1 hour default

    # Hard TTL - absolute maximum (cannot be overridden)
    hard_ttl_seconds: int = 86400        # 24 hours

    # Cleanup behavior
    cleanup_on_exit: bool = True         # Auto-cleanup on context manager exit

    # Debug/introspection
    preserve: bool = False               # Skip cleanup entirely
    preserve_on_error: bool = True       # Preserve if execution fails

    # Resource limits
    max_workspaces: int = 100            # Circuit breaker
    workspace_base_path: Path = field(
        default_factory=lambda: Path("/tmp/friday-workspaces")
    )

    @classmethod
    def from_env(cls) -> "WorkspaceConfig":
        """Load configuration from environment variables."""
        return cls(
            ttl_seconds=int(os.getenv("FRIDAY_SANDBOX_TTL", "3600")),
            hard_ttl_seconds=int(os.getenv("FRIDAY_SANDBOX_HARD_TTL", "86400")),
            preserve=os.getenv("FRIDAY_SANDBOX_PRESERVE", "").lower() == "true",
            preserve_on_error=os.getenv("FRIDAY_SANDBOX_PRESERVE_ON_ERROR", "true").lower() == "true",
            max_workspaces=int(os.getenv("FRIDAY_SANDBOX_MAX_WORKSPACES", "100")),
            workspace_base_path=Path(os.getenv(
                "FRIDAY_SANDBOX_WORKSPACE_PATH",
                "/tmp/friday-workspaces"
            )),
        )
```

### 2.2. SandboxConfig Model

**Path:** `src/friday_sandbox/config.py`

```python
@dataclass
class SandboxConfig:
    """Configuration for sandbox execution."""

    # Docker settings
    image: str = "friday-sandbox-python:latest"
    docker_socket: str = "/var/run/docker.sock"

    # Default resource limits
    default_timeout_seconds: int = 30
    default_memory_limit_mb: int = 512
    max_timeout_seconds: int = 300       # Hard limit
    max_memory_limit_mb: int = 2048      # Hard limit

    # Network isolation
    network_enabled: bool = False        # Disable network by default

    # Workspace settings
    workspace_config: WorkspaceConfig = field(default_factory=WorkspaceConfig)

    @classmethod
    def from_env(cls) -> "SandboxConfig":
        """Load configuration from environment variables."""
        return cls(
            image=os.getenv("FRIDAY_SANDBOX_IMAGE", "friday-sandbox-python:latest"),
            default_timeout_seconds=int(os.getenv("FRIDAY_SANDBOX_TIMEOUT", "30")),
            default_memory_limit_mb=int(os.getenv("FRIDAY_SANDBOX_MEMORY_MB", "512")),
            network_enabled=os.getenv("FRIDAY_SANDBOX_NETWORK", "").lower() == "true",
            workspace_config=WorkspaceConfig.from_env(),
        )
```

### 2.3. Configuration Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 4: Per-Execution Override                                 │
│   sandbox.execute(code, timeout=60, preserve=True)              │
├─────────────────────────────────────────────────────────────────┤
│ Layer 3: Agent Profile                                          │
│   AgentProfile(sandbox_config=SandboxConfig(ttl=3600))          │
├─────────────────────────────────────────────────────────────────┤
│ Layer 2: Application Config (environment variables)             │
│   FRIDAY_SANDBOX_TTL=1800                                       │
│   FRIDAY_SANDBOX_IMAGE=custom-image:v1                          │
├─────────────────────────────────────────────────────────────────┤
│ Layer 1: Package Defaults (hardcoded)                           │
│   DEFAULT_TTL=3600, HARD_TTL=86400, NETWORK=False               │
└─────────────────────────────────────────────────────────────────┘
```

**Merge Rules:**
- Higher layers override lower layers
- `hard_ttl_seconds` and `max_timeout_seconds` cannot be overridden (security)
- `preserve=True` at any layer enables preservation

---

## 3. Docker Sandbox Implementation

### 3.1. DockerSandbox Class

**Path:** `src/friday_sandbox/docker.py`

```python
import docker
from .protocols import SandboxProtocol
from .models import ExecutionResult, Workspace, FileArtifact
from .config import SandboxConfig, WorkspaceConfig

class DockerSandbox(SandboxProtocol):
    """
    Docker-based sandbox for isolated code execution.

    Features:
    - Container isolation with configurable resource limits
    - Volume mapping for file artifacts
    - Structured return value capture via JSON serialization
    - Workspace lifecycle management with TTL
    """

    def __init__(self, config: SandboxConfig | None = None):
        self.config = config or SandboxConfig.from_env()
        self.client = docker.from_env()
        self._workspaces: dict[str, Workspace] = {}

    async def execute(
        self,
        code: str,
        language: str = "python",
        timeout_seconds: int | None = None,
        memory_limit_mb: int | None = None,
        capture_return: bool = False,
        return_model: type | None = None,
        workspace_config: WorkspaceConfig | None = None,
    ) -> ExecutionResult:
        """Execute code in Docker container."""

        # 1. Create or use workspace
        ws_config = workspace_config or self.config.workspace_config
        workspace = await self.create_workspace(config=ws_config)

        # 2. Wrap code for return value capture
        wrapped_code = self._wrap_code(code, capture_return)

        # 3. Write code to workspace
        code_path = workspace.path / "__code__.py"
        code_path.write_text(wrapped_code)

        # 4. Run container
        try:
            result = await self._run_container(
                workspace=workspace,
                timeout=timeout_seconds or self.config.default_timeout_seconds,
                memory_mb=memory_limit_mb or self.config.default_memory_limit_mb,
            )
        except Exception as e:
            if ws_config.preserve_on_error:
                workspace.preserve = True
                workspace.preserve_reason = f"error: {str(e)}"
                workspace.save_metadata()
            raise

        # 5. Parse return value if captured
        if capture_return:
            result = self._parse_return_value(result, return_model)

        # 6. Collect file artifacts
        result.files_created = self._collect_artifacts(workspace)
        result.workspace_path = workspace.path
        result.workspace_id = workspace.id

        # 7. Handle cleanup
        if ws_config.cleanup_on_exit and result.success:
            await self.release_workspace(workspace.id)
        elif not result.success and ws_config.preserve_on_error:
            workspace.preserve = True
            workspace.preserve_reason = f"exit_code={result.exit_code}"
            workspace.save_metadata()

        return result

    def _wrap_code(self, code: str, capture_return: bool) -> str:
        """Wrap user code to capture return value."""
        if not capture_return:
            return code

        return f'''
import json
import sys

# User code
{code}

# Capture return value (assumes last expression or function call)
# User should assign result to __result__
if "__result__" in dir():
    with open("/workspace/__return__.json", "w") as f:
        json.dump(__result__, f)
'''

    async def _run_container(
        self,
        workspace: Workspace,
        timeout: int,
        memory_mb: int,
    ) -> ExecutionResult:
        """Run Docker container with code."""
        import time

        start_time = time.time()

        container = self.client.containers.run(
            image=self.config.image,
            command=["python", "/workspace/__code__.py"],
            volumes={
                str(workspace.path): {"bind": "/workspace", "mode": "rw"}
            },
            mem_limit=f"{memory_mb}m",
            network_disabled=not self.config.network_enabled,
            detach=True,
            user="sandbox",  # Non-root user
        )

        try:
            result = container.wait(timeout=timeout)
            logs = container.logs(stdout=True, stderr=True)
            stdout = container.logs(stdout=True, stderr=False).decode()
            stderr = container.logs(stdout=False, stderr=True).decode()
            exit_code = result["StatusCode"]
            timed_out = False
        except Exception:
            container.kill()
            stdout = ""
            stderr = "Execution timed out"
            exit_code = -1
            timed_out = True
        finally:
            container.remove()

        execution_time_ms = int((time.time() - start_time) * 1000)

        return ExecutionResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            execution_time_ms=execution_time_ms,
            timed_out=timed_out,
        )
```

### 3.2. Return Value Parsing

**Path:** `src/friday_sandbox/serialization.py`

```python
import json
from typing import Any, Type
from pydantic import BaseModel

def parse_return_value(
    workspace_path: Path,
    return_model: Type[BaseModel] | None = None,
) -> tuple[Any, str | None]:
    """
    Parse return value from workspace.

    Returns:
        Tuple of (parsed_value, raw_json)
    """
    return_file = workspace_path / "__return__.json"

    if not return_file.exists():
        return None, None

    raw_json = return_file.read_text()
    value = json.loads(raw_json)

    if return_model is not None:
        value = return_model.model_validate(value)

    return value, raw_json
```

---

## 4. Workspace Management

### 4.1. WorkspaceManager Class

**Path:** `src/friday_sandbox/workspace.py`

```python
from pathlib import Path
from datetime import datetime, timedelta, timezone
import uuid
import shutil

class WorkspaceManager:
    """Manages workspace lifecycle with TTL-based cleanup."""

    def __init__(self, config: WorkspaceConfig):
        self.config = config
        self._workspaces: dict[str, Workspace] = {}

        # Ensure base path exists
        self.config.workspace_base_path.mkdir(parents=True, exist_ok=True)

    async def create_workspace(
        self,
        ttl_seconds: int | None = None,
        agent_id: str | None = None,
        preserve: bool = False,
    ) -> Workspace:
        """Create a new workspace."""
        # Check circuit breaker
        if len(self._workspaces) >= self.config.max_workspaces:
            # Clean expired before failing
            await self.cleanup_expired()
            if len(self._workspaces) >= self.config.max_workspaces:
                raise RuntimeError(
                    f"Maximum workspaces ({self.config.max_workspaces}) exceeded"
                )

        workspace_id = f"ws-{uuid.uuid4().hex[:12]}"
        workspace_path = self.config.workspace_base_path / workspace_id
        workspace_path.mkdir(parents=True)

        ttl = ttl_seconds or self.config.ttl_seconds
        # Enforce hard limit
        ttl = min(ttl, self.config.hard_ttl_seconds)

        now = datetime.now(timezone.utc)
        workspace = Workspace(
            id=workspace_id,
            path=workspace_path,
            config=self.config,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl),
            agent_id=agent_id,
            preserve=preserve,
        )

        workspace.save_metadata()
        self._workspaces[workspace_id] = workspace

        return workspace

    async def release_workspace(self, workspace_id: str) -> None:
        """Explicitly release a workspace (immediate cleanup)."""
        workspace = self._workspaces.get(workspace_id)
        if workspace is None:
            return

        if workspace.preserve:
            # Don't delete preserved workspaces
            return

        shutil.rmtree(workspace.path, ignore_errors=True)
        del self._workspaces[workspace_id]

    async def extend_workspace(
        self,
        workspace_id: str,
        additional_seconds: int,
    ) -> None:
        """Extend workspace TTL (up to hard limit)."""
        workspace = self._workspaces.get(workspace_id)
        if workspace is None:
            raise KeyError(f"Workspace {workspace_id} not found")

        new_expires = workspace.expires_at + timedelta(seconds=additional_seconds)
        hard_limit = workspace.created_at + timedelta(
            seconds=self.config.hard_ttl_seconds
        )

        workspace.expires_at = min(new_expires, hard_limit)
        workspace.save_metadata()

    async def cleanup_expired(self) -> int:
        """Clean up expired workspaces. Returns count cleaned."""
        cleaned = 0
        expired_ids = [
            ws_id for ws_id, ws in self._workspaces.items()
            if ws.is_expired
        ]

        for ws_id in expired_ids:
            workspace = self._workspaces[ws_id]
            shutil.rmtree(workspace.path, ignore_errors=True)
            del self._workspaces[ws_id]
            cleaned += 1

        return cleaned

    async def list_preserved(self) -> list[Workspace]:
        """List all preserved workspaces."""
        return [ws for ws in self._workspaces.values() if ws.preserve]

    async def cleanup_preserved(self, workspace_id: str) -> None:
        """Force cleanup of a preserved workspace."""
        workspace = self._workspaces.get(workspace_id)
        if workspace:
            shutil.rmtree(workspace.path, ignore_errors=True)
            del self._workspaces[workspace_id]

    async def cleanup_all_preserved(self) -> int:
        """Force cleanup of all preserved workspaces."""
        preserved = await self.list_preserved()
        for ws in preserved:
            await self.cleanup_preserved(ws.id)
        return len(preserved)

    def scan_filesystem(self) -> None:
        """
        Scan filesystem for orphaned workspaces.
        Useful after process restart.
        """
        for path in self.config.workspace_base_path.iterdir():
            if path.is_dir() and path.name.startswith("ws-"):
                metadata_path = path / ".friday-workspace.json"
                if metadata_path.exists():
                    try:
                        workspace = Workspace.load_metadata(path)
                        self._workspaces[workspace.id] = workspace
                    except Exception:
                        pass  # Corrupted metadata, will be cleaned by TTL
```

---

## 5. Alternative Implementations

### 5.1. SubprocessSandbox

**Path:** `src/friday_sandbox/subprocess.py`

Fallback for development/testing when Docker is unavailable.

```python
import subprocess
import tempfile
from .protocols import SandboxProtocol

class SubprocessSandbox(SandboxProtocol):
    """
    Subprocess-based sandbox for development/testing.

    WARNING: Provides NO isolation. Only use for development.
    """

    def __init__(self, config: SandboxConfig | None = None):
        self.config = config or SandboxConfig.from_env()
        import warnings
        warnings.warn(
            "SubprocessSandbox provides NO isolation. "
            "Use DockerSandbox for production.",
            UserWarning
        )

    async def execute(
        self,
        code: str,
        timeout_seconds: int = 30,
        **kwargs,
    ) -> ExecutionResult:
        """Execute code in subprocess (no isolation)."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(code)
            f.flush()

            try:
                result = subprocess.run(
                    ["python", f.name],
                    capture_output=True,
                    timeout=timeout_seconds,
                    text=True,
                )
                return ExecutionResult(
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=result.returncode,
                    execution_time_ms=0,
                    timed_out=False,
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    stdout="",
                    stderr="Execution timed out",
                    exit_code=-1,
                    execution_time_ms=timeout_seconds * 1000,
                    timed_out=True,
                )
```

### 5.2. MockSandbox

**Path:** `src/friday_sandbox/mock.py`

For unit testing tools that depend on sandbox.

```python
from .protocols import SandboxProtocol
from .models import ExecutionResult

class MockSandbox(SandboxProtocol):
    """
    Mock sandbox for unit testing.

    Configure responses via constructor or set directly.
    """

    def __init__(self):
        self.next_result: ExecutionResult | None = None
        self.execute_calls: list[dict] = []

    async def execute(self, code: str, **kwargs) -> ExecutionResult:
        self.execute_calls.append({"code": code, **kwargs})

        if self.next_result:
            result = self.next_result
            self.next_result = None
            return result

        return ExecutionResult(
            stdout="",
            stderr="",
            exit_code=0,
            execution_time_ms=1,
            timed_out=False,
        )

    def set_next_result(self, result: ExecutionResult) -> None:
        """Set the result for the next execute call."""
        self.next_result = result
```

---

## 6. Docker Image

### 6.1. Dockerfile

**Path:** `docker/Dockerfile.python`

```dockerfile
# friday-sandbox-python:latest
FROM python:3.13.4-slim

# Install common packages
RUN pip install --no-cache-dir \
    numpy \
    pandas \
    matplotlib \
    seaborn \
    scikit-learn \
    requests \
    httpx \
    pydantic \
    python-dateutil

# Create non-root user
RUN useradd -m -s /bin/bash sandbox

# Workspace directory
WORKDIR /workspace
RUN chown sandbox:sandbox /workspace

# Switch to non-root user
USER sandbox

# Default command (overridden at runtime)
CMD ["python", "--version"]
```

### 6.2. Build Script

**Path:** `docker/build.sh`

```bash
#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

docker build \
    -t friday-sandbox-python:latest \
    -f "$SCRIPT_DIR/Dockerfile.python" \
    "$SCRIPT_DIR"

echo "Built friday-sandbox-python:latest"
```

---

## 7. Package Configuration

### 7.1. pyproject.toml

```toml
[project]
name = "friday-sandbox"
version = "0.1.0"
description = "Secure code execution sandbox for AI agents"
requires-python = ">=3.13.4"
license = { text = "MIT" }
authors = [{ name = "Friday Team" }]
keywords = ["ai", "agents", "sandbox", "docker", "isolation"]

dependencies = [
    "docker>=6.0.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.10.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/friday_sandbox"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

---

## 8. Package Structure

```
packages/friday-sandbox/
├── pyproject.toml
├── docker/
│   ├── Dockerfile.python
│   └── build.sh
├── src/friday_sandbox/
│   ├── __init__.py
│   ├── protocols.py          # SandboxProtocol
│   ├── models.py             # ExecutionResult, Workspace, FileArtifact
│   ├── config.py             # SandboxConfig, WorkspaceConfig
│   ├── docker.py             # DockerSandbox implementation
│   ├── subprocess.py         # SubprocessSandbox (dev fallback)
│   ├── mock.py               # MockSandbox (testing)
│   ├── workspace.py          # WorkspaceManager
│   └── serialization.py      # Return value parsing
└── tests/
    ├── __init__.py
    ├── test_docker_sandbox.py
    ├── test_subprocess_sandbox.py
    ├── test_workspace_manager.py
    ├── test_serialization.py
    └── conftest.py           # Fixtures
```

---

## 9. Integration with friday-tools

### 9.1. Code Execution Tools

**Path:** `friday-tools/src/friday_tools/execution/python.py`

```python
from friday_sandbox import SandboxProtocol, ExecutionResult

@tool(description="Execute Python code in isolated sandbox")
async def python_execute(
    sandbox: SandboxProtocol,        # Injected via DI
    code: str,
    timeout: int = 30,
    capture_return: bool = False,
    preserve: bool = False,
) -> ExecutionResult:
    """
    Execute Python code in an isolated Docker sandbox.

    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds
        capture_return: Whether to capture return value
        preserve: Whether to preserve workspace after execution

    Returns:
        ExecutionResult with stdout, stderr, and optional return value
    """
    return await sandbox.execute(
        code=code,
        timeout_seconds=timeout,
        capture_return=capture_return,
        workspace_config=WorkspaceConfig(preserve=preserve),
    )
```

### 9.2. Dependency Injection

```python
# At application startup
sandbox_config = SandboxConfig.from_env()
sandbox = DockerSandbox(config=sandbox_config)

# Inject into registry
registry.bind_dependency("python_execute", sandbox=sandbox)

# Or inject into agent
agent = CodingAgent(
    profile=coding_profile,
    sandbox=sandbox,
    # ...
)
```

---

## 10. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FRIDAY_SANDBOX_IMAGE` | `friday-sandbox-python:latest` | Docker image to use |
| `FRIDAY_SANDBOX_TIMEOUT` | `30` | Default execution timeout (seconds) |
| `FRIDAY_SANDBOX_MEMORY_MB` | `512` | Default memory limit |
| `FRIDAY_SANDBOX_NETWORK` | `false` | Enable network access |
| `FRIDAY_SANDBOX_TTL` | `3600` | Default workspace TTL (seconds) |
| `FRIDAY_SANDBOX_HARD_TTL` | `86400` | Maximum workspace TTL |
| `FRIDAY_SANDBOX_PRESERVE` | `false` | Preserve all workspaces |
| `FRIDAY_SANDBOX_PRESERVE_ON_ERROR` | `true` | Preserve on execution error |
| `FRIDAY_SANDBOX_WORKSPACE_PATH` | `/tmp/friday-workspaces` | Workspace base path |
| `FRIDAY_SANDBOX_MAX_WORKSPACES` | `100` | Maximum concurrent workspaces |

---

## 11. Implementation Phases

| Phase | Description | Deliverables |
|-------|-------------|--------------|
| **Phase 1** | Core models and protocols | protocols.py, models.py, config.py |
| **Phase 2** | Workspace management | workspace.py with TTL logic |
| **Phase 3** | Docker implementation | docker.py with container execution |
| **Phase 4** | Return value serialization | serialization.py with Pydantic support |
| **Phase 5** | Alternative implementations | subprocess.py, mock.py |
| **Phase 6** | Docker image | Dockerfile and build script |
| **Phase 7** | Testing | Comprehensive test suite |

---

## 12. Issues and Remediation

### 12.1. Identified Conflicts

None - this is a net-new package.

### 12.2. Required Prerequisites

| Prerequisite | Description |
|--------------|-------------|
| Docker installed | Required for DockerSandbox |
| Docker socket accessible | `/var/run/docker.sock` |
| Image built | `friday-sandbox-python:latest` must exist |

### 12.3. Security Considerations

| Risk | Mitigation |
|------|------------|
| Container escape | Use non-root user, drop capabilities |
| Resource exhaustion | Memory limits, timeout enforcement |
| Network access | Disabled by default |
| Filesystem access | Volume mapping only to workspace |
| Sensitive data in code | Do not log code; sanitize errors |

### 12.4. Future Considerations

1. **Multi-language support:** Add Node.js, Ruby, etc.
2. **Persistent kernels:** Jupyter-style stateful execution
3. **GPU support:** For ML workloads
4. **Cloud sandboxes:** E2B, Modal integration
5. **Firecracker:** MicroVM isolation for maximum security

---

## 13. Success Criteria

- [ ] Package builds and installs via `uv sync`
- [ ] Docker image builds successfully
- [ ] DockerSandbox executes Python code
- [ ] Structured returns work with Pydantic models
- [ ] Workspace TTL enforced correctly
- [ ] Preserve flag prevents cleanup
- [ ] SubprocessSandbox works as fallback
- [ ] MockSandbox enables tool testing
- [ ] All tests passing
- [ ] Integration with friday-tools verified
