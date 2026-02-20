"""
Tests for friday-cli command registry.
"""

import pytest
from friday_cli import (
    ArgumentSpec,
    CommandInfo,
    CommandRegistry,
    arg,
)


class MockContext:
    """Mock context for testing commands."""

    def __init__(self):
        self.data = {"key": "value"}


class TestCommandRegistry:
    """Test CommandRegistry class."""

    def test_register_sync_command(self):
        registry = CommandRegistry()

        @registry.command("test")
        def cmd_test(ctx):
            """Test command."""
            return "test result"

        assert "test" in registry.commands
        assert registry.commands["test"].description == "Test command."
        assert registry.commands["test"].is_async is False

    def test_register_async_command(self):
        registry = CommandRegistry()

        @registry.command("async-test")
        async def cmd_async_test(ctx):
            """Async test command."""
            return "async result"

        assert "async-test" in registry.commands
        assert registry.commands["async-test"].is_async is True

    def test_register_with_aliases(self):
        registry = CommandRegistry()

        @registry.command("history", aliases=["h", "hist"])
        def cmd_history(ctx):
            """Show history."""
            return "history"

        info = registry.get("history")
        assert info is not None
        assert info.aliases == ["h", "hist"]

        # Can get by alias
        assert registry.get("h") is info
        assert registry.get("hist") is info

    def test_register_with_arguments(self):
        registry = CommandRegistry()

        @registry.command(
            "export",
            arguments=[
                arg("format", required=False, default="json", choices=["json", "csv"]),
            ],
        )
        def cmd_export(ctx, format="json"):
            """Export data."""
            return f"exported as {format}"

        info = registry.get("export")
        assert len(info.arguments) == 1
        assert info.arguments[0].name == "format"
        assert info.arguments[0].default == "json"

    def test_register_with_category(self):
        registry = CommandRegistry()

        @registry.command("tools", category="tools")
        def cmd_tools(ctx):
            """List tools."""
            return "tools"

        @registry.command("help", category="general")
        def cmd_help(ctx):
            """Show help."""
            return "help"

        assert registry.commands["tools"].category == "tools"
        assert registry.commands["help"].category == "general"

    def test_programmatic_registration(self):
        registry = CommandRegistry()

        def handler(ctx):
            return "programmatic"

        registry.register(
            "prog",
            handler,
            aliases=["p"],
            description="Programmatic command",
        )

        info = registry.get("prog")
        assert info is not None
        assert info.description == "Programmatic command"
        assert registry.get("p") is info

    def test_unregister_command(self):
        registry = CommandRegistry()

        @registry.command("temp", aliases=["t"])
        def cmd_temp(ctx):
            """Temporary."""
            return "temp"

        assert registry.get("temp") is not None
        assert registry.get("t") is not None

        result = registry.unregister("temp")
        assert result is True
        assert registry.get("temp") is None
        assert registry.get("t") is None

    def test_unregister_nonexistent(self):
        registry = CommandRegistry()
        result = registry.unregister("nonexistent")
        assert result is False


class TestParseInput:
    """Test input parsing."""

    def test_parse_simple_command(self):
        registry = CommandRegistry()
        cmd, args = registry.parse_input("/help")

        assert cmd == "help"
        assert args == []

    def test_parse_command_with_args(self):
        registry = CommandRegistry()
        cmd, args = registry.parse_input("/export json")

        assert cmd == "export"
        assert args == ["json"]

    def test_parse_command_with_multiple_args(self):
        registry = CommandRegistry()
        cmd, args = registry.parse_input("/set key value")

        assert cmd == "set"
        assert args == ["key", "value"]

    def test_parse_quoted_args(self):
        registry = CommandRegistry()
        cmd, args = registry.parse_input('/search "hello world"')

        assert cmd == "search"
        assert args == ["hello world"]

    def test_parse_non_command(self):
        registry = CommandRegistry()
        cmd, args = registry.parse_input("hello world")

        assert cmd is None
        assert args == []

    def test_parse_empty_command(self):
        registry = CommandRegistry()
        cmd, args = registry.parse_input("/")

        assert cmd is None
        assert args == []

    def test_parse_preserves_case_in_args(self):
        registry = CommandRegistry()
        cmd, args = registry.parse_input("/Set KEY Value")

        assert cmd == "set"  # Command is lowercased
        assert args == ["KEY", "Value"]  # Args preserve case


