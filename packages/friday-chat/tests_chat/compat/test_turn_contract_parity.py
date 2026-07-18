"""Compatibility scaffolding for FridayV2 turn-processing parity."""

from __future__ import annotations

import pytest


async def test_friday_v2_no_tool_turn_processor_with_fakes() -> None:
    from friday_chat.turns import processor

    processor_type = getattr(processor, "TurnProcessor", None)
    if processor_type is None:
        pytest.xfail("FridayV2 turn processor is not implemented yet.")

    turn_processor = processor_type()
    result = await turn_processor.process("hello")

    assert result is not None
