"""Turn processing for FridayV2."""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from dataclasses import dataclass, replace
from typing import Any
from uuid import uuid4

from friday_memory.models.budget import BudgetSeverity, BudgetStatus

from friday_chat.config import FridayChatConfig
from friday_chat.display import HeartbeatFactory, HeartbeatKind, NoopHeartbeatFactory
from friday_chat.runtime import FridayRuntime, build_runtime
from friday_chat.tools.loop import ToolLoop
from friday_chat.tools.output import (
    MCPResultLimitError,
    reconcile_mcp_call_ids,
    redact_tool_request_message,
    safe_mcp_call_id,
)
from friday_chat.tools.schemas import ToolCallRecord, ToolDefinition
from friday_chat.tools.selection import (
    ToolBudgetSnapshot,
    ToolRejectionReason,
    ToolSelectionError,
)
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
    selected_tool_names: tuple[str, ...] = ()
    tool_budget_snapshot: ToolBudgetSnapshot | None = None
    budget_status: BudgetStatus | None = None
    tool_calls: tuple[ToolCallRecord, ...] = ()
    raw_response: str = ""


@dataclass(frozen=True)
class PreparedTurn:
    """Prepared prompt, context, and budget data for one turn."""

    user_message: str
    total_start: float
    tool_definitions: tuple[ToolDefinition, ...]
    tool_budget_snapshot: ToolBudgetSnapshot
    tool_context_injected: bool
    context_budget_tokens: int
    retrieval_seconds: float
    memories: list[str]
    context_text: str
    prompt_text: str
    messages: list[dict[str, Any]]
    budget_status: BudgetStatus
    mcp_tool_names: frozenset[str] = frozenset()


class TurnProcessingError(RuntimeError):
    """Base class for FridayV2 turn-processing failures."""


