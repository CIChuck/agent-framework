"""Session state helpers for FridayV2."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


class SessionIdentityMismatchError(ValueError):
    """Raised when two Friday Chat composition layers disagree on identity."""


@dataclass(frozen=True)
class SessionIdentity:
    """Immutable identity generated once for one Friday Chat invocation."""

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


@dataclass
class FridaySession:
    """Minimal session state used by the initial FridayV2 skeleton."""

    session_id: str
    user_id: str
    identity: SessionIdentity | None = None
    turn_ids: list[str] = field(default_factory=list)
    initialized: bool = False
    scoped_defaults: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        resolved_identity = self.identity or SessionIdentity(self.session_id)
        if resolved_identity.value != self.session_id:
            raise SessionIdentityMismatchError(
                "FridaySession identity does not match its session_id"
            )
        self.identity = resolved_identity

    def ensure_initialized(self, defaults: dict[str, str] | None = None) -> None:
        """Initialize per-session defaults exactly once."""
        if self.initialized:
            return
        self.scoped_defaults.update(defaults or {})
        self.initialized = True


__all__ = [
    "FridaySession",
    "SessionIdentity",
    "SessionIdentityMismatchError",
    "resolve_session_identity",
]
