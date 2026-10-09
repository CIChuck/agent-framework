import pytest
from friday_telemetry.models.execution import (
    ExecutionEvent,
    OperationFinish,
    TurnFinish,
)
from pydantic import ValidationError

IDENTITY = {"session_ref": "a" * 16, "turn_ref": "b" * 32, "operation_ref": "c" * 32}


@pytest.mark.parametrize("field,value", [
    ("duration_ms", float("nan")), ("duration_ms", float("inf")),
    ("duration_ms", -1.0), ("count", True), ("count", -1), ("count", 2**63),
    ("operation_ref", "RAW_ID"), ("session_ref", "private"),
    ("outcome", "private_error"), ("operation_kind", "selection"),
    ("reason", "raw exception"), ("unknown", "private"),
])
def test_bad_scalar_rejected(field, value):
    data = {**IDENTITY, "operation_kind": "native_tool", "outcome": "succeeded",
            "duration_ms": 0.0, "count": 0, "count_kind": "calls", field: value}
    with pytest.raises(ValidationError):
        OperationFinish.model_validate(data)


def test_forged_instance_revalidated():
    forged = OperationFinish.model_construct(**IDENTITY, operation_kind="native_tool",
                                           outcome="succeeded", duration_ms=float("nan"))
    with pytest.raises(ValidationError):
        ExecutionEvent.model_validate(forged)


def test_zero_and_optional_presence():
    event = OperationFinish(**IDENTITY, operation_kind="native_tool", outcome="succeeded",
                            duration_ms=0.0, count=0, count_kind="calls")
    assert event.attributes()["count"] == 0
    assert "reason" not in event.attributes()
    assert len(event.attributes()) <= 32
    with pytest.raises(ValidationError):
        OperationFinish(**IDENTITY, operation_kind="native_tool", outcome="succeeded", duration_ms=0.0, count=0)
    with pytest.raises(ValidationError):
        TurnFinish(**IDENTITY, outcome="succeeded", duration_ms=0.0, persistence="completed")


def test_parent_cycle_rejected():
    with pytest.raises(ValidationError):
        OperationFinish(**IDENTITY, parent_operation_ref=IDENTITY["operation_ref"],
                        operation_kind="native_tool", outcome="succeeded", duration_ms=0.0)
