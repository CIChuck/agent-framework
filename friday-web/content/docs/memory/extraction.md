---
title: "Extraction Pipeline"
description: "How Friday extracts structured facts and entities from raw conversations."
weight: 4
---

The extraction pipeline parses raw conversation turns into structured facts, entities, and relationships that are stored across the graph, vector, and episodic stores.

---

## From Conversation to Structured Knowledge

Every conversation turn triggers a **background extraction process** that converts unstructured dialogue into structured memories:

```text
┌────────────────────────────────────────────────────────────┐
│                   EXTRACTION PIPELINE                      │
│                                                            │
│  User Message + Assistant Response                        │
│              │                                             │
│              ▼                                             │
│  ┌──────────────────────┐                                 │
│  │  Extraction LLM      │  (Separate, cheaper model)     │
│  │  Analyzes turn for:  │                                 │
│  │  - Entities          │                                 │
│  │  - Relationships     │                                 │
│  │  - Insights          │                                 │
│  └─────────┬────────────┘                                 │
│            │                                               │
│            ├──────────► Entities (Person, Technology, ...)│
│            │            └─► Graph Store                    │
│            │                                               │
│            ├──────────► Relationships (USES, PREFERS, ...)│
│            │            └─► Graph Store                    │
│            │                                               │
│            └──────────► Insights (Preferences, decisions) │
│                         └─► Vector Store (with embeddings)│
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Extraction LLM Configuration

### Why a Separate Model?

- **Cost optimization**: Use cheaper model (GPT-4o-mini, Claude Haiku) for structured extraction
- **Specialized prompts**: Extraction requires different capabilities than conversation
- **Temperature control**: Lower temperature (0.3) for consistent extraction
- **Parallel execution**: Main LLM handles conversation, extraction LLM runs in background

**Configuration:**

```yaml
extraction:
  enabled: true

  llm:
    model: "gpt-4o-mini"        # Cheaper model for extraction
    temperature: 0.3            # Lower = more consistent
    max_tokens: 2000            # Shorter responses (just JSON)

  confidence_threshold: 0.6     # Minimum extraction confidence

  # What to extract
  extract_entities: true
  extract_relationships: true
  extract_insights: true
```

**Cost Comparison:**

| Model | Cost per 1M tokens | Typical Extraction Cost (per turn) |
|-------|-------------------|------------------------------------|
| GPT-4o (conversation) | $2.50 | $0.005 |
| GPT-4o-mini (extraction) | $0.15 | $0.0003 |
| **Savings** | **94%** | **$0.0047 per turn** |

For 1000 turns/day: **~$1.50/day savings** by using a dedicated extraction model.

---

## Entity Extraction

**Extraction Prompt:**

```text
Analyze the following conversation turn and extract all entities mentioned.

For each entity, provide:
- name: The entity name (normalize: "fastapi" -> "FastAPI")
- type: Person | Technology | Project | Concept | Organization | Location
- description: Brief explanation (1 sentence)
- confidence: 0.0-1.0 (how certain are you this is a distinct entity?)

Conversation:
User: "I'm using FastAPI for my project at Acme Corp"
Assistant: "FastAPI is great for building APIs in Python..."

Output as JSON:
{
  "entities": [
    {
      "name": "FastAPI",
      "type": "Technology",
      "description": "Python web framework for building APIs",
      "confidence": 0.95
    },
    {
      "name": "Acme Corp",
      "type": "Organization",
      "description": "User's employer",
      "confidence": 0.85
    },
    {
      "name": "Python",
      "type": "Technology",
      "description": "Programming language",
      "confidence": 0.98
    }
  ]
}
```

### Entity Normalization

Friday normalizes entity names to prevent duplicates:
- Case normalization: "fastapi" → "FastAPI", "python" → "Python"
- Variant consolidation: "FastAPI" = "Fast API" = "fast-api"
- Abbreviation expansion: "API" mentioned with "Application Programming Interface" → link them

### Entity Deduplication

```python
# When extracting entity "FastAPI"
existing_entity = graph_store.find_entity(name="FastAPI")