class TestExecute:
    """Test command execution."""

    @pytest.mark.asyncio
    async def test_execute_sync_command(self):
        registry = CommandRegistry()
        ctx = MockContext()

        @registry.command("test")
        def cmd_test(ctx):
            """Test."""
            return "executed"

        was_cmd, result = await registry.execute("/test", ctx)

        assert was_cmd is True
        assert result == "executed"

    @pytest.mark.asyncio
    async def test_execute_async_command(self):
        registry = CommandRegistry()
        ctx = MockContext()

        @registry.command("async")
        async def cmd_async(ctx):
            """Async."""
            return "async executed"

        was_cmd, result = await registry.execute("/async", ctx)

        assert was_cmd is True
        assert result == "async executed"

    @pytest.mark.asyncio
    async def test_execute_with_args(self):
        registry = CommandRegistry()
        ctx = MockContext()

        @registry.command(
            "greet",
            arguments=[arg("name", required=True)],
        )
        def cmd_greet(ctx, name):
            """Greet someone."""
            return f"Hello, {name}!"

        was_cmd, result = await registry.execute("/greet Alice", ctx)

        assert was_cmd is True
        assert result == "Hello, Alice!"

    @pytest.mark.asyncio
    async def test_execute_unknown_command(self):
        registry = CommandRegistry()
        ctx = MockContext()

        was_cmd, result = await registry.execute("/unknown", ctx)

        assert was_cmd is True
        assert "Unknown command" in result

    @pytest.mark.asyncio
    async def test_execute_non_command(self):
        registry = CommandRegistry()
        ctx = MockContext()

        was_cmd, result = await registry.execute("just text", ctx)

        assert was_cmd is False
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_with_alias(self):
        registry = CommandRegistry()
        ctx = MockContext()

        @registry.command("history", aliases=["h"])
        def cmd_history(ctx):
            """History."""
            return "history shown"

        was_cmd, result = await registry.execute("/h", ctx)

        assert was_cmd is True
        assert result == "history shown"

    @pytest.mark.asyncio
    async def test_execute_with_default_arg(self):
        registry = CommandRegistry()
        ctx = MockContext()

        @registry.command(
            "export",
            arguments=[arg("format", default="json")],
        )
        def cmd_export(ctx, format="json"):
            """Export."""
            return f"format: {format}"

        # Without arg
        was_cmd, result = await registry.execute("/export", ctx)
        assert result == "format: json"

        # With arg
        was_cmd, result = await registry.execute("/export csv", ctx)
        assert result == "format: csv"

    @pytest.mark.asyncio
    async def test_execute_with_extra_kwargs(self):
        registry = CommandRegistry()
        ctx = MockContext()

        @registry.command("debug")
        def cmd_debug(ctx, verbose=False):
            """Debug."""
            return f"verbose: {verbose}"

        was_cmd, result = await registry.execute("/debug", ctx, verbose=True)

        assert was_cmd is True
        assert result == "verbose: True"


class TestCommandInfo:
    """Test CommandInfo dataclass."""

    def test_usage_no_args(self):
        info = CommandInfo(
            name="help",
            handler=lambda ctx: "help",
            description="Show help",
        )
        assert info.usage == "/help"

    def test_usage_with_required_arg(self):
        info = CommandInfo(
            name="set",
            handler=lambda ctx, key, value: f"{key}={value}",
            description="Set value",
            arguments=[
                ArgumentSpec(name="key", required=True),
                ArgumentSpec(name="value", required=True),
            ],
        )
        assert info.usage == "/set <key> <value>"

    def test_usage_with_optional_arg(self):
        info = CommandInfo(
            name="export",
            handler=lambda ctx, format: format,
            description="Export",
            arguments=[
                ArgumentSpec(name="format", required=False),
            ],
        )
        assert info.usage == "/export [format]"

    def test_all_names(self):
        info = CommandInfo(
            name="history",
            handler=lambda ctx: "history",
            description="Show history",
            aliases=["h", "hist"],
        )
        assert info.all_names == ["history", "h", "hist"]


class TestHelp:
    """Test help generation."""

    def test_get_help(self):
        registry = CommandRegistry()

        @registry.command("help")
        def cmd_help(ctx):
            """Show available commands."""
            return "help"

        @registry.command("exit", aliases=["quit"])
        def cmd_exit(ctx):
            """Exit the program."""
            return "exit"

        help_dict = registry.get_help(categories=False)

        assert "/help" in help_dict
        assert help_dict["/help"] == "Show available commands."

    def test_get_help_with_aliases(self):
        registry = CommandRegistry()

        @registry.command("history", aliases=["h"])
        def cmd_history(ctx):
            """Show history."""
            return "history"

        help_dict = registry.get_help()

        # Should include alias info
        keys = list(help_dict.keys())
        assert any("/h" in k for k in keys)

    def test_get_help_by_category(self):
        registry = CommandRegistry()

        @registry.command("help", category="general")
        def cmd_help(ctx):
            """Help."""
            return "help"

        @registry.command("tools", category="tools")
        def cmd_tools(ctx):
            """Tools."""
            return "tools"

        by_category = registry.get_help_by_category()

        assert "general" in by_category
        assert "tools" in by_category
        assert len(by_category["general"]) == 1
        assert len(by_category["tools"]) == 1

    def test_command_names(self):
        registry = CommandRegistry()

        @registry.command("help")
        def cmd_help(ctx):
            """Help."""
            return "help"

        @registry.command("exit", aliases=["quit", "q"])
        def cmd_exit(ctx):
            """Exit."""
            return "exit"

        names = registry.command_names

        assert "help" in names
        assert "exit" in names
        assert "quit" in names
        assert "q" in names

    def test_get_command_for_completion(self):
        registry = CommandRegistry()

        @registry.command("help")
        def cmd_help(ctx):
            """Show help."""
            return "help"

        @registry.command("history", aliases=["h"])
        def cmd_history(ctx):
            """Show history."""
            return "history"

        names, descriptions = registry.get_command_for_completion()

        assert "help" in names
        assert "history" in names
        assert "h" in names
        assert descriptions["help"] == "Show help."
        assert "alias" in descriptions["h"].lower()


class TestArgumentSpec:
    """Test argument specifications."""

    def test_arg_helper(self):
        spec = arg(
            "format",
            required=True,
            default="json",
            description="Output format",
            choices=["json", "csv"],
        )

        assert spec.name == "format"
        assert spec.required is True
        assert spec.default == "json"
        assert spec.description == "Output format"
        assert spec.choices == ["json", "csv"]

    def test_arg_defaults(self):
        spec = arg("simple")

        assert spec.name == "simple"
        assert spec.required is False
        assert spec.default is None
        assert spec.description == ""
        assert spec.choices is None
