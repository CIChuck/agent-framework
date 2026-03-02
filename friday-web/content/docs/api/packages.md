---
title: "Package APIs"
description: "Public API surface for each Friday package with type signatures."
weight: 1
---

Public API surface for each Friday package — `friday-core`, `friday-memory`, `friday-llm`, `friday-agent`, `friday-tools`, and the rest — with full type signatures.

## friday-agent

### CopilotAgent

**Location:** `packages/friday-agent/src/friday_agent/copilot.py`

Interactive agent using the Re-Act pattern for human-in-the-loop workflows. Executes a Think → Tool → Observe loop until the LLM produces a final response.

```python
class CopilotAgent(AgentBase):

    MAX_ITERATIONS: int = 10

    def __init__(
        self,
        profile: AgentProfile,
        memory: MemoryController,
        context_engine: ContextAssembler,
        llm: LLMClient,
        tool_registry: ToolRegistry,
        telemetry: TelemetryProvider | None = None,
    ): ...

    async def run(self, input_signal: str) -> str:
        """Execute the Re-Act loop for a user query."""

    async def initialize_session(self) -> None:
        """Initialize a new session with memory priming."""

    async def archive_turn(self) -> None:
        """Archive the current turn to memory."""
```

**Usage:**

```python
from friday_agent import CopilotAgent, AgentProfile
from friday_memory import MemoryController
from friday_llm import LiteLLMService
from friday_tools import DefaultToolRegistry

profile = AgentProfile(
    name="assistant",
    role="AI Assistant",
    goal="Help users with tasks",
    temperature=0.7,
)

agent = CopilotAgent(
    profile=profile,
    memory=memory,
    context_engine=context_assembler,
    llm=LiteLLMService(model="gpt-4o-mini"),
    tool_registry=DefaultToolRegistry(),
)

await agent.initialize_session()
response = await agent.run("What files are in the current directory?")
```

### AutonomousAgent

**Location:** `packages/friday-agent/src/friday_agent/autonomous.py`

Goal-oriented agent that decomposes complex tasks into subtasks and executes them autonomously.

```python
class AutonomousAgent(AgentBase):

    MAX_DEPTH: int = 5
    MAX_PARALLEL: int = 3

    async def run(self, goal: str) -> dict[str, Any]:
        """Execute autonomous task decomposition and execution."""

    async def decompose_task(self, task: str, depth: int = 0) -> list[dict]:
        """Break a task into subtasks using the LLM."""

    async def execute_task(self, task: dict) -> dict:
        """Execute a single task."""
```

### AgentProfile

**Location:** `packages/friday-agent/src/friday_agent/profile.py`

```python
@dataclass
class AgentProfile:
    name: str
    role: str
    goal: str
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    temperature: float = 0.7
    max_tokens: int = 4096
    tool_autonomy: str = "semi_auto"   # "manual" | "semi_auto" | "auto"
    enabled_tools: list[str] | None = None
    context_strategy: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)

    def render_system_prompt(self, **kwargs) -> str:
        """Render system prompt with variable substitution."""

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "AgentProfile":
        """Load profile from a YAML file."""

    def to_yaml(self, yaml_path: str) -> None:
        """Save profile to a YAML file."""
```

---

## friday-memory

### MemoryController

**Location:** `packages/friday-memory/src/friday_memory/controller.py`

Central coordinator for all memory operations across the three storage adapters.

```python
class MemoryController:

    def __init__(
        self,
        vector_adapter: VectorStoreAdapter,
        graph_adapter: GraphStoreAdapter,
        episodic_adapter: EpisodicStoreAdapter,
        embedding_model: EmbeddingModel | None = None,
    ): ...

    async def add_fact(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Store a fact in the vector memory."""

    async def recall_facts(
        self,
        query: str,
        n_results: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[dict]:
        """Retrieve relevant facts using semantic search."""

    async def add_entity(
        self,
        entity_id: str,
        entity_type: str,
        properties: dict[str, Any],
    ) -> bool:
        """Add an entity to the knowledge graph."""

    async def add_relationship(
        self,
        subject_id: str,
        verb: str,
        object_id: str,
        properties: dict[str, Any] | None = None,
    ) -> bool:
        """Add a relationship between two entities."""

    async def get_entity_context(
        self,
        entity_id: str,
        depth: int = 1,
    ) -> dict:
        """Get entity and its neighborhood up to `depth` hops."""

    async def add_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Add a conversation turn to episodic memory."""

    async def get_recent_turns(
        self,
        session_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """Get the most recent conversation turns."""
```

### ContextAssembler

**Location:** `packages/friday-memory/src/friday_memory/context_assembler.py`

Assembles context from all memory sources into an LLM-ready prompt, implementing token budgeting and knapsack optimization.

```python
class ContextAssembler:

    def __init__(
        self,
        memory: MemoryController,
        max_tokens: int = 8192,
        budget_strategy: str = "knapsack",   # "knapsack" | "greedy"
    ): ...

    async def assemble_context(
        self,
        query: str,
        state: SessionState,
        budget_limit: int | None = None,
    ) -> ContextPayload:
        """Assemble context from all memory sources."""

    def calculate_budget_limit(
        self,
        system_prompt: str,
        tool_definitions: list[dict] | None = None,
    ) -> int:
        """Calculate the available token budget dynamically."""

    async def format_prompt(
        self,
        system_prompt: str,
        payload: ContextPayload,
    ) -> list[dict]:
        """Format context payload into LLM message format."""
```

