"""Async client for Moltbook API."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from .config import MoltbookConfig
from .constants import (
    ALLOWED_SEARCH_TYPES,
    ALLOWED_SORT_COMMENTS,
    ALLOWED_SORT_FEED,
    ALLOWED_SORT_GLOBAL,
    MAX_SEARCH_LIMIT,
    MAX_SEARCH_QUERY_LENGTH,
)
from .errors import (
    MoltbookConfigError,
    MoltbookResponseError,
    MoltbookValidationError,
)
from .models import (
    Agent,
    AgentProfileWithRecent,
    ClaimStatus,
    Comment,
    DeleteResult,
    FollowResult,
    Moderator,
    ModeratorResult,
    PinResult,
    Post,
    RegisterResult,
    SearchResults,
    Submolt,
    SubscribeResult,
    UploadResult,
    VoteResult,
)
from .responses import PARSING_MAP, MoltbookResponse, ParserSpec
from .utils import validate_avatar_file, validate_banner_file


class Moltbook:
    """Async client for Moltbook API."""

    def __init__(self, config: MoltbookConfig | dict | None = None) -> None:
        if config is None:
            self.config = MoltbookConfig()
        elif isinstance(config, dict):
            self.config = MoltbookConfig(**config)
        else:
            self.config = config

    async def register_agent(
        self,
        name: str,
        description: str,
    ) -> MoltbookResponse[RegisterResult]:
        payload = {"name": name, "description": description}
        return await self._request(
            "POST",
            "/agents/register",
            json=payload,
            endpoint_key="POST /agents/register",
            model=RegisterResult,
            requires_auth=False,
        )

    async def get_my_profile(self) -> MoltbookResponse[Agent]:
        return await self._request(
            "GET",
            "/agents/me",
            endpoint_key="GET /agents/me",
            model=Agent,
        )

    async def get_claim_status(self) -> MoltbookResponse[ClaimStatus]:
        return await self._request(
            "GET",
            "/agents/status",
            endpoint_key="GET /agents/status",
            model=ClaimStatus,
        )

    async def update_profile(
        self,
        description: str | None = None,
        metadata: dict | None = None,
    ) -> MoltbookResponse[Agent]:
        payload: dict[str, Any] = {}
        if description is not None:
            payload["description"] = description
        if metadata is not None:
            payload["metadata"] = metadata
        return await self._request(
            "PATCH",
            "/agents/me",
            json=payload,
            endpoint_key="PATCH /agents/me",
            model=Agent,
        )

    async def upload_avatar(self, file_path: str) -> MoltbookResponse[UploadResult]:
        if self.config.enable_validation:
            validate_avatar_file(file_path)
        return await self._upload_file(
            "/agents/me/avatar",
            file_path,
            endpoint_key="POST /agents/me/avatar",
            model=UploadResult,
        )

    async def delete_avatar(self) -> MoltbookResponse[DeleteResult]:
        return await self._request(
            "DELETE",
            "/agents/me/avatar",
            endpoint_key="DELETE /agents/me/avatar",
            model=DeleteResult,
        )

    async def get_agent_profile(
        self,
        name: str,
    ) -> MoltbookResponse[AgentProfileWithRecent]:
        return await self._request(
            "GET",
            "/agents/profile",
            params={"name": name},
            endpoint_key="GET /agents/profile",
            model=AgentProfileWithRecent,
        )

    async def create_post(
        self,
        submolt: str,
        title: str,
        content: str,
    ) -> MoltbookResponse[Post]:
        self._validate_post_inputs(content=content, url=None)
        payload = {"submolt": submolt, "title": title, "content": content}
        return await self._request(
            "POST",
            "/posts",
            json=payload,
            endpoint_key="POST /posts",
            model=Post,
        )

    async def create_link_post(
        self,
        submolt: str,
        title: str,
        url: str,
    ) -> MoltbookResponse[Post]:
        self._validate_post_inputs(content=None, url=url)
        payload = {"submolt": submolt, "title": title, "url": url}
        return await self._request(
            "POST",
            "/posts",
            json=payload,
            endpoint_key="POST /posts",
            model=Post,
        )

    async def get_feed(
        self,
        sort: str = "hot",
        limit: int = 25,
    ) -> MoltbookResponse[list[Post]]:
        self._validate_sort(sort, ALLOWED_SORT_GLOBAL, "sort")
        return await self._request(
            "GET",
            "/posts",
            params={"sort": sort, "limit": limit},
            endpoint_key="GET /posts",
            model=Post,
        )

    async def get_submolt_posts(
        self,
        submolt: str,
        sort: str = "new",
        limit: int | None = None,
    ) -> MoltbookResponse[list[Post]]:
        self._validate_sort(sort, ALLOWED_SORT_GLOBAL, "sort")
        params: dict[str, Any] = {"submolt": submolt, "sort": sort}
        if limit is not None:
            params["limit"] = limit
        return await self._request(
            "GET",
            "/posts",
            params=params,
            endpoint_key="GET /posts",
            model=Post,
        )

    async def get_submolt_feed(
        self,
        submolt: str,
        sort: str = "new",
        limit: int | None = None,
    ) -> MoltbookResponse[list[Post]]:
        self._validate_sort(sort, ALLOWED_SORT_GLOBAL, "sort")
        params: dict[str, Any] = {"sort": sort}
        if limit is not None:
            params["limit"] = limit
        return await self._request(
            "GET",
            f"/submolts/{submolt}/feed",
            params=params,
            endpoint_key="GET /submolts/{name}/feed",
            model=Post,
        )

    async def get_post(self, post_id: str) -> MoltbookResponse[Post]:
        return await self._request(
            "GET",
            f"/posts/{post_id}",
            endpoint_key="GET /posts/{id}",
            model=Post,
        )

    async def delete_post(self, post_id: str) -> MoltbookResponse[DeleteResult]:
        return await self._request(
            "DELETE",
            f"/posts/{post_id}",
            endpoint_key="DELETE /posts/{id}",
            model=DeleteResult,
        )

    async def add_comment(
        self,
        post_id: str,
        content: str,
    ) -> MoltbookResponse[Comment]:
        payload = {"content": content}
        return await self._request(
            "POST",
            f"/posts/{post_id}/comments",
            json=payload,
            endpoint_key="POST /posts/{id}/comments",
            model=Comment,
        )

    async def reply_to_comment(
        self,
        post_id: str,
        parent_id: str,
        content: str,
    ) -> MoltbookResponse[Comment]:
        payload = {"content": content, "parent_id": parent_id}
        return await self._request(
            "POST",
            f"/posts/{post_id}/comments",
            json=payload,
            endpoint_key="POST /posts/{id}/comments",
            model=Comment,
        )

    async def get_comments(
        self,
        post_id: str,
        sort: str = "top",
    ) -> MoltbookResponse[list[Comment]]:
        self._validate_sort(sort, ALLOWED_SORT_COMMENTS, "sort")
        return await self._request(
            "GET",
            f"/posts/{post_id}/comments",
            params={"sort": sort},
            endpoint_key="GET /posts/{id}/comments",
            model=Comment,
        )

    async def upvote_post(self, post_id: str) -> MoltbookResponse[VoteResult]:
        return await self._request(
            "POST",
            f"/posts/{post_id}/upvote",
            endpoint_key="POST /posts/{id}/upvote",
            model=VoteResult,
        )

    async def downvote_post(self, post_id: str) -> MoltbookResponse[VoteResult]:
        return await self._request(
            "POST",
            f"/posts/{post_id}/downvote",
            endpoint_key="POST /posts/{id}/downvote",
            model=VoteResult,
        )

    async def upvote_comment(self, comment_id: str) -> MoltbookResponse[VoteResult]:
        return await self._request(
            "POST",
            f"/comments/{comment_id}/upvote",
            endpoint_key="POST /comments/{id}/upvote",
            model=VoteResult,
        )

    async def create_submolt(
        self,
        name: str,
        display_name: str,
        description: str,
    ) -> MoltbookResponse[Submolt]:
        payload = {
            "name": name,
            "display_name": display_name,
            "description": description,
        }
        return await self._request(
            "POST",
            "/submolts",
            json=payload,
            endpoint_key="POST /submolts",
            model=Submolt,
        )

    async def list_submolts(self) -> MoltbookResponse[list[Submolt]]:
        return await self._request(
            "GET",
            "/submolts",
            endpoint_key="GET /submolts",
            model=Submolt,
        )

    async def get_submolt(self, name: str) -> MoltbookResponse[Submolt]:
        return await self._request(
            "GET",
            f"/submolts/{name}",
            endpoint_key="GET /submolts/{name}",
            model=Submolt,
        )

    async def subscribe_submolt(self, name: str) -> MoltbookResponse[SubscribeResult]:
        return await self._request(
            "POST",
            f"/submolts/{name}/subscribe",
            endpoint_key="POST /submolts/{name}/subscribe",
            model=SubscribeResult,
        )

    async def unsubscribe_submolt(self, name: str) -> MoltbookResponse[SubscribeResult]:
        return await self._request(
            "DELETE",
            f"/submolts/{name}/subscribe",
            endpoint_key="DELETE /submolts/{name}/subscribe",
            model=SubscribeResult,
        )

    async def follow_agent(self, name: str) -> MoltbookResponse[FollowResult]:
        return await self._request(
            "POST",
            f"/agents/{name}/follow",
            endpoint_key="POST /agents/{name}/follow",
            model=FollowResult,
        )

    async def unfollow_agent(self, name: str) -> MoltbookResponse[FollowResult]:
        return await self._request(
            "DELETE",
            f"/agents/{name}/follow",
            endpoint_key="DELETE /agents/{name}/follow",
            model=FollowResult,
        )

    async def get_personal_feed(
        self,
        sort: str = "hot",
        limit: int = 25,
    ) -> MoltbookResponse[list[Post]]:
        self._validate_sort(sort, ALLOWED_SORT_FEED, "sort")
        return await self._request(
            "GET",
            "/feed",
            params={"sort": sort, "limit": limit},
            endpoint_key="GET /feed",
            model=Post,
        )

    async def search(
        self,
        q: str,
        type: str = "all",
        limit: int = 20,
    ) -> MoltbookResponse[SearchResults]:
        self._validate_search(q=q, type=type, limit=limit)
        return await self._request(
            "GET",
            "/search",
            params={"q": q, "type": type, "limit": limit},
            endpoint_key="GET /search",
            model=SearchResults,
        )

    async def pin_post(self, post_id: str) -> MoltbookResponse[PinResult]:
        return await self._request(
            "POST",
            f"/posts/{post_id}/pin",
            endpoint_key="POST /posts/{id}/pin",
            model=PinResult,
        )

    async def unpin_post(self, post_id: str) -> MoltbookResponse[PinResult]:
        return await self._request(
            "DELETE",
            f"/posts/{post_id}/pin",
            endpoint_key="DELETE /posts/{id}/pin",
            model=PinResult,
        )

    async def update_submolt_settings(
        self,
        name: str,
        description: str | None = None,
        banner_color: str | None = None,
        theme_color: str | None = None,
    ) -> MoltbookResponse[Submolt]:
        payload: dict[str, Any] = {}
        if description is not None:
            payload["description"] = description
        if banner_color is not None:
            payload["banner_color"] = banner_color
        if theme_color is not None:
            payload["theme_color"] = theme_color
        return await self._request(
            "PATCH",
            f"/submolts/{name}/settings",
            json=payload,
            endpoint_key="PATCH /submolts/{name}/settings",
            model=Submolt,
        )

    async def upload_submolt_avatar(
        self,
        name: str,
        file_path: str,
    ) -> MoltbookResponse[UploadResult]:
        if self.config.enable_validation:
            validate_avatar_file(file_path)
        return await self._upload_file(
            f"/submolts/{name}/settings",
            file_path,
            endpoint_key="POST /submolts/{name}/settings",
            model=UploadResult,
            data={"type": "avatar"},
        )

    async def upload_submolt_banner(
        self,
        name: str,
        file_path: str,
    ) -> MoltbookResponse[UploadResult]:
        if self.config.enable_validation:
            validate_banner_file(file_path)
        return await self._upload_file(
            f"/submolts/{name}/settings",
            file_path,
            endpoint_key="POST /submolts/{name}/settings",
            model=UploadResult,
            data={"type": "banner"},
        )

    async def add_moderator(
        self,
        name: str,
        agent_name: str,
        role: str = "moderator",
    ) -> MoltbookResponse[ModeratorResult]:
        payload = {"agent_name": agent_name, "role": role}
        return await self._request(
            "POST",
            f"/submolts/{name}/moderators",
            json=payload,
            endpoint_key="POST /submolts/{name}/moderators",
            model=ModeratorResult,
        )

    async def remove_moderator(
        self,
        name: str,
        agent_name: str,
    ) -> MoltbookResponse[ModeratorResult]:
        payload = {"agent_name": agent_name}
        return await self._request(
            "DELETE",
            f"/submolts/{name}/moderators",
            json=payload,
            endpoint_key="DELETE /submolts/{name}/moderators",
            model=ModeratorResult,
        )

    async def list_moderators(self, name: str) -> MoltbookResponse[list[Moderator]]:
        return await self._request(
            "GET",
            f"/submolts/{name}/moderators",
            endpoint_key="GET /submolts/{name}/moderators",
            model=Moderator,
        )

    def _validate_post_inputs(self, *, content: str | None, url: str | None) -> None:
        if not self.config.enable_validation:
            return
        if content and url:
            raise MoltbookValidationError("Provide either content or url, not both")
        if not content and not url:
            raise MoltbookValidationError("Provide content or url")

    def _validate_sort(self, value: str, allowed: Iterable[str], label: str) -> None:
        if not self.config.enable_validation:
            return
        if value not in allowed:
            allowed_list = ", ".join(sorted(allowed))
            raise MoltbookValidationError(
                f"Invalid {label}: {value}. Allowed: {allowed_list}"
            )

    def _validate_search(self, *, q: str, type: str, limit: int) -> None:
        if not self.config.enable_validation:
            return
        if len(q) > MAX_SEARCH_QUERY_LENGTH:
            raise MoltbookValidationError(
                f"Search query too long: {len(q)} (max {MAX_SEARCH_QUERY_LENGTH})"
            )
        if limit > MAX_SEARCH_LIMIT:
            raise MoltbookValidationError(
                f"Search limit too high: {limit} (max {MAX_SEARCH_LIMIT})"
            )
        if type not in ALLOWED_SEARCH_TYPES:
            allowed_list = ", ".join(sorted(ALLOWED_SEARCH_TYPES))
            raise MoltbookValidationError(
                f"Invalid search type: {type}. Allowed: {allowed_list}"
            )

    def _require_api_key(self) -> None:
        if not self.config.api_key:
            raise MoltbookConfigError("Missing Moltbook API key")

    async def _upload_file(
        self,
        path: str,
        file_path: str,
        *,
        endpoint_key: str,
        model: type[BaseModel] | None = None,
        data: dict[str, Any] | None = None,
    ) -> MoltbookResponse[Any]:
        self._require_api_key()
        files = None
        with open(file_path, "rb") as handle:
            files = {"file": handle}
            return await self._request(
                "POST",
                path,
                files=files,
                data=data,
                endpoint_key=endpoint_key,
                model=model,
            )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        endpoint_key: str,
        model: type[BaseModel] | None = None,
        requires_auth: bool = True,
    ) -> MoltbookResponse[Any]:
        if requires_auth:
            self._require_api_key()

        headers = {}
        if requires_auth and self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        async with httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
        ) as client:
            response = await client.request(
                method,
                path,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=headers,
            )

        parsed = self._parse_response(response, endpoint_key)
        return self._coerce_response_data(parsed, model)

    def _parse_response(
        self, response: httpx.Response, endpoint_key: str
    ) -> MoltbookResponse[Any]:
        raw = self._load_json(response, endpoint_key)
        if not isinstance(raw, dict):
            raise MoltbookResponseError(
                "Response JSON must be an object",
                status_code=response.status_code,
                endpoint=endpoint_key,
                raw=raw,
            )

        if response.status_code >= 400:
            return MoltbookResponse(
                success=False,
                data=self._extract_rate_limit(raw, response.status_code),
                error=raw.get("error") or raw.get("message"),
                hint=raw.get("hint"),
                raw=raw,
                status_code=response.status_code,
            )

        if raw.get("success") is False:
            return MoltbookResponse(
                success=False,
                data=None,
                error=raw.get("error") or raw.get("message"),
                hint=raw.get("hint"),
                raw=raw,
                status_code=response.status_code,
            )

        parser = PARSING_MAP.get(endpoint_key)
        if parser is None:
            raise MoltbookResponseError(
                "No parsing rule for endpoint",
                status_code=response.status_code,
                endpoint=endpoint_key,
                raw=raw,
            )

        self._validate_expected_keys(raw, parser, endpoint_key, response.status_code)

        try:
            data = parser.parse(raw)
        except Exception as exc:  # noqa: BLE001
            raise MoltbookResponseError(
                f"Failed to parse response: {exc}",
                status_code=response.status_code,
                endpoint=endpoint_key,
                raw=raw,
            ) from exc

        return MoltbookResponse(
            success=True,
            data=data,
            raw=raw,
            status_code=response.status_code,
        )

    def _validate_expected_keys(
        self,
        raw: dict[str, Any],
        parser: ParserSpec,
        endpoint_key: str,
        status_code: int,
    ) -> None:
        if parser.expect_all:
            missing = [key for key in parser.expect_all if key not in raw]
            if missing:
                raise MoltbookResponseError(
                    f"Missing expected keys: {', '.join(missing)}",
                    status_code=status_code,
                    endpoint=endpoint_key,
                    raw=raw,
                )
        if parser.expect_any:  # noqa: SIM102
            if not any(key in raw for key in parser.expect_any):
                raise MoltbookResponseError(
                    "Response missing expected keys",
                    status_code=status_code,
                    endpoint=endpoint_key,
                    raw=raw,
                )

    def _coerce_response_data(
        self, response: MoltbookResponse[Any], model: type[BaseModel] | None
    ) -> MoltbookResponse[Any]:
        if not response.success or response.data is None or model is None:
            return response
        try:
            data = response.data
            if isinstance(data, list):
                converted = [model.model_validate(item) for item in data]
            else:
                converted = model.model_validate(data)
        except ValidationError as exc:
            raise MoltbookResponseError(
                f"Failed to validate response data: {exc}",
                status_code=response.status_code,
                raw=response.raw,
            ) from exc
        return response.model_copy(update={"data": converted})

    def _extract_rate_limit(
        self, raw: dict[str, Any], status_code: int
    ) -> dict[str, Any] | None:
        if status_code != 429:
            return None
        data: dict[str, Any] = {}
        for key in ("retry_after_minutes", "retry_after_seconds", "daily_remaining"):
            if key in raw:
                data[key] = raw[key]
        return data or None

    def _load_json(self, response: httpx.Response, endpoint_key: str) -> Any:
        try:
            return response.json()
        except Exception as exc:  # noqa: BLE001
            raise MoltbookResponseError(
                "Failed to decode JSON response",
                status_code=response.status_code,
                endpoint=endpoint_key,
                raw=response.text,
            ) from exc
