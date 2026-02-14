"""
Memory profile configuration — backward compatibility re-exports.

The canonical definitions have moved to ``friday_core.profiles``.
This module re-exports them so existing ``friday_cli.profiles``
imports continue to work without modification.

.. deprecated::
    Import from ``friday_core.profiles`` instead of
    ``friday_cli.profiles``.

Ref: Phase 1 Build Plan — MemoryProfile migration to friday-core
"""

from friday_core.profiles import (  # noqa: F401
    MemoryProfile,
    create_graph_store,
    create_vector_store,
)

__all__ = [
    "MemoryProfile",
    "create_vector_store",
    "create_graph_store",
]
