"""Process-scoped lifecycle controls for LiteLLM transport clients."""

from __future__ import annotations

import litellm


async def close_litellm_async_clients() -> None:
    """Close LiteLLM-owned async clients after process LLM work is quiescent.

    LiteLLM caches transport clients across service instances. Call this once
    during process shutdown, after all LLM-dependent work has completed.
    """
    await litellm.close_litellm_async_clients()


__all__ = ["close_litellm_async_clients"]
