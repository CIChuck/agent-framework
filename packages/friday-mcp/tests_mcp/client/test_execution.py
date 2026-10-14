"""Narrow tools/call protocol result classification and legacy extraction."""

import pytest

from friday_mcp.client.base import MCPClientBase, MCPError


class Client(MCPClientBase):
    def __init__(self, result):
        super().__init__("synthetic")
        self.result = result
        self.sent = []

    async def _create_transport(self):
        raise RuntimeError("No transport in the request double")

    async def _request(self, method, params):
        self.sent.append((method, params))
        return self.result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "result, expected",
    [
        ({"content": []}, ""),
        ({"content": [], "structuredContent": None}, "null"),
        ({"content": [], "structuredContent": [1, 2]}, "[1,2]"),
        (
            {"content": [{"type": "text", "text": "success"}], "isError": False},
            "success",
        ),
        (
            {
                "content": [
                    "legacy",
                    {"type": "image", "data": "data"},
                    {"type": "text", "text": "text"},
                ]
            },
            "legacy\ntext",
        ),
    ],
)
async def test_valid_successful_string_api_and_exact_original_routing(result, expected):
    client = Client(result)
    args = {"path": "SYNTHETIC_ARGUMENT"}
    assert await client.call_tool("Read.File", args) == expected
    assert client.sent == [("tools/call", {"name": "Read.File", "arguments": args})]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "result, code",
    [
        (
            {"isError": True, "content": [{"type": "text", "text": "WS05_SECRET"}]},
            "tool_error",
        ),
        ({"isError": "WS05_SECRET", "content": []}, "invalid_result"),
        ({"isError": 1, "content": []}, "invalid_result"),
        ({}, "invalid_result"),
        ({"content": "WS05_SECRET"}, "invalid_result"),
        ({"content": [42]}, "invalid_result"),
        (
            {"content": [{"type": "image", "data": "WS05_SECRET"}]},
            "unsupported_content",
        ),
        (
            {
                "content": [
                    {"type": "image", "data": "WS05_SECRET"},
                    {"type": "text", "text": ""},
                ]
            },
            "unsupported_content",
        ),
        (
            {"content": [{"type": "text", "text": {"secret": "WS05_SECRET"}}]},
            "invalid_result",
        ),
        ({"content": [{"type": "text"}]}, "invalid_result"),
    ],
)
async def test_failed_invalid_results_raise_only_fixed_safe_errors(result, code):
    with pytest.raises(MCPError) as caught:
        await Client(result).call_tool("Read.File", {"token": "WS05_SECRET"})
    assert caught.value.failure_code == code
    assert "WS05_SECRET" not in str(caught.value) and "WS05_SECRET" not in repr(
        caught.value
    )
