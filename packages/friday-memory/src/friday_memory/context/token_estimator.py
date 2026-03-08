# mypy: ignore-errors
"""
Token estimation utilities for prompt budgeting.

Provides a fast approximate estimator (default) and an optional tiktoken-backed
estimator for more exact counts when needed.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Protocol


class TokenEstimator(Protocol):
    """Protocol for token estimators."""

    def count(self, text: str) -> int:
        """Return estimated token count for text."""


@dataclass(frozen=True)
class ApproxTokenEstimator:
    """Fast heuristic token estimator using character count."""

    chars_per_token: float = 4.0
    overhead_pct: float = 0.15

    def count(self, text: str) -> int:
        if not text:
            return 0
        base = len(text) / max(self.chars_per_token, 0.1)
        return int(math.ceil(base * (1.0 + self.overhead_pct)))


class TiktokenEstimator:
    """Exact token estimator backed by tiktoken."""

    def __init__(self, model_name: str = "gpt-4") -> None:
        try:
            import tiktoken
        except Exception as exc:  # pragma: no cover - dependency gate
            raise RuntimeError("tiktoken is required for exact token counting") from exc

        try:
            self._encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self._encoding = tiktoken.get_encoding("cl100k_base")

    def count(self, text: str) -> int:
        if not text:
            return 0
        return len(self._encoding.encode(text))


def build_token_estimator(
    config: dict[str, Any] | None, model_name: str = "gpt-4"
) -> TokenEstimator:
    """
    Build a token estimator from config.

    Expected config keys (all optional):
      - strategy: "approx" | "tiktoken"
      - approx_chars_per_token: float
      - approx_overhead_pct: float
    """
    cfg = config or {}
    strategy = str(cfg.get("strategy", "approx")).lower()
    if strategy in {"tiktoken", "exact"}:
        return TiktokenEstimator(model_name=model_name)

    chars_per_token = float(cfg.get("approx_chars_per_token", 4.0))
    overhead_pct = float(cfg.get("approx_overhead_pct", 0.15))
    return ApproxTokenEstimator(
        chars_per_token=chars_per_token,
        overhead_pct=overhead_pct,
    )
