"""Post-related models."""

from __future__ import annotations

from pydantic import BaseModel

from .agent import AuthorRef
from .submolt import SubmoltRef


class Post(BaseModel):
    id: str | None = None
    title: str | None = None
    content: str | None = None
    url: str | None = None
    submolt: SubmoltRef | dict | None = None
    author: AuthorRef | dict | None = None
    upvotes: int | None = None
    downvotes: int | None = None
    created_at: str | None = None
    pinned: bool | None = None

    model_config = {"extra": "allow"}
