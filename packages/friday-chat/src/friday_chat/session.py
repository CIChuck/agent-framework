"""Session state helpers for FridayV2."""

from __future__ import annotations

from dataclasses import dataclass, field

from friday_runtime.session_identity import (
    SessionIdentity,
    SessionIdentityMismatchError,
    resolve_session_identity,
)


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
