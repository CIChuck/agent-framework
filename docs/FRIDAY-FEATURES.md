# Friday Framework - Feature Definition

**Version:** 0.1.0
**Last Updated:** 2026-01-09

---

## Executive Summary

### For Technology Leaders

Friday Framework is a modular, enterprise-ready Python framework for building AI-powered agentic applications. Designed with a clear separation between the "Mind" (intelligence and memory) and "Body" (execution and tools), Friday provides organizations with a flexible foundation for deploying autonomous AI agents that learn, remember, and act.

#### Key Value Propositions

**1. Persistent Memory & Contextual Intelligence**
Unlike stateless chatbots, Friday agents maintain persistent memory across sessions. The framework's three-tier memory architecture (Episodic, Semantic, and Associative) enables agents to build genuine understanding over time, learning user preferences, recalling past interactions, and making contextually relevant decisions.

**2. Provider-Agnostic LLM Integration**
Friday abstracts away LLM provider complexity through its LiteLLM integration layer. Deploy with OpenAI, Anthropic Claude, Google Gemini, local Ollama models, or any OpenRouter-accessible provider—switch between them with a single configuration change. This eliminates vendor lock-in and enables cost optimization strategies.

**3. Modular Monorepo Architecture**
Each Friday component is an independent, versioned package with clear interfaces. This enables:
- Incremental adoption (use only the packages you need)
- Independent scaling of components
- Clear dependency management
- Easier testing and maintenance

**4. Enterprise-Grade Observability**
Built-in telemetry, transcript logging, and debug tooling provide full visibility into agent decision-making. Every interaction is traceable, exportable, and auditable—critical for compliance and debugging production systems.

**5. Extensible Tool System**
Friday's tool architecture allows agents to interact with external systems, execute code, access filesystems, and integrate with any API. Tools are defined with Pydantic schemas, ensuring type safety and automatic documentation generation.

#### Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                      Friday Agent                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Memory    │  │     LLM     │  │       Tools         │  │
│  │ Controller  │◄─┤   Service   │─►│  (50+ available)    │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘  │
│         │                                                   │
│  ┌──────┴──────────────────────────────────────┐            │
│  │              Context Assembler               │           │
│  │  (Token Budgeting, Prompt Architecture)      │           │
│  └──────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
         │              │              │
    ┌────┴────┐   ┌─────┴─────┐   ┌───┴────┐
    │ Vector  │   │   Graph   │   │Episodic│
    │  Store  │   │   Store   │   │ Store  │
    │(ChromaDB)│  │(NetworkX) │   │(SQLite)│
    └─────────┘   └───────────┘   └────────┘
```

#### Investment Considerations

- **Development Stage:** Active development (v0.1.0), suitable for pilot projects and internal tools
- **Technology Stack:** Python 3.10+, async-first, Pydantic 2.0+ for data validation
- **Deployment:** Runs anywhere Python runs—cloud, on-premise, or edge devices
- **Licensing:** [Specify your license]

---

## Package Reference Guide

### For Developers & Power Users

Friday Framework consists of nine interconnected packages, each serving a specific role in the agentic architecture. Dependencies flow downward—packages only depend on packages listed above them.

---

### friday-core

**Location:** `packages/friday-core/`
**Purpose:** Foundation protocols, configuration, logging, and exceptions

#### Overview

friday-core establishes the contracts that all other packages implement. By defining abstract protocols (Python ABCs) rather than concrete implementations, Friday achieves true modularity—any component can be swapped without affecting the rest of the system.

#### Key Components

**Protocol Definitions (`interfaces/`)**
- `LLMClient` - Contract for language model inference
- `EmbeddingModel` - Contract for text embedding generation
- `ToolDefinition`, `ToolRegistry`, `ToolAdapter` - Tool management contracts
- `VectorStoreAdapter`, `GraphStoreAdapter`, `EpisodicStoreAdapter` - Storage contracts
- `ContextEngineeringInterface` - Context assembly contract
- `TelemetryRecorder` - Observability contract

**Configuration Management**
- YAML-based configuration loading
- Environment variable support
- Hierarchical config merging

**Logging Infrastructure**
- Structured logging with context propagation
- Log level configuration per component

**Exception Hierarchy**
- `FridayError` base class
- Domain-specific exceptions (Memory, LLM, Tool errors)

#### Usage Example

```python
from friday_core import TelemetryRecorder, DebugTelemetryRecorder
from friday_core.interfaces import VectorStoreAdapter

