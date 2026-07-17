"""
Agent Configuration Loader.

Loads agent profiles from YAML configuration files.
Supports validation, caching, and hot reload.

Ref: docs/archive/agent-phase-artifacts/completed-friday-agentic-core/agent-configuration-build-plan.md
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from friday_agent.profile import AgentProfile
from friday_agent.skills import is_valid_skill_ref

logger = logging.getLogger(__name__)


class AgentConfigError(Exception):
    """Raised when agent configuration is invalid."""

    def __init__(self, message: str, path: Path | None = None):
        self.path = path
        super().__init__(f"{path}: {message}" if path else message)


class AgentLoader:
    """
    Load agent profiles from YAML configuration files.

    Features:
    - YAML parsing with validation
    - Profile caching
    - Directory scanning
    - Hot reload support

    Usage:
        loader = AgentLoader(Path("agents/"))
        profile = loader.load("researcher")
        all_profiles = loader.load_all()
    """

    # Required fields in agent config. `system_prompt_template` remains a
    # compatibility alias for serialized/internal shapes.
    REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
        "name": ("name",),
        "role": ("role",),
        "goal": ("goal",),
        "system_prompt": ("system_prompt", "system_prompt_template"),
    }

    # Default values for optional fields
    DEFAULTS: dict[str, Any] = {
        "tools": [],
        "skills": [],
        "tool_autonomy": "manual",
        "capabilities": [],
        "temperature": 0.7,
        "max_tokens": None,
        "llm_service": None,
        "agent_type": "interactive",
        "context_strategy": "standard",
        "memory_config": {},
        "metadata": {},
        "injected_tools": [],
        "available_tools": [],
        "required_tools": [],
    }

    def __init__(self, agents_dir: Path | str | None = None):
        """
        Initialize loader.

        Args:
            agents_dir: Directory containing agent YAML files.
                       Defaults to ./agents/ relative to cwd.
        """
        if agents_dir is None:
            self._agents_dir = Path.cwd() / "agents"
        else:
            self._agents_dir = Path(agents_dir)

        self._cache: dict[str, AgentProfile] = {}
        logger.debug(f"AgentLoader initialized with dir: {self._agents_dir}")

    @property
    def agents_dir(self) -> Path:
        """Get the agents directory path."""
        return self._agents_dir

    def load(self, name: str) -> AgentProfile:
        """
        Load agent profile by name.

        Args:
            name: Agent name (filename without .yaml extension)

        Returns:
            AgentProfile instance

        Raises:
            AgentConfigError: If file not found or invalid
        """
        # Check cache first
        if name in self._cache:
            logger.debug(f"Returning cached profile: {name}")
            return self._cache[name]

        # Find and load file
        path = self._agents_dir / f"{name}.yaml"
        if not path.exists():
            # Try .yml extension
            path = self._agents_dir / f"{name}.yml"
            if not path.exists():
                raise AgentConfigError(f"Agent config not found: {name}", path)

        config = self._parse_yaml(path)
        profile = self._config_to_profile(config)

        # Cache the profile
        self._cache[name] = profile
        logger.info(f"Loaded agent profile: {name}")

        return profile

    def load_all(self) -> dict[str, AgentProfile]:
        """
        Load all agent profiles from the agents directory.

        Returns:
            Dict mapping agent name to profile

        Raises:
            AgentConfigError: If any file is invalid
        """
        if not self._agents_dir.exists():
            logger.warning(f"Agents directory not found: {self._agents_dir}")
            return {}

        profiles: dict[str, AgentProfile] = {}

        # Find all YAML files
        for path in sorted(self._agents_dir.glob("*.yaml")):
            name = path.stem
            try:
                profiles[name] = self.load(name)
            except AgentConfigError as e:
                logger.error(f"Failed to load {name}: {e}")
                raise

        for path in sorted(self._agents_dir.glob("*.yml")):
            name = path.stem
            if name not in profiles:  # Avoid duplicates
                try:
                    profiles[name] = self.load(name)
                except AgentConfigError as e:
                    logger.error(f"Failed to load {name}: {e}")
                    raise

        logger.info(f"Loaded {len(profiles)} agent profiles")
        return profiles

    def list_available(self) -> list[str]:
        """
        List available agent names without loading them.

        Returns:
            List of agent names (filenames without extension)
        """
        if not self._agents_dir.exists():
            return []

        names = set()
        for path in self._agents_dir.glob("*.yaml"):
            names.add(path.stem)
        for path in self._agents_dir.glob("*.yml"):
            names.add(path.stem)

        return sorted(names)

    def reload(self, name: str) -> AgentProfile:
        """
        Force reload agent config (bypass cache).

        Args:
            name: Agent name to reload

        Returns:
            Fresh AgentProfile
        """
        self._cache.pop(name, None)
        return self.load(name)

    def reload_all(self) -> dict[str, AgentProfile]:
        """
        Force reload all agent configs.

        Returns:
            Dict of fresh profiles
        """
        self._cache.clear()
        return self.load_all()

    def clear_cache(self) -> None:
        """Clear all cached profiles."""
        self._cache.clear()
        logger.debug("Agent cache cleared")

    def _parse_yaml(self, path: Path) -> dict[str, Any]:
        """
        Parse YAML file with validation.

        Args:
            path: Path to YAML file

        Returns:
            Parsed configuration dict

        Raises:
            AgentConfigError: If file is invalid
        """
        try:
            with open(path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise AgentConfigError(f"Invalid YAML: {e}", path) from e
        except OSError as e:
            raise AgentConfigError(f"Cannot read file: {e}", path) from e

        if not isinstance(config, dict):
            raise AgentConfigError("Config must be a YAML object", path)

        # Validate required fields
        missing = [
            field_name
            for field_name, aliases in self.REQUIRED_FIELDS.items()
            if not any(alias in config for alias in aliases)
        ]
        if missing:
            raise AgentConfigError(f"Missing required fields: {missing}", path)

        # Validate name matches filename
        if config["name"] != path.stem:
            raise AgentConfigError(
                f"Agent name '{config['name']}' must match filename '{path.stem}'",
                path,
            )

        # Validate field types
        self._validate_types(config, path)

        return config

    def _validate_types(self, config: dict[str, Any], path: Path) -> None:
        """Validate field types match expected schema."""
        validators: dict[str, tuple[type[Any] | tuple[type[Any], ...], str]] = {
            "name": (str, "must be a string"),
            "role": (str, "must be a string"),
            "goal": (str, "must be a string"),
            "system_prompt": (str, "must be a string"),
            "system_prompt_template": (str, "must be a string"),
            "tools": (list, "must be a list"),
            "skills": (list, "must be a list"),
            "capabilities": (list, "must be a list"),
            "temperature": ((int, float), "must be a number"),
            "max_tokens": (int, "must be an integer"),
            "llm_service": (str, "must be a string"),
            "agent_type": (str, "must be a string"),
            "tool_autonomy": (str, "must be a string"),
            "context_strategy": (str, "must be a string"),
            "memory_config": (dict, "must be an object"),
            "metadata": (dict, "must be an object"),
            "injected_tools": (list, "must be a list"),
            "available_tools": (list, "must be a list"),
            "required_tools": (list, "must be a list"),
        }

        unknown_fields = sorted(set(config) - set(validators))
        if unknown_fields:
            raise AgentConfigError(f"Unknown fields: {unknown_fields}", path)

        for field, (expected_type, message) in validators.items():
            if field in config and not isinstance(config[field], expected_type):
                raise AgentConfigError(f"Field '{field}' {message}", path)

        if (
            "system_prompt" in config
            and "system_prompt_template" in config
            and config["system_prompt"] != config["system_prompt_template"]
        ):
            raise AgentConfigError(
                "system_prompt and system_prompt_template must match when both are set",
                path,
            )

        # Validate enums
        if config.get("tool_autonomy") not in ("manual", "auto", "hybrid", None):
            raise AgentConfigError(
                "tool_autonomy must be 'manual', 'auto', or 'hybrid'", path
            )

        if config.get("context_strategy") not in (
            "minimal",
            "standard",
            "extended",
            None,
        ):
            raise AgentConfigError(
                "context_strategy must be 'minimal', 'standard', or 'extended'", path
            )

        if config.get("agent_type") not in ("interactive", "autonomous", "custom", None):
            raise AgentConfigError(
                "agent_type must be 'interactive', 'autonomous', or 'custom'",
                path,
            )

        # Validate temperature range
        temp = config.get("temperature")
        if temp is not None and not (0 <= temp <= 2):
            raise AgentConfigError("temperature must be between 0 and 2", path)

        # Validate canonical skill references
        skills = config.get("skills", [])
        for skill_ref in skills:
            if not isinstance(skill_ref, str) or not is_valid_skill_ref(skill_ref):
                raise AgentConfigError(
                    "skills entries must use canonical format skill_id@version",
                    path,
                )

    def _config_to_profile(self, config: dict[str, Any]) -> AgentProfile:
        """
        Convert parsed config to AgentProfile.

        Applies defaults for missing optional fields.
        """
        # Merge with defaults
        full_config = {**self.DEFAULTS, **config}

        return AgentProfile(
            name=full_config["name"],
            role=full_config["role"],
            goal=full_config["goal"],
            system_prompt_template=full_config.get(
                "system_prompt",
                full_config.get("system_prompt_template", ""),
            ),
            tools=full_config["tools"],
            tool_autonomy=full_config["tool_autonomy"],
            temperature=full_config["temperature"],
            max_tokens=full_config["max_tokens"],
            llm_service=full_config["llm_service"],
            agent_type=full_config["agent_type"],
            context_strategy=full_config["context_strategy"],
            # Tool autonomy
            injected_tools=full_config["injected_tools"],
            available_tools=full_config["available_tools"],
            required_tools=full_config["required_tools"],
            # Registry integration fields
            _capabilities=full_config["capabilities"],
            _skills=full_config["skills"],
            _memory_config=full_config["memory_config"],
            _metadata=full_config["metadata"],
        )
