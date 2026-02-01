# Build Plan: Promote Memory-Chat-V2 to Friday-Copilot

**Status:** Planned
**Target:** Phase 0 (Immediate Execution)
**Objective:** Promote the `memory-chat-v2` integration test into a first-class application named `friday-copilot` living in `apps/friday-copilot`.

---

## 1. Overview

`memory-chat-v2.py` has evolved into the de-facto reference implementation of the Friday Framework. It contains rich features (Lifecycle, Reorganization, Tools, Orchestration, Workflows) that are not present in the skeleton `friday-cli`.

We will promote this script to a standalone application package: **Friday-Copilot**.

### 1.1 Architecture

| Attribute | Value |
|-----------|-------|
| **Package Name** | `friday-copilot` |
| **Location** | `apps/friday-copilot` |
| **Entry Point** | `friday-copilot` command |
| **Python Module** | `friday_copilot` |

**Dependencies:**
- `friday-core` - Protocols, config, logging, telemetry
- `friday-memory` - Memory stores, context assembly, lifecycle
- `friday-llm` - LiteLLM wrapper for multi-provider LLM calls
- `friday-agent` - Orchestrator, workflows, tool registry
- `friday-tools` - Filesystem, utility, shell tools
- `friday-transcript` - Session transcript storage and export
- `friday-cli` - Shared library for CLI display/session components (now in `packages/`)
- `platformdirs` - Cross-platform XDG-compliant paths

---

## 2. Implementation Steps

### 2.1 Scaffold Application Structure

Create directory structure:

```
apps/friday-copilot/
├── pyproject.toml
├── README.md
├── src/
│   └── friday_copilot/
│       ├── __init__.py
│       ├── main.py              # Entry point (was memory-chat-v2.py)
│       ├── bootstrap.py         # Config/path initialization
│       └── resources/
│           └── default_config.yaml
└── tests/
    ├── __init__.py
    ├── test_bootstrap.py
    └── test_commands.py
```

### 2.2 Migrate Code

1. **Copy Source (Do Not Delete):** Copy `tests/integration/memory/memory-chat-v2.py` to `apps/friday-copilot/src/friday_copilot/main.py`.
   - **CRITICAL:** The source file in `tests/integration/memory/` MUST remain untouched. It serves as the baseline for regression testing.

2. **Update Imports:** Ensure all imports resolve correctly (relative imports might need adjustment if logic is split, but for a single-file move, it should be fine).

3. **Refactor Main:**
   - Rename `main()` to `async_main()`.
   - Create `run_app()` wrapper: `def run_app(): asyncio.run(async_main())`.
   - Remove `if __name__ == "__main__":` block (handled by entry point).

### 2.3 Bootstrap & Configuration

The current script hardcodes paths like `./vector`. We need robust cross-platform initialization.

**Create `bootstrap.py` module:**

```python
from pathlib import Path
from platformdirs import user_data_dir, user_config_dir, user_log_dir
import importlib.resources

def get_friday_paths() -> dict[str, Path]:
    """Return cross-platform paths for Friday data."""
    return {
        "config_dir": Path(user_config_dir("friday")),
        "data_dir": Path(user_data_dir("friday")),
        "log_dir": Path(user_log_dir("friday")),
    }

def bootstrap_config() -> Path:
    """Ensure config exists, copying defaults if needed."""
    paths = get_friday_paths()
    config_path = paths["config_dir"] / "config.yaml"

    if not config_path.exists():
        paths["config_dir"].mkdir(parents=True, exist_ok=True)
        # Copy from package resources
        default_config = importlib.resources.files("friday_copilot.resources").joinpath("default_config.yaml")
        config_path.write_text(default_config.read_text())

    return config_path

def bootstrap_data_dir() -> Path:
    """Ensure data directory exists."""
    paths = get_friday_paths()
    data_dir = paths["data_dir"]
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def bootstrap_log_dir() -> Path:
    """Ensure log directory exists."""
    paths = get_friday_paths()
    log_dir = paths["log_dir"]
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir
```

