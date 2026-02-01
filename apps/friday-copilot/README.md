# Friday Copilot

Full-featured AI assistant with persistent memory, built on the Friday Framework.

## Installation

```bash
# From the monorepo root
uv sync

# Run the assistant
uv run friday-copilot
```

## Features

### Core Capabilities
- **Persistent Memory**: Vector store (ChromaDB), graph store (NetworkX), episodic store
- **Memory Lifecycle**: Automatic promotion, decay, and reactivation of memories
- **Context Engineering**: Token-budgeted context assembly with priming
- **Tool Execution**: Filesystem, utility, and custom tools

### Agent Orchestration (Phase 3)
- Multi-agent switching and delegation
- Agent-specific context and capabilities

### Workflows (Phase 4)
- Declarative workflow definitions
- Human-in-the-loop approval gates

## Commands

| Category | Commands |
|----------|----------|
| **Help** | `/help`, `/exit`, `/quit` |
| **Memory** | `/memory`, `/entities`, `/facts`, `/insights`, `/summaries` |
| **Context** | `/context`, `/prompt`, `/prime`, `/debug` |
| **Transcript** | `/history`, `/sessions`, `/transcript`, `/export` |
| **Lifecycle** | `/reorganize`, `/migrate`, `/lifecycle` |
| **Tools** | `/tools`, `/run-tool`, `/inject-tools`, `/tool-budget` |
| **Orchestration** | `/switch`, `/agents`, `/agent`, `/delegate`, `/status` |
| **Workflows** | `/workflow list`, `/workflow run`, `/workflow status` |

## Configuration

On first run, a default configuration is created at:
- **Linux**: `~/.config/friday/config.yaml`
- **macOS**: `~/Library/Application Support/friday/config.yaml`
- **Windows**: `%APPDATA%/friday/config.yaml`

### Required Environment Variables

```bash
# For OpenRouter
export OPENROUTER_API_KEY="sk-or-v1-..."

# For OpenAI (if using directly)
export OPENAI_API_KEY="sk-..."

# For Anthropic (if using directly)
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Data Storage

Data is stored in platform-specific directories:

| Platform | Location |
|----------|----------|
| **Linux** | `~/.local/share/friday/` |
| **macOS** | `~/Library/Application Support/friday/` |
| **Windows** | `%LOCALAPPDATA%/friday/` |

Contents:
- `transcript.db` - Conversation history
- `graph.json` - Knowledge graph
- `vector/` - ChromaDB embeddings
- `exports/` - Transcript exports

## Development

```bash
# Run tests
pytest apps/friday-copilot/tests/ -v

# Run the app in development
cd apps/friday-copilot
uv run friday-copilot --config path/to/config.yaml
```

## Architecture

Friday Copilot depends on:
- `friday-core` - Protocols, config, logging
- `friday-memory` - Memory stores, context assembly
- `friday-llm` - LiteLLM wrapper for multi-provider LLM calls
- `friday-agent` - Orchestrator, workflows, tool registry
- `friday-tools` - Filesystem, utility tools
- `friday-transcript` - Session transcript storage
- `friday-cli` - Rich terminal interface components
