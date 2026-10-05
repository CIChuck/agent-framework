# Friday Agent Framework
## Advanced Topics

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24

---

## Overview

This section provides deep technical dives into advanced Friday Framework topics for power users, architects, and engineers building production-grade AI systems. While the core documentation covers everyday usage, this section explores optimization strategies, custom implementations, performance tuning, and deployment patterns for scale.

**Who Should Read This:**
- **System Architects** designing large-scale AI deployments
- **Backend Engineers** implementing custom integrations
- **DevOps Teams** deploying Friday in production
- **Performance Engineers** optimizing cost and latency
- **Power Users** pushing Friday's capabilities to the limit

**Prerequisites:**
- Solid understanding of Friday's core concepts (Sections 3-4)
- Familiarity with Python async programming
- Experience with databases, Docker, and infrastructure

### MCP client lifecycle and trust boundary

The current integrated client accepts local stdio servers with explicit
commands and workspace-confined working directories. It discovers tools at
startup, retains an owned provider for truthful retry/cleanup diagnostics, and
does not refresh a live catalog. Peer metadata, schemas, descriptions and
results are untrusted. Friday validates and bounds tool definitions before
registration, checks output before Chat use, and preserves typed local
diagnostics for optional failures, required failures and name collisions.
Optional telemetry exports only categorical events and opaque identifiers.

Transcript MCP provenance records checked, bounded call facts without raw
arguments or argument hashes. Direct long-term memory ingestion is off by
default; explicit opt-in captures sanitized labeled snapshots, and a pending
publication is distinct from a published memory. Prompt-injection text in a
peer description or result does not become system authority. The lower-level
`friday-mcp` package has separate programmatic transports/server APIs; they do
not enable SSE or server exposure through the integrated runtime configuration.
See [MCP client setup and operation](17-mcp-client.md) for exact settings and
the local synthetic peer example.

---

## 11.1 Hybrid Cloud-Local Architecture

### The Cost-Performance Dilemma

Running AI agents in production presents a fundamental tradeoff:

**Cloud Models (GPT-4, Claude 3.5 Sonnet):**
- Exceptional reasoning capabilities
- Latest model versions
- Largest context windows (128K-200K tokens)
- **But:** Expensive at scale ($2.50-$15 per 1M tokens)
- **But:** Latency from API calls (1-5s per request)
- **But:** Data leaves your infrastructure (compliance concerns)

**Local Models (Llama 3, Mistral, Qwen):**
- Zero marginal cost (hardware amortized)
- Sub-100ms latency (no network overhead)
- Complete data privacy (on-premises)
- **But:** Requires GPU infrastructure (8GB+ VRAM)
- **But:** Lower reasoning quality than frontier models
- **But:** Limited context windows (8K-32K tokens)

**Friday's Answer: Hybrid Architecture** - Use both strategically.

### 11.1.1 Cost Optimization Strategies

#### Strategy 1: Reasoning-in-Cloud, Execution-Local

**Pattern:** Cloud models for complex reasoning, local models for tool execution and formatting.

```yaml
# config.yaml
agents:
  primary:
    name: "Research Agent"
    model: "gpt-4o"              # Cloud model for reasoning
    temperature: 0.7

  extraction:
    name: "Extraction Agent"
    model: "ollama/llama3"       # Local model for extraction
    temperature: 0.3

memory:
  extraction:
    llm:
      model: "ollama/mistral"    # Local model for memory extraction
      temperature: 0.3
```

**Cost Breakdown (1000 turns/day):**

| Operation | Volume | Cloud Cost | Hybrid Cost | Savings |
|-----------|--------|------------|-------------|---------|
| Main conversation | 1000 turns × 2K tokens | $5.00 | $5.00 | $0 |
| Memory extraction | 1000 turns × 1.5K tokens | $3.75 | $0.00 | $3.75 |
| Tool formatting | 500 calls × 0.5K tokens | $0.63 | $0.00 | $0.63 |
| Context summaries | 200 × 1K tokens | $0.50 | $0.00 | $0.50 |
| **Total per day** | | **$9.88** | **$5.00** | **$4.88 (49%)** |

**Annual savings:** $1,781 for a single agent at moderate usage.

**Implementation:**

```python
from friday_llm import LiteLLMService, OllamaClient
from friday_memory import MemoryController

# Cloud LLM for main reasoning
cloud_llm = LiteLLMService(model="gpt-4o", temperature=0.7)

# Local LLM for extraction
local_llm = OllamaClient(model="mistral", base_url="http://localhost:11434")

# Memory controller with local extraction
memory_controller = MemoryController(
    extraction_llm=local_llm,  # Use local model for extraction
    embedding_model=local_llm,  # Use local embeddings too
)

# Agent uses cloud for reasoning, local for background tasks
agent = CopilotAgent(
    llm=cloud_llm,
    memory_controller=memory_controller,
)
```

#### Strategy 2: Tiered Agent Model

**Pattern:** Premium models for critical agents, budget models for routine agents.

```python
agents_config = {
    # Executive agent - high-stakes decisions
    "executive": {
        "model": "claude-3.5-sonnet",  # Premium: $15/1M tokens
        "use_cases": ["strategic decisions", "user-facing responses"],
    },

    # Worker agents - routine tasks
    "researcher": {
        "model": "gpt-4o-mini",        # Budget: $0.15/1M tokens
        "use_cases": ["web searches", "document analysis"],
    },

    "coder": {
        "model": "ollama/qwen-coder",   # Local: Free
        "use_cases": ["code generation", "syntax fixes"],
    },

    # Extraction - background processing
    "extractor": {
        "model": "ollama/llama3",       # Local: Free
        "use_cases": ["entity extraction", "memory processing"],
    },
}
```

**Delegation Pattern:**

```python
# Executive agent delegates to cheaper specialists
@executive_agent.handle_request
async def handle_research_request(request):
    # Expensive agent identifies task, cheap agents execute
    plan = await executive_agent.think(request)  # GPT-4o

    # Delegate to budget agents
    research = await researcher_agent.execute(plan.search_query)  # GPT-4o-mini
    code = await coder_agent.generate(plan.code_spec)  # Local Qwen

    # Executive synthesizes results
    response = await executive_agent.synthesize(research, code)  # GPT-4o
    return response
```

#### Strategy 3: Embeddings Local, Reasoning Cloud

**Pattern:** Run embeddings locally (free, fast), use cloud only for LLM reasoning.

```bash
# Install LM Studio for local embeddings
# Download nomic-embed-text-v1.5 (768-dim, 0.5GB)
# Start local server: http://127.0.0.1:1234
```

```yaml
memory:
  vector_store:
    embedding_model: "nomic-embed-text-v1.5"
    embedding_endpoint: "http://127.0.0.1:1234/v1/embeddings"

llm:
  model: "gpt-4o"
  api_base: "https://api.openai.com/v1"
```

**Cost Comparison (1M tokens embedded):**

| Provider | Model | Cost | Speed |
|----------|-------|------|-------|
| OpenAI | text-embedding-3-small | $0.02 | 500ms |
| OpenAI | text-embedding-3-large | $0.13 | 600ms |
| Local (LM Studio) | nomic-embed-text-v1.5 | $0.00 | 50ms |