# Use the debug recorder for development
telemetry = DebugTelemetryRecorder()

# All adapters implement the protocol
class MyCustomVectorStore(VectorStoreAdapter):
    async def search(self, query: str, limit: int) -> list[dict]:
        ...
```

---

### friday-memory

**Location:** `packages/friday-memory/`
**Purpose:** Memory management, storage adapters, and context engineering

#### Overview

friday-memory is the "brain" of the Friday Framework. It orchestrates three distinct memory systems, assembles context for LLM calls, and implements learning mechanisms that make agents smarter over time.

#### Memory Architecture

**Three-Store Model:**

| Store | Implementation | Purpose | Retention |
|-------|---------------|---------|-----------|
| **Episodic** | SQLite (via Transcript) | Conversation history | Session-scoped |
| **Semantic** | ChromaDB | Document/insight search | Permanent |
| **Associative** | NetworkX Graph | Entity relationships | Permanent |

#### Key Components

**MemoryController**
The unified facade for all memory operations:
- `recall(query, session_id)` - Retrieve relevant context
- `store_insight(text, provenance)` - Save semantic memories
- `add_turn(session_id, turn)` - Record conversation turns
- `prime_session(session_id)` - Load context from prior sessions
- Automatic Hebbian learning (frequently accessed memories strengthen)

**ContextAssembler**
Orchestrates context construction:
- Token budget management (Knapsack algorithm for optimal packing)
- Dynamic context assembly from all three stores
- Session state management

**PromptArchitect (Layout Engine)**
Structures prompts for optimal LLM attention:
- Implements "Lost in the Middle" mitigation
- Places supporting context at tail (recency effect)
- Configurable output formats (plain, JSON, XML, markdown)

**Storage Adapters**
- `ChromaVectorStore` - Persistent vector storage with ChromaDB
- `ElementXGraphStore` - Graph storage with NetworkX, JSON persistence
- `TranscriptBackedEpisodicStore` - Conversation history via transcript

**MemoryExtractor**
LLM-powered extraction of structured knowledge:
- Entity extraction (people, projects, technologies)
- Relationship extraction (directional predicates)
- Insight extraction (semantic observations)
- Turn summarization

**ContextConsolidator**
Background optimization of memory:
- Conversation summarization
- Memory compaction
- Token budget optimization

#### Configuration Options

```yaml
memory:
  context_window: 64000
  output_buffer: 3000
  max_history_turns: 999
  context_format: plain  # plain, json, xml, markdown

  priming:
    enabled: true
    top_entities: 50
    max_insights: 10
    max_summaries: 10
    recency_days: 10
    token_budget: 10000
```

#### Usage Example

```python
from friday_memory import (
    MemoryController,
    ContextAssembler,
    PromptArchitect,
    ChromaVectorStore,
    ElementXGraphStore,
)

# Initialize stores
vector = ChromaVectorStore(collection_name="my_app", persist_directory="./data")
graph = ElementXGraphStore(storage_path="./data/graph.json")

# Create controller
controller = MemoryController(
    vector_store=vector,
    graph_store=graph,
    episodic_store=episodic,
    priming_config={"enabled": True, "top_entities": 50}
)

# Recall context for a query
payload = await controller.recall(
    query="What do you know about Python?",
    session_id="session_123",
)
```

---

### friday-llm

**Location:** `packages/friday-llm/`
**Purpose:** LLM provider abstraction via LiteLLM

#### Overview

friday-llm wraps LiteLLM to provide a unified interface for interacting with any language model provider. It adds resilience patterns, streaming support, and embedding services on top of LiteLLM's multi-provider capabilities.

#### Supported Providers

| Provider | Model Examples | Configuration |
|----------|---------------|---------------|
| OpenAI | gpt-4o, gpt-4o-mini | Direct API |
| Anthropic | claude-3.5-sonnet, claude-3-haiku | Direct API |
| Google | gemini-pro, gemini-2.5-flash | Via OpenRouter or direct |
| Ollama | llama3, mistral, qwen | Local API |
| OpenRouter | Any model via openrouter/* prefix | Single API key |
| LM Studio | Any local model | OpenAI-compatible API |

#### Key Components

**LiteLLMService**
Primary interface for chat completions:
- Synchronous and streaming responses
- Automatic retry with exponential backoff
- Circuit breaker for failing endpoints
- Request/response logging

**LiteLLMEmbeddingService**
Text embedding generation:
- Batch embedding support
- Provider-agnostic interface
- Configurable dimensions

**ResilienceConfig**
Fault tolerance configuration:
- `max_retries` - Retry attempts before failure
- `timeout_seconds` - Request timeout
- `circuit_breaker_threshold` - Failures before circuit opens

#### Error Handling

```python
from friday_llm import (
    LLMTimeoutError,
    LLMRetryExhaustedError,
    CircuitBreakerOpenError,
)

