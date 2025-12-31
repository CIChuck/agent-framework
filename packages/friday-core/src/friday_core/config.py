"""
Global configuration management using Pydantic Settings.
Handles environment variable loading and validation.

Ref: Batch 0 Specification, Section 3.1
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class FridayBaseSettings(BaseSettings):
    """
    Global settings inherited by all packages.

    Configuration is loaded from environment variables and .env files.
    Inner components MUST NOT instantiate this directly - configuration
    should be injected via constructor parameters.

    Example:
        # In application layer (friday-cli):
        settings = FridayBaseSettings()
        engine = ContextEngine(
            model_name=settings.DEFAULT_MODEL,
            api_key=settings.OPENAI_API_KEY
        )
    """

    APP_ENV: str = "development"  # development | production | testing
    LOG_LEVEL: str = "INFO"

    # LLM Settings (needed by Memory components)
    DEFAULT_MODEL: str = "gpt-4-turbo"
    OPENAI_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