if existing_entity:
    # Entity exists - update metadata, increment hit_count
    existing_entity.hit_count += 1
    existing_entity.last_accessed = now()
    existing_entity.description = merge_descriptions(
        existing_entity.description,
        new_extraction.description
    )
else:
    # New entity - create node
    graph_store.add_entity(new_extraction)
```

---

## Relationship Extraction

**Extraction Prompt:**

```text
Analyze the conversation and extract relationships between entities.

For each relationship, provide:
- source: Entity name (must be from extracted entities)
- verb: Semantic relationship (USES, PREFERS, WORKING_ON, CREATED, ...)
- target: Entity name
- context: Supporting quote or explanation
- confidence: 0.0-1.0

Use specific, semantic verbs (not generic "RELATED_TO").

Conversation:
User: "I'm using FastAPI for my project because I prefer it over Flask"

Output as JSON:
{
  "relationships": [
    {
      "source": "User",
      "verb": "USES",
      "target": "FastAPI",
      "context": "for current project",
      "confidence": 0.95
    },
    {
      "source": "User",
      "verb": "PREFERS",
      "target": "FastAPI",
      "context": "prefers over Flask",
      "confidence": 0.90
    },
    {
      "source": "FastAPI",
      "verb": "ALTERNATIVE_TO",
      "target": "Flask",
      "context": "User comparing the two",
      "confidence": 0.85
    }
  ]
}
```

### Relationship Confidence Scoring

```python
def score_relationship_confidence(relationship, conversation_text):
    """Calculate confidence score for extracted relationship."""

    # Factor 1: Explicit statement (60%)
    explicit_patterns = [
        "prefers", "uses", "created", "working on"
    ]
    explicit_score = 0.6 if any(p in conversation_text.lower() for p in explicit_patterns) else 0.3

    # Factor 2: Context clarity (30%)
    context_length = len(relationship.context)
    clarity_score = min(context_length / 100, 1.0) * 0.3

    # Factor 3: Entity confidence (10%)
    entity_conf = (
        get_entity(relationship.source).confidence +
        get_entity(relationship.target).confidence
    ) / 2
    entity_score = entity_conf * 0.1

    return explicit_score + clarity_score + entity_score
```

---

## Insight Generation

### What is an Insight?

An insight is **actionable, preference-revealing, or decision-capturing knowledge** extracted from conversation.

**Good Insights:**
- "User prefers TypeScript over JavaScript for production code"
- "User follows test-driven development practices"
- "User is building a REST API with authentication requirements"
- "User decided to use PostgreSQL instead of MongoDB for data integrity"

**Bad Insights (Don't Extract):**
- "User said hello" (not actionable)
- "Weather was mentioned" (not preference-revealing)
- "User asked a question" (not decision-capturing)

**Extraction Prompt:**

```text
Analyze the conversation and generate insights.

An insight is:
- A learned preference (what the user likes/dislikes)
- A decision made (what the user chose and why)
- An observation about user behavior or expertise

For each insight, provide:
- content: 1-2 sentences capturing the insight
- type: preference | decision | observation | expertise
- confidence: 0.0-1.0
- tags: List of relevant topics

Avoid:
- Trivial statements ("user said hello")
- Temporary facts ("user is tired today")
- Purely informational ("FastAPI is a Python framework")

Conversation:
User: "I always write tests first, then implement the feature"
Assistant: "That's test-driven development, a great practice..."

