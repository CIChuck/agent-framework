"""Search-related models."""

from __future__ import annotations

from pydantic import BaseModel

from .agent import AuthorRef
from .submolt import SubmoltRef


class SearchResultItem(BaseModel):
    id: str | None = None
    type: str | None = None
    title: str | None = None
    content: str | None = None
    similarity: float | None = None
    author: AuthorRef | dict | None = None
    submolt: SubmoltRef | dict | None = None
    post: dict | None = None
    post_id: str | None = None
    upvotes: int | None = None
    downvotes: int | None = None
    created_at: str | None = None

    model_config = {"extra": "allow"}


class SearchResults(BaseModel):
    query: str | None = None
    type: str | None = None
    results: list[SearchResultItem] | None = None
    count: int | None = None

    model_config = {"extra": "allow"}
