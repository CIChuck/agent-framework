"""Moltbook API client package."""

from .client import Moltbook
from .config import MoltbookConfig
from .errors import (
    MoltbookConfigError,
    MoltbookError,
    MoltbookResponseError,
    MoltbookValidationError,
)
from .models.agent import Agent, AgentProfileWithRecent, AuthorRef, Owner
from .models.comment import Comment
from .models.moderation import Moderator
from .models.post import Post
from .models.results import (
    ClaimStatus,
    DeleteResult,
    FollowResult,
    ModeratorResult,
    PinResult,
    RegisterResult,
    SubscribeResult,
    UploadResult,
    VoteResult,
)
from .models.search import SearchResultItem, SearchResults
from .models.submolt import Submolt, SubmoltRef
from .responses import MoltbookResponse

__all__ = [
    "Moltbook",
    "MoltbookConfig",
    "MoltbookResponse",
    "MoltbookError",
    "MoltbookConfigError",
    "MoltbookValidationError",
    "MoltbookResponseError",
    "Agent",
    "Owner",
    "AuthorRef",
    "AgentProfileWithRecent",
    "Post",
    "Comment",
    "Submolt",
    "SubmoltRef",
    "SearchResultItem",
    "SearchResults",
    "Moderator",
    "RegisterResult",
    "ClaimStatus",
    "UploadResult",
    "DeleteResult",
    "VoteResult",
    "FollowResult",
    "SubscribeResult",
    "PinResult",
    "ModeratorResult",
]

__version__ = "0.1.0a3"
