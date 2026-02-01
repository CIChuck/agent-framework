"""
Progress indicators for long-running operations.

Provides spinners and progress bars using Rich, with async compatibility.

Ref: docs/build-plan/memory-chat-v2-prd.md
"""

from __future__ import annotations

import random
from collections.abc import Iterator
from contextlib import contextmanager

from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.status import Status

from .display import get_console
from .cli_config import get_cli_config


@contextmanager
def spinner(message: str, spinner_type: str = "dots") -> Iterator[Status]:
    """
    Display a spinner during a long-running operation.

    Usage:
        with spinner("Loading..."):
            # do work
            pass

    Or for updates:
        with spinner("Processing...") as status:
            status.update("Step 1...")
            # do step 1
            status.update("Step 2...")
            # do step 2

    Args:
        message: Status message to display
        spinner_type: Type of spinner animation (default: dots)

    Yields:
        Rich Status object for updating the message
    """
    console = get_console()
    status = Status(message, console=console, spinner=spinner_type)
    try:
        status.start()
        yield status
    finally:
        status.stop()


@contextmanager
def progress_bar(
    total: int,
    description: str = "Processing",
    show_speed: bool = False,  # noqa: ARG001 - reserved for future use
) -> Iterator[Progress]:
    """
    Display a progress bar for operations with known duration.

    Usage:
        with progress_bar(100, "Downloading") as progress:
            task = progress.add_task("file.txt", total=100)
            for i in range(100):
                # do work
                progress.update(task, advance=1)

    Args:
        total: Total number of steps
        description: Description of the operation
        show_speed: Whether to show items/second

    Yields:
        Rich Progress object for tracking progress
    """
    console = get_console()

    columns = [
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    ]

    progress = Progress(*columns, console=console)
    try:
        progress.start()
        # Add a default task
        progress.add_task(description, total=total)
        yield progress
    finally:
        progress.stop()


