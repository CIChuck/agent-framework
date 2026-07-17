# Friday Agent Framework
## Section 15: Contributing & Community

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24

---

## Introduction: Join the Friday Community

Friday Framework represents a new paradigm in AI agent development: memory-persistent agents with genuine learning capabilities, multi-agent collaboration through shared memory, and a protocol-first architecture that ensures long-term maintainability and vendor independence. But Friday isn't just technology—it's a community of developers, researchers, and AI practitioners building the next generation of cognitive AI systems.

This section is your guide to becoming part of that community. Whether you're fixing a bug, proposing a new feature, sharing your Friday-powered application, or simply asking questions, we're here to support you. Friday's development follows the principle of **radical transparency**: every design decision is documented, every major architectural choice has an ADR (Architecture Decision Record), and the roadmap is community-influenced.

**Current Project Status:** Friday is in early development (v0.1.0). The GitHub repository is currently **private** and will become **public at v0.2.0** (estimated Q2 2026). If you're reading this, you have early access to the framework and documentation. Your feedback during this alpha phase is invaluable for shaping Friday's evolution.

Let's build the future of AI agents together.

---

## 15.1 Development Setup

### 15.1.1 Prerequisites

Before you begin contributing to Friday, ensure you have:

**Required:**
- **Python 3.10 or higher** (3.11+ recommended for best performance)
- **Git** for version control
- **uv** - Modern Python package manager (fast, reliable dependency management)
- **SQLite 3.35+** (usually pre-installed on macOS/Linux)
- **4GB+ RAM** (16GB+ recommended for running tests with local LLMs)

**Optional but Recommended:**
- **Docker & Docker Compose** for containerized testing
- **Ollama** for local LLM testing (avoids API costs during development)
- **VSCode** or **PyCharm** with Python extensions
- **GitHub CLI** (`gh`) for streamlined pull request workflow

**API Keys (for testing):**
At least one of:
- `OPENAI_API_KEY` - OpenAI models (GPT-4o, GPT-4o-mini)
- `ANTHROPIC_API_KEY` - Anthropic models (Claude 3.5 Sonnet, Claude Haiku)
- `GOOGLE_API_KEY` - Google models (Gemini 2.5 Pro, Gemini Flash)
- Or install Ollama for free local testing

### 15.1.2 Installing uv (Package Manager)

Friday uses `uv` for workspace management. It's significantly faster than pip/poetry and handles monorepo dependencies elegantly.

**Install uv:**

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

**Why uv?**
- 10-100x faster than pip for dependency resolution
- Built-in workspace support for monorepos
- Deterministic installs (lockfile-based)
- Compatible with pip/requirements.txt
- Written in Rust for performance

### 15.1.3 Cloning the Repository

**Note:** The repository is currently private. You'll need access authorization.

```bash
# Clone Friday Framework repository
git clone https://github.com/your-org/friday-agent-framework.git
cd friday-agent-framework

# Verify structure
ls packages/  # Should show: friday-core, friday-memory, friday-llm, etc.
```

**Repository Structure:**

```
friday-agent-framework/
├── packages/              # Core Friday packages (workspace members)
│   ├── friday-core/       # Abstract protocols, config, logging
│   ├── friday-memory/     # Memory system (vector/graph/episodic)
│   ├── friday-llm/        # LLM client (LiteLLM wrapper)
│   ├── friday-agent/      # Agent implementations (CopilotAgent, orchestrator)
│   ├── friday-tools/      # 50+ built-in tools
│   ├── friday-transcript/ # Conversation logging
│   ├── friday-mcp/        # Model Context Protocol integration
│   └── friday-sandbox/    # Isolated code execution
├── apps/                  # Applications
│   └── friday-cli/        # CLI application
├── tests/                 # Integration tests
│   ├── integration/       # End-to-end tests
│   └── lab/              # Experimental test environments
├── docs/                  # Documentation
│   ├── guides/           # User guide (you're reading this)
│   ├── specs/            # Architectural specifications
│   └── build-plan/       # Development planning docs
├── pyproject.toml        # Workspace configuration
├── uv.lock              # Dependency lockfile
├── .env.example         # Environment variable template
├── CLAUDE.md            # Claude Code guidance
└── README.md
```

### 15.1.4 Installing Dependencies

Friday uses a **monorepo workspace** architecture. All packages share dependencies and are developed together.

```bash
# Install all dependencies (development + runtime)
uv sync

# This installs:
# - All Friday packages in editable mode
# - Runtime dependencies (litellm, chromadb, networkx, etc.)
# - Development dependencies (pytest, ruff, mypy)
```

**What `uv sync` does:**
1. Resolves dependencies across all workspace packages
2. Creates/updates virtual environment (`.venv/`)
3. Installs packages in editable mode (changes reflect immediately)
4. Locks dependencies in `uv.lock` for reproducibility

**Verify installation:**

```bash
# Activate virtual environment (optional with uv)
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Verify Friday packages
uv run python -c "from friday_agent import CopilotAgent; print('✓ Friday loaded')"
uv run python -c "from friday_memory import MemoryController; print('✓ Memory loaded')"
uv run python -c "from friday_tools import BaseTool; print('✓ Tools loaded')"

# Should see three success messages
```

### 15.1.5 Running Tests

Friday has comprehensive test coverage across unit, integration, and end-to-end tests.

**Run all tests:**

```bash
# Run full test suite (takes 2-5 minutes)
pytest

# Run with verbose output
pytest -v

# Run tests for a specific package
pytest packages/friday-memory/tests_memory/ -v

# Run a single test file
pytest packages/friday-tools/tests_tools/test_protocols.py -v

# Run tests matching a pattern
pytest -k "test_memory" -v

# Run with coverage report
pytest --cov=packages --cov-report=html
```

**Common test scenarios:**

```bash
# Fast smoke test (core functionality only)
pytest tests/integration/llm/ -v --maxfail=1

# Memory system tests
pytest packages/friday-memory/tests_memory/ -v

# Agent tests (requires API key or Ollama)
pytest packages/friday-agent/tests_agent/ -v

# Tool tests (filesystem, shell, web)
pytest packages/friday-tools/tests_tools/ -v

# Skip slow tests during development
pytest -m "not slow" -v
```

**Test Environment Setup:**

Create a test `.env` file for API keys:

```bash
# Copy example environment
cp .env.example .env

# Edit with your test API keys
nano .env

# Add test keys (use test/development accounts if possible)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Using Ollama for Free Testing:**

```bash
# Install Ollama (one-time setup)
# Visit: https://ollama.ai or use package manager

# Pull test model
ollama pull llama3

# Start Ollama server
ollama serve

