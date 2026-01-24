"""
Prompt Architect (Layout Engine).
Physically structures the final prompt to optimize model attention.

Ref: Batch 2a Specification, Section 5
Ref: docs/build-plan/tool-calling-build-plan.md, Phase 4

Layout Strategy (Optimized for Attention):
1. System Message: Base prompt (identity & guardrails)
2. Episodic Memory: Conversation history (chronological)
3. Final Message: Supporting context + User query
   - Prior knowledge (relationship summaries)
   - Key facts (most recent first)
   - Recent insights (most recent first)
   - Recent summaries (most recent first)
   - Tool recommendations (NEW - for recency effect)
   - Tool usage hints (NEW)
   - Session state
   - User query

Tool Context Integration (Hybrid Placement):
- Full tool schemas are passed via API `tools` parameter (not in prompt)
- Tool recommendations and hints appear in supporting context
- Placed immediately before query for maximum recency effect
- Recommendations include tool name, reason, and suggested parameters

This layout combats "Lost in the Middle" by placing supporting context
immediately before the query (recency effect) rather than in the system block.
"""

import json
from typing import Any
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

import tiktoken

from friday_memory.models import ContextPayload, SessionState


class PromptArchitect:
    """
    Layout Engine for prompt construction.

    Structures the final prompt to combat "Lost in the Middle" and
    optimize for "System 2" reasoning. Places critical information
    at the start and end of the context for maximum attention.
    """

    def __init__(
        self,
        model_name: str = "gpt-4",
        max_tokens: int = 8192,
        output_buffer: int = 1024,
        user_name: str = "User",
        assistant_name: str = "Assistant",
    ) -> None:
        """
        Initialize the Prompt Architect.

        Args:
            model_name: The model name for token counting
            max_tokens: Maximum context window tokens
            output_buffer: Reserved tokens for model output
            user_name: Display name for the user in conversation
            assistant_name: Display name for the assistant in conversation
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.output_buffer = output_buffer
        self.user_name = user_name
        self.assistant_name = assistant_name

        # Initialize tokenizer
        try:
            self._encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fall back to cl100k_base for unknown models
            self._encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self._encoding.encode(text))

    def format_prompt(
        self,
        system_prompt: str,
        user_query: str,
        payload: ContextPayload,
        state: SessionState | None = None,
        tool_definitions: list[dict[str, Any]] | None = None,
        context_format: str = "plain",
    ) -> list[dict[str, Any]]:
        """
        Arranges messages for optimal model attention.

        Implements the layout strategy defined in Batch 2a Section 5.

        Args:
            system_prompt: The base system prompt (identity & guardrails)
            user_query: The current user message
            payload: The assembled context payload
            state: Optional session state for scoped variables
            tool_definitions: Optional tool definitions for the model
            context_format: Output format for supporting context.
                Options: "plain" (default), "json", "xml", "markdown"

        Returns:
            List of message dicts in OpenAI-compatible format
        """
        messages: list[dict[str, Any]] = []

        # 1. System message (base prompt only)
        system_content = self._build_system_content(system_prompt)
        messages.append({"role": "system", "content": system_content})

        # 2. Episodic memory (conversation history, chronological)
        # Merge prior_history + history (prior sessions first, then current session)
        all_history = list(payload.prior_history) + list(payload.history)
        for turn in all_history:
            # Format timestamp for temporal context: [YYYY-MM-DD HH:MM]
            timestamp_str = ""
            if turn.timestamp:
                timestamp_str = f"[{turn.timestamp.strftime('%Y-%m-%d %H:%M')}] "

            # Append user message
            if turn.user_message:
                messages.append({
                    "role": "user",
                    "content": f"{timestamp_str}[{self.user_name}]: {turn.user_message}",
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
                    tool_summary_parts.append(turn.assistant_message)

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
                messages.append({
                    "role": "assistant",
                    "content": f"{timestamp_str}[{self.assistant_name}]: {turn.assistant_message}",
                })

        # 3. Final message: supporting context + query
        # Supporting context is placed immediately before the query for recency effect
        supporting_context = self._build_supporting_context(payload, state, context_format)
        if supporting_context:
            final_content = f"{supporting_context}\n\n---\n\n[{self.user_name}]: {user_query}"
        else:
            final_content = f"[{self.user_name}]: {user_query}"

        messages.append({"role": "user", "content": final_content})

        return messages

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
    ) -> str:
        """
        Build supporting context block for injection before query.

        Placed at the tail of the context to leverage recency effect.
        Content is ordered: relationships, insights (recent first),
        summaries (recent first), entities, state.

        Args:
            payload: The context payload with insights, summaries, entities
            state: Optional session state for scoped variables
            context_format: Output format ("plain", "json", "xml", "markdown")

        Returns:
            Formatted supporting context string, or empty string if no content
        """
        match context_format:
            case "json":
                return self._format_context_json(payload, state)
            case "xml":
                return self._format_context_xml(payload, state)
            case "markdown":
                return self._format_context_markdown(payload, state)
            case _:  # plain (default)
                return self._format_context_plain(payload, state)

    def _format_context_plain(
        self,
        payload: ContextPayload,
        state: SessionState | None,
    ) -> str:
        """Format supporting context as plain text (default format)."""
        sections: list[str] = []

        # 1. Relationship summaries (prior knowledge about entities)
        if payload.recent_memories:
            sections.append("## Prior Knowledge")
            for memory in payload.recent_memories:
                sections.append(memory)

        # 2. Key facts (most recent first - already sorted by created_at desc)
        if payload.key_facts:
            sections.append("\n## Key Facts")
            for fact in payload.key_facts:
                text = fact.get("text", "")
                created_at = fact.get("metadata", {}).get("created_at", "")
                timestamp = created_at[:16] if created_at else ""
                if timestamp:
                    sections.append(f"- [{timestamp}] {text}")
                else:
                    sections.append(f"- {text}")

        # 3. Recent insights (most recent first - already sorted by created_at desc)
        if payload.insights:
            sections.append("\n## Recent Insights")
            for insight in payload.insights:
                text = insight.get("text", "")
                sections.append(f"- {text}")

        # 4. Recent summaries (most recent first - already sorted by created_at desc)
        if payload.summaries:
            sections.append("\n## Conversation Summaries")
            for summary in payload.summaries:
                text = summary.get("text", "")
                sections.append(f"- {text}")

        # 5. Tool recommendations (for recency effect - close to query)
        if payload.recommended_tools:
            sections.append("\n## Recommended Tools")
            for rec in payload.recommended_tools:
                # Handle both ToolRecommendation objects and dicts
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

        # 6. Tool usage hints
        if payload.tool_usage_hints:
            sections.append("\n## Tool Usage Notes")
            for hint in payload.tool_usage_hints:
                sections.append(f"- {hint}")

        # 7. Scoped state variables
        if state and state.scoped_vars:
            state_block = self._format_state_block(state)
            sections.append(f"\n{state_block}")

        return "\n".join(sections) if sections else ""

    def _format_context_json(
        self,
        payload: ContextPayload,
        state: SessionState | None,
    ) -> str:
        """Format supporting context as JSON."""
        context: dict[str, Any] = {}

        if payload.recent_memories:
            context["prior_knowledge"] = payload.recent_memories

        if payload.key_facts:
            context["key_facts"] = [
                {
                    "text": f.get("text", ""),
                    "created_at": f.get("metadata", {}).get("created_at", ""),
                }
                for f in payload.key_facts
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
    ) -> str:
        """Format supporting context as XML."""
        root = Element("supporting_context")

        if payload.recent_memories:
            prior = SubElement(root, "prior_knowledge")
            for mem in payload.recent_memories:
                rel = SubElement(prior, "relationship")
                rel.text = mem

        if payload.key_facts:
            facts_elem = SubElement(root, "key_facts")
            for f in payload.key_facts:
                fact_elem = SubElement(facts_elem, "fact")
                created_at = f.get("metadata", {}).get("created_at", "")
                if created_at:
                    fact_elem.set("created_at", created_at)
                fact_elem.text = f.get("text", "")

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
    ) -> str:
        """Format supporting context as structured markdown with tables."""
        sections: list[str] = []

        # 1. Prior knowledge as table
        if payload.recent_memories:
            sections.append("## Prior Knowledge")
            sections.append("")
            sections.append("| Relationship |")
            sections.append("|--------------|")
            for mem in payload.recent_memories:
                sections.append(f"| {mem} |")

        # 2. Key facts with timestamps (bullets, most recent first)
        if payload.key_facts:
            sections.append("")
            sections.append("## Key Facts")
            sections.append("")
            for fact in payload.key_facts:
                text = fact.get("text", "")
                created_at = fact.get("metadata", {}).get("created_at", "")
                timestamp = created_at[:16] if created_at else "N/A"
                sections.append(f"- **[{timestamp}]** {text}")

        # 3. Recent insights with timestamps (bullets, not numbered)
        if payload.insights:
            sections.append("")
            sections.append("## Recent Insights")
            sections.append("")
            for insight in payload.insights:
                text = insight.get("text", "")
                created_at = insight.get("metadata", {}).get("created_at", "")
                timestamp = created_at[:16] if created_at else "N/A"
                sections.append(f"- **[{timestamp}]** {text}")

        # 4. Summaries with timestamps (bullets, not numbered)
        if payload.summaries:
            sections.append("")
            sections.append("## Conversation Summaries")
            sections.append("")
            for summary in payload.summaries:
                text = summary.get("text", "")
                created_at = summary.get("metadata", {}).get("created_at", "")
                timestamp = created_at[:16] if created_at else "N/A"
                sections.append(f"- **[{timestamp}]** {text}")

        # 5. Tool recommendations as table
        if payload.recommended_tools:
            sections.append("")
            sections.append("## Recommended Tools")
            sections.append("")
            sections.append("| Tool | Relevance | Reason |")
            sections.append("|------|-----------|--------|")
            for rec in payload.recommended_tools:
                if hasattr(rec, "tool_name"):
                    tool_name = rec.tool_name
                    relevance = getattr(rec, "relevance_score", 0.0)
                    reason = rec.reason
                else:
                    tool_name = rec.get("tool_name", "unknown")
                    relevance = rec.get("relevance_score", 0.0)
                    reason = rec.get("reason", "")
                sections.append(f"| `{tool_name}` | {relevance:.2f} | {reason} |")

        # 6. Tool usage hints
        if payload.tool_usage_hints:
            sections.append("")
            sections.append("## Tool Usage Notes")
            sections.append("")
            for hint in payload.tool_usage_hints:
                sections.append(f"- {hint}")

        # 7. Session state as table
        if state and state.scoped_vars:
            sections.append("")
            sections.append("## Session Context")
            sections.append("")
            sections.append("| Key | Value |")
            sections.append("|-----|-------|")
            for key, value in state.scoped_vars.items():
                sections.append(f"| {key} | {value} |")

        return "\n".join(sections) if sections else ""

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

    def _format_associative_block(
        self,
        entities: list,
        facts: list,
    ) -> str:
        """Format associative memory (entities and facts from graph)."""
        lines = ["## Known Entities and Facts"]

        if entities:
            lines.append("")
            lines.append("### Entities")
            for entity in entities[:10]:  # Limit to 10 entities
                entity_type = getattr(entity, "type", "entity")
                label = getattr(entity, "label", "unknown")
                properties = getattr(entity, "properties", {})
                prop_str = ", ".join(f"{k}={v}" for k, v in list(properties.items())[:3])
                lines.append(f"- {label} ({entity_type}): {prop_str}")

        if facts:
            lines.append("")
            lines.append("### Relationships")
            for fact in facts[:10]:  # Limit to 10 facts
                source = getattr(fact, "source_id", "?")
                target = getattr(fact, "target_id", "?")
                relation = getattr(fact, "relation", "related_to")
                lines.append(f"- {source} --[{relation}]--> {target}")

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