class TurnBudgetError(TurnProcessingError):
    """Required tools or the memory floor cannot fit before retrieval/model calls."""

    def __init__(self, reason: ToolRejectionReason) -> None:
        self.reason = reason
        super().__init__(
            f"Tool selection failed ({reason.value}); check required tools and turn budget policy."
        )


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
            raise TurnCircuitBreakerOpenError(
                "Turn processing circuit breaker is open."
            )

        prepared = await self._prepare_turn(user_message)
        (
            assistant_message,
            model_response,
            tool_calls,
            llm_seconds,
        ) = await self._complete_model_turn(
            prepared.user_message,
            prepared.messages,
            prepared.tool_definitions,
            mcp_names=prepared.mcp_tool_names,
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
        self._runtime.tool_selection.record_completed_turn(
            prepared.tool_budget_snapshot,
            tuple(call.name for call in tool_calls),
        )

        return TurnResult(
            user_message=prepared.user_message,
            assistant_message=assistant_message,
            retrieved_memory_count=len(prepared.memories),
            tool_context_injected=prepared.tool_context_injected,
            prompt=prepared.prompt_text,
            context=prepared.context_text,
            metrics=metrics,
            context_budget_tokens=prepared.context_budget_tokens,
            tool_schema_tokens=prepared.tool_budget_snapshot.schema_tokens,
            selected_tool_names=prepared.tool_budget_snapshot.selected_names,
            tool_budget_snapshot=prepared.tool_budget_snapshot,
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
            raise TurnCircuitBreakerOpenError(
                "Turn processing circuit breaker is open."
            )

        prepared = await self._prepare_turn(user_message)
        if prepared.tool_definitions:
            (
                assistant_message,
                model_response,
                tool_calls,
                llm_seconds,
            ) = await self._complete_model_turn(
                prepared.user_message,
                prepared.messages,
                prepared.tool_definitions,
                mcp_names=prepared.mcp_tool_names,
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
        self._runtime.tool_selection.record_completed_turn(
            prepared.tool_budget_snapshot,
            tuple(call.name for call in tool_calls),
        )

        return TurnResult(
            user_message=prepared.user_message,
            assistant_message=assistant_message,
            retrieved_memory_count=len(prepared.memories),
            tool_context_injected=prepared.tool_context_injected,
            prompt=prepared.prompt_text,
            context=prepared.context_text,
            metrics=metrics,
            context_budget_tokens=prepared.context_budget_tokens,
            tool_schema_tokens=prepared.tool_budget_snapshot.schema_tokens,
            selected_tool_names=prepared.tool_budget_snapshot.selected_names,
            tool_budget_snapshot=prepared.tool_budget_snapshot,
            budget_status=prepared.budget_status,
            tool_calls=tool_calls,
            raw_response=raw_response,
        )

    async def _prepare_turn(self, user_message: str) -> PreparedTurn:
        total_start = now_seconds()
        await self._runtime.start_mcp_tools()
        try:
            self._runtime.tool_selection.synchronize_registered_tools(
                self._runtime.tools.list_tools(),
                mcp_metadata=(
                    self._runtime.mcp_tools.tool_metadata
                    if self._runtime.mcp_tools is not None
                    else None
                ),
            )
            selection = self._runtime.tool_selection.select_for_turn(user_message)
        except ToolSelectionError as exc:
            raise TurnBudgetError(exc.reason) from None
        tool_definitions = selection.definitions
        context_budget_tokens = _calculate_dynamic_context_budget(
            self._runtime.config,
            tool_budget=selection.budget,
        )

        mcp_tool_names = frozenset(self._mcp_names())
        retrieval_start = now_seconds()
        memories = await self._runtime.memory.retrieve(
            user_message,
            token_limit=context_budget_tokens,
        )
        retrieval_seconds = elapsed_seconds(retrieval_start)

        tool_context = None
        if (
            self._runtime.config.tools.context.get("include_in_context") is True
            and tool_definitions
        ):
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
            tool_budget=selection.budget,
        )
        return PreparedTurn(
            user_message=user_message,
            total_start=total_start,
            tool_definitions=tool_definitions,
            tool_budget_snapshot=selection.budget,
            tool_context_injected=tool_context is not None,
            context_budget_tokens=context_budget_tokens,
            retrieval_seconds=retrieval_seconds,
            memories=memories,
            context_text=context_text,
            prompt_text=prompt_text,
            messages=messages,
            budget_status=budget_status,
            mcp_tool_names=mcp_tool_names,
        )

    async def _complete_model_turn(
        self,
        user_message: str,
        messages: list[dict[str, Any]],
        tool_definitions: tuple[ToolDefinition, ...],
        *,
        mcp_names: frozenset[str] | None = None,
    ) -> tuple[
        str,
        ChatModelResponse,
        tuple[ToolCallRecord, ...],
        float,
    ]:
        llm_start = now_seconds()
        mcp_names = mcp_names if mcp_names is not None else frozenset(self._mcp_names())
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
                mcp_names=mcp_names,
            )
        model_response = self._safe_model_response(
            model_response,
            mcp_names,
            used_call_ids={
                call.call_id for call in tool_calls if call.call_id is not None
            },
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
        *,
        mcp_names: frozenset[str],
    ) -> tuple[ChatModelResponse, tuple[ToolCallRecord, ...]]:
        loop_config = self._runtime.config.tools.loop
        max_iterations = _int_from_mapping(loop_config, "max_iterations", 3)
        all_tool_calls: list[ToolCallRecord] = []
        response = initial_response
        used_call_ids: set[str] = set()
        for _iteration in range(max_iterations):
            if not response.has_tool_calls:
                return response, tuple(all_tool_calls)
            tool_calls = await self._execute_tool_calls(
                response,
                tool_definitions,
                used_call_ids=used_call_ids,
                mcp_names=mcp_names,
            )
            assistant_message = redact_tool_request_message(
                _assistant_message_from_response(response),
                tool_calls,
                set(mcp_names),
            )
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
            # New native IDs may claim an ID belonging to an earlier MCP call.
            # Repair the retained pair and atomic facts even on the last/pending
            # fallback response, before another invocation or turn capture.
            reconcile_mcp_call_ids(
                all_tool_calls,
                messages,
                {
                    call.call_id
                    for call in response.tool_calls
                    if call.name not in mcp_names and call.call_id is not None
                },
                used_call_ids,
            )
        return response, tuple(all_tool_calls)

    def _mcp_names(self) -> set[str]:
        bridge = self._runtime.mcp_tools
        return set(bridge.tool_metadata) if bridge is not None else set()

    def _safe_model_response(
        self,
        response: ChatModelResponse,
        mcp_names: frozenset[str],
        *,
        used_call_ids: set[str] | None = None,
    ) -> ChatModelResponse:
        """Drop any remaining MCP request prose/raw copies before return/capture."""
        if not any(call.name in mcp_names for call in response.tool_calls):
            return response
        used = {
            call.call_id
            for call in response.tool_calls
            if call.name not in mcp_names and call.call_id is not None
        }
        used.update(used_call_ids or ())
        calls = tuple(
            replace(call, arguments={}, call_id=safe_mcp_call_id(call.call_id, used))
            if call.name in mcp_names
            else call
            for call in response.tool_calls
        )
        return replace(
            response,
            content="",
            tool_calls=calls,
            reasoning_content=None,
            raw_response=None,
        )

    async def _execute_tool_calls(
        self,
        response: ChatModelResponse,
        tool_definitions: tuple[ToolDefinition, ...],
        *,
        used_call_ids: set[str] | None = None,
        mcp_names: frozenset[str] = frozenset(),
    ) -> tuple[ToolCallRecord, ...]:
        loop_config = self._runtime.config.tools.loop
        max_iterations = _int_from_mapping(loop_config, "max_iterations", 3)
        tool_loop = ToolLoop(
            self._runtime.tools,
            max_iterations=max_iterations,
            heartbeat_factory=self._heartbeat_factory,
        )
        try:
            tool_result = await tool_loop.run(
                [_assistant_message_from_response(response)],
                tool_definitions,
                used_call_ids=used_call_ids,
                mcp_tool_names=mcp_names,
            )
        except MCPResultLimitError:
            raise TurnProcessingError(
                "MCP result limit is too small for safe execution."
            ) from None
        if any(
            call.name in mcp_names and call.mcp_provenance is None
            for call in tool_result.tool_calls
        ):
            raise TurnProcessingError("MCP execution requires per-call provenance")
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
        {
            "role": "system",
            "content": f"{system_prompt}\n\nTurn: {turn_count}\n{context_text}",
        },
        {"role": "user", "content": user_message},
    ]


