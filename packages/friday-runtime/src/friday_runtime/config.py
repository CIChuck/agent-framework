"""
Runtime configuration for the Friday Agent Framework.

RuntimeConfig preserves the existing flat compatibility surface used by the
runtime/kernel/CLI while adding the nested Phase 4 config contract and
dual-source loading helpers.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]
from friday_mcp.config import MCPConfig


def _coerce_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _deployment_profile_from_env() -> Literal["local", "container", "cloud"]:
    value = os.getenv("FRIDAY_DEPLOYMENT_PROFILE", "local")
    if value in {"local", "container", "cloud"}:
        return cast(Literal["local", "container", "cloud"], value)
    return "local"


@dataclass(frozen=True)
class ConfigPolicy:
    allow_env_override: bool = False
    strict_agent_llm_binding: bool = False
    workflow_mode: Literal["canonical", "legacy", "auto"] = "canonical"
    unknown_key_policy: Literal["fail"] = "fail"


@dataclass(frozen=True)
class RuntimePaths:
    install_root: str
    runtime_data_root: str
    workspace_root: str
    cache_root: str | None = None


@dataclass(frozen=True)
class ArtifactPolicy:
    enabled: bool = True
    root_dir: str = "artifacts"
    lineage_required: bool = True
    publish_on_task_success: bool = True


@dataclass(frozen=True)
class AgentsConfig:
    dir: str | None = None
    role_bindings: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowsConfig:
    dir: str | None = None


def _normalize_str_tuple(values: Any, *, field_name: str) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, (list, tuple)):
        normalized = []
        for value in values:
            if not isinstance(value, str):
                raise ValueError(f"{field_name} entries must be strings")
            stripped = value.strip()
            if stripped:
                normalized.append(stripped)
        return tuple(normalized)
    raise ValueError(f"{field_name} must be a list of strings")


@dataclass(frozen=True)
class ToolProviderConfig:
    enabled: bool = False
    mode: Literal["all", "selected"] = "all"
    include_categories: tuple[str, ...] = ()
    exclude_categories: tuple[str, ...] = ()
    include_tools: tuple[str, ...] = ()
    exclude_tools: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.mode not in {"all", "selected"}:
            raise ValueError("tool provider mode must be 'all' or 'selected'")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ToolProviderConfig:
        return cls(
            enabled=bool(data.get("enabled", False)),
            mode=cast(Literal["all", "selected"], data.get("mode", "all")),
            include_categories=_normalize_str_tuple(
                data.get("include_categories"),
                field_name="tools provider include_categories",
            ),
            exclude_categories=_normalize_str_tuple(
                data.get("exclude_categories"),
                field_name="tools provider exclude_categories",
            ),
            include_tools=_normalize_str_tuple(
                data.get("include_tools"),
                field_name="tools provider include_tools",
            ),
            exclude_tools=_normalize_str_tuple(
                data.get("exclude_tools"),
                field_name="tools provider exclude_tools",
            ),
        )


@dataclass(frozen=True)
class MCPToolProviderConfig:
    enabled: bool = False
    mode: Literal["all", "selected"] = "all"
    include_categories: tuple[str, ...] = ()
    exclude_categories: tuple[str, ...] = ()
    include_tools: tuple[str, ...] = ()
    exclude_tools: tuple[str, ...] = ()
    config: MCPConfig = field(default_factory=MCPConfig)

    def __post_init__(self) -> None:
        if self.mode not in {"all", "selected"}:
            raise ValueError("tool provider mode must be 'all' or 'selected'")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> MCPToolProviderConfig:
        raw_config = data.get("config", {})
        if isinstance(raw_config, MCPConfig):
            mcp_config = raw_config
        elif isinstance(raw_config, Mapping):
            mcp_config = MCPConfig.model_validate(dict(raw_config))
        else:
            raise ValueError("tools.providers.mcp.config must be an object")

        return cls(
            enabled=bool(data.get("enabled", False)),
            mode=cast(Literal["all", "selected"], data.get("mode", "all")),
            include_categories=_normalize_str_tuple(
                data.get("include_categories"),
                field_name="tools provider include_categories",
            ),
            exclude_categories=_normalize_str_tuple(
                data.get("exclude_categories"),
                field_name="tools provider exclude_categories",
            ),
            include_tools=_normalize_str_tuple(
                data.get("include_tools"),
                field_name="tools provider include_tools",
            ),
            exclude_tools=_normalize_str_tuple(
                data.get("exclude_tools"),
                field_name="tools provider exclude_tools",
            ),
            config=mcp_config,
        )


@dataclass(frozen=True)
class ToolProvidersConfig:
    builtin: ToolProviderConfig = field(
        default_factory=lambda: ToolProviderConfig(enabled=True, mode="all")
    )
    friday_tools: ToolProviderConfig = field(default_factory=ToolProviderConfig)
    mcp: MCPToolProviderConfig = field(default_factory=MCPToolProviderConfig)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ToolProvidersConfig:
        unknown = set(data) - {"builtin", "friday_tools", "mcp"}
        if unknown:
            raise ValueError(
                f"Unknown tool providers in runtime config: {sorted(unknown)}"
            )

        builtin_raw = data.get("builtin", {})
        friday_tools_raw = data.get("friday_tools", {})
        mcp_raw = data.get("mcp", {})
        if not isinstance(builtin_raw, Mapping):
            raise ValueError("tools.providers.builtin must be an object")
        if not isinstance(friday_tools_raw, Mapping):
            raise ValueError("tools.providers.friday_tools must be an object")
        if not isinstance(mcp_raw, Mapping):
            raise ValueError("tools.providers.mcp must be an object")

        return cls(
            builtin=ToolProviderConfig.from_dict(builtin_raw),
            friday_tools=ToolProviderConfig.from_dict(friday_tools_raw),
            mcp=MCPToolProviderConfig.from_dict(mcp_raw),
        )


@dataclass(frozen=True)
class ToolsConfig:
    providers: ToolProvidersConfig = field(default_factory=ToolProvidersConfig)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ToolsConfig:
        unknown = set(data) - {"providers"}
        if unknown:
            raise ValueError(
                f"Unknown keys in runtime config section 'tools': {sorted(unknown)}"
            )

        providers_raw = data.get("providers", {})
        if not isinstance(providers_raw, Mapping):
            raise ValueError("tools.providers must be an object")
        return cls(providers=ToolProvidersConfig.from_dict(providers_raw))


@dataclass(frozen=True)
class ResiliencePolicy:
    timeout_seconds: int = 60
    max_retries: int = 2

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("resilience.timeout_seconds must be > 0")
        if self.max_retries < 0:
            raise ValueError("resilience.max_retries must be >= 0")


@dataclass(frozen=True)
class LLMServiceConfig:
    provider: str = "openai"
    model: str = "gpt-4"
    api_key: str | None = None
    api_base: str | None = None
    resilience: ResiliencePolicy = field(default_factory=ResiliencePolicy)

    def __post_init__(self) -> None:
        if not self.provider:
            raise ValueError("llm service provider must be non-empty")
        if not self.model:
            raise ValueError("llm service model must be non-empty")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> LLMServiceConfig:
        resilience = data.get("resilience", {})
        if isinstance(resilience, ResiliencePolicy):
            resilience_policy = resilience
        elif isinstance(resilience, Mapping):
            resilience_policy = ResiliencePolicy(
                timeout_seconds=int(resilience.get("timeout_seconds", 60)),
                max_retries=int(resilience.get("max_retries", 2)),
            )
        else:
            raise ValueError("llm service resilience must be an object")

        return cls(
            provider=str(data.get("provider", "openai")),
            model=str(data.get("model", "gpt-4")),
            api_key=cast(str | None, data.get("api_key")),
            api_base=cast(str | None, data.get("api_base")),
            resilience=resilience_policy,
        )


@dataclass(frozen=True)
class LLMPoolConfig:
    default_service: str
    services: dict[str, LLMServiceConfig]


@dataclass(frozen=True)
class EmbeddingServiceConfig:
    provider: str = "openai"
    model: str = "text-embedding-3-small"
    api_key: str | None = None
    api_base: str | None = None
    resilience: ResiliencePolicy = field(default_factory=ResiliencePolicy)

    def __post_init__(self) -> None:
        if not self.provider:
            raise ValueError("embedding service provider must be non-empty")
        if not self.model:
            raise ValueError("embedding service model must be non-empty")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> EmbeddingServiceConfig:
        resilience = data.get("resilience", {})
        if isinstance(resilience, ResiliencePolicy):
            resilience_policy = resilience
        elif isinstance(resilience, Mapping):
            resilience_policy = ResiliencePolicy(
                timeout_seconds=int(resilience.get("timeout_seconds", 60)),
                max_retries=int(resilience.get("max_retries", 2)),
            )
        else:
            raise ValueError("embedding service resilience must be an object")

        return cls(
            provider=str(data.get("provider", "openai")),
            model=str(data.get("model", "text-embedding-3-small")),
            api_key=cast(str | None, data.get("api_key")),
            api_base=cast(str | None, data.get("api_base")),
            resilience=resilience_policy,
        )


@dataclass(frozen=True)
class EmbeddingPoolConfig:
    default_service: str
    services: dict[str, EmbeddingServiceConfig]


@dataclass(frozen=True)
class PromptingConfig:
    base_system_prompt: str | None = None


@dataclass(frozen=True)
class TranscriptConfig:
    enabled: bool = False
    backend: Literal["sqlite"] = "sqlite"
    path: str = "transcript.db"
    capture_context_log: bool = True

    def __post_init__(self) -> None:
        if self.backend != "sqlite":
            raise ValueError("transcript.backend must be 'sqlite'")
        if not self.path:
            raise ValueError("transcript.path must be non-empty")


@dataclass(frozen=True)
class MemoryRecallPolicy:
    semantic_retrieval_enabled: bool = True


@dataclass(frozen=True)
class MemoryExtractionPolicy:
    enabled: bool = True
    llm_service: str | None = None
    embedding_service: str | None = None
    max_tokens: int | None = None
    rejection_log: str | None = None
    user_name: str = "User"
    assistant_name: str = "Assistant"
    prompt: str | None = None
    ontology: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("memory.extraction.max_tokens must be > 0")


@dataclass
class RuntimeConfig:
    """
    Configuration for the Friday Runtime Kernel.

    The flat fields remain available for compatibility. Nested Phase 4 sections
    are exposed through computed properties and the `from_yaml` / `from_sources`
    helpers.
    """

    # Phase 4 policy fields
    allow_env_override: bool = False
    strict_agent_llm_binding: bool = False
    workflow_mode: Literal["canonical", "legacy", "auto"] = "canonical"
    unknown_key_policy: Literal["fail"] = "fail"

    # LLM Configuration
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"
    llm_api_key: str | None = None
    llm_api_base: str | None = None
    llm_pool_default_service: str = "default"
    llm_pool_services: dict[str, LLMServiceConfig] = field(default_factory=dict)

    # Embedding Configuration
    embedding_model: str = "text-embedding-3-small"
    embedding_pool_default_service: str = "default"
    embedding_pool_services: dict[str, EmbeddingServiceConfig] = field(
        default_factory=dict
    )

    # Prompting Configuration
    prompting_base_system_prompt: str | None = None

    # Memory Configuration
    chroma_path: str = ".friday/chroma"
    chroma_collection: str = "friday_memory"
    memory_mode: str = "single_agent"
    memory_recall_semantic_retrieval_enabled: bool = True
    memory_extraction_enabled: bool = True
    memory_extraction_llm_service: str | None = None
    memory_extraction_embedding_service: str | None = None
    memory_extraction_max_tokens: int | None = None
    memory_extraction_rejection_log: str | None = None
    memory_extraction_user_name: str = "User"
    memory_extraction_assistant_name: str = "Assistant"
    memory_extraction_prompt: str | None = None
    memory_extraction_ontology: dict[str, Any] | None = None

    # Telemetry Configuration
    telemetry_enabled: bool = False
    telemetry_endpoint: str | None = None
    debug_mode: bool = False

    # Agent Configuration
    agents_dir: str | None = None
    agents_role_bindings: dict[str, str] = field(default_factory=dict)
    workflows_dir: str | None = None
    tools_config: ToolsConfig = field(default_factory=ToolsConfig)

    # Transcript Configuration
    transcript_enabled: bool = False
    transcript_backend: Literal["sqlite"] = "sqlite"
    transcript_path: str = "transcript.db"
    transcript_capture_context_log: bool = True

    # Runtime filesystem topology
    deployment_profile: Literal["local", "container", "cloud"] = "local"
    install_root: str | None = None
    runtime_data_root: str | None = None
    workspace_root: str | None = None
    cache_root: str | None = None

    # Scratch configuration
    scratch_backend: str = "in_memory"
    scratch_path: str | None = None

    # Artifact policy
    artifacts_enabled: bool = True
    artifacts_root_dir: str = "artifacts"
    artifacts_lineage_required: bool = True
    artifacts_publish_on_task_success: bool = True

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
        if self.workflow_mode not in {"canonical", "legacy", "auto"}:
            raise ValueError("workflow_mode must be 'canonical', 'legacy', or 'auto'")
        if self.unknown_key_policy != "fail":
            raise ValueError("unknown_key_policy must be 'fail' in Phase 4")
        if self.transcript_backend != "sqlite":
            raise ValueError("transcript.backend must be 'sqlite'")
        if not self.transcript_path:
            raise ValueError("transcript.path must be non-empty")

        defaults = self.deployment_profile_defaults(self.deployment_profile)
        if self.install_root is None:
            self.install_root = defaults["install_root"]
        if self.runtime_data_root is None:
            self.runtime_data_root = defaults["runtime_data_root"]
        if self.workspace_root is None:
            self.workspace_root = defaults["workspace_root"]

        self.agents_role_bindings = dict(self.agents_role_bindings)
        if isinstance(self.tools_config, Mapping):
            self.tools_config = ToolsConfig.from_dict(self.tools_config)
        elif not isinstance(self.tools_config, ToolsConfig):
            raise ValueError("tools_config must be a ToolsConfig object")
        self.llm_pool_services = {
            name: self._coerce_service_config(service)
            for name, service in self.llm_pool_services.items()
        }
        if not self.llm_pool_services:
            self.llm_pool_services = {
                self.llm_pool_default_service: LLMServiceConfig(
                    provider=self.llm_provider,
                    model=self.llm_model,
                    api_key=self.llm_api_key,
                    api_base=self.llm_api_base,
                )
            }

        if self.llm_pool_default_service not in self.llm_pool_services:
            raise ValueError("llm_pool.default_service must reference a configured service")

        self.embedding_pool_services = {
            name: self._coerce_embedding_service_config(service)
            for name, service in self.embedding_pool_services.items()
        }
        if not self.embedding_pool_services:
            default_llm_service = self.get_llm_service_config()
            self.embedding_pool_services = {
                self.embedding_pool_default_service: EmbeddingServiceConfig(
                    provider=default_llm_service.provider,
                    model=self.embedding_model,
                    api_key=default_llm_service.api_key,
                    api_base=default_llm_service.api_base,
                )
            }

        if self.embedding_pool_default_service not in self.embedding_pool_services:
            raise ValueError(
                "embedding_pool.default_service must reference a configured service"
            )

        self.embedding_model = self.get_embedding_service_config().model

        if self.memory_extraction_llm_service is None:
            self.memory_extraction_llm_service = self.llm_pool_default_service

        if self.memory_extraction_max_tokens is not None and self.memory_extraction_max_tokens <= 0:
            raise ValueError("memory.extraction.max_tokens must be > 0")
        if not self.memory_extraction_user_name:
            raise ValueError("memory.extraction.user_name must be non-empty")
        if not self.memory_extraction_assistant_name:
            raise ValueError("memory.extraction.assistant_name must be non-empty")
        if self.memory_extraction_llm_service not in self.llm_pool_services:
            raise ValueError("memory.extraction.llm_service must reference a configured service")
        if (
            self.memory_extraction_embedding_service is not None
            and self.memory_extraction_embedding_service not in self.embedding_pool_services
        ):
            raise ValueError(
                "memory.extraction.embedding_service must reference a configured service"
            )

        self.validate_runtime_roots()
        self.validate_scratch_path()
        self.validate_artifacts_policy()
        self.validate_transcript_path()

    @staticmethod
    def _coerce_service_config(value: LLMServiceConfig | Mapping[str, Any]) -> LLMServiceConfig:
        if isinstance(value, LLMServiceConfig):
            return value
        if isinstance(value, Mapping):
            return LLMServiceConfig.from_dict(value)
        raise ValueError("llm_pool.services entries must be objects")

    @staticmethod
    def _coerce_embedding_service_config(
        value: EmbeddingServiceConfig | Mapping[str, Any]
    ) -> EmbeddingServiceConfig:
        if isinstance(value, EmbeddingServiceConfig):
            return value
        if isinstance(value, Mapping):
            return EmbeddingServiceConfig.from_dict(value)
        raise ValueError("embedding_pool.services entries must be objects")

    @staticmethod
    def _resolve(path_value: str) -> Path:
        return Path(path_value).expanduser().resolve()

    @property
    def config_policy(self) -> ConfigPolicy:
        return ConfigPolicy(
            allow_env_override=self.allow_env_override,
            strict_agent_llm_binding=self.strict_agent_llm_binding,
            workflow_mode=self.workflow_mode,
            unknown_key_policy=self.unknown_key_policy,
        )

    @property
    def runtime_paths(self) -> RuntimePaths:
        assert self.install_root is not None
        assert self.runtime_data_root is not None
        assert self.workspace_root is not None
        return RuntimePaths(
            install_root=self.install_root,
            runtime_data_root=self.runtime_data_root,
            workspace_root=self.workspace_root,
            cache_root=self.cache_root,
        )

    @property
    def artifacts(self) -> ArtifactPolicy:
        return ArtifactPolicy(
            enabled=self.artifacts_enabled,
            root_dir=self.artifacts_root_dir,
            lineage_required=self.artifacts_lineage_required,
            publish_on_task_success=self.artifacts_publish_on_task_success,
        )

    @property
    def agents(self) -> AgentsConfig:
        return AgentsConfig(
            dir=self.agents_dir,
            role_bindings=dict(self.agents_role_bindings),
        )

    @property
    def workflows(self) -> WorkflowsConfig:
        return WorkflowsConfig(dir=self.workflows_dir)

    @property
    def tools(self) -> ToolsConfig:
        return self.tools_config

    @property
    def llm_pool(self) -> LLMPoolConfig:
        return LLMPoolConfig(
            default_service=self.llm_pool_default_service,
            services=dict(self.llm_pool_services),
        )

    @property
    def embedding_pool(self) -> EmbeddingPoolConfig:
        return EmbeddingPoolConfig(
            default_service=self.embedding_pool_default_service,
            services=dict(self.embedding_pool_services),
        )

    @property
    def prompting(self) -> PromptingConfig:
        return PromptingConfig(
            base_system_prompt=self.prompting_base_system_prompt,
        )

    @property
    def memory_recall(self) -> MemoryRecallPolicy:
        return MemoryRecallPolicy(
            semantic_retrieval_enabled=self.memory_recall_semantic_retrieval_enabled
        )

    @property
    def memory_extraction(self) -> MemoryExtractionPolicy:
        return MemoryExtractionPolicy(
            enabled=self.memory_extraction_enabled,
            llm_service=self.memory_extraction_llm_service,
            embedding_service=self.memory_extraction_embedding_service,
            max_tokens=self.memory_extraction_max_tokens,
            rejection_log=self.memory_extraction_rejection_log,
            user_name=self.memory_extraction_user_name,
            assistant_name=self.memory_extraction_assistant_name,
            prompt=self.memory_extraction_prompt,
            ontology=self.memory_extraction_ontology,
        )

    @property
    def transcript(self) -> TranscriptConfig:
        return TranscriptConfig(
            enabled=self.transcript_enabled,
            backend=self.transcript_backend,
            path=self.transcript_path,
            capture_context_log=self.transcript_capture_context_log,
        )

    def get_llm_service_config(self, service_name: str | None = None) -> LLMServiceConfig:
        selected = service_name or self.llm_pool_default_service
        try:
            return self.llm_pool_services[selected]
        except KeyError as exc:
            raise ValueError(f"Unknown llm service: {selected}") from exc

    def get_embedding_service_config(
        self,
        service_name: str | None = None,
    ) -> EmbeddingServiceConfig:
        selected = service_name or self.embedding_pool_default_service
        try:
            return self.embedding_pool_services[selected]
        except KeyError as exc:
            raise ValueError(f"Unknown embedding service: {selected}") from exc

    def validate_runtime_roots(self) -> None:
        """
        Validate runtime root topology.

        Rules:
        - runtime_data_root and workspace_root cannot overlap.
        - runtime_data_root parent must be writable.
        """
        assert self.install_root is not None
        assert self.runtime_data_root is not None
        assert self.workspace_root is not None

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
        runtime_data_root = self._resolve(cast(str, self.runtime_data_root))
        workspace_root = self._resolve(cast(str, self.workspace_root))

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

    def validate_artifacts_policy(self) -> None:
        """Validate runtime artifact policy fields and root path placement."""
        self.resolve_artifacts_root_path(self.artifacts_root_dir)

    def validate_transcript_path(self) -> None:
        """Validate transcript path placement when transcript persistence is enabled."""
        if not self.transcript_enabled:
            return

        self.resolve_transcript_path(self.transcript_path)

    def resolve_artifacts_root_path(self, path_value: str) -> Path:
        """
        Resolve runtime artifact-root path under runtime_data_root.
        """
        runtime_data_root = self._resolve(cast(str, self.runtime_data_root))
        workspace_root = self._resolve(cast(str, self.workspace_root))
        raw = Path(path_value).expanduser()
        resolved = (
            (runtime_data_root / raw).resolve() if not raw.is_absolute() else raw.resolve()
        )
        if runtime_data_root not in resolved.parents and resolved != runtime_data_root:
            raise ValueError("artifacts.root_dir must be under runtime_data_root")
        if workspace_root in resolved.parents or resolved == workspace_root:
            raise ValueError("artifacts.root_dir must not be under workspace_root")
        return resolved

    def resolve_transcript_path(self, path_value: str) -> Path:
        """Resolve transcript storage path under runtime_data_root."""
        runtime_data_root = self._resolve(cast(str, self.runtime_data_root))
        workspace_root = self._resolve(cast(str, self.workspace_root))
        raw = Path(path_value).expanduser()
        resolved = (
            (runtime_data_root / raw).resolve() if not raw.is_absolute() else raw.resolve()
        )
        if runtime_data_root not in resolved.parents and resolved != runtime_data_root:
            raise ValueError("transcript.path must be under runtime_data_root")
        if workspace_root in resolved.parents or resolved == workspace_root:
            raise ValueError("transcript.path must not be under workspace_root")
        return resolved

    @classmethod
    def from_env(cls) -> RuntimeConfig:
        """Create configuration from environment variables."""
        return cls.from_sources()

    @classmethod
    def from_yaml(cls, path: str | Path) -> RuntimeConfig:
        """Create configuration from YAML with default precedence rules."""
        return cls.from_sources(yaml_path=path)

    @classmethod
    def from_sources(
        cls,
        *,
        yaml_path: str | Path | None = None,
        env: Mapping[str, str] | None = None,
        overrides: Mapping[str, Any] | None = None,
    ) -> RuntimeConfig:
        """
        Build config using Phase 4 precedence:
        defaults -> YAML -> env (if allowed or env-only) -> explicit overrides.
        """
        env_map = env if env is not None else os.environ
        merged = cls._default_source_data()

        if yaml_path is not None:
            yaml_data = cls._load_yaml(pathlib_path=Path(yaml_path))
            cls._deep_merge(merged, yaml_data)

        allow_env = yaml_path is None or bool(
            merged["config_policy"]["allow_env_override"]
        )
        if allow_env:
            cls._deep_merge(merged, cls._env_source_data(env_map))

        if overrides:
            cls._apply_flat_overrides(merged, overrides)

        return cls(**cls._nested_to_flat_kwargs(merged))

    @classmethod
    def _default_source_data(cls) -> dict[str, Any]:
        profile: Literal["local", "container", "cloud"] = "local"
        defaults = cls.deployment_profile_defaults(profile)
        return {
            "deployment_profile": profile,
            "config_policy": {
                "allow_env_override": False,
                "strict_agent_llm_binding": False,
                "workflow_mode": "canonical",
                "unknown_key_policy": "fail",
            },
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
                "api_key": None,
                "api_base": None,
            },
            "llm_pool": {
                "default_service": "default",
                "services": {
                    "default": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "api_key": None,
                        "api_base": None,
                        "resilience": {
                            "timeout_seconds": 60,
                            "max_retries": 2,
                        },
                    }
                },
            },
            "embedding_pool": {
                "default_service": "default",
                "services": {},
            },
            "embedding": {
                "model": "text-embedding-3-small",
            },
            "prompting": {
                "base_system_prompt": None,
            },
            "memory": {
                "mode": "single_agent",
                "chroma_path": ".friday/chroma",
                "chroma_collection": "friday_memory",
                "recall": {
                    "semantic_retrieval_enabled": True,
                },
                "extraction": {
                    "enabled": True,
                    "llm_service": "default",
                    "embedding_service": None,
                    "max_tokens": None,
                    "rejection_log": None,
                    "user_name": "User",
                    "assistant_name": "Assistant",
                    "prompt": None,
                    "ontology": None,
                },
            },
            "telemetry": {
                "enabled": False,
                "endpoint": None,
                "debug_mode": False,
            },
            "agents": {
                "dir": None,
                "role_bindings": {},
            },
            "workflows": {
                "dir": None,
            },
            "tools": {
                "providers": {
                    "builtin": {
                        "enabled": True,
                        "mode": "all",
                        "include_categories": [],
                        "exclude_categories": [],
                        "include_tools": [],
                        "exclude_tools": [],
                    },
                    "friday_tools": {
                        "enabled": False,
                        "mode": "all",
                        "include_categories": [],
                        "exclude_categories": [],
                        "include_tools": [],
                        "exclude_tools": [],
                    },
                    "mcp": {
                        "enabled": False,
                        "mode": "all",
                        "include_categories": [],
                        "exclude_categories": [],
                        "include_tools": [],
                        "exclude_tools": [],
                        "config": {
                            "servers": [],
                            "server": None,
                            "auto_connect": True,
                            "tool_name_prefix": "mcp_",
                        },
                    },
                }
            },
            "transcript": {
                "enabled": False,
                "backend": "sqlite",
                "path": "transcript.db",
                "capture_context_log": True,
            },
            "runtime_paths": {
                "install_root": defaults["install_root"],
                "runtime_data_root": defaults["runtime_data_root"],
                "workspace_root": defaults["workspace_root"],
                "cache_root": None,
            },
            "scratch": {
                "backend": "in_memory",
                "path": None,
            },
            "artifacts": {
                "enabled": True,
                "root_dir": "artifacts",
                "lineage_required": True,
                "publish_on_task_success": True,
            },
        }

    @classmethod
    def _env_source_data(cls, env: Mapping[str, str]) -> dict[str, Any]:
        data: dict[str, Any] = {}

        profile = env.get("FRIDAY_DEPLOYMENT_PROFILE")
        if profile in {"local", "container", "cloud"}:
            profile_defaults = cls.deployment_profile_defaults(
                cast(Literal["local", "container", "cloud"], profile)
            )
            data["deployment_profile"] = profile
            data["runtime_paths"] = {
                "install_root": profile_defaults["install_root"],
                "runtime_data_root": profile_defaults["runtime_data_root"],
                "workspace_root": profile_defaults["workspace_root"],
            }

        mappings: tuple[tuple[str, tuple[str, ...], Any], ...] = (
            ("FRIDAY_ALLOW_ENV_OVERRIDE", ("config_policy", "allow_env_override"), _coerce_bool),
            (
                "FRIDAY_STRICT_AGENT_LLM_BINDING",
                ("config_policy", "strict_agent_llm_binding"),
                _coerce_bool,
            ),
            ("FRIDAY_WORKFLOW_MODE", ("config_policy", "workflow_mode"), str),
            ("FRIDAY_UNKNOWN_KEY_POLICY", ("config_policy", "unknown_key_policy"), str),
            ("FRIDAY_LLM_PROVIDER", ("llm", "provider"), str),
            ("FRIDAY_LLM_MODEL", ("llm", "model"), str),
            ("OPENAI_API_KEY", ("llm", "api_key"), str),
            ("FRIDAY_LLM_API_BASE", ("llm", "api_base"), str),
            ("FRIDAY_EMBEDDING_MODEL", ("embedding", "model"), str),
            ("FRIDAY_BASE_SYSTEM_PROMPT", ("prompting", "base_system_prompt"), str),
            ("FRIDAY_CHROMA_PATH", ("memory", "chroma_path"), str),
            ("FRIDAY_CHROMA_COLLECTION", ("memory", "chroma_collection"), str),
            ("FRIDAY_MEMORY_MODE", ("memory", "mode"), str),
            (
                "FRIDAY_MEMORY_SEMANTIC_RETRIEVAL_ENABLED",
                ("memory", "recall", "semantic_retrieval_enabled"),
                _coerce_bool,
            ),
            (
                "FRIDAY_MEMORY_EXTRACTION_ENABLED",
                ("memory", "extraction", "enabled"),
                _coerce_bool,
            ),
            (
                "FRIDAY_MEMORY_EXTRACTION_LLM_SERVICE",
                ("memory", "extraction", "llm_service"),
                str,
            ),
            (
                "FRIDAY_MEMORY_EXTRACTION_EMBEDDING_SERVICE",
                ("memory", "extraction", "embedding_service"),
                str,
            ),
            (
                "FRIDAY_MEMORY_EXTRACTION_MAX_TOKENS",
                ("memory", "extraction", "max_tokens"),
                int,
            ),
            (
                "FRIDAY_MEMORY_EXTRACTION_REJECTION_LOG",
                ("memory", "extraction", "rejection_log"),
                str,
            ),
            (
                "FRIDAY_MEMORY_EXTRACTION_USER_NAME",
                ("memory", "extraction", "user_name"),
                str,
            ),
            (
                "FRIDAY_MEMORY_EXTRACTION_ASSISTANT_NAME",
                ("memory", "extraction", "assistant_name"),
                str,
            ),
            ("FRIDAY_TELEMETRY_ENABLED", ("telemetry", "enabled"), _coerce_bool),
            ("FRIDAY_OTEL_ENDPOINT", ("telemetry", "endpoint"), str),
            ("FRIDAY_DEBUG", ("telemetry", "debug_mode"), _coerce_bool),
            ("FRIDAY_AGENTS_DIR", ("agents", "dir"), str),
            ("FRIDAY_TRANSCRIPT_ENABLED", ("transcript", "enabled"), _coerce_bool),
            ("FRIDAY_TRANSCRIPT_BACKEND", ("transcript", "backend"), str),
            ("FRIDAY_TRANSCRIPT_PATH", ("transcript", "path"), str),
            (
                "FRIDAY_TRANSCRIPT_CAPTURE_CONTEXT_LOG",
                ("transcript", "capture_context_log"),
                _coerce_bool,
            ),
            ("FRIDAY_INSTALL_ROOT", ("runtime_paths", "install_root"), str),
            ("FRIDAY_RUNTIME_DATA_ROOT", ("runtime_paths", "runtime_data_root"), str),
            ("FRIDAY_WORKSPACE_ROOT", ("runtime_paths", "workspace_root"), str),
            ("FRIDAY_CACHE_ROOT", ("runtime_paths", "cache_root"), str),
            ("FRIDAY_SCRATCH_BACKEND", ("scratch", "backend"), str),
            ("FRIDAY_SCRATCH_PATH", ("scratch", "path"), str),
            ("FRIDAY_ARTIFACTS_ENABLED", ("artifacts", "enabled"), _coerce_bool),
            ("FRIDAY_ARTIFACTS_ROOT_DIR", ("artifacts", "root_dir"), str),
            (
                "FRIDAY_ARTIFACTS_LINEAGE_REQUIRED",
                ("artifacts", "lineage_required"),
                _coerce_bool,
            ),
            (
                "FRIDAY_ARTIFACTS_PUBLISH_ON_TASK_SUCCESS",
                ("artifacts", "publish_on_task_success"),
                _coerce_bool,
            ),
        )

        for env_name, path, coercer in mappings:
            raw_value = env.get(env_name)
            if raw_value is None:
                continue
            cls._set_nested(data, path, coercer(raw_value))

        llm_section = cast(dict[str, Any], data.setdefault("llm", {}))
        llm_pool = cast(dict[str, Any], data.setdefault("llm_pool", {}))
        llm_pool.setdefault("default_service", "default")
        services = cast(dict[str, Any], llm_pool.setdefault("services", {}))
        default_service = cast(dict[str, Any], services.setdefault("default", {}))
        if "provider" in llm_section:
            default_service["provider"] = llm_section["provider"]
        if "model" in llm_section:
            default_service["model"] = llm_section["model"]
        if "api_key" in llm_section:
            default_service["api_key"] = llm_section["api_key"]
        if "api_base" in llm_section:
            default_service["api_base"] = llm_section["api_base"]
        default_service.setdefault(
            "resilience",
            {"timeout_seconds": 60, "max_retries": 2},
        )

        embedding_section = cast(dict[str, Any], data.setdefault("embedding", {}))
        embedding_pool = cast(dict[str, Any], data.setdefault("embedding_pool", {}))
        embedding_pool.setdefault("default_service", "default")
        embedding_services = cast(
            dict[str, Any], embedding_pool.setdefault("services", {})
        )
        default_embedding_service = cast(
            dict[str, Any], embedding_services.setdefault("default", {})
        )
        if "model" in embedding_section:
            default_embedding_service["model"] = embedding_section["model"]
        default_embedding_service.setdefault("provider", "openai")
        default_embedding_service.setdefault("api_key", llm_section.get("api_key"))
        default_embedding_service.setdefault("api_base", llm_section.get("api_base"))
        default_embedding_service.setdefault(
            "resilience",
            {"timeout_seconds": 60, "max_retries": 2},
        )

        return data

    @classmethod
    def _load_yaml(cls, pathlib_path: Path) -> dict[str, Any]:
        try:
            with open(pathlib_path, encoding="utf-8") as handle:
                payload = yaml.safe_load(handle) or {}
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid runtime YAML: {exc}") from exc
        except OSError as exc:
            raise ValueError(f"Unable to read runtime YAML: {exc}") from exc

        if not isinstance(payload, dict):
            raise ValueError("Runtime YAML must be a mapping")

        cls._validate_yaml_keys(payload)
        return payload

    @classmethod
    def _validate_yaml_keys(cls, payload: Mapping[str, Any]) -> None:
        allowed_top_level = {
            "llm_pool",
            "llm",
            "embedding_pool",
            "embedding",
            "prompting",
            "memory",
            "telemetry",
            "agents",
            "workflows",
            "tools",
            "transcript",
            "runtime_paths",
            "scratch",
            "artifacts",
            "config_policy",
        }
        unknown_top = set(payload) - allowed_top_level
        if unknown_top:
            raise ValueError(f"Unknown runtime config keys: {sorted(unknown_top)}")

        section_keys: dict[str, set[str]] = {
            "llm": {"provider", "model", "api_key", "api_base"},
            "embedding": {"model"},
            "prompting": {"base_system_prompt"},
            "memory": {
                "mode",
                "chroma_path",
                "chroma_collection",
                "recall",
                "extraction",
            },
            "telemetry": {"enabled", "endpoint", "debug_mode"},
            "agents": {"dir", "role_bindings"},
            "workflows": {"dir"},
            "tools": {"providers"},
            "transcript": {"enabled", "backend", "path", "capture_context_log"},
            "runtime_paths": {
                "install_root",
                "runtime_data_root",
                "workspace_root",
                "cache_root",
            },
            "scratch": {"backend", "path"},
            "artifacts": {
                "enabled",
                "root_dir",
                "lineage_required",
                "publish_on_task_success",
            },
            "config_policy": {
                "allow_env_override",
                "strict_agent_llm_binding",
                "workflow_mode",
                "unknown_key_policy",
            },
            "llm_pool": {"default_service", "services"},
            "embedding_pool": {"default_service", "services"},
        }

        for section_name, allowed in section_keys.items():
            section = payload.get(section_name)
            if section is None:
                continue
            if not isinstance(section, dict):
                raise ValueError(f"Runtime config section '{section_name}' must be an object")
            unknown = set(section) - allowed
            if unknown:
                raise ValueError(
                    f"Unknown keys in runtime config section '{section_name}': {sorted(unknown)}"
                )

        agents = payload.get("agents", {})
        if isinstance(agents, dict) and "role_bindings" in agents:
            role_bindings = agents["role_bindings"]
            if not isinstance(role_bindings, dict):
                raise ValueError("agents.role_bindings must be an object")

        tools = payload.get("tools", {})
        if isinstance(tools, dict):
            providers = tools.get("providers")
            if providers is not None:
                if not isinstance(providers, dict):
                    raise ValueError("tools.providers must be an object")
                allowed_provider_names = {"builtin", "friday_tools", "mcp"}
                unknown_provider_names = set(providers) - allowed_provider_names
                if unknown_provider_names:
                    raise ValueError(
                        "Unknown tool providers in runtime config: "
                        f"{sorted(unknown_provider_names)}"
                    )
                allowed_provider_keys = {
                    "enabled",
                    "mode",
                    "include_categories",
                    "exclude_categories",
                    "include_tools",
                    "exclude_tools",
                    "config",
                }
                for provider_name, provider_config in providers.items():
                    if not isinstance(provider_config, dict):
                        raise ValueError(
                            f"tools.providers.{provider_name} must be an object"
                        )
                    unknown_provider_keys = set(provider_config) - allowed_provider_keys
                    if unknown_provider_keys:
                        raise ValueError(
                            "Unknown keys in runtime config section "
                            f"'tools.providers.{provider_name}': "
                            f"{sorted(unknown_provider_keys)}"
                        )
                    for list_key in (
                        "include_categories",
                        "exclude_categories",
                        "include_tools",
                        "exclude_tools",
                    ):
                        list_value = provider_config.get(list_key)
                        if list_value is not None and not isinstance(list_value, list):
                            raise ValueError(
                                f"tools.providers.{provider_name}.{list_key} "
                                "must be a list"
                            )
                    config_value = provider_config.get("config")
                    if config_value is not None and provider_name != "mcp":
                        raise ValueError(
                            f"tools.providers.{provider_name}.config is only valid for mcp"
                        )
                    if provider_name == "mcp" and config_value is not None and not isinstance(
                        config_value, dict
                    ):
                        raise ValueError("tools.providers.mcp.config must be an object")

        transcript = payload.get("transcript", {})
        if isinstance(transcript, dict):
            backend = transcript.get("backend")
            if backend is not None and backend != "sqlite":
                raise ValueError("transcript.backend must be 'sqlite'")
            path_value = transcript.get("path")
            if path_value is not None and not isinstance(path_value, str):
                raise ValueError("transcript.path must be a string")

        llm_pool = payload.get("llm_pool", {})
        if isinstance(llm_pool, dict) and "services" in llm_pool:
            services = llm_pool["services"]
            if not isinstance(services, dict):
                raise ValueError("llm_pool.services must be an object")
            allowed_service_keys = {"provider", "model", "api_key", "api_base", "resilience"}
            allowed_resilience_keys = {"timeout_seconds", "max_retries"}
            for service_name, config in services.items():
                if not isinstance(config, dict):
                    raise ValueError(f"llm_pool.services.{service_name} must be an object")
                unknown_service = set(config) - allowed_service_keys
                if unknown_service:
                    raise ValueError(
                        f"Unknown keys in llm_pool.services.{service_name}: {sorted(unknown_service)}"
                    )
                resilience = config.get("resilience", {})
                if resilience is not None:
                    if not isinstance(resilience, dict):
                        raise ValueError(
                            f"llm_pool.services.{service_name}.resilience must be an object"
                        )
                    unknown_resilience = set(resilience) - allowed_resilience_keys
                    if unknown_resilience:
                        raise ValueError(
                            "Unknown keys in "
                            f"llm_pool.services.{service_name}.resilience: "
                            f"{sorted(unknown_resilience)}"
                        )

        embedding_pool = payload.get("embedding_pool", {})
        if isinstance(embedding_pool, dict) and "services" in embedding_pool:
            services = embedding_pool["services"]
            if not isinstance(services, dict):
                raise ValueError("embedding_pool.services must be an object")
            allowed_service_keys = {"provider", "model", "api_key", "api_base", "resilience"}
            allowed_resilience_keys = {"timeout_seconds", "max_retries"}
            for service_name, config in services.items():
                if not isinstance(config, dict):
                    raise ValueError(
                        f"embedding_pool.services.{service_name} must be an object"
                    )
                unknown_service = set(config) - allowed_service_keys
                if unknown_service:
                    raise ValueError(
                        "Unknown keys in "
                        f"embedding_pool.services.{service_name}: {sorted(unknown_service)}"
                    )
                resilience = config.get("resilience", {})
                if resilience is not None:
                    if not isinstance(resilience, dict):
                        raise ValueError(
                            "embedding_pool.services."
                            f"{service_name}.resilience must be an object"
                        )
                    unknown_resilience = set(resilience) - allowed_resilience_keys
                    if unknown_resilience:
                        raise ValueError(
                            "Unknown keys in "
                            f"embedding_pool.services.{service_name}.resilience: "
                            f"{sorted(unknown_resilience)}"
                        )

        memory = payload.get("memory", {})
        if isinstance(memory, dict):
            recall = memory.get("recall")
            if recall is not None:
                if not isinstance(recall, dict):
                    raise ValueError("memory.recall must be an object")
                unknown_recall = set(recall) - {"semantic_retrieval_enabled"}
                if unknown_recall:
                    raise ValueError(
                        f"Unknown keys in runtime config section 'memory.recall': {sorted(unknown_recall)}"
                    )

            extraction = memory.get("extraction")
            if extraction is not None:
                if not isinstance(extraction, dict):
                    raise ValueError("memory.extraction must be an object")
                allowed_extraction = {
                    "enabled",
                    "llm_service",
                    "embedding_service",
                    "max_tokens",
                    "rejection_log",
                    "user_name",
                    "assistant_name",
                    "prompt",
                    "ontology",
                }
                unknown_extraction = set(extraction) - allowed_extraction
                if unknown_extraction:
                    raise ValueError(
                        "Unknown keys in runtime config section 'memory.extraction': "
                        f"{sorted(unknown_extraction)}"
                    )
                ontology = extraction.get("ontology")
                if ontology is not None and not isinstance(ontology, dict):
                    raise ValueError("memory.extraction.ontology must be an object")

    @classmethod
    def _set_nested(
        cls,
        target: dict[str, Any],
        path: tuple[str, ...],
        value: Any,
    ) -> None:
        current = target
        for key in path[:-1]:
            current = cast(dict[str, Any], current.setdefault(key, {}))
        current[path[-1]] = value

    @classmethod
    def _deep_merge(cls, target: dict[str, Any], source: Mapping[str, Any]) -> None:
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, Mapping)
            ):
                cls._deep_merge(cast(dict[str, Any], target[key]), value)
            else:
                target[key] = value

    @classmethod
    def _apply_flat_overrides(
        cls,
        merged: dict[str, Any],
        overrides: Mapping[str, Any],
    ) -> None:
        mapping: dict[str, tuple[str, ...]] = {
            "allow_env_override": ("config_policy", "allow_env_override"),
            "strict_agent_llm_binding": ("config_policy", "strict_agent_llm_binding"),
            "workflow_mode": ("config_policy", "workflow_mode"),
            "unknown_key_policy": ("config_policy", "unknown_key_policy"),
            "llm_provider": ("llm", "provider"),
            "llm_model": ("llm", "model"),
            "llm_api_key": ("llm", "api_key"),
            "llm_api_base": ("llm", "api_base"),
            "llm_pool_default_service": ("llm_pool", "default_service"),
            "llm_pool_services": ("llm_pool", "services"),
            "embedding_pool_default_service": ("embedding_pool", "default_service"),
            "embedding_pool_services": ("embedding_pool", "services"),
            "embedding_model": ("embedding", "model"),
            "prompting_base_system_prompt": ("prompting", "base_system_prompt"),
            "chroma_path": ("memory", "chroma_path"),
            "chroma_collection": ("memory", "chroma_collection"),
            "memory_mode": ("memory", "mode"),
            "memory_recall_semantic_retrieval_enabled": (
                "memory",
                "recall",
                "semantic_retrieval_enabled",
            ),
            "memory_extraction_enabled": ("memory", "extraction", "enabled"),
            "memory_extraction_llm_service": (
                "memory",
                "extraction",
                "llm_service",
            ),
            "memory_extraction_embedding_service": (
                "memory",
                "extraction",
                "embedding_service",
            ),
            "memory_extraction_max_tokens": (
                "memory",
                "extraction",
                "max_tokens",
            ),
            "memory_extraction_rejection_log": (
                "memory",
                "extraction",
                "rejection_log",
            ),
            "memory_extraction_user_name": (
                "memory",
                "extraction",
                "user_name",
            ),
            "memory_extraction_assistant_name": (
                "memory",
                "extraction",
                "assistant_name",
            ),
            "memory_extraction_prompt": ("memory", "extraction", "prompt"),
            "memory_extraction_ontology": ("memory", "extraction", "ontology"),
            "telemetry_enabled": ("telemetry", "enabled"),
            "telemetry_endpoint": ("telemetry", "endpoint"),
            "debug_mode": ("telemetry", "debug_mode"),
            "agents_dir": ("agents", "dir"),
            "agents_role_bindings": ("agents", "role_bindings"),
            "workflows_dir": ("workflows", "dir"),
            "tools_config": ("tools",),
            "transcript_enabled": ("transcript", "enabled"),
            "transcript_backend": ("transcript", "backend"),
            "transcript_path": ("transcript", "path"),
            "transcript_capture_context_log": (
                "transcript",
                "capture_context_log",
            ),
            "deployment_profile": ("deployment_profile",),
            "install_root": ("runtime_paths", "install_root"),
            "runtime_data_root": ("runtime_paths", "runtime_data_root"),
            "workspace_root": ("runtime_paths", "workspace_root"),
            "cache_root": ("runtime_paths", "cache_root"),
            "scratch_backend": ("scratch", "backend"),
            "scratch_path": ("scratch", "path"),
            "artifacts_enabled": ("artifacts", "enabled"),
            "artifacts_root_dir": ("artifacts", "root_dir"),
            "artifacts_lineage_required": ("artifacts", "lineage_required"),
            "artifacts_publish_on_task_success": (
                "artifacts",
                "publish_on_task_success",
            ),
        }
        for key, value in overrides.items():
            path = mapping.get(key)
            if path is None:
                raise ValueError(f"Unknown RuntimeConfig override: {key}")
            cls._set_nested(merged, path, value)

    @classmethod
    def _nested_to_flat_kwargs(cls, data: Mapping[str, Any]) -> dict[str, Any]:
        llm_pool = cast(Mapping[str, Any], data["llm_pool"])
        llm_services = cast(Mapping[str, Any], llm_pool["services"])
        default_service_name = cast(str, llm_pool["default_service"])
        default_service_config = dict(
            cast(Mapping[str, Any], llm_services.get(default_service_name, {}))
        )
        default_templates = cls._default_source_data()
        default_pool_service_template = cast(
            Mapping[str, Any],
            default_templates["llm_pool"]["services"]["default"],
        )
        legacy_llm = cast(Mapping[str, Any], data["llm"])
        if (
            default_service_name == "default"
            and default_service_config == dict(default_pool_service_template)
        ):
            default_service_config.update(
                {
                    "provider": legacy_llm["provider"],
                    "model": legacy_llm["model"],
                    "api_key": legacy_llm.get("api_key"),
                    "api_base": legacy_llm.get("api_base"),
                }
            )
            llm_services = dict(llm_services)
            cast(dict[str, Any], llm_services)["default"] = default_service_config

        embedding_pool_data = cast(
            Mapping[str, Any],
            data.get(
                "embedding_pool",
                {
                    "default_service": "default",
                    "services": {},
                },
            ),
        )
        embedding_services = cast(
            Mapping[str, Any], embedding_pool_data.get("services", {})
        )
        prompting = cast(Mapping[str, Any], data.get("prompting", {}))
        memory = cast(Mapping[str, Any], data["memory"])
        recall = cast(Mapping[str, Any], memory.get("recall", {}))
        extraction = cast(Mapping[str, Any], memory.get("extraction", {}))
        transcript = cast(Mapping[str, Any], data.get("transcript", {}))
        tools = cast(Mapping[str, Any], data.get("tools", {}))
        return {
            "allow_env_override": data["config_policy"]["allow_env_override"],
            "strict_agent_llm_binding": data["config_policy"][
                "strict_agent_llm_binding"
            ],
            "workflow_mode": data["config_policy"]["workflow_mode"],
            "unknown_key_policy": data["config_policy"]["unknown_key_policy"],
            "llm_provider": data["llm"]["provider"],
            "llm_model": data["llm"]["model"],
            "llm_api_key": data["llm"].get("api_key"),
            "llm_api_base": data["llm"].get("api_base"),
            "llm_pool_default_service": default_service_name,
            "llm_pool_services": {
                name: LLMServiceConfig.from_dict(cast(Mapping[str, Any], config))
                for name, config in llm_services.items()
            },
            "embedding_pool_default_service": embedding_pool_data.get(
                "default_service", "default"
            ),
            "embedding_pool_services": {
                name: EmbeddingServiceConfig.from_dict(cast(Mapping[str, Any], config))
                for name, config in embedding_services.items()
            },
            "embedding_model": data["embedding"]["model"],
            "prompting_base_system_prompt": prompting.get("base_system_prompt"),
            "chroma_path": memory["chroma_path"],
            "chroma_collection": memory["chroma_collection"],
            "memory_mode": memory["mode"],
            "memory_recall_semantic_retrieval_enabled": recall.get(
                "semantic_retrieval_enabled", True
            ),
            "memory_extraction_enabled": extraction.get("enabled", True),
            "memory_extraction_llm_service": extraction.get("llm_service"),
            "memory_extraction_embedding_service": extraction.get(
                "embedding_service"
            ),
            "memory_extraction_max_tokens": extraction.get("max_tokens"),
            "memory_extraction_rejection_log": extraction.get("rejection_log"),
            "memory_extraction_user_name": extraction.get("user_name", "User"),
            "memory_extraction_assistant_name": extraction.get(
                "assistant_name", "Assistant"
            ),
            "memory_extraction_prompt": extraction.get("prompt"),
            "memory_extraction_ontology": extraction.get("ontology"),
            "telemetry_enabled": data["telemetry"]["enabled"],
            "telemetry_endpoint": data["telemetry"].get("endpoint"),
            "debug_mode": data["telemetry"].get("debug_mode", False),
            "agents_dir": data["agents"].get("dir"),
            "agents_role_bindings": dict(data["agents"].get("role_bindings", {})),
            "workflows_dir": data.get("workflows", {}).get("dir"),
            "tools_config": ToolsConfig.from_dict(tools),
            "transcript_enabled": transcript.get("enabled", False),
            "transcript_backend": transcript.get("backend", "sqlite"),
            "transcript_path": transcript.get("path", "transcript.db"),
            "transcript_capture_context_log": transcript.get(
                "capture_context_log", True
            ),
            "deployment_profile": data["deployment_profile"],
            "install_root": data["runtime_paths"]["install_root"],
            "runtime_data_root": data["runtime_paths"]["runtime_data_root"],
            "workspace_root": data["runtime_paths"]["workspace_root"],
            "cache_root": data["runtime_paths"].get("cache_root"),
            "scratch_backend": data["scratch"]["backend"],
            "scratch_path": data["scratch"].get("path"),
            "artifacts_enabled": data["artifacts"]["enabled"],
            "artifacts_root_dir": data["artifacts"]["root_dir"],
            "artifacts_lineage_required": data["artifacts"]["lineage_required"],
            "artifacts_publish_on_task_success": data["artifacts"][
                "publish_on_task_success"
            ],
        }

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
    def for_testing(cls) -> RuntimeConfig:
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
        workspace_root = self._resolve(cast(str, self.workspace_root))
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
        runtime_data_root = self._resolve(cast(str, self.runtime_data_root))
        workspace_root = self._resolve(cast(str, self.workspace_root))
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
