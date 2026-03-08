# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""
Tests for CommandExecuteTool and CommandSafetyValidator.

Tests cover:
1. Allowed commands (curl, ls, grep, pipes, chaining)
2. Blocked commands (rm, sudo, chmod, etc.)
3. Redirect validation (cwd-only)
4. Edge cases (command in string, command in pipe)
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from friday_tools.shell.command import (
    CommandExecuteTool,
    CommandSafetyValidator,
)

# =============================================================================
# VALIDATOR TESTS
# =============================================================================


class TestCommandSafetyValidator:
    """Tests for the CommandSafetyValidator class."""

    def setup_method(self):
        """Create validator and temp directory for each test."""
        self.validator = CommandSafetyValidator()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up temp directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Allowed Commands
    # -------------------------------------------------------------------------

    def test_allows_simple_command(self):
        """Simple allowed commands should pass."""
        is_safe, error = self.validator.validate("ls -la", self.temp_dir)
        assert is_safe is True
        assert error is None

    def test_allows_curl(self):
        """curl should be allowed."""
        is_safe, error = self.validator.validate(
            "curl -s https://example.com", self.temp_dir
        )
        assert is_safe is True
        assert error is None

    def test_allows_pipes(self):
        """Pipes should be allowed (unlike ShellSandbox)."""
        is_safe, error = self.validator.validate(
            "cat file.txt | grep pattern", self.temp_dir
        )
        assert is_safe is True
        assert error is None

    def test_allows_command_chaining_and(self):
        """&& chaining should be allowed."""
        is_safe, error = self.validator.validate(
            "echo hello && echo world", self.temp_dir
        )
        assert is_safe is True
        assert error is None

    def test_allows_command_chaining_or(self):
        """|| chaining should be allowed."""
        is_safe, error = self.validator.validate(
            "cat missing || echo not found", self.temp_dir
        )
        assert is_safe is True
        assert error is None

    def test_allows_command_chaining_semicolon(self):
        """; chaining should be allowed."""
        is_safe, error = self.validator.validate("pwd ; ls", self.temp_dir)
        assert is_safe is True
        assert error is None

    def test_allows_subshell(self):
        """Subshells with $() should be allowed if inner command is safe."""
        is_safe, error = self.validator.validate("echo $(date)", self.temp_dir)
        assert is_safe is True
        assert error is None

    def test_allows_backtick_subshell(self):
        """Subshells with backticks should be allowed if inner command is safe."""
        is_safe, error = self.validator.validate("echo `whoami`", self.temp_dir)
        assert is_safe is True
        assert error is None

    def test_allows_redirect_to_relative_path(self):
        """Redirect to relative path in cwd should be allowed."""
        is_safe, error = self.validator.validate(
            "echo test > output.txt", self.temp_dir
        )
        assert is_safe is True
        assert error is None

    def test_allows_redirect_to_subdir(self):
        """Redirect to subdirectory should be allowed."""
        subdir = self.temp_dir / "subdir"
        subdir.mkdir()
        is_safe, error = self.validator.validate(
            "echo test > subdir/file.txt", self.temp_dir
        )
        assert is_safe is True
        assert error is None

    def test_allows_append_redirect(self):
        """Append redirect (>>) should be allowed."""
        is_safe, error = self.validator.validate("echo test >> log.txt", self.temp_dir)
        assert is_safe is True
        assert error is None

    def test_allows_dev_null_redirect(self):
        """Redirect to /dev/null should be allowed."""
        is_safe, error = self.validator.validate(
            "curl -s url 2>/dev/null", self.temp_dir
        )
        assert is_safe is True
        assert error is None

    def test_allows_command_with_path_prefix(self):
        """Commands with full paths should be validated by their base name."""
        is_safe, error = self.validator.validate("/usr/bin/cat file.txt", self.temp_dir)
        assert is_safe is True
        assert error is None

    # -------------------------------------------------------------------------
    # Blocked Commands
    # -------------------------------------------------------------------------

    def test_blocks_rm(self):
        """rm should be blocked."""
        is_safe, error = self.validator.validate("rm file.txt", self.temp_dir)
        assert is_safe is False
        assert "rm" in error.lower()

    def test_blocks_rm_rf(self):
        """rm -rf should be blocked."""
        is_safe, error = self.validator.validate("rm -rf /", self.temp_dir)
        assert is_safe is False
        assert "rm" in error.lower()

    def test_blocks_sudo(self):
        """sudo should be blocked."""
        is_safe, error = self.validator.validate("sudo whoami", self.temp_dir)
        assert is_safe is False
        assert "sudo" in error.lower()

    def test_blocks_chmod(self):
        """chmod should be blocked."""
        is_safe, error = self.validator.validate("chmod 777 file.txt", self.temp_dir)
        assert is_safe is False
        assert "chmod" in error.lower()

    def test_blocks_chown(self):
        """chown should be blocked."""
        is_safe, error = self.validator.validate("chown root file.txt", self.temp_dir)
        assert is_safe is False
        assert "chown" in error.lower()

    def test_blocks_dd(self):
        """dd should be blocked."""
        is_safe, error = self.validator.validate(
            "dd if=/dev/zero of=file", self.temp_dir
        )
        assert is_safe is False
        assert "dd" in error.lower()

    def test_blocks_kill(self):
        """kill should be blocked."""
        is_safe, error = self.validator.validate("kill 1234", self.temp_dir)
        assert is_safe is False
        assert "kill" in error.lower()

    def test_blocks_pkill(self):
        """pkill should be blocked."""
        is_safe, error = self.validator.validate("pkill -9 process", self.temp_dir)
        assert is_safe is False
        assert "pkill" in error.lower()

    def test_blocks_mv(self):
        """mv should be blocked."""
        is_safe, error = self.validator.validate("mv file1 file2", self.temp_dir)
        assert is_safe is False
        assert "mv" in error.lower()

    def test_blocks_cp(self):
        """cp should be blocked."""
        is_safe, error = self.validator.validate("cp file1 file2", self.temp_dir)
        assert is_safe is False
        assert "cp" in error.lower()

    def test_blocks_pip(self):
        """pip should be blocked."""
        is_safe, error = self.validator.validate("pip install package", self.temp_dir)
        assert is_safe is False
        assert "pip" in error.lower()

    def test_blocks_npm(self):
        """npm should be blocked."""
        is_safe, error = self.validator.validate("npm install package", self.temp_dir)
        assert is_safe is False
        assert "npm" in error.lower()

    def test_blocks_command_in_pipe(self):
        """Blocked command in a pipe should be blocked."""
        is_safe, error = self.validator.validate("curl url | rm -rf /", self.temp_dir)
        assert is_safe is False
        assert "rm" in error.lower()

    def test_blocks_command_in_chain(self):
        """Blocked command in && chain should be blocked."""
        is_safe, error = self.validator.validate(
            "echo test && sudo whoami", self.temp_dir
        )
        assert is_safe is False
        assert "sudo" in error.lower()

    def test_blocks_command_in_subshell(self):
        """Blocked command in subshell should be blocked."""
        is_safe, error = self.validator.validate("echo $(sudo whoami)", self.temp_dir)
        assert is_safe is False
        assert "sudo" in error.lower()

    def test_blocks_command_with_path(self):
        """Blocked command with full path should still be blocked."""
        is_safe, error = self.validator.validate("/usr/bin/sudo whoami", self.temp_dir)
        assert is_safe is False
        assert "sudo" in error.lower()

    # -------------------------------------------------------------------------
    # Redirect Validation
    # -------------------------------------------------------------------------

    def test_blocks_redirect_to_absolute_path(self):
        """Redirect to absolute path should be blocked."""
        is_safe, error = self.validator.validate(
            "echo test > /etc/passwd", self.temp_dir
        )
        assert is_safe is False
        assert "absolute" in error.lower()

    def test_blocks_redirect_with_path_traversal(self):
        """Redirect with .. should be blocked."""
        is_safe, error = self.validator.validate(
            "echo test > ../outside.txt", self.temp_dir
        )
        assert is_safe is False
        assert "traversal" in error.lower()

    def test_blocks_redirect_to_home(self):
        """Redirect to ~ should be blocked."""
        is_safe, error = self.validator.validate(
            "echo test > ~/file.txt", self.temp_dir
        )
        assert is_safe is False
        assert "home" in error.lower()

    def test_blocks_stderr_redirect_to_absolute(self):
        """stderr redirect to absolute path should be blocked."""
        is_safe, error = self.validator.validate("cmd 2>/etc/shadow", self.temp_dir)
        assert is_safe is False
        assert "absolute" in error.lower()

    # -------------------------------------------------------------------------
    # Pattern Blocking
    # -------------------------------------------------------------------------

    def test_blocks_fork_bomb(self):
        """Fork bomb pattern should be blocked."""
        is_safe, error = self.validator.validate(":(){:|:&};:", self.temp_dir)
        assert is_safe is False
        assert "pattern" in error.lower()

    # -------------------------------------------------------------------------
    # Edge Cases
    # -------------------------------------------------------------------------

    def test_allows_rm_in_string(self):
        """rm appearing in a string should be allowed."""
        is_safe, error = self.validator.validate('echo "rm -rf /"', self.temp_dir)
        assert is_safe is True
        assert error is None

    def test_allows_grep_for_rm(self):
        """Searching for rm in text should be allowed."""
        is_safe, error = self.validator.validate("grep rm file.txt", self.temp_dir)
        assert is_safe is True
        assert error is None

    def test_command_extraction_handles_quotes(self):
        """Command extraction should handle quoted strings."""
        commands = self.validator._extract_commands('echo "hello | world"')
        assert "echo" in commands
        # The pipe inside quotes should not be parsed as a command separator

    # -------------------------------------------------------------------------
    # Custom Blocklist
    # -------------------------------------------------------------------------

    def test_custom_blocked_commands(self):
        """Custom blocked commands should override defaults."""
        custom_validator = CommandSafetyValidator(blocked_commands={"foo", "bar"})

        # rm should now be allowed
        is_safe, _ = custom_validator.validate("rm file.txt", self.temp_dir)
        assert is_safe is True

        # foo should be blocked
        is_safe, error = custom_validator.validate("foo arg", self.temp_dir)
        assert is_safe is False
        assert "foo" in error.lower()

    def test_custom_blocked_patterns(self):
        """Custom blocked patterns should work."""
        custom_validator = CommandSafetyValidator(
            blocked_patterns=[r"dangerous_pattern"]
        )

        is_safe, error = custom_validator.validate(
            "dangerous_pattern here", self.temp_dir
        )
        assert is_safe is False
        assert "pattern" in error.lower()


