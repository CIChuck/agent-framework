---
title: "Custom Protocol Implementations"
description: "Implement the core interfaces to replace any storage or LLM component."
weight: 2
---

Any component in Friday can be swapped by implementing the corresponding protocol from `friday-core/interfaces/`, enabling full customization without forking the framework.

## LLMClient Protocol

The `LLMClient` protocol defines the contract that any LLM backend must satisfy. Implementing it lets you integrate Hugging Face, vLLM, proprietary models, or any HTTP-accessible inference endpoint.

```python
# From friday-core
from typing import Protocol, AsyncIterator
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class LLMResponse(BaseModel):
    content: str
    model: str
    finish_reason: str
    usage: dict[str, int]  # {"prompt_tokens": X, "completion_tokens": Y}

class LLMClient(Protocol):
    """Abstract protocol for LLM clients."""

    async def chat_completion(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate a chat completion."""
        ...

    async def streaming_completion(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Generate a streaming chat completion."""
        ...

    def get_model_info(self) -> dict:
        """Return model metadata (name, context_window, etc.)."""
        ...
```

### Example: Hugging Face Inference API Client

```python
import httpx
from friday_core import LLMClient, ChatMessage, LLMResponse

class HuggingFaceLLMClient(LLMClient):
    """LLM client for Hugging Face Inference API."""

    def __init__(
        self,
        model: str = "meta-llama/Llama-3-70b-chat-hf",
        api_key: str | None = None,
    ):
        self.model = model
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        self.base_url = "https://api-inference.huggingface.co/models"
        self.client = httpx.AsyncClient()

    async def chat_completion(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> LLMResponse:
        prompt = self._format_messages(messages)

        response = await self.client.post(
            f"{self.base_url}/{self.model}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "inputs": prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens or 2000,
                    "return_full_text": False,
                },
            },
        )
        response.raise_for_status()
        data = response.json()
        content = data[0]["generated_text"]

        return LLMResponse(
            content=content,
            model=self.model,
            finish_reason="stop",
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(content.split()),
            },
        )

    async def streaming_completion(self, messages, temperature=0.7, max_tokens=None, **kwargs):
        # Hugging Face Inference API doesn't support streaming; fall back
        response = await self.chat_completion(messages, temperature, max_tokens, **kwargs)
        yield response.content

    def get_model_info(self) -> dict:
        return {
            "name": self.model,
            "provider": "huggingface",
            "context_window": 8192,
        }

    def _format_messages(self, messages: list[ChatMessage]) -> str:
        """Format messages for Llama chat template."""
        formatted = ""
        for msg in messages:
            if msg.role == "system":
                formatted += f"<|system|>\n{msg.content}\n"
            elif msg.role == "user":
                formatted += f"<|user|>\n{msg.content}\n"
            elif msg.role == "assistant":
                formatted += f"<|assistant|>\n{msg.content}\n"
        formatted += "<|assistant|>\n"
        return formatted
```

**Usage:**

```python
from friday_agent import CopilotAgent

hf_client = HuggingFaceLLMClient(model="meta-llama/Llama-3-70b-chat-hf")

agent = CopilotAgent(
    llm=hf_client,  # Friday accepts any LLMClient implementation
    memory_controller=memory_controller,
)
```

### Example: vLLM Self-Hosted Client