**Required Code Changes in `main.py`:**

1. **Config Loading:**
   - Replace simple `load_config` with `bootstrap_config()`.
   - Use `platformdirs` for cross-platform paths.

2. **Persistence Directory:**
   - Current: `Path(__file__).parent / "vector"` (relative to script)
   - New: `user_data_dir("friday") / "vector"` (XDG Data)

3. **Export Directory:**
   - Current: `./exports`
   - New: `user_data_dir("friday") / "exports"`

4. **Logging:**
   - Update logging configuration to write to `user_log_dir("friday") / "friday.log"`.
   - Ensure the directory exists before adding the FileHandler.

### 2.4 Default Config Sanitization

Create `resources/default_config.yaml` with:

1. **Placeholder API keys** (never commit real keys):
   ```yaml
   llm:
     model: "openrouter/anthropic/claude-sonnet-4"
     api_base: "https://openrouter.ai/api/v1"
     api_key: "${OPENROUTER_API_KEY}"  # Set via environment variable
   ```

2. **Environment variable references** where supported.

3. **Safe defaults:**
   - Local embedding model (LM Studio)
   - Reasonable token budgets
   - Conservative lifecycle settings

4. **Comments explaining each required key.**

### 2.5 Dependency Management

Create `apps/friday-copilot/pyproject.toml`:

```toml
[project]
name = "friday-copilot"
version = "0.1.0"
description = "Friday Copilot - Full-featured AI assistant with persistent memory"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "Friday Team" }]
keywords = ["ai", "assistant", "memory", "agents"]

dependencies = [
    "friday-core",
    "friday-memory",
    "friday-llm",
    "friday-agent",
    "friday-tools",
    "friday-transcript",
    "friday-cli",
    "platformdirs>=4.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[project.scripts]
friday-copilot = "friday_copilot.main:run_app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/friday_copilot"]

[tool.uv.sources]
friday-core = { workspace = true }
friday-memory = { workspace = true }
friday-llm = { workspace = true }
friday-agent = { workspace = true }
friday-tools = { workspace = true }
friday-transcript = { workspace = true }
friday-cli = { workspace = true }

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

### 2.6 Runtime Environment

After the first run, the user's environment will look like this:

| Platform | Config | Data | Logs |
|----------|--------|------|------|
| **Linux** | `~/.config/friday/` | `~/.local/share/friday/` | `~/.local/state/friday/` |
| **macOS** | `~/Library/Application Support/friday/` | `~/Library/Application Support/friday/` | `~/Library/Logs/friday/` |
| **Windows** | `%APPDATA%\friday\` | `%LOCALAPPDATA%\friday\` | `%LOCALAPPDATA%\friday\logs\` |

**Data directory contents:**
- `transcript.db` - SQLite database for conversation history
- `graph.json` - Knowledge graph storage
- `vector/` - ChromaDB files for semantic memory
- `exports/` - Transcript exports (CSV, JSONL, Markdown)
- `reorganization_logs/` - Memory maintenance logs

---

## 3. Feature Inventory

The following features from `memory-chat-v2` must be preserved:

### 3.1 Core Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/exit`, `/quit` | Exit the chat |
| `/clear` | Clear conversation history |
| `/history` | Show conversation history |
| `/memory` | Show memory statistics |
| `/context [--debug]` | Show context payload |
| `/prompt` | Show full formatted prompt sent to LLM |
| `/prime` | Load and show primed context |
| `/debug` | Show debug info from context assembly |

### 3.2 Memory Commands

| Command | Description |
|---------|-------------|
| `/entities` | List graph entities and relationships |
| `/facts` | List all documents from vector store |
| `/insights` | List only insights (type='insight') |
| `/summaries` | List only turn summaries |
| `/meta` | List meta insights from synthesis |
| `/sessions` | List all stored transcript sessions |
| `/transcript [id]` | Show transcript for session |
| `/transcript export` | Export entire database to CSV |
| `/export [format]` | Export current session (jsonl, markdown, training) |
| `/reset` | Clear all memory stores and archive transcripts |

