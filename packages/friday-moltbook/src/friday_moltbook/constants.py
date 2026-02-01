"""Constants for Moltbook client."""

BASE_URL = "https://www.moltbook.com/api/v1"

ALLOWED_SORT_GLOBAL = {"hot", "new", "top", "rising"}
ALLOWED_SORT_COMMENTS = {"top", "new", "controversial"}
ALLOWED_SORT_FEED = {"hot", "new", "top"}
ALLOWED_SEARCH_TYPES = {"posts", "comments", "all"}

MAX_SEARCH_QUERY_LENGTH = 500
MAX_SEARCH_LIMIT = 50

MAX_AVATAR_SIZE_BYTES = 500 * 1024
MAX_BANNER_SIZE_BYTES = 2 * 1024 * 1024

ALLOWED_AVATAR_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
