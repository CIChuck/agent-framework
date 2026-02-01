"""Agent-related models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Owner(BaseModel):
    x_handle: str | None = None
    x_name: str | None = None
    x_avatar: str | None = None
    x_bio: str | None = None
    x_follower_count: int | None = None
    x_following_count: int | None = None
    x_verified: bool | None = None

    model_config = {"extra": "allow"}


class AuthorRef(BaseModel):
    name: str | None = None

    model_config = {"extra": "allow"}


class Agent(BaseModel):
    name: str | None = None
    description: str | None = None
    karma: int | None = None
    follower_count: int | None = None
    following_count: int | None = None
    is_claimed: bool | None = None
    is_active: bool | None = None
    created_at: str | None = None
    last_active: str | None = None
    owner: Owner | None = None

    model_config = {"extra": "allow"}


class AgentProfileWithRecent(BaseModel):
    agent: Agent | None = None
    recentPosts: list[Any] | None = Field(default=None, description="Recent posts")

    model_config = {"extra": "allow"}
