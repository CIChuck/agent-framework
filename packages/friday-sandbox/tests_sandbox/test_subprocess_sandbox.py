# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for subprocess sandbox."""

import pytest

from friday_sandbox import SandboxTimeoutError
from friday_sandbox.subprocess import SubprocessSandbox


class TestSubprocessSandbox:
    """Test suite for SubprocessSandbox."""

    @pytest.fixture
    def sandbox(self, sandbox_config, temp_workspace_path):
        """Create a subprocess sandbox for testing."""
        sandbox_config.docker.workspace_base_path = temp_workspace_path
        return SubprocessSandbox(config=sandbox_config)

    async def test_execute_simple_code(self, sandbox):
        """Test executing simple Python code."""
        result = await sandbox.execute("print('Hello, World!')")

        assert result.success
        assert "Hello, World!" in result.stdout
        assert result.exit_code == 0

    async def test_execute_with_return_value(self, sandbox):
        """Test executing code with return value."""
        code = """
__friday_result__ = {"status": "ok", "count": 42}
"""
        result = await sandbox.execute(code)

        assert result.success
        assert result.return_value == {"status": "ok", "count": 42}

    async def test_execute_with_error(self, sandbox):
        """Test executing code that raises an error."""
        code = """
raise ValueError("Something went wrong")
"""
        result = await sandbox.execute(code)

        # The code itself doesn't fail, but the error is captured
        assert result.return_value is not None
        assert result.return_value.get("type") == "ValueError"

    async def test_execute_syntax_error(self, sandbox):
        """Test executing code with syntax error."""
        code = "def broken("

        result = await sandbox.execute(code)

        assert result.exit_code != 0
        assert "SyntaxError" in result.stderr or result.stderr

    async def test_execute_with_workspace(self, sandbox):
        """Test executing code with workspace."""
        workspace = await sandbox.create_workspace()

        # Create a file in the workspace
        code = """
with open('test.txt', 'w') as f:
    f.write('Hello from sandbox!')
__friday_result__ = "done"
"""
        result = await sandbox.execute(code, workspace_id=workspace.id)

        assert result.success
        assert "test.txt" in result.files_created

        # Verify file exists
        assert (workspace.path / "test.txt").exists()
        assert (workspace.path / "test.txt").read_text() == "Hello from sandbox!"

    async def test_execute_with_environment(self, sandbox):
        """Test executing code with environment variables."""
        code = """
import os
__friday_result__ = os.environ.get('TEST_VAR', 'not found')
"""
        result = await sandbox.execute(
            code,
            environment={"TEST_VAR": "test_value"},
        )

        assert result.success
        assert result.return_value == "test_value"

    async def test_execute_timeout(self, sandbox):
        """Test that long-running code times out."""
        code = """
import time
time.sleep(10)
"""
        with pytest.raises(SandboxTimeoutError):
            await sandbox.execute(code, timeout_seconds=1)

    async def test_unsupported_language(self, sandbox):
        """Test that unsupported languages raise error."""
        with pytest.raises(ValueError, match="Unsupported language"):
            await sandbox.execute("console.log('hello')", language="javascript")

    async def test_workspace_lifecycle(self, sandbox):
        """Test workspace create, use, and cleanup."""
        workspace = await sandbox.create_workspace(agent_id="test-agent")
        assert workspace.path.exists()

        # Use workspace
        await sandbox.execute(
            "open('marker.txt', 'w').write('x')",
            workspace_id=workspace.id,
        )
        assert (workspace.path / "marker.txt").exists()

        # Cleanup
        result = await sandbox.cleanup_workspace(workspace.id)
        assert result is True
        assert not workspace.path.exists()
