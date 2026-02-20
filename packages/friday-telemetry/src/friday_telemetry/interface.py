"""
Telemetry Interface Protocol.

Defines the abstract contract for telemetry and inspection hooks.

Ref: Batch 0 Specification, Section 4.3
"""

from abc import ABC, abstractmethod
from typing import Any


class TelemetryInterface(ABC):
    """
    Protocol for telemetry and inspection hooks.

    Allows inspecting internal decision-making during tests without
    breaking encapsulation. Components accept an optional telemetry
    recorder via constructor injection.

    Example:
        recorder = DebugTelemetryRecorder()
        controller = MemoryController(..., telemetry=recorder)
        await controller.recall("test")
        assert "vector_search" in [e["name"] for e in recorder.events]
    """

    @abstractmethod
    def capture_event(self, event_name: str, data: dict[str, Any]) -> None:
        """
        Records a discrete event.

        Args:
            event_name: Identifier for the event type (e.g., 'memory_recall', 'tool_usage')
            data: Arbitrary event data to record
        """  # noqa: E501
        pass

    @abstractmethod
    def start_span(self, name: str, parent_id: str | None = None) -> str:
        """
        Starts a trace span for duration tracking.

        Args:
            name: Name of the operation being traced
            parent_id: Optional parent span ID for nested traces

        Returns:
            span_id: Unique identifier for this span, used to end it later
        """
        pass

    @abstractmethod
    def end_span(self, span_id: str, data: dict[str, Any] | None = None) -> None:
        """
        Ends a previously started span.

        Args:
            span_id: The ID returned by start_span()
            data: Optional final data to attach (e.g., result, error)
        """
        pass
