"""
Prompt Architect (Layout Engine).
Physically structures the final prompt to optimize model attention.

Ref: Batch 2a Specification, Section 5

Layout Strategy (Default):
1. System Block: Identity & Guardrails
2. Transparency Block: Recent auto-archived memories
3. Procedural Memory: Few-shot examples
4. Semantic Memory: Relevant documentation passages (Vector)
5. Episodic Memory: Conversation history (Last N turns)
6. State Memory: Scoped variables (User prefs, Env state)
7. User Trigger: The Query
"""

from typing import Any

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
    ) -> None:
        """
        Initialize the Prompt Architect.

        Args:
            model_name: The model name for token counting
            max_tokens: Maximum context window tokens
            output_buffer: Reserved tokens for model output
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.output_buffer = output_buffer

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

        Returns:
            List of message dicts in OpenAI-compatible format
        """
        messages: list[dict[str, Any]] = []

        # Build the enhanced system prompt with all context blocks
        system_content = self._build_system_content(
            system_prompt, payload, state
        )
        messages.append({"role": "system", "content": system_content})

        # Add episodic memory (conversation history)
        for turn in payload.history:
            # Add user message
            messages.append({
                "role": "user",
                "content": turn.user_message,
            })
            # Add assistant response
            if turn.assistant_message:
                messages.append({
                    "role": "assistant",
                    "content": turn.assistant_message,
                })

        # Add the current user query
        messages.append({"role": "user", "content": user_query})

        return messages

    def _build_system_content(
        self,
        base_prompt: str,
        payload: ContextPayload,
        state: SessionState | None,
    ) -> str:
        """
        Build the enhanced system prompt with context blocks.

        Order follows the layout strategy for optimal attention:
        1. Base System (Identity & Guardrails)
        2. Transparency Block (Recent Memories)
        3. Semantic Memory (Vector passages)
        4. State Memory (Scoped variables)
        """
        sections: list[str] = []

        # 1. Base System Prompt (Identity & Guardrails)
        sections.append(base_prompt)

        # 2. Transparency Block (Recent auto-archived memories)
        if payload.recent_memories:
            transparency = self._format_transparency_block(payload.recent_memories)
            sections.append(transparency)

        # 3. Semantic Memory (Relevant passages from Vector store)
        if payload.passages:
            semantic = self._format_semantic_block(payload.passages)
            sections.append(semantic)

        # 4. Associative Memory (Entities and Facts from Graph)
        if payload.entities or payload.facts:
            associative = self._format_associative_block(
                payload.entities, payload.facts
            )
            sections.append(associative)

        # 5. State Memory (Scoped variables)
        if state and state.scoped_vars:
            state_block = self._format_state_block(state)
            sections.append(state_block)

        return "\n\n".join(sections)

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
