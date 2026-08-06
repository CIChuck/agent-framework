"""Tests for nonblocking Friday Chat console input sources."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable

import pytest
from friday_chat.app import ConsoleInputSource, InputSource
from friday_chat.background import BackgroundTaskManager
from friday_chat.display import FridayCliInputSource
from friday_chat.input_sources import AsyncPromptCallable

InputSourceFactory = Callable[[AsyncPromptCallable], InputSource]


class ControlledPrompt:
    """Async prompt double that remains pending until explicitly released."""

    def __init__(self, response: str = "  unchanged response  ") -> None:
        self.response = response
        self.entered = asyncio.Event()
        self.release = asyncio.Event()
        self.prompts: list[str] = []

    async def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)
        self.entered.set()
        await self.release.wait()
        return self.response


def _console_source(prompt_fn: AsyncPromptCallable) -> InputSource:
    return ConsoleInputSource(prompt_fn=prompt_fn)


def _friday_cli_source(prompt_fn: AsyncPromptCallable) -> InputSource:
    return FridayCliInputSource("Chuck: ", prompt_fn=prompt_fn)


@pytest.mark.parametrize(
    ("source_factory", "expected_prompt"),
    [
        pytest.param(_console_source, "> ", id="console"),
        pytest.param(_friday_cli_source, "Chuck: ", id="friday-cli"),
    ],
)
async def test_input_source_yields_while_prompt_is_pending(
    source_factory: InputSourceFactory,
    expected_prompt: str,
) -> None:
    controlled_prompt = ControlledPrompt()
    source = source_factory(controlled_prompt)
    manager = BackgroundTaskManager()
    background_completed = asyncio.Event()
    read_task = asyncio.create_task(source.read())

    async def mark_background_complete() -> None:
        background_completed.set()

    result = ""
    try:
        await asyncio.wait_for(controlled_prompt.entered.wait(), timeout=1.0)
        manager.create_task(mark_background_complete())
        await asyncio.wait_for(background_completed.wait(), timeout=1.0)
        assert read_task.done() is False
    finally:
        controlled_prompt.release.set()
        result = await asyncio.wait_for(read_task, timeout=1.0)
        await manager.close()

    assert result == "  unchanged response  "
    assert controlled_prompt.prompts == [expected_prompt]


@pytest.mark.parametrize(
    "source_factory",
    [
        pytest.param(_console_source, id="console"),
        pytest.param(_friday_cli_source, id="friday-cli"),
    ],
)
@pytest.mark.parametrize("error_type", [EOFError, KeyboardInterrupt])
async def test_input_source_preserves_terminal_exceptions(
    source_factory: InputSourceFactory,
    error_type: type[BaseException],
) -> None:
    async def fail_prompt(_prompt: str) -> str:
        raise error_type

    with pytest.raises(error_type):
        await source_factory(fail_prompt).read()


def test_input_source_constructor_contracts_are_preserved() -> None:
    console_prompt = inspect.signature(ConsoleInputSource).parameters["prompt"]
    friday_prompt = inspect.signature(FridayCliInputSource).parameters["prompt"]

    assert console_prompt.default == "> "
    assert friday_prompt.default is inspect.Parameter.empty
