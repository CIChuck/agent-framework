---
title: "Common Issues"
description: "Solutions to the most frequently encountered Friday configuration and runtime errors."
weight: 1
---

Solutions to the most frequently reported issues with Friday, including missing API keys, memory store connection failures, and Re-Act loop termination errors.

## Memory Issues

Memory problems are among the most common issues when working with Friday. This section covers memory persistence, retrieval accuracy, and storage-related challenges.

### Agent Does Not Remember Previous Conversations

**Symptoms:**
- Agent responds as if it's the first interaction
- Previously discussed topics aren't recalled
- No context from prior sessions appears in responses
- Agent asks for information you've already provided

**Root Causes:**

1. Memory Not Being Saved: The `MemoryController` may not be persisting turns to storage adapters
2. Session Not Initialized: Agent session wasn't properly initialized with `initialize_session()`
3. Wrong Session ID: Agent is using a different session ID than previous conversations
4. Storage Adapter Not Configured: Vector store or graph store isn't properly initialized
5. Memory Extraction Disabled: Extraction pipeline isn't running after turns

**Step 1: Verify memory storage files exist**

```bash
# Check if memory files are being created
ls -lh ~/.friday/memory/

# Expected files:
# - chroma.sqlite3 (ChromaDB vector store)
# - graph.json (NetworkX graph store)
# - transcript.db (SQLite episodic store)
```

If files don't exist, set an explicit storage path:

```python
from friday_memory import MemoryConfig

config = MemoryConfig(
    storage_path="/absolute/path/to/memory/directory"
)
```

**Step 2: Enable debug logging to trace memory operations**

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("friday_memory")
logger.setLevel(logging.DEBUG)

# Look for log messages like:
# - "Saving interaction turn to episodic store"
# - "Extracting entities and relationships"
# - "Adding insight to vector store"
```

**Step 3: Verify session initialization**

```python
from friday_agent import CopilotAgent

agent = CopilotAgent(...)

# IMPORTANT: Initialize session before first interaction
await agent.initialize_session()

# Check session state
print(f"Session ID: {agent.session_state.session_id}")
print(f"User ID: {agent.session_state.user_id}")
```

**Step 4: Verify memory is being retrieved**

```python
from friday_memory import MemoryController

memories = await memory_controller.retrieve_insights(
    query="test query",
    limit=5
)

print(f"Found {len(memories)} memories")
for mem in memories:
    print(f"  - {mem.content} (score: {mem.score:.3f})")
```

**Step 5: Force extraction to test the pipeline**

```python
from friday_memory.extraction import MemoryExtractor

extractor = MemoryExtractor(
    llm_client=llm_client,
    memory_controller=memory_controller
)

await extractor.extract_and_store(
    conversation_history=[
        {"role": "user", "content": "My favorite programming language is Python"},
        {"role": "assistant", "content": "Great choice! Python is versatile."}
    ]
)

entities = await memory_controller.graph_store.get_all_entities()
print(f"Extracted {len(entities)} entities")
```

**Prevention:** Always call `initialize_session()` before agent interactions; use consistent `user_id` values across sessions; set explicit storage paths in production.

---

### Agent Retrieves Irrelevant or Outdated Memories

**Symptoms:**
- Agent references information that's no longer accurate
- Retrieves memories from unrelated conversations
- Memories seem randomly selected rather than relevance-based

**Step 1: Increase the retrieval similarity threshold**

```python
from friday_memory import MemoryConfig

config = MemoryConfig(
    min_relevance_threshold=0.7,  # Default: 0.5
    max_retrieved_insights=5,
)
```

**Step 2: Run decay to age out outdated memories**

```python
from friday_memory.lifecycle import MemoryLifecycleManager

manager = MemoryLifecycleManager(memory_controller)
decay_results = await manager.apply_decay()
print(f"Decayed {decay_results.decayed_count} memories")
```

**Step 3: Inspect the context payload to see what was retrieved**

```python
context_payload = await context_engine.assemble_context(
    query="What's my favorite language?",
    state=session_state,
    budget_limit=2000
)

print(f"Context Token Count: {context_payload.total_tokens}")
for insight in context_payload.insights:
    print(f"  [{insight.score:.3f}] {insight.content}")
