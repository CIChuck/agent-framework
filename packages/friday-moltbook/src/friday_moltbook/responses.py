"""Response wrapper and parsing map for Moltbook."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MoltbookResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: str | None = None
    hint: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)
    status_code: int | None = None

    model_config = {"arbitrary_types_allowed": True}


@dataclass(frozen=True)
class ParserSpec:
    expect_any: tuple[str, ...] = ()
    expect_all: tuple[str, ...] = ()
    parse: Callable[[dict[str, Any]], Any] = lambda raw: raw


def _parse_data_or_key(primary: str, fallback: str) -> Callable[[dict[str, Any]], Any]:
    def _parser(raw: dict[str, Any]) -> Any:
        if primary in raw:
            return raw[primary]
        if fallback in raw:
            return raw[fallback]
        raise KeyError(f"Expected '{primary}' or '{fallback}'")

    return _parser


def _parse_data_or_message() -> Callable[[dict[str, Any]], Any]:
    def _parser(raw: dict[str, Any]) -> Any:
        if "data" in raw:
            return raw["data"]
        if "message" in raw:
            return {"message": raw["message"]}
        raise KeyError("Expected 'data' or 'message'")

    return _parser


def _parse_status(raw: dict[str, Any]) -> dict[str, Any]:
    if "status" not in raw:
        raise KeyError("Expected 'status'")
    return {"status": raw["status"]}


def _parse_profile(raw: dict[str, Any]) -> dict[str, Any]:
    if "agent" not in raw or "recentPosts" not in raw:
        raise KeyError("Expected 'agent' and 'recentPosts'")
    return {"agent": raw["agent"], "recentPosts": raw["recentPosts"]}


def _parse_search(raw: dict[str, Any]) -> dict[str, Any]:
    for key in ("query", "type", "results", "count"):
        if key not in raw:
            raise KeyError(f"Expected '{key}'")
    return {
        "query": raw["query"],
        "type": raw["type"],
        "results": raw["results"],
        "count": raw["count"],
    }


PARSING_MAP: dict[str, ParserSpec] = {
    "POST /agents/register": ParserSpec(
        expect_any=("agent",),
        parse=_parse_data_or_key("agent", "agent"),
    ),
    "GET /agents/me": ParserSpec(
        expect_any=("data", "agent"),
        parse=_parse_data_or_key("data", "agent"),
    ),
    "GET /agents/status": ParserSpec(expect_any=("status",), parse=_parse_status),
    "PATCH /agents/me": ParserSpec(
        expect_any=("data", "agent"),
        parse=_parse_data_or_key("data", "agent"),
    ),
    "POST /agents/me/avatar": ParserSpec(
        expect_any=("data", "message"),
        parse=_parse_data_or_message(),
    ),
    "DELETE /agents/me/avatar": ParserSpec(
        expect_any=("data", "message"),
        parse=_parse_data_or_message(),
    ),
    "GET /agents/profile": ParserSpec(
        expect_all=("agent", "recentPosts"),
        parse=_parse_profile,
    ),
    "POST /posts": ParserSpec(
        expect_any=("data", "post"),
        parse=_parse_data_or_key("data", "post"),
    ),
    "GET /posts": ParserSpec(
        expect_any=("data", "posts"),
        parse=_parse_data_or_key("data", "posts"),
    ),
    "GET /submolts/{name}/feed": ParserSpec(
        expect_any=("data", "posts"),
        parse=_parse_data_or_key("data", "posts"),
    ),
    "GET /posts/{id}": ParserSpec(
        expect_any=("data", "post"),
        parse=_parse_data_or_key("data", "post"),
    ),
    "DELETE /posts/{id}": ParserSpec(
        expect_any=("data", "message"),
        parse=_parse_data_or_message(),
    ),
    "POST /posts/{id}/comments": ParserSpec(
        expect_any=("data", "comment"),
        parse=_parse_data_or_key("data", "comment"),
    ),
    "GET /posts/{id}/comments": ParserSpec(
        expect_any=("data", "comments"),
        parse=_parse_data_or_key("data", "comments"),
    ),
    "POST /posts/{id}/upvote": ParserSpec(
        expect_any=("message",),
        parse=lambda raw: raw,
    ),
    "POST /posts/{id}/downvote": ParserSpec(
        expect_any=("message",),
        parse=lambda raw: raw,
    ),
    "POST /comments/{id}/upvote": ParserSpec(
        expect_any=("message",),
        parse=lambda raw: raw,
    ),
    "POST /submolts": ParserSpec(
        expect_any=("data", "submolt"),
        parse=_parse_data_or_key("data", "submolt"),
    ),
    "GET /submolts": ParserSpec(
        expect_any=("data", "submolts"),
        parse=_parse_data_or_key("data", "submolts"),
    ),
    "GET /submolts/{name}": ParserSpec(
        expect_any=("data", "submolt"),
        parse=_parse_data_or_key("data", "submolt"),
    ),
    "POST /submolts/{name}/subscribe": ParserSpec(
        expect_any=("data", "message"),
        parse=_parse_data_or_message(),
    ),
    "DELETE /submolts/{name}/subscribe": ParserSpec(
        expect_any=("data", "message"),
        parse=_parse_data_or_message(),
    ),
    "POST /agents/{name}/follow": ParserSpec(
        expect_any=("message",),
        parse=lambda raw: raw,
    ),
    "DELETE /agents/{name}/follow": ParserSpec(
        expect_any=("message",),
        parse=lambda raw: raw,
    ),
    "GET /feed": ParserSpec(
        expect_any=("data", "posts"),
        parse=_parse_data_or_key("data", "posts"),
    ),
    "GET /search": ParserSpec(
        expect_all=("query", "type", "results", "count"),
        parse=_parse_search,
    ),
    "POST /posts/{id}/pin": ParserSpec(
        expect_any=("data", "message"),
        parse=_parse_data_or_message(),
    ),
    "DELETE /posts/{id}/pin": ParserSpec(
        expect_any=("data", "message"),
        parse=_parse_data_or_message(),
    ),
    "PATCH /submolts/{name}/settings": ParserSpec(
        expect_any=("data", "submolt"),
        parse=_parse_data_or_key("data", "submolt"),
    ),
    "POST /submolts/{name}/settings": ParserSpec(
        expect_any=("data", "message"),
        parse=_parse_data_or_message(),
    ),
    "POST /submolts/{name}/moderators": ParserSpec(
        expect_any=("data", "message"),
        parse=_parse_data_or_message(),
    ),
    "DELETE /submolts/{name}/moderators": ParserSpec(
        expect_any=("data", "message"),
        parse=_parse_data_or_message(),
    ),
    "GET /submolts/{name}/moderators": ParserSpec(
        expect_any=("data", "moderators"),
        parse=_parse_data_or_key("data", "moderators"),
    ),
}
