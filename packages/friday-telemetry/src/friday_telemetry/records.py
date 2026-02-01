"""
Telemetry Record Types.

Data structures for capturing spans and events.

Ref: Batch 0 Specification, Section 4.3
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SpanRecord:
    """Internal record of a trace span."""

    name: str
    parent_id: str | None
    start_time: float
    end_time: float | None = None
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float | None:
        """Duration in milliseconds, or None if span hasn't ended."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000


@dataclass
class EventRecord:
    """Internal record of a discrete event."""

    name: str
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
