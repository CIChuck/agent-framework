"""
Configuration loading and validation for Friday Chat.

Contains:
- load_config: Load and validate YAML configuration
- _validate_config: Validate configuration structure
- print_banner: Display welcome banner with ASCII art
"""

import sys
from pathlib import Path
from typing import Any

import yaml

# Friday CLI display functions
from friday_cli import (
    display_error,
    display_info,
    display_warning,
    get_console,
)


def load_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from YAML file."""
    if not config_path.exists():
        display_error(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Validate config structure
    _validate_config(config, config_path)
    return config


def _validate_config(config: dict[str, Any], config_path: Path) -> None:
    """
    Validate config.yaml structure and required fields.

    Exits with descriptive error if validation fails.
    """
    errors: list[str] = []

    if not isinstance(config, dict):
        display_error(f"{config_path} must contain a YAML dictionary, got {type(config).__name__}")
        sys.exit(1)

    # Required sections
    if "llm" not in config:
        errors.append("Missing required section: 'llm'")
    else:
        llm = config["llm"]
        if not isinstance(llm, dict):
            errors.append("Section 'llm' must be a dictionary")
        elif not llm.get("model"):
            errors.append("Missing required field: 'llm.model'")

    if "embedding" not in config:
        errors.append("Missing required section: 'embedding'")
    else:
        embedding = config["embedding"]
        if not isinstance(embedding, dict):
            errors.append("Section 'embedding' must be a dictionary")
        elif not embedding.get("model"):
            errors.append("Missing required field: 'embedding.model'")

    # Optional sections with type validation
    optional_sections = {
        "memory": dict,
        "chat": dict,
        "extraction": dict,
        "maintenance": dict,
        "lifecycle": dict,
        "tools": dict,
        "logging": dict,
        "transcript": dict,
    }

    for section, expected_type in optional_sections.items():
        if section in config and not isinstance(config[section], expected_type):
            errors.append(f"Section '{section}' must be a {expected_type.__name__}, got {type(config[section]).__name__}")

    # Validate tools section if present
    if "tools" in config and isinstance(config["tools"], dict):
        tools = config["tools"]
        if "registry" in tools:
            if not isinstance(tools["registry"], list):
                errors.append("Section 'tools.registry' must be a list")
            else:
                for i, tool_def in enumerate(tools["registry"]):
                    if not isinstance(tool_def, dict):
                        errors.append(f"tools.registry[{i}] must be a dictionary")
                    elif not tool_def.get("name"):
                        errors.append(f"tools.registry[{i}] missing required field 'name'")
                    elif not tool_def.get("module"):
                        errors.append(f"tools.registry[{i}] ('{tool_def.get('name')}') missing required field 'module'")
                    elif not tool_def.get("class"):
                        errors.append(f"tools.registry[{i}] ('{tool_def.get('name')}') missing required field 'class'")

    if errors:
        display_error(f"Configuration errors in {config_path}:")
        for error in errors:
            display_warning(f"  {error}")
        display_info("Please fix the configuration and try again.")
        sys.exit(1)


def print_banner() -> None:
    """Print welcome banner with ASCII art logo - italic, larger, with shadow effect."""
    from rich.text import Text

    console = get_console()

    # Just main lines for cleaner approach
    logo_lines = [
        "          ███████╗██████╗ ██╗██████╗  █████╗ ██╗   ██╗",
        "         ██╔════╝██╔══██╗██║██╔══██╗██╔══██╗╚██╗ ██╔╝",
        "        █████╗  ██████╔╝██║██║  ██║███████║ ╚████╔╝ ",
        "       ██╔══╝  ██╔══██╗██║██║  ██║██╔══██║  ╚██╔╝  ",
        "      ██║     ██║  ██║██║██████╔╝██║  ██║   ██║   ",
        "     ╚═╝     ╚═╝  ╚═╝╚═╝╚═════╝ ╚═╝  ╚═╝   ╚═╝   ",
    ]

    # Define gradient colors (blue -> purple -> pink/rose)
    gradient_colors = [
        "#4A90D9",  # Blue
        "#5B7FD9",  # Blue-purple
        "#6C6ED9",  # Purple-blue
        "#7D5DD9",  # Purple
        "#8E4CD9",  # Purple-pink
        "#9F5CB8",  # Pink-purple
        "#B06C97",  # Pink
        "#C17C76",  # Rose-pink
        "#B08090",  # Muted rose
    ]

    # Shadow color (dark, muted)
    shadow_color = "#1a1a2e"

    console.print()  # Add some spacing

    # Print each line with inline shadow effect
    # Shadow is created by appending dark chars at the right edge
    for line in logo_lines:
        text = Text()
        line_len = len(line.rstrip())

        for i, char in enumerate(line):
            if char not in (" ", ""):
                # Main character with gradient
                progress = i / max(line_len - 1, 1) if line_len > 1 else 0
                color_idx = int(progress * (len(gradient_colors) - 1))
                color = gradient_colors[color_idx]
                text.append(char, style=f"bold {color}")
            else:
                text.append(char)

        # Add shadow trail at end of line
        text.append("\u2591", style=shadow_color)  # Light shade character

        console.print(text)

    # Shadow bottom edge (shifted right to align with italic slant)
    shadow_bottom = Text()
    shadow_bottom.append("    ", style="")
    for i in range(52):
        progress = i / 51
        color_idx = int(progress * (len(gradient_colors) - 1))
        # Use very dim version of gradient for bottom shadow
        shadow_bottom.append("\u2591", style=f"dim {gradient_colors[color_idx]}")
    console.print(shadow_bottom)

    console.print()  # Spacing after logo

    # Tips section (matching Gemini CLI style)
    tips = Text()
    tips.append("Tips for getting started:\n", style="dim white")
    tips.append("1. ", style="dim white")
    tips.append("Ask questions, edit files, or run commands.\n", style="white")
    tips.append("2. ", style="dim white")
    tips.append("Be specific for the best results.\n", style="white")
    tips.append("3. ", style="dim white")
    tips.append("/help", style="bold #9F5CB8")
    tips.append(" for more information.", style="white")

    console.print(tips)
    console.print()  # Final spacing