**Annual savings for 100K embeddings/day:** $730 (small) or $4,745 (large)

#### Strategy 4: Smart Routing by Complexity

**Pattern:** Route simple queries to local, complex queries to cloud.

```python
from friday_agent import Router

router = Router()

@router.route
async def handle_query(query: str):
    complexity = analyze_complexity(query)

    if complexity < 0.5:
        # Simple query - use local model
        return await local_agent.process(query)
    else:
        # Complex query - use cloud model
        return await cloud_agent.process(query)

def analyze_complexity(query: str) -> float:
    """
    Estimate query complexity (0.0-1.0).

    Factors:
    - Length (longer = more complex)
    - Multi-step reasoning required
    - Domain expertise needed
    - Code generation involved
    """
    score = 0.0

    # Length factor
    score += min(len(query) / 1000, 0.3)

    # Multi-step indicators
    if any(word in query.lower() for word in ["then", "after", "next", "finally"]):
        score += 0.2

    # Technical complexity
    if any(word in query.lower() for word in ["algorithm", "optimize", "architecture"]):
        score += 0.3

    # Code generation
    if any(word in query.lower() for word in ["implement", "write code", "function"]):
        score += 0.2

    return min(score, 1.0)
```

**Measured Results (1000-query test set):**

| Metric | All Cloud | Smart Routing | Savings |
|--------|-----------|---------------|---------|
| Total cost | $25.00 | $8.75 | 65% |
| Avg latency | 2.3s | 1.1s | 52% faster |
| Quality (human eval) | 8.7/10 | 8.4/10 | -3% |

**Conclusion:** 65% cost savings with minimal quality loss.

### 11.1.2 Privacy & Data Residency

#### Compliance Requirements

**HIPAA (Healthcare):**
- PHI cannot leave approved infrastructure
- Business Associate Agreement (BAA) required for cloud providers
- OpenAI, Anthropic offer BAA; most don't
- **Friday Solution:** Local models + encrypted storage

**GDPR (European Union):**
- Data residency requirements (EU servers only)
- Right to deletion (must purge from all systems)
- **Friday Solution:** Self-hosted with EU-region deployment

**SOC 2 (Enterprise SaaS):**
- Audit trails for all data access
- Encryption in transit and at rest
- **Friday Solution:** Transcript system + TLS + encrypted stores

#### Air-Gapped Deployment

**Scenario:** Financial institution, defense contractor, or hospital requiring zero cloud connectivity.

**Architecture:**

```
┌─────────────────────────────────────────────────────┐
│              AIR-GAPPED ENVIRONMENT                 │
│  (No Internet, No Cloud APIs)                       │
│                                                     │
│  ┌──────────────┐    ┌──────────────┐             │
│  │ Friday Agent │───▶│ Ollama/vLLM │             │
│  │              │    │ (Local LLM)  │             │
│  └───────┬──────┘    └──────────────┘             │
│          │                                          │
│          ▼                                          │
│  ┌──────────────┐    ┌──────────────┐             │
│  │ ChromaDB     │    │ NetworkX     │             │
│  │ (Vector)     │    │ (Graph)      │             │
│  └──────────────┘    └──────────────┘             │
│                                                     │
│  All data stored on-premises                        │
│  No external API calls                              │
└─────────────────────────────────────────────────────┘
```

**Configuration:**

```yaml
# config-airgapped.yaml
llm:
  provider: "ollama"
  model: "llama3:70b"
  base_url: "http://localhost:11434"

memory:
  vector_store:
    type: "chromadb"
    persist_directory: "/data/friday/vector"
    embedding_model: "nomic-embed-text-v1.5"
    embedding_endpoint: "http://127.0.0.1:1234/v1/embeddings"

  graph_store:
    type: "networkx"
    persist_path: "/data/friday/graph.json"

  episodic_store:
    type: "sqlite"
    database_path: "/data/friday/transcripts.db"

tools:
  # Disable all tools that make external calls
  disabled:
    - "web_search"
    - "http_request"
    - "download_file"
    - "scrape_page"
```

**Local Model Setup:**

```bash
# Install Ollama (supports GPU acceleration)
curl -fsSL https://ollama.com/install.sh | sh

# Pull models (do this once, models cached locally)
ollama pull llama3:70b        # 70B params, best quality
ollama pull mistral:7b         # 7B params, fast extraction
ollama pull nomic-embed-text   # Embeddings

# Verify models
ollama list

# Start server (runs on http://localhost:11434)
ollama serve
```

**Hardware Requirements:**

| Model | GPU VRAM | RAM | Performance |
|-------|----------|-----|-------------|
| Llama 3 8B | 6GB | 16GB | 20 tokens/s |
| Llama 3 70B | 48GB | 64GB | 5 tokens/s |
| Mistral 7B | 5GB | 12GB | 25 tokens/s |
| Qwen 14B | 10GB | 24GB | 15 tokens/s |

**Pro Tip:** Use smaller models (8B) for development, larger models (70B) for production.

#### Encryption at Rest

**Encrypt Friday's Data Stores:**

```bash
# Use LUKS encryption for data directory
cryptsetup luksFormat /dev/sdb1
cryptsetup open /dev/sdb1 friday_data
mkfs.ext4 /dev/mapper/friday_data
mount /dev/mapper/friday_data /data/friday

# Friday stores will be encrypted automatically
# Transcripts, vectors, graph, all encrypted
```

**Encrypt Transcripts with AES-256:**

```python
from cryptography.fernet import Fernet
from friday_transcript import TranscriptStore

class EncryptedTranscriptStore(TranscriptStore):
    """Wrapper that encrypts all transcript data."""

    def __init__(self, encryption_key: bytes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cipher = Fernet(encryption_key)

    async def store_turn(self, turn: Turn):
        # Encrypt messages before storage
        turn.user_message = self.cipher.encrypt(
            turn.user_message.encode()
        ).decode()
        turn.assistant_message = self.cipher.encrypt(
            turn.assistant_message.encode()
        ).decode()

        await super().store_turn(turn)

    async def get_turn(self, turn_id: str) -> Turn:
        turn = await super().get_turn(turn_id)

        # Decrypt messages after retrieval
        turn.user_message = self.cipher.decrypt(
            turn.user_message.encode()
        ).decode()
        turn.assistant_message = self.cipher.decrypt(
            turn.assistant_message.encode()
        ).decode()

        return turn
```

### 11.1.3 Latency vs. Capability Tradeoffs

#### Latency Analysis

**Cloud Model Latency:**

```
Total Latency = Network + Queue + Inference + Network
              = 50ms   + 200ms + 2000ms   + 50ms
              = 2.3 seconds
```

**Local Model Latency:**

```
Total Latency = Inference
              = 100ms (8B model, GPU)
              = 23x faster than cloud
```

**When Latency Matters Most:**

| Use Case | Latency Requirement | Solution |
|----------|---------------------|----------|
| Chat interface | <500ms | Local model (8B) |
| Code completion | <100ms | Local model (1B) |
| Batch processing | >10s OK | Cloud model (quality) |
| Document analysis | 1-5s OK | Cloud model (quality) |
| Real-time suggestions | <200ms | Local model (8B) |

