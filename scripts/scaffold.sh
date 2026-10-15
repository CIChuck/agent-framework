#!/bin/bash

# Friday Framework - Project Scaffolding Generator
# Based on 'friday_project_scaffold.md'
# Run this script to generate the full directory structure and configuration files.

set -e

PROJECT_NAME="friday"

echo "🚀 Initializing Friday Framework Monorepo: $PROJECT_NAME..."

# --- 1. Root Directory & Config ---
#mkdir -p "$PROJECT_NAME"
#cd "$PROJECT_NAME"

echo "Creating root configuration..."

# Root pyproject.toml (Workspace Definition)
cat <<EOF > pyproject.toml
[project]
name = "friday"
version = "0.1.0"
description = "Friday Agentic Framework Workspace"
requires-python = ">=3.13.4"
dependencies = []

[tool.uv.workspace]
members = ["packages/*", "apps/*", "tests/lab"]

[tool.ruff]
line-length = 88
EOF

# .gitignore
cat <<EOF > .gitignore
__pycache__/
*.pyc
.env
.venv/
.idea/
.vscode/
dist/
build/
*.egg-info/
chroma_db/
*.gpickle
EOF

# .env.example
cat <<EOF > .env.example
APP_ENV=development
LOG_LEVEL=INFO
OPENAI_API_KEY=sk-proj-...
EOF

echo "# Friday Framework" > README.md

# --- 2. Packages: friday-core ---
echo "📦 Creating package: friday-core..."
CORE_DIR="packages/friday-core"
mkdir -p "$CORE_DIR/src/friday_core/interfaces"

# Config
cat <<EOF > "$CORE_DIR/pyproject.toml"
[project]
name = "friday-core"
version = "0.1.0"
description = "Foundation interfaces and utilities for Friday"
requires-python = ">=3.13.4"
dependencies = [
    "pydantic>=2.0",
    "pydantic-settings",
    "structlog",
]
EOF

# Source Files with Docstrings
cat <<EOF > "$CORE_DIR/src/friday_core/__init__.py"
"""
Friday Core Package
Foundation interfaces and shared utilities.
Ref: Batch 0 Specification
"""
EOF

cat <<EOF > "$CORE_DIR/src/friday_core/config.py"
"""
Global configuration management using Pydantic Settings.
Handles environment variable loading and validation.

Ref: Batch 0 Specification, Section 3.1
"""
EOF

cat <<EOF > "$CORE_DIR/src/friday_core/exceptions.py"
"""
Base exception hierarchy for the Friday Framework.
Defines FridayError, MemoryError, ContextOverflowError, etc.

Ref: Batch 0 Specification, Section 4.2
"""
EOF

cat <<EOF > "$CORE_DIR/src/friday_core/logging.py"
"""
Structured logging wrapper.
Provides JSON logging for production and colored output for dev.

Ref: Batch 0 Specification, Section 4.1
"""
EOF

cat <<EOF > "$CORE_DIR/src/friday_core/telemetry.py"
"""
Telemetry Interfaces and Debug Recorders.
Defines TelemetryInterface protocol for white-box testing.

Ref: Batch 0 Specification, Section 4.3
"""
EOF

cat <<EOF > "$CORE_DIR/src/friday_core/interfaces/__init__.py"
"""
Shared Protocol Definitions.
"""
EOF

cat <<EOF > "$CORE_DIR/src/friday_core/interfaces/memory.py"
"""
Abstract Base Classes for Data Storage Adapters.
Includes VectorStoreAdapter, GraphStoreAdapter, and EpisodicStoreAdapter protocols.

Ref: Batch 1 Specification, Section 1
"""
EOF

cat <<EOF > "$CORE_DIR/src/friday_core/interfaces/context.py"
"""
Abstract Base Classes for Context Engineering strategies.
Includes ContextEngineeringInterface protocol.

Ref: Batch 2a Specification, Section 1.1
"""
EOF


# --- 3. Packages: friday-memory ---
echo "🧠 Creating package: friday-memory..."
MEM_DIR="packages/friday-memory"
mkdir -p "$MEM_DIR/src/friday_memory/models"
mkdir -p "$MEM_DIR/src/friday_memory/adapters"
mkdir -p "$MEM_DIR/src/friday_memory/controller"
mkdir -p "$MEM_DIR/src/friday_memory/context"
mkdir -p "$MEM_DIR/src/friday_memory/ingestion"

# Config
cat <<EOF > "$MEM_DIR/pyproject.toml"
[project]
name = "friday-memory"
version = "0.1.0"
description = "Intelligence layer: Storage, Retrieval, and Context Engineering"
requires-python = ">=3.13.4"
dependencies = [
    "friday-core",
    "chromadb",
    "networkx",
    "litellm",
    "numpy"
]

[tool.uv.sources]
friday-core = { workspace = true }
EOF

