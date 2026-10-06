# mypy: ignore-errors

"""
Session management for CLI applications.

Provides configuration loading, lifecycle management, and graceful shutdown.

Ref: docs/archive/build-plans/completed/friday-core-legacy/memory-chat-v2-prd.md
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

import yaml

from .display import display_info, display_success

logger = logging.getLogger(__name__)

# Type variable for session context
T = TypeVar("T")


@dataclass
class SessionConfig:
    """
    Configuration container for CLI sessions.

    Loads configuration from YAML files and provides typed access
    to configuration sections.
    """

    # Raw configuration data
    raw: dict[str, Any] = field(default_factory=dict)

    # Common configuration sections
    llm: dict[str, Any] = field(default_factory=dict)
    embedding: dict[str, Any] = field(default_factory=dict)
    memory: dict[str, Any] = field(default_factory=dict)
    chat: dict[str, Any] = field(default_factory=dict)
    logging: dict[str, Any] = field(default_factory=dict)
    extraction: dict[str, Any] = field(default_factory=dict)
    transcript: dict[str, Any] = field(default_factory=dict)
    maintenance: dict[str, Any] = field(default_factory=dict)
    lifecycle: dict[str, Any] = field(default_factory=dict)
    tools: dict[str, Any] = field(default_factory=dict)
    session: dict[str, Any] = field(default_factory=dict)
    security: dict[str, Any] = field(default_factory=dict)
    speech: dict[str, Any] = field(default_factory=dict)

    # Computed/derived values
    config_path: Path | None = None

    @classmethod
    def from_yaml(cls, path: str | Path) -> SessionConfig:
        """
        Load configuration from a YAML file.

        Args:
            path: Path to YAML configuration file

        Returns:
            SessionConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
        """
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path) as f:
            raw = yaml.safe_load(f) or {}

        return cls(
            raw=raw,
            llm=raw.get("llm", {}),
            embedding=raw.get("embedding", {}),
            memory=raw.get("memory", {}),
            chat=raw.get("chat", {}),
            logging=raw.get("logging", {}),
            extraction=raw.get("extraction", {}),
            transcript=raw.get("transcript", {}),
            maintenance=raw.get("maintenance", {}),
            lifecycle=raw.get("lifecycle", {}),
            tools=raw.get("tools", {}),
            session=raw.get("session", {}),
            security=raw.get("security", {}),
            speech=raw.get("speech", {}),
            config_path=config_path,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionConfig:
        """
        Create configuration from a dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            SessionConfig instance
        """
        return cls(
            raw=data,
            llm=data.get("llm", {}),
            embedding=data.get("embedding", {}),
            memory=data.get("memory", {}),
            chat=data.get("chat", {}),
            logging=data.get("logging", {}),
            extraction=data.get("extraction", {}),
            transcript=data.get("transcript", {}),
            maintenance=data.get("maintenance", {}),
            lifecycle=data.get("lifecycle", {}),
            tools=data.get("tools", {}),
            session=data.get("session", {}),
            security=data.get("security", {}),
            speech=data.get("speech", {}),
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Get a top-level configuration value."""
        return self.raw.get(key, default)

    def get_nested(self, *keys: str, default: Any = None) -> Any:
        """
        Get a nested configuration value.

        Args:
            *keys: Path of keys to traverse
            default: Default value if not found

        Returns:
            Configuration value or default

        Example:
            config.get_nested("memory", "priming", "enabled", default=True)
        """
        value = self.raw
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    @property
    def user_name(self) -> str:
        """Get configured user display name."""
        return self.chat.get("user_name", "User")

    @property
    def assistant_name(self) -> str:
        """Get configured assistant display name."""
        return self.chat.get("assistant_name", "Assistant")

    @property
    def system_prompt(self) -> str:
        """Get configured system prompt."""
        return self.chat.get("system_prompt", "You are a helpful assistant.")

    @property
    def persist_dir(self) -> Path | None:
        """Get configured persistence directory."""
        persist_path = self.memory.get("persist_directory")
        if persist_path:
            # Resolve relative to config file if available
            if self.config_path:
                return self.config_path.parent / persist_path
            return Path(persist_path)
        return None

    # Exit maintenance properties
    @property
    def lifecycle_on_exit(self) -> bool:
        """Whether to run lifecycle cycle on exit (default: True)."""
        return self.session.get("lifecycle_on_exit", True)

    @property
    def flush_on_exit(self) -> bool:
        """Whether to flush access buffer on exit (default: True)."""
        return self.session.get("flush_on_exit", True)

    @property
    def reorganize_on_exit(self) -> bool:
        """Whether to run reorganization on exit (default: False)."""
        return self.session.get("reorganize_on_exit", False)

    @property
    def reorganize_mode(self) -> str:
        """
        Reorganization mode: 'fast' or 'full'.

        - 'fast': Backup, analyze, prune only (no LLM calls)
        - 'full': All steps including synthesis and verification

        Default: 'fast'
        """
        return self.session.get("reorganize_mode", "fast")


