#!/usr/bin/env python3
"""
Friday-Memory Integration Test - Memory Chat CLI v2

A refactored version of memory-chat.py using friday-cli display components
for professional Rich-based terminal output.

A command-line chat application that tests friday-memory's context engineering
components through an interactive chat interface with persistent memory.

Tests:
- ContextAssembler (context orchestration)
- PromptArchitect (token budgeting)
- MemoryController (unified memory facade)
- All three memory stores (episodic, vector, graph)
- ChromaDB persistence to disk

Usage:
    python memory-chat.py [--config CONFIG_PATH]

Commands (prefix with /):
  /exit, /quit     - Exit the chat
  /clear           - Clear conversation history
  /history         - Show conversation history
  /memory          - Show memory statistics
  /context [--debug] - Show context payload (--debug for token counts)
  /prompt          - Show full formatted prompt sent to LLM (FULL, no truncation)
  /prime           - Load and show primed context (works before first turn)
  /debug           - Show debug info from context assembly
  /entities        - List graph entities and relationships
  /facts           - List all documents from vector store (insights + summaries)
  /insights        - List only insights (type='insight') with structured metadata
  /summaries       - List only turn summaries (type='summary')
  /meta            - List only meta insights (type='meta_insight') from synthesis
  /sessions        - List all stored transcript sessions
  /transcript      - Show current session's transcript
  /transcript <id> - Show transcript for a specific session
  /transcript export - Export entire database to CSV
  /export [format] - Export current session (jsonl, markdown, or training)
  /reset           - Clear all memory stores (graph, vector, episodic)
  /reorganize [opts] - Run memory reorganization (analyze, prune, synthesize)
  /migrate [opts]  - Migrate existing memories to lifecycle metadata
  /lifecycle [opts] - Run memory lifecycle cycle (promotion, decay, reactivation)
  /vars            - Show scoped variables
  /set <key> <val> - Set a scoped variable
  /tools [category] - List available tools, optionally filter by category
  /run-tool <name> [json] - Execute a tool with optional JSON parameters
  /inject-tools <names> - Inject tools into context for testing
  /clear-tools       - Clear all injected tools from context
  /recommend-tools <query> - Test tool recommendations for a query
  /tool-budget       - Show tool token budget information
  /help            - Show available commands
"""

import asyncio
import importlib
import json
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Friday CLI display functions
from friday_cli import (
    display_error,
    display_warning,
    display_success,
    display_info,
    display_json,
    display_code,
    display_table,
    display_banner,
    display_panel,
    display_separator,
    display_help,
    display_tool_budget,
    display_memory_stats,
    display_entities,
    display_history,
    display_context_payload,
    spinner,
    progress_bar,
    ThinkingIndicator,
    get_console,
    reset_console,
    # Input handling
    create_friday_input_handler,
    # Command registry
    CommandRegistry,
    arg,
    # Session management
    SessionConfig,
    validate_config,
    # CLI configuration
    load_cli_config,
    # Cancellation support
    OperationCancelledError,
    run_cancellable,
)

# Logging will be configured after config is loaded (see main())
logger = logging.getLogger(__name__)

from friday_core import DebugTelemetryRecorder, TranscriptBackedEpisodicStore
from friday_core.interfaces.llm import ChatCompletionResponse, ToolCall
from friday_llm import (
    CircuitBreakerOpenError,
    LiteLLMEmbeddingService,
    LiteLLMService,
    LLMRetryExhaustedError,
    LLMTimeoutError,
    ResilienceConfig,
)
from friday_memory import (
    AccessBuffer,
    AccessBufferConfig,
    ChromaVectorStore,
    CollectionConfig,
    CollectionManager,
    ContextAssembler,
    ContextPayload,
    DecayConfig,
    ElementXGraphStore,
    FactorComputerConfig,
    GraphPathScorer,
    GraphPathScorerConfig,
    InteractionTurn,
    MemoryController,
    MemoryExtractor,
    MemoryPromotionService,
    PromptArchitect,
    PromotionResult,
    RetrievalFactorComputer,
    SessionState,
)
from friday_memory.maintenance import MemoryReorganizer
from friday_memory.maintenance.models import (
    EmbeddingConfig,
    FactCheckConfig,
    LifecycleDecayConfig,
    LogConfig,
    LogFormat,
    LogVerbosity,
    MaintenanceConfig,
    PromptsConfig,
    PruneConfig,
    SynthesisConfig,
)
from friday_transcript import (
    CSVExporter,
    JSONLExporter,
    MarkdownExporter,
    SQLiteTranscriptStore,
    TranscriptSession,
)
from friday_tools import (
    DefaultToolRegistry,
    GetCurrentDateTimeTool,
)


# =============================================================================
# FRIDAY-TOOLS INTEGRATION
# =============================================================================
# Tools are loaded dynamically from YAML configuration (config.yaml).
# The tool registry is populated with FridayTool instances based on the
# tools.registry section of the config file.
#
# To add new tools, edit config.yaml and add entries to tools.registry.
# No code changes required for adding/removing tools.
# =============================================================================


def _load_tool_from_config(tool_config: dict[str, Any]) -> Any | None:
    """
    Dynamically load a tool class from configuration.

    Args:
        tool_config: Dictionary with module, class, and optional settings.
            Required keys: module, class
            Optional keys: enabled, constructor_args

    Returns:
        Instantiated tool or None if disabled/failed to load.
    """
    tool_name = tool_config.get("name", "unknown")

    # Check if tool is enabled (default: True)
    if not tool_config.get("enabled", True):
        logger.info(f"Tool '{tool_name}' is disabled in configuration")
        return None

    try:
        module_name = tool_config.get("module")
        class_name = tool_config.get("class")

        if not module_name or not class_name:
            logger.warning(f"Tool '{tool_name}' missing required 'module' or 'class' field")
            return None

        # Dynamic import
        module = importlib.import_module(module_name)
        tool_class = getattr(module, class_name)

        # Instantiate with optional constructor arguments
        constructor_args = tool_config.get("constructor_args", {})
        tool = tool_class(**constructor_args)

        logger.debug(f"Loaded tool: {tool_name} from {module_name}.{class_name}")
        return tool

    except ImportError as e:
        logger.warning(f"Failed to import tool module '{tool_config.get('module')}': {e}")
        return None
    except AttributeError as e:
        logger.warning(f"Tool class '{tool_config.get('class')}' not found in module: {e}")
        return None
    except Exception as e:
        logger.warning(f"Failed to instantiate tool '{tool_name}': {e}")
        return None


def _build_tool_registry(tools_config: dict[str, Any] | None = None) -> DefaultToolRegistry:
    """
    Build a tool registry from YAML configuration.

    Args:
        tools_config: The 'tools' section from config.yaml.
            If None or tools.enabled is False, returns empty registry.
            If tools.registry is missing, falls back to default tools.

    Returns:
        DefaultToolRegistry populated with configured tools.
    """
    registry = DefaultToolRegistry()

    # Check if tools are enabled
    if tools_config is None or not tools_config.get("enabled", True):
        logger.info("Tools disabled in configuration")
        return registry

    # Get tool registry list from config
    tool_definitions = tools_config.get("registry", [])

    if not tool_definitions:
        # Backward compatibility: if no registry defined, use default tools
        logger.info("No tools.registry in config, using default tools")
        registry.register(GetCurrentDateTimeTool())
        return registry

    # Load each tool from configuration
    loaded_count = 0
    for tool_config in tool_definitions:
        tool = _load_tool_from_config(tool_config)
        if tool:
            registry.register(tool)
            loaded_count += 1

    logger.info(f"Loaded {loaded_count}/{len(tool_definitions)} tools from configuration")
    return registry


# Note: TOOL_REGISTRY and TOOL_SCHEMAS are initialized in main() after config is loaded.
# This allows tools to be configured via YAML without code changes.
TOOL_REGISTRY: DefaultToolRegistry | None = None
TOOL_SCHEMAS: list[dict[str, Any]] = []


async def _execute_tool(tool_name: str, **kwargs) -> str:
    """
    Execute a tool from the registry.

    Args:
        tool_name: Name of the tool to execute.
        **kwargs: Tool parameters.

    Returns:
        Tool result as string.
    """
    tool = TOOL_REGISTRY.get(tool_name)
    if tool is None:
        return f"Tool not found: {tool_name}"
    return await tool.execute(**kwargs)


def _validate_export_path(path: Path, allowed_base: Path | None = None) -> tuple[Path, str | None]:
    """
    Validate and resolve an export path to prevent path traversal.

    Args:
        path: The requested export path
        allowed_base: Base directory exports must stay within (default: current working directory)

    Returns:
        Tuple of (resolved_path, error_message). Error is None if path is valid.
    """
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


def _validate_tool_params(
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
        return f"Unknown parameter(s) for {tool_name}: {', '.join(unknown)}\nValid parameters: {valid_params}"

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
                f"  - {param_name}: expected {expected_type}, got {type(param_value).__name__}"
            )

    if type_errors:
        return f"Type errors for {tool_name}:\n" + "\n".join(type_errors)

    return None  # Validation passed


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
    """Print welcome banner using Rich display."""
    display_banner(
        title="Friday-Memory Integration Test CLI v2",
        subtitle="Type your message and press Enter to chat.\nType /help for available commands.\nType /exit or /quit to end the conversation.",
        version="0.1.0",
    )


