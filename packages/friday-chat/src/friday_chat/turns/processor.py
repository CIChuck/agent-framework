"""Turn processing for FridayV2."""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from friday_memory.models.budget import BudgetSeverity, BudgetStatus

from friday_chat.config import FridayChatConfig
from friday_chat.display import HeartbeatFactory, HeartbeatKind, NoopHeartbeatFactory
from friday_chat.runtime import FridayRuntime, build_runtime
from friday_chat.tools.loop import ToolLoop
from friday_chat.tools.schemas import ToolCallRecord, ToolDefinition
from friday_chat.turns.metrics import elapsed_seconds, now_seconds
from friday_chat.turns.models import (
    ChatModelResponse,
    InteractionTurn,
    ToolCallRequest,
    TurnMetrics,
)


@dataclass(frozen=True)
class TurnResult:
    """Result of a FridayV2 chat turn."""

    user_message: str
    assistant_message: str
    retrieved_memory_count: int
    tool_context_injected: bool
    prompt: str = ""
    context: str = ""
    metrics: TurnMetrics | None = None
    context_budget_tokens: int = 0
    tool_schema_tokens: int = 0
    budget_status: BudgetStatus | None = None
    tool_calls: tuple[ToolCallRecord, ...] = ()
    raw_response: str = ""


@dataclass(frozen=True)
class PreparedTurn:
    """Prepared prompt, context, and budget data for one turn."""

    user_message: str
    total_start: float
    tool_definitions: tuple[ToolDefinition, ...]
    tool_schema_tokens: int
    context_budget_tokens: int
    retrieval_seconds: float
    memories: list[str]
    context_text: str
    prompt_text: str
    messages: list[dict[str, Any]]
    budget_status: BudgetStatus


class TurnProcessingError(RuntimeError):
    """Base class for FridayV2 turn-processing failures."""


class TurnTimeoutError(TurnProcessingError):
    """Raised when the LLM turn exceeds its configured timeout."""

    def __init__(
        self,
        message: str = "LLM turn timed out.",
        *,
        timeout_seconds: float | None = None,
    ) -> None:
        super().__init__(message)
        self.timeout_seconds = timeout_seconds


class TurnRetryExhaustedError(TurnProcessingError):
    """Raised when all LLM retry attempts fail."""


class TurnPersistenceError(TurnProcessingError):
    """Raised when turn persistence fails."""


class TurnCircuitBreakerOpenError(TurnProcessingError):
    """Raised when turn processing is blocked by an open circuit breaker."""


