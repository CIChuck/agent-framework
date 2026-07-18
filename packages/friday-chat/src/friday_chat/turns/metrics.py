"""Turn metrics for FridayV2."""

from __future__ import annotations

import time


def now_seconds() -> float:
    """Return a monotonic timestamp for turn timing."""
    return time.perf_counter()


def elapsed_seconds(start: float) -> float:
    """Return elapsed monotonic seconds from a start timestamp."""
    return max(0.0, time.perf_counter() - start)