class MemoryChatSession:
    """Manages a multi-turn chat session with memory integration."""

    def __init__(
        self,
        llm: LiteLLMService,
        controller: MemoryController,
        assembler: ContextAssembler,
        architect: PromptArchitect,
        system_prompt: str,
        session_id: str,
        user_id: str,
        temperature: float = 0.7,
        max_history_turns: int = 10,
        extractor: "MemoryExtractor | None" = None,
        user_name: str = "You",
        assistant_name: str = "Assistant",
        transcript_store: "SQLiteTranscriptStore | None" = None,
        context_format: str = "plain",
        persist_dir: "Path | None" = None,
        maintenance_config: "MaintenanceConfig | None" = None,
        maintenance_llms: "dict[str, LiteLLMService] | None" = None,
        transcript_export_dir: "Path | None" = None,
        embedding_function: Any = None,
        promotion_service: "MemoryPromotionService | None" = None,
        access_buffer: "AccessBuffer | None" = None,
        factor_computer: "RetrievalFactorComputer | None" = None,
    ):
        self.llm = llm
        self.controller = controller
        self.assembler = assembler
        self.architect = architect
        self.system_prompt = system_prompt
        self.session_id = session_id
        self.user_id = user_id
        self.temperature = temperature
        self.max_history_turns = max_history_turns
        self.extractor = extractor
        self.user_name = user_name
        self.assistant_name = assistant_name
        self.transcript_store = transcript_store
        self.context_format = context_format
        self.persist_dir = persist_dir
        self.maintenance_config = maintenance_config
        self.maintenance_llms = maintenance_llms or {}
        self.transcript_export_dir = transcript_export_dir
        self.embedding_function = embedding_function
        self.promotion_service = promotion_service
        self.access_buffer = access_buffer
        self.factor_computer = factor_computer

        # State tracking
        self.state: SessionState | None = None
        self.last_payload: ContextPayload | None = None
        self.last_messages: list[dict[str, Any]] | None = None  # Last formatted prompt
        self.turn_ids: list[str] = []

        # Command registry for extensible command handling
        # Commands can be registered using the @registry.command decorator
        # or programmatically with registry.register()
        self.registry: CommandRegistry["MemoryChatSession"] = CommandRegistry()
        self._register_commands()

    def _register_commands(self) -> None:
        """Register commands with the CommandRegistry.

        This demonstrates the registry pattern for command handling.
        Commands can be added here or via decorator on methods.
        """
        # Example: Register exit/quit with aliases
        self.registry.register(
            "exit",
            lambda ctx: "EXIT",
            aliases=["quit", "q"],
            description="Exit the chat",
            category="session",
        )

        # Example: Register help command that uses the registry
        def cmd_help_registry(ctx):
            """Show available commands."""
            commands = ctx.registry.get_help()
            display_help(commands)
            return None  # display_help handles output

        self.registry.register(
            "help-new",
            cmd_help_registry,
            aliases=["?"],
            description="Show available commands (registry version)",
            category="general",
        )

    async def initialize(self) -> None:
        """Initialize the session state."""
        self.state = await self.assembler.initialize_session(
            self.session_id, self.user_id
        )
        # Set some default scoped variables
        self.state.set_var("user:id", self.user_id)
        self.state.set_var("session:started", datetime.now().isoformat())

    async def handle_command(self, user_input: str) -> str | None:
        """Handle /commands. Returns response string or None if not a command."""
        if not user_input.startswith("/"):
            return None  # Not a command, process as chat

        # First, try the CommandRegistry for registered commands
        # This allows gradual migration of commands to the registry pattern
        cmd_name, _ = self.registry.parse_input(user_input)
        if cmd_name and self.registry.get(cmd_name):
            was_command, result = await self.registry.execute(user_input, self)
            if was_command:
                return result

        # Fall back to legacy match/case for commands not yet in registry
        parts = user_input[1:].split(maxsplit=2)  # Remove "/" and split
        cmd = parts[0].lower() if parts else ""

        match cmd:
            # Note: exit/quit now handled by registry, but kept here for reference
            case "exit" | "quit":
                return "EXIT"  # Special signal to exit loop
            case "clear":
                return self.cmd_clear()
            case "history":
                return await self.cmd_history()
            case "memory":
                return self.cmd_memory()
            case "context":
                # Check for --debug flag
                debug_mode = "--debug" in parts[1] if len(parts) > 1 else False
                return self.cmd_context(debug_mode=debug_mode)
            case "prompt":
                return self.cmd_prompt()
            case "debug":
                return self.cmd_debug()
            case "entities":
                return await self.cmd_entities()
            case "facts":
                return await self.cmd_facts()
            case "insights":
                return await self.cmd_insights()
            case "summaries":
                return await self.cmd_summaries()
            case "meta":
                return await self.cmd_meta_insights()
            case "prime":
                return await self.cmd_prime()
            case "sessions":
                return await self.cmd_sessions()
            case "transcript":
                # Check for subcommands: /transcript <session_id> or /transcript export
                arg = parts[1] if len(parts) > 1 else None
                return await self.cmd_transcript(arg)
            case "export":
                format_type = parts[1] if len(parts) > 1 else "markdown"
                return await self.cmd_export(format_type)
            case "reset":
                return await self.cmd_reset()
            case "reorganize":
                # Parse options from remaining args
                opts = parts[1] if len(parts) > 1 else ""
                return await self.cmd_reorganize(opts)
            case "lifecycle":
                # Parse options from remaining args
                opts = parts[1] if len(parts) > 1 else ""
                return await self.cmd_lifecycle(opts)
            case "vars":
                return self.cmd_vars()
            case "set":
                if len(parts) >= 3:
                    return self.cmd_set(parts[1], parts[2])
                return "Usage: /set <key> <value>"
            case "migrate":
                opts = parts[1] if len(parts) > 1 else ""
                return await self.cmd_migrate(opts)
            case "tools":
                category = parts[1] if len(parts) > 1 else None
                return self.cmd_tools(category)
            case "run-tool":
                # Join all parts after "run-tool" (tool name + params)
                args = " ".join(parts[1:]) if len(parts) > 1 else ""
                return await self.cmd_run_tool(args)
            case "inject-tools":
                tool_names = parts[1] if len(parts) > 1 else ""
                return self.cmd_inject_tools(tool_names)
            case "clear-tools":
                return self.cmd_clear_tools()
            case "recommend-tools":
                query = parts[1] if len(parts) > 1 else ""
                return self.cmd_recommend_tools(query)
            case "tool-budget":
                return self.cmd_tool_budget()
            case "help":
                return self.cmd_help()
            case _:
                return f"Unknown command: /{cmd}. Type /help for available commands."

    def cmd_clear(self) -> str:
        """Clear conversation history."""
        self.turn_ids.clear()
        self.last_payload = None
        if self.state:
            self.state.turn_count = 0
        return "Conversation history cleared."

    async def cmd_history(self) -> str:
        """Show conversation history including prior sessions with timestamps."""
        try:
            # Get merged history from last_payload if available (includes prior sessions)
            prior_history = []
            if self.last_payload and self.last_payload.prior_history:
                prior_history = self.last_payload.prior_history

            # Fetch current session history from episodic store
            current_turns = await self.controller.episodic.get_turns(self.session_id, limit=100)

            # Combine: prior sessions first, then current session
            all_turns = list(prior_history) + list(current_turns)

            if not all_turns:
                return "No conversation history yet."

            # Count turns by type
            prior_count = len(prior_history)
            current_count = len(current_turns)

            lines = [
                "=" * 60,
                f"CONVERSATION HISTORY ({len(all_turns)} total turns)",
                f"  Prior sessions: {prior_count} turns",
                f"  Current session: {current_count} turns",
                "=" * 60
            ]

            for i, turn in enumerate(all_turns, 1):
                # Format timestamp
                timestamp = turn.timestamp.strftime("%Y-%m-%d %H:%M") if turn.timestamp else "N/A"

                # Check if this is from a prior session
                is_prior = turn.metadata.get("from_prior_session", False) if turn.metadata else False
                session_marker = " [prior]" if is_prior else ""

                user_msg = turn.user_message[:100] + "..." if len(turn.user_message or "") > 100 else (turn.user_message or "")
                asst_msg = turn.assistant_message[:100] + "..." if len(turn.assistant_message or "") > 100 else (turn.assistant_message or "")
                user_msg = user_msg.replace("\n", " ")
                asst_msg = asst_msg.replace("\n", " ")

                lines.append(f"\n  [{timestamp}]{session_marker} Turn {i}:")
                lines.append(f"    {self.user_name}: {user_msg}")
                lines.append(f"    {self.assistant_name}: {asst_msg}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving history: {e}"

    def cmd_memory(self) -> str:
        """Show memory statistics."""
        turn_count = self.state.turn_count if self.state else 0
        var_count = len(self.state.scoped_vars) if self.state else 0
        return f"""
Memory Statistics:
  Session ID: {self.session_id}
  Turns in session: {turn_count}
  Turn IDs tracked: {len(self.turn_ids)}
  Scoped variables: {var_count}
"""

    def cmd_context(self, debug_mode: bool = False) -> str:
        """
        Show detailed context assembly in configured format (FULL content).

        With --debug flag, shows additional token counts per section.
        """
        if not self.last_payload:
            return "No context assembled yet. Send a message first or use /prime."

        lines = ["=" * 60, f"CONTEXT PAYLOAD (format: {self.context_format})", "=" * 60]

        # Summary counts
        lines.append(f"\nSummary:")
        lines.append(f"  Prior session turns: {len(self.last_payload.prior_history)}")
        lines.append(f"  Current session turns: {len(self.last_payload.history)}")
        lines.append(f"  Vector passages: {len(self.last_payload.passages)}")
        lines.append(f"  Graph entities: {len(self.last_payload.entities)}")
        lines.append(f"  Graph facts (edges): {len(self.last_payload.facts)}")
        lines.append(f"  Key facts (natural language): {len(self.last_payload.key_facts)}")
        lines.append(f"  Relationship summaries: {len(self.last_payload.recent_memories)}")
        lines.append(f"  Insights: {len(self.last_payload.insights)}")
        lines.append(f"  Summaries: {len(self.last_payload.summaries)}")

        # Debug mode: show token counts and additional info
        if debug_mode:
            lines.append(f"\n--- TOKEN ESTIMATES (debug mode) ---")
            try:
                import tiktoken
                enc = tiktoken.get_encoding("cl100k_base")

                # Count tokens per section
                def count_tokens(text: str) -> int:
                    return len(enc.encode(text)) if text else 0

                # History tokens
                history_text = "\n".join(
                    f"{t.user_message} {t.assistant_message}"
                    for t in self.last_payload.history
                )
                history_tokens = count_tokens(history_text)

                # Insights tokens
                insights_text = "\n".join(
                    i.get("text", "") or i.get("document", "")
                    for i in self.last_payload.insights
                )
                insights_tokens = count_tokens(insights_text)

                # Summaries tokens
                summaries_text = "\n".join(
                    s.get("text", "") or s.get("document", "")
                    for s in self.last_payload.summaries
                )
                summaries_tokens = count_tokens(summaries_text)

                # Relationships tokens
                relationships_text = "\n".join(self.last_payload.recent_memories)
                relationships_tokens = count_tokens(relationships_text)

                # Key facts tokens
                key_facts_text = "\n".join(
                    f.get("text", "") for f in self.last_payload.key_facts
                )
                key_facts_tokens = count_tokens(key_facts_text)

                # Passages tokens
                passages_text = "\n".join(
                    p.get("text", "") for p in self.last_payload.passages
                )
                passages_tokens = count_tokens(passages_text)

                # Total formatted context
                formatted = self.architect._build_supporting_context(
                    self.last_payload, self.state, self.context_format
                )
                formatted_tokens = count_tokens(formatted or "")

                lines.append(f"  History: ~{history_tokens} tokens ({len(self.last_payload.history)} turns)")
                lines.append(f"  Insights: ~{insights_tokens} tokens ({len(self.last_payload.insights)} items)")
                lines.append(f"  Summaries: ~{summaries_tokens} tokens ({len(self.last_payload.summaries)} items)")
                lines.append(f"  Relationships: ~{relationships_tokens} tokens ({len(self.last_payload.recent_memories)} items)")
                lines.append(f"  Key Facts: ~{key_facts_tokens} tokens ({len(self.last_payload.key_facts)} items)")
                lines.append(f"  Passages: ~{passages_tokens} tokens ({len(self.last_payload.passages)} items)")
                lines.append(f"  ----------------------------------------")
                lines.append(f"  Formatted Context: ~{formatted_tokens} tokens (total)")

                # Debug info from payload
                if self.last_payload.debug_info:
                    lines.append(f"\n--- DEBUG INFO ---")
                    for key, value in self.last_payload.debug_info.items():
                        lines.append(f"  {key}: {value}")

            except ImportError:
                lines.append("  (tiktoken not available for token counting)")

        # Show formatted supporting context using PromptArchitect
        lines.append(f"\n--- Supporting Context (format: {self.context_format}) ---")
        formatted_context = self.architect._build_supporting_context(
            self.last_payload,
            self.state,
            self.context_format,
        )
        if formatted_context:
            lines.append(formatted_context)
        else:
            lines.append("  (no supporting context)")

        # History details - FULL content (shown separately since not in supporting context)
        if self.last_payload.history:
            lines.append(f"\n--- History Turns ({len(self.last_payload.history)}) ---")
            for i, turn in enumerate(self.last_payload.history, 1):
                lines.append(f"\n  Turn {i} [{turn.id[:8]}...]:")
                lines.append(f"    {self.user_name}: {turn.user_message}")
                lines.append(f"    {self.assistant_name}: {turn.assistant_message}")

        # Vector passages (shown separately for reference)
        if self.last_payload.passages:
            lines.append(f"\n--- Vector Passages ({len(self.last_payload.passages)}) ---")
            for i, passage in enumerate(self.last_payload.passages, 1):
                text = passage.get("text", "")
                similarity = passage.get("similarity", 0.0)
                lines.append(f"\n  Passage {i} (similarity: {similarity:.3f}):")
                lines.append(f"    {text}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def cmd_prompt(self) -> str:
        """Show the FULL formatted prompt sent to LLM (no truncation for debugging)."""
        if not self.last_messages:
            return "No prompt formatted yet. Send a message first."

        lines = ["=" * 60, f"FORMATTED PROMPT (format: {self.context_format})", "=" * 60]

        # Map API roles to configured names
        role_names = {
            "user": self.user_name,
            "assistant": self.assistant_name,
            "system": "SYSTEM",
        }

        for i, msg in enumerate(self.last_messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Map role to display name
            display_name = role_names.get(role, role.upper())

            # Mark the last user message as the current query + supporting context
            is_current_query = (i == len(self.last_messages) - 1 and role == "user")
            label = f"{display_name} (supporting context + query)" if is_current_query else display_name
            lines.append(f"\n--- Message {i + 1}: {label} ---")

            # Show FULL content (no truncation for debugging)
            lines.append(content)

        lines.append("\n" + "=" * 60)
        lines.append(f"Total messages: {len(self.last_messages)}")

        # Show active tools (passed as separate 'tools' parameter to LLM API)
        active_tools = self.assembler.active_tools
        if active_tools:
            lines.append("")
            lines.append("=" * 60)
            lines.append("ACTIVE TOOLS (passed to LLM API as 'tools' parameter)")
            lines.append("=" * 60)
            lines.append(f"Function calling enabled with {len(active_tools)} tool(s):\n")
            for tool in active_tools:
                name = tool.get("name", "unknown")
                desc = tool.get("description", "")[:80]
                category = tool.get("category", "uncategorized")
                lines.append(f"  • {name} [{category}]")
                lines.append(f"    {desc}{'...' if len(tool.get('description', '')) > 80 else ''}")
                # Show parameters briefly
                params = tool.get("parameters", {}).get("properties", {})
                if params:
                    param_names = list(params.keys())
                    lines.append(f"    Parameters: {', '.join(param_names)}")
                lines.append("")
        else:
            lines.append("")
            lines.append("(No tools active - streaming mode)")

        return "\n".join(lines)

    def cmd_debug(self) -> str:
        """Show detailed debug info."""
        if not self.last_payload:
            return "No debug info available. Send a message first."

        debug_info = self.last_payload.debug_info
        lines = ["Debug Information:"]
        for key, value in debug_info.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines) if len(lines) > 1 else "No debug info recorded."

    async def cmd_entities(self) -> str:
        """List graph entities and their relationships."""
        try:
            # Get all nodes and edges from graph store
            nodes = await self.controller.graph.get_all_nodes()
            edges = await self.controller.graph.get_all_edges()

            if not nodes and not edges:
                return "No entities in graph store."

            lines = ["=" * 60, "GRAPH STORE (entities & relationships)", "=" * 60]

            # Build a lookup for node labels by ID
            node_lookup = {node.id: node for node in nodes}

            # Show nodes grouped by type
            if nodes:
                lines.append(f"\nEntities ({len(nodes)} total):")
                # Group by type
                by_type: dict[str, list] = {}
                for node in nodes:
                    by_type.setdefault(node.type, []).append(node)

                for node_type, type_nodes in sorted(by_type.items()):
                    lines.append(f"\n  [{node_type}]")
                    for node in type_nodes[:500]:  # Show up to 500 per type for debugging
                        lines.append(f"    - {node.label} (hits: {node.hit_count})")
                    if len(type_nodes) > 500:
                        lines.append(f"    ... and {len(type_nodes) - 500} more")

            # Show relationships
            if edges:
                lines.append(f"\nRelationships ({len(edges)} total):")
                for edge in edges[:500]:  # Show up to 500 for debugging
                    source = node_lookup.get(edge.source_id)
                    target = node_lookup.get(edge.target_id)
                    source_label = source.label if source else edge.source_id[:8]
                    target_label = target.label if target else edge.target_id[:8]
                    lines.append(f"    {source_label} --[{edge.relation}]--> {target_label}")
                if len(edges) > 500:
                    lines.append(f"    ... and {len(edges) - 500} more")

            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving entities: {e}"

    async def cmd_facts(self) -> str:
        """List all facts/insights from the vector store."""
        try:
            # Get all documents from vector store (no practical limit for debugging)
            documents = await self.controller.vector.get_all(limit=10000)
            if not documents:
                return "No facts/insights in vector store."

            lines = ["=" * 60, "FACTS & INSIGHTS (from vector store)", "=" * 60]
            lines.append(f"\nTotal documents: {len(documents)}\n")

            for i, doc in enumerate(documents, 1):
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})

                # Truncate long text
                display_text = text[:200] + "..." if len(text) > 200 else text
                display_text = display_text.replace("\n", " ")

                lines.append(f"{i}. {display_text}")

                # Show metadata if present
                if metadata:
                    source_type = metadata.get("source_type", "unknown")
                    confidence = metadata.get("confidence", "N/A")
                    lines.append(f"   [source: {source_type}, confidence: {confidence}]")
                lines.append("")

            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving facts: {e}"

    async def cmd_insights(self) -> str:
        """List only insights (type='insight') from the vector store."""
        try:
            # Query with type filter
            documents = await self.controller.vector.get_all(
                limit=10000,
                where={"type": "insight"},
            )
            if not documents:
                return "No insights in vector store."

            lines = ["=" * 60, "INSIGHTS (type='insight' from vector store)", "=" * 60]
            lines.append(f"\nTotal insights: {len(documents)}\n")

            for i, doc in enumerate(documents, 1):
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})

                # Truncate long text
                display_text = text[:200] + "..." if len(text) > 200 else text
                display_text = display_text.replace("\n", " ")

                lines.append(f"{i}. {display_text}")

                # Show structured metadata
                meta_parts = []
                if metadata.get("topic"):
                    meta_parts.append(f"topic: {metadata['topic']}")
                if metadata.get("sentiment"):
                    meta_parts.append(f"sentiment: {metadata['sentiment']}")
                if metadata.get("confidence") is not None:
                    meta_parts.append(f"confidence: {metadata['confidence']}")
                if metadata.get("entities_mentioned"):
                    meta_parts.append(f"entities: {metadata['entities_mentioned']}")

                if meta_parts:
                    lines.append(f"   [{', '.join(meta_parts)}]")
                lines.append("")

            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving insights: {e}"

    async def cmd_summaries(self) -> str:
        """List only turn summaries (type='summary') from the vector store."""
        try:
            # Query with type filter
            documents = await self.controller.vector.get_all(
                limit=10000,
                where={"type": "summary"},
            )
            if not documents:
                return "No turn summaries in vector store."

            lines = ["=" * 60, "TURN SUMMARIES (type='summary' from vector store)", "=" * 60]
            lines.append(f"\nTotal summaries: {len(documents)}\n")

            for i, doc in enumerate(documents, 1):
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})

                # Show full summary text (these are paragraph-length)
                display_text = text[:400] + "..." if len(text) > 400 else text
                display_text = display_text.replace("\n", " ")

                lines.append(f"{i}. {display_text}")

                # Show metadata
                turn_id = metadata.get("turn_id", "")
                created_at = metadata.get("created_at", "")
                if turn_id or created_at:
                    meta_parts = []
                    if turn_id:
                        meta_parts.append(f"turn: {turn_id[:8]}...")
                    if created_at:
                        meta_parts.append(f"created: {created_at[:19]}")
                    lines.append(f"   [{', '.join(meta_parts)}]")
                lines.append("")

            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving summaries: {e}"

    async def cmd_meta_insights(self) -> str:
        """List only meta insights (type='meta_insight') from the vector store."""
        try:
            # Query with type filter for meta_insight
            documents = await self.controller.vector.get_all(
                limit=10000,
                where={"type": "meta_insight"},
            )
            if not documents:
                return "No meta insights in vector store. Run /reorganize with synthesis to generate them."

            lines = ["=" * 60, "META INSIGHTS (type='meta_insight' from vector store)", "=" * 60]
            lines.append(f"\nTotal meta insights: {len(documents)}\n")

            for i, doc in enumerate(documents, 1):
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})

                # Show full meta insight text
                display_text = text[:500] + "..." if len(text) > 500 else text
                display_text = display_text.replace("\n", " ")

                lines.append(f"{i}. {display_text}")

                # Show structured metadata
                meta_parts = []
                if metadata.get("confidence") is not None:
                    meta_parts.append(f"confidence: {metadata['confidence']}")
                if metadata.get("source_type"):
                    meta_parts.append(f"source: {metadata['source_type']}")
                if metadata.get("source_memories"):
                    source_count = len(metadata["source_memories"])
                    meta_parts.append(f"sources: {source_count} memories")
                if metadata.get("created_at"):
                    meta_parts.append(f"created: {metadata['created_at'][:19]}")

                if meta_parts:
                    lines.append(f"   [{', '.join(meta_parts)}]")
                lines.append("")

            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving meta insights: {e}"

    async def cmd_prime(self) -> str:
        """
        Show current context (works before first turn).

        Triggers a recall() to fetch insights/summaries/entities and populates
        last_payload so /context works before the first conversation turn.
        """
        try:
            # Fetch context via recall (empty query just to get supporting context)
            payload = await self.controller.recall(
                query="",
                session_id=self.session_id,
                include_history=True,
            )

            # Store for /context command
            self.last_payload = payload

            lines = ["=" * 60, "PRIMED CONTEXT", "=" * 60]

            # Summary counts
            lines.append(f"\nContext loaded:")
            lines.append(f"  Entities: {len(payload.entities)}")
            lines.append(f"  Key Facts: {len(payload.key_facts)}")
            lines.append(f"  Insights: {len(payload.insights)}")
            lines.append(f"  Summaries: {len(payload.summaries)}")
            lines.append(f"  Relationships: {len(payload.recent_memories)}")
            lines.append(f"  Prior session turns: {len(payload.prior_history)}")
            lines.append(f"  Current session turns: {len(payload.history)}")

            # Show top entities
            if payload.entities:
                lines.append("\n--- Top Entities (by hit_count) ---")
                for entity in payload.entities[:15]:
                    hit_count = getattr(entity, 'hit_count', 0)
                    lines.append(f"  - {entity.label} ({entity.type}, hits: {hit_count})")

            # Show relationship summaries
            if payload.recent_memories:
                lines.append("\n--- Relationship Summaries ---")
                for summary in payload.recent_memories[:10]:
                    lines.append(f"  {summary}")

            # Show recent insights
            if payload.insights:
                lines.append("\n--- Recent Insights (most recent first) ---")
                for i, insight in enumerate(payload.insights[:5], 1):
                    text = insight.get("text", "")[:150]
                    created = insight.get("metadata", {}).get("created_at", "")[:19]
                    lines.append(f"  {i}. [{created}] {text}...")

            # Show recent summaries
            if payload.summaries:
                lines.append("\n--- Recent Summaries (most recent first) ---")
                for i, summary in enumerate(payload.summaries[:5], 1):
                    text = summary.get("text", "")[:200]
                    created = summary.get("metadata", {}).get("created_at", "")[:19]
                    lines.append(f"  {i}. [{created}] {text}...")

            # Show key facts
            if payload.key_facts:
                lines.append("\n--- Key Facts (from vector store insights) ---")
                for i, fact in enumerate(payload.key_facts[:5], 1):
                    text = fact.get("text", "")
                    created = fact.get("metadata", {}).get("created_at", "")[:19]
                    display_text = text[:150] + "..." if len(text) > 150 else text
                    lines.append(f"  {i}. [{created}] {display_text}")

            # Show prior session history
            if payload.prior_history:
                lines.append("\n--- Prior Session History ---")
                # Group by session
                sessions_seen: set[str] = set()
                for turn in payload.prior_history[:10]:
                    session_id = turn.metadata.get("original_session_id", turn.session_id)
                    if session_id not in sessions_seen:
                        sessions_seen.add(session_id)
                        lines.append(f"  Session: {session_id[:12]}...")
                    timestamp = turn.timestamp.strftime("%Y-%m-%d %H:%M") if turn.timestamp else "N/A"
                    user_preview = (turn.user_message or "")[:50]
                    lines.append(f"    [{timestamp}] {user_preview}...")

            lines.append("\n" + "=" * 60)
            lines.append("Use /context for full details, /prompt to see formatted prompt.")
            return "\n".join(lines)

        except Exception as e:
            return f"Error fetching primed context: {e}"

    async def cmd_sessions(self) -> str:
        """List all stored transcript sessions, marking those in context."""
        if not self.transcript_store:
            return "Transcript storage not configured."

        try:
            sessions = await self.transcript_store.list_sessions(limit=1000)
            if not sessions:
                return "No transcript sessions found."

            # Get priming config to determine which sessions are "in context"
            priming_config = getattr(self.controller, '_priming_config', {})
            previous_sessions_count = priming_config.get('previous_sessions', 0)

            # Determine which sessions are in context (current + N most recent)
            in_context_ids: set[str] = {self.session_id}
            if previous_sessions_count > 0:
                # Sessions are already ordered newest first
                prior_sessions = [s for s in sessions if s.session_id != self.session_id]
                for session in prior_sessions[:previous_sessions_count]:
                    in_context_ids.add(session.session_id)

            lines = [
                "=" * 60,
                f"TRANSCRIPT SESSIONS ({len(sessions)} total)",
                f"  In context: {len(in_context_ids)} (current + {previous_sessions_count} prior)",
                "=" * 60
            ]

            for session in sessions:
                # Mark current session and in-context sessions
                markers = []
                if session.session_id == self.session_id:
                    markers.append("CURRENT")
                elif session.session_id in in_context_ids:
                    markers.append("IN CONTEXT")

                marker_str = f" [{', '.join(markers)}]" if markers else ""
                lines.append(f"\n  {session.session_id}{marker_str}")
                lines.append(f"    Started: {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
                if session.ended_at:
                    lines.append(f"    Ended: {session.ended_at.strftime('%Y-%m-%d %H:%M:%S')}")
                lines.append(f"    User: {session.user_id}")
                lines.append(f"    Model: {session.model_name}")
                lines.append(f"    Turns: {session.total_turns}, Tokens: {session.total_tokens}")

            lines.append("\n" + "=" * 60)
            lines.append("Use /transcript <session_id> to view a specific session.")
            return "\n".join(lines)
        except Exception as e:
            return f"Error listing sessions: {e}"

    async def cmd_transcript(self, arg: str | None = None) -> str:
        """
        Show transcript from persistent storage.

        Args:
            arg: Optional argument - either a session_id or "export"
        """
        if not self.transcript_store:
            return "Transcript storage not configured."

        # Handle /transcript export
        if arg and arg.lower() == "export":
            return await self._export_all_sessions_csv()

        # Determine which session to show
        target_session_id = arg if arg else self.session_id

        try:
            entries = await self.transcript_store.get_entries(
                target_session_id, limit=10000
            )
            if not entries:
                if arg:
                    return f"No transcript entries found for session: {target_session_id}"
                return "No transcript entries for this session."

            is_current = target_session_id == self.session_id
            current_marker = " [CURRENT]" if is_current else ""
            lines = ["=" * 60, f"TRANSCRIPT ({len(entries)} entries){current_marker}", "=" * 60]

            # Get session info
            session = await self.transcript_store.get_session(target_session_id)
            if session:
                lines.append(f"\nSession: {session.session_id}")
                lines.append(f"Started: {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
                lines.append(f"Model: {session.model_name}")
                lines.append(f"Total tokens: {session.total_tokens}")
                lines.append(f"Total latency: {session.total_latency_ms:.0f}ms")

            for entry in entries:
                lines.append(f"\n--- Turn {entry.turn_number} [{entry.id[:8]}...] ---")
                lines.append(f"Timestamp: {entry.timestamp.strftime('%H:%M:%S')}")

                if entry.user_message:
                    lines.append(f"\n{self.user_name}:")
                    lines.append(entry.user_message)

                if entry.assistant_message:
                    lines.append(f"\n{self.assistant_name}:")
                    # Truncate long responses for display
                    msg = entry.assistant_message
                    if len(msg) > 500:
                        msg = msg[:500] + f"\n... [{len(msg) - 500} more characters]"
                    lines.append(msg)

                # Show metrics if available
                metrics = []
                if entry.total_tokens:
                    metrics.append(f"tokens: {entry.total_tokens}")
                if entry.latency_ms:
                    metrics.append(f"latency: {entry.latency_ms:.0f}ms")
                if metrics:
                    lines.append(f"\n[{', '.join(metrics)}]")

            lines.append("\n" + "=" * 60)
            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving transcript: {e}"

    async def _export_all_sessions_csv(self) -> str:
        """Export entire transcript database to CSV files."""
        if not self.transcript_store:
            return "Transcript storage not configured."

        # Determine export directory
        if self.transcript_export_dir:
            export_dir = Path(self.transcript_export_dir)
        else:
            export_dir = Path("./exports")

        # Validate export path (must be within current directory or persist_dir)
        allowed_base = self.persist_dir.parent if self.persist_dir else Path.cwd()
        resolved_dir, path_error = _validate_export_path(export_dir, allowed_base)
        if path_error:
            return f"Export path error: {path_error}"

        try:
            # Create timestamped subdirectory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = resolved_dir / f"transcript_export_{timestamp}"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Use CSVExporter from friday-transcript
            exporter = CSVExporter(self.transcript_store)
            counts = await exporter.export_all_sessions(output_dir)

            lines = [
                "=" * 60,
                "TRANSCRIPT EXPORT COMPLETE",
                "=" * 60,
                f"\nExport directory: {output_dir}",
                f"\nFiles created:",
                f"  - sessions.csv ({counts['sessions']} sessions)",
                f"  - entries.csv ({counts['entries']} entries)",
                "\n" + "=" * 60,
            ]
            return "\n".join(lines)

        except Exception as e:
            return f"Error exporting transcripts: {e}"

    async def cmd_export(self, format_type: str = "markdown") -> str:
        """Export transcript to file."""
        if not self.transcript_store:
            return "Transcript storage not configured."

        try:
            # Determine output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"transcript_{self.session_id}_{timestamp}"

            if format_type == "jsonl":
                output_path = Path(f"./{base_name}.jsonl")
                exporter = JSONLExporter(self.transcript_store)
                count = await exporter.export_session(self.session_id, output_path)
                return f"Exported {count} entries to: {output_path}"

            elif format_type == "training":
                output_path = Path(f"./{base_name}_training.jsonl")
                exporter = JSONLExporter(self.transcript_store)
                count = await exporter.export_training_data(
                    self.session_id, output_path, format_style="chat"
                )
                return f"Exported {count} training examples to: {output_path}"

            elif format_type == "markdown" or format_type == "md":
                output_path = Path(f"./{base_name}.md")
                exporter = MarkdownExporter(
                    self.transcript_store,
                    user_name=self.user_name,
                    assistant_name=self.assistant_name,
                )
                count = await exporter.export_session(self.session_id, output_path)
                return f"Exported {count} entries to: {output_path}"

            else:
                return f"Unknown format: {format_type}. Use: jsonl, markdown, or training"

        except Exception as e:
            return f"Error exporting transcript: {e}"

    async def cmd_reset(self) -> str:
        """Clear all memory stores (graph and vector)."""
        try:
            lines = ["Resetting memory stores..."]

            # Clear graph store
            graph_result = await self.controller.graph.clear()
            lines.append(f"  Graph store: cleared {graph_result['nodes_deleted']} nodes, {graph_result['edges_deleted']} edges")

            # Clear vector store
            vector_count = await self.controller.vector.clear()
            lines.append(f"  Vector store: cleared {vector_count} documents")

            # Clear episodic store for this session
            await self.controller.episodic.clear_session(self.session_id)
            lines.append(f"  Episodic store: cleared session {self.session_id}")

            # Reset turn tracking
            self.turn_ids.clear()
            if self.state:
                self.state.turn_count = 0

            lines.append("\nMemory reset complete.")
            return "\n".join(lines)
        except Exception as e:
            return f"Error resetting memory: {e}"

    async def cmd_reorganize(self, opts: str = "") -> str:
        """
        Run memory reorganization.

        Options (space-separated):
          --execute       Run for real (default is dry-run)
          --no-backup     Skip backup before modifications
          --skip-synthesis Skip LLM-based memory synthesis
          --skip-verify   Skip LLM-based fact verification
          --skip-lifecycle Skip lifecycle and optimization steps
          --analyze       Just run analysis (no prune/synthesis/verify)
          --prune         Just run pruning
          --synthesize    Just run synthesis (meta-insights, relationships)
          --verify        Just run fact verification
          --backup        Just create a backup
          --dedupe        Just run insight deduplication (marks duplicates)

        Examples:
          /reorganize                    - Dry run with all steps
          /reorganize --execute          - Execute all steps with backup
          /reorganize --analyze          - Just analyze (read-only)
          /reorganize --execute --prune  - Execute pruning only
          /reorganize --execute --synthesize - Execute synthesis only
          /reorganize --skip-lifecycle   - Skip lifecycle/optimization steps
          /reorganize --dedupe           - Dry run insight deduplication
          /reorganize --execute --dedupe - Execute insight deduplication
        """
        if not self.persist_dir:
            return "Error: persist_dir not configured for this session."

        # Parse options
        opt_list = opts.lower().split() if opts else []

        # Determine mode
        dry_run = "--execute" not in opt_list
        backup_first = "--no-backup" not in opt_list
        skip_synthesis = "--skip-synthesis" in opt_list
        skip_verify = "--skip-verify" in opt_list
        skip_lifecycle = "--skip-lifecycle" in opt_list
        analyze_only = "--analyze" in opt_list
        prune_only = "--prune" in opt_list
        synthesize_only = "--synthesize" in opt_list
        verify_only = "--verify" in opt_list
        backup_only = "--backup" in opt_list
        dedupe_only = "--dedupe" in opt_list

        # Use maintenance config from config.yaml or defaults
        config = self.maintenance_config or MaintenanceConfig()

        # Get LLMs for maintenance operations (fall back to main chat LLM)
        synthesizer_llm = self.maintenance_llms.get("synthesizer", self.llm)
        classifier_llm = self.maintenance_llms.get("classifier", self.llm)
        researcher_llm = self.maintenance_llms.get("researcher", self.llm)
        judge_llm = self.maintenance_llms.get("judge", self.llm)

        # Track which roles are using fallback LLM
        fallback_roles = []
        for role, llm_instance in [
            ("synthesizer", synthesizer_llm),
            ("classifier", classifier_llm),
            ("researcher", researcher_llm),
            ("judge", judge_llm),
        ]:
            if llm_instance is self.llm and role not in self.maintenance_llms:
                fallback_roles.append(role)

        # Create embedding function for maintenance operations
        # Use config.embedding if available, otherwise fall back to session embedding
        maintenance_embedding = self.embedding_function
        if config.embedding and not skip_synthesis:
            try:
                from friday_llm import LiteLLMEmbeddingService, ResilienceConfig
                maintenance_embedding = LiteLLMEmbeddingService(
                    model_name=config.embedding.model,
                    api_key=config.embedding.api_key,
                    api_base=config.embedding.api_base,
                    resilience=ResilienceConfig(
                        timeout_seconds=config.embedding.timeout_seconds,
                    ),
                )
            except Exception as e:
                display_warning(f"Failed to create maintenance embedding service: {e}")
                display_info("Falling back to session embedding function.")

        # Create reorganizer with the persist_dir, config, LLMs, embedding, collection name,
        # and lifecycle components (Phase 8)
        # Lifecycle components are accessed through promotion_service
        has_lifecycle = self.promotion_service is not None and not skip_lifecycle
        reorganizer = MemoryReorganizer(
            memory_dir=self.persist_dir,
            config=config,
            llm_service=synthesizer_llm if not skip_synthesis else None,
            classifier_llm=classifier_llm if not skip_verify else None,
            researcher_llm=researcher_llm if not skip_verify else None,
            judge_llm=judge_llm if not skip_verify else None,
            embedding_function=maintenance_embedding,
            collection_name=config.collection_name,
            # Lifecycle components (Phase 8) - accessed via promotion_service
            collection_manager=self.promotion_service.collection_manager if has_lifecycle else None,
            access_buffer=self.access_buffer if has_lifecycle else None,
            factor_computer=self.factor_computer if has_lifecycle else None,
            promotion_scorer=self.promotion_service.promotion_scorer if has_lifecycle else None,
            decay_calculator=self.promotion_service.decay_calculator if has_lifecycle else None,
            graph_store=self.controller.graph if has_lifecycle else None,
        )

        try:
            lines = ["=" * 60, "MEMORY REORGANIZATION", "=" * 60]

            # Warn about fallback LLMs being used
            if fallback_roles:
                lines.append(f"\nNote: Using main chat LLM for: {', '.join(fallback_roles)}")
                lines.append("(Configure maintenance.llm in config.yaml for dedicated models)")

            if backup_only:
                # Just create a backup
                lines.append("\nCreating backup...")
                manifest = await reorganizer.backup()
                lines.append(f"  Backup ID: {manifest.backup_id[:8]}...")
                lines.append(f"  Location: {manifest.backup_dir}")
                lines.append(f"  Files backed up: {len(manifest.files)}")
                lines.append("\nBackup complete.")
                return "\n".join(lines)

            if dedupe_only:
                # Just run insight deduplication
                mode = "DRY RUN" if dry_run else "EXECUTING"
                lines.append(f"\nDeduplicating insights ({mode})...")
                if backup_first and not dry_run:
                    lines.append("Creating backup first...")
                    await reorganizer.backup()

                report = await reorganizer.dedupe_insights(dry_run=dry_run)
                lines.append(f"\nDeduplication Results:")
                lines.append(f"  Insights scanned: {report.insights_scanned}")
                lines.append(f"  Clusters found: {report.clusters_found}")
                lines.append(f"  Insights superseded: {report.insights_superseded}")

                if report.clusters:
                    lines.append(f"\nClusters (showing up to 10):")
                    for cluster in report.clusters[:10]:
                        lines.append(
                            f"  - {cluster.entity_key}: kept {cluster.primary_insight_id[:8]}..., "
                            f"superseded {len(cluster.superseded_ids)}"
                        )
                    if len(report.clusters) > 10:
                        lines.append(f"  ... and {len(report.clusters) - 10} more clusters")

                if report.errors:
                    lines.append(f"\nErrors: {len(report.errors)}")
                    for error in report.errors[:5]:
                        lines.append(f"  - {error}")

                if dry_run:
                    lines.append("\n[DRY RUN - No changes made. Use --execute to apply.]")
                else:
                    lines.append("\nDeduplication complete. Superseded insights will be filtered at retrieval.")
                return "\n".join(lines)

            if analyze_only:
                # Just analyze
                lines.append("\nAnalyzing memory consistency...")
                report = await reorganizer.analyze()
                lines.append(f"\nGraph Store:")
                lines.append(f"  Nodes: {report.graph_stats.get('node_count', 0)}")
                lines.append(f"  Edges: {report.graph_stats.get('edge_count', 0)}")
                lines.append(f"\nVector Store:")
                lines.append(f"  Documents: {report.vector_stats.get('document_count', 0)}")
                lines.append(f"\nEpisodic Store:")
                lines.append(f"  Turns: {report.episodic_stats.get('turn_count', 0)}")
                lines.append(f"\nIssues Found: {len(report.issues)}")
                lines.append(f"  Critical: {report.severity_counts['critical']}")
                lines.append(f"  Warning: {report.severity_counts['warning']}")
                lines.append(f"  Info: {report.severity_counts['info']}")

                if report.duplicate_groups:
                    lines.append(f"\nDuplicate Entity Groups: {len(report.duplicate_groups)}")
                    for group in report.duplicate_groups[:5]:
                        all_ids = [group.primary_id] + group.duplicate_ids[:2]
                        lines.append(f"  - {group.match_type}: {', '.join(all_ids)}")
                    if len(report.duplicate_groups) > 5:
                        lines.append(f"  ... and {len(report.duplicate_groups) - 5} more groups")

                lines.append("\nAnalysis complete.")
                return "\n".join(lines)

            if prune_only:
                # Just prune
                mode = "DRY RUN" if dry_run else "EXECUTING"
                lines.append(f"\nPruning redundancies ({mode})...")
                if backup_first and not dry_run:
                    lines.append("Creating backup first...")

                report = await reorganizer.prune(dry_run=dry_run, backup_first=backup_first)
                lines.append(f"\nPrune Results:")
                lines.append(f"  Entities merged: {report.entities_merged}")
                lines.append(f"  Entities removed: {report.entities_removed}")
                lines.append(f"  Insights removed: {report.insights_removed}")
                lines.append(f"  Edges removed: {report.edges_removed}")

                if dry_run:
                    lines.append("\n[DRY RUN - No changes made. Use --execute to apply.]")
                else:
                    lines.append("\nPruning complete.")
                return "\n".join(lines)

            if synthesize_only:
                # Just synthesize
                mode = "DRY RUN" if dry_run else "EXECUTING"
                lines.append(f"\nSynthesizing memories ({mode})...")
                if backup_first and not dry_run:
                    lines.append("Creating backup first...")
                    await reorganizer.backup()

                report = await reorganizer.synthesize(dry_run=dry_run)
                lines.append(f"\nSynthesis Results:")
                lines.append(f"  Topic clusters found: {len(report.topic_clusters)}")
                lines.append(f"  Meta-insights created: {report.meta_insights_created}")
                lines.append(f"  Relationships inferred: {report.relationships_inferred}")
                lines.append(f"  Knowledge gaps identified: {len(report.knowledge_gaps)}")

                if report.synthesized_memories:
                    lines.append(f"\nSynthesized Memories:")
                    for mem in report.synthesized_memories[:5]:
                        content_preview = mem.content[:80] + "..." if len(mem.content) > 80 else mem.content
                        lines.append(f"  - [{mem.type}] {content_preview}")
                    if len(report.synthesized_memories) > 5:
                        lines.append(f"  ... and {len(report.synthesized_memories) - 5} more")

                if dry_run:
                    lines.append("\n[DRY RUN - No changes made. Use --execute to apply.]")
                else:
                    lines.append("\nSynthesis complete.")
                return "\n".join(lines)

            if verify_only:
                # Just verify facts
                mode = "DRY RUN" if dry_run else "EXECUTING"
                lines.append(f"\nVerifying facts ({mode})...")

                report = await reorganizer.verify(dry_run=dry_run)
                lines.append(f"\nVerification Results:")
                lines.append(f"  Facts classified: {report.facts_classified}")
                lines.append(f"  Claims verified: {report.claims_verified}")
                lines.append(f"  Claims disputed: {report.claims_disputed}")
                lines.append(f"  Claims unverifiable: {report.claims_unverifiable}")

                if dry_run:
                    lines.append("\n[DRY RUN - No changes made. Use --execute to apply.]")
                else:
                    lines.append("\nVerification complete.")
                return "\n".join(lines)

            # Full reorganization
            mode = "DRY RUN" if dry_run else "EXECUTING"
            lines.append(f"\nRunning full reorganization ({mode})...")
            lines.append(f"  Backup first: {backup_first}")
            lines.append(f"  Skip synthesis: {skip_synthesis}")
            lines.append(f"  Skip verify: {skip_verify}")
            lines.append(f"  Skip lifecycle: {skip_lifecycle}")
            lines.append("")

            report = await reorganizer.reorganize(
                backup_first=backup_first,
                dry_run=dry_run,
                skip_synthesis=skip_synthesis,
                skip_verify=skip_verify,
                skip_lifecycle=skip_lifecycle,
            )

            # Show summary
            summary = reorganizer.generate_report_summary(report)
            lines.append(summary)

            if dry_run:
                lines.append("\n[DRY RUN - No changes made. Use --execute to apply.]")

            return "\n".join(lines)

        except Exception as e:
            logger.exception("Reorganization failed")
            error_msg = str(e).lower()
            # Provide more specific guidance for common failure modes
            if "embed" in error_msg or "vector" in error_msg:
                return (
                    f"Error during reorganization (embedding service): {e}\n"
                    "Check that your embedding service is running and configured correctly."
                )
            elif "timeout" in error_msg:
                return (
                    f"Error during reorganization (timeout): {e}\n"
                    "Consider increasing timeout_seconds in config.yaml."
                )
            elif "connection" in error_msg or "connect" in error_msg:
                return (
                    f"Error during reorganization (connection): {e}\n"
                    "Check that LLM/embedding services are reachable."
                )
            return f"Error during reorganization: {e}"

    async def cmd_lifecycle(self, opts: str = "") -> str:
        """
        Run memory lifecycle cycle (promotion, decay, reactivation).

        Options (space-separated):
          --execute       Run for real (default is dry-run)
          --stats         Show lifecycle statistics only
          --optimize      Flush access buffer and recompute retrieval factors
          --flush         Flush access buffer only

        Examples:
          /lifecycle              - Dry run lifecycle cycle
          /lifecycle --execute    - Execute lifecycle cycle
          /lifecycle --stats      - Show current lifecycle statistics
          /lifecycle --optimize   - Flush buffer and recompute factors
        """
        if not self.promotion_service:
            return "Error: Lifecycle service not configured. CollectionManager not initialized."

        # Parse options
        opt_list = opts.lower().split() if opts else []
        dry_run = "--execute" not in opt_list
        stats_only = "--stats" in opt_list
        optimize = "--optimize" in opt_list
        flush_only = "--flush" in opt_list

        try:
            lines = ["=" * 60, "MEMORY LIFECYCLE", "=" * 60]

            if stats_only:
                # Just show statistics
                lines.append("\nLifecycle Statistics:")
                stats = await self.promotion_service.collection_manager.get_stats()
                lines.append(f"  Short-term memories: {stats.get('short_term', 0)}")
                lines.append(f"  Long-term memories: {stats.get('long_term', 0)}")
                lines.append(f"  Decayed memories: {stats.get('decayed', 0)}")

                # Show access buffer stats if available
                if self.access_buffer:
                    buf_stats = self.access_buffer.get_stats()
                    lines.append("\nAccess Buffer:")
                    lines.append(f"  Short-term accesses: {buf_stats['short_term_accesses']}")
                    lines.append(f"  Long-term accesses: {buf_stats['long_term_accesses']}")
                    lines.append(f"  Seconds since flush: {buf_stats['seconds_since_flush']}")

                return "\n".join(lines)

            if flush_only:
                # Just flush access buffer
                if not self.access_buffer:
                    return "Access buffer not configured."

                lines.append("\nFlushing access buffer...")
                flush_result = await self.access_buffer.flush_all(
                    short_term_collection=self.promotion_service.collection_manager.short_term,
                    long_term_collection=self.promotion_service.collection_manager.long_term,
                )
                lines.append(f"  {flush_result.summary()}")
                return "\n".join(lines)

            if optimize:
                # Flush buffer and recompute factors
                lines.append("\nRunning latency optimization...")

                # Step 1: Flush access buffer
                if self.access_buffer:
                    lines.append("\n1. Flushing access buffer...")
                    flush_result = await self.access_buffer.flush_all(
                        short_term_collection=self.promotion_service.collection_manager.short_term,
                        long_term_collection=self.promotion_service.collection_manager.long_term,
                    )
                    lines.append(f"   {flush_result.summary()}")
                else:
                    lines.append("\n1. Access buffer: not configured (skipped)")

                # Step 2: Recompute retrieval factors
                if self.factor_computer:
                    lines.append("\n2. Recomputing retrieval factors...")
                    factor_result = await self.factor_computer.compute_factors(
                        self.promotion_service.collection_manager.long_term,
                        force_update=True,
                    )
                    lines.append(f"   {factor_result.summary()}")
                else:
                    lines.append("\n2. Factor computer: not configured (skipped)")

                lines.append("\nOptimization complete.")
                return "\n".join(lines)

            # Run promotion cycle
            mode = "DRY RUN" if dry_run else "EXECUTING"
            lines.append(f"\nRunning lifecycle cycle ({mode})...")

            result = await self.promotion_service.run_promotion_cycle(dry_run=dry_run)

            lines.append(f"\nLifecycle Results:")
            lines.append(f"  Promoted to long-term: {result.promoted_to_long_term}")
            lines.append(f"  Decayed from long-term: {result.decayed_from_long_term}")
            lines.append(f"  Reactivated: {result.reactivated}")

            if result.has_errors():
                lines.append(f"\n  Errors: {len(result.errors)}")
                for error in result.errors[:5]:
                    lines.append(f"    - {error}")
                if len(result.errors) > 5:
                    lines.append(f"    ... and {len(result.errors) - 5} more")

            # Show current stats after cycle
            lines.append("\n--- Current Statistics ---")
            stats = await self.promotion_service.collection_manager.get_stats()
            lines.append(f"  Short-term: {stats.get('short_term', 0)}")
            lines.append(f"  Long-term: {stats.get('long_term', 0)}")
            lines.append(f"  Decayed: {stats.get('decayed', 0)}")

            if dry_run:
                lines.append("\n[DRY RUN - No changes made. Use --execute to apply.]")
            else:
                lines.append("\nLifecycle cycle complete.")

            return "\n".join(lines)

        except Exception as e:
            logger.exception("Lifecycle cycle failed")
            error_msg = str(e).lower()
            if "embed" in error_msg or "vector" in error_msg:
                return (
                    f"Error during lifecycle cycle (embedding service): {e}\n"
                    "Check that your embedding service is running and configured correctly."
                )
            elif "timeout" in error_msg:
                return (
                    f"Error during lifecycle cycle (timeout): {e}\n"
                    "Consider increasing timeout_seconds in config.yaml."
                )
            elif "connection" in error_msg or "connect" in error_msg:
                return (
                    f"Error during lifecycle cycle (connection): {e}\n"
                    "Check that LLM/embedding services are reachable."
                )
            return f"Error during lifecycle cycle: {e}"

    async def cmd_migrate(self, opts: str = "") -> str:
        """
        Migrate existing memories to include lifecycle metadata.

        Options (space-separated):
          --force         Execute migration (default is dry-run/preview)

        Examples:
          /migrate              - Preview what would be migrated
          /migrate --force      - Execute migration

        Note: Migration is non-destructive (adds fields, doesn't remove data)
        and idempotent (safe to run multiple times).
        """
        if not self.persist_dir:
            return "Error: persist_dir not configured for this session."

        # Parse options
        opt_list = opts.lower().split() if opts else []
        dry_run = "--force" not in opt_list

        from friday_memory.lifecycle import MemoryMigrator

        # Create migrator with available stores
        migrator = MemoryMigrator(
            vector_store=self.controller.vector if self.controller else None,
            graph_store=self.controller.graph if self.controller else None,
            collection_manager=self.promotion_service.collection_manager if self.promotion_service else None,
        )

        try:
            mode = "DRY RUN" if dry_run else "EXECUTING"
            lines = ["=" * 60, f"MEMORY LIFECYCLE MIGRATION ({mode})", "=" * 60]

            # Check if migration is needed
            needs_migration = await migrator.check_migration_needed()
            if not needs_migration and dry_run:
                lines.append("\nNo migration needed - all memories have lifecycle metadata.")
                return "\n".join(lines)

            # Run migration
            report = await migrator.migrate(dry_run=dry_run)

            lines.append(f"\nVector Store:")
            lines.append(f"  Documents scanned: {report.vectors_scanned}")
            lines.append(f"  Documents migrated: {report.vectors_migrated}")
            lines.append(f"  Already migrated: {report.vectors_skipped}")

            lines.append(f"\nGraph Store:")
            lines.append(f"  Nodes scanned: {report.nodes_scanned}")
            lines.append(f"  Nodes migrated: {report.nodes_migrated}")
            lines.append(f"  Already migrated: {report.nodes_skipped}")

            lines.append(f"\nEdges (staleness tracking):")
            lines.append(f"  Edges scanned: {report.edges_scanned}")
            lines.append(f"  Edges migrated: {report.edges_migrated}")
            lines.append(f"  Already have staleness fields: {report.edges_skipped}")

            if report.errors:
                lines.append(f"\nErrors ({len(report.errors)}):")
                for error in report.errors[:5]:
                    lines.append(f"  - {error}")
                if len(report.errors) > 5:
                    lines.append(f"  ... and {len(report.errors) - 5} more")

            if dry_run:
                if report.needs_migration:
                    lines.append("\n[DRY RUN - Run '/migrate --force' to apply these changes.]")
                else:
                    lines.append("\nNo migration needed.")
            else:
                lines.append("\nMigration complete!")

            return "\n".join(lines)

        except Exception as e:
            logger.exception("Migration failed")
            error_msg = str(e).lower()
            if "embed" in error_msg or "vector" in error_msg:
                return (
                    f"Error during migration (embedding service): {e}\n"
                    "Check that your embedding service is running and configured correctly."
                )
            elif "timeout" in error_msg:
                return (
                    f"Error during migration (timeout): {e}\n"
                    "Consider increasing timeout_seconds in config.yaml."
                )
            elif "connection" in error_msg or "connect" in error_msg:
                return (
                    f"Error during migration (connection): {e}\n"
                    "Check that LLM/embedding services are reachable."
                )
            return f"Error during migration: {e}"

    def cmd_vars(self) -> str:
        """Show scoped variables."""
        if not self.state or not self.state.scoped_vars:
            return "No scoped variables set."
        lines = ["Scoped Variables:"]
        for key, value in self.state.scoped_vars.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)

    def cmd_set(self, key: str, value: str) -> str:
        """Set a scoped variable."""
        if not self.state:
            return "Session not initialized."
        self.state.set_var(key, value)
        return f"Set {key} = {value}"

    def cmd_tools(self, category: str | None = None) -> str:
        """
        List available tools, optionally filtered by category.

        Args:
            category: Optional category to filter by (e.g., "utility", "filesystem")

        Returns:
            Formatted string listing available tools
        """
        tools = TOOL_SCHEMAS

        if category:
            tools = [t for t in tools if t.get("category") == category]
            if not tools:
                available_categories = sorted(set(t.get("category", "uncategorized") for t in TOOL_SCHEMAS))
                return f"No tools found in category '{category}'.\nAvailable categories: {', '.join(available_categories)}"

        lines = ["=" * 60, f"AVAILABLE TOOLS ({len(tools)} total)", "=" * 60]

        # Group by category
        by_category: dict[str, list[dict]] = {}
        for tool in tools:
            cat = tool.get("category", "uncategorized")
            by_category.setdefault(cat, []).append(tool)

        for cat, cat_tools in sorted(by_category.items()):
            lines.append(f"\n[{cat}]")
            for tool in cat_tools:
                name = tool.get("name", "unknown")
                desc = tool.get("description", "")[:60]
                if len(tool.get("description", "")) > 60:
                    desc += "..."
                lines.append(f"  - {name}: {desc}")

                # Show parameters if present
                params = tool.get("parameters", {}).get("properties", {})
                if params:
                    param_names = list(params.keys())
                    lines.append(f"    Parameters: {', '.join(param_names)}")

        lines.append("")
        lines.append("Use /run-tool <name> [json_params] to execute a tool")
        return "\n".join(lines)

    async def cmd_run_tool(self, args: str) -> str:
        """
        Execute a tool by name with optional parameters.

        Usage:
            /run-tool echo hello world           (plain text for single-param tools)
            /run-tool echo {"message": "hello"}  (JSON format)
            /run-tool get_current_datetime {"timezone_name": "America/New_York"}

        Args:
            args: Tool name followed by parameters (JSON or plain text)

        Returns:
            Tool execution result as string
        """
        if not args.strip():
            available = ", ".join(TOOL_REGISTRY.list_names())
            return f"Usage: /run-tool <tool_name> [params]\nAvailable tools: {available}"

        parts = args.split(maxsplit=1)
        tool_name = parts[0]
        params_str = parts[1] if len(parts) > 1 else ""

        if TOOL_REGISTRY is None:
            return "Error: Tool registry not initialized. Restart memory-chat."

        if tool_name not in TOOL_REGISTRY:
            available = ", ".join(TOOL_REGISTRY.list_names())
            return f"Unknown tool: {tool_name}\nAvailable tools: {available}"

        # Parse parameters - try JSON first, then plain text for single-param tools
        params: dict[str, Any] = {}
        if params_str:
            # Try JSON parsing first (if it looks like JSON)
            if params_str.strip().startswith("{"):
                try:
                    params = json.loads(params_str)
                except json.JSONDecodeError as e:
                    return f"Invalid JSON parameters: {e}\nExample: /run-tool {tool_name} {{\"param\": \"value\"}}"
            else:
                # Plain text - use as 'message' parameter for tools that support it
                tool = TOOL_REGISTRY.get(tool_name)
                if tool is None:
                    return f"Tool '{tool_name}' not found in registry"

                # Get the tool's parameter schema
                if hasattr(tool, "parameters_schema"):
                    schema = tool.parameters_schema
                    props = schema.get("properties", {})
                    required = schema.get("required", [])

                    # Determine which param to use for plain text input
                    param_name = None

                    # Priority 1: If tool has a 'message' param, use it
                    if "message" in props:
                        param_name = "message"
                    # Priority 2: If exactly one required param, use it
                    elif len(required) == 1:
                        param_name = required[0]
                    # Priority 3: If tool has exactly one param, use it
                    elif len(props) == 1:
                        param_name = list(props.keys())[0]
                    # Priority 4: If multiple params but none required, use first
                    elif len(props) > 0 and len(required) == 0:
                        param_name = list(props.keys())[0]

                    if param_name:
                        params = {param_name: params_str}
                        logger.debug(f"Plain text mapped to {param_name} param")
                    else:
                        return f"Plain text not supported for {tool_name} (multiple required params).\nUse JSON: /run-tool {tool_name} {{\"param\": \"value\"}}"
                else:
                    return f"Tool {tool_name} has no parameter schema. Use JSON format."

        # Validate parameters against tool schema before execution
        tool = TOOL_REGISTRY.get(tool_name)
        if tool and hasattr(tool, "parameters_schema"):
            schema = tool.parameters_schema
            validation_error = _validate_tool_params(params, schema, tool_name)
            if validation_error:
                return validation_error

        # Execute the tool via the registry
        try:
            result = await _execute_tool(tool_name, **params)
        except TypeError as e:
            # Handle invalid parameters
            return f"Invalid parameters for {tool_name}: {e}"
        except Exception as e:
            return f"Tool execution error: {type(e).__name__}: {e}"

        return f"Tool: {tool_name}\nResult:\n{result}"

    def cmd_inject_tools(self, tool_names: str) -> str:
        """
        Inject tools into the context assembler for testing.

        Usage: /inject-tools get_current_datetime read_file write_file

        Args:
            tool_names: Space-separated list of tool names to inject

        Returns:
            Status message about injected tools
        """
        if not tool_names.strip():
            return "Usage: /inject-tools <tool_name1> [tool_name2] ...\nExample: /inject-tools get_current_datetime"

        names = tool_names.split()
        schemas = [t for t in TOOL_SCHEMAS if t.get("name") in names]

        if not schemas:
            available = ", ".join(t.get("name", "?") for t in TOOL_SCHEMAS)
            return f"No matching tools found for: {', '.join(names)}\nAvailable: {available}"

        # Inject into assembler's tool manager
        self.assembler.set_active_tools(schemas)

        injected_names = [s.get("name") for s in schemas]
        not_found = [n for n in names if n not in injected_names]

        lines = [f"Injected {len(schemas)} tools into context:"]
        for s in schemas:
            lines.append(f"  - {s.get('name')} [{s.get('category', 'uncategorized')}]")

        if not_found:
            lines.append(f"\nNot found: {', '.join(not_found)}")

        lines.append("\nUse /context to see tools in payload, /recommend-tools to test recommendations")
        return "\n".join(lines)

    def cmd_clear_tools(self) -> str:
        """
        Clear all injected tools from the context.

        Returns:
            Status message confirming tools cleared
        """
        self.assembler.clear_tools()
        return "All injected tools cleared from context."

    def cmd_recommend_tools(self, query: str) -> str:
        """
        Test tool recommendations for a given query.

        Usage: /recommend-tools read the config file

        Args:
            query: Query string to generate recommendations for

        Returns:
            Formatted list of tool recommendations with scores
        """
        if not query.strip():
            return "Usage: /recommend-tools <query>\nExample: /recommend-tools read the config file and parse JSON"

        # Generate recommendations using the assembler
        recommendations = self.assembler.recommend_tools(
            query=query,
            available_tools=TOOL_SCHEMAS,
            top_k=5,
        )

        if not recommendations:
            return f"No tool recommendations for: '{query}'\nNote: Tools need keyword matches with the query."

        lines = [
            "=" * 60,
            f"TOOL RECOMMENDATIONS for: '{query}'",
            "=" * 60,
            "",
        ]

        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec.tool_name} (score: {rec.relevance_score:.2f}, confidence: {rec.confidence:.2f})")
            lines.append(f"   Category: {rec.category}")
            lines.append(f"   Reason: {rec.reason}")
            if rec.suggested_parameters:
                params = ", ".join(f"{k}={v}" for k, v in rec.suggested_parameters.items())
                lines.append(f"   Suggested params: {params}")
            lines.append("")

        lines.append("Use /inject-tools <name> to add tools to context")
        return "\n".join(lines)

    def cmd_tool_budget(self) -> str:
        """
        Show tool token budget information.

        Returns:
            Formatted budget information
        """
        # Get active tools from assembler
        active_tools = self.assembler.active_tools

        if not active_tools:
            return """Tool Budget Info:
  No tools currently injected.

Use /inject-tools <name> to inject tools into context.
Use /tools to list available tools."""

        budget_info = self.assembler.get_tool_budget_info()

        lines = [
            "=" * 60,
            "TOOL TOKEN BUDGET",
            "=" * 60,
            "",
            f"Active tools: {budget_info['tool_count']}",
            f"Estimated tokens: {budget_info['estimated_tokens']}",
            f"Max tools allowed: {budget_info['max_tools']}",
            f"Budget limit: {budget_info['budget_limit']} tokens",
            f"Usage: {budget_info['usage_percent']:.1f}%",
            "",
            "Injected tools:",
        ]

        for tool in active_tools:
            name = tool.get("name", "unknown")
            category = tool.get("category", "uncategorized")
            lines.append(f"  - {name} [{category}]")

        return "\n".join(lines)

    def cmd_help(self) -> str:
        """Show available commands using Rich formatting."""
        commands = {
            "/exit, /quit": "Exit the chat",
            "/clear": "Clear conversation history",
            "/history": "Show conversation history",
            "/memory": "Show memory statistics",
            "/context [--debug]": "Show context payload",
            "/prompt": "Show full formatted prompt sent to LLM",
            "/prime": "Load and show primed context",
            "/debug": "Show debug info from context assembly",
            "/entities": "List graph entities and relationships",
            "/facts": "List all vector store documents",
            "/insights": "List only insights (type='insight')",
            "/summaries": "List only turn summaries (type='summary')",
            "/meta": "List meta insights from synthesis",
            "/sessions": "List stored transcript sessions",
            "/transcript [id]": "Show session transcript",
            "/export [format]": "Export session (jsonl, markdown, training)",
            "/reset": "Clear all memory stores",
            "/reorganize [opts]": "Run memory reorganization",
            "/migrate [opts]": "Migrate to lifecycle metadata",
            "/lifecycle [opts]": "Run lifecycle cycle",
            "/vars": "Show scoped variables",
            "/set <key> <val>": "Set a scoped variable",
            "/tools [category]": "List available tools",
            "/run-tool <name> [json]": "Execute a tool",
            "/inject-tools <names>": "Inject tools into context",
            "/clear-tools": "Clear injected tools",
            "/recommend-tools <query>": "Get tool recommendations",
            "/tool-budget": "Show tool token budget",
            "/help": "Show this help",
        }
        tips = [
            "/reorganize --execute: Run with changes",
            "/lifecycle --stats: View current stats",
            "/tools utility: Filter by category",
            "/run-tool get_current_datetime: Example tool call",
        ]
        display_help(commands, tips=tips)
        return ""  # Display already shown

    async def _background_extract(self, turn: InteractionTurn) -> None:
        """Run extraction in background without blocking the user."""
        try:
            result = await self.extractor.extract(turn)
            if result.get("error"):
                logger.debug(f"Background extraction error: {result['error']}")
            else:
                extracted = result.get("extracted", {})
                entity_count = len(extracted.get("entities", []))
                fact_count = len(extracted.get("facts", []))
                rel_count = len(extracted.get("relationships", []))
                logger.debug(
                    f"Background extraction complete: "
                    f"{entity_count} entities, {fact_count} facts, {rel_count} relationships"
                )
        except Exception as e:
            logger.debug(f"Background extraction failed: {e}")

    async def process_turn(self, user_input: str) -> str | None:
        """Process a user turn and return the response.

        Supports LLM function calling when tools are injected via /inject-tools.
        When tools are active, uses non-streaming mode to handle tool_calls.
        When no tools are active, uses streaming mode for better UX.
        """
        if not self.state:
            await self.initialize()

        # Calculate dynamic budget limit
        dynamic_limit = self.architect.calculate_dynamic_limit(self.system_prompt)

        # 1. Assemble context (retrieves from all stores)
        self.last_payload = await self.assembler.assemble_context(
            query=user_input,
            state=self.state,
            budget_limit=dynamic_limit,
        )

        # 2. Format prompt with assembled context AND current user input
        messages = await self.assembler.format_prompt(
            system_prompt=self.system_prompt,
            payload=self.last_payload,
            context_format=self.context_format,
            user_query=user_input,  # Pass current input directly
        )

        # Store for debugging
        self.last_messages = messages

        # Get active tool schemas (injected via /inject-tools)
        active_tools = self.assembler.active_tools
        tool_schemas = None
        if active_tools:
            # Convert to OpenAI function calling format
            tool_schemas = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t.get("description", ""),
                        "parameters": t.get("parameters", {"type": "object", "properties": {}}),
                    },
                }
                for t in active_tools
            ]
            logger.debug(f"Function calling enabled with {len(tool_schemas)} tools")

        # Print assistant name with Rich styling
        console = get_console()
        console.print()
        console.print(f"[bold cyan]{self.assistant_name}:[/bold cyan]")

        full_response = ""
        try:
            if tool_schemas:
                # Function calling mode (non-streaming with tool loop)
                full_response = await self._process_with_tools(messages, tool_schemas)
            else:
                # Streaming mode (no tools)
                full_response = await self._process_streaming(messages)

            # End newline after response
            console.print()

            # 4. Create and save interaction turn
            turn = InteractionTurn(
                id=str(uuid.uuid4()),
                session_id=self.session_id,
                timestamp=datetime.now(),
                user_message=user_input,
                assistant_message=full_response,
            )
            await self.controller.add_turn(self.session_id, turn)
            self.turn_ids.append(turn.id)

            # 5. Extract entities and facts from the turn (background)
            # Run extraction asynchronously so user can continue chatting
            if self.extractor:
                asyncio.create_task(self._background_extract(turn))
                get_console().print("  [dim][Extraction started in background][/dim]")

            # Update state turn count
            if self.state:
                self.state.turn_count += 1

            return full_response

        except LLMTimeoutError as e:
            display_error(f"Request timed out after {e.timeout_seconds}s")
            display_info("The LLM is taking too long. Try a shorter message or check the server.")
            return None

        except LLMRetryExhaustedError as e:
            display_error(f"Failed after {e.attempts} attempts", exception=e.last_error)
            display_info("The LLM service is unavailable. Check if the server is running.")
            return None

        except CircuitBreakerOpenError as e:
            display_warning("Service temporarily unavailable")
            display_info(f"Circuit breaker is open. Retry in {e.retry_after:.0f} seconds.")
            return None

        except OperationCancelledError:
            console.print()  # Newline after cancelled spinner
            display_warning("Request cancelled")
            return None

    async def _process_streaming(self, messages: list[dict[str, Any]]) -> str:
        """Process LLM call in streaming mode (no tools).

        Supports cancellation via Escape key before the first chunk arrives.
        Once streaming starts, the response completes naturally.
        """
        from friday_cli.cancellation import CancellationToken, _check_for_escape_key

        full_response = ""
        first_chunk = True
        indicator = ThinkingIndicator.random_thinking()
        indicator.start()

        # Show cancel hint
        get_console().print("  [dim]Press [Esc] to cancel[/dim]")

        # Create cancellation token for escape key monitoring
        cancel_token = CancellationToken()
        escape_task = asyncio.create_task(_check_for_escape_key(cancel_token))

        try:
            async for chunk in self.llm.chat_completion_stream(
                messages=messages,
                temperature=self.temperature,
            ):
                if first_chunk:
                    indicator.stop()  # Stop spinner on first chunk (idempotent)
                    # Stop escape monitoring once response starts
                    cancel_token.cancel()  # Signal to stop monitoring
                    escape_task.cancel()
                    first_chunk = False

                # Check if cancelled during spinner phase
                if cancel_token.is_cancelled and first_chunk:
                    raise OperationCancelledError()

                # Use sys.stdout for real-time streaming (Rich doesn't support streaming)
                sys.stdout.write(chunk)
                sys.stdout.flush()
                full_response += chunk

            # Ensure indicator is stopped even if no chunks arrived
            indicator.stop()
            return full_response

        except asyncio.CancelledError:
            if cancel_token.is_cancelled:
                raise OperationCancelledError()
            raise
        finally:
            # ALWAYS stop the indicator, even on error/timeout
            indicator.stop()

            # Clean up escape monitoring task
            if not escape_task.done():
                escape_task.cancel()
                try:
                    await escape_task
                except asyncio.CancelledError:
                    pass

    async def _display_streaming_response(
        self,
        content: str,
        chunk_size: int = 3,
        delay: float = 0.01,
    ) -> None:
        """
        Display a response with simulated streaming effect.

        Used when we have a complete response from non-streaming API (e.g., after
        tool execution) but want to display it progressively for better UX.

        Args:
            content: The complete response text to display
            chunk_size: Number of characters to output per chunk (default 3)
            delay: Seconds to wait between chunks (default 0.01)
        """
        # Output in small chunks for streaming effect
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            sys.stdout.write(chunk)
            sys.stdout.flush()
            if delay > 0:
                await asyncio.sleep(delay)

    async def _process_with_tools(
        self,
        messages: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]],
        max_iterations: int = 10,
        max_consecutive_failures: int = 3,
        max_tool_messages: int = 30,
    ) -> str:
        """Process LLM call with function calling support.

        Implements a Re-Act style loop:
        1. Call LLM with tools
        2. If tool_calls in response, execute them
        3. Add tool results to messages
        4. Loop until no more tool_calls or max iterations

        Args:
            messages: Conversation messages
            tool_schemas: Tool schemas in OpenAI function calling format
            max_iterations: Maximum tool calling iterations (default 10)
            max_consecutive_failures: Abort after N consecutive tool failures (default 3)
            max_tool_messages: Maximum messages before pruning (default 30)

        Returns:
            Final assistant response text
        """
        working_messages = list(messages)  # Copy to avoid mutation
        initial_message_count = len(working_messages)  # For pruning bounds
        iteration = 0
        consecutive_failures = 0  # Circuit breaker counter

        while iteration < max_iterations:
            iteration += 1

            # Call LLM with tools - show thinking indicator during call
            if iteration == 1:
                indicator = ThinkingIndicator.random_thinking()
            else:
                indicator = ThinkingIndicator.random_tool_processing()
            indicator.start()

            # Show cancel hint on first iteration
            if iteration == 1:
                get_console().print("  [dim]Press [Esc] to cancel[/dim]")

            try:
                # Wrap LLM call in cancellable operation
                response: ChatCompletionResponse | None = await run_cancellable(
                    self.llm.chat_completion(
                        messages=working_messages,
                        tools=tool_schemas,
                        temperature=self.temperature,
                    ),
                    show_hint=False,  # We already showed the hint with indicator
                )
            finally:
                # ALWAYS stop the indicator, even on error/timeout
                indicator.stop()

            # Check if cancelled
            if response is None:
                raise OperationCancelledError()

            # Check if response has tool calls
            if not response.has_tool_calls:
                # No tool calls - this is the final response
                # Stream it for better UX (simulated streaming for non-streaming API response)
                if response.content:
                    await self._display_streaming_response(response.content)
                return response.content or ""

            # Process tool calls
            display_info(f"Calling {len(response.tool_calls)} tool(s)...")

            # Add assistant message with tool_calls to history
            assistant_msg: dict[str, Any] = {"role": "assistant", "content": response.content or ""}
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                }
                for tc in response.tool_calls
            ]
            working_messages.append(assistant_msg)

            # Execute each tool call
            for tc in response.tool_calls:
                tool_name = tc.name
                tool_args = tc.arguments

                get_console().print(f"  [cyan]→[/cyan] {tool_name}({json.dumps(tool_args)})")

                # Execute the tool
                try:
                    result = await _execute_tool(tool_name, **tool_args)
                    truncated = result[:100] + "..." if len(result) > 100 else result
                    display_success(f"  {truncated}")
                    consecutive_failures = 0  # Reset on success
                except Exception as e:
                    consecutive_failures += 1
                    result = f"Error executing tool: {e}"
                    display_error(f"  {result}")

                    # Circuit breaker: abort after too many consecutive failures
                    if consecutive_failures >= max_consecutive_failures:
                        error_msg = (
                            f"Tool execution aborted: {consecutive_failures} consecutive failures. "
                            f"Last error: {e}"
                        )
                        display_warning(f"CIRCUIT BREAKER: {error_msg}")
                        return error_msg

                # Add tool result to messages
                working_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    }
                )

            # Message history bounds: prune if exceeding limit
            if len(working_messages) > max_tool_messages:
                # Keep original context + most recent tool messages
                preserve_count = initial_message_count
                recent_count = max_tool_messages - preserve_count
                preserved = working_messages[:preserve_count]
                recent = working_messages[-recent_count:]
                working_messages = preserved + recent
                display_info(f"Pruned message history to {len(working_messages)} messages")

        # Max iterations reached
        display_warning(f"Max tool iterations ({max_iterations}) reached")
        return "I apologize, but I've reached the maximum number of tool calls. Please try a simpler request."