try:
    response = await llm.chat_completion(messages)
except LLMTimeoutError as e:
    print(f"Timed out after {e.timeout_seconds}s")
except CircuitBreakerOpenError as e:
    print(f"Service unavailable, retry in {e.retry_after}s")
```

#### Usage Example

```python
from friday_llm import LiteLLMService, ResilienceConfig

llm = LiteLLMService(
    model_name="openrouter/anthropic/claude-3.5-sonnet",
    api_key="sk-or-...",
    api_base="https://openrouter.ai/api/v1",
    resilience=ResilienceConfig(max_retries=3, timeout_seconds=60),
)

# Streaming response
async for chunk in llm.chat_completion_stream(messages):
    print(chunk, end="")
```

---

### friday-agent

**Location:** `packages/friday-agent/`
**Purpose:** Agent orchestration, Re-Act loop, tool execution

#### Overview

friday-agent implements the core agent loop that ties together memory, LLM, and tools. The `CopilotAgent` class provides a complete implementation of the Reason-Act (Re-Act) pattern for agentic AI.

#### Key Components

**CopilotAgent**
The main agent implementation:
- Session management and initialization
- Context assembly and prompt formatting
- Tool call parsing and execution
- Multi-turn conversation handling
- Maximum iteration limits (prevents runaway agents)

**AgentProfile**
Agent personality and capability configuration:
- System prompt templates
- Tool access permissions
- Behavior constraints

**DefaultToolRegistry**
Tool discovery and management:
- Automatic tool schema generation
- Tool validation and execution
- LLM-compatible tool descriptions

#### Agent Loop

```
┌─────────────┐
│   Observe   │ ← User input + retrieved context
└──────┬──────┘
       │
┌──────▼──────┐
│    Think    │ ← LLM generates response or tool call
└──────┬──────┘
       │
   ┌───┴───┐
   │ Tool? │
   └───┬───┘
    Y/ \N
┌────▼────┐  ┌────▼────┐
│   Act   │  │ Respond │
│ Execute │  │  Done   │
│  Tool   │  └─────────┘
└────┬────┘
     │
┌────▼────┐
│ Reflect │ ← Store results, update memory
└────┬────┘
     │
     └──────► Loop (max 10 iterations)
```

#### Usage Example

```python
from friday_agent import CopilotAgent, AgentProfile

agent = CopilotAgent(
    llm=llm_service,
    memory=memory_controller,
    tool_registry=tool_registry,
    profile=AgentProfile(
        name="Friday",
        system_prompt="You are a helpful AI assistant...",
    ),
)

response = await agent.run(
    user_message="Find all Python files in the project",
    session_id="session_123",
)
```

---

### friday-tools

**Location:** `packages/friday-tools/`
**Purpose:** Tool definitions and implementations

#### Overview

friday-tools provides 50+ pre-built tools that agents can use to interact with the world. Tools are organized by category and follow a consistent interface pattern.

#### Tool Categories

| Category | Tools | Description |
|----------|-------|-------------|
| **Filesystem** | read_file, write_file, list_directory, search_files | File operations |
| **Shell** | execute_command, run_script | System command execution |
| **Web** | http_request, web_search, scrape_page | HTTP and web operations |
| **Git** | git_status, git_commit, git_diff, git_log | Version control |
| **Data** | parse_json, parse_yaml, csv_operations | Data transformation |
| **Text** | regex_search, text_replace, format_text | Text manipulation |
| **Code** | analyze_code, run_python, lint_code | Code operations |

#### Key Components

**BaseTool**
Abstract base class for all tools:
```python
class BaseTool(ABC):
    name: str
    description: str
    parameters_schema: dict  # JSON Schema

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        ...
```

**@tool Decorator**
Function-based tool definition:
```python
from friday_tools import tool

@tool
async def calculate_sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

**ToolManifest**
Generates LLM-compatible tool descriptions:
- OpenAI function calling format
- Anthropic tool use format
- Automatic schema generation from type hints