Output as JSON:
{
  "insights": [
    {
      "content": "User practices test-driven development by writing tests before implementation",
      "type": "expertise",
      "confidence": 0.92,
      "tags": ["testing", "methodology", "tdd"]
    }
  ]
}
```

### Insight Types

| Type | Description | Example |
|------|-------------|---------|
| **preference** | User likes/dislikes | "Prefers FastAPI over Flask" |
| **decision** | Choice made | "Decided to use PostgreSQL for transactions" |
| **observation** | Behavioral pattern | "Tends to ask for code examples" |
| **expertise** | Skill/knowledge level | "Experienced with Python, learning Rust" |

---

## Extraction Execution

**Asynchronous Pipeline:**

```python
async def extract_from_turn(turn: Turn):
    """Run extraction in background (doesn't block response)."""

    # Prepare extraction context
    context = f"User: {turn.user_message}\nAssistant: {turn.assistant_message}"

    # Call extraction LLM
    extraction_result = await extraction_llm.chat_completion([
        {"role": "system", "content": EXTRACTION_PROMPT},
        {"role": "user", "content": context}
    ])

    # Parse JSON response
    data = json.loads(extraction_result.content)

    # Store entities in graph
    for entity_data in data["entities"]:
        if entity_data["confidence"] >= confidence_threshold:
            await graph_store.add_or_update_entity(entity_data)

    # Store relationships in graph
    for rel_data in data["relationships"]:
        if rel_data["confidence"] >= confidence_threshold:
            await graph_store.add_relationship(rel_data)

    # Store insights in vector store
    for insight_data in data["insights"]:
        if insight_data["confidence"] >= confidence_threshold:
            # Generate embedding
            embedding = await embedding_model.embed(insight_data["content"])

            # Store in short_term collection initially
            await vector_store.add_document(
                content=insight_data["content"],
                embedding=embedding,
                metadata={
                    "type": insight_data["type"],
                    "confidence": insight_data["confidence"],
                    "tags": insight_data["tags"],
                    "turn_id": turn.id,
                    "collection": "short_term",
                    "created_at": now()
                }
            )
```

**Performance:**
- Extraction runs in **background** (doesn't delay response to user)
- Typically completes in **1-3 seconds**
- Failures are logged but don't affect conversation

### Error Handling

```python
try:
    await extract_from_turn(turn)
except JSONDecodeError:
    logger.warning(f"Extraction LLM returned invalid JSON for turn {turn.id}")
    # Continue - extraction failure doesn't block conversation
except ExtractionLLMError as e:
    logger.error(f"Extraction failed for turn {turn.id}: {e}")
    # Could retry with exponential backoff
except Exception as e:
    logger.error(f"Unexpected extraction error: {e}")
    # Alert monitoring system
```

{{< callout type="warning" >}}
Extraction failures are isolated from the main conversation loop. If extraction fails for a turn, the user's response is still delivered normally. The failure is logged for operator review.
{{< /callout >}}

---

## Extraction Quality Monitoring

**CLI Commands:**

```bash
# View recent extractions
/facts --limit 10 --sort created_at

# Check extraction confidence distribution
/facts --stats

# Review low-confidence extractions
/facts --confidence-max 0.7

# See entity extraction results
/entities --sort hit_count
```

**Quality Metrics Output:**

```text
==============================================================
EXTRACTION QUALITY METRICS
==============================================================
Last 100 Turns:
  Entities extracted:     247
  Relationships extracted: 189
  Insights extracted:      134

Confidence Distribution:
  0.9-1.0 (Excellent): 45%
  0.8-0.9 (Good):      32%
  0.7-0.8 (Fair):      18%
  0.6-0.7 (Marginal):  5%

Average Confidence:
  Entities:       0.87
  Relationships:  0.82
  Insights:       0.84

Extraction Latency:
  p50: 1.2s
  p95: 2.8s
  p99: 4.1s
==============================================================
```

---

## The MemoryExtractor Component

From the friday-memory package, the `MemoryExtractor` handles all LLM-powered extraction of structured knowledge:

- **Entity extraction**: people, projects, technologies with types and descriptions
- **Relationship extraction**: directional predicates with semantic verb types
- **Insight extraction**: semantic observations, preferences, and decisions
- **Turn summarization**: condensed summaries for long conversations

The `ContextConsolidator` then runs background optimization:
- Conversation summarization for long sessions
- Memory compaction to reduce redundancy
- Token budget optimization for future context assembly

---

## Performance Targets

| Operation | Target Latency |
|-----------|----------------|
| Extraction (background) | 1-3s |
| Entity lookup | <10ms |
| Relationship query | <50ms |
| Embedding generation (per insight) | 100-500ms |

{{< callout type="info" >}}
Background extraction is non-blocking—it doesn't impact user experience. Using a separate extraction model provides ~94% cost savings vs. using the main conversation LLM for extraction. Confidence thresholds ensure quality control (only store high-confidence extractions).
{{< /callout >}}
