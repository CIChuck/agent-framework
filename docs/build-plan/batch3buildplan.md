# Batch 3 Specification Review & Build Plan

## Executive Summary

Batch 3 defines the **Execution Layer** - transforming Friday from a passive knowledge system into an active agent. This review identifies **7 inconsistencies/gaps** and provides a **phased build plan** with 6 implementation phases.

---

## Part 1: Specification Review

### 1.1 Identified Inconsistencies

#### Issue #1: MemoryExtractor Already Uses litellm Directly (CRITICAL)
- **Location**: `packages/friday-memory/src/friday_memory/context/extractor.py:145`
- **Problem**: Batch 3 Section 7.3 says MemoryExtractor should use an **injected LLMClient** with a "Librarian" profile. However, the current implementation calls `litellm.acompletion()` directly.
- **Impact**: Violates dependency injection principle; makes testing difficult; couples memory layer to specific LLM provider.
- **Resolution**: Refactor to accept `LLMClient` via constructor, use it for extraction calls.

#### Issue #2: ContextAssembler Type Mismatch
- **Location**: Batch 3 Section 4.2 shows `context_engine: 'ContextAssembler'`
- **Problem**: Should be `context_engine: 'ContextEngineeringInterface'` per protocol-first design
- **Impact**: Minor - spec wording inconsistency, but implementation should use the interface

#### Issue #3: Tool Loop Return Type Ambiguity
- **Location**: Batch 3 Section 4.3 (CopilotAgent.run)
- **Problem**: The pseudocode checks `hasattr(response, 'tool_calls')` but `LLMClient.chat_completion()` returns `Union[str, BaseModel]`, not a complex response object with tool_calls attribute.
- **Impact**: The LLMClient interface needs refinement to support tool calling return types.
- **Resolution**: Add a `ChatCompletionResponse` model or update return type signature.

#### Issue #4: Scratchpad Tool Not Defined
- **Location**: Batch 3 Sections 7.2, 8.3 reference `scratchpad_write` tool
- **Problem**: No tool definition or ToolRegistry implementation is provided
- **Impact**: Agents cannot persist insights without a concrete scratchpad tool
- **Resolution**: Include a basic tool set (scratchpad_write, recall_memory, store_fact) as examples

#### Issue #5: OpenTelemetryProvider Lacks Implementation Detail
- **Location**: Batch 3 Section 1.1
- **Problem**: Only shows constructor stub, no method implementations or OTel SDK usage
- **Impact**: Builder lacks guidance on span attributes, semantic conventions, exporter setup
- **Resolution**: Provide sample implementation or reference OTel Python SDK patterns

#### Issue #6: SessionState Integration Not Detailed
- **Location**: Batch 3 Section 8.3 references SessionState.scoped_vars
- **Problem**: No explicit flow for how AgentBase reads/writes scoped_vars
- **Impact**: Builder must infer integration from Batch 2a
- **Resolution**: Add explicit method like `_get_scratchpad_context()` to AgentBase

#### Issue #7: AutonomousAgent is Explicitly a Placeholder
- **Location**: Batch 3 Section 4.4
- **Note**: This is acknowledged ("placeholder for future expansion") - not a true gap
- **Action**: Implement minimal stub that satisfies the ABC contract

---

### 1.2 Identified Gaps

| Gap | Description | Severity |
|-----|-------------|----------|
| Missing LLM interfaces file | `interfaces/llm.py` doesn't exist | High |
| Missing tools interface file | `interfaces/tools.py` doesn't exist | High |
| No ToolRegistry implementation | Only Protocol defined | Medium |
| No built-in tools | No example tools (scratchpad, recall) | Medium |
| No friday-llm package | Package scaffold missing | High |
| No friday-agent package | Package scaffold missing | High |
| No friday-cli container | DI wiring not implemented | Medium |
| ChromaVectorStore uses litellm directly | Needs EmbeddingModel injection | Low |

---

### 1.3 Cross-Batch Dependency Analysis

```
Batch 0 (Core)          ✅ Complete - TelemetryInterface, Config, Exceptions
    ↓
Batch 1 (Data)          ✅ Complete - All 3 adapters implemented
    ↓
Batch 2 (Memory)        ✅ Complete - MemoryController functional
    ↓
Batch 2a (Context)      ⚠️ Partial - Interfaces exist, Assembler needs LLM integration
    ↓
Batch 3 (Execution)     🔴 Not Started - This build plan
```

