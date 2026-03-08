# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for Moltbook client."""

import pytest
import respx
from friday_moltbook import Moltbook, MoltbookConfig
from friday_moltbook.errors import MoltbookResponseError, MoltbookValidationError
from httpx import Response


class TestValidation:
    """Client-side validation tests."""

    @pytest.mark.asyncio
    async def test_search_query_too_long(self):
        client = Moltbook()
        long_query = "x" * 501
        with pytest.raises(MoltbookValidationError):
            await client.search(q=long_query)

    @pytest.mark.asyncio
    async def test_invalid_sort(self):
        client = Moltbook()
        with pytest.raises(MoltbookValidationError):
            await client.get_feed(sort="invalid")


class TestParsing:
    """Response parsing tests."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_missing_keys_raises(self):
        respx.post("https://www.moltbook.com/api/v1/agents/register").mock(
            return_value=Response(200, json={"unexpected": True})
        )
        client = Moltbook()
        with pytest.raises(MoltbookResponseError):
            await client.register_agent(name="Test", description="Desc")

    @pytest.mark.asyncio
    @respx.mock
    async def test_rate_limit_response(self):
        respx.post("https://www.moltbook.com/api/v1/posts").mock(
            return_value=Response(
                429,
                json={
                    "error": "Rate limited",
                    "retry_after_minutes": 10,
                    "hint": "Wait",
                },
            )
        )
        client = Moltbook(MoltbookConfig(api_key="moltbook_test"))
        response = await client.create_post(
            submolt="general",
            title="Hello",
            content="World",
        )
        assert response.success is False
        assert response.data["retry_after_minutes"] == 10
        assert response.error == "Rate limited"
