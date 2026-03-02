---
title: "Development Setup"
description: "Clone, install dependencies, run tests, and make your first contribution."
weight: 1
---

Clone the Friday monorepo, install all dependencies with `uv sync`, run the test suite with `pytest`, and follow the contribution workflow to open your first pull request.

## Prerequisites

**Required:**
- Python 3.10 or higher (3.11+ recommended)
- Git
- `uv` — modern Python package manager
- SQLite 3.35+ (pre-installed on macOS/Linux)
- 4 GB+ RAM (16 GB+ recommended for local LLM testing)

**Optional but recommended:**
- Docker and Docker Compose for containerized testing
- Ollama for local LLM testing (avoids API costs)
- VS Code or PyCharm with Python extensions
- GitHub CLI (`gh`) for pull request workflow

**API keys (at least one required for agent tests):**
- `OPENAI_API_KEY` — OpenAI models (GPT-4o, GPT-4o-mini)
- `ANTHROPIC_API_KEY` — Anthropic models (Claude 3.5 Sonnet)
- `GOOGLE_API_KEY` — Google models (Gemini 2.5 Pro)
- Or install Ollama for free local testing (zero API cost)

---

## Install uv

Friday uses `uv` for workspace management. It is significantly faster than pip/poetry and handles monorepo dependencies cleanly.

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv

# Verify installation
uv --version
```

Why `uv`? It is 10-100x faster than pip for dependency resolution, has built-in workspace support for monorepos, produces deterministic installs via lockfile, and is written in Rust.

---

## Clone the Repository

```bash
git clone https://github.com/your-org/friday-agent-framework.git
cd friday-agent-framework

# Verify structure
ls packages/
# friday-core  friday-memory  friday-llm  friday-agent  friday-tools  ...
```

**Repository structure:**

```
friday-agent-framework/
├── packages/              # Core Friday packages (workspace members)
│   ├── friday-core/       # Abstract protocols, config, logging
│   ├── friday-memory/     # Memory system (vector/graph/episodic)
│   ├── friday-llm/        # LLM client (LiteLLM wrapper)
│   ├── friday-agent/      # CopilotAgent, orchestrator
│   ├── friday-tools/      # 50+ built-in tools
│   ├── friday-transcript/ # Conversation logging
│   ├── friday-mcp/        # Model Context Protocol integration
│   └── friday-sandbox/    # Isolated code execution
├── apps/
│   └── friday-cli/        # CLI application
├── tests/
│   ├── integration/       # End-to-end tests
│   └── lab/               # Experimental environments
├── docs/                  # Documentation and specs
├── pyproject.toml         # Workspace configuration
├── uv.lock                # Dependency lockfile
├── .env.example           # Environment variable template
└── CLAUDE.md              # Claude Code guidance
```

---

## Install Dependencies

Friday uses a monorepo workspace. All packages share dependencies and are developed together.

```bash
# Install all dependencies (development + runtime)
uv sync
```

What `uv sync` does:
1. Resolves dependencies across all workspace packages
2. Creates/updates the virtual environment (`.venv/`)
3. Installs packages in editable mode (changes reflect immediately)
4. Locks dependencies in `uv.lock` for reproducibility

**Verify installation:**

```bash
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

uv run python -c "from friday_agent import CopilotAgent; print('Friday loaded')"
uv run python -c "from friday_memory import MemoryController; print('Memory loaded')"
uv run python -c "from friday_tools import BaseTool; print('Tools loaded')"
```

---

## Running Tests

```bash
# Run full test suite
pytest

# Verbose output
pytest -v

# Run tests for a specific package
pytest packages/friday-memory/tests_memory/ -v

# Run a single test file
pytest packages/friday-tools/tests_tools/test_protocols.py -v

# Run tests matching a pattern
pytest -k "test_memory" -v

# Run with coverage report
pytest --cov=packages --cov-report=html

# Skip slow tests during development
pytest -m "not slow" -v
```

**Common test scenarios:**

```bash
# Memory system
pytest packages/friday-memory/tests_memory/ -v

# Agent tests (requires API key or Ollama)
pytest packages/friday-agent/tests_agent/ -v

# Tool tests
pytest packages/friday-tools/tests_tools/ -v
```

**Set up API keys for tests:**

```bash
cp .env.example .env
# Edit .env with your test API keys:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

