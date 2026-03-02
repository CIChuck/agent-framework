---
title: "Package Structure"
description: "The 16-package monorepo and how dependencies flow between them."
weight: 4
---

Friday is a uv-workspace monorepo where dependencies flow in a single direction from core protocols through memory, LLM, agents, tools, and finally the CLI and applications.

---

## The Eight Packages

Friday is structured as a **monorepo**—multiple packages in a single repository, with clear dependency relationships. This enables independent development, selective installation, and fine-grained versioning.

```text
friday-agent-framework/
├── packages/
│   ├── friday-core/           # Foundation (protocols, config, logging)
│   ├── friday-memory/         # Memory system (3-tier architecture)
│   ├── friday-llm/            # LLM client (provider-agnostic)
│   ├── friday-agent/          # Agent implementations (Re-Act, orchestration)
│   ├── friday-tools/          # Tool catalog (50+ built-in tools)
│   ├── friday-transcript/     # Conversation logging (SQLite)
│   ├── friday-mcp/            # Model Context Protocol integration
│   └── friday-optimization/   # Algorithms (knapsack, token budgeting)
│
├── tests/                     # Integration tests
├── workflows/                 # Example YAML workflows
├── docs/                      # Documentation
└── pyproject.toml             # Workspace configuration
```

---

## Dependency Flow

The dependency graph is **directed and acyclic**—packages only depend on layers below them:

```text
                friday-core
                    │
        ┌───────────┼───────────┐
        │           │           │
   friday-memory  friday-llm  friday-optimization
        │           │
        └─────┬─────┘
              │
        friday-agent
              │
    ┌─────────┼──────────┐
    │         │          │
friday-tools  friday-  friday-
             transcript   mcp
```

**Why this matters:**
- **Independent evolution**: Changes in `friday-tools` don't affect `friday-memory`
- **Selective installation**: Use only what you need (e.g., just `friday-memory` for custom agents)
- **Clear boundaries**: Circular dependencies are impossible by design
- **Modular testing**: Test each package in isolation

---

## Package Details

### friday-core

**Purpose:** Foundation layer with abstract protocols and shared utilities.

**Contents:**
- `interfaces/` — Abstract protocols for all major components
- `config/` — Configuration management (YAML parsing, validation)
- `logging/` — Structured logging setup
- `exceptions/` — Framework-level exceptions

**Who uses it:** All other packages depend on `friday-core`.

**When to use directly:** Building custom Friday-compatible components from scratch.

---

### friday-memory

**Purpose:** Three-tier memory system with lifecycle management.

**Contents:**
- `controller/` — MemoryController (unified facade)
- `stores/` — Vector, graph, episodic store implementations
- `context/` — ContextAssembler, PromptArchitect
- `lifecycle/` — Memory promotion, decay, reactivation
- `extraction/` — Entity and insight extraction
- `maintenance/` — Memory reorganization, pruning

**Dependencies:** `friday-core`, `friday-llm` (for extraction)

**When to use directly:** Building agents with custom memory strategies.

---

### friday-llm

**Purpose:** Provider-agnostic LLM client with resilience patterns.

**Contents:**
- `service/` — LiteLLMService (wraps litellm library)
- `resilience/` — Retry logic, circuit breakers, timeouts
- `embeddings/` — Embedding model abstraction
- `telemetry/` — LLM call instrumentation

**Dependencies:** `friday-core`

**When to use directly:** Using Friday's LLM client in non-Friday projects.

**Supported providers:**

