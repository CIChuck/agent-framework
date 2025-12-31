# Friday Memory Examples

This directory contains three progressive examples demonstrating the friday-memory package.

## Examples

### 01_introductory.py - Getting Started

Learn the fundamentals:
- **ProvenanceMetadata**: Track where data comes from
- **GraphNode**: Entities with Hebbian learning (hit_count)
- **InMemoryEpisodicStore**: Conversation history management
- Consolidation tracking and history rewind

```bash
python 01_introductory.py
```

### 02_intermediate.py - Memory Controller

Build on the basics with unified memory management:
- **MemoryController**: Facade for all memory stores
- **ChromaVectorStore**: Semantic search with embeddings
- **ElementXGraphStore**: Knowledge graph with relationships
- Unified recall across all stores
- Entity resolution (merging duplicates)
- Graph traversal and fuzzy search

```bash
python 02_intermediate.py
```

### 03_advanced.py - Full Context Engineering

Complete RAG pipeline for production systems:
- **DocumentIngestionPipeline**: Chunking with overlap
- **ContextAssembler**: Session and context orchestration
- **PromptArchitect**: Token budgeting and layout optimization
- Scoped variables (user:, session:, app:)
- Checkpoint/restore for conversation rollback
- Telemetry and observability

```bash
python 03_advanced.py
```

## Prerequisites

```bash
pip install friday-memory

# For vector store (optional - examples use mocks):
export OPENAI_API_KEY=your_key_here
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ContextAssembler                         │
│  (Session management, context assembly, consolidation)      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    MemoryController                         │
│  (Unified facade for all memory operations)                 │
└─────────────────────────────────────────────────────────────┘
          │                   │                    │
          ▼                   ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│  VectorStore    │ │   GraphStore    │ │   EpisodicStore     │
│  (ChromaDB)     │ │  (ElementX)     │ │   (In-Memory)       │
│                 │ │                 │ │                     │
│ Semantic search │ │ Entities/Facts  │ │ Conversation        │
│ RAG passages    │ │ Relationships   │ │ history             │
└─────────────────┘ └─────────────────┘ └─────────────────────┘
```

## Key Concepts

### Provenance
Every piece of data tracks its origin (source_id, source_type, confidence, author_id).

### Hebbian Learning
"Neurons that fire together, wire together" - nodes track access frequency via `touch()`.

### Token Budgeting
The "Knapsack" algorithm prioritizes what fits in the context window:
1. Deep history (turns 10+) - dropped first
2. Weak matches (similarity < 0.5) - dropped second
3. Recent history (turns 3-10) - dropped if needed
4. Immediate context (last 2 turns, query) - protected

### Scoped Variables
Three-tier variable system:
- `user:*` - User preferences (persist across sessions)
- `session:*` - Session-specific state
- `app:*` - Application configuration
