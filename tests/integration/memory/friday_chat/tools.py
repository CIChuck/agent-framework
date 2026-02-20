"""
Tool registry management for Friday Chat.

Contains:
- build_tool_registry: Build registry from YAML configuration
- execute_tool: Execute a tool from the registry
- validate_tool_params: Validate parameters against schema
- validate_export_path: Path validation for security
"""

import importlib
import logging
from pathlib import Path
from typing import Any

from friday_tools import DefaultToolRegistry, GetCurrentDateTimeTool

logger = logging.getLogger(__name__)

# Module-level tool registry and schemas
# Initialized via init_tools() after config is loaded
TOOL_REGISTRY: DefaultToolRegistry | None = None
TOOL_SCHEMAS: list[dict[str, Any]] = []

# Debug flag - set via set_tools_debug() from config
_tools_debug: bool = False


def set_tools_debug(enabled: bool) -> None:
    """
    Enable or disable verbose tool loading/execution logging.

    Note: tools_debug only enables debug output if the global log level
    is INFO or more verbose. If global level is WARNING or ERROR,
    tools_debug has no effect.
    """
    global _tools_debug
    _tools_debug = enabled


def _debug(msg: str) -> None:
    """Log debug message if tools_debug is enabled and log level permits."""
    if _tools_debug and logger.isEnabledFor(logging.INFO):
        # Log at INFO level so it's visible when tools_debug is on
        # but respects WARNING/ERROR global settings
        logger.info(f"[Tools] {msg}")


def _load_tool_from_config(
    tool_config: dict[str, Any],
    web_config: dict[str, Any] | None = None,
    smart_file_llm: Any = None,
    smart_file_config: dict | None = None,
    shared_instances: dict[str, Any] | None = None,
) -> Any | None:
    """
    Dynamically load a tool class from configuration.

    Args:
        tool_config: Dictionary with module, class, and optional settings.
            Required keys: module, class
            Optional keys: enabled, constructor_args
        web_config: Web tools configuration (from config.yaml web: section).
            Automatically injected into tools from friday_tools.web module.
        smart_file_llm: LLM service for SmartFileReadTool summarization.
        smart_file_config: Configuration dict for SmartFileReadTool (from smart_file: section).
        shared_instances: Shared objects (e.g. MassiveAgentClient) to inject
            into tools that need them, avoiding duplicate expensive resources.

    Returns:
        Instantiated tool or None if disabled/failed to load.
    """  # noqa: E501
    tool_name = tool_config.get("name", "unknown")
    _debug(f"Loading tool: {tool_name}")

    # Check if tool is enabled (default: True)
    if not tool_config.get("enabled", True):
        _debug(f"Tool '{tool_name}' is disabled in configuration")
        return None

    try:
        module_name = tool_config.get("module")
        class_name = tool_config.get("class")

        if not module_name or not class_name:
            logger.warning(
                f"[Tools] Tool '{tool_name}' missing required 'module' or 'class' field"
            )
            return None

        _debug(f"Importing {module_name}.{class_name}")

        # Dynamic import
        module = importlib.import_module(module_name)
        tool_class = getattr(module, class_name)

        # Instantiate with optional constructor arguments
        constructor_args = tool_config.get("constructor_args", {})

        # Auto-inject web config for web tools (friday_tools.web module)
        if module_name == "friday_tools.web" and web_config:  # noqa: SIM102
            # Only inject if not already specified in constructor_args
            if "config" not in constructor_args:
                constructor_args["config"] = web_config
                _debug(f"Injected web config into {tool_name}")

        # Auto-inject smart_file dependencies for SmartFileReadTool
        if class_name == "SmartFileReadTool" and smart_file_llm:
            if "fallback_llm" not in constructor_args:
                constructor_args["fallback_llm"] = smart_file_llm
                _debug("Injected fallback_llm into SmartFileReadTool")
            if smart_file_config and "config" not in constructor_args:
                from friday_memory.ingestion.large_file_processor import (
                    LargeFileProcessorConfig,
                )

                constructor_args["config"] = LargeFileProcessorConfig(
                    auto_chunk_threshold_chars=smart_file_config.get(
                        "auto_chunk_threshold", 50000
                    ),
                    chunk_size=smart_file_config.get("chunk_size", 512),
                    chunk_overlap=smart_file_config.get("chunk_overlap", 50),
                )
                _debug("Injected config into SmartFileReadTool")

        # Auto-inject shared MassiveAgentClient for finance tools
        # (friday_tools.finance module).  All finance tools share a
        # single client so the Governor rate-limiter is applied
        # consistently.
        if (
            module_name == "friday_tools.finance"
            and shared_instances
            and "massive_client" in shared_instances
            and "client" not in constructor_args
        ):
            constructor_args["client"] = shared_instances["massive_client"]
            _debug(f"Injected shared MassiveAgentClient into {tool_name}")

        tool = tool_class(**constructor_args)

        _debug(f"Successfully loaded tool: {tool_name}")
        return tool

    except ImportError as e:
        logger.warning(
            f"[Tools] Failed to import tool module '{tool_config.get('module')}': {e}"
        )
        return None
    except AttributeError as e:
        logger.warning(
            f"[Tools] Tool class '{tool_config.get('class')}' not found in module: {e}"
        )
        return None
    except Exception as e:
        logger.warning(f"[Tools] Failed to instantiate tool '{tool_name}': {e}")
        return None