# Source Files with Docstrings
cat <<EOF > "$MEM_DIR/src/friday_memory/__init__.py"
"""
Friday Memory Package.
Contains the 'Brain' logic: MemoryController, ContextEngine, and DB Adapters.
Ref: Batch 1 & 2 Specifications
"""
EOF

# Models
cat <<EOF > "$MEM_DIR/src/friday_memory/models/__init__.py"
"""Data Transfer Objects (DTOs) for the Memory subsystem."""
EOF

cat <<EOF > "$MEM_DIR/src/friday_memory/models/graph.py"
"""
Graph Data Models.
Defines GraphNode, GraphEdge, and ProvenanceMetadata with strong typing.

Ref: Batch 1 Specification, Section 2.1
"""
EOF

cat <<EOF > "$MEM_DIR/src/friday_memory/models/session.py"
"""
Session State Models.
Defines SessionState and Scoped Variable management (user:/app:/session:).

Ref: Batch 2a Specification, Section 1.2
"""
EOF

cat <<EOF > "$MEM_DIR/src/friday_memory/models/payload.py"
"""
Context Retrieval Payload.
Defines ContextPayload DTO for passing data from Controller to Assembler.
Includes recent_memories (Transparency Loop).

Ref: Batch 2 Specification, Section 1.1
"""
EOF

# Adapters
cat <<EOF > "$MEM_DIR/src/friday_memory/adapters/__init__.py"
"""Concrete implementations of Storage Adapters."""
EOF

cat <<EOF > "$MEM_DIR/src/friday_memory/adapters/graph.py"
"""
ElementX / NetworkX Graph Store Implementation.
Implements GraphStoreAdapter with persistence and schema enforcement.

Ref: Batch 1 Specification, Section 2.2
"""
EOF

cat <<EOF > "$MEM_DIR/src/friday_memory/adapters/vector.py"
"""
ChromaDB Vector Store Implementation.
Implements VectorStoreAdapter with embedding model wrapping.

Ref: Batch 1 Specification, Section 3.1
"""
EOF

cat <<EOF > "$MEM_DIR/src/friday_memory/adapters/episodic.py"
"""
Episodic Memory Adapter Implementation.
Handles short-term history logging and time-travel (rewind).

Ref: Batch 1 Specification, Section 1.1
"""
EOF

# Controller
cat <<EOF > "$MEM_DIR/src/friday_memory/controller/__init__.py"
"""Memory Orchestration Layer."""
EOF

cat <<EOF > "$MEM_DIR/src/friday_memory/controller/memory_controller.py"
"""
The Memory Controller Facade.
Orchestrates parallel retrieval from Vector, Graph, and Episodic stores.
Handles 'Store Fact', 'Recall', and 'Rollback' operations.

Ref: Batch 2 Specification, Section 2
"""
EOF

# Context
cat <<EOF > "$MEM_DIR/src/friday_memory/context/__init__.py"
"""Context Engineering Logic."""
EOF

cat <<EOF > "$MEM_DIR/src/friday_memory/context/assembler.py"
"""
Context Assembler.
Implements the 'Knapsack' budgeting logic to fit memory into the token window.
Handles Active Search queries.

Ref: Batch 2a Specification, Section 2
"""
EOF

cat <<EOF > "$MEM_DIR/src/friday_memory/context/extractor.py"
"""
Memory Extractor (The Harvester).
Analyzes conversation turns to extract new entities and facts for the Graph.

Ref: Batch 2a Specification, Section 3
"""
EOF

cat <<EOF > "$MEM_DIR/src/friday_memory/context/consolidator.py"
"""
Memory Consolidator (The Synthesizer).
Handles deduplication, summarization, and drift management of long-term memory.

Ref: Batch 2a Specification, Section 4
"""
EOF

cat <<EOF > "$MEM_DIR/src/friday_memory/context/layout.py"
"""
Prompt Architect (Layout Engine).
Physically structures the final prompt to optimize model attention.

Ref: Batch 2a Specification, Section 5
"""
EOF

# Ingestion
cat <<EOF > "$MEM_DIR/src/friday_memory/ingestion/__init__.py"
"""Document Processing Logic."""
EOF

cat <<EOF > "$MEM_DIR/src/friday_memory/ingestion/pipeline.py"
"""
Document Ingestion Pipeline.
Handles file parsing, cleaning, chunking, and metadata extraction.

Ref: Batch 1 Specification, Section 4
"""
EOF


# --- 4. Packages: friday-optimization ---
echo "🧪 Creating package: friday-optimization..."
OPT_DIR="packages/friday-optimization"
mkdir -p "$OPT_DIR/src/friday_opt/signatures"
mkdir -p "$OPT_DIR/src/friday_opt/compilers"

# Config
cat <<EOF > "$OPT_DIR/pyproject.toml"
[project]
name = "friday-optimization"
version = "0.1.0"
description = "DSPy optimization playground"
requires-python = ">=3.13.4"
dependencies = [
    "friday-memory",
    "dspy-ai"
]

