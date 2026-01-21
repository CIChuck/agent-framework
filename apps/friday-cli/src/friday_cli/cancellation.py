"""
Cancellable async operations with keyboard interrupt support.

Allows users to cancel long-running operations (like LLM calls) by pressing
Escape, without exiting the entire CLI application.

Ref: docs/build-plan/memory-chat-v2-prd.md
"""

from __future__ import annotations

import asyncio
import sys
from typing import TypeVar, Coroutine, Any

from .display import get_console

T = TypeVar("T")


class OperationCancelledError(Exception):
    """Raised when an operation is cancelled by the user."""

    def __init__(self, message: str = "Operation cancelled by user"):
        self.message = message
        super().__init__(self.message)


class CancellationToken:
    """
    Token for cooperative cancellation of async operations.

    Usage:
        token = CancellationToken()

        async def my_operation():
            while not token.is_cancelled:
                # do work
                await asyncio.sleep(0.1)

        # In another task:
        token.cancel()
    """

    def __init__(self):
        self._cancelled = False
        self._cancel_event = asyncio.Event()

    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._cancelled

    def cancel(self) -> None:
        """Request cancellation."""
        self._cancelled = True
        self._cancel_event.set()

    async def wait_for_cancellation(self) -> None:
        """Wait until cancellation is requested."""
        await self._cancel_event.wait()

    def reset(self) -> None:
        """Reset the token for reuse."""
        self._cancelled = False
        self._cancel_event.clear()


def _is_real_terminal() -> bool:
    """Check if stdin is a real terminal (not redirected/piped)."""
    try:
        return sys.stdin.isatty() and hasattr(sys.stdin, "fileno")
    except Exception:
        return False


async def _check_for_escape_key(token: CancellationToken) -> None:
    """
    Monitor for Escape key press and trigger cancellation.

    This uses platform-specific methods to check for keyboard input
    without blocking the event loop.

    If stdin is not a real terminal (e.g., in tests or piped input),
    this function simply waits for the token to be cancelled externally.
    """
    # If not a real terminal, just wait (used in tests, piped input, etc.)
    if not _is_real_terminal():
        while not token.is_cancelled:
            await asyncio.sleep(0.1)
        return

    if sys.platform == "win32":
        # Windows: use msvcrt
        import msvcrt

        while not token.is_cancelled:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b"\x1b":  # Escape key
                    token.cancel()
                    return
            await asyncio.sleep(0.05)
    else:
        # Unix/Mac: use termios for raw input
        import termios
        import tty
        import select

        try:
            # Save terminal settings
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
        except (OSError, ValueError, AttributeError):
            # Can't access terminal - just wait for external cancellation
            while not token.is_cancelled:
                await asyncio.sleep(0.1)
            return

        try:
            # Set terminal to raw mode (no echo, immediate input)
            tty.setcbreak(fd)

            while not token.is_cancelled:
                # Check if input is available (non-blocking)
                if select.select([sys.stdin], [], [], 0.05)[0]:
                    key = sys.stdin.read(1)
                    if key == "\x1b":  # Escape key
                        token.cancel()
                        return
                await asyncio.sleep(0.01)
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


async def run_cancellable(
    operation: Coroutine[Any, Any, T],
    cancel_message: str = "Press [Esc] to cancel",
    show_hint: bool = True,
) -> T | None:
    """
    Run an async operation that can be cancelled by pressing Escape.

    Args:
        operation: The async coroutine to run
        cancel_message: Message shown to indicate cancellation is available
        show_hint: Whether to display the cancel hint

    Returns:
        The result of the operation, or None if cancelled

    Raises:
        OperationCancelledError: If the operation was cancelled by the user

    Usage:
        async def fetch_data():
            await asyncio.sleep(10)
            return "data"

        try:
            result = await run_cancellable(fetch_data())
            print(f"Got: {result}")
        except OperationCancelledError:
            print("User cancelled the operation")
    """
    console = get_console()
    token = CancellationToken()

    if show_hint:
        console.print(f"  [dim]{cancel_message}[/dim]")

    # Create tasks
    operation_task = asyncio.create_task(operation)
    escape_task = asyncio.create_task(_check_for_escape_key(token))

    try:
        # Wait for either the operation to complete or Escape to be pressed
        done, pending = await asyncio.wait(
            [operation_task, escape_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Cancel pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Check if operation completed or was cancelled
        if token.is_cancelled:
            raise OperationCancelledError()

        # Operation completed successfully
        return operation_task.result()

    except asyncio.CancelledError:
        # Propagate cancellation
        operation_task.cancel()
        escape_task.cancel()
        raise


class CancellableContext:
    """
    Context manager for running cancellable operations.

    Provides a cleaner interface when you need to run multiple
    cancellable operations in sequence.

    Usage:
        async with CancellableContext() as ctx:
            result = await ctx.run(some_async_operation())
            if ctx.was_cancelled:
                print("Operation was cancelled")
    """

    def __init__(self, show_hint: bool = True, cancel_message: str = "Press [Esc] to cancel"):
        self.show_hint = show_hint
        self.cancel_message = cancel_message
        self.was_cancelled = False
        self._hint_shown = False

    async def __aenter__(self) -> "CancellableContext":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        # Don't suppress OperationCancelledError - let it propagate
        return False

    async def run(self, operation: Coroutine[Any, Any, T]) -> T | None:
        """
        Run an operation that can be cancelled.

        Returns None if cancelled, otherwise returns the operation result.
        Sets was_cancelled flag if the operation was cancelled.
        """
        try:
            # Only show hint once per context
            show = self.show_hint and not self._hint_shown
            result = await run_cancellable(
                operation,
                cancel_message=self.cancel_message,
                show_hint=show,
            )
            self._hint_shown = True
            return result
        except OperationCancelledError:
            self.was_cancelled = True
            return None