---

## friday-llm

### LiteLLMService

**Location:** `packages/friday-llm/src/friday_llm/client.py`

Provider-agnostic LLM client supporting OpenAI, Anthropic, Google, Ollama, OpenRouter, and 100+ additional providers through LiteLLM.

```python
class LiteLLMService:

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        base_url: str | None = None,
        resilience_config: ResilienceConfig | None = None,
    ): ...

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        response_model: type[BaseModel] | None = None,
        temperature: float = 0.7,
    ) -> ChatCompletionResponse:
        """Unified chat completion with optional tool calling."""

    async def embed_text(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text."""

    async def count_tokens(
        self,
        text: str,
        model: str | None = None,
    ) -> int:
        """Count the number of tokens in the text."""
```

### ResilienceConfig

```python
@dataclass
class ResilienceConfig:
    max_retries: int = 3
    initial_retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    timeout: float = 120.0
    enable_fallback: bool = True
    fallback_model: str = "gpt-4o-mini"
```

**Usage with resilience:**

```python
from friday_llm import LiteLLMService, ResilienceConfig

llm = LiteLLMService(
    model="gpt-4o",
    resilience_config=ResilienceConfig(
        max_retries=5,
        enable_fallback=True,
        fallback_model="gpt-4o-mini",
    )
)

response = await llm.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
    temperature=0.5,
)
print(response.content)
```

---

## friday-tools

### DefaultToolRegistry

**Location:** `packages/friday-tools/src/friday_tools/registry.py`

```python
class DefaultToolRegistry:

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool. Raises ValueError if already registered."""

    def get(self, name: str) -> ToolDefinition | None:
        """Get a tool by name."""

    def list_tools(self) -> list[ToolDefinition]:
        """List all registered tools."""

    def get_schemas(self, format: str = "plain") -> list[dict]:
        """Get schemas for all tools. format: 'plain' or 'openai'."""

    def get_tools_by_category(self, category: str) -> list[ToolDefinition]:
        """Get all tools in a specific category."""

    def tool(
        self,
        name: str | None = None,
        description: str | None = None,
        category: str = "uncategorized",
        tags: list[str] | None = None,
    ) -> Callable:
        """Decorator to register a function as a tool."""
```

### BaseTool

**Location:** `packages/friday-tools/src/friday_tools/definition.py`

```python
class BaseTool(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier (lowercase_with_underscores)."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description used by the LLM to decide when to call."""

    @property
    @abstractmethod
    def parameters_schema(self) -> dict[str, Any]:
        """JSON Schema Draft 7 definition of the tool's parameters."""

    @property
    def category(self) -> str:
        """Tool category for filtering. Defaults to 'uncategorized'."""
        return "uncategorized"

    @property
    def tags(self) -> list[str]:
        """Optional tags for fine-grained filtering."""
        return []

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool and return a string result."""

    def to_schema(self, format: str = "plain") -> dict[str, Any]:
        """Convert to LLM function-calling schema format."""
```

**Implementing a custom tool:**

```python
from friday_tools import BaseTool
from friday_tools import DefaultToolRegistry

class MyCustomTool(BaseTool):

    @property
    def name(self) -> str:
        return "my_custom_tool"

    @property
    def description(self) -> str:
        return (
            "Performs a custom transformation on the input string. "
            "Use this when you need to process text in a domain-specific way."
        )

    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Text to transform",
                }
            },
            "required": ["input"],
        }

    @property
    def category(self) -> str:
        return "utility"

    async def execute(self, input: str) -> str:
        return f"Processed: {input.upper()}"

registry = DefaultToolRegistry()
registry.register(MyCustomTool())
```

---

## Tool Catalog Summary

Friday ships with 50+ built-in tools organized into categories. See [Tool Catalog](/docs/api/config-schema/) for the complete reference table.

| Category | Count | Purpose | Security Level |
|----------|-------|---------|----------------|
| `filesystem` | 17 | File and directory operations | Medium — sandboxed |
| `shell` | 6 | Command execution, system info | High — restricted |
| `web` | 11 | HTTP requests, web scraping | Low — safe |
| `git` | 4 | Version control | Medium — safe |
| `code` | 5 | Code analysis and execution | High — sandboxed |
| `data` | 5 | Format parsing and conversion | Low — safe |
| `text` | 4 | Text manipulation | Low — safe |
| `encoding` | 6 | Base64, URL, hashing, UUIDs | Low — safe |
| `utility` | 5 | Math, dates, unit conversion | Low — safe |
| `memory` | 6 | Memory inspection, maintenance | Low — safe |
| `archive` | 3 | ZIP/TAR create, extract, list | Medium — safe |
| `integration` | 3 | Webhooks, SQL, email | Medium — varies |

## Related Pages

- [Protocol Specifications](/docs/api/protocols/) — Abstract interface definitions from `friday-core`
- [Configuration Schema](/docs/api/config-schema/) — JSON Schema for YAML config files
- [Custom Protocol Implementations](/docs/advanced/custom-protocols/) — Implement your own LLM client or store
