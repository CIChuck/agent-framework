"""Public LLM behavior, exact dispatch accounting, and content-free metrics."""

import asyncio
import json
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock

import litellm
import pytest
from friday_llm import (
    ChatCompletionRequest,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    LiteLLMEmbeddingService,
    LiteLLMService,
    LLMRetryExhaustedError,
    LLMTimeoutError,
    ModelTarget,
    NamedToolChoice,
    NamedToolChoiceFunction,
    ResilienceConfig,
    TranslationConflictError,
    TransportTarget,
)
from friday_llm.pricing import CostCalculator, ModelPricing, PricingConfig
from friday_llm.telemetry import classify_error, usage_from_raw
from friday_llm.telemetry_models import ConversationContext
from friday_telemetry import TelemetryInterface

SECRET = "PRIVATE_LLM_CONTENT_SENTINEL"


class Sink(TelemetryInterface):
    def __init__(self, fail=False):
        self.events = []
        self.fail = fail

    def capture_event(self, name, data):
        if self.fail:
            raise RuntimeError(SECRET)
        self.events.append((name, dict(data)))

    def start_span(self, name, parent_id=None):
        raise AssertionError("no LLM spans")

    def end_span(self, span_id, data=None):
        raise AssertionError("no LLM spans")


def response(usage="default"):
    if usage == "default":
        usage = NS(prompt_tokens=3, completion_tokens=4, total_tokens=7,
                   completion_tokens_details=NS(reasoning_tokens=2))
    return NS(choices=[NS(message=NS(content=SECRET, reasoning_content=SECRET, tool_calls=[]),
                         finish_reason=SECRET)], usage=usage, model=SECRET, id=SECRET)


def client(sink, *, retries=0, breaker=None):
    return LiteLLMService(model_name="gpt-4", telemetry=sink, service_role="primary",
                         resilience=ResilienceConfig(max_retries=retries,
                                                     backoff_min=.1, backoff_multiplier=.1,
                                                     circuit_breaker=breaker or CircuitBreakerConfig()))


def request(**kwargs):
    return ChatCompletionRequest(messages=({"role": "user", "content": SECRET},), **kwargs)


async def complete(service, api):
    if api == "typed":
        return await service.chat_completion_request(request())
    return await service.chat_completion([{"role": "user", "content": SECRET}],
                                         conversation_context=ConversationContext(
                                             session_id=SECRET, conversation_id=SECRET,
                                             turn_id=SECRET, workflow_id=SECRET, llm_service=SECRET))


def events(sink, name):
    return [data for event, data in sink.events if event == "llm." + name]


@pytest.mark.parametrize("api", ["typed", "legacy"])
@pytest.mark.parametrize("usage,expected", [("default", "reported"), (None, "unavailable"),
    (NS(prompt_tokens=0, completion_tokens=0, total_tokens=0), "reported")])
@pytest.mark.asyncio
async def test_completion_preserves_content_while_exporting_only_reported_counts(monkeypatch, api, usage, expected):
    sink = Sink()
    service = client(sink)
    dispatch = AsyncMock(return_value=response(usage))
    monkeypatch.setattr(litellm, "acompletion", dispatch)
    result = await complete(service, api)
    assert result.content == SECRET
    assert dispatch.await_count == 1
    assert [n for n, _ in sink.events] == ["llm.request_start", "llm.attempt_finish", "llm.request_finish"]
    end = events(sink, "request_finish")[0]
    assert end["usage_state"] == expected and end["outcome"] == "success"
    assert end["attempt_count"] == 1 and end["finish_reason"] == "other"
    assert end["service_role"] == "primary"
    assert SECRET not in json.dumps(sink.events)
    if usage is None:
        assert "input_tokens" not in end and end["cost_state"] == "unavailable"
    else:
        assert end["input_tokens"] == (3 if usage == "default" else 0)
        assert end["price_source"] == "builtin_2025" and end["cost_state"] == "estimated"


