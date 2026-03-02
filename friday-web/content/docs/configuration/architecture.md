---
title: "Configuration Architecture"
description: "How Friday loads and merges configuration from files, env vars, and defaults."
weight: 1
---

Friday loads configuration in a layered order — built-in defaults, then YAML config files, then environment variables — so each layer can override the previous.

## Hierarchical Config Merging

Friday merges configuration from multiple sources in a well-defined priority order.

**Configuration Priority (Lowest to Highest)**

1. **Code Defaults** — Sensible baseline values defined in Pydantic models
2. **System Config File** — `config.yaml` in your project root or working directory
3. **Environment Variables** — Override config values for deployment
4. **Runtime Overrides** — Programmatic configuration changes in code

Each layer overrides values from lower layers, allowing you to establish defaults, customize per-environment, and override at runtime when needed.

**Example: Configuration Layer Override**

```yaml
# config.yaml - Base configuration
llm:
  model: "gpt-4o-mini"
  temperature: 0.7
  max_retries: 3
```

```bash
# Environment override for production
export FRIDAY_LLM_MODEL="gpt-4o"
export FRIDAY_LLM_MAX_RETRIES="5"
```

```python
# Runtime override for specific agent
from friday_llm import ResilienceConfig

config = ResilienceConfig.from_environment()
config.max_retries = 10
```

**Deep Merge Behavior**

Friday performs deep merging for nested configuration dictionaries. You can override individual nested keys without replacing entire sections.

```yaml
# config.yaml
memory:
  priming:
    enabled: true
    top_entities: 50
    max_insights: 50
```

```bash
# Override just the top_entities value
export FRIDAY_MEMORY__PRIMING__TOP_ENTITIES="100"
# Other priming settings remain unchanged
```

**Configuration File Discovery**

Friday searches for configuration files in the following order:

1. Path specified via `--config` CLI argument
2. `FRIDAY_CONFIG_PATH` environment variable
3. `./config.yaml` in current working directory
4. `~/.friday/config.yaml` in user home directory
5. Package defaults (no file needed)

**Multi-Environment Configuration Pattern**

```bash
project/
├── config.yaml              # Base configuration
├── config.dev.yaml          # Development overrides
├── config.staging.yaml      # Staging overrides
└── config.prod.yaml         # Production overrides
```

```bash
# Load environment-specific config
export FRIDAY_CONFIG_PATH="config.prod.yaml"
python memory-chat-v2.py
```

## Configuration Validation

Friday validates all configuration on startup using Pydantic models, ensuring type safety and catching misconfigurations before they cause runtime errors.

**Type Checking**

Every configuration value is validated against its expected type. Pydantic automatically coerces compatible types and raises clear errors for incompatible values.

```yaml
# INVALID - temperature must be a float
llm:
  temperature: "very creative"  # ValidationError

# VALID - automatic type coercion
llm:
  temperature: "0.7"  # Coerced to float 0.7
```

**Range Validation**

```yaml
# INVALID - temperature must be 0.0-2.0
llm:
  temperature: 5.0  # ValidationError: Input should be less than or equal to 2.0
```

**Interpreting Validation Errors**

```text
pydantic_core._pydantic_core.ValidationError: 3 validation errors for ResilienceConfig
max_retries
  Input should be less than or equal to 10 [type=less_than_equal, input_value=100]
timeout_seconds
  Input should be greater than or equal to 1.0 [type=greater_than_equal, input_value=0]
circuit_breaker.failure_threshold
  Field required [type=missing, input_value={'enabled': True}]
```

**Common Validation Errors**

| Error Type | Cause | Solution |
|------------|-------|----------|
| `type=less_than_equal` | Value exceeds maximum | Check valid range in docs |
| `type=missing` | Required field not provided | Add the missing field |
| `type=string_type` | Expected string, got number | Quote numeric-looking strings |
| `type=url_parsing` | Invalid URL format | Verify URL syntax |
| `type=path_not_exists` | File path doesn't exist | Create directory or fix path |