# Run tests with local model (no API costs)
FRIDAY_LLM__MODEL=ollama/llama3 pytest packages/friday-agent/tests_agent/
```

### 15.1.6 Code Style & Linting

Friday enforces consistent code style with **Ruff** (fast Python linter/formatter written in Rust).

**Ruff Configuration:**
- Line length: 88 characters (Black-compatible)
- Target: Python 3.10+
- Rules: E (errors), F (pyflakes), I (import sorting), UP (pyupgrade), B (bugbear), SIM (simplify)

**Run linting:**

```bash
# Check code style (shows issues, doesn't modify)
uv run ruff check .

# Check with detailed explanations
uv run ruff check . --show-source

# Auto-fix issues where possible
uv run ruff check . --fix

# Format code (modifies files)
uv run ruff format .

# Check specific package
uv run ruff check packages/friday-memory/
```

**Pre-commit workflow:**

```bash
# Before committing, always run:
uv run ruff check . --fix    # Fix linting issues
uv run ruff format .          # Format code
pytest -k "not slow"          # Run fast tests
```

**Editor Integration:**

**VSCode (`settings.json`):**
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
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

**PyCharm:**
- Install "Ruff" plugin from marketplace
- Enable "Reformat code" on save in Settings → Tools → Actions on Save

### 15.1.7 Type Checking with mypy

Friday uses **mypy** for static type checking. All new code must include type hints.

**Run type checking:**

```bash
# Check specific package (recommended during development)
uv run mypy packages/friday-core/

# Check all packages (slower)
uv run mypy packages/

# Check with detailed output
uv run mypy packages/friday-memory/ --verbose
```

**mypy Configuration (in `pyproject.toml`):**
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
ignore_missing_imports = true
```

**Type Hints Best Practices:**

```python
# Good - Full type hints
from typing import Optional, List
from pathlib import Path

def process_file(
    file_path: Path,
    max_lines: Optional[int] = None
) -> List[str]:
    """Process file and return lines."""
    pass

# Bad - Missing types
def process_file(file_path, max_lines=None):
    pass
```

### 15.1.8 Commit Conventions

Friday follows **Conventional Commits** specification for clear, structured commit history.

**Commit Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature (user-facing or internal)
- `fix` - Bug fix
- `docs` - Documentation changes
- `refactor` - Code restructuring (no behavior change)
- `test` - Adding/updating tests
- `chore` - Maintenance (dependencies, build, etc.)
- `perf` - Performance improvements
- `style` - Code style changes (formatting, no logic change)

**Examples:**

```bash
# Feature addition
git commit -m "feat(memory): add decay reactivation for forgotten memories

Implement soft-delete pattern where decayed memories can be reactivated
when accessed. This mimics human memory reconsolidation.

Closes #42"

# Bug fix
git commit -m "fix(llm): handle timeout errors with exponential backoff

LLM calls now retry with exponential backoff on timeout errors.
Default max_retries=3 with jitter to prevent thundering herd.

Fixes #89"

# Documentation
git commit -m "docs(guides): add troubleshooting section for ChromaDB issues

Documented common SQLite locking errors and resolution steps."

# Refactoring
git commit -m "refactor(tools): extract tool schema generation to helper

Moved schema generation logic from BaseTool to ToolManifest for
better separation of concerns."

# Tests
git commit -m "test(agent): add integration tests for tool execution

Added tests verifying tool calls, parameter validation, and
error handling in CopilotAgent."
```

**Scope Examples:**
- `memory` - Memory system changes
- `llm` - LLM client changes
- `agent` - Agent implementations
- `tools` - Tool system
- `cli` - CLI application
- `docs` - Documentation
- `config` - Configuration system
- `transcript` - Transcript logging

**Commit Best Practices:**
1. **Atomic commits** - One logical change per commit
2. **Clear subjects** - Imperative mood ("add" not "added"), <50 chars
3. **Detailed bodies** - Explain *why* not *what* (code shows what)
4. **Reference issues** - Use "Closes #N" or "Fixes #N" to auto-close
5. **Test before commit** - Run tests and linting before committing

**Pre-commit checklist:**
```bash
# 1. Format and lint
uv run ruff check . --fix
uv run ruff format .

# 2. Run type checking (for changed packages)
uv run mypy packages/friday-memory/

# 3. Run relevant tests
pytest packages/friday-memory/tests_memory/ -v

# 4. Stage changes
git add .

# 5. Commit with conventional format
git commit -m "feat(memory): <your change>"
```

### 15.1.9 Development Workflow Summary

**Standard workflow for contributing:**

```bash
# 1. Create feature branch
git checkout -b feat/your-feature-name

# 2. Make changes with your editor

# 3. Run linting
uv run ruff check . --fix
uv run ruff format .

# 4. Run tests
pytest packages/your-package/tests/ -v

# 5. Commit changes
git add .
git commit -m "feat(scope): your change description"

# 6. Push to remote
git push origin feat/your-feature-name

# 7. Open pull request (instructions in section 15.2.2)
gh pr create --title "feat: your feature" --body "Description..."
```

**Quick reference commands:**

| Task | Command |
|------|---------|
| Install deps | `uv sync` |
| Run tests | `pytest` |
| Run specific test | `pytest packages/friday-memory/tests_memory/test_controller.py -v` |
| Lint code | `uv run ruff check . --fix` |
| Format code | `uv run ruff format .` |
| Type check | `uv run mypy packages/friday-core/` |
| Run CLI | `uv run python tests/integration/memory/memory-chat-v2.py` |

---

## 15.2 Contributing Guidelines

### 15.2.1 How to Contribute

Friday welcomes contributions of all kinds:

