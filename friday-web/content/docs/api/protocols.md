---
title: "Protocol Specifications"
description: "Full specification of all abstract protocols defined in friday-core."
weight: 2
---

Full specification of every abstract protocol in `friday-core/interfaces/`, including `LLMClient`, `ToolRegistry`, `VectorStoreAdapter`, `GraphStoreAdapter`, and `ContextEngineeringInterface`.

All protocols use `typing.Protocol` with `@runtime_checkable` so that implementations can be validated at runtime without inheriting from an abstract base class.

## ToolDefinition

**Location:** `packages/friday-core/src/friday_core/interfaces/tools.py`

The fundamental unit of agent capability. Every tool in Friday implements this interface.

```python
@runtime_checkable
class ToolDefinition(Protocol):
    """Abstract representation of a tool capability."""

    @property
    def name(self) -> str:
        """
        Unique tool identifier.
        Convention: lowercase_with_underscores
        Examples: "file_read", "web_search", "code_format"
        """
        ...

    @property
    def description(self) -> str:
        """
        Human-readable description for the LLM.
        Should explain:
        - What the tool does
        - When to use it
        - What it returns
        """
        ...

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """
        JSON Schema (Draft 7+) defining the tool's parameters.
        Must include type information, descriptions, and required fields.

        Example:
            {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding",
                        "default": "utf-8"
                    }
                },
                "required": ["path"]
            }
        """
        ...

    @property
    def category(self) -> str:
        """
        Tool category for grouping and filtering.
        Standard: filesystem, shell, web, git, code, data, text, utility
        Defaults to "uncategorized".
        """
        ...

    @property
    def tags(self) -> list[str]:
        """
        Optional tags for fine-grained filtering.
        Examples: ["read-only", "safe"], ["async", "requires-auth"]
        """
        ...

    async def execute(self, **kwargs: Any) -> str:
        """
        Execute the tool with the given arguments.
        Must be async. Returns a string that is fed back to the LLM.
        kwargs names and types must match parameters_schema.
        """
        ...

    def to_schema(self, format: str = "plain") -> dict[str, Any]:
        """
        Convert to LLM function-calling format.

        "plain" format:
            {"name": ..., "description": ..., "parameters": {...}}

        "openai" format:
            {"type": "function", "function": {"name": ..., ...}}
        """
        ...
```

**Implementation requirements:**
1. Tool names must be unique within a registry
2. Descriptions must be clear enough for LLM decision-making
3. Parameter schemas must be valid JSON Schema
4. `execute()` must be `async`
5. `execute()` must return a `str`

---

## LLMClient

**Location:** `packages/friday-core/src/friday_core/interfaces/llm.py`

Defines the contract for all LLM inference backends. Implementations normalize provider-specific formats into Friday's unified response structure.

```python
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
            messages: List of message dicts with 'role' and 'content'.
                     Supported roles: system, user, assistant, tool.

            tools: Optional list of tool schemas in OpenAI format:
                   [{"type": "function", "function": {"name": ..., ...}}]

            response_model: Optional Pydantic model for structured output.
                           If provided, response.content is parsed into this model.

            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).

        Returns:
            ChatCompletionResponse:
            - If the LLM returns text: response.content contains text
            - If the LLM calls tools: response.tool_calls is populated
            - Use response.has_tool_calls to check

        Raises:
            LLMError: If the call fails after retries
            ValidationError: If response doesn't match response_model
        """
        ...
```

**ChatCompletionResponse:**

```python
@dataclass
class ChatCompletionResponse:
    content: str | None
    tool_calls: list[ToolCall]
    usage: TokenUsage
    model: str
    reasoning_content: str | None = None  # For thinking models

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]

@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
```

**Implementing a custom LLM client:**

```python
from friday_core.interfaces import LLMClient, ChatCompletionResponse, TokenUsage

class MyCustomLLMClient:
    """Custom LLM client implementing the LLMClient protocol."""

    async def chat_completion(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        response_model=None,
        temperature: float = 0.7,
    ) -> ChatCompletionResponse:
        # Call your custom backend here
        raw = await my_backend.complete(messages, temperature=temperature)

        return ChatCompletionResponse(
            content=raw["text"],
            tool_calls=[],
            usage=TokenUsage(
                prompt_tokens=raw["input_tokens"],
                completion_tokens=raw["output_tokens"],
                total_tokens=raw["input_tokens"] + raw["output_tokens"],
            ),
            model="my-custom-model",
        )
```

---

## ToolRegistry

**Location:** `packages/friday-core/src/friday_core/interfaces/tools.py`

```python
class ToolRegistry(Protocol):
    """Registry for managing tool collections."""

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool. Raises ValueError if name already taken."""
        ...

    def get(self, name: str) -> ToolDefinition | None:
        """Return tool by name, or None if not found."""
        ...

    def list_tools(self) -> list[ToolDefinition]:
        """Return all registered tools."""
        ...

    def get_schemas(self, format: str = "plain") -> list[dict]:
        """Return LLM-ready schemas for all tools."""
        ...
```

---

## VectorStoreAdapter

**Location:** `packages/friday-core/src/friday_core/interfaces/storage.py`

