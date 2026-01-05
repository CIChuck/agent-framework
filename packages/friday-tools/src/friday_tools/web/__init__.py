"""
Web tools for HTTP requests and web scraping.

Ref: docs/specs/tool_specification.md - Categories 5-6: Web Tools

Provides 11 tools for web search, fetching, and HTTP operations.
"""

from .fetch import web_extract_links, web_extract_text, web_fetch, web_screenshot
from .http import http_delete, http_download, http_get, http_post, http_put, http_upload
from .search import web_search

__all__ = [
    # Search
    "web_search",
    # Fetch
    "web_fetch",
    "web_screenshot",
    "web_extract_links",
    "web_extract_text",
    # HTTP
    "http_get",
    "http_post",
    "http_put",
    "http_delete",
    "http_download",
    "http_upload",
]
