"""Typed configuration loading for FridayV2."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import yaml
from friday_llm import (
    ChatServiceBinding,
    EmbeddingServiceBinding,
    EmbeddingServiceSpec,
    LLMServiceSpec,
    ModelLibraryError,
    resolve_chat_service,
    resolve_embedding_service,
)
from friday_runtime.model_library import load_model_library
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

if TYPE_CHECKING:
    from friday_llm import (
        GenerationConfig,
        LMStudioQwenOptions,
        ModelTarget,
        ReasoningConfig,
        SamplingConfig,
        TransportTarget,
    )

TOP_LEVEL_CONFIG_SECTIONS: tuple[str, ...] = (
    "model_library",
    "llm_pool",
    "embedding_pool",
    "logging",
    "llm",
    "extraction",
    "embedding",
    "memory",
    "transcript",
    "chat",
    "maintenance",
    "lifecycle",
    "smart_file",
    "tools",
    "web",
    "langfuse",
    "finance",
    "security",
    "session",
    "speech",
)

HIGH_VALUE_NESTED_CONFIG_SECTIONS: tuple[str, ...] = (
    "memory.retrieval",
    "memory.priming",
    "memory.cache",
    "memory.supporting_context",
    "memory.passage_router",
    "memory.query_relevance_filter",
    "memory.compaction",
    "maintenance.llm",
    "maintenance.prompts",
    "tools.loop",
    "tools.registry",
    "tools.context",
    "smart_file.llm",
    "web.reader",
    "security.sanitization",
    "speech.selection",
)

TRACEABILITY_KEYS: tuple[str, ...] = (
    *TOP_LEVEL_CONFIG_SECTIONS,
    *HIGH_VALUE_NESTED_CONFIG_SECTIONS,
)

CONFIG_TRACEABILITY: dict[str, str] = {
    "model_library": "friday_runtime.model_library",
    "llm_pool": "friday_llm.resolve_chat_service",
    "embedding_pool": "friday_llm.resolve_embedding_service",
    "logging": "friday_chat.config, friday_chat.runtime.logging",
    "llm": "friday_chat.runtime.chat_llm",
    "extraction": "friday_chat.runtime.extraction",
    "embedding": "friday_chat.runtime.embedding",
    "memory": "friday_chat.runtime.memory",
    "transcript": "friday_chat.runtime.transcript",
    "chat": "friday_chat.app.session_identity",
    "maintenance": "friday_chat.runtime.maintenance",
    "lifecycle": "friday_chat.runtime.lifecycle",
    "smart_file": "friday_chat.commands.files",
    "tools": "friday_chat.tools.registry, friday_chat.tools.loop",
    "web": "friday_chat.tools.registry.web_tools",
    "langfuse": "friday_chat.runtime.telemetry",
    "finance": "friday_chat.tools.registry.finance_tools",
    "security": "friday_chat.security",
    "session": "friday_chat.app.exit_maintenance",
    "speech": "friday_chat.speech",
    "memory.retrieval": "friday_chat.runtime.memory.retrieval",
    "memory.priming": "friday_chat.runtime.memory.priming",
    "memory.cache": "friday_chat.turns.processor.prompt_cache",
    "memory.supporting_context": "friday_chat.turns.processor.context_payload",
    "memory.passage_router": "friday_chat.runtime.passage_router",
    "memory.query_relevance_filter": "friday_chat.runtime.query_filter",
    "memory.compaction": "friday_chat.background.compaction",
    "maintenance.llm": "friday_chat.runtime.maintenance_llms",
    "maintenance.prompts": "friday_chat.runtime.maintenance_prompts",
    "tools.loop": "friday_chat.tools.loop",
    "tools.registry": "friday_chat.tools.registry",
    "tools.context": "friday_chat.runtime.tool_context",
    "smart_file.llm": "friday_chat.commands.files.smart_file_llm",
    "web.reader": "friday_chat.commands.files.web_reader",
    "security.sanitization": "friday_chat.security.sanitization",
    "speech.selection": "friday_chat.speech.selection",
}

DEPRECATED_CONFIG_KEYS: dict[str, str] = {
    "llm.temperature": "Use llm.generation.sampling.temperature.",
    "llm.top_p": "Use llm.generation.sampling.top_p.",
    "llm.top_k": "Use llm.generation.sampling.top_k.",
    "llm.max_tokens": "Use llm.generation.max_tokens.",
    "llm.thinking": "Use llm.generation.reasoning.mode.",
}
RENAMED_CONFIG_KEYS: dict[str, str] = {}

ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class FridayChatConfigError(ValueError):
    """Raised when FridayV2 configuration is invalid."""


class FlexibleConfigSection(BaseModel):
    """Base model for Friday-py-compatible config sections."""

    model_config = ConfigDict(extra="allow")


class ProviderConfig(FlexibleConfigSection):
    """Common provider configuration used by LLM-like sections."""

    model: str | None = None
    api_base: str | None = None
    api_key: str | None = None
    timeout_seconds: float | None = None


class ReasoningConfigInput(BaseModel):
    """Strict YAML shape converted lazily to Friday LLM reasoning intent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: Literal["auto", "enabled", "disabled"] = "auto"
    effort: str | None = Field(default=None, min_length=1, max_length=32)
    budget_tokens: int | None = Field(default=None, gt=0)
    preserve: bool | None = None

    def to_framework(self) -> ReasoningConfig:
        from friday_llm import ReasoningConfig

        return ReasoningConfig.model_validate(self.model_dump())


