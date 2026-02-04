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
**Package**: `tests/lab` and package-level tests

| Task | File | Description |
|------|------|-------------|
| 7.1 | `packages/friday-llm/tests_llm/test_service.py` | LiteLLMService unit tests with mocked responses |
| 7.2 | `packages/friday-agent/tests_agent/test_copilot.py` | CopilotAgent tool loop tests |
| 7.3 | `packages/friday-agent/tests_agent/test_registry.py` | ToolRegistry schema generation tests |
| 7.4 | `tests/lab/experiments/exp_06_agent_loop.py` | End-to-end agent integration test |
| 7.5 | `apps/friday-cli/tests/test_container.py` | DI wiring verification |

**Testing Strategy Details:** See Part 6 below.

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
| ToolCall Model Strategy | Dual models - core for LLM, memory for storage | Keep existing `friday_memory.models.session.ToolCall` for storage; create `friday_core.interfaces.llm.ToolCall` for LLM responses |
| Tool Registration Pattern | Decorator-based with partial binding | Use `@tool` decorator for schema generation; use `functools.partial` for dependency injection |
| friday-optimization | Deferred to Batch 4 | DSPy integration not required for core agent functionality |

---

## Part 4a: Implementation Clarifications

### 4a.1 ToolCall Model Strategy

**Problem:** A `ToolCall` model already exists in `friday_memory/models/session.py:14-22`.

**Solution:** Keep both models with distinct purposes:

| Location | Purpose | Used By |
|----------|---------|---------|
| `friday_core.interfaces.llm.ToolCall` | LLM response parsing | LiteLLMService, AgentBase |
| `friday_memory.models.session.ToolCall` | Episodic storage | InteractionTurn, MemoryController |

The agent layer will convert between them when archiving turns:
```python
# In AgentBase._archive_turn()
from friday_memory.models.session import ToolCall as StorageToolCall

storage_calls = [
    StorageToolCall(id=tc.id, name=tc.name, arguments=tc.arguments)
    for tc in response.tool_calls
]
```

### 4a.2 LiteLLM Response Mapping

**Problem:** litellm returns OpenAI-format responses that must be mapped to our `ChatCompletionResponse`.

**Solution:** Explicit mapping in `LiteLLMService.chat_completion()`:

```python
# packages/friday-llm/src/friday_llm/service.py

import json
from friday_core.interfaces.llm import ChatCompletionResponse, ToolCall

async def chat_completion(self, messages, tools=None, **kwargs) -> ChatCompletionResponse:
    response = await litellm.acompletion(
        model=self.model,
        messages=messages,
        tools=tools,
        api_key=self.api_key,
        api_base=self.api_base,
    )

    # Extract message from response
    message = response.choices[0].message

    # Parse tool calls if present
    tool_calls = []
    if message.tool_calls:
        for tc in message.tool_calls:
            tool_calls.append(ToolCall(
                id=tc.id,
                name=tc.function.name,
                arguments=json.loads(tc.function.arguments),  # Parse JSON string
            ))

    return ChatCompletionResponse(
        content=message.content,
        tool_calls=tool_calls,
        model=response.model,
        usage={
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        },
    )
```

### 4a.3 Tool Registration Pattern

**Problem:** How does `ToolRegistry.get_schema()` generate OpenAI-compatible JSON schemas?

**Solution:** Decorator-based registration with auto-schema generation:

