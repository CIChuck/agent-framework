"""Capability lattice, provenance, and operator refinement tests."""

import pytest
from friday_llm import (
    CapabilityConflictError,
    CapabilityEntry,
    CapabilityState,
    ControlCapability,
    ModelTarget,
    OperatorCapabilityDeclaration,
    TransportTarget,
)
from friday_llm.capabilities import _compose_control, compose_capabilities
from friday_llm.targets import ExecutionTarget
from pydantic import ValidationError


def _target() -> ExecutionTarget:
    return ExecutionTarget(
        transport=TransportTarget(
            provider="openai_compatible",
            dialect="openai_chat_completions",
            serving_engine="lm_studio",
        ),
        model=ModelTarget(
            model_id="qwen3.8-27b-mlx",
            family="qwen3_8",
            revision="test-revision",
        ),
    )


def _declaration(
    name: str,
    capability: ControlCapability,
) -> OperatorCapabilityDeclaration:
    return OperatorCapabilityDeclaration(
        source="test-operator",
        version="1",
        controls=(CapabilityEntry(name=name, capability=capability),),
    )


def test_operator_can_refine_an_absent_unknown_control() -> None:
    capabilities = compose_capabilities(
        _target(),
        _declaration(
            "operator.custom",
            ControlCapability(state=CapabilityState.SUPPORTED),
        ),
    )

    capability = capabilities.for_control("operator.custom")
    assert capability.state is CapabilityState.SUPPORTED
    assert capability.sources == ("operator:test-operator@1",)


def test_operator_cannot_override_authoritative_unsupported() -> None:
    capabilities = compose_capabilities(
        _target(),
        _declaration(
            "reasoning.budget_tokens",
            ControlCapability(state=CapabilityState.SUPPORTED),
        ),
    )

    assert (
        capabilities.for_control("reasoning.budget_tokens").state
        is CapabilityState.UNSUPPORTED
    )


def test_operator_cannot_widen_builtin_constraints() -> None:
    with pytest.raises(CapabilityConflictError):
        compose_capabilities(
            _target(),
            _declaration(
                "sampling.temperature",
                ControlCapability(
                    state=CapabilityState.SUPPORTED,
                    minimum=0.0,
                    maximum=3.0,
                ),
            ),
        )


def test_operator_can_narrow_builtin_constraints() -> None:
    capabilities = compose_capabilities(
        _target(),
        _declaration(
            "sampling.temperature",
            ControlCapability(
                state=CapabilityState.SUPPORTED,
                minimum=0.2,
                maximum=1.0,
            ),
        ),
    )
    capability = capabilities.for_control("sampling.temperature")
    assert capability.minimum == 0.2
    assert capability.maximum == 1.0


def test_empty_constraint_intersection_is_a_conflict() -> None:
    with pytest.raises(CapabilityConflictError):
        _compose_control(
            "synthetic",
            [
                ControlCapability(
                    state=CapabilityState.SUPPORTED,
                    allowed_values=("a",),
                    sources=("one@1",),
                ),
                ControlCapability(
                    state=CapabilityState.SUPPORTED,
                    allowed_values=("b",),
                    sources=("two@1",),
                ),
            ],
        )


def test_composed_capabilities_are_deeply_immutable() -> None:
    capabilities = compose_capabilities(_target())

    with pytest.raises(ValidationError):
        capabilities.controls[0].capability.maximum = 99
