"""
Data models and utilities for Friday Chat.

Contains:
- TurnMetrics: Metrics captured during conversation turns
- TokenCounter: Tiktoken-based token counting utility
- ContextMetrics: Context size tracking for budget management
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

import tiktoken

if TYPE_CHECKING:
    from friday_memory.models import ToolCall as MemoryToolCall
    from friday_memory.models import ToolResult as MemoryToolResult


# =============================================================================
# TURN METRICS TRACKING
# =============================================================================


@dataclass
class TurnMetrics:
    """Metrics captured during a conversation turn for transcript storage."""

    # Timing
    response_started_at: datetime | None = None
    response_completed_at: datetime | None = None

    # Token usage (accumulated across tool iterations)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0

    # Model info
    model_name: str | None = None
    temperature: float | None = None

    # Tool execution tracking
    tool_calls: list["MemoryToolCall"] = field(default_factory=list)
    tool_results: list["MemoryToolResult"] = field(default_factory=list)

    # Pre-flight context estimation
    estimated_context_tokens: int = 0
    context_budget_pct: float = 0.0


# =============================================================================
# TOKEN COUNTING UTILITIES
# =============================================================================


class TokenCounter:
    """
    Utility for counting tokens using tiktoken.

    Uses cl100k_base encoding which works for GPT-4, Claude, and most modern LLMs.
    Token counts are estimates - actual counts may vary slightly by model.
    """

    _instance: "TokenCounter | None" = None
    _encoding: tiktoken.Encoding | None = None

    def __new__(cls) -> "TokenCounter":
        """Singleton pattern to avoid re-loading encoding."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._encoding = tiktoken.get_encoding("cl100k_base")
        return cls._instance

    def count(self, text: str) -> int:
        """Count tokens in a text string."""
        if not text:
            return 0
        return len(self._encoding.encode(text))

    def count_messages(self, messages: list[dict]) -> int:
        """
        Count tokens in chat messages including role overhead.

        Each message has ~4 tokens overhead for role/formatting.
        Plus ~2 tokens for conversation priming.
        """
        total = 0
        for msg in messages:
            total += 4  # Role overhead per message
            content = msg.get("content", "") or ""
            total += self.count(content)
        total += 2  # Priming tokens
        return total


# =============================================================================
# CONTEXT METRICS
# =============================================================================


@dataclass
class ContextMetrics:
    """
    Tracks context size before and after LLM call.

    Pre-flight estimates use tiktoken for measurement before sending.
    Budget tracking helps identify timeout risks from oversized contexts.
    """

    # Pre-flight estimates (tiktoken)
    estimated_total_tokens: int = 0
    estimated_system_tokens: int = 0
    estimated_history_tokens: int = 0
    estimated_user_message_tokens: int = 0

    # Budget info (from config)
    context_window: int = 0
    output_buffer: int = 0
    available_budget: int = 0
    budget_used_pct: float = 0.0

    # Actual from LLM response (filled after)
    actual_prompt_tokens: int = 0
    actual_completion_tokens: int = 0

    # Timestamp for tracking
    timestamp: datetime = field(default_factory=datetime.now)
