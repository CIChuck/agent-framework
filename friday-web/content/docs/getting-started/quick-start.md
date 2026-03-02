---
title: "Quick Start"
description: "Build and run your first Friday agent in under 5 minutes."
weight: 2
---

This guide walks you through creating and running your first Friday agent from scratch in under five minutes.

---

## Step 1: Create Your First Agent Script

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
    print("Session complete. Memory has been saved.")
    print(f"To verify persistence, run this script again.")
    print(f"Check {storage_path} for stored memories.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Step 2: Run Your First Agent

```bash
python my_first_agent.py
```

**Expected output:**

```text
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
Session complete. Memory has been saved.
To verify persistence, run this script again.
Check ./friday_data for stored memories.
============================================================
```

---

## Step 3: Verify Memory Persistence

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

Friday will remember you're Alice and that you're working on a Python project. This is genuine persistence—the memory system loaded your prior context from disk.

---

## Step 4: Inspect the Memory Stores

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

---

## What Just Happened?

Let's break down what Friday did during your first session:

### Conversation Processing
- Received your message via the `CopilotAgent`
- Assembled context from memory stores (empty on first run)
- Generated response using your configured LLM
- Returned natural language response

### Memory Extraction (Background)
- Identified entities: "Alice" (Person), "Python" (Technology), "web API" (Technology)
- Extracted relationships: Alice WORKING_ON Python, Alice INTERESTED_IN web API
- Generated insights: "User prefers Python for development", "User needs web API guidance"
- Stored in vector store with embeddings for semantic search

### Knowledge Graph Building
- Created entity nodes with types and descriptions
- Connected entities with semantic relationships
- Incremented hit counts (Hebbian learning starts)
- Persisted graph to JSON file

### Transcript Logging
- Saved complete turn to SQLite database
- Captured: user message, assistant response, timestamp, token usage
- Enabled session replay and audit trails

### Context Priming (Next Session)
- On restart, loaded top entities by hit count (Alice, Python)
- Retrieved recent insights from vector store
- Reconstructed context without explicit "remember when..."

**This is the Memory Loop in action**: conversation → extraction → storage → retrieval → context.

---

## Understanding the Code

### LLM Initialization

```python
llm = LiteLLMService(
    model="gpt-4o-mini",
    temperature=0.7,
)
```

`LiteLLMService` wraps LiteLLM for provider-agnostic LLM calls. It automatically uses `OPENAI_API_KEY` from environment and works with OpenAI, Anthropic, Google, Ollama, and 100+ models.

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

Provides a **unified interface** to all three memory stores, handles extraction (entities, relationships, insights), and manages lifecycle (promotion, decay, reactivation).

### Context Engineering

```python
assembler = ContextAssembler(...)  # Retrieves relevant memories
architect = PromptArchitect(...)   # Formats prompts with token budgeting
```

The Assembler queries stores and applies knapsack optimization. The Architect structures messages for the LLM with "lost in middle" mitigation.

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

---

## Interactive CLI

The script above demonstrates the basics, but Friday includes a full-featured interactive CLI for exploration and testing.

### Run the Reference CLI

```bash
# If installed from source
cd tests/integration/memory
python memory-chat-v2.py --config config.yaml
```

### Essential Commands

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

---

## Expanding Your Agent

Now that you have a working Friday agent, explore these enhancements:

### Add Tools

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

### Use Local Models for Privacy

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

### Customize Memory Lifecycle

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

## Configuration Deep Dive

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

- **[Core Concepts: Architecture](/docs/concepts/architecture/)** - Understand how Friday works under the hood
- **[Memory System: Three-Tier Architecture](/docs/memory/three-tier/)** - Master the three-tier memory system
- **[Memory System: Context Engineering](/docs/memory/context-engineering/)** - Understand the Knapsack algorithm and token budgeting
