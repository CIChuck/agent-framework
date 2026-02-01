"""Moltbook integration tools."""

from __future__ import annotations

from typing import Any

import os

from pydantic import BaseModel, Field

from friday_tools.base import FridayTool, ToolResult

from friday_moltbook import Moltbook, MoltbookConfig
from friday_moltbook.errors import MoltbookError


class MoltbookToolBase(FridayTool):
    """Base tool for Moltbook integrations."""

    category = "integrations"
    tags = ["moltbook", "social", "api"]

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        validate: bool | None = None,
    ) -> None:
        if api_key is None:
            api_key = os.getenv("MOLTBOOK_API_KEY")
        config_data: dict[str, Any] = {}
        if api_key is not None:
            config_data["api_key"] = api_key
        if base_url is not None:
            config_data["base_url"] = base_url
        if timeout is not None:
            config_data["timeout"] = timeout
        if validate is not None:
            config_data["validate"] = validate
        if config_data:
            self._config = MoltbookConfig(**config_data)
        else:
            self._config = MoltbookConfig()

    def _client(self) -> Moltbook:
        return Moltbook(self._config)

    async def _execute_method(self, method_name: str, args: BaseModel) -> ToolResult:
        client = self._client()
        try:
            response = await getattr(client, method_name)(**args.model_dump())
        except MoltbookError as exc:
            return ToolResult(
                content=f"{self.name} failed: {exc}",
                error=str(exc),
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                content=f"{self.name} failed: {type(exc).__name__}: {exc}",
                error=str(exc),
            )

        metadata: dict[str, Any] = {}
        if response.status_code is not None:
            metadata["status_code"] = response.status_code
        rate_limit = self._extract_rate_limit(response)
        if rate_limit:
            metadata["rate_limit"] = rate_limit

        data_payload = {
            "raw": response.raw,
            "data": response.data,
        }
        if response.error:
            data_payload["error"] = response.error
        if response.hint:
            data_payload["hint"] = response.hint

        content = self._format_content(response)
        error = None
        if not response.success:
            error = response.error or "Unknown error"

        return ToolResult(
            content=content,
            data=data_payload,
            metadata=metadata,
            error=error,
        )

    def _format_content(self, response: Any) -> str:
        if response.success:
            message = None
            if isinstance(response.data, dict) and "message" in response.data:
                message = response.data["message"]
            elif hasattr(response.data, "message"):
                message = getattr(response.data, "message")
            if message:
                return str(message)
            return f"{self.name} succeeded"
        error_text = response.error or "Unknown error"
        if response.hint:
            return f"{self.name} failed: {error_text} (hint: {response.hint})"
        return f"{self.name} failed: {error_text}"

    def _extract_rate_limit(self, response: Any) -> dict[str, Any] | None:
        if not response.raw:
            return None
        keys = ("retry_after_minutes", "retry_after_seconds", "daily_remaining")
        data = {key: response.raw.get(key) for key in keys if key in response.raw}
        return data or None


class MoltbookMethodTool(MoltbookToolBase):
    """Tool wrapper for a Moltbook client method."""

    client_method: str

    async def run(self, args: BaseModel) -> ToolResult:
        return await self._execute_method(self.client_method, args)


class NoInput(BaseModel):
    """Empty input model."""


class RegisterAgentInput(BaseModel):
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")


class UpdateProfileInput(BaseModel):
    description: str | None = Field(default=None, description="New description")
    metadata: dict | None = Field(default=None, description="Metadata dict")


class UploadAvatarInput(BaseModel):
    file_path: str = Field(..., description="Path to avatar image file")


class AgentProfileInput(BaseModel):
    name: str = Field(..., description="Agent name")


class CreatePostInput(BaseModel):
    submolt: str = Field(..., description="Submolt name")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")


class CreateLinkPostInput(BaseModel):
    submolt: str = Field(..., description="Submolt name")
    title: str = Field(..., description="Post title")
    url: str = Field(..., description="Link URL")


class FeedInput(BaseModel):
    sort: str = Field(default="hot", description="Sort order")
    limit: int = Field(default=25, description="Maximum results")


class SubmoltPostsInput(BaseModel):
    submolt: str = Field(..., description="Submolt name")
    sort: str = Field(default="new", description="Sort order")
    limit: int | None = Field(default=None, description="Maximum results")


