"""
Runtime configuration for the Friday Agent Framework.

RuntimeConfig mirrors the fields from the legacy FridayConfig
(in friday-cli/container.py) but lives in the runtime package
to avoid circular dependencies.

Ref: Phase 1 Build Plan, Step 4.1
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, cast


def _deployment_profile_from_env() -> Literal["local", "container", "cloud"]:
    value = os.getenv("FRIDAY_DEPLOYMENT_PROFILE", "local")
    if value in {"local", "container", "cloud"}:
        return cast(Literal["local", "container", "cloud"], value)
    return "local"


@dataclass
class RuntimeConfig:
    """
    Configuration for the Friday Runtime Kernel.

    Loads from environment variables with sensible defaults.
    Covers LLM, embedding, storage, telemetry, and agent settings.
    """

    # LLM Configuration
    llm_model: str = field(
        default_factory=lambda: os.getenv("FRIDAY_LLM_MODEL", "gpt-4")
    )
    llm_api_key: str | None = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    llm_api_base: str | None = field(
        default_factory=lambda: os.getenv("FRIDAY_LLM_API_BASE")
    )

    # Embedding Configuration
    embedding_model: str = field(
        default_factory=lambda: os.getenv(
            "FRIDAY_EMBEDDING_MODEL", "text-embedding-3-small"
        )
    )

    # ChromaDB Configuration
    chroma_path: str = field(
        default_factory=lambda: os.getenv("FRIDAY_CHROMA_PATH", ".friday/chroma")
    )
    chroma_collection: str = field(
        default_factory=lambda: os.getenv("FRIDAY_CHROMA_COLLECTION", "friday_memory")
    )

    # Telemetry Configuration
    telemetry_enabled: bool = field(
        default_factory=lambda: os.getenv("FRIDAY_TELEMETRY_ENABLED", "false").lower()
        == "true"
    )
    telemetry_endpoint: str | None = field(
        default_factory=lambda: os.getenv("FRIDAY_OTEL_ENDPOINT")
    )
    debug_mode: bool = field(
        default_factory=lambda: os.getenv("FRIDAY_DEBUG", "false").lower() == "true"
    )

    # Agent Configuration
    agents_dir: str | None = field(
        default_factory=lambda: os.getenv("FRIDAY_AGENTS_DIR")
    )
    memory_mode: str = field(
        default_factory=lambda: os.getenv("FRIDAY_MEMORY_MODE", "single_agent")
    )

    # Runtime filesystem topology
    install_root: str = field(
        default_factory=lambda: os.getenv("FRIDAY_INSTALL_ROOT", str(Path.cwd()))
    )
    runtime_data_root: str = field(
        default_factory=lambda: os.getenv(
            "FRIDAY_RUNTIME_DATA_ROOT", str(Path.home() / ".friday" / "runtime")
        )
    )
    workspace_root: str = field(
        default_factory=lambda: os.getenv("FRIDAY_WORKSPACE_ROOT", str(Path.cwd()))
    )
    cache_root: str | None = field(
        default_factory=lambda: os.getenv("FRIDAY_CACHE_ROOT")
    )
    scratch_backend: str = field(
        default_factory=lambda: os.getenv("FRIDAY_SCRATCH_BACKEND", "in_memory")
    )
    scratch_path: str | None = field(
        default_factory=lambda: os.getenv("FRIDAY_SCRATCH_PATH")
    )

    def __post_init__(self) -> None:
        """Validate additive config contracts while preserving defaults."""
        if self.memory_mode not in {"single_agent", "multi_agent"}:
            raise ValueError("memory_mode must be 'single_agent' or 'multi_agent'")
        if self.deployment_profile not in {"local", "container", "cloud"}:
            raise ValueError(
                "deployment_profile must be 'local', 'container', or 'cloud'"
            )
        if self.scratch_backend not in {"in_memory", "sqlite"}:
            raise ValueError("scratch_backend must be 'in_memory' or 'sqlite'")
        self.validate_runtime_roots()
        self.validate_scratch_path()

    @staticmethod
    def _resolve(path_value: str) -> Path:
        return Path(path_value).expanduser().resolve()

    def validate_runtime_roots(self) -> None:
        """
        Validate runtime root topology.

        Rules:
        - runtime_data_root and workspace_root cannot overlap.
        - runtime_data_root parent must be writable.
        """
        install_root = self._resolve(self.install_root)
        runtime_data_root = self._resolve(self.runtime_data_root)
        workspace_root = self._resolve(self.workspace_root)

        runtime_in_workspace = (
            runtime_data_root == workspace_root
            or workspace_root in runtime_data_root.parents
        )
        workspace_in_runtime = runtime_data_root in workspace_root.parents
        if runtime_in_workspace or workspace_in_runtime:
            raise ValueError("runtime_data_root and workspace_root must not overlap")

        for root in (install_root, workspace_root):
            if not root.exists():
                raise ValueError(f"runtime root does not exist: {root}")

        runtime_parent = runtime_data_root.parent
        if not runtime_parent.exists():
            raise ValueError(
                f"runtime_data_root parent does not exist: {runtime_parent}"
            )
        if not os.access(runtime_parent, os.W_OK):
            raise ValueError(
                f"runtime_data_root parent is not writable: {runtime_parent}"
            )

        if self.cache_root is not None:
            cache_root = self._resolve(self.cache_root)
            cache_parent = cache_root.parent
            if not cache_parent.exists():
                raise ValueError(f"cache_root parent does not exist: {cache_parent}")
            if not os.access(cache_parent, os.W_OK):
                raise ValueError(f"cache_root parent is not writable: {cache_parent}")

    def validate_scratch_path(self) -> None:
        """
        Validate persistent scratch storage placement.

        Rule:
        - when scratch backend is persistent, scratch_path must be inside
          runtime_data_root and outside workspace_root.
        """
        if self.scratch_backend == "in_memory":
            return

        if not self.scratch_path:
            raise ValueError("scratch_path is required when scratch_backend=sqlite")

        scratch_path = self._resolve(self.scratch_path)
        runtime_data_root = self._resolve(self.runtime_data_root)
        workspace_root = self._resolve(self.workspace_root)

        if (
            runtime_data_root not in scratch_path.parents
            and scratch_path != runtime_data_root
        ):
            raise ValueError(
                "scratch_path must be under runtime_data_root for persistent backends"
            )

        if workspace_root in scratch_path.parents or scratch_path == workspace_root:
            raise ValueError(
                "scratch_path must not be under workspace_root for persistent backends"
            )

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        """Create configuration from environment variables."""
        return cls()

    @classmethod
    def deployment_profile_defaults(
        cls,
        profile: Literal["local", "container", "cloud"],
        *,
        cwd: Path | None = None,
    ) -> dict[str, str]:
        """
        Return default path topology for deployment profiles.
        """
        root = (cwd or Path.cwd()).resolve()
        defaults = {
            "local": {
                "install_root": str(root),
                "runtime_data_root": str(Path.home() / ".friday" / "runtime"),
                "workspace_root": str(root),
            },
            "container": {
                "install_root": "/opt/friday",
                "runtime_data_root": "/var/lib/friday/runtime",
                "workspace_root": "/workspace",
            },
            "cloud": {
                "install_root": "/srv/friday/install",
                "runtime_data_root": "/srv/friday/runtime",
                "workspace_root": "/srv/friday/workspace",
            },
        }
        return defaults[profile]

    @classmethod
    def for_testing(cls) -> "RuntimeConfig":
        """
        Create configuration suitable for testing.

        Uses cheaper LLM model, disables telemetry, and uses
        a separate ChromaDB path to avoid polluting production data.
        """
        return cls(
            llm_model="gpt-3.5-turbo",
            debug_mode=True,
            telemetry_enabled=False,
            chroma_path=".friday/test_chroma",
        )

    def resolve_workspace_artifact_path(self, path_value: str) -> Path:
        """
        Resolve artifact output path and enforce workspace-root containment.
        """
        workspace_root = self._resolve(self.workspace_root)
        raw = Path(path_value).expanduser()
        resolved = (
            (workspace_root / raw).resolve() if not raw.is_absolute() else raw.resolve()
        )
        if workspace_root not in resolved.parents and resolved != workspace_root:
            raise ValueError("artifact path must be under workspace_root")
        return resolved

    def resolve_runtime_state_path(self, path_value: str) -> Path:
        """
        Resolve runtime-state path and enforce runtime-data-root containment.
        """
        runtime_data_root = self._resolve(self.runtime_data_root)
        workspace_root = self._resolve(self.workspace_root)
        raw = Path(path_value).expanduser()
        resolved = (
            (runtime_data_root / raw).resolve()
            if not raw.is_absolute()
            else raw.resolve()
        )
        if runtime_data_root not in resolved.parents and resolved != runtime_data_root:
            raise ValueError("runtime state path must be under runtime_data_root")
        if workspace_root in resolved.parents or resolved == workspace_root:
            raise ValueError("runtime state path must not be under workspace_root")
        return resolved

    # Deployment profile controls default topology templates.
    deployment_profile: Literal["local", "container", "cloud"] = field(
        default_factory=_deployment_profile_from_env
    )