**Critical Path Dependencies:**
1. Batch 3 LLMClient → Required by MemoryExtractor (Batch 2a refactor)
2. Batch 3 EmbeddingModel → Could refactor ChromaVectorStore (optional)
3. Batch 3 AgentBase → Requires ContextAssembler completion
4. Batch 3 CopilotAgent → Requires ToolRegistry + sample tools

---

## Part 2: Build Plan

### Phase 1: Core Interfaces (Foundation)
**Package**: `packages/friday-core`

| Task | File | Description |
|------|------|-------------|
| 1.1 | `interfaces/llm.py` | Create LLMClient Protocol with tool calling support |
| 1.2 | `interfaces/llm.py` | Create EmbeddingModel Protocol |
| 1.3 | `interfaces/tools.py` | Create ToolRegistry Protocol |
| 1.4 | `interfaces/__init__.py` | Export new interfaces |
| 1.5 | `models/llm.py` | Add ChatCompletionResponse, ToolCall models |

**Deliverables:**
- `LLMClient` protocol with proper tool_calls return type
- `EmbeddingModel` protocol with embed_documents/embed_query
- `ToolRegistry` protocol with get_tool/get_schema/list_tools

---

### Phase 2: Inference Layer (friday-llm Package)
**Package**: `packages/friday-llm` (NEW)

| Task | File | Description |
|------|------|-------------|
| 2.1 | `pyproject.toml` | Package scaffold with deps: litellm, tenacity |
| 2.2 | `src/friday_llm/__init__.py` | Package init |
| 2.3 | `src/friday_llm/service.py` | LiteLLMService implementing LLMClient |
| 2.4 | `src/friday_llm/embeddings.py` | LiteLLMEmbeddingService implementing EmbeddingModel |
| 2.5 | `tests/test_service.py` | Unit tests for chat completion + tool parsing |
| 2.6 | `tests/test_embeddings.py` | Unit tests for embedding service |

**Key Implementation Details:**
- Use tenacity for retry logic (max_retries from constructor)
- Support api_base for local servers (Ollama/LM Studio)
- Parse tool_calls from litellm response
- Telemetry spans for all LLM calls

---

### Phase 3: Observability Enhancement
**Package**: `packages/friday-core`

| Task | File | Description |
|------|------|-------------|
| 3.1 | `telemetry.py` | Add OpenTelemetryProvider class |
| 3.2 | `pyproject.toml` | Add opentelemetry-api, opentelemetry-sdk deps |

**Note**: DebugTelemetryRecorder already exists for testing; OpenTelemetryProvider is for production.

---

### Phase 4: Agent Orchestration (friday-agent Package)
**Package**: `packages/friday-agent` (NEW)

| Task | File | Description |
|------|------|-------------|
| 4.1 | `pyproject.toml` | Package scaffold, depends on friday-core only |
| 4.2 | `src/friday_agent/__init__.py` | Package init |
| 4.3 | `src/friday_agent/profile.py` | AgentProfile dataclass |
| 4.4 | `src/friday_agent/base.py` | AgentBase ABC with tool resolution |
| 4.5 | `src/friday_agent/copilot.py` | CopilotAgent with Re-Act loop |
| 4.6 | `src/friday_agent/autonomous.py` | AutonomousAgent placeholder |
| 4.7 | `tests/test_copilot.py` | Tool loop unit tests |

**Key Implementation Details:**
- AgentBase accepts protocol interfaces only (not concrete implementations)
- _archive_turn fires async extraction task
- _get_tool_schemas resolves profile.tools via ToolRegistry
- CopilotAgent.run implements while True loop for tool execution

---

### Phase 5: Tool Infrastructure
**Package**: `packages/friday-agent`

| Task | File | Description |
|------|------|-------------|
| 5.1 | `src/friday_agent/tools/registry.py` | Default ToolRegistry implementation |
| 5.2 | `src/friday_agent/tools/builtins.py` | Built-in tools: scratchpad_write, recall_memory |
| 5.3 | `src/friday_agent/tools/__init__.py` | Tools package init |

---

### Phase 6: Integration & Wiring
**Package**: `apps/friday-cli` and refactors

| Task | File | Description |
|------|------|-------------|
| 6.1 | `src/friday_cli/container.py` | DI container wiring all components |
| 6.2 | `friday_memory/context/extractor.py` | Refactor to inject LLMClient instead of using litellm directly |
| 6.3 | `friday_memory/adapters/vector.py` | Refactor ChromaVectorStore to accept EmbeddingModel via constructor |

---