class SubmoltFeedInput(BaseModel):
    submolt: str = Field(..., description="Submolt name")
    sort: str = Field(default="new", description="Sort order")
    limit: int | None = Field(default=None, description="Maximum results")


class PostIdInput(BaseModel):
    post_id: str = Field(..., description="Post ID")


class CommentInput(BaseModel):
    post_id: str = Field(..., description="Post ID")
    content: str = Field(..., description="Comment content")


class ReplyCommentInput(BaseModel):
    post_id: str = Field(..., description="Post ID")
    parent_id: str = Field(..., description="Parent comment ID")
    content: str = Field(..., description="Reply content")


class GetCommentsInput(BaseModel):
    post_id: str = Field(..., description="Post ID")
    sort: str = Field(default="top", description="Sort order")


class CommentIdInput(BaseModel):
    comment_id: str = Field(..., description="Comment ID")


class CreateSubmoltInput(BaseModel):
    name: str = Field(..., description="Submolt name")
    display_name: str = Field(..., description="Display name")
    description: str = Field(..., description="Description")


class SubmoltNameInput(BaseModel):
    name: str = Field(..., description="Submolt name")


class FollowAgentInput(BaseModel):
    name: str = Field(..., description="Agent name")


class PersonalFeedInput(BaseModel):
    sort: str = Field(default="hot", description="Sort order")
    limit: int = Field(default=25, description="Maximum results")


class SearchInput(BaseModel):
    q: str = Field(..., description="Search query")
    type: str = Field(default="all", description="Search type")
    limit: int = Field(default=20, description="Max results")


class UpdateSubmoltSettingsInput(BaseModel):
    name: str = Field(..., description="Submolt name")
    description: str | None = Field(default=None, description="New description")
    banner_color: str | None = Field(default=None, description="Banner color")
    theme_color: str | None = Field(default=None, description="Theme color")


class UploadSubmoltAssetInput(BaseModel):
    name: str = Field(..., description="Submolt name")
    file_path: str = Field(..., description="Path to asset file")


class AddModeratorInput(BaseModel):
    name: str = Field(..., description="Submolt name")
    agent_name: str = Field(..., description="Agent name")
    role: str = Field(default="moderator", description="Role")


class RemoveModeratorInput(BaseModel):
    name: str = Field(..., description="Submolt name")
    agent_name: str = Field(..., description="Agent name")


class ListModeratorsInput(BaseModel):
    name: str = Field(..., description="Submolt name")


class MoltbookRegisterAgentTool(MoltbookMethodTool):
    name = "moltbook_register_agent"
    description = "Register a new Moltbook agent"
    Input = RegisterAgentInput
    client_method = "register_agent"


class MoltbookGetMyProfileTool(MoltbookMethodTool):
    name = "moltbook_get_my_profile"
    description = "Get current agent profile"
    Input = NoInput
    client_method = "get_my_profile"


class MoltbookGetClaimStatusTool(MoltbookMethodTool):
    name = "moltbook_get_claim_status"
    description = "Get claim status for current agent"
    Input = NoInput
    client_method = "get_claim_status"


class MoltbookUpdateProfileTool(MoltbookMethodTool):
    name = "moltbook_update_profile"
    description = "Update current agent profile"
    Input = UpdateProfileInput
    client_method = "update_profile"


class MoltbookUploadAvatarTool(MoltbookMethodTool):
    name = "moltbook_upload_avatar"
    description = "Upload agent avatar"
    Input = UploadAvatarInput
    client_method = "upload_avatar"


class MoltbookDeleteAvatarTool(MoltbookMethodTool):
    name = "moltbook_delete_avatar"
    description = "Delete agent avatar"
    Input = NoInput
    client_method = "delete_avatar"


class MoltbookGetAgentProfileTool(MoltbookMethodTool):
    name = "moltbook_get_agent_profile"
    description = "Get another agent profile"
    Input = AgentProfileInput
    client_method = "get_agent_profile"


class MoltbookCreatePostTool(MoltbookMethodTool):
    name = "moltbook_create_post"
    description = "Create a text post"
    Input = CreatePostInput
    client_method = "create_post"


class MoltbookCreateLinkPostTool(MoltbookMethodTool):
    name = "moltbook_create_link_post"
    description = "Create a link post"
    Input = CreateLinkPostInput
    client_method = "create_link_post"


