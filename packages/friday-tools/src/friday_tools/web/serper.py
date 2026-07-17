# mypy: ignore-errors
"""
Serper.dev web search tool.

Ref: docs/reference/specs/tool_specification.md - Category 5: Web Search

Provides Google search results via Serper.dev SERP API. More reliable than
scraping, returns structured results with URLs, titles, and snippets.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from ..definition import BaseTool
from .config import DEFAULT_WEB_CONFIG, WebConfig

logger = logging.getLogger(__name__)

# Serper.dev API endpoint
SERPER_API_URL = "https://google.serper.dev"


class SerperSearchError(Exception):
    """Raised when Serper search fails."""

    def __init__(self, message: str, *, recoverable: bool = False, query: str = ""):
        super().__init__(message)
        self.recoverable = recoverable
        self.query = query


class SerperSearchTool(BaseTool):
    """
    Search the web using Serper.dev Google SERP API.

    More reliable than scraping, returns structured Google search results.
    Requires API key in config (web.serper_api_key).

    API Reference: https://serper.dev/docs
    """

    def __init__(self, config: WebConfig | dict | None = None):
        """
        Initialize Serper search tool.

        Args:
            config: Optional WebConfig or dict with serper_api_key.
                   Accepts WebConfig object, dict (from YAML), or None.
                   Uses DEFAULT_WEB_CONFIG if not provided.
        """
        logger.debug(
            f"SerperSearchTool.__init__ called with config type: {type(config)}"
        )
        if config is None:
            self._config = DEFAULT_WEB_CONFIG
        elif isinstance(config, dict):
            self._config = WebConfig.from_dict(config)
            logger.debug("Converted dict to WebConfig")
        else:
            self._config = config
        logger.debug(f"self._config type after init: {type(self._config)}")

    @property
    def name(self) -> str:
        return "serper_search"

    @property
    def description(self) -> str:
        return (
            "Search Google using Serper.dev API. Returns URLs, titles, and snippets. "
            "More reliable than scraping. Use for: finding documentation, "
            "researching topics, discovering current information, news searches. "
            "Supports regular web search, news, and image search types."
        )

    @property
    def category(self) -> str:
        return "web"

    @property
    def tags(self) -> list[str]:
        return ["search", "read-only", "internet", "google", "serp"]

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Search query. Be specific for better results. "
                        "Examples: 'Python asyncio tutorial', "
                        "'latest React documentation 2024', "
                        "'how to configure nginx reverse proxy'"
                    ),
                },
                "max_results": {
                    "type": "integer",
                    "description": (
                        "Maximum number of results to return (1-100). "
                        "Default is 10. Serper allows up to 100 results per request."
                    ),
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100,
                },
                "search_type": {
                    "type": "string",
                    "enum": ["search", "news", "images"],
                    "description": (
                        "Type of search to perform. "
                        "'search' for general web (default), "
                        "'news' for recent news articles, "
                        "'images' for image search."
                    ),
                    "default": "search",
                },
            },
            "required": ["query"],
        }

    async def execute(self, **kwargs: Any) -> str:
        """
        Execute Serper search and return formatted results.

        Returns:
            Formatted search results with titles, URLs, and snippets.
            On error, returns a descriptive error message with recovery suggestions.
        """
        query = kwargs.get("query", "").strip()
        if not query:
            return "Error: Search query is required. Please provide a search term."

        max_results = kwargs.get("max_results", 10)
        if not isinstance(max_results, int) or max_results < 1:
            max_results = 10
        max_results = min(max_results, 100)

        search_type = kwargs.get("search_type", "search")
        if search_type not in ("search", "news", "images"):
            search_type = "search"

        # Validate API key
        if isinstance(self._config, dict):
            logger.error(f"BUG: self._config is still a dict: {self._config}")
            self._config = WebConfig.from_dict(self._config)

        api_key = self._config.serper_api_key
        if not api_key:
            return (
                "Error: Serper API key not configured. "
                "Please add 'serper_api_key' to the web section of your config.yaml. "
                "Get an API key from https://serper.dev"
            )

        logger.debug(
            f"Serper search: query='{query}', max_results={max_results}, "
            f"search_type={search_type}"
        )

        timeout = self._config.client.timeout
        max_retries = self._config.client.max_retries

        # Determine endpoint based on search type
        endpoint = f"{SERPER_API_URL}/{search_type}"

        # Build request payload for Serper.dev API
        payload = {
            "q": query,
            "num": max_results,
        }

        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        }

        last_error: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        endpoint,
                        json=payload,
                        headers=headers,
                    )

                    # Handle specific HTTP errors
                    if response.status_code == 401:
                        logger.error("Serper API key invalid or unauthorized")
                        return (
                            "Error: Serper API key is invalid or unauthorized. "
                            "Please check your API key at https://serper.dev"
                        )

                    if response.status_code == 403:
                        logger.error("Serper API access forbidden")
                        return (
                            "Error: Serper API access forbidden. "
                            "Your API key may be suspended or rate limited. "
                            "Check your account at https://serper.dev"
                        )

                    if response.status_code == 429:
                        logger.warning(f"Serper rate limited (attempt {attempt + 1})")
                        if attempt < max_retries:
                            await asyncio.sleep(2**attempt)  # Exponential backoff
                            continue
                        return (
                            "Error: Serper API rate limit exceeded. "
                            "Please wait a moment and try again, or upgrade your plan."
                        )

                    if response.status_code >= 500:
                        logger.warning(f"Serper server error: {response.status_code}")
                        if attempt < max_retries:
                            await asyncio.sleep(1)
                            continue
                        return (
                            f"Error: Serper service unavailable "
                            f"(HTTP {response.status_code}). "
                            "Please try again later."
                        )

                    response.raise_for_status()

                    # Parse JSON response
                    data = response.json()

                    # Format results based on search type
                    if search_type == "search":
                        return self._format_web_results(query, data, max_results)
                    elif search_type == "news":
                        return self._format_news_results(query, data, max_results)
                    elif search_type == "images":
                        return self._format_image_results(query, data, max_results)
                    else:
                        return self._format_web_results(query, data, max_results)

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(
                    f"Serper timeout (attempt {attempt + 1}/{max_retries + 1}): {e}"
                )
                if attempt < max_retries:
                    continue
                return (
                    f"Error: Serper request timed out after {timeout}s. "
                    "Please try again or check your network connection."
                )

            except httpx.ConnectError as e:
                last_error = e
                logger.error(f"Connection error to Serper API: {e}")
                return (
                    "Error: Could not connect to Serper API. "
                    "Please check your network connection and try again."
                )

            except httpx.HTTPStatusError as e:
                last_error = e
                logger.error(f"Serper HTTP error: {e.response.status_code}")
                return (
                    f"Error: Serper request failed with HTTP {e.response.status_code}. "
                    f"Reason: {e.response.reason_phrase or 'Unknown'}. "
                    "Please try again later."
                )

            except Exception as e:
                last_error = e
                logger.exception(f"Unexpected error during Serper search: {e}")
                return (
                    f"Error: Search failed unexpectedly ({type(e).__name__}). "
                    f"Details: {str(e)[:200]}. "
                    "Please try again or report this issue if it persists."
                )

        # Should not reach here, but just in case
        logger.error(f"Serper search failed after all retries: {last_error}")
        return (
            f"Error: Search failed after {max_retries + 1} attempts. "
            "Please try again later."
        )

    def _format_web_results(self, query: str, data: dict, max_results: int) -> str:
        """Format regular web search results."""
        organic = data.get("organic", [])

        if not organic:
            logger.info(f"No results found for query: {query}")
            return (
                f"No results found for: '{query}'. "
                "Try different keywords or a broader search."
            )

        results = []
        for item in organic[:max_results]:
            title = item.get("title", "No title")
            link = item.get("link", "")
            snippet = item.get("snippet", "")

            results.append(
                {
                    "title": title,
                    "url": link,
                    "snippet": snippet,
                }
            )

        logger.info(f"Serper search: {len(results)} results for '{query}'")

        # Format output matching WebSearchTool format
        output_lines = [f"Search results for: '{query}'", ""]
        for i, r in enumerate(results, 1):
            output_lines.append(f"{i}. {r['title']}")
            if r["url"]:
                output_lines.append(f"   URL: {r['url']}")
            if r["snippet"]:
                output_lines.append(f"   {r['snippet']}")
            output_lines.append("")

        return "\n".join(output_lines)

    def _format_news_results(self, query: str, data: dict, max_results: int) -> str:
        """Format news search results."""
        news = data.get("news", [])

        if not news:
            logger.info(f"No news results found for query: {query}")
            return (
                f"No news results found for: '{query}'. "
                "Try different keywords or a broader search."
            )

        results = []
        for item in news[:max_results]:
            title = item.get("title", "No title")
            link = item.get("link", "")
            snippet = item.get("snippet", "")
            source = item.get("source", "")
            date = item.get("date", "")

            results.append(
                {
                    "title": title,
                    "url": link,
                    "snippet": snippet,
                    "source": source,
                    "date": date,
                }
            )

        logger.info(f"Serper news: {len(results)} results for '{query}'")

        output_lines = [f"News results for: '{query}'", ""]
        for i, r in enumerate(results, 1):
            output_lines.append(f"{i}. {r['title']}")
            if r["source"] or r["date"]:
                meta = " - ".join(filter(None, [r["source"], r["date"]]))
                output_lines.append(f"   Source: {meta}")
            if r["url"]:
                output_lines.append(f"   URL: {r['url']}")
            if r["snippet"]:
                output_lines.append(f"   {r['snippet']}")
            output_lines.append("")

        return "\n".join(output_lines)

    def _format_image_results(self, query: str, data: dict, max_results: int) -> str:
        """Format image search results."""
        images = data.get("images", [])

        if not images:
            logger.info(f"No image results found for query: {query}")
            return (
                f"No image results found for: '{query}'. "
                "Try different keywords or a broader search."
            )

        results = []
        for item in images[:max_results]:
            title = item.get("title", "No title")
            link = item.get("link", "")
            image_url = item.get("imageUrl", "")
            source = item.get("source", "")

            results.append(
                {
                    "title": title,
                    "url": link,
                    "image_url": image_url,
                    "source": source,
                }
            )

        logger.info(f"Serper images: {len(results)} results for '{query}'")

        output_lines = [f"Image results for: '{query}'", ""]
        for i, r in enumerate(results, 1):
            output_lines.append(f"{i}. {r['title']}")
            if r["source"]:
                output_lines.append(f"   Source: {r['source']}")
            if r["url"]:
                output_lines.append(f"   Page URL: {r['url']}")
            if r["image_url"]:
                output_lines.append(f"   Image URL: {r['image_url']}")
            output_lines.append("")

        return "\n".join(output_lines)


# Convenience instance (will fail without API key, but allows import)
serper_search = SerperSearchTool()