### 3.3 Memory Lifecycle Commands

| Command | Description |
|---------|-------------|
| `/reorganize [opts]` | Run memory reorganization (analyze, prune, synthesize) |
| `/migrate [opts]` | Migrate existing memories to lifecycle metadata |
| `/lifecycle [opts]` | Run memory lifecycle cycle (promotion, decay, reactivation) |

### 3.4 Tool Commands

| Command | Description |
|---------|-------------|
| `/tools [category]` | List available tools |
| `/run-tool <name> [json]` | Execute a tool with optional JSON parameters |
| `/inject-tools <names>` | Inject tools into context for testing |
| `/clear-tools` | Clear all injected tools from context |
| `/recommend-tools <query>` | Test tool recommendations for a query |
| `/tool-budget` | Show tool token budget information |
| `/read <path>` | Read file with smart format detection |
| `/ingest <path>` | Ingest file content into vector memory |

### 3.5 Variable Commands

| Command | Description |
|---------|-------------|
| `/vars` | Show scoped variables |
| `/set <key> <val>` | Set a scoped variable |

### 3.6 Orchestration Commands (Phase 3 - Project Hive)

| Command | Description |
|---------|-------------|
| `/switch [agent]` | Switch to agent or show current agent status |
| `/agents` | List available agents with capabilities |
| `/agent [name]` | Show detailed agent information |
| `/delegate <agent> <task>` | Delegate task to another agent |
| `/status` | Show orchestrator status |
| `@agent_name <msg>` | Direct routing to specific agent |

### 3.7 Workflow Commands (Phase 4 - Project Hive)

| Command | Description |
|---------|-------------|
| `/workflow list` | List available workflows |
| `/workflow run <name> [inputs]` | Execute a workflow |
| `/workflow status` | Show current workflow status |
| `/workflow approve` | Approve pending task |
| `/workflow skip` | Skip pending task |

---

## 4. Verification Plan

### 4.1 Installation

```bash
uv sync
```

### 4.2 Execution

```bash
uv run friday-copilot
```

**Expected:** Starts up, uses defaults or prompts for missing config.

### 4.3 Command Verification Checklist

| Category | Commands to Test | Expected Result |
|----------|------------------|-----------------|
| **Help** | `/help` | Shows all command categories |
| **Memory** | `/memory`, `/entities`, `/facts` | Shows statistics/data |
| **Context** | `/context`, `/prompt`, `/prime` | Shows context info |
| **Transcript** | `/history`, `/sessions` | Shows conversation data |
| **Tools** | `/tools`, `/tool-budget` | Lists tools and budget |
| **Lifecycle** | `/lifecycle --dry-run` | Reports what would change |
| **Orchestration** | `/agents`, `/status` | Shows agent info |
| **Workflows** | `/workflow list` | Lists available workflows |

### 4.4 Persistence Check

1. Create a memory (have a conversation).
2. Exit with `/exit`.
3. Restart app.
4. Verify memory recall works.

### 4.5 Path Verification

```bash
# Verify XDG-compliant paths are used
ls ~/.config/friday/           # Linux
ls ~/Library/Application\ Support/friday/  # macOS
```

---

## 5. Exit Criteria

- [ ] `friday-copilot` is executable via command line
- [ ] All 50+ commands from Section 3 function correctly
- [ ] Cross-platform paths work (Linux, macOS, Windows)
- [ ] Default config is created on first run (no API keys hardcoded)
- [ ] Memory persistence works across sessions
- [ ] `memory-chat-v2.py` in `tests/integration/memory/` remains untouched
- [ ] All imports resolve correctly (no import errors)
- [ ] `uv sync` succeeds with no dependency issues

---

## 6. Rollback Plan

If issues arise:

```bash
# Remove the app directory
rm -rf apps/friday-copilot

# Regenerate lock file
uv sync
```

The original `memory-chat-v2.py` remains functional as the baseline.
