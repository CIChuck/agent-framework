# Friday Agent Framework
## Section 10: Configuration Guide

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24



---

## Table of Contents

- [10.1 Configuration Architecture](#101-configuration-architecture)
  - [10.1.1 Hierarchical Config Merging](#1011-hierarchical-config-merging)
  - [10.1.2 Configuration Validation](#1012-configuration-validation)
  - [10.1.3 Environment Variable Mapping](#1013-environment-variable-mapping)
- [10.2 LLM Configuration](#102-llm-configuration)
  - [10.2.1 Provider Setup](#1021-provider-setup)
  - [10.2.2 OpenRouter for Multi-Model Access](#1022-openrouter-for-multi-model-access)
  - [10.2.3 Model-Specific Settings](#1023-model-specific-settings)
  - [10.2.4 Resilience & Retry Configuration](#1024-resilience--retry-configuration)
- [10.3 Memory Configuration](#103-memory-configuration)
  - [10.3.1 Context Window & Token Budgeting](#1031-context-window--token-budgeting)
  - [10.3.2 Priming Configuration](#1032-priming-configuration)
  - [10.3.3 Lifecycle Settings](#1033-lifecycle-settings)
  - [10.3.4 Collection Configuration](#1034-collection-configuration)
- [10.4 Tool Configuration](#104-tool-configuration)
  - [10.4.1 Tool Registry Setup](#1041-tool-registry-setup)
  - [10.4.2 Security & Sandboxing](#1042-security--sandboxing)
  - [10.4.3 Tool Allowlists and Blocklists](#1043-tool-allowlists-and-blocklists)
- [10.5 Extraction Configuration](#105-extraction-configuration)
  - [10.5.1 Extraction LLM Selection](#1051-extraction-llm-selection)
  - [10.5.2 Extraction Prompts & Rules](#1052-extraction-prompts--rules)
  - [10.5.3 Entity Types and Relationship Verbs](#1053-entity-types-and-relationship-verbs)
- [10.6 Transcript Configuration](#106-transcript-configuration)
  - [10.6.1 Storage Settings](#1061-storage-settings)
  - [10.6.2 Export Formats](#1062-export-formats)
- [10.7 Telemetry & Observability](#107-telemetry--observability)
  - [10.7.1 Logging Configuration](#1071-logging-configuration)
  - [10.7.2 Telemetry Integration](#1072-telemetry-integration)

---

## 10.1 Configuration Architecture

Friday's configuration system provides a flexible, hierarchical approach to managing settings across all framework components. Built on Pydantic for validation and type safety, the system supports multiple configuration sources with clear precedence rules.

### 10.1.1 Hierarchical Config Merging

Friday merges configuration from multiple sources in a well-defined priority order. Understanding this hierarchy is essential for effective configuration management.

**Configuration Priority (Lowest to Highest)**

1. **Code Defaults** - Sensible baseline values defined in Pydantic models
2. **System Config File** - `config.yaml` in your project root or working directory
3. **Environment Variables** - Override config values for deployment
4. **Runtime Overrides** - Programmatic configuration changes in code

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
# Override max_retries for this specific use case
config.max_retries = 10
```

**Deep Merge Behavior**

Friday performs deep merging for nested configuration dictionaries. This means you can override individual nested keys without replacing entire sections.

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

**Best Practices for Configuration Management**

- **Development**: Use `config.yaml` with local models and verbose logging
- **Staging**: Use environment variables to override API endpoints and models
- **Production**: Store secrets only in environment variables, never in config files
- **Testing**: Use runtime overrides to inject test configurations

**Multi-Environment Configuration Pattern**

```bash
# Project structure
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

### 10.1.2 Configuration Validation

Friday validates all configuration on startup using Pydantic models, ensuring type safety and catching misconfigurations before they cause runtime errors.

**Validation Features**

**Type Checking**
Every configuration value is validated against its expected type. Pydantic automatically coerces compatible types (strings to integers, etc.) and raises clear errors for incompatible values.

```yaml
# INVALID - temperature must be a float
llm:
  temperature: "very creative"  # ValidationError: Input should be a valid number

# VALID - automatic type coercion
llm:
  temperature: "0.7"  # Coerced to float 0.7
```

**Range Validation**
Numeric values are constrained to valid ranges using Pydantic's field validators.

```yaml
# INVALID - temperature must be 0.0-2.0
llm:
  temperature: 5.0  # ValidationError: Input should be less than or equal to 2.0

# INVALID - max_retries must be 0-10
llm:
  max_retries: 100  # ValidationError: Input should be less than or equal to 10
```

**Enum Validation**
Configuration values with fixed choices use enums for validation.

```yaml
# INVALID - unknown sandbox type
sandbox:
  sandbox_type: "virtual_machine"  # ValidationError: Input should be 'docker', 'subprocess', or 'mock'

# VALID
sandbox:
  sandbox_type: "docker"
```

**Dependency Validation**
Some configuration options depend on others. Friday validates these relationships automatically.

```yaml
# INVALID - circuit breaker requires failure_threshold when enabled
llm:
  resilience:
    circuit_breaker:
      enabled: true
      # Missing failure_threshold - ValidationError
```

**Custom Validators**
Complex validation rules are implemented as Pydantic validators.

```python
# From ResilienceConfig
@field_validator('backoff_min')
def validate_backoff_min(cls, v, values):
    if 'backoff_max' in values and v > values['backoff_max']:
        raise ValueError('backoff_min must be <= backoff_max')
    return v
```

**Interpreting Validation Errors**

When validation fails, Friday provides detailed error messages:

```python
pydantic_core._pydantic_core.ValidationError: 3 validation errors for ResilienceConfig
max_retries
  Input should be less than or equal to 10 [type=less_than_equal, input_value=100, input_type=int]
    For further information visit https://errors.pydantic.dev/2.5/v/less_than_equal
timeout_seconds
  Input should be greater than or equal to 1.0 [type=greater_than_equal, input_value=0, input_type=int]
    For further information visit https://errors.pydantic.dev/2.5/v/greater_than_equal
circuit_breaker.failure_threshold
  Field required [type=missing, input_value={'enabled': True}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
```

**Common Validation Errors**

| Error Type | Cause | Solution |
|------------|-------|----------|
| `type=less_than_equal` | Value exceeds maximum | Check valid range in docs |
| `type=missing` | Required field not provided | Add the missing field |
| `type=string_type` | Expected string, got number | Quote numeric-looking strings |
| `type=url_parsing` | Invalid URL format | Verify URL syntax |
| `type=path_not_exists` | File path doesn't exist | Create directory or fix path |

**Validation in Development**

During development, use validation to catch configuration errors early:

```python
from friday_llm.config import ResilienceConfig

# Test your config before running
try:
    config = ResilienceConfig.from_environment()
    print("✓ Configuration valid")
except ValidationError as e:
    print(f"✗ Configuration error:\n{e}")
```

### 10.1.3 Environment Variable Mapping

Environment variables provide a secure, deployment-friendly way to override configuration. Friday follows a consistent naming convention for environment variables.

**Naming Convention**

Environment variables use uppercase names with underscores:

```
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

# Sandbox configuration
FRIDAY_SANDBOX_TYPE="docker"
FRIDAY_SANDBOX__DOCKER__MEMORY_LIMIT="512m"
FRIDAY_SANDBOX__DOCKER__CPU_LIMIT="1.0"
```

**Type Coercion**

Environment variables are strings, but Friday automatically coerces them to the expected types:

```bash
# Boolean values (case-insensitive)
FRIDAY_MEMORY__PRIMING__ENABLED="true"   # → True
FRIDAY_MEMORY__PRIMING__ENABLED="false"  # → False
FRIDAY_MEMORY__PRIMING__ENABLED="1"      # → True
FRIDAY_MEMORY__PRIMING__ENABLED="0"      # → False

# Numeric values
FRIDAY_LLM_TEMPERATURE="0.7"             # → float 0.7
FRIDAY_LLM_MAX_RETRIES="5"               # → int 5

# Lists (comma-separated)
FRIDAY_TOOLS__REGISTRY="file_read,file_write,directory_list"  # → ["file_read", "file_write", "directory_list"]
```

**Complete Environment Variable Reference**

**Core Settings**

```bash
# Application environment
FRIDAY_APP_ENV="development"              # development | production | testing
FRIDAY_LOG_LEVEL="INFO"                   # DEBUG | INFO | WARNING | ERROR

# Default model for components that need it
FRIDAY_DEFAULT_MODEL="gpt-4o-mini"

# API keys
OPENAI_API_KEY="sk-..."                   # OpenAI API key
ANTHROPIC_API_KEY="sk-ant-..."            # Anthropic API key
GOOGLE_API_KEY="..."                      # Google Gemini API key
OPENROUTER_API_KEY="sk-or-v1-..."         # OpenRouter API key
```

**LLM Settings**

```bash
# Model selection
FRIDAY_LLM_MODEL="gpt-4o"
FRIDAY_LLM_API_BASE="https://api.openai.com/v1"
FRIDAY_LLM_TEMPERATURE="0.7"

# Retry and resilience
FRIDAY_LLM_MAX_RETRIES="3"
FRIDAY_LLM_TIMEOUT_SECONDS="30.0"
FRIDAY_LLM_STREAM_TIMEOUT_SECONDS="60.0"
FRIDAY_LLM_BACKOFF_MULTIPLIER="1.0"
FRIDAY_LLM_BACKOFF_MAX="10.0"

# Circuit breaker
FRIDAY_LLM_CIRCUIT_BREAKER_ENABLED="false"
FRIDAY_LLM_CB_FAILURE_THRESHOLD="5"
FRIDAY_LLM_CB_RECOVERY_TIMEOUT="30.0"
```

**Memory Settings**

```bash
# Context window
FRIDAY_MEMORY__CONTEXT_WINDOW="32000"
FRIDAY_MEMORY__OUTPUT_BUFFER="1000"
FRIDAY_MEMORY__MAX_HISTORY_TURNS="20"

# Priming
FRIDAY_MEMORY__PRIMING__ENABLED="true"
FRIDAY_MEMORY__PRIMING__TOP_ENTITIES="50"
FRIDAY_MEMORY__PRIMING__MAX_INSIGHTS="50"
FRIDAY_MEMORY__PRIMING__RECENCY_DAYS="0"
FRIDAY_MEMORY__PRIMING__TOKEN_BUDGET="20000"

# Lifecycle
FRIDAY_MEMORY__LIFECYCLE__ENABLED="true"
FRIDAY_MEMORY__LIFECYCLE__DECAY_RATE="0.01"
FRIDAY_MEMORY__LIFECYCLE__PROMOTION_THRESHOLD="0.7"
FRIDAY_MEMORY__LIFECYCLE__DECAY_THRESHOLD="0.5"
```

**Sandbox Settings**

```bash
# Sandbox type
FRIDAY_SANDBOX_TYPE="docker"
FRIDAY_SANDBOX_FALLBACK_SUBPROCESS="true"

# Docker configuration
FRIDAY_SANDBOX_IMAGE="friday-sandbox-python:latest"
FRIDAY_SANDBOX_MEMORY_LIMIT="512m"
FRIDAY_SANDBOX_CPU_LIMIT="1.0"
FRIDAY_SANDBOX_DEFAULT_TIMEOUT="30"
FRIDAY_SANDBOX_NETWORK_ENABLED="false"

# Workspace configuration
FRIDAY_SANDBOX_WORKSPACE_TTL="3600"
FRIDAY_SANDBOX_WORKSPACE_PATH="/tmp/friday-workspaces"
FRIDAY_SANDBOX_PRESERVE_ON_ERROR="true"
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

1. **Never commit `.env` files** - Add to `.gitignore`
2. **Use `.env.example`** - Document required variables without values
3. **Rotate keys regularly** - Especially for production environments
4. **Use secret managers** - AWS Secrets Manager, HashiCorp Vault for production
5. **Limit key scope** - Use API keys with minimal required permissions

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

---

## 10.2 LLM Configuration

Friday's LLM configuration system provides unified access to multiple model providers through LiteLLM, enabling seamless switching between OpenAI, Anthropic, Google, local models, and OpenRouter aggregation.

### 10.2.1 Provider Setup

Friday supports major cloud providers and local model hosting solutions. Each provider requires specific configuration patterns.

**OpenAI Setup**

OpenAI is the default provider with the most straightforward configuration.

```yaml
# config.yaml
llm:
  model: "gpt-4o-mini"          # or "gpt-4o", "gpt-4-turbo"
  temperature: 0.7
  max_tokens: 4096
```

```bash
# .env
OPENAI_API_KEY=sk-proj-your-openai-key
```

**Available OpenAI Models**

| Model | Context Window | Best For | Cost (per 1M tokens) |
|-------|----------------|----------|---------------------|
| `gpt-4o` | 128K | Complex reasoning, code | $2.50 / $10.00 |
| `gpt-4o-mini` | 128K | Fast, affordable tasks | $0.15 / $0.60 |
| `gpt-4-turbo` | 128K | Legacy premium tier | $10.00 / $30.00 |
| `gpt-3.5-turbo` | 16K | Simple tasks, deprecated | $0.50 / $1.50 |

**OpenAI Organization Settings**

If you belong to multiple OpenAI organizations:

```yaml
llm:
  model: "gpt-4o"
  api_base: "https://api.openai.com/v1"
```

```bash
# Specify organization in environment
OPENAI_ORGANIZATION=org-your-org-id
```

**Azure OpenAI Setup**

For Azure OpenAI Service deployments:

```yaml
llm:
  model: "azure/your-deployment-name"
  api_base: "https://your-resource.openai.azure.com"
```

```bash
# .env
AZURE_API_KEY=your-azure-key
AZURE_API_VERSION=2024-02-15-preview
```

**Anthropic Setup**

Anthropic's Claude models provide strong reasoning and tool use capabilities.

```yaml
llm:
  model: "claude-3-5-sonnet-20241022"  # Latest Sonnet
  # model: "claude-3-5-haiku-20241022"   # Fast, affordable
  # model: "claude-opus-4-5-20251101"    # Maximum capability
  temperature: 0.7
  max_tokens: 8192
```

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

**Available Claude Models**

| Model | Context Window | Best For | Cost (per 1M tokens) |
|-------|----------------|----------|---------------------|
| `claude-opus-4-5` | 200K | Frontier reasoning | $15.00 / $75.00 |
| `claude-3-5-sonnet` | 200K | Balanced performance | $3.00 / $15.00 |
| `claude-3-5-haiku` | 200K | Fast, affordable | $0.80 / $4.00 |

**Anthropic Beta Features**

Some Claude features require beta headers:

```python
# For tool use (function calling)
import litellm
litellm.modify_params = True
litellm.add_function_to_prompt = False  # Use native tool format
```

**Google Gemini Setup**

Google's Gemini models offer competitive performance with generous context windows.

```yaml
llm:
  model: "gemini/gemini-2.0-flash-exp"  # Latest experimental
  # model: "gemini/gemini-1.5-pro"      # Stable pro tier
  # model: "gemini/gemini-1.5-flash"    # Fast, affordable
  temperature: 0.7
  max_tokens: 8192
```

```bash
# .env
GOOGLE_API_KEY=your-google-api-key
```

**Available Gemini Models**

| Model | Context Window | Best For | Cost (per 1M tokens) |
|-------|----------------|----------|---------------------|
| `gemini-2.0-flash-exp` | 1M | Experimental, free tier | Free (rate limited) |
| `gemini-1.5-pro` | 1M | Production reasoning | $1.25 / $5.00 |
| `gemini-1.5-flash` | 1M | Fast, affordable | $0.075 / $0.30 |

**Gemini Grounding**

Enable Google Search grounding for factual queries:

```yaml
llm:
  model: "gemini/gemini-1.5-pro"
  # Grounding enabled via LiteLLM parameters
```

**Local Ollama Setup**

Ollama enables running models locally without API costs or rate limits.

**Installation**

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Start the service
ollama serve
```

**Pull Models**

```bash
# Download models
ollama pull llama3.1:8b         # Meta's Llama 3.1 8B
ollama pull mistral:7b          # Mistral 7B
ollama pull codellama:13b       # Code-specialized model
ollama pull qwen2.5:14b         # Alibaba's Qwen 2.5

# List downloaded models
ollama list
```

**Configuration**

```yaml
llm:
  model: "ollama/llama3.1:8b"
  api_base: "http://localhost:11434"
  temperature: 0.7
  # API key not required for local Ollama
```

**Ollama Model Selection**

| Model | Parameters | RAM Required | Best For |
|-------|-----------|--------------|----------|
| `llama3.1:8b` | 8B | 8GB | General purpose |
| `llama3.1:70b` | 70B | 48GB | Advanced reasoning |
| `mistral:7b` | 7B | 8GB | Fast inference |
| `codellama:13b` | 13B | 16GB | Code generation |
| `qwen2.5:14b` | 14B | 16GB | Multilingual |

**Local LM Studio Setup**

LM Studio provides a GUI for running local models with OpenAI-compatible API.

**Installation**

1. Download from https://lmstudio.ai
2. Install and launch LM Studio
3. Download models via the GUI (search for models by name)
4. Start local server (Developer → Start Server)

**Configuration**

```yaml
llm:
  model: "openai/local-model"      # LM Studio uses OpenAI format
  api_base: "http://localhost:1234/v1"
  api_key: "lm-studio"             # Any non-empty string
  temperature: 0.7
```

**LM Studio Best Practices**

- **Model Selection**: Download quantized models (Q4, Q5) for faster inference
- **Context Length**: Configure in LM Studio settings (default 2048, increase to 8192+ for Friday)
- **GPU Acceleration**: Enable in settings for 5-10x speedup
- **Preloading**: Load model before starting Friday to avoid cold-start delay

**Hardware Requirements for Local Models**

| Model Size | Minimum RAM | Recommended RAM | GPU VRAM (Optional) |
|------------|-------------|-----------------|---------------------|
| 3B-7B | 8GB | 16GB | 6GB |
| 8B-13B | 16GB | 32GB | 12GB |
| 30B-34B | 32GB | 64GB | 24GB |
| 70B+ | 64GB | 128GB | 48GB+ |

### 10.2.2 OpenRouter for Multi-Model Access

OpenRouter provides unified API access to 100+ models from multiple providers, enabling easy switching and fallback strategies.

**Setup**

1. Sign up at https://openrouter.ai
2. Generate API key
3. Add credits to account (pay-as-you-go)

```yaml
llm:
  model: "openrouter/anthropic/claude-3.5-sonnet"
  api_base: "https://openrouter.ai/api/v1"
```

```bash
# .env
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
```

**Model Selection**

OpenRouter uses the format `openrouter/{provider}/{model}`:

```yaml
# Anthropic models
model: "openrouter/anthropic/claude-3.5-sonnet"
model: "openrouter/anthropic/claude-3-haiku"

# OpenAI models
model: "openrouter/openai/gpt-4o"
model: "openrouter/openai/gpt-4o-mini"

# Google models
model: "openrouter/google/gemini-2.0-flash-exp"
model: "openrouter/google/gemini-1.5-pro"

# Meta models
model: "openrouter/meta-llama/llama-3.1-70b-instruct"
model: "openrouter/meta-llama/llama-3.1-405b-instruct"

# Mistral models
model: "openrouter/mistralai/mistral-large"
model: "openrouter/mistralai/mixtral-8x7b-instruct"

# Open source models
model: "openrouter/deepseek/deepseek-chat"
model: "openrouter/qwen/qwen-2.5-72b-instruct"
```

**Free Tier Models**

OpenRouter offers free-tier models (rate limited):

```yaml
model: "openrouter/google/gemini-2.0-flash-exp:free"
model: "openrouter/mistralai/mistral-7b-instruct:free"
model: "openrouter/meta-llama/llama-3.1-8b-instruct:free"
```

**Pricing**

OpenRouter adds a small markup (typically 10-15%) over provider prices. Check current pricing at https://openrouter.ai/models

**Benefits**

1. **Single API Key**: Access multiple providers without managing separate keys
2. **Fallback Strategy**: Automatically fallback to alternative models on errors
3. **Cost Optimization**: Easily switch to cheaper models for development
4. **Model Discovery**: Try new models without provider signup

**Fallback Configuration**

Configure fallback models for resilience:

```yaml
llm:
  model: "openrouter/anthropic/claude-3.5-sonnet"
  fallback_models:
    - "openrouter/openai/gpt-4o"
    - "openrouter/google/gemini-1.5-pro"
```

**Usage Tracking**

OpenRouter provides detailed usage analytics in the dashboard:
- Cost per model
- Request counts
- Latency metrics
- Error rates

### 10.2.3 Model-Specific Settings

Fine-tune model behavior with generation parameters.

**Temperature**

Controls randomness in model outputs. Lower values produce more deterministic responses.

```yaml
llm:
  temperature: 0.0  # Deterministic (fact retrieval, code)
  # temperature: 0.3  # Low variability (classification, extraction)
  # temperature: 0.7  # Balanced (general conversation)
  # temperature: 1.0  # Creative (brainstorming, writing)
  # temperature: 1.5  # Very creative (experimental)
```

**Use Cases by Temperature**

| Temperature | Best For | Example Tasks |
|-------------|----------|---------------|
| 0.0 - 0.2 | Deterministic tasks | Code generation, data extraction, classification |
| 0.3 - 0.5 | Factual responses | Q&A, summarization, translation |
| 0.6 - 0.8 | Conversational | General chat, recommendations |
| 0.9 - 1.2 | Creative tasks | Brainstorming, creative writing |
| 1.3 - 2.0 | Experimental | Highly diverse outputs |

**Max Tokens**

Limits the response length. Different models have different maximum token limits.

```yaml
llm:
  max_tokens: 1000    # Short responses
  # max_tokens: 4096   # Standard responses
  # max_tokens: 8192   # Long-form content
  # max_tokens: 16384  # Very long outputs
```

**Model Context Limits**

| Model | Max Context | Recommended max_tokens |
|-------|-------------|------------------------|
| GPT-4o | 128K | 4K - 8K |
| Claude 3.5 | 200K | 4K - 8K |
| Gemini 1.5 | 1M | 8K - 16K |
| Llama 3.1 | 128K | 2K - 4K |

**Top P (Nucleus Sampling)**

Alternative to temperature. Controls diversity by sampling from the top P probability mass.

```yaml
llm:
  top_p: 0.9  # Default, includes 90% probability mass
  # top_p: 0.95  # More diverse
  # top_p: 0.5   # Less diverse
```

**When to Use top_p vs temperature**

- Use `temperature` for most cases (more intuitive)
- Use `top_p` when you want to exclude low-probability tokens without affecting high-probability tokens
- Don't adjust both simultaneously (they interact non-linearly)

**Frequency Penalty & Presence Penalty (OpenAI)**

Reduce repetition by penalizing repeated tokens.

```yaml
llm:
  frequency_penalty: 0.5  # Penalize frequent tokens (-2.0 to 2.0)
  presence_penalty: 0.5   # Penalize any repeated tokens (-2.0 to 2.0)
```

**Penalty Guidelines**

- `frequency_penalty`: Reduces repetition based on token frequency in output
- `presence_penalty`: Reduces repetition based on token presence (yes/no)
- Higher values (0.5 - 1.0) reduce repetition
- Lower values (0.0) allow natural repetition
- Negative values encourage repetition (rarely useful)

**Stop Sequences**

Define custom tokens that stop generation.

```yaml
llm:
  stop_sequences:
    - "\n\n\n"      # Stop at triple newline
    - "###"         # Stop at delimiter
    - "END_OUTPUT"  # Stop at custom marker
```

**Use Cases**

- Structured output generation (stop at delimiter)
- Preventing overgeneration
- Multi-turn parsing (stop at turn boundary)

**Complete Model Configuration Example**

```yaml
# config.yaml - Production configuration
llm:
  # Model selection
  model: "gpt-4o"
  api_base: "https://api.openai.com/v1"

  # Generation parameters
  temperature: 0.7
  max_tokens: 4096
  top_p: 0.9
  frequency_penalty: 0.3
  presence_penalty: 0.3
  stop_sequences:
    - "\n\n\n"

  # Retry and resilience
  max_retries: 3
  timeout_seconds: 60.0

  # Cost optimization
  fallback_models:
    - "gpt-4o-mini"  # Fallback to cheaper model on rate limits
```

### 10.2.4 Resilience & Retry Configuration

Friday's resilience layer wraps LLM calls with retry logic, timeout enforcement, and circuit breakers to handle transient failures gracefully.

**Retry Configuration**

Control how Friday retries failed LLM requests.

```yaml
llm:
  resilience:
    # Retry attempts
    max_retries: 3           # 0 disables retries

    # Exponential backoff
    backoff_multiplier: 1.0  # Backoff growth rate
    backoff_min: 1.0         # Minimum wait (seconds)
    backoff_max: 10.0        # Maximum wait (seconds)
```

**Backoff Calculation**

Friday uses exponential backoff with jitter:

```
wait_time = min(backoff_min * (backoff_multiplier ^ attempt) + jitter, backoff_max)
```

**Example backoff sequence** (backoff_min=1.0, backoff_multiplier=2.0):
- Attempt 1: 1.0s
- Attempt 2: 2.0s
- Attempt 3: 4.0s
- Attempt 4: 8.0s (capped at backoff_max)

**Retryable Errors**

Friday automatically retries these error types:
- `RateLimitError` - API rate limit exceeded
- `ServiceUnavailableError` - Temporary service outage
- `APIConnectionError` - Network connectivity issues
- `InternalServerError` - Provider-side errors (5xx)

**Non-Retryable Errors**

These errors fail immediately without retry:
- `AuthenticationError` - Invalid API key
- `InvalidRequestError` - Malformed request
- `NotFoundError` - Model doesn't exist
- `ContextLengthExceededError` - Input too long

**Timeout Configuration**

Prevent hanging requests with timeout enforcement.

```yaml
llm:
  resilience:
    timeout_seconds: 30.0         # Standard calls
    stream_timeout_seconds: 60.0  # Streaming calls (longer)
```

**Timeout Guidelines**

| Operation | Recommended Timeout |
|-----------|---------------------|
| Short prompts (<500 tokens) | 30s |
| Medium prompts (500-2K tokens) | 60s |
| Long prompts (2K-8K tokens) | 120s |
| Code generation | 90s |
| Streaming responses | 60-120s |

**Circuit Breaker Configuration**

Circuit breakers prevent cascading failures by failing fast after repeated errors.

```yaml
llm:
  resilience:
    circuit_breaker:
      enabled: true
      failure_threshold: 5       # Open after N failures
      recovery_timeout: 30.0     # Wait before retry (seconds)
      half_open_max_calls: 1     # Test calls in half-open state
```

**Circuit Breaker States**

1. **CLOSED** (Normal): Requests pass through normally
2. **OPEN** (Failing): All requests fail immediately (fast-fail)
3. **HALF_OPEN** (Testing): Allow limited requests to test recovery

**State Transitions**

```
CLOSED --[failure_threshold failures]--> OPEN
OPEN --[recovery_timeout expires]--> HALF_OPEN
HALF_OPEN --[success]--> CLOSED
HALF_OPEN --[failure]--> OPEN
```

**When to Enable Circuit Breakers**

- **Enable**: Production systems with multiple LLM providers (fallback available)
- **Enable**: High-volume applications where cascading failures are costly
- **Disable**: Development environments (you want to see actual errors)
- **Disable**: Single-provider systems (failing fast doesn't help)

**Preset Configurations**

Friday provides preset resilience configurations for common scenarios.

**Default (Balanced)**

```yaml
llm:
  resilience:
    max_retries: 3
    timeout_seconds: 30.0
    backoff_multiplier: 1.0
    circuit_breaker:
      enabled: false
```

**Aggressive (High Availability)**

```python
from friday_llm.config import ResilienceConfig

config = ResilienceConfig.aggressive()
# max_retries=5, timeout=60s, circuit_breaker enabled
```

**Disabled (Development)**

```python
config = ResilienceConfig.disabled()
# max_retries=0, timeout=600s, no circuit breaker
```

**Environment Variable Override**

```bash
# Override resilience settings
export FRIDAY_LLM_MAX_RETRIES="5"
export FRIDAY_LLM_TIMEOUT_SECONDS="60.0"
export FRIDAY_LLM_CIRCUIT_BREAKER_ENABLED="true"
export FRIDAY_LLM_CB_FAILURE_THRESHOLD="3"

# Load from environment
python -c "
from friday_llm.config import ResilienceConfig
config = ResilienceConfig.from_environment()
print(config)
"
```

**Complete Resilience Example**

```yaml
# config.yaml - Production resilience configuration
llm:
  # Model configuration
  model: "gpt-4o"

  # Resilience settings
  resilience:
    # Retry configuration
    max_retries: 5
    backoff_multiplier: 2.0
    backoff_min: 1.0
    backoff_max: 30.0

    # Timeout configuration
    timeout_seconds: 60.0
    stream_timeout_seconds: 120.0

    # Circuit breaker
    circuit_breaker:
      enabled: true
      failure_threshold: 3
      recovery_timeout: 60.0
      half_open_max_calls: 1

# Fallback to cheaper model on extended outage
fallback_models:
  - "gpt-4o-mini"
```

**Monitoring Resilience**

Track resilience metrics to tune configuration:

```python
# Access resilience metrics (future feature)
from friday_llm import LiteLLMService

service = LiteLLMService(model_name="gpt-4o")

# After some operations
metrics = service.get_metrics()
print(f"Total calls: {metrics.total_calls}")
print(f"Failed calls: {metrics.failed_calls}")
print(f"Retried calls: {metrics.retried_calls}")
print(f"Circuit breaker opens: {metrics.circuit_breaker_opens}")
```

---

## 10.3 Memory Configuration

Friday's memory system is highly configurable, allowing you to optimize for different use cases, context window sizes, and performance requirements.

### 10.3.1 Context Window & Token Budgeting

Token budgeting controls how Friday allocates its limited context window across different components.

**Token Budget Hierarchy**

```
Total Context Window (e.g., 32K tokens)
├── Output Buffer (reserved for LLM response)
├── System Prompt (agent identity and instructions)
├── Priming (knowledge from prior sessions)
└── Dynamic Context (per-turn allocation)
    ├── Conversation History (episodic memory)
    ├── Retrieved Insights (vector store)
    ├── Loaded Entities (graph store)
    └── Tool Schemas (if applicable)
```

**Basic Configuration**

```yaml
memory:
  # Total context window of your LLM
  context_window: 32000

  # Tokens reserved for model output
  output_buffer: 1000

  # Maximum conversation turns to include
  max_history_turns: 20
```

**Context Window by Model**

| Model | Context Window | Recommended Setting |
|-------|----------------|---------------------|
| GPT-4o | 128K | 32000 - 128000 |
| GPT-4o-mini | 128K | 32000 - 128000 |
| Claude 3.5 Sonnet | 200K | 32000 - 200000 |
| Claude 3.5 Haiku | 200K | 32000 - 200000 |
| Gemini 1.5 Pro | 1M | 32000 - 1000000 |
| Llama 3.1 8B | 128K | 8000 - 32000 |
| Mistral 7B | 32K | 8000 - 32000 |

**Output Buffer Guidelines**

The output buffer reserves tokens for the model's response.

| Use Case | Recommended Buffer |
|----------|-------------------|
| Short responses (chat) | 500 - 1000 |
| Medium responses (explanations) | 1000 - 2000 |
| Long responses (documents) | 2000 - 4000 |
| Code generation | 2000 - 4000 |
| Multi-turn planning | 1500 - 3000 |

**Dynamic Budget Allocation**

Friday automatically allocates the remaining budget across dynamic components:

```python
dynamic_budget = context_window - output_buffer - len(system_prompt) - len(priming)
```

The ContextAssembler uses a knapsack optimization algorithm to pack maximum value into the dynamic budget:

1. **Score each memory** - Relevance × Importance × Recency
2. **Estimate token cost** - Number of tokens per memory
3. **Solve knapsack** - Maximize value within budget constraint
4. **Assemble context** - Include selected memories

**Consolidation Settings**

Automatically summarize old conversation history to save tokens.

```yaml
memory:
  # Consolidate after N turns
  consolidate_after_turns: 50

  # Keep recent turns verbatim, summarize older turns
  consolidation_keep_recent: 10
```

**How Consolidation Works**

1. After 50 turns, Friday triggers consolidation
2. Keeps last 10 turns verbatim (full detail)
3. Summarizes turns 1-40 into compact summaries
4. Reduces token usage by 60-80% for old history

**Example: Before and After Consolidation**

```
Before Consolidation (50 turns × 200 tokens = 10,000 tokens):
Turn 1: User: "What is Python?" Assistant: "Python is..."
Turn 2: User: "How do I install it?" Assistant: "You can..."
...
Turn 50: User: "Show me an example" Assistant: "Here's..."

After Consolidation (4,000 tokens):
Summary (turns 1-40): "User learned about Python basics, installation..."
Turn 41: User: "..." Assistant: "..."  [verbatim]
...
Turn 50: User: "Show me an example" Assistant: "Here's..."  [verbatim]
```

**Context Format Configuration**

Control how supporting context is formatted for the LLM.

```yaml
memory:
  # Format options: plain, json, xml, markdown
  context_format: markdown
```

**Format Comparison**

| Format | Token Efficiency | LLM Comprehension | Best For |
|--------|------------------|-------------------|----------|
| `plain` | High | Good | Local models, small context |
| `json` | Medium | Good | Structured data, APIs |
| `xml` | Low | Excellent | Claude models, complex structure |
| `markdown` | Medium | Excellent | GPT-4, general purpose |

**Example Formats**

Plain:
```
Supporting Context:
Entity: Python (Technology) - hit_count: 15
Relationship: Chuck USES Python
Insight: Chuck prefers Python for backend development
```

Markdown:
```markdown
## Supporting Context

### Entities
- **Python** (Technology) - Access count: 15
- **Chuck** (Person) - Access count: 42

### Relationships
- Chuck → USES → Python

### Insights
> Chuck prefers Python for backend development (confidence: 0.9)
```

**Advanced: Per-Component Budgets**

For fine-grained control, configure explicit budgets:

```yaml
memory:
  budgets:
    system_prompt_tokens: 1000
    history_tokens: 5000
    vector_tokens: 3000
    graph_tokens: 2000
    tool_tokens: 2000
```

This explicit allocation overrides automatic budget calculation.

### 10.3.2 Priming Configuration

Priming preloads the agent's context with relevant knowledge from prior sessions, providing continuity and domain awareness before the user's first message.

**What is Priming?**

When a session starts, Friday can prime the context with:
- Top entities by access count (most frequently referenced)
- Key relationships between entities
- Recent insights and learnings
- Session-relevant summaries

This creates a "warm start" where the agent already knows important facts about the user, project, or domain before processing the first query.

**Basic Priming Configuration**

```yaml
memory:
  priming:
    # Enable/disable priming
    enabled: true

    # Entity selection
    top_entities: 50          # Include top N most accessed entities
    include_orphans: false    # Include entities without relationships

    # Content limits
    max_insights: 50          # Maximum insights to include
    max_relationships: 100    # Maximum relationships to include

    # Temporal filtering
    recency_days: 0           # 0 = no filtering, 30 = last 30 days only

    # Token budgeting
    token_budget: 20000       # Maximum tokens for priming
```

**Entity Selection Strategies**

Control which entities are included in priming:

```yaml
memory:
  priming:
    # Strategy 1: Access-based (default)
    top_entities: 50
    sort_by: "hit_count"      # Most frequently accessed

    # Strategy 2: Recency-based
    sort_by: "last_accessed"
    recency_days: 7           # Only entities from last week

    # Strategy 3: Confidence-based
    sort_by: "confidence"     # Highest extraction confidence
    min_confidence: 0.7

    # Strategy 4: Hybrid
    sort_by: "weighted"       # Weighted combination
    weights:
      hit_count: 0.5
      confidence: 0.3
      recency: 0.2
```

**Relationship Filtering**

Configure which relationships are included:

```yaml
memory:
  priming:
    relationships:
      # Include all relationship types
      include_all_types: true

      # Or specify allowed types
      allowed_types:
        - "KNOWS"
        - "USES"
        - "WORKS_ON"
        - "PREFERS"

      # Minimum strength threshold
      min_strength: 0.5

      # Maximum per entity
      max_per_entity: 10
```

**Content Type Configuration**

Select which memory types to include:

```yaml
memory:
  priming:
    include:
      entities: true          # Entity nodes
      relationships: true     # Entity relationships
      insights: true          # Extracted insights
      summaries: true         # Session summaries
      tool_outputs: false     # Large tool outputs (usually omitted)
```

**Recency Windows**

Apply temporal filters to priming content:

```yaml
memory:
  priming:
    recency:
      # Global recency filter (applies to all content)
      enabled: true
      days: 30                # Last 30 days only

      # Per-content-type recency
      entities_days: 0        # All entities (no filter)
      relationships_days: 30  # Relationships from last 30 days
      insights_days: 7        # Insights from last week
      summaries_days: 14      # Summaries from last 2 weeks
```

**Token Budget Management**

Control how tokens are allocated within priming:

```yaml
memory:
  priming:
    token_budget: 20000

    # Budget allocation (must sum to 1.0)
    allocation:
      entities: 0.3           # 30% for entities
      relationships: 0.2      # 20% for relationships
      insights: 0.3           # 30% for insights
      summaries: 0.2          # 20% for summaries
```

**Complete Priming Example**

```yaml
# config.yaml - Comprehensive priming configuration
memory:
  priming:
    # Core settings
    enabled: true
    token_budget: 20000

    # Entity selection
    top_entities: 50
    sort_by: "hit_count"
    include_orphans: false
    min_confidence: 0.6

    # Relationship filtering
    relationships:
      max_relationships: 100
      max_per_entity: 10
      min_strength: 0.5
      allowed_types:
        - "KNOWS"
        - "USES"
        - "WORKS_ON"
        - "PREFERS"
        - "CREATED"

    # Content selection
    include:
      entities: true
      relationships: true
      insights: true
      summaries: true
      tool_outputs: false

    # Temporal filtering
    recency:
      enabled: true
      entities_days: 0        # All entities
      relationships_days: 30  # Last 30 days
      insights_days: 7        # Last week
      summaries_days: 14      # Last 2 weeks

    # Budget allocation
    allocation:
      entities: 0.3
      relationships: 0.2
      insights: 0.3
      summaries: 0.2
```

**Use Case Examples**

**Long-Running Projects**

Optimize for continuity across many sessions:

```yaml
memory:
  priming:
    enabled: true
    token_budget: 30000      # Large budget for rich context
    top_entities: 100         # Include many entities
    recency_days: 0           # All historical knowledge
    max_insights: 100
    sort_by: "hit_count"      # Most important entities
```

**Short-Term Tasks**

Optimize for recent, focused information:

```yaml
memory:
  priming:
    enabled: true
    token_budget: 10000      # Smaller budget
    top_entities: 20          # Fewer entities
    recency_days: 3           # Last 3 days only
    max_insights: 20
    sort_by: "last_accessed"  # Most recent entities
```

**Privacy-Sensitive Contexts**

Minimize priming to reduce context:

```yaml
memory:
  priming:
    enabled: true
    token_budget: 5000       # Minimal budget
    top_entities: 10
    include:
      entities: true
      relationships: false   # No relationships
      insights: true
      summaries: false       # No summaries
```

**Environment Variable Overrides**

```bash
# Enable/disable priming
FRIDAY_MEMORY__PRIMING__ENABLED="true"

# Entity selection
FRIDAY_MEMORY__PRIMING__TOP_ENTITIES="50"
FRIDAY_MEMORY__PRIMING__SORT_BY="hit_count"

# Budget
FRIDAY_MEMORY__PRIMING__TOKEN_BUDGET="20000"

# Recency
FRIDAY_MEMORY__PRIMING__RECENCY_DAYS="7"
```

### 10.3.3 Lifecycle Settings

Memory lifecycle settings control how memories age, decay, and transition between stages (SHORT_TERM → LONG_TERM → DECAYED).

**Lifecycle Stages**

Friday's memory system uses three lifecycle stages:

1. **SHORT_TERM** - New memories, recently accessed, high decay score
2. **LONG_TERM** - Promoted memories, frequently accessed, important
3. **DECAYED** - Rarely accessed memories, marked for cleanup

**Core Decay Configuration**

```yaml
memory:
  lifecycle:
    # Enable lifecycle management
    enabled: true

    # Decay parameters
    decay_rate: 0.01          # Lambda for exponential decay (0.001-0.5)
    access_boost: 0.2         # Score boost on each access

    # Stage transition thresholds
    promotion_threshold: 0.7  # Score needed for SHORT_TERM → LONG_TERM
    decay_threshold: 0.2      # Score below which → DECAYED
```

**Decay Formula**

Friday uses exponential decay:

```
score(t) = score_0 × e^(-λ × hours_since_last_access)
```

Where:
- `λ` (lambda) is the `decay_rate`
- `score_0` is the initial score (typically 1.0)
- Time is measured in hours since last access

**Decay Rate Examples**

| Decay Rate | 24h Score | 72h Score | 1 Week Score | Decay Speed |
|------------|-----------|-----------|--------------|-------------|
| 0.001 | 98% | 93% | 86% | Very slow |
| 0.005 | 88% | 68% | 39% | Slow |
| 0.01 | 79% | 49% | 19% | Medium (default) |
| 0.02 | 62% | 24% | 4% | Fast |
| 0.05 | 30% | 3% | <1% | Very fast |

**Choosing the Right Decay Rate**

```yaml
# Very slow decay - Long-term projects
memory:
  lifecycle:
    decay_rate: 0.001        # Memories stay relevant for months
    decay_threshold: 0.1     # Very forgiving

# Slow decay - General purpose
memory:
  lifecycle:
    decay_rate: 0.005
    decay_threshold: 0.2

# Medium decay - Default balanced setting
memory:
  lifecycle:
    decay_rate: 0.01
    decay_threshold: 0.2

# Fast decay - Short-term tasks
memory:
  lifecycle:
    decay_rate: 0.02
    decay_threshold: 0.3

# Very fast decay - Single-session focus
memory:
  lifecycle:
    decay_rate: 0.05
    decay_threshold: 0.4
```

**Promotion Configuration**

Control how memories are promoted from SHORT_TERM to LONG_TERM:

```yaml
memory:
  lifecycle:
    promotion:
      # Minimum time in SHORT_TERM before eligible
      min_age_hours: 24

      # Promotion score threshold
      threshold: 0.7

      # Scoring weights (must sum to 1.0)
      weights:
        age: 0.2              # Time in short-term
        access: 0.4           # Access frequency (most important)
        confidence: 0.2       # Extraction confidence
        connection: 0.2       # Graph connections
```

**Promotion Score Calculation**

```
promotion_score = (w_age × age_score) +
                 (w_access × access_score) +
                 (w_confidence × confidence_score) +
                 (w_connection × connection_score)
```

Where:
- **age_score**: Normalized time in SHORT_TERM (0-1)
- **access_score**: Normalized access count (0-1)
- **confidence_score**: Extraction confidence (0-1)
- **connection_score**: Normalized connection count (0-1)

**Access Boost Configuration**

Control how accessing memories affects their decay score:

```yaml
memory:
  lifecycle:
    # Boost applied on each access
    access_boost: 0.2         # Add 0.2 to decay score (capped at 1.0)

    # Maximum score from repeated access
    max_score: 1.0            # Score ceiling

    # Cool-down between boosts (prevents spam)
    boost_cooldown_hours: 1   # Only boost once per hour
```

**Decay Check Scheduling**

Control when decay calculations run:

```yaml
memory:
  lifecycle:
    # Decay check interval
    check_interval_hours: 24  # Run decay checks daily

    # Run on session start
    check_on_session_start: true

    # Run on session end
    check_on_session_end: false

    # Batch size for processing
    batch_size: 100           # Process 100 memories at a time
```

**Cleanup Configuration**

Control how DECAYED memories are handled:

```yaml
memory:
  lifecycle:
    cleanup:
      # Retention period for DECAYED memories
      retention_days: 30      # Keep DECAYED for 30 days

      # Hard deletion after retention
      auto_delete: true       # Delete after retention_days

      # Cleanup schedule
      cleanup_interval_hours: 168  # Weekly cleanup (7 days)

      # Safety limits
      max_deletions_per_run: 1000  # Maximum memories to delete at once
```

**Stage-Specific Settings**

Configure behavior per lifecycle stage:

```yaml
memory:
  lifecycle:
    stages:
      short_term:
        # Minimum age before promotion check
        min_age_hours: 24

        # Maximum capacity (soft limit)
        max_capacity: 10000

        # Decay rate (can override global)
        decay_rate: 0.01

      long_term:
        # Maximum capacity (soft limit)
        max_capacity: 50000

        # Decay rate (slower than short-term)
        decay_rate: 0.005

        # Re-evaluation interval
        reeval_interval_days: 30

      decayed:
        # Retention before hard delete
        retention_days: 30

        # Allow resurrection on access
        allow_resurrection: true

        # Resurrection threshold
        resurrection_boost: 0.5
```

**Complete Lifecycle Example**

```yaml
# config.yaml - Comprehensive lifecycle configuration
memory:
  lifecycle:
    # Core settings
    enabled: true

    # Decay parameters
    decay_rate: 0.01          # Medium decay
    access_boost: 0.2
    max_score: 1.0
    boost_cooldown_hours: 1

    # Stage transitions
    promotion_threshold: 0.7
    decay_threshold: 0.2

    # Promotion scoring
    promotion:
      min_age_hours: 24
      weights:
        age: 0.2
        access: 0.4
        confidence: 0.2
        connection: 0.2

    # Decay checks
    check_interval_hours: 24
    check_on_session_start: true
    check_on_session_end: false
    batch_size: 100

    # Cleanup
    cleanup:
      retention_days: 30
      auto_delete: true
      cleanup_interval_hours: 168
      max_deletions_per_run: 1000

    # Stage-specific
    stages:
      short_term:
        min_age_hours: 24
        max_capacity: 10000
        decay_rate: 0.01

      long_term:
        max_capacity: 50000
        decay_rate: 0.005
        reeval_interval_days: 30

      decayed:
        retention_days: 30
        allow_resurrection: true
        resurrection_boost: 0.5
```

**Environment Variable Overrides**

```bash
# Enable lifecycle
FRIDAY_MEMORY__LIFECYCLE__ENABLED="true"

# Decay settings
FRIDAY_MEMORY__LIFECYCLE__DECAY_RATE="0.01"
FRIDAY_MEMORY__LIFECYCLE__ACCESS_BOOST="0.2"

# Thresholds
FRIDAY_MEMORY__LIFECYCLE__PROMOTION_THRESHOLD="0.7"
FRIDAY_MEMORY__LIFECYCLE__DECAY_THRESHOLD="0.2"

# Promotion
FRIDAY_MEMORY__LIFECYCLE__PROMOTION__MIN_AGE_HOURS="24"

# Cleanup
FRIDAY_MEMORY__LIFECYCLE__CLEANUP__RETENTION_DAYS="30"
```

### 10.3.4 Collection Configuration

Friday's vector store supports multiple collections for organizing memories by lifecycle stage, topic, or session. Collection configuration controls how memories are distributed and retrieved.

**Default Single Collection**

By default, Friday uses a single collection for all memories:

```yaml
memory:
  vector:
    # Single collection mode (default)
    collection_name: "friday_memories"
    multi_collection: false
```

**Multi-Collection Mode**

Enable stage-based collections for lifecycle management:

```yaml
memory:
  vector:
    multi_collection: true

    # Collection naming
    collection_prefix: "friday"

    # Stage-based collections
    collections:
      short_term: "friday_short_term"
      long_term: "friday_long_term"
      decayed: "friday_decayed"
```

**Collection Strategies**

Different strategies for organizing memories:

**Strategy 1: Lifecycle Stages (Recommended)**

```yaml
memory:
  vector:
    strategy: "lifecycle"
    multi_collection: true
    collections:
      short_term: "friday_short_term"
      long_term: "friday_long_term"
      decayed: "friday_decayed"

    # Automatic migration on stage transitions
    auto_migrate: true
```

**Strategy 2: Session-Based**

```yaml
memory:
  vector:
    strategy: "session"
    collection_template: "friday_session_{session_id}"

    # Merge on session end
    merge_on_end: true
    merge_target: "friday_memories"
```

**Strategy 3: Topic-Based**

```yaml
memory:
  vector:
    strategy: "topic"

    # Topic detection settings
    topic_detection:
      enabled: true
      model: "gpt-4o-mini"
      max_topics: 10

    # Auto-create collections per topic
    auto_create_collections: true
    collection_template: "friday_topic_{topic}"
```

**Strategy 4: User-Based**

```yaml
memory:
  vector:
    strategy: "user"
    collection_template: "friday_user_{user_id}"

    # Isolation settings
    cross_user_search: false  # Prevent cross-user data leaks
```

**Collection Metadata**

Attach metadata to collections for tracking:

```yaml
memory:
  vector:
    collections:
      short_term:
        name: "friday_short_term"
        metadata:
          description: "Short-term memories under evaluation"
          max_age_days: 30
          auto_cleanup: true

      long_term:
        name: "friday_long_term"
        metadata:
          description: "Promoted long-term knowledge"
          max_age_days: 365
          auto_cleanup: false
```

**Retrieval Configuration**

Control how memories are retrieved from collections:

```yaml
memory:
  vector:
    retrieval:
      # Search across collections
      search_strategy: "priority"  # priority | parallel | cascade

      # Priority order (for "priority" strategy)
      search_order:
        - "short_term"
        - "long_term"
        # Omit "decayed" from search

      # Per-collection limits
      limits:
        short_term: 20
        long_term: 30

      # Minimum similarity threshold per collection
      min_similarity:
        short_term: 0.7
        long_term: 0.75
```

**Search Strategies Explained**

**Priority Search**

Search collections in order, stop when quota filled:

```yaml
retrieval:
  search_strategy: "priority"
  search_order:
    - "short_term"    # Search here first
    - "long_term"     # Then here if needed
  total_limit: 50     # Stop when 50 results found
```

**Parallel Search**

Search all collections simultaneously, merge results:

```yaml
retrieval:
  search_strategy: "parallel"
  limits:
    short_term: 25
    long_term: 25
  merge_strategy: "interleave"  # interleave | concat | best_score
```

**Cascade Search**

Search with fallback on insufficient results:

```yaml
retrieval:
  search_strategy: "cascade"
  search_order:
    - "short_term"
  fallback_order:
    - "long_term"
    - "decayed"       # Last resort
  min_results: 10     # Trigger fallback if < 10 results
```

**Migration Configuration**

Control how memories move between collections:

```yaml
memory:
  vector:
    migration:
      # Automatic migration on stage change
      auto_migrate: true

      # Migration strategy
      strategy: "copy_delete"  # copy_delete | move | duplicate

      # Batch settings
      batch_size: 100
      batch_delay_ms: 100      # Delay between batches

      # Verification
      verify_migration: true   # Verify after migration
      rollback_on_error: true
```

**Collection Size Limits**

Prevent collections from growing too large:

```yaml
memory:
  vector:
    limits:
      # Per-collection limits
      short_term:
        max_memories: 10000
        max_size_mb: 500
        eviction_policy: "lru"  # lru | fifo | lowest_score

      long_term:
        max_memories: 50000
        max_size_mb: 2000
        eviction_policy: "lowest_score"
```

**Complete Multi-Collection Example**

```yaml
# config.yaml - Multi-collection configuration
memory:
  vector:
    # Core settings
    multi_collection: true
    strategy: "lifecycle"
    collection_prefix: "friday"

    # Collection definitions
    collections:
      short_term:
        name: "friday_short_term"
        metadata:
          description: "Recent memories under evaluation"
          max_age_days: 30
        limits:
          max_memories: 10000
          max_size_mb: 500
          eviction_policy: "lru"

      long_term:
        name: "friday_long_term"
        metadata:
          description: "Promoted long-term knowledge"
          max_age_days: 365
        limits:
          max_memories: 50000
          max_size_mb: 2000
          eviction_policy: "lowest_score"

      decayed:
        name: "friday_decayed"
        metadata:
          description: "Decayed memories pending deletion"
          retention_days: 30
        limits:
          max_memories: 5000
          max_size_mb: 200

    # Retrieval settings
    retrieval:
      search_strategy: "priority"
      search_order:
        - "short_term"
        - "long_term"
      limits:
        short_term: 20
        long_term: 30
      min_similarity:
        short_term: 0.7
        long_term: 0.75

    # Migration settings
    migration:
      auto_migrate: true
      strategy: "copy_delete"
      batch_size: 100
      verify_migration: true
      rollback_on_error: true
```

**Environment Variable Overrides**

```bash
# Multi-collection mode
FRIDAY_MEMORY__VECTOR__MULTI_COLLECTION="true"
FRIDAY_MEMORY__VECTOR__STRATEGY="lifecycle"

# Collection names
FRIDAY_MEMORY__VECTOR__COLLECTIONS__SHORT_TERM__NAME="friday_short_term"
FRIDAY_MEMORY__VECTOR__COLLECTIONS__LONG_TERM__NAME="friday_long_term"

# Retrieval
FRIDAY_MEMORY__VECTOR__RETRIEVAL__SEARCH_STRATEGY="priority"

# Migration
FRIDAY_MEMORY__VECTOR__MIGRATION__AUTO_MIGRATE="true"
```

---

## 10.4 Tool Configuration

Friday's tool system provides 50+ built-in tools for filesystem operations, shell commands, web access, git operations, and more. Tool configuration controls which tools are available, how they're executed, and security boundaries.

### 10.4.1 Tool Registry Setup

The tool registry manages which tools are available to agents and how they're discovered.

**Default Registry**

Friday includes a default registry with all built-in tools:

```python
from friday_tools import DefaultToolRegistry

# Initialize with all built-in tools
registry = DefaultToolRegistry()

# Available categories:
# - filesystem (read_file, write_file, directory_list, etc.)
# - shell (shell_execute, shell_background)
# - web (web_fetch, web_search, web_scrape)
# - git (git_status, git_commit, git_diff, etc.)
# - data (json_parse, csv_parse, xml_parse)
# - text (text_search, text_replace, regex_match)
# - code (python_execute, code_analyze)
```

**Registry Configuration**

```yaml
tools:
  registry:
    # Registry type
    type: "default"           # default | custom | dynamic

    # Auto-load built-in tools
    load_builtins: true

    # Custom tool directories
    custom_tool_paths:
      - "./tools/custom"
      - "./tools/project_specific"

    # Discovery settings
    auto_discover: true       # Auto-discover tools in custom paths
    discovery_pattern: "**/*_tool.py"
```

**Loading Specific Tool Categories**

Control which tool categories are loaded:

```yaml
tools:
  registry:
    # Load only specific categories
    categories:
      - "filesystem"
      - "shell"
      - "git"

    # Exclude specific categories
    exclude_categories:
      - "web"               # Disable web access
      - "code"              # Disable code execution
```

**Individual Tool Selection**

Enable or disable specific tools:

```yaml
tools:
  registry:
    # Allowlist approach (only these tools available)
    mode: "allowlist"
    allowed_tools:
      - "read_file"
      - "write_file"
      - "directory_list"
      - "git_status"
      - "git_commit"

    # Blocklist approach (all tools except these)
    # mode: "blocklist"
    # blocked_tools:
    #   - "shell_execute"
    #   - "web_fetch"
```

**Custom Tool Registration**

Register project-specific tools:

```python
from friday_tools import BaseTool, ToolRegistry

class CustomAnalyzerTool(BaseTool):
    name = "custom_analyzer"
    description = "Analyzes project-specific data"

    parameters_schema = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
        },
        "required": ["file_path"],
    }

    async def execute(self, file_path: str) -> dict:
        # Implementation
        return {"status": "success"}

# Register custom tool
registry = ToolRegistry()
registry.register(CustomAnalyzerTool())
```

**Configuration-Based Tool Registration**

```yaml
tools:
  registry:
    custom_tools:
      - name: "custom_analyzer"
        module: "project.tools.analyzer"
        class: "CustomAnalyzerTool"
        enabled: true

      - name: "project_builder"
        module: "project.tools.builder"
        class: "BuilderTool"
        enabled: false        # Disabled
```

**Tool Manifest Generation**

Control how tools are presented to the LLM:

```yaml
tools:
  manifest:
    # Include in tool descriptions
    include_examples: true
    include_categories: true
    include_cost_estimates: false

    # Description length
    description_max_length: 200

    # Parameter detail level
    parameter_detail: "full"  # full | minimal | none
```

**Dynamic Tool Loading**

Load tools on-demand based on task:

```yaml
tools:
  registry:
    # Dynamic loading
    dynamic_loading: true

    # Load tools based on user query
    query_based_loading: true

    # Maximum tools to load per task
    max_tools_per_task: 20

    # Cache loaded tools
    cache_loaded_tools: true
    cache_ttl_seconds: 3600
```

**Tool Versioning**

Manage multiple versions of tools:

```yaml
tools:
  registry:
    versioning:
      enabled: true

      # Default version selection
      default_strategy: "latest"  # latest | stable | pinned

      # Version constraints
      constraints:
        read_file: ">=2.0.0"
        shell_execute: "1.5.0"    # Pin specific version
```

**Complete Registry Example**

```yaml
# config.yaml - Tool registry configuration
tools:
  registry:
    # Core settings
    type: "default"
    load_builtins: true

    # Tool selection
    mode: "allowlist"
    categories:
      - "filesystem"
      - "git"
      - "text"
      - "data"

    allowed_tools:
      - "read_file"
      - "write_file"
      - "directory_list"
      - "file_search"
      - "git_status"
      - "git_commit"
      - "git_diff"
      - "git_log"
      - "text_search"
      - "text_replace"
      - "json_parse"
      - "yaml_parse"

    # Custom tools
    custom_tool_paths:
      - "./tools/custom"
    auto_discover: true
    discovery_pattern: "**/*_tool.py"

    # Manifest
    manifest:
      include_examples: true
      include_categories: true
      description_max_length: 200
      parameter_detail: "full"

    # Dynamic loading
    dynamic_loading: false
    max_tools_per_task: 20
```

**Environment Variable Overrides**

```bash
# Registry mode
FRIDAY_TOOLS__REGISTRY__MODE="allowlist"

# Load built-ins
FRIDAY_TOOLS__REGISTRY__LOAD_BUILTINS="true"

# Categories (comma-separated)
FRIDAY_TOOLS__REGISTRY__CATEGORIES="filesystem,git,text"

# Custom paths (comma-separated)
FRIDAY_TOOLS__REGISTRY__CUSTOM_TOOL_PATHS="./tools/custom,./tools/project"
```

### 10.4.2 Security & Sandboxing

Friday executes code and shell commands in isolated environments to prevent system damage and security vulnerabilities.

**Sandbox Types**

Friday supports three sandbox types:

1. **Docker** - Isolated containers (recommended for production)
2. **Subprocess** - OS-level process isolation
3. **Mock** - No execution, returns fake results (testing only)

**Docker Sandbox Configuration**

```yaml
sandbox:
  # Sandbox type selection
  sandbox_type: "docker"

  # Fallback to subprocess if Docker unavailable
  fallback_to_subprocess: true

  docker:
    # Container image
    image: "friday-sandbox-python:latest"
    pull_policy: "if-not-present"  # always | if-not-present | never

    # Resource limits
    memory_limit: "512m"
    cpu_limit: 1.0              # CPU cores

    # Execution limits
    default_timeout_seconds: 30
    max_timeout_seconds: 300

    # Security
    network_enabled: false      # Disable network access
    read_only_rootfs: true      # Read-only root filesystem
    user: "sandbox:sandbox"     # Non-root user

    # Workspace
    workspace_base_path: "/tmp/friday-workspaces"
```

**Building the Sandbox Image**

Friday provides a Dockerfile for the sandbox environment:

```dockerfile
# Friday Sandbox Image
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r sandbox && useradd -r -g sandbox sandbox

# Install common dependencies
RUN pip install --no-cache-dir numpy pandas requests

# Set up workspace
RUN mkdir -p /workspace && chown sandbox:sandbox /workspace
WORKDIR /workspace

# Switch to non-root user
USER sandbox

# No CMD - container receives code at runtime
```

Build and tag:

```bash
docker build -t friday-sandbox-python:latest -f Dockerfile.sandbox .
```

**Subprocess Sandbox Configuration**

```yaml
sandbox:
  sandbox_type: "subprocess"

  subprocess:
    # Execution limits
    timeout_seconds: 30

    # Resource limits (if supported by OS)
    max_memory_mb: 512
    max_cpu_percent: 50

    # Working directory
    workspace_path: "/tmp/friday-workspaces"

    # Environment isolation
    inherit_env: false          # Don't inherit parent environment
    allowed_env_vars:
      - "PATH"
      - "HOME"
      - "LANG"
```

**Workspace Configuration**

Workspaces provide isolated filesystem areas for tool execution:

```yaml
sandbox:
  workspace:
    # Time-to-live
    ttl_seconds: 3600           # 1 hour
    ttl_soft_limit_seconds: 3600
    ttl_hard_limit_seconds: 86400  # 24 hours max

    # Cleanup
    cleanup_interval_seconds: 300  # 5 minutes
    preserve_on_error: true        # Keep workspace if execution fails

    # Size limits
    max_workspace_size_mb: 100
    max_files_per_workspace: 1000
```

**Security Policies**

Define security boundaries for tool execution:

```yaml
tools:
  security:
    # File system access
    filesystem:
      # Allowed directories (allowlist)
      allowed_paths:
        - "/workspace"
        - "/tmp/friday"

      # Blocked directories (blocklist)
      blocked_paths:
        - "/etc"
        - "/usr"
        - "/var"
        - "/root"
        - "$HOME/.ssh"

      # File operation limits
      max_file_size_mb: 10
      max_files_per_operation: 100

    # Shell command restrictions
    shell:
      # Allowed commands (allowlist)
      allowed_commands:
        - "ls"
        - "cat"
        - "grep"
        - "find"

      # Blocked commands (blocklist)
      blocked_commands:
        - "rm -rf /"
        - "dd"
        - "mkfs"
        - ":(){ :|:& };:"     # Fork bomb

      # Blocked patterns
      blocked_patterns:
        - ".*sudo.*"
        - ".*curl.*\\|.*bash.*"  # Piped execution

    # Network restrictions
    network:
      enabled: false            # Disable all network access
      # Or allow specific domains:
      # allowed_domains:
      #   - "api.openai.com"
      #   - "api.anthropic.com"

      # Blocked domains
      blocked_domains:
        - "internal.company.com"
        - "localhost"
        - "127.0.0.1"
```

**Execution Policies**

Control how tools execute:

```yaml
tools:
  execution:
    # Concurrent execution
    max_concurrent_tools: 5

    # Retry policy
    retry_on_failure: true
    max_retries: 2
    retry_delay_seconds: 1

    # Timeout
    default_timeout_seconds: 30
    max_timeout_seconds: 300

    # Resource limits
    max_memory_mb: 512
    max_cpu_percent: 80
```

**Audit Logging**

Log all tool executions for security auditing:

```yaml
tools:
  audit:
    # Enable audit logging
    enabled: true

    # Log destination
    log_path: "./logs/tool_audit.log"
    log_format: "json"          # json | text

    # What to log
    log_inputs: true            # Log tool inputs
    log_outputs: true           # Log tool outputs
    log_errors: true            # Log errors

    # Redact sensitive data
    redact_patterns:
      - "password"
      - "api_key"
      - "secret"
      - "token"
```

**Complete Security Example**

```yaml
# config.yaml - Comprehensive security configuration
sandbox:
  # Sandbox selection
  sandbox_type: "docker"
  fallback_to_subprocess: true

  # Docker settings
  docker:
    image: "friday-sandbox-python:latest"
    memory_limit: "512m"
    cpu_limit: 1.0
    default_timeout_seconds: 30
    max_timeout_seconds: 300
    network_enabled: false
    read_only_rootfs: true
    user: "sandbox:sandbox"

  # Workspace
  workspace:
    ttl_seconds: 3600
    cleanup_interval_seconds: 300
    preserve_on_error: true
    max_workspace_size_mb: 100
    max_files_per_workspace: 1000

tools:
  # Security policies
  security:
    filesystem:
      allowed_paths:
        - "/workspace"
      blocked_paths:
        - "/etc"
        - "/root"
      max_file_size_mb: 10

    shell:
      blocked_commands:
        - "rm -rf /"
        - "dd"
      blocked_patterns:
        - ".*sudo.*"

    network:
      enabled: false

  # Execution
  execution:
    max_concurrent_tools: 5
    default_timeout_seconds: 30
    max_retries: 2

  # Audit
  audit:
    enabled: true
    log_path: "./logs/tool_audit.log"
    log_format: "json"
    log_inputs: true
    log_outputs: true
    redact_patterns:
      - "password"
      - "api_key"
```

**Environment Variable Overrides**

```bash
# Sandbox type
FRIDAY_SANDBOX_TYPE="docker"
FRIDAY_SANDBOX_FALLBACK_SUBPROCESS="true"

# Docker settings
FRIDAY_SANDBOX_IMAGE="friday-sandbox-python:latest"
FRIDAY_SANDBOX_MEMORY_LIMIT="512m"
FRIDAY_SANDBOX_NETWORK_ENABLED="false"

# Workspace
FRIDAY_SANDBOX_WORKSPACE_TTL="3600"
FRIDAY_SANDBOX_PRESERVE_ON_ERROR="true"
```

### 10.4.3 Tool Allowlists and Blocklists

Control precisely which tools are available and how they can be used.

**Allowlist Mode (Recommended)**

In allowlist mode, only explicitly allowed tools are available:

```yaml
tools:
  registry:
    mode: "allowlist"

    # Only these tools are available
    allowed_tools:
      # Filesystem (read-only)
      - "read_file"
      - "directory_list"
      - "file_search"
      - "file_stat"

      # Git (read-only)
      - "git_status"
      - "git_log"
      - "git_diff"

      # Data parsing
      - "json_parse"
      - "yaml_parse"
      - "csv_parse"

      # Text processing
      - "text_search"
      - "regex_match"
```

**Blocklist Mode**

In blocklist mode, all tools are available except blocked ones:

```yaml
tools:
  registry:
    mode: "blocklist"

    # Block dangerous tools
    blocked_tools:
      # File system writes
      - "write_file"
      - "delete_file"
      - "file_move"

      # Shell execution
      - "shell_execute"
      - "shell_background"

      # Network access
      - "web_fetch"
      - "web_scrape"

      # Code execution
      - "python_execute"
      - "code_execute"
```

**Category-Based Filtering**

Filter tools by category:

```yaml
tools:
  registry:
    # Allow only specific categories
    allowed_categories:
      - "filesystem"
      - "git"
      - "data"

    # Within filesystem, block write operations
    category_exceptions:
      filesystem:
        blocked_tools:
          - "write_file"
          - "delete_file"
```

**Permission Levels**

Define permission levels for different contexts:

```yaml
tools:
  permissions:
    # Development environment
    development:
      mode: "allowlist"
      allowed_categories:
        - "filesystem"
        - "git"
        - "shell"
        - "code"
        - "web"

    # Production environment
    production:
      mode: "allowlist"
      allowed_tools:
        - "read_file"
        - "directory_list"
        - "git_status"
        - "git_log"
      blocked_categories:
        - "shell"
        - "code"

    # Testing environment
    testing:
      mode: "blocklist"
      blocked_tools:
        - "shell_execute"
        - "web_fetch"
```

**User-Based Permissions**

Different permissions for different users:

```yaml
tools:
  user_permissions:
    # Admin users (full access)
    admin:
      mode: "allowlist"
      allowed_categories: "*"

    # Developer users (most tools)
    developer:
      mode: "allowlist"
      allowed_categories:
        - "filesystem"
        - "git"
        - "shell"
        - "code"
      blocked_tools:
        - "delete_file"
        - "shell_execute"  # No arbitrary shell

    # Read-only users
    readonly:
      mode: "allowlist"
      allowed_tools:
        - "read_file"
        - "directory_list"
        - "git_status"
        - "git_log"
```

**Context-Based Restrictions**

Apply restrictions based on execution context:

```yaml
tools:
  context_restrictions:
    # Restrict based on file path
    filesystem:
      "/etc/**":
        allowed_tools: []       # No tools can access /etc

      "/workspace/**":
        allowed_tools: "*"      # Full access to workspace

      "$HOME/.ssh/**":
        allowed_tools: []       # Block SSH directory

    # Restrict based on git repo
    git:
      "production-repo":
        blocked_tools:
          - "git_commit"
          - "git_push"
        allowed_tools:
          - "git_status"
          - "git_log"
```

**Parameter Restrictions**

Restrict tool parameters:

```yaml
tools:
  parameter_restrictions:
    shell_execute:
      # Block dangerous command patterns
      command:
        blocked_patterns:
          - ".*rm -rf.*"
          - ".*sudo.*"
          - ".*curl.*\\|.*bash.*"

    web_fetch:
      # Restrict allowed URLs
      url:
        allowed_domains:
          - "api.openai.com"
          - "api.anthropic.com"
        blocked_domains:
          - "localhost"
          - "*.internal.company.com"

    write_file:
      # Restrict file paths
      file_path:
        allowed_patterns:
          - "/workspace/**"
          - "/tmp/friday/**"
        blocked_patterns:
          - "/etc/**"
          - "/root/**"

      # Restrict file size
      content:
        max_length: 10485760    # 10MB
```

**Dynamic Allowlists**

Change allowlists based on context:

```python
from friday_agent import CopilotAgent

agent = CopilotAgent(profile=profile)

# Start with minimal tools
agent.set_allowed_tools([
    "read_file",
    "directory_list",
])

# Expand after user confirms
if user_confirms_code_execution:
    agent.expand_allowed_tools([
        "python_execute",
        "shell_execute",
    ])

# Revoke after task complete
agent.revoke_tools([
    "python_execute",
    "shell_execute",
])
```

**Complete Allowlist Example**

```yaml
# config.yaml - Comprehensive allowlist configuration
tools:
  registry:
    # Allowlist mode
    mode: "allowlist"

    # Allowed tools by category
    allowed_categories:
      - "filesystem"
      - "git"
      - "data"
      - "text"

    # Specific allowed tools
    allowed_tools:
      # Filesystem (read-only)
      - "read_file"
      - "directory_list"
      - "file_search"
      - "file_stat"

      # Git (read-only)
      - "git_status"
      - "git_log"
      - "git_diff"
      - "git_show"

      # Data parsing
      - "json_parse"
      - "yaml_parse"
      - "csv_parse"
      - "xml_parse"

      # Text processing
      - "text_search"
      - "text_replace"
      - "regex_match"
      - "regex_replace"

  # Parameter restrictions
  parameter_restrictions:
    read_file:
      file_path:
        allowed_patterns:
          - "/workspace/**"
          - "/project/**"
        blocked_patterns:
          - "**/.env"
          - "**/*.key"
          - "**/.ssh/**"

    file_search:
      path:
        allowed_patterns:
          - "/workspace/**"
        blocked_patterns:
          - "/etc/**"

  # Context restrictions
  context_restrictions:
    filesystem:
      "/etc/**":
        allowed_tools: []
      "/workspace/**":
        allowed_tools: "*"

  # User permissions
  user_permissions:
    default:
      mode: "allowlist"
      allowed_tools:
        - "read_file"
        - "directory_list"
        - "git_status"
```

---

## 10.5 Extraction Configuration

Memory extraction transforms conversation history into structured knowledge (entities, relationships, insights). Extraction configuration controls the LLM used, prompts, and extraction rules.

### 10.5.1 Extraction LLM Selection

Friday uses a dedicated LLM for extraction, which can be different from the main conversational model.

**Why Use a Separate Extraction LLM?**

- **Cost optimization**: Use cheaper models for extraction
- **Speed**: Use faster models to reduce extraction latency
- **Specialization**: Use models optimized for structured extraction

**Basic Extraction LLM Configuration**

```yaml
extraction:
  llm:
    # Model selection
    model: "gpt-4o-mini"      # Cheaper than main model
    temperature: 0.0          # Deterministic extraction
    max_tokens: 4096

    # Fallback model
    fallback_model: "gpt-3.5-turbo"
```

**Model Recommendations by Use Case**

**High Accuracy (Recommended)**

```yaml
extraction:
  llm:
    model: "gpt-4o"
    temperature: 0.0
    max_tokens: 4096
```

Best for: Production systems, high-value knowledge extraction

**Balanced (Cost vs Quality)**

```yaml
extraction:
  llm:
    model: "gpt-4o-mini"
    temperature: 0.0
    max_tokens: 4096
```

Best for: Most use cases, good balance of cost and quality

**Fast & Affordable**

```yaml
extraction:
  llm:
    model: "gpt-3.5-turbo"
    temperature: 0.0
    max_tokens: 2048
```

Best for: Development, testing, low-value extractions

**Local Models**

```yaml
extraction:
  llm:
    model: "ollama/llama3.1:8b"
    api_base: "http://localhost:11434"
    temperature: 0.0
    max_tokens: 4096
```

Best for: Privacy-sensitive, offline operation, cost-free

**OpenRouter for Experimentation**

```yaml
extraction:
  llm:
    model: "openrouter/google/gemini-2.0-flash-exp:free"
    temperature: 0.0
    max_tokens: 4096
```

Best for: Experimentation, free tier usage

**Multi-Model Extraction**

Use different models for different extraction types:

```yaml
extraction:
  llm:
    # Entity extraction (needs high accuracy)
    entity_model: "gpt-4o"

    # Relationship extraction (moderate accuracy)
    relationship_model: "gpt-4o-mini"

    # Insight extraction (needs reasoning)
    insight_model: "gpt-4o"

    # Summarization (speed prioritized)
    summary_model: "gpt-3.5-turbo"
```

**Extraction Retry Configuration**

```yaml
extraction:
  llm:
    # Retry on failure
    max_retries: 3
    backoff_multiplier: 2.0

    # Timeout
    timeout_seconds: 60.0

    # Validation retry
    retry_on_invalid_json: true
    max_validation_retries: 2
```

**Extraction Batching**

Process multiple extraction requests efficiently:

```yaml
extraction:
  batching:
    # Batch size
    batch_size: 5             # Extract 5 turns at once

    # Batch delay
    batch_delay_ms: 100       # Wait 100ms before batching

    # Maximum wait time
    max_batch_wait_ms: 1000   # Process after 1s even if batch not full
```

**Complete Extraction LLM Example**

```yaml
# config.yaml - Extraction LLM configuration
extraction:
  llm:
    # Primary model
    model: "gpt-4o-mini"
    temperature: 0.0
    max_tokens: 4096

    # Fallback
    fallback_model: "gpt-3.5-turbo"

    # Retry
    max_retries: 3
    backoff_multiplier: 2.0
    timeout_seconds: 60.0
    retry_on_invalid_json: true

    # Multi-model (optional)
    entity_model: "gpt-4o"
    relationship_model: "gpt-4o-mini"
    insight_model: "gpt-4o"
    summary_model: "gpt-3.5-turbo"

  # Batching
  batching:
    enabled: true
    batch_size: 5
    batch_delay_ms: 100
    max_batch_wait_ms: 1000
```

**Environment Variable Overrides**

```bash
# Extraction model
FRIDAY_EXTRACTION__LLM__MODEL="gpt-4o-mini"
FRIDAY_EXTRACTION__LLM__TEMPERATURE="0.0"

# Retry
FRIDAY_EXTRACTION__LLM__MAX_RETRIES="3"

# Batching
FRIDAY_EXTRACTION__BATCHING__ENABLED="true"
FRIDAY_EXTRACTION__BATCHING__BATCH_SIZE="5"
```

### 10.5.2 Extraction Prompts & Rules

Extraction prompts guide the LLM in identifying entities, relationships, and insights. Friday provides default prompts that can be customized.

**Default Extraction Prompt Structure**

```
You are a knowledge extraction system. Analyze the conversation and extract:

1. **Entities**: People, places, concepts, technologies
2. **Relationships**: Connections between entities
3. **Insights**: Key learnings and preferences

Output valid JSON only.
```

**Customizing Entity Extraction Prompts**

```yaml
extraction:
  prompts:
    entity:
      system_prompt: |
        You are an entity extraction system specialized in software development.

        Extract entities from the conversation. Focus on:
        - People (developers, users, stakeholders)
        - Technologies (languages, frameworks, tools)
        - Projects (repositories, applications, features)
        - Concepts (design patterns, algorithms, methodologies)

        For each entity, provide:
        - name: The entity name
        - entity_type: The type (person, technology, project, concept)
        - confidence: Your confidence (0.0-1.0)
        - properties: Additional attributes

        Output as JSON array.

      user_template: |
        Extract entities from this conversation:

        {conversation}

        Remember to:
        - Extract only factual entities mentioned
        - Use canonical names (e.g., "Python" not "python programming")
        - Include confidence scores

        Output JSON only.
```

**Relationship Extraction Prompts**

```yaml
extraction:
  prompts:
    relationship:
      system_prompt: |
        You are a relationship extraction system.

        Identify relationships between entities. Common relationship types:
        - KNOWS (person-person connections)
        - USES (person-technology usage)
        - WORKS_ON (person-project involvement)
        - PREFERS (person-technology preferences)
        - DEPENDS_ON (project-technology dependencies)
        - CONTAINS (project-component containment)

        For each relationship:
        - source: Source entity name
        - verb: Relationship type
        - target: Target entity name
        - strength: Relationship strength (0.0-1.0)
        - confidence: Extraction confidence (0.0-1.0)
        - evidence: Supporting text from conversation

      user_template: |
        Given these entities:
        {entities}

        Extract relationships from this conversation:
        {conversation}

        Output JSON array of relationships.
```

**Insight Extraction Prompts**

```yaml
extraction:
  prompts:
    insight:
      system_prompt: |
        You are an insight extraction system.

        Extract key learnings, preferences, and domain knowledge.

        Types of insights:
        - User preferences (e.g., "Chuck prefers Python over JavaScript")
        - Technical decisions (e.g., "Team chose React for frontend")
        - Domain knowledge (e.g., "API rate limit is 1000 requests/hour")
        - Workflows (e.g., "Deploy process requires code review")

        For each insight:
        - insight_text: The core insight (concise statement)
        - category: Type (preference, decision, knowledge, workflow)
        - confidence: Extraction confidence (0.0-1.0)
        - related_entities: List of relevant entity names

      user_template: |
        Extract insights from this conversation:
        {conversation}

        Focus on:
        - Expressed preferences
        - Technical decisions
        - Domain-specific knowledge
        - Established workflows

        Output JSON array.
```

**Extraction Rules**

Define rules that guide extraction behavior:

```yaml
extraction:
  rules:
    # Entity rules
    entities:
      # Minimum confidence for extraction
      min_confidence: 0.7

      # Deduplica strategies
      deduplication:
        enabled: true
        fuzzy_matching: true
        similarity_threshold: 0.85

      # Normalization
      normalization:
        lowercase_names: false
        strip_articles: true    # Remove "the", "a", "an"
        canonical_forms:
          "JS": "JavaScript"
          "TS": "TypeScript"
          "GH": "GitHub"

      # Filtering
      filters:
        # Minimum name length
        min_name_length: 2

        # Blocked patterns
        blocked_patterns:
          - "^\\d+$"            # Pure numbers
          - "^[a-z]$"           # Single letters

        # Blocked entity types
        blocked_types:
          - "stopword"

    # Relationship rules
    relationships:
      # Minimum confidence
      min_confidence: 0.6

      # Minimum strength
      min_strength: 0.3

      # Require evidence
      require_evidence: true
      min_evidence_length: 10

      # Bidirectional relationships
      create_bidirectional: false

      # Relationship validation
      validate_entity_exists: true

    # Insight rules
    insights:
      # Minimum confidence
      min_confidence: 0.7

      # Minimum insight length
      min_length: 20
      max_length: 500

      # Categorization
      require_category: true
      allowed_categories:
        - "preference"
        - "decision"
        - "knowledge"
        - "workflow"
        - "constraint"

      # Deduplication
      deduplication:
        enabled: true
        similarity_threshold: 0.9
```

**Output Format Configuration**

Control the extraction output format:

```yaml
extraction:
  output:
    # Format type
    format: "json"              # json | yaml | structured

    # JSON formatting
    json:
      pretty_print: true
      indent: 2
      sort_keys: false

    # Validation
    validate_schema: true
    strict_parsing: true

    # Error handling
    on_invalid_output: "retry"  # retry | skip | log_warning
    max_retry_attempts: 2
```

**Complete Extraction Prompts & Rules Example**

```yaml
# config.yaml - Comprehensive extraction configuration
extraction:
  prompts:
    entity:
      system_prompt: |
        Extract entities from conversations. Focus on people, technologies, projects.
        Output: JSON array with name, entity_type, confidence, properties.
      user_template: |
        Extract entities from: {conversation}
        Entities: {entities}
        Output JSON only.

    relationship:
      system_prompt: |
        Extract relationships. Types: KNOWS, USES, WORKS_ON, PREFERS, DEPENDS_ON.
        Output: JSON array with source, verb, target, strength, confidence.
      user_template: |
        Entities: {entities}
        Conversation: {conversation}
        Output relationships as JSON.

    insight:
      system_prompt: |
        Extract insights: preferences, decisions, knowledge, workflows.
        Output: JSON array with insight_text, category, confidence, related_entities.
      user_template: |
        Extract insights from: {conversation}
        Output JSON only.

  rules:
    entities:
      min_confidence: 0.7
      deduplication:
        enabled: true
        similarity_threshold: 0.85
      normalization:
        canonical_forms:
          "JS": "JavaScript"
          "TS": "TypeScript"
      filters:
        min_name_length: 2

    relationships:
      min_confidence: 0.6
      min_strength: 0.3
      require_evidence: true
      validate_entity_exists: true

    insights:
      min_confidence: 0.7
      min_length: 20
      require_category: true
      allowed_categories:
        - "preference"
        - "decision"
        - "knowledge"
        - "workflow"

  output:
    format: "json"
    validate_schema: true
    on_invalid_output: "retry"
    max_retry_attempts: 2
```

### 10.5.3 Entity Types and Relationship Verbs

Configure which entity types and relationship verbs Friday recognizes and extracts.

**Entity Type Configuration**

Define a taxonomy of entity types:

```yaml
extraction:
  entity_types:
    # Core types (always available)
    core:
      - name: "person"
        description: "Individuals (users, developers, stakeholders)"
        examples: ["Chuck", "Alice", "Bob"]

      - name: "technology"
        description: "Tools, languages, frameworks"
        examples: ["Python", "React", "Docker"]

      - name: "project"
        description: "Software projects, repositories"
        examples: ["Friday Framework", "API Gateway"]

      - name: "concept"
        description: "Abstract ideas, patterns, methodologies"
        examples: ["Microservices", "DDD", "SOLID"]

    # Domain-specific types
    custom:
      - name: "api_endpoint"
        description: "REST API endpoints"
        examples: ["/api/users", "/api/orders"]

      - name: "database"
        description: "Database systems and tables"
        examples: ["PostgreSQL", "users_table"]

      - name: "deployment"
        description: "Deployment environments"
        examples: ["production", "staging"]
```

**Entity Type Hierarchy**

Define parent-child relationships between entity types:

```yaml
extraction:
  entity_types:
    hierarchy:
      technology:
        children:
          - language
          - framework
          - library
          - tool

      person:
        children:
          - developer
          - designer
          - manager

      project:
        children:
          - repository
          - application
          - service
```

**Entity Type Properties**

Define expected properties for each entity type:

```yaml
extraction:
  entity_types:
    properties:
      person:
        required:
          - name
        optional:
          - role
          - email
          - github_username

      technology:
        required:
          - name
          - type          # language | framework | tool
        optional:
          - version
          - documentation_url

      project:
        required:
          - name
        optional:
          - repository_url
          - status        # active | archived
          - owner
```

**Relationship Verb Configuration**

Define allowed relationship verbs:

```yaml
extraction:
  relationship_verbs:
    # Personal relationships
    personal:
      - verb: "KNOWS"
        description: "Person knows another person"
        source_types: ["person"]
        target_types: ["person"]
        bidirectional: true

      - verb: "REPORTS_TO"
        description: "Person reports to another person"
        source_types: ["person"]
        target_types: ["person"]
        bidirectional: false

    # Technical relationships
    technical:
      - verb: "USES"
        description: "Person or project uses technology"
        source_types: ["person", "project"]
        target_types: ["technology"]
        bidirectional: false

      - verb: "WORKS_ON"
        description: "Person works on project"
        source_types: ["person"]
        target_types: ["project"]
        bidirectional: false

      - verb: "DEPENDS_ON"
        description: "Project depends on technology"
        source_types: ["project"]
        target_types: ["technology", "project"]
        bidirectional: false

    # Preference relationships
    preference:
      - verb: "PREFERS"
        description: "Person prefers one option over another"
        source_types: ["person"]
        target_types: ["technology", "concept"]
        bidirectional: false

      - verb: "DISLIKES"
        description: "Person dislikes something"
        source_types: ["person"]
        target_types: ["technology", "concept"]
        bidirectional: false

    # Structural relationships
    structural:
      - verb: "CONTAINS"
        description: "Project contains component"
        source_types: ["project"]
        target_types: ["project", "technology"]
        bidirectional: false

      - verb: "PART_OF"
        description: "Component is part of project"
        source_types: ["project", "technology"]
        target_types: ["project"]
        bidirectional: false
```

**Relationship Constraints**

Define constraints on relationship creation:

```yaml
extraction:
  relationships:
    constraints:
      # Type compatibility
      enforce_type_compatibility: true

      # Self-loops
      allow_self_loops: false

      # Duplicate relationships
      allow_duplicate_relationships: false

      # Bidirectional creation
      auto_create_inverse:
        enabled: true
        inverse_mappings:
          "CONTAINS": "PART_OF"
          "DEPENDS_ON": "REQUIRED_BY"
          "USES": "USED_BY"

      # Relationship limits
      max_relationships_per_entity: 100
      max_same_verb_per_pair: 1
```

**Custom Extraction Schemas**

Define custom extraction schemas for specialized domains:

```yaml
extraction:
  custom_schemas:
    # Software architecture domain
    software_architecture:
      entity_types:
        - "service"
        - "component"
        - "interface"
        - "data_model"

      relationship_verbs:
        - "CALLS"
        - "IMPLEMENTS"
        - "EXTENDS"
        - "DEPENDS_ON"

      insight_categories:
        - "architectural_decision"
        - "design_pattern"
        - "scalability_concern"

    # DevOps domain
    devops:
      entity_types:
        - "pipeline"
        - "environment"
        - "deployment"
        - "monitoring_tool"

      relationship_verbs:
        - "DEPLOYS_TO"
        - "MONITORS"
        - "TRIGGERS"

      insight_categories:
        - "deployment_process"
        - "infrastructure_requirement"
```

**Entity Type Validation**

Validate extracted entities against type definitions:

```yaml
extraction:
  validation:
    # Validate entity types
    validate_entity_types: true
    strict_type_checking: true

    # Unknown type handling
    on_unknown_type: "reject"  # reject | accept_as_generic | log_warning

    # Property validation
    validate_required_properties: true
    validate_property_types: true

    # Relationship verb validation
    validate_relationship_verbs: true
    validate_source_target_types: true
```

**Complete Entity Types & Relationship Verbs Example**

```yaml
# config.yaml - Entity types and relationship verbs
extraction:
  entity_types:
    core:
      - name: "person"
        description: "People"
        properties:
          required: ["name"]
          optional: ["role", "email"]

      - name: "technology"
        description: "Technologies"
        properties:
          required: ["name", "type"]
          optional: ["version"]

      - name: "project"
        description: "Projects"
        properties:
          required: ["name"]
          optional: ["repository_url", "status"]

    custom:
      - name: "api_endpoint"
        description: "API endpoints"

      - name: "database"
        description: "Databases"

  relationship_verbs:
    technical:
      - verb: "USES"
        source_types: ["person", "project"]
        target_types: ["technology"]
        bidirectional: false

      - verb: "WORKS_ON"
        source_types: ["person"]
        target_types: ["project"]
        bidirectional: false

      - verb: "DEPENDS_ON"
        source_types: ["project"]
        target_types: ["technology", "project"]
        bidirectional: false

    preference:
      - verb: "PREFERS"
        source_types: ["person"]
        target_types: ["technology"]
        bidirectional: false

    structural:
      - verb: "CONTAINS"
        source_types: ["project"]
        target_types: ["project", "technology"]
        bidirectional: false

  relationships:
    constraints:
      enforce_type_compatibility: true
      allow_self_loops: false
      allow_duplicate_relationships: false
      max_relationships_per_entity: 100

  validation:
    validate_entity_types: true
    validate_relationship_verbs: true
    on_unknown_type: "accept_as_generic"
```

---

## 10.6 Transcript Configuration

Transcripts provide a complete, auditable record of agent conversations. Transcript configuration controls storage, export formats, and compression.

### 10.6.1 Storage Settings

Configure where and how transcripts are stored.

**Storage Backend Selection**

Friday supports multiple transcript storage backends:

```yaml
transcript:
  storage:
    # Backend type
    backend: "sqlite"         # sqlite | jsonl | postgresql | memory

    # SQLite configuration
    sqlite:
      db_path: "./data/transcripts.db"
      wal_mode: true          # Write-Ahead Logging for performance
      synchronous: "NORMAL"   # FULL | NORMAL | OFF

    # JSONL configuration (alternative)
    # jsonl:
    #   directory: "./data/transcripts"
    #   file_pattern: "{session_id}.jsonl"
```

**SQLite Storage Configuration**

SQLite is the recommended backend for most use cases:

```yaml
transcript:
  storage:
    backend: "sqlite"
    sqlite:
      # Database file
      db_path: "./data/transcripts.db"

      # Performance settings
      wal_mode: true           # Enable Write-Ahead Logging
      synchronous: "NORMAL"    # FULL | NORMAL | OFF
      cache_size: 10000        # Page cache size

      # Connection pool
      max_connections: 5
      connection_timeout: 30

      # Pragmas
      pragmas:
        foreign_keys: true
        journal_mode: "WAL"
        synchronous: "NORMAL"
```

**JSONL Storage Configuration**

JSONL provides simple file-based storage:

```yaml
transcript:
  storage:
    backend: "jsonl"
    jsonl:
      # Directory for transcript files
      directory: "./data/transcripts"

      # File naming pattern
      file_pattern: "{session_id}.jsonl"

      # Compression
      compression: "gzip"      # none | gzip | bzip2

      # File rotation
      max_file_size_mb: 100
      rotate_on_size: true
```

**PostgreSQL Storage Configuration**

For production deployments with high volume:

```yaml
transcript:
  storage:
    backend: "postgresql"
    postgresql:
      # Connection
      host: "localhost"
      port: 5432
      database: "friday_transcripts"
      user: "friday"
      password: "${POSTGRES_PASSWORD}"

      # Connection pool
      min_pool_size: 2
      max_pool_size: 10

      # Table names
      sessions_table: "transcript_sessions"
      entries_table: "transcript_entries"
```

**Memory Storage (Testing Only)**

```yaml
transcript:
  storage:
    backend: "memory"
    memory:
      max_sessions: 100
      max_entries_per_session: 1000
```

**Storage Retention Policies**

Control how long transcripts are retained:

```yaml
transcript:
  retention:
    # Automatic cleanup
    auto_cleanup: true
    cleanup_interval_hours: 24

    # Retention periods
    active_sessions_days: 90     # Active sessions
    archived_sessions_days: 365  # Archived sessions
    error_sessions_days: 30      # Sessions with errors

    # Deletion strategy
    deletion_strategy: "soft"    # soft | hard

    # Soft deletion
    soft_delete_column: "deleted_at"

    # Hard deletion (permanent)
    hard_delete_after_days: 730  # 2 years after soft delete
```

**Archival Configuration**

Archive old transcripts to reduce storage costs:

```yaml
transcript:
  archival:
    # Enable archival
    enabled: true

    # Archival trigger
    archive_after_days: 90

    # Archival storage
    archive_backend: "s3"      # s3 | local | glacier

    # S3 configuration
    s3:
      bucket: "friday-transcript-archive"
      prefix: "transcripts/{year}/{month}/"
      storage_class: "GLACIER"  # STANDARD | GLACIER | DEEP_ARCHIVE

      # Compression
      compress: true
      compression_format: "gzip"

    # Local archival
    local:
      directory: "./data/archive"
      compress: true
```

**Backup Configuration**

Backup transcripts for disaster recovery:

```yaml
transcript:
  backup:
    # Enable backups
    enabled: true

    # Backup schedule
    schedule: "daily"          # hourly | daily | weekly
    backup_time: "02:00"       # 2 AM

    # Backup destination
    destination: "local"       # local | s3 | rsync

    # Local backups
    local:
      directory: "./backups/transcripts"
      keep_daily: 7
      keep_weekly: 4
      keep_monthly: 12

    # S3 backups
    s3:
      bucket: "friday-backups"
      prefix: "transcripts/"
```

**Complete Storage Example**

```yaml
# config.yaml - Comprehensive transcript storage
transcript:
  storage:
    # Backend
    backend: "sqlite"
    sqlite:
      db_path: "./data/transcripts.db"
      wal_mode: true
      synchronous: "NORMAL"
      cache_size: 10000
      max_connections: 5

  # Retention
  retention:
    auto_cleanup: true
    cleanup_interval_hours: 24
    active_sessions_days: 90
    archived_sessions_days: 365
    deletion_strategy: "soft"

  # Archival
  archival:
    enabled: true
    archive_after_days: 90
    archive_backend: "local"
    local:
      directory: "./data/archive"
      compress: true

  # Backup
  backup:
    enabled: true
    schedule: "daily"
    backup_time: "02:00"
    destination: "local"
    local:
      directory: "./backups/transcripts"
      keep_daily: 7
      keep_weekly: 4
      keep_monthly: 12
```

### 10.6.2 Export Formats

Export transcripts in various formats for analysis, auditing, and archival.

**Supported Export Formats**

Friday supports multiple export formats:

- **JSON** - Structured data for programmatic access
- **JSONL** - Line-delimited JSON for streaming
- **Markdown** - Human-readable conversation format
- **HTML** - Styled conversation for viewing
- **CSV** - Tabular data for analysis
- **PDF** - Print-ready formatted conversation

**JSON Export Configuration**

```yaml
transcript:
  export:
    json:
      # Formatting
      pretty_print: true
      indent: 2
      sort_keys: false

      # Content
      include_metadata: true
      include_system_messages: true
      include_tool_calls: true
      include_timestamps: true

      # Filtering
      exclude_fields:
        - "internal_state"
        - "debug_info"
```

**JSONL Export Configuration**

```yaml
transcript:
  export:
    jsonl:
      # One entry per line
      one_entry_per_line: true

      # Compression
      compress: true
      compression_format: "gzip"

      # Content
      include_metadata: true
      include_system_messages: false
```

**Markdown Export Configuration**

```yaml
transcript:
  export:
    markdown:
      # Formatting
      style: "github"          # github | simple | detailed

      # Header
      include_header: true
      header_template: |
        # Conversation Transcript
        **Session ID**: {session_id}
        **Started**: {started_at}
        **Model**: {model_name}
        ---

      # Message formatting
      user_prefix: "**User:**"
      assistant_prefix: "**Assistant:**"

      # Tool calls
      include_tool_calls: true
      tool_call_format: "code_block"  # code_block | inline | summary

      # Timestamps
      include_timestamps: true
      timestamp_format: "%Y-%m-%d %H:%M:%S"
```

**HTML Export Configuration**

```yaml
transcript:
  export:
    html:
      # Template
      template: "default"      # default | minimal | detailed
      custom_template_path: null

      # Styling
      css_style: "embedded"    # embedded | external | inline
      theme: "light"           # light | dark | auto

      # Content
      include_metadata: true
      include_tool_calls: true
      syntax_highlighting: true

      # Interactive features
      collapsible_tool_calls: true
      search_functionality: true
```

**CSV Export Configuration**

```yaml
transcript:
  export:
    csv:
      # Delimiter
      delimiter: ","

      # Columns
      columns:
        - "turn_number"
        - "timestamp"
        - "role"
        - "message"
        - "model_name"
        - "tokens"
        - "latency_ms"

      # Encoding
      encoding: "utf-8"

      # Handling
      quote_all: false
      escape_char: "\\"
```

**PDF Export Configuration**

```yaml
transcript:
  export:
    pdf:
      # Page settings
      page_size: "A4"          # A4 | Letter | Legal
      orientation: "portrait"  # portrait | landscape

      # Fonts
      font_family: "Arial"
      font_size: 11

      # Formatting
      include_header: true
      include_footer: true
      include_page_numbers: true

      # Content
      syntax_highlighting: true
      include_tool_calls: true
```

**Export Triggers**

Configure when exports are automatically generated:

```yaml
transcript:
  export:
    auto_export:
      # Trigger conditions
      on_session_end: true
      on_archive: true
      on_error: false

      # Formats to export
      formats:
        - "json"
        - "markdown"

      # Export destination
      destination: "./exports/transcripts"

      # Naming
      filename_template: "{session_id}_{timestamp}.{format}"
```

**Filtered Exports**

Export only specific parts of transcripts:

```yaml
transcript:
  export:
    filters:
      # Date range
      date_range:
        start: "2025-01-01"
        end: "2025-12-31"

      # User filter
      user_ids:
        - "user_123"
        - "user_456"

      # Content filter
      include_only:
        - turns_with_errors: false
        - turns_with_tool_calls: true

      # Minimum/maximum
      min_turns: 5
      max_turns: 1000
```

**Compression Options**

```yaml
transcript:
  export:
    compression:
      # Enable compression
      enabled: true

      # Compression format
      format: "gzip"           # gzip | bzip2 | xz

      # Compression level
      level: 6                 # 1-9 (1=fastest, 9=best compression)

      # Batch compression
      batch_compress: true
      batch_size: 10
```

**Complete Export Example**

```yaml
# config.yaml - Comprehensive export configuration
transcript:
  export:
    # JSON export
    json:
      pretty_print: true
      indent: 2
      include_metadata: true
      include_tool_calls: true

    # Markdown export
    markdown:
      style: "github"
      include_header: true
      include_timestamps: true
      tool_call_format: "code_block"

    # HTML export
    html:
      template: "default"
      theme: "light"
      syntax_highlighting: true
      collapsible_tool_calls: true

    # Auto-export
    auto_export:
      on_session_end: true
      formats:
        - "json"
        - "markdown"
      destination: "./exports/transcripts"
      filename_template: "{session_id}_{timestamp}.{format}"

    # Compression
    compression:
      enabled: true
      format: "gzip"
      level: 6
```

**Environment Variable Overrides**

```bash
# Storage backend
FRIDAY_TRANSCRIPT__STORAGE__BACKEND="sqlite"
FRIDAY_TRANSCRIPT__STORAGE__SQLITE__DB_PATH="./data/transcripts.db"

# Export
FRIDAY_TRANSCRIPT__EXPORT__AUTO_EXPORT__ON_SESSION_END="true"
FRIDAY_TRANSCRIPT__EXPORT__COMPRESSION__ENABLED="true"
```

---

## 10.7 Telemetry & Observability

Telemetry and observability provide visibility into Friday's runtime behavior, performance metrics, and operational health.

### 10.7.1 Logging Configuration

Configure structured logging for debugging and auditing.

**Log Level Configuration**

```yaml
logging:
  # Global log level
  level: "INFO"              # DEBUG | INFO | WARNING | ERROR

  # Per-package log levels
  package_levels:
    friday_core: "INFO"
    friday_memory: "DEBUG"
    friday_llm: "INFO"
    friday_agent: "INFO"
    friday_tools: "WARNING"
```

**Log Format Configuration**

```yaml
logging:
  format:
    # Output format
    type: "json"             # json | text | colored

    # JSON formatting
    json:
      pretty_print: false
      timestamp_format: "iso"  # iso | unix | custom
      include_hostname: true
      include_process_id: true

    # Text formatting
    text:
      template: "[{timestamp}] {level} {logger}: {message}"
      timestamp_format: "%Y-%m-%d %H:%M:%S"
      colored: true
```

**Log Destinations**

Configure where logs are written:

```yaml
logging:
  outputs:
    # Console output
    console:
      enabled: true
      level: "INFO"
      format: "colored"

    # File output
    file:
      enabled: true
      path: "./logs/friday.log"
      level: "DEBUG"
      format: "json"

      # Rotation
      rotation:
        enabled: true
        max_size_mb: 100
        backup_count: 10
        rotation_time: "midnight"

    # Syslog output
    syslog:
      enabled: false
      host: "localhost"
      port: 514
      facility: "local0"
```

**Structured Logging Context**

Add contextual information to all logs:

```yaml
logging:
  context:
    # Always included
    always_include:
      - "session_id"
      - "user_id"
      - "agent_id"
      - "environment"

    # Environment info
    include_environment: true
    include_hostname: true
    include_process_info: true

    # Custom fields
    custom_fields:
      application: "friday-agent"
      version: "0.1.0"
      deployment: "production"
```

**Log Sampling**

Reduce log volume in high-traffic scenarios:

```yaml
logging:
  sampling:
    # Enable sampling
    enabled: true

    # Sample rate (0.0-1.0)
    rate: 0.1                # Log 10% of messages

    # Always log these levels
    always_log_levels:
      - "ERROR"
      - "CRITICAL"

    # Sample per logger
    per_logger_rates:
      friday_memory: 0.05    # 5% for memory operations
      friday_llm: 0.5        # 50% for LLM calls
```

**Sensitive Data Redaction**

Automatically redact sensitive information:

```yaml
logging:
  redaction:
    # Enable redaction
    enabled: true

    # Patterns to redact
    patterns:
      - "password"
      - "api_key"
      - "secret"
      - "token"
      - "authorization"

    # Redaction replacement
    replacement: "[REDACTED]"

    # Redact values by key
    redact_keys:
      - "password"
      - "api_key"
      - "OPENAI_API_KEY"
      - "ANTHROPIC_API_KEY"
```

**Performance Logging**

Log performance metrics:

```yaml
logging:
  performance:
    # Enable performance logging
    enabled: true

    # Log slow operations
    slow_operation_threshold_ms: 1000

    # Operations to track
    track_operations:
      - "llm_call"
      - "memory_retrieval"
      - "tool_execution"
      - "extraction"

    # Include metrics
    include_metrics:
      - "duration_ms"
      - "memory_usage_mb"
      - "cpu_percent"
```

**Complete Logging Example**

```yaml
# config.yaml - Comprehensive logging configuration
logging:
  # Log levels
  level: "INFO"
  package_levels:
    friday_memory: "DEBUG"
    friday_tools: "WARNING"

  # Format
  format:
    type: "json"
    json:
      pretty_print: false
      timestamp_format: "iso"
      include_hostname: true

  # Outputs
  outputs:
    console:
      enabled: true
      level: "INFO"
      format: "colored"

    file:
      enabled: true
      path: "./logs/friday.log"
      level: "DEBUG"
      format: "json"
      rotation:
        enabled: true
        max_size_mb: 100
        backup_count: 10

  # Context
  context:
    always_include:
      - "session_id"
      - "user_id"
    custom_fields:
      application: "friday-agent"
      environment: "production"

  # Redaction
  redaction:
    enabled: true
    patterns:
      - "password"
      - "api_key"
      - "token"
    redact_keys:
      - "OPENAI_API_KEY"

  # Performance
  performance:
    enabled: true
    slow_operation_threshold_ms: 1000
    track_operations:
      - "llm_call"
      - "memory_retrieval"
```

### 10.7.2 Telemetry Integration

Integrate with observability platforms for metrics, tracing, and monitoring.

**OpenTelemetry Integration**

Friday supports OpenTelemetry for standardized telemetry:

```yaml
telemetry:
  # Enable telemetry
  enabled: true

  # Provider
  provider: "opentelemetry"

  opentelemetry:
    # Service name
    service_name: "friday-agent"
    service_version: "0.1.0"

    # Exporter
    exporter: "otlp"         # otlp | jaeger | zipkin | prometheus

    # OTLP configuration
    otlp:
      endpoint: "http://localhost:4317"
      protocol: "grpc"       # grpc | http
      headers:
        authorization: "Bearer ${OTEL_TOKEN}"

    # Resource attributes
    resource_attributes:
      deployment.environment: "production"
      service.namespace: "friday"
```

**Metrics Configuration**

Configure what metrics are collected:

```yaml
telemetry:
  metrics:
    # Enable metrics collection
    enabled: true

    # Metrics to collect
    collect:
      # LLM metrics
      llm:
        - "llm.calls.total"
        - "llm.calls.duration_ms"
        - "llm.tokens.prompt"
        - "llm.tokens.completion"
        - "llm.tokens.total"
        - "llm.cost.usd"
        - "llm.errors.total"

      # Memory metrics
      memory:
        - "memory.entities.count"
        - "memory.relationships.count"
        - "memory.retrieval.duration_ms"
        - "memory.extraction.duration_ms"

      # Tool metrics
      tools:
        - "tools.executions.total"
        - "tools.executions.duration_ms"
        - "tools.executions.errors"

      # System metrics
      system:
        - "system.memory.usage_mb"
        - "system.cpu.usage_percent"

    # Metric aggregation
    aggregation:
      interval_seconds: 60
      histogram_buckets: [10, 50, 100, 500, 1000, 5000]
```

**Distributed Tracing**

Enable distributed tracing for request flows:

```yaml
telemetry:
  tracing:
    # Enable tracing
    enabled: true

    # Sampling
    sampling:
      strategy: "probabilistic"  # always | probabilistic | rate_limit
      rate: 0.1                 # Sample 10% of traces

    # Trace propagation
    propagation:
      formats:
        - "tracecontext"        # W3C Trace Context
        - "baggage"             # W3C Baggage

    # Spans to create
    create_spans_for:
      - "llm_calls"
      - "memory_operations"
      - "tool_executions"
      - "agent_turns"

    # Span attributes
    span_attributes:
      include_inputs: false     # Don't log full inputs
      include_outputs: false
      include_errors: true
```

**DataDog Integration**

Integrate with DataDog for monitoring:

```yaml
telemetry:
  datadog:
    # Enable DataDog
    enabled: true

    # API configuration
    api_key: "${DATADOG_API_KEY}"
    site: "datadoghq.com"     # datadoghq.com | datadoghq.eu

    # Service mapping
    service: "friday-agent"
    env: "production"
    version: "0.1.0"

    # Metrics
    metrics:
      enabled: true
      flush_interval_seconds: 10

      # Tags
      global_tags:
        - "team:ai"
        - "application:friday"

    # APM (traces)
    apm:
      enabled: true
      sample_rate: 0.1
```

**Prometheus Integration**

Expose metrics for Prometheus scraping:

```yaml
telemetry:
  prometheus:
    # Enable Prometheus metrics
    enabled: true

    # HTTP server for /metrics endpoint
    http_server:
      host: "0.0.0.0"
      port: 9090
      path: "/metrics"

    # Metrics configuration
    metrics:
      # Metric prefix
      namespace: "friday"
      subsystem: "agent"

      # Additional labels
      constant_labels:
        environment: "production"
        version: "0.1.0"
```

**Sentry Integration**

Error tracking with Sentry:

```yaml
telemetry:
  sentry:
    # Enable Sentry
    enabled: true

    # DSN
    dsn: "${SENTRY_DSN}"

    # Environment
    environment: "production"
    release: "friday-agent@0.1.0"

    # Sampling
    traces_sample_rate: 0.1
    profiles_sample_rate: 0.1

    # Error filtering
    ignore_errors:
      - "KeyboardInterrupt"
      - "SystemExit"

    # Breadcrumbs
    max_breadcrumbs: 100
    attach_stacktrace: true
```

**Custom Telemetry Backends**

Integrate with custom telemetry systems:

```yaml
telemetry:
  custom:
    # Enable custom backend
    enabled: true

    # Backend configuration
    backend_type: "http"

    # HTTP backend
    http:
      url: "https://telemetry.company.com/ingest"
      method: "POST"
      headers:
        authorization: "Bearer ${TELEMETRY_TOKEN}"

      # Batching
      batch_size: 100
      batch_interval_seconds: 5
```

**Complete Telemetry Example**

```yaml
# config.yaml - Comprehensive telemetry configuration
telemetry:
  # Core settings
  enabled: true
  provider: "opentelemetry"

  # OpenTelemetry
  opentelemetry:
    service_name: "friday-agent"
    service_version: "0.1.0"
    exporter: "otlp"
    otlp:
      endpoint: "http://localhost:4317"
      protocol: "grpc"
    resource_attributes:
      deployment.environment: "production"

  # Metrics
  metrics:
    enabled: true
    collect:
      llm:
        - "llm.calls.total"
        - "llm.calls.duration_ms"
        - "llm.tokens.total"
        - "llm.cost.usd"
      memory:
        - "memory.entities.count"
        - "memory.retrieval.duration_ms"
      tools:
        - "tools.executions.total"
        - "tools.executions.duration_ms"
    aggregation:
      interval_seconds: 60

  # Tracing
  tracing:
    enabled: true
    sampling:
      strategy: "probabilistic"
      rate: 0.1
    create_spans_for:
      - "llm_calls"
      - "memory_operations"
      - "tool_executions"

  # DataDog
  datadog:
    enabled: true
    api_key: "${DATADOG_API_KEY}"
    service: "friday-agent"
    env: "production"
    metrics:
      enabled: true
      global_tags:
        - "team:ai"

  # Prometheus
  prometheus:
    enabled: true
    http_server:
      port: 9090
      path: "/metrics"
```

**Environment Variable Overrides**

```bash
# Telemetry
FRIDAY_TELEMETRY__ENABLED="true"
FRIDAY_TELEMETRY__PROVIDER="opentelemetry"

# OpenTelemetry
FRIDAY_TELEMETRY__OPENTELEMETRY__SERVICE_NAME="friday-agent"
FRIDAY_TELEMETRY__OPENTELEMETRY__OTLP__ENDPOINT="http://localhost:4317"

# DataDog
DATADOG_API_KEY="your-api-key"
FRIDAY_TELEMETRY__DATADOG__ENABLED="true"

# Prometheus
FRIDAY_TELEMETRY__PROMETHEUS__ENABLED="true"
FRIDAY_TELEMETRY__PROMETHEUS__HTTP_SERVER__PORT="9090"
```

---

## Summary

This comprehensive configuration guide has covered all aspects of Friday Agent Framework configuration:

**10.1 Configuration Architecture** - Hierarchical config merging, validation, environment variables

**10.2 LLM Configuration** - Provider setup, OpenRouter, model settings, resilience

**10.3 Memory Configuration** - Context windowing, priming, lifecycle, collections

**10.4 Tool Configuration** - Registry setup, security, sandboxing, allowlists

**10.5 Extraction Configuration** - LLM selection, prompts, entity types, relationship verbs

**10.6 Transcript Configuration** - Storage backends, export formats, compression

**10.7 Telemetry & Observability** - Logging, metrics, tracing, monitoring integrations

With these configuration options, you can tailor Friday to your specific use case, from lightweight development setups to production-grade deployments with full observability.

---

**Next Steps:**

- Section 11: Deployment & Operations - Production deployment patterns
- Section 12: Troubleshooting & FAQ - Common issues and solutions
- Section 13: API Reference - Complete API documentation

