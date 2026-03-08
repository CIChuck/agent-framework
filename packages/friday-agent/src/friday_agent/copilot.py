"""
Compatibility alias for the interactive runtime agent.

Phase 4 keeps `CopilotAgent` for compatibility while the runtime default moves
to `InteractiveAgent`.
"""

from __future__ import annotations

import warnings
from typing import Any

from friday_agent.interactive import InteractiveAgent


class CopilotAgent(InteractiveAgent):
    """Deprecated Phase 4 compatibility alias for `InteractiveAgent`."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "CopilotAgent is deprecated in Phase 4; use InteractiveAgent instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
