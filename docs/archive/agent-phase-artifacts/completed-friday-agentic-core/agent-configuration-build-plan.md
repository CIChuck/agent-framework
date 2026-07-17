# Agent Configuration Build Plan

**Status:** Planning
**Target:** Phase 2, Section 3.1 of Project Hive Master Plan
**Objective:** Define agents as data (YAML) with declarative configuration

---

## 1. Problem Statement

Agent profiles are currently hardcoded or passed programmatically. This creates friction for:
- **Version control**: Agent definitions can't be easily tracked in git
- **Customization**: Changing agent behavior requires code changes
- **Team collaboration**: Sharing agent configurations is difficult
- **Experimentation**: A/B testing different agent configs is cumbersome
- **Non-developers**: Business users can't modify agent behavior

We need declarative YAML-based configuration that enables:
- Version-controlled agent definitions
- Easy customization without code changes
- Team sharing of agent configurations
- Runtime loading without redeployment

---

## 2. Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      agents/ Directory                       │
├─────────────────────────────────────────────────────────────┤
│  researcher.yaml  │  coder.yaml  │  reviewer.yaml  │  ...   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       AgentLoader                            │
│  - Parses YAML files                                        │
│  - Validates against schema                                 │
│  - Converts to AgentProfile                                 │
│  - Caches loaded profiles                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      AgentProfile                            │
│  - name, role, goal                                         │
│  - system_prompt_template                                   │
│  - tools, capabilities                                      │
│  - temperature, max_tokens                                  │
│  - context_strategy                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AgentRegistry (next phase)                │
│  - Stores profiles for orchestrator access                  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Design Principles

1. **Schema-First**: YAML schema defines the contract
2. **Validation**: Fail fast on invalid configurations
3. **Templating**: System prompts support `{{placeholders}}`
4. **Extensible**: Metadata field allows custom extensions
5. **Cacheable**: Profiles loaded once and cached

---

## 3. Implementation

### 3.1 Agent YAML Schema

**Location:** `packages/friday-agent/src/friday_agent/schemas/agent.schema.yaml`

```yaml
# JSON Schema for agent configuration files
$schema: "http://json-schema.org/draft-07/schema#"
$id: "https://friday.ai/schemas/agent.schema.yaml"
title: "Friday Agent Configuration"
description: "Schema for defining Friday agent profiles"
type: object

required:
  - name
  - role
  - goal
  - system_prompt

properties:
  name:
    type: string
    description: "Unique agent identifier (lowercase, alphanumeric with underscores)"
    pattern: "^[a-z][a-z0-9_]*$"
    minLength: 2
    maxLength: 50
    examples:
      - researcher
      - coder
      - code_reviewer

  role:
    type: string
    description: "Human-readable role description"
    minLength: 5
    maxLength: 100
    examples:
      - "Research Analyst"
      - "Software Developer"

  goal:
    type: string
    description: "Primary objective of the agent"
    minLength: 10
    maxLength: 500
    examples:
      - "Find accurate information and synthesize knowledge"

  system_prompt:
    type: string
    description: "System prompt template. Supports {{placeholder}} syntax for variable substitution."
    minLength: 50

  tools:
    type: array
    description: "List of tool names to enable for this agent"
    items:
      type: string
    default: []
    examples:
      - ["web_search", "read_file", "recall_memory"]

  tool_autonomy:
    type: string
    description: "Tool execution mode"
    enum:
      - manual    # User must approve each tool call
      - auto      # Tools execute automatically
      - hybrid    # Auto for safe tools, manual for destructive
    default: "manual"

  capabilities:
    type: array
    description: "Capability tags for orchestrator routing"
    items:
      type: string
      pattern: "^[a-z][a-z0-9_]*$"
    default: []
    examples:
      - ["research", "information_gathering", "fact_checking"]

  temperature:
    type: number
    description: "LLM temperature (0.0 = deterministic, 2.0 = creative)"
    minimum: 0
    maximum: 2
    default: 0.7

  max_tokens:
    type: integer
    description: "Maximum tokens in LLM response"
    minimum: 1
    maximum: 128000
    default: 4096

  context_strategy:
    type: string
    description: "Context assembly strategy"
    enum:
      - minimal   # Minimal context (fast, cheap)
      - standard  # Balanced context
      - extended  # Maximum context (thorough, expensive)
    default: "standard"

  memory_config:
    type: object
    description: "Agent-specific memory settings"
    properties:
      enable_graph:
        type: boolean
        default: true
      enable_vector:
        type: boolean
        default: true
      max_episodic_turns:
        type: integer
        minimum: 1
        default: 20
    default: {}

  metadata:
    type: object
    description: "Additional custom metadata for extensions"
    additionalProperties: true
    default: {}

additionalProperties: false
```

