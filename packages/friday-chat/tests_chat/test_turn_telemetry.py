import asyncio
from uuid import uuid4

import pytest
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import (
    FakeChatModel,
    build_runtime,
)
from friday_chat.tools.selection import ToolRejectionReason, ToolSelectionError
from friday_chat.turns.models import ChatModelResponse, ToolCallRequest
from friday_chat.turns.processor import (
    TurnBudgetError,
    TurnCircuitBreakerOpenError,
    TurnPersistenceError,
    TurnProcessor,
    TurnRetryExhaustedError,
    TurnTimeoutError,
)
from friday_telemetry.models.llm_events import RequestStart


def runtime(*, tools=False, enabled=True):
    return build_runtime(FridayChatConfig.model_validate({"llm": {"model": "fake/test", "timeout_seconds": 0.01},
        "tools": {"enabled": tools}, "telemetry": {"enabled": enabled},
        "transcript": {"capture_raw_prompts": True}}))


def events(r, name):
    return [dict(e.attributes) for e in r.telemetry.snapshot().events if e.name == "execution." + name]


@pytest.mark.asyncio
@pytest.mark.parametrize("streaming", [False, True])
async def test_whole_turn_links_and_persistence(streaming):
    r = runtime()
    class Model(FakeChatModel):
        async def complete(self, messages, *, tools=()):
            event = RequestStart(request_id=uuid4().hex, model_ref=uuid4().hex,
                                 operation="chat", api="legacy_completion", service_role="primary")
            r.telemetry.capture_event(event.name, event.model_dump(exclude={"name"}, exclude_none=True))
            return await super().complete(messages, tools=tools)
    r.chat_llm = Model("fake")
    chunks = []
    async def capture(chunk):
        chunks.append(chunk)
    p = TurnProcessor(r)
    result = await p.process_streaming("PRIVATE_PROMPT", on_chunk=capture) if streaming else await p.process("PRIVATE_PROMPT")
    start, = events(r, "turn_start")
    finish, = events(r, "turn_finish")
    link, = events(r, "llm_link")
    assert finish["outcome"] == "succeeded" and finish["persistence"] == "completed"
    assert start["turn_ref"] == finish["turn_ref"] == link["turn_ref"] == result.correlation_context.turn_ref
    assert link["operation_ref"] in {e["operation_ref"] for e in events(r, "operation_start")}
    assert r.telemetry.correlation.current() is None and not r.telemetry._spans
    assert "PRIVATE_PROMPT" not in repr(r.telemetry.snapshot())
    if streaming:
        assert "".join(chunks) == result.assistant_message


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["retrieve", "model", "record_turn", "record_context_log", "record_interaction", "speech"])
@pytest.mark.parametrize("cancel", [False, True])
async def test_failures_at_each_boundary_preserve_primary(stage, cancel):
    r = runtime()
    class Unprintable(RuntimeError):
        def __str__(self):
            raise AssertionError("must not stringify")
    error = asyncio.CancelledError() if cancel else Unprintable()
    async def fail(*args, **kwargs):
        raise error
    if stage == "retrieve":
        r.memory.retrieve = fail
    elif stage == "model":
        r.chat_llm.complete = fail
    elif stage == "speech":
        r.speech.speak = fail
    else:
        setattr(r.transcript, stage, fail)
    expected = asyncio.CancelledError if cancel else TurnRetryExhaustedError if stage == "model" else TurnPersistenceError if stage.startswith("record_") else Unprintable
    with pytest.raises(expected) as caught:
        await TurnProcessor(r).process("PRIVATE")
    assert caught.value is error or caught.value.__cause__ is error
    terminal, = events(r, "turn_finish")
    assert terminal["outcome"] == ("cancelled" if cancel else "failed")
    assert terminal["persistence"] == ("completed" if stage == "speech" else "not_started" if stage in {"retrieve", "model"} else "cancelled" if cancel else "failed")
    assert r.telemetry.correlation.current() is None and not r.telemetry._spans
    assert not any(e["outcome"] == "succeeded" for e in events(r, "turn_finish"))