```

**Step 4: Prune fully decayed memories**

```python
cleanup_results = await manager.cleanup_decayed_memories(
    min_days_since_access=30,
    min_decay_score=0.1
)
print(f"Removed {cleanup_results.removed_count} stale memories")
```

---

### Memory Retrieval is Extremely Slow

**Symptoms:**
- Agent takes 5+ seconds to respond to simple queries
- Context assembly is the bottleneck
- Response times increase as the memory store grows

**Performance targets:**
- Context assembly: < 500ms
- Vector retrieval: < 200ms for 10 candidates
- Graph query: < 100ms for entity + 2-hop relationships

**Step 1: Profile retrieval time**

```python
import time

start = time.time()
context_payload = await context_engine.assemble_context(
    query="test query",
    state=session_state,
    budget_limit=2000
)
print(f"Context assembly: {time.time() - start:.2f}s")
```

**Step 2: Tune ChromaDB HNSW index**

```python
adapter = ChromaAdapter(
    persist_directory="./memory",
    collection_name="memories_long_term",
    metadata={
        "hnsw:space": "cosine",
        "hnsw:construction_ef": 200,
        "hnsw:search_ef": 100,
        "hnsw:M": 16
    }
)
```

**Step 3: Reduce candidate set size**

```python
config = MemoryConfig(
    max_retrieved_insights=5,    # Down from 10
    max_retrieved_entities=10,   # Down from 20
    min_relevance_threshold=0.7,
)
```

**Step 4: Move to Neo4j for large graph stores (10K+ nodes)**

```python
from friday_memory.adapters.graph import Neo4jAdapter

adapter = Neo4jAdapter(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)
```

---

## LLM Issues

### API Key Not Found

**Symptoms:**
- Error: `AuthenticationError: Invalid API key`
- Error: `OPENAI_API_KEY not found in environment`

**Step 1: Verify the environment variable is set**

```bash
echo $OPENAI_API_KEY
# Should print: sk-proj-...

# If empty, set it
export OPENAI_API_KEY="sk-proj-your-key-here"
```

**Step 2: Use a `.env` file for development**

```bash
cat > .env <<EOF
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
EOF
```

```python
from dotenv import load_dotenv
load_dotenv()  # Call this before importing Friday modules
```

**Step 3: Validate the key format**

```python
import os

api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key:
    print("ERROR: API key not set")
elif api_key.startswith(" ") or api_key.endswith(" "):
    print("ERROR: API key has whitespace — strip and retry")
elif not api_key.startswith("sk-"):
    print("ERROR: Key doesn't match expected format (sk-...)")
else:
    print(f"Key looks valid: {api_key[:10]}...")
```

**Step 4: Test the key directly with LiteLLM**

```python
import litellm

try:
    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'test successful'"}],
    )
    print("API key works!")
except Exception as e:
    print(f"Key test failed: {e}")
```

---

### Tool Calls Not Working

**Symptoms:**
- Agent never attempts to call tools
- LLM responds directly instead of using available tools
- Error: `Tool not found in registry`

**Step 1: Verify tools are registered**

```python
from friday_agent.tools import DefaultToolRegistry

registry = DefaultToolRegistry()
tools = registry.list_tools()
print(f"Registered {len(tools)} tools:")
for tool in tools:
    print(f"  - {tool.name}: {tool.description[:60]}...")
```

**Step 2: Confirm the model supports function calling**

```python
# Models with tool support: gpt-4o, gpt-4o-mini, gpt-4-turbo,
# claude-3-5-sonnet-20241022, gemini-2.5-pro-latest

# Models WITHOUT tool support: gpt-3.5-turbo-instruct, text-davinci-003
```

**Step 3: Write clear, specific tool descriptions**

```python
class WeatherTool(BaseTool):
    # BAD: Vague
    # description = "Gets weather"

    # GOOD: Clear and specific
    description = (
        "Retrieves current weather conditions for a specific city. "
        "Use this when the user asks about weather, temperature, or climate. "
        "Returns temperature, conditions, and humidity."
    )
```

**Step 4: Enable tool call logging**

```python
import logging
logging.getLogger("friday_agent.tools").setLevel(logging.DEBUG)
# Look for: "Tool schemas generated", "Executing tool: ..."
```

---

### Rate Limiting

**Symptoms:**
- Error: `RateLimitError: Rate limit exceeded`
- Error: `429 Too Many Requests`

**Step 1: Enable automatic retry with exponential backoff**

```python
from friday_llm import ResilienceConfig

config = ResilienceConfig(
    max_retries=5,
    initial_retry_delay=1.0,
    max_retry_delay=60.0,
    exponential_base=2.0,
    jitter=True
)
```

**Step 2: Implement a rate limiter**

```python
import asyncio
from collections import deque
import time

