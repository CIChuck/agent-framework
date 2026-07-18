"""Turn models for FridayV2."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from friday_chat.tools.schemas import ToolCallRecord


@dataclass(frozen=True)
class ToolCallRequest:
    """Structured tool call requested by an LLM response."""

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    call_id: str | None = None


@dataclass(frozen=True)
class ChatModelResponse:
    """Structured assistant response from a chat model."""

    content: str = ""
    tool_calls: tuple[ToolCallRequest, ...] = ()
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)
    reasoning_content: str | None = None
    raw_response: Any | None = None

    @classmethod
    def from_text(cls, text: str) -> ChatModelResponse:
        """Create a structured response from plain text."""
        return cls(content=text)

    @property
    def has_tool_calls(self) -> bool:
        """Return whether this response requested any tools."""
        return bool(self.tool_calls)


@dataclass(frozen=True)
class TurnMetrics:
    """Timing metrics captured for a FridayV2 turn."""

    retrieval_seconds: float
    llm_seconds: float
    persistence_seconds: float
    total_seconds: float

    def as_dict(self) -> dict[str, float]:
        """Return metrics as a command-friendly mapping."""
        return {
            "retrieval": self.retrieval_seconds,
            "llm": self.llm_seconds,
            "persistence": self.persistence_seconds,
            "total": self.total_seconds,
        }


@dataclass(frozen=True)
class InteractionTurn:
    """Persisted interaction turn captured by FridayV2."""

    turn_id: str
    user_message: str
    assistant_message: str
    prompt: str
    context: str
    memory_snippets: tuple[str, ...]
    metrics: TurnMetrics
    raw_prompt_captured: bool = False
    tool_calls: tuple[ToolCallRecord, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)
