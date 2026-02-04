"""
Pytest configuration for friday-agent tests.
"""

import pytest
from friday_agent.tools.registry import _GLOBAL_TOOL_REGISTRY


@pytest.fixture(autouse=True)
def clear_global_registry():
    """Clear the global tool registry between tests."""
    _GLOBAL_TOOL_REGISTRY.clear()
    yield
    _GLOBAL_TOOL_REGISTRY.clear()
