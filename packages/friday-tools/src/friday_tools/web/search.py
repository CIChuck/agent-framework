# mypy: ignore-errors
"""
Web search tools.

Ref: docs/specs/tool_specification.md - Category 5: Web Search
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from ..definition import BaseTool
from .config import DEFAULT_WEB_CONFIG, WebConfig

logger = logging.getLogger(__name__)


class WebSearchError(Exception):
    """Raised when web search fails."""

    def __init__(self, message: str, *, recoverable: bool = False, query: str = ""):
        super().__init__(message)
        self.recoverable = recoverable
        self.query = query


class WebSearchTool(BaseTool):
    """
    Search the web using DuckDuckGo.

    This tool performs web searches and returns structured results including
    titles, URLs, and snippets. It's useful for finding current information,
    researching topics, or discovering relevant web pages.
    """

    def __init__(self, config: WebConfig | dict | None = None):
        """
        Initialize web search tool.

        Args:
            config: Optional WebConfig or dict for timeout/retry settings.
                   Accepts WebConfig object, dict (from YAML), or None.
                   Uses DEFAULT_WEB_CONFIG if not provided.
        """
        logger.debug(f"WebSearchTool.__init__ called with config type: {type(config)}")
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
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Search the web for information using DuckDuckGo. "
            "Use this tool to find current information, research topics, "
            "discover documentation, or locate relevant web pages. "
            "Returns titles, URLs, and snippets for each result. "
            "Best for: factual queries, 'how to' questions, "
            "finding official documentation, news, and general research. "
            "Note: For specific websites, use web_reader instead."
        )

    @property
    def category(self) -> str:
        return "web"

    @property
    def tags(self) -> list[str]:
        return ["search", "read-only", "internet", "research"]

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The search query. Be specific for better results. "
                        "Examples: 'Python asyncio tutorial', "
                        "'React hooks documentation 2024', "
                        "'how to configure nginx reverse proxy'"
                    ),
                },
                "max_results": {
                    "type": "integer",
                    "description": (
                        "Maximum number of results to return (1-25). "
                        "Default is 10. Use fewer for quick lookups, more for research."
                    ),
                    "default": 10,
                    "minimum": 1,
                    "maximum": 25,
                },
                "region": {
                    "type": "string",
                    "description": (
                        "Region/language for search results. "
                        "Format: 'xx-xx' (e.g., 'us-en', 'uk-en', 'de-de'). "
                        "Default 'wt-wt' returns worldwide results."
                    ),
                    "default": "wt-wt",
                },
            },
            "required": ["query"],
        }

    async def execute(self, **kwargs: Any) -> str:
        """
        Execute web search and return formatted results.

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
        max_results = min(max_results, 25)  # Cap at 25

        region = kwargs.get("region", "wt-wt")

        logger.debug(
            f"Web search: query='{query}', max_results={max_results}, region={region}"
        )

        # Import bs4 early to give clear error if missing
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            logger.error("BeautifulSoup4 not installed")
            return (
                "Error: Web search requires BeautifulSoup4 library. "
                "Install it with: pip install beautifulsoup4"
            )

        logger.debug(f"In execute: self._config type = {type(self._config)}")
        if isinstance(self._config, dict):
            logger.error(f"BUG: self._config is still a dict: {self._config}")
            self._config = WebConfig.from_dict(self._config)
        timeout = self._config.client.timeout
        max_retries = self._config.client.max_retries
        user_agent = self._config.client.user_agent

        last_error: Exception | None = None

        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        "https://html.duckduckgo.com/html/",
                        params={
                            "q": query,
                            "kl": region,
                        },
                        headers={
                            "User-Agent": user_agent,
                        },
                    )

                    # Handle specific HTTP errors
                    if response.status_code == 429:
                        logger.warning(
                            f"Rate limited by DuckDuckGo (attempt {attempt + 1})"
                        )
                        if attempt < max_retries:
                            import asyncio

                            await asyncio.sleep(2**attempt)  # Exponential backoff
                            continue
                        return (
                            "Error: Search rate limit exceeded. "
                            "DuckDuckGo is temporarily limiting requests. "
                            "Please wait a moment and try again."
                        )

                    if response.status_code == 403:
                        logger.error("Forbidden response from DuckDuckGo")
                        return (
                            "Error: Search request was blocked (HTTP 403). "
                            "This may be due to automated request detection. "
                            "Try again later or use a different search approach."
                        )

                    if response.status_code >= 500:
                        logger.warning(
                            f"DuckDuckGo server error: {response.status_code}"
                        )
                        if attempt < max_retries:
                            import asyncio

                            await asyncio.sleep(1)
                            continue
                        return (
                            f"Error: DuckDuckGo unavailable "
                            f"(HTTP {response.status_code}). "
                            "Service may be experiencing issues. "
                            "Please try again later."
                        )

                    response.raise_for_status()

                # Parse results from HTML
                soup = BeautifulSoup(response.text, "html.parser")
                result_elements = soup.select(".result")

                if not result_elements:
                    # Check if we got a valid page but no results vs parsing failure
                    if (
                        soup.select_one(".no-results")
                        or "no results" in response.text.lower()
                    ):
                        logger.info(f"No results found for query: {query}")
                        return (
                            f"No results found for: '{query}'. "
                            "Try different keywords or a broader search."
                        )

                    # Check for common page elements to verify we got a real response
                    if not soup.select_one("body") or len(response.text) < 1000:
                        logger.error(
                            f"Unexpected response from DuckDuckGo: "
                            f"{len(response.text)} bytes"
                        )
                        return (
                            "Error: Unexpected response from search service. "
                            "The page format may have changed. "
                            "Please try again or report this issue."
                        )

                    # Page looks valid but selectors didn't match - HTML change
                    logger.warning(
                        "Search result selectors did not match - "
                        "DDG HTML may have changed"
                    )
                    return (
                        f"No results could be extracted for: '{query}'. "
                        "This may indicate the search service format has changed. "
                        "Please try again or use web_reader to visit a specific URL."
                    )

                results = []
                for i, result in enumerate(result_elements):
                    if i >= max_results:
                        break

                    title_elem = result.select_one(".result__title")
                    snippet_elem = result.select_one(".result__snippet")
                    link_elem = result.select_one(".result__url")

                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        snippet = (
                            snippet_elem.get_text(strip=True) if snippet_elem else ""
                        )
                        url = link_elem.get_text(strip=True) if link_elem else ""

                        # Skip results without meaningful content
                        if title and (url or snippet):
                            results.append(
                                {
                                    "title": title,
                                    "snippet": snippet,
                                    "url": url,
                                }
                            )

                if not results:
                    logger.info(f"No usable results found for query: {query}")
                    return (
                        f"No usable results found for: '{query}'. "
                        "Try different keywords."
                    )

                logger.info(f"Search completed: {len(results)} results for '{query}'")

                # Format output
                output_lines = [f"Search results for: '{query}'", ""]
                for i, r in enumerate(results, 1):
                    output_lines.append(f"{i}. {r['title']}")
                    if r["url"]:
                        output_lines.append(f"   URL: {r['url']}")
                    if r["snippet"]:
                        output_lines.append(f"   {r['snippet']}")
                    output_lines.append("")

                return "\n".join(output_lines)

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(
                    f"Search timeout (attempt {attempt + 1}/{max_retries + 1}): {e}"
                )
                if attempt < max_retries:
                    continue
                return (
                    f"Error: Search request timed out after {timeout}s. "
                    "The search service may be slow or unreachable. "
                    "Please try again or check your network connection."
                )

            except httpx.ConnectError as e:
                last_error = e
                logger.error(f"Connection error during search: {e}")
                return (
                    "Error: Could not connect to search service. "
                    "Please check your network connection and try again."
                )

            except httpx.HTTPStatusError as e:
                last_error = e
                logger.error(f"HTTP error during search: {e.response.status_code}")
                return (
                    f"Error: Search request failed with HTTP {e.response.status_code}. "
                    f"Reason: {e.response.reason_phrase or 'Unknown'}. "
                    "Please try again later."
                )

            except Exception as e:
                last_error = e
                logger.exception(f"Unexpected error during web search: {e}")
                return (
                    f"Error: Search failed unexpectedly ({type(e).__name__}). "
                    f"Details: {str(e)[:200]}. "
                    "Please try again or report this issue if it persists."
                )

        # Should not reach here, but just in case
        logger.error(f"Search failed after all retries: {last_error}")
        return (
            f"Error: Search failed after {max_retries + 1} attempts. "
            "Please try again later."
        )


# Convenience instance with default config
web_search = WebSearchTool()