```python
# packages/friday-agent/src/friday_agent/tools/registry.py

import inspect
import json
from functools import partial
from typing import Any, Callable, get_type_hints

def tool(
    name: str | None = None,
    description: str | None = None,
):
    """Decorator to register a function as a tool."""
    def decorator(func: Callable) -> Callable:
        func._tool_name = name or func.__name__
        func._tool_description = description or func.__doc__ or ""
        func._is_tool = True
        return func
    return decorator


class DefaultToolRegistry:
    """Default implementation of ToolRegistry protocol."""

    def __init__(self):
        self._tools: dict[str, Callable] = {}
        self._schemas: dict[str, dict] = {}
        self._bound_args: dict[str, dict] = {}  # Pre-bound arguments

    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: dict[str, Any],
        bound_args: dict[str, Any] | None = None,
    ) -> None:
        """Register a tool with explicit schema."""
        self._tools[name] = func
        self._schemas[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            }
        }
        if bound_args:
            self._bound_args[name] = bound_args

    def register_decorated(self, func: Callable, **bound_args) -> None:
        """Register a @tool decorated function with auto-generated schema."""
        if not getattr(func, "_is_tool", False):
            raise ValueError(f"{func.__name__} is not decorated with @tool")

        name = func._tool_name
        schema = self._generate_schema(func)
        self._tools[name] = func
        self._schemas[name] = schema
        if bound_args:
            self._bound_args[name] = bound_args

    def _generate_schema(self, func: Callable) -> dict:
        """Generate OpenAI-compatible schema from function signature."""
        hints = get_type_hints(func)
        sig = inspect.signature(func)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            # Skip injected dependencies (not exposed to LLM)
            if param_name in ("state", "memory_controller", "self"):
                continue

            param_type = hints.get(param_name, str)
            properties[param_name] = self._type_to_json_schema(param_type)

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": func._tool_name,
                "description": func._tool_description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
        }

    def _type_to_json_schema(self, python_type) -> dict:
        """Convert Python type hint to JSON Schema type."""
        type_map = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            list: {"type": "array"},
            dict: {"type": "object"},
        }
        return type_map.get(python_type, {"type": "string"})

    def get_tool(self, name: str) -> Callable:
        """Get executable with pre-bound dependencies."""
        func = self._tools[name]
        bound = self._bound_args.get(name, {})
        if bound:
            return partial(func, **bound)
        return func

    def get_schema(self, name: str) -> dict:
        return self._schemas[name]

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())
```

### 4a.4 Built-in Tools Dependency Injection

**Problem:** Tools like `scratchpad_write(state, key, value)` need `state` injected, but LLMs only pass `key` and `value`.

**Solution:** Pre-bind dependencies when registering tools:

```python
# In CopilotAgent.__init__ or container.py

registry = DefaultToolRegistry()

# Register with bound dependencies
registry.register_decorated(
    scratchpad_write,
    state=session_state,  # Pre-bound
)
registry.register_decorated(
    recall_memory,
    memory_controller=memory_controller,  # Pre-bound
)

# When LLM calls scratchpad_write(key="foo", value="bar"):
# Registry returns partial(scratchpad_write, state=session_state)
# Which gets called as: scratchpad_write(state=session_state, key="foo", value="bar")
```

### 4a.5 Workspace pyproject.toml Updates

**File:** Root `pyproject.toml`

Add to workspace members:
```toml
[tool.uv.workspace]
members = [
    "packages/friday-core",
    "packages/friday-memory",
    "packages/friday-llm",         # NEW
    "packages/friday-agent",       # NEW
    "packages/friday-optimization",
    "apps/friday-cli",
]
```

**File:** `packages/friday-llm/pyproject.toml`
```toml
[project]
name = "friday-llm"
version = "0.1.0"
dependencies = [
    "friday-core",
    "litellm>=1.0.0",
    "tenacity>=8.0.0",
]

[tool.uv.sources]
friday-core = { workspace = true }
```

**File:** `packages/friday-agent/pyproject.toml`
```toml
[project]
name = "friday-agent"
version = "0.1.0"
dependencies = [
    "friday-core",
    # NOTE: Does NOT depend on friday-llm or friday-memory
    # Those are injected at runtime via protocols
]

[tool.uv.sources]
friday-core = { workspace = true }
```

### 4a.6 friday-optimization Scope

**Decision:** Defer DSPy integration to Batch 4.

**Rationale:**
- Batch 3 focus is agent execution, not prompt optimization
- DSPy requires working agents to optimize against
- Current `packages/friday-optimization` contains minimal stubs
- Can be added after core agent loop is stable

**Action:** No changes to friday-optimization in Batch 3.

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

from friday_core.interfaces.llm import LLMClient
from friday_core.interfaces.tools import ToolRegistry

from .profile import AgentProfile


