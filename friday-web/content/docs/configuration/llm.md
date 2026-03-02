---
title: "LLM Providers"
description: "Configure OpenAI, Anthropic, Ollama, and OpenRouter in one config line."
weight: 2
---

Friday uses [LiteLLM](https://litellm.ai) as a unified client, providing consistent access to OpenAI, Anthropic, Google, Ollama, LM Studio, and OpenRouter with a single configuration interface.

## Provider Setup

Friday supports major cloud providers and local model hosting solutions. Each provider requires specific configuration patterns.

### OpenAI

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

If you belong to multiple OpenAI organizations:

```yaml
llm:
  model: "gpt-4o"
  api_base: "https://api.openai.com/v1"
```

```bash
OPENAI_ORGANIZATION=org-your-org-id
```

**Azure OpenAI**

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

### Anthropic

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

### Google Gemini

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

### Ollama (Local)

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
ollama pull llama3.1:8b         # Meta's Llama 3.1 8B
ollama pull mistral:7b          # Mistral 7B
ollama pull codellama:13b       # Code-specialized model
ollama pull qwen2.5:14b         # Alibaba's Qwen 2.5

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

### LM Studio (Local)

LM Studio provides a GUI for running local models with an OpenAI-compatible API.

1. Download from https://lmstudio.ai
2. Install and launch LM Studio
3. Download models via the GUI (search for models by name)
4. Start local server (Developer → Start Server)

```yaml
llm:
  model: "openai/local-model"      # LM Studio uses OpenAI format
  api_base: "http://localhost:1234/v1"
  api_key: "lm-studio"             # Any non-empty string
  temperature: 0.7
```

**LM Studio Best Practices**

- Download quantized models (Q4, Q5) for faster inference
- Configure context length in LM Studio settings (increase to 8192+ for Friday)
- Enable GPU acceleration in settings for 5-10x speedup
- Load the model before starting Friday to avoid cold-start delay

**Hardware Requirements for Local Models**

| Model Size | Minimum RAM | Recommended RAM | GPU VRAM (Optional) |
|------------|-------------|-----------------|---------------------|
| 3B-7B | 8GB | 16GB | 6GB |
| 8B-13B | 16GB | 32GB | 12GB |
| 30B-34B | 32GB | 64GB | 24GB |
| 70B+ | 64GB | 128GB | 48GB+ |

## OpenRouter for Multi-Model Access

OpenRouter provides unified API access to 100+ models from multiple providers, enabling easy switching and fallback strategies.

**Setup**

1. Sign up at https://openrouter.ai
2. Generate an API key
3. Add credits to your account (pay-as-you-go)

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

# OpenAI models
model: "openrouter/openai/gpt-4o"

# Google models
model: "openrouter/google/gemini-2.0-flash-exp"

# Meta models
model: "openrouter/meta-llama/llama-3.1-70b-instruct"

# Mistral models
model: "openrouter/mistralai/mistral-large"

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

**Fallback Configuration**

Configure fallback models for resilience:

```yaml
llm:
  model: "openrouter/anthropic/claude-3.5-sonnet"
  fallback_models:
    - "openrouter/openai/gpt-4o"
    - "openrouter/google/gemini-1.5-pro"
```

OpenRouter adds a small markup (typically 10-15%) over provider prices. Check current pricing at https://openrouter.ai/models.

## Model-Specific Settings

Fine-tune model behavior with generation parameters.

### Temperature

Controls randomness in model outputs. Lower values produce more deterministic responses.

```yaml
llm:
  temperature: 0.0  # Deterministic (fact retrieval, code)
  # temperature: 0.3  # Low variability (classification, extraction)
  # temperature: 0.7  # Balanced (general conversation)
  # temperature: 1.0  # Creative (brainstorming, writing)
  # temperature: 1.5  # Very creative (experimental)
```

| Temperature | Best For | Example Tasks |
|-------------|----------|---------------|
| 0.0 - 0.2 | Deterministic tasks | Code generation, data extraction, classification |
| 0.3 - 0.5 | Factual responses | Q&A, summarization, translation |
| 0.6 - 0.8 | Conversational | General chat, recommendations |
| 0.9 - 1.2 | Creative tasks | Brainstorming, creative writing |
| 1.3 - 2.0 | Experimental | Highly diverse outputs |

### Max Tokens

Limits the response length. Different models have different maximum token limits.

```yaml
llm:
  max_tokens: 1000    # Short responses
  # max_tokens: 4096   # Standard responses
  # max_tokens: 8192   # Long-form content
  # max_tokens: 16384  # Very long outputs
```

| Model | Max Context | Recommended max_tokens |
|-------|-------------|------------------------|
| GPT-4o | 128K | 4K - 8K |
| Claude 3.5 | 200K | 4K - 8K |
| Gemini 1.5 | 1M | 8K - 16K |
| Llama 3.1 | 128K | 2K - 4K |

### Top P (Nucleus Sampling)

Alternative to temperature. Controls diversity by sampling from the top P probability mass.

```yaml
llm:
  top_p: 0.9  # Default, includes 90% probability mass
```

Use `temperature` for most cases. Use `top_p` when you want to exclude low-probability tokens without affecting high-probability tokens. Avoid adjusting both simultaneously.

### Frequency and Presence Penalty

Reduce repetition by penalizing repeated tokens (OpenAI models only).

```yaml
llm:
  frequency_penalty: 0.5  # Penalize frequent tokens (-2.0 to 2.0)
  presence_penalty: 0.5   # Penalize any repeated tokens (-2.0 to 2.0)
```

### Stop Sequences

Define custom tokens that stop generation.

```yaml
llm:
  stop_sequences:
    - "\n\n\n"      # Stop at triple newline
    - "###"         # Stop at delimiter
    - "END_OUTPUT"  # Stop at custom marker
```

**Complete Model Configuration Example**

```yaml
# config.yaml - Production configuration
llm:
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
    - "gpt-4o-mini"
```

## Resilience and Retry Configuration

Friday's resilience layer wraps LLM calls with retry logic, timeout enforcement, and circuit breakers to handle transient failures gracefully.

### Retry Configuration

```yaml
llm:
  resilience:
    max_retries: 3           # 0 disables retries

    # Exponential backoff
    backoff_multiplier: 1.0  # Backoff growth rate
    backoff_min: 1.0         # Minimum wait (seconds)
    backoff_max: 10.0        # Maximum wait (seconds)
```

Friday uses exponential backoff with jitter:

```text
wait_time = min(backoff_min * (backoff_multiplier ^ attempt) + jitter, backoff_max)
```

Example backoff sequence (backoff_min=1.0, backoff_multiplier=2.0):
- Attempt 1: 1.0s
- Attempt 2: 2.0s
- Attempt 3: 4.0s
- Attempt 4: 8.0s (capped at backoff_max)

**Retryable Errors** — Friday automatically retries:
- `RateLimitError` — API rate limit exceeded
- `ServiceUnavailableError` — Temporary service outage
- `APIConnectionError` — Network connectivity issues
- `InternalServerError` — Provider-side errors (5xx)

**Non-Retryable Errors** — These fail immediately:
- `AuthenticationError` — Invalid API key
- `InvalidRequestError` — Malformed request
- `NotFoundError` — Model doesn't exist
- `ContextLengthExceededError` — Input too long

### Timeout Configuration

```yaml
llm:
  resilience:
    timeout_seconds: 30.0         # Standard calls
    stream_timeout_seconds: 60.0  # Streaming calls (longer)
```

| Operation | Recommended Timeout |
|-----------|---------------------|
| Short prompts (<500 tokens) | 30s |
| Medium prompts (500-2K tokens) | 60s |
| Long prompts (2K-8K tokens) | 120s |
| Code generation | 90s |
| Streaming responses | 60-120s |

### Circuit Breaker Configuration

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

```text
CLOSED --[failure_threshold failures]--> OPEN
OPEN --[recovery_timeout expires]--> HALF_OPEN
HALF_OPEN --[success]--> CLOSED
HALF_OPEN --[failure]--> OPEN
```

Enable circuit breakers for production systems with multiple LLM providers where cascading failures are costly. Disable them in development environments where you want to see actual errors.

### Preset Configurations

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
export FRIDAY_LLM_MAX_RETRIES="5"
export FRIDAY_LLM_TIMEOUT_SECONDS="60.0"
export FRIDAY_LLM_CIRCUIT_BREAKER_ENABLED="true"
export FRIDAY_LLM_CB_FAILURE_THRESHOLD="3"
```

**Complete Resilience Example**

```yaml
# config.yaml - Production resilience configuration
llm:
  model: "gpt-4o"
  resilience:
    max_retries: 5
    backoff_multiplier: 2.0
    backoff_min: 1.0
    backoff_max: 30.0

    timeout_seconds: 60.0
    stream_timeout_seconds: 120.0

    circuit_breaker:
      enabled: true
      failure_threshold: 3
      recovery_timeout: 60.0
      half_open_max_calls: 1

fallback_models:
  - "gpt-4o-mini"
```

## Related Pages

- [Configuration Architecture](/docs/configuration/architecture/) — How Friday loads and merges configuration layers
- [Memory Settings](/docs/configuration/memory/) — Memory-specific configuration options
- [Full Reference](/docs/configuration/reference/) — Complete configuration key reference and defaults
