"""
Prompt Architect (Layout Engine).
Physically structures the final prompt to optimize model attention.

Ref: Batch 2a Specification, Section 5
Ref: docs/build-plan/tool-calling-build-plan.md, Phase 4
Ref: docs/build-plan/copilot-promotion-build-plan.md (Prompt Caching)

Layout Strategy (Optimized for Attention - Default):
1. System Message: Base prompt (identity & guardrails)
2. Episodic Memory: Conversation history (chronological)
3. Final Message: Supporting context + User query
   - Known facts (graph relationship summaries)
   - Recent insights (most recent first, with timestamps)
   - Recent summaries (most recent first)
   - Tool recommendations (for recency effect)
   - Tool usage hints
   - Session state
   - User query

Layout Strategy (Optimized for Caching - Optional):
When cache_config.enabled=True, layout is reordered for prefix caching:
1. System Message: Base prompt (identity & guardrails) [CACHEABLE]
2. Static Context: Insights, facts, summaries (stable across turns) [CACHEABLE]
3. Episodic Memory: Conversation history [CACHEABLE up to breakpoint]
4. [CACHE BREAKPOINT] - Anthropic: cache_control marker
5. Dynamic Context: Tool recommendations, session state (changes per turn)
6. User Query

This allows LLM providers to cache the stable prefix:
- Anthropic: Explicit cache_control markers with ephemeral type
- OpenAI: Automatic prefix caching (no markers needed)

Tool Context Integration (Hybrid Placement):
- Full tool schemas are passed via API `tools` parameter (not in prompt)
- Tool recommendations and hints appear in supporting context
- Placed immediately before query for maximum recency effect
- Recommendations include tool name, reason, and suggested parameters

This layout combats "Lost in the Middle" by placing supporting context
immediately before the query (recency effect) rather than in the system block.
"""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Any
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from pydantic import BaseModel, Field

from friday_memory.context.token_estimator import build_token_estimator
from friday_memory.models import ContextPayload, SessionState

if TYPE_CHECKING:
    from friday_memory.context.cache_config import PromptCacheConfig
    from friday_memory.models.budget import BudgetStatus

logger = logging.getLogger(__name__)


# =============================================================================
# FORMATTING OVERHEAD CONSTANTS
# =============================================================================
# These constants account for tokens added during prompt formatting that are
# not counted during budget estimation in assembler._apply_budget().
# =============================================================================

# Per-turn overhead: timestamp prefix "[2026-01-30 14:23] " + role "[Chuck]: "
TOKENS_PER_TURN_OVERHEAD = 30

# Per-section header: "## Section Name\n"
TOKENS_PER_SECTION_HEADER = 10

# Per-passage metadata: source, type indicators, header formatting
TOKENS_PER_PASSAGE_METADATA = 15

# Per-list item: "- " prefix
TOKENS_PER_LIST_ITEM = 3

# Separator between supporting context and query
TOKENS_SEPARATOR = 10


# =============================================================================
# SUPPORTING CONTEXT CONFIGURATION
# =============================================================================
# Controls budget allocation and priority ordering for supporting context
# sections built by _build_supporting_context().
# =============================================================================


class SupportingContextConfig(BaseModel):
    """
    Configuration for supporting context budget and priority.

    The supporting context includes: known_facts, passages, insights,
    summaries, tools, and session state. This config controls how much
    of the token budget goes to supporting context vs conversation
    history, and in what order sections are added when truncating.
    """

    # Percentage of available budget allocated to supporting context (0.0-1.0)
    # Remaining budget goes to conversation history
    budget_ratio: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="Fraction of dynamic budget for supporting context",
    )

    # Priority order for sections when truncating (first = highest priority)
    # Sections with higher priority are added first and kept when space is limited
    section_priority: list[str] = Field(
        default=[
            "known_facts",
            "passages",
            "insights",
            "summaries",
            "tools",
            "state",
        ],
        description="Order of section importance (first = highest priority)",
    )

    # Maximum items per section (hard limits before budget truncation)
    max_items: dict[str, int] = Field(
        default={
            "passages": 10,
            "known_facts": 25,
            "insights": 25,
            "summaries": 10,
            "tools": 5,
        },
        description="Hard limit on items per section",
    )

# Pattern to match existing timestamp/role prefixes that may have been echoed back
# Matches patterns like: [2026-01-27 10:42] [Assistant]:
TIMESTAMP_ROLE_PATTERN = re.compile(
    r"^(\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\]\s*\[(User|Assistant|Chuck|Friday)\]:\s*)+"
)


