---
title: "Full Reference"
description: "Complete listing of every configuration key and its default value."
weight: 4
---

Complete listing of every configuration key Friday recognizes, its type, default value, and a brief description of its effect.

## Complete config.yaml Template

The annotated template below covers all available settings. Copy and customize for your own configuration.

```yaml
# =============================================================================
# Friday Agent Framework - Complete Configuration Template
# Version: v0.1.0
# =============================================================================

# -----------------------------------------------------------------------------
# Application Settings
# -----------------------------------------------------------------------------
app:
  # Environment: development, production, testing
  env: development

  # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_level: INFO

  # Working directory for relative paths
  working_dir: "."

  # Telemetry and observability
  telemetry:
    enabled: true
    provider: "opentelemetry"  # opentelemetry, datadog, newrelic, none
    endpoint: "http://localhost:4317"
    sample_rate: 1.0

# -----------------------------------------------------------------------------
# LLM Configuration
# -----------------------------------------------------------------------------
llm:
  model: "gpt-4o-mini"

  fast_model: "gpt-4o-mini"  # For quick operations
  smart_model: "gpt-4o"      # For complex reasoning

  temperature: 0.7
  max_tokens: 4096

  # Set via environment variables, not config files
  openai_api_key: null
  anthropic_api_key: null

  ollama:
    base_url: "http://localhost:11434"
    enabled: false

  openrouter:
    enabled: false
    api_key: null
    base_url: "https://openrouter.ai/api/v1"

  resilience:
    max_retries: 3
    initial_backoff: 1.0
    max_backoff: 60.0
    timeout: 120.0
    enable_fallback: true
    fallback_model: "gpt-4o-mini"

# -----------------------------------------------------------------------------
# Memory Configuration
# -----------------------------------------------------------------------------
memory:
  context:
    max_tokens: 8192
    reserved_tokens: 2048
    budget_strategy: "knapsack"  # knapsack, greedy, priority
    token_counter: "tiktoken"

  priming:
    enabled: true
    top_entities: 50
    max_insights: 50
    recent_turns: 10
    use_pagerank: true

  lifecycle:
    enable_decay: true
    decay_algorithm: "exponential"  # exponential, linear, stepwise
    decay_rate: 0.1
    enable_consolidation: true
    consolidation_threshold: 0.85
    enable_pruning: true
    pruning_threshold: 0.2
    max_episodic_age: 30
    max_semantic_age: 90

  vector:
    provider: "chroma"  # chroma, faiss, pinecone, weaviate
    collection_name: "friday_memory"
    persist_directory: "./data/chroma"
    embedding_model: "text-embedding-3-small"
    embedding_dimensions: 1536
    distance_metric: "cosine"
    top_k: 5
    min_similarity: 0.7
    enable_hybrid: false
    enable_reranking: false

  graph:
    provider: "networkx"  # networkx, neo4j, elementx
    persist_path: "./data/graph.json"
    neo4j:
      uri: "bolt://localhost:7687"
      username: "neo4j"
      password: null  # Set via NEO4J_PASSWORD
    hebbian:
      enabled: true
      learning_rate: 0.1
      decay_rate: 0.05
      min_hit_count: 3
    entity_resolution:
      enabled: true
      fuzzy_threshold: 0.85
      matching_algorithm: "jaro_winkler"

  episodic:
    provider: "sqlite"  # json, sqlite, postgres
    db_path: "./data/transcript.db"
    postgres:
      host: "localhost"
      port: 5432
      database: "friday_memory"
      username: "friday"
      password: null  # Set via POSTGRES_PASSWORD
    max_active_turns: 50
    enable_consolidation: true
    consolidation_interval: 10

# -----------------------------------------------------------------------------
# Extraction Configuration
# -----------------------------------------------------------------------------
extraction:
  enabled: true
  llm:
    model: "gpt-4o-mini"
    temperature: 0.3
    max_tokens: 2048
  trigger:
    interval: 5              # Every N turns
    on_explicit_signal: true
    on_session_end: true
  entities:
    min_confidence: 0.7
    allowed_types:
      - person
      - organization
      - location
      - concept
      - technology
      - project
      - document
      - event
      - task
    enable_coreference: true
  relationships:
    min_confidence: 0.6
    allowed_verbs:
      - works_at
      - located_in
      - part_of
      - related_to
      - owns
      - manages
      - collaborates_with
      - depends_on
      - implements
      - uses
    bidirectional: false
  insights:
    enabled: true
    min_importance: 0.8
    categories:
      - preference
      - goal
      - constraint
      - pattern
      - decision
      - learning

# -----------------------------------------------------------------------------
# Tool Configuration
# -----------------------------------------------------------------------------
tools:
  selection_strategy: "selective"  # all, selective, dynamic
  enable_dynamic_selection: true
  allowlist: []   # empty = all tools available
  blocklist: []
  allowed_categories:
    - filesystem
    - shell
    - web
    - git
    - code
    - data
    - text
    - utility
    - memory
  security:
    enable_sandbox: true
    allowed_paths:
      - "."
      - "./data"
      - "./output"
    blocked_paths:
      - "/etc"
      - "/System"
      - "~/.ssh"
      - "~/.aws"
    enable_shell_sandbox: true
    allowed_commands:
      - git
      - ls
      - cat
      - grep
      - find
      - python
    blocked_commands:
      - rm -rf
      - dd
      - mkfs
  filesystem:
    max_file_size: 10485760   # 10MB in bytes
    default_encoding: "utf-8"
    detect_binary: true
  web:
    timeout: 30
    max_response_size: 10485760
    user_agent: "Friday-Agent/0.1.0"
    verify_ssl: true
    follow_redirects: true
    max_redirects: 5
  code_execution:
    enabled: true
    environment: "subprocess"  # subprocess, docker, kubernetes
    timeout: 60
    max_output_size: 1048576  # 1MB
    allowed_languages:
      - python
      - javascript
      - bash

# -----------------------------------------------------------------------------
# Agent Configuration
# -----------------------------------------------------------------------------
agent:
  default_profile: "copilot"
  profiles_dir: "./agents"
  copilot:
    max_iterations: 10
    enable_streaming: false
    tool_autonomy: "semi_auto"  # manual, semi_auto, auto
  autonomous:
    max_depth: 5
    max_parallel: 3
    task_timeout: 300
    enable_checkpointing: true

# -----------------------------------------------------------------------------
# Transcript Configuration
# -----------------------------------------------------------------------------
transcript:
  enabled: true
  storage_dir: "./data/transcripts"
  recording:
    record_user: true
    record_agent: true
    record_tools: true
    record_reasoning: true
    record_context: false
    record_tokens: true
  export:
    default_format: "markdown"
    include_metadata: true
    include_timestamps: true
    pretty_json: true
  retention:
    max_age: 90              # days, 0 = never delete
    auto_cleanup: true
    cleanup_interval: 7

# -----------------------------------------------------------------------------
# MCP (Model Context Protocol) Configuration
# -----------------------------------------------------------------------------
mcp:
  enabled: false
  server:
    host: "localhost"
    port: 8765
    transport: "sse"  # sse, websocket
    require_auth: false
    api_key: null   # Set via MCP_API_KEY
  client:
    enabled: false
    servers: []

# -----------------------------------------------------------------------------
# Performance Configuration
# -----------------------------------------------------------------------------
performance:
  caching:
    enabled: true
    provider: "memory"  # memory, redis, memcached
    ttl: 3600
    max_size: 500
    redis:
      host: "localhost"
      port: 6379
      db: 0
      password: null  # Set via REDIS_PASSWORD
  concurrency:
    max_llm_concurrency: 5
    max_tool_concurrency: 10
    enable_queuing: true
    max_queue_size: 100
  limits:
    max_memory: 4096
    max_cpu: 80
    enable_monitoring: true

# -----------------------------------------------------------------------------
# Development & Debugging
# -----------------------------------------------------------------------------
development:
  debug: false
  verbose: false
  enable_profiling: false
  profiling_dir: "./data/profiling"
  log_requests: false
  include_stack_traces: true
  mock:
    mock_llm: false
    mock_tools: false
    mock_data_dir: "./tests/fixtures"
```