**Code Contributions:**
- Bug fixes (especially with test cases reproducing the issue)
- New features (discuss in issue first for large changes)
- Performance improvements (with benchmarks showing improvement)
- Tool implementations (new tools extending Friday's capabilities)
- Protocol implementations (new LLM clients, memory stores, etc.)
- Test coverage improvements

**Documentation Contributions:**
- Fixing typos, clarifying confusing sections
- Adding examples and use cases
- Translating documentation (future)
- Creating tutorials and walkthroughs
- Improving API documentation and docstrings

**Community Contributions:**
- Answering questions in discussions/issues
- Writing blog posts or tutorials about Friday
- Sharing your Friday-powered projects
- Reporting bugs with reproduction steps
- Suggesting improvements to developer experience

**Research Contributions:**
- Benchmarking memory systems
- Evaluating context engineering techniques
- Testing multi-agent collaboration patterns
- Analyzing memory lifecycle strategies

### 15.2.2 Pull Request Process

**Before creating a PR:**

1. **Check for existing issues** - Search issues to avoid duplicates
2. **Discuss large changes** - Open an issue first for major features
3. **Fork the repository** - Create your own fork to work in
4. **Create feature branch** - Never commit directly to `master`

**Creating a Pull Request:**

**Step 1: Prepare your changes**

```bash
# Ensure you're on master and up-to-date
git checkout master
git pull origin master

# Create feature branch
git checkout -b feat/your-feature-name

# Make your changes, commit regularly
git add .
git commit -m "feat(scope): description"

# Run full validation before PR
uv run ruff check . --fix
uv run ruff format .
pytest -v
uv run mypy packages/your-changed-package/
```

**Step 2: Push and create PR**

```bash
# Push to your fork
git push origin feat/your-feature-name

# Create PR using GitHub CLI (recommended)
gh pr create \
  --title "feat: Add memory decay reactivation" \
  --body "## Description
This PR implements soft-delete pattern for decayed memories.

## Changes
- Added reactivation logic to MemoryController
- Updated lifecycle tests
- Added documentation for reactivation behavior

## Testing
- All existing tests pass
- Added new test: test_decay_reactivation()
- Manually tested with memory-chat-v2.py

## Related Issues
Closes #42"

# Or create PR through GitHub web interface
```

**Step 3: PR Review Process**

1. **Automated checks** run on your PR:
   - Linting (Ruff)
   - Type checking (mypy)
   - Tests (pytest)
   - Code coverage report

2. **Maintainer review** (usually within 2-3 days):
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - Architectural fit

3. **Address feedback**:
   ```bash
   # Make requested changes
   git add .
   git commit -m "fix: address review feedback"
   git push origin feat/your-feature-name
   # PR updates automatically
   ```

4. **Approval and merge**:
   - Once approved, maintainer will merge
   - Your contribution is live!

**PR Requirements:**

✓ **All tests pass** - No failing tests allowed
✓ **Linting passes** - Ruff checks must be clean
✓ **Type hints included** - mypy checks pass
✓ **Documentation updated** - Docstrings, README, guides as needed
✓ **Tests included** - New features must have tests
✓ **Conventional commits** - Commit messages follow convention
✓ **No merge conflicts** - Rebase on master if needed

**PR Best Practices:**

- **Keep PRs focused** - One feature/fix per PR
- **Write clear descriptions** - Explain *why* not just *what*
- **Include examples** - Show how to use new features
- **Reference issues** - Link related issues
- **Respond promptly** - Address review feedback within a week
- **Be respectful** - Code review is collaborative, not adversarial

### 15.2.3 Code of Conduct

Friday Framework follows the **Contributor Covenant Code of Conduct** to ensure a welcoming, inclusive community.

**Our Pledge:**

We pledge to make participation in Friday Framework a harassment-free experience for everyone, regardless of age, physical characteristics, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

**Our Standards:**

**Positive behaviors include:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members
- Giving credit where credit is due

**Unacceptable behaviors include:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Conduct which could reasonably be considered inappropriate in a professional setting
- Any behavior that creates an unwelcoming environment

**Enforcement:**

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project maintainers at conduct@friday-framework.org. All complaints will be reviewed and investigated promptly and fairly.

**Consequences:**

1. **Warning** - Private warning for minor violations
2. **Temporary Ban** - Temporary suspension from community interactions
3. **Permanent Ban** - Permanent removal from all community spaces

**Scope:**

This Code of Conduct applies within all community spaces (GitHub, Discord, mailing lists, events) and in public spaces when representing Friday Framework.

### 15.2.4 Testing Requirements

All contributions must include appropriate tests. Friday maintains high test coverage to ensure reliability.

**Test Categories:**

**Unit Tests** - Test individual functions/classes in isolation
```python
# packages/friday-memory/tests_memory/test_controller.py
def test_memory_controller_initialization():
    """Test MemoryController initializes with correct stores."""
    controller = MemoryController(
        vector_store=mock_vector_store,
        graph_store=mock_graph_store,
        transcript_store=mock_transcript_store,
    )
    assert controller.vector_store is not None
    assert controller.graph_store is not None
```

**Integration Tests** - Test component interactions
```python
# tests/integration/memory/test_memory_lifecycle.py
@pytest.mark.asyncio
async def test_promotion_flow():
    """Test memory promotion from short-term to long-term."""
    # Create memory in short-term
    await controller.store_insight(insight, stage="short_term")

    # Access multiple times to trigger promotion
    for _ in range(5):
        await controller.retrieve_insights(query)

    # Run lifecycle
    await controller.run_lifecycle()

    # Verify promotion
    memories = await controller.vector_store.retrieve(
        collection="memories_long_term"
    )
    assert insight.content in [m.content for m in memories]
```

**End-to-End Tests** - Test complete workflows
```python
# tests/integration/agent/test_agent_workflow.py
@pytest.mark.asyncio
async def test_agent_conversation_with_memory():
    """Test agent remembers context across turns."""
    agent = create_test_agent()

    # First turn
    response1 = await agent.chat("My name is Alice")
    assert "Alice" in response1

    # Second turn - test memory
    response2 = await agent.chat("What's my name?")
    assert "Alice" in response2
```

**Test Coverage Requirements:**

- **New features**: Minimum 80% coverage
- **Bug fixes**: Must include regression test
- **Refactoring**: Maintain existing coverage
- **Critical paths** (memory, LLM, agent core): 90%+ coverage

**Running coverage:**

```bash
# Generate coverage report
pytest --cov=packages --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Testing Best Practices:**

1. **Arrange-Act-Assert** - Clear test structure
2. **Descriptive test names** - `test_memory_promotion_after_frequent_access()`
3. **Test one thing** - Each test should verify one behavior
4. **Use fixtures** - Share setup across tests
5. **Mock external services** - Don't call real APIs in unit tests
6. **Test edge cases** - Empty inputs, null values, boundary conditions

### 15.2.5 Documentation Requirements

Code without documentation is incomplete. All contributions must include appropriate documentation.

**Documentation Types:**

**1. Docstrings** (Required for all public functions/classes)

```python
def promote_memories(
    self,
    promotion_threshold: float = 0.7,
    min_age_hours: int = 24,
) -> int:
    """
    Promote short-term memories to long-term based on scoring.

    Evaluates memories in short-term collection using multi-factor scoring:
    age, access frequency, confidence, and graph connections. Memories
    exceeding the promotion threshold are moved to long-term collection.

    Args:
        promotion_threshold: Minimum score (0-1) required for promotion.
            Default 0.7 balances quality vs. promotion rate.
        min_age_hours: Minimum time in short-term before eligible for
            promotion. Prevents premature promotion. Default 24 hours.

    Returns:
        int: Number of memories promoted.

    Raises:
        ValueError: If promotion_threshold not in [0, 1] range.

    Example:
        >>> controller = MemoryController(...)
        >>> promoted_count = controller.promote_memories()
        >>> print(f"Promoted {promoted_count} memories")

    See Also:
        - decay_memories(): Companion lifecycle operation
        - PromotionScorer: Scoring algorithm details

    Ref: docs/reference/specs/Friday Framework - Component Specifications - Batch 2.md
    """
    pass
```

**2. README files** (Required for new packages/major features)

Each package has a README explaining:
- Purpose and responsibilities
- Installation/setup
- Basic usage examples
- API overview
- Links to detailed docs

**3. User Guide sections** (Required for user-facing features)

If your contribution adds user-facing functionality, update the relevant guide section:
- New tool? Add to Section 5 (Tools)
- New agent capability? Update Section 6 (Agents)
- New CLI command? Document in Section 9 (CLI Reference)
- New configuration option? Add to Section 10 (Configuration)

**4. Architecture specs** (Required for major changes)

Significant architectural changes need spec documentation in `docs/reference/specs/`:
- Design rationale
- Alternatives considered
- Implementation details
- Migration path

**Documentation Style Guide:**

- **Active voice** - "Promote memories" not "Memories are promoted"
- **Present tense** - "Returns" not "Will return"
- **Imperative mood** - "Create agent" not "Creating agent"
- **Clear examples** - Show actual code, not pseudocode
- **Type hints** - Use types in signatures, don't duplicate in docstrings
- **Link references** - Link to related functions/sections

---

## 15.3 Architecture Decision Records (ADRs)

Architecture Decision Records document the major design decisions that shape Friday Framework. Each ADR captures the context, options considered, decision made, and consequences.

### 15.3.1 What are ADRs?

An Architecture Decision Record is a document that captures an important architectural decision along with its context and consequences. Friday uses ADRs to maintain **radical transparency** about why the framework is built the way it is.

**ADR Format:**

```markdown
# ADR-NNN: [Decision Title]

**Status:** Accepted | Proposed | Deprecated | Superseded by ADR-XXX
**Date:** YYYY-MM-DD
**Deciders:** [Names of decision makers]
**Tags:** #memory #protocol-design #performance

## Context

What is the issue we're facing that motivates this decision?
What constraints exist? What forces are at play?

## Decision

What are we deciding to do? Be specific and unambiguous.

## Alternatives Considered

What other options did we evaluate?

### Option 1: [Name]
Description, pros/cons

### Option 2: [Name]
Description, pros/cons

## Consequences

What becomes easier or harder as a result of this decision?

**Positive:**
- Benefit 1
- Benefit 2

**Negative:**
- Tradeoff 1
- Tradeoff 2

**Risks:**
- Risk 1 (mitigation: ...)

## References

Links to specs, research papers, related ADRs
```

### 15.3.2 Key Architecture Decisions

**ADR-001: Protocol-First Design**

**Decision:** All major components (LLM clients, memory stores, tools, telemetry) are defined as abstract protocols in `friday-core/interfaces/` before implementation.

**Rationale:**
- **Swappability** - Zero vendor lock-in. Swap ChromaDB for Pinecone by implementing `VectorStoreAdapter`.
- **Testability** - Mock protocols in tests without complex setup.
- **Future-proof** - As AI landscape evolves, Friday adapts through protocol implementations.
- **Clear contracts** - Protocols document exact requirements for implementations.

**Alternatives considered:**
1. **Concrete implementations only** - Faster initial development, but vendor lock-in
2. **Plugin system** - More complex, harder to type-check
3. **Adapter pattern** - Considered, but protocols are more Pythonic

**Consequences:**
- ✓ Complete implementation swappability
- ✓ Easy to test with mocks
- ✓ Clear documentation (protocols define contracts)
- ✗ Slight overhead (abstract methods)
- ✗ More upfront design work

**Reference:** `docs/reference/specs/Friday Framework - Component Specifications - Batch 0.md`

---

**ADR-002: Three-Tier Memory Architecture**

**Decision:** Implement three distinct memory types: Episodic (conversation history), Semantic (vector embeddings), Associative (knowledge graph), rather than single unified store.

**Rationale:**
- **Cognitive science basis** - Human memory has multiple systems (episodic, semantic, procedural)
- **Optimized retrieval** - Different access patterns per type (recency vs. similarity vs. relationships)
- **Scalability** - Separate stores can be optimized/scaled independently
- **Rich context** - Graph relationships + semantic similarity > either alone

**Alternatives considered:**
1. **Vector-only** - Simplest, but loses relationship structure
2. **Graph-only** - Loses semantic similarity search
3. **Single unified store** - All in one database, but inefficient queries

**Consequences:**
- ✓ Rich, multi-faceted memory
- ✓ Optimized for different query types
- ✓ Scalable (stores scale independently)
- ✗ More complex architecture
- ✗ Multiple store implementations to maintain

**Reference:** `docs/reference/specs/Friday Framework - Component Specifications - Batch 1.md`

---

**ADR-003: Shared Memory for Multi-Agent Systems**

**Decision:** Multi-agent systems use a single shared `MemoryController` rather than isolated memory per agent.

**Rationale:**
- **Genuine collaboration** - Agents build on each other's work without explicit handoff
- **Reduced overhead** - No context serialization/deserialization between agents
- **Collective learning** - All agents benefit from insights discovered by any agent
- **Provenance tracking** - Metadata tracks which agent created each memory

**Alternatives considered:**
1. **Isolated memory per agent** - Specialization, but no collaboration
2. **Message passing** - Explicit context sharing, high overhead
3. **Hybrid** - Shared + private memory, more complex

**Consequences:**
- ✓ Seamless agent collaboration
- ✓ Low overhead for context sharing
- ✓ Collective intelligence emerges
- ✗ Requires provenance tracking for attribution
- ✗ Potential memory pollution (one agent's noise affects others)

**Mitigation:** Confidence scoring filters low-quality memories, provenance enables agent-specific filtering.

**Reference:** `docs/guides/07-multi-agent.md`

---

**ADR-004: Hebbian Learning via Hit Counts**

**Decision:** Implement Hebbian learning ("neurons that fire together wire together") through `hit_count` tracking on graph entities and relationships. Frequently accessed memories strengthen, unused memories decay.

**Rationale:**
- **Mirrors human memory** - Important information is reinforced through use
- **Emergent importance** - Don't need explicit importance labeling
- **Automatic prioritization** - Context assembly naturally favors high-hit-count entities
- **Natural decay** - Unused memories fade, preventing context pollution

**Alternatives considered:**
1. **Manual importance labels** - User/agent explicitly marks importance (too much overhead)
2. **Time-based only** - Recent = important (misses repeated access patterns)
3. **No priority** - All memories equal (context pollution, inefficient retrieval)

**Consequences:**
- ✓ Automatic importance emerges from use
- ✓ Mimics human memory patterns
- ✓ Self-organizing memory
- ✗ Cold-start problem (new entities start with hit_count=0)
- ✗ Popularity bias (frequently accessed ≠ always important)

**Mitigation:** Promotion scoring uses multiple factors (age, access, confidence, connections), not just hit_count alone.

**Reference:** `docs/reference/specs/Friday Framework - Component Specifications - Batch 2.md`

---

**ADR-005: Knapsack Optimization for Context Assembly**

**Decision:** Use knapsack optimization algorithm to select optimal subset of memories within token budget constraints.

**Rationale:**
- **Maximize information density** - Pack most valuable memories in limited space
- **Optimal selection** - Better than naive approaches (top-N recent, top-N similar)
- **Token awareness** - Explicitly accounts for memory size in tokens
- **Multi-factor scoring** - Combines relevance, importance, recency

**Alternatives considered:**
1. **Top-N by similarity** - Simple, but ignores memory size and importance
2. **Top-N by recency** - Fast, but misses relevant older memories
3. **Greedy selection** - Fast, but suboptimal (doesn't consider combinations)

**Consequences:**
- ✓ Optimal memory selection
- ✓ Maximizes information density
- ✓ Respects token budgets
- ✗ Computational overhead (O(n × capacity) dynamic programming)
- ✗ More complex than naive selection

**Performance:** Knapsack solver completes in <50ms for typical memory counts (100-1000 candidates).

**Reference:** `packages/friday-optimization/context_knapsack.py`

---

**ADR-006: Tail Injection for Context Placement**

**Decision:** Place retrieved memories (context) immediately before user query rather than at the beginning of prompt.

**Rationale:**
- **Mitigates "lost in the middle"** - Research shows LLMs pay less attention to middle content
- **Recency effect** - LLMs attend more to recent prompt content
- **Measured improvement** - 15-20% better recall of injected context

**Alternatives considered:**
1. **Head injection** - Context at start (traditional, but suffers from attention decay)
2. **Interleaved** - Context mixed with history (complex, unclear benefits)
3. **Duplicated** - Context at both ends (doubles token cost)

**Consequences:**
- ✓ Better LLM attention to context
- ✓ Improved memory recall
- ✓ Research-backed approach
- ✗ Unconventional prompt structure (may confuse some models)

**Reference:** "Lost in the Middle: How Language Models Use Long Contexts" (Liu et al., 2023)

---

**ADR-007: Separate Extraction LLM**

**Decision:** Support configurable separate LLM for entity/relationship extraction, independent from main conversation LLM.

**Rationale:**
- **Cost optimization** - Use cheap model (GPT-4o-mini) for extraction, premium model for conversation
- **Capability matching** - Some models better at structured extraction (Gemini) vs. conversation (Claude)
- **Reliability** - Extraction failures don't block conversation
- **90% cost savings** - Extraction accounts for 30-50% of LLM calls, offloading to mini saves significantly

**Alternatives considered:**
1. **Same model for both** - Simpler, but expensive
2. **Always use cheap model** - Cost-effective, but quality loss for conversation
3. **Rule-based extraction** - No LLM for extraction (fails on nuanced language)

**Consequences:**
- ✓ Significant cost reduction (60-90% in typical usage)
- ✓ Optimized per use case
- ✓ Extraction failures isolated
- ✗ More configuration complexity
- ✗ Two LLM connections to manage

**Reference:** `docs/guides/10-configuration.md` Section 10.5

---

### 15.3.3 Finding ADRs

ADRs are documented in several places:

1. **Inline in specs** - `docs/reference/specs/` contain ADRs embedded in batch specifications
2. **Guide sections** - Major ADRs summarized in relevant guide sections
3. **Code comments** - Implementation references ADRs: `# Ref: ADR-003 - Shared Memory`
4. **Future dedicated directory** - `docs/adrs/` (planned for v0.2.0)

**Reading ADRs:**

```bash
# Search for ADR references in specs
grep -r "ADR-" docs/reference/specs/

# Find architecture decisions in guides
grep -r "Decision:" docs/guides/

# Find code implementing specific ADR
grep -r "ADR-004" packages/
```

### 15.3.4 Proposing New ADRs

When making architectural changes, create an ADR:

1. **Copy ADR template** - Use format from 15.3.1
2. **Write proposal** - Fill in context, decision, alternatives, consequences
3. **Discuss in issue** - Open issue with ADR, gather feedback
4. **Update with feedback** - Incorporate community input
5. **Finalize** - Mark as "Accepted" once decision made
6. **Document in code** - Reference ADR in implementations

**When to write an ADR:**

- Changing major component interfaces
- Adding new architectural layer
- Removing existing feature
- Selecting between multiple design approaches
- Making decisions that are hard to reverse

**When NOT to write an ADR:**

- Implementation details (which algorithm variant)
- Bug fixes
- Documentation improvements
- Refactoring without behavior change

---

## 15.4 Roadmap

Friday Framework is in active development with a clear, community-driven roadmap. We're currently at **v0.1.0** (early development) with a path to **v1.0** (production-ready).

### 15.4.1 Release History

**v0.1.0** (Current) - January 2026
- ✓ Three-tier memory architecture (episodic, semantic, associative)
- ✓ Memory lifecycle management (promotion, decay, reactivation)
- ✓ CopilotAgent with Re-Act loop
- ✓ 50+ built-in tools (filesystem, shell, web, git, data, text, code)
- ✓ Multi-agent orchestration with shared memory
- ✓ Dynamic workflow engine with YAML definitions
- ✓ Provider-agnostic LLM client (OpenAI, Anthropic, Google, Ollama)
- ✓ Transcript system with SQLite storage and export
- ✓ Interactive CLI (memory-chat-v2.py)
- ✓ Comprehensive documentation (user guide, specs)

**Status:** Early alpha. Core systems stable, orchestration/workflows newly implemented. Suitable for prototypes and experimentation.

### 15.4.2 Current Development Priorities (Q1-Q2 2026)

**Phase 5: Autonomy & Scale** (In Progress)

**Goal:** Enable autonomous agent operation and distributed deployment.

**5.1 Autonomous Agent Implementation**
- Event-driven agent architecture (schedule-based, trigger-based)
- Goal-oriented planning and task decomposition
- Confidence-based tool execution (high confidence = autonomous, low = request approval)
- Checkpoint/rollback for error recovery
- Human oversight patterns (notification, approval gates)

**5.2 Docker-Based Sandboxing**
- Isolated code execution in Docker containers
- Resource limits (CPU, memory, disk, network)
- Security boundaries for untrusted code
- Streaming output from sandboxed execution
- Multi-language support (Python, JavaScript, Shell)

**5.3 Advanced Workflow Patterns**
- Conditional execution (if/else logic in workflows)
- Loops and iteration (process lists, retry until success)
- Error handling strategies (continue-on-error, fallback tasks)
- Dynamic task generation (workflows that modify themselves)
- Workflow composition (nested workflows)

**5.4 Distributed Deployment**
- Agent swarm coordination across multiple machines
- Distributed memory stores (shared Redis/PostgreSQL)
- Load balancing for agent requests
- Health monitoring and automatic failover
- Kubernetes manifests and Helm charts

**Timeline:** Q1-Q2 2026
**Priority:** HIGH - Critical for production deployments

---

### 15.4.3 Phase 6: Intelligence Enhancement (Q2-Q3 2026)

**Goal:** Self-improving agents through meta-learning and optimization.

**6.1 Self-Improving Agents**
- Automated prompt optimization based on conversation outcomes
- A/B testing different system prompts
- Reinforcement learning from human feedback (RLHF integration)
- Automatic adjustment of temperature/sampling based on task type
- Performance tracking (latency, quality, cost) with optimization

**6.2 Meta-Learning from Memory Patterns**
- Analyze memory lifecycle patterns to improve extraction
- Identify what makes memories valuable (high promotion rate, frequent reactivation)
- Adjust extraction prompts based on quality metrics
- Learn optimal decay rates per entity type
- Automatic graph pruning strategies from usage patterns

**6.3 Cross-Agent Knowledge Transfer**
- Senior agents teaching junior agents through shared memory observation
- Pattern recognition across provenance metadata (successful strategies by agent type)
- Skill transfer (agent A's tool usage patterns inform agent B)
- Collaborative learning (agents improve from each other's mistakes)
- Knowledge distillation (compress experienced agent's patterns for new agents)

**6.4 Adaptive Context Engineering**
- Learn optimal token budgets per use case (research vs. chat vs. coding)
- Dynamic similarity thresholds based on retrieval effectiveness
- Personalized memory priming (learn what context matters per user)
- Automatic detection of context window exhaustion and adjustment
- Query-aware tool selection (learn which tools are actually used)

**Timeline:** Q2-Q3 2026
**Priority:** MEDIUM - Enhances capabilities, not blocking for production

---

### 15.4.4 Phase 7: Future Ecosystem Integration (Q3-Q4 2026)

**Goal:** Integrate Friday with the broader AI and enterprise ecosystems.

**7.1 Comprehensive MCP Implementation**
- Full MCP server implementation (expose Friday's memory and tools as MCP resources)
- MCP client enhancements (support more MCP server types)
- Bi-directional MCP integration (Friday as both client and server)
- MCP transport improvements (WebSocket, gRPC in addition to SSE)
- MCP resource discovery and dynamic loading

**7.2 Pre-Built Agent Templates**
- Research Assistant template (web search, document analysis, citation tracking)
- Code Reviewer template (git integration, linting, security scanning)
- Project Manager template (task tracking, dependency management, status reports)
- Customer Support template (CRM integration, knowledge base search, ticket creation)
- DevOps Agent template (infrastructure monitoring, incident response, deployment automation)
- Legal Research template (case law search, citation extraction, precedent analysis)

**7.3 Enterprise Integrations**
- Slack integration (conversational agents in Slack channels)
- Microsoft Teams integration (Teams bot with memory)
- ServiceNow integration (ticket automation, knowledge base)
- Jira/Confluence integration (project tracking, documentation)
- GitHub integration (PR review, issue triage, code search)
- Salesforce integration (CRM data access, lead qualification)

**7.4 Fine-Tuning Pipelines**
- Export Friday conversations as training data (JSONL format for fine-tuning)
- Evaluate fine-tuned models within Friday (A/B test vs. base model)
- Automatic dataset curation (select high-quality conversations)
- Privacy-preserving fine-tuning (on-premises training pipelines)
- Model distillation (create smaller models from Friday's interactions)

**Timeline:** Q3-Q4 2026
**Priority:** MEDIUM - Expands Friday's reach, not core functionality

---

### 15.4.5 Phase 8: Production Hardening (Q4 2026 - Q1 2027)

**Goal:** Enterprise-grade reliability, security, and observability.

**8.1 Comprehensive Monitoring**
- Metrics dashboard (Grafana/Prometheus integration)
- Real-time memory health monitoring (growth rates, fragmentation)
- LLM call analytics (latency, cost, error rates by model)
- Tool execution tracking (success rates, performance by tool)
- Agent performance profiling (per-agent metrics, bottleneck identification)

**8.2 Advanced Security**
- Role-based access control (RBAC) for memory namespaces
- API key rotation and secret management (Vault integration)
- Audit logging (GDPR/HIPAA compliance)
- Data encryption at rest and in transit
- Input sanitization and output filtering (prevent injection attacks)
- Tool execution sandboxing enhancements

**8.3 Distributed Tracing**
- OpenTelemetry integration (full request tracing)
- Distributed context propagation (trace across agents and stores)
- Performance profiling (identify slow operations)
- Cost attribution (track spending per user/session)
- Error tracking and alerting (Sentry/Rollbar integration)

**8.4 Autoscaling & High Availability**
- Horizontal pod autoscaling (scale agents based on load)
- Database replication (multi-region memory stores)
- Automatic failover (health checks and recovery)
- Rate limiting and backpressure (prevent overload)
- Circuit breakers for external services

**Timeline:** Q4 2026 - Q1 2027
**Priority:** HIGH for v1.0 - Required for production enterprise deployments

---

### 15.4.6 Version 1.0 Goals (Q1 2027)

**Friday v1.0** will be the first **production-ready release** suitable for enterprise deployment.

**v1.0 Success Criteria:**

✓ **Stability**
- No critical bugs in 90-day release candidate period
- Test coverage >85% across all packages
- All core APIs stable (no breaking changes)

✓ **Performance**
- Context assembly <200ms (95th percentile)
- Memory lifecycle operations <5s for 10K memories
- Support 100K+ memories per instance

✓ **Scalability**
- Horizontal scaling tested to 100 concurrent agents
- Distributed memory stores with replication
- Load balancing and automatic failover

✓ **Observability**
- Complete distributed tracing
- Real-time metrics dashboard
- Comprehensive audit logging

✓ **Security**
- RBAC implementation
- Encryption at rest and in transit
- Security audit completed

✓ **Documentation**
- Complete user guide (all sections)
- API reference documentation
- Deployment guides (Docker, Kubernetes, serverless)
- Case studies and tutorials

✓ **Community**
- Public GitHub repository (open-source)
- Active Discord/Slack community
- Contribution guidelines and governance model
- 50+ contributors (stretch goal)

**Post-1.0 Vision:**
- Community-driven feature development
- Plugin marketplace (custom tools, stores, agents)
- Enterprise support offerings
- Conference talks and research publications

---

### 15.4.7 How to Influence the Roadmap

The roadmap is **community-driven**. Your input shapes Friday's evolution.

**Ways to influence roadmap:**

1. **GitHub Issues**
   - Feature requests with clear use cases
   - Upvote issues you care about (👍 reaction)
   - Comment with additional context or requirements

2. **GitHub Discussions**
   - Propose architectural changes
   - Discuss tradeoffs and alternatives
   - Share experiences and requirements

3. **Pull Requests**
   - Implement features you need
   - Prototype and demonstrate value
   - Prove feasibility for roadmap items

4. **Community Calls**
   - Monthly community calls (starting Q2 2026)
   - Demo your Friday projects
   - Discuss roadmap priorities
   - Voice feature needs

5. **Sponsorship**
   - Sponsor specific features (enterprise sponsorship program)
   - Fund core development
   - Prioritize your organization's needs

**Roadmap Prioritization Criteria:**

1. **Impact** - How many users benefit?
2. **Feasibility** - How difficult to implement?
3. **Alignment** - Fits Friday's vision and principles?
4. **Community demand** - How many upvotes/requests?
5. **Maintainability** - Can we support long-term?

**Request a feature:**

```markdown
# Feature Request Template

**Feature:** [Clear, concise title]

**Use Case:**
Describe the problem you're trying to solve. Who is affected?
Why is this important?

**Proposed Solution:**
How would you like this to work? Include examples.

**Alternatives Considered:**
What other approaches could solve this? Why is your proposal better?

**Additional Context:**
- Impact on your work: [Low/Medium/High]
- Willingness to contribute: [Yes/Maybe/No]
- Related issues: [Links]

**Example:**
Show what the feature would look like in practice (code, CLI commands, config).
```

---

## 15.5 Community Resources

### 15.5.1 GitHub Repository

**Repository:** `https://github.com/your-org/friday-agent-framework` (currently private)

**Status:** Private alpha. Will become public at v0.2.0 (estimated Q2 2026).

**Access:** If you're reading this documentation, you likely have access. Check your GitHub invitations.

**Repository Structure:**

- **Issues** - Bug reports, feature requests, questions
- **Discussions** - Longer-form discussions, RFCs, Q&A
- **Pull Requests** - Code contributions, reviews
- **Wiki** - Community-contributed guides and tutorials (future)
- **Releases** - Version history, changelogs, release notes
- **Projects** - Roadmap tracking, sprint planning

**Using GitHub effectively:**

**Issues:**
```bash
# Create issue
gh issue create --title "Bug: Memory decay not working" --body "..."

# List issues
gh issue list

# Search issues
gh issue list --search "memory"

# Add labels
gh issue edit 42 --add-label "bug,memory"
```

**Discussions:**
- Preferred for: Design discussions, architecture questions, use case sharing
- Format: Start with context, ask specific questions, provide examples
- Etiquette: Search before posting, stay on topic, be respectful

**Starring & Watching:**
- **Star** the repo to bookmark and show support
- **Watch** for notifications on all issues/PRs
- **Watch: Releases only** for version announcements

### 15.5.2 Issue Tracker

**Issue Types:**

1. **Bug Reports** - Something broken or not working as documented
2. **Feature Requests** - New capabilities or enhancements
3. **Documentation** - Unclear/missing documentation
4. **Questions** - How-to questions (also use Discussions)
5. **Performance** - Slowness or resource issues

**Bug Report Template:**

```markdown
## Bug Description
Clear description of what's broken.

## Expected Behavior
What should happen?

## Actual Behavior
What actually happens?

## Reproduction Steps
1. Step one
2. Step two
3. Bug occurs

## Environment
- Friday version: v0.1.0
- Python version: 3.11
- OS: macOS 14.2
- LLM provider: OpenAI (gpt-4o-mini)
- Memory stores: ChromaDB, NetworkX, SQLite

## Logs/Screenshots
```
[Paste relevant logs or attach screenshots]
```

## Minimal Reproducible Example
[Code that reproduces the bug]
```

**Feature Request Template:** (See 15.4.7)

**Issue Labels:**

| Label | Meaning |
|-------|---------|
| `bug` | Something broken |
| `feature` | New capability request |
| `documentation` | Docs improvement |
| `performance` | Speed/resource issue |
| `good-first-issue` | Beginner-friendly |
| `help-wanted` | Maintainers need help |
| `memory` | Memory system related |
| `agent` | Agent system related |
| `tools` | Tool system related |
| `priority-high` | Important, will address soon |
| `priority-low` | Nice-to-have |
| `wontfix` | Not planned (with explanation) |

**Issue Etiquette:**
- Search before creating (avoid duplicates)
- Provide complete information (use templates)
- Be respectful and patient
- Update issue if you find solutions
- Close issues when resolved

### 15.5.3 Documentation Site

**URL:** `https://docs.friday-framework.org` (planned, not yet live)

**Current Documentation:**
- User guide: `docs/guides/` in repository
- Specifications: `docs/reference/specs/` in repository
- API reference: Generated from docstrings (future)

**Documentation Improvements:**

Found unclear documentation? Please contribute:
```bash
# Edit the guide section
nano docs/guides/04-adaptive-memory.md

# Commit and push
git add docs/guides/04-adaptive-memory.md
git commit -m "docs(guides): clarify memory lifecycle promotion"
git push origin docs/memory-lifecycle-clarification

# Create PR
gh pr create --title "docs: clarify memory lifecycle promotion" --body "..."
```

**Documentation Style:**
- Clear and concise
- Code examples for every feature
- Real-world use cases
- Troubleshooting sections
- Active voice, present tense
- No jargon without explanation

### 15.5.4 Community Discussions

**GitHub Discussions** (Primary)

Categories:
- **Announcements** - Release notes, important updates
- **General** - Anything Friday-related
- **Q&A** - Ask questions, get answers
- **Show and Tell** - Share your Friday projects
- **Ideas** - Feature ideas and brainstorming
- **RFCs** - Request for Comments on major changes

**Discord Server** (Planned Q2 2026)

Channels:
- `#announcements` - Official updates
- `#general` - General chat
- `#help` - Get help from community
- `#showcase` - Show your projects
- `#development` - Contributor discussions
- `#random` - Off-topic

**Community Calls** (Planned Q2 2026)

- Monthly video calls (Zoom/Google Meet)
- Demo new features and projects
- Discuss roadmap priorities
- Q&A with maintainers
- Recorded and posted to YouTube

### 15.5.5 How to Get Help

**Priority Order:**

1. **Check documentation** - Read relevant guide sections
2. **Search issues** - Someone may have had same problem
3. **Search discussions** - Check Q&A category
4. **Ask in discussions** - Post new Q&A discussion
5. **Open issue** - If it's a bug, open issue with template
6. **Discord** (future) - Real-time help from community

**Good Questions:**
- Include context (what you're trying to do, why)
- Show what you've tried
- Provide minimal reproducible example
- Specify environment (Friday version, Python version, OS)
- Be specific (not "memory doesn't work", but "promotion not triggering after 5 accesses")

**Response Times:**
- **Critical bugs** - Within 24 hours
- **Feature requests** - Within 1 week
- **Questions** - Community response varies (usually 1-3 days)
- **Pull requests** - Initial review within 2-3 days

**Getting Faster Help:**
- Provide complete information upfront
- Include logs and error messages
- Show minimal reproducible code
- Search documentation first
- Be patient and respectful

---

## 15.6 Acknowledgments

### 15.6.1 Contributors

Friday Framework is built by a community of developers, researchers, and AI practitioners.

**Core Team:**
- [Lead contributors will be listed here as project grows]

**Contributors:**
- Thank you to everyone who has contributed code, documentation, bug reports, and ideas
- Full contributor list: `https://github.com/your-org/friday-agent-framework/graphs/contributors`

**How to get listed:**
- Code contributions (merged PRs)
- Documentation improvements
- Bug reports with quality reproduction steps
- Active participation in discussions
- Community support (answering questions)

**Hall of Fame:**
(Future: Recognize exceptional contributors)

### 15.6.2 Inspirations & Prior Art

Friday stands on the shoulders of giants. We acknowledge the research, frameworks, and ideas that inspired Friday's design.

**Research Foundations:**

- **Cognitive Science & Memory:**
  - Atkinson-Shiffrin multi-store model (1968) - Inspired three-tier memory
  - Hebb's learning rule (1949) - Foundation for hit_count reinforcement
  - Tulving's episodic/semantic memory distinction (1972) - Memory type separation

- **LLM Context Research:**
  - "Lost in the Middle" (Liu et al., 2023) - Motivated tail injection
  - "Retrieval-Augmented Generation" (Lewis et al., 2020) - Context assembly patterns
  - "Recursive Summarization" (Wu et al., 2021) - Conversation compression

- **Agent Architectures:**
  - ReAct (Yao et al., 2023) - Reasoning and Acting pattern
  - AutoGPT - Autonomous agent inspiration
  - BabyAGI - Goal-directed agent design

**Framework Inspirations:**

- **LangChain** - Demonstrated market demand for agent frameworks, chain composition patterns
- **LlamaIndex** - Document ingestion and RAG patterns
- **CrewAI** - Multi-agent collaboration concepts
- **Semantic Kernel** - Plugin architecture, planner design
- **Haystack** - Pipeline-based architecture

**Open Source Libraries:**

Friday builds on excellent open-source tools:
- **LiteLLM** - Provider-agnostic LLM client (unified API across providers)
- **ChromaDB** - Embedded vector database (semantic memory store)
- **NetworkX** - Graph library (associative memory implementation)
- **Pydantic** - Data validation (type safety throughout Friday)
- **pytest** - Testing framework
- **Ruff** - Fast Python linter/formatter
- **uv** - Modern Python package manager

**Community Influence:**

Friday's design has been shaped by:
- Community feedback on agent framework pain points
- Real-world deployment experiences shared by practitioners
- Academic research on agent memory and learning
- Enterprise requirements for production AI systems

### 15.6.3 Technologies Used

**Core Technologies:**

- **Python 3.10+** - Primary language (async/await, type hints, modern syntax)
- **SQLite** - Episodic memory (transcript storage)
- **ChromaDB** - Semantic memory (vector embeddings)
- **NetworkX** - Associative memory (knowledge graph)
- **LiteLLM** - LLM client (OpenAI, Anthropic, Google, local models)
- **Pydantic** - Data validation and settings management

**Development Tools:**

- **uv** - Package management and workspace tooling
- **pytest** - Testing framework
- **Ruff** - Linting and formatting
- **mypy** - Static type checking
- **GitHub Actions** - CI/CD (future)

**Optional Dependencies:**

- **Ollama** - Local LLM runtime
- **Docker** - Containerization and sandboxing
- **OpenTelemetry** - Distributed tracing
- **FastAPI** - API server (future HTTP API)

**Documentation:**

- **Markdown** - All documentation format
- **GitHub Pages** - Documentation hosting (future)
- **MkDocs** - Static site generator (future)

### 15.6.4 License

**Friday Framework is licensed under the MIT License.**

```
MIT License

Copyright (c) 2026 Friday Framework Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**What This Means:**

✓ **Use freely** - Commercial and non-commercial
✓ **Modify** - Change code to fit your needs
✓ **Distribute** - Share with others
✓ **Sublicense** - Include in your projects with different licenses
✓ **No warranty** - Use at your own risk

**Attribution:**
While not required, we appreciate:
- Mentioning Friday Framework in your project
- Linking to the GitHub repository
- Contributing improvements back to the community

---

## Summary: Contributing to Friday

**Getting Started:**
1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Clone repo: `git clone https://github.com/your-org/friday-agent-framework.git`
3. Install deps: `uv sync`
4. Run tests: `pytest`
5. Start contributing!

**Development Workflow:**
1. Create feature branch: `git checkout -b feat/your-feature`
2. Make changes with tests
3. Lint and format: `uv run ruff check . --fix && uv run ruff format .`
4. Run tests: `pytest -v`
5. Commit: `git commit -m "feat(scope): description"`
6. Push and create PR: `gh pr create`

**Community:**
- GitHub Issues: Bug reports, feature requests
- GitHub Discussions: Q&A, RFCs, show & tell
- Discord (planned): Real-time community chat
- Monthly calls (planned): Demos and roadmap discussions

**Roadmap:**
- **v0.1.0** (Current): Core memory, agents, tools, orchestration, workflows
- **Phase 5** (Q1-Q2 2026): Autonomy, sandboxing, distributed deployment
- **Phase 6** (Q2-Q3 2026): Self-improving agents, meta-learning
- **Phase 7** (Q3-Q4 2026): MCP, templates, enterprise integrations
- **v1.0** (Q1 2027): Production-ready, public release

**Resources:**
- Documentation: `docs/guides/` in repository
- Specifications: `docs/reference/specs/` for architectural details
- ADRs: Design decisions and rationale
- CLAUDE.md: Guidance for Claude Code when working with Friday

**Principles:**
- **Protocol-first design** - Swappable implementations, zero lock-in
- **Radical transparency** - All decisions documented (ADRs)
- **Community-driven** - Roadmap shaped by users and contributors
- **Production-ready** - Enterprise-grade from day one

**Welcome to Friday!** We're building the future of AI agents together. Your contributions—code, documentation, ideas, questions—make Friday better for everyone.

Join us. Build memory-persistent agents that genuinely learn and grow.

---

**Next:** Ready to build? Return to [Section 2: Getting Started](02-getting-started.md) to create your first Friday agent, or dive into [Section 3: Core Concepts](03-core-concepts.md) to understand the architecture.

**Questions?** See [Section 13: Troubleshooting & FAQ](13-troubleshooting.md) or open a discussion on GitHub.

**Happy Contributing!**