```python
from friday_llm.config import ResilienceConfig
from pydantic import ValidationError

try:
    config = ResilienceConfig.from_environment()
    print("Configuration valid")
except ValidationError as e:
    print(f"Configuration error:\n{e}")
```

## Environment Variable Mapping

Environment variables provide a secure, deployment-friendly way to override configuration. Friday follows a consistent naming convention.

**Naming Convention**

```text
FRIDAY_{PACKAGE}_{SECTION}__{NESTED_KEY}
```

- `FRIDAY_` prefix identifies Friday configuration
- `{PACKAGE}` identifies the package (LLM, MEMORY, SANDBOX)
- `{SECTION}` identifies the config section
- Double underscore `__` separates nested levels
- Single underscore `_` separates words within a key

**Examples**

```bash
# Top-level core settings
FRIDAY_APP_ENV="production"
FRIDAY_LOG_LEVEL="INFO"

# LLM configuration
FRIDAY_LLM_MODEL="gpt-4o"
FRIDAY_LLM_TEMPERATURE="0.7"
FRIDAY_LLM_MAX_RETRIES="5"

# Nested configuration (double underscore)
FRIDAY_LLM__CIRCUIT_BREAKER__ENABLED="true"
FRIDAY_LLM__CIRCUIT_BREAKER__FAILURE_THRESHOLD="3"

# Memory configuration
FRIDAY_MEMORY__CONTEXT_WINDOW="32000"
FRIDAY_MEMORY__PRIMING__ENABLED="true"
FRIDAY_MEMORY__PRIMING__TOP_ENTITIES="50"
```

**Type Coercion**

Environment variables are strings, but Friday automatically coerces them to the expected types:

```bash
# Boolean values (case-insensitive)
FRIDAY_MEMORY__PRIMING__ENABLED="true"   # → True
FRIDAY_MEMORY__PRIMING__ENABLED="false"  # → False
FRIDAY_MEMORY__PRIMING__ENABLED="1"      # → True

# Numeric values
FRIDAY_LLM_TEMPERATURE="0.7"             # → float 0.7
FRIDAY_LLM_MAX_RETRIES="5"               # → int 5

# Lists (comma-separated)
FRIDAY_TOOLS__REGISTRY="file_read,file_write,directory_list"
```

**Loading from .env Files**

Friday automatically loads environment variables from `.env` files using Pydantic Settings:

```bash
# .env file
FRIDAY_APP_ENV=production
OPENAI_API_KEY=sk-proj-...
FRIDAY_LLM_MODEL=gpt-4o
FRIDAY_LLM_MAX_RETRIES=5
```

```python
# Automatically loaded on import
from friday_core.config import FridayBaseSettings

settings = FridayBaseSettings()  # Loads from .env
print(settings.APP_ENV)  # "production"
```

**Security Best Practices**

1. Never commit `.env` files — add to `.gitignore`
2. Use `.env.example` to document required variables without values
3. Rotate keys regularly, especially for production environments
4. Use secret managers (AWS Secrets Manager, HashiCorp Vault) for production
5. Limit key scope — use API keys with minimal required permissions

**Example .env.example**

```bash
# Friday Agent Framework Configuration
# Copy to .env and fill in your values

# Required: API Keys
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: Model Configuration
FRIDAY_LLM_MODEL=gpt-4o-mini
FRIDAY_LLM_TEMPERATURE=0.7

# Optional: Memory Configuration
FRIDAY_MEMORY__CONTEXT_WINDOW=32000
FRIDAY_MEMORY__PRIMING__ENABLED=true

# Optional: Logging
FRIDAY_LOG_LEVEL=INFO
```

**Best Practices by Environment**

- **Development**: Use `config.yaml` with local models and verbose logging
- **Staging**: Use environment variables to override API endpoints and models
- **Production**: Store secrets only in environment variables, never in config files
- **Testing**: Use runtime overrides to inject test configurations

## Related Pages

- [LLM Providers](/docs/configuration/llm/) — Configure cloud and local LLM providers
- [Memory Settings](/docs/configuration/memory/) — Memory-specific configuration options
- [Full Reference](/docs/configuration/reference/) — Complete key reference and defaults table