def build_tool_registry(
    tools_config: dict[str, Any] | None = None,
    web_config: dict[str, Any] | None = None,
    smart_file_llm: Any = None,
    smart_file_config: dict | None = None,
    finance_config: dict[str, Any] | None = None,
) -> DefaultToolRegistry:
    """
    Build a tool registry from YAML configuration.

    Args:
        tools_config: The 'tools' section from config.yaml.
            If None or tools.enabled is False, returns empty registry.
            If tools.registry is missing, falls back to default tools.
        web_config: The 'web' section from config.yaml.
            Automatically injected into web tools (friday_tools.web module).
        smart_file_llm: LLM service for SmartFileReadTool summarization.
        smart_file_config: Configuration dict for SmartFileReadTool (from smart_file: section).
        finance_config: The 'finance' section from config.yaml.
            Used to create a shared MassiveAgentClient for finance tools.

    Returns:
        DefaultToolRegistry populated with configured tools.
    """  # noqa: E501
    registry = DefaultToolRegistry()

    # Build shared instances for expensive objects that multiple tools share
    shared_instances: dict[str, Any] = {}
    massive_cfg = (finance_config or {}).get("massive", {})
    massive_api_key = massive_cfg.get("api_key")
    if massive_api_key:
        try:
            from friday_finance import MassiveAgentClient

            shared_instances["massive_client"] = MassiveAgentClient(
                api_key=str(massive_api_key),
                tier=massive_cfg.get("tier", "free"),
            )
            _debug(
                f"Created shared MassiveAgentClient "
                f"(tier={massive_cfg.get('tier', 'free')})"
            )
        except Exception as e:
            logger.warning(f"[Tools] Failed to create MassiveAgentClient: {e}")

    # Debug: log received config
    _debug(f"tools_config is None: {tools_config is None}")
    if tools_config:
        _debug(f"tools_config.enabled: {tools_config.get('enabled', 'NOT SET')}")
        _debug(
            f"tools_config.registry has {len(tools_config.get('registry', []))} entries"
        )

    # Check if tools are enabled
    if tools_config is None or not tools_config.get("enabled", True):
        logger.warning("[Tools] Tools disabled in configuration or config is None")
        return registry

    # Get tool registry list from config
    tool_definitions = tools_config.get("registry", [])

    if not tool_definitions:
        # Backward compatibility: if no registry defined, use default tools
        logger.warning("[Tools] No tools.registry in config, using default tools")
        registry.register(GetCurrentDateTimeTool())
        return registry

    # Debug: show tool names in registry
    tool_names_in_config = [t.get("name", "unnamed") for t in tool_definitions]
    _debug(f"Tools in config: {tool_names_in_config}")

    # Load each tool from configuration
    loaded_count = 0
    for tool_config in tool_definitions:
        tool = _load_tool_from_config(
            tool_config,
            web_config=web_config,
            smart_file_llm=smart_file_llm,
            smart_file_config=smart_file_config,
            shared_instances=shared_instances,
        )
        if tool:
            if not getattr(tool, "category", None) or tool.category == "uncategorized":
                raise ValueError(
                    f"Tool '{tool_config.get('name', tool.__class__.__name__)}' "
                    "must declare a non-default category."
                )
            registry.register(tool)
            loaded_count += 1

    logger.info(
        f"[Tools] Loaded {loaded_count}/{len(tool_definitions)} tools from configuration"  # noqa: E501
    )
    if loaded_count < len(tool_definitions):
        logger.warning(
            f"[Tools] Only loaded {loaded_count}/{len(tool_definitions)} tools - check for errors above"  # noqa: E501
        )
    return registry


