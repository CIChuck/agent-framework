"""Moderation-related models."""

from __future__ import annotations

from pydantic import BaseModel


class Moderator(BaseModel):
    name: str | None = None
    role: str | None = None

    model_config = {"extra": "allow"}
