"""
Quarantine store for raw tool outputs that triggered detections.

Stores JSONL records for later security review.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from friday_core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class QuarantineRecord:
    """Record for a quarantined tool output."""

    tool_name: str
    tool_category: str
    risk_level: str
    detected_patterns: list[str]
    content: str
    created_at: str
    metadata: dict[str, Any] | None = None


class QuarantineStore:
    """Append-only JSONL quarantine store."""

    def __init__(self, path: str | Path) -> None:
        """
        Initialize the quarantine store and validate writability.

        Args:
            path: JSONL path for quarantine records.

        Raises:
            OSError: If the path cannot be created or written.
        """
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

        # Fail fast if not writable.
        try:
            with self._path.open("a", encoding="utf-8"):
                pass
        except OSError as exc:
            logger.error(
                "Quarantine path not writable",
                path=str(self._path),
                error=str(exc),
            )
            raise

    def append(
        self,
        content: str,
        tool_name: str,
        tool_category: str,
        risk_level: str,
        detected_patterns: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Append a quarantine record to the JSONL file.

        Args:
            content: Raw tool output content.
            tool_name: Tool name.
            tool_category: Tool category.
            risk_level: Risk classification.
            detected_patterns: Detected pattern names.
            metadata: Optional metadata for auditing.
        """
        record = QuarantineRecord(
            tool_name=tool_name,
            tool_category=tool_category,
            risk_level=risk_level,
            detected_patterns=detected_patterns,
            content=content,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata,
        )
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record)) + "\n")
