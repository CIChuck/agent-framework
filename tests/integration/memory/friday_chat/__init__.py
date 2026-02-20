"""
Friday Chat - Modular chat session package for friday-memory integration testing.

This package provides:
- TurnMetrics, TokenCounter, ContextMetrics: Data models
- Config loading and validation
- Tool registry management
- Command handlers (organized by category)
- LLM turn processing utilities
"""

from .commands import register_all_commands
from .config import load_config, print_banner
from .models import ContextMetrics, TokenCounter, TurnMetrics
from .processing import display_streaming_response, parse_text_tool_calls
from .tools import (
    TOOL_REGISTRY,
    TOOL_SCHEMAS,
    build_tool_registry,
    execute_tool,
    init_tools,
    set_tools_debug,
    validate_export_path,
    validate_tool_params,
)

__all__ = [
    # Models
    "TurnMetrics",
    "TokenCounter",
    "ContextMetrics",
    # Config
    "load_config",
    "print_banner",
    # Tools
    "build_tool_registry",
    "execute_tool",
    "init_tools",
    "set_tools_debug",
    "validate_tool_params",
    "validate_export_path",
    "TOOL_REGISTRY",
    "TOOL_SCHEMAS",
    # Processing
    "display_streaming_response",
    "parse_text_tool_calls",
    # Commands
    "register_all_commands",
]
