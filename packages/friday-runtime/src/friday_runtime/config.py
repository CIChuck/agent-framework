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

    # Memory Configuration
    chroma_path: str = ".friday/chroma"
    chroma_collection: str = "friday_memory"
    memory_mode: str = "single_agent"

    # Telemetry Configuration
    telemetry_enabled: bool = False
    telemetry_endpoint: str | None = None
    debug_mode: bool = False

    # Agent Configuration
    agents_dir: str | None = None
    agents_role_bindings: dict[str, str] = field(default_factory=dict)

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

        defaults = self.deployment_profile_defaults(self.deployment_profile)
        if self.install_root is None:
            self.install_root = defaults["install_root"]
        if self.runtime_data_root is None:
            self.runtime_data_root = defaults["runtime_data_root"]
        if self.workspace_root is None:
            self.workspace_root = defaults["workspace_root"]

        self.agents_role_bindings = dict(self.agents_role_bindings)
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

        self.validate_runtime_roots()
        self.validate_scratch_path()
        self.validate_artifacts_policy()

    @staticmethod
    def _coerce_service_config(value: LLMServiceConfig | Mapping[str, Any]) -> LLMServiceConfig:
        if isinstance(value, LLMServiceConfig):
            return value
        if isinstance(value, Mapping):
            return LLMServiceConfig.from_dict(value)
        raise ValueError("llm_pool.services entries must be objects")

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
    def llm_pool(self) -> LLMPoolConfig:
        return LLMPoolConfig(
            default_service=self.llm_pool_default_service,
            services=dict(self.llm_pool_services),
        )

    def get_llm_service_config(self, service_name: str | None = None) -> LLMServiceConfig:
        selected = service_name or self.llm_pool_default_service
        try:
            return self.llm_pool_services[selected]
        except KeyError as exc:
            raise ValueError(f"Unknown llm service: {selected}") from exc

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
            "embedding": {
                "model": "text-embedding-3-small",
            },
            "memory": {
                "mode": "single_agent",
                "chroma_path": ".friday/chroma",
                "chroma_collection": "friday_memory",
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
            ("FRIDAY_CHROMA_PATH", ("memory", "chroma_path"), str),
            ("FRIDAY_CHROMA_COLLECTION", ("memory", "chroma_collection"), str),
            ("FRIDAY_MEMORY_MODE", ("memory", "mode"), str),
            ("FRIDAY_TELEMETRY_ENABLED", ("telemetry", "enabled"), _coerce_bool),
            ("FRIDAY_OTEL_ENDPOINT", ("telemetry", "endpoint"), str),
            ("FRIDAY_DEBUG", ("telemetry", "debug_mode"), _coerce_bool),
            ("FRIDAY_AGENTS_DIR", ("agents", "dir"), str),
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
            "embedding",
            "memory",
            "telemetry",
            "agents",
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
            "memory": {"mode", "chroma_path", "chroma_collection"},
            "telemetry": {"enabled", "endpoint", "debug_mode"},
            "agents": {"dir", "role_bindings"},
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
            "embedding_model": ("embedding", "model"),
            "chroma_path": ("memory", "chroma_path"),
            "chroma_collection": ("memory", "chroma_collection"),
            "memory_mode": ("memory", "mode"),
            "telemetry_enabled": ("telemetry", "enabled"),
            "telemetry_endpoint": ("telemetry", "endpoint"),
            "debug_mode": ("telemetry", "debug_mode"),
            "agents_dir": ("agents", "dir"),
            "agents_role_bindings": ("agents", "role_bindings"),
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
        services = cast(Mapping[str, Any], llm_pool["services"])
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
            "llm_pool_default_service": llm_pool["default_service"],
            "llm_pool_services": {
                name: LLMServiceConfig.from_dict(cast(Mapping[str, Any], config))
                for name, config in services.items()
            },
            "embedding_model": data["embedding"]["model"],
            "chroma_path": data["memory"]["chroma_path"],
            "chroma_collection": data["memory"]["chroma_collection"],
            "memory_mode": data["memory"]["mode"],
            "telemetry_enabled": data["telemetry"]["enabled"],
            "telemetry_endpoint": data["telemetry"].get("endpoint"),
            "debug_mode": data["telemetry"].get("debug_mode", False),
            "agents_dir": data["agents"].get("dir"),
            "agents_role_bindings": dict(data["agents"].get("role_bindings", {})),
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
