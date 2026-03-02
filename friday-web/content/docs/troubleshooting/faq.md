---
title: "FAQ"
description: "Frequently asked questions about Friday Framework."
weight: 3
---

Answers to the most frequently asked questions about Friday Framework, covering installation, licensing, LLM compatibility, memory limits, and upgrade paths.

## General

**Q: Can Friday run completely offline?**

Yes, with limitations. Friday can run offline using local LLM providers and local storage adapters. However, some components require internet access.

**Offline-capable:**
- Local LLM inference with Ollama (Llama 3, Mistral, etc.)
- Vector storage with ChromaDB (local SQLite)
- Graph storage with NetworkX + JSON
- Episodic storage with SQLite
- All Friday core functionality

**Requires internet:**
- Cloud LLM providers (OpenAI, Anthropic, Google)
- Web search tools
- Remote MCP servers
- Package installation (`uv sync`)

**Setup for offline use:**

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model (requires internet once)
ollama pull llama3
```

```python
from friday_llm import LiteLLMService

llm = LiteLLMService(
    model="ollama/llama3",
    api_base="http://localhost:11434"
)
```

Local models are 2-10x slower than cloud models but sufficient for many use cases.

---

**Q: How much does it cost to run Friday?**

Cost depends entirely on your LLM provider and usage volume.

**Development (low volume):**
- ~$1-5/month with GPT-4o-mini
- ~$10-20/month with GPT-4o
- $0/month with Ollama (local inference)

**Production (100 queries/day):**
- ~$10-30/month with GPT-4o-mini
- ~$100-300/month with GPT-4o
- ~$5-15/month with Claude Haiku
- $0/month with Ollama (hardware cost instead)

**Cost optimization tips:**
1. Use GPT-4o-mini or Claude Haiku for memory extraction (up to 94% savings)
2. Set aggressive token budgets
3. Cache repeated queries
4. Run maintenance to prune old memories
5. Use local models for development

---

**Q: What are the hardware requirements?**

**Minimum (cloud LLMs):**
- 2 CPU cores, 4 GB RAM, 10 GB disk, internet connection

**Recommended (cloud LLMs):**
- 4+ CPU cores, 8 GB RAM, 50 GB SSD, stable internet

**Local LLMs (Ollama):**
- 4+ CPU cores (8+ recommended)
- 8 GB RAM minimum (16 GB+ recommended)
- 50 GB disk (models are large)
- GPU strongly recommended: NVIDIA 6 GB+ VRAM (e.g., RTX 3060) or Apple Silicon M1+

**Large deployments (1000+ users):**
- Dedicated database servers (Neo4j, PostgreSQL)
- Vector database cluster (Pinecone, Weaviate)
- Load balancer, Redis for caching, Kubernetes

---

**Q: Can I migrate from LangChain, AutoGPT, or CrewAI?**

Yes, but it requires code changes. Friday has a different architecture from wrapper libraries.

**Migration from LangChain:**

```python
# LangChain
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
from langchain.tools import Tool

llm = OpenAI(temperature=0.7)
tools = [Tool(name="search", func=search_func, description="...")]
agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
result = agent.run("query")

# Friday equivalent
from friday_agent import CopilotAgent, AgentProfile
from friday_llm import LiteLLMService
from friday_tools import BaseTool

class SearchTool(BaseTool):
    name = "search"
    description = "..."
    async def execute(self, **kwargs):
        return search_func(kwargs)

llm = LiteLLMService(model="gpt-4o", temperature=0.7)
agent = CopilotAgent(profile=profile, llm=llm, tool_registry=registry)
result = await agent.run("query")
```

**Key differences:**
- Friday is fully async (`await`)
- Memory is built-in, not optional
- Tools are protocol-based with cleaner interfaces
- No "chains" concept — use workflows instead

**Migration strategy:** Start a Friday agent alongside existing code, port tools one at a time, migrate conversation history, then switch traffic gradually. Estimated 1-2 weeks for a medium-sized application.

---

**Q: How does Friday compare to LangChain, AutoGPT, and CrewAI?**

**Friday vs LangChain:**

| Feature | Friday | LangChain |
|---------|--------|-----------|
| Architecture | Protocol-first, modular | Wrapper library |
| Memory | Three-tier, adaptive | Basic (separate LangMem) |
| Learning | Hebbian, decay, promotion | No learning |
| Multi-agent | Built-in orchestration | LangGraph (separate) |
| Vendor lock-in | Zero (protocols) | Moderate |
| Best for | Stateful agents | Quick integrations |

**Friday vs AutoGPT:**

| Feature | Friday | AutoGPT |
|---------|--------|---------|
| Architecture | Framework (library) | Application (run it) |
| Memory | Sophisticated (3-tier) | Vector only |
| Control | Full programmatic | Limited |
| Tool system | 50+ extensible | Fixed set |
| Best for | Building agents | Autonomous tasks |

**Friday vs CrewAI:**

| Feature | Friday | CrewAI |
|---------|--------|--------|
| Focus | General agent framework | Multi-agent teams |
| Memory | Per-agent + shared | Shared context |
| Learning | Adaptive memory | Static |
| Best for | Any agent type | Collaborative teams |

**Choose Friday when** you need genuine memory and learning, are building long-running agents, want zero vendor lock-in, or need protocol-based extensibility.

---

**Q: Is Friday production-ready?**

**Friday v0.1.0 is early development phase.**

**What works well:**
- Core memory architecture (tested with 10K+ memories)
- LLM integrations (OpenAI, Anthropic, Google, Ollama)
- Tool system (50+ built-in tools)
- Single-agent workflows
- Transcript logging

**What's experimental:**
- Multi-agent orchestration (basic functionality)
- MCP integration (protocol is evolving)
- Sandbox isolation (Docker version pending)
- Distributed deployments

**Production recommendations:**
- Use for internal tools and prototypes
- Use with proper error handling and monitoring
- Test thoroughly in staging first
- Use caution for customer-facing applications
- Implement fallbacks for critical paths

**Production checklist:**
- [ ] Comprehensive logging configured
- [ ] Error handling and circuit breakers in place
- [ ] Rate limiting and cost monitoring active
- [ ] Regular memory maintenance scheduled
- [ ] Backup strategy for memory stores
- [ ] Staging environment for testing
- [ ] Rollback plan documented

---

**Q: Can Friday agents collaborate with non-Friday agents?**

Yes, through several mechanisms:

**1. MCP (Model Context Protocol)**

```python
from friday_mcp import MCPClient