class TurnProcessor:
    """Process one user turn through the configured FridayV2 runtime."""

    def __init__(
        self,
        runtime: FridayRuntime | None = None,
        *,
        config: FridayChatConfig | None = None,
        circuit_breaker_open: bool = False,
        heartbeat_factory: HeartbeatFactory | None = None,
    ) -> None:
        if runtime is None:
            if config is None:
                config = FridayChatConfig.model_validate(
                    {"llm": {"model": "fake/test-chat-model"}}
                )
            runtime = build_runtime(config)
        self._runtime = runtime
        self._circuit_breaker_open = circuit_breaker_open
        self._heartbeat_factory = heartbeat_factory or NoopHeartbeatFactory()
        self._turn_count = 0

    async def process(self, user_message: str) -> TurnResult:
        """Process a deterministic fake turn."""
        if self._circuit_breaker_open:
            raise TurnCircuitBreakerOpenError("Turn processing circuit breaker is open.")

        prepared = await self._prepare_turn(user_message)
        assistant_message, model_response, tool_calls, llm_seconds = (
            await self._complete_model_turn(
                prepared.user_message,
                prepared.messages,
                prepared.tool_definitions,
            )
        )
        raw_response = _serialize_response(model_response)

        metrics = await self._persist_turn(
            user_message=prepared.user_message,
            assistant_message=assistant_message,
            prompt_text=prepared.prompt_text,
            context_text=prepared.context_text,
            memories=prepared.memories,
            tool_calls=tool_calls,
            retrieval_seconds=prepared.retrieval_seconds,
            llm_seconds=llm_seconds,
            total_start=prepared.total_start,
            raw_response=raw_response,
        )
        await self._runtime.speech.speak(assistant_message)
        self._turn_count += 1

        return TurnResult(
            user_message=prepared.user_message,
            assistant_message=assistant_message,
            retrieved_memory_count=len(prepared.memories),
            tool_context_injected=self._runtime.tool_context is not None,
            prompt=prepared.prompt_text,
            context=prepared.context_text,
            metrics=metrics,
            context_budget_tokens=prepared.context_budget_tokens,
            tool_schema_tokens=prepared.tool_schema_tokens,
            budget_status=prepared.budget_status,
            tool_calls=tool_calls,
            raw_response=raw_response,
        )

    async def stream_process(self, user_message: str) -> AsyncIterator[str]:
        """Process a turn and stream the fake assistant response in chunks."""
        chunks: list[str] = []

        async def capture_chunk(chunk: str) -> None:
            chunks.append(chunk)

        await self.process_streaming(user_message, on_chunk=capture_chunk)
        for chunk in chunks:
            yield chunk

    async def process_streaming(
        self,
        user_message: str,
        *,
        on_chunk: Callable[[str], Awaitable[None]],
    ) -> TurnResult:
        """Process a no-tool turn using streaming output."""
        if self._circuit_breaker_open:
            raise TurnCircuitBreakerOpenError("Turn processing circuit breaker is open.")

        prepared = await self._prepare_turn(user_message)
        if prepared.tool_definitions:
            assistant_message, model_response, tool_calls, llm_seconds = (
                await self._complete_model_turn(
                    prepared.user_message,
                    prepared.messages,
                    prepared.tool_definitions,
                )
            )
            await on_chunk(assistant_message)
        else:
            llm_start = now_seconds()
            assistant_chunks: list[str] = []
            heartbeat = self._heartbeat_factory.create_heartbeat("thinking")
            heartbeat_stopped = False

            def stop_heartbeat_once() -> None:
                nonlocal heartbeat_stopped
                if not heartbeat_stopped:
                    heartbeat.stop()
                    heartbeat_stopped = True

            try:
                heartbeat.start()
                async for chunk in self._runtime.chat_llm.stream_complete(
                    prepared.messages,
                    tools=(),
                ):
                    if not assistant_chunks:
                        stop_heartbeat_once()
                    assistant_chunks.append(chunk)
                    await on_chunk(chunk)
            finally:
                stop_heartbeat_once()
            assistant_message = "".join(assistant_chunks)
            model_response = ChatModelResponse.from_text(assistant_message)
            tool_calls = ()
            llm_seconds = elapsed_seconds(llm_start)

        raw_response = _serialize_response(model_response)
        metrics = await self._persist_turn(
            user_message=prepared.user_message,
            assistant_message=assistant_message,
            prompt_text=prepared.prompt_text,
            context_text=prepared.context_text,
            memories=prepared.memories,
            tool_calls=tool_calls,
            retrieval_seconds=prepared.retrieval_seconds,
            llm_seconds=llm_seconds,
            total_start=prepared.total_start,
            raw_response=raw_response,
        )
        await self._runtime.speech.speak(assistant_message)
        self._turn_count += 1

        return TurnResult(
            user_message=prepared.user_message,
            assistant_message=assistant_message,
            retrieved_memory_count=len(prepared.memories),
            tool_context_injected=self._runtime.tool_context is not None,
            prompt=prepared.prompt_text,
            context=prepared.context_text,
            metrics=metrics,
            context_budget_tokens=prepared.context_budget_tokens,
            tool_schema_tokens=prepared.tool_schema_tokens,
            budget_status=prepared.budget_status,
            tool_calls=tool_calls,
            raw_response=raw_response,
        )

    async def _prepare_turn(self, user_message: str) -> PreparedTurn:
        total_start = now_seconds()
        tool_definitions: tuple[ToolDefinition, ...] = ()
        if self._runtime.config.tools.enabled:
            tool_definitions = _select_turn_tools(
                user_message,
                tuple(self._runtime.tools.list_tools()),
                self._runtime.config,
            )
        tool_schema_tokens = _estimate_tool_schema_tokens(tool_definitions)
        context_budget_tokens = _calculate_dynamic_context_budget(
            self._runtime.config,
            tool_schema_tokens=tool_schema_tokens,
        )

        retrieval_start = now_seconds()
        memories = await self._runtime.memory.retrieve(
            user_message,
            token_limit=context_budget_tokens,
        )
        retrieval_seconds = elapsed_seconds(retrieval_start)

        tool_context = self._runtime.tool_context
        if tool_context is not None:
            tool_context = _build_tool_context_block(tool_definitions)
        context_text = _build_context_text(memories, tool_context)
        current_turn = self._turn_count + 1
        prompt_text = _build_prompt_text(
            self._runtime.config.chat.system_prompt,
            context_text,
            user_message,
            turn_count=current_turn,
        )
        messages = _build_model_messages(
            system_prompt=self._runtime.config.chat.system_prompt,
            context_text=context_text,
            user_message=user_message,
            turn_count=current_turn,
        )
        budget_status = _build_budget_status(
            prompt_text,
            self._runtime.config,
            tool_schema_tokens=tool_schema_tokens,
        )
        return PreparedTurn(
            user_message=user_message,
            total_start=total_start,
            tool_definitions=tool_definitions,
            tool_schema_tokens=tool_schema_tokens,
            context_budget_tokens=context_budget_tokens,
            retrieval_seconds=retrieval_seconds,
            memories=memories,
            context_text=context_text,
            prompt_text=prompt_text,
            messages=messages,
            budget_status=budget_status,
        )

    async def _complete_model_turn(
        self,
        user_message: str,
        messages: list[dict[str, Any]],
        tool_definitions: tuple[ToolDefinition, ...],
    ) -> tuple[
        str,
        ChatModelResponse,
        tuple[ToolCallRecord, ...],
        float,
    ]:
        llm_start = now_seconds()
        model_response = await self._complete_with_retries(
            messages,
            tools=tool_definitions,
        )
        model_response = _with_text_tool_calls(model_response, tool_definitions)
        tool_calls: tuple[ToolCallRecord, ...] = ()
        if model_response.has_tool_calls and tool_definitions:
            model_response, tool_calls = await self._complete_tool_turn(
                messages,
                model_response,
                tool_definitions,
            )
        assistant_message = model_response.content
        if not assistant_message and tool_calls:
            assistant_message = _tool_fallback_message(tool_calls)
        return (
            assistant_message,
            model_response,
            tool_calls,
            elapsed_seconds(llm_start),
        )

    async def _complete_with_retries(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: tuple[ToolDefinition, ...] = (),
        heartbeat_kind: HeartbeatKind = "thinking",
    ) -> ChatModelResponse:
        attempts = max(1, self._runtime.config.llm.max_retries + 1)
        last_error: BaseException | None = None
        for _attempt in range(attempts):
            heartbeat = self._heartbeat_factory.create_heartbeat(heartbeat_kind)
            try:
                heartbeat.start()
                timeout = self._runtime.config.llm.timeout_seconds
                if timeout is not None:
                    response = await asyncio.wait_for(
                        self._runtime.chat_llm.complete(messages, tools=tools),
                        timeout=timeout,
                    )
                    return _ensure_chat_response(response)
                return _ensure_chat_response(
                    await self._runtime.chat_llm.complete(messages, tools=tools)
                )
            except TimeoutError as exc:
                raise TurnTimeoutError(
                    "LLM turn timed out.",
                    timeout_seconds=timeout,
                ) from exc
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                last_error = exc
            finally:
                heartbeat.stop()

        raise TurnRetryExhaustedError("LLM retry attempts exhausted.") from last_error

    async def _complete_tool_turn(
        self,
        messages: list[dict[str, Any]],
        initial_response: ChatModelResponse,
        tool_definitions: tuple[ToolDefinition, ...],
    ) -> tuple[ChatModelResponse, tuple[ToolCallRecord, ...]]:
        loop_config = self._runtime.config.tools.loop
        max_iterations = _int_from_mapping(loop_config, "max_iterations", 3)
        all_tool_calls: list[ToolCallRecord] = []
        response = initial_response
        for _iteration in range(max_iterations):
            if not response.has_tool_calls:
                return response, tuple(all_tool_calls)
            assistant_message = _assistant_message_from_response(response)
            tool_calls = await self._execute_tool_calls(response, tool_definitions)
            all_tool_calls.extend(tool_calls)
            messages.append(assistant_message)
            messages.extend(_tool_result_messages(tool_calls))
            if not tool_calls:
                break
            response = await self._complete_with_retries(
                messages,
                tools=tool_definitions,
                heartbeat_kind="tool",
            )
            response = _with_text_tool_calls(response, tool_definitions)
        return response, tuple(all_tool_calls)

    async def _execute_tool_calls(
        self,
        response: ChatModelResponse,
        tool_definitions: tuple[ToolDefinition, ...],
    ) -> tuple[ToolCallRecord, ...]:
        loop_config = self._runtime.config.tools.loop
        max_iterations = _int_from_mapping(loop_config, "max_iterations", 3)
        tool_loop = ToolLoop(
            self._runtime.tools,
            max_iterations=max_iterations,
            heartbeat_factory=self._heartbeat_factory,
        )
        tool_result = await tool_loop.run(
            [_assistant_message_from_response(response)],
            tool_definitions,
        )
        return tuple(tool_result.tool_calls)

    async def _persist_turn(
        self,
        *,
        user_message: str,
        assistant_message: str,
        prompt_text: str,
        context_text: str,
        memories: list[str],
        tool_calls: tuple[ToolCallRecord, ...],
        retrieval_seconds: float,
        llm_seconds: float,
        total_start: float,
        raw_response: str,
    ) -> TurnMetrics:
        persistence_start = now_seconds()
        try:
            await self._runtime.memory.store_turn(user_message, assistant_message)
            await self._runtime.transcript.record_turn(user_message, assistant_message)
            if self._runtime.config.transcript.capture_raw_prompts:
                await self._runtime.transcript.record_context_log(
                    prompt_text,
                    raw_response,
                )
            metrics = TurnMetrics(
                retrieval_seconds=retrieval_seconds,
                llm_seconds=llm_seconds,
                persistence_seconds=elapsed_seconds(persistence_start),
                total_seconds=elapsed_seconds(total_start),
            )
            await self._runtime.transcript.record_interaction(
                InteractionTurn(
                    turn_id=str(uuid4()),
                    user_message=user_message,
                    assistant_message=assistant_message,
                    prompt=prompt_text,
                    context=context_text,
                    memory_snippets=tuple(memories),
                    metrics=metrics,
                    raw_prompt_captured=(
                        self._runtime.config.transcript.capture_raw_prompts
                    ),
                    tool_calls=tool_calls,
                )
            )
        except Exception as exc:
            _rollback_fake_memory_turn(
                self._runtime.memory,
                user_message,
                assistant_message,
            )
            raise TurnPersistenceError("Failed to persist turn.") from exc
        return metrics


