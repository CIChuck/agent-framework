"""
Pytest configuration for friday-llm tests.
"""

import pytest


@pytest.fixture(autouse=True)
def reset_litellm_mocks():
    """Reset any global state between tests."""
    yield
