# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Friday Framework is a Python-based agentic framework with a modular architecture for building AI agents. It follows a "Mind" (intelligence layer) and "Body" (execution layer) design, with a central "Memory Loop" for context retrieval, learning, and decision-making.

**Current Status:** v0.1.0 - Early development/scaffold phase. Most code files contain stubs with docstrings referencing specifications.

## Build Commands

```bash
# Install/sync all dependencies (uses uv workspaces)
uv sync

# Run tests (from project root)
pytest

# Run a single test file
pytest tests/lab/experiments/exp_01_telemetry.py

# Run main entry point (currently just Hello World)
python main.py
```

## Monorepo Structure & Dependency Flow

The project uses `uv` workspaces. Dependencies flow in one direction:

```
friday-core (foundation)
    ↓
friday-memory (intelligence layer)
    ↓
friday-optimization (DSPy integration)
    ↓
friday-cli (application)
    ↓
friday-lab (tests & observability)
```

| Package | Location | Purpose |
|---------|----------|---------|
| friday-core | `packages/friday-core/` | Config, logging, exceptions, abstract protocols |
| friday-memory | `packages/friday-memory/` | Storage adapters, memory controller, context engineering |
| friday-optimization | `packages/friday-optimization/` | DSPy prompt optimization |
| friday-cli | `apps/friday-cli/` | CLI REPL, FastAPI server |
| friday-lab | `tests/lab/` | "MRI Suite" - experiments, dashboards, pytest fixtures |

## Architecture Patterns

**Protocol-First Design:** Abstract protocols in `friday-core/interfaces/` define contracts. Implementations in `friday-memory/adapters/` are swappable.

**Three Memory Stores:**
- **Graph Store** (NetworkX/ElementX): Structured facts and relationships
- **Vector Store** (ChromaDB): Semantic search for documents
- **Episodic Store**: Short-term conversation history

**Key Components in friday-memory:**
- `models/` - Pydantic DTOs (GraphNode, GraphEdge, ContextPayload, SessionState)
- `adapters/` - Storage implementations (vector.py, graph.py, episodic.py)
- `controller/` - MemoryController facade orchestrating all stores
- `context/` - Assembler (token budgeting), Extractor (entities/facts), Consolidator (dedup), Layout (prompt structure)
- `ingestion/` - Document parsing and chunking pipeline

## Development Conventions

**Specification-Driven:** All development follows the batch specifications in `docs/specs/`:
- Batch 0: Core utilities
- Batch 1: Data layer (IO adapters, storage)
- Batch 2: Intelligence layer (memory controller, context)
- Batch 2a: Advanced context features

Code modules include `Ref:` comments pointing to relevant spec sections.

**Inside-Out Development:** Always build from core → memory → optimization → cli.

**Pydantic Everywhere:** All data models use Pydantic 2.0+ for validation at boundaries.

**Ruff Formatting:** Line length 88 characters.

## Key Concepts

- **Auto-Memorize:** System decides whether info goes to graph (facts) or vector store (documents)
- **Hebbian Learning:** `hit_count` on graph nodes reinforces frequently accessed knowledge
- **Knapsack Algorithm:** Context assembler optimizes context to fit token windows

## Environment Variables

Copy `.env.example` to `.env`:
- `APP_ENV` - development/production
- `LOG_LEVEL` - INFO/DEBUG
- `OPENAI_API_KEY` - Required for LLM calls