@pytest.mark.parametrize("api", ["typed", "legacy"])
@pytest.mark.parametrize("exhausted", [False, True])
@pytest.mark.asyncio
async def test_successful_and_exhausted_retries_match_actual_dispatches(monkeypatch, api, exhausted):
    sink = Sink()
    service = client(sink, retries=1)
    error = litellm.RateLimitError(SECRET, model=SECRET, llm_provider="openai")
    dispatch = AsyncMock(side_effect=[error, error if exhausted else response()])
    monkeypatch.setattr(litellm, "acompletion", dispatch)
    if exhausted:
        with pytest.raises(LLMRetryExhaustedError) as raised:
            await complete(service, api)
        assert raised.value.attempts == 2 and raised.value.last_error is error
    else:
        assert (await complete(service, api)).content == SECRET
    attempts = events(sink, "attempt_finish")
    assert dispatch.await_count == 2
    assert [a["attempt_number"] for a in attempts] == [1, 2]
    assert len({a["attempt_id"] for a in attempts}) == 2
    assert len({d["request_id"] for _, d in sink.events}) == 1
    assert events(sink, "request_finish")[0]["attempt_count"] == 2
    assert events(sink, "request_finish")[0]["outcome"] == ("error" if exhausted else "success")
    assert SECRET not in json.dumps(sink.events)


@pytest.mark.parametrize("api", ["typed", "legacy"])
@pytest.mark.asyncio
async def test_circuit_denial_has_no_dispatch_and_parsing_error_keeps_successful_attempt(monkeypatch, api):
    sink = Sink()
    service = client(sink, breaker=CircuitBreakerConfig(enabled=True, failure_threshold=1))
    error = RuntimeError(SECRET)
    dispatch = AsyncMock(side_effect=error)
    monkeypatch.setattr(litellm, "acompletion", dispatch)
    with pytest.raises(RuntimeError) as first:
        await complete(service, api)
    assert first.value is error
    with pytest.raises(CircuitBreakerOpenError):
        await complete(service, api)
    assert dispatch.await_count == 1
    assert events(sink, "request_finish")[-1]["outcome"] == "blocked"
    assert events(sink, "request_finish")[-1]["attempt_count"] == 0
    service = client(sink)
    monkeypatch.setattr(litellm, "acompletion", AsyncMock(return_value=NS(choices=[], usage=None)))
    with pytest.raises(IndexError):
        await complete(service, api)
    assert events(sink, "attempt_finish")[-1]["outcome"] == "success"
    assert events(sink, "request_finish")[-1]["outcome"] == "error"


@pytest.mark.asyncio
async def test_pre_dispatch_validation_emits_zero_attempt_request(monkeypatch):
    sink = Sink()
    service = client(sink)
    dispatch = AsyncMock(return_value=response())
    monkeypatch.setattr(litellm, "acompletion", dispatch)
    service = LiteLLMService(model_name="openai/qwen3.8", telemetry=sink,
        transport_target=TransportTarget(provider="openai_compatible", dialect="openai_chat_completions", serving_engine="lm_studio"),
        model_target=ModelTarget(model_id="qwen3.8", family="qwen3_8", revision="exact"))
    bad = request(tools=({"type": "function", "function": {"name": "available", "parameters": {"type": "object"}}},),
                  tool_choice=NamedToolChoice(function=NamedToolChoiceFunction(name="missing")))
    with pytest.raises(TranslationConflictError):
        await service.chat_completion_request(bad)
    assert dispatch.await_count == 0
    assert not events(sink, "attempt_finish")
    assert events(sink, "request_finish")[0]["attempt_count"] == 0


class Stream:
    def __init__(self, chunks, error=None, close_error=None, stall=False):
        self.chunks = iter(chunks)
        self.error = error
        self.close_error = close_error
        self.stall = stall
        self.close_count = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.chunks)
        except StopIteration:
            if self.error is not None:
                raise self.error from None
            if self.stall:
                await asyncio.Event().wait()
            raise StopAsyncIteration from None

    async def aclose(self):
        self.close_count += 1
        if self.close_error is not None:
            raise self.close_error