def _rollback_fake_memory_turn(
    memory: object,
    user_message: str,
    assistant_message: str,
) -> None:
    stored_turns = getattr(memory, "stored_turns", None)
    if not isinstance(stored_turns, list) or not stored_turns:
        return
    if stored_turns[-1] == (user_message, assistant_message):
        stored_turns.pop()


def _build_context_text(memories: list[str], tool_context: str | None) -> str:
    sections = ["Context payload:"]
    if memories:
        sections.append("Memory:")
        sections.extend(f"- {memory}" for memory in memories)
    else:
        sections.append("Memory: none")
    if tool_context:
        sections.append("Tools:")
        sections.append(tool_context)
    return "\n".join(sections)


def _build_tool_context_block(tools: tuple[ToolDefinition, ...]) -> str:
    lines = ["Available tools:"]
    for tool in tools:
        lines.append(f"- {tool.name}: {tool.description}")
    return "\n".join(lines)


def _build_prompt_text(
    system_prompt: str,
    context: str,
    user_message: str,
    *,
    turn_count: int,
) -> str:
    return "\n".join(
        [
            f"System: {system_prompt}",
            f"Turn: {turn_count}",
            context,
            f"User: {user_message}",
        ]
    )


def _build_model_messages(
    *,
    system_prompt: str,
    context_text: str,
    user_message: str,
    turn_count: int,
) -> list[dict[str, Any]]:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"Turn: {turn_count}\n{context_text}"},
        {"role": "user", "content": user_message},
    ]


