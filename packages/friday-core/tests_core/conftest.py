# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""
Shared test fixtures for friday-core tests.
"""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("APP_ENV=testing\n")
        f.write("LOG_LEVEL=DEBUG\n")
        f.write("DEFAULT_MODEL=gpt-4\n")
        f.write("OPENAI_API_KEY=test-key-12345\n")
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def clean_env():
    """Ensure a clean environment for config tests."""
    # Save original values
    original = {}
    env_vars = ["APP_ENV", "LOG_LEVEL", "DEFAULT_MODEL", "OPENAI_API_KEY"]
    for var in env_vars:
        original[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]

    yield

    # Restore original values
    for var, value in original.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]