def chunk(text=None, usage=None, finish=None, reasoning=None):
    return NS(usage=usage, choices=[NS(delta=NS(content=text, reasoning_content=reasoning),
                                     finish_reason=finish)])


def generator(service, api, *, timeout=None):
    return (service.chat_completion_events(request(timeout=timeout)) if api == "typed" else
            service.chat_completion_stream([{"role": "user", "content": SECRET}], timeout=timeout))


@pytest.mark.parametrize("api", ["typed", "legacy"])
@pytest.mark.asyncio
async def test_stream_cumulative_usage_after_finish_and_no_word_token_estimate(monkeypatch, api):
    sink = Sink()
    service = client(sink, retries=1)
    usage = NS(prompt_tokens=3, completion_tokens=4, total_tokens=7)
    stream = Stream([chunk(reasoning=SECRET), chunk(text=SECRET), chunk(finish="stop"),
                     NS(choices=[], usage=usage), NS(choices=[], usage=usage)])
    error = litellm.RateLimitError(SECRET, model=SECRET, llm_provider="openai")
    dispatch = AsyncMock(side_effect=[error, stream])
    monkeypatch.setattr(litellm, "acompletion", dispatch)
    values = [value async for value in generator(service, api)]
    assert values if api == "typed" else values == [SECRET]
    end = events(sink, "request_finish")[0]
    assert end["total_tokens"] == 7 and end["chunk_count"] == 5
    assert end["attempt_count"] == 2 and end["first_text_ms"] >= 90
    assert end["finish_reason"] == "stop" and end["outcome"] == "success"
    assert stream.close_count == 1
    assert SECRET not in json.dumps(sink.events)


@pytest.mark.parametrize("api", ["typed", "legacy"])
@pytest.mark.parametrize("outcome", ["cancelled", "error", "incomplete", "timeout"])
@pytest.mark.asyncio
async def test_stream_cancel_failure_timeout_early_close_keep_primary_and_close(monkeypatch, api, outcome):
    sink = Sink()
    service = client(sink)
    error = asyncio.CancelledError() if outcome == "cancelled" else RuntimeError(SECRET) if outcome == "error" else None
    stream = Stream([chunk(text=SECRET)], error=error, close_error=RuntimeError("close-failure"),
                    stall=outcome == "timeout")
    dispatch = AsyncMock(return_value=stream)
    monkeypatch.setattr(litellm, "acompletion", dispatch)
    values = generator(service, api, timeout=.02)
    await anext(values)
    if outcome == "incomplete":
        await values.aclose()
    else:
        expected = LLMTimeoutError if outcome == "timeout" else type(error)
        with pytest.raises(expected) as raised:
            await anext(values)
        if error is not None:
            assert raised.value is error
    end = events(sink, "request_finish")[0]
    assert end["outcome"] == ("error" if outcome == "timeout" else outcome)
    assert stream.close_count == 1 and dispatch.await_count == 1
    assert end["usage_state"] == "unavailable" and "input_tokens" not in end
    assert service._telemetry_helper.safe.snapshot().failure_count == 1


@pytest.mark.parametrize("api", ["typed", "legacy"])
@pytest.mark.asyncio
async def test_cancel_during_setup_and_backoff_is_not_success(monkeypatch, api):
    sink = Sink()
    service = client(sink, retries=1)
    monkeypatch.setattr(litellm, "acompletion", AsyncMock(side_effect=asyncio.CancelledError()))
    with pytest.raises(asyncio.CancelledError):
        await anext(generator(service, api))
    assert events(sink, "attempt_finish")[-1]["outcome"] == "cancelled"
    assert events(sink, "request_finish")[-1]["outcome"] == "cancelled"
    entered = asyncio.Event()
    async def rate_limit(**kwargs):
        entered.set()
        raise litellm.RateLimitError(SECRET, model=SECRET, llm_provider="openai")
    monkeypatch.setattr(litellm, "acompletion", rate_limit)
    task = asyncio.create_task(complete(service, api))
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert events(sink, "request_finish")[-1]["outcome"] == "cancelled"
    assert events(sink, "request_finish")[-1]["attempt_count"] == 1