def _calculate_dynamic_context_budget(
    config: FridayChatConfig,
    *,
    tool_schema_tokens: int,
) -> int:
    context_window = config.memory.context_window or 8192
    output_buffer = config.memory.output_buffer or 1024
    system_prompt_tokens = max(1, len(config.chat.system_prompt) // 4)
    return max(512, context_window - output_buffer - system_prompt_tokens - tool_schema_tokens)


def _estimate_tool_schema_tokens(tools: tuple[ToolDefinition, ...]) -> int:
    return sum(
        max(1, (len(tool.name) + len(tool.description) + len(str(tool.input_schema))) // 4)
        for tool in tools
    )


def _select_turn_tools(
    user_message: str,
    tools: tuple[ToolDefinition, ...],
    config: FridayChatConfig,
) -> tuple[ToolDefinition, ...]:
    if not tools:
        return ()

    context_config = config.tools.context
    max_tools = _int_from_mapping(context_config, "max_tools", len(tools))
    max_tools = max(1, max_tools)
    threshold = _float_from_mapping(context_config, "recommendation_threshold", 0.5)
    scored = [
        (score, index, tool)
        for index, tool in enumerate(tools)
        if (score := _tool_relevance_score(user_message, tool)) >= threshold
    ]
    if not scored:
        return tools[:max_tools]

    scored.sort(key=lambda item: (-item[0], item[1]))
    return tuple(tool for _score, _index, tool in scored[:max_tools])


def _tool_relevance_score(user_message: str, tool: ToolDefinition) -> float:
    query_tokens = _scoring_tokens(user_message)
    if not query_tokens:
        return 0.0

    name_tokens = _scoring_tokens(tool.name)
    description_tokens = _scoring_tokens(tool.description)
    schema_tokens = _scoring_tokens(json.dumps(tool.input_schema, sort_keys=True))
    category_tokens = _scoring_tokens(tool.category)

    score = 0.0
    if query_tokens & name_tokens:
        score += 0.4
    description_overlap = len(query_tokens & description_tokens)
    score += min(description_overlap * 0.15, 0.3)
    schema_overlap = len(query_tokens & schema_tokens)
    score += min(schema_overlap * 0.05, 0.15)
    if query_tokens & category_tokens:
        score += 0.1
    if _matches_temporal_tool(user_message, tool):
        score += 0.6
    if _matches_file_read_tool(user_message, tool):
        score += 0.6
    if _matches_file_write_tool(user_message, tool):
        score += 0.6
    if _is_file_read_query(user_message) and _is_file_write_tool(tool):
        score -= 0.5
    if _is_file_write_query(user_message) and _is_file_read_tool(tool):
        score -= 0.5
    return min(score, 1.0)


def _matches_temporal_tool(user_message: str, tool: ToolDefinition) -> bool:
    tool_tokens = _normalized_tokens(
        f"{tool.name} {tool.description} {json.dumps(tool.input_schema, sort_keys=True)}"
    )
    if not ({"date", "time", "datetime", "current"} & tool_tokens):
        return False
    query_tokens = _normalized_tokens(user_message)
    return bool(
        {
            "date",
            "time",
            "day",
            "today",
            "now",
            "timezone",
        }
        & query_tokens
    )


def _matches_file_read_tool(user_message: str, tool: ToolDefinition) -> bool:
    if not _is_file_read_query(user_message):
        return False
    return _is_file_read_tool(tool)


def _matches_file_write_tool(user_message: str, tool: ToolDefinition) -> bool:
    if not _is_file_write_query(user_message):
        return False
    return _is_file_write_tool(tool)


def _is_file_read_query(user_message: str) -> bool:
    query_tokens = _normalized_tokens(user_message)
    read_intents = {
        "read",
        "review",
        "evaluate",
        "inspect",
        "analyze",
        "analyse",
        "summarize",
        "summarise",
        "show",
        "open",
        "load",
    }
    file_markers = {
        "file",
        "path",
        "config",
        "yaml",
        "yml",
        "json",
        "toml",
        "md",
        "py",
        "txt",
    }
    return bool(query_tokens & read_intents) and (
        bool(query_tokens & file_markers) or "/" in user_message or "\\" in user_message
    )


def _is_file_write_query(user_message: str) -> bool:
    query_tokens = _normalized_tokens(user_message)
    write_intents = {
        "write",
        "create",
        "save",
        "edit",
        "modify",
        "update",
        "append",
        "overwrite",
        "delete",
        "remove",
    }
    file_markers = {"file", "path", "config", "yaml", "yml", "json", "toml", "md", "py", "txt"}
    return bool(query_tokens & write_intents) and (
        bool(query_tokens & file_markers) or "/" in user_message or "\\" in user_message
    )


def _is_file_read_tool(tool: ToolDefinition) -> bool:
    tool_tokens = _normalized_tokens(
        f"{tool.name} {tool.description} {json.dumps(tool.input_schema, sort_keys=True)}"
    )
    return "path" in tool_tokens and (
        "read" in tool_tokens or "summarize" in tool_tokens or "process" in tool_tokens
    )


def _is_file_write_tool(tool: ToolDefinition) -> bool:
    tool_tokens = _normalized_tokens(
        f"{tool.name} {tool.description} {json.dumps(tool.input_schema, sort_keys=True)}"
    )
    return "path" in tool_tokens and (
        "write" in tool_tokens
        or "append" in tool_tokens
        or "overwrite" in tool_tokens
    )


def _normalized_tokens(value: str) -> set[str]:
    return {_normalize_token(token) for token in re.findall(r"[a-z0-9]+", value.lower())}


def _scoring_tokens(value: str) -> set[str]:
    ignored = {
        "a",
        "an",
        "and",
        "api",
        "current",
        "dev",
        "for",
        "get",
        "the",
        "to",
        "using",
        "with",
    }
    return {token for token in _normalized_tokens(value) if token not in ignored}


def _normalize_token(token: str) -> str:
    if len(token) > 3 and token.endswith("ies"):
        return f"{token[:-3]}y"
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def _build_budget_status(
    prompt_text: str,
    config: FridayChatConfig,
    *,
    tool_schema_tokens: int,
) -> BudgetStatus:
    available_budget = max(
        1,
        (config.memory.context_window or 8192) - (config.memory.output_buffer or 1024),
    )
    message_tokens = max(1, len(prompt_text) // 4)
    total_tokens = message_tokens + tool_schema_tokens
    utilization_pct = (total_tokens / available_budget) * 100
    return BudgetStatus(
        total_tokens=total_tokens,
        available_budget=available_budget,
        utilization_pct=utilization_pct,
        overage_tokens=max(0, total_tokens - available_budget),
        severity=BudgetSeverity.from_utilization(utilization_pct),
        message_tokens=message_tokens,
        tool_tokens=tool_schema_tokens,
    )


def _with_text_tool_calls(
    response: ChatModelResponse,
    tool_definitions: tuple[ToolDefinition, ...],
) -> ChatModelResponse:
    if response.has_tool_calls or not response.content or not tool_definitions:
        return response

    parsed = _parse_text_tool_calls(response.content, tool_definitions)
    if not parsed:
        return response
    return ChatModelResponse(
        content=response.content,
        tool_calls=tuple(parsed),
        model=response.model,
        usage=response.usage,
        reasoning_content=response.reasoning_content,
        raw_response=response.raw_response,
    )


def _parse_text_tool_calls(
    content: str,
    tool_definitions: tuple[ToolDefinition, ...],
) -> list[ToolCallRequest]:
    tool_names = {tool.name for tool in tool_definitions}
    parsed: list[ToolCallRequest] = []
    for match in re.finditer(r"->?\s*(\w+)\(([^)]*)\)|\b(\w+)\(([^)]*)\)", content):
        name = match.group(1) or match.group(3)
        args_text = match.group(2) if match.group(1) else match.group(4)
        if name not in tool_names:
            continue
        parsed.append(
            ToolCallRequest(
                name=name,
                arguments=_parse_text_tool_arguments(args_text or ""),
                call_id=f"text-parsed-{name}-{len(parsed)}",
            )
        )
    return parsed


def _parse_text_tool_arguments(arguments: str) -> dict[str, Any]:
    if not arguments.strip():
        return {}
    try:
        parsed = json.loads(arguments)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        return parsed

    values: dict[str, Any] = {}
    pattern = r"(\w+)\s*=\s*(?:'([^']*)'|\"([^\"]*)\"|([^,\\s]+))"
    for match in re.finditer(pattern, arguments):
        key = match.group(1)
        value = match.group(2) or match.group(3) or match.group(4) or ""
        values[key] = value
    return values


def _ensure_chat_response(response: object) -> ChatModelResponse:
    if isinstance(response, ChatModelResponse):
        return response
    if isinstance(response, str):
        return ChatModelResponse.from_text(response)
    raise TypeError(f"Chat model returned unsupported response type: {type(response)!r}")


def _assistant_message_from_response(
    response: ChatModelResponse,
) -> dict[str, Any]:
    message: dict[str, Any] = {
        "role": "assistant",
        "content": response.content,
        "tool_calls": [
            {
                "id": call.call_id,
                "type": "function",
                "function": {
                    "name": call.name,
                    "arguments": json.dumps(call.arguments, sort_keys=True),
                },
            }
            for call in response.tool_calls
        ],
    }
    if response.reasoning_content:
        message["reasoning_content"] = response.reasoning_content
    return message


def _tool_result_messages(calls: tuple[ToolCallRecord, ...] | list[ToolCallRecord]) -> list[dict[str, Any]]:
    return [
        {
            "role": "tool",
            "tool_call_id": call.call_id or call.name,
            "name": call.name,
            "content": call.result,
        }
        for call in calls
    ]


def _tool_fallback_message(calls: tuple[ToolCallRecord, ...]) -> str:
    results = "\n".join(f"{call.name}: {call.result}" for call in calls)
    return f"Tool results:\n{results}"


def _serialize_response(response: ChatModelResponse) -> str:
    return json.dumps(
        {
            "content": response.content,
            "tool_calls": [
                {
                    "id": call.call_id,
                    "name": call.name,
                    "arguments": call.arguments,
                }
                for call in response.tool_calls
            ],
            "model": response.model,
            "usage": response.usage,
            "reasoning_content": response.reasoning_content,
        },
        sort_keys=True,
    )


def _int_from_mapping(data: Mapping[str, Any], key: str, default: int) -> int:
    value = data.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _float_from_mapping(data: Mapping[str, Any], key: str, default: float) -> float:
    value = data.get(key, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


__all__ = [
    "TurnCircuitBreakerOpenError",
    "TurnProcessingError",
    "TurnProcessor",
    "TurnPersistenceError",
    "TurnResult",
    "TurnRetryExhaustedError",
    "TurnTimeoutError",
]