#### Usage Example

```python
from friday_tools import FileSystemTools, ShellTools

# Get tool instances
fs_tools = FileSystemTools()
shell_tools = ShellTools()

# Execute a tool
result = await fs_tools.read_file.execute(path="/etc/hostname")
print(result.output)
```

---

### friday-sandbox

**Location:** `packages/friday-sandbox/`
**Purpose:** Isolated code execution environment

#### Overview

friday-sandbox provides secure, isolated execution environments for running untrusted code generated by LLMs. It prevents agents from accidentally (or intentionally) damaging the host system.

#### Execution Modes

| Mode | Isolation | Performance | Use Case |
|------|-----------|-------------|----------|
| **Subprocess** | Process-level | Fast | Development, trusted code |
| **Docker** | Container-level | Medium | Production, untrusted code |
| **Remote** | Network-level | Slower | Multi-tenant, maximum isolation |

#### Key Components

**SubprocessSandbox**
Lightweight process isolation:
- Timeout enforcement
- Memory limits
- Output capture
- Working directory isolation

**DockerSandbox** (Planned)
Container-based isolation:
- Full filesystem isolation
- Network restrictions
- Resource quotas
- Ephemeral containers

#### Usage Example

```python
from friday_sandbox import SubprocessSandbox

sandbox = SubprocessSandbox(
    timeout_seconds=30,
    working_directory="/tmp/sandbox",
)

result = await sandbox.execute(
    code="print('Hello from sandbox!')",
    language="python",
)
print(result.stdout)  # "Hello from sandbox!"
```

---

### friday-transcript

**Location:** `packages/friday-transcript/`
**Purpose:** Conversation logging and export

#### Overview

friday-transcript provides persistent storage and export capabilities for conversation history. It enables training data generation, compliance auditing, and session replay.

#### Key Components

**SQLiteTranscriptStore**
Primary storage backend:
- Session metadata (model, system prompt, timestamps)
- Turn-by-turn message storage
- Token usage and latency tracking
- Full-text search capability

**Export Formats**

| Format | Exporter | Use Case |
|--------|----------|----------|
| JSONL | `JSONLExporter` | Data processing, backup |
| Markdown | `MarkdownExporter` | Human-readable documentation |
| Training | `JSONLExporter.export_training_data()` | Fine-tuning datasets |

**TranscriptSession**
Session metadata model:
- Session ID and user ID
- Model name and configuration
- Aggregate statistics (total tokens, latency)

#### Usage Example

```python
from friday_transcript import SQLiteTranscriptStore, MarkdownExporter

store = SQLiteTranscriptStore("./transcripts.db")

# Export session as markdown
exporter = MarkdownExporter(store, user_name="User", assistant_name="Friday")
await exporter.export_session("session_123", Path("./export.md"))
```

---

### friday-mcp

**Location:** `packages/friday-mcp/`
**Purpose:** Model Context Protocol client/server

#### Overview

friday-mcp implements the Model Context Protocol (MCP) for standardized communication between AI applications and context providers. This enables Friday agents to access external knowledge sources and tools through a common interface.

#### Key Components

**MCPClient**
Connect to MCP-compatible servers:
- Server discovery
- Tool invocation
- Resource retrieval

**MCPServer**
Expose Friday capabilities via MCP:
- Tool registration
- Resource serving
- SSE transport support

---

### friday-optimization (friday-opt)

**Location:** `packages/friday-optimization/`
**Purpose:** Performance optimization utilities

#### Overview

friday-opt provides optimization algorithms used throughout the framework, particularly for context assembly and token budget management.

#### Key Components

**Knapsack Solver**
Optimal context packing within token budgets:
- Dynamic programming implementation
- Priority-weighted selection
- Token counting integration

---

## New Features

### Development Log

This section documents features added during development sessions. Each entry includes the implementation date, a brief description, and details about the feature's impact on the Friday Framework.

---

#### Configurable Context Format Output

**Date:** 2026-01-09
**Category:** Context Engineering
**Files Modified:**
- `packages/friday-memory/src/friday_memory/context/layout.py`
- `packages/friday-memory/src/friday_memory/context/assembler.py`
- `tests/integration/memory/config.yaml`
- `tests/integration/memory/memory-chat.py`

**Description:** Added config-driven support for formatting supporting context (insights, summaries, entities, relationships) in multiple output formats when delivered to the LLM.