### 3.2 Example Agent Configurations

**Researcher Agent (`agents/researcher.yaml`):**

```yaml
# Researcher Agent Configuration
# Specializes in finding and synthesizing information

name: researcher
role: "Research Analyst"
goal: "Find accurate information and synthesize knowledge from multiple sources"

system_prompt: |
  You are a research analyst specializing in {{domain}}.

  Your task is to find accurate, relevant information and present it clearly.

  Guidelines:
  - Always cite sources when possible
  - Distinguish between facts and opinions
  - Acknowledge uncertainty when information is incomplete
  - Cross-reference multiple sources for accuracy
  - Summarize findings in a clear, structured format

  Current research focus: {{focus}}

tools:
  - web_search
  - read_file
  - recall_memory
  - store_fact
  - search_documents

tool_autonomy: auto

capabilities:
  - research
  - information_gathering
  - fact_checking
  - summarization
  - citation

temperature: 0.3
max_tokens: 8192
context_strategy: extended

memory_config:
  enable_graph: true
  enable_vector: true
  max_episodic_turns: 30

metadata:
  version: "1.0.0"
  author: "friday-team"
  tags: ["core", "research"]
```

**Coder Agent (`agents/coder.yaml`):**

```yaml
# Coder Agent Configuration
# Specializes in writing and reviewing code

name: coder
role: "Software Developer"
goal: "Write clean, tested, maintainable code following best practices"

system_prompt: |
  You are an expert software developer.

  Your responsibilities:
  - Write clean, well-documented code
  - Follow best practices for the language/framework
  - Consider edge cases and error handling
  - Write tests for critical functionality
  - Explain your design decisions

  Coding style:
  - Prefer clarity over cleverness
  - Use meaningful variable names
  - Keep functions small and focused
  - Document public APIs

  Current project context: {{project_context}}

tools:
  - read_file
  - write_file
  - execute_code
  - recall_memory
  - search_code
  - run_tests

tool_autonomy: hybrid

capabilities:
  - coding
  - debugging
  - code_review
  - testing
  - refactoring

temperature: 0.2
max_tokens: 4096
context_strategy: standard

memory_config:
  enable_graph: true
  enable_vector: true
  max_episodic_turns: 20

metadata:
  version: "1.0.0"
  author: "friday-team"
  supported_languages: ["python", "typescript", "go"]
```

**Reviewer Agent (`agents/reviewer.yaml`):**

```yaml
# Reviewer Agent Configuration
# Specializes in code review and quality assurance

name: reviewer
role: "Code Reviewer"
goal: "Ensure code quality through thorough, constructive reviews"

system_prompt: |
  You are an experienced code reviewer.

  Your review approach:
  - Be constructive, not critical
  - Focus on significant issues first
  - Explain the "why" behind suggestions
  - Acknowledge good practices
  - Consider maintainability and readability

  Review checklist:
  - Logic correctness
  - Error handling
  - Security concerns
  - Performance implications
  - Test coverage
  - Documentation

tools:
  - read_file
  - search_code
  - recall_memory
  - store_fact

tool_autonomy: auto

capabilities:
  - code_review
  - quality_assurance
  - security_review
  - documentation_review

temperature: 0.3
max_tokens: 4096
context_strategy: extended

metadata:
  version: "1.0.0"
  author: "friday-team"
```

### 3.3 AgentLoader Implementation

**Location:** `packages/friday-agent/src/friday_agent/loader.py`