class RateLimiter:
    def __init__(self, max_requests: int, time_window: float):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()

    async def acquire(self):
        now = time.time()
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()

        if len(self.requests) >= self.max_requests:
            sleep_time = self.requests[0] + self.time_window - now
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                return await self.acquire()

        self.requests.append(now)

# 50 requests per minute
rate_limiter = RateLimiter(max_requests=50, time_window=60.0)
```

---

## Context Window Issues

### Context Length Exceeded

**Symptoms:**
- Error: `InvalidRequestError: context_length_exceeded`
- Request fails after assembling context

**Step 1: Check model context limits**

| Model | Context Window |
|-------|----------------|
| gpt-4o / gpt-4o-mini | 128,000 |
| claude-3-5-sonnet | 200,000 |
| gemini-2.5-pro | 2,097,152 |
| llama3 (local) | 8,192 |
| mistral (local) | 32,768 |

**Step 2: Configure a token budget — leave 25% for the response**

```python
from friday_memory import ContextEngineeringConfig

config = ContextEngineeringConfig(
    context_window_tokens=96_000,   # 75% of 128K
    system_prompt_budget=1000,
    tools_budget=5000,
    history_budget=10000,
    retrieved_memory_budget=80000,
)
```

**Step 3: Reduce tool set to essentials**

```python
registry = DefaultToolRegistry(
    allowed_tools=["read_file", "write_file", "list_directory", "web_search"]
)
```

**Step 4: Truncate old conversation history**

```python
config = ContextEngineeringConfig(
    max_history_turns=10,
    history_budget=5000,
    truncate_from_middle=True
)
```

---

## Tool Execution Issues

### Permission and Access Errors

**Symptoms:**
- Error: `PermissionError: [Errno 13] Permission denied`
- Error: `FileNotFoundError: No such file or directory`

**Step 1: Use absolute paths**

```python
import os

# BAD: Relative paths can break
file_path = "data/config.yaml"

# GOOD: Use absolute paths
file_path = os.path.abspath("data/config.yaml")
```

**Step 2: Configure sandbox permissions**

```python
from friday_sandbox import SubprocessSandbox, SandboxConfig

config = SandboxConfig(
    allowed_directories=["/home/user/projects", "/tmp"],
    allowed_commands=["git", "python3", "npm"],
    allow_network=True,
    allow_file_read=True,
    allow_file_write=True
)
```

### Tool Execution Timeouts

**Symptoms:**
- Error: `TimeoutError: Tool execution exceeded 30 seconds`

**Set a timeout with graceful error handling**

```python
import asyncio
from friday_tools import BaseTool

class MyTool(BaseTool):
    timeout_seconds = 30

    async def execute(self, **kwargs):
        try:
            return await asyncio.wait_for(
                self._do_work(**kwargs),
                timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Tool execution exceeded {self.timeout_seconds}s"
            }
```

**Use background tasks for very long operations**

```python
import uuid

BACKGROUND_TASKS: dict[str, asyncio.Task] = {}

class BackgroundTool(BaseTool):
    async def execute(self, **kwargs):
        task_id = str(uuid.uuid4())
        task = asyncio.create_task(self._long_operation(**kwargs))
        BACKGROUND_TASKS[task_id] = task
        return {
            "success": True,
            "task_id": task_id,
            "message": "Task started. Use check_status to monitor."
        }
```

---

## Multi-Agent Communication Issues

### Agents Not Receiving Messages

**Symptoms:**
- Agent A sends a message but Agent B doesn't respond
- Message queue appears empty

**Step 1: Verify agent registration**

```python
orchestrator.register_agent("agent_a", agent_a)
orchestrator.register_agent("agent_b", agent_b)

print(orchestrator.list_agents())
# Should print: ['agent_a', 'agent_b']
```

**Step 2: Use only serializable types in messages**

```python
# BAD: datetime objects are not JSON-serializable
message = {"text": "Hello", "timestamp": datetime.now()}

# GOOD: Serialize first
message = {"text": "Hello", "timestamp": datetime.now().isoformat()}
```

**Step 3: Enable message logging**

```python
import logging
logging.getLogger("friday_agent.orchestrator").setLevel(logging.DEBUG)
```

## Related Pages

- [Debugging Strategies](/docs/troubleshooting/debugging/) — Structured logs, telemetry, and transcript analysis
- [FAQ](/docs/troubleshooting/faq/) — General questions about Friday
- [Performance Optimization](/docs/advanced/performance/) — Latency and cost tuning