@pytest.mark.asyncio
async def test_block_timeout_callback_and_disabled():
    r = runtime()
    with pytest.raises(TurnCircuitBreakerOpenError):
        await TurnProcessor(r, circuit_breaker_open=True).process("safe")
    assert events(r, "turn_finish")[0]["outcome"] == "blocked"
    r = runtime()
    r.chat_llm.delay_seconds = 0.1
    with pytest.raises(TurnTimeoutError):
        await TurnProcessor(r).process("safe")
    assert events(r, "turn_finish")[0]["reason"] == "timeout"
    r = runtime()
    async def bad_chunk(chunk):
        raise RuntimeError("PRIVATE_CALLBACK")
    with pytest.raises(RuntimeError):
        await TurnProcessor(r).process_streaming("safe", on_chunk=bad_chunk)
    assert events(r, "turn_finish")[0]["outcome"] == "failed"
    disabled = runtime(enabled=False)
    result = await TurnProcessor(disabled).process("safe")
    assert result.correlation_context is None and not events(disabled, "turn_start")


@pytest.mark.asyncio
async def test_native_followup_reasoning_and_concurrent_turns():
    r = runtime(tools=True)
    r.chat_llm = FakeChatModel("fake", responses=[ChatModelResponse(
        tool_calls=(ToolCallRequest("echo", {"text": "safe"}, "RAW_CALL"),), reasoning_content="PRIVATE_REASONING"),
        ChatModelResponse.from_text("done")])
    await TurnProcessor(r).process("echo")
    reason, = events(r, "reasoning_history")
    assert reason["present"] and reason["preserved"] and reason["eligible"]
    assert events(r, "turn_finish")[0]["completed_tools"] == 1
    assert "PRIVATE_REASONING" not in repr(r.telemetry.snapshot())
    r = runtime()
    r.chat_llm.delay_seconds = 0.001
    await asyncio.gather(TurnProcessor(r).process("one"), TurnProcessor(r).process("two"))
    refs = {e["turn_ref"] for e in events(r, "turn_finish")}
    assert len(refs) == 2
    assert {e["turn_ref"] for e in events(r, "operation_finish")} == refs
    assert not r.telemetry._spans


@pytest.mark.asyncio
async def test_public_iterator_holds_no_scope_at_yield():
    r = runtime()
    iterator = TurnProcessor(r).stream_process("safe")
    await anext(iterator)
    assert r.telemetry.correlation.current() is None and not r.telemetry._spans
    await iterator.aclose()


@pytest.mark.asyncio
async def test_selection_block_and_retry_attempt_layers():
    r = runtime(tools=True)
    def reject(message):
        raise ToolSelectionError(ToolRejectionReason.UNKNOWN_TOOL, ("PRIVATE_TOOL",), "PRIVATE_ERROR")
    r.tool_selection.select_for_turn = reject
    with pytest.raises(TurnBudgetError):
        await TurnProcessor(r).process("private")
    assert events(r, "turn_finish")[0]["outcome"] == "blocked"
    assert not events(r, "operation_start") and not r.chat_llm.calls
    assert "PRIVATE_TOOL" not in repr(r.telemetry.snapshot())
    r = runtime()
    r.chat_llm.failures = [RuntimeError("private")]
    await TurnProcessor(r).process("safe")
    calls = [e for e in events(r, "operation_finish") if e["operation_kind"] == "model_call"]
    assert [e["outcome"] for e in calls] == ["failed", "succeeded"]


