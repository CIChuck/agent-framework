"""Exceptions for the Moltbook client."""

from __future__ import annotations

from typing import Any


class MoltbookError(Exception):
    """Base exception for Moltbook errors."""


class MoltbookConfigError(MoltbookError):
    """Raised when configuration is invalid or incomplete."""


class MoltbookValidationError(MoltbookError):
    """Raised when client-side validation fails."""


class MoltbookResponseError(MoltbookError):
    """Raised when a response cannot be parsed or is missing expected fields."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        endpoint: str | None = None,
        raw: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint
        self.raw = raw

    def __str__(self) -> str:
        message = self.args[0] if self.args else "Moltbook response error"
        details: list[str] = []
        if self.endpoint:
            details.append(f"endpoint={self.endpoint}")
        if self.status_code is not None:
            details.append(f"status_code={self.status_code}")
        if details:
            return f"{message} ({', '.join(details)})"
        return message
