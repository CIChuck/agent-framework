"""
Copilot Agent Implementation.

Interactive Re-Act agent with tool calling support.
Implements the Think → Tool → Observe loop for human-in-the-loop workflows.

Ref: Batch 3 Specification, Section 4.3
"""

import json
import logging
from typing import Any

from friday_core.interfaces import ChatCompletionResponse

from .base import AgentBase

logger = logging.getLogger(__name__)


class CopilotAgent(AgentBase):
    """
    Interactive agent using the Re-Act pattern.

    Executes a Think → Tool → Observe loop until the LLM
    produces a final response without tool calls. Designed
    for human-in-the-loop workflows where the agent assists
    a user with tasks.

    Re-Act Loop:
    1. Think: LLM reasons about the task and decides next action
    2. Tool: Execute tool calls if any
    3. Observe: Feed tool results back to LLM
    4. Repeat until LLM produces final response

    Example:
        agent = CopilotAgent(
            profile=profile,
            memory=memory_controller,
            context_engine=context_assembler,
            llm=llm_client,
            tool_registry=registry,
        )

        response = await agent.run("What meetings do I have today?")
    """

    # Maximum iterations to prevent infinite loops
    MAX_ITERATIONS: int = 10

    async def run(self, input_signal: str) -> str:
        """
        Execute the Re-Act loop for a user query.

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
            # Ensure session is initialized
            if self.session_state is None:
                await self.initialize_session()

            # 1. Assemble context for this query
            # Calculate dynamic budget based on system prompt and tools
            system_prompt = self.profile.render_system_prompt()
            tool_schemas = self._get_tool_schemas()
            budget_limit = self.context_engine.calculate_budget_limit(
                system_prompt=system_prompt,
                tool_definitions=tool_schemas if tool_schemas else None,
            )

            context_payload = await self.context_engine.assemble_context(
                query=input_signal,
                state=self.session_state,
                budget_limit=budget_limit,
            )

            # 2. Format the prompt (system_prompt already calculated above)
            messages = await self.context_engine.format_prompt(
                system_prompt=system_prompt,
                payload=context_payload,
            )

            # 3. Add the user's message
            messages.append({"role": "user", "content": input_signal})
            self._add_to_history("user", input_signal)

            # 4. Get tool schemas
            tool_schemas = self._get_tool_schemas()

            # 5. Execute Re-Act loop
            iteration = 0
            accumulated_tool_calls: list[dict[str, Any]] = []
            accumulated_tool_results: list[dict[str, Any]] = []

            while iteration < self.MAX_ITERATIONS:
                iteration += 1

                self._emit_event(
                    "react_iteration",
                    {"iteration": iteration, "message_count": len(messages)},
                )

                # Call LLM
                response: ChatCompletionResponse = await self.llm.chat_completion(
                    messages=messages,
                    tools=tool_schemas if tool_schemas else None,
                    temperature=self.profile.temperature,
                )

                # Check if LLM wants to use tools
                if response.has_tool_calls:
                    # Process each tool call
                    tool_results = []
                    tool_call_dicts = []

                    for tool_call in response.tool_calls:
                        tc_dict = {
                            "id": tool_call.id,
                            "name": tool_call.name,
                            "arguments": tool_call.arguments,
                        }
                        tool_call_dicts.append(tc_dict)

                        # Execute the tool
                        result = await self._execute_tool_call(
                            tool_call.name,
                            tool_call.arguments,
                        )
                        tool_results.append(result)

                        # Track for archiving
                        accumulated_tool_calls.append(tc_dict)
                        accumulated_tool_results.append({
                            "tool_call_id": tool_call.id,
                            "output": result,
                            "error": None,
                        })

                    # Add tool interactions to conversation
                    self._add_tool_call_to_history(tool_call_dicts, tool_results)

                    # Update messages for next iteration.
                    # Add assistant message with tool calls.
                    # Preserve reasoning_content for thinking models
                    # (e.g. Moonshot Kimi K2.5) — the provider rejects
                    # the next request if it's missing.
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
                                        if isinstance(
                                            tc["arguments"], dict
                                        )
                                        else tc["arguments"]
                                    ),
                                },
                            }
                            for tc in tool_call_dicts
                        ],
                    }
                    if response.reasoning_content:
                        assistant_msg["reasoning_content"] = (
                            response.reasoning_content
                        )
                    messages.append(assistant_msg)

                    # Add tool results
                    for tc, result in zip(tool_call_dicts, tool_results):
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": result,
                        })

                    # Continue loop to get LLM's response to tool results
                    continue

                else:
                    # No tool calls - this is the final response
                    final_response = response.content or ""

                    # Add to history
                    self._add_to_history("assistant", final_response)

                    # Archive the complete turn
                    await self._archive_turn(
                        user_message=input_signal,
                        assistant_message=final_response,
                        tool_calls=accumulated_tool_calls if accumulated_tool_calls else None,
                        tool_results=accumulated_tool_results if accumulated_tool_results else None,
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

            # Max iterations reached
            error_msg = (
                f"Agent exceeded maximum iterations ({self.MAX_ITERATIONS}). "
                "This may indicate a loop in tool usage."
            )
            logger.error(error_msg)

            # Archive what we have
            await self._archive_turn(
                user_message=input_signal,
                assistant_message=error_msg,
                tool_calls=accumulated_tool_calls if accumulated_tool_calls else None,
                tool_results=accumulated_tool_results if accumulated_tool_results else None,
            )

            raise RuntimeError(error_msg)

        finally:
            if span_id and self.telemetry:
                self.telemetry.end_span(span_id)

    async def run_with_streaming(self, input_signal: str):
        """
        Execute Re-Act loop with streaming response.

        TODO: Implement streaming support for real-time response display.
        This is a placeholder for future enhancement.

        Args:
            input_signal: The user's message/query

        Yields:
            Response chunks as they're generated
        """
        # For now, fall back to non-streaming
        response = await self.run(input_signal)
        yield response
