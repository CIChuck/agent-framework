# Friday Agent Framework
## Section 14: Appendices - Technical Reference

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24

---

## Table of Contents

- [Appendix A: Complete Configuration Reference](#appendix-a-complete-configuration-reference)
  - [A.1 Full Annotated config.yaml](#a1-full-annotated-configyaml)
  - [A.2 Environment Variable Mappings](#a2-environment-variable-mappings)
  - [A.3 Configuration Schema Reference](#a3-configuration-schema-reference)
- [Appendix B: Tool Catalog](#appendix-b-tool-catalog)
  - [B.1 Complete Tool List](#b1-complete-tool-list)
  - [B.2 Tool Quick Reference Table](#b2-tool-quick-reference-table)
  - [B.3 Tool Categories](#b3-tool-categories)
- [Appendix C: API Reference](#appendix-c-api-reference)
  - [C.1 Core Agent Classes](#c1-core-agent-classes)
  - [C.2 Memory System API](#c2-memory-system-api)
  - [C.3 Tool System API](#c3-tool-system-api)
  - [C.4 LLM Client API](#c4-llm-client-api)
- [Appendix D: Protocol Specifications](#appendix-d-protocol-specifications)
  - [D.1 ToolDefinition Protocol](#d1-tooldefinition-protocol)
  - [D.2 LLMClient Protocol](#d2-llmclient-protocol)
  - [D.3 Storage Adapter Protocols](#d3-storage-adapter-protocols)
  - [D.4 ToolRegistry Protocol](#d4-toolregistry-protocol)
- [Appendix E: Migration Guides](#appendix-e-migration-guides)
  - [E.1 Version History](#e1-version-history)
  - [E.2 Breaking Changes](#e2-breaking-changes)
  - [E.3 Migration Scripts](#e3-migration-scripts)
- [Appendix F: Glossary](#appendix-f-glossary)
  - [F.1 Core Concepts](#f1-core-concepts)
  - [F.2 Memory Systems](#f2-memory-systems)
  - [F.3 Agent Patterns](#f3-agent-patterns)
  - [F.4 Technical Terms](#f4-technical-terms)

---

## Appendix A: Complete Configuration Reference

### A.1 Full Annotated config.yaml

This section provides a complete, production-ready `config.yaml` with all available settings documented inline. Use this as a template for your own configurations.

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
  # Controls logging verbosity, error reporting, and safety checks
  env: development

  # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
  # Affects console and file logging output
  log_level: INFO

  # Working directory for relative paths
  # All file operations use this as the base directory
  working_dir: "."

  # Enable telemetry and observability features
  # Tracks agent performance, memory usage, and tool execution
  telemetry:
    enabled: true
    provider: "opentelemetry"  # opentelemetry, datadog, newrelic, none
    endpoint: "http://localhost:4317"
    sample_rate: 1.0  # 0.0 to 1.0, controls what % of traces to capture

# -----------------------------------------------------------------------------
# LLM Configuration
# -----------------------------------------------------------------------------
llm:
  # Default model for agent reasoning
  # Supports OpenAI, Anthropic, Ollama, and OpenRouter models
  model: "gpt-4o-mini"

  # Alternative models for specific use cases
  fast_model: "gpt-4o-mini"  # For quick operations
  smart_model: "gpt-4o"      # For complex reasoning

  # Sampling temperature (0.0 = deterministic, 1.0 = creative)
  temperature: 0.7

  # Maximum tokens in response
  max_tokens: 4096

  # API Keys (prefer environment variables in production)
  # These can also be set via OPENAI_API_KEY, ANTHROPIC_API_KEY env vars
  openai_api_key: null  # Set via OPENAI_API_KEY environment variable
  anthropic_api_key: null  # Set via ANTHROPIC_API_KEY environment variable

  # Ollama configuration for local models
  ollama:
    base_url: "http://localhost:11434"
    enabled: false

  # OpenRouter configuration for unified model access
  openrouter:
    enabled: false
    api_key: null  # Set via OPENROUTER_API_KEY environment variable
    base_url: "https://openrouter.ai/api/v1"

  # Resilience configuration
  resilience:
    # Maximum retry attempts for failed LLM calls
    max_retries: 3

    # Initial backoff delay in seconds (exponential backoff)
    initial_backoff: 1.0

    # Maximum backoff delay in seconds
    max_backoff: 60.0

    # Request timeout in seconds
    timeout: 120.0

    # Enable automatic fallback to alternative models
    enable_fallback: true

    # Fallback model to use on primary failure
    fallback_model: "gpt-4o-mini"

# -----------------------------------------------------------------------------
# Memory Configuration
# -----------------------------------------------------------------------------
memory:
  # Context window settings
  context:
    # Maximum tokens in context window
    # Should be less than model's actual limit to allow response space
    max_tokens: 8192

    # Reserved tokens for system prompt and tools
    reserved_tokens: 2048

    # Token budget allocation strategy: knapsack, greedy, priority
    budget_strategy: "knapsack"

    # Token counting method: tiktoken, approximate, llm
    token_counter: "tiktoken"

  # Priming configuration (loading context at session start)
  priming:
    # Enable memory priming
    enabled: true

    # Number of top entities to load from graph
    top_entities: 50

    # Number of recent insights to include
    max_insights: 50

    # Number of recent conversations to summarize
    recent_turns: 10

    # Use PageRank for entity importance
    use_pagerank: true

    # Priming prompt template
    prompt_template: |
      You are continuing a conversation with access to previous context.

      Key entities: {entities}
      Recent insights: {insights}
      Conversation summary: {summary}

  # Memory lifecycle settings
  lifecycle:
    # Enable automatic decay of old memories
    enable_decay: true

    # Decay algorithm: exponential, linear, stepwise
    decay_algorithm: "exponential"

    # Decay rate (memories lose importance over time)
    decay_rate: 0.1

    # Enable memory consolidation (merge similar memories)
    enable_consolidation: true

    # Consolidation threshold (similarity score 0.0-1.0)
    consolidation_threshold: 0.85

    # Enable automatic pruning of low-value memories
    enable_pruning: true

    # Pruning threshold (importance score 0.0-1.0)
    pruning_threshold: 0.2

    # Maximum age for episodic memories (days)
    max_episodic_age: 30

    # Maximum age for semantic memories (days)
    max_semantic_age: 90

  # Vector store configuration
  vector:
    # Vector store provider: chroma, faiss, pinecone, weaviate
    provider: "chroma"

    # Collection name for vector storage
    collection_name: "friday_memory"

    # Persist directory for ChromaDB
    persist_directory: "./data/chroma"

    # Embedding model
    embedding_model: "text-embedding-3-small"

    # Embedding dimensions (model-specific)
    embedding_dimensions: 1536

    # Distance metric: cosine, euclidean, dot
    distance_metric: "cosine"

    # Number of results to return in queries
    top_k: 5

    # Minimum similarity score for results (0.0-1.0)
    min_similarity: 0.7

    # Enable hybrid search (semantic + keyword)
    enable_hybrid: false

    # Enable reranking for better results
    enable_reranking: false

  # Graph store configuration
  graph:
    # Graph store provider: networkx, neo4j, elementx
    provider: "networkx"

    # Persist path for NetworkX graphs
    persist_path: "./data/graph.json"

    # Neo4j connection (if using Neo4j provider)
    neo4j:
      uri: "bolt://localhost:7687"
      username: "neo4j"
      password: null  # Set via NEO4J_PASSWORD environment variable

    # Hebbian learning settings
    hebbian:
      # Enable Hebbian learning (strengthen frequently accessed paths)
      enabled: true

      # Learning rate for weight updates
      learning_rate: 0.1

      # Decay rate for unused connections
      decay_rate: 0.05

      # Minimum hit count to prevent pruning
      min_hit_count: 3

    # Entity resolution settings
    entity_resolution:
      # Enable automatic entity merging
      enabled: true

      # Fuzzy matching threshold (0.0-1.0)
      fuzzy_threshold: 0.85

      # Matching algorithm: levenshtein, jaro_winkler, soundex
      matching_algorithm: "jaro_winkler"

  # Episodic store configuration (conversation history)
  episodic:
    # Episodic store provider: json, sqlite, postgres
    provider: "sqlite"

    # Database path for SQLite
    db_path: "./data/transcript.db"

    # PostgreSQL connection (if using postgres provider)
    postgres:
      host: "localhost"
      port: 5432
      database: "friday_memory"
      username: "friday"
      password: null  # Set via POSTGRES_PASSWORD environment variable

    # Maximum turns to keep in active memory
    max_active_turns: 50

    # Enable automatic turn consolidation
    enable_consolidation: true

    # Consolidation interval (process every N turns)
    consolidation_interval: 10

# -----------------------------------------------------------------------------
# Extraction Configuration
# -----------------------------------------------------------------------------
extraction:
  # Enable automatic memory extraction from conversations
  enabled: true

  # Extraction LLM (can differ from main agent LLM)
  llm:
    model: "gpt-4o-mini"
    temperature: 0.3
    max_tokens: 2048

  # Extraction trigger settings
  trigger:
    # Trigger extraction every N turns
    interval: 5

    # Also trigger on explicit signals (store_fact, recall_memory, etc.)
    on_explicit_signal: true

    # Trigger on session end
    on_session_end: true

  # Entity extraction settings
  entities:
    # Minimum confidence to create entity (0.0-1.0)
    min_confidence: 0.7

    # Allowed entity types
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

    # Enable coreference resolution (link pronouns to entities)
    enable_coreference: true

  # Relationship extraction settings
  relationships:
    # Minimum confidence to create relationship (0.0-1.0)
    min_confidence: 0.6

    # Allowed relationship verbs
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

    # Enable bidirectional relationships
    bidirectional: false

  # Insight extraction settings
  insights:
    # Enable insight extraction (high-level observations)
    enabled: true

    # Minimum importance score (0.0-1.0)
    min_importance: 0.8

    # Insight categories
    categories:
      - preference
      - goal
      - constraint
      - pattern
      - decision
      - learning

  # Extraction prompts
  prompts:
    entity_extraction: |
      Extract entities from the following conversation turns.
      Focus on named entities that are explicitly mentioned.

      Return entities as JSON with: name, type, confidence, description.

    relationship_extraction: |
      Extract relationships between entities from the conversation.
      Focus on explicit connections stated in the conversation.

      Return relationships as JSON with: subject, verb, object, confidence.

    insight_extraction: |
      Extract high-level insights and observations from the conversation.
      Focus on user preferences, goals, constraints, and patterns.

      Return insights as JSON with: content, category, importance.

# -----------------------------------------------------------------------------
# Tool Configuration
# -----------------------------------------------------------------------------
tools:
  # Tool selection strategy: all, selective, dynamic
  selection_strategy: "selective"

  # Enable dynamic tool selection (agent chooses at runtime)
  enable_dynamic_selection: true

  # Tool allowlist (only these tools are available)
  # Empty list = all tools available
  allowlist: []

  # Tool blocklist (these tools are never available)
  blocklist: []

  # Category-based tool filtering
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

  # Security settings
  security:
    # Enable filesystem sandboxing
    enable_sandbox: true

    # Allowed paths for filesystem operations
    allowed_paths:
      - "."
      - "./data"
      - "./output"

    # Blocked paths (absolute deny)
    blocked_paths:
      - "/etc"
      - "/System"
      - "/Windows"
      - "~/.ssh"
      - "~/.aws"

    # Enable shell command sandboxing
    enable_shell_sandbox: true

    # Allowed shell commands
    allowed_commands:
      - git
      - ls
      - cat
      - grep
      - find
      - python
      - node
      - npm

    # Blocked shell commands
    blocked_commands:
      - rm -rf
      - dd
      - mkfs
      - fdisk
      - chmod 777

  # Tool-specific configurations
  filesystem:
    # Maximum file size to read (bytes)
    max_file_size: 10485760  # 10MB

    # Default encoding for text files
    default_encoding: "utf-8"

    # Enable automatic binary detection
    detect_binary: true

  web:
    # HTTP request timeout (seconds)
    timeout: 30

    # Maximum response size (bytes)
    max_response_size: 10485760  # 10MB

    # User agent string
    user_agent: "Friday-Agent/0.1.0"

    # Enable SSL verification
    verify_ssl: true

    # Follow redirects
    follow_redirects: true

    # Maximum redirects to follow
    max_redirects: 5

  code_execution:
    # Enable code execution tools
    enabled: true

    # Execution environment: subprocess, docker, kubernetes
    environment: "subprocess"

    # Timeout for code execution (seconds)
    timeout: 60

    # Maximum output size (bytes)
    max_output_size: 1048576  # 1MB

    # Allowed languages
    allowed_languages:
      - python
      - javascript
      - bash

# -----------------------------------------------------------------------------
# Agent Configuration
# -----------------------------------------------------------------------------
agent:
  # Default agent profile
  default_profile: "copilot"

  # Agent profiles directory
  profiles_dir: "./agents"

  # CopilotAgent settings
  copilot:
    # Maximum Re-Act loop iterations
    max_iterations: 10

    # Enable streaming responses
    enable_streaming: false

    # Tool autonomy level: manual, semi_auto, auto
    tool_autonomy: "semi_auto"

  # AutonomousAgent settings
  autonomous:
    # Maximum task tree depth
    max_depth: 5

    # Maximum parallel tasks
    max_parallel: 3

    # Task timeout (seconds)
    task_timeout: 300

    # Enable task checkpointing
    enable_checkpointing: true

# -----------------------------------------------------------------------------
# Workflow Configuration
# -----------------------------------------------------------------------------
workflow:
  # Workflow definitions directory
  workflows_dir: "./workflows"

  # Workflow engine settings
  engine:
    # Maximum workflow execution time (seconds)
    max_execution_time: 3600

    # Enable workflow persistence
    enable_persistence: true

    # Persistence directory
    persistence_dir: "./data/workflows"

    # Checkpoint interval (seconds)
    checkpoint_interval: 60

  # Workflow orchestration
  orchestration:
    # Orchestration strategy: sequential, parallel, dynamic
    strategy: "dynamic"

    # Maximum agents in workflow
    max_agents: 10

    # Enable agent communication
    enable_agent_communication: true

# -----------------------------------------------------------------------------
# Transcript Configuration
# -----------------------------------------------------------------------------
transcript:
  # Enable transcript recording
  enabled: true

  # Transcript storage directory
  storage_dir: "./data/transcripts"

  # Recording settings
  recording:
    # Record user messages
    record_user: true

    # Record agent messages
    record_agent: true

    # Record tool executions
    record_tools: true

    # Record internal reasoning (thoughts)
    record_reasoning: true

    # Record context assembly details
    record_context: false

    # Record token usage statistics
    record_tokens: true

  # Export settings
  export:
    # Default export format: json, markdown, html, txt
    default_format: "markdown"

    # Include metadata in exports
    include_metadata: true

    # Include timestamps
    include_timestamps: true

    # Pretty-print JSON exports
    pretty_json: true

  # Retention settings
  retention:
    # Maximum age for transcripts (days, 0 = never delete)
    max_age: 90

    # Enable automatic cleanup
    auto_cleanup: true

    # Cleanup interval (days)
    cleanup_interval: 7

# -----------------------------------------------------------------------------
# MCP (Model Context Protocol) Configuration
# -----------------------------------------------------------------------------
mcp:
  # Enable MCP server
  enabled: false

  # MCP server settings
  server:
    # Server host
    host: "localhost"

    # Server port
    port: 8765

    # Transport protocol: sse, websocket
    transport: "sse"

    # Enable authentication
    require_auth: false

    # API key for authentication
    api_key: null  # Set via MCP_API_KEY environment variable

  # MCP client settings
  client:
    # Enable MCP client (connect to external MCP servers)
    enabled: false

    # List of MCP servers to connect to
    servers: []
      # - name: "example_server"
      #   url: "http://localhost:8765"
      #   api_key: null

# -----------------------------------------------------------------------------
# Security Configuration
# -----------------------------------------------------------------------------
security:
  # Enable security features
  enabled: true

  # Secrets management
  secrets:
    # Secrets provider: environment, vault, aws_secrets
    provider: "environment"

    # Vault configuration (if using vault provider)
    vault:
      url: "http://localhost:8200"
      token: null  # Set via VAULT_TOKEN environment variable

    # AWS Secrets Manager (if using aws_secrets provider)
    aws_secrets:
      region: "us-east-1"

  # Input validation
  validation:
    # Enable input sanitization
    enable_sanitization: true

    # Maximum input length (characters)
    max_input_length: 100000

    # Block potentially malicious patterns
    block_patterns:
      - ".*rm -rf.*"
      - ".*DROP TABLE.*"
      - ".*DELETE FROM.*"

  # Rate limiting
  rate_limiting:
    # Enable rate limiting
    enabled: false

    # Maximum requests per minute
    max_requests_per_minute: 60

    # Maximum tokens per minute
    max_tokens_per_minute: 100000

# -----------------------------------------------------------------------------
# Performance Configuration
# -----------------------------------------------------------------------------
performance:
  # Caching settings
  caching:
    # Enable response caching
    enabled: true

    # Cache provider: memory, redis, memcached
    provider: "memory"

    # Cache TTL (seconds)
    ttl: 3600

    # Maximum cache size (MB)
    max_size: 500

    # Redis configuration (if using redis provider)
    redis:
      host: "localhost"
      port: 6379
      db: 0
      password: null  # Set via REDIS_PASSWORD environment variable

  # Concurrency settings
  concurrency:
    # Maximum concurrent LLM requests
    max_llm_concurrency: 5

    # Maximum concurrent tool executions
    max_tool_concurrency: 10

    # Enable request queuing
    enable_queuing: true

    # Maximum queue size
    max_queue_size: 100

  # Resource limits
  limits:
    # Maximum memory usage (MB, 0 = unlimited)
    max_memory: 4096

    # Maximum CPU usage (%, 0 = unlimited)
    max_cpu: 80

    # Enable resource monitoring
    enable_monitoring: true

# -----------------------------------------------------------------------------
# Development & Debugging
# -----------------------------------------------------------------------------
development:
  # Enable debug mode
  debug: false

  # Enable verbose logging
  verbose: false

  # Enable profiling
  enable_profiling: false

  # Profiling output directory
  profiling_dir: "./data/profiling"

  # Enable request/response logging
  log_requests: false

  # Enable stack traces in errors
  include_stack_traces: true

  # Mock services for testing
  mock:
    # Mock LLM responses
    mock_llm: false

    # Mock tool executions
    mock_tools: false

    # Mock data directory
    mock_data_dir: "./tests/fixtures"
```

### A.2 Environment Variable Mappings

Friday supports environment variable overrides for all configuration settings. Variables use the `FRIDAY_` prefix followed by the configuration path with double underscores (`__`) for nesting.

**Naming Convention:**
```
FRIDAY_<SECTION>__<SUBSECTION>__<SETTING>
```

**Common Environment Variables:**

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

**Usage Examples:**

```bash
# Basic LLM configuration
export OPENAI_API_KEY="sk-proj-xxx"
export FRIDAY_LLM__MODEL="gpt-4o"
export FRIDAY_LLM__TEMPERATURE="0.5"

# Memory configuration
export FRIDAY_MEMORY__CONTEXT__MAX_TOKENS="16384"
export FRIDAY_MEMORY__PRIMING__ENABLED="true"
export FRIDAY_MEMORY__PRIMING__TOP_ENTITIES="100"

# Security configuration
export FRIDAY_TOOLS__SECURITY__ENABLE_SANDBOX="true"

# Production environment
export APP_ENV="production"
export LOG_LEVEL="WARNING"
export FRIDAY_LLM__RESILIENCE__MAX_RETRIES="5"
```

**Type Conversion Rules:**

- **Booleans**: `"true"`, `"false"`, `"1"`, `"0"`, `"yes"`, `"no"` (case-insensitive)
- **Numbers**: Parsed as int or float based on presence of decimal point
- **Lists**: Comma-separated values: `"item1,item2,item3"`
- **None/Null**: `"null"`, `"none"`, empty string (case-insensitive)

### A.3 Configuration Schema Reference

**FridayBaseSettings Class**

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

**Configuration Loading Priority:**

1. **Default values** in Pydantic models
2. **`.env` file** in project root
3. **Environment variables** (highest priority)
4. **Runtime overrides** via code

**Configuration Validation:**

All configuration uses Pydantic for automatic validation and type checking. Invalid configurations will raise validation errors at startup with detailed error messages.

---

## Appendix B: Tool Catalog

### B.1 Complete Tool List

Friday includes 50+ built-in tools organized into categories. Each tool implements the `ToolDefinition` protocol and can be used individually or composed into complex workflows.

#### B.1.1 Filesystem Tools (13 tools)

**File Reading:**
- `file_read` - Read file contents with encoding detection
- `file_read_lines` - Read specific line ranges from files
- `file_info` - Get file metadata (size, modified time, permissions)
- `file_grep` - Search file contents with regex patterns

**File Writing:**
- `file_write` - Write content to file (create or overwrite)
- `file_append` - Append content to end of file
- `file_insert` - Insert content at specific line number
- `file_replace` - Replace text using search/replace patterns
- `file_patch` - Apply unified diff patches

**File Operations:**
- `file_copy` - Copy files or directories
- `file_move` - Move or rename files
- `file_delete` - Delete files or directories
- `file_chmod` - Change file permissions

**Directory Operations:**
- `directory_list` - List directory contents with filtering
- `directory_tree` - Generate tree view of directory structure
- `directory_create` - Create directories (with parents)
- `file_search` - Search for files by name pattern

**Specialized Readers:**
- PDF reader - Extract text from PDF files
- DOCX reader - Read Microsoft Word documents
- XLSX reader - Read Excel spreadsheets
- CSV reader - Parse CSV files with dialect detection

#### B.1.2 Shell Tools (6 tools)

**Command Execution:**
- `shell_execute` - Execute shell commands with sandboxing
- `shell_script` - Execute multi-line shell scripts

**System Information:**
- `process_list` - List running processes
- `process_kill` - Terminate processes by PID
- `environment_get` - Read environment variables
- `system_info` - Get system information (OS, CPU, memory)

#### B.1.3 Web Tools (11 tools)

**Web Fetching:**
- `web_fetch` - Fetch and parse web pages
- `web_screenshot` - Capture screenshots of web pages
- `web_extract_links` - Extract all links from HTML
- `web_extract_text` - Extract clean text from HTML

**HTTP Operations:**
- `http_get` - HTTP GET request with headers
- `http_post` - HTTP POST with JSON/form data
- `http_put` - HTTP PUT request
- `http_delete` - HTTP DELETE request
- `http_download` - Download files from URLs
- `http_upload` - Upload files via HTTP

**Search:**
- `web_search` - Web search using DuckDuckGo API

#### B.1.4 Git Tools (4 tools)

**Branch Operations:**
- `git_branch_list` - List all branches
- `git_branch_create` - Create new branch
- `git_branch_switch` - Switch to different branch
- `git_branch_delete` - Delete branch

**Status & History:**
- `git_status` - Get repository status
- `git_log` - View commit history
- `git_diff` - Show uncommitted changes

#### B.1.5 Code Tools (5 tools)

**Code Analysis:**
- `code_parse_ast` - Parse code into Abstract Syntax Tree
- `code_extract_symbols` - Extract functions, classes, variables

**Code Formatting:**
- `code_format` - Format code using Black/Prettier
- `code_lint` - Lint code using Ruff/ESLint

**Code Execution:**
- `python_execute` - Execute Python code in sandbox
- `code_generation` - Generate code using LLM and tools

#### B.1.6 Data Tools (5 tools)

**JSON:**
- `json_parse` - Parse JSON strings
- `json_format` - Pretty-print JSON
- `json_query` - Query JSON using JSONPath

**CSV:**
- `csv_parse` - Parse CSV strings
- `csv_to_json` - Convert CSV to JSON

**XML:**
- `xml_parse` - Parse XML documents
- `xml_to_json` - Convert XML to JSON

**YAML:**
- `yaml_parse` - Parse YAML documents
- `yaml_to_json` - Convert YAML to JSON

**TOML:**
- `toml_parse` - Parse TOML files
- `toml_to_json` - Convert TOML to JSON

#### B.1.7 Text Tools (4 tools)

**Text Transformation:**
- `text_transform` - Case conversion, trimming, padding
- `text_convert` - Encoding conversions
- `text_search` - Search text with regex
- `text_split` - Split text by delimiters

#### B.1.8 Encoding Tools (6 tools)

**Encoding/Decoding:**
- `base64_encode` - Encode to Base64
- `base64_decode` - Decode from Base64
- `url_encode` - URL-encode strings
- `url_decode` - URL-decode strings

**Hashing & IDs:**
- `hash_compute` - Compute SHA256/MD5 hashes
- `uuid_generate` - Generate UUIDs (v4)

#### B.1.9 Math & Utility Tools (5 tools)

**Calculations:**
- `calculator` - Evaluate mathematical expressions
- `unit_convert` - Convert units (length, weight, temperature)

**Date/Time:**
- `date_parse` - Parse date strings
- `date_format` - Format dates
- `get_current_datetime` - Get current date and time

#### B.1.10 Memory Tools (6 tools)

**Memory Inspection:**
- `memory_stats` - Get memory system statistics
- `graph_inspection` - Inspect graph store contents
- `vector_inspection` - Inspect vector store contents

**Memory Maintenance:**
- `memory_maintenance` - Run maintenance operations
- `memory_reset` - Clear memory stores
- `lifecycle` - Trigger memory lifecycle operations

#### B.1.11 Archive Tools (3 tools)

**Archive Operations:**
- `archive_create` - Create ZIP/TAR archives
- `archive_extract` - Extract archive contents
- `archive_list` - List archive contents

#### B.1.12 Integration Tools (3 tools)

**External Integrations:**
- `webhook` - Send webhook notifications
- `database_query` - Execute SQL queries
- `email_send` - Send emails

### B.2 Tool Quick Reference Table

| Tool Name | Category | Description | Key Parameters |
|-----------|----------|-------------|----------------|
| `file_read` | filesystem | Read file contents | `path`, `encoding` |
| `file_write` | filesystem | Write content to file | `path`, `content` |
| `file_append` | filesystem | Append to file | `path`, `content` |
| `file_copy` | filesystem | Copy files | `source`, `destination` |
| `file_move` | filesystem | Move/rename files | `source`, `destination` |
| `file_delete` | filesystem | Delete files | `path` |
| `directory_list` | filesystem | List directory | `path`, `pattern` |
| `directory_tree` | filesystem | Tree view | `path`, `max_depth` |
| `directory_create` | filesystem | Create directory | `path` |
| `file_search` | filesystem | Search for files | `pattern`, `path` |
| `file_grep` | filesystem | Search file contents | `path`, `pattern` |
| `shell_execute` | shell | Execute shell command | `command`, `args` |
| `shell_script` | shell | Execute shell script | `script`, `shell` |
| `process_list` | shell | List processes | `filter` |
| `process_kill` | shell | Kill process | `pid`, `signal` |
| `environment_get` | shell | Get environment variable | `name` |
| `system_info` | shell | System information | none |
| `web_fetch` | web | Fetch web page | `url`, `method` |
| `web_screenshot` | web | Screenshot web page | `url`, `output_path` |
| `web_extract_links` | web | Extract links | `url` or `html` |
| `web_extract_text` | web | Extract text | `url` or `html` |
| `http_get` | web | HTTP GET | `url`, `headers` |
| `http_post` | web | HTTP POST | `url`, `data`, `headers` |
| `http_put` | web | HTTP PUT | `url`, `data` |
| `http_delete` | web | HTTP DELETE | `url` |
| `http_download` | web | Download file | `url`, `output_path` |
| `http_upload` | web | Upload file | `url`, `file_path` |
| `web_search` | web | Web search | `query`, `max_results` |
| `git_status` | git | Repository status | `repo_path` |
| `git_log` | git | Commit history | `repo_path`, `max_count` |
| `git_diff` | git | Show changes | `repo_path`, `staged` |
| `git_branch_list` | git | List branches | `repo_path` |
| `code_parse_ast` | code | Parse AST | `code`, `language` |
| `code_extract_symbols` | code | Extract symbols | `code`, `language` |
| `code_format` | code | Format code | `code`, `language` |
| `code_lint` | code | Lint code | `code`, `language` |
| `python_execute` | code | Execute Python | `code`, `timeout` |
| `code_generation` | code | Generate code | `task`, `tools` |
| `json_parse` | data | Parse JSON | `json_string` |
| `json_format` | data | Pretty-print JSON | `data`, `indent` |
| `json_query` | data | Query JSON | `data`, `query` |
| `csv_parse` | data | Parse CSV | `csv_string` |
| `csv_to_json` | data | CSV to JSON | `csv_string` |
| `xml_parse` | data | Parse XML | `xml_string` |
| `xml_to_json` | data | XML to JSON | `xml_string` |
| `yaml_parse` | data | Parse YAML | `yaml_string` |
| `yaml_to_json` | data | YAML to JSON | `yaml_string` |
| `text_transform` | text | Transform text | `text`, `operation` |
| `text_search` | text | Search with regex | `text`, `pattern` |
| `text_split` | text | Split text | `text`, `delimiter` |
| `base64_encode` | encoding | Encode Base64 | `data` |
| `base64_decode` | encoding | Decode Base64 | `data` |
| `url_encode` | encoding | URL encode | `text` |
| `url_decode` | encoding | URL decode | `text` |
| `hash_compute` | encoding | Compute hash | `data`, `algorithm` |
| `uuid_generate` | encoding | Generate UUID | none |
| `calculator` | utility | Calculate | `expression` |
| `unit_convert` | utility | Convert units | `value`, `from_unit`, `to_unit` |
| `date_parse` | utility | Parse date | `date_string`, `format` |
| `date_format` | utility | Format date | `date`, `format` |
| `get_current_datetime` | utility | Current time | `format`, `timezone` |
| `memory_stats` | memory | Memory statistics | none |
| `graph_inspection` | memory | Inspect graph | `node_id` |
| `vector_inspection` | memory | Inspect vectors | `query` |
| `archive_create` | archive | Create archive | `files`, `output`, `format` |
| `archive_extract` | archive | Extract archive | `archive_path`, `output_dir` |
| `archive_list` | archive | List contents | `archive_path` |

### B.3 Tool Categories

**Category Descriptions:**

| Category | Tool Count | Purpose | Security Level |
|----------|------------|---------|----------------|
| `filesystem` | 17 | File and directory operations | Medium - Sandboxed |
| `shell` | 6 | Command execution and system info | High - Restricted |
| `web` | 11 | HTTP requests and web scraping | Low - Safe |
| `git` | 4 | Version control operations | Medium - Safe |
| `code` | 5 | Code analysis and execution | High - Sandboxed |
| `data` | 5 | Data format parsing/conversion | Low - Safe |
| `text` | 4 | Text manipulation | Low - Safe |
| `encoding` | 6 | Encoding/decoding operations | Low - Safe |
| `utility` | 5 | General utilities | Low - Safe |
| `memory` | 6 | Memory system operations | Low - Safe |
| `archive` | 3 | Archive management | Medium - Safe |
| `integration` | 3 | External service integrations | Medium - Varies |

**Security Levels Explained:**

- **Low**: Safe operations with no side effects (read-only, pure functions)
- **Medium**: Operations with limited side effects (file I/O, network requests)
- **High**: Operations requiring sandboxing (code execution, shell commands)

**Tool Selection Strategies:**

1. **All Tools**: Provide entire tool catalog to agent (best for general-purpose agents)
2. **Category-Based**: Select tools by category (e.g., only `filesystem` + `web`)
3. **Allowlist**: Explicitly list allowed tools (most restrictive)
4. **Blocklist**: Exclude specific tools (allow all except dangerous ones)
5. **Dynamic**: Let agent request tools at runtime based on task

---

## Appendix C: API Reference

### C.1 Core Agent Classes

#### CopilotAgent

**Location:** `packages/friday-agent/src/friday_agent/copilot.py`

Interactive agent using the Re-Act pattern for human-in-the-loop workflows.

**Class Definition:**

```python
class CopilotAgent(AgentBase):
    """
    Interactive agent using the Re-Act pattern.

    Executes a Think → Tool → Observe loop until the LLM
    produces a final response without tool calls.
    """

    MAX_ITERATIONS: int = 10

    def __init__(
        self,
        profile: AgentProfile,
        memory: MemoryController,
        context_engine: ContextAssembler,
        llm: LLMClient,
        tool_registry: ToolRegistry,
        telemetry: TelemetryProvider | None = None,
    ):
        """
        Initialize CopilotAgent.

        Args:
            profile: Agent profile with system prompt and settings
            memory: Memory controller for storage operations
            context_engine: Context assembly for prompt building
            llm: LLM client for inference
            tool_registry: Registry of available tools
            telemetry: Optional telemetry provider
        """
```

**Key Methods:**

```python
async def run(self, input_signal: str) -> str:
    """
    Execute the Re-Act loop for a user query.

    Args:
        input_signal: The user's message/query

    Returns:
        The agent's final response string

    Raises:
        RuntimeError: If max iterations exceeded
    """

async def initialize_session(self) -> None:
    """
    Initialize a new session with memory priming.

    Creates session state and loads relevant context
    from memory stores.
    """

async def archive_turn(self) -> None:
    """
    Archive the current turn to memory.

    Stores the interaction in episodic memory and
    triggers extraction if configured.
    """
```

**Usage Example:**

```python
from friday_agent import CopilotAgent, AgentProfile
from friday_memory import MemoryController
from friday_llm import LiteLLMService
from friday_tools import DefaultToolRegistry

# Initialize components
profile = AgentProfile(
    name="assistant",
    role="AI Assistant",
    goal="Help users with tasks",
    temperature=0.7,
)

memory = MemoryController(
    vector_adapter=chroma_adapter,
    graph_adapter=networkx_adapter,
    episodic_adapter=sqlite_adapter,
)

llm = LiteLLMService(model="gpt-4o-mini")
registry = DefaultToolRegistry()

# Create agent
agent = CopilotAgent(
    profile=profile,
    memory=memory,
    context_engine=context_assembler,
    llm=llm,
    tool_registry=registry,
)

# Use agent
await agent.initialize_session()
response = await agent.run("What files are in the current directory?")
print(response)
```

#### AutonomousAgent

**Location:** `packages/friday-agent/src/friday_agent/autonomous.py`

Goal-oriented agent that breaks down complex tasks into subtasks and executes them autonomously.

**Class Definition:**

```python
class AutonomousAgent(AgentBase):
    """
    Autonomous agent with task decomposition and planning.

    Breaks complex goals into subtasks, executes them,
    and tracks progress toward completion.
    """

    MAX_DEPTH: int = 5
    MAX_PARALLEL: int = 3

    def __init__(
        self,
        profile: AgentProfile,
        memory: MemoryController,
        context_engine: ContextAssembler,
        llm: LLMClient,
        tool_registry: ToolRegistry,
        telemetry: TelemetryProvider | None = None,
    ):
        """Initialize AutonomousAgent."""
```

**Key Methods:**

```python
async def run(self, goal: str) -> dict[str, Any]:
    """
    Execute autonomous task decomposition and execution.

    Args:
        goal: High-level goal to achieve

    Returns:
        Dictionary with result, task_tree, and metadata
    """

async def decompose_task(self, task: str, depth: int = 0) -> list[dict]:
    """
    Break task into subtasks using LLM.

    Args:
        task: Task to decompose
        depth: Current decomposition depth

    Returns:
        List of subtask dictionaries
    """

async def execute_task(self, task: dict) -> dict:
    """
    Execute a single task.

    Args:
        task: Task dictionary with type and parameters

    Returns:
        Result dictionary with output and status
    """
```

#### AgentProfile

**Location:** `packages/friday-agent/src/friday_agent/profile.py`

Configuration profile defining agent behavior and capabilities.

**Class Definition:**

```python
@dataclass
class AgentProfile:
    """
    Agent profile defining behavior and capabilities.

    Attributes:
        name: Agent identifier
        role: Agent's role description
        goal: Agent's primary objective
        system_prompt: Base system prompt template
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens in response
        tool_autonomy: Tool usage level (manual, semi_auto, auto)
        enabled_tools: List of allowed tool names
        context_strategy: Context assembly strategy
        metadata: Additional profile metadata
    """

    name: str
    role: str
    goal: str
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    temperature: float = 0.7
    max_tokens: int = 4096
    tool_autonomy: str = "semi_auto"
    enabled_tools: list[str] | None = None
    context_strategy: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)
```

**Key Methods:**

```python
def render_system_prompt(self, **kwargs) -> str:
    """
    Render system prompt with variable substitution.

    Args:
        **kwargs: Variables to substitute in template

    Returns:
        Rendered system prompt string
    """

@classmethod
def from_yaml(cls, yaml_path: str) -> "AgentProfile":
    """
    Load profile from YAML file.

    Args:
        yaml_path: Path to YAML profile file

    Returns:
        AgentProfile instance
    """

def to_yaml(self, yaml_path: str) -> None:
    """
    Save profile to YAML file.

    Args:
        yaml_path: Path to write YAML file
    """
```

### C.2 Memory System API

#### MemoryController

**Location:** `packages/friday-memory/src/friday_memory/controller.py`

Central coordinator for all memory operations.

**Class Definition:**

```python
class MemoryController:
    """
    Central memory controller coordinating all storage adapters.

    Manages vector, graph, and episodic stores with unified
    interface for agents.
    """

    def __init__(
        self,
        vector_adapter: VectorStoreAdapter,
        graph_adapter: GraphStoreAdapter,
        episodic_adapter: EpisodicStoreAdapter,
        embedding_model: EmbeddingModel | None = None,
    ):
        """
        Initialize memory controller.

        Args:
            vector_adapter: Vector storage implementation
            graph_adapter: Graph storage implementation
            episodic_adapter: Episodic storage implementation
            embedding_model: Optional custom embedding model
        """
```

**Key Methods:**

```python
async def add_fact(
    self,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> bool:
    """
    Store a fact in vector memory.

    Args:
        content: Fact text content
        metadata: Optional metadata (source, timestamp, etc.)

    Returns:
        True if successful
    """

async def recall_facts(
    self,
    query: str,
    n_results: int = 5,
    filters: dict[str, Any] | None = None,
) -> list[dict]:
    """
    Retrieve relevant facts using semantic search.

    Args:
        query: Search query
        n_results: Maximum results to return
        filters: Optional metadata filters

    Returns:
        List of fact dictionaries with content and metadata
    """

async def add_entity(
    self,
    entity_id: str,
    entity_type: str,
    properties: dict[str, Any],
) -> bool:
    """
    Add entity to knowledge graph.

    Args:
        entity_id: Unique entity identifier
        entity_type: Entity type (person, organization, etc.)
        properties: Entity properties dictionary

    Returns:
        True if successful
    """

async def add_relationship(
    self,
    subject_id: str,
    verb: str,
    object_id: str,
    properties: dict[str, Any] | None = None,
) -> bool:
    """
    Add relationship between entities.

    Args:
        subject_id: Subject entity ID
        verb: Relationship verb (works_at, owns, etc.)
        object_id: Object entity ID
        properties: Optional relationship properties

    Returns:
        True if successful
    """

async def get_entity_context(
    self,
    entity_id: str,
    depth: int = 1,
) -> dict:
    """
    Get entity and its neighborhood context.

    Args:
        entity_id: Entity to retrieve
        depth: How many hops to traverse

    Returns:
        Dictionary with entity and neighbor information
    """

async def add_turn(
    self,
    session_id: str,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> bool:
    """
    Add interaction turn to episodic memory.

    Args:
        session_id: Session identifier
        role: Message role (user, assistant, system, tool)
        content: Message content
        metadata: Optional turn metadata

    Returns:
        True if successful
    """

async def get_recent_turns(
    self,
    session_id: str,
    limit: int = 10,
) -> list[dict]:
    """
    Get recent conversation turns.

    Args:
        session_id: Session identifier
        limit: Maximum turns to retrieve

    Returns:
        List of turn dictionaries
    """
```

#### ContextAssembler

**Location:** `packages/friday-memory/src/friday_memory/context_assembler.py`

Assembles context from memory for prompt construction.

**Class Definition:**

```python
class ContextAssembler:
    """
    Assembles context from memory stores for LLM prompts.

    Implements token budgeting, relevance ranking, and
    lost-in-the-middle mitigation.
    """

    def __init__(
        self,
        memory: MemoryController,
        max_tokens: int = 8192,
        budget_strategy: str = "knapsack",
    ):
        """
        Initialize context assembler.

        Args:
            memory: Memory controller instance
            max_tokens: Maximum tokens in assembled context
            budget_strategy: Budgeting algorithm (knapsack, greedy)
        """
```

**Key Methods:**

```python
async def assemble_context(
    self,
    query: str,
    state: SessionState,
    budget_limit: int | None = None,
) -> ContextPayload:
    """
    Assemble context from all memory sources.

    Args:
        query: User query
        state: Current session state
        budget_limit: Override default token budget

    Returns:
        ContextPayload with assembled context chunks
    """

def calculate_budget_limit(
    self,
    system_prompt: str,
    tool_definitions: list[dict] | None = None,
) -> int:
    """
    Calculate dynamic token budget.

    Args:
        system_prompt: Agent's system prompt
        tool_definitions: Optional tool schemas

    Returns:
        Available tokens for context
    """

async def format_prompt(
    self,
    system_prompt: str,
    payload: ContextPayload,
) -> list[dict]:
    """
    Format context into LLM message format.

    Args:
        system_prompt: System prompt string
        payload: Context payload from assemble_context

    Returns:
        List of message dictionaries
    """
```

### C.3 Tool System API

#### DefaultToolRegistry

**Location:** `packages/friday-tools/src/friday_tools/registry.py`

Registry for managing tool collections.

**Class Definition:**

```python
class DefaultToolRegistry:
    """
    Default implementation of ToolRegistry protocol.

    Manages tool registration, retrieval, and schema access.
    """

    def __init__(self):
        """Initialize empty registry."""
```

**Key Methods:**

```python
def register(self, tool: ToolDefinition) -> None:
    """
    Register a tool.

    Args:
        tool: Tool implementing ToolDefinition protocol

    Raises:
        ValueError: If tool already registered
    """

def get(self, name: str) -> ToolDefinition | None:
    """
    Get tool by name.

    Args:
        name: Tool identifier

    Returns:
        Tool instance or None
    """

def list_tools(self) -> list[ToolDefinition]:
    """List all registered tools."""

def get_schemas(self, format: str = "plain") -> list[dict]:
    """
    Get schemas for all tools.

    Args:
        format: "plain" or "openai"

    Returns:
        List of tool schemas
    """

def get_tools_by_category(self, category: str) -> list[ToolDefinition]:
    """
    Get tools in specific category.

    Args:
        category: Category name

    Returns:
        List of matching tools
    """

def tool(
    self,
    name: str | None = None,
    description: str | None = None,
    category: str = "uncategorized",
    tags: list[str] | None = None,
) -> Callable:
    """
    Decorator to register function as tool.

    Example:
        @registry.tool(name="my_tool", category="utility")
        async def my_tool(input: str) -> str:
            return f"Processed: {input}"
    """
```

#### BaseTool

**Location:** `packages/friday-tools/src/friday_tools/definition.py`

Base class for implementing tools.

**Class Definition:**

```python
class BaseTool(ABC):
    """
    Base class for Friday tools.

    Implements ToolDefinition protocol with common functionality.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description."""

    @property
    @abstractmethod
    def parameters_schema(self) -> dict[str, Any]:
        """JSON Schema for parameters."""

    @property
    def category(self) -> str:
        """Tool category."""
        return "uncategorized"

    @property
    def tags(self) -> list[str]:
        """Optional tags."""
        return []

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool."""

    def to_schema(self, format: str = "plain") -> dict[str, Any]:
        """Convert to LLM-ready schema."""
```

**Usage Example:**

```python
from friday_tools import BaseTool

class MyCustomTool(BaseTool):
    """Custom tool implementation."""

    @property
    def name(self) -> str:
        return "my_custom_tool"

    @property
    def description(self) -> str:
        return "Performs custom operation on input"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Input string to process",
                },
            },
            "required": ["input"],
        }

    @property
    def category(self) -> str:
        return "utility"

    async def execute(self, input: str) -> str:
        """Execute custom logic."""
        return f"Processed: {input.upper()}"

# Register tool
registry = DefaultToolRegistry()
registry.register(MyCustomTool())
```

### C.4 LLM Client API

#### LiteLLMService

**Location:** `packages/friday-llm/src/friday_llm/client.py`

Provider-agnostic LLM client using LiteLLM.

**Class Definition:**

```python
class LiteLLMService:
    """
    LLM client using LiteLLM for multi-provider support.

    Supports OpenAI, Anthropic, Ollama, and 100+ other providers
    through unified interface.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        base_url: str | None = None,
        resilience_config: ResilienceConfig | None = None,
    ):
        """
        Initialize LiteLLM service.

        Args:
            model: Model identifier (e.g., "gpt-4o", "claude-3-5-sonnet")
            api_key: API key for provider
            base_url: Optional base URL override
            resilience_config: Retry and fallback configuration
        """
```

**Key Methods:**

```python
async def chat_completion(
    self,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    response_model: type[BaseModel] | None = None,
    temperature: float = 0.7,
) -> ChatCompletionResponse:
    """
    Unified chat completion with tool calling support.

    Args:
        messages: List of message dictionaries
        tools: Optional tool schemas for function calling
        response_model: Optional Pydantic model for structured output
        temperature: Sampling temperature

    Returns:
        ChatCompletionResponse with content and/or tool_calls

    Raises:
        LLMError: If call fails after retries
    """

async def embed_text(self, text: str) -> list[float]:
    """
    Generate embedding vector for text.

    Args:
        text: Text to embed

    Returns:
        Embedding vector
    """

async def count_tokens(
    self,
    text: str,
    model: str | None = None,
) -> int:
    """
    Count tokens in text.

    Args:
        text: Text to count
        model: Optional model override

    Returns:
        Token count
    """
```

**Usage Example:**

```python
from friday_llm import LiteLLMService, ResilienceConfig

# Initialize with resilience
resilience = ResilienceConfig(
    max_retries=5,
    enable_fallback=True,
    fallback_model="gpt-4o-mini",
)

llm = LiteLLMService(
    model="gpt-4o",
    resilience_config=resilience,
)

# Chat completion
response = await llm.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
    temperature=0.5,
)

print(response.content)  # "The capital of France is Paris."

# With tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                },
                "required": ["location"],
            },
        },
    },
]

response = await llm.chat_completion(
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
)

if response.has_tool_calls:
    for tool_call in response.tool_calls:
        print(f"Tool: {tool_call.name}")
        print(f"Args: {tool_call.arguments}")
```

---

## Appendix D: Protocol Specifications

### D.1 ToolDefinition Protocol

**Location:** `packages/friday-core/src/friday_core/interfaces/tools.py`

Defines the contract for all Friday tools.

```python
@runtime_checkable
class ToolDefinition(Protocol):
    """
    Abstract representation of a tool capability.

    This protocol defines what a "tool" IS in Friday - the fundamental
    unit of agent capability. All tools must implement this interface.
    """

    @property
    def name(self) -> str:
        """
        Unique tool identifier.

        Must be unique across all tools in a registry.
        Convention: lowercase_with_underscores
        Examples: "file_read", "web_search", "code_format"
        """
        ...

    @property
    def description(self) -> str:
        """
        Human-readable description for the LLM.

        Should clearly explain:
        - What the tool does
        - When to use it
        - What it returns

        The LLM uses this to decide when to invoke the tool.
        """
        ...

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """
        JSON Schema defining the tool's parameters.

        Must be valid JSON Schema Draft 7 or later.
        Should include:
        - Type information for each parameter
        - Descriptions for each parameter
        - Required fields
        - Constraints (min/max, patterns, enums)

        Example:
            {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding",
                        "default": "utf-8"
                    }
                },
                "required": ["path"]
            }
        """
        ...

    @property
    def category(self) -> str:
        """
        Tool category for grouping and filtering.

        Standard categories:
        - "filesystem": File and directory operations
        - "shell": Command execution
        - "web": HTTP requests, web scraping
        - "git": Version control operations
        - "code": Code analysis, execution, generation
        - "data": Data processing, transformation
        - "text": Text manipulation, search
        - "utility": General utilities (datetime, etc.)
        - "uncategorized": Default for tools without explicit category

        Returns:
            Category string, defaults to "uncategorized" if not set.
        """
        ...

    @property
    def tags(self) -> list[str]:
        """
        Optional tags for fine-grained filtering.

        Tags provide additional metadata for tool discovery and filtering
        beyond the primary category.

        Examples:
        - ["read-only", "safe"]
        - ["async", "requires-auth"]
        - ["idempotent", "expensive"]

        Returns:
            List of tag strings, empty list if no tags.
        """
        ...

    async def execute(self, **kwargs: Any) -> str:
        """
        Execute the tool with given arguments.

        This is the actual implementation of the tool's functionality.
        Must be async to support I/O operations.

        Args:
            **kwargs: Tool-specific parameters matching the schema.
                     Parameter names and types must match parameters_schema.

        Returns:
            String result of the tool execution.
            Return value is fed back to the LLM as tool output.

        Raises:
            Can raise tool-specific exceptions for error conditions.
            Exceptions should be descriptive for debugging.
        """
        ...

    def to_schema(self, format: str = "plain") -> dict[str, Any]:
        """
        Convert tool to JSON schema format for LLM function calling.

        Args:
            format: Output format - "plain" or "openai".

                   "plain" format:
                   {
                       "name": "tool_name",
                       "description": "Tool description",
                       "parameters": { ... JSON Schema ... }
                   }

                   "openai" format:
                   {
                       "type": "function",
                       "function": {
                           "name": "tool_name",
                           "description": "Tool description",
                           "parameters": { ... JSON Schema ... }
                       }
                   }

        Returns:
            Dictionary suitable for LLM function calling.
        """
        ...
```

**Implementation Requirements:**

1. **Name Uniqueness**: Tool names must be unique within a registry
2. **Description Clarity**: Descriptions should be clear enough for LLM understanding
3. **Schema Validity**: Parameter schemas must be valid JSON Schema
4. **Async Execution**: Execute method must be async
5. **String Returns**: Execute must return string (for LLM consumption)

### D.2 LLMClient Protocol

**Location:** `packages/friday-core/src/friday_core/interfaces/llm.py`

Defines the contract for LLM inference clients.

```python
class LLMClient(Protocol):
    """
    Abstract interface for LLM inference.

    Implementations should handle:
    - Provider-specific API formatting
    - Retry logic for transient errors
    - Tool call parsing from responses
    - Telemetry/observability hooks
    """

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        response_model: type[BaseModel] | None = None,
        temperature: float = 0.7,
    ) -> ChatCompletionResponse:
        """
        Unified chat completion with optional tool calling.

        This is the primary interface for LLM inference in Friday.
        Implementations must normalize provider-specific formats
        into Friday's unified response structure.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
                     Supported roles: 'system', 'user', 'assistant', 'tool'

                     Example:
                     [
                         {"role": "system", "content": "You are a helpful assistant."},
                         {"role": "user", "content": "Hello!"},
                         {"role": "assistant", "content": "Hi! How can I help?"},
                     ]

            tools: Optional list of tool JSON schemas in OpenAI format.
                   Each schema should have 'type': 'function' and 'function' keys.

                   Example:
                   [
                       {
                           "type": "function",
                           "function": {
                               "name": "get_weather",
                               "description": "Get weather for location",
                               "parameters": {
                                   "type": "object",
                                   "properties": {
                                       "location": {"type": "string"}
                                   },
                                   "required": ["location"]
                               }
                           }
                       }
                   ]

            response_model: Optional Pydantic model for structured output.
                           If provided, response.content will be parsed into this model.
                           Enables instructor-style structured extraction.

            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
                        Controls randomness in response generation.

        Returns:
            ChatCompletionResponse with content and/or tool_calls.

            - If LLM responds with text: response.content contains text
            - If LLM calls tools: response.tool_calls contains list of ToolCall objects
            - Both can be present in some providers

            Use response.has_tool_calls to check if tools were requested.

        Raises:
            LLMError: If the API call fails after retries
            ValidationError: If response doesn't match response_model
        """
        ...
```

**Response Structure:**

```python
@dataclass
class ChatCompletionResponse:
    """
    Structured response from chat completion.

    Provides a unified format regardless of the underlying LLM provider.
    """

    content: str | None = None
    """Response text content (None if only tool calls)"""

    tool_calls: list[ToolCall] = field(default_factory=list)
    """List of tool calls requested by the LLM"""

    model: str = ""
    """Model that generated the response"""

    usage: dict[str, int] = field(default_factory=dict)
    """Token usage statistics"""

    @property
    def has_tool_calls(self) -> bool:
        """Check if the response contains tool calls."""
        return len(self.tool_calls) > 0


@dataclass
class ToolCall:
    """Represents a tool call requested by the LLM."""

    id: str
    """Unique identifier for this tool call"""

    name: str
    """Tool name to invoke"""

    arguments: dict[str, Any]
    """Arguments to pass to the tool"""
```

### D.3 Storage Adapter Protocols

#### VectorStoreAdapter

**Location:** `packages/friday-core/src/friday_core/interfaces/memory.py`

Protocol for semantic search storage.

```python
class VectorStoreAdapter(ABC):
    """
    Protocol for semantic search storage.

    Handles embedding and retrieval of document chunks for
    similarity-based search. Implementations might use:
    ChromaDB, FAISS, Pinecone, Weaviate, Qdrant, etc.
    """

    @abstractmethod
    async def add_documents(
        self,
        texts: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> bool:
        """
        Embeds and stores raw text using the internal embedding model.

        The adapter is responsible for:
        1. Generating embeddings for each text
        2. Storing embeddings with metadata
        3. Ensuring IDs are unique

        Args:
            texts: List of text chunks to embed and store
            metadatas: List of metadata dicts (must include provenance)
                      Recommended metadata fields:
                      - source_type: "conversation", "document", "extraction"
                      - timestamp: ISO 8601 timestamp
                      - session_id: Session identifier (if applicable)
                      - confidence: Confidence score 0.0-1.0 (if applicable)
            ids: List of unique document IDs
                Convention: Use UUIDs or "{source_type}_{timestamp}_{hash}"

        Returns:
            True if successful, False otherwise

        Raises:
            May raise storage-specific exceptions
        """
        pass

    @abstractmethod
    async def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
        rerank: bool = False,
        hybrid: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Performs semantic retrieval on stored documents.

        Args:
            query_text: The search query (will be embedded)
            n_results: Maximum number of results to return
            where: Optional metadata filter
                  Examples:
                  - {'source_type': 'document'}
                  - {'timestamp': {'$gte': '2024-01-01'}}
                  - {'session_id': 'session_123'}
            rerank: If True, apply reranking to improve result quality
                   Reranking uses cross-encoder models for better accuracy
            hybrid: If True, combine semantic and keyword search
                   Useful for queries with specific terms

        Returns:
            List of result dicts containing:
            - text: The document text
            - metadata: Document metadata
            - score: Similarity score (higher = more relevant)
            - id: Document ID

            Results are sorted by relevance (highest score first)

        Raises:
            May raise storage-specific exceptions
        """
        pass

    @abstractmethod
    async def delete(self, ids: list[str]) -> bool:
        """
        Removes documents by ID.

        Args:
            ids: List of document IDs to delete

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete_where(self, where: dict[str, Any]) -> int:
        """
        Removes documents matching a metadata filter.

        Essential for time-based pruning and lifecycle management.

        Args:
            where: Metadata filter to match documents for deletion
                  Examples:
                  - {'timestamp': {'$lt': '2024-01-01'}}  # Before date
                  - {'source_type': 'temporary'}  # By source
                  - {'confidence': {'$lt': 0.5}}  # Low confidence

        Returns:
            Number of documents deleted

        Raises:
            May raise storage-specific exceptions
        """
        pass
```

#### GraphStoreAdapter

**Location:** `packages/friday-core/src/friday_core/interfaces/memory.py`

Protocol for relationship graph storage.

```python
class GraphStoreAdapter(ABC):
    """
    Protocol for relationship graph storage.

    Handles entities, concepts, and their relationships for
    structured knowledge representation. Implementations might use:
    NetworkX, Neo4j, ElementX, TigerGraph, etc.
    """

    # --- CRUD Operations ---

    @abstractmethod
    async def add_node(self, node: "GraphNode") -> bool:
        """
        Adds a node to the graph.

        The node must include provenance metadata (enforced by Pydantic).

        Args:
            node: The GraphNode to add
                 Required fields:
                 - id: Unique node identifier
                 - label: Node type (person, organization, concept, etc.)
                 - properties: Dict of node properties
                 - metadata: Provenance and tracking info

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If node with same ID already exists
        """
        pass

    @abstractmethod
    async def add_edge(self, edge: "GraphEdge") -> bool:
        """
        Adds an edge (relationship) between two nodes.

        Both source and target nodes must already exist.

        Args:
            edge: The GraphEdge to add
                 Required fields:
                 - source_id: ID of source node
                 - target_id: ID of target node
                 - relationship: Relationship verb
                 - properties: Dict of edge properties
                 - metadata: Provenance and tracking info

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If source or target node doesn't exist
        """
        pass

    @abstractmethod
    async def remove_node(self, node_id: str) -> bool:
        """
        Removes a node and all its connected edges.

        This is a cascading delete - all relationships
        involving this node are also removed.

        Args:
            node_id: The ID of the node to remove

        Returns:
            True if successful, False otherwise
        """
        pass

    # --- Traversal Operations ---

    @abstractmethod
    async def get_neighbors(
        self,
        node_id: str,
        depth: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Gets connected nodes within the specified depth.

        Args:
            node_id: The starting node ID
            depth: How many hops to traverse (default 1 = immediate neighbors)
                  depth=1: Direct neighbors
                  depth=2: Neighbors and neighbors-of-neighbors
                  depth=N: Up to N hops away

        Returns:
            List of neighbor node dicts with relationship info:
            - node: The neighbor node data
            - relationship: The connecting relationship
            - distance: Number of hops from source
            - path: List of node IDs in the path
        """
        pass

    @abstractmethod
    async def find_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 5,
    ) -> list[str]:
        """
        Finds a path between two nodes.

        Uses breadth-first search to find shortest path.

        Args:
            start_id: Starting node ID
            end_id: Target node ID
            max_depth: Maximum path length to search

        Returns:
            List of node IDs representing the path, or empty list if no path
            Example: ["person_1", "org_1", "person_2"]
        """
        pass

    # --- Intelligence Operations ---

    @abstractmethod
    async def merge_nodes(self, primary_id: str, secondary_id: str) -> bool:
        """
        Entity Resolution: Merges two nodes representing the same entity.

        Algorithm:
        1. Identify all edges where secondary is source/target
        2. Create copies of those edges pointing to/from primary
        3. Copy unique properties from secondary to primary (primary wins conflicts)
        4. Delete secondary node
        5. Emit 'graph_node_merged' telemetry event

        Used when the Agent realizes 'Bob' and 'Robert' are the same person.

        Args:
            primary_id: The node to keep
            secondary_id: The node to merge into primary and delete

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If either node doesn't exist
        """
        pass

    @abstractmethod
    async def fuzzy_search(
        self,
        query: str,
        threshold: float = 0.8,
    ) -> list["GraphNode"]:
        """
        Finds nodes with similar names/labels.

        Used to prevent duplicate entity creation (e.g., 'Bob' vs 'Robert').

        Args:
            query: The search string
            threshold: Minimum similarity score (0.0 to 1.0)
                      0.8 = 80% similar

        Returns:
            List of matching GraphNodes sorted by similarity

        Note:
            Implementations typically use:
            - Levenshtein distance
            - Jaro-Winkler similarity
            - Soundex matching
        """
        pass

    @abstractmethod
    async def rank_nodes(self, algorithm: str = "pagerank") -> list[dict[str, Any]]:
        """
        Ranks nodes by importance using graph algorithms.

        Args:
            algorithm: The ranking algorithm to use
                      Supported algorithms:
                      - "pagerank": Google's PageRank algorithm
                      - "degree": Simple degree centrality
                      - "betweenness": Betweenness centrality
                      - "closeness": Closeness centrality

        Returns:
            List of dicts with node_id and rank score, sorted by rank:
            [
                {"node_id": "person_1", "rank": 0.95},
                {"node_id": "org_1", "rank": 0.87},
                ...
            ]
        """
        pass
```

#### EpisodicStoreAdapter

**Location:** `packages/friday-core/src/friday_core/interfaces/memory.py`

Protocol for short-term conversation history storage.

```python
class EpisodicStoreAdapter(ABC):
    """
    Protocol for short-term conversation history storage.

    Handles the "Thread" of interactions for a session. Critical for
    the Context Engineering extraction cycle. Implementations might use:
    JSON files, SQLite, PostgreSQL, Redis, etc.
    """

    @abstractmethod
    async def add_turn(self, session_id: str, turn: "InteractionTurn") -> bool:
        """
        Logs a single user/assistant interaction.

        Args:
            session_id: Unique session identifier
            turn: The interaction turn to store
                 Required fields:
                 - turn_id: Unique turn identifier
                 - role: "user", "assistant", "system", or "tool"
                 - content: Message content
                 - timestamp: When the turn occurred
                 - tool_calls: Optional list of tool invocations
                 - metadata: Additional tracking info

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_turns(
        self,
        session_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list["InteractionTurn"]:
        """
        Retrieves chronological history for context injection.

        Args:
            session_id: Unique session identifier
            limit: Maximum number of turns to retrieve
            offset: Number of turns to skip (for pagination)

        Returns:
            List of interaction turns, ordered chronologically (oldest first)
        """
        pass

    @abstractmethod
    async def get_unconsolidated_turns(
        self,
        session_id: str,
    ) -> list["InteractionTurn"]:
        """
        Retrieves turns that have NOT yet been processed by the Memory Consolidator.

        Used by the 'Extraction' cycle to identify new information
        that needs to be analyzed and potentially stored in long-term memory.

        Args:
            session_id: Unique session identifier

        Returns:
            List of unprocessed interaction turns
        """
        pass

    @abstractmethod
    async def mark_consolidated(self, turn_ids: list[str]) -> bool:
        """
        Marks specific turns as 'processed' so they aren't re-extracted.

        Called after the Memory Consolidator has processed the turns
        and extracted relevant facts/entities.

        Args:
            turn_ids: List of turn IDs to mark as consolidated

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def rewind_history(self, session_id: str, target_turn_id: str) -> bool:
        """
        Hard Reset: Deletes all interaction turns *after* the target_turn_id.

        Used to recover from 'death spirals' or logic errors. Provides
        Google ADK-style "time travel" capability.

        Args:
            session_id: Unique session identifier
            target_turn_id: The turn ID to rewind to (this turn is kept)

        Returns:
            True if successful, False otherwise
        """
        pass
```

### D.4 ToolRegistry Protocol

**Location:** `packages/friday-core/src/friday_core/interfaces/tools.py`

Protocol for managing tool collections.

```python
@runtime_checkable
class ToolRegistry(Protocol):
    """
    Registry for managing tool collections.

    Provides unified interface for tool registration, retrieval, and
    schema access. Supports both object-based and callable-based access
    patterns for backward compatibility.
    """

    def register(self, tool: ToolDefinition) -> None:
        """
        Register a tool with the registry.

        Args:
            tool: Tool to register (must implement ToolDefinition).

        Raises:
            ValueError: If tool with same name already registered.
        """
        ...

    def get(self, name: str) -> ToolDefinition | None:
        """
        Get a tool by name.

        Args:
            name: The tool's unique identifier.

        Returns:
            The tool if found, None otherwise.
        """
        ...

    def get_callable(self, name: str) -> Callable[..., Any]:
        """
        Get the executable callable for a tool.

        Args:
            name: The tool's unique identifier.

        Returns:
            Callable that can be invoked with tool arguments.

        Raises:
            KeyError: If tool not found.
        """
        ...

    def list_tools(self) -> list[ToolDefinition]:
        """
        List all registered tools.

        Returns:
            List of all registered ToolDefinition instances.
        """
        ...

    def list_names(self) -> list[str]:
        """
        List all registered tool names.

        Returns:
            List of tool name strings.
        """
        ...

    def get_schemas(self, format: str = "plain") -> list[dict[str, Any]]:
        """
        Get JSON schemas for all registered tools.

        Args:
            format: Output format - "plain" or "openai".

        Returns:
            List of tool schemas suitable for LLM function calling.
        """
        ...

    def get_schema(self, name: str, format: str = "plain") -> dict[str, Any] | None:
        """
        Get JSON schema for a specific tool.

        Args:
            name: The tool name.
            format: Output format - "plain" or "openai".

        Returns:
            Tool schema if found, None otherwise.
        """
        ...

    def get_tools_by_category(self, category: str) -> list[ToolDefinition]:
        """
        Get all tools in a specific category.

        Args:
            category: Category to filter by (e.g., "filesystem", "web").

        Returns:
            List of tools in the specified category.
        """
        ...

    def get_tools_by_tags(
        self,
        tags: list[str],
        match_all: bool = False,
    ) -> list[ToolDefinition]:
        """
        Get tools matching specified tags.

        Args:
            tags: List of tags to filter by.
            match_all: If True, tool must have ALL tags. If False, ANY tag matches.

        Returns:
            List of tools matching the tag criteria.
        """
        ...

    def list_categories(self) -> list[str]:
        """
        List all unique categories across registered tools.

        Returns:
            Sorted list of category strings.
        """
        ...
```

---

## Appendix E: Migration Guides

### E.1 Version History

**v0.1.0 - Initial Release (Current)**

*Release Date: January 2026*

Initial public release of Friday Agent Framework.

**Features:**
- CopilotAgent with Re-Act pattern
- AutonomousAgent with task decomposition
- Adaptive memory system (vector, graph, episodic)
- 50+ built-in tools
- LiteLLM integration for multi-provider support
- Protocol-first architecture
- Comprehensive transcript system
- Memory lifecycle management
- Context engineering with token budgeting
- Knapsack optimization for context assembly
- Hebbian learning in graph memory
- MCP (Model Context Protocol) support

**Known Limitations:**
- NetworkX-only graph storage (Neo4j planned for v0.2)
- Limited multi-agent orchestration (enhanced in v0.2)
- No built-in authentication (coming in v0.2)
- Single-user sessions only (multi-user in v0.3)

### E.2 Breaking Changes

Since this is v0.1.0, there are no breaking changes yet. This section will document breaking changes in future releases.

**Future Breaking Change Policy:**

- **Major versions** (1.0, 2.0): May include breaking changes
- **Minor versions** (0.2, 0.3): Avoid breaking changes when possible
- **Patch versions** (0.1.1, 0.1.2): No breaking changes

**Deprecation Process:**

1. Feature marked as deprecated in documentation
2. Deprecation warnings emitted at runtime
3. Deprecated for at least one minor version
4. Removed in next major version

### E.3 Migration Scripts

#### Future: v0.1.x to v0.2.0 (Planned)

**Expected Changes:**

- Enhanced multi-agent orchestration
- Neo4j graph adapter
- Authentication system
- Performance improvements

**Anticipated Migration Path:**

```bash
# Backup existing data
python -m friday.cli backup --output ./backup

# Upgrade Friday
pip install friday-agent-framework --upgrade

# Run migration script
python -m friday.cli migrate --from 0.1 --to 0.2

# Verify migration
python -m friday.cli verify
```

**Configuration Changes (Anticipated):**

```yaml
# v0.1.0 config
agent:
  default_profile: "copilot"

# v0.2.0 config (expected)
agent:
  default_profile: "copilot"
  orchestration:
    enabled: true  # New setting
    max_agents: 10  # New setting
```

Migration scripts will be provided with each release to handle:
- Configuration file updates
- Database schema changes
- Tool signature changes
- Protocol updates

---

## Appendix F: Glossary

### F.1 Core Concepts

**Agent**
: An autonomous software entity that uses LLMs for reasoning, tools for action, and memory for learning. Agents perceive their environment, make decisions, and execute tasks toward goals.

**Intelligence Plane vs Control Plane Architecture**
: Architectural separation where the Intelligence Plane (memory, reasoning, context) handles intelligence and the Control Plane (tools, execution) handles action. Enables independent scaling and clear security boundaries.

**Protocol-First Design**
: Architectural pattern where abstract interfaces (protocols) define contracts before implementation. Enables dependency injection, testing, and provider flexibility.

**Provenance**
: Metadata tracking the origin and history of information. Essential for trust, debugging, and memory lifecycle management. Includes source, timestamp, confidence, and processing history.

**Session State**
: The active context for an ongoing conversation or task. Includes episodic history, working memory, current goals, and transient data. Persisted across interactions but not permanent.

**Tool**
: A discrete capability that agents can invoke to interact with external systems. Tools have names, descriptions, parameter schemas, and execute methods. Friday includes 50+ built-in tools.

**Transcript**
: Complete record of an agent's execution including messages, tool calls, reasoning steps, and metadata. Used for debugging, auditing, analysis, and improvement.

### F.2 Memory Systems

**Adaptive Memory**
: Memory system that learns from usage patterns and adjusts importance scores dynamically. Combines Hebbian learning (strengthening frequently accessed paths) with decay (forgetting unused information).

**Associative Memory**
: Memory retrieval based on relationships between concepts rather than exact matches. Implemented via graph traversal - accessing one entity activates related entities.

**Context Assembly**
: Process of selecting and formatting relevant information from memory stores to fit within the LLM's context window. Uses token budgeting, relevance ranking, and optimization algorithms.

**Decay**
: Process of reducing importance scores for unused memories over time. Prevents memory stores from growing unbounded and ensures only relevant information persists.

**Episodic Memory**
: Short-term memory of specific events in chronological order. In Friday, stores conversation turns with full context including messages, tool calls, and timestamps. Analogous to human episodic memory.

**Extraction**
: Process of analyzing conversation turns to identify entities, relationships, and insights for storage in long-term memory. Runs periodically or on explicit signals. Uses specialized LLM prompts.

**Graph Memory (Associative Memory)**
: Structured memory storing entities as nodes and relationships as edges. Enables traversal, path finding, entity resolution, and importance ranking. Implements Hebbian learning via hit counts.

**Hebbian Learning**
: "Neurons that fire together wire together" - strengthening connections based on co-activation. In Friday, increases hit_count on graph edges when traversed together, making frequently used paths stronger.

**Knapsack Optimization**
: Algorithm for context assembly that maximizes value (relevance) subject to capacity constraints (token budget). Ensures most relevant information fits in context window.

**Lifecycle Management**
: Automated maintenance of memory systems including decay, consolidation, pruning, and staging. Keeps memory healthy without manual intervention.

**Lost-in-the-Middle Mitigation**
: Technique addressing LLMs' tendency to ignore information in the middle of long contexts. Friday uses tail injection (placing critical info at the end) and strategic ordering.

**Memory Consolidation**
: Process of merging similar or redundant memories to reduce storage and improve retrieval. Identifies duplicates, resolves entities, and combines related information.

**Priming**
: Loading relevant context at session start to establish baseline knowledge. Friday's priming loads top entities, recent insights, and conversation summaries before first user message.

**Pruning**
: Removal of low-value memories based on importance scores, age, and usage patterns. Prevents memory bloat and maintains quality.

**Semantic Memory (Vector Memory)**
: Long-term memory of facts and concepts without temporal context. In Friday, stores document chunks as embeddings for semantic search. Analogous to human semantic memory.

**Staging**
: Temporary holding area for uncertain or low-confidence information before committing to long-term memory. Allows validation and refinement before permanent storage.

**Token Budgeting**
: Allocation of available context tokens across different information sources (system prompt, episodic history, facts, entities, tools). Ensures critical information fits within limits.

**Vector Memory (Semantic Memory)**
: Storage of embeddings (vector representations) of text for similarity-based retrieval. Enables semantic search - finding conceptually related information rather than keyword matches.

### F.3 Agent Patterns

**Autonomous Agent**
: Agent pattern that operates independently toward goals, decomposing complex tasks into subtasks and executing them without human intervention. Friday's AutonomousAgent implements this pattern.

**CopilotAgent**
: Interactive agent pattern designed for human-in-the-loop workflows. Assists users by reasoning about tasks, calling tools, and providing responses. Implements Re-Act loop.

**Multi-Agent System**
: Architecture where multiple specialized agents collaborate on complex tasks. Agents have distinct roles, capabilities, and communication patterns. Friday supports workflows with multiple agents.

**Re-Act Pattern**
: Agent loop of Reasoning + Acting: (1) Think about task, (2) Act by calling tools, (3) Observe results, (4) Repeat. Enables agents to iteratively solve problems using available tools.

**Task Decomposition**
: Breaking complex goals into smaller, manageable subtasks. AutonomousAgent uses LLM to recursively decompose tasks until reaching primitive actions (tool calls).

**Tool Autonomy Levels**
: Degrees of agent independence in tool usage:
- **Manual**: Agent suggests tools, human approves
- **Semi-Auto**: Agent uses safe tools automatically, asks for risky ones
- **Auto**: Agent uses all tools autonomously

**Workflow Orchestration**
: Coordination of multiple agents to execute complex processes. Defines agent roles, task assignments, communication patterns, and execution order.

### F.4 Technical Terms

**Abstract Syntax Tree (AST)**
: Tree representation of code structure. Used by code analysis tools to understand and manipulate code programmatically.

**Base64 Encoding**
: Binary-to-text encoding scheme representing binary data in ASCII string format. Used for transmitting binary data over text-based protocols.

**ChromaDB**
: Open-source embedding database optimized for AI applications. Friday's default vector store implementation.

**Context Window**
: Maximum number of tokens an LLM can process in a single request. Includes prompt and response. Modern models range from 4K to 200K+ tokens.

**Embedding**
: Vector (list of numbers) representing the semantic meaning of text. Similar texts have similar embeddings. Used for semantic search in vector stores.

**JSON Schema**
: Standard for describing the structure of JSON data. Used to define tool parameters, validate inputs, and generate documentation.

**LiteLLM**
: Python library providing unified interface to 100+ LLM providers. Friday's LLM client is built on LiteLLM for provider flexibility.

**Model Context Protocol (MCP)**
: Emerging standard for connecting AI models to data sources and tools. Friday implements MCP server and client for integration with MCP-compatible tools.

**NetworkX**
: Python library for graph data structures and algorithms. Friday's default graph store implementation.

**PageRank**
: Algorithm for ranking nodes in a graph based on incoming links. Used to identify important entities in knowledge graphs.

**Pydantic**
: Python library for data validation using type hints. Friday uses Pydantic extensively for configuration, models, and API contracts.

**Resilience**
: System's ability to handle failures gracefully. Friday's LLM client includes retry logic, exponential backoff, fallback models, and timeout handling.

**Sandbox**
: Isolated execution environment with restricted permissions. Friday sandboxes filesystem operations and code execution for security.

**Structured Output**
: LLM response parsed into typed data structures rather than raw text. Enables reliable extraction of entities, relationships, and other structured data.

**Tail Injection**
: Placing critical information at the end of context to mitigate lost-in-the-middle effect. LLMs pay more attention to recent context.

**Telemetry**
: Collection of performance metrics, traces, and logs for observability. Friday supports OpenTelemetry integration for monitoring agent behavior.

**Token**
: Basic unit of text for LLMs. Roughly 3-4 characters or 0.75 words in English. Token counting is essential for context management.

**uv**
: Fast Python package installer and workspace manager. Friday uses uv for dependency management in its monorepo structure.

---

## Conclusion

These appendices provide comprehensive reference material for Friday Agent Framework. Use them as quick references when developing agents, configuring systems, or troubleshooting issues.

**Quick Navigation:**

- **Configuration issues?** → See [Appendix A](#appendix-a-complete-configuration-reference)
- **Looking for a specific tool?** → See [Appendix B](#appendix-b-tool-catalog)
- **Writing code?** → See [Appendix C](#appendix-c-api-reference)
- **Implementing protocols?** → See [Appendix D](#appendix-d-protocol-specifications)
- **Upgrading versions?** → See [Appendix E](#appendix-e-migration-guides)
- **Don't understand a term?** → See [Appendix F](#appendix-f-glossary)

For more detailed information, refer to the main guide sections:
- [Section 1: Executive Summary](01-executive-summary.md)
- [Section 2: Getting Started](02-getting-started.md)
- [Section 3: Core Concepts](03-core-concepts.md)
- [Section 4: Adaptive Memory](04-adaptive-memory.md)
- [Section 5: Tools](05-tools.md)
- [Section 6: Agents](06-agents.md)
- [Section 7: Multi-Agent Systems](07-multi-agent.md)
- [Section 8: Workflows](08-workflows.md)
- [Section 9: CLI Reference](09-cli-reference.md)
- [Section 10: Configuration](10-configuration.md)
- [Section 11: Advanced Topics](11-advanced-topics.md)
- [Section 12: Use Cases](12-use-cases.md)
- [Section 13: Troubleshooting](13-troubleshooting.md)

**Version:** 1.0 | **Framework Version:** v0.1.0 | **Last Updated:** 2026-01-24
