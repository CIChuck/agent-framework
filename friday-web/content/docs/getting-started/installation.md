---
title: "Installation"
description: "Install Friday Framework and its dependencies using uv or pip."
weight: 1
---

Install Friday Framework using `uv` (recommended) or `pip`, then configure your environment variables to connect to your LLM provider.

---

## Option 1: Install from PyPI (Recommended)

Friday is available on PyPI. Install using `pip` or `uv`:

```bash
# Using pip
pip install friday-agent

# Or using uv (faster, recommended)
uv pip install friday-agent
```

This installs all core Friday packages:

- `friday-core` - Abstract protocols
- `friday-memory` - Memory system with lifecycle management
- `friday-llm` - LLM client with resilience patterns
- `friday-agent` - Agent implementations and orchestration
- `friday-tools` - 50+ built-in tools
- `friday-transcript` - Conversation logging

**Optional packages** (install separately if needed):

```bash
# For MCP (Model Context Protocol) support
pip install friday-mcp
```

---

## Option 2: Install from Source (Development)

{{< callout type="info" >}}
The GitHub repository is currently private. Access requires authorization. The repository will become public at the v0.2.0 release.
{{< /callout >}}

```bash
# Clone the repository (requires access)
git clone https://github.com/your-org/friday-agent-framework.git
cd friday-agent-framework

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies (uses uv workspaces)
uv sync

# Verify installation
uv run python -c "from friday_agent import CopilotAgent; print('Friday installed successfully!')"
```

---

## Verify Installation

```bash
python -c "from friday_agent import CopilotAgent, AgentOrchestrator, WorkflowEngine; print('Friday is ready')"
```

If you see `Friday is ready`, installation succeeded.

---

## Configure Your API Keys

Choose **one** provider and set the environment variable:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GOOGLE_API_KEY="..."

# OpenRouter (access to 100+ models)
export OPENROUTER_API_KEY="sk-or-..."

# Ollama (local, no key needed)
# Just ensure Ollama is running: ollama serve
```

**For persistent configuration**, add to your shell profile (`~/.bashrc`, `~/.zshrc`):

```bash
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
source ~/.zshrc
```

---

## Create a Basic Configuration File

Create a file `config.yaml` in your project directory:

```yaml
# Minimal Friday configuration
llm:
  # Choose your provider (uncomment one)
  model: "gpt-4o-mini"              # OpenAI (fast, cheap)
  # model: "claude-3-haiku"         # Anthropic (fast, cheap)
  # model: "gemini-2.5-flash"       # Google (fast, cheap)
  # model: "ollama/llama3"          # Local (free, requires Ollama)

  temperature: 0.7
  max_tokens: 4000

memory:
  # Where to store persistent memory
  storage_path: "./friday_data"

  # Token budget for context window
  total_tokens: 8000
  history_tokens: 2000
  context_tokens: 4000

chat:
  user_name: "You"
  assistant_name: "Friday"

# Basic logging
logging:
  level: "INFO"
```

That's all you need to get started.

---

## Common Issues

### "ImportError: No module named 'friday_agent'"

```bash
# Verify installation
pip list | grep friday

# Reinstall if needed
pip install --upgrade friday-agent
```

### "API key not found" or "Authentication failed"

```bash
# Verify environment variable is set
echo $OPENAI_API_KEY

# Re-export with correct key
export OPENAI_API_KEY="sk-..."

# Check the key is visible to Python
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

### "ChromaDB SQLite error" or "Database locked"

ChromaDB occasionally has SQLite locking issues. Fix:

```bash
# Remove ChromaDB lock file
rm -rf ./friday_data/vector/*.sqlite3-*

# Restart the agent
```

### Memory not persisting across sessions

```python
# Use absolute paths
from pathlib import Path
storage_path = Path("/absolute/path/to/friday_data")

# Check the path exists and has write permissions
storage_path.mkdir(parents=True, exist_ok=True)
```

---

## Next Step

With Friday installed and your API key configured, continue to the [Quick Start](/docs/getting-started/quick-start/) guide to build and run your first memory-persistent agent.