class AgentBase(ABC):
    """Abstract base class for all agents."""

    def __init__(
        self,
        profile: AgentProfile,
        memory: Any,  # MemoryController - use Any to avoid circular import
        context_engine: Any,  # ContextEngineeringInterface
        llm: LLMClient,
        tool_registry: ToolRegistry,
        telemetry: Any | None = None,  # TelemetryInterface
    ):
        self.profile = profile
        self.memory = memory
        self.context_engine = context_engine
        self.llm = llm
        self.tool_registry = tool_registry
        self.telemetry = telemetry
        self.session_id = str(uuid4())
        self._session_state = None  # Lazy initialized

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

    async def _get_session_state(self):
        """Lazy-load or retrieve current session state."""
        if self._session_state is None:
            self._session_state = await self.context_engine.initialize_session(
                self.session_id, user_id="default"
            )
        return self._session_state

    def _get_scratchpad_context(self) -> str:
        """Format scratchpad for system prompt injection."""
        if self._session_state is None:
            return ""
        items = []
        for key, value in self._session_state.scoped_vars.items():
            if key.startswith("session:"):
                items.append(f"- {key.replace('session:', '')}: {value}")
        return "\n**Agent Scratchpad:**\n" + "\n".join(items) if items else ""

    async def _archive_turn(
        self,
        user_message: str | None,
        assistant_message: str | None,
        tool_calls: list | None = None,
        tool_results: list | None = None,
    ) -> None:
        """Save interaction to episodic store and trigger extraction."""
        from friday_memory.models.session import InteractionTurn, ToolCall as StorageToolCall

        # Convert LLM tool calls to storage format
        storage_calls = []
        if tool_calls:
            for tc in tool_calls:
                storage_calls.append(StorageToolCall(
                    id=tc.id, name=tc.name, arguments=tc.arguments
                ))

        turn = InteractionTurn(
            id=str(uuid4()),
            session_id=self.session_id,
            user_message=user_message,
            assistant_message=assistant_message,
            tool_calls=storage_calls,
            tool_results=tool_results or [],
        )
        await self.memory.add_turn(self.session_id, turn)

        # Async extraction (non-blocking)
        asyncio.create_task(
            self.context_engine.extract_context(turn, async_execution=True)
        )
```

### 5.5 CopilotAgent Full Implementation

```python
# packages/friday-agent/src/friday_agent/copilot.py

from typing import Any
from friday_core.interfaces.llm import ChatCompletionResponse
from .base import AgentBase


class CopilotAgent(AgentBase):
    """
    Human-in-the-loop agent with Multi-Step Tool Execution.

    Implements the Re-Act pattern:
    Input -> [Think -> Tool -> Observe]* -> Response
    """

    async def run(self, user_input: str) -> str:
        """
        Execute a single conversation turn with tool loop.

        Args:
            user_input: The user's message

        Returns:
            The agent's final text response
        """
        span_id = None
        if self.telemetry:
            span_id = self.telemetry.start_span(f"copilot_turn_{self.profile.name}")

        try:
            # 1. Initialize session state
            state = await self._get_session_state()
            state.increment_turn()

            # 2. Assemble context from memory
            budget = 4096  # TODO: Calculate based on model context window
            payload = await self.context_engine.assemble_context(
                query=user_input,
                state=state,
                budget_limit=budget,
            )

            # 3. Build initial messages
            system_prompt = self.profile.render_system_prompt()
            scratchpad = self._get_scratchpad_context()
            if scratchpad:
                system_prompt += f"\n\n{scratchpad}"

            messages = await self.context_engine.format_prompt(
                system_prompt=system_prompt,
                payload=payload,
            )
            messages.append({"role": "user", "content": user_input})

            # 4. Get tool schemas
            tool_schemas = self._get_tool_schemas() if self.profile.tools else None

            # 5. Execute Re-Act loop
            all_tool_calls = []
            all_tool_results = []
            final_response = ""
            max_iterations = 10  # Safety limit

            for iteration in range(max_iterations):
                # A. Call LLM
                response: ChatCompletionResponse = await self.llm.chat_completion(
                    messages=messages,
                    tools=tool_schemas,
                    temperature=self.profile.temperature,
                )

                # B. Check for tool calls
                if response.has_tool_calls:
                    # Append assistant's tool request to history
                    messages.append({
                        "role": "assistant",
                        "content": response.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.name,
                                    "arguments": str(tc.arguments),
                                }
                            }
                            for tc in response.tool_calls
                        ]
                    })

                    # Execute each tool
                    for tool_call in response.tool_calls:
                        try:
                            result = await self._execute_tool_call(
                                tool_call.name,
                                tool_call.arguments,
                            )
                            error = None
                        except Exception as e:
                            result = f"Error: {str(e)}"
                            error = str(e)

                        # Track for archival
                        all_tool_calls.append(tool_call)
                        all_tool_results.append({
                            "tool_call_id": tool_call.id,
                            "output": result,
                            "error": error,
                        })

                        # Append tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        })

                    # Continue loop - let LLM process tool results
                    continue

                # C. No tool calls - we're done
                final_response = response.content or ""
                break

            # 6. Archive the complete turn
            await self._archive_turn(
                user_message=user_input,
                assistant_message=final_response,
                tool_calls=all_tool_calls,
                tool_results=all_tool_results,
            )

            return final_response

        finally:
            if span_id:
                self.telemetry.end_span(span_id)


