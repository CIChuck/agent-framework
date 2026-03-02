---
title: "Context Engineering"
description: "Token-budget-aware context assembly using the Knapsack algorithm."
weight: 3
---

Friday's ContextAssembler uses a Knapsack algorithm to pack the highest-value memories into each LLM call while staying within the configured token budget.

---

## The Challenge: Limited Context Windows

LLMs have **fixed context windows**—the maximum amount of text they can process in a single request:

| Model | Context Window | Cost Implications |
|-------|----------------|-------------------|
| GPT-4o | 128K tokens | Higher cost, more capacity |
| GPT-4o-mini | 128K tokens | Lower cost, same capacity |
| Claude 3.5 Sonnet | 200K tokens | Highest capacity |
| Claude 3 Haiku | 200K tokens | Fast, budget-friendly |
| Gemini 2.5 Flash | 1M tokens | Massive capacity |
| Llama 3 (8B) | 8K tokens | Local, limited capacity |

**The Problem:** Friday's three memory stores can contain gigabytes of information, but the LLM can only see 8K-200K tokens per request.

**The Solution:** **Context Engineering**—intelligently select and structure the most relevant subset of memories to fit within the token budget.

---

## The Knapsack Problem

Context assembly is fundamentally a **0/1 knapsack optimization**:

```text
Given:
  - N memories, each with:
    - value_i (relevance score)
    - weight_i (token cost)
  - Budget B (maximum tokens)

Find:
  - Subset S of memories where:
    - sum(weight_i) <= B (fits within budget)
    - sum(value_i) is maximized (most relevant memories)
```

**Naive approaches fail:**
- **Most recent N**: Ignores relevance (old but highly relevant memories excluded)
- **Highest similarity**: Ignores cost (one huge memory might consume entire budget)
- **Round-robin**: Ignores both relevance and cost

**Friday's Solution:** Dynamic programming knapsack solver from `friday-optimization` package.

---

## Token Budget Allocation

**Budget Structure:**

```yaml
memory:
  total_tokens: 8000            # Total LLM context window

  # Allocated budgets:
  system_prompt_tokens: 1000    # Identity, capabilities, guidelines
  history_tokens: 2000          # Recent conversation turns
  context_tokens: 4000          # Retrieved memories (knapsack optimized)
  query_tokens: 1000            # User's current message + buffer
```

**Why these allocations?**
- **System prompt (12.5%)**: Static, defines agent identity
- **History (25%)**: Recent turns for conversation coherence
- **Context (50%)**: Largest allocation—retrieved memories are most valuable
- **Query (12.5%)**: User message + buffer for response

### Adaptive Budgeting

Friday can adjust allocations dynamically:

```python
# If query is short, reallocate to context
if query_tokens < 500:
    context_tokens += (1000 - query_tokens)  # Use saved budget

# If history is minimal (early conversation), reallocate to context
if history_tokens < 1000:
    context_tokens += (2000 - history_tokens)
```

---

## Context Assembly Algorithm

### Step 1: Retrieve Candidate Memories

Query all three stores in parallel:

```python
# Episodic: Recent turns
episodic_memories = await transcript_store.get_recent_turns(
    session_id=session_id,
    limit=10
)

# Semantic: Similar insights
semantic_memories = await vector_store.similarity_search(
    query=user_message,
    limit=50,  # Retrieve more candidates than budget allows
    threshold=0.7,
    collections=["long_term", "short_term"]  # Search both, long-term first
)

# Associative: Related entities
associative_memories = await graph_store.get_related_entities(
    query_terms=extract_keywords(user_message),
    limit=20,
    min_hit_count=3  # Only entities accessed at least 3 times
)
```

### Step 2: Score Candidates

Each memory gets a **composite relevance score**:

```python
def score_memory(memory, query, current_turn):
    """Calculate relevance score (0-1) for a memory."""

    # Component 1: Semantic Similarity (40%)
    similarity = cosine_similarity(memory.embedding, query.embedding)
    sim_score = similarity * 0.40

    # Component 2: Recency (30%)
    age_hours = (current_turn - memory.created_at).total_seconds() / 3600
    recency_score = 1.0 / (1.0 + log(1 + age_hours))  # Logarithmic decay
    recency_score = recency_score * 0.30

    # Component 3: Importance (20%)
    # For semantic: confidence score
    # For associative: hit_count (Hebbian)
    if memory.type == "insight":
        importance = memory.confidence
    elif memory.type == "entity":
        importance = min(memory.hit_count / 50, 1.0)  # Normalize to 0-1
    importance_score = importance * 0.20

    # Component 4: Collection Stage (10%)
    # Long-term memories are more valuable than short-term
    stage_scores = {
        "long_term": 1.0,
        "short_term": 0.7,
        "decayed": 0.3
    }
    stage_score = stage_scores.get(memory.collection, 0.5) * 0.10

    return sim_score + recency_score + importance_score + stage_score
```

### Step 3: Estimate Token Costs

