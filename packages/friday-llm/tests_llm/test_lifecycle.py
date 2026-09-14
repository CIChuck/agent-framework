"""Tests for process-scoped LiteLLM client cleanup."""

from __future__ import annotations

import asyncio

import friday_llm.lifecycle as lifecycle_module
import pytest
from aiohttp import ClientSession
from friday_llm import close_litellm_async_clients
from litellm.caching.evicted_client_closer import EvictedClientCloser
from litellm.caching.llm_caching_handler import LLMClientCache


async def test_close_litellm_async_clients_delegates_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    async def close_clients() -> None:
        nonlocal calls
        calls += 1

    monkeypatch.setattr(
        lifecycle_module.litellm,
        "close_litellm_async_clients",
        close_clients,
    )

    await close_litellm_async_clients()

    assert calls == 1


async def test_close_litellm_async_clients_propagates_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def close_clients() -> None:
        raise RuntimeError("synthetic cleanup failure")

    monkeypatch.setattr(
        lifecycle_module.litellm,
        "close_litellm_async_clients",
        close_clients,
    )

    with pytest.raises(RuntimeError, match="synthetic cleanup failure"):
        await close_litellm_async_clients()


async def test_litellm_owned_client_eviction_closes_aiohttp_session() -> None:
    exception_contexts: list[dict[str, object]] = []
    loop = asyncio.get_running_loop()
    previous_handler = loop.get_exception_handler()
    loop.set_exception_handler(
        lambda _loop, context: exception_contexts.append(context),
    )
    closer = EvictedClientCloser(grace_seconds=0)
    cache = LLMClientCache(
        max_size_in_memory=1,
        evicted_client_closer=closer,
    )
    first = ClientSession()
    second = ClientSession()
    try:
        cache.set_cache("first", first, litellm_owned_client=True)
        cache.set_cache("second", second, litellm_owned_client=True)
        await asyncio.sleep(0)

        assert first.closed is True
        assert second.closed is False
        assert closer.pending_count == 0
        assert exception_contexts == []
    finally:
        await first.close()
        await second.close()
        loop.set_exception_handler(previous_handler)
