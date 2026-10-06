"""Friday LLM test isolation."""

from __future__ import annotations

import os
import socket
from collections.abc import Generator
from typing import Any

import pytest

# LiteLLM otherwise attempts to refresh its model-cost map during import.
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")


@pytest.fixture(autouse=True)
def prohibit_external_network(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[None]:
    """Permit deterministic loopback transports and reject external DNS."""

    original = socket.getaddrinfo

    def guarded_getaddrinfo(
        host: str | bytes | None,
        *args: Any,
        **kwargs: Any,
    ) -> list[tuple[Any, ...]]:
        normalized = host.decode() if isinstance(host, bytes) else host
        if normalized not in (None, "127.0.0.1", "localhost", "::1"):
            raise RuntimeError("external network is prohibited in Friday LLM tests")
        return original(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
    yield
