"""Accounting and sink isolation without an SDK, provider client or transport."""

import asyncio
import json

import pytest
from friday_telemetry import TelemetryInterface
from friday_telemetry.helpers.safe_llm import SafeLLMTelemetry
from friday_telemetry.models.llm_events import CostMetrics, UsageMetrics


class Sink(TelemetryInterface):
    def __init__(self, fail=False):
        self.events = []
        self.fail = fail

    def capture_event(self, event_name, data):
        if self.fail:
            raise RuntimeError("private-sink-error")
        self.events.append((event_name, dict(data)))

    def start_span(self, name, parent_id=None):
        raise AssertionError("LLM metrics must not hold an ambient span")

    def end_span(self, span_id, data=None):
        raise AssertionError("LLM metrics have no span lifecycle")


def request(helper, api="typed_completion", category="unknown"):
    return helper.request(api, classify=lambda error: category, estimate=lambda usage: CostMetrics())


def test_request_retry_and_batch_ids_are_independent_and_exact():
    sink = Sink()
    helper = SafeLLMTelemetry(sink)
    with request(helper, "embedding_documents") as tracker:
        for i in range(2):
            with tracker.batch(1) as batch:
                if i == 0:
                    with pytest.raises(RuntimeError), tracker.attempt(batch):
                        raise RuntimeError("private-provider-error")
                with tracker.attempt(batch):
                    pass
                batch.usage = UsageMetrics(usage_state="reported", input_tokens=3, total_tokens=3)
    attempts = [d for n, d in sink.events if n == "llm.attempt_finish"]
    batches = [d for n, d in sink.events if n == "llm.batch_finish"]
    end = sink.events[-1][1]
    assert [d["attempt_number"] for d in attempts] == [1, 2, 3]
    assert len({d["attempt_id"] for d in attempts}) == 3
    assert attempts[0]["batch_id"] == attempts[1]["batch_id"] == batches[0]["batch_id"]
    assert attempts[2]["batch_id"] == batches[1]["batch_id"] != batches[0]["batch_id"]
    assert [d["attempt_count"] for d in batches] == [2, 1]
    assert end["input_tokens"] == 6 and end["attempt_count"] == 3 and end["batch_count"] == 2
    assert end["usage_coverage"] == "complete"
    assert "private-" not in json.dumps(sink.events)


@pytest.mark.parametrize("exception,outcome", [
    (RuntimeError("secret"), "error"), (asyncio.CancelledError(), "cancelled"),
    (GeneratorExit(), "incomplete"),
])
def test_finalization_does_not_replace_primary_baseexception(exception, outcome):
    sink = Sink()
    helper = SafeLLMTelemetry(sink)
    with pytest.raises(type(exception)) as raised, request(helper) as tracker:
        raise exception
    assert raised.value is exception
    assert sink.events[-1][1]["outcome"] == outcome
    before = len(sink.events)
    tracker.finish()
    assert len(sink.events) == before


def test_sink_failure_is_bounded_without_raw_payload_or_exception_retention():
    helper = SafeLLMTelemetry(Sink(fail=True))
    for _ in range(100):
        with request(helper) as tracker, tracker.attempt():
            pass
    snapshot = helper.snapshot()
    assert snapshot.failure_count == 300
    assert len(snapshot.records) == 256 and snapshot.dropped_count == 44
    assert all(record.reason == "sink_failed" for record in snapshot.records)
    assert "private-sink" not in repr(snapshot)


def test_no_dispatch_outcomes_have_zero_attempts_and_no_invented_usage():
    sink = Sink()
    helper = SafeLLMTelemetry(sink)
    for outcome in ["cache_hit", "empty_input"]:
        with request(helper, "embedding_query") as tracker:
            tracker.outcome = outcome
    with pytest.raises(RuntimeError), request(helper, category="circuit_open"):
        raise RuntimeError("private-open-circuit")
    ends = [d for n, d in sink.events if n == "llm.request_finish"]
    assert [d["outcome"] for d in ends] == ["cache_hit", "empty_input", "blocked"]
    assert all(d["attempt_count"] == 0 and "input_tokens" not in d for d in ends)


def test_final_cumulative_stream_usage_is_not_summed_and_invalid_cannot_fall_back():
    sink = Sink()
    helper = SafeLLMTelemetry(sink)
    with request(helper, "typed_stream") as tracker:
        for _ in range(3):
            tracker.record_chunk(UsageMetrics(usage_state="reported", input_tokens=2,
                                             output_tokens=4, total_tokens=6))
        tracker.text_seen()
    assert sink.events[-1][1]["total_tokens"] == 6
    assert sink.events[-1][1]["chunk_count"] == 3
    with request(helper, "typed_stream") as tracker:
        tracker.record_chunk(UsageMetrics(usage_state="reported", input_tokens=2))
        tracker.record_chunk(UsageMetrics(usage_state="invalid"))
    assert sink.events[-1][1]["usage_state"] == "invalid"
    assert "input_tokens" not in sink.events[-1][1]
