# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""
Pytest configuration for friday-agent tests.
"""

import pytest
from friday_agent.tools.registry import _GLOBAL_TOOL_REGISTRY


@pytest.fixture(autouse=True)
def clear_global_registry():
    """Isolate test registrations while preserving prior declarations."""
    original_registry = dict(_GLOBAL_TOOL_REGISTRY)
    _GLOBAL_TOOL_REGISTRY.clear()
    try:
        yield
    finally:
        _GLOBAL_TOOL_REGISTRY.clear()
        _GLOBAL_TOOL_REGISTRY.update(original_registry)
