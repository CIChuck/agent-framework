"""UI-neutral session identity for Friday runtime callers."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


class SessionIdentityMismatchError(ValueError):
    """Raised when composition layers disagree on session identity."""


@dataclass(frozen=True)
class SessionIdentity:
    """Immutable identity generated once for one Friday invocation."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or self.value != self.value.strip():
            raise ValueError("session identity must be non-empty and trimmed")

    @classmethod
    def generate(cls) -> SessionIdentity:
        """Create one production session identity."""
        return cls(f"session_{uuid4().hex}")

    def __str__(self) -> str:
        return self.value


def resolve_session_identity(
    *,
    session_identity: SessionIdentity | None = None,
    session_id: str | None = None,
) -> SessionIdentity:
    """Resolve typed and compatibility injection into one identity."""
    if session_identity is not None and session_id is not None:
        if session_identity.value != session_id:
            raise SessionIdentityMismatchError(
                "typed session identity does not match injected session_id"
            )
        return session_identity
    if session_identity is not None:
        return session_identity
    if session_id is not None:
        return SessionIdentity(session_id)
    return SessionIdentity.generate()


__all__ = [
    "SessionIdentity",
    "SessionIdentityMismatchError",
    "resolve_session_identity",
]
