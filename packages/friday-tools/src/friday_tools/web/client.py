# mypy: ignore-errors
"""
Shared HTTP client factory and utilities.

Provides a configured httpx AsyncClient based on WebConfig settings,
with support for retries, proxies, SSL configuration, and response size limiting.

Ref: docs/specs/tool_specification.md - Category 5-6: Web Tools
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import httpx

from .config import DEFAULT_WEB_CONFIG, WebConfig

if TYPE_CHECKING:
    from collections.abc import Mapping


class ResponseTooLargeError(Exception):
    """Raised when a response exceeds the maximum allowed size."""

    def __init__(self, size: int, max_size: int):
        self.size = size
        self.max_size = max_size
        super().__init__(f"Response too large: {size} bytes (max: {max_size})")


def create_http_client(config: WebConfig | None = None) -> httpx.AsyncClient:
    """
    Create a configured async HTTP client from WebConfig.

    The client is configured with:
    - Timeout from config.client.timeout
    - Retries from config.client.max_retries
    - Redirect following from config.client.follow_redirects
    - User-Agent header from config.client.user_agent
    - Proxy settings from config.proxy
    - SSL verification from config.ssl

    Args:
        config: WebConfig instance, or None for defaults

    Returns:
        Configured httpx.AsyncClient (use as async context manager)

    Example:
        async with create_http_client(config) as client:
            response = await client.get(url)
    """
    cfg = config or DEFAULT_WEB_CONFIG

    # Build proxy dict if configured
    proxy: str | dict[str, str] | None = None
    if cfg.proxy.http or cfg.proxy.https:
        proxy = {}
        if cfg.proxy.http:
            proxy["http://"] = cfg.proxy.http
        if cfg.proxy.https:
            proxy["https://"] = cfg.proxy.https

    # Build SSL verification setting
    # Can be: True, False, or path to CA bundle
    verify: bool | str = cfg.ssl.ca_bundle if cfg.ssl.ca_bundle else cfg.ssl.verify

    # Create transport with retry support
    transport = httpx.AsyncHTTPTransport(retries=cfg.client.max_retries)

    return httpx.AsyncClient(
        transport=transport,
        timeout=httpx.Timeout(cfg.client.timeout),
        follow_redirects=cfg.client.follow_redirects,
        headers={"User-Agent": cfg.client.user_agent},
        proxy=proxy,
        verify=verify,
    )


async def fetch_with_limit(
    client: httpx.AsyncClient,
    url: str,
    max_bytes: int,
    method: str = "GET",
    **kwargs,
) -> tuple[bytes, httpx.Headers]:
    """
    Fetch a URL with response size limiting (streaming).

    This function streams the response and enforces a maximum size limit
    to prevent memory exhaustion from large responses.

    Args:
        client: httpx.AsyncClient to use for the request
        url: URL to fetch
        max_bytes: Maximum response size in bytes
        method: HTTP method (default: GET)
        **kwargs: Additional arguments passed to client.stream()

    Returns:
        Tuple of (content_bytes, response_headers)

    Raises:
        ResponseTooLargeError: If response exceeds max_bytes
        httpx.HTTPStatusError: If response status indicates an error
    """
    async with client.stream(method, url, **kwargs) as response:
        response.raise_for_status()

        # Check Content-Length header if available
        content_length = response.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > max_bytes:
                    raise ResponseTooLargeError(length, max_bytes)
            except ValueError:
                pass  # Invalid Content-Length header, continue with streaming

        # Stream and accumulate chunks with size check
        chunks: list[bytes] = []
        total = 0

        async for chunk in response.aiter_bytes(chunk_size=8192):
            total += len(chunk)
            if total > max_bytes:
                raise ResponseTooLargeError(total, max_bytes)
            chunks.append(chunk)

        return b"".join(chunks), response.headers


def format_http_response(
    response: httpx.Response,
    max_body_length: int = 5000,
    include_headers: bool = True,
) -> str:
    """
    Format an HTTP response for human-readable output.

    Used by HTTP tools (http_get, http_post, etc.) to format responses
    in a consistent, readable format.

    Args:
        response: httpx.Response to format
        max_body_length: Maximum body length before truncation
        include_headers: Whether to include response headers

    Returns:
        Formatted string representation of the response
    """
    lines = [
        f"Status: {response.status_code} {response.reason_phrase}",
    ]

    if include_headers:
        lines.append("")
        lines.append("Headers:")
        for key, value in response.headers.items():
            lines.append(f"  {key}: {value}")

    lines.append("")
    lines.append("Body:")

    # Try to parse and pretty-print JSON
    content_type = response.headers.get("content-type", "")
    body: str

    if "application/json" in content_type:
        try:
            data = response.json()
            body = json.dumps(data, indent=2, ensure_ascii=False)
        except Exception:
            body = response.text
    else:
        body = response.text

    # Truncate if needed
    if len(body) > max_body_length:
        lines.append(body[:max_body_length])
        lines.append("\n...(truncated)")
    else:
        lines.append(body)

    return "\n".join(lines)


def format_headers(headers: Mapping[str, str]) -> str:
    """
    Format HTTP headers as a string.

    Args:
        headers: Headers mapping

    Returns:
        Formatted headers string
    """
    lines = []
    for key, value in headers.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)