@dataclass
class SessionContext[T]:
    """
    Container for an active session with its resources.

    Provides access to the session object and associated resources
    that need cleanup on shutdown.
    """

    session: T
    config: SessionConfig
    resources: dict[str, Any] = field(default_factory=dict)

    def get_resource(self, name: str) -> Any | None:
        """Get a named resource."""
        return self.resources.get(name)

    def set_resource(self, name: str, resource: Any) -> None:
        """Store a named resource for cleanup."""
        self.resources[name] = resource


class SessionManager[T]:
    """
    Manages CLI session lifecycle with graceful shutdown.

    Provides:
    - Configuration loading and validation
    - Async context manager for session lifecycle
    - Signal handling for graceful shutdown (SIGINT, SIGTERM)
    - Resource cleanup on exit

    Usage:
        async with SessionManager(config_path="config.yaml") as ctx:
            session = ctx.session
            # Use session...

    Or with a factory function:
        manager = SessionManager(
            config_path="config.yaml",
            session_factory=create_my_session,
        )
        async with manager as ctx:
            # ctx.session is created by factory
    """

    def __init__(
        self,
        config: SessionConfig | None = None,
        config_path: str | Path | None = None,
        session_factory: Any | None = None,
        on_shutdown: Any | None = None,
    ):
        """
        Initialize session manager.

        Args:
            config: Pre-loaded SessionConfig (mutually exclusive with config_path)
            config_path: Path to YAML config file
            session_factory: Async callable (config) -> session to create session
            on_shutdown: Async callable (context) -> None for cleanup
        """
        if config is None and config_path is None:
            raise ValueError("Either config or config_path must be provided")

        if config is not None and config_path is not None:
            raise ValueError("Cannot provide both config and config_path")

        self._config = config
        self._config_path = Path(config_path) if config_path else None
        self._session_factory = session_factory
        self._on_shutdown = on_shutdown

        self._context: SessionContext[T] | None = None
        self._shutdown_event: asyncio.Event | None = None
        self._original_handlers: dict[int, Any] = {}

    @property
    def config(self) -> SessionConfig:
        """Get the loaded configuration."""
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Use as context manager.")
        return self._config

    @property
    def context(self) -> SessionContext[T]:
        """Get the current session context."""
        if self._context is None:
            raise RuntimeError("Session not started. Use as context manager.")
        return self._context

    def _load_config(self) -> SessionConfig:
        """Load configuration from file if not already provided."""
        if self._config is not None:
            return self._config

        if self._config_path is None:
            raise RuntimeError("No configuration source available")

        return SessionConfig.from_yaml(self._config_path)

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        if sys.platform == "win32":
            # Windows has limited signal support
            return

        self._shutdown_event = asyncio.Event()

        def signal_handler(signum: int, frame: Any) -> None:
            logger.info(f"Received signal {signum}, initiating shutdown...")
            if self._shutdown_event:
                self._shutdown_event.set()

        # Store original handlers and install new ones
        for sig in (signal.SIGINT, signal.SIGTERM):
            self._original_handlers[sig] = signal.signal(sig, signal_handler)

    def _restore_signal_handlers(self) -> None:
        """Restore original signal handlers."""
        for sig, handler in self._original_handlers.items():
            signal.signal(sig, handler)
        self._original_handlers.clear()

    async def _create_session(self, config: SessionConfig) -> T:
        """Create session using factory or return None for manual setup."""
        if self._session_factory is None:
            return None  # type: ignore

        if asyncio.iscoroutinefunction(self._session_factory):
            return await self._session_factory(config)
        else:
            return self._session_factory(config)

    async def _cleanup(self, context: SessionContext[T]) -> None:
        """Clean up session resources."""
        if self._on_shutdown:
            try:
                if asyncio.iscoroutinefunction(self._on_shutdown):
                    await self._on_shutdown(context)
                else:
                    self._on_shutdown(context)
            except Exception as e:
                logger.error(f"Error during shutdown cleanup: {e}")

    async def __aenter__(self) -> SessionContext[T]:
        """Enter async context, loading config and creating session."""
        # Load configuration
        self._config = self._load_config()

        # Set up signal handlers
        self._setup_signal_handlers()

        # Create session
        session = await self._create_session(self._config)

        # Create context
        self._context = SessionContext(
            session=session,
            config=self._config,
        )

        return self._context

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit async context, cleaning up resources."""
        try:
            if self._context:
                display_info("Shutting down session...")
                await self._cleanup(self._context)
                display_success("Session closed.")
        finally:
            self._restore_signal_handlers()
            self._context = None

        # Don't suppress exceptions
        return False

    @property
    def shutdown_requested(self) -> bool:
        """Check if shutdown has been requested via signal."""
        if self._shutdown_event is None:
            return False
        return self._shutdown_event.is_set()

    async def wait_for_shutdown(self) -> None:
        """Wait for a shutdown signal."""
        if self._shutdown_event:
            await self._shutdown_event.wait()


@asynccontextmanager
async def managed_session(
    config_path: str | Path | None = None,
    config: SessionConfig | None = None,
    session_factory: Any | None = None,
    on_shutdown: Any | None = None,
):
    """
    Convenience async context manager for managed sessions.

    Args:
        config_path: Path to YAML configuration file
        config: Pre-loaded SessionConfig
        session_factory: Async callable to create session
        on_shutdown: Async callable for cleanup

    Yields:
        SessionContext with session and config

    Example:
        async with managed_session(config_path="config.yaml") as ctx:
            print(f"User: {ctx.config.user_name}")
    """
    manager = SessionManager(
        config=config,
        config_path=config_path,
        session_factory=session_factory,
        on_shutdown=on_shutdown,
    )
    async with manager as ctx:
        yield ctx


def load_config(path: str | Path) -> SessionConfig:
    """
    Load configuration from a YAML file.

    Convenience function for simple config loading.

    Args:
        path: Path to configuration file

    Returns:
        SessionConfig instance
    """
    return SessionConfig.from_yaml(path)


def validate_config(
    config: SessionConfig,
    required_sections: list[str] | None = None,
) -> list[str]:
    """
    Validate configuration and return list of errors.

    Args:
        config: Configuration to validate
        required_sections: List of required top-level sections

    Returns:
        List of validation error messages (empty if valid)
    """
    errors: list[str] = []

    required = required_sections or ["llm"]

    for section in required:
        if not config.raw.get(section):
            errors.append(f"Missing required configuration section: {section}")

    # Validate LLM config if present
    if config.llm and not config.llm.get("model"):
        errors.append("llm.model is required")

    return errors
