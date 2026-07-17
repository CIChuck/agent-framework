# mypy: ignore-errors
"""
Friday CLI - Rich terminal interface components.

Provides professional terminal output using the Rich library,
including status messages, tables, syntax highlighting, and progress indicators.

Ref: docs/archive/build-plans/completed/friday-core-legacy/memory-chat-v2-prd.md
"""

from .cancellation import (
    CancellableContext,
    CancellationToken,
    OperationCancelledError,
    run_cancellable,
)
from .cli_config import (
    CLIConfig,
    IconsConfig,
    PromptConfig,
    SpinnerConfig,
    ThemeConfig,
    get_cli_config,
    load_cli_config,
    set_cli_config,
)
from .commands import (
    ArgumentSpec,
    CommandInfo,
    CommandRegistry,
    arg,
)
from .display import (
    # Banners & panels
    display_banner,
    display_code,
    display_command_help,
    display_context_payload,
    display_entities,
    # Status messages
    display_error,
    # Domain-specific
    display_help,
    display_history,
    display_info,
    # Structured data
    display_json,
    display_memory_stats,
    display_panel,
    display_separator,
    display_success,
    display_table,
    display_tool_budget,
    display_warning,
    # Console management
    get_console,
    reset_console,
    set_console,
)
from .input import (
    FRIDAY_COMMAND_DESCRIPTIONS,
    FRIDAY_COMMANDS,
    CommandCompleter,
    InputHandler,
    create_friday_input_handler,
)
from .progress import (
    ProgressTracker,
    ThinkingIndicator,
    progress_bar,
    spinner,
)
from .session import (
    SessionConfig,
    SessionContext,
    SessionManager,
    load_config,
    managed_session,
    validate_config,
)

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # CLI configuration
    "CLIConfig",
    "ThemeConfig",
    "IconsConfig",
    "PromptConfig",
    "SpinnerConfig",
    "get_cli_config",
    "set_cli_config",
    "load_cli_config",
    # Console management
    "get_console",
    "set_console",
    "reset_console",
    # Status messages
    "display_error",
    "display_warning",
    "display_success",
    "display_info",
    # Structured data
    "display_json",
    "display_code",
    "display_table",
    # Banners & panels
    "display_banner",
    "display_panel",
    "display_separator",
    # Domain-specific
    "display_help",
    "display_command_help",
    "display_tool_budget",
    "display_memory_stats",
    "display_entities",
    "display_history",
    "display_context_payload",
    # Progress indicators
    "spinner",
    "progress_bar",
    "ProgressTracker",
    "ThinkingIndicator",
    # Input handling
    "InputHandler",
    "CommandCompleter",
    "create_friday_input_handler",
    "FRIDAY_COMMANDS",
    "FRIDAY_COMMAND_DESCRIPTIONS",
    # Command registry
    "CommandRegistry",
    "CommandInfo",
    "ArgumentSpec",
    "arg",
    # Session management
    "SessionConfig",
    "SessionContext",
    "SessionManager",
    "managed_session",
    "load_config",
    "validate_config",
    # Cancellation support
    "OperationCancelledError",
    "CancellationToken",
    "CancellableContext",
    "run_cancellable",
]