@pytest.mark.parametrize("api", ["typed", "legacy"])
@pytest.mark.asyncio
async def test_failing_sink_cannot_change_success_error_or_cancellation(monkeypatch, api):
    sink = Sink(fail=True)
    service = client(sink)
    monkeypatch.setattr(litellm, "acompletion", AsyncMock(return_value=response()))
    assert (await complete(service, api)).content == SECRET
    class NoStringError(Exception):
        def __str__(self):
            raise AssertionError("telemetry must not stringify errors")
    error = NoStringError()
    monkeypatch.setattr(litellm, "acompletion", AsyncMock(side_effect=error))
    with pytest.raises(NoStringError) as raised:
        await complete(service, api)
    assert raised.value is error and classify_error(error) == "unknown"
    monkeypatch.setattr(litellm, "acompletion", AsyncMock(side_effect=asyncio.CancelledError()))
    with pytest.raises(asyncio.CancelledError):
        await complete(service, api)
    snapshot = service._telemetry_helper.safe.snapshot()
    assert snapshot.failure_count == 9 and SECRET not in repr(snapshot)


@pytest.mark.asyncio
async def test_concurrent_requests_have_unique_ids_and_preserved_responses(monkeypatch):
    sink = Sink()
    service = client(sink)
    async def dispatch(**kwargs):
        await asyncio.sleep(0)
        return response()
    monkeypatch.setattr(litellm, "acompletion", dispatch)
    results = await asyncio.gather(*(complete(service, "typed") for _ in range(8)))
    assert all(result.content == SECRET for result in results)
    starts = events(sink, "request_start")
    ends = events(sink, "request_finish")
    assert len({e["request_id"] for e in starts}) == 8
    assert {e["request_id"] for e in starts} == {e["request_id"] for e in ends}
    assert len({e["model_ref"] for e in starts}) == 1
    assert all(e["attempt_count"] == 1 for e in ends)


@pytest.mark.asyncio
async def test_embedding_batches_cache_empty_partial_failure_and_usage_presence(monkeypatch):
    sink = Sink()
    service = LiteLLMEmbeddingService(telemetry=sink, batch_size=2,
                                      resilience=ResilienceConfig(max_retries=0))
    async def dispatch(**kwargs):
        return NS(data=[{"embedding": [float(i)]} for i, _ in enumerate(kwargs["input"])],
                  usage=NS(prompt_tokens=len(kwargs["input"]), total_tokens=len(kwargs["input"])))
    mock = AsyncMock(side_effect=dispatch)
    monkeypatch.setattr(litellm, "aembedding", mock)
    assert len(await service.embed_documents([SECRET] * 3)) == 3
    end = events(sink, "request_finish")[-1]
    assert end["input_tokens"] == 3 and end["batch_count"] == 2 and end["attempt_count"] == 2
    assert end["cost_state"] == "estimated"
    vector = await service.embed_query(SECRET)
    assert await service.embed_query(SECRET) is vector
    assert events(sink, "request_finish")[-1]["outcome"] == "cache_hit"
    assert events(sink, "request_finish")[-1]["attempt_count"] == 0
    assert await service.embed_documents([]) == []
    assert events(sink, "request_finish")[-1]["outcome"] == "empty_input"
    monkeypatch.setattr(litellm, "aembedding", AsyncMock(side_effect=[
        NS(data=[{"embedding": [1.0]}, {"embedding": [2.0]}], usage=NS(prompt_tokens=2, total_tokens=2)),
        RuntimeError(SECRET),
    ]))
    with pytest.raises(RuntimeError):
        await service.embed_documents([SECRET] * 3)
    end = events(sink, "request_finish")[-1]
    assert end["input_tokens"] == 2 and end["usage_coverage"] == "partial"
    assert end["cost_state"] == "unavailable" and end["attempt_count"] == 2
    monkeypatch.setattr(litellm, "aembedding", AsyncMock(return_value=NS(data=[{"embedding": [0.0]}], usage=None)))
    await service.embed_documents([SECRET])
    assert events(sink, "request_finish")[-1]["usage_state"] == "unavailable"
    assert "input_tokens" not in events(sink, "request_finish")[-1]
    assert SECRET not in json.dumps(sink.events)