| Provider | Model Examples | Configuration |
|----------|---------------|---------------|
| OpenAI | gpt-4o, gpt-4o-mini | Direct API |
| Anthropic | claude-3.5-sonnet, claude-3-haiku | Direct API |
| Google | gemini-pro, gemini-2.5-flash | Via OpenRouter or direct |
| Ollama | llama3, mistral, qwen | Local API |
| OpenRouter | Any model via openrouter/* prefix | Single API key |
| LM Studio | Any local model | OpenAI-compatible API |

---

### friday-agent

**Purpose:** Agent implementations and orchestration.

**Contents:**
- `copilot.py` — CopilotAgent (Re-Act loop with tools)
- `autonomous.py` — AutonomousAgent (planned)
- `orchestrator.py` — Multi-agent coordination
- `profile.py` — AgentProfile (identity and capabilities)
- `registry.py` — AgentRegistry (discovery and instantiation)
- `loader.py` — AgentLoader (YAML-based configuration)
- `workflows/` — Workflow engine, task graphs

**Dependencies:** `friday-core`, `friday-memory`, `friday-llm`

**When to use directly:** This is the primary package for most users.

---

### friday-tools

**Purpose:** Tool catalog and execution infrastructure.

**Contents:**
- `base.py` — BaseTool abstract class
- `filesystem/` — File operations (read, write, search)
- `shell/` — Command execution (subprocess, scripts)
- `web/` — HTTP requests, scraping, search
- `git/` — Version control operations
- `data/` — Parsing (JSON, YAML, CSV, XML)
- `text/` — Text manipulation (regex, formatting)
- `code/` — Code execution, linting, analysis
- `integrations/` — External APIs (future: Slack, GitHub, etc.)

**Tool categories:**

| Category | Tools | Description |
|----------|-------|-------------|
| **Filesystem** | read_file, write_file, list_directory, search_files | File operations |
| **Shell** | execute_command, run_script | System command execution |
| **Web** | http_request, web_search, scrape_page | HTTP and web operations |
| **Git** | git_status, git_commit, git_diff, git_log | Version control |
| **Data** | parse_json, parse_yaml, csv_operations | Data transformation |
| **Text** | regex_search, text_replace, format_text | Text manipulation |
| **Code** | analyze_code, run_python, lint_code | Code operations |

**Dependencies:** `friday-core`

**When to use directly:** Using Friday tools in non-Friday projects, or building custom tools.

---

### friday-transcript

**Purpose:** Conversation logging with export capabilities.

**Contents:**
- `store.py` — SQLiteTranscriptStore (default implementation)
- `models.py` — Data models (Session, Turn, ToolCall)
- `exporter.py` — Export to JSONL, Markdown, training format

**Export Formats:**

| Format | Exporter | Use Case |
|--------|----------|----------|
| JSONL | `JSONLExporter` | Data processing, backup |
| Markdown | `MarkdownExporter` | Human-readable documentation |
| Training | `JSONLExporter.export_training_data()` | Fine-tuning datasets |

**Dependencies:** `friday-core`

**When to use directly:** Custom transcript storage or analysis.

---

### friday-mcp

**Purpose:** Model Context Protocol client and server implementations.

**Contents:**
- `client.py` — MCP client (consume external MCP servers)
- `server.py` — MCP server (expose Friday resources)
- `transport/` — SSE, stdio transports
- `adapters/` — Friday tool → MCP tool adapter

**Dependencies:** `friday-core`, `friday-tools`

**When to use directly:** Integrating Friday with MCP ecosystem.

---

### friday-optimization

**Purpose:** Optimization algorithms for context engineering.

**Contents:**
- `knapsack.py` — 0/1 knapsack solver for token budgeting
- `scoring.py` — Relevance scoring functions
- `utils.py` — Mathematical utilities

**Dependencies:** `friday-core`

**When to use directly:** Custom context assembly strategies.

---

## Package Management with uv

Friday uses **uv** as its package manager and build tool. uv is a modern, high-performance Python package manager written in Rust.

### Why uv?

- **10-100x faster installation** compared to pip
- **Deterministic dependency resolution** (like Poetry, but faster)
- **Workspace support** for monorepos (critical for Friday's 8-package structure)
- **Compatible with pip** (uses PyPI, respects requirements.txt)
- **Single binary** installation (no bootstrapping issues)

### Performance Benchmarks

Real-world Friday framework installation times:

| Tool | Cold install | Cached install |
|------|-------------|----------------|
| **uv** | 12s | 3s |
| **pip** | 245s | 180s |
| **Poetry** | 89s | 45s |

*Test environment: M2 MacBook Pro, installing all Friday packages + dependencies (~150 packages total)*

**Result:** uv is **20x faster** than pip for cold installs, **7x faster** than Poetry.

### uv Workspace Configuration

Friday's monorepo is configured as a uv workspace via `pyproject.toml`:

```toml
[tool.uv.workspace]
members = [
    "packages/friday-core",
    "packages/friday-memory",
    "packages/friday-llm",
    "packages/friday-agent",
    "packages/friday-tools",
    "packages/friday-transcript",
    "packages/friday-mcp",
    "packages/friday-optimization",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]
```

This enables:
- **Single virtual environment** for all packages (no juggling multiple venvs)
- **Shared dependencies** across packages (install once, use everywhere)
- **Editable installs** (changes in one package immediately visible to others)
- **Unified testing** (run tests across all packages with one command)

### Common uv Commands

```bash
# Install all workspace dependencies (one command for entire Friday framework)
uv sync

# Add a dependency to a specific package
uv add --package friday-memory chromadb

# Run tests across all packages
uv run pytest

# Update dependencies
uv lock --upgrade

# Install from PyPI (pip-compatible)
uv pip install friday-agent
```

---

## Installation Patterns

**Full Stack (Most Common):**

```bash
# Using pip
pip install friday-agent

# Or using uv (10-100x faster)
uv pip install friday-agent
```

Installs all core packages (`friday-core`, `friday-memory`, `friday-llm`, `friday-agent`, `friday-tools`, `friday-transcript`).

**Memory Only:**

```bash
uv pip install friday-memory
```

Installs just the memory system + dependencies (`friday-core`, `friday-llm`). Use case: building custom agents with Friday's memory but your own execution logic.

**Tools Only:**

```bash
uv pip install friday-tools
```

Installs just the tool catalog + dependencies (`friday-core`). Use case: using Friday's tools in a non-Friday project.

**Development Install:**

```bash
# Clone repository
git clone <repo>
cd friday-agent-framework

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# One command installs all packages in editable mode (seconds, not minutes)
uv sync

# Verify installation
uv run python -c "from friday_agent import CopilotAgent; print('Ready')"
```

---

## Practical Implications

**Cost control:** Only install and pay for what you need (e.g., skip `friday-mcp` if not using MCP).

**Risk distribution:** Issues in one package don't affect others (blast radius containment).

**Vendor evaluation:** Each package can use different vendors (ChromaDB for vector, Neo4j for graph).

**Team organization:** Different teams can own different packages.

**Deployment flexibility:** Deploy packages on different infrastructure (memory on high-RAM nodes, tools on CPU-optimized).

**Security boundaries:** Run tools in sandboxed containers while memory stays in trusted environment.

**Update strategy:** Update packages independently (patch `friday-tools` without touching `friday-memory`).

**Learning curve:** Study packages in dependency order (core → memory → llm → agent).

**Debugging:** Package boundaries help isolate issues (memory retrieval vs. tool execution vs. LLM calls).
