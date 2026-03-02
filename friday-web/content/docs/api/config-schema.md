---
title: "Configuration Schema"
description: "JSON Schema for Friday's YAML configuration files."
weight: 3
---

The JSON Schema that validates every Friday YAML configuration file, including all required and optional fields, enum values, and nested object definitions.

## Tool Catalog

### Filesystem Tools (17 tools)

**File reading:**

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `file_read` | Read file contents with encoding detection | `path`, `encoding` |
| `file_read_lines` | Read specific line ranges | `path`, `start_line`, `end_line` |
| `file_info` | Get file metadata (size, modified time) | `path` |
| `file_grep` | Search file contents with regex | `path`, `pattern` |

**File writing:**

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `file_write` | Write content (create or overwrite) | `path`, `content` |
| `file_append` | Append content to end of file | `path`, `content` |
| `file_insert` | Insert content at a specific line | `path`, `line`, `content` |
| `file_replace` | Replace text using search/replace | `path`, `old_text`, `new_text` |
| `file_patch` | Apply unified diff patches | `path`, `patch` |

**File operations:**

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `file_copy` | Copy files or directories | `source`, `destination` |
| `file_move` | Move or rename files | `source`, `destination` |
| `file_delete` | Delete files or directories | `path` |
| `directory_list` | List directory contents | `path`, `pattern` |
| `directory_tree` | Generate tree view | `path`, `max_depth` |
| `directory_create` | Create directories with parents | `path` |
| `file_search` | Search for files by name pattern | `pattern`, `path` |

### Shell Tools (6 tools)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `shell_execute` | Execute shell commands with sandboxing | `command`, `args` |
| `shell_script` | Execute multi-line shell scripts | `script`, `shell` |
| `process_list` | List running processes | `filter` |
| `process_kill` | Terminate processes by PID | `pid`, `signal` |
| `environment_get` | Read environment variables | `name` |
| `system_info` | Get system information (OS, CPU, RAM) | none |

### Web Tools (11 tools)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `web_fetch` | Fetch and parse web pages | `url`, `method` |
| `web_screenshot` | Capture screenshots of web pages | `url`, `output_path` |
| `web_extract_links` | Extract all links from HTML | `url` or `html` |
| `web_extract_text` | Extract clean text from HTML | `url` or `html` |
| `http_get` | HTTP GET request with headers | `url`, `headers` |
| `http_post` | HTTP POST with JSON/form data | `url`, `data`, `headers` |
| `http_put` | HTTP PUT request | `url`, `data` |
| `http_delete` | HTTP DELETE request | `url` |
| `http_download` | Download files from URLs | `url`, `output_path` |
| `http_upload` | Upload files via HTTP | `url`, `file_path` |
| `web_search` | Web search via DuckDuckGo API | `query`, `max_results` |

### Git Tools (4 tools)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `git_status` | Get repository status | `repo_path` |
| `git_log` | View commit history | `repo_path`, `max_count` |
| `git_diff` | Show uncommitted changes | `repo_path`, `staged` |
| `git_branch_list` | List all branches | `repo_path` |

### Code Tools (5 tools)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `code_parse_ast` | Parse code into AST | `code`, `language` |
| `code_extract_symbols` | Extract functions/classes/variables | `code`, `language` |
| `code_format` | Format code (Black/Prettier) | `code`, `language` |
| `code_lint` | Lint code (Ruff/ESLint) | `code`, `language` |
| `python_execute` | Execute Python code in sandbox | `code`, `timeout` |

### Data Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `json_parse` | Parse JSON strings | `json_string` |
| `json_format` | Pretty-print JSON | `data`, `indent` |
| `json_query` | Query JSON with JSONPath | `data`, `query` |
| `csv_parse` | Parse CSV strings | `csv_string` |
| `csv_to_json` | Convert CSV to JSON | `csv_string` |
| `xml_parse` | Parse XML documents | `xml_string` |
| `xml_to_json` | Convert XML to JSON | `xml_string` |
| `yaml_parse` | Parse YAML documents | `yaml_string` |
| `yaml_to_json` | Convert YAML to JSON | `yaml_string` |

### Utility Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `base64_encode` | Encode to Base64 | `data` |
| `base64_decode` | Decode from Base64 | `data` |
| `url_encode` | URL-encode a string | `text` |
| `url_decode` | URL-decode a string | `text` |
| `hash_compute` | Compute SHA256/MD5 hash | `data`, `algorithm` |
| `uuid_generate` | Generate UUID v4 | none |
| `calculator` | Evaluate mathematical expressions | `expression` |
| `unit_convert` | Convert units | `value`, `from_unit`, `to_unit` |
| `date_parse` | Parse date strings | `date_string`, `format` |
| `date_format` | Format date values | `date`, `format` |
| `get_current_datetime` | Get current date and time | `format`, `timezone` |

### Memory Tools (6 tools)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `memory_stats` | Get memory system statistics | none |
| `graph_inspection` | Inspect graph store contents | `node_id` |
| `vector_inspection` | Inspect vector store contents | `query` |
| `memory_maintenance` | Run maintenance operations | none |
| `memory_reset` | Clear memory stores | none |
| `lifecycle` | Trigger lifecycle operations | `operation` |