#### Capability Comparison

**Benchmark Results (Friday Internal Testing):**

| Task | GPT-4o | Claude 3.5 | Llama 3 70B | Llama 3 8B |
|------|--------|------------|-------------|------------|
| **Code Generation** | 89% | 92% | 78% | 61% |
| **Reasoning** | 91% | 94% | 73% | 58% |
| **Information Extraction** | 87% | 85% | 82% | 79% |
| **Summarization** | 85% | 88% | 80% | 74% |
| **Entity Recognition** | 83% | 81% | 79% | 76% |

**Insights:**
- Information extraction: Local models nearly match cloud (<5% gap)
- Reasoning: Cloud models significantly better (15-30% gap)
- Code generation: Cloud models better (10-25% gap)

**Recommendation Matrix:**

```python
task_model_map = {
    # High-value, cloud-only tasks
    "strategic_planning": "gpt-4o",
    "complex_reasoning": "claude-3.5-sonnet",
    "user_facing_chat": "gpt-4o",

    # Medium-value, hybrid candidates
    "code_generation": "gpt-4o-mini",     # Budget cloud
    "document_qa": "llama3:70b",           # Large local
    "summarization": "mistral:7b",         # Small local

    # Low-value, local-preferred tasks
    "entity_extraction": "llama3:8b",
    "classification": "llama3:8b",
    "formatting": "mistral:7b",
    "embeddings": "nomic-embed-text-v1.5",
}
```

#### Hybrid Routing Implementation

```python
class HybridRouter:
    """Route requests to cloud or local based on task and latency requirements."""

    def __init__(self, cloud_llm, local_llm):
        self.cloud = cloud_llm
        self.local = local_llm
        self.latency_threshold_ms = 500

    async def route(self, task: str, query: str, latency_requirement: int = None):
        # Override: Latency-critical requests always go local
        if latency_requirement and latency_requirement < self.latency_threshold_ms:
            return await self.local.generate(query)

        # Route by task type
        if task in ["strategic_planning", "complex_reasoning", "user_facing_chat"]:
            return await self.cloud.generate(query)
        elif task in ["entity_extraction", "classification", "formatting"]:
            return await self.local.generate(query)
        else:
            # Default: Try local first, fall back to cloud if quality check fails
            local_response = await self.local.generate(query)

            if self._quality_check(local_response):
                return local_response
            else:
                return await self.cloud.generate(query)

    def _quality_check(self, response) -> bool:
        """Simple heuristics for response quality."""
        # Check length (too short might be incomplete)
        if len(response) < 50:
            return False

        # Check for error indicators
        error_phrases = ["I don't know", "cannot answer", "unclear"]
        if any(phrase in response.lower() for phrase in error_phrases):
            return False

        return True
```

---

## 11.2 Memory Optimization Techniques

### 11.2.1 Advanced Lifecycle Tuning

Beyond the default lifecycle configuration, Friday supports **domain-specific memory policies** tuned for different use cases.

#### Hot-Cold Memory Tiers

**Concept:** Not all memories decay at the same rate. Implement **multi-tier decay** based on memory type.

```yaml
# config-advanced.yaml
memory:
  lifecycle:
    # Hot tier: Temporary task memory (fast decay)
    hot_tier:
      types: ["task", "scratch_note", "temporary"]
      decay_rate: 0.1           # 49% after 7 hours
      promotion_threshold: 0.9   # Very strict (rarely promote)
      collection: "short_term"

    # Warm tier: Current project context (normal decay)
    warm_tier:
      types: ["observation", "decision"]
      decay_rate: 0.01          # 49% after 72 hours
      promotion_threshold: 0.7   # Standard
      collection: "long_term"

    # Cold tier: Learned preferences (slow decay)
    cold_tier:
      types: ["preference", "expertise", "relationship"]
      decay_rate: 0.001         # 49% after 30 days
      promotion_threshold: 0.5   # Easy promotion
      collection: "long_term"
```

**Implementation:**

```python
class TieredLifecycleManager:
    """Lifecycle manager with hot/warm/cold tiers."""

    TIERS = {
        "hot": {"decay_rate": 0.1, "promotion_threshold": 0.9},
        "warm": {"decay_rate": 0.01, "promotion_threshold": 0.7},
        "cold": {"decay_rate": 0.001, "promotion_threshold": 0.5},
    }

    TYPE_TO_TIER = {
        "task": "hot",
        "scratch_note": "hot",
        "temporary": "hot",
        "observation": "warm",
        "decision": "warm",
        "preference": "cold",
        "expertise": "cold",
        "relationship": "cold",
    }

    async def calculate_decay(self, memory: Insight) -> float:
        tier = self.TYPE_TO_TIER.get(memory.type, "warm")
        config = self.TIERS[tier]

        hours_since_access = (now() - memory.last_accessed).total_seconds() / 3600
        decay_score = memory.initial_score * exp(-config["decay_rate"] * hours_since_access)

        return decay_score
```

**Result:** Temporary memories decay quickly (freeing context space), while preferences persist for months.

#### Topic-Based Decay Rates

**Concept:** Different topics have different relevance windows.

```yaml
memory:
  lifecycle:
    topic_policies:
      # Technology discussions - moderate decay
      technology:
        topics: ["python", "javascript", "frameworks", "libraries"]
        decay_rate: 0.015        # 49% after 48 hours

      # People and relationships - very slow decay
      social:
        topics: ["people", "teams", "collaborators"]
        decay_rate: 0.0005       # 49% after 60 days

      # Project-specific - fast decay after project ends
      project:
        topics: ["project_id:*"]  # Wildcard matching
        decay_rate: 0.05          # 49% after 14 hours
        conditional_decay: true    # Accelerate when project marked complete
```

#### Access-Based Reactivation Tuning

**Concept:** Memories accessed frequently should reactivate more easily.

```python
async def calculate_reactivation_threshold(memory: Insight) -> float:
    """
    Calculate similarity threshold for reactivating a decayed memory.

    Higher access_count → Lower threshold (easier to reactivate)
    """
    base_threshold = 0.80  # Default for decayed memories

    # Reduce threshold by 0.02 per access (min 0.65)
    adjustment = min(memory.access_count * 0.02, 0.15)

    return max(base_threshold - adjustment, 0.65)

# Example:
# Memory with access_count=3: threshold = 0.80 - 0.06 = 0.74
# Memory with access_count=8: threshold = 0.80 - 0.15 = 0.65 (minimum)
```

**Result:** Frequently-accessed memories are easier to recall even after decay.

### 11.2.2 Graph Pruning Strategies

As the knowledge graph grows (10K+ entities), performance degrades. Implement **intelligent pruning** to maintain quality.

#### Strategy 1: Weak Edge Removal

**Concept:** Delete relationships with low confidence and low access.