```python
def estimate_tokens(text: str) -> int:
    """Rough token estimation: 1 token approximately equals 4 characters."""
    return len(text) // 4

# Calculate cost for each memory
for memory in candidates:
    memory.token_cost = estimate_tokens(memory.content)
    memory.value = score_memory(memory, query, current_turn)
```

### Step 4: Knapsack Optimization

```python
from friday_optimization import solve_knapsack

selected_memories = solve_knapsack(
    items=candidates,
    capacity=context_tokens,  # Token budget (e.g., 4000)
    get_weight=lambda m: m.token_cost,
    get_value=lambda m: m.value
)

# Result: Subset of memories that maximizes relevance within budget
```

**Example knapsack run:**

**Budget:** 4000 tokens
**Candidates:**

| Memory | Content | Tokens | Relevance | Selected? |
|--------|---------|--------|-----------|-----------|
| M1 | "User prefers FastAPI" | 150 | 0.92 | Yes |
| M2 | "Mentioned web API project" | 200 | 0.88 | Yes |
| M3 | "Discussed Python vs JavaScript" | 600 | 0.45 | No |
| M4 | "FastAPI has good docs" | 180 | 0.85 | Yes |
| M5 | "Likes automated testing" | 140 | 0.78 | Yes |
| M47 | "Weather was nice" | 100 | 0.15 | No |

**Output:** Selected 28 memories totaling 3,950 tokens with combined relevance score of 23.4

**Knapsack ensures:**
- **Optimal packing**: No wasted token budget
- **Relevance maximization**: Highest-value memories selected
- **Fairness**: Balance between many small memories vs. few large ones

---

## Lost-in-the-Middle Mitigation

### The Research

Studies (Liu et al., 2023) show LLMs pay less attention to content in the middle of long contexts:

```text
┌─────────────────────────────────────────────┐
│         LLM ATTENTION DISTRIBUTION          │
│                                             │
│  High |################       #############|│
│       |                                    |│
│  Low  |          ##########               |│
│       |                                    |│
│       └────────────────────────────────────┘│
│        Start        Middle          End      │
└─────────────────────────────────────────────┘

# = Strong attention
```

**The Problem:** If we structure the prompt as:

```text
1. System prompt (start - strong attention)
2. Retrieved memories (middle - WEAK ATTENTION)  <- Problem!
3. User query (end - strong attention)
```

Then the most relevant memories (retrieved context) get the least attention.

### Friday's Solution: Tail Injection

Place retrieved memories **immediately before** the user query:

```text
1. System prompt (start)
2. Conversation history (middle - less critical for recent turns)
3. Retrieved memories (just before end)  <- Strong attention!
4. User query (end)
```

**Prompt Structure:**

```python
messages = [
    {
        "role": "system",
        "content": system_prompt + "\n\n" + agent_capabilities
    },
    {
        "role": "user",
        "content": history_turn_1_user
    },
    {
        "role": "assistant",
        "content": history_turn_1_assistant
    },
    # ... more history turns ...
    {
        "role": "user",
        "content": (
            "# Relevant Context:\n" +
            retrieved_memory_1 + "\n" +
            retrieved_memory_2 + "\n" +
            # ... more retrieved memories ...
            "\n# Current Query:\n" +
            user_current_message
        )
    }
]
```

**Effect:** Retrieved memories are placed in the **recency zone** where LLM attention is highest, dramatically improving context utilization.

---

## Context Payload Structure

**ContextPayload Data Model:**

```python
@dataclass
class ContextPayload:
    """Assembled context ready for LLM."""

    # Core components
    system_prompt: str
    conversation_history: list[Turn]
    retrieved_insights: list[Insight]
    loaded_entities: list[Entity]
    injected_tools: list[ToolSchema]
    scoped_variables: dict[str, Any]

    # Metadata
    token_counts: dict[str, int]  # Per-component token usage
    retrieval_latency_ms: int
    knapsack_efficiency: float  # % of budget used

    # Debug info
    candidates_considered: int
    candidates_selected: int
    similarity_threshold: float
```

**Token Count Breakdown:**

```python
{
    "system_prompt": 823,
    "history": 1456,
    "insights": 2891,  # Knapsack-selected semantic memories
    "entities": 478,   # Graph-loaded entities
    "tools": 312,      # Tool schemas (if any)
    "variables": 45,   # Scoped variables
    "query": 215,      # User message
    "total": 6220,     # Sum (must be <= total_tokens)
    "buffer": 1780     # Remaining budget (22% unused)
}
```

---

## Context Formats

Friday supports multiple output formats for different LLM preferences:

**1. Plain Text (Default):**

```text
You are Friday, an AI assistant with memory.

Recent Conversation:
Turn 1: User asked about Python web frameworks
Turn 2: You recommended FastAPI

Relevant Memories:
- User prefers FastAPI over Flask
- User values automatic documentation
- User is working on a REST API project

Current Query:
Should I use Flask or FastAPI for my project?
```

**2. XML (Claude Optimal):**

