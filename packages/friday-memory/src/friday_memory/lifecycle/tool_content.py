"""
Tool Content Lifecycle Manager.

Tracks large tool outputs and manages reference-based decay.
When a tool output is not referenced for N turns, it gets summarized
to save context tokens while preserving key information.

Ref: docs/build-plan/to-do/tool-content-lifecycle-build-plan.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from friday_core.interfaces.llm import LLMClient


logger = logging.getLogger(__name__)


@dataclass
class TrackedToolOutput:
    """
    Represents a tracked large tool output.

    The lifecycle manager tracks outputs that exceed the minimum token threshold.
    Each output is monitored for references, and decayed when stale.
    """

    tool_call_id: str
    tool_name: str
    content: str
    token_count: int
    turn_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_referenced_turn_id: str | None = None
    referencing_turns: list[str] = field(default_factory=list)
    is_decayed: bool = False
    summary: str | None = None


@dataclass
class ToolContentConfig:
    """
    Configuration for tool content lifecycle.

    Attributes:
        enabled: Whether lifecycle management is active
        min_tokens_for_tracking: Only track outputs >= this size
        decay_threshold_turns: Summarize after N turns without reference
        tool_policies: Per-tool decay threshold overrides
    """

    enabled: bool = True
    min_tokens_for_tracking: int = 500  # Only track outputs >= this size
    decay_threshold_turns: int = 3  # Summarize after N turns without reference

    # Per-tool overrides (tool_name -> decay_threshold)
    # e.g., {"read_file": 2, "web_search": 1}
    tool_policies: dict[str, int] = field(default_factory=dict)


class ToolContentManager:
    """
    Manages lifecycle of large tool outputs.

    Responsibilities:
    - Track active large tool outputs for the session
    - Calculate relevance based on recency (last referenced turn)
    - Trigger summarization when outputs become stale

    The manager maintains an in-memory cache of tracked outputs for the session.
    When an output isn't referenced for decay_threshold_turns, it's summarized
    using the LLM and the is_decayed flag is set.

    Usage:
        manager = ToolContentManager(config, llm_client)

        # When tool executes
        manager.track_output(tool_call_id, tool_name, content, turn_id)

        # When turn processes (to detect references)
        manager.mark_referenced(tool_call_id, turn_id)

        # After each turn
        decayed = await manager.check_and_decay(current_turn_number)

    Example:
        >>> config = ToolContentConfig(min_tokens_for_tracking=500)
        >>> manager = ToolContentManager(config, llm_client)
        >>> manager.track_output("tc_1", "read_file", large_content, "turn_1")
        True
        >>> manager.mark_referenced("tc_1", "turn_2")  # User asks about file
        >>> await manager.check_and_decay(5)  # 3 turns since last reference
        ["tc_1"]  # Decayed because gap > threshold
    """

    def __init__(
        self,
        config: ToolContentConfig | None = None,
        llm_client: LLMClient | None = None,
    ):
        """
        Initialize the ToolContentManager.

        Args:
            config: Configuration for lifecycle management
            llm_client: LLM client for generating summaries (optional)
        """
        self.config = config or ToolContentConfig()
        self._llm = llm_client
        self._tracked: dict[str, TrackedToolOutput] = {}  # tool_call_id -> output
        self._session_turn_count: int = 0

    @property
    def tracked_count(self) -> int:
        """Get the number of tracked outputs."""
        return len(self._tracked)

    @property
    def active_count(self) -> int:
        """Get the number of non-decayed outputs."""
        return len([o for o in self._tracked.values() if not o.is_decayed])

    def track_output(
        self,
        tool_call_id: str,
        tool_name: str,
        content: str,
        turn_id: str,
        token_count: int | None = None,
    ) -> bool:
        """
        Track a tool output for lifecycle management.

        Only outputs exceeding the minimum token threshold are tracked.
        Outputs below threshold are ignored (they don't need decay management).

        Args:
            tool_call_id: Unique ID for this tool call
            tool_name: Name of the tool that produced the output
            content: The tool output content
            turn_id: ID of the turn where this tool was executed
            token_count: Optional pre-computed token count

        Returns:
            True if output is being tracked, False if too small or disabled
        """
        if not self.config.enabled:
            return False

        # Estimate tokens if not provided (rough: 4 chars per token)
        if token_count is None:
            token_count = len(content) // 4

        if token_count < self.config.min_tokens_for_tracking:
            logger.debug(
                f"Tool output {tool_call_id} too small ({token_count} tokens), not tracking"  # noqa: E501
            )
            return False

        self._tracked[tool_call_id] = TrackedToolOutput(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            content=content,
            token_count=token_count,
            turn_id=turn_id,
            last_referenced_turn_id=turn_id,  # Created = referenced
            referencing_turns=[turn_id],
        )

        logger.debug(f"Tracking tool output: {tool_call_id} ({token_count} tokens)")
        return True

    def mark_referenced(self, tool_call_id: str, turn_id: str) -> bool:
        """
        Mark a tool output as referenced in a turn.

        This resets the decay timer for the output. Call this when the user
        or assistant references a previous tool output.

        Args:
            tool_call_id: ID of the tool call being referenced
            turn_id: ID of the turn making the reference

        Returns:
            True if the output was found and marked, False otherwise
        """
        if tool_call_id not in self._tracked:
            return False

        output = self._tracked[tool_call_id]
        output.last_referenced_turn_id = turn_id
        output.referencing_turns.append(turn_id)
        logger.debug(f"Tool output referenced: {tool_call_id} in turn {turn_id}")
        return True

    def get_output(self, tool_call_id: str) -> TrackedToolOutput | None:
        """Get a tracked output by ID."""
        return self._tracked.get(tool_call_id)

    def get_active_outputs(self) -> list[TrackedToolOutput]:
        """Get all non-decayed tracked outputs."""
        return [o for o in self._tracked.values() if not o.is_decayed]

    def get_decayed_outputs(self) -> list[TrackedToolOutput]:
        """Get all decayed tracked outputs."""
        return [o for o in self._tracked.values() if o.is_decayed]

    async def check_and_decay(self, current_turn_number: int) -> list[str]:
        """
        Check all tracked outputs and decay stale ones.

        Compares each output's last_referenced_turn against current_turn_number.
        If the gap exceeds the decay threshold, the output is summarized.

        Args:
            current_turn_number: The current turn number in the session

        Returns:
            List of tool_call_ids that were decayed in this check
        """
        if not self.config.enabled:
            return []

        self._session_turn_count = current_turn_number
        decayed: list[str] = []

        for tool_call_id, output in self._tracked.items():
            if output.is_decayed:
                continue

            # Get decay threshold for this tool (per-tool override or default)
            threshold = self.config.tool_policies.get(
                output.tool_name, self.config.decay_threshold_turns
            )

            # Parse turn number from turn_id (assumes turn_id ends with number or is just number)  # noqa: E501
            try:
                last_ref_turn = self._parse_turn_number(
                    output.last_referenced_turn_id or output.turn_id
                )
            except ValueError:
                # If we can't parse the turn number, use the position in referencing_turns  # noqa: E501
                last_ref_turn = len(output.referencing_turns)

            gap = current_turn_number - last_ref_turn

            if gap > threshold:
                summary = await self._summarize_content(output)
                output.is_decayed = True
                output.summary = summary
                decayed.append(tool_call_id)
                logger.info(
                    f"Decayed tool output: {tool_call_id} (gap={gap}, threshold={threshold})"  # noqa: E501
                )

        return decayed

    def _parse_turn_number(self, turn_id: str) -> int:
        """
        Parse turn number from turn_id.

        Handles formats like "turn_5", "5", or UUIDs (uses position).
        """
        # Try to extract number from end of turn_id
        if turn_id.startswith("turn_"):
            return int(turn_id[5:])
        try:
            return int(turn_id)
        except ValueError:
            # For UUIDs or other formats, raise so caller can handle
            raise ValueError(f"Cannot parse turn number from: {turn_id}")  # noqa: B904

    async def _summarize_content(self, output: TrackedToolOutput) -> str:
        """
        Generate a summary of the tool output.

        Uses the LLM to create a concise summary that captures key information.
        If no LLM is available, falls back to simple truncation.

        Args:
            output: The tracked output to summarize

        Returns:
            A summary string
        """
        if not self._llm:
            # Fallback: simple truncation with indicator
            max_chars = 200
            if len(output.content) <= max_chars:
                return output.content
            return f"{output.content[:max_chars]}... [truncated, original {output.token_count} tokens]"  # noqa: E501

        prompt = f"""Summarize the following tool output in 2-3 sentences.
Focus on the key information that would be useful for future reference.

Tool: {output.tool_name}
Content:
{output.content[:4000]}

Summary:"""

        try:
            response = await self._llm.chat_completion(
                [{"role": "user", "content": prompt}]
            )
            return response.content.strip()
        except Exception as e:
            logger.warning(f"Failed to generate summary via LLM: {e}")
            # Fallback on error
            return f"{output.content[:200]}... [summarization failed, original {output.token_count} tokens]"  # noqa: E501

    def clear(self) -> int:
        """
        Clear all tracked outputs.

        Returns:
            Number of outputs cleared
        """
        count = len(self._tracked)
        self._tracked.clear()
        self._session_turn_count = 0
        logger.debug(f"Cleared {count} tracked tool outputs")
        return count

    def get_stats(self) -> dict:
        """
        Get statistics about tracked outputs.

        Returns:
            Dictionary with tracking statistics
        """
        active = [o for o in self._tracked.values() if not o.is_decayed]
        decayed = [o for o in self._tracked.values() if o.is_decayed]

        return {
            "total_tracked": len(self._tracked),
            "active_count": len(active),
            "decayed_count": len(decayed),
            "active_tokens": sum(o.token_count for o in active),
            "decayed_tokens": sum(o.token_count for o in decayed),
            "session_turn_count": self._session_turn_count,
        }