[vLLM](https://github.com/vllm-project/vllm) is a high-performance inference server for self-hosting LLMs.

```python
class vLLMLLMClient(LLMClient):
    """LLM client for self-hosted vLLM server."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        model: str = "meta-llama/Llama-3-70b-chat-hf",
    ):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient()

    async def chat_completion(self, messages, temperature=0.7, max_tokens=None, **kwargs):
        # vLLM uses OpenAI-compatible API
        response = await self.client.post(
            f"{self.base_url}/v1/chat/completions",
            json={
                "model": self.model,
                "messages": [msg.model_dump() for msg in messages],
                "temperature": temperature,
                "max_tokens": max_tokens or 2000,
            },
        )
        response.raise_for_status()
        data = response.json()
        choice = data["choices"][0]

        return LLMResponse(
            content=choice["message"]["content"],
            model=self.model,
            finish_reason=choice["finish_reason"],
            usage=data["usage"],
        )

    async def streaming_completion(self, messages, temperature=0.7, max_tokens=None, **kwargs):
        async with self.client.stream(
            "POST",
            f"{self.base_url}/v1/chat/completions",
            json={
                "model": self.model,
                "messages": [msg.model_dump() for msg in messages],
                "temperature": temperature,
                "max_tokens": max_tokens or 2000,
                "stream": True,
            },
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data.get("choices"):
                        delta = data["choices"][0]["delta"]
                        if "content" in delta:
                            yield delta["content"]

    def get_model_info(self) -> dict:
        return {"name": self.model, "provider": "vllm", "context_window": 8192}
```

**Deployment:**

```bash
pip install vllm

python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-70b-chat-hf \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 4  # Use 4 GPUs
```

## VectorStoreAdapter Protocol

The `VectorStoreAdapter` protocol allows replacing ChromaDB with Pinecone, Weaviate, Qdrant, or any vector database.

```python
from typing import Protocol
from pydantic import BaseModel

class Document(BaseModel):
    id: str
    content: str
    embedding: list[float]
    metadata: dict

class VectorStoreAdapter(Protocol):
    """Abstract protocol for vector stores."""

    async def add_document(
        self,
        content: str,
        embedding: list[float],
        metadata: dict,
        collection: str = "default",
    ) -> str:
        """Add a document and return its ID."""
        ...

    async def similarity_search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        threshold: float = 0.7,
        collection: str = "default",
        filters: dict | None = None,
    ) -> list[Document]:
        """Search for similar documents."""
        ...

    async def delete_document(self, doc_id: str, collection: str = "default") -> bool:
        """Delete a document by ID."""
        ...

    async def get_document(self, doc_id: str, collection: str = "default") -> Document | None:
        """Retrieve a document by ID."""
        ...
```

### Example: Pinecone Adapter

```python
import pinecone
from friday_memory import VectorStoreAdapter, Document

class PineconeAdapter(VectorStoreAdapter):
    """Vector store adapter for Pinecone."""

    def __init__(self, api_key: str, environment: str, index_name: str):
        pinecone.init(api_key=api_key, environment=environment)
        self.index = pinecone.Index(index_name)

    async def add_document(self, content, embedding, metadata, collection="default") -> str:
        doc_id = str(uuid.uuid4())

        # Pinecone uses namespace for collections
        self.index.upsert(
            vectors=[{
                "id": doc_id,
                "values": embedding,
                "metadata": {**metadata, "content": content, "collection": collection},
            }],
            namespace=collection,
        )
        return doc_id

    async def similarity_search(self, query_embedding, limit=10, threshold=0.7, collection="default", filters=None):
        results = self.index.query(
            vector=query_embedding,
            top_k=limit,
            namespace=collection,
            filter=filters,
            include_metadata=True,
        )

        return [
            Document(
                id=match["id"],
                content=match["metadata"].pop("content"),
                embedding=query_embedding,
                metadata=match["metadata"],
            )
            for match in results["matches"]
            if match["score"] >= threshold
        ]
```

**Usage:**

```python
from friday_memory import MemoryController

pinecone_store = PineconeAdapter(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment="us-west1-gcp",
    index_name="friday-memories",
)

memory_controller = MemoryController(
    vector_store=pinecone_store,  # Friday accepts any VectorStoreAdapter
    graph_store=graph_store,
    episodic_store=episodic_store,
)
```

## GraphStoreAdapter Protocol

The graph store adapter allows replacing NetworkX with Neo4j, Amazon Neptune, or any property graph database.

### Example: Neo4j Graph Store

```python
from neo4j import AsyncGraphDatabase
from friday_memory import GraphStoreAdapter, Entity, Relationship

class Neo4jGraphAdapter(GraphStoreAdapter):
    """Graph store adapter for Neo4j."""

    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def add_entity(self, name, entity_type, description, metadata=None) -> Entity:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MERGE (e:Entity {name: $name})
                ON CREATE SET
                    e.type = $type,
                    e.description = $description,
                    e.hit_count = 1,
                    e.created_at = datetime(),
                    e.last_accessed = datetime()
                ON MATCH SET
                    e.hit_count = e.hit_count + 1,
                    e.last_accessed = datetime()
                RETURN e
                """,
                name=name,
                type=entity_type,
                description=description,
            )
            record = await result.single()
            node = record["e"]

            return Entity(
                name=node["name"],
                type=node["type"],
                description=node["description"],
                hit_count=node["hit_count"],
                metadata=metadata or {},
            )

    async def add_relationship(self, source, verb, target, context, confidence) -> Relationship:
        async with self.driver.session() as session:
            await session.run(
                """
                MATCH (s:Entity {name: $source})
                MATCH (t:Entity {name: $target})
                MERGE (s)-[r:RELATES {verb: $verb}]->(t)
                ON CREATE SET r.context = $context, r.confidence = $confidence, r.hit_count = 1
                ON MATCH SET r.hit_count = r.hit_count + 1
                """,
                source=source, target=target, verb=verb,
                context=context, confidence=confidence,
            )

            return Relationship(source=source, verb=verb, target=target,
                                context=context, confidence=confidence)
```

## Custom Tool Protocols

### Wrapping External APIs as Tools

Any HTTP API can be wrapped as a Friday tool by subclassing `BaseTool`.

```python
from friday_tools import BaseTool, ToolResult
from pydantic import BaseModel, Field
import httpx

class SendSlackMessageParams(BaseModel):
    channel: str = Field(..., description="Slack channel ID or name")
    message: str = Field(..., description="Message text to send")
    thread_ts: str | None = Field(None, description="Thread timestamp for replies")

class SlackTool(BaseTool):
    """Send messages to Slack channels."""

    name = "send_slack_message"
    description = "Send a message to a Slack channel or thread"
    category = "integrations"
    tags = ["slack", "messaging", "notifications"]
    parameters_schema = SendSlackMessageParams

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.client = httpx.AsyncClient()

    async def execute(self, **params) -> ToolResult:
        validated = self.parameters_schema(**params)

        try:
            response = await self.client.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {self.bot_token}"},
                json={
                    "channel": validated.channel,
                    "text": validated.message,
                    "thread_ts": validated.thread_ts,
                },
            )
            response.raise_for_status()
            data = response.json()

            if not data["ok"]:
                return ToolResult(
                    content=f"Slack API error: {data.get('error')}",
                    error=data.get("error"),
                )

            return ToolResult(
                content=f"Message sent to #{validated.channel}",
                data={"channel": validated.channel, "ts": data["ts"]},
            )

        except Exception as e:
            return ToolResult(
                content=f"Failed to send Slack message: {str(e)}",
                error=str(e),
            )

# Register the tool
from friday_agent import DefaultToolRegistry

slack_tool = SlackTool(bot_token=os.getenv("SLACK_BOT_TOKEN"))
DefaultToolRegistry.register(slack_tool)
```

### Streaming Tools

For long-running operations, implement `execute_streaming` to yield partial results with progress updates.

```python
class StreamingReportTool(BaseTool):
    """Generate a multi-section report with streaming progress."""

    name = "generate_report"
    description = "Generate a detailed report on a topic"
    category = "content"

    async def execute_streaming(self, **params) -> AsyncIterator[ToolResult]:
        """Yield partial results so agents can display progress in real-time."""
        validated = self.parameters_schema(**params)

        yield ToolResult(
            content=f"Starting report generation: {validated.topic}",
            metadata={"progress": 0, "total": validated.sections},
        )

        report_sections = []
        for i in range(validated.sections):
            section = await self._generate_section(validated.topic, i + 1)
            report_sections.append(section)

            yield ToolResult(
                content=f"Completed section {i+1}/{validated.sections}: {section.title}",
                data={"section": section.model_dump()},
                metadata={"progress": i + 1, "total": validated.sections},
            )

        full_report = "\n\n".join(s.content for s in report_sections)
        yield ToolResult(
            content=f"Report complete: {len(report_sections)} sections",
            data={"report": full_report},
            metadata={"progress": validated.sections, "total": validated.sections},
        )

    async def execute(self, **params) -> ToolResult:
        """Non-streaming fallback: collect all results and return the final one."""
        async for result in self.execute_streaming(**params):
            if result.metadata.get("progress") == result.metadata.get("total"):
                return result
```

## Related Pages

- [Hybrid Cloud-Local](/docs/advanced/hybrid/) — Route requests between cloud and local models
- [Performance Optimization](/docs/advanced/performance/) — Caching, parallelism, and indexing
- [Protocol Specifications](/docs/api/protocols/) — Full protocol interface definitions
