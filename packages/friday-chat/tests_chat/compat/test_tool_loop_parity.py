"""Compatibility scaffolding for FridayV2 tool-loop parity."""

from __future__ import annotations

import pytest


async def test_friday_v2_tool_loop_uses_fake_tools() -> None:
    from friday_chat.tools import loop

    loop_type = getattr(loop, "ToolLoop", None)
    if loop_type is None:
        pytest.xfail("FridayV2 tool loop is not implemented yet.")

    tool_loop = loop_type()
    result = await tool_loop.run(messages=[], tool_schemas=[])

    assert result is not None