def init_tools(
    tools_config: dict[str, Any] | None,
    web_config: dict[str, Any] | None,
    smart_file_llm: Any = None,
    smart_file_config: dict | None = None,
    finance_config: dict[str, Any] | None = None,
) -> tuple:
    """
    Initialize the global tool registry and schemas.

    Call this after loading configuration.

    Args:
        tools_config: The 'tools' section from config.yaml.
        web_config: The 'web' section from config.yaml.
        smart_file_llm: LLM service for SmartFileReadTool summarization.
        smart_file_config: Configuration dict for SmartFileReadTool (from smart_file: section).
        finance_config: The 'finance' section from config.yaml.

    Returns:
        Tuple of (TOOL_REGISTRY, TOOL_SCHEMAS) for convenience
    """  # noqa: E501
    global TOOL_REGISTRY, TOOL_SCHEMAS
    TOOL_REGISTRY = build_tool_registry(
        tools_config,
        web_config=web_config,
        smart_file_llm=smart_file_llm,
        smart_file_config=smart_file_config,
        finance_config=finance_config,
    )
    TOOL_SCHEMAS = TOOL_REGISTRY.get_schemas()
    return TOOL_REGISTRY, TOOL_SCHEMAS


async def execute_tool(tool_name: str, **kwargs) -> str:
    """
    Execute a tool from the registry.

    Args:
        tool_name: Name of the tool to execute.
        **kwargs: Tool parameters.

    Returns:
        Tool result as string.
    """
    if TOOL_REGISTRY is None:
        return "Tool registry not initialized"
    tool = TOOL_REGISTRY.get(tool_name)
    if tool is None:
        return f"Tool not found: {tool_name}"
    return await tool.execute(**kwargs)


def validate_export_path(
    path: Path, allowed_base: Path | None = None
) -> tuple[Path, str | None]:
    """
    Validate and resolve an export path to prevent path traversal.

    Args:
        path: The requested export path
        allowed_base: Base directory exports must stay within (default: current working directory)

    Returns:
        Tuple of (resolved_path, error_message). Error is None if path is valid.
    """  # noqa: E501
    if allowed_base is None:
        allowed_base = Path.cwd()

    try:
        # Resolve to absolute path (resolves symlinks and ..)
        resolved = path.resolve()
        allowed_resolved = allowed_base.resolve()

        # Check if resolved path is within allowed directory
        try:
            resolved.relative_to(allowed_resolved)
        except ValueError:
            return resolved, f"Export path must be within {allowed_resolved}"

        return resolved, None

    except Exception as e:
        return path, f"Invalid export path: {e}"


def validate_tool_params(
    params: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> str | None:
    """
    Validate tool parameters against JSON schema.

    Args:
        params: Parameters to validate
        schema: JSON schema for the tool's parameters
        tool_name: Tool name for error messages

    Returns:
        Error message if validation fails, None if valid
    """
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    # Check for missing required parameters
    missing = [r for r in required if r not in params]
    if missing:
        return f"Missing required parameter(s) for {tool_name}: {', '.join(missing)}"

    # Check for unknown parameters
    unknown = [p for p in params if p not in properties]
    if unknown:
        valid_params = ", ".join(properties.keys()) if properties else "(none)"
        return f"Unknown parameter(s) for {tool_name}: {', '.join(unknown)}\nValid parameters: {valid_params}"  # noqa: E501

    # Type validation for provided parameters
    type_errors = []
    for param_name, param_value in params.items():
        if param_name not in properties:
            continue

        expected_type = properties[param_name].get("type")
        if not expected_type:
            continue

        # Map JSON schema types to Python types
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        expected_python_type = type_map.get(expected_type)
        if expected_python_type and not isinstance(param_value, expected_python_type):
            type_errors.append(
                f"  - {param_name}: expected {expected_type}, got {type(param_value).__name__}"  # noqa: E501
            )

    if type_errors:
        return f"Type errors for {tool_name}:\n" + "\n".join(type_errors)

    return None  # Validation passed