class MoltbookGetFeedTool(MoltbookMethodTool):
    name = "moltbook_get_feed"
    description = "Get global feed"
    Input = FeedInput
    client_method = "get_feed"


class MoltbookGetSubmoltPostsTool(MoltbookMethodTool):
    name = "moltbook_get_submolt_posts"
    description = "Get posts from a submolt (query)"
    Input = SubmoltPostsInput
    client_method = "get_submolt_posts"


class MoltbookGetSubmoltFeedTool(MoltbookMethodTool):
    name = "moltbook_get_submolt_feed"
    description = "Get submolt feed (convenience endpoint)"
    Input = SubmoltFeedInput
    client_method = "get_submolt_feed"


class MoltbookGetPostTool(MoltbookMethodTool):
    name = "moltbook_get_post"
    description = "Get a single post"
    Input = PostIdInput
    client_method = "get_post"


class MoltbookDeletePostTool(MoltbookMethodTool):
    name = "moltbook_delete_post"
    description = "Delete a post"
    Input = PostIdInput
    client_method = "delete_post"


class MoltbookAddCommentTool(MoltbookMethodTool):
    name = "moltbook_add_comment"
    description = "Add a comment to a post"
    Input = CommentInput
    client_method = "add_comment"


class MoltbookReplyToCommentTool(MoltbookMethodTool):
    name = "moltbook_reply_to_comment"
    description = "Reply to a comment"
    Input = ReplyCommentInput
    client_method = "reply_to_comment"


class MoltbookGetCommentsTool(MoltbookMethodTool):
    name = "moltbook_get_comments"
    description = "Get comments for a post"
    Input = GetCommentsInput
    client_method = "get_comments"


class MoltbookUpvotePostTool(MoltbookMethodTool):
    name = "moltbook_upvote_post"
    description = "Upvote a post"
    Input = PostIdInput
    client_method = "upvote_post"


class MoltbookDownvotePostTool(MoltbookMethodTool):
    name = "moltbook_downvote_post"
    description = "Downvote a post"
    Input = PostIdInput
    client_method = "downvote_post"


class MoltbookUpvoteCommentTool(MoltbookMethodTool):
    name = "moltbook_upvote_comment"
    description = "Upvote a comment"
    Input = CommentIdInput
    client_method = "upvote_comment"


class MoltbookCreateSubmoltTool(MoltbookMethodTool):
    name = "moltbook_create_submolt"
    description = "Create a submolt"
    Input = CreateSubmoltInput
    client_method = "create_submolt"


class MoltbookListSubmoltsTool(MoltbookMethodTool):
    name = "moltbook_list_submolts"
    description = "List all submolts"
    Input = NoInput
    client_method = "list_submolts"


class MoltbookGetSubmoltTool(MoltbookMethodTool):
    name = "moltbook_get_submolt"
    description = "Get a submolt"
    Input = SubmoltNameInput
    client_method = "get_submolt"


class MoltbookSubscribeSubmoltTool(MoltbookMethodTool):
    name = "moltbook_subscribe_submolt"
    description = "Subscribe to a submolt"
    Input = SubmoltNameInput
    client_method = "subscribe_submolt"


class MoltbookUnsubscribeSubmoltTool(MoltbookMethodTool):
    name = "moltbook_unsubscribe_submolt"
    description = "Unsubscribe from a submolt"
    Input = SubmoltNameInput
    client_method = "unsubscribe_submolt"


class MoltbookFollowAgentTool(MoltbookMethodTool):
    name = "moltbook_follow_agent"
    description = "Follow an agent"
    Input = FollowAgentInput
    client_method = "follow_agent"


class MoltbookUnfollowAgentTool(MoltbookMethodTool):
    name = "moltbook_unfollow_agent"
    description = "Unfollow an agent"
    Input = FollowAgentInput
    client_method = "unfollow_agent"


class MoltbookGetPersonalFeedTool(MoltbookMethodTool):
    name = "moltbook_get_personal_feed"
    description = "Get personalized feed"
    Input = PersonalFeedInput
    client_method = "get_personal_feed"


class MoltbookSearchTool(MoltbookMethodTool):
    name = "moltbook_search"
    description = "Search posts and comments"
    Input = SearchInput
    client_method = "search"


class MoltbookPinPostTool(MoltbookMethodTool):
    name = "moltbook_pin_post"
    description = "Pin a post"
    Input = PostIdInput
    client_method = "pin_post"


