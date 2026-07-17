# Friday Agent Framework
## Getting Started: Your First Friday Agent

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24

---

## Overview

This guide will have you running a memory-persistent Friday agent in **under 15 minutes**. You'll:

1. Install Friday from PyPI
2. Configure a basic agent with your choice of LLM provider
3. Run your first conversation
4. Verify memory persistence across sessions
5. Explore the interactive CLI

By the end, you'll have a working Friday agent that remembers conversations, learns from interactions, and demonstrates genuine memory persistence.

---

## Prerequisites

### System Requirements
- **Python 3.10 or higher** (3.11+ recommended)
- **4GB RAM minimum** (16+GB recommended for local LLMs)
- **macOS, Linux, or Windows** (WSL2 recommended for Windows)
- **Internet connection** (for cloud LLM providers) or local Ollama instance

### Required Knowledge
- Basic Python experience (ability to run scripts, understand basic syntax)
- Familiarity with terminal/command line
- API keys for your chosen LLM provider (or Ollama installed locally)

### LLM Provider Options

You'll need **at least one** of the following:

**Cloud Providers (Recommended for Getting Started):**
- **OpenAI**: Get API key from [platform.openai.com](https://platform.openai.com) - Models: GPT-4o, GPT-4o-mini
- **Anthropic**: Get API key from [console.anthropic.com](https://console.anthropic.com) - Models: Claude 3.5 Sonnet, Claude 3 Haiku
- **Google AI**: Get API key from [ai.google.dev](https://ai.google.dev) - Models: Gemini 2.5 Pro, Gemini 2.5 Flash
- **OpenRouter**: Get API key from [openrouter.ai](https://openrouter.ai) - Access to 100+ models with single key

**Local Option (No API Keys Required):**
- **Ollama**: Install from [ollama.ai](https://ollama.ai) - Models: Llama 3, Mistral, and more
  - Requires 8GB+ RAM, GPU recommended but not required
  - Run: `ollama pull llama3` to download model

---

## Installation

### Option 1: Install from PyPI (Recommended)

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

# For sandbox isolation (Docker-based, Phase 5)
# pip install friday-sandbox  # Coming soon
```

### Option 2: Install from Source (Development)

**Note:** The GitHub repository is currently private. Access requires authorization.

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

**The repository will become public at v0.2.0 release.**

### Verify Installation

```bash
python -c "from friday_agent import CopilotAgent, AgentOrchestrator, WorkflowEngine; print('✓ Friday is ready')"
```

If you see `✓ Friday is ready`, installation succeeded!

---

## Quick Start: First Agent in 5 Minutes

Let's create your first Friday agent with minimal configuration.

### Step 1: Set Your API Key

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

### Step 2: Create a Basic Configuration

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

**That's it!** This is all you need to get started.

### Step 3: Create Your First Agent Script

Create a file `my_first_agent.py`:

```python
#!/usr/bin/env python3
"""
My First Friday Agent - A minimal example demonstrating memory persistence.
"""

import asyncio
from pathlib import Path

from friday_agent import CopilotAgent
from friday_llm import LiteLLMService
from friday_memory import (
    ChromaVectorStore,
    ElementXGraphStore,
    MemoryController,
    ContextAssembler,
    PromptArchitect,
)
from friday_transcript import SQLiteTranscriptStore


async def main():
    """Run a simple Friday agent with memory."""

    # Configuration
    storage_path = Path("./friday_data")
    storage_path.mkdir(exist_ok=True)

    session_id = "demo_session"
    user_id = "demo_user"

    # Initialize LLM (uses OPENAI_API_KEY from environment)
    llm = LiteLLMService(
        model="gpt-4o-mini",  # Change to your preferred model
        temperature=0.7,
    )

    # Initialize memory stores
    vector_store = ChromaVectorStore(
        persist_directory=storage_path / "vector",
        collection_name="friday_memories",
    )

    graph_store = ElementXGraphStore(
        storage_path=storage_path / "graph.json"
    )

    transcript_store = SQLiteTranscriptStore(
        db_path=storage_path / "transcripts.db"
    )

    # Initialize memory controller
    controller = MemoryController(
        vector_store=vector_store,
        graph_store=graph_store,
        transcript_store=transcript_store,
        llm_client=llm,  # For entity extraction
    )

    # Initialize context engineering
    assembler = ContextAssembler(
        controller=controller,
        session_id=session_id,
        user_id=user_id,
    )

    architect = PromptArchitect(
        system_prompt="You are Friday, a helpful AI assistant with persistent memory.",
        total_tokens=8000,
        history_tokens=2000,
        context_tokens=4000,
    )

    # Create the agent
    agent = CopilotAgent(
        llm=llm,
        controller=controller,
        assembler=assembler,
        architect=architect,
        session_id=session_id,
        user_id=user_id,
    )

    print("=" * 60)
    print("FRIDAY AGENT - First Run Demo")
    print("=" * 60)
    print(f"Session: {session_id}")
    print(f"Storage: {storage_path}")
    print(f"Model: {llm.model}")
    print("=" * 60)
    print()

    # First conversation
    print("You: Hello Friday! My name is Alice, and I'm working on a Python project.")
    response1 = await agent.chat(
        "Hello Friday! My name is Alice, and I'm working on a Python project."
    )
    print(f"Friday: {response1}")
    print()

    # Second conversation
    print("You: What technologies should I use for building a web API?")
    response2 = await agent.chat(
        "What technologies should I use for building a web API?"
    )
    print(f"Friday: {response2}")
    print()

    # Third conversation - test memory
    print("You: Can you remind me what I told you about myself?")
    response3 = await agent.chat(
        "Can you remind me what I told you about myself?"
    )
    print(f"Friday: {response3}")
    print()

    print("=" * 60)
    print("✓ Session complete. Memory has been saved.")
    print(f"✓ To verify persistence, run this script again.")
    print(f"✓ Check {storage_path} for stored memories.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
```

### Step 4: Run Your First Agent

```bash
# Make the script executable
chmod +x my_first_agent.py

# Run it
python my_first_agent.py
```

**Expected output:**
```
============================================================
FRIDAY AGENT - First Run Demo
============================================================
Session: demo_session
Storage: ./friday_data
Model: gpt-4o-mini
============================================================

You: Hello Friday! My name is Alice, and I'm working on a Python project.
Friday: Hello Alice! It's great to meet you. I'm Friday, and I'm here to help
with your Python project. What are you building?

You: What technologies should I use for building a web API?
Friday: For a Python web API, I'd recommend FastAPI or Flask. FastAPI is modern,
fast, and has great automatic documentation. Flask is simpler and more flexible...

You: Can you remind me what I told you about myself?
Friday: You told me your name is Alice and that you're working on a Python project.
You also asked about technologies for building a web API, which suggests you're
interested in backend development.

============================================================
✓ Session complete. Memory has been saved.
✓ To verify persistence, run this script again.
✓ Check ./friday_data for stored memories.
============================================================
```

**Friday remembered your name and context!** But the real test is persistence across sessions...

### Step 5: Verify Memory Persistence

**Exit the script completely**, then run it again with a new conversation:

```python
# Modify the conversation in my_first_agent.py to test memory:
print("You: Hi Friday, do you remember me?")
response = await agent.chat("Hi Friday, do you remember me?")
print(f"Friday: {response}")
```

Run again:
```bash
python my_first_agent.py
```

**Friday will remember you're Alice and that you're working on a Python project!** This is genuine persistence—the memory system loaded your prior context from disk.

### Step 6: Inspect the Memory Stores

Check what Friday stored:

```bash
# Vector store (ChromaDB)
ls -lh ./friday_data/vector/

# Graph store (NetworkX + JSON)
cat ./friday_data/graph.json | jq '.entities | length'  # Count entities

# Transcript store (SQLite)
sqlite3 ./friday_data/transcripts.db "SELECT COUNT(*) FROM turns;"
```

You'll see:
- ChromaDB collections with embedded memories
- JSON graph with entities (Alice, Python, web API)
- SQLite database with full conversation turns

**Congratulations!** You've created a memory-persistent Friday agent.

---

## Interactive CLI: The Full Experience

The script above demonstrates the basics, but Friday includes a full-featured interactive CLI for exploration and testing.

### Run the Reference CLI

Friday includes `memory-chat-v2.py` as a reference implementation:

```bash
# If installed from source
cd tests/integration/memory
python memory-chat-v2.py --config config.yaml

# Or create your own based on the template
```

### Essential Commands

Once in the interactive CLI:

```bash
# Memory inspection
/memory              # Show memory statistics
/entities            # List entities in knowledge graph
/facts               # List insights from vector store
/context             # Show current context payload

# Session management
/history             # Show conversation history
/clear               # Clear current conversation
/reset               # Complete memory wipe (requires confirmation)

# Configuration
/vars                # Show scoped variables
/set user:name Alice # Store persistent user preference

# Help
/help                # List all commands
/help memory         # Detailed help for specific command
```

### Example Interactive Session

```
Friday Agent CLI v2
Type your message or /help for commands.

> Hello Friday! My name is Bob and I'm learning about AI agents.

Friday: Hello Bob! It's wonderful to meet you. I'm Friday, an AI assistant
with persistent memory. I'm excited to help you learn about AI agents...

> /entities

==============================================================
ENTITIES (2)
==============================================================
  Bob (Person)
    Description: User learning about AI agents
    Hit Count: 1
    Relationships: 0

  AI Agents (Technology)
    Description: Topic of interest
    Hit Count: 1
    Relationships: 1 (Bob LEARNING_ABOUT AI Agents)

> What are the key components of an AI agent?

Friday: Based on my own architecture, key components include:
1. Memory systems (episodic, semantic, associative)
2. Tool integration for external actions
3. Context assembly and prompt engineering...

> /memory

==============================================================
MEMORY STATISTICS
==============================================================
Vector Store:
  Short-term: 2 insights
  Long-term: 0 insights
  Decayed: 0 insights

Graph Store:
  Entities: 5 (2 Person, 2 Technology, 1 Concept)
  Relationships: 3

Episodic Store:
  Current session: 3 turns
  Total tokens: 1,247

> exit

Goodbye! Your memories have been saved.
```

---

## What Just Happened?

Let's break down what Friday did during your first session:

### 1. **Conversation Processing**
- Received your message via the `CopilotAgent`
- Assembled context from memory stores (empty on first run)
- Generated response using your configured LLM
- Returned natural language response

### 2. **Memory Extraction** (Background)
- Identified entities: "Alice" (Person), "Python" (Technology), "web API" (Technology)
- Extracted relationships: Alice WORKING_ON Python, Alice INTERESTED_IN web API
- Generated insights: "User prefers Python for development", "User needs web API guidance"
- Stored in vector store with embeddings for semantic search

### 3. **Knowledge Graph Building**
- Created entity nodes with types and descriptions
- Connected entities with semantic relationships
- Incremented hit counts (Hebbian learning starts)
- Persisted graph to JSON file

### 4. **Transcript Logging**
- Saved complete turn to SQLite database
- Captured: user message, assistant response, timestamp, token usage
- Enabled session replay and audit trails

### 5. **Context Priming** (Next Session)
- On restart, loaded top entities by hit count (Alice, Python)
- Retrieved recent insights from vector store
- Reconstructed context without explicit "remember when..."

**This is the Memory Loop in action**: conversation → extraction → storage → retrieval → context.

---

## Next Steps: Expanding Your Agent

Now that you have a working Friday agent, explore these enhancements:

### 1. Add Tools

Give Friday the ability to interact with systems:

```python
from friday_tools import (
    ReadFileTool,
    WriteFileTool,
    WebSearchTool,
    GitStatusTool,
)

# Register tools with the agent
agent.register_tools([
    ReadFileTool(),
    WriteFileTool(),
    WebSearchTool(),
    GitStatusTool(),
])
```

Now Friday can read files, write code, search the web, and check git status!

### 2. Configure Multi-Agent Orchestration

Create specialized agents that collaborate:

```python
from friday_agent import AgentOrchestrator, AgentProfile

# Define agent profiles
researcher = AgentProfile(
    name="researcher",
    role="Research Analyst",
    goal="Find and synthesize information",
    tools=["web_search", "read_file"],
)

coder = AgentProfile(
    name="coder",
    role="Software Developer",
    goal="Write and review code",
    tools=["read_file", "write_file", "git_status"],
)

# Create orchestrator
orchestrator = AgentOrchestrator(
    controller=controller,
    session_id=session_id,
    user_id=user_id,
)

orchestrator.register_agent(researcher)
orchestrator.register_agent(coder)

# Delegate tasks
research_result = await orchestrator.delegate(
    "researcher",
    "Find the latest best practices for FastAPI development"
)

code_result = await orchestrator.delegate(
    "coder",
    "Create a basic FastAPI endpoint structure based on the research"
)
```

### 3. Create YAML Workflows

Define multi-step workflows with approval gates:

```yaml
# workflow.yaml
name: "API Development Workflow"
tasks:
  - id: research
    agent: researcher
    description: "Research FastAPI best practices"
    outputs: ["best_practices"]

  - id: design
    agent: coder
    description: "Design API structure based on research"
    inputs:
      research: "$best_practices"
    outputs: ["api_design"]
    depends_on: [research]

  - id: approval
    description: "Review API design"
    requires_approval: true
    depends_on: [design]

  - id: implement
    agent: coder
    description: "Implement the approved design"
    inputs:
      design: "$api_design"
    depends_on: [approval]
```

Run workflows via CLI:
```bash
/workflow run api_development topic="User authentication"
/workflow approve  # When prompted
```

### 4. Use Local Models for Privacy

Switch to Ollama for local, private execution:

```yaml
# config.yaml
llm:
  model: "ollama/llama3"
  base_url: "http://localhost:11434"

embedding:
  model: "nomic-embed-text"
  base_url: "http://localhost:11434"
```

Now all LLM calls and embeddings run locally—no cloud API calls, no data leaves your machine.

### 5. Customize Memory Lifecycle

Tune memory decay and promotion for your use case:

```yaml
# config.yaml
memory:
  lifecycle:
    decay_rate: 0.01              # How fast memories fade (0.01 = ~79% after 24h)
    promotion_threshold: 0.7       # Minimum score for long-term promotion
    promotion_min_age_hours: 24    # Minimum time in short-term before promotion
    auto_lifecycle: true           # Run lifecycle after each turn
```

---

## Common Issues & Solutions

### Issue: "ImportError: No module named 'friday_agent'"

**Solution:**
```bash
# Verify installation
pip list | grep friday

# Reinstall if needed
pip install --upgrade friday-agent
```

### Issue: "API key not found" or "Authentication failed"

**Solution:**
```bash
# Verify environment variable is set
echo $OPENAI_API_KEY

# Re-export with correct key
export OPENAI_API_KEY="sk-..."

# Check the key is visible to Python
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Issue: "Context length exceeded"

**Solution:** Reduce token budgets in config:
```yaml
memory:
  total_tokens: 8000    # Reduce if using models with smaller context windows
  history_tokens: 1000  # Reduce conversation history
  context_tokens: 2000  # Reduce retrieved memories
```

### Issue: "ChromaDB SQLite error" or "Database locked"

**Solution:** ChromaDB occasionally has SQLite locking issues. Fix:
```bash
# Remove ChromaDB lock file
rm -rf ./friday_data/vector/*.sqlite3-*

# Restart the agent
```

### Issue: Memory not persisting across sessions

**Solution:** Verify storage path consistency:
```python
# Use absolute paths
storage_path = Path("/absolute/path/to/friday_data")

# Check the path exists and has write permissions
storage_path.mkdir(parents=True, exist_ok=True)
```

---

## Understanding the Code

Let's break down the minimal agent script:

### LLM Initialization
```python
llm = LiteLLMService(
    model="gpt-4o-mini",
    temperature=0.7,
)
```
- `LiteLLMService` wraps LiteLLM for provider-agnostic LLM calls
- Automatically uses `OPENAI_API_KEY` from environment
- Works with OpenAI, Anthropic, Google, Ollama, and 100+ models

### Memory Stores
```python
vector_store = ChromaVectorStore(...)  # Semantic memory
graph_store = ElementXGraphStore(...)  # Associative memory
transcript_store = SQLiteTranscriptStore(...)  # Episodic memory
```
- **ChromaDB**: Stores embeddings for similarity search
- **NetworkX**: Stores entities and relationships as a graph
- **SQLite**: Stores full conversation transcripts

### Memory Controller
```python
controller = MemoryController(
    vector_store=vector_store,
    graph_store=graph_store,
    transcript_store=transcript_store,
    llm_client=llm,
)
```
- **Unified interface** to all three memory stores
- Handles extraction (entities, relationships, insights)
- Manages lifecycle (promotion, decay, reactivation)

### Context Engineering
```python
assembler = ContextAssembler(...)  # Retrieves relevant memories
architect = PromptArchitect(...)   # Formats prompts with token budgeting
```
- **Assembler**: Queries stores, applies knapsack optimization
- **Architect**: Structures messages for LLM with "lost in middle" mitigation

### Agent Execution
```python
agent = CopilotAgent(...)
response = await agent.chat("Your message here")
```
- **Re-Act loop**: Reason → Act → Observe (with tool support)
- **Automatic memory**: Extraction and storage happen transparently
- **Streaming support**: Can stream responses in real-time

---

## Configuration Deep Dive

Your `config.yaml` controls Friday's behavior. Here's what each section does:

### LLM Configuration
```yaml
llm:
  model: "gpt-4o-mini"        # Model identifier
  temperature: 0.7             # 0=deterministic, 2=very creative
  max_tokens: 4000            # Response length limit
  timeout_seconds: 60         # Request timeout
  max_retries: 3              # Retry with exponential backoff
```

### Memory Configuration
```yaml
memory:
  storage_path: "./friday_data"  # Where to persist memory

  # Token budgeting (must fit in model's context window)
  total_tokens: 8000
  system_prompt_tokens: 1000
  history_tokens: 2000
  context_tokens: 4000
  query_tokens: 500

  # Context assembly
  max_history_turns: 10         # Conversation history depth
  context_format: "plain"       # plain, json, xml, markdown
```

### Lifecycle Configuration
```yaml
memory:
  lifecycle:
    enabled: true
    decay_rate: 0.01                 # Lambda for exponential decay
    promotion_threshold: 0.7         # Score needed for long-term
    promotion_min_age_hours: 24      # Minimum time before promotion
    decay_threshold_turns: 3         # Decay after N turns without access
```

### Extraction Configuration
```yaml
extraction:
  enabled: true
  llm:
    model: "gpt-4o-mini"      # Separate model for extraction
    temperature: 0.3          # Lower temp for consistent extraction
  confidence_threshold: 0.6   # Minimum extraction confidence
```

---

## What's Next?

You now have a working Friday agent with persistent memory. Ready to go deeper?

**Continue to:**
- **[Section 3: Core Concepts & Architecture](03-core-concepts.md)** - Understand how Friday works under the hood
- **[Section 4: Adaptive Memory](04-adaptive-memory.md)** - Master the three-tier memory system
- **[Section 5: Tools](05-tools.md)** - Give Friday the ability to interact with systems
- **[Section 9: CLI Reference](09-cli-reference.md)** - Complete command documentation

**Or explore:**
- **[Section 7: Multi-Agent Orchestration](07-multi-agent.md)** - Build agent teams
- **[Section 8: Workflows](08-workflows.md)** - Create automated task graphs
- **[Section 12: Use Cases](12-use-cases.md)** - Real-world examples

**Or jump to:**
- **[Section 10: Configuration Guide](10-configuration.md)** - Complete YAML reference
- **[Section 11: Advanced Topics](11-advanced-topics.md)** - Optimization and deployment

---

## Quick Reference

### Minimal Agent (10 lines)
```python
from friday_agent import CopilotAgent
from friday_llm import LiteLLMService
from friday_memory import MemoryController, ContextAssembler, PromptArchitect

llm = LiteLLMService(model="gpt-4o-mini")
controller = MemoryController.create_default("./friday_data", llm)
assembler = ContextAssembler(controller, "session_1", "user_1")
architect = PromptArchitect("You are Friday.", total_tokens=8000)
agent = CopilotAgent(llm, controller, assembler, architect, "session_1", "user_1")

response = await agent.chat("Hello Friday!")
```

### Essential CLI Commands
```bash
/memory              # Memory statistics
/context             # Current context payload
/entities            # Knowledge graph entities
/help                # Command reference
/reset               # Complete memory wipe
```

### Essential Config Sections
```yaml
llm:
  model: "gpt-4o-mini"
  temperature: 0.7

memory:
  storage_path: "./friday_data"
  total_tokens: 8000
```

---

**You're ready to build memory-persistent AI agents with Friday!**

*Questions? See [Section 13: Troubleshooting & FAQ](13-troubleshooting.md)*
*Want to contribute? See [Section 15: Contributing & Community](15-contributing.md)*
