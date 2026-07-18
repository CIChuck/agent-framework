"""Typed configuration loading for FridayV2."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

TOP_LEVEL_CONFIG_SECTIONS: tuple[str, ...] = (
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

DEPRECATED_CONFIG_KEYS: dict[str, str] = {}
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


class LoggingConfig(FlexibleConfigSection):
    """Logging configuration."""

    level: str = "WARNING"
    extraction_debug: bool = False
    extraction_rejections: bool = False
    extraction_rejections_file: str | None = None
    tools_debug: bool = False


class LLMConfig(ProviderConfig):
    """Primary chat LLM configuration."""

    temperature: float = 0.7
    top_p: float | None = None
    top_k: int | None = None
    max_tokens: int | None = None
    max_retries: int = 3
    thinking: bool = False


class ExtractionConfig(ProviderConfig):
    """Entity and fact extraction configuration."""

    temperature: float = 0.0
    max_tokens: int | None = None
    max_retries: int = 2
    interval: int = 0
    rejection_log: str | None = None
    ontology: dict[str, Any] = Field(default_factory=dict)
    prompt: dict[str, Any] | str | None = None


class EmbeddingConfig(ProviderConfig):
    """Embedding provider configuration."""


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

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    llm: LLMConfig
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
    data = _load_yaml_mapping(config_path)
    interpolated = _interpolate_env(data, env or os.environ)
    if not isinstance(interpolated, dict):
        raise FridayChatConfigError("Config root must be a mapping.")

    diagnostics = _collect_diagnostics(interpolated)
    allowed = set(TOP_LEVEL_CONFIG_SECTIONS)
    normalized = {key: value for key, value in interpolated.items() if key in allowed}
    normalized["diagnostics"] = diagnostics

    try:
        config = FridayChatConfig.model_validate(normalized)
    except ValidationError as exc:
        raise FridayChatConfigError(str(exc)) from exc

    if not config.llm.model:
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
    return diagnostics


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
    "LangfuseConfig",
    "LifecycleConfig",
    "LLMConfig",
    "LoggingConfig",
    "MaintenanceConfig",
    "MemoryConfig",
    "SecurityConfig",
    "SessionConfig",
    "SmartFileConfig",
    "SpeechConfig",
    "ToolsConfig",
    "TranscriptConfig",
    "WebConfig",
    "get_config_traceability",
    "load_friday_py_config",
]