class MoltbookUnpinPostTool(MoltbookMethodTool):
    name = "moltbook_unpin_post"
    description = "Unpin a post"
    Input = PostIdInput
    client_method = "unpin_post"


class MoltbookUpdateSubmoltSettingsTool(MoltbookMethodTool):
    name = "moltbook_update_submolt_settings"
    description = "Update submolt settings"
    Input = UpdateSubmoltSettingsInput
    client_method = "update_submolt_settings"


class MoltbookUploadSubmoltAvatarTool(MoltbookMethodTool):
    name = "moltbook_upload_submolt_avatar"
    description = "Upload submolt avatar"
    Input = UploadSubmoltAssetInput
    client_method = "upload_submolt_avatar"


class MoltbookUploadSubmoltBannerTool(MoltbookMethodTool):
    name = "moltbook_upload_submolt_banner"
    description = "Upload submolt banner"
    Input = UploadSubmoltAssetInput
    client_method = "upload_submolt_banner"


class MoltbookAddModeratorTool(MoltbookMethodTool):
    name = "moltbook_add_moderator"
    description = "Add a submolt moderator"
    Input = AddModeratorInput
    client_method = "add_moderator"


class MoltbookRemoveModeratorTool(MoltbookMethodTool):
    name = "moltbook_remove_moderator"
    description = "Remove a submolt moderator"
    Input = RemoveModeratorInput
    client_method = "remove_moderator"


class MoltbookListModeratorsTool(MoltbookMethodTool):
    name = "moltbook_list_moderators"
    description = "List submolt moderators"
    Input = ListModeratorsInput
    client_method = "list_moderators"


moltbook_register_agent = MoltbookRegisterAgentTool()
moltbook_get_my_profile = MoltbookGetMyProfileTool()
moltbook_get_claim_status = MoltbookGetClaimStatusTool()
moltbook_update_profile = MoltbookUpdateProfileTool()
moltbook_upload_avatar = MoltbookUploadAvatarTool()
moltbook_delete_avatar = MoltbookDeleteAvatarTool()
moltbook_get_agent_profile = MoltbookGetAgentProfileTool()

moltbook_create_post = MoltbookCreatePostTool()
moltbook_create_link_post = MoltbookCreateLinkPostTool()
moltbook_get_feed = MoltbookGetFeedTool()
moltbook_get_submolt_posts = MoltbookGetSubmoltPostsTool()
moltbook_get_submolt_feed = MoltbookGetSubmoltFeedTool()
moltbook_get_post = MoltbookGetPostTool()
moltbook_delete_post = MoltbookDeletePostTool()

moltbook_add_comment = MoltbookAddCommentTool()
moltbook_reply_to_comment = MoltbookReplyToCommentTool()
moltbook_get_comments = MoltbookGetCommentsTool()

moltbook_upvote_post = MoltbookUpvotePostTool()
moltbook_downvote_post = MoltbookDownvotePostTool()
moltbook_upvote_comment = MoltbookUpvoteCommentTool()

moltbook_create_submolt = MoltbookCreateSubmoltTool()
moltbook_list_submolts = MoltbookListSubmoltsTool()
moltbook_get_submolt = MoltbookGetSubmoltTool()
moltbook_subscribe_submolt = MoltbookSubscribeSubmoltTool()
moltbook_unsubscribe_submolt = MoltbookUnsubscribeSubmoltTool()

moltbook_follow_agent = MoltbookFollowAgentTool()
moltbook_unfollow_agent = MoltbookUnfollowAgentTool()

moltbook_get_personal_feed = MoltbookGetPersonalFeedTool()
moltbook_search = MoltbookSearchTool()

moltbook_pin_post = MoltbookPinPostTool()
moltbook_unpin_post = MoltbookUnpinPostTool()
moltbook_update_submolt_settings = MoltbookUpdateSubmoltSettingsTool()
moltbook_upload_submolt_avatar = MoltbookUploadSubmoltAvatarTool()
moltbook_upload_submolt_banner = MoltbookUploadSubmoltBannerTool()
moltbook_add_moderator = MoltbookAddModeratorTool()
moltbook_remove_moderator = MoltbookRemoveModeratorTool()
moltbook_list_moderators = MoltbookListModeratorsTool()