def _calculate_dynamic_context_budget(
    config: FridayChatConfig,
    *,
    tool_budget: ToolBudgetSnapshot,
) -> int:
    system_prompt_tokens = max(1, len(config.chat.system_prompt) // 4)
    return min(
        tool_budget.available_context_tokens,
        max(
            0,
            tool_budget.available_context_tokens
            - system_prompt_tokens
            - tool_budget.schema_tokens
            - tool_budget.reserved_result_tokens,
        ),
    )


def _build_budget_status(
    prompt_text: str,
    *,
    tool_budget: ToolBudgetSnapshot,
) -> BudgetStatus:
    available_budget = tool_budget.available_context_tokens
    message_tokens = max(1, len(prompt_text) // 4)
    total_tokens = message_tokens + tool_budget.schema_tokens
    utilization_pct = (
        (total_tokens / available_budget) * 100
        if available_budget
        else (100.0 if total_tokens else 0.0)
    )
    return BudgetStatus(
        total_tokens=total_tokens,
        available_budget=available_budget,
        utilization_pct=utilization_pct,
        overage_tokens=max(0, total_tokens - available_budget),
        severity=BudgetSeverity.from_utilization(utilization_pct),
        message_tokens=message_tokens,
        tool_tokens=tool_budget.schema_tokens,
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
    raise TypeError(
        f"Chat model returned unsupported response type: {type(response)!r}"
    )


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


def _tool_result_messages(
    calls: tuple[ToolCallRecord, ...] | list[ToolCallRecord],
) -> list[dict[str, Any]]:
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
