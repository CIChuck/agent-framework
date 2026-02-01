"""Comment-related models."""

from __future__ import annotations

from pydantic import BaseModel

from .agent import AuthorRef


class Comment(BaseModel):
    id: str | None = None
    content: str | None = None
    author: AuthorRef | dict | None = None
    upvotes: int | None = None
    downvotes: int | None = None
    created_at: str | None = None
    parent_id: str | None = None
    post_id: str | None = None

    model_config = {"extra": "allow"}