**Supported Formats:**
| Format | Token Overhead | Best For |
|--------|---------------|----------|
| `plain` | Baseline | Conversational use, token efficiency |
| `json` | +20-30% | Structured extraction, tool-use |
| `xml` | +30-40% | Claude models, structured parsing |
| `markdown` | +10-15% | Readable structure, tables |

**Impact:** This feature enables optimization of context delivery based on the target LLM. Claude models perform particularly well with XML-formatted context due to their training on Anthropic's XML-based tool format. JSON format is ideal for agents that need to extract structured information from context. The format is applied on every conversation turn, not just during initial priming, ensuring consistent context presentation throughout the session.

**Configuration:**
```yaml
memory:
  context_format: plain  # Options: plain, json, xml, markdown
```

---

#### Context Priming on Startup

**Date:** 2026-01-09
**Category:** Memory System
**Files Modified:**
- `tests/integration/memory/memory-chat.py`

**Description:** Fixed an issue where the `/context` command showed "No context assembled yet" immediately after startup, even though context priming had occurred.

**Impact:** The session's `last_payload` is now populated immediately after priming by calling `controller.recall()`. This ensures that debugging commands (`/context`, `/prompt`) work immediately after application startup without requiring the user to send a message first. This improves the developer experience when debugging context assembly and memory priming behavior.

---

#### Dynamic Context Loading

**Date:** 2026-01-09
**Category:** Context Engineering
**Files Modified:**
- `packages/friday-memory/src/friday_memory/controller/memory_controller.py`
- `packages/friday-memory/src/friday_memory/models/payload.py`
- `packages/friday-memory/src/friday_memory/context/layout.py`

**Description:** Changed from static context priming (loaded once at session start) to dynamic context loading where insights and summaries are fetched fresh on every `recall()` call.

**Impact:** This ensures that newly extracted insights and summaries from the MemoryExtractor are immediately available in subsequent conversation turns. Previously, context was only loaded during initial priming and wouldn't reflect knowledge gained during the current session. Now, the "Memory Loop" is truly dynamic—insights extracted from turn N are available in the context for turn N+1. Content is sorted by `created_at` descending (most recent first) to leverage the LLM's recency effect.

---

#### Context Layout Restructuring (Tail Injection)

**Date:** 2026-01-09
**Category:** Context Engineering
**Files Modified:**
- `packages/friday-memory/src/friday_memory/context/layout.py`
- `packages/friday-memory/tests/test_context/test_layout.py`

**Description:** Restructured the prompt layout to combat the "Lost in the Middle" phenomenon. Supporting context (insights, summaries, entities, session state) is now placed immediately before the user query in the final message, rather than in the system message.

**Layout Strategy:**
1. **System Message:** Base prompt (identity & guardrails only)
2. **Episodic Memory:** Conversation history (chronological)
3. **Final Message:** Supporting context + User query (tail injection)

**Impact:** Research shows that LLMs pay the most attention to the beginning (primacy effect) and end (recency effect) of their context window, with information in the middle receiving less attention. By placing critical supporting context immediately before the query, Friday leverages the recency effect to ensure insights, summaries, and entity information have maximum impact on the model's response. This is particularly important for long conversations where supporting context might otherwise get "lost" in the middle of a large context window.

---

#### Supporting Context Prompt Integration Fix

**Date:** 2026-01-09
**Category:** Context Engineering (Bug Fix)
**Files Modified:**
- `packages/friday-memory/src/friday_memory/context/assembler.py`
- `tests/integration/memory/memory-chat.py`

**Description:** Fixed a critical bug where supporting context (Prior Knowledge, Known Entities, Insights, Summaries) was being assembled correctly but then wiped out before being sent to the LLM.

**Root Cause:** The `process_turn()` method was replacing the entire final user message content with just the raw user input, effectively discarding the supporting context that `PromptArchitect.format_prompt()` had carefully assembled.

**Solution:** Updated `ContextAssembler.format_prompt()` to accept an optional `user_query` parameter, allowing callers to pass the current user input directly. This eliminates the need for post-hoc message replacement and ensures the supporting context is preserved.

**Impact:** This fix ensures that the LLM actually receives the rich supporting context that Friday's memory system assembles. Without this fix, the "Lost in the Middle" mitigation, entity relationships, insights, and summaries were never reaching the model—the entire context engineering pipeline was effectively bypassed. Now, `/prompt` correctly shows the full formatted message including supporting context immediately before the user query.

---

*This document is updated with each feature development session.*