### Phase 7: Testing & Validation
**Package**: `tests/lab`

| Task | File | Description |
|------|------|-------------|
| 7.1 | `experiments/exp_06_agent_loop.py` | End-to-end agent test |
| 7.2 | Integration tests | CLI wiring verification |

---

## Part 3: Critical Files Reference

### Files to CREATE:
```
packages/friday-core/src/friday_core/interfaces/llm.py
packages/friday-core/src/friday_core/interfaces/tools.py
packages/friday-llm/                                    (entire package)
packages/friday-agent/                                  (entire package)
apps/friday-cli/src/friday_cli/container.py
```

### Files to MODIFY:
```
packages/friday-core/src/friday_core/interfaces/__init__.py   (export new interfaces)
packages/friday-core/src/friday_core/telemetry.py             (add OpenTelemetryProvider)
packages/friday-memory/src/friday_memory/context/extractor.py (inject LLMClient)
packages/friday-memory/src/friday_memory/adapters/vector.py   (inject EmbeddingModel)
uv.lock                                                       (workspace updates)
pyproject.toml                                                (workspace updates)
```

---

## Part 4: Design Decisions (Confirmed)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Tool Calling Return Type | Structured `ChatCompletionResponse` object | Single method with optional tool_calls attribute |
| AutonomousAgent Scope | Minimal stub | Satisfy ABC with pass/NotImplementedError |
| ChromaVectorStore Refactor | Yes, include in this batch | Use EmbeddingModel protocol for consistency |
| Built-in Tools | Core memory tools | scratchpad_write, scratchpad_read, recall_memory, store_fact |

---

## Estimated Complexity

| Phase | Effort | Risk |
|-------|--------|------|
| Phase 1: Core Interfaces | Low | Low |
| Phase 2: friday-llm | Medium | Medium (API parsing) |
| Phase 3: Observability | Low | Low |
| Phase 4: friday-agent | High | High (tool loop complexity) |
| Phase 5: Tool Infrastructure | Medium | Low |
| Phase 6: Integration | Medium | Medium (DI wiring) |
| Phase 7: Testing | Medium | Low |

**Total New Code**: ~2000-2500 lines
**Refactored Code**: ~300 lines (MemoryExtractor + ChromaVectorStore)

---

## Part 5: Interface Code Examples

### 5.1 LLMClient Protocol

```python
# packages/friday-core/src/friday_core/interfaces/llm.py

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol
from pydantic import BaseModel


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ChatCompletionResponse:
    """Structured response from chat completion."""
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class LLMClient(Protocol):
    """Abstract interface for LLM inference."""

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        response_model: type[BaseModel] | None = None,
        temperature: float = 0.7,
    ) -> ChatCompletionResponse:
        """
        Unified chat completion with optional tool calling.

        Args:
            messages: List of message dicts (role, content)
            tools: Optional list of tool JSON schemas
            response_model: Optional Pydantic model for structured output
            temperature: Sampling temperature

        Returns:
            ChatCompletionResponse with content and/or tool_calls
        """
        ...


class EmbeddingModel(Protocol):
    """Abstract interface for text embeddings."""

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents (for indexing)."""
        ...

    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query (for search)."""
        ...
```

### 5.2 ToolRegistry Protocol

```python
# packages/friday-core/src/friday_core/interfaces/tools.py

from typing import Any, Callable, Protocol


class ToolRegistry(Protocol):
    """Registry mapping tool names to executable functions."""

    def get_tool(self, name: str) -> Callable[..., Any]:
        """Returns the executable function for the tool."""
        ...

    def get_schema(self, name: str) -> dict[str, Any]:
        """Returns OpenAI-compatible JSON Schema for the tool."""
        ...

    def list_tools(self) -> list[str]:
        """Returns all registered tool names."""
        ...

    def register(
        self,
        name: str,
        func: Callable[..., Any],
        description: str,
        parameters: dict[str, Any]
    ) -> None:
        """Register a new tool dynamically."""
        ...
```

### 5.3 AgentProfile Dataclass

```python
# packages/friday-agent/src/friday_agent/profile.py

from dataclasses import dataclass, field


@dataclass
class AgentProfile:
    """
    Defines agent identity and capabilities.
    Serializable to YAML/JSON for config-driven agents.
    """
    name: str
    role: str
    goal: str
    system_prompt_template: str

    # Tool names (resolved via ToolRegistry)
    tools: list[str] = field(default_factory=list)

    # Context strategy (maps to ContextEngineeringInterface implementations)
    context_strategy: str = "standard"

    # LLM parameters
    temperature: float = 0.7
    max_tokens: int | None = None

    def render_system_prompt(self, **kwargs) -> str:
        """Render system prompt with variable substitution."""
        return self.system_prompt_template.format(
            name=self.name,
            role=self.role,
            goal=self.goal,
            **kwargs
        )
```