## Environment Variable Mappings

All configuration settings can be overridden via environment variables. The naming convention is:

```text
FRIDAY_<SECTION>__<SUBSECTION>__<SETTING>
```

| Environment Variable | Config Path | Description | Example |
|---------------------|-------------|-------------|---------|
| `APP_ENV` | `app.env` | Application environment | `production` |
| `LOG_LEVEL` | `app.log_level` | Logging verbosity | `INFO` |
| `OPENAI_API_KEY` | `llm.openai_api_key` | OpenAI API key | `sk-proj-...` |
| `ANTHROPIC_API_KEY` | `llm.anthropic_api_key` | Anthropic API key | `sk-ant-...` |
| `OLLAMA_BASE_URL` | `llm.ollama.base_url` | Ollama server URL | `http://localhost:11434` |
| `FRIDAY_LLM__MODEL` | `llm.model` | Default LLM model | `gpt-4o` |
| `FRIDAY_LLM__TEMPERATURE` | `llm.temperature` | Sampling temperature | `0.7` |
| `FRIDAY_LLM__MAX_TOKENS` | `llm.max_tokens` | Max response tokens | `4096` |
| `FRIDAY_LLM__RESILIENCE__MAX_RETRIES` | `llm.resilience.max_retries` | Max retry attempts | `5` |
| `FRIDAY_MEMORY__CONTEXT__MAX_TOKENS` | `memory.context.max_tokens` | Context window size | `8192` |
| `FRIDAY_MEMORY__PRIMING__ENABLED` | `memory.priming.enabled` | Enable memory priming | `true` |
| `FRIDAY_MEMORY__PRIMING__TOP_ENTITIES` | `memory.priming.top_entities` | Entities to prime | `50` |
| `FRIDAY_MEMORY__VECTOR__PROVIDER` | `memory.vector.provider` | Vector store type | `chroma` |
| `FRIDAY_MEMORY__VECTOR__COLLECTION_NAME` | `memory.vector.collection_name` | Collection name | `friday_memory` |
| `FRIDAY_MEMORY__GRAPH__PROVIDER` | `memory.graph.provider` | Graph store type | `networkx` |
| `FRIDAY_MEMORY__EPISODIC__PROVIDER` | `memory.episodic.provider` | Episodic store type | `sqlite` |
| `FRIDAY_TOOLS__SECURITY__ENABLE_SANDBOX` | `tools.security.enable_sandbox` | Enable tool sandboxing | `true` |
| `FRIDAY_EXTRACTION__ENABLED` | `extraction.enabled` | Enable memory extraction | `true` |
| `FRIDAY_TRANSCRIPT__ENABLED` | `transcript.enabled` | Enable transcripts | `true` |
| `NEO4J_PASSWORD` | `memory.graph.neo4j.password` | Neo4j password | `password123` |
| `POSTGRES_PASSWORD` | `memory.episodic.postgres.password` | PostgreSQL password | `password123` |
| `VAULT_TOKEN` | `security.secrets.vault.token` | Vault access token | `hvs.xxx` |
| `REDIS_PASSWORD` | `performance.caching.redis.password` | Redis password | `password123` |
| `MCP_API_KEY` | `mcp.server.api_key` | MCP server API key | `sk-mcp-...` |