```python
"""Agent configuration loader from YAML files."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from friday_agent.profile import AgentProfile


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

    # Required fields in agent config
    REQUIRED_FIELDS = ["name", "role", "goal", "system_prompt"]

    # Default values for optional fields
    DEFAULTS = {
        "tools": [],
        "tool_autonomy": "manual",
        "capabilities": [],
        "temperature": 0.7,
        "max_tokens": 4096,
        "context_strategy": "standard",
        "memory_config": {},
        "metadata": {},
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
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise AgentConfigError(f"Invalid YAML: {e}", path)
        except IOError as e:
            raise AgentConfigError(f"Cannot read file: {e}", path)

        if not isinstance(config, dict):
            raise AgentConfigError("Config must be a YAML object", path)

        # Validate required fields
        missing = [f for f in self.REQUIRED_FIELDS if f not in config]
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
        validators = {
            "name": (str, "must be a string"),
            "role": (str, "must be a string"),
            "goal": (str, "must be a string"),
            "system_prompt": (str, "must be a string"),
            "tools": (list, "must be a list"),
            "capabilities": (list, "must be a list"),
            "temperature": ((int, float), "must be a number"),
            "max_tokens": (int, "must be an integer"),
            "tool_autonomy": (str, "must be a string"),
            "context_strategy": (str, "must be a string"),
            "memory_config": (dict, "must be an object"),
            "metadata": (dict, "must be an object"),
        }

        for field, (expected_type, message) in validators.items():
            if field in config and not isinstance(config[field], expected_type):
                raise AgentConfigError(f"Field '{field}' {message}", path)

        # Validate enums
        if config.get("tool_autonomy") not in ("manual", "auto", "hybrid", None):
            raise AgentConfigError(
                f"tool_autonomy must be 'manual', 'auto', or 'hybrid'", path
            )

        if config.get("context_strategy") not in (
            "minimal",
            "standard",
            "extended",
            None,
        ):
            raise AgentConfigError(
                f"context_strategy must be 'minimal', 'standard', or 'extended'", path
            )

        # Validate temperature range
        temp = config.get("temperature")
        if temp is not None and not (0 <= temp <= 2):
            raise AgentConfigError("temperature must be between 0 and 2", path)

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
            system_prompt_template=full_config["system_prompt"],
            tools=full_config["tools"],
            tool_autonomy=full_config["tool_autonomy"],
            temperature=full_config["temperature"],
            max_tokens=full_config["max_tokens"],
            context_strategy=full_config["context_strategy"],
            # Registry integration fields
            _capabilities=full_config["capabilities"],
            _memory_config=full_config["memory_config"],
            _metadata=full_config["metadata"],
        )
```

### 3.4 AgentProfile Updates

**Location:** `packages/friday-agent/src/friday_agent/profile.py`

Update existing AgentProfile to support new fields:

```python
"""Agent profile data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentProfile:
    """
    Profile defining an agent's identity, capabilities, and configuration.

    The profile is the declarative specification of an agent, typically
    loaded from YAML configuration. It defines:
    - Identity: name, role, goal
    - Behavior: system prompt, tools, autonomy level
    - Configuration: temperature, max_tokens, context strategy

    Attributes:
        name: Unique identifier (lowercase, alphanumeric with underscores)
        role: Human-readable role description
        goal: Primary objective
        system_prompt_template: System prompt with {{placeholder}} support
        tools: List of enabled tool names
        tool_autonomy: Tool execution mode (manual/auto/hybrid)
        temperature: LLM temperature (0.0-2.0)
        max_tokens: Maximum response tokens
        context_strategy: Context assembly strategy
    """

    # Core identity
    name: str
    role: str
    goal: str

    # Behavior
    system_prompt_template: str
    tools: list[str] = field(default_factory=list)
    tool_autonomy: str = "manual"

    # LLM configuration
    temperature: float = 0.7
    max_tokens: int | None = None
    context_strategy: str = "standard"

    # Registry integration (prefixed with _ to indicate internal use)
    _capabilities: list[str] = field(default_factory=list)
    _memory_config: dict[str, Any] = field(default_factory=dict)
    _metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def capabilities(self) -> list[str]:
        """Capability tags for orchestrator routing."""
        return self._capabilities

    @property
    def memory_config(self) -> dict[str, Any]:
        """Agent-specific memory settings."""
        return self._memory_config

    @property
    def metadata(self) -> dict[str, Any]:
        """Additional custom metadata."""
        return self._metadata

    def render_system_prompt(self, **variables: Any) -> str:
        """
        Render system prompt template with variable substitution.

        Args:
            **variables: Variables to substitute (e.g., domain="AI")

        Returns:
            Rendered system prompt

        Example:
            prompt = profile.render_system_prompt(domain="AI", focus="agents")
        """
        prompt = self.system_prompt_template
        for key, value in variables.items():
            placeholder = "{{" + key + "}}"
            prompt = prompt.replace(placeholder, str(value))
        return prompt

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize profile to dictionary.

        Returns:
            Dict representation suitable for JSON/YAML
        """
        return {
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "system_prompt": self.system_prompt_template,
            "tools": self.tools,
            "tool_autonomy": self.tool_autonomy,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "context_strategy": self.context_strategy,
            "capabilities": self._capabilities,
            "memory_config": self._memory_config,
            "metadata": self._metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentProfile:
        """
        Deserialize profile from dictionary.

        Args:
            data: Dict from to_dict() or YAML config

        Returns:
            AgentProfile instance
        """
        return cls(
            name=data["name"],
            role=data["role"],
            goal=data["goal"],
            system_prompt_template=data.get("system_prompt", ""),
            tools=data.get("tools", []),
            tool_autonomy=data.get("tool_autonomy", "manual"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens"),
            context_strategy=data.get("context_strategy", "standard"),
            _capabilities=data.get("capabilities", []),
            _memory_config=data.get("memory_config", {}),
            _metadata=data.get("metadata", {}),
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"AgentProfile({self.name}: {self.role})"

    def __repr__(self) -> str:
        """Debug representation."""
        return (
            f"AgentProfile(name={self.name!r}, role={self.role!r}, "
            f"tools={len(self.tools)}, capabilities={self._capabilities})"
        )
```