# =============================================================================
# TOOL TESTS
# =============================================================================


class TestCommandExecuteTool:
    """Tests for the CommandExecuteTool class."""

    def setup_method(self):
        """Create tool and temp directory for each test."""
        self.tool = CommandExecuteTool()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up temp directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Tool Properties
    # -------------------------------------------------------------------------

    def test_tool_name(self):
        """Tool should have correct name."""
        assert self.tool.name == "command_execute"

    def test_tool_description(self):
        """Tool should have description."""
        assert "execute" in self.tool.description.lower()
        assert "command" in self.tool.description.lower()

    def test_tool_category(self):
        """Tool should have shell category."""
        assert self.tool.category == "shell"

    def test_tool_has_tags(self):
        """Tool should have tags."""
        assert "shell" in self.tool.tags
        assert "curl" in self.tool.tags

    def test_tool_parameters_schema(self):
        """Tool should have valid parameters schema."""
        schema = self.tool.parameters_schema
        assert "properties" in schema
        assert "command" in schema["properties"]

    # -------------------------------------------------------------------------
    # Command Execution
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_execute_simple_command(self):
        """Simple command should execute successfully."""
        result = await self.tool.run(
            self.tool.Input(command="echo hello", cwd=str(self.temp_dir))
        )
        assert result.error is None
        assert "hello" in result.content
        assert result.data["return_code"] == 0

    @pytest.mark.asyncio
    async def test_execute_with_pipe(self):
        """Command with pipe should work."""
        result = await self.tool.run(
            self.tool.Input(
                command="echo 'hello world' | grep hello", cwd=str(self.temp_dir)
            )
        )
        assert result.error is None
        assert "hello" in result.content
        assert result.data["return_code"] == 0

    @pytest.mark.asyncio
    async def test_execute_with_chain(self):
        """Command chaining should work."""
        result = await self.tool.run(
            self.tool.Input(command="echo first && echo second", cwd=str(self.temp_dir))
        )
        assert result.error is None
        assert "first" in result.content
        assert "second" in result.content

    @pytest.mark.asyncio
    async def test_execute_blocked_command(self):
        """Blocked command should return error."""
        result = await self.tool.run(
            self.tool.Input(command="rm -rf /", cwd=str(self.temp_dir))
        )
        assert result.error is not None
        assert "blocked" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_with_redirect(self):
        """Redirect to relative path should work."""
        result = await self.tool.run(
            self.tool.Input(command="echo test > output.txt", cwd=str(self.temp_dir))
        )
        assert result.error is None
        # Check file was created
        assert (self.temp_dir / "output.txt").exists()
        assert (self.temp_dir / "output.txt").read_text().strip() == "test"

    @pytest.mark.asyncio
    async def test_execute_with_blocked_redirect(self):
        """Redirect to absolute path should be blocked."""
        result = await self.tool.run(
            self.tool.Input(command="echo test > /etc/passwd", cwd=str(self.temp_dir))
        )
        assert result.error is not None
        assert "blocked" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_nonexistent_cwd(self):
        """Nonexistent cwd should return error."""
        result = await self.tool.run(
            self.tool.Input(command="ls", cwd="/nonexistent/path/12345")
        )
        assert result.error is not None
        assert "not exist" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_with_env(self):
        """Custom env vars should be passed."""
        result = await self.tool.run(
            self.tool.Input(
                command="echo $MY_VAR",
                cwd=str(self.temp_dir),
                env={"MY_VAR": "custom_value"},
            )
        )
        assert result.error is None
        assert "custom_value" in result.content

    @pytest.mark.asyncio
    async def test_execute_timeout(self):
        """Command exceeding timeout should return error."""
        result = await self.tool.run(
            self.tool.Input(command="sleep 10", cwd=str(self.temp_dir), timeout=1)
        )
        assert result.error is not None
        assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_failed_command(self):
        """Failed command should return non-zero exit code."""
        result = await self.tool.run(
            self.tool.Input(command="false", cwd=str(self.temp_dir))
        )
        assert result.data["return_code"] != 0
        # Error might be set based on stderr

    @pytest.mark.asyncio
    async def test_execute_with_stderr(self):
        """stderr should be captured."""
        result = await self.tool.run(
            self.tool.Input(command="ls /nonexistent 2>&1", cwd=str(self.temp_dir))
        )
        # Command should fail and stderr should have content
        assert result.data is not None

    # -------------------------------------------------------------------------
    # Custom Blocklist via Constructor
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_custom_tool_blocklist(self):
        """Tool with custom blocklist should work."""
        custom_tool = CommandExecuteTool(blocked_commands={"echo"})

        result = await custom_tool.run(
            custom_tool.Input(command="echo hello", cwd=str(self.temp_dir))
        )
        assert result.error is not None
        assert "blocked" in result.error.lower()

        # rm should now be allowed
        result = await custom_tool.run(
            custom_tool.Input(command="true", cwd=str(self.temp_dir))
        )
        assert result.error is None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestCommandExecuteIntegration:
    """Integration tests for realistic command patterns."""

    def setup_method(self):
        """Create tool and temp directory."""
        self.tool = CommandExecuteTool()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up temp directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_curl_pipe_jq_pattern(self):
        """curl ... | jq pattern should be allowed."""
        # We can't actually run curl to an external service in tests,
        # but we can validate the command is allowed
        validator = CommandSafetyValidator()
        is_safe, error = validator.validate(
            "curl -s https://api.example.com | jq '.data'", self.temp_dir
        )
        assert is_safe is True

    @pytest.mark.asyncio
    async def test_find_grep_pattern(self):
        """find ... | grep pattern should work."""
        result = await self.tool.run(
            self.tool.Input(
                command="find . -name '*.txt' 2>/dev/null | head -5",
                cwd=str(self.temp_dir),
            )
        )
        # Should succeed (even if no files found)
        assert result.data["return_code"] == 0

    @pytest.mark.asyncio
    async def test_complex_pipeline(self):
        """Complex pipeline should work."""
        result = await self.tool.run(
            self.tool.Input(
                command="echo 'a\nb\nc' | sort | uniq | wc -l",
                cwd=str(self.temp_dir),
            )
        )
        assert result.error is None
        assert "3" in result.content.strip()

    @pytest.mark.asyncio
    async def test_network_diagnostics(self):
        """Network diagnostic commands should be allowed."""
        validator = CommandSafetyValidator()

        for cmd in ["ping -c 1 localhost", "dig example.com", "host example.com"]:
            is_safe, _ = validator.validate(cmd, self.temp_dir)
            assert is_safe is True, f"Command should be allowed: {cmd}"

    @pytest.mark.asyncio
    async def test_system_info_commands(self):
        """System info commands should be allowed."""
        validator = CommandSafetyValidator()

        for cmd in ["df -h", "du -sh .", "uptime", "date", "whoami", "env"]:
            is_safe, _ = validator.validate(cmd, self.temp_dir)
            assert is_safe is True, f"Command should be allowed: {cmd}"
