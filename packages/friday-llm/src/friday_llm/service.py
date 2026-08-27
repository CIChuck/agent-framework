"""
LiteLLM Chat Completion Service.

Wraps litellm.acompletion with retry logic, telemetry, and
structured response parsing.

Ref: Batch 3 Specification, Section 3.1
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import warnings
from collections.abc import AsyncIterator
from typing import Any

import litellm
from friday_core.interfaces.llm import ChatCompletionResponse, ToolCall
from pydantic import BaseModel
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from friday_llm.capabilities import OperatorCapabilityDeclaration
from friday_llm.circuit_breaker import CircuitBreaker
from friday_llm.config import ResilienceConfig
from friday_llm.exceptions import (
    LLMConfigurationError,
    LLMRetryExhaustedError,
    LLMTimeoutError,
    TargetIdentityError,
)
from friday_llm.generation import (
    GenerationConfig,
    ReasoningConfig,
    ReasoningMode,
    SamplingConfig,
    resolve_generation,
)
from friday_llm.pricing import CostCalculator, PricingConfig
from friday_llm.provider_options import ProviderOptions
from friday_llm.requests import (
    ChatCompletionRequest,
    CompletionAssurance,
    CompletionToolCall,
    CompletionUsage,
    TypedChatCompletionResponse,
)
from friday_llm.streaming import (
    FinishEvent,
    ReasoningDeltaEvent,
    StreamEvent,
    TextDeltaEvent,
    ToolCallAssembler,
    ToolCallDeltaEvent,
    UsageEvent,
)
from friday_llm.targets import ExecutionTarget, ModelTarget, TransportTarget
from friday_llm.telemetry_helper import LLMTelemetryHelper
from friday_llm.telemetry_models import ConversationContext, TokenUsage
from friday_llm.translation import (
    LiteLLMCallSpec,
    TranslationSummary,
    _translate_tool_selection,
    translate_generation,
)

logger = logging.getLogger(__name__)


class LiteLLMService:
    """
    Chat completion service using LiteLLM.

    Implements the LLMClient protocol with:
    - Multi-provider support (OpenAI, Anthropic, Ollama, etc.)
    - Configurable retry logic with exponential backoff
    - Timeout support for all operations
    - Optional circuit breaker for fail-fast behavior
    - Tool call parsing from responses
    - Optional telemetry integration

    Example:
        # Simple usage with sensible defaults
        service = LiteLLMService(model_name="gpt-4")

        # Custom resilience settings
        service = LiteLLMService(
            model_name="gpt-4",
            resilience=ResilienceConfig(
                max_retries=5,
                timeout_seconds=60.0,
            ),
        )
    """

    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        api_base: str | None = None,
        max_retries: int | None = None,
        telemetry: Any | None = None,
        resilience: ResilienceConfig | None = None,
        pricing_config: PricingConfig | None = None,
        thinking_enabled: bool | None = None,
        transport_target: TransportTarget | None = None,
        model_target: ModelTarget | None = None,
        generation_defaults: GenerationConfig | None = None,
        capability_declaration: OperatorCapabilityDeclaration | None = None,
    ) -> None:
        """
        Initialize the LiteLLM service.

        Args:
            model_name: Model identifier (e.g., 'gpt-4', 'claude-3-opus',
                       'ollama/llama2')
            api_key: API key for the provider. Not needed for local models.
            api_base: Base URL for API (e.g., 'http://localhost:11434' for Ollama)
            max_retries: DEPRECATED - Use resilience=ResilienceConfig(max_retries=N)
            telemetry: Optional TelemetryInterface for observability
            resilience: Configuration for retry, timeout, and circuit breaker
            pricing_config: Configuration for cost estimation
            thinking_enabled: Enable model thinking/reasoning mode.
                When *False* (default), ``thinking`` is explicitly
                disabled in the API call, which avoids
                ``reasoning_content`` validation errors on providers
                like Moonshot Kimi K2.5.
        """
        self.model = model_name
        self.api_key = api_key
        self.api_base = api_base
        self.telemetry = telemetry
        self.thinking_enabled = False if thinking_enabled is None else thinking_enabled
        self._legacy_thinking_explicit = thinking_enabled is not None
        self.generation_defaults = generation_defaults
        self.capability_declaration = capability_declaration
        if (transport_target is None) != (model_target is None):
            raise TargetIdentityError(
                "transport_target and model_target must be supplied together"
            )
        self.execution_target = (
            ExecutionTarget(transport=transport_target, model=model_target)
            if transport_target is not None and model_target is not None
            else None
        )
        if self.execution_target is not None:
            model_id = self.execution_target.model.model_id
            if model_name != model_id and not model_name.endswith(f"/{model_id}"):
                raise TargetIdentityError(
                    "model_name routing identity contradicts model_target.model_id"
                )
            transport = self.execution_target.transport
            if (
                transport.provider == "openai_compatible"
                and transport.dialect == "openai_chat_completions"
                and not model_name.startswith("openai/")
            ):
                raise TargetIdentityError(
                    "OpenAI-compatible Chat targets require LiteLLM's openai/ "
                    "routing prefix"
                )
        if thinking_enabled is not None and generation_defaults is not None:
            configured = generation_defaults.reasoning
            if configured is not None:
                expected = (
                    ReasoningMode.ENABLED
                    if thinking_enabled
                    else ReasoningMode.DISABLED
                )
                if configured.mode is not expected:
                    raise LLMConfigurationError(
                        "thinking_enabled conflicts with generation_defaults.reasoning"
                    )
            warnings.warn(
                "thinking_enabled is deprecated; use generation_defaults.reasoning",
                DeprecationWarning,
                stacklevel=2,
            )
        elif thinking_enabled is not None:
            warnings.warn(
                "thinking_enabled is deprecated; use generation_defaults.reasoning",
                DeprecationWarning,
                stacklevel=2,
            )

        # Handle backward compatibility with max_retries
        if max_retries is not None:
            warnings.warn(
                "max_retries parameter is deprecated. "
                "Use resilience=ResilienceConfig(max_retries=N) instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            if resilience is None:
                resilience = ResilienceConfig(max_retries=max_retries)
            # If both provided, resilience takes precedence (don't override)

        # Use defaults if no config provided
        self._resilience = resilience or ResilienceConfig()

        # Initialize circuit breaker
        self._circuit_breaker = CircuitBreaker(
            self._resilience.circuit_breaker,
            model=model_name,
        )

        # Initialize telemetry helper with cost calculator
        self._cost_calculator = CostCalculator(pricing_config)
        self._telemetry_helper = LLMTelemetryHelper(
            telemetry=telemetry,
            cost_calculator=self._cost_calculator,
            provider_name=self._detect_provider(model_name),
        )

    def _detect_provider(self, model: str) -> str:
        """Detect provider from model name."""
        model_lower = model.lower()
        if model_lower.startswith("gpt") or "openai" in model_lower:
            return "openai"
        if model_lower.startswith("claude") or "anthropic" in model_lower:
            return "anthropic"
        if "ollama" in model_lower:
            return "ollama"
        if "gemini" in model_lower:
            return "google"
        if "bedrock" in model_lower:
            return "aws.bedrock"
        if "lmstudio" in model_lower or "local" in model_lower:
            return "lmstudio"
        return "litellm"

    @property
    def resilience(self) -> ResilienceConfig:
        """Get current resilience configuration."""
        return self._resilience

    def _legacy_generation_config(
        self,
        *,
        temperature: float,
        max_tokens: int | None,
    ) -> GenerationConfig:
        defaults = self.generation_defaults or GenerationConfig()
        reasoning = defaults.reasoning or ReasoningConfig(
            mode=(
                ReasoningMode.ENABLED
                if self.thinking_enabled
                else ReasoningMode.DISABLED
            )
        )
        sampling_values = (
            defaults.sampling.model_dump() if defaults.sampling is not None else {}
        )
        sampling_values["temperature"] = temperature
        return GenerationConfig(
            reasoning=reasoning,
            sampling=SamplingConfig.model_validate(sampling_values),
            max_tokens=max_tokens if max_tokens is not None else defaults.max_tokens,
        )

    def _build_call_spec(
        self,
        *,
        messages: list[dict[str, Any]] | tuple[dict[str, Any], ...],
        tools: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
        tool_choice: str | dict[str, Any] | None,
        generation: GenerationConfig,
        provider_options: ProviderOptions | None,
        metadata: dict[str, Any] | None,
        legacy: bool,
    ) -> LiteLLMCallSpec:
        if legacy and self.execution_target is None:
            kwargs: dict[str, Any] = {"drop_params": True, "modify_params": True}
            sampling = generation.sampling
            if sampling is not None and sampling.temperature is not None:
                kwargs["temperature"] = sampling.temperature
            if generation.max_tokens is not None:
                kwargs["max_tokens"] = generation.max_tokens
            if not self.thinking_enabled:
                kwargs["thinking"] = {"type": "disabled"}
            summary = TranslationSummary(
                requested_fields=("legacy.thinking_enabled",),
                emitted_fields=("thinking",) if not self.thinking_enabled else (),
                capability_sources=("legacy_compatibility@1",),
            )
        else:
            translated = translate_generation(
                self.execution_target,
                generation,
                provider_options,
                self.capability_declaration,
            )
            kwargs = dict(translated.kwargs)
            kwargs["drop_params"] = bool(legacy)
            if legacy:
                kwargs["modify_params"] = True
            summary = translated.summary

        tool_selection = _translate_tool_selection(
            self.execution_target,
            tools,
            tool_choice,
        )
        tools = tool_selection.tools
        tool_choice = tool_selection.tool_choice
        if tool_selection.requested_fields:
            summary = TranslationSummary(
                requested_fields=(
                    *summary.requested_fields,
                    *tool_selection.requested_fields,
                ),
                emitted_fields=(
                    *summary.emitted_fields,
                    *tool_selection.emitted_fields,
                ),
                capability_sources=summary.capability_sources,
                target_profile=summary.target_profile,
                litellm_version=summary.litellm_version,
            )

        return LiteLLMCallSpec.from_parts(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            generation_kwargs=kwargs,
            api_key=self.api_key,
            api_base=self.api_base,
            metadata=metadata,
            summary=summary,
        )

    def _validate_legacy_reasoning(self, generation: GenerationConfig) -> None:
        if not self._legacy_thinking_explicit or generation.reasoning is None:
            return
        expected = (
            ReasoningMode.ENABLED
            if self.thinking_enabled
            else ReasoningMode.DISABLED
        )
        if generation.reasoning.mode is not expected:
            raise LLMConfigurationError(
                "thinking_enabled conflicts with typed request reasoning"
            )

    async def chat_completion_request(
        self,
        request: ChatCompletionRequest,
    ) -> TypedChatCompletionResponse:
        """Execute a strict typed completion request."""

        generation = resolve_generation(
            self.generation_defaults,
            request.overrides,
        )
        self._validate_legacy_reasoning(generation)
        metadata = self._build_langfuse_metadata(None, "chat_completion_request")
        spec = self._build_call_spec(
            messages=request.messages,
            tools=request.tools,
            tool_choice=(
                request.tool_choice.model_dump(mode="json")
                if isinstance(request.tool_choice, BaseModel)
                else request.tool_choice
            ),
            generation=generation,
            provider_options=request.provider_options,
            metadata=metadata,
            legacy=False,
        )
        response = await self._call_with_retry(
            spec=spec,
            timeout=request.timeout or self._resilience.timeout_seconds,
            operation="chat_completion_request",
        )
        return self._parse_typed_response(response, spec.summary)

    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event if configured."""
        if self.telemetry:
            self.telemetry.capture_event(event_name, data)

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        response_model: type[BaseModel] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        timeout: float | None = None,
        conversation_context: ConversationContext | None = None,
    ) -> ChatCompletionResponse:
        """
        Execute chat completion with optional tool calling.

        Args:
            messages: Conversation history in OpenAI format
            tools: Optional tool schemas for function calling
            response_model: Optional Pydantic model for structured output
            temperature: Sampling temperature
            max_tokens: Maximum tokens for the response (limits output length)
            timeout: Override default timeout for this call
            conversation_context: Optional context for request/response pairing

        Returns:
            ChatCompletionResponse with content and/or tool_calls

        Raises:
            LLMTimeoutError: If the call times out
            LLMRetryExhaustedError: If max retries exceeded
            CircuitBreakerOpenError: If circuit breaker is open
        """
        effective_timeout = timeout or self._resilience.timeout_seconds

        langfuse_meta = self._build_langfuse_metadata(
            conversation_context, "chat_completion"
        )
        spec = self._build_call_spec(
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None,
            generation=self._legacy_generation_config(
                temperature=temperature,
                max_tokens=max_tokens,
            ),
            provider_options=None,
            metadata=langfuse_meta,
            legacy=True,
        )

        with self._telemetry_helper.track_completion(
            model=self.model,
            context=conversation_context,
            temperature=temperature,
            tool_count=len(tools) if tools else 0,
        ) as tracker:
            try:
                response = await self._call_with_retry(
                    spec=spec,
                    timeout=effective_timeout,
                    operation="chat_completion",
                )

                # Parse the response
                result = self._parse_response(response)

                # Extract finish reasons
                finish_reasons = []
                for choice in response.choices:
                    if hasattr(choice, "finish_reason") and choice.finish_reason:
                        finish_reasons.append(choice.finish_reason)

                # Record response details for telemetry
                tracker.set_response(
                    response_model=getattr(response, "model", self.model),
                    response_id=getattr(response, "id", None),
                    usage=TokenUsage.from_response(result.usage),
                    finish_reasons=finish_reasons,
                    tool_calls_count=len(result.tool_calls),
                )

                # Handle structured output if requested
                if response_model and result.content:
                    try:
                        raw = result.content.strip()
                        # Strip markdown code fences that LLMs
                        # sometimes wrap around JSON responses
                        raw = re.sub(
                            r"^```(?:json)?\s*\n?",
                            "",
                            raw,
                        )
                        raw = re.sub(r"\n?```\s*$", "", raw)
                        parsed = response_model.model_validate_json(raw)
                        result._parsed_model = parsed
                    except Exception as e:
                        logger.warning(
                            "Failed to parse response into model: %s",
                            e,
                        )

                return result

            except LLMRetryExhaustedError as e:
                tracker.set_retry_info(e.attempts, e.attempts)
                raise

            except LLMTimeoutError:
                raise

    async def chat_completion_stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        timeout: float | None = None,
        conversation_context: ConversationContext | None = None,
    ) -> AsyncIterator[str]:
        """
        Execute streaming chat completion with resilience and TTFT tracking.

        Yields content chunks as they arrive from the LLM.
        Includes retry logic, timeout support, and time-to-first-token tracking.

        Args:
            messages: Conversation history in OpenAI format
            tools: Optional tool schemas for function calling
            temperature: Sampling temperature
            max_tokens: Maximum tokens for the response (limits output length)
            timeout: Override default stream timeout for this call
            conversation_context: Optional context for request/response pairing

        Yields:
            String chunks of the response content

        Raises:
            LLMTimeoutError: If the call times out
            LLMRetryExhaustedError: If max retries exceeded
            CircuitBreakerOpenError: If circuit breaker is open

        Example:
            async for chunk in llm.chat_completion_stream(messages):
                print(chunk, end="", flush=True)
        """
        effective_timeout = timeout or self._resilience.stream_timeout_seconds
        streaming_tracker = self._telemetry_helper.create_streaming_tracker()
        langfuse_meta = self._build_langfuse_metadata(
            conversation_context, "chat_completion_stream"
        )
        spec = self._build_call_spec(
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None,
            generation=self._legacy_generation_config(
                temperature=temperature,
                max_tokens=max_tokens,
            ),
            provider_options=None,
            metadata=langfuse_meta,
            legacy=True,
        )

        with self._telemetry_helper.track_completion(
            model=self.model,
            context=conversation_context,
            temperature=temperature,
            tool_count=len(tools) if tools else 0,
        ) as tracker:
            try:
                # Setup stream with retry logic
                response = await self._call_stream_with_retry(
                    spec=spec,
                    timeout=effective_timeout,
                )

                # Start TTFT tracking after connection established
                streaming_tracker.start()

                # Stream chunks with timeout
                try:
                    async for event in self._events_from_response(
                        self._iterate_with_timeout(response, effective_timeout)
                    ):
                        if isinstance(event, TextDeltaEvent):
                            streaming_tracker.record_chunk(
                                len(event.text.split())
                            )
                            yield event.text
                except asyncio.TimeoutError as e:
                    await self._close_stream(response)
                    raise LLMTimeoutError(
                        "Streaming response timed out",
                        timeout_seconds=effective_timeout,
                        operation="streaming",
                        model=self.model,
                    ) from e
                except asyncio.CancelledError:
                    await self._close_stream(response)
                    raise

                # Record streaming metrics
                tracker.set_streaming_metrics(streaming_tracker.finish())
                tracker.set_response(response_model=self.model)

            except LLMRetryExhaustedError as e:
                tracker.set_retry_info(e.attempts, e.attempts)
                raise

            except LLMTimeoutError:
                raise

    async def chat_completion_events(
        self,
        request: ChatCompletionRequest,
    ) -> AsyncIterator[StreamEvent]:
        """Stream typed text, reasoning, tool, usage, and finish events."""

        generation = resolve_generation(
            self.generation_defaults,
            request.overrides,
        )
        self._validate_legacy_reasoning(generation)
        spec = self._build_call_spec(
            messages=request.messages,
            tools=request.tools,
            tool_choice=(
                request.tool_choice.model_dump(mode="json")
                if isinstance(request.tool_choice, BaseModel)
                else request.tool_choice
            ),
            generation=generation,
            provider_options=request.provider_options,
            metadata=self._build_langfuse_metadata(None, "chat_completion_events"),
            legacy=False,
        )
        timeout = request.timeout or self._resilience.stream_timeout_seconds
        response = await self._call_stream_with_retry(spec=spec, timeout=timeout)
        try:
            async for event in self._events_from_response(
                self._iterate_with_timeout(response, timeout)
            ):
                yield event
        except asyncio.CancelledError:
            await self._close_stream(response)
            raise
        except asyncio.TimeoutError as error:
            await self._close_stream(response)
            raise LLMTimeoutError(
                "Streaming response timed out",
                timeout_seconds=timeout,
                operation="streaming",
                model=self.model,
            ) from error

    async def _events_from_response(self, response: Any) -> AsyncIterator[StreamEvent]:
        assembler = ToolCallAssembler()
        async for chunk in response:
            usage = getattr(chunk, "usage", None)
            choices = getattr(chunk, "choices", None) or []
            if usage is not None:
                details = getattr(usage, "completion_tokens_details", None)
                yield UsageEvent(
                    prompt_tokens=int(getattr(usage, "prompt_tokens", 0) or 0),
                    completion_tokens=int(
                        getattr(usage, "completion_tokens", 0) or 0
                    ),
                    total_tokens=int(getattr(usage, "total_tokens", 0) or 0),
                    reasoning_tokens=(
                        int(getattr(details, "reasoning_tokens", 0))
                        if details is not None
                        and getattr(details, "reasoning_tokens", None) is not None
                        else None
                    ),
                )
            if not choices:
                continue
            choice = choices[0]
            delta = getattr(choice, "delta", None)
            if delta is not None:
                content = getattr(delta, "content", None)
                if content:
                    yield TextDeltaEvent(text=str(content))
                reasoning = getattr(delta, "reasoning_content", None) or getattr(
                    delta, "reasoning", None
                )
                if reasoning:
                    yield ReasoningDeltaEvent(text=str(reasoning))
                for tool_delta in getattr(delta, "tool_calls", None) or []:
                    function = getattr(tool_delta, "function", None)
                    event = ToolCallDeltaEvent(
                        index=int(getattr(tool_delta, "index", 0) or 0),
                        call_id=getattr(tool_delta, "id", None),
                        name=getattr(function, "name", None),
                        arguments_delta=str(
                            getattr(function, "arguments", "") or ""
                        ),
                    )
                    assembler.add(event)
                    yield event
            finish_reason = getattr(choice, "finish_reason", None)
            if finish_reason is not None:
                for completed_event in assembler.finish():
                    yield completed_event
                yield FinishEvent(finish_reason=str(finish_reason))

    @staticmethod
    async def _iterate_with_timeout(
        response: Any,
        timeout: float,
    ) -> AsyncIterator[Any]:
        iterator = response.__aiter__()
        while True:
            try:
                yield await LiteLLMService._next_with_timeout(iterator, timeout)
            except StopAsyncIteration:
                break

    @staticmethod
    async def _next_with_timeout(iterator: Any, timeout: float) -> Any:
        """Read one item while preserving cancellation on Python 3.10."""

        pending_read: asyncio.Future[Any] = asyncio.ensure_future(
            iterator.__anext__()
        )
        try:
            done, _ = await asyncio.wait({pending_read}, timeout=timeout)
        except asyncio.CancelledError:
            pending_read.cancel()
            await asyncio.gather(pending_read, return_exceptions=True)
            raise
        if not done:
            pending_read.cancel()
            await asyncio.gather(pending_read, return_exceptions=True)
            raise asyncio.TimeoutError
        return pending_read.result()

    @staticmethod
    async def _close_stream(response: Any) -> None:
        close = getattr(response, "aclose", None)
        if close is not None:
            result = close()
            if asyncio.iscoroutine(result):
                await result

    def _build_langfuse_metadata(
        self,
        context: ConversationContext | None,
        generation_name: str = "chat_completion",
    ) -> dict[str, Any]:
        """
        Build LangFuse trace metadata from conversation context.

        Returns a metadata dict for ``litellm.acompletion`` that
        LangFuse's native callback uses to group and label traces.

        Always returns a dict (never ``None``) so that the model
        name is visible in Langfuse even when no conversation
        context is available.

        Args:
            context: The conversation context for this call.
            generation_name: Label for this generation in LangFuse.

        Returns:
            Metadata dict with at least ``generation_name``.
        """
        # Include the model name in the generation label so traces
        # are immediately identifiable in the Langfuse UI.
        label = f"{self.model} - {generation_name}"
        meta: dict[str, Any] = {
            "generation_name": label,
        }

        if context is not None:
            meta["trace_user_id"] = context.session_id
            meta["session_id"] = context.session_id
            if context.conversation_id:
                meta["trace_id"] = context.conversation_id
                meta["trace_name"] = (
                    f"turn-{context.turn_id}" if context.turn_id else "agent-turn"
                )
            if context.turn_id:
                meta["tags"] = [f"turn:{context.turn_id}"]

        return meta

    async def _call_with_retry(
        self,
        spec: LiteLLMCallSpec,
        timeout: float,
        operation: str,
    ) -> Any:
        """Execute LiteLLM call with retry logic, timeout, and circuit breaker."""
        retry_exceptions = self._resilience.get_retry_exceptions()
        attempts = 0

        @retry(
            retry=retry_if_exception_type(retry_exceptions),
            stop=stop_after_attempt(self._resilience.max_retries + 1),
            wait=wait_exponential(
                multiplier=self._resilience.backoff_multiplier,
                min=self._resilience.backoff_min,
                max=self._resilience.backoff_max,
            ),
            reraise=False,
        )
        async def _call() -> Any:
            nonlocal attempts
            attempts += 1
            kwargs = spec.to_kwargs()

            logger.debug(
                "litellm.acompletion: model=%s has_metadata=%s generation_name=%s",
                kwargs.get("model"),
                bool(kwargs.get("metadata")),
                kwargs.get("metadata", {}).get("generation_name"),
            )

            try:
                return await asyncio.wait_for(
                    litellm.acompletion(**kwargs),
                    timeout=timeout,
                )
            except asyncio.TimeoutError as e:
                raise LLMTimeoutError(
                    f"LLM call timed out after {timeout}s",
                    timeout_seconds=timeout,
                    operation=operation,
                    model=self.model,
                ) from e

        try:
            # Execute through circuit breaker
            return await self._circuit_breaker.call(_call)
        except RetryError as e:
            # Convert tenacity RetryError to our custom exception
            candidate = e.last_attempt.exception() if e.last_attempt else e
            last_error = (
                candidate
                if isinstance(candidate, Exception)
                else RuntimeError("retry failed without an Exception result")
            )
            raise LLMRetryExhaustedError(
                f"LLM call failed after {attempts} attempts",
                attempts=attempts,
                last_error=last_error,
                model=self.model,
            ) from e

    async def _call_stream_with_retry(
        self,
        spec: LiteLLMCallSpec,
        timeout: float,
    ) -> Any:
        """Execute streaming call setup with retry on connection errors."""
        retry_exceptions = self._resilience.get_retry_exceptions()
        attempts = 0

        @retry(
            retry=retry_if_exception_type(retry_exceptions),
            stop=stop_after_attempt(self._resilience.max_retries + 1),
            wait=wait_exponential(
                multiplier=self._resilience.backoff_multiplier,
                min=self._resilience.backoff_min,
                max=self._resilience.backoff_max,
            ),
            reraise=False,
        )
        async def _setup_stream() -> Any:
            nonlocal attempts
            attempts += 1
            kwargs = spec.to_kwargs(stream=True)

            logger.debug(
                "litellm.acompletion (stream) kwargs: model=%s "
                "has_metadata=%s generation_name=%s",
                kwargs.get("model"),
                bool(kwargs.get("metadata")),
                kwargs.get("metadata", {}).get("generation_name"),
            )

            try:
                return await asyncio.wait_for(
                    litellm.acompletion(**kwargs),
                    timeout=timeout,
                )
            except asyncio.TimeoutError as e:
                raise LLMTimeoutError(
                    f"Stream setup timed out after {timeout}s",
                    timeout_seconds=timeout,
                    operation="streaming",
                    model=self.model,
                ) from e

        try:
            return await self._circuit_breaker.call(_setup_stream)
        except RetryError as e:
            candidate = e.last_attempt.exception() if e.last_attempt else e
            last_error = (
                candidate
                if isinstance(candidate, Exception)
                else RuntimeError("stream retry failed without an Exception result")
            )
            raise LLMRetryExhaustedError(
                f"Stream setup failed after {attempts} attempts",
                attempts=attempts,
                last_error=last_error,
                model=self.model,
            ) from e

    def _parse_response(self, response: Any) -> ChatCompletionResponse:
        """Parse LiteLLM response into ChatCompletionResponse."""
        message = response.choices[0].message

        # Parse tool calls if present
        tool_calls: list[ToolCall] = []
        if message.tool_calls:
            for tc in message.tool_calls:
                arguments = self._parse_tool_arguments(
                    tc.function.arguments,
                    tc.function.name,
                )
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=arguments,
                    )
                )

        # Extract usage information
        usage = {}
        if hasattr(response, "usage") and response.usage:
            usage = {
                "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                "total_tokens": getattr(response.usage, "total_tokens", 0),
            }

        # Preserve reasoning_content for thinking models (e.g. Moonshot
        # Kimi K2.5).  Must be replayed in assistant tool-call messages
        # or the provider will reject the next request.
        reasoning_content = getattr(message, "reasoning_content", None)

        return ChatCompletionResponse(
            content=message.content,
            tool_calls=tool_calls,
            model=getattr(response, "model", self.model),
            usage=usage,
            reasoning_content=reasoning_content,
        )

    def _parse_typed_response(
        self,
        response: Any,
        summary: TranslationSummary,
    ) -> TypedChatCompletionResponse:
        """Convert the dynamic LiteLLM response into the typed Friday contract."""

        legacy = self._parse_response(response)
        choice = response.choices[0]
        message = choice.message
        reasoning_content = getattr(message, "reasoning_content", None) or getattr(
            message, "reasoning", None
        )
        usage = getattr(response, "usage", None)
        details = (
            getattr(usage, "completion_tokens_details", None)
            if usage is not None
            else None
        )
        return TypedChatCompletionResponse(
            content=legacy.content,
            reasoning_content=reasoning_content,
            tool_calls=tuple(
                CompletionToolCall(
                    id=tool_call.id,
                    name=tool_call.name,
                    arguments=tool_call.arguments,
                )
                for tool_call in legacy.tool_calls
            ),
            model=legacy.model,
            usage=CompletionUsage(
                prompt_tokens=legacy.usage.get("prompt_tokens", 0),
                completion_tokens=legacy.usage.get("completion_tokens", 0),
                total_tokens=legacy.usage.get("total_tokens", 0),
                reasoning_tokens=(
                    int(getattr(details, "reasoning_tokens", 0))
                    if details is not None
                    and getattr(details, "reasoning_tokens", None) is not None
                    else None
                ),
            ),
            finish_reason=getattr(choice, "finish_reason", None),
            assurance=CompletionAssurance(
                requested_fields=summary.requested_fields,
                resolved_fields=summary.requested_fields,
                emitted_fields=summary.emitted_fields,
                capability_sources=summary.capability_sources,
                target_profile=summary.target_profile,
                litellm_version=summary.litellm_version,
            ),
        )

    def _parse_tool_arguments(
        self,
        raw_args: str,
        tool_name: str,
    ) -> dict[str, Any]:
        """Parse tool call arguments with progressive JSON repair.

        Some models (e.g. Kimi K2.5) produce malformed JSON for
        tool calls with large string parameters.  Common failures
        include truncation, unescaped control characters, and
        missing closing delimiters.

        This method tries progressively more aggressive repair
        strategies before falling back to ``{"raw": ...}``.

        Args:
            raw_args: The raw JSON string from the model.
            tool_name: Tool name for diagnostic logging.

        Returns:
            Parsed arguments dict, or ``{"raw": raw_args}`` if
            all repair strategies fail.
        """
        # Strategy 1: Direct parse
        try:
            parsed = json.loads(raw_args)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass

        # Strategy 2: Fix unescaped control characters
        # Models sometimes emit literal newlines/tabs inside
        # JSON string values instead of \\n / \\t
        try:
            cleaned = self._escape_control_chars(raw_args)
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass

        # Strategy 3: Repair truncated JSON
        # Model hit output token limit mid-argument
        repaired = self._repair_truncated_json(raw_args)
        if repaired is not None:
            try:
                parsed = json.loads(repaired)
                if isinstance(parsed, dict):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass

        # All strategies failed — fall back to raw
        logger.warning(
            "Could not parse tool '%s' arguments "
            "(len=%d). Falling back to raw wrapper.",
            tool_name,
            len(raw_args) if raw_args else 0,
        )
        return {"raw": raw_args}

    @staticmethod
    def _escape_control_chars(s: str) -> str:
        """Escape literal control characters inside JSON strings.

        Replaces unescaped newlines, carriage returns, and tabs
        that appear inside JSON string values with their escaped
        equivalents (``\\n``, ``\\r``, ``\\t``).

        Args:
            s: Raw JSON string that may contain unescaped
                control characters.

        Returns:
            JSON string with control characters properly escaped.
        """
        # Replace unescaped control chars that break json.loads
        # but only inside string values (between quotes).
        # We walk through the string tracking whether we're
        # inside a JSON string value.
        result = []
        in_string = False
        i = 0
        while i < len(s):
            ch = s[i]
            if ch == '"' and (i == 0 or s[i - 1] != "\\"):
                in_string = not in_string
                result.append(ch)
            elif in_string and ch == "\n":
                result.append("\\n")
            elif in_string and ch == "\r":
                result.append("\\r")
            elif in_string and ch == "\t":
                result.append("\\t")
            else:
                result.append(ch)
            i += 1
        return "".join(result)

    @staticmethod
    def _repair_truncated_json(s: str) -> str | None:
        """Attempt to close truncated JSON from LLM output.

        When a model hits its output token limit mid-tool-call,
        the JSON arguments string is truncated.  This method
        tries to close any open string literals and brace
        delimiters to produce parseable JSON.

        Args:
            s: Potentially truncated JSON string.

        Returns:
            Repaired JSON string, or ``None`` if the input
            doesn't look like truncated JSON.
        """
        if not s or not s.lstrip().startswith("{"):
            return None

        stripped = s.rstrip()

        # Count unmatched braces (ignoring those in strings)
        depth = 0
        in_str = False
        last_was_escape = False
        for ch in stripped:
            if last_was_escape:
                last_was_escape = False
                continue
            if ch == "\\" and in_str:
                last_was_escape = True
                continue
            if ch == '"':
                in_str = not in_str
            elif not in_str:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1

        if depth <= 0:
            # Already balanced or over-closed — not truncated
            return None

        # If we're inside an open string, close it
        if in_str:
            stripped += '"'

        # Close open braces
        stripped += "}" * depth

        return stripped
