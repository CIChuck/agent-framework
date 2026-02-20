"""Configuration for Moltbook client."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .constants import BASE_URL


class MoltbookConfig(BaseModel):
    """Configuration for Moltbook client."""

    api_key: str | None = Field(default=None, description="Moltbook API key")
    base_url: str = Field(default=BASE_URL, description="Base API URL")
    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=600.0,
        description="HTTP timeout in seconds",
    )
    enable_validation: bool = Field(
        default=True,
        alias="validate",
        description="Enable client-side parameter validation",
    )

    @field_validator("base_url")
    @classmethod
    def _validate_base_url(cls, value: str) -> str:
        if not value.startswith("https://www.moltbook.com/api/v1"):
            raise ValueError("Base URL must start with https://www.moltbook.com/api/v1")
        return value.rstrip("/")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )
