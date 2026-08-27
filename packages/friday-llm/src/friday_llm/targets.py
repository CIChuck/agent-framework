"""Typed target identity models, separate from generation intent."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TransportTarget(BaseModel):
    """Transport and serving-engine identity used to select adapters."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    provider: str = Field(min_length=1, max_length=64)
    dialect: str = Field(min_length=1, max_length=64)
    serving_engine: str | None = Field(default=None, min_length=1, max_length=64)


class ModelTarget(BaseModel):
    """Model identity used for capability resolution, not transport routing."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: str = Field(min_length=1, max_length=256)
    family: str | None = Field(default=None, min_length=1, max_length=64)
    revision: str | None = Field(default=None, min_length=1, max_length=128)


class ExecutionTarget(BaseModel):
    """Independent transport and model target descriptors."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    transport: TransportTarget
    model: ModelTarget

    @model_validator(mode="after")
    def require_explicit_release_one_identity(self) -> ExecutionTarget:
        if self.model.family is None or self.model.revision is None:
            raise ValueError(
                "normalized targets require explicit model family and revision"
            )
        return self
