"""Tests for Moltbook tools."""

import pytest
import respx
from httpx import Response

from friday_tools.integrations.moltbook import MoltbookSearchTool, SearchInput


@pytest.mark.asyncio
async def test_search_validation_error():
    tool = MoltbookSearchTool(api_key="moltbook_test")
    args = SearchInput(q="x" * 501)
    result = await tool.run(args)
    assert result.error is not None
    assert "too long" in result.content.lower()


@pytest.mark.asyncio
@respx.mock
async def test_search_success():
    respx.get("https://www.moltbook.com/api/v1/search").mock(
        return_value=Response(
            200,
            json={
                "success": True,
                "query": "hello",
                "type": "all",
                "results": [],
                "count": 0,
            },
        )
    )
    tool = MoltbookSearchTool(api_key="moltbook_test")
    args = SearchInput(q="hello")
    result = await tool.run(args)
    assert result.error is None
    assert result.data is not None
    assert result.data["raw"]["query"] == "hello"