async def main() -> None:
    """Main chat loop."""
    # Determine config path
    if len(sys.argv) > 2 and sys.argv[1] == "--config":
        config_path = Path(sys.argv[2])
    else:
        config_path = Path(__file__).parent / "config.yaml"

    # Load CLI configuration (theme, icons, prompt styling)
    # This looks for cli-config.yaml next to config.yaml
    load_cli_config(config_path)
    reset_console()  # Rebuild console with new theme

    # Load configuration using SessionConfig for typed access
    # SessionConfig provides cleaner access to common values
    session_config = SessionConfig.from_yaml(config_path)

    # Validate configuration
    errors = validate_config(session_config, required_sections=["llm"])
    if errors:
        for error in errors:
            display_error(error)
        sys.exit(1)

    # Also load as raw dict for backwards compatibility with existing code
    config = load_config(config_path)
    llm_config = config.get("llm", {})
    extraction_config = config.get("extraction", {})
    embedding_config = config.get("embedding", {})
    memory_config = config.get("memory", {})
    chat_config = config.get("chat", {})
    logging_config = config.get("logging", {})
    transcript_config = config.get("transcript", {})
    maintenance_yaml = config.get("maintenance", {})
    lifecycle_yaml = config.get("lifecycle", {})
    tools_config = config.get("tools", {})

    # Initialize tool registry from YAML configuration
    global TOOL_REGISTRY, TOOL_SCHEMAS
    TOOL_REGISTRY = _build_tool_registry(tools_config)
    TOOL_SCHEMAS = TOOL_REGISTRY.get_schemas()
    display_success(f"Tool registry initialized with {len(TOOL_SCHEMAS)} tool(s)")

    # Build MaintenanceConfig from YAML
    pruning_yaml = maintenance_yaml.get("pruning", {})
    synthesis_yaml = maintenance_yaml.get("synthesis", {})
    fact_check_yaml = maintenance_yaml.get("fact_checking", {})
    prompts_yaml = maintenance_yaml.get("prompts", {})
    logging_yaml = maintenance_yaml.get("logging", {})
    maintenance_embedding_yaml = maintenance_yaml.get("embedding", {})

    # Build PromptsConfig - only override prompts that are explicitly set in config
    prompts_kwargs = {}
    if prompts_yaml.get("classification"):
        prompts_kwargs["classification"] = prompts_yaml["classification"]
    if prompts_yaml.get("research"):
        prompts_kwargs["research"] = prompts_yaml["research"]
    if prompts_yaml.get("judge"):
        prompts_kwargs["judge"] = prompts_yaml["judge"]
    if prompts_yaml.get("meta_insight"):
        prompts_kwargs["meta_insight"] = prompts_yaml["meta_insight"]
    if prompts_yaml.get("knowledge_gap"):
        prompts_kwargs["knowledge_gap"] = prompts_yaml["knowledge_gap"]
    if prompts_yaml.get("relationship_inference"):
        prompts_kwargs["relationship_inference"] = prompts_yaml["relationship_inference"]

    # Build LogConfig - parse verbosity and format strings to enums
    log_verbosity_str = logging_yaml.get("verbosity", "normal").lower()
    log_format_str = logging_yaml.get("format", "markdown").lower()
    try:
        log_verbosity = LogVerbosity(log_verbosity_str)
    except ValueError:
        log_verbosity = LogVerbosity.NORMAL
    try:
        log_format = LogFormat(log_format_str)
    except ValueError:
        log_format = LogFormat.MARKDOWN

    # Build EmbeddingConfig for maintenance operations
    # Priority: maintenance.embedding > main embedding config > None
    maintenance_embedding_config = None
    if maintenance_embedding_yaml:
        # Use maintenance-specific embedding config
        maintenance_embedding_config = EmbeddingConfig(
            model=maintenance_embedding_yaml.get("model", "openai/nomic-embed-text-v1.5"),
            api_base=maintenance_embedding_yaml.get("api_base"),
            api_key=maintenance_embedding_yaml.get("api_key"),
            timeout_seconds=maintenance_embedding_yaml.get("timeout_seconds", 60.0),
        )
    elif embedding_config:
        # Fall back to main embedding config
        maintenance_embedding_config = EmbeddingConfig(
            model=embedding_config.get("model", "openai/nomic-embed-text-v1.5"),
            api_base=embedding_config.get("api_base"),
            api_key=embedding_config.get("api_key"),
            timeout_seconds=embedding_config.get("timeout_seconds", 60.0),
        )

    # Get collection name - prefer maintenance config, fall back to memory config
    maintenance_collection_name = (
        maintenance_yaml.get("collection_name")
        or memory_config.get("collection_name", "memory_chat_test")
    )

    # Build LifecycleDecayConfig from lifecycle YAML
    lifecycle_decay_config = LifecycleDecayConfig(
        enabled=lifecycle_yaml.get("enabled", True),
        decay_rate=lifecycle_yaml.get("decay_rate", 0.01),
        access_boost=lifecycle_yaml.get("access_boost", 0.2),
        promotion_threshold=lifecycle_yaml.get("promotion_threshold", 0.7),
        decay_threshold=lifecycle_yaml.get("decay_threshold", 0.2),
        short_term_min_age_hours=lifecycle_yaml.get("short_term_min_age_hours", 24),
        decayed_retention_days=lifecycle_yaml.get("decayed_retention_days", 30),
        promotion_weight_age=lifecycle_yaml.get("promotion_weight_age", 0.2),
        promotion_weight_access=lifecycle_yaml.get("promotion_weight_access", 0.4),
        promotion_weight_confidence=lifecycle_yaml.get("promotion_weight_confidence", 0.2),
        promotion_weight_connection=lifecycle_yaml.get("promotion_weight_connection", 0.2),
    )

    maintenance_config = MaintenanceConfig(
        pruning=PruneConfig(
            stale_threshold_days=pruning_yaml.get("stale_threshold_days", 90),
            min_hit_count=pruning_yaml.get("min_hit_count", 1),
            similarity_threshold=pruning_yaml.get("similarity_threshold", 0.95),
        ),
        synthesis=SynthesisConfig(
            cluster_min_size=synthesis_yaml.get("cluster_min_size", 3),
            meta_insight_confidence=synthesis_yaml.get("meta_insight_confidence", 0.7),
        ),
        fact_checking=FactCheckConfig(
            batch_size=fact_check_yaml.get("batch_size", 50),
            verification_timeout=fact_check_yaml.get("verification_timeout", 30),
        ),
        prompts=PromptsConfig(**prompts_kwargs) if prompts_kwargs else PromptsConfig(),
        logging=LogConfig(
            enabled=logging_yaml.get("enabled", True),
            log_directory=logging_yaml.get("log_directory", "./reorganization_logs"),
            verbosity=log_verbosity,
            format=log_format,
        ),
        embedding=maintenance_embedding_config,
        collection_name=maintenance_collection_name,
        backup_directory=maintenance_yaml.get("backup_directory"),
        decay=lifecycle_decay_config,
    )

    # Load maintenance LLM configurations
    maintenance_llm_yaml = maintenance_yaml.get("llm", {})

    # Configure logging from config
    log_level_str = logging_config.get("level", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logging.basicConfig(level=log_level, format='%(name)s: %(message)s')

    # Optionally enable verbose extraction debugging
    if logging_config.get("extraction_debug", False):
        logging.getLogger('friday_memory.context.extractor').setLevel(logging.DEBUG)

    # Chat participant names
    # Use SessionConfig for clean typed access to common values
    user_name = session_config.user_name
    assistant_name = session_config.assistant_name

    # Token budget settings - use context_window (new) or fall back to max_context_tokens (deprecated)
    context_window = memory_config.get("context_window", memory_config.get("max_context_tokens", 8192))
    output_buffer = memory_config.get("output_buffer", 2000)

    # Priming configuration (entity-driven semantic search with recency)
    priming_config = memory_config.get("priming", {
        "enabled": True,
        "top_entities": 10,
        "insights_per_entity": 3,
        "max_facts": 10,
        "recency_days": 0,
        "token_budget": 500,
    })

    # Determine if using separate extraction model
    use_separate_extraction = (
        extraction_config.get("model")
        and extraction_config.get("model") != llm_config.get("model")
    )

    # Display configuration
    print_banner()
    display_info(f"Chat: {user_name} ↔ {assistant_name}")
    get_console().print(f"[cyan]Chat LLM:[/cyan] {llm_config.get('model', 'unknown')}")
    if use_separate_extraction:
        get_console().print(f"[cyan]Extraction LLM:[/cyan] {extraction_config.get('model')} (separate)")
    else:
        get_console().print(f"[cyan]Extraction LLM:[/cyan] {llm_config.get('model', 'unknown')} (shared)")
    if extraction_config.get("prompt"):
        get_console().print("[cyan]Extraction prompt:[/cyan] custom (from config)")
    else:
        get_console().print("[cyan]Extraction prompt:[/cyan] default")
    get_console().print(f"[cyan]Embedding Model:[/cyan] {embedding_config.get('model', 'unknown')}")
    get_console().print(f"[cyan]API Base:[/cyan] {llm_config.get('api_base', 'default')}")
    get_console().print(f"[cyan]Temperature:[/cyan] {llm_config.get('temperature', 0.7)}")
    get_console().print()
    get_console().print("[bold]Token Budget:[/bold]")
    get_console().print(f"  Context window: {context_window}")
    get_console().print(f"  Output buffer: {output_buffer}")
    get_console().print(f"  Available for context: ~{context_window - output_buffer - 500} tokens")
    get_console().print(f"[cyan]Max History Turns:[/cyan] {memory_config.get('max_history_turns', 10)}")
    get_console().print()
    # Context format applies to all turns
    get_console().print(f"[cyan]Context Format:[/cyan] {memory_config.get('context_format', 'plain')}")
    get_console().print()
    if priming_config.get("enabled", True):
        top_ent = priming_config.get("top_entities", 10)
        insights_per = priming_config.get("insights_per_entity", 3)
        recency = priming_config.get("recency_days", 0)
        recency_str = f", last {recency} days" if recency > 0 else ", all time"
        display_info(f"Context Priming: {top_ent} entities × {insights_per} insights each{recency_str}")
        get_console().print(f"  [dim]Token budget: {priming_config.get('token_budget', 500)}[/dim]")
    else:
        display_info("Context Priming: disabled")
    get_console().print()

    # Build resilience config
    resilience = ResilienceConfig(
        max_retries=llm_config.get("max_retries", 3),
        timeout_seconds=llm_config.get("timeout_seconds", 30.0),
    )

    # 1. Initialize Chat LLM service
    try:
        llm = LiteLLMService(
            model_name=llm_config.get("model", "openai/local-model"),
            api_key=llm_config.get("api_key"),
            api_base=llm_config.get("api_base"),
            resilience=resilience,
        )
    except Exception as e:
        display_error(f"Error initializing Chat LLM: {e}")
        sys.exit(1)

    # 2. Initialize Extraction LLM service (separate or shared)
    if use_separate_extraction:
        try:
            extraction_resilience = ResilienceConfig(
                max_retries=extraction_config.get("max_retries", 2),
                timeout_seconds=extraction_config.get("timeout_seconds", 60.0),
            )
            extraction_llm = LiteLLMService(
                model_name=extraction_config.get("model"),
                api_key=extraction_config.get("api_key"),
                api_base=extraction_config.get("api_base"),
                resilience=extraction_resilience,
            )
        except Exception as e:
            display_warning(f"Error initializing Extraction LLM: {e}")
            display_info("Falling back to shared LLM for extraction.")
            extraction_llm = llm
    else:
        extraction_llm = llm

    # 2b. Initialize Maintenance LLM services (for /reorganize command)
    maintenance_llms: dict[str, LiteLLMService] = {}
    maintenance_llm_failures: list[str] = []  # Track which roles failed

    def create_maintenance_llm(role: str) -> LiteLLMService | None:
        """Create a LiteLLMService for a maintenance role if configured."""
        role_config = maintenance_llm_yaml.get(role, {})
        if not role_config or not role_config.get("model"):
            return None  # Not configured - will fall back to main LLM
        try:
            role_resilience = ResilienceConfig(
                max_retries=role_config.get("max_retries", 2),
                timeout_seconds=role_config.get("timeout_seconds", 60.0),
            )
            return LiteLLMService(
                model_name=role_config.get("model"),
                api_key=role_config.get("api_key"),
                api_base=role_config.get("api_base"),
                resilience=role_resilience,
            )
        except Exception as e:
            logger.warning(f"Failed to create {role} LLM: {e}")
            maintenance_llm_failures.append(f"{role}: {e}")
            return None

    for role in ["synthesizer", "classifier", "researcher", "judge"]:
        role_llm = create_maintenance_llm(role)
        if role_llm:
            maintenance_llms[role] = role_llm

    # Report maintenance LLM status to user
    if maintenance_llms:
        display_info(f"Maintenance LLMs: {', '.join(maintenance_llms.keys())}")
    if maintenance_llm_failures:
        display_warning("Some maintenance LLMs failed to initialize:")
        for failure in maintenance_llm_failures:
            get_console().print(f"  [dim]- {failure}[/dim]")
        get_console().print("  [dim]/reorganize will use main chat LLM as fallback[/dim]")

    # 3. Initialize Embedding service
    try:
        embedding_resilience = ResilienceConfig(
            timeout_seconds=embedding_config.get("timeout_seconds", 30.0),
        )
        embedding = LiteLLMEmbeddingService(
            model_name=embedding_config.get("model", "openai/nomic-embed-text-v1.5"),
            api_key=embedding_config.get("api_key"),
            api_base=embedding_config.get("api_base"),
            resilience=embedding_resilience,
        )
    except Exception as e:
        display_error(f"Error initializing LiteLLMEmbeddingService: {e}")
        sys.exit(1)

    # 3. Create memory stores
    # Persistence directory for vector, graph, and transcript stores
    persist_dir = Path(__file__).parent / memory_config.get("persist_directory", "./vector")
    persist_dir.mkdir(parents=True, exist_ok=True)

    # SQLite transcript store for persistent conversation logging
    transcript_path = persist_dir / "transcript.db"
    transcript_store = SQLiteTranscriptStore(transcript_path)

    # TranscriptBackedEpisodicStore wraps transcript for episodic memory
    system_prompt = chat_config.get("system_prompt", "You are a helpful assistant.")
    episodic = TranscriptBackedEpisodicStore(
        transcript_store=transcript_store,
        model_name=llm_config.get("model", "unknown"),
        system_prompt=system_prompt,
    )

    # ElementXGraphStore with disk persistence
    graph_path = persist_dir / "graph.json"
    graph = ElementXGraphStore(storage_path=str(graph_path))

    # ChromaVectorStore with disk persistence

    vector = ChromaVectorStore(
        collection_name=memory_config.get("collection_name", "memory_chat_test"),
        embedding_function=embedding,
        persist_directory=str(persist_dir),
    )

    # 3b. Create CollectionManager for lifecycle management
    lifecycle_config = memory_config.get("lifecycle", {})
    collection_config = CollectionConfig(
        short_term_collection=memory_config.get("collection_name", "memory_chat_test") + "_short",
        long_term_collection=memory_config.get("collection_name", "memory_chat_test") + "_long",
        decayed_collection=memory_config.get("collection_name", "memory_chat_test") + "_decayed",
    )
    collection_manager = CollectionManager(
        embedding_function=embedding,
        config=collection_config,
        path=str(persist_dir),
    )

    # 3c. Create MemoryPromotionService for lifecycle operations
    decay_config = DecayConfig(
        decay_rate=lifecycle_config.get("decay_rate", 0.01),
        short_term_min_age_hours=lifecycle_config.get("short_term_min_age_hours", 24),
        promotion_threshold=lifecycle_config.get("promotion_threshold", 0.7),
        decay_threshold=lifecycle_config.get("decay_threshold", 0.2),
    )
    promotion_service = MemoryPromotionService(
        config=decay_config,
        collection_manager=collection_manager,
        graph_store=graph,
    )

    # 3d. Create AccessBuffer for lazy access tracking
    access_buffer_config = AccessBufferConfig(
        max_buffer_size=lifecycle_config.get("access_buffer_size", 1000),
        max_buffer_age_seconds=lifecycle_config.get("access_buffer_age_seconds", 300),
        decay_score_boost=lifecycle_config.get("decay_score_boost", 0.1),
    )
    access_buffer = AccessBuffer(access_buffer_config)

    # 3e. Create RetrievalFactorComputer for pre-computed scores
    factor_config = FactorComputerConfig(
        decay_rate=lifecycle_config.get("factor_decay_rate", 0.005),
        usage_boost_factor=lifecycle_config.get("usage_boost_factor", 0.1),
    )
    factor_computer = RetrievalFactorComputer(factor_config)

    # 3f. Create GraphPathScorer for graph path filtering
    graph_scorer_config = GraphPathScorerConfig(
        edge_weight=lifecycle_config.get("graph_edge_weight", 0.4),
        target_weight=lifecycle_config.get("graph_target_weight", 0.6),
        hit_count_boost=lifecycle_config.get("graph_hit_boost", 0.05),
        path_threshold=lifecycle_config.get("graph_path_threshold", 0.5),
    )
    graph_scorer = GraphPathScorer(graph_scorer_config)

    # 4. Create telemetry recorder
    telemetry = DebugTelemetryRecorder()

    # 5. Create MemoryController with priming config and lifecycle components
    controller = MemoryController(
        vector_store=vector,
        graph_store=graph,
        episodic_store=episodic,
        telemetry=telemetry,
        priming_config=priming_config,
        # Lifecycle components (Phase 6)
        collection_manager=collection_manager,
        access_buffer=access_buffer,
        graph_scorer=graph_scorer,
        # Cross-session history support
        transcript_store=transcript_store,
    )

    # 6. Create PromptArchitect (token budgeting) with speaker names
    architect = PromptArchitect(
        model_name=llm_config.get("model", "gpt-4"),
        max_tokens=context_window,
        output_buffer=output_buffer,
        user_name=user_name,
        assistant_name=assistant_name,
    )

    # 7. Create ContextAssembler
    assembler = ContextAssembler(
        memory_controller=controller,
        model_name=llm_config.get("model", "gpt-4"),
        max_tokens=context_window,
        telemetry=telemetry,
    )

    # 8. Create MemoryExtractor with extraction LLM, custom prompt, and participant names
    #    Pass embedding model for pre-computing edge embeddings (enables fast graph path scoring)
    extraction_prompt = extraction_config.get("prompt")  # None uses default
    extractor = MemoryExtractor(
        memory_controller=controller,
        llm=extraction_llm,  # Uses dedicated extraction LLM (or shared if not configured)
        telemetry=telemetry,
        prompt_template=extraction_prompt,
        user_name=user_name,
        assistant_name=assistant_name,
        embedding_model=embedding,  # Pre-compute edge embeddings for graph path scoring
    )
    assembler.set_extractor(extractor)

    # 9. Create session
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    user_id = "test_user"

    # Create transcript session for persistent logging
    transcript_session = TranscriptSession(
        session_id=session_id,
        user_id=user_id,
        model_name=llm_config.get("model", "unknown"),
        system_prompt=system_prompt,
        config_snapshot={
            "temperature": llm_config.get("temperature", 0.7),
            "max_history_turns": memory_config.get("max_history_turns", 10),
        },
    )
    await transcript_store.create_session(transcript_session)

    # Get context format from memory config (applies to all turns, not just priming)
    context_format = memory_config.get("context_format", "plain")

    # Get transcript export directory from config
    transcript_export_dir = transcript_config.get("export_directory")
    if transcript_export_dir:
        transcript_export_dir = Path(transcript_export_dir)

    session = MemoryChatSession(
        llm=llm,
        controller=controller,
        assembler=assembler,
        architect=architect,
        system_prompt=system_prompt,
        session_id=session_id,
        user_id=user_id,
        temperature=llm_config.get("temperature", 0.7),
        max_history_turns=memory_config.get("max_history_turns", 10),
        extractor=extractor,
        user_name=user_name,
        assistant_name=assistant_name,
        transcript_store=transcript_store,
        context_format=context_format,
        persist_dir=persist_dir,
        maintenance_config=maintenance_config,
        maintenance_llms=maintenance_llms,
        transcript_export_dir=transcript_export_dir,
        embedding_function=embedding,
        promotion_service=promotion_service,
        access_buffer=access_buffer,
        factor_computer=factor_computer,
    )

    # Initialize session
    await session.initialize()

    # Auto-inject tools if configured
    tools_context_config = tools_config.get("context", {})
    if tools_context_config.get("include_in_context", False):
        session.assembler.set_active_tools(TOOL_SCHEMAS)
        logger.info(f"Auto-injected {len(TOOL_SCHEMAS)} tools into context")
        get_console().print(f"  [dim]- Tools: {len(TOOL_SCHEMAS)} auto-injected[/dim]")

    display_success(f"Session initialized: {session_id}")
    display_info(f"Persistence directory: {persist_dir}")
    get_console().print("  [dim]- Vector store: ChromaDB[/dim]")
    get_console().print(f"  [dim]- Graph store: {graph_path}[/dim]")
    get_console().print(f"  [dim]- Transcript store: {transcript_path}[/dim]")
    get_console().print("  [dim]- Lifecycle: enabled (short/long/decayed collections)[/dim]")
    get_console().print("  [dim]- Access buffer: enabled (lazy tracking)[/dim]")
    get_console().print("  [dim]- Factor computer: enabled (pre-computed scores)[/dim]")
    get_console().print("  [dim]- Graph scorer: enabled (path filtering)[/dim]")
    get_console().print("  [dim]- Retrieval integration: enabled (lifecycle-aware recall)[/dim]")

    # Trigger priming and populate session.last_payload for /context command
    if priming_config.get("enabled", True):
        await controller._ensure_session_primed(session_id)

        # Fetch primed context into session.last_payload so /context works immediately
        session.last_payload = await controller.recall(
            query="",
            session_id=session_id,
            include_history=True,
        )

        priming_info = controller.get_priming_info(session_id)
        if priming_info["primed"] and priming_info["entity_count"] > 0:
            entity_count = priming_info['entity_count']
            insight_count = priming_info.get('insight_count', 0)
            summary_count = priming_info.get('summary_count', 0)
            rel_count = priming_info['relationship_count']
            display_success(f"Context primed: {entity_count} entities, {insight_count} insights, {summary_count} summaries, {rel_count} relationships")
            if priming_info["relationship_summaries"]:
                get_console().print("  [bold]Prior knowledge:[/bold]")
                for summary in priming_info["relationship_summaries"][:3]:
                    get_console().print(f"    [dim]{summary}[/dim]")
                if rel_count > 3:
                    get_console().print(f"    [dim]... and {rel_count - 3} more[/dim]")
        else:
            display_info("Context priming: no prior data found (new memory)")
    display_info("Entity extraction: enabled (LLM-based)")
    get_console().print()

    # Create input handler with history and command completion
    history_file = persist_dir / ".friday_history" if persist_dir else None
    input_handler = create_friday_input_handler(
        user_name=user_name,
        history_file=history_file,
        multiline=False,  # Single-line mode by default
    )

    # Main loop with cleanup
    try:
        while True:
            try:
                # Get user input with readline editing, history, and completion
                user_input = await input_handler.get_input_async()

                # Handle EOF (Ctrl+D)
                if user_input is None:
                    display_info("\nGoodbye!")
                    break

                # Skip empty input
                if not user_input:
                    continue

                # Handle commands
                cmd_result = await session.handle_command(user_input)
                if cmd_result is not None:
                    if cmd_result == "EXIT":
                        display_info("Goodbye!")
                        break
                    get_console().print(cmd_result)
                    continue

                # Process as chat message
                await session.process_turn(user_input)

            except KeyboardInterrupt:
                display_info("\nInterrupted. Goodbye!")
                break
            except Exception as e:
                display_error(f"Unexpected error: {type(e).__name__}: {e}", exception=e)

    finally:
        # Session cleanup: finalize transcript and resources
        display_info("Finalizing session...")
        try:
            if transcript_store and session_id:
                ended = await transcript_store.end_session(session_id)
                if ended:
                    logger.info(f"Session {session_id} finalized")
                else:
                    logger.warning(f"Session {session_id} could not be finalized")
        except Exception as e:
            logger.warning(f"Error during session cleanup: {e}")


if __name__ == "__main__":
    asyncio.run(main())
