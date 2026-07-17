# mypy: ignore-errors
"""
Command registry for CLI command dispatch.

Provides decorator-based command registration, argument parsing,
help generation, and aliasing support.

Ref: docs/archive/build-plans/completed/friday-core-legacy/memory-chat-v2-prd.md
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

# Type for command handler functions
T = TypeVar("T")  # Context type (e.g., MemoryChatSession)
CommandResult = str | None
SyncHandler = Callable[..., CommandResult]
AsyncHandler = Callable[..., Awaitable[CommandResult]]
Handler = SyncHandler | AsyncHandler


@dataclass
class ArgumentSpec:
    """Specification for a command argument."""

    name: str
    required: bool = False
    default: Any = None
    description: str = ""
    choices: list[str] | None = None


@dataclass
class CommandInfo:
    """Information about a registered command."""

    name: str
    handler: Handler
    description: str
    aliases: list[str] = field(default_factory=list)
    arguments: list[ArgumentSpec] = field(default_factory=list)
    is_async: bool = False
    category: str = "general"

    @property
    def usage(self) -> str:
        """Generate usage string for the command."""
        parts = [f"/{self.name}"]
        for arg in self.arguments:
            if arg.required:
                parts.append(f"<{arg.name}>")
            else:
                parts.append(f"[{arg.name}]")
        return " ".join(parts)

    @property
    def all_names(self) -> list[str]:
        """Get all names including aliases."""
        return [self.name] + self.aliases


@runtime_checkable
class CommandContext(Protocol):
    """Protocol for command context objects."""

    pass


class CommandRegistry(Generic[T]):
    """
    Registry for CLI commands with decorator-based registration.

    Usage:
        registry = CommandRegistry()

        @registry.command("history", aliases=["h"])
        async def cmd_history(ctx: Session) -> str:
            '''Show conversation history.'''
            return "History..."

        # Execute command
        result = await registry.execute("/history", session)
    """

    def __init__(self):
        """Initialize empty command registry."""
        self._commands: dict[str, CommandInfo] = {}
        self._aliases: dict[str, str] = {}  # alias -> canonical name

    def command(
        self,
        name: str,
        aliases: list[str] | None = None,
        arguments: list[ArgumentSpec] | None = None,
        category: str = "general",
    ) -> Callable[[Handler], Handler]:
        """
        Decorator to register a command handler.

        Args:
            name: Command name (without leading slash)
            aliases: Optional list of alternative names
            arguments: Optional list of argument specifications
            category: Category for grouping in help

        Returns:
            Decorator function

        Example:
            @registry.command("history", aliases=["h"])
            async def cmd_history(ctx) -> str:
                '''Show conversation history.'''
                return "..."
        """

        def decorator(func: Handler) -> Handler:
            # Extract description from docstring
            description = ""
            if func.__doc__:
                # Get first line of docstring
                description = func.__doc__.strip().split("\n")[0]

            # Check if async
            is_async = asyncio.iscoroutinefunction(func)

            # Create command info
            info = CommandInfo(
                name=name,
                handler=func,
                description=description,
                aliases=aliases or [],
                arguments=arguments or [],
                is_async=is_async,
                category=category,
            )

            # Register command
            self._commands[name] = info

            # Register aliases
            for alias in info.aliases:
                self._aliases[alias] = name

            return func

        return decorator

    def register(
        self,
        name: str,
        handler: Handler,
        aliases: list[str] | None = None,
        arguments: list[ArgumentSpec] | None = None,
        category: str = "general",
        description: str | None = None,
    ) -> None:
        """
        Programmatically register a command handler.

        Args:
            name: Command name (without leading slash)
            handler: Handler function
            aliases: Optional alternative names
            arguments: Optional argument specifications
            category: Category for grouping
            description: Optional description (overrides docstring)
        """
        # Extract description from docstring if not provided
        desc = description or ""
        if not desc and handler.__doc__:
            desc = handler.__doc__.strip().split("\n")[0]

        is_async = asyncio.iscoroutinefunction(handler)

        info = CommandInfo(
            name=name,
            handler=handler,
            description=desc,
            aliases=aliases or [],
            arguments=arguments or [],
            is_async=is_async,
            category=category,
        )

        self._commands[name] = info
        for alias in info.aliases:
            self._aliases[alias] = name

    def unregister(self, name: str) -> bool:
        """
        Remove a command from the registry.

        Args:
            name: Command name to remove

        Returns:
            True if command was removed, False if not found
        """
        if name not in self._commands:
            return False

        info = self._commands[name]
        del self._commands[name]

        # Remove aliases
        for alias in info.aliases:
            if alias in self._aliases:
                del self._aliases[alias]

        return True

    def get(self, name: str) -> CommandInfo | None:
        """
        Get command info by name or alias.

        Args:
            name: Command name or alias

        Returns:
            CommandInfo if found, None otherwise
        """
        # Check canonical name
        if name in self._commands:
            return self._commands[name]

        # Check aliases
        canonical = self._aliases.get(name)
        if canonical:
            return self._commands.get(canonical)

        return None

    def parse_input(self, user_input: str) -> tuple[str | None, list[str]]:
        """
        Parse user input into command name and arguments.

        Args:
            user_input: Raw user input string

        Returns:
            Tuple of (command_name, args) or (None, []) if not a command
        """
        if not user_input.startswith("/"):
            return None, []

        # Split on whitespace, preserving quoted strings
        parts = self._split_args(user_input[1:])  # Remove leading /
        if not parts:
            return None, []

        cmd_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        return cmd_name, args

    def _split_args(self, text: str) -> list[str]:
        """
        Split argument string, respecting quoted strings.

        Args:
            text: Input text to split

        Returns:
            List of arguments
        """
        # Simple regex to handle quoted strings
        pattern = r'(?:[^\s"\']+|"[^"]*"|\'[^\']*\')+'
        matches = re.findall(pattern, text)

        # Remove surrounding quotes
        result = []
        for match in matches:
            if (match.startswith('"') and match.endswith('"')) or (
                match.startswith("'") and match.endswith("'")
            ):
                result.append(match[1:-1])
            else:
                result.append(match)

        return result

    async def execute(
        self,
        user_input: str,
        context: T,
        **extra_kwargs: Any,
    ) -> tuple[bool, CommandResult]:
        """
        Execute a command from user input.

        Args:
            user_input: Raw user input (e.g., "/history --verbose")
            context: Context object passed to handler
            **extra_kwargs: Additional keyword arguments for handler

        Returns:
            Tuple of (was_command, result)
            - was_command: True if input was a command, False otherwise
            - result: Command result string or None
        """
        cmd_name, args = self.parse_input(user_input)

        if cmd_name is None:
            return False, None

        info = self.get(cmd_name)
        if info is None:
            return (
                True,
                f"Unknown command: /{cmd_name}. Type /help for available commands.",
            )

        # Build kwargs from arguments
        kwargs = self._build_kwargs(info, args)
        kwargs.update(extra_kwargs)

        try:
            if info.is_async:
                result = await info.handler(context, **kwargs)
            else:
                result = info.handler(context, **kwargs)

            # Handle cases where a non-async lambda returns a coroutine or Task
            # This supports patterns like: lambda ctx: asyncio.create_task(ctx.async_method())  # noqa: E501
            if asyncio.iscoroutine(result) or isinstance(result, asyncio.Task):
                result = await result

            return True, result
        except TypeError as e:
            # Likely argument mismatch
            return True, f"Error: {e}\nUsage: {info.usage}"
        except Exception as e:
            return True, f"Command error: {type(e).__name__}: {e}"

    def _build_kwargs(self, info: CommandInfo, args: list[str]) -> dict[str, Any]:
        """
        Build keyword arguments from positional args based on spec.

        Args:
            info: Command info with argument specs
            args: Positional arguments from user

        Returns:
            Dictionary of keyword arguments
        """
        kwargs: dict[str, Any] = {}

        for i, arg_spec in enumerate(info.arguments):
            if i < len(args):
                value = args[i]
                # Validate choices if specified
                if arg_spec.choices and value not in arg_spec.choices:
                    # Still pass the value, let handler validate
                    pass
                kwargs[arg_spec.name] = value
            elif arg_spec.default is not None:
                kwargs[arg_spec.name] = arg_spec.default
            elif not arg_spec.required:
                kwargs[arg_spec.name] = None

        # Pass remaining args as 'args' if there are more than spec
        if len(args) > len(info.arguments):
            kwargs["extra_args"] = args[len(info.arguments) :]

        return kwargs

    @property
    def commands(self) -> dict[str, CommandInfo]:
        """Get all registered commands."""
        return self._commands.copy()

    @property
    def command_names(self) -> list[str]:
        """Get list of all command names (including aliases)."""
        names = list(self._commands.keys())
        names.extend(self._aliases.keys())
        return sorted(set(names))

    def get_help(self, categories: bool = True) -> dict[str, str]:
        """
        Generate help text for all commands.

        Args:
            categories: Group commands by category

        Returns:
            Dict of command -> description (or category -> commands if categories=True)
        """
        if not categories:
            return {
                f"/{info.name}": info.description for info in self._commands.values()
            }

        # Group by category
        result: dict[str, str] = {}
        for info in sorted(self._commands.values(), key=lambda x: x.name):
            # Include aliases in display
            if info.aliases:
                alias_str = ", ".join(f"/{a}" for a in info.aliases)
                name = f"/{info.name} ({alias_str})"
            else:
                name = f"/{info.name}"

            result[name] = info.description

        return result

    def get_help_by_category(self) -> dict[str, dict[str, str]]:
        """
        Generate help text grouped by category.

        Returns:
            Dict of category -> {command -> description}
        """
        categories: dict[str, dict[str, str]] = {}

        for info in self._commands.values():
            if info.category not in categories:
                categories[info.category] = {}

            # Include aliases
            if info.aliases:
                alias_str = ", ".join(f"/{a}" for a in info.aliases)
                name = f"/{info.name} ({alias_str})"
            else:
                name = f"/{info.name}"

            categories[info.category][name] = info.description

        return categories

    def get_detailed_help(self, cmd_name: str) -> dict[str, Any] | None:
        """
        Get detailed help for a specific command.

        Args:
            cmd_name: Command name (with or without leading /)

        Returns:
            Dict with keys: name, description, usage, aliases, arguments, category
            or None if command not found
        """
        # Strip leading slash if present
        if cmd_name.startswith("/"):
            cmd_name = cmd_name[1:]

        info = self.get(cmd_name)
        if not info:
            return None

        return {
            "name": info.name,
            "description": info.description,
            "usage": info.usage,
            "aliases": info.aliases,
            "arguments": [
                {
                    "name": arg.name,
                    "required": arg.required,
                    "default": arg.default,
                    "description": arg.description,
                    "choices": arg.choices,
                }
                for arg in info.arguments
            ],
            "category": info.category,
        }

    def get_command_for_completion(self) -> tuple[list[str], dict[str, str]]:
        """
        Get command data formatted for InputHandler completion.

        Returns:
            Tuple of (command_names, descriptions)
        """
        names = []
        descriptions = {}

        for info in self._commands.values():
            names.append(info.name)
            descriptions[info.name] = info.description

            for alias in info.aliases:
                names.append(alias)
                descriptions[alias] = f"(alias for /{info.name}) {info.description}"

        return names, descriptions


# Convenience function to create argument specs
def arg(
    name: str,
    required: bool = False,
    default: Any = None,
    description: str = "",
    choices: list[str] | None = None,
) -> ArgumentSpec:
    """
    Create an argument specification.

    Args:
        name: Argument name
        required: Whether argument is required
        default: Default value if not provided
        description: Help text for argument
        choices: Valid values for argument

    Returns:
        ArgumentSpec instance
    """
    return ArgumentSpec(
        name=name,
        required=required,
        default=default,
        description=description,
        choices=choices,
    )
