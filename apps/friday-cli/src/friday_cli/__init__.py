"""
Friday CLI - Rich terminal interface components.

Provides professional terminal output using the Rich library,
including status messages, tables, syntax highlighting, and progress indicators.

Ref: docs/build-plan/memory-chat-v2-prd.md
"""

from .cli_config import (
    CLIConfig,
    ThemeConfig,
    IconsConfig,
    PromptConfig,
    SpinnerConfig,
    get_cli_config,
    set_cli_config,
    load_cli_config,
)
from .display import (
    # Console management
    get_console,
    set_console,
    reset_console,
    # Status messages
    display_error,
    display_warning,
    display_success,
    display_info,
    # Structured data
    display_json,
    display_code,
    display_table,
    # Banners & panels
    display_banner,
    display_panel,
    display_separator,
    # Domain-specific
    display_help,
    display_tool_budget,
    display_memory_stats,
    display_entities,
    display_history,
    display_context_payload,
)
from .progress import (
    spinner,
    progress_bar,
    ProgressTracker,
    ThinkingIndicator,
)
from .input import (
    InputHandler,
    CommandCompleter,
    create_friday_input_handler,
    FRIDAY_COMMANDS,
    FRIDAY_COMMAND_DESCRIPTIONS,
)
from .commands import (
    CommandRegistry,
    CommandInfo,
    ArgumentSpec,
    arg,
)
from .session import (
    SessionConfig,
    SessionContext,
    SessionManager,
    managed_session,
    load_config,
    validate_config,
)
from .cancellation import (
    OperationCancelledError,
    CancellationToken,
    CancellableContext,
    run_cancellable,
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
