"""Capability records and deterministic target composition."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from friday_llm.exceptions import CapabilityConflictError
from friday_llm.targets import ExecutionTarget


class CapabilityState(str, Enum):
    """Known support state for one normalized control."""

    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


class ControlCapability(BaseModel):
    """Capability state, constraints, and source provenance for one control."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    state: CapabilityState
    sources: tuple[str, ...] = ()
    allowed_values: tuple[str, ...] | None = None
    minimum: float | None = None
    maximum: float | None = None


class CapabilityEntry(BaseModel):
    """Immutable named capability entry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, max_length=128)
    capability: ControlCapability


class CapabilityRecord(BaseModel):
    """Versioned capability claims from one target identity axis."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: str = Field(min_length=1, max_length=128)
    version: str = Field(min_length=1, max_length=32)
    controls: tuple[CapabilityEntry, ...]

    @model_validator(mode="after")
    def unique_control_names(self) -> CapabilityRecord:
        names = [entry.name for entry in self.controls]
        if len(names) != len(set(names)):
            raise ValueError("capability control names must be unique")
        return self


class OperatorCapabilityDeclaration(CapabilityRecord):
    """Explicit operator claims used only to refine unknown capabilities."""


class ProviderCapabilities(BaseModel):
    """Composed capabilities for an execution target."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    controls: tuple[CapabilityEntry, ...]
    record_versions: tuple[str, ...]

    def for_control(self, name: str) -> ControlCapability:
        for entry in self.controls:
            if entry.name == name:
                return entry.capability
        return ControlCapability(state=CapabilityState.UNKNOWN)


def _entry(
    name: str,
    state: CapabilityState = CapabilityState.SUPPORTED,
    *,
    allowed_values: tuple[str, ...] | None = None,
    minimum: float | None = None,
    maximum: float | None = None,
) -> CapabilityEntry:
    return CapabilityEntry(
        name=name,
        capability=ControlCapability(
            state=state,
            allowed_values=allowed_values,
            minimum=minimum,
            maximum=maximum,
        ),
    )


_OPENAI_CHAT = CapabilityRecord(
    source="dialect:openai_chat_completions",
    version="1",
    controls=(
        _entry("sampling.temperature", minimum=0.0, maximum=2.0),
        _entry("sampling.top_p", minimum=0.0, maximum=1.0),
        _entry("sampling.presence_penalty", minimum=-2.0, maximum=2.0),
        _entry("sampling.frequency_penalty", minimum=-2.0, maximum=2.0),
        _entry("max_tokens"),
    ),
)

_LM_STUDIO = CapabilityRecord(
    source="engine:lm_studio",
    version="1",
    controls=(
        _entry("reasoning.mode"),
        _entry("reasoning.effort"),
        _entry("reasoning.preserve"),
        _entry("sampling.top_k", minimum=1.0),
        _entry("sampling.min_p", minimum=0.0, maximum=1.0),
        _entry("sampling.repetition_penalty", minimum=0.0),
    ),
)

_QWEN_38 = CapabilityRecord(
    source="model_family:qwen3_8",
    version="1",
    controls=(
        _entry("reasoning.mode"),
        _entry(
            "reasoning.effort",
            allowed_values=("xhigh", "medium", "low"),
        ),
        _entry("reasoning.preserve"),
        _entry("reasoning.budget_tokens", CapabilityState.UNSUPPORTED),
    ),
)


def _records_for_target(target: ExecutionTarget) -> tuple[CapabilityRecord, ...]:
    records: list[CapabilityRecord] = []
    if target.transport.dialect == "openai_chat_completions":
        records.append(_OPENAI_CHAT)
    if target.transport.serving_engine == "lm_studio":
        records.append(_LM_STUDIO)
    if target.model.family == "qwen3_8":
        records.append(_QWEN_38)
    return tuple(records)


def compose_capabilities(
    target: ExecutionTarget,
    operator_declaration: OperatorCapabilityDeclaration | None = None,
) -> ProviderCapabilities:
    """Compose built-in records using the documented conservative lattice."""

    records = _records_for_target(target)
    controls: dict[str, list[ControlCapability]] = {}
    for record in records:
        for entry in record.controls:
            with_source = entry.capability.model_copy(
                update={"sources": (f"{record.source}@{record.version}",)}
            )
            controls.setdefault(entry.name, []).append(with_source)

    if operator_declaration is not None:
        operator_source = (
            f"operator:{operator_declaration.source}@{operator_declaration.version}"
        )
        for entry in operator_declaration.controls:
            built_in_claims = controls.get(entry.name, [])
            _validate_operator_claim(entry.name, built_in_claims, entry.capability)
            with_source = entry.capability.model_copy(
                update={"sources": (operator_source,)}
            )
            if built_in_claims and _compose_control(
                entry.name, built_in_claims
            ).state is CapabilityState.UNKNOWN:
                controls[entry.name] = []
            controls.setdefault(entry.name, []).append(with_source)

    composed = tuple(
        CapabilityEntry(name=name, capability=_compose_control(name, controls[name]))
        for name in sorted(controls)
    )
    versions = [f"{record.source}@{record.version}" for record in records]
    if operator_declaration is not None:
        versions.append(
            f"operator:{operator_declaration.source}@{operator_declaration.version}"
        )
    return ProviderCapabilities(controls=composed, record_versions=tuple(versions))


def _validate_operator_claim(
    name: str,
    built_in_claims: list[ControlCapability],
    operator_claim: ControlCapability,
) -> None:
    if not built_in_claims:
        return
    built_in = _compose_control(name, built_in_claims)
    if built_in.state is CapabilityState.UNSUPPORTED:
        return
    if (
        built_in.state is CapabilityState.SUPPORTED
        and operator_claim.state is not CapabilityState.SUPPORTED
    ):
        raise CapabilityConflictError(
            name,
            built_in.sources,
            "operator declaration contradicts built-in support",
        )
    if built_in.state is not CapabilityState.SUPPORTED:
        return
    if built_in.allowed_values is not None and (
        operator_claim.allowed_values is None
        or not set(operator_claim.allowed_values).issubset(built_in.allowed_values)
    ):
        raise CapabilityConflictError(
            name,
            built_in.sources,
            "operator declaration widens allowed values",
        )
    if built_in.minimum is not None and (
        operator_claim.minimum is None or operator_claim.minimum < built_in.minimum
    ):
        raise CapabilityConflictError(
            name,
            built_in.sources,
            "operator declaration widens the minimum",
        )
    if built_in.maximum is not None and (
        operator_claim.maximum is None or operator_claim.maximum > built_in.maximum
    ):
        raise CapabilityConflictError(
            name,
            built_in.sources,
            "operator declaration widens the maximum",
        )


def _compose_control(
    name: str,
    claims: list[ControlCapability],
) -> ControlCapability:
    sources = tuple(source for claim in claims for source in claim.sources)
    if any(claim.state is CapabilityState.UNSUPPORTED for claim in claims):
        return ControlCapability(
            state=CapabilityState.UNSUPPORTED,
            sources=sources,
        )
    if any(claim.state is CapabilityState.UNKNOWN for claim in claims):
        return ControlCapability(state=CapabilityState.UNKNOWN, sources=sources)

    allowed_sets = [set(claim.allowed_values) for claim in claims if claim.allowed_values]
    allowed_values: tuple[str, ...] | None = None
    if allowed_sets:
        intersection = set.intersection(*allowed_sets)
        if not intersection:
            raise CapabilityConflictError(name, sources, "empty allowed-value set")
        allowed_values = tuple(sorted(intersection))

    minima = [claim.minimum for claim in claims if claim.minimum is not None]
    maxima = [claim.maximum for claim in claims if claim.maximum is not None]
    minimum = max(minima) if minima else None
    maximum = min(maxima) if maxima else None
    if minimum is not None and maximum is not None and minimum > maximum:
        raise CapabilityConflictError(name, sources, "empty numeric range")

    return ControlCapability(
        state=CapabilityState.SUPPORTED,
        sources=sources,
        allowed_values=allowed_values,
        minimum=minimum,
        maximum=maximum,
    )