```xml
<system>
  <identity>You are Friday, an AI assistant with memory.</identity>
</system>

<history>
  <turn>
    <user>What's the best Python web framework?</user>
    <assistant>FastAPI is excellent for modern APIs...</assistant>
  </turn>
</history>

<context>
  <memory type="preference">User prefers FastAPI over Flask</memory>
  <memory type="observation">User values automatic documentation</memory>
  <entity name="User" type="Person">
    <relationship>WORKING_ON</relationship>
    <entity name="REST_API" type="Project"/>
  </entity>
</context>

<query>Should I use Flask or FastAPI for my project?</query>
```

**3. JSON (Structured Extraction):**

```json
{
  "system": {
    "identity": "You are Friday, an AI assistant with memory."
  },
  "history": [
    {"role": "user", "content": "What's the best Python web framework?"},
    {"role": "assistant", "content": "FastAPI is excellent..."}
  ],
  "context": {
    "memories": [
      {"type": "preference", "content": "User prefers FastAPI over Flask", "confidence": 0.92}
    ],
    "entities": [
      {"name": "User", "type": "Person", "relationships": [{"verb": "WORKING_ON", "target": "REST_API"}]}
    ]
  },
  "query": "Should I use Flask or FastAPI for my project?"
}
```

**Configuration:**

```yaml
memory:
  context_format: "xml"  # plain | xml | json | markdown
```

**Format overhead comparison:**

| Format | Token Overhead | Best For |
|--------|---------------|----------|
| `plain` | Baseline | Conversational use, token efficiency |
| `json` | +20-30% | Structured extraction, tool-use |
| `xml` | +30-40% | Claude models, structured parsing |
| `markdown` | +10-15% | Readable structure, tables |

{{< callout type="info" >}}
Claude models perform particularly well with XML-formatted context due to their training on Anthropic's XML-based tool format. JSON format is ideal for agents that need to extract structured information from context.
{{< /callout >}}

---

## Session Priming & Cross-Session Continuity

### The Cold Start Problem

**Challenge:** When starting a new session (new day, new terminal window, agent restart), Friday has no context. Without priming, the first few turns feel like talking to a stranger who doesn't know you.

**Solution:** **Session Priming**—automatically load the most important memories when initializing a session, before the first user message.

### What Gets Primed

```python
async def prime_session(session_id: str, user_id: str):
    """Load important memories before first turn."""

    # 1. Top entities by Hebbian importance
    top_entities = await graph_store.get_top_entities(
        limit=10,              # Top 10 most-accessed entities
        min_hit_count=5        # Only entities accessed at least 5 times
    )

    # 2. Recent insights (from last N days)
    recent_insights = await vector_store.query(
        collection="long_term",
        filters={"created_at": {"$gte": days_ago(30)}},
        sort_by="created_at",
        limit=20
    )

    # 3. User preferences (high-confidence insights)
    preferences = await vector_store.query(
        collection="long_term",
        filters={"type": "preference", "confidence": {"$gte": 0.8}},
        limit=15
    )

    # 4. Recent conversation summaries
    summaries = await transcript_store.get_session_summaries(
        user_id=user_id,
        days=7,  # Last week
        limit=5
    )
```

### Priming Configuration

```yaml
memory:
  priming:
    enabled: true

    # What to load
    top_n_entities: 10         # Most accessed entities
    top_n_insights: 20         # Recent insights
    top_n_preferences: 15      # User preferences

    # Filters
    min_entity_hit_count: 5    # Only load frequently-accessed entities
    recency_days: 30           # Only load memories from last 30 days
    min_confidence: 0.8        # Only load high-confidence preferences
```

### Priming in Action

**Session 1 (Monday):**

```text
User: "Hi, I'm Alice. I'm working on a Python web API using FastAPI."
Friday: "Hello Alice! I'll remember that you're working with Python and FastAPI..."

[Extraction runs in background]
Entities: Alice (Person), Python (Technology), FastAPI (Technology)
Insights: "User (Alice) is developing a web API with Python and FastAPI"
```

**Session 2 (Tuesday):**

```text
[Priming loads before first message]
- Entity: Alice (hit_count=5, type=Person)
- Entity: FastAPI (hit_count=8, type=Technology)
- Insight: "Alice is developing a web API with Python and FastAPI" (confidence=0.89)

User: "Good morning!"
Friday: "Good morning, Alice! How's your FastAPI project coming along?"
         ^-- Remembered name and project without being reminded!
```

**CLI commands:** `/prime`, `/context --debug`, `/prompt`

---

## Performance Targets

| Operation | Target Latency |
|-----------|----------------|
| Context assembly | <200ms |
| Session priming | <500ms |
| Knapsack solver (O(n x capacity)) | <50ms |
| Vector similarity search | 50-200ms |
| Graph query | <50ms |

{{< callout type="info" >}}
Use `/context --debug` to see a full token budget breakdown. Check `knapsack_efficiency` to see if the budget is well-utilized (>90% is ideal). Adjust `context_tokens` budget if retrieval feels insufficient.
{{< /callout >}}
