"""Session state helpers for FridayV2."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FridaySession:
    """Minimal session state used by the initial FridayV2 skeleton."""

    session_id: str
    user_id: str
    turn_ids: list[str] = field(default_factory=list)
    initialized: bool = False
    scoped_defaults: dict[str, str] = field(default_factory=dict)

    def ensure_initialized(self, defaults: dict[str, str] | None = None) -> None:
        """Initialize per-session defaults exactly once."""
        if self.initialized:
            return
        self.scoped_defaults.update(defaults or {})
        self.initialized = True
