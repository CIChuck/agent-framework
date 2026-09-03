"""
REPL-style agent base implementation.

Owns the generic LLM/tool-calling loop shared by interactive-style agents.
"""

from __future__ import annotations

import json
import logging
from typing import Any, cast

from friday_memory.context.assembler import ContextAssembler

from friday_agent.base import AgentBase
from friday_agent.llm_completion import AgentCompletion, complete_agent_request
from friday_agent.prompting import compose_system_prompt

logger = logging.getLogger(__name__)


class ReplAgentBase(AgentBase):
    """
    Base class for agents that use an LLM-driven REPL/tool-calling loop.

    Subclasses inherit the generic Think -> Tool -> Observe behavior and may
    customize presentation or compatibility semantics without re-implementing
    the runtime loop.
    """

    MAX_ITERATIONS: int = 10

    async def run(self, input_signal: str) -> str:
        """
        Execute the REPL loop for an interactive query.

        Args:
            input_signal: The user's message/query

        Returns:
            The agent's final response string

        Raises:
            RuntimeError: If max iterations exceeded
        """
        span_id = None
        if self.telemetry:
            span_id = self.telemetry.start_span("copilot_run")

        try:
            if self.session_state is None:
                await self.initialize_session()

            prompt_composition = compose_system_prompt(
                profile=self.profile,
                runtime_base_prompt=self.runtime_base_system_prompt,
            )
            system_prompt = prompt_composition.composed_system_prompt
            tool_schemas = self._get_tool_schemas()
            context_engine = cast(ContextAssembler, self.context_engine)
            budget_limit = context_engine.calculate_budget_limit(
                system_prompt=system_prompt,
                tool_definitions=tool_schemas if tool_schemas else None,
            )

            context_payload = await self.context_engine.assemble_context(
                query=input_signal,
                state=self.session_state,
                budget_limit=budget_limit,
                context_strategy=self.profile.context_strategy,
            )

            messages = await self.context_engine.format_prompt(
                system_prompt=system_prompt,
                payload=context_payload,
            )

            messages.append({"role": "user", "content": input_signal})
            self._add_to_history("user", input_signal)

            iteration = 0
            accumulated_tool_calls: list[dict[str, Any]] = []
            accumulated_tool_results: list[dict[str, Any]] = []
            llm_trace: list[dict[str, Any]] = []

            while iteration < self.MAX_ITERATIONS:
                iteration += 1

                self._emit_event(
                    "react_iteration",
                    {"iteration": iteration, "message_count": len(messages)},
                )

                prompt_snapshot = self._sanitize_prompt_messages(messages)
                response = await complete_agent_request(
                    self.llm,
                    messages=messages,
                    tools=tool_schemas if tool_schemas else None,
                    temperature=self.profile.temperature,
                )
                llm_trace.append(
                    {
                        "iteration": iteration,
                        "messages": prompt_snapshot,
                        "response": self._serialize_chat_response(response),
                    }
                )

                if response.has_tool_calls:
                    tool_results = []
                    tool_call_dicts = []

                    for tool_call in response.tool_calls:
                        tc_dict = {
                            "id": tool_call.id,
                            "name": tool_call.name,
                            "arguments": tool_call.arguments,
                        }
                        tool_call_dicts.append(tc_dict)

                        result = await self._execute_tool_call(
                            tool_call.name,
                            tool_call.arguments,
                        )
                        tool_results.append(result)

                        accumulated_tool_calls.append(tc_dict)
                        accumulated_tool_results.append(
                            {
                                "tool_call_id": tool_call.id,
                                "output": result,
                                "error": None,
                            }
                        )

                    self._add_tool_call_to_history(tool_call_dicts, tool_results)

                    assistant_msg: dict[str, Any] = {
                        "role": "assistant",
                        "content": response.content,
                        "tool_calls": [
                            {
                                "id": tc["id"],
                                "type": "function",
                                "function": {
                                    "name": tc["name"],
                                    "arguments": (
                                        json.dumps(tc["arguments"])
                                        if isinstance(tc["arguments"], dict)
                                        else tc["arguments"]
                                    ),
                                },
                            }
                            for tc in tool_call_dicts
                        ],
                    }
                    if response.reasoning_content:
                        assistant_msg["reasoning_content"] = response.reasoning_content
                    messages.append(assistant_msg)

                    for tc, result in zip(tool_call_dicts, tool_results, strict=False):
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tc["id"],
                                "content": result,
                            }
                        )

                    continue

                final_response = response.content or ""

                self._add_to_history("assistant", final_response)

                await self._archive_turn(
                    user_message=input_signal,
                    assistant_message=final_response,
                    tool_calls=accumulated_tool_calls
                    if accumulated_tool_calls
                    else None,
                    tool_results=accumulated_tool_results
                    if accumulated_tool_results
                    else None,
                    raw_prompt_messages=prompt_snapshot,
                    raw_response_payload={
                        **self._serialize_chat_response(response),
                        "llm_trace": llm_trace,
                    },
                    prompt_composition=prompt_composition,
                )

                self._emit_event(
                    "copilot_completed",
                    {
                        "iterations": iteration,
                        "tool_calls_total": len(accumulated_tool_calls),
                        "response_length": len(final_response),
                    },
                )

                return final_response

            error_msg = (
                f"Agent exceeded maximum iterations ({self.MAX_ITERATIONS}). "
                "This may indicate a loop in tool usage."
            )
            logger.error(error_msg)

            await self._archive_turn(
                user_message=input_signal,
                assistant_message=error_msg,
                tool_calls=accumulated_tool_calls if accumulated_tool_calls else None,
                tool_results=accumulated_tool_results
                if accumulated_tool_results
                else None,
                prompt_composition=prompt_composition,
            )

            raise RuntimeError(error_msg)

        finally:
            if self.telemetry and span_id is not None:
                self.telemetry.end_span(span_id)

    @staticmethod
    def _serialize_chat_response(response: AgentCompletion) -> dict[str, Any]:
        return {
            "content": response.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "name": tool_call.name,
                    "arguments": tool_call.arguments,
                }
                for tool_call in response.tool_calls
            ],
            "model": response.model,
            "usage": dict(response.usage),
        }

    @staticmethod
    def _sanitize_prompt_messages(
        messages: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Copy a provider prompt without persisting private reasoning fields."""
        return [
            {key: value for key, value in message.items() if key != "reasoning_content"}
            for message in messages
        ]