class ProgressTracker:
    """
    Helper class for tracking multi-step progress.

    Usage:
        tracker = ProgressTracker(steps=["Load", "Process", "Save"])
        with tracker:
            tracker.advance("Loading data...")
            # do load
            tracker.advance("Processing...")
            # do process
            tracker.advance("Saving...")
            # do save
            tracker.complete()
    """

    def __init__(self, steps: list[str], title: str = "Progress"):
        """
        Initialize progress tracker.

        Args:
            steps: List of step names
            title: Overall title for the progress
        """
        self.steps = steps
        self.title = title
        self.current_step = 0
        self._progress: Progress | None = None
        self._task_id: int | None = None

    def __enter__(self) -> ProgressTracker:
        """Start tracking progress."""
        console = get_console()
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        )
        self._progress.start()
        self._task_id = self._progress.add_task(
            self.steps[0] if self.steps else self.title,
            total=len(self.steps),
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop tracking progress."""
        if self._progress:
            self._progress.stop()

    def advance(self, description: str | None = None) -> None:
        """
        Advance to the next step.

        Args:
            description: Optional description override
        """
        if self._progress and self._task_id is not None:
            self.current_step += 1
            desc = description or (
                self.steps[self.current_step - 1]
                if self.current_step <= len(self.steps)
                else "Complete"
            )
            self._progress.update(self._task_id, advance=1, description=desc)

    def complete(self, message: str = "Complete") -> None:
        """Mark the progress as complete."""
        if self._progress and self._task_id is not None:
            remaining = len(self.steps) - self.current_step
            if remaining > 0:
                self._progress.update(
                    self._task_id,
                    advance=remaining,
                    description=message,
                )


class ThinkingIndicator:
    """
    Manual spinner for async operations like LLM calls.

    Unlike the spinner() context manager, this can be manually started
    and stopped - perfect for streaming responses where you want to
    show a spinner until the first chunk arrives.

    Usage:
        # With random messages from config:
        indicator = ThinkingIndicator.random_thinking()
        indicator.start()

        async for chunk in llm.stream():
            indicator.stop()  # Stop on first chunk (safe to call multiple times)
            print(chunk, end="", flush=True)

        # Or with explicit message:
        indicator = ThinkingIndicator("Custom message...")
        indicator.start()

    Or as context manager for non-streaming:
        with ThinkingIndicator.random_thinking():
            result = await llm.complete(prompt)

    Features:
        - Safe to call stop() multiple times (idempotent)
        - Can be used as context manager or manually
        - Configurable message and spinner style
        - Random message selection from cli-config.yaml
        - Uses theme's highlight color for the message
    """

    def __init__(
        self,
        message: str = "Thinking...",
        spinner_type: str | None = None,
    ):
        """
        Initialize thinking indicator.

        Args:
            message: Message to display while thinking
            spinner_type: Rich spinner animation type (dots, line, dots12, etc.)
                         If None, uses spinner_type from cli-config.yaml
        """
        self.message = message
        # Use config spinner_type if not explicitly provided
        if spinner_type is None:
            config = get_cli_config()
            self.spinner_type = config.spinner.spinner_type
        else:
            self.spinner_type = spinner_type
        self._status: Status | None = None
        self._running = False

    @classmethod
    def random_thinking(cls) -> "ThinkingIndicator":
        """
        Create a ThinkingIndicator with a random thinking message.

        Uses thinking_messages from cli-config.yaml spinner settings.
        If randomize is False, uses the first message.

        Returns:
            ThinkingIndicator with random (or first) thinking message
        """
        config = get_cli_config()
        messages = config.spinner.thinking_messages

        if config.spinner.randomize and len(messages) > 1:
            message = random.choice(messages)
        else:
            message = messages[0] if messages else "Thinking..."

        return cls(message=message, spinner_type=config.spinner.spinner_type)

    @classmethod
    def random_tool_processing(cls) -> "ThinkingIndicator":
        """
        Create a ThinkingIndicator with a random tool processing message.

        Uses tool_messages from cli-config.yaml spinner settings.
        If randomize is False, uses the first message.

        Returns:
            ThinkingIndicator with random (or first) tool processing message
        """
        config = get_cli_config()
        messages = config.spinner.tool_messages

        if config.spinner.randomize and len(messages) > 1:
            message = random.choice(messages)
        else:
            message = messages[0] if messages else "Processing..."

        return cls(message=message, spinner_type=config.spinner.spinner_type)

    @property
    def is_running(self) -> bool:
        """Check if the indicator is currently running."""
        return self._running

    def start(self) -> None:
        """Start the thinking indicator."""
        if self._running:
            return  # Already running

        console = get_console()
        config = get_cli_config()

        # Use separate styles for text and spinner animation
        text_style = config.spinner.text_style
        spinner_style = config.spinner.spinner_style
        styled_message = f"[{text_style}]{self.message}[/{text_style}]"

        self._status = Status(
            styled_message,
            console=console,
            spinner=self.spinner_type,
            spinner_style=spinner_style,
        )
        self._status.start()
        self._running = True

    def stop(self) -> None:
        """
        Stop the thinking indicator.

        Safe to call multiple times - only stops if running.
        """
        if not self._running or self._status is None:
            return

        self._status.stop()
        self._status = None
        self._running = False

    def update(self, message: str) -> None:
        """
        Update the thinking message.

        Args:
            message: New message to display
        """
        if self._status and self._running:
            config = get_cli_config()
            text_style = config.spinner.text_style
            styled_message = f"[{text_style}]{message}[/{text_style}]"
            self._status.update(styled_message)

    def __enter__(self) -> "ThinkingIndicator":
        """Start indicator when entering context."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop indicator when exiting context."""
        self.stop()

    async def __aenter__(self) -> "ThinkingIndicator":
        """Async context manager support."""
        self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager support."""
        self.stop()