class AutonomousAgent(AgentBase):
    """
    Goal-directed agent with plan decomposition.

    Placeholder for future expansion.
    """

    async def run(self, goal: str) -> str:
        """Execute goal-directed task. Not yet implemented."""
        raise NotImplementedError(
            "AutonomousAgent is a placeholder for future expansion. "
            "Use CopilotAgent for interactive tasks."
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

---

## Part 6: Testing Strategy

### 6.1 Test Fixtures & Mocks

**File:** `tests/conftest.py` (shared fixtures)

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from friday_core.interfaces.llm import ChatCompletionResponse, ToolCall


@pytest.fixture
def mock_llm_client():
    """Mock LLMClient that returns configurable responses."""
    client = AsyncMock()

    def configure_response(content: str = None, tool_calls: list = None):
        response = ChatCompletionResponse(
            content=content,
            tool_calls=tool_calls or [],
            model="mock-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )
        client.chat_completion.return_value = response

    client.configure_response = configure_response
    client.configure_response("Default response")
    return client


@pytest.fixture
def mock_tool_call():
    """Factory for creating mock tool calls."""
    def _create(name: str, arguments: dict, id: str = "call_123"):
        return ToolCall(id=id, name=name, arguments=arguments)
    return _create


@pytest.fixture
def mock_memory_controller():
    """Mock MemoryController for agent tests."""
    controller = AsyncMock()
    controller.add_turn = AsyncMock()
    controller.recall = AsyncMock(return_value=MagicMock(
        history=[],
        passages=[],
        entities=[],
        facts=[],
        recent_memories=[],
        debug_info={},
    ))
    return controller


@pytest.fixture
def mock_context_engine():
    """Mock ContextEngineeringInterface for agent tests."""
    from friday_memory.models import SessionState

    engine = AsyncMock()
    engine.initialize_session = AsyncMock(return_value=SessionState(
        session_id="test-session",
        user_id="test-user",
        turn_count=0,
        scoped_vars={},
    ))
    engine.assemble_context = AsyncMock(return_value=MagicMock(
        history=[],
        passages=[],
        entities=[],
        facts=[],
        recent_memories=[],
        debug_info={},
    ))
    engine.format_prompt = AsyncMock(return_value=[
        {"role": "system", "content": "You are a helpful assistant."}
    ])
    engine.extract_context = AsyncMock()
    return engine


@pytest.fixture
def sample_agent_profile():
    """Sample AgentProfile for testing."""
    from friday_agent.profile import AgentProfile
    return AgentProfile(
        name="TestAgent",
        role="Test Assistant",
        goal="Help with tests",
        system_prompt_template="You are {name}, a {role}. Your goal: {goal}",
        tools=["test_tool"],
        temperature=0.7,
    )
```

### 6.2 LLMClient Unit Tests

**File:** `packages/friday-llm/tests_llm/test_service.py`

```python
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from friday_llm.service import LiteLLMService


@pytest.fixture
def llm_service():
    return LiteLLMService(
        model_name="gpt-4",
        api_key="test-key",
        telemetry=None,
    )


class TestLiteLLMService:

    @pytest.mark.asyncio
    async def test_chat_completion_basic(self, llm_service):
        """Test basic text completion without tools."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello, world!"
        mock_response.choices[0].message.tool_calls = None
        mock_response.model = "gpt-4"
        mock_response.usage = MagicMock(
            prompt_tokens=10, completion_tokens=5, total_tokens=15
        )

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock:
            mock.return_value = mock_response

            result = await llm_service.chat_completion(
                messages=[{"role": "user", "content": "Hi"}]
            )

            assert result.content == "Hello, world!"
            assert result.has_tool_calls is False

    @pytest.mark.asyncio
    async def test_chat_completion_with_tool_calls(self, llm_service):
        """Test completion that returns tool calls."""
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_abc123"
        mock_tool_call.function.name = "get_weather"
        mock_tool_call.function.arguments = '{"location": "NYC"}'

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_response.model = "gpt-4"
        mock_response.usage = MagicMock(
            prompt_tokens=20, completion_tokens=15, total_tokens=35
        )

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock:
            mock.return_value = mock_response

            result = await llm_service.chat_completion(
                messages=[{"role": "user", "content": "Weather in NYC?"}],
                tools=[{"type": "function", "function": {"name": "get_weather"}}],
            )

            assert result.has_tool_calls is True
            assert len(result.tool_calls) == 1
            assert result.tool_calls[0].name == "get_weather"
            assert result.tool_calls[0].arguments == {"location": "NYC"}
```

### 6.3 CopilotAgent Tool Loop Tests

**File:** `packages/friday-agent/tests_agent/test_copilot.py`

```python
import pytest
from unittest.mock import AsyncMock
from friday_agent.copilot import CopilotAgent
from friday_agent.tools.registry import DefaultToolRegistry, tool
from friday_core.interfaces.llm import ChatCompletionResponse, ToolCall


@tool(name="calculator", description="Performs basic math")
async def mock_calculator(operation: str, a: int, b: int) -> str:
    if operation == "add":
        return str(a + b)
    return "Unknown operation"


class TestCopilotAgent:

    @pytest.fixture
    def agent(self, sample_agent_profile, mock_llm_client,
              mock_memory_controller, mock_context_engine):
        registry = DefaultToolRegistry()
        registry.register_decorated(mock_calculator)

        sample_agent_profile.tools = ["calculator"]

        return CopilotAgent(
            profile=sample_agent_profile,
            memory=mock_memory_controller,
            context_engine=mock_context_engine,
            llm=mock_llm_client,
            tool_registry=registry,
        )

    @pytest.mark.asyncio
    async def test_simple_response_no_tools(self, agent, mock_llm_client):
        """Test agent returns response when no tools are called."""
        mock_llm_client.configure_response("The answer is 42.")

        result = await agent.run("What is the meaning of life?")

        assert result == "The answer is 42."
        assert mock_llm_client.chat_completion.call_count == 1

    @pytest.mark.asyncio
    async def test_single_tool_call(self, agent, mock_llm_client, mock_tool_call):
        """Test agent executes single tool and returns final response."""
        # First call: LLM requests tool
        tool_call = mock_tool_call("calculator", {"operation": "add", "a": 2, "b": 3})
        first_response = ChatCompletionResponse(
            content=None,
            tool_calls=[tool_call],
        )
        # Second call: LLM provides final answer
        second_response = ChatCompletionResponse(
            content="2 + 3 = 5",
            tool_calls=[],
        )
        mock_llm_client.chat_completion.side_effect = [first_response, second_response]

        result = await agent.run("What is 2 + 3?")

        assert result == "2 + 3 = 5"
        assert mock_llm_client.chat_completion.call_count == 2

    @pytest.mark.asyncio
    async def test_multi_step_tool_loop(self, agent, mock_llm_client, mock_tool_call):
        """Test agent handles multiple sequential tool calls."""
        # Call 1: First tool
        # Call 2: Second tool
        # Call 3: Final response
        responses = [
            ChatCompletionResponse(
                tool_calls=[mock_tool_call("calculator", {"operation": "add", "a": 1, "b": 2}, "call_1")]
            ),
            ChatCompletionResponse(
                tool_calls=[mock_tool_call("calculator", {"operation": "add", "a": 3, "b": 4}, "call_2")]
            ),
            ChatCompletionResponse(content="First: 3, Second: 7"),
        ]
        mock_llm_client.chat_completion.side_effect = responses

        result = await agent.run("Calculate 1+2 and 3+4")

        assert result == "First: 3, Second: 7"
        assert mock_llm_client.chat_completion.call_count == 3

    @pytest.mark.asyncio
    async def test_tool_error_handling(self, agent, mock_llm_client, mock_tool_call):
        """Test agent handles tool execution errors gracefully."""
        # Register a tool that will fail
        @tool(name="failing_tool", description="Always fails")
        async def failing_tool() -> str:
            raise ValueError("Intentional failure")

        agent.tool_registry.register_decorated(failing_tool)
        agent.profile.tools.append("failing_tool")

        # LLM calls failing tool, then provides response
        responses = [
            ChatCompletionResponse(
                tool_calls=[mock_tool_call("failing_tool", {}, "call_fail")]
            ),
            ChatCompletionResponse(content="I encountered an error with that tool."),
        ]
        mock_llm_client.chat_completion.side_effect = responses

        result = await agent.run("Use the failing tool")

        # Should still get a response despite tool error
        assert "error" in result.lower() or "encountered" in result.lower()
```

### 6.4 ToolRegistry Tests

**File:** `packages/friday-agent/tests_agent/test_registry.py`

```python
import pytest
from friday_agent.tools.registry import DefaultToolRegistry, tool


class TestToolRegistry:

    def test_register_with_explicit_schema(self):
        registry = DefaultToolRegistry()
        registry.register(
            name="test_tool",
            func=lambda x: x,
            description="A test tool",
            parameters={
                "type": "object",
                "properties": {"x": {"type": "string"}},
                "required": ["x"],
            }
        )

        schema = registry.get_schema("test_tool")
        assert schema["function"]["name"] == "test_tool"
        assert "x" in schema["function"]["parameters"]["properties"]

    def test_register_decorated_auto_schema(self):
        @tool(name="greet", description="Greets a person")
        def greet(name: str, formal: bool = False) -> str:
            return f"Hello, {name}!"

        registry = DefaultToolRegistry()
        registry.register_decorated(greet)

        schema = registry.get_schema("greet")
        assert schema["function"]["name"] == "greet"
        assert "name" in schema["function"]["parameters"]["properties"]
        assert "name" in schema["function"]["parameters"]["required"]
        assert "formal" not in schema["function"]["parameters"]["required"]

    def test_bound_args_injection(self):
        @tool(name="with_state", description="Uses state")
        def with_state(state, key: str) -> str:
            return state.get(key, "not found")

        registry = DefaultToolRegistry()
        mock_state = {"foo": "bar"}
        registry.register_decorated(with_state, state=mock_state)

        # Get the tool - should have state pre-bound
        func = registry.get_tool("with_state")
        result = func(key="foo")  # Only pass key, state is bound
        assert result == "bar"

    def test_list_tools(self):
        registry = DefaultToolRegistry()
        registry.register("tool_a", lambda: None, "A", {})
        registry.register("tool_b", lambda: None, "B", {})

        tools = registry.list_tools()
        assert "tool_a" in tools
        assert "tool_b" in tools
```

### 6.5 Integration Test Example

**File:** `tests/lab/experiments/exp_06_agent_loop.py`

```python
"""
Experiment 06: End-to-end Agent Loop Test

Tests the full agent lifecycle with real components (but mocked LLM).
Validates:
- DI container wiring
- Memory integration
- Context assembly
- Tool execution
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

# Skip if not running integration tests
pytestmark = pytest.mark.integration


async def test_full_agent_conversation():
    """Test a complete multi-turn conversation."""
    # This would use actual components with mocked LLM
    # See container.py for real wiring
    pass  # Placeholder for actual integration test


if __name__ == "__main__":
    asyncio.run(test_full_agent_conversation())
```

### 6.6 Test Categories

| Category | Scope | Mocking Strategy |
|----------|-------|------------------|
| Unit | Single class/function | Mock all dependencies |
| Integration | Package boundary | Mock external services (LLM, DB) |
| E2E | Full system | Mock only LLM API calls |

**Running Tests:**
```bash
# All tests
pytest

# Specific package
pytest packages/friday-agent/tests_agent/

# Only unit tests (fast)
pytest -m "not integration"

# Only integration tests
pytest -m integration
```