[tool.uv.sources]
friday-memory = { workspace = true }
EOF

# Source Files with Docstrings
cat <<EOF > "$OPT_DIR/src/friday_opt/__init__.py"
"""
Friday Optimization Package.
Contains DSPy signatures and compilers for prompt optimization.
Ref: Lab Environment Spec
"""
EOF

cat <<EOF > "$OPT_DIR/src/friday_opt/signatures/summarization.py"
"""
DSPy Signatures for Memory Summarization.
Ref: Lab Environment Spec
"""
EOF

cat <<EOF > "$OPT_DIR/src/friday_opt/signatures/query_gen.py"
"""
DSPy Signatures for generating active memory search queries.
Ref: Lab Environment Spec
"""
EOF

cat <<EOF > "$OPT_DIR/src/friday_opt/compilers/optimize_context.py"
"""
Optimization scripts for tuning the Context Engine prompts.
Ref: Lab Environment Spec
"""
EOF


# --- 5. Apps: friday-cli ---
echo "💻 Creating app: friday-cli..."
CLI_DIR="apps/friday-cli"
mkdir -p "$CLI_DIR/src/friday_cli/server"

# Config
cat <<EOF > "$CLI_DIR/pyproject.toml"
[project]
name = "friday-cli"
version = "0.1.0"
description = "The Friday Assistant Runtime"
requires-python = ">=3.13.4"
dependencies = [
    "friday-memory",
    "typer",
    "fastapi",
    "uvicorn"
]

[tool.uv.sources]
friday-memory = { workspace = true }
EOF

# Source Files with Docstrings
cat <<EOF > "$CLI_DIR/src/friday_cli/__init__.py"
"""
Friday CLI Application.
Entry point for the Agent runtime.
Ref: Batch 3 Specification (Pending)
"""
EOF

cat <<EOF > "$CLI_DIR/src/friday_cli/main.py"
"""
Main entry point for the CLI.
Ref: Batch 3 Specification (Pending)
"""
EOF

cat <<EOF > "$CLI_DIR/src/friday_cli/container.py"
"""
Dependency Injection Container.
Wires configuration to the MemoryController and other components.
Ref: Batch 3 Specification (Pending)
"""
EOF

cat <<EOF > "$CLI_DIR/src/friday_cli/repl.py"
"""
Read-Eval-Print Loop for interactive agent sessions.
Ref: Batch 3 Specification (Pending)
"""
EOF

cat <<EOF > "$CLI_DIR/src/friday_cli/server/api.py"
"""
FastAPI Server endpoints for remote agent interaction.
Ref: Batch 3 Specification (Pending)
"""
EOF


# --- 6. Tests & Lab ---
echo "🔬 Creating Lab Environment..."
LAB_DIR="tests/lab"
mkdir -p "$LAB_DIR/dashboard"
mkdir -p "$LAB_DIR/datasets"
mkdir -p "$LAB_DIR/experiments"

# Config
cat <<EOF > "$LAB_DIR/pyproject.toml"
[project]
name = "friday-lab"
version = "0.1.0"
description = "The MRI Suite: Observability and Experiments"
requires-python = ">=3.13.4"
dependencies = [
    "friday-memory",
    "friday-cli",
    "ragas",
    "arize-phoenix",
    "streamlit",
    "pyvis",
    "pytest",
    "pytest-asyncio"
]

[tool.uv.sources]
friday-memory = { workspace = true }
friday-cli = { workspace = true }
EOF

# Source Files with Docstrings
cat <<EOF > "$LAB_DIR/conftest.py"
"""
Pytest configuration for the Lab.
Sets up Phoenix collectors and test fixtures.
Ref: Lab Environment Spec
"""
EOF

cat <<EOF > "$LAB_DIR/dashboard/app.py"
"""
Streamlit Dashboard ('Friday Inspector').
Visual UI for interacting with Memory and Graph.
Ref: Lab Environment Spec
"""
EOF

cat <<EOF > "$LAB_DIR/experiments/exp_01_telemetry.py"
"""
Experiment 1: The 'Live Wire' Test.
Verifies that Telemetry hooks are correctly emitting traces.
Ref: Lab Environment Spec, Phase A
"""
EOF

cat <<EOF > "$LAB_DIR/experiments/exp_03_graph_persistence.py"
"""
Experiment 3: The 'Amnesia' Test.
Verifies Graph persistence to disk.
Ref: Lab Environment Spec, Phase B
"""
EOF

cat <<EOF > "$LAB_DIR/experiments/exp_05_entity_merging.py"
"""
Experiment 5: The 'Doppelgänger' Test.
Verifies entity merging logic in the Graph Store.
Ref: Lab Environment Spec, Phase B
"""
EOF


echo "✅ Scaffolding complete!"
echo "To initialize the environment:"
echo "  1. cd $PROJECT_NAME"
echo "  2. Ensure 'uv' is installed (pip install uv)"
echo "  3. Run 'uv sync'"