```python
async def prune_weak_edges(graph_store, min_hit_count=3, min_confidence=0.6):
    """
    Remove weak relationships that haven't been validated by usage.

    Args:
        min_hit_count: Minimum times relationship accessed
        min_confidence: Minimum extraction confidence
    """
    pruned = 0

    for edge in graph_store.get_all_edges():
        if edge.hit_count < min_hit_count and edge.confidence < min_confidence:
            graph_store.remove_edge(edge.source, edge.verb, edge.target)
            pruned += 1

    logger.info(f"Pruned {pruned} weak edges")
    return pruned

# Run weekly via cron
# friday-cli memory prune-edges --min-hits 3 --min-confidence 0.6
```

**Recommended Thresholds:**

| Graph Size | Min Hit Count | Min Confidence | % Edges Removed |
|------------|---------------|----------------|-----------------|
| <1K entities | 2 | 0.5 | ~5% |
| 1K-10K entities | 3 | 0.6 | ~15% |
| >10K entities | 5 | 0.7 | ~25% |

#### Strategy 2: Orphan Node Cleanup

**Concept:** Remove entities with no relationships (usually extraction errors).

```python
async def remove_orphan_nodes(graph_store, min_age_days=7):
    """
    Remove entities with:
    - Zero relationships
    - Low hit_count (< 3)
    - Existed for at least min_age_days (give time to form relationships)
    """
    orphans = []

    for entity in graph_store.get_all_entities():
        relationships = graph_store.get_relationships(entity.name)

        if (
            len(relationships) == 0
            and entity.hit_count < 3
            and (now() - entity.created_at).days >= min_age_days
        ):
            orphans.append(entity.name)

    for entity_name in orphans:
        graph_store.remove_entity(entity_name)

    logger.info(f"Removed {len(orphans)} orphan entities")
    return len(orphans)
```

#### Strategy 3: Entity Deduplication

**Concept:** Merge entities that refer to the same thing (fuzzy matching).

```python
from difflib import SequenceMatcher

async def deduplicate_entities(graph_store, similarity_threshold=0.85):
    """
    Merge entities with similar names.

    Examples:
    - "FastAPI" + "Fast API" → "FastAPI"
    - "Python" + "python" → "Python"
    - "Alice Smith" + "Alice" → "Alice Smith" (if same type)
    """
    entities = graph_store.get_all_entities()
    merged = 0

    for i, entity_a in enumerate(entities):
        for entity_b in entities[i+1:]:
            # Only merge same-type entities
            if entity_a.type != entity_b.type:
                continue

            similarity = SequenceMatcher(
                None,
                entity_a.name.lower(),
                entity_b.name.lower()
            ).ratio()

            if similarity >= similarity_threshold:
                # Merge entity_b into entity_a (keep higher hit_count name)
                if entity_b.hit_count > entity_a.hit_count:
                    entity_a, entity_b = entity_b, entity_a

                # Merge relationships
                for rel in graph_store.get_relationships(entity_b.name):
                    graph_store.add_relationship(
                        source=entity_a.name if rel.source == entity_b.name else rel.source,
                        verb=rel.verb,
                        target=entity_a.name if rel.target == entity_b.name else rel.target,
                        context=rel.context,
                        confidence=rel.confidence,
                    )

                # Remove duplicate
                graph_store.remove_entity(entity_b.name)
                merged += 1

    logger.info(f"Merged {merged} duplicate entities")
    return merged
```

#### Strategy 4: Subgraph Extraction

**Concept:** Extract topic-specific subgraphs for focused agents.

```python
async def extract_subgraph(
    graph_store,
    seed_entities: list[str],
    max_depth: int = 2,
    output_path: str = None
):
    """
    Extract a subgraph starting from seed entities.

    Use case: Create focused knowledge graphs for specialized agents.

    Example: Extract "Python ecosystem" subgraph
    Seeds: ["Python", "Django", "FastAPI", "Flask"]
    Result: All entities within 2 hops of seeds
    """
    subgraph_entities = set(seed_entities)
    subgraph_edges = []

    # BFS traversal from seed entities
    frontier = set(seed_entities)
    for depth in range(max_depth):
        next_frontier = set()

        for entity in frontier:
            relationships = graph_store.get_relationships(entity)

            for rel in relationships:
                subgraph_edges.append(rel)

                # Add connected entities to next frontier
                if rel.target not in subgraph_entities:
                    next_frontier.add(rel.target)
                    subgraph_entities.add(rel.target)

        frontier = next_frontier

    # Create subgraph
    subgraph = {
        "entities": [
            graph_store.get_entity(name)
            for name in subgraph_entities
        ],
        "relationships": subgraph_edges,
    }

    if output_path:
        with open(output_path, "w") as f:
            json.dump(subgraph, f, indent=2)

    return subgraph
```

### 11.2.3 Vector Store Compaction

#### Reindexing for Performance

ChromaDB performance degrades as collections grow. **Reindex periodically** to maintain speed.

```python
async def reindex_vector_store(vector_store):
    """
    Reindex ChromaDB collections for optimal performance.

    Recommended: Run monthly or when similarity search > 500ms
    """
    collections = ["short_term", "long_term", "decayed"]

    for collection_name in collections:
        logger.info(f"Reindexing collection: {collection_name}")

        # Get all documents
        docs = await vector_store.get_all_documents(collection=collection_name)

        # Recreate collection (drops indexes)
        await vector_store.delete_collection(collection_name)
        await vector_store.create_collection(collection_name)

        # Re-add documents (rebuilds indexes)
        for doc in docs:
            await vector_store.add_document(
                content=doc.content,
                embedding=doc.embedding,
                metadata=doc.metadata,
                collection=collection_name,
            )

        logger.info(f"Reindexed {len(docs)} documents in {collection_name}")
```

#### Embedding Model Upgrades

**Scenario:** Newer, better embedding models are released. Migrate existing embeddings.

```python
async def migrate_embeddings(
    vector_store,
    old_embedding_model,
    new_embedding_model,
    batch_size: int = 100
):
    """
    Re-embed all documents with a new embedding model.

    Example: Migrate from text-embedding-3-small to text-embedding-3-large
    """
    collections = ["short_term", "long_term", "decayed"]
    total_migrated = 0

    for collection_name in collections:
        logger.info(f"Migrating embeddings in {collection_name}")

        docs = await vector_store.get_all_documents(collection=collection_name)

        # Process in batches
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i+batch_size]

            # Generate new embeddings
            texts = [doc.content for doc in batch]
            new_embeddings = await new_embedding_model.embed_batch(texts)

            # Update documents
            for doc, new_embedding in zip(batch, new_embeddings):
                await vector_store.update_document(
                    doc_id=doc.id,
                    embedding=new_embedding,
                    collection=collection_name,
                )

            total_migrated += len(batch)
            logger.info(f"Migrated {total_migrated}/{len(docs)} documents")

    logger.info(f"Migration complete: {total_migrated} documents updated")
```

#### Vector Quantization

**Concept:** Reduce embedding dimensions for faster search (with quality tradeoff).