@pytest.mark.parametrize("raw", [NS(prompt_tokens=True), NS(prompt_tokens=-1),
    NS(prompt_tokens=2**63), NS(prompt_tokens=float("nan")), NS(prompt_tokens=1.0),
    NS(prompt_tokens=3, completion_tokens=4, total_tokens=100)])
def test_invalid_usage_has_no_fabricated_count(raw):
    result = usage_from_raw(raw)
    assert result.usage_state == "invalid" and result.input_tokens is None


@pytest.mark.parametrize("model,source,match", [
    ("gpt-4", "builtin_2025", "exact"), ("openai/gpt-4", "builtin_2025", "base_model"),
    ("gpt-4-0613", "builtin_2025", "prefix"), ("ollama/local", "builtin_2025", "provider"),
    (SECRET, "fallback", "fallback"),
])
def test_price_provenance_and_legacy_numeric_api_are_truthful(model, source, match):
    calculator = CostCalculator()
    old = calculator.calculate(model, 1000, 500)
    estimate = calculator.estimate_with_provenance(model, 1000, 500)
    assert estimate.price_source == source and estimate.price_match == match
    assert estimate.total_cost_usd == old.total_cost
    assert SECRET not in estimate.model_dump_json()


def test_custom_supplied_disabled_unknown_invalid_prices_have_explicit_disposition():
    custom = CostCalculator(PricingConfig(custom_pricing={SECRET: {"input_cost_per_1k": .2, "output_cost_per_1k": .4}}))
    assert custom.estimate_with_provenance(SECRET, 1, 1).price_source == "custom_config"
    supplied = CostCalculator(pricing_table={SECRET: ModelPricing(.3, .4)})
    assert supplied.estimate_with_provenance(SECRET, 1, 1).price_source == "supplied_table"
    assert CostCalculator(PricingConfig(enabled=False)).estimate_with_provenance("gpt-4", 1).cost_state == "unavailable"
    assert CostCalculator(PricingConfig(estimate_unknown=False)).estimate_with_provenance(SECRET, 1).cost_state == "unavailable"
    invalid = CostCalculator(pricing_table={SECRET: ModelPricing(float("inf"), .4)})
    assert invalid.estimate_with_provenance(SECRET, 1).cost_state == "invalid"


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["typed", "legacy"])
async def test_uniterated_and_reasoning_tool_only_streams_have_no_first_text(monkeypatch, api):
    sink = Sink()
    service = client(sink)
    tool = NS(choices=[NS(delta=NS(content=None, reasoning_content=None,
        tool_calls=[NS(index=0, id=SECRET, function=NS(name=SECRET, arguments='{"secret": "value"}'))]),
        finish_reason=None)], usage=None)
    stream = Stream([chunk(reasoning=SECRET), tool, chunk(finish="tool_calls")])
    dispatch = AsyncMock(return_value=stream)
    monkeypatch.setattr(litellm, "acompletion", dispatch)
    values = generator(service, api)
    assert sink.events == [] and dispatch.await_count == 0
    result = [item async for item in values]
    assert result if api == "typed" else result == []
    end = events(sink, "request_finish")[0]
    assert "first_text_ms" not in end and "total_tokens" not in end
    assert end["chunk_count"] == 3 and end["finish_reason"] == "tool_calls"
    assert stream.close_count == 1 and SECRET not in json.dumps(sink.events)


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["typed", "legacy"])
@pytest.mark.parametrize("last", [NS(prompt_tokens=2, completion_tokens=4, total_tokens=6),
    NS(prompt_tokens=3, completion_tokens=4, total_tokens=99)])