### 3.5 Package Exports

**Location:** `packages/friday-agent/src/friday_agent/__init__.py`

Update to export new components:

```python
"""Friday Agent package."""

from friday_agent.profile import AgentProfile
from friday_agent.loader import AgentLoader, AgentConfigError
from friday_agent.base import AgentBase
from friday_agent.copilot import CopilotAgent

__all__ = [
    "AgentProfile",
    "AgentLoader",
    "AgentConfigError",
    "AgentBase",
    "CopilotAgent",
]
```

---

## 4. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `packages/friday-agent/src/friday_agent/schemas/agent.schema.yaml` | Create | JSON Schema for YAML validation |
| `packages/friday-agent/src/friday_agent/loader.py` | Create | AgentLoader implementation |
| `packages/friday-agent/src/friday_agent/profile.py` | Modify | Add capabilities, metadata, memory_config fields |
| `packages/friday-agent/src/friday_agent/__init__.py` | Modify | Export AgentLoader, AgentConfigError |
| `agents/researcher.yaml` | Create | Example researcher agent |
| `agents/coder.yaml` | Create | Example coder agent |
| `agents/reviewer.yaml` | Create | Example reviewer agent |
| `packages/friday-agent/tests_agent/test_loader.py` | Create | Unit tests for AgentLoader |
| `packages/friday-agent/tests_agent/fixtures/agents/` | Create | Test fixture agent configs |

---

## 5. Dependencies

### 5.1 Required (Already in project)
- `pyyaml>=6.0.0` - YAML parsing (already in friday-tools)

### 5.2 Optional (For schema validation)
- `jsonschema>=4.0.0` - Runtime schema validation (optional enhancement)

---

## 6. Verification

### 6.1 Unit Tests

```bash
# Run loader tests
pytest packages/friday-agent/tests_agent/test_loader.py -v
```

**Test Cases:**
1. Load valid agent config
2. Load all agents from directory
3. Handle missing required fields
4. Handle invalid field types
5. Handle invalid enum values
6. Handle temperature out of range
7. Handle name/filename mismatch
8. Cache behavior (load twice, hit cache)
9. Reload bypasses cache
10. Handle missing directory gracefully

### 6.2 Integration Test

```python
# Test complete flow
from friday_agent import AgentLoader, AgentProfile

# Load from YAML
loader = AgentLoader(Path("agents/"))
researcher = loader.load("researcher")

# Verify profile
assert researcher.name == "researcher"
assert "research" in researcher.capabilities
assert researcher.temperature == 0.3

# Render prompt
prompt = researcher.render_system_prompt(domain="AI", focus="agents")
assert "AI" in prompt
assert "agents" in prompt
```

### 6.3 Manual Validation

```bash
# Create test agent
cat > agents/test.yaml << EOF
name: test
role: "Test Agent"
goal: "Test the configuration system"
system_prompt: |
  You are a test agent for {{purpose}}.
tools: []
capabilities: [testing]
EOF

# Verify it loads
python -c "
from friday_agent import AgentLoader
loader = AgentLoader()
profile = loader.load('test')
print(f'Loaded: {profile}')
print(f'Capabilities: {profile.capabilities}')
"
```

---

## 7. Exit Criteria

1. `AgentLoader` can load valid YAML configs
2. `AgentLoader` rejects invalid configs with clear error messages
3. `AgentProfile` supports all schema fields
4. Example agents (researcher, coder, reviewer) load successfully
5. System prompt templating works with `{{placeholders}}`
6. Unit tests achieve 90%+ coverage
7. Documentation includes usage examples
