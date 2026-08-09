"""Datetime compatibility helpers for persisted Friday Memory metadata."""

from __future__ import annotations

from datetime import datetime


def elapsed_hours(earlier: datetime, later: datetime | None = None) -> float:
    """Return elapsed hours across aware UTC and legacy naive-local values."""
    resolved_later = later or datetime.now().astimezone()
    return (_as_aware(resolved_later) - _as_aware(earlier)).total_seconds() / 3600


def _as_aware(value: datetime) -> datetime:
    """Interpret legacy naive values as local wall time without rewriting them."""
    if value.tzinfo is not None and value.utcoffset() is not None:
        return value
    return value.astimezone()


__all__ = ["elapsed_hours"]