mcp_client = MCPClient("http://external-service:8000")
await registry.register_mcp_tools(mcp_client)
```

**2. REST API**

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/chat")
async def chat(query: str, session_id: str):
    response = await friday_agent.run(query)
    return {"response": response}
```

**3. Message Queue (RabbitMQ)**

```python
import aio_pika

async def message_handler(message: aio_pika.IncomingMessage):
    query = message.body.decode()
    response = await friday_agent.run(query)
    await channel.default_exchange.publish(
        aio_pika.Message(body=response.encode()),
        routing_key=message.reply_to
    )
```

**4. Shared Memory Store**

```python
# Friday agent A and a custom agent B share the same MemoryController
agent_a = CopilotAgent(memory=shared_memory_controller, ...)

class CustomAgent:
    def __init__(self, memory: MemoryController):
        self.memory = memory  # Same shared instance
```

---

**Q: How do I back up and restore Friday's memory?**

**Backup script:**

```bash
#!/bin/bash
BACKUP_DIR="/backups/friday-$(date +%Y%m%d-%H%M%S)"
MEMORY_DIR="$HOME/.friday/memory"

mkdir -p "$BACKUP_DIR"
cp "$MEMORY_DIR/chroma.sqlite3" "$BACKUP_DIR/"
cp "$MEMORY_DIR/graph.json" "$BACKUP_DIR/"
cp "$MEMORY_DIR/transcript.db" "$BACKUP_DIR/"

tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"
echo "Backup created: $BACKUP_DIR.tar.gz"
```

**Restore script:**

```bash
#!/bin/bash
BACKUP_FILE="$1"
MEMORY_DIR="$HOME/.friday/memory"

# Stop Friday first: systemctl stop friday-agent
tar -xzf "$BACKUP_FILE" -C /tmp/
cp /tmp/friday-*/chroma.sqlite3 "$MEMORY_DIR/"
cp /tmp/friday-*/graph.json "$MEMORY_DIR/"
cp /tmp/friday-*/transcript.db "$MEMORY_DIR/"
rm -rf /tmp/friday-*
echo "Memory restored from $BACKUP_FILE"
```

**Programmatic export/import:**

```python
import json
from friday_memory import MemoryController

async def export_memory(memory: MemoryController, output_path: str):
    data = {
        "entities": [e.dict() for e in await memory.graph_store.get_all_entities()],
        "relationships": [r.dict() for r in await memory.graph_store.get_all_relationships()],
        "insights": await memory.vector_store.export_all(),
        "transcript": await memory.episodic_store.export_all()
    }
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

async def import_memory(memory: MemoryController, input_path: str):
    with open(input_path) as f:
        data = json.load(f)
    for entity_data in data["entities"]:
        await memory.graph_store.add_entity(Entity(**entity_data))
    await memory.vector_store.import_all(data["insights"])
    await memory.episodic_store.import_all(data["transcript"])
```

---

**Q: Can I use Friday without the memory system?**

Yes, but you lose the main value proposition — Friday's memory is what distinguishes it.

**Minimal agent without memory:**

```python
from friday_llm import LiteLLMService
from friday_agent.tools import DefaultToolRegistry

llm = LiteLLMService(model="gpt-4o")
registry = DefaultToolRegistry()

messages = [{"role": "user", "content": "Query"}]
while True:
    response = await llm.chat_completion(
        messages=messages,
        tools=registry.get_tool_schemas()
    )
    if not response.tool_calls:
        break
    for tool_call in response.tool_calls:
        result = await registry.execute_tool(tool_call.name, tool_call.arguments)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })
```

You can also install individual Friday packages standalone:

```bash
pip install friday-llm      # Just the LLM client
pip install friday-tools    # Just the tools
pip install friday-memory   # Just the memory system
```

## Related Pages

- [Common Issues](/docs/troubleshooting/common-issues/) — Step-by-step fixes for specific errors
- [Debugging Strategies](/docs/troubleshooting/debugging/) — Logs, telemetry, and transcript analysis
- [Hybrid Cloud-Local](/docs/advanced/hybrid/) — Running Friday entirely on local infrastructure