class RetainedStream:
    def __init__(self, values, cleanup=None, primary=None):
        self.values = iter(values)
        self.cleanup = cleanup
        self.primary = primary
        self.close_attempts = 0
        self.closed = False
    def __aiter__(self):
        return self
    async def __anext__(self):
        if self.primary is not None:
            raise self.primary
        try:
            return next(self.values)
        except StopIteration:
            raise StopAsyncIteration from None
    async def aclose(self):
        self.close_attempts += 1
        await asyncio.sleep(0)
        self.closed = True
        if self.cleanup is not None:
            raise self.cleanup


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["direct", "legacy", "typed"])
@pytest.mark.parametrize("failure", ["normal", "callback", "callback_cancel", "model_cancel"])
@pytest.mark.parametrize("cleanup", ["normal", "error", "cancel"])
async def test_retained_actual_stream_cleanup_before_terminal_and_primary_identity(path, failure, cleanup):
    from friday_chat.adapters import FrameworkChatModel
    from friday_chat.config import LegacyLLMExecutionConfig
    from friday_llm import TextDeltaEvent
    r = runtime()
    primary = asyncio.CancelledError() if failure in {"callback_cancel", "model_cancel"} else RuntimeError("PRIVATE_PRIMARY")
    cleanup_error = RuntimeError("PRIVATE_CLEANUP") if cleanup == "error" else asyncio.CancelledError() if cleanup == "cancel" else None
    upstream = RetainedStream([TextDeltaEvent(text="first"), TextDeltaEvent(text="second")] if path == "typed" else ["first", "second"],
                              cleanup_error, primary if failure == "model_cancel" else None)
    class Service:
        def chat_completion_stream(self, **kwargs):
            return upstream
        def chat_completion_events(self, request):
            return upstream
    if path == "direct":
        class Model:
            def stream_complete(self, *args, **kwargs):
                return upstream
        r.chat_llm = Model()
    else:
        cfg = FridayChatConfig.model_validate({"llm": {"model": "fake/test", "transport_target": {"provider": "openai_compatible", "dialect": "openai_chat_completions", "serving_engine": "lm_studio"}, "model_target": {"model_id": "fake/test", "family": "qwen3_8", "revision": "fake"}}})
        execution = LegacyLLMExecutionConfig(0.0, None, None) if path == "legacy" else cfg.llm.resolve_execution()
        r.chat_llm = FrameworkChatModel(Service(), cfg, execution)
    chunks = []
    async def capture(chunk):
        chunks.append(chunk)
        if failure.startswith("callback"):
            raise primary
    expected = primary if failure != "normal" else cleanup_error
    if expected is None:
        result = await TurnProcessor(r).process_streaming("PRIVATE", on_chunk=capture)
        assert result.assistant_message == "firstsecond" and chunks == ["first", "second"]
    else:
        with pytest.raises(type(expected)) as caught:
            await TurnProcessor(r).process_streaming("PRIVATE", on_chunk=capture)
        assert caught.value is expected
    assert upstream.close_attempts == 1 and upstream.closed
    terminal, = events(r, "turn_finish")
    assert terminal["outcome"] == ("succeeded" if expected is None else "cancelled" if isinstance(expected, asyncio.CancelledError) else "failed")
    assert not r.telemetry._spans and r.telemetry.correlation.current() is None
    assert "PRIVATE" not in repr(r.telemetry.snapshot())


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["legacy", "typed"])
@pytest.mark.parametrize("cleanup", [None, "error", "cancel"])
async def test_public_adapter_early_close_awaits_retained_upstream(path, cleanup):
    from friday_chat.adapters import FrameworkChatModel
    from friday_chat.config import LegacyLLMExecutionConfig
    from friday_llm import TextDeltaEvent
    cfg = FridayChatConfig.model_validate({"llm": {"model": "fake/test", "transport_target": {"provider": "openai_compatible", "dialect": "openai_chat_completions", "serving_engine": "lm_studio"}, "model_target": {"model_id": "fake/test", "family": "qwen3_8", "revision": "fake"}}})
    upstream = RetainedStream([TextDeltaEvent(text="first"), TextDeltaEvent(text="second")] if path == "typed" else ["first", "second"],
                              RuntimeError("PRIVATE") if cleanup == "error" else asyncio.CancelledError() if cleanup == "cancel" else None)
    class Service:
        def chat_completion_stream(self, **kwargs):
            return upstream
        def chat_completion_events(self, request):
            return upstream
    model = FrameworkChatModel(Service(), cfg, LegacyLLMExecutionConfig(0.0, None, None) if path == "legacy" else cfg.llm.resolve_execution())
    iterator = model.stream_complete([{"role": "user", "content": "safe"}])
    assert await anext(iterator) == "first"
    await iterator.aclose()  # GeneratorExit remains primary if cleanup also fails.
    assert upstream.close_attempts == 1 and upstream.closed
