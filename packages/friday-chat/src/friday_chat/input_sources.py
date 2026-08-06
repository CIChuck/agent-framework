"""Shared asynchronous console-input support for Friday Chat."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

AsyncPromptCallable = Callable[[str], Awaitable[str]]


class AsyncPromptReader:
    """Read terminal input without blocking the application event loop."""

    def __init__(self, prompt_fn: AsyncPromptCallable | None = None) -> None:
        self._prompt_fn = prompt_fn
        self._session: PromptSession[str] | None = None

    async def read(self, prompt: str) -> str:
        """Read one prompt value while preserving async task progress."""
        with patch_stdout():
            if self._prompt_fn is not None:
                return await self._prompt_fn(prompt)
            if self._session is None:
                self._session = PromptSession()
            return await self._session.prompt_async(prompt)


__all__ = ["AsyncPromptCallable", "AsyncPromptReader"]