async def test_final_decreasing_or_contradictory_stream_usage_remains_invalid(monkeypatch, api, last):
    sink = Sink()
    service = client(sink)
    stream = Stream([chunk(text=SECRET), chunk(finish="stop"),
        NS(choices=[], usage=NS(prompt_tokens=3, completion_tokens=4, total_tokens=7)),
        NS(choices=[], usage=last)])
    monkeypatch.setattr(litellm, "acompletion", AsyncMock(return_value=stream))
    [item async for item in generator(service, api)]
    end = events(sink, "request_finish")[0]
    assert end["outcome"] == "success" and end["usage_state"] == "invalid"
    assert end["cost_state"] == "unavailable" and "total_tokens" not in end


@pytest.mark.asyncio
async def test_nested_requests_keep_separate_ids_and_dispatch_counts(monkeypatch):
    sink = Sink()
    outer, inner = client(sink), client(sink)
    entered = False
    async def dispatch(**kwargs):
        nonlocal entered
        if not entered:
            entered = True
            assert (await complete(inner, "typed")).content == SECRET
        return response()
    monkeypatch.setattr(litellm, "acompletion", dispatch)
    await complete(outer, "typed")
    starts = events(sink, "request_start")
    ends = events(sink, "request_finish")
    assert len(starts) == len(ends) == 2
    assert starts[0]["request_id"] == ends[1]["request_id"]
    assert starts[1]["request_id"] == ends[0]["request_id"]
    assert all(e["attempt_count"] == 1 for e in ends)


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["query", "documents"])
async def test_embedding_retry_and_cancel_retain_batch_identity(monkeypatch, api):
    sink = Sink()
    service = LiteLLMEmbeddingService(telemetry=sink, resilience=ResilienceConfig(
        max_retries=1, backoff_min=.1, backoff_multiplier=.1))
    error = litellm.RateLimitError(SECRET, model=SECRET, llm_provider="openai")
    raw = NS(data=[{"embedding": [1.0]}], usage=NS(prompt_tokens=0, total_tokens=0))
    dispatch = AsyncMock(side_effect=[error, raw])
    monkeypatch.setattr(litellm, "aembedding", dispatch)
    call = service.embed_query if api == "query" else service.embed_documents
    result = await call(SECRET if api == "query" else [SECRET])
    assert result and dispatch.await_count == 2
    attempts = events(sink, "attempt_finish")
    batch = events(sink, "batch_finish")[0]
    assert all(a["batch_id"] == batch["batch_id"] for a in attempts)
    assert batch["attempt_count"] == 2
    assert events(sink, "request_finish")[-1]["input_tokens"] == 0
    monkeypatch.setattr(litellm, "aembedding", AsyncMock(side_effect=asyncio.CancelledError()))
    with pytest.raises(asyncio.CancelledError):
        await call("different" if api == "query" else [SECRET])
    assert events(sink, "attempt_finish")[-1]["outcome"] == "cancelled"
    assert events(sink, "batch_finish")[-1]["outcome"] == "cancelled"
    assert events(sink, "request_finish")[-1]["outcome"] == "cancelled"


@pytest.mark.asyncio
async def test_embedding_missing_batch_component_is_not_a_complete_total(monkeypatch):
    sink = Sink()
    service = LiteLLMEmbeddingService(telemetry=sink, batch_size=1,
                                      resilience=ResilienceConfig(max_retries=0))
    monkeypatch.setattr(litellm, "aembedding", AsyncMock(side_effect=[
        NS(data=[{"embedding": [1.0]}], usage=NS(prompt_tokens=3, total_tokens=3)),
        NS(data=[{"embedding": [2.0]}], usage=None)]))
    assert await service.embed_documents([SECRET, SECRET]) == [[1.0], [2.0]]
    end = events(sink, "request_finish")[-1]
    assert end["usage_coverage"] == "partial" and end["cost_state"] == "unavailable"
    assert "input_tokens" not in end and "total_tokens" not in end
    assert events(sink, "batch_finish")[0]["input_tokens"] == 3
    assert "input_tokens" not in events(sink, "batch_finish")[1]