```python
from sklearn.decomposition import PCA

async def quantize_embeddings(
    vector_store,
    target_dimensions: int = 512,  # Reduce from 1536 to 512
):
    """
    Apply PCA to reduce embedding dimensions.

    Benefits:
    - 3x faster similarity search
    - 3x less storage

    Tradeoffs:
    - ~5% reduction in retrieval quality
    """
    docs = await vector_store.get_all_documents()

    # Extract embeddings
    embeddings = np.array([doc.embedding for doc in docs])

    # Fit PCA
    pca = PCA(n_components=target_dimensions)
    reduced_embeddings = pca.fit_transform(embeddings)

    # Update documents
    for doc, new_embedding in zip(docs, reduced_embeddings):
        await vector_store.update_document(
            doc_id=doc.id,
            embedding=new_embedding.tolist(),
        )

    # Save PCA model for new embeddings
    joblib.dump(pca, "pca_model.pkl")

    logger.info(f"Quantized {len(docs)} embeddings to {target_dimensions} dimensions")
```

---

## 11.3 Custom Protocol Implementations

Friday's protocol-first architecture enables **complete swappability** of core components.

### 11.3.1 Implementing Custom LLM Clients

**Use Case:** Integrate a custom LLM backend (Hugging Face, vLLM, proprietary model).

#### LLMClient Protocol

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

