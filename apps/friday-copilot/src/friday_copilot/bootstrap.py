"""
Bootstrap utilities for Friday Copilot.

Provides cross-platform path resolution and configuration initialization
using XDG Base Directory standards (via platformdirs).
"""

from pathlib import Path
from typing import TypedDict

from platformdirs import user_config_dir, user_data_dir, user_log_dir


class FridayPaths(TypedDict):
    """Type definition for Friday directory paths."""

    config_dir: Path
    data_dir: Path
    log_dir: Path


def get_friday_paths() -> FridayPaths:
    """
    Return cross-platform paths for Friday data.

    Uses platformdirs for XDG-compliant paths:
    - Linux: ~/.config/friday, ~/.local/share/friday, ~/.local/state/friday
    - macOS: ~/Library/Application Support/friday (all three)
    - Windows: %APPDATA%/friday, %LOCALAPPDATA%/friday
    """
    return FridayPaths(
        config_dir=Path(user_config_dir("friday")),
        data_dir=Path(user_data_dir("friday")),
        log_dir=Path(user_log_dir("friday")),
    )


def bootstrap_config() -> Path:
    """
    Ensure config directory and default config exist.

    On first run, copies default_config.yaml from package resources
    to the user's config directory.

    Returns:
        Path to the config.yaml file
    """
    import importlib.resources

    paths = get_friday_paths()
    config_path = paths["config_dir"] / "config.yaml"

    if not config_path.exists():
        paths["config_dir"].mkdir(parents=True, exist_ok=True)
        # Copy from package resources
        try:
            default_config = importlib.resources.files(
                "friday_copilot.resources"
            ).joinpath("default_config.yaml")
            config_path.write_text(default_config.read_text())
        except Exception as e:
            # If resources aren't available, create minimal config
            config_path.write_text(_minimal_config())
            print(f"Warning: Could not load default config, created minimal: {e}")

    return config_path


def bootstrap_cli_config() -> Path:
    """
    Ensure CLI config exists in user config directory.

    On first run, copies default_cli_config.yaml from package resources
    to the user's config directory as cli-config.yaml.

    Returns:
        Path to the cli-config.yaml file
    """
    import importlib.resources

    paths = get_friday_paths()
    cli_config_path = paths["config_dir"] / "cli-config.yaml"

    if not cli_config_path.exists():
        paths["config_dir"].mkdir(parents=True, exist_ok=True)
        try:
            default_cli_config = importlib.resources.files(
                "friday_copilot.resources"
            ).joinpath("default_cli_config.yaml")
            cli_config_path.write_text(default_cli_config.read_text())
        except Exception:
            # CLI config is optional, skip if resources unavailable
            pass

    return cli_config_path


def bootstrap_data_dir() -> Path:
    """
    Ensure data directory exists.

    Creates the directory structure for:
    - vector/ (ChromaDB)
    - transcript.db (SQLite)
    - graph.json
    - exports/
    - reorganization_logs/

    Returns:
        Path to the data directory
    """
    paths = get_friday_paths()
    data_dir = paths["data_dir"]
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (data_dir / "exports").mkdir(exist_ok=True)
    (data_dir / "reorganization_logs").mkdir(exist_ok=True)

    return data_dir


def bootstrap_log_dir() -> Path:
    """
    Ensure log directory exists.

    Returns:
        Path to the log directory
    """
    paths = get_friday_paths()
    log_dir = paths["log_dir"]
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _minimal_config() -> str:
    """Return a minimal config for when resources aren't available."""
    return """\
# Friday Copilot Configuration
# This is a minimal configuration. Copy the full default_config.yaml for all options.

logging:
  level: INFO

llm:
  model: "openrouter/anthropic/claude-sonnet-4"
  api_base: "https://openrouter.ai/api/v1"
  api_key: "${OPENROUTER_API_KEY}"
  temperature: 0.4
  timeout_seconds: 60.0

embedding:
  model: "openai/nomic-embed-text-v1.5"
  api_base: "http://127.0.0.1:1234/v1"
  api_key: "lm-studio"

memory:
  persist_directory: null  # Uses platformdirs data directory
  context_window: 32000
  output_buffer: 1000

chat:
  user_name: "User"
  assistant_name: "Friday"
  system_prompt: |
    You are Friday, a helpful AI assistant with persistent memory.
"""
