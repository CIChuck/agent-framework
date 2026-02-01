"""Moltbook API client package."""

from .client import Moltbook
from .config import MoltbookConfig
from .errors import (
    MoltbookError,
    MoltbookConfigError,
    MoltbookValidationError,
    MoltbookResponseError,
)
from .responses import MoltbookResponse
from .models.agent import Agent, Owner, AgentProfileWithRecent, AuthorRef
from .models.post import Post
from .models.comment import Comment
from .models.submolt import Submolt, SubmoltRef
from .models.search import SearchResultItem, SearchResults
from .models.moderation import Moderator
from .models.results import (
    RegisterResult,
    ClaimStatus,
    UploadResult,
    DeleteResult,
    VoteResult,
    FollowResult,
    SubscribeResult,
    PinResult,
    ModeratorResult,
)

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

__version__ = "0.1.0"