#### Example: Hugging Face Inference API Client

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
        # Format messages as prompt
        prompt = self._format_messages(messages)

        # Call Hugging Face API
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

        # Parse response
        content = data[0]["generated_text"]

        return LLMResponse(
            content=content,
            model=self.model,
            finish_reason="stop",
            usage={
                "prompt_tokens": len(prompt.split()),  # Approximate
                "completion_tokens": len(content.split()),
            },
        )

    async def streaming_completion(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        # Hugging Face doesn't support streaming via Inference API
        # Fall back to non-streaming
        response = await self.chat_completion(messages, temperature, max_tokens, **kwargs)
        yield response.content

    def get_model_info(self) -> dict:
        return {
            "name": self.model,
            "provider": "huggingface",
            "context_window": 8192,  # Model-specific
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

        formatted += "<|assistant|>\n"  # Prompt for response
        return formatted
```

**Usage:**

```python
from friday_agent import CopilotAgent

# Use custom HuggingFace client
hf_client = HuggingFaceLLMClient(model="meta-llama/Llama-3-70b-chat-hf")

agent = CopilotAgent(
    llm=hf_client,  # Friday accepts any LLMClient implementation
    memory_controller=memory_controller,
)

response = await agent.process("What is FastAPI?")
```

#### Example: vLLM Self-Hosted Client

**vLLM** is a high-performance inference server for self-hosting LLMs.

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

    async def chat_completion(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> LLMResponse:
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

    async def streaming_completion(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> AsyncIterator[str]:
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
        return {
            "name": self.model,
            "provider": "vllm",
            "context_window": 8192,
        }
```

**Deployment:**

```bash
# Install vLLM
pip install vllm

# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-70b-chat-hf \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 4  # Use 4 GPUs
```

### 11.3.2 Implementing Custom Memory Stores

#### VectorStoreAdapter Protocol

```python
# From friday-memory
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

    async def delete_document(
        self,
        doc_id: str,
        collection: str = "default",
    ) -> bool:
        """Delete a document by ID."""
        ...

    async def get_document(
        self,
        doc_id: str,
        collection: str = "default",
    ) -> Document | None:
        """Retrieve a document by ID."""
        ...
```

#### Example: Pinecone Adapter

```python
import pinecone
from friday_memory import VectorStoreAdapter, Document

class PineconeAdapter(VectorStoreAdapter):
    """Vector store adapter for Pinecone."""

    def __init__(
        self,
        api_key: str,
        environment: str,
        index_name: str,
    ):
        pinecone.init(api_key=api_key, environment=environment)
        self.index = pinecone.Index(index_name)

    async def add_document(
        self,
        content: str,
        embedding: list[float],
        metadata: dict,
        collection: str = "default",
    ) -> str:
        doc_id = str(uuid.uuid4())

        # Pinecone uses namespace for collections
        self.index.upsert(
            vectors=[
                {
                    "id": doc_id,
                    "values": embedding,
                    "metadata": {
                        **metadata,
                        "content": content,
                        "collection": collection,
                    },
                }
            ],
            namespace=collection,
        )

        return doc_id

    async def similarity_search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        threshold: float = 0.7,
        collection: str = "default",
        filters: dict | None = None,
    ) -> list[Document]:
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=limit,
            namespace=collection,
            filter=filters,
            include_metadata=True,
        )

        # Convert to Document format
        documents = []
        for match in results["matches"]:
            if match["score"] >= threshold:
                documents.append(
                    Document(
                        id=match["id"],
                        content=match["metadata"].pop("content"),
                        embedding=query_embedding,  # Pinecone doesn't return vectors
                        metadata=match["metadata"],
                    )
                )

        return documents

    async def delete_document(
        self,
        doc_id: str,
        collection: str = "default",
    ) -> bool:
        self.index.delete(ids=[doc_id], namespace=collection)
        return True

    async def get_document(
        self,
        doc_id: str,
        collection: str = "default",
    ) -> Document | None:
        results = self.index.fetch(ids=[doc_id], namespace=collection)

        if doc_id in results["vectors"]:
            vec = results["vectors"][doc_id]
            return Document(
                id=doc_id,
                content=vec["metadata"].pop("content"),
                embedding=vec["values"],
                metadata=vec["metadata"],
            )

        return None
```

**Usage:**

```python
from friday_memory import MemoryController

# Use Pinecone instead of ChromaDB
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

#### Example: Neo4j Graph Store

```python
from neo4j import AsyncGraphDatabase
from friday_memory import GraphStoreAdapter, Entity, Relationship

class Neo4jGraphAdapter(GraphStoreAdapter):
    """Graph store adapter for Neo4j."""

    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def add_entity(
        self,
        name: str,
        entity_type: str,
        description: str,
        metadata: dict | None = None,
    ) -> Entity:
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
                created_at=node["created_at"],
                last_accessed=node["last_accessed"],
                metadata=metadata or {},
            )

    async def add_relationship(
        self,
        source: str,
        verb: str,
        target: str,
        context: str,
        confidence: float,
    ) -> Relationship:
        async with self.driver.session() as session:
            await session.run(
                """
                MATCH (s:Entity {name: $source})
                MATCH (t:Entity {name: $target})
                MERGE (s)-[r:RELATES {verb: $verb}]->(t)
                ON CREATE SET
                    r.context = $context,
                    r.confidence = $confidence,
                    r.hit_count = 1,
                    r.created_at = datetime()
                ON MATCH SET
                    r.hit_count = r.hit_count + 1
                """,
                source=source,
                target=target,
                verb=verb,
                context=context,
                confidence=confidence,
            )

            return Relationship(
                source=source,
                verb=verb,
                target=target,
                context=context,
                confidence=confidence,
            )

    async def query_relationships(
        self,
        source: str,
        verb: str | None = None,
        target_type: str | None = None,
    ) -> list[Relationship]:
        query = """
        MATCH (s:Entity {name: $source})-[r:RELATES]->(t:Entity)
        """

        filters = []
        if verb:
            filters.append("r.verb = $verb")
        if target_type:
            filters.append("t.type = $target_type")

        if filters:
            query += "WHERE " + " AND ".join(filters)

        query += "RETURN r, t"

        async with self.driver.session() as session:
            result = await session.run(
                query,
                source=source,
                verb=verb,
                target_type=target_type,
            )

            relationships = []
            async for record in result:
                rel = record["r"]
                target = record["t"]

                relationships.append(
                    Relationship(
                        source=source,
                        verb=rel["verb"],
                        target=target["name"],
                        context=rel["context"],
                        confidence=rel["confidence"],
                    )
                )

            return relationships
```

### 11.3.3 Custom Tool Protocols & Wrappers

#### Wrapping External APIs as Tools

**Example: Slack Integration**

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
                data={
                    "channel": validated.channel,
                    "ts": data["ts"],
                    "thread_ts": validated.thread_ts,
                },
            )

        except Exception as e:
            return ToolResult(
                content=f"Failed to send Slack message: {str(e)}",
                error=str(e),
            )

# Register tool
from friday_agent import DefaultToolRegistry

slack_tool = SlackTool(bot_token=os.getenv("SLACK_BOT_TOKEN"))
DefaultToolRegistry.register(slack_tool)
```

#### Streaming Tools

**Example: Long-Running Operation with Progress**

```python
class GenerateReportParams(BaseModel):
    topic: str = Field(..., description="Report topic")
    sections: int = Field(5, description="Number of sections")

class StreamingReportTool(BaseTool):
    """Generate a multi-section report with streaming progress."""

    name = "generate_report"
    description = "Generate a detailed report on a topic"
    category = "content"
    parameters_schema = GenerateReportParams

    async def execute_streaming(self, **params) -> AsyncIterator[ToolResult]:
        """
        Streaming execute - yield partial results.

        Friday agents can display progress in real-time.
        """
        validated = self.parameters_schema(**params)

        yield ToolResult(
            content=f"Starting report generation: {validated.topic}",
            metadata={"progress": 0, "total": validated.sections},
        )

        report_sections = []

        for i in range(validated.sections):
            # Generate section (call LLM, search web, etc.)
            section = await self._generate_section(validated.topic, i+1)
            report_sections.append(section)

            # Yield progress update
            yield ToolResult(
                content=f"Completed section {i+1}/{validated.sections}: {section.title}",
                data={"section": section.model_dump()},
                metadata={"progress": i+1, "total": validated.sections},
            )

        # Final result
        full_report = "\n\n".join(section.content for section in report_sections)

        yield ToolResult(
            content=f"Report complete: {len(report_sections)} sections, {len(full_report)} chars",
            data={"report": full_report, "sections": report_sections},
            metadata={"progress": validated.sections, "total": validated.sections},
        )

    async def execute(self, **params) -> ToolResult:
        """Fallback non-streaming execute."""
        # Collect all streaming results and return final
        async for result in self.execute_streaming(**params):
            if result.metadata.get("progress") == result.metadata.get("total"):
                return result
```

---

## 11.4 Performance Optimization

### 11.4.1 Context Assembly Optimization

#### Parallel Store Retrieval

**Before (Sequential - Slow):**

```python
async def assemble_context_sequential(session_id, user_message):
    # Sequential queries = sum of latencies
    episodic = await transcript_store.get_recent_turns(session_id, limit=10)  # 50ms
    semantic = await vector_store.similarity_search(user_message, limit=20)    # 180ms
    associative = await graph_store.get_related_entities(user_message)         # 80ms

    # Total: 310ms
    return {"episodic": episodic, "semantic": semantic, "associative": associative}
```

**After (Parallel - Fast):**

```python
async def assemble_context_parallel(session_id, user_message):
    # Parallel queries = max of latencies (not sum!)
    episodic_task = transcript_store.get_recent_turns(session_id, limit=10)
    semantic_task = vector_store.similarity_search(user_message, limit=20)
    associative_task = graph_store.get_related_entities(user_message)

    # Await all concurrently
    episodic, semantic, associative = await asyncio.gather(
        episodic_task,
        semantic_task,
        associative_task,
    )

    # Total: 180ms (longest task) - 42% faster!
    return {"episodic": episodic, "semantic": semantic, "associative": associative}
```

**Benchmark Results:**

| Method | Latency | Improvement |
|--------|---------|-------------|
| Sequential | 310ms | Baseline |
| Parallel (asyncio.gather) | 180ms | 42% faster |

#### Context Caching

**Pattern:** Cache assembled context for rapid-fire turns (same session, similar queries).

```python
from cachetools import TTLCache

class CachedContextAssembler:
    """Context assembler with TTL cache."""

    def __init__(self, assembler, ttl_seconds=60):
        self.assembler = assembler
        self.cache = TTLCache(maxsize=100, ttl=ttl_seconds)

    async def assemble(self, session_id: str, user_message: str):
        # Generate cache key
        cache_key = f"{session_id}:{hash(user_message)}"

        # Check cache
        if cache_key in self.cache:
            logger.debug(f"Context cache hit: {cache_key}")
            return self.cache[cache_key]

        # Miss - assemble fresh context
        context = await self.assembler.assemble(session_id, user_message)

        # Store in cache
        self.cache[cache_key] = context

        return context
```

**Cache Invalidation:**

```python
# Invalidate cache when memory updated
@memory_controller.on_memory_update
async def invalidate_context_cache(session_id: str):
    # Remove all cached contexts for this session
    keys_to_remove = [k for k in cache.keys() if k.startswith(f"{session_id}:")]
    for key in keys_to_remove:
        del cache[key]
```

**Benchmark:**

| Turn | Uncached | Cached | Speedup |
|------|----------|--------|---------|
| 1 | 180ms | 180ms (miss) | 1x |
| 2 (similar) | 180ms | 2ms (hit) | 90x |
| 3 (similar) | 180ms | 2ms (hit) | 90x |
| 4 (different) | 180ms | 180ms (miss) | 1x |

**Use Case:** Chat interfaces where users ask follow-up questions rapidly.

#### Lazy Entity Loading

**Pattern:** Don't load full entity details until needed.

```python
class LazyEntity:
    """Entity proxy that loads details on-demand."""

    def __init__(self, name: str, entity_type: str, graph_store):
        self.name = name
        self.type = entity_type
        self._graph_store = graph_store
        self._details = None

    @property
    async def description(self) -> str:
        if self._details is None:
            self._details = await self._graph_store.get_entity(self.name)
        return self._details.description

    @property
    async def relationships(self) -> list[Relationship]:
        if self._details is None:
            self._details = await self._graph_store.get_entity(self.name)
        return self._details.relationships

# Context assembly only loads entity names initially
entities = [
    LazyEntity(name="Python", entity_type="Technology", graph_store=graph_store),
    LazyEntity(name="Alice", entity_type="Person", graph_store=graph_store),
]

# Details loaded only if agent accesses them
description = await entities[0].description  # Triggers load
```

### 11.4.2 Memory Store Indexing

#### Database Indexing Strategy

**SQLite (Episodic Store):**

```sql
-- Index for session-based queries (most common)
CREATE INDEX idx_turns_session_timestamp
    ON turns(session_id, timestamp DESC);

-- Index for user-based queries
CREATE INDEX idx_turns_user_timestamp
    ON turns(user_id, timestamp DESC);

-- Index for tool execution queries
CREATE INDEX idx_turns_tool_calls
    ON turns(tool_calls)
    WHERE tool_calls IS NOT NULL;

-- Analyze query performance
EXPLAIN QUERY PLAN
SELECT * FROM turns
WHERE session_id = 'abc123'
ORDER BY timestamp DESC
LIMIT 10;
```

**ChromaDB (Vector Store):**

```python
# Tune HNSW index parameters
collection = client.create_collection(
    name="memories_long_term",
    metadata={
        "hnsw:space": "cosine",           # Distance metric
        "hnsw:M": 16,                     # Max connections per layer (higher = more accurate, slower)
        "hnsw:ef_construction": 200,      # Construction effort (higher = better quality index)
        "hnsw:ef_search": 100,            # Search effort (higher = more accurate, slower)
    },
)
```

**HNSW Tuning Guide:**

| Use Case | M | ef_construction | ef_search | Quality | Speed |
|----------|---|-----------------|-----------|---------|-------|
| Speed-critical | 8 | 100 | 50 | Good | Very Fast |
| Balanced (default) | 16 | 200 | 100 | Better | Fast |
| Quality-critical | 32 | 400 | 200 | Best | Slower |

**NetworkX (Graph Store):**

```python
# Pre-compute frequently-used subgraphs
@lru_cache(maxsize=100)
def get_entity_neighborhood(entity_name: str, depth: int = 1):
    """Cache entity neighborhood subgraphs."""
    return nx.ego_graph(graph, entity_name, radius=depth)

# Index entities by type for fast filtering
entity_by_type = defaultdict(list)
for entity_name, entity_data in graph.nodes(data=True):
    entity_by_type[entity_data["type"]].append(entity_name)
```

### 11.4.3 Token Budget Optimization

#### Compression Strategies

**Strategy 1: Summarize Old Turns**

```python
async def compress_history(turns: list[Turn], max_tokens: int = 2000):
    """
    Summarize old conversation turns to fit token budget.

    Keep recent turns verbatim, summarize older turns.
    """
    if estimate_tokens(turns) <= max_tokens:
        return turns  # Fits already

    # Keep last 3 turns verbatim (most important for coherence)
    recent_turns = turns[-3:]
    old_turns = turns[:-3]

    # Summarize old turns
    old_text = "\n\n".join(
        f"User: {t.user_message}\nAssistant: {t.assistant_message}"
        for t in old_turns
    )

    summary = await llm.generate(
        f"Summarize this conversation concisely:\n\n{old_text}"
    )

    # Create synthetic turn for summary
    summary_turn = Turn(
        id="summary",
        user_message="[Earlier conversation]",
        assistant_message=summary,
    )

    return [summary_turn] + recent_turns
```

**Strategy 2: Aggressive Relevance Filtering**

```python
async def filter_low_relevance_memories(
    memories: list[Insight],
    query: str,
    threshold: float = 0.75,  # Raise from default 0.70
):
    """
    Use higher similarity threshold to include only highly relevant memories.

    Tradeoff: Fewer memories, but each is more relevant.
    """
    filtered = [m for m in memories if m.similarity >= threshold]

    logger.info(f"Filtered {len(memories)} → {len(filtered)} memories (threshold {threshold})")

    return filtered
```

**Strategy 3: Tool Schema Minimization**

```python
def minimize_tool_schema(tool: BaseTool) -> dict:
    """
    Generate minimal tool schema (parameters only, no descriptions).

    Use when token budget is tight.
    """
    return {
        "name": tool.name,
        "parameters": {
            param_name: {"type": param_type.__name__}
            for param_name, param_type in tool.parameters_schema.__annotations__.items()
        },
    }

# Before: ~150 tokens per tool (with descriptions)
# After: ~30 tokens per tool (parameters only)
# Savings: 80%
```

#### Dynamic Budget Reallocation

```python
async def assemble_context_dynamic(session_id, user_message, total_budget=8000):
    """
    Dynamically reallocate token budget based on what's available.

    Priority order: system > query > history > context
    """
    budgets = {
        "system": 1000,    # Fixed
        "query": len(user_message.split()),  # Actual size
        "history": 2000,   # Target
        "context": 4000,   # Target
    }

    # Calculate remaining budget after query
    used = budgets["system"] + budgets["query"]
    remaining = total_budget - used

    # Reallocate remaining budget
    if remaining < 6000:
        # Tight budget - reduce history, prioritize context
        budgets["history"] = int(remaining * 0.3)
        budgets["context"] = int(remaining * 0.7)
    else:
        # Plenty of space - use targets
        budgets["history"] = 2000
        budgets["context"] = remaining - 2000

    # Assemble with dynamic budgets
    context = await assemble_with_budgets(
        session_id,
        user_message,
        history_budget=budgets["history"],
        context_budget=budgets["context"],
    )

    return context
```

---

## 11.5 Deployment Patterns

### 11.5.1 Docker Deployment

#### Multi-Stage Dockerfile

```dockerfile
# Stage 1: Build dependencies
FROM python:3.13.4-slim AS builder

WORKDIR /app

# Install uv (fast Python package manager)
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies to /app/.venv
RUN uv sync --frozen

# Stage 2: Runtime image
FROM python:3.13.4-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY packages/ ./packages/
COPY scripts/ ./scripts/
COPY config.yaml ./

# Create data directories
RUN mkdir -p /data/friday/vector \
             /data/friday/graph \
             /data/friday/transcripts \
             /data/friday/exports

# Use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Non-root user
RUN useradd -m -u 1000 friday && \
    chown -R friday:friday /app /data/friday
USER friday

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import friday_agent; print('healthy')"

# Expose port (if running API server)
EXPOSE 8000

# Entry point
CMD ["python", "-m", "friday_agent.cli"]
```

**Build & Run:**

```bash
# Build image
docker build -t friday-agent:latest .

# Run with volume mounts for persistence
docker run -d \
    --name friday \
    -v $(pwd)/data:/data/friday \
    -e OPENAI_API_KEY=$OPENAI_API_KEY \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -p 8000:8000 \
    friday-agent:latest
```

#### Docker Compose Stack

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Friday agent
  friday:
    build: .
    container_name: friday-agent
    volumes:
      - ./data/friday:/data/friday
      - ./config.yaml:/app/config.yaml:ro
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
      - chromadb
    networks:
      - friday-network
    restart: unless-stopped

  # Ollama for local LLMs
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ./data/ollama:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - friday-network
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # ChromaDB (optional - can use embedded)
  chromadb:
    image: chromadb/chroma:latest
    container_name: chromadb
    volumes:
      - ./data/chromadb:/chroma/chroma
    ports:
      - "8001:8000"
    networks:
      - friday-network
    restart: unless-stopped

networks:
  friday-network:
    driver: bridge
```

**Launch Stack:**

```bash
# Start all services
docker-compose up -d

# Pull Ollama models
docker exec ollama ollama pull llama3
docker exec ollama ollama pull mistral

# Check logs
docker-compose logs -f friday

# Stop stack
docker-compose down
```

### 11.5.2 Kubernetes Deployment

#### Deployment Manifest

```yaml
# friday-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: friday-agent
  namespace: ai-agents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: friday-agent
  template:
    metadata:
      labels:
        app: friday-agent
    spec:
      containers:
      - name: friday
        image: myregistry/friday-agent:v0.1.0
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: friday-secrets
              key: openai-api-key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: friday-secrets
              key: anthropic-api-key
        - name: OLLAMA_BASE_URL
          value: "http://ollama-service:11434"
        volumeMounts:
        - name: friday-data
          mountPath: /data/friday
        - name: config
          mountPath: /app/config.yaml
          subPath: config.yaml
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: friday-data
        persistentVolumeClaim:
          claimName: friday-data-pvc
      - name: config
        configMap:
          name: friday-config
---
apiVersion: v1
kind: Service
metadata:
  name: friday-service
  namespace: ai-agents
spec:
  selector:
    app: friday-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: friday-data-pvc
  namespace: ai-agents
spec:
  accessModes:
  - ReadWriteMany  # Shared across replicas
  resources:
    requests:
      storage: 50Gi
  storageClassName: nfs  # Use NFS for shared storage
```

#### ConfigMap & Secrets

```yaml
# friday-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: friday-config
  namespace: ai-agents
data:
  config.yaml: |
    llm:
      model: "gpt-4o"
      temperature: 0.7
    memory:
      storage_path: "/data/friday"
      total_tokens: 8000
    extraction:
      llm:
        model: "ollama/mistral"
---
apiVersion: v1
kind: Secret
metadata:
  name: friday-secrets
  namespace: ai-agents
type: Opaque
stringData:
  openai-api-key: "sk-proj-..."
  anthropic-api-key: "sk-ant-..."
```

**Deploy:**

```bash
# Create namespace
kubectl create namespace ai-agents

# Apply configs
kubectl apply -f friday-config.yaml
kubectl apply -f friday-deployment.yaml

# Check status
kubectl get pods -n ai-agents
kubectl logs -f deployment/friday-agent -n ai-agents

# Scale replicas
kubectl scale deployment/friday-agent --replicas=5 -n ai-agents
```

#### Horizontal Pod Autoscaling

```yaml
# friday-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: friday-hpa
  namespace: ai-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: friday-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 120
```

### 11.5.3 Serverless Deployment (AWS Lambda)

**Challenges:**
- Cold start latency (1-3s for first request)
- Memory store initialization overhead
- Stateless environment (must load context from persistent storage)

**Solutions:**

#### Minimal Context Priming

```yaml
# config-lambda.yaml
memory:
  priming:
    enabled: true
    top_n_entities: 5       # Reduce from 10
    top_n_insights: 10      # Reduce from 20
    recency_days: 7         # Reduce from 30

  # Use faster stores
  vector_store:
    type: "dynamodb"  # AWS DynamoDB for serverless
  graph_store:
    type: "dynamodb"
  episodic_store:
    type: "dynamodb"
```

#### Lambda Handler

```python
# lambda_handler.py
import json
from friday_agent import CopilotAgent
from friday_memory import MemoryController

# Initialize outside handler (reused across invocations)
memory_controller = None
agent = None

def init_agent():
    """Initialize agent once per container lifetime."""
    global memory_controller, agent

    if agent is None:
        memory_controller = MemoryController.from_config("config-lambda.yaml")
        agent = CopilotAgent(
            llm=llm_client,
            memory_controller=memory_controller,
        )

    return agent

def lambda_handler(event, context):
    """
    AWS Lambda handler for Friday agent.

    Event structure:
    {
        "session_id": "session_123",
        "user_id": "user_456",
        "message": "What is FastAPI?"
    }
    """
    # Initialize agent (reuses if already loaded)
    agent = init_agent()

    # Extract request
    session_id = event["session_id"]
    user_id = event["user_id"]
    message = event["message"]

    # Process request
    response = await agent.process(
        message,
        session_id=session_id,
        user_id=user_id,
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "response": response,
            "session_id": session_id,
        }),
    }
