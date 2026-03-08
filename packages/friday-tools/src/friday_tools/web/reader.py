# mypy: ignore-errors
"""
Web reader tool for fetching and extracting content from web pages.

Provides a production-ready tool for reading web content with:
- SSRF protection
- Response size limiting
- Multiple output formats (markdown, text, html, json)
- Metadata extraction (title, description, Open Graph)
- Configurable via WebConfig

Ref: docs/specs/tool_specification.md - Category 5: Web Fetch
"""

from __future__ import annotations

import json
import logging
from typing import Any, Literal

from bs4 import BeautifulSoup
from charset_normalizer import from_bytes
from markdownify import markdownify as md
from pydantic import BaseModel, Field

from ..base import FridayTool, ToolResult
from .client import ResponseTooLargeError, create_http_client, fetch_with_limit
from .config import DEFAULT_WEB_CONFIG, WebConfig
from .validators import URLValidationError, validate_url

logger = logging.getLogger(__name__)


class WebReaderInput(BaseModel):
    """Input schema for WebReaderTool."""

    url: str = Field(..., description="URL to read")
    output_format: Literal["auto", "markdown", "text", "html", "json"] = Field(
        default="auto",
        description="Output format (auto detects from Content-Type)",
    )
    max_length: int = Field(
        default=50000,
        ge=1000,
        le=500000,
        description="Maximum output length in characters",
    )
    include_metadata: bool = Field(
        default=False,
        description="Include page metadata (title, description, links)",
    )
    include_links: bool = Field(
        default=True,
        description="Include hyperlinks in markdown output",
    )
    include_images: bool = Field(
        default=False,
        description="Include image references in markdown output",
    )