---

## Configuration Schema Reference

### FridayBaseSettings

**Location:** `packages/friday-core/src/friday_core/config.py`

The root Pydantic settings class inherited by all packages.

```python
class FridayBaseSettings(BaseSettings):
    """Global settings inherited by all packages."""

    APP_ENV: str = "development"   # development | production | testing
    LOG_LEVEL: str = "INFO"        # DEBUG | INFO | WARNING | ERROR | CRITICAL
    DEFAULT_MODEL: str = "gpt-4-turbo"
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
```

### Configuration Loading Priority

Settings are applied in this order (later overrides earlier):

1. Default values in Pydantic model definitions
2. `.env` file in the project root
3. Environment variables (highest priority at startup)
4. Runtime overrides via code

### Environment Variable Naming

All Friday configuration keys can be set via environment variables using the `FRIDAY_` prefix and double-underscore (`__`) nesting notation:

```
FRIDAY_<SECTION>__<SUBSECTION>__<SETTING>
```

**Common environment variables:**

| Environment Variable | Config Path | Example |
|---------------------|-------------|---------|
| `OPENAI_API_KEY` | `llm.openai_api_key` | `sk-proj-...` |
| `ANTHROPIC_API_KEY` | `llm.anthropic_api_key` | `sk-ant-...` |
| `OLLAMA_BASE_URL` | `llm.ollama.base_url` | `http://localhost:11434` |
| `FRIDAY_LLM__MODEL` | `llm.model` | `gpt-4o` |
| `FRIDAY_LLM__TEMPERATURE` | `llm.temperature` | `0.7` |
| `FRIDAY_LLM__MAX_TOKENS` | `llm.max_tokens` | `4096` |
| `FRIDAY_LLM__RESILIENCE__MAX_RETRIES` | `llm.resilience.max_retries` | `5` |
| `FRIDAY_MEMORY__CONTEXT__MAX_TOKENS` | `memory.context.max_tokens` | `8192` |
| `FRIDAY_MEMORY__PRIMING__ENABLED` | `memory.priming.enabled` | `true` |
| `FRIDAY_MEMORY__PRIMING__TOP_ENTITIES` | `memory.priming.top_entities` | `50` |
| `FRIDAY_MEMORY__VECTOR__PROVIDER` | `memory.vector.provider` | `chroma` |
| `FRIDAY_MEMORY__GRAPH__PROVIDER` | `memory.graph.provider` | `networkx` |
| `FRIDAY_TOOLS__SECURITY__ENABLE_SANDBOX` | `tools.security.enable_sandbox` | `true` |
| `FRIDAY_EXTRACTION__ENABLED` | `extraction.enabled` | `true` |
| `FRIDAY_TRANSCRIPT__ENABLED` | `transcript.enabled` | `true` |
| `NEO4J_PASSWORD` | `memory.graph.neo4j.password` | — |
| `POSTGRES_PASSWORD` | `memory.episodic.postgres.password` | — |
| `REDIS_PASSWORD` | `performance.caching.redis.password` | — |
| `MCP_API_KEY` | `mcp.server.api_key` | — |
| `APP_ENV` | `app.env` | `production` |
| `LOG_LEVEL` | `app.log_level` | `WARNING` |

**Type conversion rules:**
- **Booleans:** `"true"`, `"false"`, `"1"`, `"0"`, `"yes"`, `"no"` (case-insensitive)
- **Numbers:** Parsed as int or float based on decimal point presence
- **Lists:** Comma-separated values: `"item1,item2,item3"`
- **None/Null:** `"null"`, `"none"`, or empty string

### Schema Sections Overview

The complete `config.yaml` is divided into these top-level sections:

| Section | Purpose |
|---------|---------|
| `app` | Environment, log level, telemetry |
| `llm` | Model, API keys, resilience, fallback |
| `memory.context` | Token budget, budget strategy |
| `memory.priming` | Entity loading, insight loading, recency |
| `memory.lifecycle` | Decay, consolidation, pruning |
| `memory.vector` | Vector store provider, collection, HNSW |
| `memory.graph` | Graph store provider, Hebbian learning |
| `memory.episodic` | Conversation history provider |
| `extraction` | Entity/relationship/insight extraction |
| `tools` | Selection strategy, allowlist, blocklist, security |
| `agent` | CopilotAgent and AutonomousAgent settings |
| `workflow` | Workflow engine, orchestration |
| `transcript` | Recording settings, export, retention |
| `mcp` | MCP server and client settings |
| `security` | Secrets, input validation, rate limiting |
| `performance` | Caching, concurrency, resource limits |
| `development` | Debug mode, profiling, mock services |

For the complete annotated `config.yaml` template with every key and default value, see [Full Reference](/docs/configuration/reference/).

## Related Pages

- [Full Reference](/docs/configuration/reference/) — Complete annotated `config.yaml` template
- [Package APIs](/docs/api/packages/) — Public API for each Friday package
- [Protocol Specifications](/docs/api/protocols/) — Abstract interface definitions