```

#### Deployment Package

```bash
# Install dependencies to package directory
pip install -r requirements.txt -t package/

# Copy Friday code
cp -r packages/ package/

# Create deployment ZIP
cd package
zip -r ../friday-lambda.zip .
cd ..
zip -g friday-lambda.zip lambda_handler.py config-lambda.yaml

# Upload to Lambda
aws lambda update-function-code \
    --function-name friday-agent \
    --zip-file fileb://friday-lambda.zip
```

#### API Gateway Integration

```yaml
# serverless.yml (using Serverless Framework)
service: friday-agent

provider:
  name: aws
  runtime: python3.11
  region: us-west-2
  memorySize: 2048
  timeout: 30
  environment:
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}
    DYNAMODB_TABLE: friday-memories

functions:
  process:
    handler: lambda_handler.lambda_handler
    events:
      - httpApi:
          path: /process
          method: POST

resources:
  Resources:
    MemoriesTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: friday-memories
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: pk
            AttributeType: S
          - AttributeName: sk
            AttributeType: S
        KeySchema:
          - AttributeName: pk
            KeyType: HASH
          - AttributeName: sk
            KeyType: RANGE
```

**Deploy:**

```bash
serverless deploy
```

**Invoke:**

```bash
curl -X POST https://abc123.execute-api.us-west-2.amazonaws.com/process \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_123",
    "user_id": "user_456",
    "message": "What is FastAPI?"
  }'
