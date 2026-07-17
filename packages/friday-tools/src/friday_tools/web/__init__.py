# mypy: ignore-errors
"""
Web tools for HTTP requests and web scraping.

Ref: docs/reference/specs/tool_specification.md - Categories 5-6: Web Tools

Provides tools for web search, fetching, content reading, and HTTP operations.
"""

# Configuration
# HTTP Client utilities
from .client import (
    ResponseTooLargeError,
    create_http_client,
    fetch_with_limit,
    format_http_response,
)
from .config import (
    DEFAULT_WEB_CONFIG,
    HttpClientConfig,
    ProxyConfig,
    ReaderConfig,
    SecurityConfig,
    SSLConfig,
    WebConfig,
)

# Legacy fetch tools (kept for backwards compatibility)
from .fetch import web_extract_links, web_extract_text, web_fetch, web_screenshot

# HTTP tools (classes and convenience instances)
from .http import (
    HttpDeleteTool,
    HttpDownloadTool,
    HttpGetTool,
    HttpPostTool,
    HttpPutTool,
    HttpUploadTool,
    http_delete,
    http_download,
    http_get,
    http_post,
    http_put,
    http_upload,
)

# WebReaderTool (primary content extraction tool)
from .reader import WebReaderInput, WebReaderTool, web_reader

# Search
from .search import WebSearchTool, web_search
from .serper import SerperSearchTool, serper_search

# URL validation and security
from .validators import URLValidationError, is_safe_url, validate_url

__all__ = [
    # Configuration
    "WebConfig",
    "HttpClientConfig",
    "SSLConfig",
    "ProxyConfig",
    "SecurityConfig",
    "ReaderConfig",
    "DEFAULT_WEB_CONFIG",
    # Client utilities
    "create_http_client",
    "fetch_with_limit",
    "format_http_response",
    "ResponseTooLargeError",
    # Validation
    "validate_url",
    "is_safe_url",
    "URLValidationError",
    # WebReaderTool
    "WebReaderTool",
    "WebReaderInput",
    "web_reader",
    # Search
    "WebSearchTool",
    "web_search",
    "SerperSearchTool",
    "serper_search",
    # Legacy Fetch tools
    "web_fetch",
    "web_screenshot",
    "web_extract_links",
    "web_extract_text",
    # HTTP tool classes
    "HttpGetTool",
    "HttpPostTool",
    "HttpPutTool",
    "HttpDeleteTool",
    "HttpDownloadTool",
    "HttpUploadTool",
    # HTTP tool instances
    "http_get",
    "http_post",
    "http_put",
    "http_delete",
    "http_download",
    "http_upload",
]
