"""Submolt-related models."""

from __future__ import annotations

from pydantic import BaseModel


class SubmoltRef(BaseModel):
    name: str | None = None
    display_name: str | None = None

    model_config = {"extra": "allow"}


class Submolt(BaseModel):
    name: str | None = None
    display_name: str | None = None
    description: str | None = None
    banner_color: str | None = None
    theme_color: str | None = None
    your_role: str | None = None

    model_config = {"extra": "allow"}