```

---

## Summary: Advanced Topics

You've now mastered Friday's advanced capabilities:

1. **Hybrid Cloud-Local Architecture (Section 11.1)**
   - Cost optimization strategies (65%+ savings)
   - Privacy-compliant deployments (air-gapped, encrypted)
   - Latency vs capability tradeoffs

2. **Memory Optimization (Section 11.2)**
   - Hot-cold-warm memory tiers
   - Graph pruning strategies (25% edge reduction)
   - Vector store compaction and quantization

3. **Custom Protocols (Section 11.3)**
   - Implementing LLMClient for custom backends
   - VectorStoreAdapter for Pinecone, Neo4j
   - Tool wrappers for external APIs

4. **Performance Optimization (Section 11.4)**
   - Parallel context assembly (42% faster)
   - Memory store indexing
   - Token budget optimization (80% schema savings)

5. **Deployment Patterns (Section 11.5)**
   - Docker and Docker Compose
   - Kubernetes with HPA
   - AWS Lambda serverless

**Next Steps:**

- **[Section 12: Use Cases](12-use-cases.md)** - Real-world applications
- **[Section 13: Troubleshooting](13-troubleshooting.md)** - Debugging production issues
- **[Appendix D: Protocol Specifications](14-appendices.md#appendix-d-protocol-specifications)** - Complete interface definitions

---

*You've completed Section 11: Advanced Topics. You now have the knowledge to build, optimize, and deploy production-grade Friday agents at scale.*