class WebReaderTool(FridayTool):
    """
    Read and extract content from web pages.

    Features:
    - Auto-detects content type (HTML, JSON, plain text)
    - Converts HTML to clean markdown
    - Extracts main content (removes nav, ads, scripts)
    - Optional metadata extraction (title, description, links)
    - Security: SSRF protection, response size limits
    - Configurable via WebConfig (timeout, proxy, SSL, etc.)

    Example:
        reader = WebReaderTool()
        result = await reader.run(WebReaderInput(url="https://example.com"))
        print(result.content)  # Markdown content
    """

    name = "web_reader"
    description = (
        "Read and extract content from web pages, converting to markdown or plain text. "  # noqa: E501
        "Supports HTML, JSON, and plain text content types."
    )
    category = "web"
    tags = ["read-only", "async", "scraping"]
    Input = WebReaderInput

    def __init__(self, config: WebConfig | dict | None = None):
        """
        Initialize WebReaderTool with configuration.

        Args:
            config: WebConfig instance, dict from YAML, or None for defaults
        """
        if config is None:
            self._config = DEFAULT_WEB_CONFIG
        elif isinstance(config, dict):
            self._config = WebConfig.from_dict(config)
        else:
            self._config = config

    async def run(self, args: WebReaderInput) -> ToolResult:
        """
        Fetch and extract content from a URL.

        Args:
            args: Validated WebReaderInput

        Returns:
            ToolResult with extracted content and optional metadata
        """
        # 1. Validate URL (SSRF protection)
        try:
            validated_url = validate_url(
                args.url,
                allow_private_ips=self._config.security.allow_private_ips,
                blocked_hosts=set(self._config.security.blocked_hosts),
            )
        except URLValidationError as e:
            return ToolResult(
                content=f"URL validation failed: {e}",
                error=str(e),
            )

        # 2. Fetch content with size limit
        try:
            async with create_http_client(self._config) as client:
                content_bytes, headers = await fetch_with_limit(
                    client,
                    validated_url,
                    max_bytes=self._config.client.max_response_size,
                )
        except ResponseTooLargeError as e:
            return ToolResult(
                content=f"Response too large: {e.size} bytes (max: {e.max_size})",
                error=str(e),
            )
        except Exception as e:
            error_msg = f"Failed to fetch URL: {type(e).__name__}: {e}"
            logger.warning(error_msg)
            return ToolResult(content=error_msg, error=str(e))

        # 3. Detect content type
        content_type = headers.get("content-type", "text/html").lower()

        # 4. Determine output format
        output_format = args.output_format
        if output_format == "auto":
            output_format = self._detect_format(content_type)

        # 5. Parse content based on type
        try:
            text, metadata = self._parse_content(
                content_bytes, content_type, output_format, args
            )
        except Exception as e:
            error_msg = f"Failed to parse content: {type(e).__name__}: {e}"
            logger.warning(error_msg)
            return ToolResult(content=error_msg, error=str(e))

        # 6. Truncate if needed
        truncated = False
        if len(text) > args.max_length:
            text = text[: args.max_length] + "\n\n...(truncated)"
            truncated = True

        # 7. Build result
        result_metadata: dict[str, Any] = {
            "url": validated_url,
            "content_type": content_type,
            "output_format": output_format,
            "truncated": truncated,
            "content_length": len(text),
        }

        if args.include_metadata and metadata:
            result_metadata["page"] = metadata

        return ToolResult(
            content=text,
            data={"text": text, "metadata": metadata} if metadata else None,
            metadata=result_metadata,
        )

    def _detect_format(
        self, content_type: str
    ) -> Literal["markdown", "text", "html", "json"]:
        """Detect output format from Content-Type header."""
        if "application/json" in content_type:
            return "json"
        elif "text/html" in content_type or "text/markdown" in content_type:
            return "markdown"
        elif "text/plain" in content_type:
            return "text"
        else:
            # Default to markdown (will try HTML parsing)
            return "markdown"

    def _parse_content(
        self,
        content: bytes,
        content_type: str,
        output_format: str,
        args: WebReaderInput,
    ) -> tuple[str, dict | None]:
        """
        Parse content based on type and format.

        Returns:
            Tuple of (text_content, metadata_dict or None)
        """
        metadata: dict | None = None

        if output_format == "json":
            text = self._parse_json(content)
        elif output_format == "html":
            text = self._decode_content(content)
        elif output_format == "text":
            if "text/html" in content_type:
                text, metadata = self._parse_html_to_text(content, args)
            else:
                text = self._decode_content(content)
        else:  # markdown
            if "text/html" in content_type or "text/xml" in content_type:
                text, metadata = self._parse_html_to_markdown(content, args)
            else:
                text = self._decode_content(content)

        return text, metadata

    def _decode_content(self, content: bytes) -> str:
        """Decode bytes to string with encoding detection."""
        result = from_bytes(content)
        best = result.best()
        if best:
            return str(best)
        # Fallback to UTF-8 with error handling
        return content.decode("utf-8", errors="replace")

    def _parse_json(self, content: bytes) -> str:
        """Parse and pretty-print JSON content."""
        text = self._decode_content(content)
        try:
            data = json.loads(text)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            return text

    def _parse_html_to_markdown(
        self, content: bytes, args: WebReaderInput
    ) -> tuple[str, dict | None]:
        """
        Parse HTML and convert to markdown.

        Returns:
            Tuple of (markdown_text, metadata_dict or None)
        """
        text = self._decode_content(content)
        soup = BeautifulSoup(text, "lxml")

        # Extract metadata before removing elements
        metadata = self._extract_metadata(soup) if args.include_metadata else None

        # Remove unwanted elements
        for tag_name in self._config.reader.remove_elements:
            for element in soup.find_all(tag_name):
                element.decompose()

        # Find main content
        main_content = self._find_main_content(soup)

        # Convert to markdown
        strip_tags = []
        if not args.include_images:
            strip_tags.append("img")
        if not args.include_links:
            strip_tags.append("a")

        markdown = md(
            str(main_content),
            strip=strip_tags if strip_tags else None,
            heading_style="atx",
        )

        # Clean up whitespace
        lines = []
        for line in markdown.split("\n"):
            stripped = line.strip()
            if stripped:
                lines.append(stripped)

        return "\n\n".join(lines), metadata

    def _parse_html_to_text(
        self, content: bytes, args: WebReaderInput
    ) -> tuple[str, dict | None]:
        """
        Parse HTML and extract plain text.

        Returns:
            Tuple of (plain_text, metadata_dict or None)
        """
        text = self._decode_content(content)
        soup = BeautifulSoup(text, "lxml")

        # Extract metadata before removing elements
        metadata = self._extract_metadata(soup) if args.include_metadata else None

        # Remove unwanted elements
        for tag_name in self._config.reader.remove_elements:
            for element in soup.find_all(tag_name):
                element.decompose()

        # Find main content
        main_content = self._find_main_content(soup)

        # Extract text
        plain_text = main_content.get_text(separator="\n", strip=True)

        # Clean up whitespace
        lines = []
        for line in plain_text.split("\n"):
            stripped = line.strip()
            if stripped:
                lines.append(stripped)

        return "\n".join(lines), metadata

    def _find_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Find the main content area of an HTML document.

        Tries to locate <main>, <article>, or common content containers.
        Falls back to <body> if no specific container is found.
        """
        # Try semantic elements first
        main = soup.find("main")
        if main:
            return main

        article = soup.find("article")
        if article:
            return article

        # Try common class/id patterns
        for selector in [
            {"class_": "content"},
            {"class_": "main-content"},
            {"class_": "post-content"},
            {"class_": "article-content"},
            {"id": "content"},
            {"id": "main-content"},
            {"id": "main"},
        ]:
            element = soup.find("div", **selector)
            if element:
                return element

        # Fall back to body
        return soup.body if soup.body else soup

    def _extract_metadata(self, soup: BeautifulSoup) -> dict[str, Any]:
        """Extract page metadata from HTML."""
        metadata: dict[str, Any] = {}

        # Title
        if soup.title and soup.title.string:
            metadata["title"] = soup.title.string.strip()

        # Meta description
        desc = soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            metadata["description"] = desc["content"]

        # Canonical URL
        canonical = soup.find("link", attrs={"rel": "canonical"})
        if canonical and canonical.get("href"):
            metadata["canonical_url"] = canonical["href"]

        # Language
        if soup.html and soup.html.get("lang"):
            metadata["language"] = soup.html["lang"]

        # Open Graph
        og_title = soup.find("meta", attrs={"property": "og:title"})
        if og_title and og_title.get("content"):
            metadata["og_title"] = og_title["content"]

        og_description = soup.find("meta", attrs={"property": "og:description"})
        if og_description and og_description.get("content"):
            metadata["og_description"] = og_description["content"]

        og_image = soup.find("meta", attrs={"property": "og:image"})
        if og_image and og_image.get("content"):
            metadata["og_image"] = og_image["content"]

        # Link count
        metadata["link_count"] = len(soup.find_all("a", href=True))

        return metadata


# Convenience instance with default configuration
web_reader = WebReaderTool()
