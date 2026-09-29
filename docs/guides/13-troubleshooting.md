# Friday Agent Framework
## Section 13: Troubleshooting & FAQ

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24



---

## Table of Contents

- [13.1 Common Issues & Solutions](#131-common-issues--solutions)
  - [13.1.1 Memory Issues](#1311-memory-issues)
  - [13.1.2 LLM Issues](#1312-llm-issues)
  - [13.1.3 Context Window Issues](#1313-context-window-issues)
  - [13.1.4 Tool Execution Issues](#1314-tool-execution-issues)
  - [13.1.5 Agent Communication Issues](#1315-agent-communication-issues)
- [13.2 Debugging Strategies](#132-debugging-strategies)
  - [13.2.1 Logging & Telemetry](#1321-logging--telemetry)
  - [13.2.2 Interactive Debugging](#1322-interactive-debugging)
  - [13.2.3 Transcript Analysis](#1323-transcript-analysis)
- [13.3 Performance Tuning](#133-performance-tuning)
  - [13.3.1 Latency Optimization](#1331-latency-optimization)
  - [13.3.2 Cost Optimization](#1332-cost-optimization)
  - [13.3.3 Memory Optimization](#1333-memory-optimization)
- [13.4 FAQ](#134-faq)

---

## Introduction

This section provides practical troubleshooting guidance for common Friday Framework issues. Each problem includes symptom descriptions, root cause analysis, step-by-step solutions, and prevention strategies. Whether you're debugging memory persistence issues, optimizing performance, or understanding cost implications, this guide offers actionable solutions based on real-world deployment experience.

**When to Use This Guide:**
- Agent behavior doesn't match expectations
- Memory retrieval seems inaccurate or incomplete
- Performance is slower than expected
- LLM API calls are failing or timing out
- Tool execution encounters errors
- Cost or token usage is higher than anticipated

**Support Resources:**
- GitHub Issues: `https://github.com/your-org/friday-agent-framework/issues`
- Documentation: `/docs/guides/` directory
- Community Discord: Link in README
- Stack Overflow: Tag `friday-agent`

---

## 13.1 Common Issues & Solutions

### Integrated MCP client checks

The [MCP client guide](17-mcp-client.md) has a parser-checked local stdio
example. Use `RuntimeKernel.mcp_provider.operational_diagnostics` or Friday
Chat's `MCPChatRegistry.provider.operational_diagnostics` for typed local
evidence. Telemetry events are redacted categorical summaries; they are not a
dump of peer output.

| Symptom | Check and next action |
| --- | --- |
| No tools or disabled server | Confirm `tools.providers.mcp.enabled`, `config.servers[].enabled`, startup-only discovery, and that the local stdio command exists. Restart after changing the peer catalog. |
| Optional server failed | Inspect the lifecycle outcome; fix the command, workspace-confined `cwd`, timeout or peer startup. Other providers can remain usable **only if** no explicit `include_tools` name from that peer is missing; a missing include stops registration with `missing_include`. |
| Required server stopped startup | `required: true` makes connection/list-tools failure fatal. Fix the peer or explicitly make it optional; do not mark a disabled server required. |
| A named tool is missing | Use the normalized canonical name in `include_tools`; check `exclude_tools`, missing include diagnostics, schema/total caps and both contenders in any name collision. For nonfatal optional-peer absence, consider `include_categories: [mcp]` only if admitting all valid discovered MCP tools is acceptable. |
| Tool appears but Chat skips it | Inspect per-turn selection reasons and `tools.context.max_tools`, `max_mcp_tools`, schema ratio, result reservation and minimum memory floor. |
| Output is truncated or blocked | Review `config.limits.max_result_bytes` and the peer's result size/content. Friday uses checked output, not raw peer bytes. |
| MCP memory is absent | Direct ingestion defaults off. Check `config.ingestion` opt-ins and sanitized-content policy, then distinguish pending from published outcomes. A transcript receipt alone does not prove publication. |
| `config_file` fails validation | External MCP config includes are reserved for deferred WS-09; use inline `tools.providers.mcp.config`. |

### 13.1.1 Memory Issues

Memory problems are among the most common issues when working with Friday. This subsection covers memory persistence, retrieval accuracy, and storage-related challenges.

---

#### Problem: Agent Doesn't Remember Previous Conversations

**Symptoms:**
- Agent responds as if it's the first interaction
- Previously discussed topics aren't recalled
- No context from prior sessions appears in responses
- Agent asks for information you've already provided

**Root Causes:**

1. **Memory Not Being Saved**: The `MemoryController` may not be persisting turns to storage adapters
2. **Session Not Initialized**: Agent session wasn't properly initialized with `initialize_session()`
3. **Wrong Session ID**: Agent is using a different session ID than previous conversations
4. **Storage Adapter Not Configured**: Vector store or graph store isn't properly initialized
5. **Memory Extraction Disabled**: Extraction pipeline isn't running after turns

**Step-by-Step Solution:**

**Step 1: Verify Memory Storage Files Exist**

```bash
# Check if memory files are being created
ls -lh ~/.friday/memory/

# Expected files:
# - chroma.sqlite3 (ChromaDB vector store)
# - graph.json (NetworkX graph store)
# - transcript.db (SQLite episodic store)
```

If files don't exist:
```python
# Explicitly set memory directory in config
from friday_memory import MemoryConfig

config = MemoryConfig(
    storage_path="/absolute/path/to/memory/directory"
)
```

**Step 2: Enable Debug Logging to Trace Memory Operations**

```python
import logging

# Enable detailed memory logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("friday_memory")
logger.setLevel(logging.DEBUG)

# Run your agent
# Look for log messages like:
# - "Saving interaction turn to episodic store"
# - "Extracting entities and relationships"
# - "Adding insight to vector store"
```

**Step 3: Verify Session Initialization**

```python
from friday_agent import CopilotAgent

agent = CopilotAgent(...)

# IMPORTANT: Initialize session before first interaction
await agent.initialize_session()

# Check session state
print(f"Session ID: {agent.session_state.session_id}")
print(f"User ID: {agent.session_state.user_id}")
```

**Step 4: Verify Memory is Being Retrieved**

```python
from friday_memory import MemoryController

# After a conversation, manually query memory
memories = await memory_controller.retrieve_insights(
    query="test query",
    limit=5
)

print(f"Found {len(memories)} memories")
for mem in memories:
    print(f"  - {mem.content} (score: {mem.score:.3f})")
```

**Step 5: Check Memory Extraction is Enabled**

```python
# In your agent configuration
from friday_agent import CopilotAgent

agent = CopilotAgent(
    memory=memory_controller,  # Must be provided
    # ... other config
)

# Verify extraction is happening after turns
# Check logs for "Running memory extraction pipeline"
```

**Step 6: Force Memory Extraction (Testing)**

```python
# Manually trigger extraction to test pipeline
from friday_memory.extraction import MemoryExtractor

extractor = MemoryExtractor(
    llm_client=llm_client,
    memory_controller=memory_controller
)

# Extract from a conversation turn
await extractor.extract_and_store(
    conversation_history=[
        {"role": "user", "content": "My favorite programming language is Python"},
        {"role": "assistant", "content": "Great choice! Python is versatile."}
    ]
)

# Verify extraction results
entities = await memory_controller.graph_store.get_all_entities()
print(f"Extracted {len(entities)} entities")
```

**Prevention Tips:**

1. **Always call `initialize_session()` before agent interactions**
2. **Use consistent `user_id` across sessions** for the same user
3. **Set explicit storage paths** in production (not default temp directories)
4. **Enable persistence checks** in CI/CD pipelines
5. **Monitor memory file sizes** to ensure data is being written
6. **Set up health checks** that verify memory retrieval works

**Advanced Debugging:**

```python
# Dump entire memory state for inspection
import json

# Get all entities
entities = await memory_controller.graph_store.get_all_entities()
print(json.dumps([e.dict() for e in entities], indent=2))

# Get all insights from vector store
from friday_memory.adapters.vector import ChromaAdapter

adapter = ChromaAdapter(...)
results = adapter.collection.get(limit=1000)
print(f"Total insights in vector store: {len(results['ids'])}")

# Check episodic memory (transcript)
from friday_memory.adapters.episodic import TranscriptStoreAdapter

transcript_adapter = TranscriptStoreAdapter(...)
turns = await transcript_adapter.get_recent_turns(session_id="your_session", limit=50)
print(f"Transcript has {len(turns)} turns")
```

---

#### Problem: Agent Retrieves Irrelevant or Outdated Memories

**Symptoms:**
- Agent references information that's no longer accurate
- Retrieves memories from unrelated conversations
- Includes context that doesn't match the current query
- Memories seem randomly selected rather than relevance-based

**Root Causes:**

1. **Poor Embedding Quality**: Semantic search isn't finding truly similar content
2. **No Decay Applied**: Old memories haven't decayed, pollution context
3. **Low Relevance Threshold**: Retrieval is including low-quality matches
4. **Insufficient Knapsack Scoring**: Context assembly isn't properly prioritizing memories
5. **Graph Relationships Stale**: Entity connections haven't been updated

**Step-by-Step Solution:**

**Step 1: Adjust Retrieval Threshold**

```python
from friday_memory import MemoryConfig

config = MemoryConfig(
    # Increase minimum similarity threshold (default: 0.5)
    min_relevance_threshold=0.7,  # Only retrieve highly relevant memories

    # Reduce number of candidates
    max_retrieved_insights=5,  # Default: 10
)
```

**Step 2: Run Memory Maintenance to Apply Decay**

```python
from friday_memory.lifecycle import MemoryLifecycleManager

manager = MemoryLifecycleManager(memory_controller)

# Apply decay to outdated memories
decay_results = await manager.apply_decay()
print(f"Decayed {decay_results.decayed_count} memories")

# Promote recent, valuable memories
promotion_results = await manager.run_promotion_cycle()
print(f"Promoted {promotion_results.promoted_count} memories")
```

**Step 3: Inspect Retrieved Context**

```python
# Enable context payload inspection
context_payload = await context_engine.assemble_context(
    query="What's my favorite language?",
    state=session_state,
    budget_limit=2000
)

# Examine what was retrieved
print(f"Context Token Count: {context_payload.total_tokens}")
print(f"Retrieved {len(context_payload.insights)} insights:")
for insight in context_payload.insights:
    print(f"  [{insight.score:.3f}] {insight.content}")

print(f"Retrieved {len(context_payload.entities)} entities:")
for entity in context_payload.entities:
    print(f"  [{entity.importance:.3f}] {entity.name} ({entity.entity_type})")
```

**Step 4: Re-embed Memories with Better Embedding Model**

```python
from friday_llm import LiteLLMEmbeddings
from friday_memory.adapters.vector import ChromaAdapter

# Use a better embedding model
embeddings = LiteLLMEmbeddings(
    model="text-embedding-3-large",  # Upgrade from text-embedding-3-small
    dimensions=1536
)

# Re-embed all existing memories
adapter = ChromaAdapter(...)
all_insights = adapter.collection.get()

for i, (id, text) in enumerate(zip(all_insights['ids'], all_insights['documents'])):
    new_embedding = await embeddings.embed(text)
    adapter.collection.update(
        ids=[id],
        embeddings=[new_embedding]
    )
    if i % 100 == 0:
        print(f"Re-embedded {i}/{len(all_insights['ids'])} insights")
```

**Step 5: Prune Irrelevant Memories**

```python
# Remove low-value memories that have fully decayed
cleanup_results = await manager.cleanup_decayed_memories(
    min_days_since_access=30,  # Only remove if not accessed in 30 days
    min_decay_score=0.1  # Only remove if decay score < 0.1
)

print(f"Removed {cleanup_results.removed_count} stale memories")
```

**Prevention Tips:**

1. **Run regular maintenance cycles** (daily or weekly decay/promotion)
2. **Set appropriate relevance thresholds** for your domain
3. **Use high-quality embedding models** (OpenAI ada-002 or better)
4. **Monitor context payload quality** in development
5. **Implement feedback loops** to mark bad retrievals
6. **Use user-specific collections** to avoid cross-user pollution

---

#### Problem: Memory Retrieval is Extremely Slow

**Symptoms:**
- Agent takes 5+ seconds to respond to simple queries
- Context assembly is the bottleneck in latency profiling
- Memory retrieval times increase over time
- Database operations time out

**Root Causes:**

1. **Large Vector Store**: Thousands of embeddings with no indexing optimization
2. **Inefficient Graph Queries**: Complex graph traversals without optimization
3. **No Caching**: Repeatedly computing embeddings for the same queries
4. **Disk I/O Bottleneck**: Storage on slow disk or network filesystem
5. **Knapsack Algorithm Overhead**: Complex optimization with large candidate sets

**Step-by-Step Solution:**

**Step 1: Profile Memory Retrieval**

```python
import time

start = time.time()
context_payload = await context_engine.assemble_context(
    query="test query",
    state=session_state,
    budget_limit=2000
)
total_time = time.time() - start

print(f"Total context assembly time: {total_time:.2f}s")
print(f"  - Token count: {context_payload.total_tokens}")
print(f"  - Insights: {len(context_payload.insights)}")
print(f"  - Entities: {len(context_payload.entities)}")
```

**Step 2: Enable Vector Store Optimization**

```python
from friday_memory.adapters.vector import ChromaAdapter

# Use ChromaDB's HNSW index for faster similarity search
adapter = ChromaAdapter(
    persist_directory="./memory",
    collection_name="memories_long_term",
    # Optimize HNSW parameters
    metadata={
        "hnsw:space": "cosine",
        "hnsw:construction_ef": 200,  # Higher = better accuracy, slower build
        "hnsw:search_ef": 100,  # Higher = better accuracy, slower search
        "hnsw:M": 16  # Connections per node (16-64 typical)
    }
)
```

**Step 3: Implement Query Caching**

```python
from functools import lru_cache
import hashlib

class CachedMemoryController:
    def __init__(self, memory_controller):
        self.controller = memory_controller
        self._cache = {}

    async def retrieve_insights(self, query: str, limit: int = 10):
        # Create cache key from query
        cache_key = hashlib.sha256(f"{query}:{limit}".encode()).hexdigest()

        if cache_key in self._cache:
            return self._cache[cache_key]

        # Call actual retrieval
        results = await self.controller.retrieve_insights(query, limit)

        # Cache for 5 minutes (300 seconds)
        self._cache[cache_key] = results
        return results

# Use cached controller
cached_controller = CachedMemoryController(memory_controller)
```

**Step 4: Reduce Candidate Set Size**

```python
from friday_memory import MemoryConfig

config = MemoryConfig(
    # Reduce number of candidates for knapsack algorithm
    max_retrieved_insights=5,  # Down from 10
    max_retrieved_entities=10,  # Down from 20

    # Set stricter relevance threshold
    min_relevance_threshold=0.7,  # Up from 0.5
)
```

**Step 5: Optimize Graph Queries**

```python
from friday_memory.adapters.graph import NetworkXAdapter

# For large graphs, switch to Neo4j for indexed queries
from friday_memory.adapters.graph import Neo4jAdapter

adapter = Neo4jAdapter(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Neo4j provides native indexing on entity names and types
# Much faster for large graphs (10k+ nodes)
```

**Step 6: Move Storage to Faster Disk**

```bash
# Check current disk I/O
iostat -x 1 5  # Linux
# or
sudo fs_usage -w | grep friday  # macOS

# Move to SSD if on HDD
mv ~/.friday/memory/ /path/to/ssd/friday-memory/
ln -s /path/to/ssd/friday-memory/ ~/.friday/memory

# Or use tmpfs for extreme speed (data lost on reboot)
sudo mount -t tmpfs -o size=2G tmpfs /tmp/friday-memory
```

**Prevention Tips:**

1. **Benchmark retrieval performance** during development
2. **Set budget limits** to constrain retrieval size
3. **Implement caching layers** for repeated queries
4. **Use enterprise graph databases** (Neo4j) for large deployments
5. **Run maintenance in background** (don't block user interactions)
6. **Monitor storage performance** in production

**Performance Targets:**

- **Context Assembly**: < 500ms for typical queries
- **Vector Retrieval**: < 200ms for 10 candidates
- **Graph Query**: < 100ms for entity + 2-hop relationships
- **Total Agent Response**: < 2s for non-tool queries

---

### 13.1.2 LLM Issues

LLM-related problems involve API connectivity, authentication, rate limiting, and model-specific behaviors.

---

#### Problem: "API Key Not Found" or Authentication Errors

**Symptoms:**
- Error: `AuthenticationError: Invalid API key`
- Error: `OPENAI_API_KEY not found in environment`
- Agent fails to start or respond
- LLM calls immediately fail

**Root Causes:**

1. **Missing Environment Variables**: API keys not set in shell environment
2. **Wrong Variable Names**: Using incorrect env var names
3. **Trailing Whitespace**: API key has spaces or newlines
4. **Config File Not Loaded**: `.env` file not in correct location
5. **Runtime Environment Issue**: Different env in Docker/systemd

**Step-by-Step Solution:**

**Step 1: Verify Environment Variable is Set**

```bash
# Check if API key is in environment
echo $OPENAI_API_KEY
# Should print: sk-proj-...

# If empty, set it
export OPENAI_API_KEY="sk-proj-your-key-here"

# Make persistent in shell profile
echo 'export OPENAI_API_KEY="sk-proj-your-key-here"' >> ~/.bashrc
source ~/.bashrc  # or ~/.zshrc for zsh
```

**Step 2: Use .env File for Development**

```bash
# Create .env file in project root
cat > .env <<EOF
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_AI_API_KEY=your-google-key-here
EOF

# Load .env in Python
from dotenv import load_dotenv
load_dotenv()  # Call this before importing Friday modules
```

**Step 3: Verify API Key Format**

```python
import os

api_key = os.environ.get("OPENAI_API_KEY", "")

# Check for common issues
if not api_key:
    print("ERROR: API key not set")
elif api_key.startswith(" ") or api_key.endswith(" "):
    print("ERROR: API key has whitespace")
    api_key = api_key.strip()
    os.environ["OPENAI_API_KEY"] = api_key
elif not api_key.startswith("sk-"):
    print("ERROR: API key doesn't match expected format (sk-...)")
else:
    print(f"API key looks valid: {api_key[:10]}...")
```

**Step 4: Test API Key Directly**

```python
# Test with LiteLLM directly
import litellm

try:
    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'test successful'"}],
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    print("API Key works!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"API Key test failed: {e}")
```

**Step 5: Pass API Key Explicitly (Not Recommended for Production)**

```python
from friday_llm import LiteLLMService

# Override environment variable
llm_service = LiteLLMService(
    model="gpt-4o-mini",
    api_key="sk-proj-explicit-key-here",  # Explicit override
    temperature=0.7
)
```

**Prevention Tips:**

1. **Use .env files** for local development
2. **Use secret managers** (AWS Secrets Manager, Vault) for production
3. **Validate API keys** at application startup
4. **Don't commit .env to git** (add to .gitignore)
5. **Rotate keys regularly** and test rotation process
6. **Use different keys** for dev/staging/prod

---

#### Problem: Tool Calls Not Working or Being Ignored

**Symptoms:**
- Agent never attempts to call tools
- LLM responds directly instead of using available tools
- Error: `Tool not found in registry`
- Tools are called but results aren't used

**Root Causes:**

1. **Tools Not Registered**: Tool registry not passed to agent
2. **Tool Schemas Malformed**: JSON schemas don't match LLM provider expectations
3. **Model Doesn't Support Tools**: Using a model without function calling
4. **Tool Description Unclear**: LLM doesn't understand when to use tool
5. **System Prompt Discourages Tools**: Prompt biases against tool usage

**Step-by-Step Solution:**

**Step 1: Verify Tools Are Registered**

```python
from friday_agent.tools import DefaultToolRegistry

registry = DefaultToolRegistry()

# Check what tools are available
tools = registry.list_tools()
print(f"Registered {len(tools)} tools:")
for tool in tools:
    print(f"  - {tool.name}: {tool.description[:60]}...")

# Verify specific tool exists
if not registry.has_tool("read_file"):
    print("ERROR: read_file tool not registered")
```

**Step 2: Verify Model Supports Function Calling**

```python
# Models that support tool calling:
SUPPORTED_MODELS = [
    # OpenAI
    "gpt-4o", "gpt-4o-mini", "gpt-4-turbo",
    # Anthropic
    "claude-3-5-sonnet-20241022", "claude-3-opus-20240229",
    # Google
    "gemini-2.5-pro-latest", "gemini-2.5-flash-latest",
]

# Models that DON'T support tools:
UNSUPPORTED_MODELS = [
    "gpt-3.5-turbo-instruct",  # Completion API, not chat
    "text-davinci-003",  # Old completion model
]

current_model = "gpt-4o-mini"  # Your configured model
if current_model in UNSUPPORTED_MODELS:
    print(f"ERROR: {current_model} doesn't support function calling")
```

**Step 3: Test Tool Calling Directly**

```python
import litellm

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    }
]

response = litellm.completion(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "What's the weather in San Francisco?"}
    ],
    tools=tools,
    tool_choice="auto"
)

# Should return a tool call
if response.choices[0].message.tool_calls:
    print("Tool calling works!")
    print(response.choices[0].message.tool_calls[0])
else:
    print("ERROR: No tool calls made")
```

**Step 4: Improve Tool Descriptions**

```python
from friday_tools import BaseTool

class WeatherTool(BaseTool):
    name = "get_weather"

    # BAD: Vague description
    # description = "Gets weather"

    # GOOD: Clear, specific description with usage context
    description = (
        "Retrieves current weather conditions and forecast for a specific city. "
        "Use this tool when the user asks about weather, temperature, or climate "
        "in a particular location. Returns temperature, conditions, and humidity."
    )

    parameters_schema = {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name, optionally with state/country (e.g., 'San Francisco, CA' or 'London, UK')"
            }
        },
        "required": ["location"]
    }
```

**Step 5: Adjust System Prompt to Encourage Tools**

```python
from friday_agent import AgentProfile

profile = AgentProfile(
    name="Assistant",
    system_prompt=(
        "You are a helpful AI assistant with access to tools. "
        "When the user asks for information you don't have, "
        "ALWAYS use available tools rather than apologizing or declining. "
        "You have access to file operations, web search, code execution, and more. "
        "Use tools confidently and explain what you're doing."
    )
)
```

**Step 6: Enable Tool Call Logging**

```python
import logging

# Enable detailed tool execution logging
logging.getLogger("friday_agent.tools").setLevel(logging.DEBUG)

# Run agent and check logs for:
# - "Tool schemas generated: 15 tools"
# - "LLM requested tool call: read_file"
# - "Executing tool: read_file with params: {...}"
# - "Tool execution result: ..."
```

**Prevention Tips:**

1. **Always test tool calling** with new models
2. **Write clear, specific tool descriptions**
3. **Include usage examples** in tool docstrings
4. **Monitor tool usage rates** (should be >0% for assistant agents)
5. **Provide feedback** when tools fail gracefully
6. **Test edge cases** (missing parameters, invalid inputs)

---

#### Problem: Rate Limiting or Quota Exceeded Errors

**Symptoms:**
- Error: `RateLimitError: Rate limit exceeded`
- Error: `429 Too Many Requests`
- Sporadic failures during high-volume usage
- Requests succeed after waiting

**Root Causes:**

1. **Exceeding Provider Limits**: Making too many requests per minute
2. **No Retry Logic**: Failures aren't automatically retried
3. **Burst Traffic**: Sudden spike in requests without throttling
4. **Insufficient Tier**: Using free or basic API tier
5. **Concurrent Requests**: Multiple agents sharing same API key

**Step-by-Step Solution:**

**Step 1: Enable Automatic Retry with Backoff**

```python
from friday_llm import ResilienceConfig

config = ResilienceConfig(
    max_retries=5,  # Retry up to 5 times
    initial_retry_delay=1.0,  # Start with 1 second
    max_retry_delay=60.0,  # Cap at 60 seconds
    exponential_base=2.0,  # Exponential backoff (1s, 2s, 4s, 8s, 16s)
    jitter=True  # Add randomness to prevent thundering herd
)

llm_service = LiteLLMService(resilience_config=config)
```

**Step 2: Check Rate Limits for Your Provider**

```python
# Common rate limits (as of 2026)

# OpenAI (Free Tier)
# - 3 requests per minute (RPM)
# - 200 requests per day (RPD)

# OpenAI (Tier 1 - $5+ spent)
# - 500 RPM
# - 10,000 RPD
# - 100,000 tokens per minute (TPM)

# Anthropic (Free Tier)
# - 5 RPM
# - 50 RPD

# Anthropic (Pro)
# - 50 RPM
# - 1,000 RPD

# Check your current tier
import openai
client = openai.OpenAI()
# Visit: https://platform.openai.com/account/limits
```

**Step 3: Implement Request Throttling**

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

        # Remove requests outside time window
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()

        # Wait if at limit
        if len(self.requests) >= self.max_requests:
            sleep_time = self.requests[0] + self.time_window - now
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                return await self.acquire()

        self.requests.append(now)

# Use with LLM service
rate_limiter = RateLimiter(max_requests=50, time_window=60.0)  # 50 RPM

async def call_llm_with_rate_limit(messages):
    await rate_limiter.acquire()
    return await llm_service.chat_completion(messages=messages)
```

**Step 4: Enable Circuit Breaker**

```python
from friday_llm.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=5,  # Open circuit after 5 failures
    recovery_timeout=60.0,  # Try again after 60 seconds
    expected_exception=Exception  # Catch all exceptions
)

circuit_breaker = CircuitBreaker(config)

# Wrap LLM calls
@circuit_breaker.call
async def protected_llm_call(messages):
    return await llm_service.chat_completion(messages=messages)
```

**Step 5: Use Request Batching**

```python
# Instead of individual requests, batch multiple queries
async def batch_process_queries(queries: list[str]):
    # Process in smaller batches with delays
    batch_size = 5
    delay_between_batches = 12.0  # 5 batches/minute = 12 sec between

    results = []
    for i in range(0, len(queries), batch_size):
        batch = queries[i:i + batch_size]

        # Process batch concurrently
        batch_results = await asyncio.gather(*[
            llm_service.chat_completion(messages=[
                {"role": "user", "content": query}
            ])
            for query in batch
        ])
        results.extend(batch_results)

        # Wait before next batch
        if i + batch_size < len(queries):
            await asyncio.sleep(delay_between_batches)

    return results
```

**Prevention Tips:**

1. **Upgrade API tier** before production deployment
2. **Monitor rate limit headers** from API responses
3. **Implement backoff** from day one
4. **Use circuit breakers** to prevent cascading failures
5. **Cache responses** where appropriate
6. **Plan capacity** based on expected traffic

---

### 13.1.3 Context Window Issues

Context window problems occur when the prompt exceeds the model's maximum token limit.

---

#### Problem: "Context Length Exceeded" Errors

**Symptoms:**
- Error: `InvalidRequestError: context_length_exceeded`
- Error: `This model's maximum context length is 4096 tokens`
- Request fails after assembling context
- Large conversations or rich memory fail

**Root Causes:**

1. **Budget Not Set**: No token budget limit configured
2. **Model Has Small Context**: Using model with small window (4K, 8K)
3. **Long Tool Schemas**: Too many tools with verbose schemas
4. **Large System Prompt**: System instructions exceed reasonable size
5. **No Truncation Logic**: Old conversation history not trimmed

**Step-by-Step Solution:**

**Step 1: Check Model Context Limits**

```python
# Context windows by model (as of 2026)
MODEL_CONTEXT_WINDOWS = {
    # OpenAI
    "gpt-4o": 128_000,
    "gpt-4o-mini": 128_000,
    "gpt-4-turbo": 128_000,
    "gpt-3.5-turbo": 16_385,

    # Anthropic
    "claude-3-5-sonnet-20241022": 200_000,
    "claude-3-opus-20240229": 200_000,
    "claude-3-haiku-20240307": 200_000,

    # Google
    "gemini-2.5-pro-latest": 2_097_152,  # 2M tokens!
    "gemini-2.5-flash-latest": 1_048_576,  # 1M tokens

    # Local
    "llama3": 8_192,
    "mistral": 32_768,
}

current_model = "gpt-4o-mini"
max_tokens = MODEL_CONTEXT_WINDOWS.get(current_model, 4096)
print(f"{current_model} max context: {max_tokens:,} tokens")
```

**Step 2: Configure Appropriate Token Budget**

```python
from friday_memory import ContextEngineeringConfig

config = ContextEngineeringConfig(
    # Set budget to 75% of model limit (leave room for response)
    context_window_tokens=96_000,  # For 128K model

    # Allocate budget across components
    system_prompt_budget=1000,
    tools_budget=5000,
    history_budget=10000,  # Recent conversation
    retrieved_memory_budget=80000,  # Bulk of context
)

context_engine = ContextAssembler(config=config)
```

**Step 3: Enable Automatic Budget Calculation**

```python
# Friday automatically calculates available budget
system_prompt = profile.render_system_prompt()
tool_schemas = registry.get_tool_schemas()

# Calculate remaining budget after system prompt and tools
budget_limit = context_engine.calculate_budget_limit(
    system_prompt=system_prompt,
    tool_definitions=tool_schemas
)

print(f"Calculated budget: {budget_limit} tokens")
# Uses this budget for memory retrieval
```

**Step 4: Reduce Tool Set Size**

```python
# Only register essential tools
from friday_agent.tools import DefaultToolRegistry

registry = DefaultToolRegistry()

# Option 1: Allowlist specific tools
registry = DefaultToolRegistry(
    allowed_tools=[
        "read_file",
        "write_file",
        "list_directory",
        "bash_command",
        "web_search"
    ]
)

# Option 2: Remove verbose tools
registry.unregister_tool("generate_code")  # Often has large schemas
registry.unregister_tool("complex_data_analysis")
```

**Step 5: Truncate Conversation History**

```python
from friday_memory.context import ContextAssembler

# Configure history truncation
config = ContextEngineeringConfig(
    max_history_turns=10,  # Only include last 10 turns
    history_budget=5000,  # Cap history at 5K tokens
    truncate_from_middle=True  # Keep first + last, remove middle
)

# Context engine will automatically truncate
```

**Step 6: Use Summarization for Long Contexts**

```python
from friday_memory.context import ConversationSummarizer

summarizer = ConversationSummarizer(llm_client=llm_client)

# Summarize old conversation turns
if len(conversation_history) > 20:
    # Summarize turns 0-15, keep last 5 verbatim
    summary = await summarizer.summarize_turns(
        turns=conversation_history[:15]
    )

    # Replace old turns with summary
    conversation_history = [
        {"role": "system", "content": f"Previous conversation summary: {summary}"},
        *conversation_history[15:]
    ]
```

**Prevention Tips:**

1. **Always set token budgets** explicitly
2. **Monitor token usage** per request
3. **Use models with large contexts** for complex agents
4. **Implement summarization** for long conversations
5. **Prune tool sets** to essentials
6. **Test with maximum context** scenarios

---

### 13.1.4 Tool Execution Issues

Tool execution problems involve failures when agents attempt to call tools.

---

#### Problem: Tools Fail with Permission or Access Errors

**Symptoms:**
- Error: `PermissionError: [Errno 13] Permission denied`
- Error: `FileNotFoundError: No such file or directory`
- Tool execution succeeds but returns errors
- Shell commands fail with "command not found"

**Root Causes:**

1. **Insufficient File Permissions**: Agent can't read/write files
2. **Path Issues**: Relative paths resolve incorrectly
3. **Missing Dependencies**: Required binaries not installed
4. **Sandbox Restrictions**: Docker/subprocess sandbox blocking access
5. **Environment Variables Not Set**: Tools depend on env vars

**Step-by-Step Solution:**

**Step 1: Verify File Permissions**

```bash
# Check permissions on target files/directories
ls -la /path/to/file

# Grant read/write permissions
chmod 644 /path/to/file  # File
chmod 755 /path/to/directory  # Directory

# Change ownership if needed
chown $USER:$USER /path/to/file
```

**Step 2: Use Absolute Paths**

```python
import os

# BAD: Relative paths can break
file_path = "data/config.yaml"

# GOOD: Use absolute paths
file_path = os.path.abspath("data/config.yaml")

# Or set explicit working directory
os.chdir("/absolute/path/to/project")
file_path = "data/config.yaml"  # Now resolves correctly
```

**Step 3: Verify Tool Dependencies**

```python
import shutil

# Check if required binaries exist
required_commands = ["git", "docker", "npm"]

for cmd in required_commands:
    if not shutil.which(cmd):
        print(f"ERROR: {cmd} not found in PATH")
        print(f"Install with: apt install {cmd}  # or brew install {cmd}")
```

**Step 4: Configure Sandbox Permissions**

```python
from friday_sandbox import SubprocessSandbox, SandboxConfig

config = SandboxConfig(
    # Allow access to specific directories
    allowed_directories=[
        "/home/user/projects",
        "/tmp"
    ],

    # Allow specific commands
    allowed_commands=[
        "git",
        "python3",
        "npm"
    ],

    # Network access
    allow_network=True,

    # File operations
    allow_file_read=True,
    allow_file_write=True
)

sandbox = SubprocessSandbox(config=config)
```

**Step 5: Check Environment Variables**

```python
# Verify env vars are available to tools
import os

required_env_vars = [
    "HOME",
    "PATH",
    "GITHUB_TOKEN",  # If using git tools
]

for var in required_env_vars:
    value = os.environ.get(var)
    if not value:
        print(f"WARNING: {var} not set")
    else:
        print(f"{var}: {value[:20]}...")  # Show first 20 chars
```

**Prevention Tips:**

1. **Use absolute paths** consistently
2. **Verify dependencies** at startup
3. **Run with least privilege** (don't use root unless necessary)
4. **Test tools in isolation** before integrating
5. **Document required permissions** in tool docstrings
6. **Provide helpful error messages** from tools

---

#### Problem: Tool Execution Timeouts

**Symptoms:**
- Error: `TimeoutError: Tool execution exceeded 30 seconds`
- Long-running tools never complete
- Agent becomes unresponsive
- Bash commands hang indefinitely

**Root Causes:**

1. **No Timeout Configured**: Tools run indefinitely
2. **Blocking Operations**: Waiting for user input or external service
3. **Infinite Loops**: Tool logic has bugs
4. **Large Data Processing**: Tool handles more data than expected
5. **Network Latency**: API calls or downloads take too long

**Step-by-Step Solution:**

**Step 1: Set Reasonable Timeouts**

```python
from friday_tools import BaseTool
import asyncio

class MyTool(BaseTool):
    timeout_seconds = 30  # Default timeout

    async def execute(self, **kwargs):
        try:
            # Wrap actual execution with timeout
            return await asyncio.wait_for(
                self._do_work(**kwargs),
                timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Tool execution exceeded {self.timeout_seconds}s timeout"
            }

    async def _do_work(self, **kwargs):
        # Actual tool logic here
        pass
```

**Step 2: Make Long Operations Interruptible**

```python
import asyncio

async def long_running_operation(data):
    results = []

    for i, item in enumerate(data):
        # Check for cancellation periodically
        if i % 100 == 0:
            await asyncio.sleep(0)  # Allow event loop to process cancellation

        # Process item
        result = process_item(item)
        results.append(result)

    return results
```

**Step 3: Stream Results for Long Operations**

```python
from typing import AsyncIterator

class LongRunningTool(BaseTool):
    async def execute_streaming(self, **kwargs) -> AsyncIterator[dict]:
        """Stream results as they're produced"""

        items = get_items_to_process()

        for i, item in enumerate(items):
            result = await process_item(item)

            # Yield partial result
            yield {
                "progress": f"{i+1}/{len(items)}",
                "result": result
            }

        # Final result
        yield {"complete": True}
```

**Step 4: Add Progress Indicators**

```python
from tqdm import tqdm

async def tool_with_progress(items: list):
    results = []

    for item in tqdm(items, desc="Processing"):
        result = await process_item(item)
        results.append(result)

    return results
```

**Step 5: Use Background Tasks for Very Long Operations**

```python
import uuid
from typing import Dict

# Global task registry
BACKGROUND_TASKS: Dict[str, asyncio.Task] = {}

class BackgroundTool(BaseTool):
    async def execute(self, **kwargs):
        # Start task in background
        task_id = str(uuid.uuid4())
        task = asyncio.create_task(self._long_operation(**kwargs))
        BACKGROUND_TASKS[task_id] = task

        return {
            "success": True,
            "task_id": task_id,
            "message": "Task started in background. Use check_status tool to monitor."
        }

class CheckStatusTool(BaseTool):
    async def execute(self, task_id: str):
        task = BACKGROUND_TASKS.get(task_id)

        if not task:
            return {"error": "Task not found"}

        if task.done():
            return {"status": "complete", "result": task.result()}
        else:
            return {"status": "running"}
```

**Prevention Tips:**

1. **Always set timeouts** for external operations
2. **Make long operations cancellable**
3. **Show progress** for operations >5 seconds
4. **Use async/await** properly (don't block event loop)
5. **Test worst-case scenarios** (slow network, large files)
6. **Provide manual cancellation** mechanisms

---

### 13.1.5 Agent Communication Issues

Multi-agent communication problems involve message passing, shared state, and coordination.

---

#### Problem: Agents Not Receiving Messages from Each Other

**Symptoms:**
- Agent A sends message but Agent B doesn't respond
- Message queue appears empty
- Orchestrator doesn't relay messages correctly
- Messages arrive out of order

**Root Causes:**

1. **Incorrect Agent IDs**: Sending to wrong agent
2. **Message Bus Not Initialized**: Shared event bus not configured
3. **Async Issues**: Awaiting message send but not handling receive
4. **Serialization Failures**: Complex objects can't be passed
5. **Subscription Not Set Up**: Receiver isn't listening for messages

**Step-by-Step Solution:**

**Step 1: Verify Agent Registration**

```python
from friday_agent import OrchestratorAgent, CopilotAgent

orchestrator = OrchestratorAgent()

# Register all agents
agent_a = CopilotAgent(...)
agent_b = CopilotAgent(...)

orchestrator.register_agent("agent_a", agent_a)
orchestrator.register_agent("agent_b", agent_b)

# Verify registration
print(orchestrator.list_agents())
# Should print: ['agent_a', 'agent_b']
```

**Step 2: Enable Message Logging**

```python
import logging

# Log all message passing
logging.getLogger("friday_agent.orchestrator").setLevel(logging.DEBUG)

# Logs should show:
# "Agent agent_a sending message to agent_b"
# "Agent agent_b received message from agent_a"
# "Message content: ..."
```

**Step 3: Test Message Passing Directly**

```python
# Test without orchestrator
async def test_direct_messaging():
    from friday_agent.messaging import MessageBus

    bus = MessageBus()

    # Subscribe agent B to messages
    received_messages = []

    async def message_handler(message):
        received_messages.append(message)

    bus.subscribe("agent_b", message_handler)

    # Send message from agent A
    await bus.publish(
        sender="agent_a",
        recipient="agent_b",
        content="Test message"
    )

    # Wait for processing
    await asyncio.sleep(0.1)

    # Verify receipt
    assert len(received_messages) == 1
    print("Direct messaging works!")

await test_direct_messaging()
```

**Step 4: Check Message Serialization**

```python
import json
from datetime import datetime

# Complex objects might not serialize
message = {
    "text": "Hello",
    "timestamp": datetime.now(),  # Can't serialize directly!
    "data": custom_object  # Won't work!
}

# Use serializable types
message = {
    "text": "Hello",
    "timestamp": datetime.now().isoformat(),  # String
    "data": custom_object.dict()  # If Pydantic model
}

# Test serialization
try:
    json.dumps(message)
    print("Message is serializable")
except TypeError as e:
    print(f"Serialization error: {e}")
```

**Step 5: Implement Message Acknowledgment**

```python
class ReliableMessaging:
    def __init__(self):
        self.pending_acks = {}

    async def send_with_ack(self, recipient: str, content: dict, timeout: float = 5.0):
        message_id = str(uuid.uuid4())

        # Send message with ID
        await bus.publish(
            recipient=recipient,
            content={"id": message_id, **content}
        )

        # Wait for acknowledgment
        try:
            await asyncio.wait_for(
                self._wait_for_ack(message_id),
                timeout=timeout
            )
            return True
        except asyncio.TimeoutError:
            return False

    async def _wait_for_ack(self, message_id: str):
        while message_id not in self.pending_acks:
            await asyncio.sleep(0.1)
```

**Prevention Tips:**

1. **Use explicit agent IDs** (don't rely on defaults)
2. **Log all message passing** in development
3. **Test messaging** before complex orchestration
4. **Use serializable types** for message content
5. **Implement timeouts** for message waits
6. **Add acknowledgment** for critical messages

---

## 13.2 Debugging Strategies

### 13.2.1 Logging & Telemetry

Effective logging is essential for diagnosing Friday agent issues. This section covers logging configuration, analysis techniques, and telemetry integration.

---

#### Comprehensive Logging Configuration

**Step 1: Configure Python Logging**

```python
import logging
import sys

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/friday/agent.log')
    ]
)

# Configure Friday package loggers
friday_loggers = [
    'friday_core',
    'friday_memory',
    'friday_llm',
    'friday_agent',
    'friday_tools',
]

for logger_name in friday_loggers:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # Verbose Friday logs
```

**Step 2: Enable Component-Specific Logging**

```python
# Memory operations (retrieval, storage, lifecycle)
logging.getLogger('friday_memory.context').setLevel(logging.DEBUG)
logging.getLogger('friday_memory.lifecycle').setLevel(logging.INFO)
logging.getLogger('friday_memory.adapters').setLevel(logging.DEBUG)

# LLM calls (requests, responses, token counts)
logging.getLogger('friday_llm.service').setLevel(logging.DEBUG)
logging.getLogger('friday_llm.circuit_breaker').setLevel(logging.INFO)

# Agent execution (Re-Act loop, tool calls)
logging.getLogger('friday_agent.copilot').setLevel(logging.DEBUG)
logging.getLogger('friday_agent.tools').setLevel(logging.DEBUG)

# Tool execution details
logging.getLogger('friday_tools').setLevel(logging.DEBUG)
```

**Step 3: Structured Logging with JSON**

```python
import json
import logging

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_data['session_id'] = record.session_id
        if hasattr(record, 'token_count'):
            log_data['token_count'] = record.token_count

        return json.dumps(log_data)

# Apply formatter
handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())
logging.getLogger().addHandler(handler)
```

**Step 4: Log Contextual Information**

```python
# Use extra parameter to add context
logger = logging.getLogger(__name__)

logger.info(
    "Context assembled successfully",
    extra={
        'user_id': 'user_123',
        'session_id': 'session_456',
        'token_count': 1523,
        'retrieved_insights': 5,
        'retrieved_entities': 8
    }
)

# Use adapters for automatic context
class AgentLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        # Automatically add session context
        extra = kwargs.get('extra', {})
        extra.update({
            'session_id': self.extra['session_id'],
            'user_id': self.extra['user_id'],
            'agent_name': self.extra['agent_name']
        })
        kwargs['extra'] = extra
        return msg, kwargs

# Use adapter
adapter = AgentLoggerAdapter(
    logger,
    {
        'session_id': session_id,
        'user_id': user_id,
        'agent_name': 'CopilotAgent'
    }
)

adapter.info("Processing user query")  # Automatically includes context
```

**Step 5: Performance Logging**

```python
import time
from contextlib import contextmanager

@contextmanager
def log_performance(operation_name: str, logger: logging.Logger):
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        logger.info(
            f"{operation_name} completed",
            extra={'duration_ms': duration * 1000}
        )

# Use in code
with log_performance("context_assembly", logger):
    context_payload = await context_engine.assemble_context(...)

# Logs: "context_assembly completed" with duration_ms
```

---

#### Log Analysis Techniques

**Pattern 1: Trace Request Flow**

```bash
# Find all logs for a specific session
grep "session_abc123" agent.log | less

# Trace a specific request
grep "request_id_xyz" agent.log | \
  awk '{print $1, $2, $4, $5}' | \
  column -t

# Output:
# 2026-01-24 10:15:23 [INFO] friday_agent: Query received
# 2026-01-24 10:15:23 [DEBUG] friday_memory: Assembling context
# 2026-01-24 10:15:24 [DEBUG] friday_memory: Retrieved 5 insights
# 2026-01-24 10:15:24 [DEBUG] friday_llm: Calling LLM with 1523 tokens
# 2026-01-24 10:15:26 [INFO] friday_agent: Response generated
```

**Pattern 2: Identify Performance Bottlenecks**

```bash
# Extract duration metrics
grep "duration_ms" agent.log | \
  jq -r '[.operation, .duration_ms] | @csv' | \
  sort -t',' -k2 -rn | \
  head -20

# Output: slowest operations
# "context_assembly",3456.7
# "llm_call",2890.3
# "memory_retrieval",1234.5
```

**Pattern 3: Find Errors and Exceptions**

```bash
# All errors
grep "ERROR" agent.log | wc -l

# Error types
grep "ERROR" agent.log | \
  sed 's/.*ERROR] //' | \
  sed 's/:.*//' | \
  sort | uniq -c | sort -rn

# Stack traces
grep -A 20 "Traceback" agent.log
```

**Pattern 4: Monitor Token Usage**

```bash
# Total tokens used
grep "token_count" agent.log | \
  jq '.token_count' | \
  awk '{sum+=$1} END {print "Total tokens:", sum}'

# Average tokens per request
grep "token_count" agent.log | \
  jq '.token_count' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count}'

# Highest token requests
grep "token_count" agent.log | \
  jq -r '[.timestamp, .token_count] | @csv' | \
  sort -t',' -k2 -rn | \
  head -10
```

---

#### Telemetry Integration

**OpenTelemetry Setup**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Configure OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Export to Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Use in Friday agent
from friday_agent import CopilotAgent

async def instrumented_run(agent: CopilotAgent, query: str):
    with tracer.start_as_current_span("agent_run") as span:
        span.set_attribute("query_length", len(query))

        # Context assembly span
        with tracer.start_as_current_span("context_assembly"):
            context = await agent.context_engine.assemble_context(...)
            span.set_attribute("context_tokens", context.total_tokens)

        # LLM call span
        with tracer.start_as_current_span("llm_call"):
            response = await agent.llm.chat_completion(...)
            span.set_attribute("response_tokens", response.usage.total_tokens)

        return response
```

**Custom Metrics**

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
agent_requests = Counter(
    'friday_agent_requests_total',
    'Total agent requests',
    ['agent_name', 'status']
)

agent_latency = Histogram(
    'friday_agent_latency_seconds',
    'Agent request latency',
    ['agent_name']
)

memory_size = Gauge(
    'friday_memory_entities_total',
    'Total entities in memory',
    ['user_id']
)

# Use metrics
async def monitored_agent_run(agent: CopilotAgent, query: str):
    start = time.time()

    try:
        response = await agent.run(query)
        agent_requests.labels(agent_name='copilot', status='success').inc()
        return response
    except Exception as e:
        agent_requests.labels(agent_name='copilot', status='error').inc()
        raise
    finally:
        duration = time.time() - start
        agent_latency.labels(agent_name='copilot').observe(duration)

# Expose metrics endpoint
from prometheus_client import start_http_server
start_http_server(8000)  # Metrics at http://localhost:8000/metrics
```

---

### 13.2.2 Interactive Debugging

#### Using Friday CLI Debug Mode

```bash
# Start CLI in debug mode
friday-cli --debug

# Available debug commands
/debug memory          # Show current memory state
/debug context         # Show last context payload
/debug tokens          # Show token usage breakdown
/debug tools           # List registered tools
/debug session         # Show session information
/debug llm             # Show LLM configuration

# Example: Inspect memory
> /debug memory

Memory State:
  Vector Store: 156 insights
    - Short-term: 23
    - Long-term: 98
    - Decayed: 35
  Graph Store: 89 entities, 234 relationships
  Episodic Store: 45 conversation turns

Last Maintenance:
  Decay cycle: 2 hours ago
  Promotion cycle: 6 hours ago
```

#### Python Debugger Integration

```python
# Set breakpoint in agent code
import pdb

class CopilotAgent(AgentBase):
    async def run(self, input_signal: str):
        # Debug context assembly
        context_payload = await self.context_engine.assemble_context(...)

        pdb.set_trace()  # Breakpoint here
        # Inspect variables:
        # (Pdb) p context_payload.total_tokens
        # (Pdb) p len(context_payload.insights)
        # (Pdb) p [e.name for e in context_payload.entities]

        messages = await self.context_engine.format_prompt(...)
        return await self._execute_loop(messages)
```

#### Remote Debugging with VS Code

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Friday Agent",
            "type": "python",
            "request": "launch",
            "module": "friday_cli",
            "args": ["chat"],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "LOG_LEVEL": "DEBUG"
            },
            "justMyCode": false  // Step into Friday code
        }
    ]
}
```

---

### 13.2.3 Transcript Analysis

The transcript system records every interaction for later analysis.

#### Exporting Transcripts

```python
from friday_memory.adapters.episodic import TranscriptStoreAdapter

adapter = TranscriptStoreAdapter(db_path="~/.friday/memory/transcript.db")

# Export to JSONL for analysis
await adapter.export_jsonl(
    output_path="/tmp/transcript.jsonl",
    session_id="optional_filter",
    start_date="2026-01-01",
    end_date="2026-01-24"
)

# Export to Markdown for human review
await adapter.export_markdown(
    output_path="/tmp/transcript.md",
    session_id="session_123"
)
```

#### Analyzing Conversation Patterns

```python
import json
from collections import Counter

# Load transcript
with open('/tmp/transcript.jsonl') as f:
    turns = [json.loads(line) for line in f]

# Analyze tool usage
tool_calls = []
for turn in turns:
    if turn['tool_calls']:
        tool_calls.extend([tc['name'] for tc in turn['tool_calls']])

tool_usage = Counter(tool_calls)
print("Most used tools:")
for tool, count in tool_usage.most_common(10):
    print(f"  {tool}: {count}")

# Analyze token usage over time
import matplotlib.pyplot as plt

timestamps = [turn['timestamp'] for turn in turns]
tokens = [turn['token_count'] for turn in turns]

plt.plot(timestamps, tokens)
plt.xlabel('Time')
plt.ylabel('Tokens per Turn')
plt.title('Token Usage Over Time')
plt.savefig('/tmp/token_usage.png')
```

#### Detecting Failure Patterns

```python
# Find failed turns
failures = [t for t in turns if t.get('error')]

print(f"Found {len(failures)} failed turns")
for failure in failures:
    print(f"\nTimestamp: {failure['timestamp']}")
    print(f"Error: {failure['error']}")
    print(f"Query: {failure['user_message'][:100]}...")

# Group by error type
error_types = Counter([f['error'].split(':')[0] for f in failures])
print("\nError distribution:")
for error_type, count in error_types.most_common():
    print(f"  {error_type}: {count}")
```

---

## 13.3 Performance Tuning

### 13.3.1 Latency Optimization

Reducing response latency is critical for interactive agents.

---

#### Target Benchmarks

**Acceptable Latency by Agent Type:**

| Agent Type | Target Latency | Max Acceptable |
|------------|---------------|----------------|
| Chat (no tools) | < 2 seconds | 5 seconds |
| Chat (with tools) | < 5 seconds | 10 seconds |
| Code generation | < 10 seconds | 30 seconds |
| Long research tasks | < 30 seconds | 2 minutes |

**Component Latency Targets:**

| Component | Target | Notes |
|-----------|--------|-------|
| Memory retrieval | < 200ms | Vector + graph query |
| Context assembly | < 500ms | Full knapsack optimization |
| LLM call | 1-3s | Depends on model, tokens |
| Tool execution | < 1s | Per tool, excluding long ops |

---

#### Profiling Agent Performance

```python
import cProfile
import pstats
from pstats import SortKey

# Profile agent run
profiler = cProfile.Profile()
profiler.enable()

# Run agent
response = await agent.run("What's the weather?")

profiler.disable()

# Analyze results
stats = pstats.Stats(profiler)
stats.sort_stats(SortKey.CUMULATIVE)
stats.print_stats(20)  # Top 20 slowest functions

# Output shows where time is spent:
# ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#    1    0.001    0.001    2.456    2.456 copilot.py:50(run)
#    1    0.123    0.123    1.234    1.234 context.py:100(assemble_context)
#    1    0.045    0.045    0.890    0.890 service.py:200(chat_completion)
```

#### Optimization: Parallel Memory Retrieval

```python
import asyncio

# SLOW: Sequential retrieval
insights = await memory.retrieve_insights(query)
entities = await memory.retrieve_entities(query)
history = await memory.get_recent_history(session_id)

# FAST: Parallel retrieval
insights, entities, history = await asyncio.gather(
    memory.retrieve_insights(query),
    memory.retrieve_entities(query),
    memory.get_recent_history(session_id)
)

# Reduces latency from 600ms to 200ms (fastest of three)
```

#### Optimization: Streaming Responses

```python
# Instead of waiting for complete response
response = await agent.run("Long query...")  # 5 seconds

# Stream response as it's generated
async for chunk in agent.run_streaming("Long query..."):
    print(chunk, end='', flush=True)  # First token in 500ms
```

#### Optimization: Caching

```python
from functools import lru_cache
from friday_memory import MemoryController

class CachedMemoryController:
    def __init__(self, memory: MemoryController):
        self.memory = memory
        self._insight_cache = {}

    async def retrieve_insights(self, query: str, limit: int = 10):
        cache_key = f"{query}:{limit}"

        # Check cache
        if cache_key in self._insight_cache:
            cached_result, timestamp = self._insight_cache[cache_key]

            # Cache valid for 5 minutes
            if time.time() - timestamp < 300:
                return cached_result

        # Cache miss - retrieve and cache
        result = await self.memory.retrieve_insights(query, limit)
        self._insight_cache[cache_key] = (result, time.time())

        return result
```

#### Optimization: Reduce Context Size

```python
# Smaller context = faster LLM calls
config = ContextEngineeringConfig(
    max_history_turns=5,  # Down from 10
    max_retrieved_insights=3,  # Down from 10
    max_retrieved_entities=5,  # Down from 20
)

# Trade-off: Less context but faster responses
```

---

### 13.3.2 Cost Optimization

Minimizing LLM API costs while maintaining quality.

---

#### Understanding Costs

**Cost by Model (per 1M tokens, as of 2026):**

| Provider | Model | Input | Output | Notes |
|----------|-------|-------|--------|-------|
| OpenAI | GPT-4o | $2.50 | $10.00 | Best quality |
| OpenAI | GPT-4o-mini | $0.15 | $0.60 | Best value |
| Anthropic | Claude 3.5 Sonnet | $3.00 | $15.00 | Great quality |
| Anthropic | Claude 3 Haiku | $0.25 | $1.25 | Fast, cheap |
| Google | Gemini 2.5 Pro | $1.25 | $5.00 | Large context |
| Google | Gemini 2.5 Flash | $0.10 | $0.40 | Cheapest |

**Example Cost Calculation:**

```python
# Typical agent query
input_tokens = 2000  # Context + query
output_tokens = 500  # Response

# GPT-4o cost
cost_gpt4o = (2000 * 2.50 / 1_000_000) + (500 * 10.00 / 1_000_000)
print(f"GPT-4o: ${cost_gpt4o:.4f}")  # $0.0100

# GPT-4o-mini cost
cost_mini = (2000 * 0.15 / 1_000_000) + (500 * 0.60 / 1_000_000)
print(f"GPT-4o-mini: ${cost_mini:.4f}")  # $0.0006

# Savings: 94%
```

---

#### Strategy 1: Use Cheaper Models for Extraction

```python
from friday_llm import LiteLLMService

# Main agent uses high-quality model
main_llm = LiteLLMService(
    model="gpt-4o",  # $2.50/$10 per 1M tokens
    temperature=0.7
)

# Extraction uses cheap model
extraction_llm = LiteLLMService(
    model="gpt-4o-mini",  # $0.15/$0.60 per 1M tokens
    temperature=0.3
)

# Configure memory to use cheap model for extraction
memory_controller = MemoryController(
    extraction_llm=extraction_llm,  # 94% cheaper
    ...
)

# Savings: Extraction is 30-40% of total token usage
```

#### Strategy 2: Token Budget Optimization

```python
# Monitor token usage
from friday_llm.pricing import TokenPriceCalculator

calculator = TokenPriceCalculator()

response = await llm.chat_completion(messages=messages)

cost = calculator.calculate_cost(
    model="gpt-4o",
    input_tokens=response.usage.prompt_tokens,
    output_tokens=response.usage.completion_tokens
)

print(f"Request cost: ${cost:.6f}")

# Set aggressive budget limits
config = ContextEngineeringConfig(
    context_window_tokens=4000,  # Down from 8000
    max_retrieved_insights=3,  # Fewer memories
)

# Reduces input tokens by 50% = 50% cost reduction
```

#### Strategy 3: Caching for Repeated Queries

```python
from friday_llm import LiteLLMService

# Enable prompt caching (supported by some providers)
llm = LiteLLMService(
    model="claude-3-5-sonnet-20241022",
    # Anthropic charges 10% of input cost for cached tokens
    cache_prompts=True
)

# For repeated queries with same context:
# - First call: Full price
# - Subsequent calls: 10% input price (90% savings on cached portion)
```

#### Strategy 4: Local Models for Development

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model (free)
ollama pull llama3

# Use local model (zero cost)
```

```python
from friday_llm import LiteLLMService

# Use local model in development
llm = LiteLLMService(
    model="ollama/llama3",
    api_base="http://localhost:11434",
    # No API key needed, zero cost
)
```

#### Strategy 5: Monitor and Alert on Usage

```python
from datetime import datetime, timedelta

class CostMonitor:
    def __init__(self, daily_budget: float):
        self.daily_budget = daily_budget
        self.daily_usage = 0.0
        self.reset_time = datetime.now()

    def track_request(self, cost: float):
        # Reset daily counter
        if datetime.now() - self.reset_time > timedelta(days=1):
            self.daily_usage = 0.0
            self.reset_time = datetime.now()

        self.daily_usage += cost

        # Alert if over budget
        if self.daily_usage > self.daily_budget:
            raise RuntimeError(
                f"Daily budget exceeded: ${self.daily_usage:.2f} > ${self.daily_budget:.2f}"
            )

        # Warn at 80% of budget
        if self.daily_usage > self.daily_budget * 0.8:
            logger.warning(
                f"Budget warning: ${self.daily_usage:.2f} / ${self.daily_budget:.2f} used"
            )

# Use monitor
monitor = CostMonitor(daily_budget=10.0)  # $10/day

response = await llm.chat_completion(messages=messages)
cost = calculator.calculate_cost(...)
monitor.track_request(cost)
```

---

### 13.3.3 Memory Optimization

Optimizing memory storage and retrieval for large deployments.

---

#### Problem: Large Memory Stores Slow Down Over Time

**Symptoms:**
- Retrieval gets slower as memory grows
- Database file sizes reach gigabytes
- Queries that took 100ms now take 5+ seconds
- Memory footprint grows continuously

**Solutions:**

**1. Regular Maintenance and Pruning**

```python
from friday_memory.lifecycle import MemoryLifecycleManager

manager = MemoryLifecycleManager(memory_controller)

# Run weekly maintenance
async def weekly_maintenance():
    # Apply decay to outdated memories
    await manager.apply_decay()

    # Promote valuable recent memories
    await manager.run_promotion_cycle()

    # Remove fully decayed memories older than 90 days
    cleanup_results = await manager.cleanup_decayed_memories(
        min_days_since_access=90,
        min_decay_score=0.05
    )

    print(f"Cleaned up {cleanup_results.removed_count} memories")

# Schedule with cron or systemd timer
```

**2. Partition Memory by User**

```python
# Instead of single shared vector store
# Use per-user collections
from friday_memory.adapters.vector import ChromaAdapter

class PartitionedVectorStore:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.adapters = {}

    def get_adapter_for_user(self, user_id: str) -> ChromaAdapter:
        if user_id not in self.adapters:
            self.adapters[user_id] = ChromaAdapter(
                persist_directory=f"{self.base_path}/{user_id}",
                collection_name="memories_long_term"
            )
        return self.adapters[user_id]

# Benefits:
# - Smaller per-user stores (faster queries)
# - Can archive inactive users
# - Better privacy isolation
```

**3. Use Enterprise Databases for Scale**

```python
# For >100K memories, switch to enterprise solutions

# Neo4j for graph (scales to billions of nodes)
from friday_memory.adapters.graph import Neo4jAdapter

graph_adapter = Neo4jAdapter(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Pinecone for vectors (managed, auto-scaling)
from friday_memory.adapters.vector import PineconeAdapter

vector_adapter = PineconeAdapter(
    api_key=os.environ["PINECONE_API_KEY"],
    environment="us-east-1-aws",
    index_name="friday-memories"
)

# Benefits:
# - Professional indexing and optimization
# - Horizontal scaling
# - Managed backups
```

**4. Implement TTL (Time-To-Live) Policies**

```python
from datetime import datetime, timedelta

class TTLMemoryController:
    def __init__(self, memory: MemoryController, ttl_days: int):
        self.memory = memory
        self.ttl_days = ttl_days

    async def retrieve_insights(self, query: str, limit: int = 10):
        # Get all results
        results = await self.memory.retrieve_insights(query, limit * 2)

        # Filter by TTL
        cutoff = datetime.now() - timedelta(days=self.ttl_days)
        filtered = [
            r for r in results
            if r.created_at > cutoff
        ]

        return filtered[:limit]

# Use with short TTL for chat (30 days) vs long TTL for knowledge base (365 days)
```

**5. Compress Old Memories**

```python
# Summarize old conversation turns to save space
from friday_memory.context import ConversationSummarizer

summarizer = ConversationSummarizer(llm_client=llm)

# Summarize turns older than 30 days
old_turns = await transcript_adapter.get_turns_before(
    date=datetime.now() - timedelta(days=30)
)

if len(old_turns) > 20:
    summary = await summarizer.summarize_turns(old_turns)

    # Store summary as single memory
    await memory.add_insight(
        content=f"Historical context (30+ days ago): {summary}",
        confidence=1.0,
        metadata={"type": "summary", "turn_count": len(old_turns)}
    )

    # Delete original turns
    await transcript_adapter.delete_turns([t.id for t in old_turns])

    print(f"Compressed {len(old_turns)} turns into 1 summary")
```

---

## 13.4 FAQ

### General Questions

**Q: Can Friday run completely offline?**

A: Yes, with limitations. Friday can run offline using local LLM providers (Ollama) and local storage adapters (ChromaDB, NetworkX, SQLite). However:

- **Offline-capable components:**
  - Local LLM inference with Ollama (Llama 3, Mistral, etc.)
  - Vector storage with ChromaDB (local SQLite)
  - Graph storage with NetworkX + JSON
  - Episodic storage with SQLite
  - All Friday core functionality

- **Requires internet:**
  - Cloud LLM providers (OpenAI, Anthropic, Google)
  - Web search tools
  - Remote MCP services used through separate programmatic clients (the
    integrated client uses local stdio)
  - Package installation (uv sync)

- **Setup for offline:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3

# Configure Friday to use local model
```

```python
from friday_llm import LiteLLMService

llm = LiteLLMService(
    model="ollama/llama3",
    api_base="http://localhost:11434"
)
```

**Performance note:** Local models are 2-10x slower than cloud models and generally lower quality, but sufficient for many use cases.

---

**Q: How much does it cost to run Friday?**

A: Cost depends entirely on your LLM provider and usage:

**Development (low volume):**
- ~$1-5/month with GPT-4o-mini
- ~$10-20/month with GPT-4o
- $0/month with Ollama (local)

**Production (100 queries/day):**
- ~$10-30/month with GPT-4o-mini
- ~$100-300/month with GPT-4o
- ~$5-15/month with Claude Haiku
- $0/month with Ollama (hardware cost instead)

**Cost factors:**
- Model choice (see section 13.3.2)
- Context window size (larger = more expensive)
- Query frequency
- Memory extraction frequency
- Tool usage (more turns = more cost)

**Cost optimization tips:**
1. Use GPT-4o-mini or Claude Haiku for extraction (94% savings)
2. Set aggressive token budgets
3. Use caching for repeated queries
4. Run maintenance to prune memories
5. Use local models for development

---

**Q: What are the hardware requirements?**

**Minimum (cloud LLMs):**
- 2 CPU cores
- 4GB RAM
- 10GB disk (for memories and transcripts)
- Internet connection

**Recommended (cloud LLMs):**
- 4+ CPU cores
- 8GB RAM
- 50GB SSD
- Stable internet (1+ Mbps)

**Local LLMs (Ollama):**
- 4+ CPU cores (8+ recommended)
- 8GB RAM minimum (16GB+ recommended)
- 50GB disk (models are large)
- GPU optional but highly recommended:
  - NVIDIA GPU with 6GB+ VRAM (e.g., RTX 3060)
  - Apple Silicon M1/M2/M3 (uses Metal)

**Large deployments (1000+ users):**
- Dedicated database servers (Neo4j, PostgreSQL)
- Vector database cluster (Pinecone, Weaviate)
- Load balancer for agent instances
- Redis for caching
- Kubernetes cluster recommended

---

**Q: Can I migrate from LangChain/AutoGPT/CrewAI?**

A: Yes, but requires code changes. Friday has a different architecture than wrapper libraries.

**Migration from LangChain:**

```python
# LangChain code
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
profile = AgentProfile(name="Agent")
agent = CopilotAgent(
    profile=profile,
    llm=llm,
    tool_registry=registry
)
result = await agent.run("query")
```

**Key differences:**
- Friday is fully async (`await`)
- Memory is built-in (not optional)
- Tools are protocol-based (cleaner interfaces)
- No "chains" concept (use workflows instead)

**Migration strategy:**
1. Start with new Friday agent alongside existing code
2. Port tools one at a time (tools are standalone)
3. Migrate conversation history to transcript store
4. Switch traffic gradually
5. Remove old framework once validated

**Time estimate:** 1-2 weeks for medium-sized application

---

**Q: Is Friday production-ready?**

A: **Friday v0.1.0 is early development phase.**

**What works well:**
- Core memory architecture (tested with 10K+ memories)
- LLM integrations (OpenAI, Anthropic, Google, Ollama)
- Tool system (50+ built-in tools)
- Single-agent workflows
- Transcript logging

**What's experimental:**
- Multi-agent orchestration (basic functionality)
- Broader remote MCP integration beyond the implemented local-stdio client
- Sandbox isolation (Docker version pending)
- Distributed deployments

**Production recommendations:**
- ✅ Use for internal tools and prototypes
- ✅ Use with proper error handling and monitoring
- ✅ Test thoroughly in staging environment
- ⚠️ Use caution for customer-facing applications
- ⚠️ Implement fallbacks for critical paths
- ❌ Don't use for mission-critical systems (yet)

**Production checklist:**
- [ ] Comprehensive logging configured
- [ ] Error handling and circuit breakers
- [ ] Rate limiting and cost monitoring
- [ ] Regular memory maintenance scheduled
- [ ] Backup strategy for memory stores
- [ ] Monitoring and alerting set up
- [ ] Staging environment for testing
- [ ] Rollback plan

**Roadmap to v1.0 (production-ready):**
- Enhanced error recovery
- Production-grade orchestration
- Comprehensive test coverage
- Performance benchmarks
- Migration tools
- Enterprise authentication
- SLA guarantees

---

**Q: How does Friday compare to LangChain/AutoGPT/CrewAI?**

**Friday vs LangChain:**

| Feature | Friday | LangChain |
|---------|--------|-----------|
| Architecture | Protocol-first, modular | Wrapper library |
| Memory | Three-tier, adaptive | Basic (separate LangMem) |
| Learning | Hebbian, decay, promotion | No learning |
| Multi-agent | Built-in orchestration | LangGraph (separate) |
| Vendor lock-in | Zero (protocols) | Moderate |
| Complexity | Medium | High (many abstractions) |
| Best for | Stateful agents | Quick integrations |

**Friday vs AutoGPT:**

| Feature | Friday | AutoGPT |
|---------|--------|---------|
| Architecture | Framework (library) | Application (run it) |
| Memory | Sophisticated (3-tier) | Vector only |
| Control | Full programmatic | Limited (autonomous) |
| Tool system | 50+ extensible | Fixed set |
| Multi-agent | Yes | No |
| Best for | Building agents | Autonomous tasks |

**Friday vs CrewAI:**

| Feature | Friday | CrewAI |
|---------|--------|--------|
| Focus | General agent framework | Multi-agent teams |
| Memory | Per-agent + shared | Shared context |
| Flexibility | High (protocols) | Medium |
| Learning | Adaptive memory | Static |
| Orchestration | Flexible patterns | Role-based |
| Best for | Any agent type | Collaborative teams |

**When to choose Friday:**
- Need genuine memory and learning
- Building long-running agents
- Want zero vendor lock-in
- Need protocol-based extensibility
- Want full control over behavior

**When to choose alternatives:**
- Quick prototype (LangChain)
- Autonomous agent (AutoGPT)
- Primarily multi-agent teams (CrewAI)
- Prefer mature, battle-tested (LangChain)

---

**Q: Can Friday agents collaborate with non-Friday agents?**

A: Yes, through multiple mechanisms:

**1. MCP (Model Context Protocol)**

Friday's integrated runtime can consume tools from a configured **local
stdio** MCP server through `tools.providers.mcp`. See the
[MCP client guide](17-mcp-client.md) for a working configuration and its
limits. The former HTTP `MCPClient`/`register_mcp_tools` example did not
describe this implemented integration; remote transports and Friday-as-server
APIs are separate programmatic surfaces, not Chat configuration features.

**2. REST API Wrapper**

Expose Friday agent as REST API:

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/chat")
async def chat(query: str, session_id: str):
    response = await friday_agent.run(query)
    return {"response": response}

# Other systems call HTTP endpoint
```

**3. Message Queue Integration**

```python
import aio_pika

async def message_handler(message: aio_pika.IncomingMessage):
    query = message.body.decode()
    response = await friday_agent.run(query)

    # Publish response
    await channel.default_exchange.publish(
        aio_pika.Message(body=response.encode()),
        routing_key=message.reply_to
    )

# Connect to RabbitMQ
connection = await aio_pika.connect_robust("amqp://localhost")
channel = await connection.channel()
queue = await channel.declare_queue("friday_input")
await queue.consume(message_handler)
```

**4. Shared Memory Store**

Multiple agents (Friday or not) can share memory:

```python
# Friday agent A
agent_a = CopilotAgent(
    memory=shared_memory_controller,  # Shared instance
    ...
)

# Non-Friday agent B (custom implementation)
class CustomAgent:
    def __init__(self, memory: MemoryController):
        self.memory = memory  # Same shared memory

    async def process(self, query: str):
        # Query shared memory
        insights = await self.memory.retrieve_insights(query)
        # ... custom logic
```

---

**Q: How do I backup and restore Friday memory?**

**Backup Strategy:**

```bash
#!/bin/bash
# backup-friday-memory.sh

BACKUP_DIR="/backups/friday-$(date +%Y%m%d-%H%M%S)"
MEMORY_DIR="$HOME/.friday/memory"

mkdir -p "$BACKUP_DIR"

# Backup all memory files
cp "$MEMORY_DIR/chroma.sqlite3" "$BACKUP_DIR/"
cp "$MEMORY_DIR/graph.json" "$BACKUP_DIR/"
cp "$MEMORY_DIR/transcript.db" "$BACKUP_DIR/"

# Compress
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "Backup created: $BACKUP_DIR.tar.gz"

# Optional: Upload to S3
# aws s3 cp "$BACKUP_DIR.tar.gz" s3://my-bucket/friday-backups/
```

**Restore:**

```bash
#!/bin/bash
# restore-friday-memory.sh

BACKUP_FILE="$1"
MEMORY_DIR="$HOME/.friday/memory"

# Stop Friday agent first!
# systemctl stop friday-agent

# Extract backup
tar -xzf "$BACKUP_FILE" -C /tmp/

# Restore files
cp /tmp/friday-*/chroma.sqlite3 "$MEMORY_DIR/"
cp /tmp/friday-*/graph.json "$MEMORY_DIR/"
cp /tmp/friday-*/transcript.db "$MEMORY_DIR/"

# Cleanup
rm -rf /tmp/friday-*

echo "Memory restored from $BACKUP_FILE"

# Restart agent
# systemctl start friday-agent
```

**Programmatic Export/Import:**

```python
from friday_memory import MemoryController
import json

# Export to JSON
async def export_memory(memory: MemoryController, output_path: str):
    data = {
        "entities": [e.dict() for e in await memory.graph_store.get_all_entities()],
        "relationships": [r.dict() for r in await memory.graph_store.get_all_relationships()],
        "insights": await memory.vector_store.export_all(),
        "transcript": await memory.episodic_store.export_all()
    }

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

# Import from JSON
async def import_memory(memory: MemoryController, input_path: str):
    with open(input_path) as f:
        data = json.load(f)

    # Import entities
    for entity_data in data["entities"]:
        await memory.graph_store.add_entity(Entity(**entity_data))

    # Import relationships
    for rel_data in data["relationships"]:
        await memory.graph_store.add_relationship(Relationship(**rel_data))

    # Import insights
    await memory.vector_store.import_all(data["insights"])

    # Import transcript
    await memory.episodic_store.import_all(data["transcript"])
```

---

**Q: Can I use Friday without the memory system?**

A: Yes, but you lose the main value proposition. Friday's memory is what makes it unique.

**Minimal Agent (no memory):**

```python
from friday_llm import LiteLLMService
from friday_agent.tools import DefaultToolRegistry

# Just LLM + tools
llm = LiteLLMService(model="gpt-4o")
registry = DefaultToolRegistry()

# Manual Re-Act loop
messages = [{"role": "user", "content": "Query"}]

while True:
    response = await llm.chat_completion(
        messages=messages,
        tools=registry.get_tool_schemas()
    )

    if not response.tool_calls:
        break  # Done

    # Execute tools
    for tool_call in response.tool_calls:
        result = await registry.execute_tool(
            tool_call.name,
            tool_call.arguments
        )
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })
```

**Use cases for memory-free:**
- One-off queries
- Stateless APIs
- Testing/debugging
- Cost optimization (extraction has cost)

**Better approach:** Use individual Friday packages:

```bash
# Just LLM client
pip install friday-llm

# Just tools
pip install friday-tools

# Just memory (for your own agent)
pip install friday-memory
```

This gives you Friday's quality without the full framework.

---

**Q: How do I contribute to Friday?**

A: Friday welcomes contributions! (Once repository is public)

**Ways to contribute:**

1. **Bug reports** - Open GitHub issues with reproduction steps
2. **Feature requests** - Discuss in GitHub Discussions
3. **Documentation** - Improve guides, add examples
4. **Code** - Submit pull requests (see CONTRIBUTING.md)
5. **Tools** - Create new tool implementations
6. **Adapters** - Implement storage adapters for new databases

**Development setup:**

```bash
# Fork repository
git clone https://github.com/your-username/friday-agent-framework.git
cd friday-agent-framework

# Install in development mode
uv sync

# Run tests
pytest

# Lint and format
uv run ruff check .
uv run ruff format .

# Create feature branch
git checkout -b feature/my-new-feature

# Make changes, commit
git commit -m "Add my new feature"

# Push and create PR
git push origin feature/my-new-feature
```

**Contribution guidelines:**
- Follow existing code style (Ruff)
- Add tests for new features
- Update documentation
- Reference specs in code comments
- Be respectful in discussions

---

## Conclusion

This troubleshooting guide covered the most common Friday Framework issues, debugging strategies, performance tuning, and frequently asked questions. The key to successful Friday deployment is:

1. **Proactive Monitoring** - Log everything, track metrics, set up alerts
2. **Regular Maintenance** - Run lifecycle management, prune memories, optimize storage
3. **Incremental Tuning** - Measure first, optimize bottlenecks, validate improvements
4. **Cost Awareness** - Monitor usage, use appropriate models, implement budgets

**Remember:**
- Memory issues → Check storage, verify extraction, run maintenance
- LLM issues → Validate API keys, check rate limits, test models
- Performance issues → Profile execution, optimize retrieval, cache results
- Cost issues → Use cheaper models, set budgets, monitor usage

For additional support:
- Documentation: `/docs/guides/`
- GitHub Issues: Report bugs and request features
- Community: Discord/Slack (links in README)
- Commercial Support: Contact for enterprise deployments

**Next Steps:**
- Review Section 11 (Advanced Topics) for optimization techniques
- Check Section 10 (Configuration Guide) for tuning parameters
- Read Section 9 (CLI Reference) for debugging commands
- Explore Section 4 (Adaptive Memory) for memory lifecycle details

Happy building with Friday!
