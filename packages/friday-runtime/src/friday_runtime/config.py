"""
Runtime configuration for the Friday Agent Framework.

RuntimeConfig mirrors the fields from the legacy FridayConfig
(in friday-cli/container.py) but lives in the runtime package
to avoid circular dependencies.

Ref: Phase 1 Build Plan, Step 4.1
"""

import os
from dataclasses import dataclass, field


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
    llm_api_key: str | None = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
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
        default_factory=lambda: os.getenv(
            "FRIDAY_CHROMA_PATH", ".friday/chroma"
        )
    )
    chroma_collection: str = field(
        default_factory=lambda: os.getenv(
            "FRIDAY_CHROMA_COLLECTION", "friday_memory"
        )
    )

    # Telemetry Configuration
    telemetry_enabled: bool = field(
        default_factory=lambda: os.getenv(
            "FRIDAY_TELEMETRY_ENABLED", "false"
        ).lower()
        == "true"
    )
    telemetry_endpoint: str | None = field(
        default_factory=lambda: os.getenv("FRIDAY_OTEL_ENDPOINT")
    )
    debug_mode: bool = field(
        default_factory=lambda: os.getenv(
            "FRIDAY_DEBUG", "false"
        ).lower()
        == "true"
    )

    # Agent Configuration
    agents_dir: str | None = field(
        default_factory=lambda: os.getenv("FRIDAY_AGENTS_DIR")
    )

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        """Create configuration from environment variables."""
        return cls()

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