**Use Ollama for zero-cost testing:**

```bash
# Pull a test model (one-time)
ollama pull llama3

# Run agent tests with local model
FRIDAY_LLM__MODEL=ollama/llama3 pytest packages/friday-agent/tests_agent/
```

---

## Code Style and Linting

Friday enforces consistent style with **Ruff** — a fast Python linter and formatter.

**Configuration:**
- Line length: 88 characters (Black-compatible)
- Target: Python 3.10+
- Rules: E (errors), F (pyflakes), I (import sorting), UP (pyupgrade), B (bugbear), SIM (simplify)

```bash
# Check for issues (no modifications)
uv run ruff check .

# Auto-fix issues where possible
uv run ruff check . --fix

# Format code (modifies files)
uv run ruff format .

# Check a specific package
uv run ruff check packages/friday-memory/
```

**Pre-commit workflow:**

```bash
uv run ruff check . --fix   # Fix linting issues
uv run ruff format .         # Format code
pytest -k "not slow"         # Run fast tests
```

**VS Code `settings.json`:**

```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll": true,
            "source.organizeImports": true
        }
    }
}
```

---

## Type Checking with mypy

All new code must include type hints.

```bash
# Check a specific package (recommended during development)
uv run mypy packages/friday-core/

# Check all packages
uv run mypy packages/

# mypy configuration in pyproject.toml:
# python_version = "3.10"
# warn_return_any = true
# disallow_untyped_defs = true
```

**Type hints best practices:**

```python
# Good — full type hints
from typing import Optional, List
from pathlib import Path

def process_file(
    file_path: Path,
    max_lines: Optional[int] = None
) -> List[str]:
    """Process file and return lines."""
    ...

# Bad — missing types
def process_file(file_path, max_lines=None):
    ...
```

---

## Commit Conventions

Friday follows the **Conventional Commits** specification.

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `style`

**Scopes:** `memory`, `llm`, `agent`, `tools`, `cli`, `docs`, `config`, `transcript`

**Examples:**

```bash
# Feature
git commit -m "feat(memory): add decay reactivation for forgotten memories

Implement soft-delete pattern where decayed memories can be reactivated
when accessed again.

Closes #42"

# Bug fix
git commit -m "fix(llm): handle timeout errors with exponential backoff

Fixes #89"

# Documentation
git commit -m "docs(guides): add troubleshooting section for ChromaDB issues"

# Refactoring
git commit -m "refactor(tools): extract tool schema generation to helper"
```

**Best practices:**
1. Atomic commits — one logical change per commit
2. Subject line in imperative mood, under 50 characters
3. Body explains *why*, not *what* (code shows what)
4. Use `Closes #N` or `Fixes #N` to auto-close issues

---

## Standard Contribution Workflow

```bash
# 1. Create a feature branch from master
git checkout -b feat/your-feature-name

# 2. Make your changes

# 3. Lint and format
uv run ruff check . --fix
uv run ruff format .

# 4. Type check (for changed packages)
uv run mypy packages/your-package/

# 5. Run relevant tests
pytest packages/your-package/tests/ -v

# 6. Commit
git add .
git commit -m "feat(scope): your change description"

# 7. Push
git push origin feat/your-feature-name

# 8. Open pull request
gh pr create \
  --title "feat: Add your feature" \
  --body "## Description
...

## Testing
- All existing tests pass
- Added test: test_your_feature()

Closes #N"
```

**PR requirements:**
- All tests pass
- Ruff linting is clean
- Type hints included and mypy passes
- Documentation updated (docstrings, guide sections if user-facing)
- Tests included for new features
- Conventional commit messages

**Quick reference:**

| Task | Command |
|------|---------|
| Install deps | `uv sync` |
| Run all tests | `pytest` |
| Run specific tests | `pytest packages/friday-memory/tests_memory/ -v` |
| Lint | `uv run ruff check . --fix` |
| Format | `uv run ruff format .` |
| Type check | `uv run mypy packages/friday-core/` |
| Run CLI | `uv run python tests/integration/memory/memory-chat-v2.py` |

## Related Pages

- [Architecture Decisions](/docs/contributing/adrs/) — ADRs explaining key design choices
- [Roadmap](/docs/contributing/roadmap/) — Planned features and milestones
- [Configuration Reference](/docs/configuration/reference/) — Full config.yaml template
