# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Friday Framework is a Python-based agentic framework with a modular monorepo architecture. It follows a "Mind" (intelligence layer) and "Body" (execution layer) design, with a central "Memory Loop" for context retrieval, learning, and decision-making.

**Current Status:** v0.1.0 - Early development phase.

## Build Commands

```bash
# Install/sync all dependencies (uses uv workspaces)
uv sync

# Run all tests
pytest

# Run tests for a specific package
pytest packages/friday-agent/tests_agent/

# Run a single test file
pytest packages/friday-tools/tests_tools/test_protocols.py -v

# Lint and format
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy packages/friday-core/

# Run the main assistant application
uv run friday-copilot

# Run with custom config
uv run friday-copilot --config path/to/config.yaml
```

## Monorepo Structure & Dependency Flow

The project uses `uv` workspaces. Dependencies flow in one direction:

```
friday-core (protocols, config, logging)
    ↓
friday-memory (storage adapters, context engineering)
    ↓
friday-llm (LiteLLM wrapper for multi-provider LLM calls)
    ↓
friday-transcript (persistent conversation storage)
    ↓
friday-agent (CopilotAgent, tool registry, Re-Act loop)
    ↓
friday-tools (filesystem, shell, web, git, code execution)
    ↓
friday-sandbox (isolated code execution)
    ↓
friday-mcp (Model Context Protocol client/server)
    ↓
friday-cli (Rich terminal interface components)
    ↓
friday-copilot (full-featured AI assistant app)
```

| Package | Location | Purpose |
|---------|----------|---------|
| friday-core | `packages/friday-core/` | Abstract protocols in `interfaces/`, config, logging, exceptions |
| friday-memory | `packages/friday-memory/` | MemoryController, storage adapters (vector/graph/episodic), ContextAssembler |
| friday-llm | `packages/friday-llm/` | LiteLLMService wrapping litellm for OpenAI/Anthropic/Ollama |
| friday-transcript | `packages/friday-transcript/` | Immutable conversation transcript storage (SQLite via aiosqlite) |
| friday-agent | `packages/friday-agent/` | CopilotAgent (Re-Act loop), AgentProfile, DefaultToolRegistry |
| friday-tools | `packages/friday-tools/` | BaseTool, tool categories (filesystem, shell, web, git, data, text, code) |
| friday-sandbox | `packages/friday-sandbox/` | SubprocessSandbox for isolated Python execution |
| friday-mcp | `packages/friday-mcp/` | MCP protocol client, tool adapters, SSE transport |
| friday-cli | `packages/friday-cli/` | Rich/Prompt Toolkit terminal interface, command registry, session management |
| friday-copilot | `apps/friday-copilot/` | Main AI assistant application with memory, tools, and agent orchestration |

## Architecture Patterns

**Protocol-First Design:** Abstract protocols in `friday-core/interfaces/` define contracts:
- `LLMClient`, `EmbeddingModel` - LLM inference
- `ToolDefinition`, `ToolRegistry`, `ToolAdapter` - Tool management
- `VectorStoreAdapter`, `GraphStoreAdapter`, `EpisodicStoreAdapter` - Storage
- `ContextEngineeringInterface` - Context assembly

**CopilotAgent Flow:**
1. Initialize session via ContextAssembler
2. Assemble context (token budgeting with Knapsack algorithm)
3. Call LLM with tool schemas
4. Execute tool calls in Re-Act loop (max 10 iterations)
5. Archive turn to memory

**Tool System:**
- `BaseTool` abstract class with `name`, `description`, `parameters_schema`, `execute()`
- `@tool` decorator for function-based tools
- `ToolManifest` generates LLM-ready tool descriptions
- `CodeGenerationTool` uses LLM to compose tools into executable code

**Three Memory Stores:**
- **Graph Store** (NetworkX): Entities and relationships with Hebbian learning (`hit_count`)
- **Vector Store** (ChromaDB): Semantic search for documents
- **Episodic Store**: Short-term conversation history

## Development Conventions

**Specification-Driven:** Code references specs in `docs/specs/` via `Ref:` comments.

**Pydantic Models:** All data boundaries use Pydantic 2.0+ for validation.

**Async Throughout:** Tools and LLM calls are async (`async def execute()`).

**Ruff:** Line length 88, Python 3.10+.

## Environment Variables

Copy `.env.example` to `.env`:
- `OPENAI_API_KEY` - For OpenAI models
- `ANTHROPIC_API_KEY` - For Claude models
- `OPENROUTER_API_KEY` - For OpenRouter (multi-provider gateway)
- `OLLAMA_BASE_URL` - For local Ollama (default: http://localhost:11434)

Source code is not allowed to fail silently. 

All logging our debugging code is wrapped in the appropriate logging levels depicted in the friday-core package 

Ensure that all code has detailed docstrings provided. Documentation is a critical task must be performed when writing code. 