class PromptArchitect:
    """
    Layout Engine for prompt construction.

    Structures the final prompt to combat "Lost in the Middle" and
    optimize for "System 2" reasoning. Places critical information
    at the start and end of the context for maximum attention.

    Supports optional cache-optimized layout for LLM providers that
    support prefix caching (Anthropic, OpenAI).
    """

    def __init__(
        self,
        model_name: str = "gpt-4",
        max_tokens: int = 8192,
        output_buffer: int = 1024,
        user_name: str = "User",
        assistant_name: str = "Assistant",
        cache_config: PromptCacheConfig | None = None,
        supporting_context_config: SupportingContextConfig | dict | None = None,
        token_estimator_config: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the Prompt Architect.

        Args:
            model_name: The model name for token counting
            max_tokens: Maximum context window tokens
            output_buffer: Reserved tokens for model output
            user_name: Display name for the user in conversation
            assistant_name: Display name for the assistant in conversation
            cache_config: Optional prompt caching configuration
            supporting_context_config: Optional config for supporting context
                budget and priority. If dict, will be converted to
                SupportingContextConfig. If None, uses defaults.
            token_estimator_config: Optional token estimator configuration
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.output_buffer = output_buffer
        self.user_name = user_name
        self.assistant_name = assistant_name
        self._cache_config = cache_config

        # Initialize supporting context config
        if supporting_context_config is None:
            self._supporting_context_config = SupportingContextConfig()
        elif isinstance(supporting_context_config, dict):
            self._supporting_context_config = SupportingContextConfig(**supporting_context_config)
        else:
            self._supporting_context_config = supporting_context_config

        # Token counting now uses a configurable estimator (approx by default).
        self._token_estimator = build_token_estimator(token_estimator_config, model_name)

        # Budget status from the most recent format_prompt() call.
        # Populated by _validate_prompt_budget() for downstream consumers
        # (e.g. ContextBudgetMonitor).
        self.last_budget_status: BudgetStatus | None = None

    @property
    def cache_config(self) -> PromptCacheConfig | None:
        """Access the cache configuration."""
        return self._cache_config

    def set_cache_config(self, config: PromptCacheConfig | None) -> None:
        """Update the cache configuration."""
        self._cache_config = config

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        # Swapped from tiktoken to estimator to reduce CPU latency.
        return self._token_estimator.count(text)

    def _strip_existing_prefixes(self, text: str) -> str:
        """
        Strip any existing timestamp/role prefixes from message content.

        This prevents nested prefixes when LLM echoes back formatted context.
        Patterns like "[2026-01-27 10:42] [Assistant]: ..." are stripped.

        Args:
            text: The message text to clean

        Returns:
            Text with existing prefixes removed
        """
        if not text:
            return text
        return TIMESTAMP_ROLE_PATTERN.sub("", text)

    def format_prompt(
        self,
        system_prompt: str,
        user_query: str,
        payload: ContextPayload,
        state: SessionState | None = None,
        tool_definitions: list[dict[str, Any]] | None = None,
        context_format: str = "plain",
        turn_count: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Arranges messages for optimal model attention.

        Implements the layout strategy defined in Batch 2a Section 5.
        When cache_config is enabled and conditions are met, uses
        cache-optimized layout instead.

        Args:
            system_prompt: The base system prompt (identity & guardrails)
            user_query: The current user message
            payload: The assembled context payload
            state: Optional session state for scoped variables
            tool_definitions: Optional tool definitions for the model
            context_format: Output format for supporting context.
                Options: "plain" (default), "json", "xml", "markdown"
            turn_count: Current conversation turn count (for cache eligibility)

        Returns:
            List of message dicts in OpenAI-compatible format
        """
        # Check if we should use cache-optimized layout
        if self._cache_config and self._cache_config.should_cache(turn_count, self.model_name):
            messages = self._format_prompt_cached(
                system_prompt=system_prompt,
                user_query=user_query,
                payload=payload,
                state=state,
                tool_definitions=tool_definitions,
                context_format=context_format,
            )
        else:
            # Default attention-optimized layout
            messages = self._format_prompt_attention(
                system_prompt=system_prompt,
                user_query=user_query,
                payload=payload,
                state=state,
                tool_definitions=tool_definitions,
                context_format=context_format,
            )

        # Post-format validation: warn if budget exceeded
        self.last_budget_status = self._validate_prompt_budget(
            messages, tool_definitions
        )

        return messages

    def _validate_prompt_budget(
        self,
        messages: list[dict[str, Any]],
        tool_definitions: list[dict[str, Any]] | None = None,
    ) -> BudgetStatus:
        """Validate that the formatted prompt fits the token budget.

        Computes utilization metrics, classifies severity, and logs
        a warning when the prompt exceeds the budget. Returns a
        ``BudgetStatus`` so that downstream consumers (e.g.
        ``ContextBudgetMonitor``) can decide whether to trigger
        background compaction.

        Args:
            messages: The formatted messages array.
            tool_definitions: Optional tool definitions.

        Returns:
            BudgetStatus with utilization data and severity.
        """
        from friday_memory.models.budget import (
            BudgetSeverity,
            BudgetStatus,
        )

        # Calculate total tokens in messages
        message_tokens = sum(
            self.count_tokens(m.get("content", ""))
            for m in messages
        )

        # Add tool definition tokens if present
        tool_tokens = 0
        if tool_definitions:
            tool_tokens = self.count_tokens(
                json.dumps(tool_definitions)
            )

        total_tokens = message_tokens + tool_tokens

        # Available budget = max_tokens - output_buffer
        available_budget = self.max_tokens - self.output_buffer

        utilization_pct = (
            (total_tokens / available_budget) * 100
            if available_budget > 0
            else 100.0
        )
        overage = max(0, total_tokens - available_budget)
        severity = BudgetSeverity.from_utilization(
            utilization_pct
        )

        # Backward-compatible logging
        if total_tokens > available_budget:
            overage_pct = (overage / available_budget) * 100
            logger.warning(
                "Prompt exceeds budget: %d > %d tokens "
                "(overage: %d tokens, %.1f%%). "
                "Consider reducing history or increasing "
                "context_window.",
                total_tokens,
                available_budget,
                overage,
                overage_pct,
            )
        else:
            logger.debug(
                "Prompt budget: %d/%d tokens "
                "(%.1f%% utilized)",
                total_tokens,
                available_budget,
                utilization_pct,
            )

        return BudgetStatus(
            total_tokens=total_tokens,
            available_budget=available_budget,
            utilization_pct=utilization_pct,
            overage_tokens=overage,
            severity=severity,
            message_tokens=message_tokens,
            tool_tokens=tool_tokens,
        )

    def _format_prompt_attention(
        self,
        system_prompt: str,
        user_query: str,
        payload: ContextPayload,
        state: SessionState | None = None,
        tool_definitions: list[dict[str, Any]] | None = None,
        context_format: str = "plain",
    ) -> list[dict[str, Any]]:
        """
        Default attention-optimized layout (combats "Lost in the Middle").

        Layout:
        1. System message
        2. Conversation history
        3. Supporting context + User query (recency effect)

        Budget allocation:
        - Fixed costs: system_prompt + tool_definitions + output_buffer
        - Dynamic budget: max_tokens - fixed_costs
        - Supporting context gets: dynamic_budget * budget_ratio
        - History gets: remaining dynamic budget
        """
        messages: list[dict[str, Any]] = []

        # Calculate budget for supporting context
        # Dynamic budget = max_tokens - system_prompt - tools - output_buffer
        fixed_costs = self.calculate_fixed_costs(system_prompt, tool_definitions)
        dynamic_budget = max(0, self.max_tokens - fixed_costs)

        # Supporting context budget = dynamic_budget * budget_ratio
        config = self._supporting_context_config
        supporting_context_budget = int(dynamic_budget * config.budget_ratio)

        logger.debug(
            f"Budget allocation: max_tokens={self.max_tokens}, "
            f"fixed={fixed_costs}, dynamic={dynamic_budget}, "
            f"supporting_context={supporting_context_budget} "
            f"(ratio={config.budget_ratio})"
        )

        # 1. System message (base prompt only)
        system_content = self._build_system_content(system_prompt)
        messages.append({"role": "system", "content": system_content})

        # 2. Episodic memory (conversation history, chronological)
        # Merge prior_history + history (prior sessions first, then current session)
        all_history = list(payload.prior_history) + list(payload.history)
        for turn in all_history:
            # Skip incomplete turns (no assistant response).
            # This prevents orphaned user messages from appearing as pending questions.
            # Can happen from interrupted sessions or failed LLM calls.
            if turn.user_message and not turn.assistant_message and not turn.tool_calls:
                continue

            # Format timestamp for temporal context: [YYYY-MM-DD HH:MM]
            timestamp_str = ""
            if turn.timestamp:
                timestamp_str = f"[{turn.timestamp.strftime('%Y-%m-%d %H:%M')}] "

            # Append user message
            if turn.user_message:
                # Strip any echoed timestamp/role prefixes to prevent nesting
                clean_msg = self._strip_existing_prefixes(turn.user_message)
                messages.append({
                    "role": "user",
                    "content": f"{timestamp_str}[{self.user_name}]: {clean_msg}",
                })

            # Check if this turn has tool calls
            # NOTE: Historical tool calls are rendered as plain text summaries, not native
            # tool message format. Native format requires strict pairing (tool_result must
            # immediately follow its tool_call), which breaks when restoring history.
            # Current in-progress tool interactions use native format via _process_with_tools().
            #
            # Lifecycle support: If a tool result has is_decayed=True, we render the
            # summary instead of the full output to save context tokens.
            if turn.tool_calls:
                # Build assistant message with tool call summaries
                tool_summary_parts = []
                if turn.assistant_message:
                    # Strip any echoed timestamp/role prefixes from the message
                    clean_msg = self._strip_existing_prefixes(turn.assistant_message)
                    tool_summary_parts.append(clean_msg)

                # Summarize each tool call and its result
                tool_summary_parts.append("\n[Tool Calls:]")
                for tc in turn.tool_calls:
                    args_str = ", ".join(f"{k}={v!r}" for k, v in tc.arguments.items())
                    tool_summary_parts.append(f"  → {tc.name}({args_str})")

                    # Find matching result
                    for tr in turn.tool_results:
                        if tr.tool_call_id == tc.id:
                            if tr.error:
                                tool_summary_parts.append(f"    ✗ Error: {tr.error}")
                            else:
                                # Check if output has been decayed (summarized)
                                is_decayed = getattr(tr, "is_decayed", False)
                                summary = getattr(tr, "summary", None)

                                if is_decayed and summary:
                                    # Use the LLM-generated summary for decayed outputs
                                    tool_summary_parts.append(f"    ✓ [Summary]: {summary}")
                                else:
                                    # Full output (truncate if too long)
                                    output_str = str(tr.output) if tr.output else ""
                                    if len(output_str) > 500:
                                        output_str = output_str[:500] + "..."
                                    tool_summary_parts.append(f"    ✓ {output_str}")
                            break

                messages.append({
                    "role": "assistant",
                    "content": f"{timestamp_str}[{self.assistant_name}]: " + "\n".join(tool_summary_parts),
                })
            elif turn.assistant_message:
                # No tool calls - just append assistant message
                # Strip any echoed timestamp/role prefixes to prevent nesting
                clean_msg = self._strip_existing_prefixes(turn.assistant_message)
                messages.append({
                    "role": "assistant",
                    "content": f"{timestamp_str}[{self.assistant_name}]: {clean_msg}",
                })

        # 3. Final message: supporting context + query
        # Supporting context is placed immediately before the query for recency effect
        # Pass the calculated budget to enable truncation
        supporting_context = self._build_supporting_context(
            payload, state, context_format, max_tokens=supporting_context_budget
        )
        if supporting_context:
            final_content = f"{supporting_context}\n\n---\n\n[{self.user_name}]: {user_query}"
        else:
            final_content = f"[{self.user_name}]: {user_query}"

        messages.append({"role": "user", "content": final_content})

        return messages

    def _format_prompt_cached(
        self,
        system_prompt: str,
        user_query: str,
        payload: ContextPayload,
        state: SessionState | None = None,
        tool_definitions: list[dict[str, Any]] | None = None,
        context_format: str = "plain",
    ) -> list[dict[str, Any]]:
        """
        Cache-optimized layout for LLM providers with prefix caching.

        Layout (optimized for cache hits):
        1. System message [CACHEABLE]
        2. Static context (insights, facts, summaries) [CACHEABLE - if configured]
        3. Conversation history [CACHEABLE up to breakpoint]
        4. [CACHE BREAKPOINT - Anthropic cache_control marker]
        5. Dynamic context (tool recommendations, state)
        6. User query

        For Anthropic: Adds cache_control markers to messages.
        For OpenAI: Layout only (auto-prefix caching).
        """
        from friday_memory.context.cache_config import CacheBreakpoint, CacheProvider

        messages: list[dict[str, Any]] = []
        cache_marker = self._cache_config.get_cache_control_marker(self.model_name) if self._cache_config else None
        provider = self._cache_config.detect_provider(self.model_name) if self._cache_config else CacheProvider.NONE
        breakpoint = self._cache_config.breakpoint if self._cache_config else CacheBreakpoint.AFTER_HISTORY

        # 1. System message [CACHEABLE]
        system_content = self._build_system_content(system_prompt)
        system_msg: dict[str, Any] = {"role": "system", "content": system_content}

        # Add cache marker for system-only breakpoint
        if breakpoint == CacheBreakpoint.SYSTEM_ONLY and cache_marker and provider == CacheProvider.ANTHROPIC:
            system_msg["cache_control"] = cache_marker

        messages.append(system_msg)

        # 2. Static context (if configured to be in prefix) [CACHEABLE]
        static_context = ""
        if self._cache_config and self._cache_config.static_context_in_prefix:
            static_context = self._build_static_context(payload, context_format)

        if static_context:
            static_msg: dict[str, Any] = {"role": "user", "content": f"[Context Reference]\n{static_context}"}

            # Add cache marker for after-static breakpoint
            if breakpoint == CacheBreakpoint.AFTER_STATIC and cache_marker and provider == CacheProvider.ANTHROPIC:
                static_msg["cache_control"] = cache_marker

            messages.append(static_msg)

            # Add assistant acknowledgment for proper message alternation
            messages.append({"role": "assistant", "content": "[Context loaded]"})

        # 3. Conversation history [CACHEABLE up to breakpoint]
        all_history = list(payload.prior_history) + list(payload.history)
        for i, turn in enumerate(all_history):
            # Skip incomplete turns (no assistant response).
            # This prevents orphaned user messages from appearing as pending questions.
            if turn.user_message and not turn.assistant_message and not turn.tool_calls:
                continue

            timestamp_str = ""
            if turn.timestamp:
                timestamp_str = f"[{turn.timestamp.strftime('%Y-%m-%d %H:%M')}] "

            # User message
            if turn.user_message:
                clean_msg = self._strip_existing_prefixes(turn.user_message)
                messages.append({
                    "role": "user",
                    "content": f"{timestamp_str}[{self.user_name}]: {clean_msg}",
                })

            # Assistant message (with tool call handling)
            if turn.tool_calls:
                tool_summary_parts = []
                if turn.assistant_message:
                    clean_msg = self._strip_existing_prefixes(turn.assistant_message)
                    tool_summary_parts.append(clean_msg)

                tool_summary_parts.append("\n[Tool Calls:]")
                for tc in turn.tool_calls:
                    args_str = ", ".join(f"{k}={v!r}" for k, v in tc.arguments.items())
                    tool_summary_parts.append(f"  → {tc.name}({args_str})")

                    for tr in turn.tool_results:
                        if tr.tool_call_id == tc.id:
                            if tr.error:
                                tool_summary_parts.append(f"    ✗ Error: {tr.error}")
                            else:
                                is_decayed = getattr(tr, "is_decayed", False)
                                summary = getattr(tr, "summary", None)
                                if is_decayed and summary:
                                    tool_summary_parts.append(f"    ✓ [Summary]: {summary}")
                                else:
                                    output_str = str(tr.output) if tr.output else ""
                                    if len(output_str) > 500:
                                        output_str = output_str[:500] + "..."
                                    tool_summary_parts.append(f"    ✓ {output_str}")
                            break

                assistant_msg: dict[str, Any] = {
                    "role": "assistant",
                    "content": f"{timestamp_str}[{self.assistant_name}]: " + "\n".join(tool_summary_parts),
                }

                # Add cache marker on last history message for after-history breakpoint
                is_last = (i == len(all_history) - 1)
                if is_last and breakpoint == CacheBreakpoint.AFTER_HISTORY and cache_marker and provider == CacheProvider.ANTHROPIC:
                    assistant_msg["cache_control"] = cache_marker

                messages.append(assistant_msg)

            elif turn.assistant_message:
                clean_msg = self._strip_existing_prefixes(turn.assistant_message)
                assistant_msg = {
                    "role": "assistant",
                    "content": f"{timestamp_str}[{self.assistant_name}]: {clean_msg}",
                }

                # Add cache marker on last history message
                is_last = (i == len(all_history) - 1)
                if is_last and breakpoint == CacheBreakpoint.AFTER_HISTORY and cache_marker and provider == CacheProvider.ANTHROPIC:
                    assistant_msg["cache_control"] = cache_marker

                messages.append(assistant_msg)

        # 4. Dynamic context + User query [NOT CACHED - changes each turn]
        # Build dynamic context (tool recommendations, session state)
        dynamic_context = self._build_dynamic_context(payload, state, context_format)

        if dynamic_context:
            final_content = f"{dynamic_context}\n\n---\n\n[{self.user_name}]: {user_query}"
        else:
            final_content = f"[{self.user_name}]: {user_query}"

        messages.append({"role": "user", "content": final_content})

        return messages

    def _build_static_context(
        self,
        payload: ContextPayload,
        context_format: str = "plain",
    ) -> str:
        """
        Build static context block (stable across turns, suitable for caching).

        Includes: known facts, insights, summaries, passages.
        Excludes: tool recommendations, session state (dynamic per turn).

        Args:
            payload: The context payload
            context_format: Output format

        Returns:
            Formatted static context string
        """
        sections: list[str] = []

        # Known facts (graph relationship summaries)
        if payload.recent_memories:
            sections.append("## Known Facts")
            for memory in payload.recent_memories:
                sections.append(memory)

        # Semantic passages from vector search
        if payload.passages:
            sections.append("\n## Relevant Context")
            for i, passage in enumerate(payload.passages[:10], 1):
                text = passage.get("text", "")
                metadata = passage.get("metadata", {})
                source = metadata.get("filename") or metadata.get("source", "memory")
                doc_type = metadata.get("type", "")

                header = f"### [{source}]"
                if doc_type == "ingested_file":
                    header += " (ingested)"
                elif doc_type == "tool_output":
                    tool_name = metadata.get("tool_name", "")
                    header += f" (from {tool_name})"
                sections.append(header)
                sections.append(text)
                sections.append("")

        # Recent insights (with timestamps)
        if payload.insights:
            sections.append("\n## Recent Insights")
            for insight in payload.insights:
                text = insight.get("text", "")
                created_at = insight.get("metadata", {}).get("created_at", "")
                timestamp = created_at[:16] if created_at else ""
                if timestamp:
                    sections.append(f"- [{timestamp}] {text}")
                else:
                    sections.append(f"- {text}")

        # Conversation summaries
        if payload.summaries:
            sections.append("\n## Conversation Summaries")
            for summary in payload.summaries:
                text = summary.get("text", "")
                sections.append(f"- {text}")

        return "\n".join(sections) if sections else ""

    def _build_dynamic_context(
        self,
        payload: ContextPayload,
        state: SessionState | None,
        context_format: str = "plain",
    ) -> str:
        """
        Build dynamic context block (changes per turn, not cached).

        Includes: tool recommendations, tool hints, session state.
        Excludes: insights, facts, summaries (static, cached separately).

        Args:
            payload: The context payload
            state: Optional session state
            context_format: Output format

        Returns:
            Formatted dynamic context string
        """
        sections: list[str] = []

        # Tool recommendations
        if payload.recommended_tools:
            sections.append("## Recommended Tools")
            for rec in payload.recommended_tools:
                if hasattr(rec, "tool_name"):
                    tool_name = rec.tool_name
                    reason = rec.reason
                    suggested = getattr(rec, "suggested_parameters", None)
                else:
                    tool_name = rec.get("tool_name", "unknown")
                    reason = rec.get("reason", "")
                    suggested = rec.get("suggested_parameters")

                line = f"- {tool_name}: {reason}"
                if suggested:
                    params = ", ".join(f"{k}={v}" for k, v in suggested.items())
                    line += f" (suggested: {params})"
                sections.append(line)

        # Tool usage hints
        if payload.tool_usage_hints:
            sections.append("\n## Tool Usage Notes")
            for hint in payload.tool_usage_hints:
                sections.append(f"- {hint}")

        # Session state
        if state and state.scoped_vars:
            state_block = self._format_state_block(state)
            sections.append(f"\n{state_block}")

        return "\n".join(sections) if sections else ""

    def _build_system_content(self, base_prompt: str) -> str:
        """
        Build the system prompt with identity and guardrails only.

        Supporting context (insights, summaries, entities) is now placed
        at the tail of the context, immediately before the query.

        Args:
            base_prompt: The base system prompt (identity & guardrails)

        Returns:
            System prompt content
        """
        # For now, just return the base prompt
        # Future: Add function/tool definitions here when Friday-Tools integration is added
        return base_prompt

    def _build_supporting_context(
        self,
        payload: ContextPayload,
        state: SessionState | None,
        context_format: str = "plain",
        max_tokens: int | None = None,
    ) -> str:
        """
        Build supporting context block for injection before query.

        Placed at the tail of the context to leverage recency effect.
        Content is ordered by section_priority in config, with budget-aware
        truncation when max_tokens is specified.

        Args:
            payload: The context payload with insights, summaries, entities
            state: Optional session state for scoped variables
            context_format: Output format ("plain", "json", "xml", "markdown")
            max_tokens: Optional token budget for supporting context.
                If specified, sections are added in priority order until
                budget is exhausted.

        Returns:
            Formatted supporting context string, or empty string if no content
        """
        match context_format:
            case "json":
                return self._format_context_json(payload, state, max_tokens)
            case "xml":
                return self._format_context_xml(payload, state, max_tokens)
            case "markdown":
                return self._format_context_markdown(payload, state, max_tokens)
            case _:  # plain (default)
                return self._format_context_plain(payload, state, max_tokens)

    def _format_context_plain(
        self,
        payload: ContextPayload,
        state: SessionState | None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Format supporting context as plain text with budget-aware truncation.

        When max_tokens is specified, sections are built in priority order
        and truncated when the budget is exhausted.

        Args:
            payload: The context payload
            state: Optional session state
            max_tokens: Optional token budget (None = no limit)

        Returns:
            Formatted supporting context string
        """
        config = self._supporting_context_config
        sections: list[str] = []
        tokens_used = 0

        # Build section builders for each section type
        section_builders: dict[str, callable] = {
            "known_facts": lambda: self._build_section_known_facts(payload, config),
            "passages": lambda: self._build_section_passages(payload, config),
            "insights": lambda: self._build_section_insights(payload, config),
            "summaries": lambda: self._build_section_summaries(payload, config),
            "tools": lambda: self._build_section_tools(payload, config),
            "state": lambda: self._build_section_state(state),
        }

        # Build sections in priority order
        for section_name in config.section_priority:
            if max_tokens and tokens_used >= max_tokens:
                logger.debug(
                    f"Supporting context budget exhausted at section '{section_name}' "
                    f"({tokens_used}/{max_tokens} tokens)"
                )
                break

            builder = section_builders.get(section_name)
            if not builder:
                continue

            section_content = builder()
            if not section_content:
                continue

            section_tokens = self.count_tokens(section_content)

            # Check if this section fits in remaining budget
            if max_tokens:
                remaining = max_tokens - tokens_used
                if section_tokens > remaining:
                    # Try to truncate the section to fit
                    truncated = self._truncate_section_to_budget(
                        section_content, remaining
                    )
                    if truncated:
                        sections.append(truncated)
                        tokens_used += self.count_tokens(truncated)
                        logger.debug(
                            f"Truncated section '{section_name}' to fit budget "
                            f"({self.count_tokens(truncated)}/{section_tokens} tokens)"
                        )
                    break
                else:
                    sections.append(section_content)
                    tokens_used += section_tokens
            else:
                sections.append(section_content)
                tokens_used += section_tokens

        if max_tokens:
            logger.debug(
                f"Supporting context built: {tokens_used}/{max_tokens} tokens "
                f"({len(sections)} sections)"
            )

        return "\n".join(sections) if sections else ""

    def _build_section_known_facts(
        self, payload: ContextPayload, config: SupportingContextConfig
    ) -> str:
        """Build the known facts section from graph relationship summaries."""
        if not payload.recent_memories:
            return ""

        max_facts = config.max_items.get("known_facts", 25)
        lines = ["## Known Facts"]
        for memory in payload.recent_memories[:max_facts]:
            lines.append(memory)
        return "\n".join(lines)

    def _build_section_passages(
        self, payload: ContextPayload, config: SupportingContextConfig
    ) -> str:
        """Build the passages (relevant context) section."""
        if not payload.passages:
            return ""

        max_passages = config.max_items.get("passages", 10)
        lines = ["\n## Relevant Context"]

        for i, passage in enumerate(payload.passages[:max_passages], 1):
            text = passage.get("text", "")
            metadata = passage.get("metadata", {})
            source = metadata.get("filename") or metadata.get("source", "memory")
            doc_type = metadata.get("type", "")

            header = f"### [{source}]"
            if doc_type == "ingested_file":
                header += " (ingested)"
            elif doc_type == "tool_output":
                tool_name = metadata.get("tool_name", "")
                header += f" (from {tool_name})"
            lines.append(header)
            lines.append(text)
            lines.append("")

        return "\n".join(lines)

    def _build_section_insights(
        self, payload: ContextPayload, config: SupportingContextConfig
    ) -> str:
        """Build the insights section with timestamps."""
        if not payload.insights:
            return ""

        max_insights = config.max_items.get("insights", 25)
        lines = ["\n## Recent Insights"]

        for insight in payload.insights[:max_insights]:
            text = insight.get("text", "")
            created_at = insight.get("metadata", {}).get("created_at", "")
            timestamp = created_at[:16] if created_at else ""
            if timestamp:
                lines.append(f"- [{timestamp}] {text}")
            else:
                lines.append(f"- {text}")

        return "\n".join(lines)

    def _build_section_summaries(
        self, payload: ContextPayload, config: SupportingContextConfig
    ) -> str:
        """Build the summaries section with timestamps."""
        if not payload.summaries:
            return ""

        max_summaries = config.max_items.get("summaries", 10)
        lines = ["\n## Conversation Summaries"]

        for summary in payload.summaries[:max_summaries]:
            text = summary.get("text", "")
            created_at = summary.get("metadata", {}).get("created_at", "")
            timestamp = created_at[:16] if created_at else ""
            if timestamp:
                lines.append(f"- **[{timestamp}]** {text}")
            else:
                lines.append(f"- {text}")

        return "\n".join(lines)

    def _build_section_tools(
        self, payload: ContextPayload, config: SupportingContextConfig
    ) -> str:
        """Build the tools section (recommendations + hints)."""
        lines: list[str] = []
        max_tools = config.max_items.get("tools", 5)

        if payload.recommended_tools:
            lines.append("\n## Recommended Tools")
            for rec in payload.recommended_tools[:max_tools]:
                if hasattr(rec, "tool_name"):
                    tool_name = rec.tool_name
                    reason = rec.reason
                    suggested = getattr(rec, "suggested_parameters", None)
                else:
                    tool_name = rec.get("tool_name", "unknown")
                    reason = rec.get("reason", "")
                    suggested = rec.get("suggested_parameters")

                line = f"- {tool_name}: {reason}"
                if suggested:
                    params = ", ".join(f"{k}={v}" for k, v in suggested.items())
                    line += f" (suggested: {params})"
                lines.append(line)

        if payload.tool_usage_hints:
            lines.append("\n## Tool Usage Notes")
            for hint in payload.tool_usage_hints:
                lines.append(f"- {hint}")

        return "\n".join(lines) if lines else ""

    def _build_section_state(self, state: SessionState | None) -> str:
        """Build the session state section."""
        if not state or not state.scoped_vars:
            return ""

        return f"\n{self._format_state_block(state)}"

    def _truncate_section_to_budget(
        self, section_content: str, max_tokens: int
    ) -> str:
        """
        Truncate a section to fit within the given token budget.

        Tries to preserve complete items (lines) rather than cutting mid-line.

        Args:
            section_content: The section content to truncate
            max_tokens: Maximum tokens allowed

        Returns:
            Truncated section content, or empty string if even header doesn't fit
        """
        if self.count_tokens(section_content) <= max_tokens:
            return section_content

        lines = section_content.split("\n")
        if not lines:
            return ""

        # Always keep the header (first line or two)
        result_lines: list[str] = []
        tokens_used = 0

        for i, line in enumerate(lines):
            line_tokens = self.count_tokens(line + "\n")

            # Check if this line fits
            if tokens_used + line_tokens > max_tokens:
                # Don't cut the header (first 2 lines typically)
                if i < 2:
                    continue
                break

            result_lines.append(line)
            tokens_used += line_tokens

        if len(result_lines) > 2:  # Has content beyond header
            result_lines.append("  ... (truncated due to budget)")

        return "\n".join(result_lines) if result_lines else ""

    def _format_context_json(
        self,
        payload: ContextPayload,
        state: SessionState | None,
        max_tokens: int | None = None,
    ) -> str:
        """Format supporting context as JSON.

        Note: max_tokens is accepted for interface compatibility but JSON
        format doesn't implement per-section truncation (entire output is
        built then truncated if needed).
        """
        context: dict[str, Any] = {}

        if payload.recent_memories:
            context["known_facts"] = payload.recent_memories

        if payload.passages:
            context["relevant_context"] = [
                {
                    "text": p.get("text", ""),
                    "source": p.get("metadata", {}).get("filename") or p.get("metadata", {}).get("source", "memory"),
                    "type": p.get("metadata", {}).get("type", ""),
                    "similarity": p.get("similarity", 0.0),
                }
                for p in payload.passages[:10]
            ]

        if payload.insights:
            context["recent_insights"] = [
                {
                    "text": i.get("text", ""),
                    "created_at": i.get("metadata", {}).get("created_at", ""),
                }
                for i in payload.insights
            ]

        if payload.summaries:
            context["conversation_summaries"] = [
                {
                    "text": s.get("text", ""),
                    "created_at": s.get("metadata", {}).get("created_at", ""),
                }
                for s in payload.summaries
            ]

        # Tool recommendations
        if payload.recommended_tools:
            recommendations = []
            for rec in payload.recommended_tools:
                if hasattr(rec, "tool_name"):
                    recommendations.append({
                        "tool_name": rec.tool_name,
                        "reason": rec.reason,
                        "relevance_score": getattr(rec, "relevance_score", 0.0),
                        "suggested_parameters": getattr(rec, "suggested_parameters", None),
                    })
                else:
                    recommendations.append({
                        "tool_name": rec.get("tool_name", "unknown"),
                        "reason": rec.get("reason", ""),
                        "relevance_score": rec.get("relevance_score", 0.0),
                        "suggested_parameters": rec.get("suggested_parameters"),
                    })
            context["recommended_tools"] = recommendations

        # Tool usage hints
        if payload.tool_usage_hints:
            context["tool_usage_hints"] = payload.tool_usage_hints

        if state and state.scoped_vars:
            context["session_state"] = dict(state.scoped_vars)

        return json.dumps(context, indent=2) if context else ""

    def _format_context_xml(
        self,
        payload: ContextPayload,
        state: SessionState | None,
        max_tokens: int | None = None,
    ) -> str:
        """Format supporting context as XML.

        Note: max_tokens is accepted for interface compatibility but XML
        format doesn't implement per-section truncation.
        """
        root = Element("supporting_context")

        if payload.recent_memories:
            facts = SubElement(root, "known_facts")
            for mem in payload.recent_memories:
                fact = SubElement(facts, "fact")
                fact.text = mem

        if payload.passages:
            passages_elem = SubElement(root, "relevant_context")
            for p in payload.passages[:10]:
                passage_elem = SubElement(passages_elem, "passage")
                metadata = p.get("metadata", {})
                source = metadata.get("filename") or metadata.get("source", "memory")
                passage_elem.set("source", source)
                passage_elem.set("type", metadata.get("type", ""))
                passage_elem.set("similarity", str(p.get("similarity", 0.0)))
                passage_elem.text = p.get("text", "")

        if payload.insights:
            insights_elem = SubElement(root, "recent_insights")
            for i in payload.insights:
                insight = SubElement(insights_elem, "insight")
                created_at = i.get("metadata", {}).get("created_at", "")
                if created_at:
                    insight.set("created_at", created_at)
                insight.text = i.get("text", "")

        if payload.summaries:
            summaries_elem = SubElement(root, "conversation_summaries")
            for s in payload.summaries:
                summary = SubElement(summaries_elem, "summary")
                created_at = s.get("metadata", {}).get("created_at", "")
                if created_at:
                    summary.set("created_at", created_at)
                summary.text = s.get("text", "")

        # Tool recommendations
        if payload.recommended_tools:
            tools_elem = SubElement(root, "recommended_tools")
            for rec in payload.recommended_tools:
                tool_elem = SubElement(tools_elem, "tool")
                if hasattr(rec, "tool_name"):
                    tool_elem.set("name", rec.tool_name)
                    tool_elem.set("relevance", str(getattr(rec, "relevance_score", 0.0)))
                    reason_elem = SubElement(tool_elem, "reason")
                    reason_elem.text = rec.reason
                    suggested = getattr(rec, "suggested_parameters", None)
                    if suggested:
                        params_elem = SubElement(tool_elem, "suggested_parameters")
                        for k, v in suggested.items():
                            param = SubElement(params_elem, "param")
                            param.set("name", k)
                            param.text = str(v)
                else:
                    tool_elem.set("name", rec.get("tool_name", "unknown"))
                    tool_elem.set("relevance", str(rec.get("relevance_score", 0.0)))
                    reason_elem = SubElement(tool_elem, "reason")
                    reason_elem.text = rec.get("reason", "")
                    suggested = rec.get("suggested_parameters")
                    if suggested:
                        params_elem = SubElement(tool_elem, "suggested_parameters")
                        for k, v in suggested.items():
                            param = SubElement(params_elem, "param")
                            param.set("name", k)
                            param.text = str(v)

        # Tool usage hints
        if payload.tool_usage_hints:
            hints_elem = SubElement(root, "tool_usage_hints")
            for hint in payload.tool_usage_hints:
                hint_elem = SubElement(hints_elem, "hint")
                hint_elem.text = hint

        if state and state.scoped_vars:
            state_elem = SubElement(root, "session_state")
            for key, value in state.scoped_vars.items():
                var = SubElement(state_elem, "var")
                var.set("key", key)
                var.text = str(value)

        # Check if we have any children
        if len(root) == 0:
            return ""

        # Pretty print
        rough_string = tostring(root, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        # Remove XML declaration line
        lines = reparsed.toprettyxml(indent="  ").split("\n")
        return "\n".join(lines[1:]).strip()

    def _format_context_markdown(
        self,
        payload: ContextPayload,
        state: SessionState | None,
        max_tokens: int | None = None,
    ) -> str:
        """Format supporting context as structured markdown with tables.

        Uses the same budget-aware section-builder loop as the plain format,
        but produces markdown tables for structured data (known facts, tools)
        and timestamped bullets for insights/summaries.

        Sections are built in priority order from SupportingContextConfig.
        Each section respects max_items limits. When max_tokens is specified,
        sections are truncated when the budget is exhausted.

        Args:
            payload: The context payload
            state: Optional session state
            max_tokens: Optional token budget (None = no limit)

        Returns:
            Formatted supporting context string in markdown
        """
        config = self._supporting_context_config
        sections: list[str] = []
        tokens_used = 0

        # Build section builders for each section type (markdown variants)
        section_builders: dict[str, callable] = {
            "known_facts": lambda: self._build_section_known_facts_md(
                payload, config
            ),
            "passages": lambda: self._build_section_passages_md(
                payload, config
            ),
            "insights": lambda: self._build_section_insights_md(
                payload, config
            ),
            "summaries": lambda: self._build_section_summaries_md(
                payload, config
            ),
            "tools": lambda: self._build_section_tools_md(payload, config),
            "state": lambda: self._build_section_state(state),
        }

        # Build sections in priority order (same loop as plain format)
        for section_name in config.section_priority:
            if max_tokens and tokens_used >= max_tokens:
                logger.debug(
                    f"Markdown context budget exhausted at '{section_name}' "
                    f"({tokens_used}/{max_tokens} tokens)"
                )
                break

            builder = section_builders.get(section_name)
            if not builder:
                continue

            section_content = builder()
            if not section_content:
                continue

            section_tokens = self.count_tokens(section_content)

            # Check if this section fits in remaining budget
            if max_tokens:
                remaining = max_tokens - tokens_used
                if section_tokens > remaining:
                    truncated = self._truncate_section_to_budget(
                        section_content, remaining
                    )
                    if truncated:
                        sections.append(truncated)
                        tokens_used += self.count_tokens(truncated)
                        logger.debug(
                            f"Truncated markdown section '{section_name}' "
                            f"({self.count_tokens(truncated)}/{section_tokens})"
                        )
                    break
                else:
                    sections.append(section_content)
                    tokens_used += section_tokens
            else:
                sections.append(section_content)
                tokens_used += section_tokens

        if max_tokens:
            logger.debug(
                f"Markdown context built: {tokens_used}/{max_tokens} tokens "
                f"({len(sections)} sections)"
            )

        return "\n".join(sections) if sections else ""

    # --- Markdown Section Builders ---

    def _build_section_known_facts_md(
        self, payload: ContextPayload, config: SupportingContextConfig
    ) -> str:
        """Build known facts as a markdown table with max_items enforcement."""
        if not payload.recent_memories:
            return ""

        max_facts = config.max_items.get("known_facts", 25)
        lines = ["## Known Facts", "", "| Fact |", "|------|"]
        for mem in payload.recent_memories[:max_facts]:
            lines.append(f"| {mem} |")
        return "\n".join(lines)

    def _build_section_passages_md(
        self, payload: ContextPayload, config: SupportingContextConfig
    ) -> str:
        """Build passages section in markdown with max_items enforcement."""
        if not payload.passages:
            return ""

        max_passages = config.max_items.get("passages", 10)
        lines = ["\n## Relevant Context", ""]

        for passage in payload.passages[:max_passages]:
            text = passage.get("text", "")
            metadata = passage.get("metadata", {})
            source = (
                metadata.get("filename")
                or metadata.get("source", "memory")
            )
            doc_type = metadata.get("type", "")
            similarity = passage.get("similarity", 0.0)

            header = f"### {source}"
            if doc_type == "ingested_file":
                header += " *(ingested)*"
            elif doc_type == "tool_output":
                tool_name = metadata.get("tool_name", "")
                header += f" *(from {tool_name})*"
            lines.append(header)
            lines.append(f"*Relevance: {similarity:.2f}*")
            lines.append("")
            lines.append(text)
            lines.append("")

        return "\n".join(lines)

    def _build_section_insights_md(
        self, payload: ContextPayload, config: SupportingContextConfig
    ) -> str:
        """Build insights section as timestamped markdown bullets."""
        if not payload.insights:
            return ""

        max_insights = config.max_items.get("insights", 25)
        lines = ["\n## Recent Insights", ""]

        for insight in payload.insights[:max_insights]:
            text = insight.get("text", "")
            created_at = insight.get("metadata", {}).get("created_at", "")
            timestamp = created_at[:16] if created_at else ""
            if timestamp:
                lines.append(f"- **[{timestamp}]** {text}")
            else:
                lines.append(f"- {text}")

        return "\n".join(lines)

    def _build_section_summaries_md(
        self, payload: ContextPayload, config: SupportingContextConfig
    ) -> str:
        """Build summaries section as timestamped markdown bullets."""
        if not payload.summaries:
            return ""

        max_summaries = config.max_items.get("summaries", 10)
        lines = ["\n## Conversation Summaries", ""]

        for summary in payload.summaries[:max_summaries]:
            text = summary.get("text", "")
            created_at = summary.get("metadata", {}).get("created_at", "")
            timestamp = created_at[:16] if created_at else ""
            if timestamp:
                lines.append(f"- **[{timestamp}]** {text}")
            else:
                lines.append(f"- {text}")

        return "\n".join(lines)

    def _build_section_tools_md(
        self, payload: ContextPayload, config: SupportingContextConfig
    ) -> str:
        """Build tools section as markdown table + hints."""
        lines: list[str] = []

        max_tools = config.max_items.get("tools", 5)

        # Tool recommendations table
        if payload.recommended_tools:
            lines.extend([
                "\n## Recommended Tools",
                "",
                "| Tool | Relevance | Reason |",
                "|------|-----------|--------|",
            ])
            for rec in payload.recommended_tools[:max_tools]:
                if hasattr(rec, "tool_name"):
                    tool_name = rec.tool_name
                    relevance = getattr(rec, "relevance_score", 0.0)
                    reason = rec.reason
                else:
                    tool_name = rec.get("tool_name", "unknown")
                    relevance = rec.get("relevance_score", 0.0)
                    reason = rec.get("reason", "")
                lines.append(
                    f"| `{tool_name}` | {relevance:.2f} | {reason} |"
                )

        # Tool usage hints
        if payload.tool_usage_hints:
            lines.extend(["\n## Tool Usage Notes", ""])
            for hint in payload.tool_usage_hints:
                lines.append(f"- {hint}")

        return "\n".join(lines) if lines else ""

    def _format_transparency_block(self, recent_memories: list[str]) -> str:
        """Format the transparency block showing recent auto-archived memories."""
        lines = ["## Recent Memories"]
        lines.append("The system has automatically archived the following observations:")
        for memory in recent_memories[:5]:  # Limit to 5 most recent
            lines.append(f"- {memory}")
        return "\n".join(lines)

    def _format_semantic_block(self, passages: list[dict[str, Any]]) -> str:
        """Format semantic memory passages from vector store."""
        lines = ["## Relevant Documentation"]
        lines.append("The following passages may be relevant to the current context:")
        lines.append("")

        for i, passage in enumerate(passages[:5], 1):  # Limit to 5 passages
            text = passage.get("text", "")
            similarity = passage.get("similarity", 0.0)
            source = passage.get("metadata", {}).get("source_name", "unknown")

            lines.append(f"### Passage {i} (relevance: {similarity:.2f})")
            lines.append(f"Source: {source}")
            lines.append(text)
            lines.append("")

        return "\n".join(lines)

    def _format_state_block(self, state: SessionState) -> str:
        """Format state memory (scoped variables)."""
        lines = ["## Session Context"]

        # Group by scope
        user_vars = {}
        app_vars = {}
        session_vars = {}

        for key, value in state.scoped_vars.items():
            if key.startswith("user:"):
                user_vars[key[5:]] = value
            elif key.startswith("app:"):
                app_vars[key[4:]] = value
            elif key.startswith("session:"):
                session_vars[key[8:]] = value

        if user_vars:
            lines.append("")
            lines.append("### User Preferences")
            for key, value in user_vars.items():
                lines.append(f"- {key}: {value}")

        if session_vars:
            lines.append("")
            lines.append("### Current Session")
            for key, value in session_vars.items():
                lines.append(f"- {key}: {value}")

        if app_vars:
            lines.append("")
            lines.append("### Application State")
            for key, value in app_vars.items():
                lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    def calculate_fixed_costs(
        self,
        system_prompt: str,
        tool_definitions: list[dict[str, Any]] | None = None,
    ) -> int:
        """
        Calculate fixed token costs for budget calculation.

        Fixed_Cost = len(System_Prompt) + len(Tool_Definitions) + Output_Buffer

        Args:
            system_prompt: The base system prompt
            tool_definitions: Optional tool definitions

        Returns:
            Total fixed token cost
        """
        fixed = self.count_tokens(system_prompt)

        if tool_definitions:
            # Estimate tool tokens (JSON serialization)
            import json
            tools_str = json.dumps(tool_definitions)
            fixed += self.count_tokens(tools_str)

        fixed += self.output_buffer
        return fixed

    def calculate_dynamic_limit(
        self,
        system_prompt: str,
        tool_definitions: list[dict[str, Any]] | None = None,
    ) -> int:
        """
        Calculate available token budget for dynamic content.

        Dynamic_Limit = Model_Max_Tokens - Fixed_Cost

        Args:
            system_prompt: The base system prompt
            tool_definitions: Optional tool definitions

        Returns:
            Available tokens for dynamic content
        """
        fixed_cost = self.calculate_fixed_costs(system_prompt, tool_definitions)
        return max(0, self.max_tokens - fixed_cost)