### 5.4 AgentBase Abstract Class

```python
# packages/friday-agent/src/friday_agent/base.py

from abc import ABC, abstractmethod
from typing import Any
from uuid import uuid4
import asyncio

from friday_core import TelemetryInterface
from friday_core.interfaces import ContextEngineeringInterface
from friday_core.interfaces.llm import LLMClient
from friday_core.interfaces.tools import ToolRegistry

from friday_memory.controller import MemoryController
from friday_memory.models import InteractionTurn

from .profile import AgentProfile


class AgentBase(ABC):
    """Abstract base class for all agents."""

    def __init__(
        self,
        profile: AgentProfile,
        memory: MemoryController,
        context_engine: ContextEngineeringInterface,
        llm: LLMClient,
        tool_registry: ToolRegistry,
        telemetry: TelemetryInterface | None = None,
    ):
        self.profile = profile
        self.memory = memory
        self.context_engine = context_engine
        self.llm = llm
        self.tool_registry = tool_registry
        self.telemetry = telemetry
        self.session_id = str(uuid4())

    @abstractmethod
    async def run(self, input_signal: Any) -> Any:
        """Execute the agent's main loop. Implemented by subclasses."""
        pass

    def _get_tool_schemas(self) -> list[dict[str, Any]]:
        """Resolve profile.tools to JSON schemas."""
        return [
            self.tool_registry.get_schema(name)
            for name in self.profile.tools
        ]

    async def _execute_tool_call(self, tool_name: str, args: dict) -> str:
        """Execute tool and return string result."""
        func = self.tool_registry.get_tool(tool_name)
        result = await func(**args) if asyncio.iscoroutinefunction(func) else func(**args)
        return str(result)

    async def _archive_turn(self, role: str, content: str) -> None:
        """Save interaction to episodic store and trigger extraction."""
        turn = InteractionTurn(
            user_message=content if role == "user" else None,
            assistant_response=content if role == "assistant" else None,
        )
        await self.memory.add_turn(self.session_id, turn)
        # Async extraction (non-blocking)
        asyncio.create_task(
            self.context_engine.extract_context(turn, async_execution=True)
        )
```

### 5.5 Built-in Tools

```python
# packages/friday-agent/src/friday_agent/tools/builtins.py

from typing import Any
from friday_memory.models import SessionState


async def scratchpad_write(state: SessionState, key: str, value: str) -> str:
    """Write a value to the agent's scratchpad (survives context pruning)."""
    state.set_var(f"session:{key}", value)
    return f"Saved '{key}' to scratchpad"


async def scratchpad_read(state: SessionState, key: str) -> str:
    """Read a value from the agent's scratchpad."""
    value = state.get_var(f"session:{key}")
    return value if value else f"No value found for key '{key}'"


async def recall_memory(memory_controller, query: str, limit: int = 5) -> str:
    """Search agent's memory for relevant information."""
    payload = await memory_controller.recall(query, vector_results=limit)
    results = []
    for passage in payload.passages[:limit]:
        results.append(f"- {passage.get('text', '')[:200]}...")
    return "\n".join(results) if results else "No relevant memories found"


async def store_fact(memory_controller, subject: str, predicate: str, object: str) -> str:
    """Explicitly store a fact in the knowledge graph."""
    from friday_memory.models import GraphNode, GraphEdge, ProvenanceMetadata
    import uuid

    provenance = ProvenanceMetadata(
        source_id="agent_explicit",
        source_type="tool",
        confidence=1.0,
        author_id="agent",
    )

    # Create nodes and edge
    subject_node = GraphNode(
        id=str(uuid.uuid4()),
        type="entity",
        label=subject,
        provenance=provenance,
    )
    object_node = GraphNode(
        id=str(uuid.uuid4()),
        type="entity",
        label=object,
        provenance=provenance,
    )
    edge = GraphEdge(
        source_id=subject_node.id,
        target_id=object_node.id,
        relation=predicate,
        provenance=provenance,
    )

    await memory_controller.store_fact(subject_node)
    await memory_controller.store_fact(object_node, edge)

    return f"Stored: {subject} {predicate} {object}"
```