class SamplingConfigInput(BaseModel):
    """Strict YAML shape converted lazily to Friday LLM sampling intent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = Field(default=None, gt=0)
    min_p: float | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    repetition_penalty: float | None = None

    def to_framework(self) -> SamplingConfig:
        from friday_llm import SamplingConfig

        return SamplingConfig.model_validate(self.model_dump())


class GenerationConfigInput(BaseModel):
    """Strict primary-generation YAML independent of provider wire fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    reasoning: ReasoningConfigInput | None = None
    sampling: SamplingConfigInput | None = None
    max_tokens: int | None = Field(default=None, gt=0)


class TransportTargetInput(BaseModel):
    """Explicit transport identity supplied by the operator."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    provider: str = Field(min_length=1, max_length=64)
    dialect: str = Field(min_length=1, max_length=64)
    serving_engine: str | None = Field(default=None, min_length=1, max_length=64)

    def to_framework(self) -> TransportTarget:
        from friday_llm import TransportTarget

        return TransportTarget.model_validate(self.model_dump())


class ModelTargetInput(BaseModel):
    """Explicit model identity supplied by the operator."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: str = Field(min_length=1, max_length=256)
    family: str | None = Field(default=None, min_length=1, max_length=64)
    revision: str | None = Field(default=None, min_length=1, max_length=128)

    def to_framework(self) -> ModelTarget:
        from friday_llm import ModelTarget

        return ModelTarget.model_validate(self.model_dump())


class LMStudioQwenOptionsInput(BaseModel):
    """Bounded release-one provider options, separate from normalized intent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    namespace: Literal["lm_studio.qwen3_8"] = "lm_studio.qwen3_8"
    enable_thinking: bool | None = None
    reasoning_effort: Literal["xhigh", "medium", "low"] | None = None
    preserve_thinking: bool | None = None

    def to_framework(self) -> LMStudioQwenOptions:
        from friday_llm import LMStudioQwenOptions

        return LMStudioQwenOptions.model_validate(self.model_dump())


@dataclass(frozen=True)
class LegacyLLMExecutionConfig:
    """Resolved primary configuration for the temporary legacy call path."""

    temperature: float
    max_tokens: int | None
    thinking_enabled: bool | None


@dataclass(frozen=True)
class TypedLLMExecutionConfig:
    """Resolved primary configuration for Friday LLM's typed call path."""

    generation: GenerationConfig
    transport_target: TransportTarget
    model_target: ModelTarget
    provider_options: LMStudioQwenOptions | None


PrimaryLLMExecutionConfig = LegacyLLMExecutionConfig | TypedLLMExecutionConfig


class LoggingConfig(FlexibleConfigSection):
    """Logging configuration."""

    level: str = "WARNING"
    extraction_debug: bool = False
    extraction_rejections: bool = False
    extraction_rejections_file: str | None = None
    tools_debug: bool = False