**Type Conversion Rules**

Environment variable values are always strings. Friday converts them as follows:

- **Booleans**: `"true"`, `"false"`, `"1"`, `"0"`, `"yes"`, `"no"` (case-insensitive)
- **Numbers**: Parsed as int or float based on presence of decimal point
- **Lists**: Comma-separated values: `"item1,item2,item3"`
- **None/Null**: `"null"`, `"none"`, empty string (case-insensitive)

## FridayBaseSettings Class

The `FridayBaseSettings` class is the root Pydantic settings model. All packages inherit from it.

Location: `packages/friday-core/src/friday_core/config.py`

```python
class FridayBaseSettings(BaseSettings):
    """Global settings inherited by all packages."""

    APP_ENV: str = "development"  # development | production | testing
    LOG_LEVEL: str = "INFO"       # DEBUG | INFO | WARNING | ERROR | CRITICAL
    DEFAULT_MODEL: str = "gpt-4-turbo"
    OPENAI_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
```

**Configuration Loading Priority**

1. Default values in Pydantic models
2. `.env` file in the project root
3. Environment variables (highest priority)
4. Runtime overrides via code

All configuration uses Pydantic 2.0+ for automatic validation and type checking. Invalid configurations raise `ValidationError` at startup with detailed error messages showing the field path, expected type, and the invalid value.

## Related Pages

- [Configuration Architecture](/docs/configuration/architecture/) — How Friday loads and merges configuration layers
- [LLM Providers](/docs/configuration/llm/) — Configure cloud and local LLM providers
- [Memory Settings](/docs/configuration/memory/) — Memory-specific configuration options
