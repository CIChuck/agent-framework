"""
Web search tools.

Ref: docs/specs/tool_specification.md - Category 5: Web Search
"""

from __future__ import annotations

from typing import Any

import httpx

from ..definition import BaseTool


class WebSearchTool(BaseTool):
    """Search the web using DuckDuckGo."""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web using DuckDuckGo and return relevant results."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10,
                },
                "region": {
                    "type": "string",
                    "description": "Region for search (e.g., 'us-en', 'uk-en')",
                    "default": "wt-wt",
                },
            },
            "required": ["query"],
        }

    async def execute(self, **kwargs: Any) -> str:
        query = kwargs["query"]
        max_results = kwargs.get("max_results", 10)
        region = kwargs.get("region", "wt-wt")

        try:
            # Use DuckDuckGo HTML API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://html.duckduckgo.com/html/",
                    params={
                        "q": query,
                        "kl": region,
                    },
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; FridayBot/1.0)"
                    },
                )
                response.raise_for_status()

            # Parse results from HTML
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            for i, result in enumerate(soup.select(".result")):
                if i >= max_results:
                    break

                title_elem = result.select_one(".result__title")
                snippet_elem = result.select_one(".result__snippet")
                link_elem = result.select_one(".result__url")

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    url = link_elem.get_text(strip=True) if link_elem else ""

                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": url,
                    })

            if not results:
                return f"No results found for: {query}"

            # Format output
            output_lines = []
            for i, r in enumerate(results, 1):
                output_lines.append(f"{i}. {r['title']}")
                if r['url']:
                    output_lines.append(f"   URL: {r['url']}")
                if r['snippet']:
                    output_lines.append(f"   {r['snippet']}")
                output_lines.append("")

            return "\n".join(output_lines)

        except httpx.HTTPStatusError as e:
            return f"Error: HTTP {e.response.status_code} - {e.response.reason_phrase}"
        except Exception as e:
            return f"Error: Failed to search: {e}"


# Convenience instance
web_search = WebSearchTool()
