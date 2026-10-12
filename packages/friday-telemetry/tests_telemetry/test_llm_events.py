"""Closed runtime schema: legitimate scalars and rejected forged/unknown payloads."""

import pytest
from friday_telemetry.models.llm_events import LLMEvent, RequestStart
from pydantic import ValidationError


def identity():
    return dict(schema_version=1, request_id="a" * 32, operation="chat",
                api="typed_completion", service_role="primary", model_ref="b" * 32)


def finish():
    return dict(identity(), name="llm.request_finish", outcome="success", attempt_count=1,
                batch_count=0, duration_ms=1.25, usage_state="reported", usage_coverage="complete",
                input_tokens=0, output_tokens=0, total_tokens=0, cost_state="estimated",
                input_cost_usd=0.0, output_cost_usd=0.0, total_cost_usd=0.0,
                currency="USD", price_source="builtin_2025", price_match="exact",
                pricing_ref="c" * 16)


@pytest.mark.parametrize("name", ["llm.request_start", "llm.request_finish"])
def test_closed_serialization_keeps_reported_zero_and_finite_scalars(name):
    data = finish() if name.endswith("finish") else dict(identity(), name=name)
    event = LLMEvent.model_validate(data)
    values = event.attributes()
    assert "name" not in values
    assert len(values) <= 32
    assert all(value is not None for value in values.values())
    if name.endswith("finish"):
        assert values["input_tokens"] == 0
        assert values["total_cost_usd"] == 0.0
        assert values["duration_ms"] == 1.25
    with pytest.raises(ValidationError):
        event.root.request_id = "d" * 32


@pytest.mark.parametrize("patch", [
    {"name": "llm.unknown"}, {"schema_version": True}, {"schema_version": 2},
    {"model_ref": "private-model"}, {"request_id": "A" * 32},
    {"session_ref": "user-id"}, {"api": "embedding_query"}, {"service_role": "private-role"},
    {"error_message": "secret"}, {"prompt": {"text": "secret"}},
    {"duration_ms": float("nan")}, {"duration_ms": float("inf")}, {"duration_ms": -1},
    {"input_tokens": True}, {"input_tokens": -1}, {"input_tokens": 2**63},
    {"input_tokens": 1.0}, {"total_tokens": 1}, {"reasoning_tokens": 1},
    {"cost_state": "unavailable"}, {"price_source": "live-billing"},
    {"total_cost_usd": float("inf")}, {"outcome": "error"}, {"usage_coverage": "partial"},
])
def test_forged_or_content_payload_is_rejected(patch):
    with pytest.raises(ValidationError):
        LLMEvent.model_validate(finish() | patch)


def test_attempt_requires_paired_batch_and_real_dispatch_ordinal():
    data = dict(identity(), name="llm.attempt_finish", attempt_id="c" * 32,
                attempt_number=1, outcome="success", duration_ms=0.0)
    assert LLMEvent.model_validate(data).root.attempt_number == 1
    for patch in [{"attempt_number": 0}, {"batch_id": "d" * 32}, {"batch_number": 1}]:
        with pytest.raises(ValidationError):
            LLMEvent.model_validate(data | patch)


def test_unavailable_is_absence_and_batch_rejects_output_counts():
    data = dict(identity(), name="llm.request_finish", outcome="error", attempt_count=0,
                batch_count=0, duration_ms=0.0, usage_state="unavailable",
                usage_coverage="none", cost_state="unavailable")
    assert "input_tokens" not in LLMEvent.model_validate(data).attributes()
    with pytest.raises(ValidationError):
        LLMEvent.model_validate(data | {"input_tokens": 0})
    batch = dict(identity(), operation="embedding", api="embedding_documents",
                 name="llm.batch_finish", batch_id="c" * 32, batch_number=1,
                 outcome="success", attempt_count=1, item_count=2, duration_ms=0.0,
                 usage_state="reported", input_tokens=3, total_tokens=3)
    assert LLMEvent.model_validate(batch).root.item_count == 2
    with pytest.raises(ValidationError):
        LLMEvent.model_validate(batch | {"output_tokens": 0})


def test_model_construct_cannot_bypass_runtime_schema():
    forged = RequestStart.model_construct(**(identity() | {"service_role": "private-content"}))
    with pytest.raises(ValidationError):
        LLMEvent.model_validate(forged)
