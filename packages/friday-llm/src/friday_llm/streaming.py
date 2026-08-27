"""Typed streaming event contracts and tool-call assembly."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    TypeAdapter,
    ValidationError,
)


class TextDeltaEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    type: Literal["text_delta"] = "text_delta"
    text: str


class ReasoningDeltaEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    type: Literal["reasoning_delta"] = "reasoning_delta"
    text: str


class ToolCallDeltaEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    type: Literal["tool_call_delta"] = "tool_call_delta"
    index: int = Field(ge=0)
    call_id: str | None = None
    name: str | None = None
    arguments_delta: str = ""


class ToolCallCompleteEvent(BaseModel):
    """A fully assembled and validated streaming tool call."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    type: Literal["tool_call_complete"] = "tool_call_complete"
    index: int = Field(ge=0)
    call_id: str
    name: str
    arguments: dict[str, JsonValue]


class StreamErrorEvent(BaseModel):
    """Diagnostic-safe stream failure without provider payload values."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    type: Literal["error"] = "error"
    code: Literal["incomplete_tool_identity", "malformed_tool_arguments"]
    index: int = Field(ge=0)
    message: str = Field(max_length=256)


class UsageEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    type: Literal["usage"] = "usage"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    reasoning_tokens: int | None = None


class FinishEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    type: Literal["finish"] = "finish"
    finish_reason: str | None = None


StreamEvent = Annotated[
    TextDeltaEvent
    | ReasoningDeltaEvent
    | ToolCallDeltaEvent
    | ToolCallCompleteEvent
    | UsageEvent
    | FinishEvent
    | StreamErrorEvent,
    Field(discriminator="type"),
]


@dataclass(slots=True)
class _ToolState:
    call_id: str = ""
    name: str = ""
    arguments: str = ""


_ARGUMENTS_ADAPTER = TypeAdapter(dict[str, JsonValue])


class ToolCallAssembler:
    """Assemble tool fragments by provider index without mixing content lanes."""

    def __init__(self) -> None:
        self._states: dict[int, _ToolState] = {}

    def add(self, event: ToolCallDeltaEvent) -> None:
        state = self._states.setdefault(event.index, _ToolState())
        if event.call_id:
            state.call_id += event.call_id
        if event.name:
            state.name += event.name
        state.arguments += event.arguments_delta

    def finish(self) -> tuple[ToolCallCompleteEvent | StreamErrorEvent, ...]:
        events: list[ToolCallCompleteEvent | StreamErrorEvent] = []
        for index in sorted(self._states):
            state = self._states[index]
            if not state.call_id or not state.name:
                events.append(
                    StreamErrorEvent(
                        code="incomplete_tool_identity",
                        index=index,
                        message="streamed tool call is missing its ID or name",
                    )
                )
                continue
            try:
                arguments = _ARGUMENTS_ADAPTER.validate_python(
                    json.loads(state.arguments)
                )
            except (json.JSONDecodeError, ValidationError):
                events.append(
                    StreamErrorEvent(
                        code="malformed_tool_arguments",
                        index=index,
                        message="streamed tool arguments are not a JSON object",
                    )
                )
                continue
            events.append(
                ToolCallCompleteEvent(
                    index=index,
                    call_id=state.call_id,
                    name=state.name,
                    arguments=arguments,
                )
            )
        return tuple(events)
