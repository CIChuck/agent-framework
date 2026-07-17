# mypy: ignore-errors
"""
Web fetching tools.

Ref: docs/reference/specs/tool_specification.md - Category 5: Web Fetch
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from ..definition import BaseTool


class WebFetchTool(BaseTool):
    """Fetch a webpage and convert to markdown."""

    @property
    def name(self) -> str:
        return "web_fetch"

    @property
    def description(self) -> str:
        return "Fetch a webpage and convert its content to markdown."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL of the webpage to fetch",
                },
                "include_images": {
                    "type": "boolean",
                    "description": "Include image markdown in output",
                    "default": False,
                },
                "include_links": {
                    "type": "boolean",
                    "description": "Include hyperlinks in output",
                    "default": True,
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum length of returned content",
                    "default": 10000,
                },
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        include_images = kwargs.get("include_images", False)
        include_links = kwargs.get("include_links", True)
        max_length = kwargs.get("max_length", 10000)

        try:
            async with httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
            ) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; FridayBot/1.0)"},
                )
                response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()

            # Convert to markdown
            markdown = md(
                str(soup),
                strip=["img"] if not include_images else [],
                convert=["a"] if include_links else [],
            )

            # Clean up
            lines = markdown.split("\n")
            cleaned_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped:
                    cleaned_lines.append(stripped)

            result = "\n\n".join(cleaned_lines)

            if len(result) > max_length:
                result = result[:max_length] + "\n\n...(truncated)"

            return result

        except httpx.HTTPStatusError as e:
            return f"Error: HTTP {e.response.status_code} - {e.response.reason_phrase}"
        except Exception as e:
            return f"Error: Failed to fetch URL: {e}"


class WebScreenshotTool(BaseTool):
    """Take a screenshot of a webpage (stub)."""

    @property
    def name(self) -> str:
        return "web_screenshot"

    @property
    def description(self) -> str:
        return "Take a screenshot of a webpage. (Not yet implemented)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL of the webpage to screenshot",
                },
                "width": {
                    "type": "integer",
                    "description": "Viewport width in pixels",
                    "default": 1280,
                },
                "height": {
                    "type": "integer",
                    "description": "Viewport height in pixels",
                    "default": 800,
                },
                "full_page": {
                    "type": "boolean",
                    "description": "Capture full page (not just viewport)",
                    "default": False,
                },
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        # This is a stub - would require playwright or selenium
        return (
            "Error: web_screenshot is not yet implemented. "
            "This feature requires a headless browser (e.g., Playwright)."
        )


class WebExtractLinksTool(BaseTool):
    """Extract all links from a webpage."""

    @property
    def name(self) -> str:
        return "web_extract_links"

    @property
    def description(self) -> str:
        return "Extract all hyperlinks from a webpage."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL of the webpage",
                },
                "include_internal": {
                    "type": "boolean",
                    "description": "Include internal links (same domain)",
                    "default": True,
                },
                "include_external": {
                    "type": "boolean",
                    "description": "Include external links",
                    "default": True,
                },
                "max_links": {
                    "type": "integer",
                    "description": "Maximum number of links to return",
                    "default": 100,
                },
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        include_internal = kwargs.get("include_internal", True)
        include_external = kwargs.get("include_external", True)
        max_links = kwargs.get("max_links", 100)

        try:
            async with httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
            ) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; FridayBot/1.0)"},
                )
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            base_domain = urlparse(url).netloc

            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                text = a.get_text(strip=True)[:50]

                # Resolve relative URLs
                full_url = urljoin(url, href)
                parsed = urlparse(full_url)

                # Skip non-http URLs
                if parsed.scheme not in ("http", "https"):
                    continue

                # Filter by internal/external
                is_internal = parsed.netloc == base_domain
                if is_internal and not include_internal:
                    continue
                if not is_internal and not include_external:
                    continue

                links.append(
                    {
                        "url": full_url,
                        "text": text or "(no text)",
                        "type": "internal" if is_internal else "external",
                    }
                )

                if len(links) >= max_links:
                    break

            if not links:
                return "No links found on page"

            # Format output
            output_lines = []
            for link in links:
                output_lines.append(f"[{link['type']}] {link['text']}")
                output_lines.append(f"  {link['url']}")

            return "\n".join(output_lines)

        except httpx.HTTPStatusError as e:
            return f"Error: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error: Failed to extract links: {e}"


class WebExtractTextTool(BaseTool):
    """Extract main text content from a webpage."""

    @property
    def name(self) -> str:
        return "web_extract_text"

    @property
    def description(self) -> str:
        return (
            "Extract the main text content from a webpage, removing navigation and ads."
        )

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL of the webpage",
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum length of extracted text",
                    "default": 5000,
                },
            },
            "required": ["url"],
        }

    async def execute(self, **kwargs: Any) -> str:
        url = kwargs["url"]
        max_length = kwargs.get("max_length", 5000)

        try:
            async with httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
            ) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; FridayBot/1.0)"},
                )
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements
            for element in soup(
                [
                    "script",
                    "style",
                    "nav",
                    "footer",
                    "header",
                    "aside",
                    "form",
                    "button",
                    "input",
                    "select",
                    "noscript",
                    "iframe",
                    "svg",
                ]
            ):
                element.decompose()

            # Try to find main content
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", class_="content")
                or soup.find("div", id="content")
                or soup.body
            )

            if not main_content:
                return "Error: Could not find main content"

            # Extract text
            text = main_content.get_text(separator="\n", strip=True)

            # Clean up whitespace
            lines = []
            for line in text.split("\n"):
                stripped = line.strip()
                if stripped:
                    lines.append(stripped)

            result = "\n".join(lines)

            if len(result) > max_length:
                result = result[:max_length] + "\n...(truncated)"

            return result

        except httpx.HTTPStatusError as e:
            return f"Error: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error: Failed to extract text: {e}"


# Convenience instances
web_fetch = WebFetchTool()
web_screenshot = WebScreenshotTool()
web_extract_links = WebExtractLinksTool()
web_extract_text = WebExtractTextTool()
