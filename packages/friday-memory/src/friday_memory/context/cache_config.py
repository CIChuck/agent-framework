# mypy: ignore-errors
"""
Prompt Caching Configuration.

Controls cache-optimized prompt layout for LLM providers that support
prefix caching (Anthropic, OpenAI, etc.).

Ref: docs/planning/build-plans/copilot-promotion-build-plan.md
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CacheProvider(str, Enum):
    """Supported cache providers."""

    AUTO = "auto"  # Auto-detect from model name
    ANTHROPIC = "anthropic"  # Explicit cache_control markers
    OPENAI = "openai"  # Automatic prefix caching
    NONE = "none"  # No caching support


class CacheBreakpoint(str, Enum):
    """Where to place the cache breakpoint."""

    AFTER_HISTORY = "after_history"  # Cache system + tools + static + history
    AFTER_STATIC = "after_static"  # Cache system + tools + static only
    SYSTEM_ONLY = "system_only"  # Cache only system prompt


class PromptCacheConfig(BaseModel):
    """Configuration for prompt caching optimization."""

    enabled: bool = Field(
        default=False,
        description="Enable cache-optimized prompt layout",
    )

    provider: CacheProvider = Field(
        default=CacheProvider.AUTO,
        description="Cache provider (auto-detect from model name)",
    )

    breakpoint: CacheBreakpoint = Field(
        default=CacheBreakpoint.AFTER_HISTORY,
        description="Where to place the cache breakpoint",
    )

    static_context_in_prefix: bool = Field(
        default=True,
        description="Include static context (insights, facts) in cacheable prefix",
    )

    min_turns_for_cache: int = Field(
        default=3,
        ge=0,
        description="Minimum turns before enabling cache optimization",
    )

    ttl_seconds: int = Field(
        default=0,
        ge=0,
        description="TTL hint for Anthropic cache (0 = provider default)",
    )

    def detect_provider(self, model_name: str) -> CacheProvider:
        """
        Auto-detect cache provider from model name.

        Args:
            model_name: The LLM model name (e.g., "anthropic/claude-3-opus")

        Returns:
            Detected CacheProvider
        """
        if self.provider != CacheProvider.AUTO:
            return self.provider

        model_lower = model_name.lower()

        # Anthropic models (direct or via OpenRouter)
        if "claude" in model_lower or "anthropic" in model_lower:
            return CacheProvider.ANTHROPIC

        # OpenAI models (direct or via OpenRouter)
        if "gpt" in model_lower or "openai" in model_lower:
            return CacheProvider.OPENAI

        # Default to none for unknown providers
        return CacheProvider.NONE

    def should_cache(self, turn_count: int, model_name: str) -> bool:
        """
        Determine if caching should be used for this request.

        Args:
            turn_count: Current conversation turn count
            model_name: The LLM model name

        Returns:
            True if caching should be enabled
        """
        if not self.enabled:
            return False

        if turn_count < self.min_turns_for_cache:
            return False

        provider = self.detect_provider(model_name)
        return provider != CacheProvider.NONE

    def get_cache_control_marker(self, model_name: str) -> dict[str, Any] | None:
        """
        Get the cache control marker for Anthropic API.

        Args:
            model_name: The LLM model name

        Returns:
            Cache control dict for Anthropic, or None for other providers
        """
        provider = self.detect_provider(model_name)

        if provider != CacheProvider.ANTHROPIC:
            return None

        marker: dict[str, Any] = {"type": "ephemeral"}

        if self.ttl_seconds > 0:
            marker["ttl"] = self.ttl_seconds

        return marker
