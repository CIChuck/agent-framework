"""
Friday Copilot - Full-featured AI assistant with persistent memory.

A command-line AI assistant that provides:
- Persistent memory across sessions (vector, graph, episodic stores)
- Memory lifecycle management (promotion, decay, reactivation)
- Tool execution and context injection
- Agent orchestration (Phase 3 - Project Hive)
- Workflow automation (Phase 4 - Project Hive)
- Rich terminal interface via friday-cli
"""

__version__ = "0.1.0"

from .bootstrap import (
    FridayPaths,
    bootstrap_cli_config,
    bootstrap_config,
    bootstrap_data_dir,
    bootstrap_log_dir,
    get_friday_paths,
)
from .main import async_main, run_app

__all__ = [
    "__version__",
    # Bootstrap
    "FridayPaths",
    "get_friday_paths",
    "bootstrap_config",
    "bootstrap_cli_config",
    "bootstrap_data_dir",
    "bootstrap_log_dir",
    # Entry points
    "run_app",
    "async_main",
]
