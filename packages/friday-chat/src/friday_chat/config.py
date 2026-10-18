"""Compatibility facade for Friday Chat application configuration."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from friday_runtime.application_config import (
    DEFAULT_DEPRECATED_CONFIG_KEYS,
    DEFAULT_RENAMED_CONFIG_KEYS,
    HIGH_VALUE_NESTED_CONFIG_SECTIONS,
    TOP_LEVEL_CONFIG_SECTIONS,
    TRACEABILITY_KEYS,
    ChatConfig,
    ConfigDiagnostic,
    ConfigDiagnosticRules,
    EmbeddingConfig,
    ExtractionConfig,
    FinanceConfig,
    FridayChatConfig,
    FridayChatConfigError,
    GenerationConfigInput,
    LangfuseConfig,
    LegacyLLMExecutionConfig,
    LifecycleConfig,
    LLMConfig,
    LMStudioQwenOptionsInput,
    LoggingConfig,
    MaintenanceConfig,
    MemoryConfig,
    ModelTargetInput,
    PrimaryLLMExecutionConfig,
    ReasoningConfigInput,
    SamplingConfigInput,
    SecurityConfig,
    SessionConfig,
    SmartFileConfig,
    SpeechConfig,
    ToolsConfig,
    TranscriptConfig,
    TransportTargetInput,
    TypedLLMExecutionConfig,
    WebConfig,
    load_application_config,
)
from friday_runtime.application_config import (
    ENV_PATTERN as ENV_PATTERN,
)
from friday_runtime.application_config import (
    ChatServicePoolConfig as ChatServicePoolConfig,
)
from friday_runtime.application_config import (
    ChatTelemetryConfig as ChatTelemetryConfig,
)
from friday_runtime.application_config import (
    EmbeddingServicePoolConfig as EmbeddingServicePoolConfig,
)
from friday_runtime.application_config import (
    FlexibleConfigSection as FlexibleConfigSection,
)
from friday_runtime.application_config import (
    ModelLibraryReference as ModelLibraryReference,
)
from friday_runtime.application_config import (
    ProviderConfig as ProviderConfig,
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
    "telemetry": "friday_chat.telemetry, friday_chat.runtime.telemetry",
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

DEPRECATED_CONFIG_KEYS: dict[str, str] = dict(DEFAULT_DEPRECATED_CONFIG_KEYS)
RENAMED_CONFIG_KEYS: dict[str, str] = dict(DEFAULT_RENAMED_CONFIG_KEYS)


def get_config_traceability() -> dict[str, str]:
    """Return the machine-checkable FridayV2 config traceability map."""
    return dict(CONFIG_TRACEABILITY)


def load_friday_py_config(
    path: str | Path,
    *,
    env: Mapping[str, str] | None = None,
) -> FridayChatConfig:
    """Load Friday-py-style YAML through the shared Runtime schema."""
    return load_application_config(
        path,
        env=env,
        diagnostic_rules=ConfigDiagnosticRules(
            deprecated_keys=DEPRECATED_CONFIG_KEYS,
            renamed_keys=RENAMED_CONFIG_KEYS,
        ),
    )


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