```python
class VectorStoreAdapter(Protocol):
    """Abstract interface for vector similarity search."""

    async def add(
        self,
        text: str,
        metadata: dict[str, Any],
        collection: str = "default",
    ) -> str:
        """
        Add a document to the vector store.

        Args:
            text: Document text to embed and store
            metadata: Arbitrary metadata attached to the document
            collection: Collection name (default: "default")

        Returns:
            Document ID assigned by the store
        """
        ...

    async def search(
        self,
        query: str,
        n_results: int = 5,
        filters: dict[str, Any] | None = None,
        collection: str = "default",
    ) -> list[SearchResult]:
        """
        Semantic search for documents similar to the query.

        Args:
            query: Search query text
            n_results: Maximum documents to return
            filters: Metadata filters (AND logic)
            collection: Collection to search

        Returns:
            List of SearchResult ordered by descending similarity
        """
        ...

    async def delete(
        self,
        document_id: str,
        collection: str = "default",
    ) -> bool:
        """Delete a document by ID."""
        ...

    async def update_metadata(
        self,
        document_id: str,
        metadata: dict[str, Any],
        collection: str = "default",
    ) -> bool:
        """Update metadata for an existing document."""
        ...

    async def count(self, collection: str = "default") -> int:
        """Return total document count in the collection."""
        ...
```

**SearchResult:**

```python
@dataclass
class SearchResult:
    id: str
    content: str
    metadata: dict[str, Any]
    score: float              # Similarity score 0.0-1.0
    collection: str
```

**Implementing a custom vector store:**

```python
from friday_core.interfaces import VectorStoreAdapter, SearchResult

class MyVectorStore:
    """Custom vector store (e.g., wrapping Pinecone or Weaviate)."""

    async def add(self, text: str, metadata: dict, collection: str = "default") -> str:
        embedding = await self._embed(text)
        doc_id = await self._backend.upsert(embedding, metadata, namespace=collection)
        return doc_id

    async def search(self, query: str, n_results: int = 5, ...) -> list[SearchResult]:
        query_embedding = await self._embed(query)
        raw_results = await self._backend.query(query_embedding, top_k=n_results)
        return [
            SearchResult(
                id=r["id"],
                content=r["metadata"]["text"],
                metadata=r["metadata"],
                score=r["score"],
                collection=collection,
            )
            for r in raw_results["matches"]
        ]
```

---

## GraphStoreAdapter

**Location:** `packages/friday-core/src/friday_core/interfaces/storage.py`

```python
class GraphStoreAdapter(Protocol):
    """Abstract interface for knowledge graph storage."""

    async def add_entity(
        self,
        entity_id: str,
        entity_type: str,
        properties: dict[str, Any],
    ) -> bool:
        """Add or update an entity node in the graph."""
        ...

    async def add_relationship(
        self,
        subject_id: str,
        verb: str,
        object_id: str,
        properties: dict[str, Any] | None = None,
    ) -> bool:
        """Create a directed relationship between two entities."""
        ...

    async def get_entity(self, entity_id: str) -> dict | None:
        """Return entity node data, or None if not found."""
        ...

    async def get_neighbors(
        self,
        entity_id: str,
        depth: int = 1,
        relationship_types: list[str] | None = None,
    ) -> list[dict]:
        """Return entities within `depth` hops."""
        ...

    async def search_entities(
        self,
        query: str,
        entity_type: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search for entities by name or properties."""
        ...

    async def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and all its relationships."""
        ...

    async def get_all_entities(self) -> list[dict]:
        """Return all entities in the graph."""
        ...
```

---

## EpisodicStoreAdapter

**Location:** `packages/friday-core/src/friday_core/interfaces/storage.py`

```python
class EpisodicStoreAdapter(Protocol):
    """Abstract interface for conversation history storage."""

    async def add_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Store a conversation turn."""
        ...

    async def get_turns(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Return conversation turns for a session, newest first."""
        ...

    async def get_sessions(self, user_id: str) -> list[str]:
        """Return all session IDs for a user."""
        ...

    async def delete_session(self, session_id: str) -> bool:
        """Delete all turns for a session (used for right-to-erasure)."""
        ...
```

---

## ContextEngineeringInterface

**Location:** `packages/friday-core/src/friday_core/interfaces/context.py`

```python
class ContextEngineeringInterface(Protocol):
    """Abstract interface for context assembly."""

    async def assemble_context(
        self,
        query: str,
        state: SessionState,
        budget_limit: int | None = None,
    ) -> ContextPayload:
        """Assemble and rank context from all memory sources."""
        ...

    def calculate_budget_limit(
        self,
        system_prompt: str,
        tool_definitions: list[dict] | None = None,
    ) -> int:
        """Calculate available token budget after system overhead."""
        ...

    async def format_prompt(
        self,
        system_prompt: str,
        payload: ContextPayload,
    ) -> list[dict]:
        """Format context into LLM message list."""
        ...
```

---

## EmbeddingModel

**Location:** `packages/friday-core/src/friday_core/interfaces/llm.py`

```python
class EmbeddingModel(Protocol):
    """Abstract interface for text embedding models."""

    async def embed(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text."""
        ...

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a batch of texts."""
        ...

    @property
    def dimensions(self) -> int:
        """Return the dimensionality of the embedding vectors."""
        ...
```

---

## Protocol Design Principles

All Friday protocols follow these design principles established in ADR-001:

1. **Zero vendor lock-in** — Swap any component by implementing the protocol
2. **Testability** — Mock any protocol in unit tests without complex setup
3. **Clear contracts** — Protocols document exact requirements for implementors
4. **Async throughout** — All I/O methods are `async def`
5. **Pydantic at boundaries** — Input/output types use Pydantic for validation

## Related Pages

- [Package APIs](/docs/api/packages/) — Concrete class signatures for every package
- [Custom Protocol Implementations](/docs/advanced/custom-protocols/) — Step-by-step guides for implementing each protocol
- [Configuration Schema](/docs/api/config-schema/) — JSON Schema for config files