class ModelLibraryReference(BaseModel):
    """Local canonical model-library reference."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str = Field(min_length=1)


class ChatServicePoolConfig(BaseModel):
    """Named canonical chat-service bindings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    default_service: str = Field(min_length=1, max_length=64)
    services: dict[str, ChatServiceBinding] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_default(self) -> ChatServicePoolConfig:
        if self.default_service not in self.services:
            raise ValueError("llm_pool.default_service must reference a service")
        return self


class EmbeddingServicePoolConfig(BaseModel):
    """Named canonical embedding-service bindings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    default_service: str = Field(min_length=1, max_length=64)
    services: dict[str, EmbeddingServiceBinding] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_default(self) -> EmbeddingServicePoolConfig:
        if self.default_service not in self.services:
            raise ValueError(
                "embedding_pool.default_service must reference a service"
            )
        return self


class LLMConfig(ProviderConfig):
    """Primary chat LLM configuration."""

    model_config = ConfigDict(extra="forbid")

    temperature: float = 0.7
    top_p: float | None = None
    top_k: int | None = None
    max_tokens: int | None = None
    max_retries: int = 3
    thinking: bool = False
    generation: GenerationConfigInput | None = None
    transport_target: TransportTargetInput | None = None
    model_target: ModelTargetInput | None = None
    provider_options: LMStudioQwenOptionsInput | None = None

    @model_validator(mode="after")
    def validate_typed_configuration(self) -> LLMConfig:
        has_transport = self.transport_target is not None
        has_model = self.model_target is not None
        if has_transport != has_model:
            raise ValueError(
                "llm.transport_target and llm.model_target must be supplied together"
            )
        if not has_transport:
            if self.generation is not None:
                raise ValueError(
                    "llm.generation requires explicit llm.transport_target and "
                    "llm.model_target"
                )
            if self.provider_options is not None:
                raise ValueError(
                    "llm.provider_options requires explicit llm.transport_target and "
                    "llm.model_target"
                )
            return self

        if self.model_target is None:
            raise ValueError("llm.model_target is required for typed execution")
        if self.model_target.family is None or self.model_target.revision is None:
            raise ValueError(
                "llm.model_target.family and llm.model_target.revision are required"
            )
        if self.model is not None:
            model_id = self.model_target.model_id
            if self.model != model_id and not self.model.endswith(f"/{model_id}"):
                raise ValueError(
                    "llm.model routing identity contradicts llm.model_target.model_id"
                )

        self.resolve_execution()
        return self

    def resolve_execution(self) -> PrimaryLLMExecutionConfig:
        """Resolve legacy compatibility fields into one explicit call path."""
        if self.transport_target is None or self.model_target is None:
            return LegacyLLMExecutionConfig(
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                thinking_enabled=(
                    self.thinking if "thinking" in self.model_fields_set else None
                ),
            )

        from friday_llm import (
            GenerationConfig,
            ReasoningConfig,
            ReasoningMode,
            SamplingConfig,
        )

        generation = self.generation or GenerationConfigInput()
        sampling_values = (
            generation.sampling.model_dump()
            if generation.sampling is not None
            else {}
        )
        sampling_fields = (
            generation.sampling.model_fields_set
            if generation.sampling is not None
            else set()
        )
        for legacy_name in ("temperature", "top_p", "top_k"):
            legacy_is_set = legacy_name in self.model_fields_set
            legacy_value = getattr(self, legacy_name)
            if legacy_is_set and legacy_name in sampling_fields:
                nested_value = sampling_values[legacy_name]
                if legacy_value != nested_value:
                    raise ValueError(
                        f"llm.{legacy_name} conflicts with "
                        f"llm.generation.sampling.{legacy_name}"
                    )
            if legacy_is_set:
                sampling_values[legacy_name] = legacy_value
            elif legacy_name == "temperature" and legacy_name not in sampling_fields:
                sampling_values[legacy_name] = 0.7

        reasoning = (
            generation.reasoning.to_framework()
            if generation.reasoning is not None
            else None
        )
        if "thinking" in self.model_fields_set:
            legacy_mode = (
                ReasoningMode.ENABLED if self.thinking else ReasoningMode.DISABLED
            )
            if reasoning is not None and reasoning.mode is not legacy_mode:
                raise ValueError(
                    "llm.thinking conflicts with llm.generation.reasoning.mode"
                )
            if reasoning is None:
                reasoning = ReasoningConfig(mode=legacy_mode)
        elif reasoning is None:
            reasoning = ReasoningConfig(mode=ReasoningMode.DISABLED)

        resolved_max_tokens = generation.max_tokens
        nested_max_tokens_is_set = "max_tokens" in generation.model_fields_set
        if "max_tokens" in self.model_fields_set:
            if nested_max_tokens_is_set and self.max_tokens != resolved_max_tokens:
                raise ValueError(
                    "llm.max_tokens conflicts with llm.generation.max_tokens"
                )
            resolved_max_tokens = self.max_tokens

        return TypedLLMExecutionConfig(
            generation=GenerationConfig(
                reasoning=reasoning,
                sampling=SamplingConfig.model_validate(sampling_values),
                max_tokens=resolved_max_tokens,
            ),
            transport_target=self.transport_target.to_framework(),
            model_target=self.model_target.to_framework(),
            provider_options=(
                self.provider_options.to_framework()
                if self.provider_options is not None
                else None
            ),
        )


class ExtractionConfig(ProviderConfig):
    """Entity and fact extraction configuration."""

    temperature: float = 0.0
    max_tokens: int | None = None
    max_retries: int = 2
    interval: int = 0
    rejection_log: str | None = None
    ontology: dict[str, Any] = Field(default_factory=dict)
    prompt: dict[str, Any] | str | None = None
    llm_service: str | None = None


class EmbeddingConfig(ProviderConfig):
    """Embedding provider configuration."""

    embedding_service: str | None = None


class MemoryConfig(FlexibleConfigSection):
    """Memory, retrieval, and context assembly configuration."""

    collection_name: str | None = None
    persist_directory: str | None = None
    retrieval: dict[str, Any] = Field(default_factory=dict)
    context_window: int | None = None
    output_buffer: int | None = None
    token_estimator: dict[str, Any] = Field(default_factory=dict)
    max_history_turns: int | None = None
    consolidate_after_turns: int | None = None
    compaction: dict[str, Any] = Field(default_factory=dict)
    context_format: str | None = None
    supporting_context: dict[str, Any] = Field(default_factory=dict)
    passage_router: dict[str, Any] = Field(default_factory=dict)
    query_relevance_filter: dict[str, Any] = Field(default_factory=dict)
    cache: dict[str, Any] = Field(default_factory=dict)
    priming: dict[str, Any] = Field(default_factory=dict)


class TranscriptConfig(FlexibleConfigSection):
    """Transcript persistence and export configuration."""

    export_directory: str | None = None
    capture_raw_prompts: bool = False


class ChatConfig(FlexibleConfigSection):
    """User-facing chat identity and prompt configuration."""

    user_name: str = "User"
    assistant_name: str = "Friday"
    system_prompt: str = "You are Friday."


class MaintenanceConfig(FlexibleConfigSection):
    """Memory maintenance configuration."""

    backup_directory: str | None = None
    pruning: dict[str, Any] = Field(default_factory=dict)
    synthesis: dict[str, Any] = Field(default_factory=dict)
    fact_checking: dict[str, Any] = Field(default_factory=dict)
    llm: dict[str, Any] = Field(default_factory=dict)
    embedding: dict[str, Any] | None = None
    defaults: dict[str, Any] = Field(default_factory=dict)
    logging: dict[str, Any] = Field(default_factory=dict)
    prompts: dict[str, Any] = Field(default_factory=dict)


class LifecycleConfig(FlexibleConfigSection):
    """Memory lifecycle configuration."""

    enabled: bool = False
    access_buffer: dict[str, Any] = Field(default_factory=dict)
    factor_computer: dict[str, Any] = Field(default_factory=dict)


class SmartFileConfig(FlexibleConfigSection):
    """Smart file reading and ingestion configuration."""

    auto_chunk_threshold: int | None = None
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    default_add_to_context: bool = True
    default_store_to_memory: bool = True
    code: dict[str, Any] = Field(default_factory=dict)
    llm: dict[str, Any] = Field(default_factory=dict)
    prompts: dict[str, Any] = Field(default_factory=dict)


class ToolsConfig(FlexibleConfigSection):
    """Tool loading, context, and loop configuration."""

    enabled: bool = True
    loop: dict[str, Any] = Field(default_factory=dict)
    registry: Any = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)


class WebConfig(FlexibleConfigSection):
    """Web tool configuration."""

    client: dict[str, Any] = Field(default_factory=dict)
    ssl: dict[str, Any] = Field(default_factory=dict)
    proxy: dict[str, Any] = Field(default_factory=dict)
    security: dict[str, Any] = Field(default_factory=dict)
    reader: dict[str, Any] = Field(default_factory=dict)
    serper_api_key: str | None = None


class LangfuseConfig(FlexibleConfigSection):
    """Langfuse telemetry configuration."""

    enabled: bool = False
    public_key: str | None = None
    secret_key: str | None = None
    host: str | None = None


class FinanceConfig(FlexibleConfigSection):
    """Finance tool provider configuration."""

    massive: dict[str, Any] = Field(default_factory=dict)


class SecurityConfig(FlexibleConfigSection):
    """Runtime security and sanitization configuration."""

    sanitization: dict[str, Any] = Field(default_factory=dict)


class SessionConfig(FlexibleConfigSection):
    """Exit maintenance session configuration."""

    flush_on_exit: bool = True
    lifecycle_on_exit: bool = True
    reorganize_on_exit: bool = False
    reorganize_mode: str = "fast"


class SpeechConfig(FlexibleConfigSection):
    """Speech service configuration."""

    enabled: bool = False
    tts: dict[str, Any] = Field(default_factory=dict)
    wakeword: dict[str, Any] = Field(default_factory=dict)
    elevenlabs: dict[str, Any] = Field(default_factory=dict)
    picovoice: dict[str, Any] = Field(default_factory=dict)
    mode: str = "file"
    streaming: Any = Field(default_factory=dict)
    playback: dict[str, Any] = Field(default_factory=dict)
    selection: dict[str, Any] = Field(default_factory=dict)
    chunking: dict[str, Any] = Field(default_factory=dict)


class ConfigDiagnostic(BaseModel):
    """Diagnostic emitted while loading FridayV2 config."""

    kind: Literal["unknown_key", "deprecated_key", "renamed_key"]
    path: str
    message: str


class FridayChatConfig(BaseModel):
    """Typed FridayV2 configuration compatible with Friday-py YAML shape."""

    model_config = ConfigDict(extra="forbid")

    model_library: ModelLibraryReference | None = None
    llm_pool: ChatServicePoolConfig | None = None
    embedding_pool: EmbeddingServicePoolConfig | None = None
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    transcript: TranscriptConfig = Field(default_factory=TranscriptConfig)
    chat: ChatConfig = Field(default_factory=ChatConfig)
    maintenance: MaintenanceConfig = Field(default_factory=MaintenanceConfig)
    lifecycle: LifecycleConfig = Field(default_factory=LifecycleConfig)
    smart_file: SmartFileConfig = Field(default_factory=SmartFileConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    web: WebConfig = Field(default_factory=WebConfig)
    langfuse: LangfuseConfig = Field(default_factory=LangfuseConfig)
    finance: FinanceConfig = Field(default_factory=FinanceConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    speech: SpeechConfig = Field(default_factory=SpeechConfig)
    diagnostics: list[ConfigDiagnostic] = Field(default_factory=list)
    llm_service_specs: dict[str, LLMServiceSpec] = Field(
        default_factory=dict,
        exclude=True,
        repr=False,
    )
    embedding_service_specs: dict[str, EmbeddingServiceSpec] = Field(
        default_factory=dict,
        exclude=True,
        repr=False,
    )


def get_config_traceability() -> dict[str, str]:
    """Return the machine-checkable FridayV2 config traceability map."""
    return dict(CONFIG_TRACEABILITY)


def load_friday_py_config(
    path: str | Path,
    *,
    env: Mapping[str, str] | None = None,
) -> FridayChatConfig:
    """Load Friday-py-style YAML into typed FridayV2 config models."""
    config_path = Path(path)
    environment = env if env is not None else os.environ
    data = _load_yaml_mapping(config_path)
    interpolated = _interpolate_env(data, environment)
    if not isinstance(interpolated, dict):
        raise FridayChatConfigError("Config root must be a mapping.")

    diagnostics = _collect_diagnostics(interpolated)
    allowed = set(TOP_LEVEL_CONFIG_SECTIONS)
    normalized = {key: value for key, value in interpolated.items() if key in allowed}
    normalized["diagnostics"] = diagnostics

    try:
        config = FridayChatConfig.model_validate(normalized)
    except ValidationError as exc:
        raise FridayChatConfigError(_format_validation_error(exc)) from exc

    canonical_sections = (
        config.model_library,
        config.llm_pool,
        config.embedding_pool,
    )
    if any(section is not None for section in canonical_sections):
        if not all(section is not None for section in canonical_sections):
            raise FridayChatConfigError(
                "model_library, llm_pool, and embedding_pool are required together"
            )
        if config.model_library is None or config.llm_pool is None:
            raise FridayChatConfigError("Incomplete canonical LLM configuration")
        if config.embedding_pool is None:
            raise FridayChatConfigError("Incomplete canonical embedding configuration")
        try:
            loaded = load_model_library(
                config.model_library.path,
                runtime_config_path=config_path,
                environment=environment,
                allow_env_override=False,
            )
            config.llm_service_specs = {
                name: resolve_chat_service(loaded.library, binding, environment)
                for name, binding in config.llm_pool.services.items()
            }
            config.embedding_service_specs = {
                name: resolve_embedding_service(
                    loaded.library,
                    binding,
                    environment,
                )
                for name, binding in config.embedding_pool.services.items()
            }
        except (ModelLibraryError, ValueError) as exc:
            raise FridayChatConfigError(
                "Unable to resolve canonical model-library services: "
                f"{exc}"
            ) from exc
    elif not config.llm.model:
        raise FridayChatConfigError("Missing required config: llm.model")

    return config


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FridayChatConfigError(f"Config file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise FridayChatConfigError(f"Invalid YAML in config file: {path}") from exc
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise FridayChatConfigError("Config root must be a mapping.")
    return raw


def _interpolate_env(value: Any, env: Mapping[str, str]) -> Any:
    if isinstance(value, str):
        return _interpolate_string(value, env)
    if isinstance(value, list):
        return [_interpolate_env(item, env) for item in value]
    if isinstance(value, dict):
        return {key: _interpolate_env(item, env) for key, item in value.items()}
    return value


def _interpolate_string(value: str, env: Mapping[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in env:
            raise FridayChatConfigError(
                f"Environment variable {name} is required by config."
            )
        return env[name]

    return ENV_PATTERN.sub(replace, value)


def _collect_diagnostics(data: dict[str, Any]) -> list[ConfigDiagnostic]:
    diagnostics: list[ConfigDiagnostic] = []
    for path in sorted(_iter_config_paths(data)):
        if path in RENAMED_CONFIG_KEYS:
            diagnostics.append(
                ConfigDiagnostic(
                    kind="renamed_key",
                    path=path,
                    message=(
                        f"Config key {path} has been renamed to "
                        f"{RENAMED_CONFIG_KEYS[path]}."
                    ),
                )
            )
        elif path in DEPRECATED_CONFIG_KEYS:
            diagnostics.append(
                ConfigDiagnostic(
                    kind="deprecated_key",
                    path=path,
                    message=f"Config key {path} is deprecated: {DEPRECATED_CONFIG_KEYS[path]}",
                )
            )

    allowed = set(TOP_LEVEL_CONFIG_SECTIONS)
    for key in sorted(data):
        if key not in allowed:
            diagnostics.append(
                ConfigDiagnostic(
                    kind="unknown_key",
                    path=key,
                    message=f"Unknown top-level config section: {key}",
                )
            )
    llm = data.get("llm")
    if isinstance(llm, Mapping) and not (
        "transport_target" in llm or "model_target" in llm
    ) and "model_library" not in data:
        diagnostics.append(
            ConfigDiagnostic(
                kind="deprecated_key",
                path="llm",
                message=(
                    "Legacy primary LLM execution is deprecated; add explicit "
                    "llm.transport_target and llm.model_target to use typed Friday "
                    "LLM controls."
                ),
            )
        )
    if "model_library" not in data:
        diagnostics.extend(_legacy_auxiliary_provider_diagnostics(data))
    return diagnostics


def _legacy_auxiliary_provider_diagnostics(
    data: Mapping[str, Any],
) -> list[ConfigDiagnostic]:
    """Report inline auxiliary providers that should become named services."""
    candidates: list[tuple[str, object]] = [
        ("extraction", data.get("extraction")),
        ("embedding", data.get("embedding")),
    ]
    memory = data.get("memory")
    if isinstance(memory, Mapping):
        candidates.append(("memory.passage_router", memory.get("passage_router")))
    maintenance = data.get("maintenance")
    if isinstance(maintenance, Mapping):
        maintenance_llms = maintenance.get("llm")
        if isinstance(maintenance_llms, Mapping):
            candidates.extend(
                (f"maintenance.llm.{role}", role_config)
                for role, role_config in maintenance_llms.items()
            )
        candidates.append(("maintenance.embedding", maintenance.get("embedding")))
    smart_file = data.get("smart_file")
    if isinstance(smart_file, Mapping):
        smart_file_llms = smart_file.get("llm")
        if isinstance(smart_file_llms, Mapping):
            candidates.extend(
                (f"smart_file.llm.{role}", role_config)
                for role, role_config in smart_file_llms.items()
            )

    provider_fields = {
        "model",
        "api_base",
        "api_key",
        "temperature",
        "max_tokens",
        "timeout_seconds",
        "max_retries",
    }
    return [
        ConfigDiagnostic(
            kind="deprecated_key",
            path=path,
            message=(
                f"Inline provider settings at {path} are deprecated; use a "
                "model-library profile and named service binding."
            ),
        )
        for path, value in candidates
        if isinstance(value, Mapping) and provider_fields.intersection(value)
    ]


def _format_validation_error(error: ValidationError) -> str:
    """Render validation failures without echoing untrusted config values."""
    details: list[str] = []
    for item in error.errors(include_input=False, include_url=False):
        location = ".".join(str(part) for part in item.get("loc", ())) or "config"
        details.append(f"{location}: {item.get('msg', 'invalid value')}")
    return "; ".join(details) or "Invalid Friday Chat configuration."


def _iter_config_paths(data: Mapping[str, Any], prefix: str = "") -> list[str]:
    paths: list[str] = []
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        paths.append(path)
        if isinstance(value, Mapping):
            paths.extend(_iter_config_paths(value, path))
    return paths


__all__ = [
    "CONFIG_TRACEABILITY",
    "DEPRECATED_CONFIG_KEYS",
    "HIGH_VALUE_NESTED_CONFIG_SECTIONS",
    "RENAMED_CONFIG_KEYS",
    "TOP_LEVEL_CONFIG_SECTIONS",
    "TRACEABILITY_KEYS",
    "ChatConfig",
    "ConfigDiagnostic",
    "EmbeddingConfig",
    "ExtractionConfig",
    "FinanceConfig",
    "FridayChatConfig",
    "FridayChatConfigError",
    "GenerationConfigInput",
    "LangfuseConfig",
    "LegacyLLMExecutionConfig",
    "LifecycleConfig",
    "LLMConfig",
    "LMStudioQwenOptionsInput",
    "LoggingConfig",
    "MaintenanceConfig",
    "MemoryConfig",
    "ModelTargetInput",
    "PrimaryLLMExecutionConfig",
    "ReasoningConfigInput",
    "SamplingConfigInput",
    "SecurityConfig",
    "SessionConfig",
    "SmartFileConfig",
    "SpeechConfig",
    "ToolsConfig",
    "TranscriptConfig",
    "TransportTargetInput",
    "TypedLLMExecutionConfig",
    "WebConfig",
    "get_config_traceability",
    "load_friday_py_config",
]
