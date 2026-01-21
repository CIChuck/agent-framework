"""
Tool Context Manager.

Manages tool selection, token budgeting, and context integration for LLM calls.
Supports the hybrid placement strategy where tool schemas are passed to the API
and recommendations appear in supporting context.

Ref: Tool Calling Build Plan - Phase 3
"""

from __future__ import annotations

import logging
from typing import Any

from friday_memory.models.tools import ToolRecommendation, ToolSchema

logger = logging.getLogger(__name__)


class ToolContextManager:
    """
    Manages tool selection and context for LLM calls.

    Responsibilities:
    - Track active tools for the current task
    - Estimate token usage for tool schemas
    - Select tools within token budget
    - Generate tool recommendations with reasons
    - Build tool context for inclusion in payload

    Example:
        ```python
        manager = ToolContextManager(max_tools=20, max_budget_ratio=0.25)

        # Set active tools for a task
        manager.set_active_tools(selected_schemas)

        # Get tools within budget
        schemas, recommendations = manager.build_tool_context(
            query="Read the config file",
            budget=5000,
        )
        ```
    """

    # Rough estimate: ~50 tokens per tool schema on average
    TOKENS_PER_TOOL_ESTIMATE = 50

    def __init__(
        self,
        max_tool_budget_ratio: float = 0.25,
        max_tools: int = 20,
        recommendation_threshold: float = 0.5,
    ):
        """
        Initialize the tool context manager.

        Args:
            max_tool_budget_ratio: Maximum ratio of dynamic budget for tools (0.0-1.0).
            max_tools: Maximum number of tools to include in context.
            recommendation_threshold: Minimum relevance score for recommendations.
        """
        self._max_budget_ratio = max_tool_budget_ratio
        self._max_tools = max_tools
        self._recommendation_threshold = recommendation_threshold

        # Active tools state
        self._active_tools: list[dict[str, Any]] = []
        self._tool_recommendations: list[ToolRecommendation] = []

    @property
    def active_tools(self) -> list[dict[str, Any]]:
        """Get currently active tool schemas."""
        return self._active_tools

    @property
    def recommendations(self) -> list[ToolRecommendation]:
        """Get current tool recommendations."""
        return self._tool_recommendations

    def set_active_tools(self, tools: list[dict[str, Any]]) -> None:
        """
        Set the active tools for the current task.

        Args:
            tools: List of tool schemas to activate.
        """
        self._active_tools = tools[:self._max_tools]  # Enforce max limit
        logger.debug(f"Set {len(self._active_tools)} active tools")

    def expand_tools(self, additional_tools: list[dict[str, Any]]) -> int:
        """
        Expand active tools with additional ones.

        Args:
            additional_tools: Tools to add to the active set.

        Returns:
            Number of tools actually added (respects max_tools limit).
        """
        available_slots = self._max_tools - len(self._active_tools)
        tools_to_add = additional_tools[:available_slots]

        # Avoid duplicates
        existing_names = {t.get("name") for t in self._active_tools}
        new_tools = [t for t in tools_to_add if t.get("name") not in existing_names]

        self._active_tools.extend(new_tools)
        logger.debug(f"Expanded tools by {len(new_tools)}, total: {len(self._active_tools)}")
        return len(new_tools)

    def clear_tools(self) -> None:
        """Clear all active tools and recommendations."""
        self._active_tools = []
        self._tool_recommendations = []
        logger.debug("Cleared all active tools")

    def estimate_schema_tokens(self, tool_schemas: list[dict[str, Any]]) -> int:
        """
        Estimate token count for tool schemas.

        Uses a simple heuristic based on schema size. More sophisticated
        estimation could use actual tokenization.

        Args:
            tool_schemas: List of tool schemas.

        Returns:
            Estimated token count.
        """
        total = 0
        for schema in tool_schemas:
            # Base tokens for structure
            tokens = 20

            # Name and description
            name = schema.get("name", "")
            description = schema.get("description", "")
            tokens += len(name.split()) + len(description.split())

            # Parameters
            params = schema.get("parameters", {})
            if isinstance(params, dict):
                props = params.get("properties", {})
                tokens += len(props) * 15  # ~15 tokens per parameter

            total += tokens

        return total

    def select_tools_within_budget(
        self,
        available_tools: list[dict[str, Any]],
        budget: int,
        prioritize_by: str = "relevance",
    ) -> list[dict[str, Any]]:
        """
        Filter and prioritize tools within token budget.

        Args:
            available_tools: All available tool schemas.
            budget: Maximum tokens for tools.
            prioritize_by: How to prioritize - "relevance", "recency", or "name".

        Returns:
            List of tool schemas that fit within budget.
        """
        if not available_tools:
            return []

        # Sort by priority (for now, just use order as-is or by name)
        if prioritize_by == "name":
            sorted_tools = sorted(available_tools, key=lambda t: t.get("name", ""))
        else:
            sorted_tools = list(available_tools)

        # Add tools until budget exhausted
        selected = []
        current_tokens = 0

        for tool in sorted_tools:
            tool_tokens = self._estimate_single_tool_tokens(tool)
            if current_tokens + tool_tokens <= budget:
                selected.append(tool)
                current_tokens += tool_tokens

            if len(selected) >= self._max_tools:
                break

        logger.debug(
            f"Selected {len(selected)} tools within budget "
            f"({current_tokens}/{budget} tokens)"
        )
        return selected

    def _estimate_single_tool_tokens(self, schema: dict[str, Any]) -> int:
        """Estimate tokens for a single tool schema."""
        return self.estimate_schema_tokens([schema])

    def generate_recommendations(
        self,
        query: str,
        available_tools: list[dict[str, Any]],
        top_k: int = 5,
    ) -> list[ToolRecommendation]:
        """
        Generate tool recommendations based on query.

        Uses simple keyword matching for now. Could be enhanced with
        embeddings or LLM-based selection.

        Args:
            query: User query or task description.
            available_tools: Tools to consider.
            top_k: Maximum recommendations to return.

        Returns:
            List of ToolRecommendation objects.
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored_tools = []

        for tool in available_tools:
            name = tool.get("name", "").lower()
            description = tool.get("description", "").lower()
            category = tool.get("category", "uncategorized").lower()
            tags = [t.lower() for t in tool.get("tags", [])]

            # Simple keyword matching score
            score = 0.0

            # Name match
            if any(word in name for word in query_words):
                score += 0.4

            # Description match
            desc_words = set(description.split())
            overlap = len(query_words & desc_words)
            score += min(overlap * 0.1, 0.3)

            # Category relevance heuristics
            category_keywords = {
                "filesystem": ["file", "read", "write", "directory", "path", "folder"],
                "shell": ["command", "run", "execute", "terminal", "bash"],
                "web": ["http", "url", "fetch", "request", "api", "web"],
                "git": ["git", "commit", "branch", "repository", "repo", "version"],
                "code": ["code", "function", "class", "analyze", "parse"],
                "data": ["data", "json", "csv", "parse", "transform"],
                "text": ["text", "string", "search", "replace", "regex"],
            }

            if category in category_keywords:
                if any(kw in query_lower for kw in category_keywords[category]):
                    score += 0.2

            # Tag match
            for tag in tags:
                if tag in query_lower:
                    score += 0.1

            if score >= self._recommendation_threshold:
                reason = self._generate_reason(tool, query)
                scored_tools.append((score, tool, reason))

        # Sort by score descending
        scored_tools.sort(key=lambda x: x[0], reverse=True)

        # Build recommendations
        recommendations = []
        for score, tool, reason in scored_tools[:top_k]:
            rec = ToolRecommendation(
                tool_name=tool.get("name", "unknown"),
                category=tool.get("category", "uncategorized"),
                relevance_score=min(score, 1.0),
                reason=reason,
                confidence=min(score * 0.8, 1.0),
            )
            recommendations.append(rec)

        self._tool_recommendations = recommendations
        return recommendations

    def _generate_reason(self, tool: dict[str, Any], query: str) -> str:
        """Generate a reason for recommending a tool."""
        name = tool.get("name", "unknown")
        category = tool.get("category", "uncategorized")
        description = tool.get("description", "")

        # Simple template-based reasons
        if category == "filesystem":
            return f"Use {name} for file operations"
        elif category == "shell":
            return f"Use {name} to execute commands"
        elif category == "web":
            return f"Use {name} for web requests"
        elif category == "git":
            return f"Use {name} for version control"
        elif category == "code":
            return f"Use {name} for code analysis"
        else:
            # Use first sentence of description
            first_sentence = description.split(".")[0] if description else ""
            return first_sentence or f"Consider {name} for this task"

    def build_tool_context(
        self,
        query: str,
        budget: int,
        available_tools: list[dict[str, Any]] | None = None,
    ) -> tuple[list[dict[str, Any]], list[ToolRecommendation]]:
        """
        Build complete tool context for inclusion in payload.

        Args:
            query: User query for generating recommendations.
            budget: Token budget for tools.
            available_tools: Tools to consider (uses active_tools if None).

        Returns:
            Tuple of (tool_schemas, recommendations).
        """
        tools = available_tools if available_tools is not None else self._active_tools

        if not tools:
            return [], []

        # Calculate tool budget
        tool_budget = int(budget * self._max_budget_ratio)

        # Select tools within budget
        selected_schemas = self.select_tools_within_budget(tools, tool_budget)

        # Generate recommendations
        recommendations = self.generate_recommendations(query, selected_schemas)

        return selected_schemas, recommendations

    def get_budget_info(self, tools: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """
        Get information about tool token budget usage.

        Args:
            tools: Tools to analyze (uses active_tools if None).

        Returns:
            Dictionary with budget information.
        """
        tool_list = tools if tools is not None else self._active_tools

        estimated_tokens = self.estimate_schema_tokens(tool_list)
        max_tokens = self._max_tools * self.TOKENS_PER_TOOL_ESTIMATE

        return {
            "tool_count": len(tool_list),
            "estimated_tokens": estimated_tokens,
            "max_tools": self._max_tools,
            "budget_limit": max_tokens,
            "usage_percent": (estimated_tokens / max_tokens * 100) if max_tokens > 0 else 0,
        }
